import json

import pandas as pd
import ray
import xgboost as xgb
from ray.data import Dataset, DatasetPipeline
from ray.data.preprocessors import StandardScaler
from rich import print
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

from fiat_copilot.trainer.xgboost_util import define_xgb_trainer_and_fit, \
    convert_xgboost_model_into_checkpoint, compose_xgboost_batch_predictor
from fiat_copilot.workflow.annotations import as_asset, form_definitions
from fiat_copilot.workflow.storage import get_io_manager, PersistStorage, DataFormat

# home_path = os.environ['HOME']
# ray.init(address="ray://10.112.172.14:10001")
# ray.init(address="ray://10.112.67.227:10001")
ray.init(
    address="auto",
    runtime_env={
        "pip": [
            "xgboost",
            "xgboost_ray",
            "rich"
        ]
    }
)


@as_asset(
    name="load_breast_cancer_dataset",
    description="Loading breast cancer dataset."
)
def load_breast_cancer_dataset():
    print("Loading dataset...")
    dataset = ray.data.read_parquet(f"datasets/breast_cancer")
    train_dataset, valid_dataset = dataset.train_test_split(test_size=0.3)
    test_dataset = valid_dataset.drop_columns(["target"])

    return {
        "train": train_dataset.to_pandas().to_json(),
        "test": test_dataset.to_pandas().to_json()
    }


@as_asset(
    name="train_xgboost_model_with_ray",
    description="Form XGBoost trainer and train it."
)
def train_xgboost_model_with_ray(load_breast_cancer_dataset):
    print("Form XGBoost trainer and training")

    dataset = load_breast_cancer_dataset
    df = pd.read_json(dataset['train'])
    train_dataset = ray.data.from_pandas(df)

    result = define_xgb_trainer_and_fit(
        dataset={
            "train": train_dataset
        },
        label_col="target",
        scaling_conf={
            "num_workers": 2,
            "use_gpu": False
        },
        boost_round=20,
        training_params={
            "objective": "binary:logistic",
            "eval_metric": ["logloss", "error"],
        },
        preprocess_pipeline=StandardScaler(
            columns=["mean radius", "mean texture"]
        )
    )

    with open("datasets/xgboost_test/result.json", "w+", encoding='utf-8') as file_obj:
        json.dump(result.metrics, file_obj)

    return result.checkpoint


@as_asset(
    name="train_vanilla_xgboost_model",
    description="Train native XGBoost Classifier"
)
def train_vanilla_xgboost_model():
    # Dataloading from sklearn
    cancer = load_breast_cancer()
    X = cancer.data
    y = cancer.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.3,
        random_state=1898
    )
    model = xgb.XGBClassifier().fit(X_train, y_train)

    return model


@as_asset(
    name="form_predictor_with_checkpoint",
    description="Test different predictor.",
    io_manager_key="json_io_manager"
)
def form_predictor_with_checkpoint(
        load_breast_cancer_dataset,
        train_xgboost_model_with_ray,
        train_vanilla_xgboost_model
):
    dataset = load_breast_cancer_dataset
    df = pd.read_json(dataset['test'])
    test_dataset = ray.data.from_pandas(df)

    # Ray predictor
    ray_ckpt = train_xgboost_model_with_ray
    ray_xgb_predictor = compose_xgboost_batch_predictor(ray_ckpt)

    # Vanilla predictor
    vanilla_model = train_vanilla_xgboost_model
    vanilla_ckpt = convert_xgboost_model_into_checkpoint(xgb_model=vanilla_model)
    vanilla_xgb_predictor = compose_xgboost_batch_predictor(vanilla_ckpt)

    # Predicting
    print("Start predicting...")
    ray_predicted_prob: Dataset | DatasetPipeline = ray_xgb_predictor.predict(test_dataset)
    print("Done prediction! Results:")
    ray_predicted_prob.show()
    print("Finished")

    print("Start predicting...")
    vanilla_predicted_prob: Dataset | DatasetPipeline = vanilla_xgb_predictor.predict(test_dataset)
    print("Done prediction! Results:")
    vanilla_predicted_prob.show()
    print("Finished")

    # Form output
    result = {
        "ray_predicted_results": ray_predicted_prob.to_pandas().to_dict(),
        "vanilla_predicted_results": vanilla_predicted_prob.to_pandas().to_dict()
    }

    return result


defs = form_definitions(
    assets=[
        load_breast_cancer_dataset, train_xgboost_model_with_ray,
        train_vanilla_xgboost_model, form_predictor_with_checkpoint
    ],
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


ray.shutdown()
