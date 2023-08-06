from typing import Optional

from anyscale.api_utils.cloud_util import _is_v2_cloud
from anyscale.api_utils.exceptions.job_errors import NoJobRunError
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as BaseApi
from anyscale.sdk.anyscale_client.models.cluster_compute import ClusterCompute
from anyscale.sdk.anyscale_client.models.job import Job
from anyscale.sdk.anyscale_client.models.production_job import ProductionJob
from anyscale.sdk.anyscale_client.models.session import Session


def _get_job_run_id(
    base_api: BaseApi,
    *,
    job_id: Optional[str] = None,
    job_run_id: Optional[str] = None,
) -> str:
    assert bool(job_id) != bool(
        job_run_id
    ), "Exactly one of `job_id` or `job_run_id` must be provided."
    if job_id:
        prod_job: ProductionJob = base_api.get_production_job(job_id).result
        if not prod_job.last_job_run_id:
            raise NoJobRunError(f"Production job {job_id} has no job runs.")
        job_run_id = prod_job.last_job_run_id
    return job_run_id  # type: ignore


def _is_job_on_v2_cloud(base_api: BaseApi, job_id: str) -> bool:
    job: Job = base_api.get_job(job_id).result
    cluster: Session = base_api.get_session(job.cluster_id).result
    return _is_v2_cloud(base_api, cluster.cloud_id)


def _is_production_job_on_v2_cloud(base_api: BaseApi, production_job_id: str) -> bool:
    prod_job: ProductionJob = base_api.get_production_job(production_job_id).result
    cluster_compute: ClusterCompute = base_api.get_cluster_compute(
        prod_job.config.compute_config_id
    ).result
    return _is_v2_cloud(base_api, cluster_compute.config.cloud_id)
