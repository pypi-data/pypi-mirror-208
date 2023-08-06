from ray import tune
from ray.air import RunConfig, CheckpointConfig, ScalingConfig
from ray.tune.schedulers import ASHAScheduler

from trainer.torch_util import build_lightning_config, form_lightning_tuner
from tune_test.mnist_model import MNISTClassifier, MNISTDataModule
from workflow.annotations import as_asset, form_definitions
from workflow.ray_utils import long_run_job_client, JobDescription
from workflow.storage import get_io_manager, PersistStorage, DataFormat

# Configure Search Space
# The maximum training epochs
num_epochs = 5
# Number of sampls from parameter space
num_samples = 10
# Specify Accelerator
accelerator = "gpu"


@as_asset(
    name="form_lightning_config",
    description="define lightning config",
    io_manager_key="json_io_manager"
)
def form_lightning_config():
    config = {
        "layer_1_size": tune.choice([32, 64, 128]),
        "layer_2_size": tune.choice([64, 128, 256]),
        "lr": tune.loguniform(1e-4, 1e-1),
    }

    trainer_conf = {
        "num_epochs": num_epochs,
        "accelerator": accelerator
    }

    checkpoint_conf = {
        "monitor": "ckpt_monitor",
        "save_top_k": 2,
        "mode": "max"
    }

    ltn_config = build_lightning_config(
        pl_module=MNISTClassifier,
        data_module=MNISTDataModule(batch_size=64),
        module_conf=config,
        trainer_conf=trainer_conf,
        ckpt_conf=checkpoint_conf,
    )

    return ltn_config


@as_asset(
    name="define_lightning_tuner",
    description="Form Ray lightning tuner"
)
def define_lightning_tuner(form_lightning_config):
    # specify ray worker scaling config
    scaling_conf = ScalingConfig(
        num_workers=3,
        use_gpu=True,
        resources_per_worker={
            "CPU": 4,
            "GPU": 1
        }
    )
    # define runtime config
    run_conf = RunConfig(
        checkpoint_config=CheckpointConfig(
            num_to_keep=2,
            checkpoint_score_attribute="ptl/val_accuracy",
            checkpoint_score_order="max",
        )
    )
    # use ASHA scheduler
    asha_scheduler = ASHAScheduler(
        max_t=num_epochs,
        grace_period=1,
        reduction_factor=2
    )
    # compose the tuner
    ltn_conf = form_lightning_config
    asha_tuner = form_lightning_tuner(
        name="tune_mnist_pbt",
        ptl_config=ltn_conf,
        num_samples=num_samples,
        scheduler=asha_scheduler,
        scaling_conf=scaling_conf,
        runing_conf=run_conf
    )

    return asha_tuner


@as_asset(
    name="tuning_with_ray",
    description="Fit tuner and get best results.",
    io_manager_key="json_io_manager"
)
def tuning_with_ray(define_lightning_tuner):
    cluster_url = "http://10.112.67.227:8265"
    job_description = JobDescription(
        entrypoint="python script.py",
        working_dir="examples/",
        pip_packages=[]
    )
    job_id = long_run_job_client(
        cluster=cluster_url,
        description=JobDescription(
            entrypoint="python script.py",
            working_dir="tune_test/",
            pip_packages=[]
        )
    )

    return {
        "job_id": job_id,
        "cluster": cluster_url,
        "job_descrption": job_description.dict()
    }


defs = form_definitions(
    assets=[form_lightning_config, define_lightning_tuner, tuning_with_ray],
    resources={
        "default_io_manager": get_io_manager(
            medium=PersistStorage.OSS,
            base_path="xgboost"
        ),
        "json_io_manager": get_io_manager(
            medium=PersistStorage.OSS,
            base_path="xgboost",
            data_format=DataFormat.JSON
        )
    }
)
