from pygame import Vector2


class ProjectedCircle:
    def __init__(self, center: Vector2, radius: float, key=None) -> None:
        self.center: Vector2 = center
        self.radius: float = radius
        self.key = key

    @property
    def as_json(self) -> dict:
        return {
            "__class__": self.__class__.__name__,
            "center": [*self.center],
            "radius": self.radius
        }

    @classmethod
    def from_json(cls, json_data: dict) -> 'ProjectedCircle':
        return ProjectedCircle(
            Vector2(*json_data["center"]),
            json_data["radius"]
        )

class ProjectedLine:
    def __init__(self, a: Vector2, b: Vector2, key=None) -> None:
        self.a: Vector2 = a
        self.b: Vector2 = b
        self.key = key

    @property
    def as_json(self) -> dict:
        return {
            "__class__": self.__class__.__name__,
            "a": [*self.a],
            "b": [*self.b]
        }

    @classmethod
    def from_json(cls, json_data: dict) -> 'ProjectedLine':
        return ProjectedLine(
            Vector2(*json_data["a"]),
            Vector2(*json_data["b"])
        )

class ProjectedPolygon:
    def __init__(self, points: list[Vector2], key=None, is_spline:bool=False) -> None:
        self.points: list[Vector2] = points
        self.key = key
        self.is_spline: bool = is_spline

    @property
    def as_json(self) -> dict:
        return {
            "__class__": self.__class__.__name__,
            "points": [[*point] for point in self.points],
            "is spline": self.is_spline
        }

    @classmethod
    def from_json(cls, json_data: dict) -> 'ProjectedPolygon':
        return ProjectedPolygon(
            points=[Vector2(*point_data) for point_data in json_data["points"]],
            is_spline=json_data["is spline"]
        )
