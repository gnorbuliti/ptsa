import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.31121994, 103.75806169999998)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.3111353, 103.75804705)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.31109214, 103.75809596999999)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.31114764, 103.75812375999999)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_2 = GeometryPoint(EPSG_Type.EPSG_4326, 1.31115593, 103.75810739999999)

point_0x1: shapely.Point = line_1.nearest_point_on_line(point_0b.EPSG_3857.x, point_0b.EPSG_3857.y)
point_0x2: shapely.Point = line_0.nearest_point_on_line(point_2.EPSG_3857.x, point_2.EPSG_3857.y)

print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x2.xy).EPSG_4326_xy)