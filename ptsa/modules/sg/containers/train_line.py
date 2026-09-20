from ptsa.geospatial.geometry.core import Coordinate
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.linestring import GeometryLineString
from ptsa.geospatial.geometry.point import GeometryPointBearing
from ptsa.modules.sg.containers.train_station import TrainStation, TrainStationDistance


class TrainLineGeometry(GeometryLineString):
    def __init__(self, EPSG: EPSG_Type, coordinates: list[Coordinate]):
        super().__init__(EPSG, coordinates)
        self.start_station: TrainStation = None
        self.end_station: TrainStation | None = None

    def simplify_geometry(self, tolerance_metre: float):
        item: GeometryLineString = self.simplify(tolerance_metre)
        super().__init__(EPSG_Type.EPSG_4326, list(item.EPSG_4326.coords))

    @staticmethod
    def nearest_train_stations(train_stations: list[TrainStation], bearing_point: GeometryPointBearing, threshold_distance: float) -> list[TrainStationDistance]:
        distances: list[TrainStationDistance] = [TrainStationDistance(i, 0.0) for i in train_stations if any(j.EPSG_4326.covers(bearing_point.destination.EPSG_4326) for j in i.polygons)]
        if not distances:
            distances = [TrainStationDistance(i, j.EPSG_3857.distance(bearing_point.destination.EPSG_3857)) for i in train_stations for j in i.polygons]
            distances = [i for i in distances if i.distance <= threshold_distance]
            distances.sort(key=lambda x: x.distance)
        return distances
