from enum import Enum

from datagen_protocol.config import conf
from datagen_protocol.schema import fields
from datagen_protocol.schema.base import SchemaBaseModel
from datagen_protocol.schema.d3 import Point, Rotation


class LightType(str, Enum):
    NIR = "nir"


class Light(SchemaBaseModel):
    light_type: LightType
    beam_angle: float = fields.numeric(conf["light"]["beam_angle"])
    brightness: float = fields.numeric(conf["light"]["brightness"])
    falloff: float = fields.numeric(conf["light"]["falloff"])
    location: Point = fields.point(conf["light"]["location"])
    rotation: Rotation = fields.rotation(conf["light"]["rotation"])
