from pathlib import Path
import json

from ..h2_math.h2_ray import H2Ray
from ..h2_math.h2_transform import H2Transform
from ..h2_math.h2_vector import H2Vector
from ..h2_math.matrix3D import Matrix3D

from .h2_billboard import H2Billboard
from .h2_camera import H2Camera
from .h2_walker import H2Walker

from ..projections.gans import GansModel
from ..projections.general_perspective import GeneralPerspectiveModel
from ..projections.hyperbolical import HyperbolicalModel
from ..projections.hyperpolar import HyperpolarModel
from ..projections.klein import KleinModel
from ..projections.pointcare import PointcareModel

from ..shapes.arc import H2Arc
from ..shapes.circle import H2Circle
from ..shapes.horocycle import Horocycle
from ..shapes.hypercycle import Hypercycle
from ..shapes.line import H2Line
from ..shapes.polygon import H2Polygon
from ..shapes.projected import ProjectedCircle, ProjectedLine, ProjectedPolygon

from ..tessellations.flood_tessellation import FloodTessellation

class H2Loader:

    CLASS_MAP = {
        "H2Ray": H2Ray,
        "H2Transform": H2Transform,
        "H2Vector": H2Vector,
        "Matrix3D": Matrix3D,
        "H2Billboard": H2Billboard,
        "H2Camera": H2Camera,
        "H2Walker": H2Walker,
        "GansModel": GansModel,
        "GeneralPerspectiveModel": GeneralPerspectiveModel,
        "HyperbolicalModel": HyperbolicalModel,
        "HyperpolarModel": HyperpolarModel,
        "KleinModel": KleinModel,
        "PointcareModel": PointcareModel,
        "H2Arc": H2Arc,
        "H2Circle": H2Circle,
        "Horocycle": Horocycle,
        "Hypercycle": Hypercycle,
        "H2Line": H2Line,
        "H2Polygon": H2Polygon,
        "ProjectedCircle": ProjectedCircle,
        "ProjectedLine": ProjectedLine,
        "ProjectedPolygon": ProjectedPolygon,
        "FloodTessellation": FloodTessellation,
    }

    @classmethod
    def load(cls, json_data: dict) -> object:
        assert "__class__" in json_data

        class_name: str = json_data["__class__"]

        if class_name not in cls.CLASS_MAP:
            raise ValueError(f"Unknown class: {class_name}")

        object_ = cls.CLASS_MAP[class_name].from_json(json_data)
        return object_

    @classmethod
    def load_from_file(cls, path: Path) -> object:
        with open(path, 'r') as f:
            object_data = json.load(f)

        return cls.load(object_data)

    @classmethod
    def save_to_file(cls, path: Path, object_: object) -> None:
        with open(path, 'w') as f:
            json.dump(object_.as_json, f, indent=4)
