from copy import deepcopy
import json
import os
from typing import Collection, Optional
from unittest.mock import ANY, call, Mock, mock_open, patch

import click
from pydantic import ValidationError
import pytest

from anyscale.client.openapi_client.models.apply_production_service_v2_model import (
    ApplyProductionServiceV2Model,
)
from anyscale.client.openapi_client.models.create_production_service import (
    CreateProductionService,
)
from anyscale.client.openapi_client.models.decoratedlistserviceapimodel_list_response import (
    DecoratedlistserviceapimodelListResponse,
)
from anyscale.client.openapi_client.models.list_response_metadata import (
    ListResponseMetadata,
)
from anyscale.client.openapi_client.models.production_job_config import (
    ProductionJobConfig,
)
from anyscale.controllers.service_controller import ServiceConfig, ServiceController
from anyscale.utils.workload_types import Workload


TEST_SERVICE_ID = "test-service-id"
TEST_SERVICE_NAME = "test-service-name"


def test_service_config_model_with_entrypoint():
    config_dict = {
        "entrypoint": "python test.py",
        "project_id": "test_project_id",
        "build_id": "test_build_id",
        "compute_config_id": "test_compute_config_id",
        "healthcheck_url": "test.url",
    }
    mock_validate_successful_build = Mock()
    with patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        service_config = ServiceConfig.parse_obj(config_dict)
        assert service_config.ray_serve_config is None


def test_service_config_model_with_ray_serve_config():
    runtime_env = {
        "pip": ["requests"],
        "working_dir": "https://github.com/anyscale/docs_examples/archive/refs/heads/main.zip",
    }
    config_dict = {
        "ray_serve_config": {
            "import_path": "serve_hello:entrypoint",
            "runtime_env": runtime_env,
        },
        "project_id": "test_project_id",
        "build_id": "test_build_id",
        "compute_config_id": "test_compute_config_id",
    }
    mock_validate_successful_build = Mock()
    with patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        service_config = ServiceConfig.parse_obj(config_dict)
        assert service_config.entrypoint is None
        assert service_config.runtime_env is None
        assert service_config.ray_serve_config["runtime_env"] == runtime_env


def test_service_config_model_with_ray_serve_config_working_dir():
    runtime_env = {"pip": ["requests"], "working_dir": "."}
    config_dict = {
        "ray_serve_config": {
            "import_path": "serve_hello:entrypoint",
            "runtime_env": runtime_env,
        },
        "project_id": "test_project_id",
        "build_id": "test_build_id",
        "compute_config_id": "test_compute_config_id",
    }
    mock_validate_successful_build = Mock()
    with patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        service_config = ServiceConfig.parse_obj(config_dict)
        assert service_config.entrypoint is None
        assert service_config.ray_serve_config["runtime_env"] == runtime_env
        assert service_config.ray_gcs_external_storage_config is None


def test_service_config_model_with_ray_gcs_external_storage_config():
    config_dict = {
        "ray_serve_config": {"runtime_env": {"pip": ["requests"], "working_dir": "."}},
        "project_id": "test_project_id",
        "build_id": "test_build_id",
        "compute_config_id": "test_compute_config_id",
        "ray_gcs_external_storage_config": {"address": "addr:port",},
    }
    mock_validate_successful_build = Mock()
    with patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        service_config = ServiceConfig.parse_obj(config_dict)
        assert (
            service_config.ray_gcs_external_storage_config
            == config_dict["ray_gcs_external_storage_config"]
        )
        assert service_config.runtime_env is None


@pytest.mark.parametrize("use_default_project", [True, False])
@pytest.mark.parametrize("access", ["public", "private"])
@pytest.mark.parametrize("maximum_uptime_minutes", [60, None])
def test_update_service(
    mock_auth_api_client,
    use_default_project: bool,
    access: str,
    maximum_uptime_minutes: Optional[int],
) -> None:
    config_dict = {
        "entrypoint": "mock_entrypoint",
        "build_id": "mock_build_id",
        "compute_config_id": "mock_compute_config_id",
        "healthcheck_url": "mock_healthcheck_url",
        "access": access,
    }
    mock_logger = Mock()
    service_controller = ServiceController(log=mock_logger)
    if use_default_project:
        mock_infer_project_id = Mock(return_value="mock_default_project_id")
    else:
        mock_infer_project_id = Mock(return_value="mock_project_id")

    mock_validate_successful_build = Mock()

    mock_override_runtime_env_config = Mock(return_value=None)

    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple(
        "anyscale.controllers.service_controller",
        infer_project_id=mock_infer_project_id,
        override_runtime_env_config=mock_override_runtime_env_config,
    ), patch.object(
        ServiceController,
        "_get_maximum_uptime_minutes",
        return_value=maximum_uptime_minutes,
    ), patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ), patch.multiple(
        "os.path", exists=Mock(return_value=True)
    ):
        service_controller.deploy(
            "mock_config_file", name="mock_name", description="mock_description",
        )

    service_controller.api_client.apply_service_api_v2_decorated_ha_jobs_apply_service_put.assert_called_once_with(
        CreateProductionService(
            name="mock_name",
            description="mock_description",
            project_id="mock_default_project_id"
            if use_default_project
            else "mock_project_id",
            config=ProductionJobConfig(  # noqa: PIE804
                **{
                    "entrypoint": "mock_entrypoint",
                    "build_id": "mock_build_id",
                    "compute_config_id": "mock_compute_config_id",
                }
            ),
            healthcheck_url="mock_healthcheck_url",
            access=access,
        )
    )
    assert mock_logger.info.call_count == 4


