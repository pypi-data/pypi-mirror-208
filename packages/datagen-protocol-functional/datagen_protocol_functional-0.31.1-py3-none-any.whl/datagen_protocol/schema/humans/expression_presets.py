from enum import Enum

from datagen_protocol.schema.humans.human import ExpressionName

from datagen_protocol.schema.humans.presets.expression_presets.anger import ANGER_PRESET
from datagen_protocol.schema.humans.presets.expression_presets.contempt import CONTEMPT_PRESET
from datagen_protocol.schema.humans.presets.expression_presets.disgust import DISGUST_PRESET
from datagen_protocol.schema.humans.presets.expression_presets.fear import FEAR_PRESET
from datagen_protocol.schema.humans.presets.expression_presets.happiness import HAPPINESS_PRESET
from datagen_protocol.schema.humans.presets.expression_presets.mouth_open import MOUTH_OPEN_PRESET
from datagen_protocol.schema.humans.presets.expression_presets.sadness import SADNESS_PRESET
from datagen_protocol.schema.humans.presets.expression_presets.surprise import SURPRISE_PRESET


class ExpressionPresets(Enum):
    ANGER = ExpressionName.ANGER, ANGER_PRESET
    CONTEMPT = ExpressionName.CONTEMPT, CONTEMPT_PRESET
    DISGUST = ExpressionName.DISGUST, DISGUST_PRESET
    FEAR = ExpressionName.FEAR, FEAR_PRESET
    HAPPINESS = ExpressionName.HAPPINESS, HAPPINESS_PRESET
    MOUTH_OPEN = ExpressionName.MOUTH_OPEN, MOUTH_OPEN_PRESET
    SADNESS = ExpressionName.SADNESS, SADNESS_PRESET
    SURPRISE = ExpressionName.SURPRISE, SURPRISE_PRESET
    NONE = ExpressionName.NEUTRAL, {}

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: str, expression_preset: dict):
        self.expression_preset = expression_preset

    def get_expression_preset(self) -> dict:
        return self.expression_preset
