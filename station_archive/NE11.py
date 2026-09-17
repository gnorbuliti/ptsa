import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

# VERTICAL
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.33932195, 103.87111436)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.3399313, 103.87112239)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

# VERTICAL
point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.34012807, 103.87085717999999)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.34012446, 103.87112774999999)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)