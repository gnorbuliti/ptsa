import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

# 1
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.37214507, 103.89056375)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.37210641, 103.89052787)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.3716591, 103.89083690000001)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.37209038, 103.89039057)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)

# 1
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.37197286, 103.89027846999998)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.37209038, 103.89039057)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.37210641, 103.89052787)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.37250592, 103.89011441999999)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)
