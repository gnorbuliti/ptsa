import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

# 1
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27779023, 103.84984659)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27735811, 103.85051314)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.27767173, 103.84994924)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27770594, 103.84997113999998)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_2a = GeometryPoint(EPSG_Type.EPSG_4326, 1.277635, 103.85000589)
point_2b = GeometryPoint(EPSG_Type.EPSG_4326, 1.27766921, 103.85002779)
line_2 = LineEquation.from_shapely_points(point_2a.EPSG_3857, point_2b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
point_0x2: shapely.Point = line_0.intersection_point(line_2)

print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x2.xy).EPSG_4326_xy)
