import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

# 1
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27628554, 103.85508246)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27626902, 103.85498405)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27632185, 103.85497427)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27617013, 103.85499945)  ##
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)


# 2
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27625032, 103.85472010999999)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27539128, 103.85486247)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27617013, 103.85499945)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27611741, 103.85468588999998)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)
