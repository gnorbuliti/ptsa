import argparse
import asyncio
import enum
import pathlib

import geopandas
import shapely

from ptsa.geospatial.geometry.core import Coordinate
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.modules.sg.constants import PRECISION, SIMPLIFICATION_METRE, x03_MAXIMUM_ANGLE_DEGREE, x03_MAXIMUM_DISPLACEMENT_METRE
from ptsa.modules.sg.containers.train_line import TrainLineGeometry
from ptsa.workflow.task_manager import ApplicationModulePackage


class TrainLineGeometryx03(TrainLineGeometry):
    @property
    def is_matched(self) -> bool:
        return bool(self.start_code and self.end_code and not self.merge_ids)

    @property
    def is_merging(self) -> bool:
        return bool(self.start_code) != bool(self.end_code) and bool(self.merge_ids)

    def __init__(self, EPSG: EPSG_Type, coordinates: list[Coordinate]):
        super().__init__(EPSG, coordinates)
        self.start_code: str = ""
        self.end_code: str = ""
        self.merge_ids: set[str] = set()
        self.merged: set[str] = set()


class TaskType(enum.IntEnum):
    TrainLine_Load_GeoJSON = 100
    TrainLine_Merge = 101
    TrainLine_Export_GeoJSON = 102


class MainRoutine(ApplicationModulePackage):
    def __init__(self):
        super().__init__(
            {
                TaskType.TrainLine_Load_GeoJSON: [TaskType.TrainLine_Merge],
                TaskType.TrainLine_Merge: [TaskType.TrainLine_Export_GeoJSON],
            },
            {
                TaskType.TrainLine_Merge: [TaskType.TrainLine_Load_GeoJSON],
                TaskType.TrainLine_Export_GeoJSON: [TaskType.TrainLine_Merge],
            },
        )

        self.train_line_geometries: list[TrainLineGeometry] = []

    async def run(self, train_line_input_path: pathlib.Path, train_line_output_path: pathlib.Path):
        self.tracker.start("x03")
        self.task_add(TaskType.TrainLine_Load_GeoJSON, self.task_load_geojson_train_lines, train_line_input_path)
        while self.tasks:
            next_tasks: set[TaskType] = await self.task_next()
            for i in next_tasks:
                match i:
                    case TaskType.TrainLine_Merge:
                        self.task_add(i, self.task_train_lines_merge)
                    case TaskType.TrainLine_Export_GeoJSON:
                        self.task_add(i, self.task_export_train_lines_geojson, train_line_output_path)
        self.tracker.stop()

    async def task_load_geojson_train_lines(self, input_path: pathlib.Path):
        df: geopandas.GeoDataFrame = geopandas.read_file(input_path, engine="pyogrio", on_invalid="ignore")
        df = df.to_crs(epsg=4326).explode(ignore_index=True)
        df = df[df.geometry.notnull() & ~df.geometry.is_empty & df.geometry.is_valid]
        df["geometry"] = shapely.set_precision(df.geometry, grid_size=PRECISION)
        df = df[df.geometry.apply(lambda geom: not (geom.geom_type == "LineString" and len(geom.coords) <= 1))]
        wkb = df.geometry.to_wkb()
        df = df.loc[~wkb.duplicated()].copy()
        for i in df.itertuples(index=False):
            if bool(i.retain):
                item = TrainLineGeometryx03(EPSG_Type.EPSG_4326, i.geometry.coords)
                item.simplify_geometry(SIMPLIFICATION_METRE)
                item.identifier = str(i.id)
                item.start_code = str(i.start)
                item.end_code = str(i.end)
                item.merge_ids = {j for j in str(i.merge).split(",") if j and j != item.identifier}
                item.merged.add(item.identifier)
                self.train_line_geometries.append(item)

    async def task_train_lines_merge(self) -> str:
        self.error_ids: list[str] = []
        self.matched: list[TrainLineGeometryx03] = []
        self.merging: list[TrainLineGeometryx03] = []

        for i in self.train_line_geometries:
            if bool(i.start_code and i.end_code):
                if i.start_code == i.end_code or i.merge_ids:
                    self.error_ids.append(i.identifier)
                else:
                    self.matched.append(i)
            else:
                self.merging.append(i)

        segments: dict[str, TrainLineGeometryx03] = {i.identifier: i for i in self.merging}

        for i in self.merging:
            for j in i.merge_ids:
                segment: TrainLineGeometryx03 | None = segments.get(j)
                if segment is not None:
                    segment.merge_ids.add(i.identifier)

        is_skipping: set[str] = set()
        while True:
            valid_items = [i for i in segments.values() if i.is_merging and i.identifier not in is_skipping]
            valid_items.sort(key=lambda x: len(x.merge_ids), reverse=True)
            if not valid_items:
                break
            reference: TrainLineGeometryx03 = valid_items[0]
            if not self.task_train_lines_merge_item(segments, reference):
                is_skipping.add(reference.identifier)

        self.merged = list(segments.values())

    def task_train_lines_merge_item(self, segments: dict[str, TrainLineGeometryx03], reference: TrainLineGeometryx03) -> bool:
        candidates: list[TrainLineGeometryx03] = []
        for i in reference.merge_ids:
            item: TrainLineGeometryx03 | None = segments.get(i)
            if item is None:
                continue
            self.merge(reference, item, x03_MAXIMUM_DISPLACEMENT_METRE, x03_MAXIMUM_ANGLE_DEGREE)
            candidates.append(item)

        if not candidates:
            return False

        if reference.identifier in segments:
            del segments[reference.identifier]

        for i in candidates:
            if i.is_matched:
                self.matched.append(i)
                del segments[i.identifier]

        for i in candidates:
            if not i.is_matched:
                self.task_train_lines_merge_item(segments, i)

        return True

    def merge(self, reference: TrainLineGeometryx03, candidate: TrainLineGeometryx03, MAXIMUM_DISPLACEMENT_METRE: float, MAXIMUM_ANGLE_DEGREE: float):
        pass

    async def task_export_train_lines_geojson(self, output_path: pathlib.Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "geometry": linestring.EPSG_4326,
                "rotate": False,
            }
            for linestring in self.train_line_geometries
        ]
        df = geopandas.GeoDataFrame(data, crs="EPSG:4326")
        df.to_file(output_path, driver="GeoJSON")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("train_Line_input_path", type=pathlib.Path, help="Path to the Train Line Input GeoJSON file")
    parser.add_argument("train_Line_output_path", type=pathlib.Path, help="Path to the Train Line Output GeoJSON file")
    args: argparse.Namespace = parser.parse_args()

    routine = MainRoutine()
    try:
        asyncio.run(routine.run(args.train_Line_input_path, args.train_Line_output_path))
    except KeyboardInterrupt:
        pass
