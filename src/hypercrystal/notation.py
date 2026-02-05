def untested(func):
    return func


Resolution = tuple[int, int]
H2RayHit = float | None
H2Intersection = list
H2PolygonIntersection = list[tuple[int, H2Intersection]]
H2PolygonsIntersection = list[tuple[int, int, H2Intersection]]
