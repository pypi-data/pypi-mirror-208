import logging
from typing import List

from ray import serve
from starlette.requests import Request

logger = logging.getLogger("rich")


class BatchTextGenerator:
    batch_size: int = 4

    def __init__(
            self,
            model,
            batch_handler,
            batch_size: int = 4
    ):
        self.model = model
        self.batch_handler = batch_handler
        self.batch_size = batch_size

    @serve.batch(max_batch_size=batch_size)
    async def handle_batch(self, inputs: List[str]) -> List[str]:
        logger.info(f"Our input array has length: {len(inputs)}")

        outputs = self.batch_handler(self.model, inputs)

        return outputs

    async def __call__(self, requests: List[Request]) -> List[str]:
        ret = await self.handle_batch(
            inputs=[request.query_params["text"] for request in requests]
        )

        return ret


class BatchImageInferencing:
    batch_size: int = 4

    def __init__(
            self,
            model,
            batch_handler,
            batch_size: int = 4
    ):
        self.model = model
        self.batch_handler = batch_handler
        self.batch_size = batch_size

    @serve.batch(max_batch_size=batch_size)
    async def handle_batch(self, inputs: List[str]) -> List[str]:
        logger.info(f"Our input array has length: {len(inputs)}")

        outputs = self.batch_handler(self.model, inputs)

        return outputs

    async def __call__(self, requests: List[Request]) -> List[str]:
        ret = await self.handle_batch(
            inputs=[request.query_params["text"] for request in requests]
        )

        return ret


class BatchTabularPredictor:
    batch_size: int = 4

    def __init__(
            self,
            model,
            batch_handler,
            batch_size: int = 4
    ):
        self.model = model
        self.batch_handler = batch_handler
        self.batch_size = batch_size

    @serve.batch(max_batch_size=batch_size)
    async def handle_batch(self, inputs: List[str]) -> List[str]:
        logger.info(f"Our input array has length: {len(inputs)}")

        outputs = self.batch_handler(self.model, inputs)

        return outputs

    async def __call__(self, requests: List[Request]) -> List[str]:
        ret = await self.handle_batch(
            inputs=[request.query_params["text"] for request in requests]
        )

        return ret
