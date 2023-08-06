import difflib
import pprint
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from anyscale.aws_iam_policies import (
    AMAZON_ECR_READONLY_ACCESS_POLICY_NAME,
    ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE,
    ANYSCALE_IAM_PERMISSIONS_SERVICE_STEADY_STATE,
    get_anyscale_aws_iam_assume_role_policy,
    get_anyscale_iam_permissions_ec2_restricted,
)
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.create_cloud_resource import (
    CreateCloudResource,
)
from anyscale.client.openapi_client.models.subnet_id_with_availability_zone_aws import (
    SubnetIdWithAvailabilityZoneAWS,
)
from anyscale.shared_anyscale_utils.aws import AwsRoleArn
from anyscale.shared_anyscale_utils.conf import ANYSCALE_HOST
from anyscale.util import (  # pylint:disable=private-import
    _get_subnet,
    contains_control_plane_role,
    filter_actions_associated_with_role,
    filter_actions_from_policy_document,
)
from anyscale.utils.network_verification import (
    AWS_SUBNET_CAPACITY,
    AWS_VPC_CAPACITY,
)
from anyscale.utils.s3 import verify_s3_access


# This needs to be kept in sync with the Ray autoscaler in
# https://github.com/ray-project/ray/blob/eb9c5d8fa70b1c360b821f82c7697e39ef94b25e/python/ray/autoscaler/_private/aws/config.py
# It should go away with the SSM refactor.
DEFAULT_RAY_IAM_ROLE = "ray-autoscaler-v1"


def compare_dicts_diff(d1: Dict[Any, Any], d2: Dict[Any, Any]) -> str:
    """Returns a string representation of the difference of the two dictionaries.
    Example:

    Input:
    print(compare_dicts_diff({"a": {"c": 1}, "b": 2}, {"a": {"c": 2}, "d": 3}))

    Output:
    - {'a': {'c': 1}, 'b': 2}
    ?             ^    ^   ^

    + {'a': {'c': 2}, 'd': 3}
    ?             ^    ^   ^
    """

    return "\n" + "\n".join(
        difflib.ndiff(pprint.pformat(d1).splitlines(), pprint.pformat(d2).splitlines())
    )


def log_resource_not_found_error(
    resource_name: str, resource_id: str, logger: BlockLogger
) -> None:
    logger.error(
        f"Could not find {resource_name} with id {resource_id}. Please validate that you're using the correct AWS account/credentials and that the resource values are correct"
    )


def verify_aws_vpc(
    cloud_resource: CreateCloudResource,
    boto3_session: boto3.Session,
    logger: BlockLogger,
    ignore_capacity_errors: bool = False,  # TODO: Probably don't do this forever. Its kinda hacky
    strict: bool = False,  # strict is currently unused # noqa: ARG001
) -> bool:
    logger.info("Verifying VPC ...")
    if not cloud_resource.aws_vpc_id:
        logger.error("Missing VPC id.")
        return False

    ec2 = boto3_session.resource("ec2")
    vpc = ec2.Vpc(cloud_resource.aws_vpc_id)

    # Verify the VPC exists
    try:
        vpc.load()
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidVpcID.NotFound":
            log_resource_not_found_error("VPC", cloud_resource.aws_vpc_id, logger)
            return False
        raise e

    # Verify that the VPC has "enough" capacity.
    if (
        AWS_VPC_CAPACITY.verify_network_capacity(
            cidr_block_str=vpc.cidr_block, resource_name=vpc.id, logger=logger
        )
        or ignore_capacity_errors
    ):
        logger.info(f"VPC {vpc.id} verification succeeded.")
        return True
    return False


def _get_subnets_from_subnet_ids(subnet_ids: List[str], region: str) -> List[Any]:
    return [
        _get_subnet(subnet_arn=subnet_id, region=region) for subnet_id in subnet_ids
    ]


