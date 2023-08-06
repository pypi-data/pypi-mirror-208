from enum import Enum
from typing import List, Optional

from datagen_protocol.config import conf
from datagen_protocol.schema import fields
from datagen_protocol.schema.attributes import Age, Ethnicity, EyesColor, FacialHairStyle, Gender, HairLength, HairStyle
from datagen_protocol.schema.base import Asset, AssetAttributes, AttributesList, SchemaBaseModel
from datagen_protocol.schema.d3 import Point, Rotation, Vector
from datagen_protocol.schema.environment import Background, Camera, Light
from datagen_protocol.schema.humans.accessories import Accessories
from pydantic import BaseModel, Field


class HairColor(SchemaBaseModel):
    melanin: float = fields.numeric(conf["human"]["hair"]["melanin"])
    redness: float = fields.numeric(conf["human"]["hair"]["redness"])
    whiteness: float = fields.numeric(conf["human"]["hair"]["whiteness"])
    roughness: float = fields.numeric(conf["human"]["hair"]["roughness"])
    index_of_refraction: float = fields.numeric(conf["human"]["hair"]["refraction"])


class HairModel(SchemaBaseModel):
    color_settings: HairColor = Field(default_factory=HairColor)


class HairAttributes(AssetAttributes):
    age_group_match: AttributesList[Age]
    ethnicity_match: AttributesList[Ethnicity]
    gender_match: AttributesList[Gender]
    length: HairLength
    style: AttributesList[HairStyle]


class FacialHairAttributes(AssetAttributes):
    style: FacialHairStyle


class EyebrowsAttributes(AssetAttributes):
    age_group_match: AttributesList[Age]
    ethnicity_match: AttributesList[Ethnicity]
    gender_match: AttributesList[Gender]


class Hair(HairModel, Asset[HairAttributes]):
    pass


class FacialHair(HairModel, Asset[FacialHairAttributes]):
    pass


class Eyebrows(HairModel, Asset[EyebrowsAttributes]):
    pass


class Gaze(SchemaBaseModel):
    distance: float = fields.numeric(conf["human"]["eyes"]["gaze"]["distance"])
    direction: Vector = fields.vector(conf["human"]["eyes"]["gaze"]["direction"])


class EyesAttributes(AssetAttributes):
    color: EyesColor


class Eyes(Asset[EyesAttributes]):
    target_of_gaze: Gaze = Field(default_factory=Gaze)
    eyelid_closure: float = fields.numeric(conf["human"]["eyes"]["eyelid_closure"])
    iris_diameter: float = fields.numeric(conf["human"]["eyes"]["iris_diameter"])
    pupil_diameter: float = fields.numeric(conf["human"]["eyes"]["pupil_diameter"])
    sclera_seed: int = fields.numeric(conf["human"]["eyes"]["sclera_seed"])
    redness: float = fields.numeric(conf["human"]["eyes"]["redness"])


class ExpressionName(str, Enum):
    NEUTRAL = "none"
    HAPPINESS = "happiness"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    FEAR = "fear"
    ANGER = "anger"
    DISGUST = "disgust"
    CONTEMPT = "contempt"
    MOUTH_OPEN = "mouth_open"


class Expression(SchemaBaseModel):
    name: ExpressionName = fields.enum(ExpressionName, conf["human"]["expression"]["name"])
    intensity: float = fields.numeric(conf["human"]["expression"]["intensity"])


# TODO: add blemishes and make SchemaBaseModel the base class
class Head(BaseModel):
    eyes: Eyes
    hair: Optional[Hair]
    eyebrows: Optional[Eyebrows]
    facial_hair: Optional[FacialHair]
    expression: Expression = Field(default_factory=Expression)
    location: Point = fields.point(conf["human"]["head"]["location"])
    rotation: Rotation = fields.rotation(conf["human"]["head"]["rotation"])


class HumanAttributes(AssetAttributes):
    ethnicity: Ethnicity
    age: Age
    gender: Gender


class Human(Asset[HumanAttributes]):
    head: Head


class HumanDatapoint(SchemaBaseModel):
    human: Human
    camera: Camera
    accessories: Optional[Accessories]
    background: Optional[Background]
    lights: Optional[List[Light]]
