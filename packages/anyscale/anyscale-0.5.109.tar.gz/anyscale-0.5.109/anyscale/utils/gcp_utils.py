from functools import partial
import importlib
import subprocess
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from click import ClickException
from google.api_core.exceptions import NotFound
import google.auth
from google.auth.credentials import Credentials
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from google.auth.transport.requests import Request
import google.cloud
from google.iam.v1.policy_pb2 import Binding
from google.oauth2 import service_account
from googleapiclient.discovery import build as api_client_build

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.gcp_file_store_config import (
    GCPFileStoreConfig,
)
from anyscale.util import confirm


class GCPLogger:
    def __init__(
        self, logger: BlockLogger, project_id: str, spinner: Any, yes: bool = False
    ):
        self.internal = logger
        self.project_id = project_id
        self.spinner = spinner
        self.yes = yes

    def log_resource_not_found_error(self, resource_name: str, resource_id: str):
        if resource_name == "Project":
            self.internal.error(
                f"Could not find {resource_name} with id {resource_id}. Please validate that you're using the correct GCP project."
            )
        else:
            self.internal.error(
                f"Could not find {resource_name} with id {resource_id} in project {self.project_id}. Please validate that you're using the correct GCP project and that the resource values are correct."
            )

    def confirm_missing_permission(self, error_str: str):
        self.internal.error(error_str)
        self.spinner.stop()
        confirm(
            "If the serivce account has these required permissions granted via other roles\n"
            "or via a group, press 'y' to continue with verification or 'N' to abort.",
            yes=self.yes,
        )
        self.spinner.start()


class GoogleCloudClientFactory:
    """Factory to generate both Google Cloud Client libraries & Google API Client libraries.

    Google Cloud Client libraries are instantiated by:
    ```
        factory = GoogleCloudClientFactory(credentials=AnonymousCredentials())
        client = factory.compute_v1.ExampleClient()
    ```

    Google API Client libraries are instantiated by:
    ```
        factory = GoogleCloudClientFactory(credentials=AnonymousCredentials())
        client = factory.build("iam", "v1")
    ```
    """

    def __init__(self, credentials: Credentials, force_rest=False, **kwargs):
        kwargs["credentials"] = credentials
        self.kwargs = kwargs
        self.force_rest = force_rest

    def __getattr__(self, client_library: str):
        """Get a wrapped Google Cloud Client library that injects default values from the factory."""
        if not hasattr(google.cloud, client_library):
            importlib.import_module(f"google.cloud.{client_library}")
        module = getattr(google.cloud, client_library)
        kwargs = self.kwargs

        # NOTE the `storage` library only supports HTTP, but doesn't
        # have the `transport` argument in its signature.
        if self.force_rest and client_library != "storage":
            kwargs["transport"] = "rest"

        class WrappedClient:
            def __getattr__(self, client_type: str):
                return partial(getattr(module, client_type), **kwargs)

        return WrappedClient()

    def build(self, service_name: str, version: str):
        """Return a Google API Client with default values from the factor"""
        return api_client_build(
            service_name, version, cache_discovery=False, **self.kwargs
        )


def get_application_default_credentials(
    logger: BlockLogger,
) -> Tuple[Credentials, Optional[str]]:
    """Get application default credentials, or run `gcloud` to try to log in."""
    try:
        credentials, project = google.auth.default(
            default_scopes="https://www.googleapis.com/auth/cloud-platform"
        )
        # Don't try to refresh credentials if they are from a Service Account Key File
        if isinstance(credentials, service_account.Credentials):
            return credentials, project
        try:
            credentials.refresh(Request())
            return credentials, project
        except RefreshError:
            logger.warning(
                "Reauthentication is needed, running `gcloud auth application-default login`"
            )
    except DefaultCredentialsError:
        logger.warning(
            "Could not automatically determine Google Application Default Credentials, trying to authenticate via GCloud"
        )
    auth_login = subprocess.run(["gcloud", "auth", "application-default", "login"])
    if auth_login.returncode != 0:
        raise RuntimeError("Failed to authenticate via gcloud")

    return google.auth.default()


def get_google_cloud_client_factory(logger: BlockLogger, project_id: str):
    credentials, credentials_project = get_application_default_credentials(logger)
    if credentials_project != project_id:
        logger.warning(
            f"Default credentials are for {credentials_project}, but this cloud is being configured for {project_id}"
        )

    factory = GoogleCloudClientFactory(credentials=credentials)
    return factory


def binding_from_dictionary(
    inp: List[Dict[str, Union[List[str], str]]]
) -> List[Binding]:
    return [Binding(role=b["role"], members=b["members"]) for b in inp]


def check_policy_bindings(
    iam_policy: List[Binding], member: str, possible_roles: Set[str]
) -> bool:
    """Checks if `member` has any role in `possible_roles` given the specified iam_policy."""
    return any(
        policy.role in possible_roles and member in policy.members
        for policy in iam_policy
    )


def check_required_policy_bindings(
    iam_policy: List[Binding], member: str, required_roles: Set[str]
) -> bool:
    """Checks if `member` has all roles in `required_roles` given the specified iam_policy."""
    granted_roles = {policy.role for policy in iam_policy if member in policy.members}
    return required_roles.issubset(granted_roles)


def get_gcp_filestore_config(
    factory: GoogleCloudClientFactory,
    project_id: str,
    vpc_name: str,
    filestore_location: str,
    filestore_instance_id: str,
    logger: BlockLogger,
):
    client = factory.filestore_v1.CloudFilestoreManagerClient()
    instance_name = "projects/{}/locations/{}/instances/{}".format(
        project_id, filestore_location, filestore_instance_id
    )
    try:
        file_store = client.get_instance(name=instance_name)
    except NotFound as e:
        raise ClickException(
            f"Could not find Filestore with id {filestore_instance_id} in project {project_id}. Please validate that you're using the correct GCP project and that the resource values are correct. Error details: {e}"
        )
    root_dir = file_store.file_shares[0].name
    for v in file_store.networks:
        if v.network == vpc_name:
            mount_target_ip = v.ip_addresses[0]
            break
    else:
        logger.error(
            f"Filestore {filestore_instance_id} is not connected to {vpc_name}, but to {file_store.networks}. "
            f"This cannot be edited on an existing Filestore instance. Please recreate the filestore and connect it to {vpc_name}."
        )
        raise ClickException(
            f"Filestore {filestore_instance_id} is not connected to {vpc_name}."
        )
    return GCPFileStoreConfig(
        instance_name=instance_name, root_dir=root_dir, mount_target_ip=mount_target_ip,
    )
