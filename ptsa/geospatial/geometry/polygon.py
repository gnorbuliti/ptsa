from __future__ import annotations

from typing import Any

import shapely

from ptsa.geospatial.geometry.core import Coordinate, GeometryCore
from ptsa.geospatial.geometry.enumeration import EPSG_Type


class GeometryPolygon(GeometryCore[list[list[Coordinate]], shapely.Polygon]):
    @property
    def EPSG_3857_coordinates(self) -> list[list[Coordinate]]:
        coordinates: list[list[Coordinate]] = [list(self.EPSG_3857.exterior.coords)]
        coordinates.extend([list(interior.coords) for interior in self.EPSG_3857.interiors])
        return coordinates

    @property
    def EPSG_4326_coordinates(self) -> list[list[Coordinate]]:
        coordinates: list[list[Coordinate]] = [list(self.EPSG_4326.exterior.coords)]
        coordinates.extend([list(interior.coords) for interior in self.EPSG_4326.interiors])
        return coordinates

    def __init__(self, EPSG: EPSG_Type, coordinates: list[list[Coordinate]], tags: dict[str, Any] | None = None):
        super().__init__(EPSG, tags)
        self.item = shapely.Polygon(coordinates[0], *coordinates[1:])
        self.key: bytes = self.EPSG_4326.wkb

    def reverse(self, in_place: bool = False) -> GeometryPolygon:
        coordinates: list[list[Coordinate]] = [list(self.EPSG_4326.exterior.coords)[::-1]]
        coordinates.extend(list(interior.coords)[::-1] for interior in self.EPSG_4326.interiors)
        if in_place:
            self.reset(EPSG_Type.EPSG_4326, coordinates)
            return self
        else:
            return GeometryPolygon(EPSG_Type.EPSG_4326, coordinates, self.category)

    def simplify(self, tolerance_metre: float) -> GeometryPolygon:
        simplified: shapely.Polygon = self.EPSG_3857.simplify(tolerance=tolerance_metre, preserve_topology=True)
        coordinates: list[list[Coordinate]] = [list(simplified.exterior.coords)]
        coordinates.extend(list(interior.coords) for interior in simplified.interiors)
        return GeometryPolygon(EPSG_Type.EPSG_3857, coordinates, self.category)
