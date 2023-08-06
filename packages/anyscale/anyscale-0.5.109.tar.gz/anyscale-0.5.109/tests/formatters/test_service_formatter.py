from unittest.mock import Mock, patch

from anyscale.formatters.service_formatter import format_service_config
from anyscale.models.service_model import ServiceConfig


def test_format_service_v1_config():
    entrypoint = "python test.py"
    project_id = "test_project_id"
    build_id = "test_build_id"
    compute_config_id = "test_compute_config_id"
    config_dict = {
        "entrypoint": entrypoint,
        "project_id": project_id,
        "build_id": build_id,
        "compute_config_id": compute_config_id,
        "healthcheck_url": "test.url",
    }
    mock_validate_successful_build = Mock()
    with patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        service_config = ServiceConfig.parse_obj(config_dict)

    apply_service_config = format_service_config(service_config)

    assert apply_service_config.service_v2_config is None
    assert apply_service_config.service_v1_config.project_id == project_id
    assert apply_service_config.service_v1_config.config.entrypoint == entrypoint
    assert apply_service_config.service_v1_config.config.build_id == build_id
    assert (
        apply_service_config.service_v1_config.config.compute_config_id
        == compute_config_id
    )


def test_format_service_v2_config():
    """
    Tests that for a Service config with ray_serve_config field set,
    the formatter method will return both Service v1 and v2 configs.
    """
    ray_serve_config = {"runtime_env": {"pip": ["requests"], "working_dir": "."}}
    project_id = "test_project_id"
    build_id = "test_build_id"
    compute_config_id = "test_compute_config_id"
    version = "test_version"
    canary_percent = 60
    config_dict = {
        "ray_serve_config": ray_serve_config,
        "project_id": project_id,
        "build_id": build_id,
        "compute_config_id": compute_config_id,
        "version": version,
        "canary_percent": canary_percent,
    }
    mock_validate_successful_build = Mock()
    with patch.multiple(
        "anyscale.controllers.job_controller",
        validate_successful_build=mock_validate_successful_build,
    ):
        service_config = ServiceConfig.parse_obj(config_dict)

    apply_service_config = format_service_config(service_config)

    assert apply_service_config.service_v1_config.project_id == project_id
    assert apply_service_config.service_v1_config.config.entrypoint is None
    assert (
        apply_service_config.service_v1_config.config.ray_serve_config
        == ray_serve_config
    )
    assert apply_service_config.service_v1_config.config.build_id == build_id
    assert (
        apply_service_config.service_v1_config.config.compute_config_id
        == compute_config_id
    )
    assert (
        apply_service_config.service_v1_config.config.ray_serve_config
        == ray_serve_config
    )
    assert apply_service_config.service_v2_config.project_id == project_id
    assert apply_service_config.service_v2_config.ray_serve_config == ray_serve_config
    assert apply_service_config.service_v2_config.version == version
    assert apply_service_config.service_v2_config.canary_percent == canary_percent
