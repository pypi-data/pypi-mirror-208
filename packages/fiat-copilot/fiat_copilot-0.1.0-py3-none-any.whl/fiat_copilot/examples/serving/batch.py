from typing import List

from rich import print
from transformers import pipeline

from serving.context import adhoc_serving_setup, get_serving_result_with_handle
from serving.domain import AppDescription, ServiceType
from utils.config import get_application_conf


def model_inference(model, inputs: List[str]):
    model_results = model(inputs)

    return [result[0]["generated_text"] for result in model_results]


if __name__ == '__main__':
    # Load your model
    model = pipeline("text-generation", "gpt2")
    # Get ray config
    conf: dict = get_application_conf()
    serving_conf: dict = conf['ray']['serving']

    with adhoc_serving_setup(
            ray_cluster=None,
            serving_model=model,
            handle_func=model_inference,
            serving_type=ServiceType.Text,
            app_description=AppDescription(
                host="127.0.0.1",
                port=0,
                name="test",
                route_prefix="/fiat/serve",
                resource_config=serving_conf
            ),
    ) as serve_handle:
        input_batch = [
            'Once upon a time,',
            'Hi my name is Lewis and I like to',
            'My name is Mary, and my favorite',
            'My name is Clara and I am',
            'My name is Julien and I like to',
            'Today I accidentally',
            'My greatest wish is to',
            'In a galaxy far far away',
            'My best talent is',
        ]
        print("Input batch is", input_batch)

        result_batch = get_serving_result_with_handle(
            handle=serve_handle,
            input_batch=input_batch
        )

        print("Result batch is", result_batch)
