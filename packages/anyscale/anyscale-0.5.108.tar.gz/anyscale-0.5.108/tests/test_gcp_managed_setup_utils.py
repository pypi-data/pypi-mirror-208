import re
from unittest.mock import Mock, patch

from click import ClickException
import pytest
import yaml

from anyscale.cli_logger import BlockLogger
from anyscale.utils.gcp_managed_setup_utils import (
    append_project_iam_policy,
    configure_firewall_policy,
    create_anyscale_aws_provider,
    create_workload_identity_pool,
    delete_gcp_deployment,
    delete_workload_identity_pool,
    enable_project_apis,
    generate_deployment_manager_config,
    get_anyscale_gcp_access_service_acount,
    get_deployment_resources,
    get_project_number,
    get_workload_identity_pool,
    remove_firewall_policy_associations,
    update_deployment_with_bucket_only,
    wait_for_operation_completion,
)


@pytest.mark.parametrize(
    ("response", "expected_error_message"),
    [
        pytest.param(("200 OK", "project_get.json"), None, id="succeed",),
        pytest.param(
            ("403 Forbidden", None),
            "Error occurred when trying to access the project",
            id="error",
        ),
    ],
)
def test_get_project_number(setup_mock_server, response, expected_error_message):
    factory, tracker = setup_mock_server
    mock_project_id = "anyscale-bridge-deadbeef"
    mock_project_name = "projects/112233445566"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            get_project_number(factory, mock_project_id)
            e.match(expected_error_message)
    else:
        assert get_project_number(factory, mock_project_id) == mock_project_name


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [
                ("200 OK", "project_get_iam_policy.json"),
                ("200 OK", "project_set_iam_policy.json"),
            ],
            None,
            id="no-role-in-bindings",
        ),
        pytest.param(
            [
                ("200 OK", "project_get_iam_policy_role_exists.json"),
                ("200 OK", "project_set_iam_policy_role_exists.json"),
            ],
            None,
            id="member-not-in-role",
        ),
        pytest.param(
            [
                ("200 OK", "project_set_iam_policy.json"),
                ("200 OK", "project_set_iam_policy.json"),
            ],
            None,
            id="member-already-exists",
        ),
        pytest.param(
            [("400 Bad Request", None)],
            "Failed to set IAM policy for project",
            id="member not found",
        ),
        pytest.param(
            [("403 Forbidden", None)],
            "Failed to set IAM policy for project",
            id="project-not-found",
        ),
    ],
)
def test_append_project_iam_policy(
    setup_mock_server, responses, expected_error_message
):
    factory, tracker = setup_mock_server
    tracker.reset({".*": responses})
    mock_project_id = "mock-project"
    mock_role = "roles/iam.securityAdmin"
    mock_member = "serviceAccount:112233445566@cloudservices.gserviceaccount.com"
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            append_project_iam_policy(factory, mock_project_id, mock_role, mock_member)
            e.match(expected_error_message)
    else:
        updated_policy = append_project_iam_policy(
            factory, mock_project_id, mock_role, mock_member
        )
        bingdings = updated_policy.bindings
        assert mock_role in [binding.role for binding in bingdings]
        assert mock_member in [
            member
            for binding in bingdings
            if binding.role == mock_role
            for member in binding.members
        ]


@pytest.mark.parametrize(
    ("response", "expected_error_message"),
    [
        pytest.param(("200 OK", "enable_api_operation.json"), None, id="succeed",),
        pytest.param(
            ("403 Forbidden", None), "Failed to enable APIs for project", id="error",
        ),
    ],
)
def test_enable_project_apis(setup_mock_server, response, expected_error_message):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ), pytest.raises(ClickException) as e:
            enable_project_apis(factory, mock_project_id)
            e.match(expected_error_message)
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            assert enable_project_apis(factory, mock_project_id) is None