def verify_aws_subnets(  # noqa: PLR0911
    cloud_resource: CreateCloudResource,
    region: str,
    is_private_network: bool,
    logger: BlockLogger,
    ignore_capacity_errors: bool = False,  # TODO: Probably don't do this forever. Its kinda hacky
    strict: bool = False,
) -> bool:
    """Verify the subnets cloud resource of a cloud."""

    logger.info("Verifying subnets ...")

    if not cloud_resource.aws_vpc_id:
        logger.error("Missing VPC ID.")
        return False

    subnet_ids = []
    if (
        cloud_resource.aws_subnet_ids_with_availability_zones
        and len(cloud_resource.aws_subnet_ids_with_availability_zones) > 0
    ):
        subnet_ids = [
            subnet_id_with_az.subnet_id
            for subnet_id_with_az in cloud_resource.aws_subnet_ids_with_availability_zones
        ]
    else:
        logger.error("Missing subnet IDs.")
        return False

    # We must have at least 2 subnets since services requires 2 different subnets to setup ALB.
    if len(subnet_ids) < 2:
        logger.error(
            "Need at least 2 subnets for a cloud. This is required for Anyscale services to function properly."
        )
        return False

    subnets = _get_subnets_from_subnet_ids(subnet_ids=subnet_ids, region=region)
    subnet_azs = set()

    for subnet, subnet_id in zip(subnets, subnet_ids):
        # Verify subnet exists
        if not subnet:
            log_resource_not_found_error("Subnet", subnet_id, logger)
            return False

        # Verify the Subnet has "enough" capacity.
        if (
            not AWS_SUBNET_CAPACITY.verify_network_capacity(
                cidr_block_str=subnet.cidr_block, resource_name=subnet.id, logger=logger
            )
            and not ignore_capacity_errors
        ):
            return False

        # Verify that the subnet is in the provided VPC all of these are in the same VPC.
        if subnet.vpc_id != cloud_resource.aws_vpc_id:
            logger.error(
                f"The subnet {subnet_id} is not in a vpc of this cloud. The vpc of this subnet is {subnet.vpc_id} and the vpc of this cloud is {cloud_resource.aws_vpc_id}."
            )
            return False

        # Verify that the subnet is auto-assigning public IP addresses if it's not private.
        if not is_private_network and not subnet.map_public_ip_on_launch:
            logger.warning(
                f"The subnet {subnet_id} does not have the 'Auto-assign Public IP' option enabled. This is not currently supported."
            )
            if strict:
                return False

        # Success!
        logger.info(f"Subnet {subnet.id}'s verification succeeded.")
        subnet_azs.add(subnet.availability_zone)

    if len(subnet_azs) < 2:
        logger.error(
            "Subnets should be in at least 2 Availability Zones. This is required for Anyscale services to function properly."
        )
        return False

    logger.info(
        f"Subnets {cloud_resource.aws_subnet_ids_with_availability_zones} verification succeeded."
    )
    return True


def associate_aws_subnets_with_azs(
    aws_subnet_ids: List[str], region: str
) -> List[SubnetIdWithAvailabilityZoneAWS]:
    """This function combines the subnets with its availability zone.
    """

    subnets = _get_subnets_from_subnet_ids(subnet_ids=aws_subnet_ids, region=region)

    # combine subnet and its availability zone
    subnet_ids_with_availability_zones = [
        SubnetIdWithAvailabilityZoneAWS(
            subnet_id=subnet.id, availability_zone=subnet.availability_zone,
        )
        for subnet in subnets
    ]

    return subnet_ids_with_availability_zones


def _get_roles_from_cloud_resource(
    cloud_resource: CreateCloudResource,
    boto3_session: boto3.Session,
    logger: BlockLogger,
) -> Optional[List[Any]]:
    iam = boto3_session.resource("iam")
    roles = [
        iam.Role(AwsRoleArn.from_string(role_arn).to_role_name())
        for role_arn in cloud_resource.aws_iam_role_arns
    ]
    # Validate the roles exist.
    # `.load()` will throw an exception if the Role does not exist.
    for role in roles:
        try:
            role.load()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                logger.error(f"Could not find role: {role.name}")
                return None
            raise e
    return roles


