import pickle

from sklearn.datasets import load_breast_cancer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

from rich import print


def get_serialized_obj(path: str):
    with open(path, "rb") as file_obj:
        buf = file_obj.read()
        obj = pickle.loads(buf)

    return obj


def load_xgboost_model():
    model = get_serialized_obj(path="datasets/xgboost_test/train_vanilla_xgboost_model.bin")

    cancer = load_breast_cancer()
    X = cancer.data
    y = cancer.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.3,
        random_state=1898
    )

    y_pred = model.predict(X_test)

    print(confusion_matrix(y_test, y_pred))


def load_final_result():
    data = get_serialized_obj(path="datasets/xgboost_test/form_predictor_with_checkpoint.json")

    print(data)


if __name__ == '__main__':
    load_final_result()
