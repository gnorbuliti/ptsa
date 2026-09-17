import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.34077357, 103.84639036999998)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.34070219, 103.84746800999999)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.34112853, 103.8470246)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.34102224, 103.84701770999999)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)

point_2a = GeometryPoint(EPSG_Type.EPSG_4326, 1.33999956, 103.8469032)
point_2b = GeometryPoint(EPSG_Type.EPSG_4326, 1.340611416634, 103.84694288991095)
line_2 = LineEquation.from_shapely_points(point_2a.EPSG_3857, point_2b.EPSG_3857)

point_0x2: shapely.Point = line_0.intersection_point(line_2)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x2.xy).EPSG_4326_xy)

point_3a = GeometryPoint(EPSG_Type.EPSG_4326, 1.34102224, 103.84701770999999)
point_3b = GeometryPoint(EPSG_Type.EPSG_4326, 1.34105352, 103.84640140000002)
line_3 = LineEquation.from_shapely_points(point_3a.EPSG_3857, point_3b.EPSG_3857)

point_3x2: shapely.Point = line_3.intersection_point(line_2)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_3x2.xy).EPSG_4326_xy)