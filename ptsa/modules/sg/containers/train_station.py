from typing import Any

from ptsa.geospatial.geometry.core import Coordinate
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint
from ptsa.geospatial.geometry.polygon import GeometryPolygon


class TrainStationPolygon(GeometryPolygon):
    def __init__(self, EPSG: EPSG_Type, coordinates: list[list[Coordinate]]):
        super().__init__(EPSG, coordinates)
        self.name: str = ""
        self.codes: set[str] = set()
        self.index: int = -1


class TrainStation:
    def __init__(self, row: tuple[Any, ...]):
        self.code: str = str(row[0])
        self.line: str = str(row[1])
        self.abbreviation: str = str(row[2])
        self.english: str = str(row[3])
        self.point = GeometryPoint(EPSG_Type.EPSG_4326, float(row[9]), float(row[10]))
        self.altitude: float = row[11]

        self.point.tags["code"] = self.code
        self.polygons: list[TrainStationPolygon] = []
        self.english_lower: str = self.english.lower()