def verify_aws_iam_roles(  # noqa: PLR0911
    cloud_resource: CreateCloudResource,
    boto3_session: boto3.Session,
    anyscale_aws_account: str,
    logger: BlockLogger,
    cloud_id: str,
    strict: bool = False,
    _use_strict_iam_permissions: bool = False,
) -> bool:

    logger.info("Verifying IAM roles ...")
    if not cloud_resource.aws_iam_role_arns:
        logger.error("Missing IAM role arns.")
        return False
    accounts = [
        AwsRoleArn.from_string(role).account_id
        for role in cloud_resource.aws_iam_role_arns
    ]
    if len(set(accounts)) != 1:
        logger.error(
            f"All IAM roles must be in the same AWS account: {cloud_resource.aws_iam_role_arns}"
        )
        return False

    roles = _get_roles_from_cloud_resource(cloud_resource, boto3_session, logger)
    if roles is None:
        return False

    # verifying control plane role: anyscale iam role
    anyscale_iam_role = roles[0]
    assume_role_policy_document = anyscale_iam_role.assume_role_policy_document
    if not contains_control_plane_role(
        assume_role_policy_document=assume_role_policy_document,
        anyscale_aws_account=anyscale_aws_account,
    ):
        logger.warning(
            f"Anyscale IAM role {anyscale_iam_role.arn} does not contain expected assume role policy. It must allow assume role from arn:aws:iam::{anyscale_aws_account}:root."
        )
        expected_assume_role_policy_document = get_anyscale_aws_iam_assume_role_policy(
            anyscale_aws_account=anyscale_aws_account
        )
        logger.warning(
            compare_dicts_diff(
                assume_role_policy_document, expected_assume_role_policy_document
            )
        )
        if strict:
            return False

    # Verify EC2 steady state permissions
    # If permissions are missing, log warning message
    anyscale_iam_permissions_ec2 = ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE
    if _use_strict_iam_permissions:
        anyscale_iam_permissions_ec2 = get_anyscale_iam_permissions_ec2_restricted(
            cloud_id
        )

    allow_actions_expected = filter_actions_from_policy_document(
        anyscale_iam_permissions_ec2
    )
    allow_actions_on_role = filter_actions_associated_with_role(
        boto3_session, anyscale_iam_role
    )
    allow_actions_missing = allow_actions_expected - allow_actions_on_role

    if allow_actions_missing:
        logger.warning(
            f"IAM role {anyscale_iam_role.arn} does not have sufficient permissions for cluster management. We suggest adding these actions to ensure that cluster management works properly: {allow_actions_missing}. "
        )

    # Verify Service Steady State permissions
    # If service permissions are missing, display confirmation message to user if they would like to continue
    allow_actions_expected = filter_actions_from_policy_document(
        ANYSCALE_IAM_PERMISSIONS_SERVICE_STEADY_STATE
    )
    allow_actions_missing = allow_actions_expected - allow_actions_on_role
    if allow_actions_missing:
        logger.print_red_error_message(
            "[SERVICES V2] Permissions are missing to enable services v2 "
        )
        logger.confirm_missing_permission(
            f"For IAM role {anyscale_iam_role.arn}, we suggest adding the following actions:\n{pprint.pformat(allow_actions_missing)}.\n"
        )
        if strict:
            return False

    # verifying data plane role: ray autoscaler role
    cluster_node_role = roles[1]
    policy_names = [
        policy.policy_name for policy in cluster_node_role.attached_policies.all()
    ]
    if AMAZON_ECR_READONLY_ACCESS_POLICY_NAME not in policy_names:
        logger.warning(
            f"Dataplane role {cluster_node_role.arn} does not contain policy {AMAZON_ECR_READONLY_ACCESS_POLICY_NAME}. This is safe to ignore if you are not pulling custom Docker Images from an ECR repository."
        )
        if strict:
            return False

    if (
        len(
            [
                profile
                for profile in cluster_node_role.instance_profiles.all()
                if profile.name == cluster_node_role.name
            ]
        )
        == 0
    ):
        logger.warning(
            f"Dataplane role {cluster_node_role.arn} is required to have an instance profile with the name {cluster_node_role.name}."
            "\nPlease create this isntance profile and associate it to the role."
        )
        return False

    logger.info(f"IAM roles {cloud_resource.aws_iam_role_arns} verification succeeded.")
    return True


