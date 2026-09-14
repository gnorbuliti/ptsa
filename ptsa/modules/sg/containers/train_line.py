from ptsa.geospatial.geometry.core import Coordinate
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.linestring import GeometryLineString
from ptsa.modules.sg.containers.train_station import TrainStation


class TrainLineSegment(GeometryLineString):
    def __init__(self, EPSG: EPSG_Type, coordinates: list[Coordinate]):
        super().__init__(EPSG, coordinates)
        self.start_station: TrainStation | None = None
        self.end_station: TrainStation | None = None
