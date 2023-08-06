import os
from string import Template
import time
from typing import Any, Dict

from click import ClickException
from google.api_core.exceptions import BadRequest, Forbidden, NotFound, PermissionDenied
from google.cloud.compute_v1.types import (
    FirewallPolicyAssociation,
    FirewallPolicyRule,
    Operation,
)
from google.iam.v1.iam_policy_pb2 import SetIamPolicyRequest
from google.iam.v1.policy_pb2 import Binding
from googleapiclient.errors import HttpError
import yaml

from anyscale.cli_logger import BlockLogger
import anyscale.conf
import anyscale.shared_anyscale_utils.conf as shared_anyscale_conf
from anyscale.utils.gcp_utils import GoogleCloudClientFactory


def get_project_number(factory: GoogleCloudClientFactory, project_id: str):
    project_client = factory.resourcemanager_v3.ProjectsClient()
    try:
        project = project_client.get_project(name=f"projects/{project_id}")
        return project.name  # format: "/projects/{project_number}"
    except (NotFound, PermissionDenied, Forbidden) as e:
        raise ClickException(
            f"Error occurred when trying to access the project {project_id}: {e}"
        )


def append_project_iam_policy(
    factory: GoogleCloudClientFactory, project_id: str, role: str, member: str
):
    policy_client = factory.resourcemanager_v3.ProjectsClient()
    try:
        policy = policy_client.get_iam_policy(resource=f"projects/{project_id}")
        if policy.bindings is None:
            policy.bindings = []

        policy.bindings.append(Binding(role=role, members=[member]))
        updated_policy = policy_client.set_iam_policy(
            SetIamPolicyRequest(policy=policy, resource=f"projects/{project_id}")
        )
        return updated_policy
    except (BadRequest, NotFound, PermissionDenied, Forbidden) as e:
        raise ClickException(f"Failed to set IAM policy for project {project_id}: {e}")


def enable_project_apis(factory: GoogleCloudClientFactory, project_id: str):
    """ Automatically enable APIs that Anyscale needs.
    """
    try:
        service_usage_client = factory.build("serviceusage", "v1")

        response = (
            service_usage_client.services()
            .batchEnable(
                parent="projects/" + project_id,
                body={
                    "serviceIds": [
                        "compute.googleapis.com",  # Compute Engine
                        "file.googleapis.com",  # Filestore
                        "storage-component.googleapis.com",  # Cloud Storage
                        "storage.googleapis.com",  # Cloud Storage
                        "deploymentmanager.googleapis.com",  # Deployment Manager
                        "cloudresourcemanager.googleapis.com",  # Resource Manager
                        "certificatemanager.googleapis.com",  # Certificate Manager for Services
                    ],
                },
            )
            .execute()
        )

        wait_for_operation_completion(
            service_usage_client,
            {"name": response["name"]},
            f"Enable APIs for project {project_id}",
        )
    except HttpError as e:
        raise ClickException(f"Failed to enable APIs for project {project_id}: {e}")


def get_workload_identity_pool(
    factory: GoogleCloudClientFactory, project_id: str, pool_id: str,
):
    workload_identity_pool_client = (
        factory.build("iam", "v1").projects().locations().workloadIdentityPools()
    )

    try:
        workload_identity_pool_client.get(
            name=f"projects/{project_id}/locations/global/workloadIdentityPools/{pool_id}"
        ).execute()
        return pool_id
    except HttpError as e:
        if e.status_code == 404:
            # workload identity pool not found
            return None
        else:
            raise ClickException(f"Failed to get Workload Identity Provider Pool. {e}")


def get_anyscale_gcp_access_service_acount(
    factory: GoogleCloudClientFactory, anyscale_access_service_account: str,
):
    service_account_client = factory.build("iam", "v1").projects().serviceAccounts()

    try:
        service_account_client.get(
            name=f"projects/-/serviceAccounts/{anyscale_access_service_account}"
        ).execute()
        return anyscale_access_service_account
    except HttpError as e:
        if e.status_code == 404:
            # service account not found
            return None
        else:
            raise ClickException(f"Failed to get service account: {e}")


