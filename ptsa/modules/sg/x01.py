import argparse
import asyncio
import enum
import pathlib

import geopandas
import shapely

from ptsa.geospatial.geometry.core import Coordinate
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.modules.sg.constants import PRECISION
from ptsa.modules.sg.containers.train_station import TrainStation, TrainStationPolygon
from ptsa.workflow.task_manager import ApplicationModulePackage


class TaskType(enum.IntEnum):
    TrainStation_Load_Database = 100
    TrainStation_Load_GeoJSON = 101
    TrainStation_AssignPolygon = 102
    TrainStation_Export_GeoJSON = 103


class MainRoutine(ApplicationModulePackage):
    def __init__(self):
        super().__init__(
            {
                TaskType.TrainStation_Load_Database: [TaskType.TrainStation_AssignPolygon],
                TaskType.TrainStation_Load_GeoJSON: [TaskType.TrainStation_AssignPolygon],
                TaskType.TrainStation_AssignPolygon: [TaskType.TrainStation_Export_GeoJSON],
            },
            {
                TaskType.TrainStation_AssignPolygon: [TaskType.TrainStation_Load_Database, TaskType.TrainStation_Load_GeoJSON],
                TaskType.TrainStation_Export_GeoJSON: [TaskType.TrainStation_AssignPolygon],
            },
        )

        self.train_station_polygons: list[TrainStationPolygon] = []
        self.train_stations: list[TrainStation] = []

    async def run(self, database_path: str, train_station_input_path: pathlib.Path, train_station_output_path: pathlib.Path):
        self.task_add(TaskType.TrainStation_Load_Database, self.task_load_train_stations_database, database_path)
        self.task_add(TaskType.TrainStation_Load_GeoJSON, self.task_load_train_station_geojson, train_station_input_path)

        while self.tasks:
            next_tasks: set[TaskType] = await self.task_next()
            for i in next_tasks:
                match i:
                    case TaskType.TrainStation_AssignPolygon:
                        self.task_add(i, self.task_train_station_assign_polygon, PRECISION)
                    case TaskType.TrainStation_Export_GeoJSON:
                        self.task_add(i, self.task_export_train_station_geojson, train_station_output_path)

    async def task_load_train_stations_database(self, database_path: str):
        self.train_stations = [TrainStation(i) for i in MainRoutine.task_read_database_table(database_path, "TrainStation")]

    async def task_load_train_station_geojson(self, input_path: pathlib.Path):
        COLUMNS_DROP: list[str] = ["OBJECTID", "GRND_LEVEL", "RAIL_TYPE", "FMEL_UPD_D", "SHAPE.AREA", "SHAPE.LEN"]
        df: geopandas.GeoDataFrame = geopandas.read_file(input_path, engine="pyogrio", on_invalid="ignore")
        df = df.to_crs(epsg=4326).explode(ignore_index=True)
        df = df.drop(columns=[i for i in COLUMNS_DROP if i in df.columns], errors="ignore")
        df = df[df.geometry.notnull() & ~df.geometry.is_empty & df.geometry.is_valid]
        df["geometry"] = df.geometry.buffer(0)
        df = df[df.geometry.is_valid]
        df["geometry"] = shapely.set_precision(df.geometry, grid_size=PRECISION)
        wkb = df.geometry.to_wkb()
        df = df.loc[~wkb.duplicated()].copy()
        df["geometry"] = df["geometry"].apply(lambda x: shapely.Polygon(x.exterior) if x and x.geom_type == "Polygon" else x)
        for i in df.itertuples(index=False):
            coordinates: list[list[Coordinate]] = [list(i.geometry.exterior.coords)]
            coordinates.extend([list(interior.coords) for interior in i.geometry.interiors])
            item = TrainStationPolygon(EPSG_Type.EPSG_4326, coordinates)
            item.name = str(i.NAME).lower()
            item.tags["INC_CRC"] = str(i.INC_CRC)
            self.train_station_polygons.append(item)

    async def task_train_station_assign_polygon(self, threshold_distance: float) -> str:
        for train_station in self.train_stations:
            polygon_within: list[TrainStationPolygon] = [i for i in self.train_station_polygons if train_station.english_lower in i.name or i.name in train_station.english_lower]
            if len(polygon_within) == 1:
                polygon_within[0].codes.add(train_station.code)
                train_station.polygons.append(polygon_within[0])
                continue

            polygons_within = [i for i in self.train_station_polygons if i.EPSG_4326.covers(train_station.point.EPSG_4326)]
            if len(polygons_within) == 1:
                polygons_within[0].codes.add(train_station.code)
                train_station.polygons.append(polygons_within[0])
                continue

            distances: list[tuple[TrainStationPolygon, float]] = [(i, i.EPSG_3857.distance(train_station.point.EPSG_3857)) for i in self.train_station_polygons]
            distances.sort(key=lambda x: x[1])
            nearest: tuple[TrainStationPolygon, float] = distances[0]
            if nearest[1] <= threshold_distance:
                nearest[0].codes.add(train_station.code)
                train_station.polygons.append(nearest[0])
                continue

        print(f"No polygon was assigned to [{(', '.join([i.code for i in self.train_stations if len(i.polygons) == 0]))}].")

    async def task_export_train_station_geojson(self, output_path: pathlib.Path):
        df = geopandas.GeoDataFrame(geometry=[i.EPSG_4326 for i in self.train_station_polygons], crs="EPSG:4326")
        df["id"] = range(1, len(df) + 1)
        df["codes"] = [",".join(i.codes) for i in self.train_station_polygons]
        df.to_file(output_path, driver="GeoJSON")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database_path", type=pathlib.Path, help="Path to the SQLite database file")
    parser.add_argument("train_station_input_path", type=pathlib.Path, help="Path to the Train Station Input GeoJSON file")
    parser.add_argument("train_station_output_path", type=pathlib.Path, help="Path to the Train Station Output GeoJSON file")
    args: argparse.Namespace = parser.parse_args()

    routine = MainRoutine()
    try:
        asyncio.run(routine.run(args.database_path, args.train_station_input_path, args.train_station_output_path))
    except KeyboardInterrupt:
        pass
