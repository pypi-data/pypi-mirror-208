from enum import Enum
from typing import Optional

from datagen_protocol.config import conf
from datagen_protocol.schema import fields
from datagen_protocol.schema.attributes import AccessoryPosition, Gender, GlassesStyle, MaskStyle
from datagen_protocol.schema.base import Asset, AssetAttributes, AttributesList, SchemaBaseModel
from pydantic.fields import Field


class AccessoryAttributes(AssetAttributes):
    gender: AttributesList[Gender]
    supported_position: AttributesList[AccessoryPosition]


class GlassesAttributes(AccessoryAttributes):
    style: GlassesStyle


class Color(str, Enum):
    BLACK = "black"
    WHITE = "white"
    LIGHT_BLUE = "light_blue"
    BLUE = "blue"
    RED = "red"
    LIGHT_RED = "light_red"
    PINK = "pink"
    GREEN = "green"
    APPLE_GREEN = "apple_green"
    DARK_GREEN = "dark_green"
    YELLOW = "yellow"
    LIGHT_YELLOW = "light_yellow"
    ORANGE = "orange"
    ORANGE_RED = "orange_red"
    GRAY = "gray"
    WHEAT = "wheat"
    BROWN = "brown"
    SILVER = "silver"
    ROSE_GOLD = "rose_gold"
    ICE_BLUE = "ice_blue"
    PURPLE = "purple"
    GOLD = "gold"
    ROSE_RED = "rose_red"


class GlassesPosition(str, Enum):
    ON_NOSE = "on_nose"


class Glasses(Asset[GlassesAttributes]):
    lens_color: Color = fields.enum(Color, conf["accessories"]["glasses"]["lens"]["color"])
    lens_reflectivity: float = fields.numeric(conf["accessories"]["glasses"]["lens"]["reflectivity"])
    lens_transparency: float = fields.numeric(conf["accessories"]["glasses"]["lens"]["transparency"])
    frame_color: Color = fields.enum(Color, conf["accessories"]["glasses"]["frame"]["color"])
    frame_metalness: float = fields.numeric(conf["accessories"]["glasses"]["frame"]["metalness"])
    position: GlassesPosition = fields.enum(GlassesPosition, conf["accessories"]["glasses"]["position"])


class MaskAttributes(AccessoryAttributes):
    style: MaskStyle


class MaskPosition(str, Enum):
    ON_NOSE = "on_nose"
    ON_MOUTH = "on_mouth"
    ON_CHIN = "on_chin"


class MaskTexture(str, Enum):
    CLOTH = "cloth"
    DIAMOND_PATTERN = "diamond_pattern"
    WOVEN = "woven"


class Mask(Asset[MaskAttributes]):
    color: Color = fields.enum(Color, conf["accessories"]["mask"]["color"])
    texture: MaskTexture = fields.enum(MaskTexture, conf["accessories"]["mask"]["texture"])
    position: MaskPosition = fields.enum(MaskPosition, conf["accessories"]["mask"]["position"])
    roughness: float = fields.numeric(conf["accessories"]["mask"]["roughness"])


class Accessories(SchemaBaseModel):
    glasses: Optional[Glasses]
    mask: Optional[Mask]
