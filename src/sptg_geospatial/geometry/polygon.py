from __future__ import annotations

from collections.abc import Sequence

import shapely
import shapely.ops

from sptg_geospatial.geometry.constant import transform_3857_to_4326
from sptg_geospatial.geometry.core import Coordinate, GeometryCore
from sptg_geospatial.geometry.enumeration import EPSG_Type


class GeometryPolygon(GeometryCore[shapely.Polygon]):
    def __init__(self, coordinates: Sequence[Coordinate], EPSG: EPSG_Type | None = EPSG_Type.EPSG_4326):
        super().__init__(EPSG)
        self.item = shapely.Polygon(coordinates[0], *coordinates[1:])
        self.key: bytes = self.EPSG_4326.wkb

    def reverse(self) -> GeometryPolygon:
        exterior: list[Coordinate] = list(self.EPSG_4326.exterior.coords)[::-1]
        interiors: list[list[Coordinate]] = [list(interior.coords)[::-1] for interior in self.EPSG_4326.interiors]
        return GeometryPolygon([exterior, interiors], self.category)

    def simplify(self, tolerance_metre=0.05) -> GeometryPolygon:
        simplified = self.EPSG_3857.simplify(tolerance=tolerance_metre, preserve_topology=True)
        transformed: shapely.Polygon = shapely.ops.transform(transform_3857_to_4326, simplified)
        exterior: list[Coordinate] = list(transformed.exterior.coords)
        interiors: list[list[Coordinate]] = [list(interior.coords) for interior in transformed.interiors]
        return GeometryPolygon([exterior, interiors], self.category)
