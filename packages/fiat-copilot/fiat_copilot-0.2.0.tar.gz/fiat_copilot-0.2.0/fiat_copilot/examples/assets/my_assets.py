import json

import requests
from rich import print

from fiat_copilot.workflow.annotations import as_asset, form_definitions
from fiat_copilot.workflow.ray_utils import adhoc_task_on_ray, ResourceQuota
from fiat_copilot.workflow.storage import PersistStorage, DataFormat, get_io_manager
from fiat_copilot.utils.config import get_application_conf


@as_asset(
    name="get_baidu_html",
    description="get baidu",
    io_manager_key="text_io_manager"
)
def get_baidu_html():
    ret = requests.get("https://www.baidu.com/")
    return ret.text


@as_asset(
    name="get_user_info",
    description="get user information",
    io_manager_key="json_io_manager"
)
def get_user_info():
    with open("application.json", "r+", encoding='utf-8') as file_obj:
        conf: dict = json.load(file_obj)
        info: dict = conf['info']

    return info


@as_asset(
    name="to_json",
    description="convert html to json",
    io_manager_key="json_io_manager"
)
def to_json(get_baidu_html, get_user_info):
    ray_conf = get_application_conf()['ray']
    with adhoc_task_on_ray(
        cluster=ray_conf['cluster'],
        resource=ResourceQuota(
            cpu=ray_conf['resource']['cpu'],
            gpu=ray_conf['resource']['gpu']
        )
    ) as remote_util:
        info_dict = get_user_info
        html = get_baidu_html

        def my_func():
            data = {
                "info": info_dict,
                "text": html
            }
            print(data)
            return data

        result = remote_util(my_func)

    return result


defs = form_definitions(
    assets=[get_baidu_html, get_user_info, to_json],
    resources={
        "default_io_manager": get_io_manager(
            medium=PersistStorage.OSS,
            base_path="test"
        ),
        "json_io_manager": get_io_manager(
            medium=PersistStorage.OSS,
            base_path="test",
            data_format=DataFormat.JSON
        ),
        "text_io_manager": get_io_manager(
            medium=PersistStorage.OSS,
            base_path="test",
            data_format=DataFormat.PlainText
        ),
    }
)
