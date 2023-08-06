from enum import Enum

from pydantic import BaseModel


class AppDescription(BaseModel):
    host: str = "127.0.0.1",
    port: int = 0,
    name: str = "test",
    route_prefix: str = "/fiat/serve"
    resource_config: dict


class ServiceType(Enum):
    Text = "text"
    Image = "image"
    Tabular = "tabular"