def get_deployment_resources(
    factory: GoogleCloudClientFactory,
    deployment_name: str,
    project_id: str,
    anyscale_access_service_account_name: str,
):
    try:
        deployment_client = factory.build("deploymentmanager", "v2")
        manifest = (
            deployment_client.deployments()
            .get(project=project_id, deployment=deployment_name)
            .execute()["manifest"]
        )
        manifest_name = manifest.split("/")[-1]
        manifest = (
            deployment_client.manifests()
            .get(project=project_id, deployment=deployment_name, manifest=manifest_name)
            .execute()
        )
        config = yaml.safe_load(manifest["config"]["content"])
    except HttpError as e:
        raise ClickException(f"Failed to get deployment {deployment_name}. {e}")

    # TODO (congding): use a pydantic model instead of dict
    cloud_resources = {}
    for resource in config["resources"]:
        if resource["name"] == anyscale_access_service_account_name:
            # we should just keep the cluster service account and skip this
            continue
        if "iamMemberBinding" in resource["type"]:
            # skip IAM member binding
            continue
        if resource["type"] == "gcp-types/file-v1beta1:projects.locations.instances":
            # get filestore location and instance
            cloud_resources["filestore_instance"] = resource["properties"]["instanceId"]
            cloud_resources["filestore_location"] = resource["properties"][
                "parent"
            ].split("/")[-1]
        cloud_resources[resource["type"]] = resource["name"]

    return cloud_resources


def create_workload_identity_pool(
    factory: GoogleCloudClientFactory,
    project_id: str,
    pool_id: str,
    logger: BlockLogger,
    display_name: str = "a workload identity pool",
    description: str = "a workload identity pool",
):
    """ Create a GCP Workload Identity Provider Pool. The functionality is not
    currently supported by GCP Deployment Manager.
    """
    workload_identity_pool_client = (
        factory.build("iam", "v1").projects().locations().workloadIdentityPools()
    )

    parent = f"projects/{project_id}/locations/global"
    pool = {"displayName": display_name, "description": description}

    try:
        create_workload_identity_pool_operation = workload_identity_pool_client.create(
            parent=parent, workloadIdentityPoolId=pool_id, body=pool
        ).execute()

        wait_for_operation_completion(
            workload_identity_pool_client,
            {"name": create_workload_identity_pool_operation["name"]},
            description="creating workload identity provider pool",
        )

        workload_identity_pool = create_workload_identity_pool_operation["name"].split(
            "/operation"
        )[0]
        logger.info(f"Workload Identity Pool created: {workload_identity_pool}")
        return workload_identity_pool
    except HttpError as e:
        if e.status_code == 409:
            logger.error(
                f"Provider Pool {pool_id} already exists in project {project_id}."
            )
        else:
            logger.error(
                f"Error occurred when trying to build Workload Identity Provider Pool. Detailed: {e}"
            )
        raise ClickException("Failed to create Workload Identity Provider Pool. ")


def create_anyscale_aws_provider(
    factory: GoogleCloudClientFactory,
    organization_id: str,
    pool_id: str,
    provider_id: str,
    aws_account_id: str,
    display_name: str,
    logger: BlockLogger,
):
    """ Create a GCP Workload Identity Provider for Anyscale cross account access.
    The functionality is notcurrently supported by GCP Deployment Manager.
    """
    provider_client = (
        factory.build("iam", "v1")
        .projects()
        .locations()
        .workloadIdentityPools()
        .providers()
    )

    parent = pool_id
    provider = {
        "aws": {"accountId": aws_account_id},
        "name": provider_id,
        "displayName": display_name,
        "description": "provider for Anyscale access",
        "attributeMapping": {
            "attribute.aws_role": "assertion.arn.contains('assumed-role') ? assertion.arn.extract('{account_arn}assumed-role/') + 'assumed-role/' + assertion.arn.extract('assumed-role/{role_name}/') : assertion.arn",
            "google.subject": "assertion.arn",
            "attribute.arn": "assertion.arn",
        },
        "attributeCondition": f"google.subject.startsWith('arn:aws:sts::{aws_account_id}:assumed-role/gcp_if_{organization_id}')",
    }

    try:
        response = provider_client.create(
            parent=parent, workloadIdentityPoolProviderId=provider_id, body=provider
        ).execute()
        wait_for_operation_completion(
            provider_client,
            {"name": response["name"]},
            description="creating workload identity provider",
        )
        workload_identity_provider = response["name"].split("/operation")[0]
        logger.info(f"Anyscale provider created: {workload_identity_provider}")
        return workload_identity_provider
    except HttpError as e:
        if e.status_code == 409:
            logger.error(f"Provider {provider_id} already exists in pool {parent}.")
        else:
            logger.error(
                f"Error occurred when trying to build Workload Identity Provider Pool. Detailed: {e}"
            )
        raise ClickException("Failed to create Anyscale AWS Workload Identity Provider")


