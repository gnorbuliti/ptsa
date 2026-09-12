import pyproj

transform_4326_to_3857 = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
transform_3857_to_4326 = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform
