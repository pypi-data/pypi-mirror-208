from typing import Optional, Tuple

from click.exceptions import ClickException

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.cloud import get_cloud_id_and_name


def get_organization_default_cloud(api_client: DefaultApi) -> Optional[str]:
    """Return default cloud name for organization if it exists and
        if user has correct permissions for it.

        Returns:
            Name of default cloud name for organization if it exists and
            if user has correct permissions for it.
        """
    user = api_client.get_user_info_api_v2_userinfo_get().result
    organization = user.organizations[0]  # Each user only has one org
    if organization.default_cloud_id:
        try:
            # Check permissions
            _, cloud_name = get_cloud_id_and_name(
                api_client, cloud_id=organization.default_cloud_id
            )
            return str(cloud_name)
        except Exception:  # noqa: BLE001
            return None
    return None


def get_default_cloud(
    api_client: DefaultApi, cloud_name: Optional[str]
) -> Tuple[str, str]:
    """Returns the cloud id from cloud name.
    If cloud name is not provided, returns the default cloud name if exists in organization.
    If default cloud name does not exist returns last used cloud.
    """

    if cloud_name is None:
        default_cloud_name = get_organization_default_cloud(api_client)
        if default_cloud_name:
            cloud_name = default_cloud_name
    return get_cloud_id_and_name(api_client, cloud_name=cloud_name)


def verify_anyscale_access(
    api_client: DefaultApi, cloud_id: str, logger: BlockLogger
) -> bool:
    try:
        api_client.verify_access_api_v2_cloudsverify_access_cloud_id_get(cloud_id)
        return True
    except ClickException as e:
        logger.error(
            f"Anyscale's control plane is unable to access resources on your cloud provider.\n{e}"
        )
        return False