def generate_deployment_manager_config(  # noqa: PLR0913
    region: str,
    project_id: str,
    cloud_id: str,
    anyscale_access_service_account_name: str,
    workload_identity_pool_name: str,
    anyscale_aws_account: str,
    organization_id: str,
    subnet_cidr: str = "10.0.0.0/20",
    zone: str = "b",  # some regions like us-east1 or europe-west1 don't have zone "a"
    fileshare_capacity_gb: int = 1024,
) -> str:
    cloud_id = cloud_id.replace("_", "-").lower()

    with open(
        os.path.join(anyscale.conf.ROOT_DIR_PATH, "anyscale-cloud-setup-gcp.yaml")
    ) as f:
        deployment_manager_config = Template(f.read())

    params = {
        "ANYSCALE_HOST": shared_anyscale_conf.ANYSCALE_HOST,
        "REGION": region,
        "CLOUD_ID": cloud_id,
        "PROJECT_ID": project_id,
        "ANYSCALE_ACCESS_SERVICE_ACCOUNT": anyscale_access_service_account_name,
        "WORKLOAD_IDENTITY_POOL_NAME": workload_identity_pool_name,
        "ANYSCALE_AWS_ACCOUNT": anyscale_aws_account,
        "ORGANIZATION_ID": organization_id,
        "SUBNET_CIDR": subnet_cidr,
        "ZONE": zone,
        "FILESHARE_CAPACITY_GB": fileshare_capacity_gb,
    }

    return deployment_manager_config.substitute(params)


def configure_firewall_policy(
    factory: GoogleCloudClientFactory,
    vpc_name: str,
    project_id: str,
    firewall_policy: str,
    subnet_cidr: str = "10.0.0.0/20",
):
    """ Add VPC association and necessary firewall rules to a firewall policy.
    """
    association = FirewallPolicyAssociation(
        name=f"{firewall_policy}-for-{vpc_name}",
        attachment_target=f"projects/{project_id}/global/networks/{vpc_name}",
    )

    rules = [
        FirewallPolicyRule(
            action="allow",
            direction="INGRESS",
            priority=1000,
            match={
                "src_ip_ranges": ["0.0.0.0/0"],
                "layer4_configs": [{"ip_protocol": "TCP", "ports": ["22", "443"]}],
            },
        ),
        FirewallPolicyRule(
            action="allow",
            direction="INGRESS",
            priority=1001,
            match={
                "src_ip_ranges": [subnet_cidr],
                "layer4_configs": [{"ip_protocol": "all"}],
            },
        ),
    ]

    network_firewall_policy_client = factory.compute_v1.NetworkFirewallPoliciesClient()
    client = factory.compute_v1.GlobalOperationsClient()
    try:
        operations = []
        for rule in rules:
            operation = network_firewall_policy_client.add_rule(
                project=project_id,
                firewall_policy=firewall_policy,
                firewall_policy_rule_resource=rule,
            )
            operations.append(operation)
        operation = network_firewall_policy_client.add_association(
            project=project_id,
            firewall_policy=firewall_policy,
            firewall_policy_association_resource=association,
        )
        operations.append(operation)

        for operation in operations:
            response = client.wait(project=project_id, operation=operation.name)
            if response.status != Operation.Status.DONE:
                # timeout
                raise ClickException(
                    "Timeout when trying to configure firewall policy."
                )
            if response.error:
                raise ClickException(
                    f"Failed to configure firewall policy {firewall_policy}. {response.error}"
                )
    except (NotFound, BadRequest) as e:
        raise ClickException(
            f"Failed to configure firewall policy {firewall_policy}. {e}"
        )


def delete_workload_identity_pool(
    factory: GoogleCloudClientFactory, pool_name: str, logger: BlockLogger
):
    service = factory.build("iam", "v1").projects().locations().workloadIdentityPools()

    # we can directly delete the pool even if there're providers in it
    try:
        delete_pool_operation = service.delete(name=pool_name).execute()
        wait_for_operation_completion(
            service,
            {"name": delete_pool_operation["name"]},
            "deleting workload identity provider pool",
        )
        logger.info(f"Deleted workload identity pool: {pool_name}")
    except HttpError as e:
        if e.status_code == 404:
            return
        raise ClickException(
            f"Error occurred when trying to delete workload identity pool {pool_name}: {e}. Please delete the resources by yourself."
        )


def wait_for_operation_completion(
    service: Any,
    request: Dict[str, str],
    description: str = "Operation",
    timeout: int = 300,
    polling_interval: int = 3,
) -> None:
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_operation = service.operations().get(**request).execute()
        if (
            current_operation.get("done", False)
            or current_operation.get("status", None) == "DONE"
        ):
            if "error" in current_operation:
                raise ClickException(
                    f"{description} encountered an error: {current_operation['error']}"
                )
            break
        time.sleep(polling_interval)
    else:
        raise ClickException(
            f"{description} did not complete within the timeout period ({timeout}s)"
        )


