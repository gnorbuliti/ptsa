import shapely

from ptsa.geospatial.equation.line import LineEquation
from ptsa.geospatial.geometry.enumeration import EPSG_Type
from ptsa.geospatial.geometry.point import GeometryPoint

# 1
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.31539163, 103.76486717999998)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.31539061, 103.76486486)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.31565902, 103.76469513)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.31545281, 103.76478471)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)

# 2
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.31562581, 103.76476546)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.31566547, 103.7648556)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.3157625, 103.76507109)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.31575195, 103.76507567)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)

# 3
point_0a = GeometryPoint(EPSG_Type.EPSG_4326, 1.31591155, 103.76523202)
point_0b = GeometryPoint(EPSG_Type.EPSG_4326, 1.31582299, 103.76503075)
line_0 = LineEquation.from_shapely_points(point_0a.EPSG_3857, point_0b.EPSG_3857)

point_1a = GeometryPoint(EPSG_Type.EPSG_4326, 1.31571539, 103.76482324)
point_1b = GeometryPoint(EPSG_Type.EPSG_4326, 1.31572943, 103.76482758)
line_1 = LineEquation.from_shapely_points(point_1a.EPSG_3857, point_1b.EPSG_3857)

point_0x1: shapely.Point = line_0.intersection_point(line_1)
print(GeometryPoint.from_coordinate(EPSG_Type.EPSG_3857, point_0x1.xy).EPSG_4326_xy)
