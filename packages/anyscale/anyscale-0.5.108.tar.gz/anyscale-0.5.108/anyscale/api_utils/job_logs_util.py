from typing import List, Optional

from anyscale.api_utils.exceptions.log_retrieval_errors import (
    wrap_as_unsupported_log_retrieval_method_error,
    wrap_job_run_log_not_retrievable_on_active_cluster_error,
)
from anyscale.api_utils.job_util import _get_job_run_id
from anyscale.api_utils.logs_util import (
    _download_log_from_ray_json_response,
    _download_logs_concurrently,
    _remove_ansi_escape_sequences,
)
from anyscale.controllers.logs_controller import DEFAULT_PARALLELISM
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as BaseApi
from anyscale.sdk.anyscale_client.models.log_download_result import LogDownloadResult


async def _get_logs_from_active_job_run(
    base_api: BaseApi,
    job_run_id: str,
    raise_connection_issue_as_cli_error: bool = False,
    remove_escape_chars: bool = True,
) -> str:
    """
    Retrieves logs directly from the cluster (assumed to be active) that the **job run** is on.

    This first retrieves
    Raises:
        ExpectedLogRetrievalError: Reasons include:
            a. If the cluster is not active
            b. If the cluster is running < Ray 2.0
            c. The job run was on a previous uptime / session of the cluster
                (ie. the cluster has since restarted since the job run)
            d. The Anyscale SDK/CLI client cannot directly connect to the cluster
                (due to VPN issues or high load on the cluster)
    """
    # 1. Get the Ray API URL where it can stream (ie. download from active Ray cluster) job logs.
    # Raises ExpectedLogRetrievalError on a. and b.
    with wrap_as_unsupported_log_retrieval_method_error():
        job_logs_url: str = base_api.get_job_logs_stream(
            job_id=job_run_id
        ).result.http_url
    # 2. Call the Ray API URL and parse the logs from the JSON response
    # Raises ExpectedLogRetrievalError on c. and d.
    with wrap_job_run_log_not_retrievable_on_active_cluster_error(
        job_run_id, raise_connection_issue_as_cli_error
    ):
        logs = await _download_log_from_ray_json_response(job_logs_url)
        if remove_escape_chars:
            logs = _remove_ansi_escape_sequences(logs)
    return logs


async def _get_logs_from_running_production_job(
    base_api: BaseApi, production_job_id: str, remove_escape_chars: bool = True,
) -> str:
    """
    Retrieves logs directly from the cluster (assumed to be active) that the **job** is on.

    This is done by determining the last job run of the job and calling
    `_get_logs_from_active_job_run()` above.

    Raises:
        NoJobRunError: If a job run hasn't been created yet.
        ExpectedLogRetrievalError: See `_get_logs_from_active_job_run`
    """
    last_job_run_id = _get_job_run_id(base_api, job_id=production_job_id)
    return await _get_logs_from_active_job_run(
        base_api, last_job_run_id, remove_escape_chars
    )


async def _get_job_logs_from_storage_bucket(
    base_api: BaseApi,
    *,
    job_id: Optional[str] = None,
    job_run_id: Optional[str] = None,
    parallelism: int = DEFAULT_PARALLELISM,
    remove_escape_chars: bool = True,
) -> str:
    """Retrieves logs directly from the storage bucket.
    Currently, this is supported only for AWS clouds (through S3)

    Args:
        parallelism (int, optional): Defaults to 10 (AWS S3's default `max_concurrent_requests` value)
            There is no documented upper limit. However, please set a reasonable value.
        remove_escape_chars (bool, optional): Removes ANSI escape sequences from the logs, which are
            commonly used to color terminal output. Defaults to True.

    Raises:
        NoJobRunError: If a job run hasn't been created yet.
        ExpectedLogRetrievalError: If the job is on a cloud that does not support log download
            (such as GCP), or using the existing Anyscale V1 implementation.
    """
    job_run_id = _get_job_run_id(base_api, job_id=job_id, job_run_id=job_run_id)

    with wrap_as_unsupported_log_retrieval_method_error():
        log_download_result: LogDownloadResult = base_api.get_job_logs_download(
            job_id=job_run_id, all_logs=True
        ).result

    all_log_chunk_urls: List[str] = [chunk.chunk_url for chunk in log_download_result.log_chunks]  # type: ignore
    logs = await _download_logs_concurrently(all_log_chunk_urls, parallelism)
    if remove_escape_chars:
        logs = _remove_ansi_escape_sequences(logs)
    return logs
