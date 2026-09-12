from __future__ import annotations

import geographiclib.geodesic
import numpy
import shapely
import shapely.ops

from sptg_geospatial.equation.line import LineEquation
from sptg_geospatial.geometry.constant import transform_3857_to_4326, transform_4326_to_3857
from sptg_geospatial.geometry.enumeration import EPSG_Type
from sptg_geospatial.geometry.linestring import GeometryLineString
from sptg_geospatial.geometry.point import GeometryPoint


def project_point(reference_origin: GeometryPoint, reference_destination: GeometryPoint, candidate_origin: GeometryPoint | None = None, distance_metre: float | None = None) -> GeometryPoint:
    result = geographiclib.geodesic.Geodesic.WGS84.Inverse(reference_origin.EPSG_4326.y, reference_origin.EPSG_4326.x, reference_destination.EPSG_4326.y, reference_destination.EPSG_4326.x)
    bearing = result["azi1"]
    distance_metre = distance_metre if distance_metre else result["s12"]
    candidate_origin: GeometryPoint = candidate_origin if candidate_origin else reference_destination
    result = geographiclib.geodesic.Geodesic.WGS84.Direct(lat1=candidate_origin.EPSG_4326.y, lon1=candidate_origin.EPSG_4326.x, azi1=bearing, s12=distance_metre)
    return GeometryPoint(result["lat2"], result["lon2"])


def project_point_along_bearing(candidate: GeometryPoint, distance_metre: float, bearing_degree: float) -> GeometryPoint:
    result = geographiclib.geodesic.Geodesic.WGS84.Direct(lat1=candidate.EPSG_4326.y, lon1=candidate.EPSG_4326.x, azi1=bearing_degree, s12=distance_metre)
    return GeometryPoint(result["lat2"], result["lon2"])


def compute_baseline_point(reference_origin: GeometryPoint, reference_destination: GeometryPoint, candidate: GeometryPoint) -> GeometryPoint:
    reference: LineEquation = LineEquation.from_points(reference_origin.EPSG_3857.x, reference_origin.EPSG_3857.y, reference_destination.EPSG_3857.x, reference_destination.EPSG_3857.y)
    baseline: LineEquation = reference.get_orthogonal_line(reference_destination.EPSG_3857.x, reference_destination.EPSG_3857.y)
    x1, y1 = baseline.nearest_point_on_line(candidate.EPSG_3857.x, candidate.EPSG_3857.y)
    return GeometryPoint(x1, y1, EPSG_Type.EPSG_3857)


def compute_intersect_point(reference_origin:GeometryPoint, reference_destination: GeometryPoint, candidate_origin: GeometryPoint, candidate_baseline: GeometryPoint) -> GeometryPoint:
    reference = LineEquation.from_points(reference_origin.EPSG_3857.x, reference_origin.EPSG_3857.y, reference_destination.EPSG_3857.x, reference_destination.EPSG_3857.y)
    candidate = LineEquation.from_points(candidate_origin.EPSG_3857.x, candidate_origin.EPSG_3857.y, candidate_baseline.EPSG_3857.x, candidate_baseline.EPSG_3857.y)
    intersection: shapely.Point = reference.intersection_point(candidate)
    return GeometryPoint(intersection.y, intersection.x, EPSG_Type.EPSG_3857)

def bezier_connection(reference_origin: GeometryPoint, reference_destination: GeometryPoint, candidate_baseline: GeometryPoint, candidate_origin: GeometryPoint, handle_factor=0.35, n=50):
    oa, ob = map(numpy.asarray, ((reference_origin.EPSG_4326.x, reference_origin.EPSG_4326.y), (reference_destination.EPSG_4326.x, reference_destination.EPSG_4326.y)))
    da, db = map(numpy.asarray, ((candidate_baseline.EPSG_4326.x, candidate_baseline.EPSG_4326.y), (candidate_origin.EPSG_4326.x, candidate_origin.EPSG_4326.y)))

    v1 = numpy.asarray(ob - oa, float)
    t0 = v1 / numpy.linalg.norm(v1)
    del v1

    v2 = numpy.asarray(db - da, float)
    t1 = v2 / numpy.linalg.norm(v2)
    del v2

    P0 = ob
    P3 = da

    d = numpy.linalg.norm(P3 - P0)
    h = d * handle_factor

    P1 = P0 + t0 * h
    P2 = P3 - t1 * h

    t = numpy.linspace(0, 1, n)
    omt = 1 - t

    curve = omt[:, None] ** 3 * P0 + 3 * omt[:, None] ** 2 * t[:, None] * P1 + 3 * omt[:, None] * t[:, None] ** 2 * P2 + t[:, None] ** 3 * P3

    return GeometryLineString(curve)
