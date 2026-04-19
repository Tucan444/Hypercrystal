from ..h2_math.h2_vector import H2Vector
from ..shapes.circle import H2Circle
import random


class H2Cluster:
    def __init__(self, clusters: list['H2Cluster']=None, circles: list[H2Circle]=None) -> None:
        self.circle: H2Circle | None = None
        self.clusters: list[H2Cluster] = [] if clusters is None else clusters
        self.circles: list[H2Circle] = [] if circles is None else circles

    @property
    def circles_visual(self) -> list[H2Circle]:
        if self.circle is None:
            self.compute_circle()

        circles: list[H2Circle] = [self.circle] + self.circles

        for cluster in self.clusters:
            circles += cluster.circles_visual

        circles.sort(key=lambda x: -x.radius)
        return circles

    @property
    def circles_reduction(self):
        circles: list[H2Circle] = []

        for circle in self.clusters:
            if circle.circle is None:
                circle.compute_circle()

            circles.append(circle.circle)

        for circle in self.circles:
            circles.append(circle)

        return circles

    @property
    def points(self) -> list[H2Vector]:
        points: list[H2Vector] = []

        for cluster in self.clusters:
            if cluster.circle is None:
                cluster.compute_circle()

            points.append(cluster.circle.center)

        for circle in self.circles:
            points.append(circle.center)

        return points

    @property
    def points_linked(self) -> list[H2Vector]:
        points: list[H2Vector] = []

        for cluster in self.clusters:
            if cluster.circle is None:
                cluster.compute_circle()

            points.append(cluster.circle.center.clone)
            points[-1].key = cluster

        for circle in self.circles:
            points.append(circle.center.clone)
            points[-1].key = circle

        return points

    def compute_circle(self) -> None:
        circles: list[H2Circle] = self.circles_reduction
        points: list[H2Vector] = [
            circle.center for circle in circles
        ]

        center: H2Vector = H2Vector.GetMean(points)
        radius: float = 0

        for circle in circles:
            new_radius: float = circle.center.distance_to(center) + circle.radius
            radius = max(radius, new_radius)

        self.circle = H2Circle(center, radius)

    @classmethod
    def clusterize(cls, circles: list[H2Circle],
                   k: int=3, steps: int = 5, leaf_n: int=20) -> 'H2Cluster':
        root: H2Cluster = H2Cluster(circles=circles)
        cls.split_cluster(root, k, steps, leaf_n)
        return root

    @classmethod
    def split_cluster(cls, cluster: 'H2Cluster',
                       k: int = 3, steps: int = 5, leaf_n: int = 20) -> None:
        points: list[H2Vector] = cluster.points_linked
        if len(points) <= leaf_n:
            return

        centers: list[H2Vector] = random.sample(points, k)
        centers = [c.clone for c in centers]
        groups: list[list[H2Vector]] = [[] for _ in range(k)]

        for step_i in range(steps):
            groups = [[] for _ in range(k)]

            for p in points:
                distances: list[tuple[float, int]] = []
                for i, c in enumerate(centers):
                    distances.append((c.distance_to(p), i))

                closest: tuple[float, int] = min(distances, key=lambda x: x[0])
                groups[closest[1]].append(p)

            for i, g in enumerate(groups):
                centers[i] = H2Vector.GetMean(g)

            print(f"Clusterizing {len(points)} points, step {step_i+1}/{steps} done")

        cluster.clusters = []
        cluster.circles = []

        for g in groups:
            new_cluster: H2Cluster = H2Cluster()

            for element in g:
                if type(element.key) == H2Cluster:
                    new_cluster.clusters.append(element.key)
                elif type(element.key) ==H2Circle:
                    new_cluster.circles.append(element.key)

                else:
                    raise Exception(f"uknown type {type(element.key)}")

            cls.split_cluster(new_cluster, k, steps, leaf_n)
            cluster.clusters.append(new_cluster)
