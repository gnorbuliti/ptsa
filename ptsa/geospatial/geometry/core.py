from __future__ import annotations

from typing import Any

import shapely
import shapely.geometry.base
import shapely.ops

from ptsa.geospatial.geometry.constant import transform_3857_to_4326, transform_4326_to_3857
from ptsa.geospatial.geometry.enumeration import EPSG_Type

Coordinate2D = tuple[float, float]
Coordinate3D = tuple[float, float, float]
Coordinate = Coordinate2D | Coordinate3D


class GeometryCore[T, U: shapely.geometry.base.BaseGeometry]:
    @property
    def EPSG_3857(self) -> U:
        match self.category:
            case EPSG_Type.EPSG_3857:
                return self.item
            case EPSG_Type.EPSG_4326:
                self._EPSG_3857 = shapely.ops.transform(transform_4326_to_3857, self.item)
                return self._EPSG_3857
            case _:
                return self.item

    @property
    def EPSG_4326(self) -> U:
        match self.category:
            case EPSG_Type.EPSG_3857:
                self._EPSG_4326 = shapely.ops.transform(transform_3857_to_4326, self.item)
                return self._EPSG_4326
            case EPSG_Type.EPSG_4326:
                return self.item
            case _:
                return self.item

    def __init__(self, EPSG: EPSG_Type, tags: dict[str, Any] | None = None):
        self.category: EPSG_Type = EPSG
        self.item: shapely.geometry.base.BaseGeometry | None = None
        self._EPSG_4326: U | None = None
        self._EPSG_3857: U | None = None
        self.tags: dict[str, Any] = tags or {}

    def reset(self, EPSG: EPSG_Type, coordinates: T):
        self.category = EPSG
        self.item = U(coordinates)
        self._EPSG_4326: U | None = None
        self._EPSG_3857: U | None = None

    @staticmethod
    def are_same_direction_degree(reference_degree: float, candidate_degree: float, threshold_degree: float):
        diff = abs(reference_degree - candidate_degree)
        diff = min(diff, 360.0 - diff)
        return diff <= threshold_degree

    @staticmethod
    def are_opposite_direction_degree(reference_degree: float, candidate_degree: float, threshold_degree: float):
        diff = abs(reference_degree - candidate_degree)
        diff = min(diff, 360.0 - diff)
        return abs(diff - 180.0) <= threshold_degree
