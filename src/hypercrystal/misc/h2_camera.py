from ..h2_math.h2_vector import H2Vector
from ..h2_math.h2_transform import H2Transform


class H2Camera:
    def __init__(self, position: H2Vector, up: H2Vector, zoom: float=1, invert_y_movement: bool=True,
                 bounded: bool=True, bounded_radius: float = 7.5):
        self.position: H2Vector = position
        self.up: H2Vector = up
        self.right: H2Vector = H2Transform.Around(self.position, -H2Transform.HALF_PI) @ self.up

        self.bounded: bool = bounded
        self.bounded_radius: float = bounded_radius

        # zoom is ignored for bounded region projections
        self.zoom: float = zoom
        self.invert_y_movement: bool = invert_y_movement

    @property
    def transform(self) -> H2Transform:
        return H2Transform.LineToXY(self.position, self.right)

    def _use_transform(self, transform: H2Transform, ignore_position: bool=False) -> None:
        self._apply_transform(transform, ignore_position)
        self._check_bounds(transform)

    def _apply_transform(self, transform: H2Transform, ignore_position: bool=False) -> None:
        if not ignore_position:
            self.position = transform @ self.position

        self.up = transform @ self.up
        self.right = transform @ self.right

    def move_right(self, distance: float) -> None:
        transform: H2Transform = H2Transform.AtoB(self.position, self.right, distance)
        self._use_transform(transform)

    def move_left(self, distance: float) -> None:
        transform: H2Transform = H2Transform.AtoB(self.position, self.right, -distance)
        self._use_transform(transform)

    def move_up(self, distance: float) -> None:
        if self.invert_y_movement:
            distance *= -1

        transform: H2Transform = H2Transform.AtoB(self.position, self.up, distance)
        self._use_transform(transform)

    def move_down(self, distance: float) -> None:
        if self.invert_y_movement:
            distance *= -1

        transform: H2Transform = H2Transform.AtoB(self.position, self.up, -distance)
        self._use_transform(transform)

    def rotate(self, angle: float) -> None:
        transform: H2Transform = H2Transform.Around(self.position, angle)
        self._use_transform(transform, True)

    def move(self, direction: H2Vector, distance: float) -> None:
        transform: H2Transform = H2Transform.AtoB(self.position, direction, distance)
        self._use_transform(transform)

    def move_by_theta(self, theta: float, distance: float) -> None:
        rotor: H2Transform = H2Transform.Around(self.position, theta)
        direction: H2Vector = rotor.apply_on_vector(self.right)
        self.move(direction, distance)

    def _check_bounds(self, transform: H2Transform) -> None:
        if not self.bounded:
            return

        if self.position.alpha <= self.bounded_radius:
            return

        inverse: H2Transform = transform.inverse
        self._use_transform(inverse)
