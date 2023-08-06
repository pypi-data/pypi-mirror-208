from dataclasses import dataclass
from typing import List, Literal, Optional, Union
from enum import Enum


import scale_sensor_fusion_io.spec.sfs as SFS


SensorID = SFS.SensorID
AnnotationID = SFS.AnnotationID

PosePath = SFS.PosePath

PointsSensorPoints = SFS.PointsSensorPoints
PointsSensor = SFS.PointsSensor

LidarSensorPoints = SFS.LidarSensorPoints
LidarSensorFrame = SFS.LidarSensorFrame
LidarSensor = SFS.LidarSensor

RadarSensorPoints = SFS.RadarSensorPoints
RadarSensorFrame = SFS.RadarSensorFrame
RadarSensor = SFS.RadarSensor

DistortionModel = SFS.DistortionModel
CameraDistortion = SFS.CameraDistortion

CameraIntrinsics = SFS.CameraIntrinsics

CameraSensorVideo = SFS.CameraSensorVideo
CameraSensorImage = SFS.CameraSensorImage
CameraSensor = SFS.CameraSensor

OdometrySensor = SFS.OdometrySensor

AttributePath = SFS.AttributePath

CuboidPath = SFS.CuboidPath
CuboidActivationPath = SFS.CuboidActivationPath
CuboidProjectionPath = SFS.CuboidProjectionPath


@dataclass
class StaticPath:
    timestamps: List[int]
    values: List[bool]


@dataclass
class CuboidMetadata:
    static_path: StaticPath


@dataclass
class _CuboidAnnotationBase:
    cuboid_metadata: CuboidMetadata


@dataclass
class CuboidAnnotation(SFS.CuboidAnnotation, _CuboidAnnotationBase):
    pass


AttributesAnnotation = SFS.AttributesAnnotation
Box2DPath = SFS.Box2DPath
Box2DAnnotation = SFS.Box2DAnnotation
PolygonPath = SFS.PolygonPath
PolygonAnnotation = SFS.PolygonAnnotation

EventAnnotation = SFS.EventAnnotation

LabeledPoint = SFS.LabeledPoint
LabeledPointsAnnotation = SFS.LabeledPointsAnnotation


class CuboidLayerMode(Enum):
    Position = "position"
    PositionRotation = "position-rotation"
    ZLevel = "z-level"
    XY = "XY"
    ICP = "icp"


@dataclass
class LocalizationAdjustmentLayerMetadata:
    layer_type: Literal["base", "cuboid"]
    order: int
    name: str
    cuboids: Optional[List[CuboidPath]] = None
    algorithm: Optional[CuboidLayerMode] = None


## NOTE: This is implemented this way to be able to inherit from the SFS dataclasses, which contain defaults
@dataclass
class _LocalizationAdjustmentAnnotationBase:
    layer_metadata: LocalizationAdjustmentLayerMetadata


@dataclass
class LocalizationAdjustmentAnnotation(
    SFS.LocalizationAdjustmentAnnotation, _LocalizationAdjustmentAnnotationBase
):
    pass


ObjectAnnotation = SFS.ObjectAnnotation

Sensor = Union[CameraSensor, LidarSensor, RadarSensor, OdometrySensor, PointsSensor]

Annotation = Union[
    CuboidAnnotation,
    AttributesAnnotation,
    Box2DAnnotation,
    PolygonAnnotation,
    LabeledPointsAnnotation,
    LocalizationAdjustmentAnnotation,
    ObjectAnnotation,
]


@dataclass
class Scene:
    version: Literal["5.1"] = "5.1"
    sensors: Optional[List[Sensor]] = None
    annotations: Optional[List[Annotation]] = None
    attributes: Optional[List[AttributePath]] = None
    time_offset: Optional[int] = None
    time_unit: Optional[Literal["microseconds", "nanoseconds"]] = "microseconds"
