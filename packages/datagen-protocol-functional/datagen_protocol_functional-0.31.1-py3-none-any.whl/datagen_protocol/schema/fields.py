from typing import Type

from box import BoxKeyError
from datagen_protocol.schema import d3 as core_3d_schema
from pydantic import Field, HttpUrl


def numeric(field_config) -> Field:
    field_params = _parse_common_params(field_config)
    try:
        field_params["le"] = field_config.max
    except BoxKeyError:
        pass
    try:
        field_params["ge"] = field_config.min
    except BoxKeyError:
        pass
    return Field(**field_params)


def enum(enum_type: Type, field_config) -> Field:
    field_params = _parse_common_params(field_config)
    try:
        default_val_str = field_params["default"]
        field_params["default"] = enum_type[default_val_str]
    except KeyError:
        pass
    return Field(**field_params)


def bool(field_config) -> Field:
    field_params = _parse_common_params(field_config)
    return Field(**field_params)


def point(field_config) -> Field:
    return Field(
        default_factory=lambda: core_3d_schema.Point(
            x=field_config.x.default, y=field_config.y.default, z=field_config.z.default
        )
    )


def rotation(field_config) -> Field:
    return Field(
        default_factory=lambda: core_3d_schema.Rotation(
            yaw=field_config.yaw.default, pitch=field_config.pitch.default, roll=field_config.roll.default
        )
    )


def vector(field_config) -> Field:
    return Field(
        default_factory=lambda: core_3d_schema.Vector(
            x=field_config.x.default, y=field_config.y.default, z=field_config.z.default
        )
    )


def _parse_common_params(field_config) -> dict:
    field_params = {}
    try:
        field_params["title"] = field_config.title
    except BoxKeyError:
        pass
    try:
        field_params["description"] = field_config.description
    except BoxKeyError:
        pass
    try:
        field_params["default"] = field_config.default
    except BoxKeyError:
        pass
    return field_params
