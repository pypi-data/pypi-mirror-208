import json
import sys

from pprint import pprint as ppt

import oss2

# admin
RAM = {
    "ID": "LTAI5tLsHgQV221ZupXQWhaw",
    "Secret": "hOUlXZUKVfbVvuS9KfCITGGimyjDDt"
}
ADMIN = {
    "ID": "LTAI5tHhFnRehhHsh1Jbfj87",
    "Secret": "7DsJLJwEn0R0n4xU1O4QC5Zr6cV9lf"
}
# ram
conf = {
    "accessKey": ADMIN,
    "bucket_name": "ken-database",
    "endpoint": "oss-cn-beijing.aliyuncs.com"
}


# consumed_bytes表示已上传的数据量。
# total_bytes表示待上传的总数据量。当无法确定待上传的数据长度时，total_bytes的值为None。
def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end='')
        sys.stdout.flush()


if __name__ == '__main__':
    auth = oss2.Auth(conf['accessKey']['ID'], conf['accessKey']['Secret'])
    bucket = oss2.Bucket(auth, f"https://{conf['endpoint']}", conf['bucket_name'])

    ppt(f"Auth: {auth}")
    ppt(f"Bucket: {bucket}")

    # progress_callback为可选参数，用于实现进度条功能。
    obj_key = "fiat_persistence/test.json"
    put_ret = bucket.put_object(
        key=obj_key,
        data=json.dumps(conf),
        progress_callback=percentage
    )

    ppt(f"File submitted: {put_ret.__dict__}")
    ppt(f"Response: {put_ret.resp}")

    # get it
    with bucket.get_object(
        key=obj_key,
        progress_callback=percentage
    ) as object_stream:
        buf = object_stream.read()
        get_obj = json.loads(buf)

    ppt(f"File downloaded: {get_obj}")


