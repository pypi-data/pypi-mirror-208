from dataclasses import dataclass
from typing import List, Literal, Optional, Union

import numpy as np
import numpy.typing as npt

SensorID = Union[str, int]
AnnotationID = Union[str, int]


# Define PosePath dataclass
@dataclass
class PosePath:
    timestamps: List[int]
    values: List[List[float]]  # x y z qx qy qz qw


# Define PointsSensorPoints dataclass
@dataclass
class PointsSensorPoints:
    positions: npt.NDArray[np.float32]
    colors: Optional[npt.NDArray[np.uint8]]


# Define PointsSensor dataclass
@dataclass
class PointsSensor:
    id: SensorID
    points: PointsSensorPoints
    type: Literal["points"] = "points"
    parent_id: Optional[SensorID] = None


# Define LidarSensorPoints dataclass
@dataclass
class LidarSensorPoints:
    positions: npt.NDArray[np.float32]
    colors: Optional[npt.NDArray[np.uint8]] = None
    intensities: Optional[npt.NDArray[np.uint8]] = None
    timestamps: Optional[Union[npt.NDArray[np.uint32], npt.NDArray[np.uint64]]] = None


# Define LidarSensorFrame dataclass
@dataclass
class LidarSensorFrame:
    timestamp: int
    points: LidarSensorPoints


# Define LidarSensor dataclass
@dataclass
class LidarSensor:
    id: SensorID
    poses: PosePath
    frames: List[LidarSensorFrame]
    parent_id: Optional[SensorID] = None
    coordinates: Literal["ego", "world"] = "world"
    type: Literal["lidar"] = "lidar"


# Define RadarSensorPoints dataclass
@dataclass
class RadarSensorPoints:
    positions: npt.NDArray[np.float32]
    directions: Optional[npt.NDArray[np.float32]] = None
    lengths: Optional[npt.NDArray[np.float32]] = None
    timestamps: Optional[Union[npt.NDArray[np.uint32], npt.NDArray[np.uint64]]] = None


# Define RadarSensorFrame dataclass
@dataclass
class RadarSensorFrame:
    timestamp: int
    points: RadarSensorPoints


# Define RadarSensor dataclass
@dataclass
class RadarSensor:
    id: SensorID
    poses: PosePath
    frames: List[RadarSensorFrame]
    type: Literal["radar"] = "radar"
    coordinates: Literal["ego", "world"] = "world"
    parent_id: Optional[SensorID] = None


# Define DistortionModel enum
DistortionModel = Literal[
    "brown_conrady",
    "mod_equi_fish",
    "mod_kannala",
    "fisheye",
    "fisheye_rad_tan_prism",
    "cylindrical",
    "omnidirectional",
]


# Define CameraDistortion dataclass
@dataclass
class CameraDistortion:
    model: DistortionModel
    params: List[float]


# Define CameraIntrinsics dataclass
@dataclass
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int
    distortion: Optional[CameraDistortion]


# Define CameraSensorContent dataclass
@dataclass
class CameraSensorVideo:
    timestamps: List[int]
    content: npt.NDArray[np.uint8]
    fps: float


# Define CameraSensorImages dataclass
@dataclass
class CameraSensorImage:
    timestamp: int
    content: npt.NDArray[np.uint8]


# Define CameraSensor dataclass
@dataclass
class CameraSensor:
    id: SensorID
    poses: PosePath
    intrinsics: CameraIntrinsics
    video: Optional[CameraSensorVideo] = None
    images: Optional[List[CameraSensorImage]] = None
    type: Literal["camera"] = "camera"
    parent_id: Optional[SensorID] = None


# Define OdometrySensor dataclass
@dataclass
class OdometrySensor:
    id: SensorID
    poses: PosePath
    type: Literal["odometry"] = "odometry"
    parent_id: Optional[SensorID] = None


# Define AttributePath dataclass
@dataclass
class AttributePath:
    name: str
    timestamps: List[int]
    values: List[Union[str, int, List[str]]]
    sensor_id: Optional[SensorID] = None
    static: bool = False


