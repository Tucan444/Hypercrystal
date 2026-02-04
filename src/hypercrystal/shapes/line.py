import math
from typing import Union

from pygame import Vector2

from .polygon import H2Polygon
from ..h2_math.h2_vector import H2Vector
from ..h2_math.h2_transform import H2Transform
from .circle import H2Circle

class H2Line:
    def __init__(self, a: H2Vector, b: H2Vector, key=None) -> None:
        self.a: H2Vector = a
        self.b: H2Vector = b
        self.key = key

        assert self.length != 0

    @classmethod
    def LimitingToHorizon(cls, angle_to_horizon: float, a: H2Vector) -> 'H2Line':
        horizon_point: Vector2 = Vector2(math.cos(angle_to_horizon), math.sin(angle_to_horizon))
        return cls.LimitingToHorizonPoint(horizon_point, a)

    @classmethod
    def LimitingToHorizonPoint(cls, horizon_point: Vector2, a: H2Vector) -> 'H2Line':
        a_klein: Vector2 = Vector2(a.y / a.x, a.z / a.x)

        b_klein: Vector2 = a_klein.lerp(horizon_point, 0.05)
        b: H2Vector = H2Vector(1, b_klein.x, b_klein.y).normalized

        return H2Line(a.clone, b)

    @classmethod
    def LimitingToLine(cls, line: 'H2Line', a: H2Vector, AB: bool=True) -> 'H2Line':
        horizon_point: Vector2

        if AB:
            horizon_point = line.horizon_AB
        else:
            horizon_point = line.horizon_BA

        limiting_line: H2Line = cls.LimitingToHorizonPoint(horizon_point, a)
        limiting_line.key = line.key
        return limiting_line

    @classmethod
    def TangentAtT(cls, line: 'H2Line', t: float=0) -> 'H2Line':
        a: H2Vector = line.sample(t) if t != 0 else line.a.clone
        b: H2Vector = line.sample(t + 1)
        rotor: H2Transform = H2Transform.Around(a, angle=H2Transform.HALF_PI)

        b = rotor.apply_on_vector(b)
        return H2Line(a, b, line.key)

    @classmethod
    def TangentToPoint(cls, line: 'H2Line', p: H2Vector) -> Union['H2Line', None]:
        transform: H2Transform = H2Transform.LineToXZ(line.a, line.b)
        p_model: H2Vector = transform @ p

        a_model: H2Vector = H2Vector.FromHyperbolical(0, p_model.beta)
        a: H2Vector = transform.inverse @ a_model

        b: H2Vector = p.clone
        if a.distance_to(b) == 0:
            return None

        return H2Line(a, b, line.key)

    @classmethod
    def UltraparallelAtT(cls, line: 'H2Line', t: float, distance_from_line: float,
                         forward_padding: float=0.5, backward_padding: float=0.5) -> 'H2Line':
        assert forward_padding + backward_padding != 0

        tangent_line: H2Line = cls.TangentAtT(line, t)
        transform: H2Transform = H2Transform.AtoB(tangent_line.a, tangent_line.b, distance_from_line)

        a_online: H2Vector = line.sample(t - backward_padding)
        b_online: H2Vector = line.sample(t + forward_padding)

        a: H2Vector = transform @ a_online
        b: H2Vector = transform @ b_online

        return H2Line(a, b, line.key)

    @classmethod
    def UltraparallelToPoint(cls, line: 'H2Line', p: H2Vector,
            forward_padding: float=0.5, backward_padding: float=0.5) -> Union['H2Line', None]:
        assert forward_padding + backward_padding != 0

        transform: H2Transform = H2Transform.LineToXZ(line.a, line.b)
        p_model: H2Vector = transform @ p

        t: float = p_model.beta / line.length
        distance_from_line: float = -p_model.gamma

        return cls.UltraparallelAtT(line, t, distance_from_line, forward_padding, backward_padding)

    @property
    def angle_at_horizon_AB(self) -> float:
        horizon: Vector2 = self.horizon_AB
        return math.atan2(horizon.y, horizon.x)

    @property
    def angle_at_horizon_BA(self) -> float:
        horizon: Vector2 = self.horizon_BA
        return math.atan2(horizon.y, horizon.x)

    @property
    def horizon_AB(self) -> Vector2:
        return self._get_horizon(self.a, self.b)

    @property
    def horizon_BA(self) -> Vector2:
        return self._get_horizon(self.b, self.a)

    @staticmethod
    def _get_horizon(a: H2Vector, b: H2Vector) -> Vector2:
        a_klein: Vector2 = Vector2(a.y / a.x, a.z / a.x)
        b_klein: Vector2 = Vector2(b.y / b.x, b.z / b.x)
        d: float = a_klein.length()

        if d == 0:
            return b_klein.normalize()

        a: Vector2 = -a_klein.normalize()
        b: Vector2 = (b_klein - a_klein).normalize()

        alpha: float = math.acos(a.dot(b))
        beta: float = math.asin(math.sin(alpha) * d)
        gamma: float = math.pi - alpha - beta

        if alpha == 0:
            return a_klein + (b * (1 + b_klein.length()))

        c_length: float = math.sin(gamma) / math.sin(alpha)
        c_klein: Vector2 = a_klein + (c_length * b)
        return c_klein

    @property
    def length(self) -> float:
        return self.a.distance_to(self.b)

    def set_length(self, length: float, AB: bool=True) -> None:
        assert length != 0

        if AB:
            transform: H2Transform = H2Transform.AtoB(self.a, self.b, length)
        else:
            transform: H2Transform = H2Transform.AtoB(self.b, self.a, length)

        self.b = transform @ self.b

    def approximate(self, samples: int=10) -> H2Polygon:
        assert samples >= 2

        points: list[H2Vector] = [self.a.clone]
        t: float = 1 / (samples - 1)
        movement: H2Transform = H2Transform.LerpAB(self.a, self.b, t)

        for _ in range(samples-1):
            points.append(movement.apply_on_vector(points[-1]))

        return H2Polygon(points, self.key, is_spline=True)

    def sample(self, t: float) -> H2Vector:
        transform: H2Transform = H2Transform.LerpAB(self.a, self.b, t)
        return transform @ self.a

    @property
    def circle_hull(self) -> H2Circle:
        return H2Circle(self.a @ self.b, self.length / 2, self.key)
