import argparse
import asyncio
import enum
import pathlib
from collections import defaultdict

import geopandas
import shapely

from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.modules.sg.constants import PRECISION, x02_MAXIMUM_DISPLACEMENT_METRE
from ptsa.modules.sg.containers.train_line import TrainLineGeometry
from ptsa.modules.sg.containers.train_station import TrainStation, TrainStationDistance, TrainStationGeometry
from ptsa.workflow.task_manager import ApplicationModulePackage


class TaskType(enum.IntEnum):
    TrainStation_Load_Database = 100
    TrainStation_Load_GeoJSON = 101
    TrainLine_Load_GeoJSON = 102

    TrainStation_AssignGeometry = 200
    TrainStation_Export_GeoJSON = 201

    TrainLine_AssignTrainStation = 300
    TrainLine_Export_GeoJSON = 301


class MainRoutine(ApplicationModulePackage):
    def __init__(self):
        super().__init__(
            {
                TaskType.TrainStation_Load_Database: [TaskType.TrainStation_AssignGeometry],
                TaskType.TrainStation_Load_GeoJSON: [TaskType.TrainStation_AssignGeometry],
                TaskType.TrainStation_AssignGeometry: [TaskType.TrainStation_Export_GeoJSON, TaskType.TrainLine_AssignTrainStation],
                TaskType.TrainLine_Load_GeoJSON: [TaskType.TrainLine_AssignTrainStation],
                TaskType.TrainLine_AssignTrainStation: [TaskType.TrainLine_Export_GeoJSON],
            },
            {
                TaskType.TrainStation_AssignGeometry: [TaskType.TrainStation_Load_Database, TaskType.TrainStation_Load_GeoJSON],
                TaskType.TrainStation_Export_GeoJSON: [TaskType.TrainStation_AssignGeometry],
                TaskType.TrainLine_AssignTrainStation: [TaskType.TrainLine_Load_GeoJSON, TaskType.TrainStation_AssignGeometry],
                TaskType.TrainLine_Export_GeoJSON: [TaskType.TrainLine_AssignTrainStation],
            },
        )

        self.train_station_geometries: list[TrainStationGeometry] = []
        self.train_stations: list[TrainStation] = []
        self.train_line_geometries: list[TrainLineGeometry] = []

    async def run(self, database_path: str, train_station_input_path: pathlib.Path, train_station_output_path: pathlib.Path, train_line_input_path: pathlib.Path, train_line_output_path: pathlib.Path):
        self.task_add(TaskType.TrainStation_Load_Database, self.task_load_train_stations_database, database_path)
        self.task_add(TaskType.TrainStation_Load_GeoJSON, self.task_load_train_station_geojson, train_station_input_path)
        self.task_add(TaskType.TrainLine_Load_GeoJSON, self.task_load_geojson_train_line, train_line_input_path)

        while self.tasks:
            next_tasks: set[TaskType] = await self.task_next()
            for i in next_tasks:
                match i:
                    case TaskType.TrainStation_AssignGeometry:
                        self.task_add(i, self.task_train_station_assign_geometry)
                    case TaskType.TrainStation_Export_GeoJSON:
                        self.task_add(i, self.task_export_train_station_geojson, train_station_output_path)
                    case TaskType.TrainLine_AssignTrainStation:
                        self.task_add(i, self.task_export_train_line_assign_train_station)
                    case TaskType.TrainLine_Export_GeoJSON:
                        self.task_add(i, self.task_export_train_line_geojson, train_line_output_path)

    async def task_load_train_stations_database(self, database_path: str):
        self.train_stations = [TrainStation(i) for i in MainRoutine.task_read_database_table(database_path, "TrainStation")]

    async def task_load_train_station_geojson(self, input_path: pathlib.Path):
        df: geopandas.GeoDataFrame = geopandas.read_file(input_path, engine="pyogrio", on_invalid="ignore")
        df: geopandas.GeoDataFrame = df.to_crs(epsg=4326)
        for i in df.itertuples(index=False):
            if i.retain:
                coordinates = [list(i.geometry.exterior.coords), [list(interior.coords) for interior in i.geometry.interiors]]
                item = TrainStationGeometry(EPSG_Type.EPSG_4326, coordinates)
                item.identifier = i.id
                item.codes = set(str(i.codes).split(","))
                self.train_station_geometries.append(item)

    async def task_load_geojson_train_line(self, input_path: pathlib.Path):
        df: geopandas.GeoDataFrame = geopandas.read_file(input_path, engine="pyogrio", on_invalid="ignore")
        df = df.to_crs(epsg=4326).explode(ignore_index=True)
        df = df[df.geometry.notnull() & ~df.geometry.is_empty & df.geometry.is_valid]
        df["geometry"] = shapely.set_precision(df.geometry, grid_size=PRECISION)
        df = df[df.geometry.apply(lambda geom: not (geom.geom_type == "LineString" and len(geom.coords) <= 1))]
        wkb = df.geometry.to_wkb()
        df = df.loc[~wkb.duplicated()].copy()
        for i in df.itertuples(index=False):
            item = TrainLineGeometry(EPSG_Type.EPSG_4326, i.geometry.coords)
            item.tags["INC_CRC"] = str(i.INC_CRC)
            self.train_line_geometries.append(item)

    async def task_train_station_assign_geometry(self):
        for i in self.train_stations:
            i.polygons.extend(j for j in self.train_station_geometries if i.code in j.codes)
        print(f"No polygon was assigned to [{(', '.join([i.code for i in self.train_stations if len(i.polygons) == 0]))}].")

    async def task_export_train_station_geojson(self, output_path: pathlib.Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = [{"geometry": polygon.EPSG_4326, "id": polygon.identifier, "codes": ",".join(sorted(polygon.codes))} for polygon in self.train_station_geometries]
        df = geopandas.GeoDataFrame(data, crs="EPSG:4326")
        df.to_file(output_path, driver="GeoJSON")

    async def task_export_train_line_assign_train_station(self):
        for geometry in self.train_line_geometries:
            start_stations: list[TrainStationDistance] = TrainLineGeometry.nearest_train_stations(self.train_stations, geometry.start, x02_MAXIMUM_DISPLACEMENT_METRE)
            end_stations: list[TrainStationDistance] = TrainLineGeometry.nearest_train_stations(self.train_stations, geometry.end, x02_MAXIMUM_DISPLACEMENT_METRE)

            if not start_stations and not end_stations:
                return
            elif not start_stations:
                self.end_station = end_stations[0].station
            elif not end_stations:
                self.start_station = start_stations[0].station
            else:
                common_lines: set[str] = {i.station.line for i in start_stations} & {i.station.line for i in end_stations}
                if common_lines:
                    starts: dict[str, TrainStationDistance] = {i.station.line: i for i in start_stations}
                    ends: dict[str, TrainStationDistance] = {i.station.line: i for i in end_stations}

                    candidates: list[tuple[float, TrainStationDistance, TrainStationDistance]] = []
                    for line in common_lines:
                        start = starts.get(line)
                        end = ends.get(line)
                        candidates.append((start.distance + end.distance, start, end))

                    _, best_start, best_end = min(candidates, key=lambda x: x[0])
                    if best_start.station.code != best_end.station.code:
                        self.start_station = best_start.station
                        self.end_station = best_end.station
                    elif best_start.distance < best_end.distance:
                        self.start_station = best_start.station
                    else:
                        self.end_station = best_end.station
                else:
                    self.start_station = start_stations[0].station
                    self.end_station = end_stations[0].station

    async def task_export_train_line_geojson(self, output_path: pathlib.Path):
        grouped = defaultdict(list)
        for item in self.train_line_geometries:
            grouped[item.tags["INC_CRC"]].append(item)

        grouped_dict: dict[str, list[TrainStationGeometry]] = dict(grouped)
        for items in grouped_dict.values():
            for index, item in enumerate(items):
                item.identifier = f"{item.tags['INC_CRC']}_{index}"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "geometry": linestring.EPSG_4326,
                "id": linestring.identifier,
                "start": linestring.start_station.code if linestring.start_station else "",
                "end": linestring.end_station.code if linestring.end_station else "",
                "merge": "",
                "retain": True
            }
            for linestring in self.train_line_geometries
        ]
        df = geopandas.GeoDataFrame(data, crs="EPSG:4326")
        df.to_file(output_path, driver="GeoJSON")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database_path", type=pathlib.Path, help="Path to the SQLite database file")
    parser.add_argument("train_station_input_path", type=pathlib.Path, help="Path to the Train Station Input GeoJSON file")
    parser.add_argument("train_station_output_path", type=pathlib.Path, help="Path to the Train Station Output GeoJSON file")
    parser.add_argument("train_Line_input_path", type=pathlib.Path, help="Path to the Train Line Input GeoJSON file")
    parser.add_argument("train_Line_output_path", type=pathlib.Path, help="Path to the Train Line Output GeoJSON file")
    args: argparse.Namespace = parser.parse_args()

    routine = MainRoutine()
    try:
        asyncio.run(routine.run(args.database_path, args.train_station_input_path, args.train_station_output_path, args.train_Line_input_path, args.train_Line_output_path))
    except KeyboardInterrupt:
        pass