def test_generate_config_from_entrypoint(mock_auth_api_client):
    mock_logger = Mock()
    service_controller = ServiceController(log=mock_logger)
    entrypoint = ["python", "test.py"]
    name = "test_name"
    description = "test_description"

    test_compute_config_id = "mock_compute_config_id"
    test_build_id = "mock_build_id"

    mock_get_default_cluster_compute = Mock(
        return_value=Mock(id=test_compute_config_id)
    )
    mock_validate_successful_build = Mock()
    mock_get_default_cluster_env_build = Mock(return_value=Mock(id=test_build_id))
    with patch.multiple(
        "anyscale.controllers.job_controller",
        get_default_cluster_compute=mock_get_default_cluster_compute,
        validate_successful_build=mock_validate_successful_build,
        get_default_cluster_env_build=mock_get_default_cluster_env_build,
    ):
        job_config = service_controller.generate_config_from_entrypoint(
            entrypoint, name, description
        )

    assert job_config.entrypoint == "python test.py"
    assert job_config.name == name
    assert job_config.description == description


@pytest.mark.parametrize(
    ("ray_serve_config", "runtime_env"),
    [
        [{"runtime_env": {"pip": ["requests"], "working_dir": "."}}, None],
        [None, {"pip": ["requests"]}],
    ],
)
def test_generate_config_from_file(
    mock_auth_api_client, ray_serve_config: Optional[str], runtime_env: Optional[str]
):
    """
    This test checks that the config file for Service v1 and v2
    can be properly parsed.
    """
    service_controller = ServiceController()

    name = "test_service_name"
    description = "mock_description"
    build_id = "test_build_id"
    compute_config_id = "test_compute_config_id"
    project_id = "test_project_id"
    rollout_strategy = "ROLLOUT"
    canary_percent = 100
    config_dict = {
        "name": name,
        "description": description,
        "ray_serve_config": ray_serve_config,
        "entrypoint": "python test.py" if runtime_env else None,
        "healthcheck_url": "test.com" if runtime_env else None,
        "runtime_env": runtime_env,
        "project_id": project_id,
        "build_id": build_id,
        "compute_config_id": compute_config_id,
        "version": "test_abc",
        "canary_percent": canary_percent,
        "rollout_strategy": rollout_strategy,
    }
    mock_validate_successful_build = Mock()
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        config = service_controller.generate_config_from_file(
            "test_ser8vice_config_file",
        )

        expected_service_config = ServiceConfig(
            name=name,
            description=description,
            ray_serve_config=ray_serve_config,
            entrypoint="python test.py" if runtime_env else None,
            runtime_env=runtime_env,
            healthcheck_url="test.com" if runtime_env else None,
            project_id=project_id,
            build_id=build_id,
            compute_config_id=compute_config_id,
            version="test_abc",
            canary_percent=canary_percent,
            rollout_strategy=rollout_strategy,
        )
    assert config == expected_service_config


@pytest.mark.parametrize("add_extra_field", [True, False])
def test_config_validation(add_extra_field, mock_auth_api_client):
    """
    This test checks that an error is thrown if extra/mispelled fields
    are added into the config file
    """
    service_controller = ServiceController()

    name = "test_service_name"
    description = "mock_description"
    build_id = "test_build_id"
    compute_config_id = "test_compute_config_id"
    project_id = "test_project_id"
    rollout_strategy = "ROLLOUT"
    extra_field_value = "*****"
    canary_percent = 100
    config_dict = {
        "name": name,
        "description": description,
        "ray_serve_config": {},
        "entrypoint": "python test.py",
        "healthcheck_url": "test.com",
        "runtime_env": {},
        "project_id": project_id,
        "build_id": build_id,
        "compute_config_id": compute_config_id,
        "version": "test_abc",
        "canary_percent": canary_percent,
        "rollout_strategy": rollout_strategy,
    }

    if add_extra_field:
        extra_field_value = "*****"
        config_dict["extra_field"] = extra_field_value

    mock_validate_successful_build = Mock()
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        if add_extra_field:
            with pytest.raises(ValidationError):
                service_controller.generate_config_from_file(
                    "test_service_config_file", name=name, description=description,
                )
        else:
            service_controller.generate_config_from_file(
                "test_service_config_file", name=name, description=description,
            )


