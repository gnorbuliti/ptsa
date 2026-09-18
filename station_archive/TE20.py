import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

# 1
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27556304, 103.85443983)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27602243, 103.85436359)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27600899, 103.85433218)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27601494, 103.85436762999998)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)

# 2
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27680299, 103.85423660999999)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27681256, 103.85429367)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27680139, 103.85429253)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27689211, 103.85427747999998)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)

# 2
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27661566, 103.85426764)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27663513, 103.85438364999999)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27653908, 103.8543194)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27642534, 103.85433825)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)
