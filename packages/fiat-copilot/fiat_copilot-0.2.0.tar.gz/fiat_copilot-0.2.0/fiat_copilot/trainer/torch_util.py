import os
from enum import Enum
from typing import Type

from pytorch_lightning import LightningModule, LightningDataModule
from pytorch_lightning.loggers import TensorBoardLogger
from ray.air import ScalingConfig, RunConfig, Checkpoint
from ray.train.lightning import LightningConfigBuilder, LightningTrainer
from ray.tune import Tuner, TuneConfig, SyncConfig
from ray.tune.schedulers import TrialScheduler, AsyncHyperBandScheduler, PopulationBasedTraining


class SchedulerType(Enum):
    ASHA = AsyncHyperBandScheduler
    PBT = PopulationBasedTraining


def build_lightning_config(
        pl_module: Type[LightningModule],
        data_module: LightningDataModule,
        module_conf: dict,
        trainer_conf: dict,
        ckpt_conf: dict,
        trainer_logger: TensorBoardLogger | None = None
):
    if not trainer_logger:
        trainer_logger = TensorBoardLogger(save_dir=os.getcwd(), name=os.getcwd().split("/")[-1], version="1.0")

    lightning_config = LightningConfigBuilder() \
        .module(cls=pl_module, config=module_conf) \
        .trainer(
        max_epochs=trainer_conf['num_epochs'],
        accelerator=trainer_conf['accelerator'],
        logger=trainer_logger
    ) \
        .fit_params(datamodule=data_module) \
        .checkpointing(**ckpt_conf) \
        .build()

    return lightning_config


def form_lightning_tuner(
        name: str,
        ptl_config: dict[str, any],
        num_samples: int,
        scheduler: TrialScheduler,
        scaling_conf: ScalingConfig,
        runing_conf: RunConfig,
        sync_conf: SyncConfig = SyncConfig(
            syncer=None  # Disable syncing
        )
):
    # Define a base LightningTrainer without hyperparameters for Tuner
    lightning_trainer = LightningTrainer(
        scaling_config=scaling_conf,
        run_config=runing_conf,
    )

    tuner = Tuner(
        lightning_trainer,
        param_space={
            "lightning_config": ptl_config
        },
        tune_config=TuneConfig(
            metric="ptl/val_accuracy",
            mode="max",
            num_samples=num_samples,
            scheduler=scheduler,
        ),
        run_config=RunConfig(
            name=name,
            sync_config=sync_conf
        )
    )

    return tuner


def form_lightning_trainer(
        ptl_config: dict[str, any],
        scaling_conf: ScalingConfig,
        runing_conf: RunConfig,
        checkpoint: Checkpoint | None = None
):
    return LightningTrainer(
        lightning_config=ptl_config,
        scaling_config=scaling_conf,
        run_config=runing_conf,
        resume_from_checkpoint=checkpoint
    )


def tuning_and_get_best(tuner: Tuner):
    result = tuner.fit()
    best_result = result.get_best_result(metric="ptl/val_accuracy", mode="max")

    ret = {
        "best_checkpoint": best_result.checkpoint.to_dict(),
        "metrics": best_result.metrics,
        "result_path": best_result.path,
        "config": best_result.config
    }

    return ret