@pytest.mark.parametrize(
    ("response", "expected_error_message", "pool_exists"),
    [
        pytest.param(
            ("200 OK", "get_workload_identity_pool.json"), None, True, id="succeed",
        ),
        pytest.param(("404 Not Found", None), None, False, id="NotFound"),
        pytest.param(
            ("403 Forbidden", None),
            "Failed to get Workload Identity Provider Pool.",
            True,
            id="error",
        ),
    ],
)
def test_get_workload_identity_pool(
    setup_mock_server, response, pool_exists, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_project_id = "anyscale-bridge-deadbeef"
    mock_pool_id = "mock-pool-id"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            get_workload_identity_pool(factory, mock_project_id, mock_pool_id)
            e.match(expected_error_message)
    else:
        if pool_exists:
            assert (
                get_workload_identity_pool(factory, mock_project_id, mock_pool_id)
                == mock_pool_id
            )
        else:
            assert (
                get_workload_identity_pool(factory, mock_project_id, mock_pool_id)
                is None
            )


@pytest.mark.parametrize(
    ("response", "expected_error_message", "service_account_exists"),
    [
        pytest.param(("200 OK", "get_service_account.json"), None, True, id="succeed",),
        pytest.param(("404 Not Found", None), None, False, id="NotFound"),
        pytest.param(
            ("403 Forbidden", None), "Failed to get service account: ", True, id="error"
        ),
    ],
)
def test_get_anyscale_gcp_access_service_acount(
    setup_mock_server, response, service_account_exists, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_service_account = (
        "anyscale-access@anyscale-bridge-deadbeef.iam.gserviceaccount.com"
    )
    tracker.reset({".*": [response]})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            get_anyscale_gcp_access_service_acount(factory, mock_service_account)
            e.match(expected_error_message)
    else:
        if service_account_exists:
            assert (
                get_anyscale_gcp_access_service_acount(factory, mock_service_account)
                == mock_service_account
            )
        else:
            assert (
                get_anyscale_gcp_access_service_acount(factory, mock_service_account)
                is None
            )


@pytest.mark.parametrize(
    ("response", "expected_log_message"),
    [
        pytest.param(
            ("200 OK", "create_workload_identity_pool.json"), None, id="succeed",
        ),
        pytest.param(("409 conflict", None), "already exists", id="pool-exists",),
        pytest.param(("418 I'm a teapot", None), "Error occurred", id="error",),
    ],
)
def test_create_workload_identity_pool(
    setup_mock_server, response, expected_log_message, capsys
):
    factory, tracker = setup_mock_server
    mock_project_id = "anyscale-bridge-deadbeef"
    mock_project_number = "123456789"
    mock_pool_id = "mock-pool-id"
    display_name = "mock pool"
    description = "mock provider pool"
    tracker.reset({".*": [response]})
    if expected_log_message:
        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            create_workload_identity_pool(
                factory,
                mock_project_id,
                mock_pool_id,
                BlockLogger(),
                display_name,
                description,
            )
        e.match("Failed to create Workload Identity Provider Pool")
        _, err = capsys.readouterr()
        assert expected_log_message in err

    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            assert (
                create_workload_identity_pool(
                    factory,
                    mock_project_id,
                    mock_pool_id,
                    BlockLogger(),
                    display_name,
                    description,
                )
                == f"projects/{mock_project_number}/locations/global/workloadIdentityPools/{mock_pool_id}"
            )


@pytest.mark.parametrize(
    ("response", "expected_error_message"),
    [
        pytest.param(
            ("200 OK", "create_workload_identity_provider.json"), None, id="succeed",
        ),
        pytest.param(("409 conflict", None), "already exists", id="pool-exists",),
        pytest.param(("404 Not Found", None), "Error occurred", id="error",),
    ],
)
def test_create_anyscale_aws_provider(
    setup_mock_server, response, expected_error_message, capsys
):
    factory, tracker = setup_mock_server
    mock_project_number = "123456789"
    mock_pool_id = f"projects/{mock_project_number}/locations/global/workloadIdentityPools/mock-pool-id"
    mock_provider_id = "mock-provider"
    mock_aws_account = "123456"
    mock_display_name = "mock provider"
    mock_org_id = "mock_org_id"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            create_anyscale_aws_provider(
                factory,
                mock_org_id,
                mock_pool_id,
                mock_provider_id,
                mock_aws_account,
                mock_display_name,
                BlockLogger(),
            )
        e.match("Failed to create Anyscale AWS Workload Identity Provider")
        _, err = capsys.readouterr()
        assert expected_error_message in err
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            assert (
                create_anyscale_aws_provider(
                    factory,
                    mock_org_id,
                    mock_pool_id,
                    mock_provider_id,
                    mock_aws_account,
                    mock_display_name,
                    BlockLogger(),
                )
                == f"{mock_pool_id}/providers/{mock_provider_id}"
            )


@pytest.mark.parametrize(
    ("response", "expected_log_message", "deletion_succeed"),
    [
        pytest.param(
            ("200 OK", "delete_workload_identity_pool.json"),
            "Deleted workload identity pool",
            True,
            id="succeed",
        ),
        pytest.param(
            ("403 Forbidden", None),
            "Error occurred when trying to delete workload identity pool",
            False,
            id="error1",
        ),
        pytest.param(("404 Not Found", None), None, False, id="error2",),
    ],
)
def test_delete_workload_identity_pool(
    setup_mock_server, response, deletion_succeed, expected_log_message, capsys
):
    factory, tracker = setup_mock_server
    mock_project_number = "123456789"
    mock_pool_id = "mock-pool-id"
    mock_pool_name = f"projects/{mock_project_number}/locations/global/workloadIdentityPools/{mock_pool_id}"
    tracker.reset({".*": [response]})
    if deletion_succeed:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            delete_workload_identity_pool(
                factory, mock_pool_name, BlockLogger(),
            )
            _, log = capsys.readouterr()
            assert expected_log_message in log
    elif expected_log_message:
        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            delete_workload_identity_pool(
                factory, mock_pool_name, BlockLogger(),
            )
            e.match(expected_log_message)
    else:
        # not found
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            assert (
                delete_workload_identity_pool(factory, mock_pool_name, BlockLogger(),)
                is None
            )


@pytest.mark.parametrize("service_type", ["workload_identity_pool", "provider"])
@pytest.mark.parametrize(
    ("response", "expected_error_message"),
    [
        pytest.param(
            ("200 OK", "create_workload_identity_pool.json"),
            "did not complete within the timeout period",
            id="timeout",
        ),
        pytest.param(("200 OK", "operation_completed.json"), None, id="succeed",),
        pytest.param(
            ("200 OK", "operation_error.json"), "encountered an error", id="error",
        ),
    ],
)
def test_wait_for_operation_completion(
    setup_mock_server, response, expected_error_message, service_type
):
    factory, tracker = setup_mock_server
    mock_project_name = "projects/112233445566"
    mock_pool_id = "mock-pool-id"
    mock_provider_id = "mock-provider"
    if service_type == "workload_identity_pool":
        service = (
            factory.build("iam", "v1").projects().locations().workloadIdentityPools()
        )
        mock_operation_id = f"{mock_project_name}/locations/global/workloadIdentityPools/{mock_pool_id}/operations/mock_operation_id"
    elif service_type == "provider":
        service = (
            factory.build("iam", "v1")
            .projects()
            .locations()
            .workloadIdentityPools()
            .providers()
        )
        mock_operation_id = f"{mock_project_name}/locations/global/workloadIdentityPools/{mock_pool_id}/providers/{mock_provider_id}/operations/mock_operation_id"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils.time",
            time=Mock(side_effect=list(range(10))),  # only iterates once
            sleep=Mock(),
        ), pytest.raises(ClickException) as e:
            wait_for_operation_completion(
                service,
                {"name": mock_operation_id},
                "test",
                timeout=1,
                polling_interval=10,
            )
            e.match(expected_error_message)
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils.time",
            time=Mock(side_effect=list(range(10))),
            sleep=Mock(),
        ):
            assert (
                wait_for_operation_completion(
                    service, {"name": mock_operation_id}, "test",
                )
                is None
            )


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "associate_firewall_policy.json"),
                ("200 OK", "add_firewall_policy_rule_done.json"),
                ("200 OK", "add_firewall_policy_rule_done.json"),
                ("200 OK", "associate_firewall_policy_done.json"),
            ],
            None,
            id="succeed",
        ),
        pytest.param(
            [
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "associate_firewall_policy.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
            ],
            "Timeout when trying to configure firewall policy",
            id="timeout",
        ),
        pytest.param(
            [
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "associate_firewall_policy.json"),
                ("200 OK", "add_firewall_policy_rule_error.json"),
            ],
            "Failed to configure firewall policy ",
            id="error",
        ),
        pytest.param(
            [("400 Bad Request", None)],
            "Failed to configure firewall policy",
            id="bad-request",
        ),
        pytest.param(
            [
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
                ("404 Not Found", None),
            ],
            "Failed to configure firewall policy",
            id="not-found",
        ),
    ],
)
def test_configure_firewall_policy(
    setup_mock_server, responses, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_vpc_name = "mock-vpc"
    mock_firewall_policy = "mock-fp"
    mock_subnet_cidr = "10.0.0.0/20"
    tracker.reset({".*": responses})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            configure_firewall_policy(
                factory,
                mock_vpc_name,
                mock_project_id,
                mock_firewall_policy,
                mock_subnet_cidr,
            )
        e.match(expected_error_message)
    else:
        configure_firewall_policy(
            factory,
            mock_vpc_name,
            mock_project_id,
            mock_firewall_policy,
            mock_subnet_cidr,
        )


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [("404 Not Found", None)], "Failed to get deployment", id="failed",
        ),
        pytest.param(
            [("200 OK", "deployment_get.json"), ("200 OK", "manifest_get.json")],
            None,
            id="succeed",
        ),
    ],
)
def test_get_deployment_resources(setup_mock_server, responses, expected_error_message):
    factory, tracker = setup_mock_server
    mock_deployment_name = "mock-deployment"
    mock_project_id = "mock-project"
    mock_anyscale_access_service_account_name = "anyscale-access-cld-congtest"
    tracker.reset({".*": responses})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            get_deployment_resources(
                factory,
                mock_deployment_name,
                mock_project_id,
                mock_anyscale_access_service_account_name,
            )
            e.match(expected_error_message)
    else:
        assert get_deployment_resources(
            factory,
            mock_deployment_name,
            mock_project_id,
            mock_anyscale_access_service_account_name,
        ) == {
            "compute.v1.network": "vpc-cld-congtest",
            "compute.v1.subnetwork": "subnet-cld-congtest",
            "gcp-types/compute-v1:networkFirewallPolicies": "firewall-policy-cld-congtest",
            "filestore_instance": "filestore-cld-congtest",
            "filestore_location": "us-west1",
            "gcp-types/file-v1beta1:projects.locations.instances": "filestore-cld-congtest",
            "storage.v1.bucket": "storage-bucket-cld-congtest",
            "iam.v1.serviceAccount": "instance-cld-congtest",
        }


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [("200 OK", "deployment_get.json"), ("200 OK", "deployment_delete.json")],
            None,
            id="no-bucket-delete-succeed",
        ),
        pytest.param(
            [("200 OK", "deployment_get.json"), ("403 Forbidden", None)],
            "Failed to delete deployment",
            id="no-bucket-delete-fail",
        ),
        pytest.param([("404 Not Found", None)], None, id="no-deployment"),
        pytest.param(
            [("403 Forbidden", None)], "Failed to get deployment", id="forbidden"
        ),
    ],
)
def test_delete_gcp_deployment(setup_mock_server, responses, expected_error_message):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_deployment = "mock-deployment"
    tracker.reset({".*": responses})

    if expected_error_message:

        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            delete_gcp_deployment(factory, mock_project_id, mock_deployment)
            e.match(expected_error_message)
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):

            assert (
                delete_gcp_deployment(factory, mock_project_id, mock_deployment) is None
            )


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [
                ("200 OK", "deployment_get.json"),
                ("200 OK", "manifest_get.json"),
                ("200 OK", "deployment_update.json"),
            ],
            None,
            id="keep-bucket-delete-succeed",
        ),
        pytest.param(
            [
                ("200 OK", "deployment_get.json"),
                ("200 OK", "manifest_get.json"),
                ("403 Forbidden", None),
            ],
            "Failed to delete deployment",
            id="keep-bucket-delete-fail",
        ),
        pytest.param(
            [("404 Not Found", None)], "Failed to delete deployment", id="no-deployment"
        ),
        pytest.param(
            [("403 Forbidden", None)], "Failed to delete deployment", id="forbidden"
        ),
    ],
)
def test_update_deployment_with_bucket_only(
    setup_mock_server, responses, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_deployment = "mock-deployment"
    tracker.reset({".*": responses})

    if expected_error_message:

        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            update_deployment_with_bucket_only(
                factory, mock_project_id, mock_deployment
            )
            e.match(expected_error_message)
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):

            assert (
                update_deployment_with_bucket_only(
                    factory, mock_project_id, mock_deployment
                )
                is None
            )


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param([("404 Not Found", None)], None, id="no-firewall",),
        pytest.param(
            [
                ("200 OK", "firewall_policy_get.json"),
                ("200 OK", "remove_firewall_vpc_association.json"),
                ("200 OK", "remove_firewall_vpc_association_done.json"),
            ],
            None,
            id="succeed",
        ),
        pytest.param(
            [("200 OK", "firewall_policy_get.json"), ("400 Bad Request", None)],
            None,
            id="no-association",
        ),
        pytest.param(
            [("200 OK", "firewall_policy_get.json"), ("403 Forbidden", None)],
            "Failed to remove firewall policy association.",
            id="forbidden",
        ),
        pytest.param(
            [
                ("200 OK", "firewall_policy_get.json"),
                ("200 OK", "remove_firewall_vpc_association.json"),
                ("200 OK", "remove_firewall_vpc_association.json"),
            ],
            "Timeout",
            id="timeout",
        ),
        pytest.param(
            [
                ("200 OK", "firewall_policy_get.json"),
                ("200 OK", "remove_firewall_vpc_association.json"),
                ("200 OK", "remove_firewall_vpc_association_error.json"),
            ],
            "Failed to remove",
            id="error",
        ),
    ],
)
def test_remove_firewall_policy_associations(
    setup_mock_server, responses, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_firewall_policy = "mock-firewall-policy"
    tracker.reset({".*": responses})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            remove_firewall_policy_associations(
                factory, mock_project_id, mock_firewall_policy
            )
            e.match(expected_error_message)
    else:
        assert (
            remove_firewall_policy_associations(
                factory, mock_project_id, mock_firewall_policy
            )
            is None
        )


def test_generate_deployment_manager_config():
    mock_region = "mock-region"
    mock_project_id = "mock-project"
    mock_cloud_id = "cld_mock"
    mock_service_account_name = "anyscale-access-mock"
    workload_identity_pool_name = (
        "projects/112233445566/locations/global/workloadIdentityPools/mock-pool"
    )
    anyscale_aws_account = "123456"
    organization_id = "org_mock"

    generated_config = generate_deployment_manager_config(
        mock_region,
        mock_project_id,
        mock_cloud_id,
        mock_service_account_name,
        workload_identity_pool_name,
        anyscale_aws_account,
        organization_id,
    )

    # verify it's a valid yaml file
    yaml.safe_load(generated_config)

    # verify all ${val} are substituted
    assert re.search(r"\$\{.*\}", generated_config) is None
