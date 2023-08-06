from dataclasses import dataclass
from typing import List, Literal, Optional

import numpy as np
import numpy.typing as npt

from ..common import AnnotationID, AnnotationKind, SensorID


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
    type: Literal[AnnotationKind.LabeledPoints] = AnnotationKind.LabeledPoints
    parent_id: Optional[AnnotationID] = None
