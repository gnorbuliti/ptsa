from __future__ import annotations

import math

import shapely


class LineEquation:
    def __init__(self, gradient: float | None = None, y_intercept: float | None = None, x_intercept: float | None = None):
        self.gradient: float | None = None if gradient is None or math.isnan(gradient) else gradient
        self.y_intercept: float | None = None if y_intercept is None or math.isnan(y_intercept) else y_intercept
        self.x_intercept: float | None = None if x_intercept is None or math.isnan(x_intercept) else x_intercept
        self.unavailable: bool = gradient is None and x_intercept is None

    @staticmethod
    def _ensure_not_nan(*values: float | None) -> None:
        if any(value is None or math.isnan(value) for value in values):
            raise ValueError("Line equation arguments cannot be NaN")

    @staticmethod
    def from_points(x1: float, y1: float, x2: float, y2: float) -> LineEquation:
        if any(value is None or math.isnan(value) for value in [x1, y1, x2, y2]):
            return LineEquation(gradient=None, y_intercept=None, x_intercept=None)

        dx = x2 - x1
        if dx == 0:
            return LineEquation(x_intercept=x1)
        else:
            gradient = (y2 - y1) / dx
            y_intercept = y1 - (gradient * x1)
            return LineEquation(gradient=gradient, y_intercept=y_intercept)

    @staticmethod
    def from_shapely_points(p1: shapely.Point, p2: shapely.Point) -> LineEquation:
        if any(value is None or math.isnan(value) for value in [p1.x, p1.y, p2.x, p2.y]):
            return LineEquation(gradient=None, y_intercept=None, x_intercept=None)

        dx = p2.x - p1.x
        if dx == 0:
            return LineEquation(x_intercept=p1.x)
        else:
            gradient = (p2.y - p1.y) / dx
            y_intercept = p1.y - (gradient * p1.x)
            return LineEquation(gradient=gradient, y_intercept=y_intercept)

    @staticmethod
    def from_gradient(gradient: float | None, x1: float, y1: float) -> LineEquation:
        if any(value is None or math.isnan(value) for value in [gradient, x1, y1]):
            return LineEquation(gradient=None, y_intercept=None, x_intercept=None)
        elif gradient is None or math.isinf(gradient):
            return LineEquation(x_intercept=x1)
        else:
            y_intercept = y1 - (gradient * x1)
            return LineEquation(gradient=gradient, y_intercept=y_intercept)

    def compute_x(self, y: float) -> float:
        if y is None or math.isnan(y) or self.gradient == 0:
            return float("nan")
        elif self.gradient is None:
            return self.x_intercept
        else:
            return (y - self.y_intercept) / self.gradient

    def compute_y(self, x: float) -> float:
        if x is None or math.isnan(x) or self.gradient is None:
            return float("nan")
        else:
            return (self.gradient * x) + self.y_intercept

    def get_orthogonal_line(self, x1: float, y1: float) -> LineEquation:
        if any(value is None or math.isnan(value) for value in [x1, y1]):
            return LineEquation(gradient=None, y_intercept=None, x_intercept=None)
        elif self.gradient is None:
            return LineEquation(gradient=0.0, y_intercept=y1)
        elif self.gradient == 0.0:
            return LineEquation(x_intercept=x1)
        else:
            return LineEquation.from_gradient(-1.0 / self.gradient, x1, y1)

    def nearest_point_on_line(self, x1: float, y1: float) -> shapely.Point:
        if any(value is None or math.isnan(value) for value in [x1, y1]):
            return shapely.Point(float("nan"), float("nan"))
        elif self.gradient is None:
            return shapely.Point(self.x_intercept, y1)
        elif self.gradient == 0:
            return shapely.Point(x1, self.y_intercept)
        else:
            xo = (x1 + self.gradient * (y1 - self.y_intercept)) / ((self.gradient**2) + 1)
            yo = self.gradient * xo + self.y_intercept
            return shapely.Point(xo, yo)

    def intersection_point(self, candidate: LineEquation) -> shapely.Point | None:
        if self.gradient is None and candidate.gradient is None:
            # Both lines are vertical and do not intersect
            return None

        if self.gradient == candidate.gradient or self.y_intercept == candidate.y_intercept:
            # Parallel (or coincident) lines
            return None

        elif self.gradient is None:
            # Self is vertical
            x = self.x_intercept
            y = candidate.compute_y(x)
            return shapely.Point(x, y)

        elif candidate.gradient is None:
            # Candidate is vertical
            x = candidate.x_intercept
            y = self.compute_y(x)
            return shapely.Point(x, y)

        else:
            # General case
            x = (candidate.y_intercept - self.y_intercept) / (self.gradient - candidate.gradient)
            y = self.compute_y(x)

            return shapely.Point(x, y)
