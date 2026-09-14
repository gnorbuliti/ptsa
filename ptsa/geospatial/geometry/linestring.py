from __future__ import annotations

import sys
from typing import Any

import geographiclib.geodesic
import shapely

from ptsa.geospatial.geometry.core import Coordinate, GeometryCore
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint, GeometryPointBearing


class GeometryLineString(GeometryCore[list[Coordinate], shapely.LineString]):
    def __init__(self, EPSG: EPSG_Type, coordinates: list[Coordinate], tags: dict[str, Any] | None = None):
        super().__init__(EPSG, tags)
        self.item = shapely.LineString(coordinates)
        self.key: bytes = self.EPSG_4326.wkb
        self.start: GeometryPointBearing = GeometryPointBearing.from_coordinates(self.EPSG_4326.coords[1], self.EPSG_4326.coords[0])
        self.end: GeometryPointBearing = GeometryPointBearing.from_coordinates(self.EPSG_4326.coords[-2], self.EPSG_4326.coords[-1])

        WGS84 = geographiclib.geodesic.Geodesic.WGS84
        inv: dict[str, float] = WGS84.Inverse(self.start.destination.EPSG_4326.y, self.start.destination.EPSG_4326.x, self.end.destination.EPSG_4326.y, self.end.destination.EPSG_4326.x)
        self.displacement: float = inv["s12"]

        mid: dict[str, float] = WGS84.Direct(self.start.destination.EPSG_4326.y, self.start.destination.EPSG_4326.x, inv["azi1"], self.displacement / 2)
        self.centre = GeometryPoint(mid["lat2"], mid["lon2"], EPSG_Type.EPSG_4326)

    def reverse(self, in_place: bool = False) -> GeometryLineString:
        coordinates: list[Coordinate] = list(self.EPSG_4326.coords)[::-1]
        if in_place:
            self.reset(EPSG_Type.EPSG_4326, coordinates)
            return self
        else:
            return GeometryLineString(EPSG_Type.EPSG_4326, coordinates, self.tags)

    def simplify(self, tolerance_metre: float = 0.05, in_place: bool = False) -> GeometryLineString:
        simplified: shapely.LineString = self.EPSG_3857.simplify(tolerance=tolerance_metre, preserve_topology=True)
        if in_place:
            self.reset(EPSG_Type.EPSG_3857, list(simplified.coords))
            return self
        else:
            return GeometryLineString(EPSG_Type.EPSG_3857, list(simplified.coords), self.tags)

    def flatten_zigzag(self, envelope_tolerance_degree: float = sys.float_info.max, in_place: bool = False) -> GeometryLineString:
        coordinates: list[Coordinate] = list(self.EPSG_4326.coords)
        if len(coordinates) < 3:
            if in_place:
                self.reset(EPSG_Type.EPSG_4326, coordinates)
                return self
            else:
                return GeometryLineString(EPSG_Type.EPSG_4326, coordinates, self.tags)

        cleaned: list[Coordinate] = [coordinates[0]]
        for i in range(1, len(coordinates) - 1):
            if coordinates[i] == cleaned[-1] or coordinates[i] == coordinates[i + 1]:
                continue
            x1, y1 = cleaned[-1]
            x2, y2 = coordinates[i]
            x3, y3 = coordinates[i + 1]
            result12 = geographiclib.geodesic.Geodesic.WGS84.Inverse(y1, x1, y2, x2)
            result23 = geographiclib.geodesic.Geodesic.WGS84.Inverse(y2, x2, y3, x3)
            if GeometryCore.are_same_direction_degree(result12["azi1"], result23["azi1"], envelope_tolerance_degree):
                cleaned.append(coordinates[i])
        cleaned.append(coordinates[-1])
        coordinates = cleaned

        if in_place:
            self.reset(EPSG_Type.EPSG_4326, coordinates)
            return self
        else:
            return GeometryLineString(EPSG_Type.EPSG_4326, coordinates, self.tags)
