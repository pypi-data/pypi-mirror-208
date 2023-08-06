import xgboost as xgb
from ray.air import ScalingConfig
from ray.data.preprocessor import Preprocessor
from ray.train.batch_predictor import BatchPredictor
from ray.train.xgboost import XGBoostCheckpoint, XGBoostPredictor
from ray.train.xgboost import XGBoostTrainer
from xgboost.core import XGBoostError

from fiat_copilot.utils.config import get_logger

logger = get_logger()


def define_xgb_trainer_and_fit(
        dataset: dict,
        label_col: str,
        scaling_conf: dict,
        boost_round: int,
        training_params: dict,
        preprocess_pipeline: Preprocessor,
):
    trainer = XGBoostTrainer(
        label_column=label_col,
        num_boost_round=boost_round,
        scaling_config=ScalingConfig(**scaling_conf),
        params=training_params,
        datasets=dataset,
        preprocessor=preprocess_pipeline,
    )
    logger.debug(f"Trainer: {trainer}")

    logger.debug("Start training...")
    result = trainer.fit()
    logger.debug(f"Training complete, result metrics: {result.metrics}")
    logger.debug("You can access the final checkpoint with - 'result.checkpoint' or 'result.best_checkpoint'.")

    return result


def convert_xgboost_model_into_checkpoint(
        xgb_model=None,
        path: str | None = None
) -> XGBoostCheckpoint:
    logger.debug("Converting booster into XGBoostCheckpoint...")
    try:
        if not xgb_model:
            model = xgb.Booster()
            model.load_model(path)

            checkpoint: XGBoostCheckpoint = XGBoostCheckpoint.from_model(model)
        else:
            checkpoint: XGBoostCheckpoint = XGBoostCheckpoint.from_model(xgb_model.get_booster())
    except XGBoostError:
        logger.error("Cannot load Booster model!")
        raise SystemError

    return checkpoint


def compose_xgboost_batch_predictor(checkpoint: XGBoostCheckpoint):
    logger.debug(f"Composing batch predictor with checkpoint: {checkpoint}")
    batch_predictor = BatchPredictor.from_checkpoint(
        checkpoint=checkpoint,
        predictor_cls=XGBoostPredictor
    )
    logger.debug(f"Predictor: {batch_predictor}")

    return batch_predictor