@pytest.mark.parametrize(
    ("working_dir"),
    [
        ("https://github.com/anyscale/docs_examples/archive/refs/heads/main.zip"),
        ("s3://already-a-uri/path"),
    ],
)
def test_generate_config_from_file_inside_workspace_no_working_dir_override(
    mock_auth_api_client, working_dir: str,
):
    """
    This test checks that if the service v2 is launched from the workspace with
    a remote working dir being specified, the method would inspect the remote url
    and not override it.
    """
    service_controller = ServiceController()

    name = "test_service_name"
    description = "mock_description"
    ray_serve_config = {
        "runtime_env": {"pip": ["requests"], "working_dir": working_dir,}
    }
    build_id = "test_build_id"
    compute_config_id = "test_compute_config_id"
    project_id = "test_project_id"
    rollout_strategy = "ROLLOUT"
    canary_percent = 100
    config_dict = {
        "name": name,
        "description": description,
        "ray_serve_config": ray_serve_config,
        "project_id": project_id,
        "build_id": build_id,
        "compute_config_id": compute_config_id,
        "version": "test_abc",
        "canary_percent": canary_percent,
        "rollout_strategy": rollout_strategy,
    }
    mock_validate_successful_build = Mock()

    workspace_id = "Test_workspace_id"
    with patch.dict(
        os.environ,
        {
            "ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": workspace_id,
            "ANYSCALE_SESSION_ID": "test_session_id",
        },
    ), patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple(
        "os.path", exists=Mock(return_value=True)
    ), patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        config = service_controller.generate_config_from_file(
            "test_service_config_file",
        )

        expected_service_config = ServiceConfig(
            name=name,
            description=description,
            ray_serve_config=ray_serve_config,
            project_id=project_id,
            build_id=build_id,
            compute_config_id=compute_config_id,
            version="test_abc",
            canary_percent=canary_percent,
            rollout_strategy=rollout_strategy,
        )

    assert config == expected_service_config


def test_service_submit_parse_logic(mock_auth_api_client) -> None:
    service_controller = ServiceController()
    service_controller.generate_config_from_entrypoint = Mock()  # type: ignore
    service_controller.generate_config_from_file = Mock()  # type: ignore
    service_controller.deploy_from_config = Mock()  # type: ignore

    # We are not in a workspace, so entrypoint should not be allowed
    with pytest.raises(click.ClickException):
        service_controller.deploy(
            "file", None, None, entrypoint=["entrypoint"], is_entrypoint_cmd=False
        )

    with pytest.raises(click.ClickException):
        service_controller.deploy(
            "file", None, None, entrypoint=["entrypoint"], is_entrypoint_cmd=True
        )

    with pytest.raises(click.ClickException):
        service_controller.deploy(
            "file",
            None,
            None,
            entrypoint=["entrypoint", "commands"],
            is_entrypoint_cmd=True,
        )

    # Simulate a workspace
    with patch.dict(
        os.environ, {"ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": "fake_workspace_id"}
    ), patch.multiple(
        "anyscale.controllers.service_controller",
        override_runtime_env_config=Mock(return_value={"rewritten": True}),
    ):
        # Fails due to is_entrypoint_cmd being False
        with pytest.raises(click.ClickException):
            service_controller.deploy(
                "file",
                name=None,
                description=None,
                entrypoint=["entrypoint"],
                is_entrypoint_cmd=False,
            )

        mock_config = Mock()
        service_controller.generate_config_from_file.return_value = mock_config
        service_controller.deploy(
            "file", name=None, description=None, entrypoint=[], is_entrypoint_cmd=False
        )
        service_controller.generate_config_from_file.assert_called_once_with(
            "file", name=None, description=None, healthcheck_url=None
        )
        service_controller.deploy_from_config.assert_called_once_with(mock_config)
        service_controller.generate_config_from_file.reset_mock()
        service_controller.deploy_from_config.reset_mock()

        mock_config = Mock()
        service_controller.generate_config_from_entrypoint.return_value = mock_config
        service_controller.deploy(
            "file",
            name=None,
            description=None,
            entrypoint=["entrypoint"],
            is_entrypoint_cmd=True,
        )
        service_controller.generate_config_from_entrypoint.assert_called_once_with(
            ["file", "entrypoint"], name=None, description=None, healthcheck_url=None
        )
        service_controller.deploy_from_config.assert_called_once_with(mock_config)


@pytest.mark.parametrize("override_name", [None, "override_service_name"])
@pytest.mark.parametrize("override_version", [None, "override_version"])
@pytest.mark.parametrize(
    ("override_canary_percent", "first_get_ha_job_throws_error"),
    [[None, False], [0, False], [0, True], [40, False], [40, True]],
)
@pytest.mark.parametrize("override_rollout_strategy", [None, "IN_PLACE"])
def test_service_rollout(
    mock_auth_api_client,
    override_name: Optional[str],
    override_version: Optional[str],
    override_canary_percent: Optional[int],
    first_get_ha_job_throws_error: bool,
    override_rollout_strategy: Optional[str],
) -> None:
    """
    This tests that when we submit a Service config with ray_serve_config,
    we submit both the Service v1 and Service v2 configs.
    Please reference services_internal_api_models.py for more details.
    """
    service_controller = ServiceController()
    service_controller.api_client.apply_service_v2_api_v2_services_v2_apply_put = Mock(
        return_value=Mock(
            result=(
                Mock(
                    versions=[
                        Mock(),
                        Mock(production_job_ids=["test_production_job_id"]),
                    ]
                )
            )
        )
    )
    if first_get_ha_job_throws_error:
        service_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get = Mock(
            side_effect=[Exception("Error!"), Mock()]
        )

    name = "test_service_name"
    description = "mock_description"
    ray_serve_config = {"runtime_env": {"pip": ["requests"], "working_dir": "."}}
    build_id = "test_build_id"
    compute_config_id = "test_compute_config_id"
    project_id = "test_project_id"
    rollout_strategy = "ROLLOUT"

    config_dict = {
        "name": name,
        "description": description,
        "ray_serve_config": ray_serve_config,
        "project_id": project_id,
        "build_id": build_id,
        "compute_config_id": compute_config_id,
        "version": "test_abc",
        "canary_percent": 100,
        "rollout_strategy": rollout_strategy,
    }
    mock_validate_successful_build = Mock()
    mock_override_runtime_env_config = Mock(
        return_value={"pip": ["requests"], "working_dir": "."}
    )
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ), patch.multiple(
        "anyscale.controllers.service_controller",
        override_runtime_env_config=mock_override_runtime_env_config,
    ):
        service_controller.rollout(
            "test_ser8vice_config_file",
            name=override_name,
            version=override_version,
            canary_percent=override_canary_percent,
            rollout_strategy=override_rollout_strategy,
        )

    service_v2_config = ApplyProductionServiceV2Model(
        name=override_name if override_name else name,
        description=description,
        build_id=build_id,
        compute_config_id=compute_config_id,
        project_id=project_id,
        ray_serve_config=ray_serve_config,
        version=override_version if override_version else "test_abc",
        canary_percent=override_canary_percent
        if override_canary_percent is not None
        else 100,
        rollout_strategy=override_rollout_strategy
        if override_rollout_strategy
        else "ROLLOUT",
    )

    service_controller.api_client.apply_service_v2_api_v2_services_v2_apply_put.assert_called_once_with(
        service_v2_config
    )


