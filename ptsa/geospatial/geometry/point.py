from __future__ import annotations

from typing import Any

import geographiclib.geodesic
import shapely

from ptsa.geospatial.geometry.core import Coordinate, GeometryCore
from ptsa.geospatial.geometry.enumeration import EPSG_Type


class GeometryPoint(GeometryCore[Coordinate, shapely.Point]):
    @property
    def EPSG_4326_yx(self) -> str:
        item = self.EPSG_4326
        return f"{item.y},{item.x}"

    @property
    def EPSG_4326_xy(self) -> str:
        item = self.EPSG_4326
        return f"{item.x},{item.y}"

    @property
    def EPSG_3857_xy(self) -> str:
        item = self.EPSG_3857
        return f"{item.y},{item.x}"

    def __init__(self, EPSG: EPSG_Type, latitude: float, longitude: float, tags: dict[str, Any] | None = None):
        super().__init__(EPSG, tags)
        self.item = shapely.Point(longitude, latitude)
        self.key: bytes = self.EPSG_4326.wkb

    @staticmethod
    def from_coordinate(EPSG: EPSG_Type, coordinate: Coordinate) -> GeometryPoint:
        return GeometryPoint(EPSG, coordinate[1], coordinate[0])


class GeometryPointBearing:
    def __init__(self, EPSG: EPSG_Type, origin: GeometryPoint, destination: GeometryPoint):
        self.category: EPSG_Type = EPSG
        self.origin: GeometryPoint = origin
        self.destination: GeometryPoint = destination
        self.key: bytes = self.origin.key + self.destination.key
        self.tags: dict[str, Any] = {}

        result = geographiclib.geodesic.Geodesic.WGS84.Inverse(origin.EPSG_4326.y, origin.EPSG_4326.x, destination.EPSG_4326.y, destination.EPSG_4326.x)
        self.bearing_degree: float = result["azi1"]
        # self.bearing_degree = 0.0     [Destination is NORTH OF Origin]
        # self.bearing_degree = 90.0    [Destination is EAST OF Origin]
        # self.bearing_degree = 180.0   [Destination is SOUTH OF Origin] OR [Origin == Destination]
        # self.bearing_degree = -90.0   [Destination is WEST OF Origin]

    def is_same_direction_degree(self, candidate_degree: float, threshold_degree: float):
        diff = abs(self.bearing_degree - candidate_degree)
        diff = min(diff, 360.0 - diff)
        return diff <= threshold_degree

    def is_opposite_direction_degree(self, candidate_degree: float, threshold_degree: float):
        diff = abs(self.bearing_degree - candidate_degree)
        diff = min(diff, 360.0 - diff)
        return abs(diff - 180.0) <= threshold_degree

    @staticmethod
    def from_coordinates(EPSG: EPSG_Type, origin: Coordinate, destination: Coordinate) -> GeometryPointBearing:
        return GeometryPointBearing(EPSG, GeometryPoint.from_coordinate(EPSG, origin), GeometryPoint.from_coordinate(EPSG, destination))
