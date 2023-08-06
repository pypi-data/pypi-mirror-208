import pytorch_lightning as pl
from pytorch_lightning.loggers.csv_logs import CSVLogger
from ray.air.config import RunConfig, ScalingConfig, CheckpointConfig
from ray.train.lightning import (
    LightningTrainer,
    LightningConfigBuilder,
    LightningCheckpoint,
)

from tune_test.mnist_model import MNISTDataModule, MNISTClassifier

datamodule = MNISTDataModule(batch_size=128)


accelerator = "gpu"


lightning_config = (
    LightningConfigBuilder()
    .module(MNISTClassifier, lr=1e-3, feature_dim=128)
    .trainer(
        max_epochs=10,
        accelerator=accelerator,
        log_every_n_steps=100,
        logger=CSVLogger("logs"),
    )
    .fit_params(datamodule=datamodule)
    .checkpointing(monitor="val_accuracy", mode="max", save_top_k=3)
    .build()
)

scaling_config = ScalingConfig(
    num_workers=4, use_gpu=True, resources_per_worker={"CPU": 1, "GPU": 1}
)

run_config = RunConfig(
    name="ptl-mnist-example",
    local_dir="/tmp/ray_results",
    checkpoint_config=CheckpointConfig(
        num_to_keep=3,
        checkpoint_score_attribute="val_accuracy",
        checkpoint_score_order="max",
    ),
)

ptl_ray_trainer = LightningTrainer(
    lightning_config=lightning_config,
    scaling_config=scaling_config,
    run_config=run_config
)

result = ptl_ray_trainer.fit()
print("Validation Accuracy: ", result.metrics["val_accuracy"])

checkpoint: LightningCheckpoint | None = result.checkpoint
best_model: pl.LightningModule = checkpoint.get_model(MNISTClassifier)
pl_trainer = pl.Trainer()
test_dataloader = datamodule.test_dataloader()
result = pl_trainer.test(best_model, dataloaders=test_dataloader)