def verify_aws_security_groups(  # noqa: PLR0912
    cloud_resource: CreateCloudResource,
    boto3_session: boto3.Session,
    logger: BlockLogger,
    strict: bool = False,
) -> bool:
    logger.info("Verifying security groups ...")
    if not cloud_resource.aws_security_groups:
        logger.error("Missing security group IDs.")
        return False

    ec2 = boto3_session.resource("ec2")

    aws_security_group_ids = cloud_resource.aws_security_groups
    anyscale_security_groups = []

    for anyscale_security_group_id in aws_security_group_ids:
        anyscale_security_group = ec2.SecurityGroup(anyscale_security_group_id)
        try:
            anyscale_security_group.load()
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidGroup.NotFound":
                log_resource_not_found_error(
                    "Security group", anyscale_security_group_id, logger
                )
                return False
            raise e
        anyscale_security_groups.append(anyscale_security_group)

    expected_open_ports = [443, 22]  # 443 is for HTTPS ingress, 22 is for SSH

    inbound_ip_permissions = [
        ip_permission
        for anyscale_security_group in anyscale_security_groups
        for ip_permission in anyscale_security_group.ip_permissions
    ]
    inbound_ip_permissions_with_specific_port = {
        ip_permission["FromPort"]
        for ip_permission in inbound_ip_permissions
        if "FromPort" in ip_permission
    }
    inbound_sg_rule_with_self = []  # type: ignore
    for sg_rule in inbound_ip_permissions:
        if sg_rule.get("IpProtocol") == "-1":
            inbound_sg_rule_with_self.extend(sg_rule.get("UserIdGroupPairs"))  # type: ignore

    missing_open_ports = []
    for port in expected_open_ports:
        if not any(
            inbound_ip_permission_port == port
            for inbound_ip_permission_port in inbound_ip_permissions_with_specific_port
        ):
            missing_open_ports.append(port)
    if missing_open_ports:
        logger.warning(
            f"Security groups {aws_security_group_ids} do not contain inbound permission for ports: {missing_open_ports}. These ports are used for interaction with the clusters from Anyscale UI. Please make sure to configure them according to https://docs.anyscale.com/user-guide/onboard/clouds/deploy-on-aws#appendix-detailed-resource-requirements"
        )
        if strict:
            return False

    if not any(
        sg_rule.get("GroupId") in aws_security_group_ids
        for sg_rule in inbound_sg_rule_with_self
    ):
        logger.error(
            f"Security groups {aws_security_group_ids} do not contain inbound permission for all ports for traffic from the same security group."
        )
        return False

    if len(inbound_ip_permissions_with_specific_port) > len(expected_open_ports):
        logger.warning(
            f"Security groups {aws_security_group_ids} allows access to more than {expected_open_ports}. This may not be safe by default."
        )
        if strict:
            return False

    logger.info(f"Security group {aws_security_group_ids} verification succeeded.")
    return True