# Define CuboidPath dataclass
@dataclass
class CuboidPath:
    timestamps: List[int]
    values: List[List[float]]  # x y z yaw pitch roll dx dy dz


# Define CuboidActivationPath dataclass
@dataclass
class CuboidActivationPath:
    sensor_id: SensorID
    timestamps: List[int]
    durations: List[float]
    cuboids: Optional[List[List[float]]]  # x y z yaw pitch roll dx dy dz


# Define CuboidProjectionPath dataclass
@dataclass
class CuboidProjectionPath:
    sensor_id: SensorID  # 2d sensor like cameras
    timestamps: List[int]
    boxes: List[List[float]]  # x y width height
    cuboids: Optional[List[List[float]]]  # dx dy dz px py pz roll pitch yaw


# Define CuboidAnnotation dataclass
@dataclass
class CuboidAnnotation:
    id: AnnotationID
    path: CuboidPath
    label: Optional[str] = None
    stationary: Optional[bool] = False
    type: Literal["cuboid"] = "cuboid"
    attributes: Optional[List[AttributePath]] = None
    sensor_attributes: Optional[List[AttributePath]] = None
    sensor_activations: Optional[List[CuboidActivationPath]] = None
    sensor_projections: Optional[List[CuboidProjectionPath]] = None
    parent_id: Optional[AnnotationID] = None


# Define AttributesAnnotation dataclass
@dataclass
class AttributesAnnotation:
    id: AnnotationID
    type: Literal["attributes"] = "attributes"
    parent_id: Optional[AnnotationID] = None
    attributes: Optional[List[AttributePath]] = None
    sensor_attributes: Optional[List[AttributePath]] = None


@dataclass
class Box2DPath:
    timestamps: List[int]
    values: List[List[float]]  # left, top, width, height


@dataclass
class Box2DAnnotation:
    id: AnnotationID
    sensor_id: SensorID
    path: Box2DPath
    type: Literal["box"] = "box"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class PolygonPath:
    timestamps: List[int]
    values: List[List[float]]  # x_0, y_0, x_1, y_1, ..., x_n, y_n


@dataclass
class PolygonAnnotation:
    id: AnnotationID
    sensor_id: SensorID
    path: PolygonPath
    type: Literal["polygon"] = "polygon"
    parent_id: Optional[AnnotationID] = None
    stationary: Optional[bool] = False
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


@dataclass
class EventAnnotation:
    id: AnnotationID
    start: int
    type: Literal["event"] = "event"
    parent_id: Optional[AnnotationID] = None
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None
    duration: Optional[int] = None
    sensor_id: Optional[SensorID] = None


# Define LabeledPointsAnnotationLabeledPoint dataclass
@dataclass
class LabeledPoint:
    sensor_id: SensorID
    point_ids: npt.NDArray[np.uint32]
    sensor_frame: Optional[int] = None


# Define LabeledPointsAnnotation dataclass
@dataclass
class LabeledPointsAnnotation:
    id: AnnotationID
    label: str
    labeled_points: List[LabeledPoint]
    is_instance: bool = False
    type: Literal["labeled_points"] = "labeled_points"
    parent_id: Optional[AnnotationID] = None


@dataclass
class LocalizationAdjustmentAnnotation:
    id: AnnotationID
    poses: PosePath
    type: Literal["localization_adjustment"] = "localization_adjustment"
    parent_id: Optional[AnnotationID] = None


@dataclass
class ObjectAnnotation:
    id: AnnotationID
    type: Literal["object"] = "object"
    parent_id: Optional[AnnotationID] = None
    label: Optional[str] = None
    attributes: Optional[List[AttributePath]] = None


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

# Define Scene dataclass


@dataclass
class Scene:
    version: Literal["1.0"] = "1.0"
    sensors: Optional[List[Sensor]] = None
    annotations: Optional[List[Annotation]] = None
    attributes: Optional[List[AttributePath]] = None
    time_offset: Optional[int] = None
    time_unit: Optional[Literal["microseconds", "nanoseconds"]] = "microseconds"
