from __future__ import annotations

from typing import Any

import geographiclib.geodesic
import shapely

from sptg_geospatial.geometry.core import Coordinate, GeometryCore
from sptg_geospatial.geometry.enumeration import EPSG_Type


class GeometryPoint(GeometryCore[shapely.Point]):
    def __init__(self, latitude: float, longitude: float, EPSG: EPSG_Type | None = EPSG_Type.EPSG_4326):
        super().__init__(EPSG)
        self.item = shapely.Point(longitude, latitude)
        self.key: bytes = self.EPSG_4326.wkb

    @staticmethod
    def from_coordinate(coordinate: Coordinate, EPSG: EPSG_Type | None = EPSG_Type.EPSG_4326) -> GeometryPoint:
        return GeometryPoint(coordinate[1], coordinate[0], EPSG)


class GeometryPointBearing(GeometryCore):
    def __init__(self, origin: GeometryPoint, destination: GeometryPoint, EPSG: EPSG_Type | None = EPSG_Type.EPSG_4326):
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
    def from_coordinates(origin: Coordinate, destination: Coordinate, EPSG: EPSG_Type | None = EPSG_Type.EPSG_4326) -> GeometryPointBearing:
        return GeometryPointBearing(GeometryPoint.from_coordinate(origin, EPSG), GeometryPoint.from_coordinate(destination, EPSG))
