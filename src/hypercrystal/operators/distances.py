from ..h2_math.h2_transform import H2Transform
from ..h2_math.h2_vector import H2Vector
from ..shapes.circle import H2Circle
from ..shapes.line import H2Line

Measurable = H2Line | H2Circle | H2Vector


class Distances:
    @classmethod
    def Process(cls, a: Measurable, b: Measurable) -> float:
        if type(a) == H2Vector:
            if type(b) == H2Vector:
                return cls.PointPoint(a, b)
            elif type(b) == H2Line:
                return cls.PointLine(a, b)
            elif type(b) == H2Circle:
                return cls.PointCircle(a, b)

        elif type(a) == H2Line:
            if type(b) == H2Vector:
                return cls.PointLine(b, a)
            elif type(b) == H2Line:
                raise TypeError(f"LineLine distance not supported")
            elif type(b) == H2Circle:
                raise TypeError(f"LineCircle distance not supported")
            else:
                raise TypeError(f"invalid type of b: {type(b)}")

        elif type(a) == H2Circle:
            if type(b) == H2Vector:
                return cls.PointCircle(b, a)
            elif type(b) == H2Line:
                raise TypeError(f"LineCircle distance not supported")
            elif type(b) == H2Circle:
                return cls.CircleCircle(a, b)
            else:
                raise TypeError(f"invalid type of b: {type(b)}")

        else:
            raise TypeError(f"invalid type of a: {type(a)}")

    @classmethod
    def PointPoint(cls, a: H2Vector, b: H2Vector) -> float:
        return a.distance_to(b)

    @classmethod
    def PointLine(cls, a: H2Vector, b: H2Line) -> float:
        transform: H2Transform = H2Transform.LineToXZ(b.a, b.b)
        a_: H2Vector = transform @ a
        beta: float = a_.beta

        if beta < 0:
            return a.distance_to(b.a)
        elif beta > b.length:
            return a.distance_to(b.b)

        return abs(a_.gamma)

    @classmethod
    def PointCircle(cls, a: H2Vector, b: H2Circle) -> float:
        return a.distance_to(b.center) - b.radius

    @classmethod
    def CircleCircle(cls, a: H2Circle, b: H2Circle) -> float:
        return (a.center.distance_to(b.center) - a.radius) - b.radius
