import re
from typing import Any, Tuple
from unittest.mock import Mock, patch

from click import ClickException
from google.auth.exceptions import DefaultCredentialsError, RefreshError
import pytest

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.gcp_file_store_config import (
    GCPFileStoreConfig,
)
from anyscale.utils.gcp_utils import (
    get_application_default_credentials,
    get_gcp_filestore_config,
)


@pytest.mark.parametrize(
    ("filestore_id", "response", "not_found", "expected_result"),
    [
        pytest.param(
            "regional-filestore",
            ("200 OK", "regional_filestore.json"),
            False,
            GCPFileStoreConfig(
                instance_name="projects/anyscale-bridge-deadbeef/locations/us-central1/instances/regional-filestore",
                root_dir="something",
                mount_target_ip="172.22.236.2",
            ),
            id="regional",
        ),
        pytest.param(
            "zonal-filestore",
            ("200 OK", "zonal_filestore.json"),
            False,
            GCPFileStoreConfig(
                instance_name="projects/anyscale-bridge-deadbeef/locations/us-central1/instances/zonal-filestore",
                root_dir="test",
                mount_target_ip="172.27.155.250",
            ),
            id="zonal",
        ),
        pytest.param(
            "regional-filestore",
            ("200 OK", "regional_filestore_wrong_vpc.json"),
            False,
            None,
            id="wrong_vpc",
        ),
        pytest.param(
            "regional-filestore", ("404 Not Found", None), True, None, id="not_found"
        ),
    ],
)
def test_get_gcp_filestore_config(
    setup_mock_server, filestore_id, capsys, response, not_found, expected_result,
):
    factory, tracker = setup_mock_server
    mock_project_id = "anyscale-bridge-deadbeef"
    mock_vpc_name = "vpc_one"
    mock_filestore_region = "us-central1"
    tracker.reset({".*": [response]})
    if expected_result:
        assert (
            get_gcp_filestore_config(
                factory,
                mock_project_id,
                mock_vpc_name,
                mock_filestore_region,
                filestore_id,
                BlockLogger(),
            )
            == expected_result
        )
    else:
        if not_found:
            with pytest.raises(ClickException) as e:
                get_gcp_filestore_config(
                    factory,
                    mock_project_id,
                    mock_vpc_name,
                    mock_filestore_region,
                    filestore_id,
                    BlockLogger(),
                )
                e.match("Could not find Filestore with id")
        else:
            with pytest.raises(ClickException):
                get_gcp_filestore_config(
                    factory,
                    mock_project_id,
                    mock_vpc_name,
                    mock_filestore_region,
                    filestore_id,
                    BlockLogger(),
                )
            _, err = capsys.readouterr()
            assert "This cannot be edited on an existing Filestore instance." in err


def test_get_application_default_credentials_success(capsys):
    mock_run = Mock()
    with patch(
        "anyscale.utils.gcp_utils.google.auth",
        default=Mock(return_value=(Mock(), "project_abc")),
    ), patch("anyscale.utils.gcp_utils.subprocess", run=mock_run):
        credentials, project = get_application_default_credentials(BlockLogger())
        assert credentials is not None
        assert project == "project_abc"

    _, err = capsys.readouterr()
    assert err == ""

    mock_run.assert_not_called()


@pytest.mark.parametrize(
    ("refresh_error", "expected_output"),
    [
        pytest.param(True, "Reauthentication is needed", id="ReAuthNeeded"),
        pytest.param(False, "GCloud", id="NoAuthFound"),
    ],
)
def test_get_application_default_credentials_reauth(
    capsys, refresh_error: bool, expected_output: str
):
    num_calls = 0

    def default(*args: Any, **kwargs: Any) -> Tuple[Any, str]:
        nonlocal num_calls
        num_calls += 1
        if num_calls > 1:
            return Mock(), "project_abc"
        if refresh_error:
            mock_credentials = Mock()
            mock_credentials.refresh = Mock(side_effect=RefreshError)
            return mock_credentials, ""
        raise DefaultCredentialsError("abc")

    mock_run = Mock()
    mock_run.return_value.returncode = 0
    with patch(
        "anyscale.utils.gcp_utils.google.auth", default=Mock(side_effect=default)
    ), patch("anyscale.utils.gcp_utils.subprocess", run=mock_run):
        credentials, project = get_application_default_credentials(BlockLogger())
        assert credentials is not None
        assert project == "project_abc"

    assert num_calls == 2
    mock_run.assert_called_once()
    _, err = capsys.readouterr()
    assert re.search(expected_output, err), err
