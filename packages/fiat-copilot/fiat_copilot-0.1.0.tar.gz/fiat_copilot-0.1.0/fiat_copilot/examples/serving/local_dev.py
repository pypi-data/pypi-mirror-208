import starlette.requests
from ray import serve


@serve.deployment
class Doubler:
    def double_input(self, s: str):
        return s + " " + s


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "initial_replicas": 1,
        "max_replicas": 1,
        "target_num_ongoing_requests_per_replica": 10
    },
    name="double-hello",
    route_prefix="/hello"
)
class HelloDeployment:
    def __init__(self, doubler):
        self.doubler = doubler

    async def say_hello_twice(self, name: str):
        ref = await self.doubler.double_input.remote(f"Hello, {name}!")
        return await ref

    async def __call__(self, request: starlette.requests.Request):
        return await self.say_hello_twice(request.query_params["name"])


graph = HelloDeployment.bind(Doubler.bind())
