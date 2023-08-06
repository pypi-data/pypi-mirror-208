from contextlib import contextmanager
from enum import Enum

from obs import ObsClient


class StatusCode(Enum):
    Succeed = 0
    Failure = 1


@contextmanager
def init_obs_client(
        key_id: str,
        key_secret: str,
        endpoint: str
):
    # 创建ObsClient实例
    obsClient = ObsClient(
        access_key_id=key_id,
        secret_access_key=key_secret,
        server=endpoint
    )

    try:
        # 使用访问OBS
        yield obsClient
    finally:
        # 关闭obsClient
        obsClient.close()


async def upload_file_with_stream(
        obs_client: ObsClient,
        bucket: str,
        file_path: str
):
    try:
        with open(file_path, "rb") as file_io:
            resp = obs_client.putContent(
                bucketName=bucket,
                objectKey=file_path,
                content=file_io
            )

        if resp.status < 300:
            print('requestId:', resp.requestId)
        else:
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
    except RuntimeError:
        import traceback

        print(traceback.format_exc())

        return StatusCode.Failure

    return StatusCode.Succeed


async def download_file_with_stream(
        obs_client: ObsClient,
        bucket: str,
        file_path: str,
        download_path: str
):
    try:
        resp = obs_client.getObject(
            bucketName=bucket,
            objectKey=file_path,
            downloadPath=f"{download_path}/{file_path}",
            loadStreamInMemory=False
        )

        if resp.status < 300:
            print('requestId:', resp.requestId)
            # 读取对象内容
            # while True:
            #     chunk = resp.body.response.read(65536)
            #     if not chunk:
            #         break
            #     print(chunk)
            # resp.body.response.close()
        else:
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
    except RuntimeError:
        import traceback

        print(traceback.format_exc())

        return StatusCode.Failure

    return StatusCode.Succeed
