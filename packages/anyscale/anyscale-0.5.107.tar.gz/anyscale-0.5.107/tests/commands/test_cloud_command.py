from unittest.mock import Mock, patch

from click.testing import CliRunner
import pytest

from anyscale.client.openapi_client.models import ClusterManagementStackVersions
from anyscale.commands.cloud_commands import setup_cloud


@pytest.mark.parametrize(
    "use_legacy_stack", [True, False],
)
def test_cloud_setup(use_legacy_stack):
    runner = CliRunner()
    mock_cloud_controller = Mock()
    mock_setup_managed_cloud = Mock()
    mock_cloud_controller().setup_managed_cloud = mock_setup_managed_cloud

    provider = "aws"
    region = "us-west-2"
    name = "unit-test-cloud"
    cluster_management_stack_version = (
        ClusterManagementStackVersions.V1
        if use_legacy_stack
        else ClusterManagementStackVersions.V2
    )

    args = ["--provider", provider, "--name", name, "--region", region]

    if use_legacy_stack:
        args.append("--use-legacy-stack")

    with patch(
        "anyscale.commands.cloud_commands.CloudController", new=mock_cloud_controller,
    ):
        runner.invoke(setup_cloud, args=args)

    mock_setup_managed_cloud.assert_called_once_with(
        provider=provider,
        region=region,
        name=name,
        cluster_management_stack_version=cluster_management_stack_version,
    )
