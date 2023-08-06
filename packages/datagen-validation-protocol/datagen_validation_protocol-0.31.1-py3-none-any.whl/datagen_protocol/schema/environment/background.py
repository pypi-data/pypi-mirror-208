from typing import Optional

from datagen_protocol.config import conf
from datagen_protocol.schema import fields
from datagen_protocol.schema.attributes import Environment, Generator, HICDomain, TimeOfDay
from datagen_protocol.schema.base import Asset, AssetAttributes, AttributesList


class BackgroundAttributes(AssetAttributes):
    environment: Environment
    time_of_day: TimeOfDay
    generator: Generator
    domain: Optional[AttributesList[HICDomain]] = None


class Background(Asset[BackgroundAttributes]):
    rotation: float = fields.numeric(conf["background"]["rotation"])
    transparent: bool = fields.bool(conf["background"]["transparency"])
