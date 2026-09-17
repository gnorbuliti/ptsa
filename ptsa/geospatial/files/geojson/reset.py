import argparse
import pathlib

import geopandas


def reset_file(file_path: pathlib.Path):
    try:
        gdf = geopandas.read_file(file_path)
        gdf = gdf[gdf.columns]
        gdf.to_file(file_path, driver="GeoJSON", encoding="utf-8")
        print(f"Successfully processed and updated: {file_path}")
    except (OSError, ValueError, KeyError, RuntimeError) as e:
        print(f"An error occurred while processing the file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load and resave a spatial data file as a GeoJSON.")
    parser.add_argument("file_path", type=pathlib.Path, help="Path to the vector spatial file (e.g., .geojson, .shp)")
    args: argparse.Namespace = parser.parse_args()
    file_path: pathlib.Path = args.file_path

    if file_path.is_file():
        reset_file(file_path)
    else:
        parser.error(f"File '{file_path}' is either missing or invalid.")