class TestGetServiceID:
    def test_invalid_inputs(self, mock_auth_api_client):
        service_controller = ServiceController()

        with pytest.raises(
            click.ClickException,
            match="Service ID, name, or config file must be specified.",
        ):
            service_controller.get_service_id()

        with pytest.raises(click.ClickException, match="Only one of"):
            service_controller.get_service_id(
                service_id="test-id", service_name="test-name"
            )

        with pytest.raises(click.ClickException, match="Only one of"):
            service_controller.get_service_id(
                service_id="test-id",
                service_config_file="test-config-file-path",
                project_id=None,
            )

        with pytest.raises(click.ClickException, match="Only one of"):
            service_controller.get_service_id(
                service_id="test-id",
                service_name="test-name",
                service_config_file="test-config-file-path",
            )

        with pytest.raises(click.ClickException, match="Only one of"):
            service_controller.get_service_id(
                service_name="test-name", service_config_file="test-config-file-path"
            )

        with pytest.raises(click.ClickException, match="not found"):
            service_controller.get_service_id(
                service_config_file="/fake/service/config/path"
            )

    def test_service_id_provided(self, mock_auth_api_client):
        """If the ID is provided, the same ID should always be returned and no API calls made."""
        service_controller = ServiceController()

        assert service_controller.get_service_id(service_id="test-id") == "test-id"
        service_controller.api_client.list_services_api_v2_services_v2_get.assert_not_called()

    def test_name_provided_no_matching_service(self, mock_auth_api_client):
        """If a name is provided but no services match it, an exception should be raised."""
        service_controller = ServiceController()

        service_controller.api_client.list_services_api_v2_services_v2_get.return_value = DecoratedlistserviceapimodelListResponse(
            results=[], metadata=Mock(next_paging_token=None),
        )

        with pytest.raises(
            click.ClickException,
            match=f"No service with name '{TEST_SERVICE_NAME}' was found",
        ):
            service_controller.get_service_id(service_name=TEST_SERVICE_NAME)

        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            count=10, creator_id=None, name=TEST_SERVICE_NAME, project_id=None,
        )
        service_controller.api_client.list_services_api_v2_services_v2_get.reset_mock()

        # Test the config file codepath.
        mock_service_config = Mock()
        mock_service_config.configure_mock(name=TEST_SERVICE_NAME, project_id=None)
        service_controller._read_service_config_file = Mock(
            return_value=mock_service_config,
        )

        with pytest.raises(
            click.ClickException,
            match=f"No service with name '{TEST_SERVICE_NAME}' was found",
        ):
            service_controller.get_service_id(service_config_file="test-config-file")

        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            count=10, creator_id=None, name=TEST_SERVICE_NAME, project_id=None,
        )

    def test_name_provided_single_matching_service(self, mock_auth_api_client):
        """If a name is provided and one service matches it, its ID should be returned."""
        service_controller = ServiceController()

        service_controller.api_client.list_services_api_v2_services_v2_get.return_value = DecoratedlistserviceapimodelListResponse(
            results=[Mock(id=TEST_SERVICE_ID)], metadata=Mock(next_paging_token=None),
        )

        assert (
            service_controller.get_service_id(service_name=TEST_SERVICE_NAME)
            == TEST_SERVICE_ID
        )
        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            count=10, creator_id=None, name=TEST_SERVICE_NAME, project_id=None,
        )
        service_controller.api_client.list_services_api_v2_services_v2_get.reset_mock()

        # Test the config file codepath.
        mock_service_config = Mock()
        mock_service_config.configure_mock(name=TEST_SERVICE_NAME, project_id=None)
        service_controller._read_service_config_file = Mock(
            return_value=mock_service_config,
        )
        assert (
            service_controller.get_service_id(service_config_file="test-config-file")
            == TEST_SERVICE_ID
        )
        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            count=10, creator_id=None, name=TEST_SERVICE_NAME, project_id=None,
        )

    def test_name_provided_multiple_matching_services(self, mock_auth_api_client):
        """If a name is provided and multiple services match it, an exception should be raised."""
        service_controller = ServiceController()

        service_controller.api_client.list_services_api_v2_services_v2_get.return_value = DecoratedlistserviceapimodelListResponse(
            results=[Mock(id="test-service-id-1"), Mock(id="test-service-id-2")],
            metadata=Mock(next_paging_token=None),
        )

        with pytest.raises(
            click.ClickException,
            match=f"There are multiple services with name '{TEST_SERVICE_NAME}'.",
        ):
            service_controller.get_service_id(service_name=TEST_SERVICE_NAME)

        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            count=10, creator_id=None, name=TEST_SERVICE_NAME, project_id=None,
        )
        service_controller.api_client.list_services_api_v2_services_v2_get.reset_mock()

        mock_service_config = Mock()
        mock_service_config.configure_mock(name=TEST_SERVICE_NAME, project_id=None)
        service_controller._read_service_config_file = Mock(
            return_value=mock_service_config,
        )

        with pytest.raises(
            click.ClickException,
            match=f"There are multiple services with name '{TEST_SERVICE_NAME}'.",
        ):
            service_controller.get_service_id(service_config_file="test-config-file")

        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            count=10, creator_id=None, name=TEST_SERVICE_NAME, project_id=None,
        )

    def test_no_project_id(self, mock_auth_api_client):
        """If there is no project_id, the results should not be filtered based on project."""
        service_controller = ServiceController()

        service_controller.api_client.list_services_api_v2_services_v2_get.return_value = DecoratedlistserviceapimodelListResponse(
            results=[Mock(id=TEST_SERVICE_ID)], metadata=Mock(next_paging_token=None),
        )

        mock_infer_project_id = Mock(return_value="mock_default_project_id")
        with patch.multiple(
            "anyscale.controllers.service_controller",
            infer_project_id=mock_infer_project_id,
        ):
            assert (
                service_controller.get_service_id(service_name=TEST_SERVICE_NAME)
                == TEST_SERVICE_ID
            )
            service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
                count=10, creator_id=None, name=TEST_SERVICE_NAME, project_id=None,
            )

    def test_project_id_in_service_config(self, mock_auth_api_client):
        """If the project_id is passed in the service config it should be used as a filter."""
        service_controller = ServiceController()

        service_controller.api_client.list_services_api_v2_services_v2_get.return_value = DecoratedlistserviceapimodelListResponse(
            results=[Mock(id=TEST_SERVICE_ID)], metadata=Mock(next_paging_token=None),
        )

        mock_service_config = Mock()
        mock_service_config.configure_mock(
            name=TEST_SERVICE_NAME, project_id="test-project-id"
        )
        service_controller._read_service_config_file = Mock(
            return_value=mock_service_config,
        )

        mock_infer_project_id = Mock(return_value="mock_default_project_id")
        with patch.multiple(
            "anyscale.controllers.service_controller",
            infer_project_id=mock_infer_project_id,
        ):
            assert (
                service_controller.get_service_id(
                    service_config_file="test-config-file"
                )
                == TEST_SERVICE_ID
            )
            service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
                count=10,
                creator_id=None,
                name=TEST_SERVICE_NAME,
                project_id="test-project-id",
            )

    def test_override_project_id(self, mock_auth_api_client):
        """If the project_id is passed directly, the passed value should be used to filter."""
        service_controller = ServiceController()

        service_controller.api_client.list_services_api_v2_services_v2_get.return_value = DecoratedlistserviceapimodelListResponse(
            results=[Mock(id=TEST_SERVICE_ID)], metadata=Mock(next_paging_token=None),
        )

        # Test overriding when getting service ID by name.
        assert (
            service_controller.get_service_id(
                service_name=TEST_SERVICE_NAME, project_id="overridden-project-id"
            )
            == TEST_SERVICE_ID
        )
        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            count=10,
            creator_id=None,
            name=TEST_SERVICE_NAME,
            project_id="overridden-project-id",
        )
        service_controller.api_client.list_services_api_v2_services_v2_get.reset_mock()

        # Test overriding when getting service ID by config file.
        mock_service_config = Mock()
        mock_service_config.configure_mock(
            name=TEST_SERVICE_NAME, project_id="test-project-id"
        )
        service_controller._read_service_config_file = Mock(
            return_value=mock_service_config,
        )

        mock_infer_project_id = Mock(return_value="mock_default_project_id")
        with patch.multiple(
            "anyscale.controllers.service_controller",
            infer_project_id=mock_infer_project_id,
        ):
            assert (
                service_controller.get_service_id(
                    service_config_file="test-config-file",
                    project_id="overridden-project-id",
                )
                == TEST_SERVICE_ID
            )

        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            count=10,
            creator_id=None,
            name=TEST_SERVICE_NAME,
            project_id="overridden-project-id",
        )


