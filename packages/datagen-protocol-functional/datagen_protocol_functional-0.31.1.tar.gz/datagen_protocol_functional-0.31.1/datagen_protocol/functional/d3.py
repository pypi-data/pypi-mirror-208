import abc
from typing import Type, TypeVar

import numpy as np
from datagen_protocol.schema import d3 as core_3d_schema
from pydantic import BaseModel, Field


class Functional3dObject(abc.ABC):
    @abc.abstractmethod
    def to_array(self) -> np.ndarray:
        pass

    @classmethod
    @abc.abstractmethod
    def from_array(cls, arr: np.ndarray):
        pass


class Point(core_3d_schema.Point, Functional3dObject):
    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr: np.ndarray):
        return cls(x=arr[0], y=arr[1], z=arr[2])


class Vector(core_3d_schema.Vector, Functional3dObject):
    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr: np.ndarray):
        return cls(x=arr[0], y=arr[1], z=arr[2])


class Rotation(core_3d_schema.Rotation, Functional3dObject):
    def to_array(self) -> np.ndarray:
        return self._to_yaw_pitch_roll()

    def _to_yaw_pitch_roll(self) -> np.ndarray:
        return np.array([self.yaw, self.pitch, self.roll])

    @classmethod
    def from_array(cls, arr: np.ndarray):
        return cls._from_yaw_pitch_roll(arr)

    @classmethod
    def _from_yaw_pitch_roll(cls, arr: np.ndarray):
        return cls(yaw=arr[0], pitch=arr[1], roll=arr[2])


core_3d_schema.Point = Point
core_3d_schema.Rotation = Rotation
core_3d_schema.Vector = Vector
