import math

from pygame import Vector2

from ..misc.h2_camera import H2Camera
from .h2_projection import H2Projection
from ..h2_math import H2Vector
from ..notation import Resolution
from ..shapes.circle import H2Circle
from ..shapes.projected import ProjectedPolygon, ProjectedCircle


class SquishModel(H2Projection):
    def __init__(self, camera: H2Camera, display_size: Resolution, perspective_distance=2):
        super().__init__(camera, display_size)
        self.perspective_distance = perspective_distance

    def project(self, point: H2Vector) -> Vector2:
        view_point: H2Vector = self.world_to_view_space(point)
        projected_point: Vector2 = Vector2(
            view_point.y / (self.perspective_distance + view_point.x),
            view_point.z / (self.perspective_distance + view_point.x))

        magnitude: float = projected_point.length()
        if magnitude > 0.0001:
            projected_point *= magnitude / max(abs(projected_point.x), abs(projected_point.y))

        if self.display_size[0] > self.display_size[1]:
            projected_point.x *= self.display_size[0] / self.display_size[1]
        else:
            projected_point.y *= self.display_size[1] / self.display_size[0]

        return self.projected_to_display_space(projected_point)

    def reproject(self, point: Vector2) -> H2Vector | None:
        projected_point: Vector2 = self.display_to_projected_space(point)

        if self.display_size[0] > self.display_size[1]:
            projected_point.x /= self.display_size[0] / self.display_size[1]
        else:
            projected_point.y /= self.display_size[1] / self.display_size[0]

        magnitude: float = max(abs(projected_point.x), abs(projected_point.y))
        if magnitude > 0.0001:
            projected_point *= magnitude / projected_point.length()

        y, z = projected_point

        if projected_point.length() >= 1:
            return None

        o: float = -self.perspective_distance
        A: float = 1 - y * y - z * z
        if A <= 0:
            return None

        D: float = o * o - ((o * o - 1) * A)
        if D < 0:
            return None

        t = (-o + math.sqrt(D)) / A
        view_point: H2Vector = H2Vector(o + t, t * y, t * z)
        return self.view_to_world_space(view_point)

    def project_circles(self, circles: list[H2Circle]) -> list[ProjectedCircle]:
        raise Exception("NOT SUPPORTED FOR SQUISH MODEL")

    @property
    def disc_present(self) -> bool:
        return False

    @property
    def limit_shape(self) -> ProjectedPolygon:
        disc: ProjectedCircle = self.disc
        points: list[Vector2] = [
            offset * disc.radius
            for offset in [Vector2(-1, -1), Vector2(1, -1), Vector2(1, 1), Vector2(-1, 1)]
        ]

        for p in points:
            if self.display_size[0] > self.display_size[1]:
                p.x *= self.display_size[0] / self.display_size[1]
            else:
                p.y *= self.display_size[1] / self.display_size[0]

            p += disc.center

        return ProjectedPolygon(points)

    @property
    def as_json(self) -> dict:
        json_data: dict = super().as_json
        json_data["__class__"] = self.__class__.__name__
        json_data["perspective distance"] = self.perspective_distance

        return json_data

    @classmethod
    def from_json(cls, json_data: dict) -> 'SquishModel':
        model: SquishModel = SquishModel(
            H2Camera.from_json(json_data["camera"]),
            tuple(json_data["display size"]),
            json_data["perspective distance"]
        )

        model.cull_range = json_data["cull range"]
        return model
