import random
import string

from anyscale.client.openapi_client.models.apply_production_service_v2_model import (
    ApplyProductionServiceV2Model,
)
from anyscale.client.openapi_client.models.apply_service_config import (
    ApplyServiceConfig,
)
from anyscale.client.openapi_client.models.create_production_service import (
    CreateProductionService,
)
from anyscale.client.openapi_client.models.production_job_config import (
    ProductionJobConfig,
)
from anyscale.client.openapi_client.models.user_service_access_types import (
    UserServiceAccessTypes as UserServiceAccessTypesAPIModel,
)
from anyscale.models.service_model import ServiceConfig, UserServiceAccessTypes


def format_service_config(service_config: ServiceConfig) -> ApplyServiceConfig:
    """
    This method formats the ServiceConfig into the API model ApplyServiceConfig.

    Please note that ServiceConfig captures Service configs for both Service v1 and v2.
    Since the CLI client can't determine whether the Service v1 or v2 should be launched
    because it depends on FFs, the CLI client will try to parse ServiceConfig into
    both the Service v1 and v2 configs. Therefore, both the Service v1 and v2 configs
    can exist at the same time.
    """
    production_job_config = ProductionJobConfig(
        entrypoint=service_config.entrypoint,
        runtime_env=service_config.runtime_env,
        build_id=service_config.build_id,
        compute_config_id=service_config.compute_config_id,
        max_retries=service_config.max_retries,
        ray_serve_config=service_config.ray_serve_config,
    )

    service_name = service_config.name or _generate_random_service_name()
    access = (
        UserServiceAccessTypesAPIModel.PUBLIC
        if service_config.access == UserServiceAccessTypes.public
        else UserServiceAccessTypesAPIModel.PRIVATE
    )
    service_v1_config = CreateProductionService(
        name=service_name,
        description=service_config.description or "Service updated from CLI",
        project_id=service_config.project_id,
        config=production_job_config,
        healthcheck_url=service_config.healthcheck_url,
        access=access,
    )
    # We construct the Service v2 config model only if ray_serve_config is present
    if service_config.ray_serve_config:
        service_v2_config = ApplyProductionServiceV2Model(
            name=service_name,
            description=service_config.description or "Service updated from CLI",
            project_id=service_config.project_id,
            version=service_config.version,
            canary_percent=service_config.canary_percent,
            ray_serve_config=service_config.ray_serve_config,
            ray_gcs_external_storage_config=service_config.ray_gcs_external_storage_config,
            build_id=service_config.build_id,
            compute_config_id=service_config.compute_config_id,
        )
    else:
        service_v2_config = None
    return ApplyServiceConfig(
        service_v1_config=service_v1_config, service_v2_config=service_v2_config
    )


def format_service_config_v2(
    service_config: ServiceConfig,
) -> ApplyProductionServiceV2Model:
    if not service_config.ray_serve_config:
        raise RuntimeError(
            "ray_serve_config is expected for the Service configuration."
        )

    service_name = service_config.name or _generate_random_service_name()

    return ApplyProductionServiceV2Model(
        name=service_name,
        description=service_config.description or "Service updated from CLI",
        project_id=service_config.project_id,
        version=service_config.version,
        canary_percent=service_config.canary_percent,
        ray_serve_config=service_config.ray_serve_config,
        ray_gcs_external_storage_config=service_config.ray_gcs_external_storage_config,
        build_id=service_config.build_id,
        compute_config_id=service_config.compute_config_id,
        rollout_strategy=service_config.rollout_strategy,
    )


def _generate_random_service_name() -> str:
    """Generates a random service name
    Format:
        cli-service-{10 random characters}
    """
    random_chars = "".join(random.choices(string.ascii_letters, k=10)).lower()
    return "cli-service-" + random_chars