def test_terminate_service(mock_auth_api_client):
    """Test that v2 IDs go through v2 API, v1 through v1."""
    service_controller = ServiceController()

    service_controller.terminate("service2_abc123")
    service_controller.api_client.terminate_service_api_v2_services_v2_service_id_terminate_post.assert_called_once_with(
        "service2_abc123",
    )

    service_controller.job_controller._resolve_job_object = Mock(
        return_value=Mock(id="service_abc123"),
    )
    service_controller.terminate("service_abc123")
    service_controller.api_client.terminate_job_api_v2_decorated_ha_jobs_production_job_id_terminate_post.assert_called_once_with(
        "service_abc123",
    )


class TestListServices:
    def test_list_service_v1_with_id(self, mock_auth_api_client):
        service_controller = ServiceController()
        service_controller.list(service_id="service_v1_id")

        service_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get.assert_called_once_with(
            "service_v1_id",
        )

    def test_list_service_v2_with_id(self, mock_auth_api_client):
        service_controller = ServiceController()
        service_controller.list(service_id="service2_id")

        service_controller.api_client.get_service_api_v2_services_v2_service_id_get.assert_called_once_with(
            "service2_id",
        )

    def test_list_service_unexpected_error(self, mock_auth_api_client):
        service_controller = ServiceController()
        service_controller.list(service_id="service2_id")

        service_controller.api_client.list_services_api_v2_services_v2_get.side_effect = Exception(
            "Request failed! Unexpected exception!"
        )

        service_controller.list()

        service_controller.job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_not_called()

    def test_list_service_error_fallback(self, mock_auth_api_client):
        """
        We fallback to list Services v1 if the execption indicates that the
        FF is turned off for the user.
        """
        service_controller = ServiceController()
        service_controller.list(service_id="service2_id")

        service_controller.api_client.list_services_api_v2_services_v2_get.side_effect = Exception(
            "Services v2 is not enabled for your organization."
        )
        service_controller.job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.return_value = DecoratedlistserviceapimodelListResponse(
            results=[], metadata=Mock(next_paging_token=None),
        )

        service_controller.list()

        service_controller.job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_called_once_with(
            creator_id=None,
            name=None,
            project_id=None,
            type_filter="SERVICE",
            archive_status="NOT_ARCHIVED",
            count=10,
        )

    @pytest.mark.parametrize("name", [None, "service_name"])
    @pytest.mark.parametrize("project_id", [None, "test_project_id"])
    @pytest.mark.parametrize("created_by_me", [True, False])
    def test_list_service(
        self,
        mock_auth_api_client,
        name: Optional[str],
        project_id: Optional[str],
        created_by_me: bool,
    ):
        service_controller = ServiceController()
        service_controller.api_client.list_services_api_v2_services_v2_get.return_value = DecoratedlistserviceapimodelListResponse(
            results=[], metadata=Mock(next_paging_token=None),
        )
        if created_by_me:
            creator_id = "test_user_id"
            service_controller.api_client.get_user_info_api_v2_userinfo_get.return_value = Mock(
                result=Mock(id=creator_id)
            )
        else:
            creator_id = None

        service_controller.list(
            name=name, project_id=project_id, created_by_me=created_by_me
        )

        service_controller.api_client.list_services_api_v2_services_v2_get.assert_called_once_with(
            creator_id=creator_id, name=name, project_id=project_id, count=10,
        )

    def test_list_service_with_pagination(
        self, mock_auth_api_client,
    ):
        service_controller = ServiceController()

        next_paging_token = "test"
        list_return_values = [
            DecoratedlistserviceapimodelListResponse(
                results=[],
                metadata=ListResponseMetadata(
                    total=11, next_paging_token=next_paging_token
                ),
            ),
            DecoratedlistserviceapimodelListResponse(
                results=[],
                metadata=ListResponseMetadata(total=11, next_paging_token=None),
            ),
        ]
        service_controller.api_client.list_services_api_v2_services_v2_get.side_effect = (
            list_return_values
        )

        service_controller.list()

        calls = [
            call(creator_id=None, name=None, project_id=None, count=10),
            call(
                creator_id=None,
                name=None,
                project_id=None,
                count=10,
                paging_token=next_paging_token,
            ),
        ]
        service_controller.api_client.list_services_api_v2_services_v2_get.assert_has_calls(
            calls
        )


