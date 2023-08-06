from enum import Enum
from typing import Union

SensorID = Union[str, int]
AnnotationID = Union[str, int]


class AnnotationKind(Enum):
    Attributes = "attributes"
    Box2D = "box_2d"
    Cuboid = "cuboid"
    Event = "event"
    LabeledPoints = ("labeled_points",)
    LocalizationAdjustment = "localization_adjustment"
    Object = ("object",)
    Polygon = "polygon"


class SensorKind(Enum):
    Camera = "camera"
    Lidar = "lidar"
    Radar = "radar"
    Points = "points"
    Odometer = "odometer"
