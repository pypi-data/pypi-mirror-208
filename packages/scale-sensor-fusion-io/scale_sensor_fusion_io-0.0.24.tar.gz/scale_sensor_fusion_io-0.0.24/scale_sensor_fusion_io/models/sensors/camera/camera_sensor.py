from dataclasses import dataclass
from typing import List, Literal, Optional

import numpy as np
import numpy.typing as npt
from scale_sensor_fusion_io.models.sensors.camera import (
    CameraIntrinsics,
)

from ...common import SensorID, SensorKind
from ...paths import PosePath


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
    type: Literal[SensorKind.Camera] = SensorKind.Camera
    parent_id: Optional[SensorID] = None