def test_rollback(mock_auth_api_client):
    """Test that v2 IDs go through v2 API, v1 is rejected."""
    service_controller = ServiceController()

    service_controller.rollback("service2_abc123")
    service_controller.api_client.rollback_service_api_v2_services_v2_service_id_rollback_post.assert_called_once_with(
        "service2_abc123",
    )

    with pytest.raises(
        click.ClickException, match="rollback is only supported for v2 services"
    ):
        service_controller.rollback("service_abc123")


def test_archive(mock_auth_api_client):
    """Test that v1 IDs go through v1 API, v2 is rejected."""
    service_controller = ServiceController()

    with pytest.raises(
        click.ClickException, match="archive is not currently supported for v2 services"
    ):
        service_controller.archive("service2_abc123")

    service_controller.job_controller._resolve_job_object = Mock(
        return_value=Mock(id="service_abc123"),
    )
    service_controller.archive("service_abc123")
    service_controller.api_client.archive_job_api_v2_decorated_ha_jobs_production_job_id_archive_post.assert_called_once_with(
        "service_abc123",
    )


@pytest.mark.parametrize("is_v2_stack", [True, False])
@pytest.mark.parametrize("init_runtime_env", [None, {}, {"working_dir": "."}])
def test_override_runtime_env_config_and_infer_project_id_v1(
    mock_auth_api_client, is_v2_stack: bool, init_runtime_env: Collection[str],
):
    """Test helper functions in deploy_from_config function (service v1 path)
    Test that runtime_env is overwrriten from override_runtime_env_config
    Test the project_id is autopopulated from infer_project_id
    If using deploy in v1 stack:
        - Runtime_env should be added directly into ProductionJobConfig
    If using deploy in v2 stacK:
        - Runtime_env should be added into ray_serve_config
    """
    if is_v2_stack:
        config_dict = {
            "name": "mock_name",
            "description": "mock_description",
            "build_id": "mock_build_id",
            "compute_config_id": "mock_compute_config_id",
            "ray_serve_config": {
                "import_path": "mock_import_path",
                "runtime_env": init_runtime_env,
            },
        }

    else:
        config_dict = {
            "name": "mock_name",
            "entrypoint": "mock_entrypoint",
            "description": "mock_description",
            "build_id": "mock_build_id",
            "compute_config_id": "mock_compute_config_id",
            "healthcheck_url": "mock_healthcheck_url",
            "runtime_env": init_runtime_env,
        }

    assert "project_id" not in config_dict

    mock_project_id = "default"

    with patch.multiple(
        "anyscale.controllers.job_controller", validate_successful_build=Mock(),
    ):
        service_config = ServiceConfig.parse_obj(config_dict)

    new_runtime_env = {"working_dir": "s3://bucket"}
    mock_override_config = Mock(return_value=new_runtime_env)

    mock_infer_project_id = Mock(return_value=mock_project_id)

    with patch.multiple(
        "anyscale.controllers.service_controller",
        infer_project_id=mock_infer_project_id,
        override_runtime_env_config=mock_override_config,
    ), patch.object(
        ServiceController, "_get_maximum_uptime_output", Mock()
    ), patch.object(
        ServiceController, "_get_additional_log_if_maximum_uptime_enabled", Mock()
    ):

        service_controller = ServiceController()
        service_controller.api_client = Mock()
        service_controller.anyscale_api_client = Mock()
        service_controller.log = Mock()
        service_controller.api_client.apply_service_api_v2_decorated_ha_jobs_apply_service_put = (
            Mock()
        )

        service_controller.deploy_from_config(service_config)

        mock_override_config.assert_called_once_with(
            anyscale_api_client=service_controller.anyscale_api_client,
            api_client=service_controller.api_client,
            compute_config_id=config_dict["compute_config_id"],
            runtime_env=init_runtime_env,
            workload_type=Workload.SERVICES,
            log=service_controller.log,
        )

        if is_v2_stack:
            expected_ray_serve_config = {
                "import_path": "mock_import_path",
                "runtime_env": new_runtime_env,
            }
            service_controller.api_client.apply_service_api_v2_decorated_ha_jobs_apply_service_put.assert_called_once_with(
                CreateProductionService(
                    name=config_dict["name"],
                    description=config_dict["description"],
                    project_id=mock_project_id,
                    config=ProductionJobConfig(
                        entrypoint=None,
                        ray_serve_config=expected_ray_serve_config,
                        build_id=service_config.build_id,
                        compute_config_id=service_config.compute_config_id,
                        max_retries=service_config.max_retries,
                    ),
                    access="public",
                )
            )
        else:

            service_controller.api_client.apply_service_api_v2_decorated_ha_jobs_apply_service_put.assert_called_once_with(
                CreateProductionService(
                    name=config_dict["name"],
                    description=config_dict["description"],
                    project_id=mock_project_id,
                    config=ProductionJobConfig(
                        entrypoint=service_config.entrypoint,
                        runtime_env=new_runtime_env,
                        build_id=service_config.build_id,
                        compute_config_id=service_config.compute_config_id,
                        max_retries=service_config.max_retries,
                    ),
                    healthcheck_url=service_config.healthcheck_url,
                    access="public",
                )
            )


