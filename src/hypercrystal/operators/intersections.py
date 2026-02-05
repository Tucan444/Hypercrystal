from ..h2_math.h2_ray import H2Ray
from ..h2_math.h2_vector import H2Vector
from ..h2_math.h2_transform import H2Transform
from ..shapes.line import H2Line
from ..shapes.circle import H2Circle
from ..shapes.polygon import H2Polygon
from ..notation import H2Intersection, H2RayHit, H2PolygonIntersection, H2PolygonsIntersection
from ..h2_math.low_functions import gamma_from_sidelengths

Intersectable = H2Line | H2Circle | H2Polygon


class Intersections:
    @classmethod
    def Process(cls, a: Intersectable, b: Intersectable) -> H2Intersection:
        if type(a) == H2Line:
            if type(b) == H2Line:
                return cls.LineLine(a, b)
            elif type(b) == H2Circle:
                return cls.LineCircle(a, b)
            elif type(b) == H2Polygon:
                return cls.LinePolygon(a, b)
            else:
                raise TypeError(f"invalid type of b: {type(b)}")

        elif type(a) == H2Circle:
            if type(b) == H2Line:
                return cls.LineCircle(b, a)
            elif type(b) == H2Circle:
                return cls.CircleCircle(a, b)
            elif type(b) == H2Polygon:
                return cls.CirclePolygon(a, b)
            else:
                raise TypeError(f"invalid type of b: {type(b)}")

        elif type(a) == H2Polygon:
            if type(b) == H2Line:
                return cls.LinePolygon(b, a)
            elif type(b) == H2Circle:
                return cls.CirclePolygon(b, a)
            elif type(b) == H2Polygon:
                return cls.PolygonPolygon(a, b)
            else:
                raise TypeError(f"invalid type of b: {type(b)}")

        else:
            raise TypeError(f"invalid type of a: {type(a)}")

    @classmethod
    def LineLine(cls, a: H2Line, b: H2Line) -> H2Intersection:
        ray: H2Ray = H2Ray.FromLine(a, True)
        intersections: H2Intersection = []

        result_AB: H2Vector = cls._LineLineSingleDirection(a, b, ray)
        if result_AB is None:
            return intersections

        intersections.append(result_AB)

        ray = H2Ray.FromLine(a, False)
        result_BA: H2Vector = cls._LineLineSingleDirection(a, b, ray)
        if result_BA is None:
            return intersections

        if result_AB.distance_to(result_BA) == 0:
            return intersections

        intersections.append(result_BA)
        return intersections

    @classmethod
    def LineCircle(cls, a: H2Line, b: H2Circle) -> H2Intersection:
        ray: H2Ray = H2Ray.FromLine(a, True)
        intersections: H2Intersection = []

        result_AB: H2Vector = cls._LineCircleSingleDirection(a, b, ray)
        if result_AB is not None:
            intersections.append(result_AB)

        ray = H2Ray.FromLine(a, False)
        result_BA: H2Vector = cls._LineCircleSingleDirection(a, b, ray)
        if result_BA is None:
            return intersections

        if result_AB.distance_to(result_BA) == 0:
            return intersections

        intersections.append(result_BA)
        return intersections

    @classmethod
    def CircleCircle(cls, a: H2Circle, b: H2Circle) -> H2Intersection:
        d: float = a.center.distance_to(b.center)
        if d > a.radius + b.radius:
            return []

        if d == 0:
            return []

        seed: H2Vector = H2Transform.AtoB(a.center, b.center, a.radius) @ a.center

        if d == a.radius + b.radius:
            return [seed]

        gamma: float = gamma_from_sidelengths(a.radius, d, b.radius)
        up: H2Transform = H2Transform.Around(a.center, gamma)
        down: H2Transform = H2Transform.Around(a.center, -gamma)

        return [
            up @ seed, down @ seed
        ]

    @classmethod
    def LinePolygon(cls, a: H2Line, b: H2Polygon) -> H2PolygonIntersection:
        intersections: H2PolygonIntersection = []

        for i in range(len(b.points) + (-1 if b.is_spline else 0)):
            intersect: H2Intersection = cls.LineLine(a, H2Line(
                b.points[i], b.points[(i+1) % len(b.points)]
            ))

            if len(intersect) == 0:
                continue

            intersections.append((i, intersect))

        return intersections

    @classmethod
    def CirclePolygon(cls, a: H2Circle, b: H2Polygon) -> H2PolygonIntersection:
        intersections: H2PolygonIntersection = []

        for i in range(len(b.points) + (-1 if b.is_spline else 0)):
            intersect: H2Intersection = cls.LineCircle(H2Line(
                b.points[i], b.points[(i + 1) % len(b.points)]
            ), a)

            if len(intersect) == 0:
                continue

            intersections.append((i, intersect))

        return intersections

    @classmethod
    def PolygonPolygon(cls, a: H2Polygon, b: H2Polygon) -> H2PolygonsIntersection:
        intersections: H2PolygonsIntersection = []

        for j in range(len(a.points) + (-1 if a.is_spline else 0)):
            for i in range(len(b.points) + (-1 if b.is_spline else 0)):
                intersect: H2Intersection = cls.LineLine(
                H2Line(
                    a.points[j], a.points[(j + 1) % len(a.points)]
                ),
                H2Line(
                    b.points[i], b.points[(i + 1) % len(b.points)]
                ))

                if len(intersect) == 0:
                    continue

                intersections.append((j, i, intersect))

        return intersections

    @staticmethod
    def _LineLineSingleDirection(a: H2Line, b: H2Line, ray: H2Ray) -> H2Vector | None:
        result: H2RayHit = ray.cast_against_line(b)

        if result is None:
            return None

        if result > a.length:
            return None

        intersect: H2Vector = ray.sample(result)
        b_length: float = b.length

        if b.a.distance_to(intersect) > b_length:
            return None

        if b.b.distance_to(intersect) > b_length:
            return None

        return intersect

    @classmethod
    def _LineCircleSingleDirection(cls, a: H2Line, b: H2Circle, ray: H2Ray):
        result: H2RayHit = ray.cast_against_circle(b)

        if result is None:
            return None

        if result > a.length:
            return None

        intersect: H2Vector = ray.sample(result)
        return intersect
