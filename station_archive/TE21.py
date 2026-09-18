import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

# 1
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27302169, 103.86297659999998)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27306821, 103.86290484)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27318868, 103.86281606)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27313013, 103.8627786)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)
