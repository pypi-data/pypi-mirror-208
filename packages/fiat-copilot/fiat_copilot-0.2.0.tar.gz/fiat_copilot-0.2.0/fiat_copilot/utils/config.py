import json
import logging

import click
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[click])]
)


def get_logger():
    logger = logging.getLogger("rich")

    return logger


def get_application_conf() -> dict:
    try:
        with open("application.json", "r+", encoding="utf-8") as file_io:
            conf = json.load(file_io)
    except FileNotFoundError:
        raise SystemExit

    return conf