def verify_aws_s3(  # noqa: PLR0911, PLR0912
    cloud_resource: CreateCloudResource,
    boto3_session: boto3.Session,
    region: str,
    logger: BlockLogger,
    strict: bool = False,
) -> bool:
    logger.info("Verifying S3 ...")
    if not cloud_resource.aws_s3_id:
        logger.error("Missing S3 ID.")
        return False

    s3 = boto3_session.resource("s3")
    bucket_name = cloud_resource.aws_s3_id.split(":")[-1]
    s3_bucket = s3.Bucket(bucket_name)

    # Check for the existence of `creation_date` because this incurs a `list_bucket` call.
    # Calling `.load()` WILL NOT ERROR in cases where the caller does not have access to the bucket.
    if s3_bucket.creation_date is None:
        log_resource_not_found_error("S3 bucket", cloud_resource.aws_s3_id, logger)
        return False

    has_correct_cors_rule = False
    """
    Verify CORS rules. The correct CORS rule should look like:
    [{
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET"
        ],
        "AllowedOrigins": [
            "https://console.anyscale-staging.com"
        ],
        "ExposeHeaders": []
    }]
    """

    try:
        cors_rules = s3_bucket.Cors().cors_rules
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchCORSConfiguration":
            logger.warning(
                f"S3 bucket {bucket_name} does not have CORS rules. This is safe to ignore if you are not using Anyscale UI. Otherwise please create the correct CORS rule for Anyscale according to https://docs.anyscale.com/anyscale-cloud-administration/deploy-on-aws#appendix-detailed-resource-requirements"
            )
            cors_rules = []
            if strict:
                return False
        else:
            raise e

    for rule in cors_rules:
        assert isinstance(rule, dict), "Malformed CORS rule."
        has_correct_cors_rule = (
            ANYSCALE_HOST in rule.get("AllowedOrigins", [])
            and "*" in rule.get("AllowedHeaders", [])
            and "GET" in rule.get("AllowedMethods", [])
        )

    if not has_correct_cors_rule:
        logger.warning(
            f"S3 bucket {bucket_name} does not have the correct CORS rule for Anyscale. This is safe to ignore if you are not using Anyscale UI. Otherwise please create the correct CORS rule for Anyscale according to https://docs.anyscale.com/anyscale-cloud-administration/deploy-on-aws#appendix-detailed-resource-requirements"
        )
        if strict:
            return False

    returned_bucket_location = boto3_session.client("s3").get_bucket_location(
        Bucket=bucket_name
    )["LocationConstraint"]

    # LocationConstraint is `None` if the bucket is located in us-east-1
    bucket_region = returned_bucket_location or "us-east-1"
    if bucket_region != region:
        logger.warning(
            f"S3 bucket {bucket_name} is in region {bucket_region}, but this cloud is being set up in {region}."
            "This can result in degraded cluster launch & logging performance as well as additional cross-region costs."
        )
        if strict:
            return False

    roles = _get_roles_from_cloud_resource(cloud_resource, boto3_session, logger)
    if roles is None:
        return False

    if not verify_s3_access(boto3_session, s3_bucket, roles[0], logger):
        logger.warning(
            f"S3 Bucket {bucket_name} does not appear to have correct permissions for the Anyscale Control Plane role {roles[0].name}"
        )
        if strict:
            return False

    if not verify_s3_access(boto3_session, s3_bucket, roles[1], logger):
        logger.warning(
            f"S3 Bucket {bucket_name} does not appear to have correct permissions for the Data Plane role {roles[1].name}"
        )
        if strict:
            return False
    logger.info(f"S3 {cloud_resource.aws_s3_id} verification succeeded.")
    return True


def _get_network_interfaces_from_mount_targets(
    mount_targets_response: dict, boto3_session: Any, logger: BlockLogger
) -> List[Any]:
    ec2 = boto3_session.resource("ec2")
    network_interfaces = []
    for network_interface_id in [
        mount_target["NetworkInterfaceId"]
        for mount_target in mount_targets_response["MountTargets"]
    ]:
        network_interface = ec2.NetworkInterface(network_interface_id)
        try:
            network_interface.load()
        except ClientError as e:
            logger.warning(f"Network interface loading error: {e}")
            continue
        network_interfaces.append(network_interface)
    return network_interfaces


