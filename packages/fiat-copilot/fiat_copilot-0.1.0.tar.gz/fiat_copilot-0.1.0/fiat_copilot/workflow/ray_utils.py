from contextlib import contextmanager
from typing import Callable, Any

from pydantic import BaseModel
from ray.job_submission import JobSubmissionClient

from fiat_copilot.utils.config import get_logger


logger = get_logger()


class ResourceQuota(BaseModel):
    cpu: int
    gpu: int


class JobDescription(BaseModel):
    entrypoint: str  # "python script.py"
    working_dir: str  # "examples/"
    pip_packages: list[str]


@contextmanager
def adhoc_task_on_ray(
        cluster: str | None = None,
        resource: ResourceQuota = ResourceQuota(
            cpu=1,
            gpu=0
        )
):
    import ray

    if not cluster:
        logger.info("Trying to initialize local Ray instance.")
        ray.init()
    else:
        logger.info(f"Trying to initialize Ray instance at {cluster}")
        ray.init(
            address=f"ray://{cluster}"
        )
    logger.info("Ray instance initialized!")

    def run_remote_func(compute_fn: Callable[..., Any]):
        @ray.remote(
            num_cpus=resource.cpu,
            num_gpus=resource.gpu
        )
        def task_wrapper(func: Callable[..., Any]):
            return func()

        ref = task_wrapper.remote(compute_fn)
        ret = ray.get(ref)

        return ret

    try:
        yield run_remote_func
    finally:
        logger.info("Shutdown Ray instance.")
        ray.shutdown()


@contextmanager
def form_job_client(
        cluster_url: str = "auto"
):
    try:
        # If using a remote cluster, replace 127.0.0.1 with the head node's IP address.
        client: JobSubmissionClient = JobSubmissionClient(
            address=cluster_url,
            create_cluster_if_needed=True
        )

        yield client
    except RuntimeError:
        logger.error("Failed to start a Ray cluster job client. Please check your target URL.")


def long_run_job_client(
        cluster: str,
        description: JobDescription
):
    try:
        with form_job_client(cluster_url=cluster) as job_client:
            job_id = job_client.submit_job(
                # Entrypoint bash command to execute
                entrypoint=description.entrypoint,
                # Path to the local directory that contains the script.py file
                runtime_env={
                    "working_dir": description.working_dir,
                    "pip": description.pip_packages
                }
            )
            logger.debug(f"Job submission with id: {job_id}")

        return job_id
    except RuntimeError:
        logger.error("Failed to submit job")
        raise SystemExit
