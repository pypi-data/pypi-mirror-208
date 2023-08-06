from enum import Enum
from typing import Any

from dagster import IOManager, InputContext, OutputContext, FilesystemIOManager

from fiat_copilot.utils.alioss import download_object_with_stream, upload_object_with_stream
from fiat_copilot.utils.config import get_logger, get_application_conf

logger = get_logger()


class PersistStorage(Enum):
    Local = "local"
    JDBC = "jdbc"
    S3 = "s3"
    OSS = "oss"
    OBS = "obs"
    COS = "cos"


class DataFormat(Enum):
    Binary = ".bin"
    JSON = ".json"
    CSV = ".csv"
    PlainText = ".txt"
    Parquet = ".parquet"


class OSSIOManager(IOManager):
    def __init__(self, file_path: str, storage_format: DataFormat):
        self.path = file_path
        conf: dict = get_application_conf()
        self.bucket_name: str = conf['oss']['bucket_name']
        self.endpoint: str = conf['oss']['endpoint']
        self.accessKey: dict = conf['oss']['accessKey']
        self.format_suffix = storage_format.value

    def load_input(self, context: InputContext):
        key = f"{context.asset_key.path[0]}" + self.format_suffix
        obj_name = f"fiat_persistence/{self.path}/{key}"

        logger.debug(f"Trying to load asset: {obj_name}")
        ret_obj = download_object_with_stream(
            access_key_id=self.accessKey['ID'],
            access_key_secret=self.accessKey['Secret'],
            endpoint=self.endpoint,
            bucket=self.bucket_name,
            obj_key=obj_name
        )
        logger.debug(f"Asset loaded: {ret_obj}")

        return ret_obj

    def handle_output(self, context: OutputContext, obj: Any):
        key = f"{context.asset_key.path[0]}" + self.format_suffix
        obj_name = f"fiat_persistence/{self.path}/{key}"

        logger.debug(f"Trying to upload asset: {obj_name}")
        ret = upload_object_with_stream(
            access_key_id=self.accessKey['ID'],
            access_key_secret=self.accessKey['Secret'],
            endpoint=self.endpoint,
            bucket=self.bucket_name,
            obj_key=obj_name,
            obj_data=obj
        )
        logger.debug(f"File submitted with status: {ret.status}")

        return


def get_io_manager(
        medium: PersistStorage = PersistStorage.Local,
        base_path: str = "tmp",
        data_format: DataFormat = DataFormat.Binary
):
    if medium is PersistStorage.Local:
        return FilesystemIOManager(base_dir=base_path)
    elif medium is PersistStorage.OSS:
        return OSSIOManager(
            file_path=base_path,
            storage_format=data_format
        )
