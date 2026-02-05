from .intersections import Intersections
from ..shapes.circle import H2Circle
from ..shapes.line import H2Line

Collidable = H2Line | H2Circle


class Collisions:
    @classmethod
    def Process(cls, a: Collidable, b: Collidable) -> bool:
        if type(a) == H2Line:
            if type(b) == H2Line:
                return cls.LineLine(a, b)
            elif type(b) == H2Circle:
                return cls.LineCircle(a, b)
            else:
                raise TypeError(f"invalid type of b: {type(b)}")

        elif type(a) == H2Circle:
            if type(b) == H2Line:
                return cls.LineCircle(b, a)
            elif type(b) == H2Circle:
                return cls.CircleCircle(a, b)
            else:
                raise TypeError(f"invalid type of b: {type(b)}")

        else:
            raise TypeError(f"invalid type of a: {type(a)}")

    @classmethod
    def LineLine(cls, a: H2Line, b: H2Line) -> bool:
        return len(Intersections.LineLine(a, b)) > 0

    @classmethod
    def LineCircle(cls, a: H2Line, b: H2Circle) -> bool:
        intersecting: bool = len(Intersections.LineCircle(a, b)) > 0
        if intersecting:
            return True

        a_in: bool = a.a.distance_to(b.center) <= b.radius
        return a_in

    @classmethod
    def CircleCircle(cls, a: H2Circle, b: H2Circle) -> bool:
        d: float = a.center.distance_to(b.center)
        return d < a.radius + b.radius
