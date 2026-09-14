import argparse
import asyncio
import enum
import pathlib

import geopandas
import shapely

from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.modules.sg.constants import PRECISION
from ptsa.modules.sg.containers.train_line import TrainLineSegment
from ptsa.modules.sg.containers.train_station import TrainStation, TrainStationPolygon
from ptsa.workflow.task_manager import ApplicationModulePackage


class TaskType(enum.IntEnum):
    TrainStation_Load_Database = 100
    TrainStation_Load_GeoJSON = 101
    TrainLine_Load_GeoJSON = 102

    TrainStation_AssignPolygon = 200
    TrainStation_Export_GeoJSON = 201

    TrainLine_AssignTrainStation = 300
    TrainLine_Export_GeoJSON = 301


class MainRoutine(ApplicationModulePackage):
    def __init__(self):
        super().__init__(
            {
                TaskType.TrainStation_Load_Database: [TaskType.TrainStation_AssignPolygon],
                TaskType.TrainStation_Load_GeoJSON: [TaskType.TrainStation_AssignPolygon],
                TaskType.TrainStation_AssignPolygon: [TaskType.TrainStation_Export_GeoJSON, TaskType.TrainLine_AssignTrainStation],
                TaskType.TrainLine_Load_GeoJSON: [TaskType.TrainLine_AssignTrainStation],
                TaskType.TrainLine_AssignTrainStation: [TaskType.TrainLine_Export_GeoJSON],
            },
            {
                TaskType.TrainStation_AssignPolygon: [TaskType.TrainStation_Load_Database, TaskType.TrainStation_Load_GeoJSON],
                TaskType.TrainStation_Export_GeoJSON: [TaskType.TrainStation_AssignPolygon],
                TaskType.TrainLine_AssignTrainStation: [TaskType.TrainLine_Load_GeoJSON, TaskType.TrainStation_AssignPolygon],
                TaskType.TrainLine_Export_GeoJSON: [TaskType.TrainLine_AssignTrainStation],
            },
        )

        self.train_station_polygons: list[TrainStationPolygon] = []
        self.train_stations: list[TrainStation] = []
        self.train_line_segments: list[TrainLineSegment] = []

    async def run(self, database_path: str, train_station_input_path: pathlib.Path, train_station_output_path: pathlib.Path, train_line_input_path: pathlib.Path, train_line_output_path: pathlib.Path):
        self.task_add(TaskType.TrainStation_Load_Database, self.task_load_train_stations_database, database_path)
        self.task_add(TaskType.TrainStation_Load_GeoJSON, self.task_load_train_station_geojson, train_station_input_path)
        self.task_add(TaskType.TrainLine_Load_GeoJSON, self.task_load_geojson_train_line, train_line_input_path)

        while self.tasks:
            next_tasks: set[TaskType] = await self.task_next()
            for i in next_tasks:
                match i:
                    case TaskType.TrainStation_AssignPolygon:
                        self.task_add(i, self.task_train_station_assign_polygon)
                    case TaskType.TrainStation_Export_GeoJSON:
                        self.task_add(i, self.task_export_train_station_geojson, train_station_output_path)
                    case TaskType.TrainLine_AssignTrainStation:
                        self.task_add(i, self.task_train_line_linestring_assign_train_station)
                    case TaskType.TrainLine_Export_GeoJSON:
                        self.task_add(i, self.task_train_line_linestring_export)

    async def task_load_train_stations_database(self, database_path: str):
        self.train_stations = [TrainStation(i) for i in MainRoutine.task_read_database_table(database_path, "TrainStation")]

    async def task_load_train_station_geojson(self, input_path: pathlib.Path):
        df: geopandas.GeoDataFrame = geopandas.read_file(input_path, engine="pyogrio", on_invalid="ignore")
        df: geopandas.GeoDataFrame = df.to_crs(epsg=4326)
        for i in df.itertuples(index=False):
            coordinates = [list(i.geometry.exterior.coords), [list(interior.coords) for interior in i.geometry.interiors]]
            item = TrainStationPolygon(coordinates)
            item.codes = set(str(i.codes).split(","))
            self.train_station_polygons.append(item)

    async def task_load_geojson_train_line(self, input_path: pathlib.Path):
        COLUMNS_DROP: list[str] = ["OBJECTID", "GRND_LEVEL", "RAIL_TYPE", "INC_CRC", "FMEL_UPD_D", "SHAPE.LEN"]
        df: geopandas.GeoDataFrame = geopandas.read_file(input_path, engine="pyogrio", on_invalid="ignore")
        df = df.to_crs(epsg=4326).explode(ignore_index=True)
        df = df.drop(columns=[i for i in COLUMNS_DROP if i in df.columns], errors="ignore")
        df = df[df.geometry.notnull() & ~df.geometry.is_empty & df.geometry.is_valid]
        df["geometry"] = shapely.set_precision(df.geometry, grid_size=PRECISION)
        df = df[df.geometry.apply(lambda geom: not (geom.geom_type == "LineString" and len(geom.coords) <= 1))]
        wkb = df.geometry.to_wkb()
        df = df.loc[~wkb.duplicated()].copy()
        for i in df.itertuples(index=False):
            self.train_line_segments.append(TrainLineSegment(EPSG_Type.EPSG_4326, i))

    async def task_train_station_assign_polygon(self):
        for i in self.train_stations:
            i.polygons.extend(j for j in self.train_station_polygons if i.code in j.codes)
        print(f"No polygon was assigned to [{(', '.join([i.code for i in self.train_stations if len(i.polygons) == 0]))}].")

    async def task_export_train_station_geojson(self, output_path: pathlib.Path):
        for index, i in enumerate(self.train_station_polygons, start=1):
            i.index = index
        df = geopandas.GeoDataFrame(geometry=[i.EPSG_4326 for i in self.train_station_polygons], crs="EPSG:4326")
        df["id"] = [i.index for i in self.train_station_polygons]
        df["codes"] = [",".join(i.codes) for i in self.train_station_polygons]
        df.to_file(output_path, driver="GeoJSON")


# python ptsa/modules/sg/x01.py data/database_sg.db data/input/TrainStationPolygon.geojson data/intermediate/TrainStationPolygon_x01_Output.geojson
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database_path", type=pathlib.Path, help="Path to the SQLite database file")
    parser.add_argument("train_station_input_path", type=pathlib.Path, help="Path to the Train Station Input GeoJSON file")
    parser.add_argument("train_station_output_path", type=pathlib.Path, help="Path to the Train Station Output GeoJSON file")
    parser.add_argument("train_station_input_path", type=pathlib.Path, help="Path to the Train Station Input GeoJSON file")
    parser.add_argument("train_station_output_path", type=pathlib.Path, help="Path to the Train Station Output GeoJSON file")
    args: argparse.Namespace = parser.parse_args()

    routine = MainRoutine()
    try:
        asyncio.run(routine.run(args.database_path, args.train_station_input_path, args.train_station_output_path))
    except KeyboardInterrupt:
        pass
