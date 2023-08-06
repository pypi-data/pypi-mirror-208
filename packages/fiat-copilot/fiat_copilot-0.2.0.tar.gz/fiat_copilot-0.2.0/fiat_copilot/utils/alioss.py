import pickle
import sys
from typing import Any

import oss2

from fiat_copilot.utils.config import get_logger

logger = get_logger()


# consumed_bytes表示已上传的数据量。
# total_bytes表示待上传的总数据量。当无法确定待上传的数据长度时，total_bytes的值为None。
def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end='')
        sys.stdout.flush()


def download_object_with_stream(
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        bucket: str,
        obj_key: str
):
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(
        auth=auth,
        endpoint=f"https://{endpoint}",
        bucket_name=bucket
    )

    # progress_callback为可选参数，用于实现进度条功能。
    with bucket.get_object(
            key=obj_key,
            progress_callback=percentage
    ) as object_stream:
        buf = object_stream.read()
        # 由于get_object接口返回的是一个stream流，需要执行read()后才能计算出返回Object数据的CRC checksum，因此需要在调用该接口后进行CRC校验。
        if object_stream.client_crc != object_stream.server_crc:
            print("The CRC checksum between client and server is inconsistent!")
        obj = pickle.loads(buf)

    return obj


def upload_object_with_stream(
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        bucket: str,
        obj_key: str,
        obj_data: Any
):
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(
        auth=auth,
        endpoint=f"https://{endpoint}",
        bucket_name=bucket
    )

    # progress_callback为可选参数，用于实现进度条功能。
    buf = pickle.dumps(
        obj=obj_data,
        protocol=pickle.HIGHEST_PROTOCOL
    )
    resp = bucket.put_object(
        key=obj_key,
        data=buf,
        progress_callback=percentage
    )

    return resp
