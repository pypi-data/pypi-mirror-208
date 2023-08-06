import logging
from contextlib import contextmanager
from typing import Callable, Any

from ray import serve
from ray.dag import ClassNode, FunctionNode
from ray.serve.handle import RayServeHandle

from fiat_copilot.serving.attendant import BatchTextGenerator, BatchImageInferencing, \
    BatchTabularPredictor
from fiat_copilot.serving.domain import AppDescription, ServiceType

logger = logging.getLogger("rich")


def get_attendant(
        serving_type: ServiceType,
        resource_quota: dict,
):
    if serving_type is ServiceType.Text:
        return serve.deployment(
            ray_actor_options=resource_quota['actor'],
            autoscaling_config=resource_quota['autoscale']
        )(BatchTextGenerator)
    elif serving_type is ServiceType.Image:
        return serve.deployment(
            ray_actor_options=resource_quota['actor'],
            autoscaling_config=resource_quota['autoscale']
        )(BatchImageInferencing)
    elif serving_type is ServiceType.Tabular:
        return serve.deployment(
            ray_actor_options=resource_quota['actor'],
            autoscaling_config=resource_quota['autoscale']
        )(BatchTabularPredictor)
    else:
        raise SystemError


def get_serving_result_with_handle(
        handle: RayServeHandle,
        input_batch: list
):
    import ray

    result_batch = ray.get(
        [handle.handle_batch.remote(batch) for batch in input_batch]
    )

    return result_batch


@contextmanager
def adhoc_serving_setup(
        serving_model,
        handle_func: Callable[..., Any],
        serving_type: ServiceType,
        app_description: AppDescription,
        ray_cluster: str | None = None,
) -> RayServeHandle | None:
    import ray

    try:
        if not ray_cluster:
            logger.info("Trying to initialize local Ray instance.")
            ray.init()
        else:
            logger.info(f"Trying to initialize Ray instance at {ray_cluster}")
            ray.init(
                address=f"ray://{ray_cluster}"
            )
        logger.info("Ray instance initialized!")

        attendant: ClassNode | FunctionNode = get_attendant(
            serving_type=serving_type,
            resource_quota=app_description.resource_config
        ).bind(model=serving_model, batch_handler=handle_func)

        handle = serve.run(
            target=attendant,
            host=app_description.host,
            port=app_description.port,
            name=app_description.name,
            route_prefix=app_description.route_prefix
        )

        yield handle
    finally:
        serve.shutdown()
        ray.shutdown()