@pytest.mark.parametrize("init_runtime_env", [None, {}, {"working_dir": "."}])
def test_override_runtime_env_config_and_infer_project_id_v2(
    mock_auth_api_client, init_runtime_env: Collection[str],
):
    """Test helper functions in rollout function (service v2 path)
    Test that runtime_env is overwrriten from override_runtime_env_config
    Test the project_id is autopopulated from infer_project_id
    """
    config_dict = {
        "name": "mock_name",
        "description": "mock_description",
        "build_id": "mock_build_id",
        "compute_config_id": "mock_compute_config_id",
        "ray_serve_config": {
            "import_path": "mock_import_path",
            "runtime_env": init_runtime_env,
        },
    }

    assert "project_id" not in config_dict

    mock_project_id = "default"

    with patch.multiple(
        "anyscale.controllers.job_controller", validate_successful_build=Mock(),
    ):
        service_config = ServiceConfig.parse_obj(config_dict)

    new_runtime_env = {"working_dir": "s3://bucket"}
    mock_override_config = Mock(return_value=new_runtime_env)

    mock_infer_project_id = Mock(return_value=mock_project_id)

    mock_generate_config_from_file = Mock(return_value=service_config)

    with patch.multiple(
        "anyscale.controllers.service_controller",
        infer_project_id=mock_infer_project_id,
        override_runtime_env_config=mock_override_config,
    ), patch.object(
        ServiceController, "generate_config_from_file", mock_generate_config_from_file
    ):
        service_controller = ServiceController()
        service_controller.api_client = Mock()
        service_controller.anyscale_api_client = Mock()
        service_controller.log = Mock()
        service_controller.api_client.apply_service_v2_api_v2_services_v2_apply_put = (
            Mock()
        )

        service_controller.rollout(service_config)

        mock_override_config.assert_called_once_with(
            anyscale_api_client=service_controller.anyscale_api_client,
            api_client=service_controller.api_client,
            compute_config_id=config_dict["compute_config_id"],
            runtime_env=init_runtime_env,
            workload_type=Workload.SERVICES,
            log=service_controller.log,
        )

        expected_ray_serve_config = {
            "import_path": "mock_import_path",
            "runtime_env": new_runtime_env,
        }

        service_controller.api_client.apply_service_v2_api_v2_services_v2_apply_put.assert_called_once_with(
            ApplyProductionServiceV2Model(
                name=config_dict["name"],
                description=config_dict["description"],
                project_id=mock_project_id,
                canary_percent=None,
                ray_serve_config=expected_ray_serve_config,
                build_id=config_dict["build_id"],
                compute_config_id=service_config.compute_config_id,
                rollout_strategy=service_config.rollout_strategy,
            )
        )


