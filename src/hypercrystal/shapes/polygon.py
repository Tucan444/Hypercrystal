from ..h2_math.h2_vector import H2Vector
from ..h2_math.h2_transform import H2Transform

class H2Polygon:
    def __init__(self, points: list[H2Vector], key=None, is_spline: bool=False) -> None:
        self.points: list[H2Vector] = points
        self.key = key
        self.is_spline: bool=is_spline

    @property
    def circle_hull(self) -> 'H2Circle':
        from .circle import H2Circle
        center, radius = H2Vector.GetCircleHull(self.points)
        return H2Circle(center, radius, self.key)

    def subdivide(self, samples=3) -> 'H2Polygon':
        assert samples >= 0
        points: list[H2Vector] = []

        iter_amount: int = len(self.points)
        if self.is_spline:
            iter_amount -= 1

        for i in range(iter_amount):
            points.append(self.points[i].clone)

            rotor: H2Transform = H2Transform.LerpAB(
                self.points[i], self.points[(i+1) % len(self.points)], 1 / (samples + 1))

            for t in range(samples):
                points.append(
                    rotor @ points[-1])

        if self.is_spline:
            points.append(self.points[-1].clone)

        return H2Polygon(points, self.key, self.is_spline)

    @property
    def as_json(self) -> dict:
        return {
            "__class__": self.__class__.__name__,
            "points": [p.as_json for p in self.points],
            "is spline": self.is_spline
        }

    @classmethod
    def from_json(cls, json_data: dict) -> 'H2Polygon':
        return H2Polygon(
            points=[
                H2Vector.from_json(p_data) for p_data in json_data["points"]
            ],
            is_spline=json_data["is spline"]
        )
