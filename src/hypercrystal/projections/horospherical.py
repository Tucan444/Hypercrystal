import math

from pygame import Vector2

from ..misc.h2_camera import H2Camera
from .h2_projection import H2Projection
from ..h2_math import H2Transform
from ..h2_math import H2Vector
from ..notation import Resolution
from ..shapes.circle import H2Circle
from ..shapes.projected import ProjectedCircle



class HorosphericalModel(H2Projection):
    def __init__(self, camera: H2Camera, display_size: Resolution):
        super().__init__(camera, display_size)

    def project(self, point: H2Vector) -> Vector2:
        view_point: H2Vector = self.world_to_view_space(point)
        projected_point: Vector2 = Vector2(view_point.y / (1 + view_point.x),
                                           view_point.z / (1 + view_point.x))

        projected_point.y += 1
        projected_point *= 4/projected_point.magnitude_squared()
        projected_point.y -= 2

        projected_point.y = math.log2(abs(projected_point.y))
        projected_point.y *= -1

        return self.projected_to_display_space(projected_point)

    def reproject(self, point: Vector2) -> H2Vector | None:
        projected_point: Vector2 = self.display_to_projected_space(point)

        projected_point.y *= -1
        projected_point.y = 2 ** projected_point.y

        projected_point.y += 2
        projected_point *= 4 / projected_point.magnitude_squared()
        projected_point.y -= 1

        y, z = projected_point

        if projected_point.length() >= 1:
            return None

        t: float = 2 / (1 - y*y - z*z)
        view_point: H2Vector = H2Vector(t-1, t*y, t*z)
        return self.view_to_world_space(view_point)

    @property
    def as_json(self) -> dict:
        json_data: dict = super().as_json
        json_data["__class__"] = self.__class__.__name__

        return json_data

    @classmethod
    def from_json(cls, json_data: dict) -> 'PointcareModel':
        model: HorosphericalModel = HorosphericalModel(
            H2Camera.from_json(json_data["camera"]),
            tuple(json_data["display size"])
        )

        model.cull_range = json_data["cull range"]
        return model
