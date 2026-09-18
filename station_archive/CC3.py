import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

# 1
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.29365397, 103.85547282)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.29389008, 103.85508808)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.29404032, 103.85524734)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.29388434, 103.85514860999999)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)

# 2
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.2940792, 103.85518671)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.29392321, 103.85508799)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.29388159, 103.85508292999998)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.29390357, 103.85504710999999)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)