def verify_aws_efs(  # noqa: PLR0911, PLR0912
    cloud_resource: CreateCloudResource,
    boto3_session: boto3.Session,
    logger: BlockLogger,
    strict: bool = False,
) -> bool:
    logger.info("Verifying EFS ...")
    if not cloud_resource.aws_efs_id:
        logger.error("Missing EFS ID.")
        return False
    subnet_ids = []
    if (
        cloud_resource.aws_subnet_ids_with_availability_zones
        and len(cloud_resource.aws_subnet_ids_with_availability_zones) > 0
    ):
        subnet_ids = [
            subnet_id_with_az.subnet_id
            for subnet_id_with_az in cloud_resource.aws_subnet_ids_with_availability_zones
        ]
    else:
        logger.error("Missing subnet IDs.")
        return False
    if not cloud_resource.aws_security_groups:
        logger.error("Missing security group IDs.")
        return False

    client = boto3_session.client("efs")
    try:
        file_systems_response = client.describe_file_systems(
            FileSystemId=cloud_resource.aws_efs_id
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "FileSystemNotFound":
            log_resource_not_found_error("EFS", cloud_resource.aws_efs_id, logger)
            return False
        raise e

    if len(file_systems_response.get("FileSystems", [])) == 0:
        log_resource_not_found_error("EFS", cloud_resource.aws_efs_id, logger)
        return False

    # verify that there is a mount target for each subnet and security group
    mount_targets_response = client.describe_mount_targets(
        FileSystemId=cloud_resource.aws_efs_id
    )
    mount_targets = mount_targets_response.get("MountTargets")
    if not mount_targets:
        logger.warning(
            f"EFS with id {cloud_resource.aws_efs_id} does not contain mount targets."
        )
        return False

    # verify the mount target ID stored in our database is still valid
    mount_target_ips = [mount_target["IpAddress"] for mount_target in mount_targets]
    if cloud_resource.aws_efs_mount_target_ip and (
        cloud_resource.aws_efs_mount_target_ip not in mount_target_ips
    ):
        logger.error(
            f"Mount target registered with the cloud no longer exists. EFS ID: {cloud_resource.aws_efs_id} IP address: {cloud_resource.aws_efs_mount_target_ip}. Please make sure you have the correct AWS credentials set. If the EFS mount target has been deleted, please recreate the cloud or contact Anyscale for support."
        )
        return False

    network_interfaces = _get_network_interfaces_from_mount_targets(
        mount_targets_response, boto3_session, logger
    )

    expected_security_group_id = cloud_resource.aws_security_groups[0]
    for subnet_id in subnet_ids:
        contains_subnet_id_security_group = False
        for network_interface in network_interfaces:
            network_interface_security_group_ids = [
                group["GroupId"]
                for group in network_interface.groups
                if group.get("GroupId")
            ]
            if (
                network_interface.subnet_id == subnet_id
                and expected_security_group_id in network_interface_security_group_ids
            ):
                contains_subnet_id_security_group = True
                break
        if not contains_subnet_id_security_group:
            logger.warning(
                f"EFS with id {cloud_resource.aws_efs_id} does not contain network interface with subnet id {subnet_id} and security group id {cloud_resource.aws_security_groups[0]}."
            )
            if strict:
                return False

    logger.info(f"EFS {cloud_resource.aws_efs_id} verification succeeded.")
    return True


def verify_aws_cloudformation_stack(
    cloud_resource: CreateCloudResource,
    boto3_session: boto3.Session,
    logger: BlockLogger,
    strict: bool = False,  # strict is currently unused # noqa: ARG001
) -> bool:
    logger.info("Verifying CloudFormation stack ...")
    if not cloud_resource.aws_cloudformation_stack_id:
        logger.error("Missing CloudFormation stack id.")
        return False

    cloudformation = boto3_session.resource("cloudformation")
    stack = cloudformation.Stack(cloud_resource.aws_cloudformation_stack_id)
    try:
        stack.load()
    except ClientError as e:
        if e.response["Error"]["Code"] == "ValidationError":
            log_resource_not_found_error(
                "CloudFormation stack",
                cloud_resource.aws_cloudformation_stack_id,
                logger,
            )
            return False
        raise e

    logger.info(
        f"CloudFormation stack {cloud_resource.aws_cloudformation_stack_id} verification succeeded."
    )
    return True