def delete_gcp_deployment(
    factory: GoogleCloudClientFactory, project_id: str, deployment_name: str,
):
    """
    Get the GCP Deployment and try to delete the deployment if it exists.
    """
    deployment_client = factory.build("deploymentmanager", "v2")
    try:
        # get the deployment
        deployment_client.deployments().get(
            project=project_id, deployment=deployment_name
        ).execute()
    except HttpError as e:
        if e.status_code == 404:
            # no deployment found
            return
        raise ClickException(
            f"Failed to get deployment {deployment_name}: {e}. Please delete the resources yourself"
        )

    try:
        # delete the deployment
        response = (
            deployment_client.deployments()
            .delete(project=project_id, deployment=deployment_name)
            .execute()
        )
        wait_for_operation_completion(
            deployment_client,
            {"operation": response["name"], "project": project_id},
            f"Delete deployment {deployment_name}",
            timeout=600,
        )
    except HttpError as e:
        raise ClickException(
            f"Failed to delete deployment {deployment_name}: {e}. Please delete the resources yourself."
        )


def update_deployment_with_bucket_only(
    factory: GoogleCloudClientFactory, project_id: str, deployment_name: str
):
    """
    Update all resources in the deployment except the bucket.
    Removing the resources in deployment deletes the underlying resource by default.
    See https://cloud.google.com/deployment-manager/docs/reference/latest/deployments/update
    """
    # update the deployment with only the bucket
    deployment_client = factory.build("deploymentmanager", "v2")
    try:
        # get the deployment
        deployment = (
            deployment_client.deployments()
            .get(project=project_id, deployment=deployment_name)
            .execute()
        )
        fingerprint = deployment["fingerprint"]
        manifest = deployment["manifest"]
        manifest_name = manifest.split("/")[-1]

        # get manifest
        manifest = (
            deployment_client.manifests()
            .get(
                project=project_id, deployment=deployment_name, manifest=manifest_name,
            )
            .execute()
        )
        config = yaml.safe_load(manifest["config"]["content"])

        # build a resource config with only the bucket
        resources = list(
            filter(lambda r: r["type"] == "storage.v1.bucket", config["resources"])
        )

        # update the deployment
        deployment = {
            "name": deployment_name,
            "fingerprint": fingerprint,
            "target": {"config": {"content": yaml.dump({"resources": resources}),},},
        }
        response = (
            deployment_client.deployments()
            .update(project=project_id, deployment=deployment_name, body=deployment)
            .execute()
        )
        wait_for_operation_completion(
            deployment_client,
            {"operation": response["name"], "project": project_id},
            f"Delete deployment {deployment_name}",
            timeout=600,
        )
    except HttpError as e:
        raise ClickException(
            f"Failed to delete deployment {deployment_name}. Error: {e}"
        )


def remove_firewall_policy_associations(
    factory: GoogleCloudClientFactory, project_id: str, firewall_policy_name: str,
):
    """
    Remove the firewall policy associations if exist
    """
    # get the firewall first
    network_firewall_policy_client = factory.compute_v1.NetworkFirewallPoliciesClient()
    operation_client = factory.compute_v1.GlobalOperationsClient()
    try:
        firewall_policy = network_firewall_policy_client.get(
            project=project_id, firewall_policy=firewall_policy_name
        )
    except NotFound:
        # no firewall policy
        return
    except (PermissionDenied, Forbidden, BadRequest) as e:
        raise ClickException(f"Failed to remove firewall policy associations. {e}")

    if not firewall_policy.associations:
        # no associations
        return

    operations = []
    associations = firewall_policy.associations
    for association in associations:
        try:
            remove_association_request = {
                "name": association.name,
                "project": project_id,
                "firewall_policy": firewall_policy_name,
            }
            operation = network_firewall_policy_client.remove_association(
                request=remove_association_request
            )
        except (BadRequest, NotFound):
            # BadRequest: no association found, NotFound: no firewall policy found
            continue
        except (PermissionDenied, Forbidden) as e:
            raise ClickException(f"Failed to remove firewall policy association. {e}")
        operations.append(operation)

    for operation in operations:
        response = operation_client.wait(project=project_id, operation=operation.name)
        if response.status != Operation.Status.DONE:
            # timeout
            raise ClickException(
                "Timeout when trying to remove firewall policy association."
            )
        if response.error:
            raise ClickException(
                f"Failed to remove firewall policy association. {response.error}"
            )