def test_overwrite_runtime_env_in_v2_ray_serve_config(mock_auth_api_client):
    """Test that runtime env is overwritten in v2 single-app configs as expected.
    Delegates the runtime env overwriting logic to override_runtime_env_config(), simply
    makes sure that override_runtime_env_config is called with the correct arguments.
    """
    service_controller = ServiceController()

    # Runtime environments
    original_runtime_env = {
        "pip": ["requests"],
        "working_dir": ".",
        "upload_path": "s3://already-a-uri/path",
    }
    rewritten_runtime_env = {
        "pip": ["requests"],
        "working_dir": "s3://bucket",
    }

    # Service configs
    with patch.multiple(
        "anyscale.controllers.job_controller", validate_successful_build=Mock(),
    ):
        service_config = ServiceConfig.parse_obj(
            {
                "name": "mock_name",
                "description": "mock_description",
                "build_id": "mock_build_id",
                "compute_config_id": "mock_compute_config_id",
                "ray_serve_config": {
                    "import_path": "a.b.c",
                    "runtime_env": original_runtime_env,
                },
            }
        )
        expected_service_config = deepcopy(service_config)
        expected_service_config.ray_serve_config["runtime_env"] = rewritten_runtime_env

    # Perform test
    override_runtime_env_config_mock = Mock(return_value=rewritten_runtime_env)
    with patch.multiple(
        "anyscale.controllers.service_controller",
        override_runtime_env_config=override_runtime_env_config_mock,
    ):
        service_controller._overwrite_runtime_env_in_v2_ray_serve_config(service_config)

    calls = [
        call(
            runtime_env=original_runtime_env,
            anyscale_api_client=ANY,
            api_client=ANY,
            workload_type=Workload.SERVICES,
            compute_config_id="mock_compute_config_id",
            log=ANY,
        )
    ]
    assert service_config == expected_service_config
    override_runtime_env_config_mock.assert_has_calls(calls)


def test_overwrite_runtime_env_in_v2_ray_serve_config_multi_app(mock_auth_api_client):
    """Test that runtime env for each app is overwritten in v2 multi-app configs.
    Delegates the runtime env overwriting logic to override_runtime_env_config(), simply
    makes sure that override_runtime_env_config is called with the correct arguments.
    """
    service_controller = ServiceController()

    # Runtime environments
    original_runtime_env1 = {
        "pip": ["requests"],
        "working_dir": ".",
        "upload_path": "s3://already-a-uri/path",
    }
    original_runtime_env2 = None
    rewritten_runtime_env = {
        "pip": ["requests"],
        "working_dir": "s3://bucket",
    }

    # Service configs
    with patch.multiple(
        "anyscale.controllers.job_controller", validate_successful_build=Mock(),
    ):
        service_config = ServiceConfig.parse_obj(
            {
                "name": "mock_name",
                "description": "mock_description",
                "build_id": "mock_build_id",
                "compute_config_id": "mock_compute_config_id",
                "ray_serve_config": {
                    "applications": [
                        {"import_path": "a.b", "runtime_env": original_runtime_env1},
                        {"import_path": "c.d"},
                    ]
                },
            }
        )
        expected_service_config = deepcopy(service_config)
        for app in expected_service_config.ray_serve_config["applications"]:
            app["runtime_env"] = rewritten_runtime_env

    # Perform test
    override_runtime_env_config_mock = Mock(return_value=rewritten_runtime_env)
    with patch.multiple(
        "anyscale.controllers.service_controller",
        override_runtime_env_config=override_runtime_env_config_mock,
    ):
        service_controller._overwrite_runtime_env_in_v2_ray_serve_config(service_config)

    calls = [
        call(
            runtime_env=original_runtime_env1,
            anyscale_api_client=ANY,
            api_client=ANY,
            workload_type=Workload.SERVICES,
            compute_config_id="mock_compute_config_id",
            log=ANY,
        ),
        call(
            runtime_env=original_runtime_env2,
            anyscale_api_client=ANY,
            api_client=ANY,
            workload_type=Workload.SERVICES,
            compute_config_id="mock_compute_config_id",
            log=ANY,
        ),
    ]
    assert service_config == expected_service_config
    override_runtime_env_config_mock.assert_has_calls(calls)
