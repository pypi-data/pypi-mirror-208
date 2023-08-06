import asyncio

from rich import print

from utils.huaweiobs import init_obs_client, upload_file_with_stream, download_file_with_stream

# Username	Access Key ID	Secret Access Key
# fiat	DAFZA5PA4WWXERRR2X6O	5I4w9Ktvhqgf9dht0qJK4ZUrfctwc48PBVXNdY40

user_info = {
    "id": "DAFZA5PA4WWXERRR2X6O",
    "secret": "5I4w9Ktvhqgf9dht0qJK4ZUrfctwc48PBVXNdY40",
    "endpoint": "obs.cn-north-4.myhuaweicloud.com",
    "bucket": "ken-datasets"
}


async def upload_parquet_bulk(base_path: str):
    import os

    filenames = os.listdir(base_path)

    with init_obs_client(
            key_id=user_info['id'],
            key_secret=user_info['secret'],
            endpoint=user_info['endpoint'],
    ) as client:
        num = 1
        domain = f"{user_info['bucket']}.{user_info['endpoint']}"

        for filename in filenames:
            target = f"{base_path}/{filename}"
            ret = await upload_file_with_stream(
                bucket=user_info['bucket'],
                file_path=target,
                obs_client=client
            )
            num += 1

            print(f"[{num}] Status: {ret} - Submitted: '{target}' at bucket: {domain}")

    return True


async def download_parquet_bulk(base_path: str):
    import os

    filenames = os.listdir(base_path)

    with init_obs_client(
            key_id=user_info['id'],
            key_secret=user_info['secret'],
            endpoint=user_info['endpoint'],
    ) as client:
        num = 1
        domain = f"{user_info['bucket']}.{user_info['endpoint']}"

        for filename in filenames:
            target = f"{base_path}/{filename}"
            print(target)
            ret = await download_file_with_stream(
                bucket=user_info['bucket'],
                file_path=target,
                obs_client=client,
                download_path="test"
            )
            num += 1

            print(f"[{num}] Status: {ret} - Downloaded: '{target}' at bucket: {domain}")

    return True


async def main():
    # ret = await upload_parquet_bulk("datasets/breast_cancer")
    ret = await download_parquet_bulk("../datasets/breast_cancer")

    assert ret


if __name__ == '__main__':
    asyncio.run(main())
