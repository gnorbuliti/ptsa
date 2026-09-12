from __future__ import annotations

import geographiclib.geodesic
import shapely
import shapely.ops

from sptg_geospatial.geometry.constant import transform_3857_to_4326
from sptg_geospatial.geometry.core import Coordinate, GeometryCore
from sptg_geospatial.geometry.enumeration import EPSG_Type
from sptg_geospatial.geometry.point import GeometryPoint, GeometryPointBearing


class GeometryLineString(GeometryCore[shapely.LineString]):
    def __init__(self, coordinates: list[Coordinate], EPSG: EPSG_Type | None = EPSG_Type.EPSG_4326):
        super().__init__(EPSG)
        self.item = shapely.LineString(coordinates)
        self.key: bytes = self.EPSG_4326.wkb
        self.start: GeometryPointBearing = GeometryPointBearing.from_coordinates(self.EPSG_4326.coords[1], self.EPSG_4326.coords[0])
        self.end: GeometryPointBearing = GeometryPointBearing.from_coordinates(self.EPSG_4326.coords[-2], self.EPSG_4326.coords[-1])

        WGS84 = geographiclib.geodesic.Geodesic.WGS84
        inv: dict[str, float] = WGS84.Inverse(self.start.destination.EPSG_4326.y, self.start.destination.EPSG_4326.x, self.end.destination.EPSG_4326.y, self.end.destination.EPSG_4326.x)
        self.displacement: float = inv["s12"]

        mid: dict[str, float] = WGS84.Direct(self.start.destination.EPSG_4326.y, self.start.destination.EPSG_4326.x, inv["azi1"], self.displacement / 2)
        self.centre = GeometryPoint(mid["lat2"], mid["lon2"], EPSG_Type.EPSG_4326)

    def reverse(self) -> GeometryLineString:
        return GeometryLineString(list(self.EPSG_4326.coords)[::-1], self.category)

    def simplify(self, tolerance_metre=0.05) -> GeometryLineString:
        simplified = self.EPSG_3857.simplify(tolerance=tolerance_metre, preserve_topology=True)
        return GeometryLineString(list(shapely.ops.transform(transform_3857_to_4326, simplified).coords), self.category)
