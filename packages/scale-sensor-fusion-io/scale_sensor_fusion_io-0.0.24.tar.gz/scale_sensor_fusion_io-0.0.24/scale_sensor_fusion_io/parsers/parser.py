# type: ignore
from enum import Enum
from typing_extensions import TypeAlias
from typing import (
    List,
    Literal,
    Optional,
    Union,
    TypeVar,
    Generic,
    Callable,
)
from scale_json_binary import read_file
from scale_sensor_fusion_io.models import (
    PosePath,
    Scene,
    CameraSensor,
    CameraIntrinsics,
    CameraDistortion,
    Sensor,
    LidarSensor,
    LidarSensorFrame,
    LidarSensorPoints,
)

from dataclasses import dataclass, asdict
from scale_sensor_fusion_io.spec import BS5

import scale_sensor_fusion_io.parsers.dacite_internal as dacite

CFG = dacite.Config(cast=[Enum, tuple])

"""Parse a bs5 file"""

T = TypeVar("T")  # Declare type variable


@dataclass
class ParseSuccess(Generic[T]):
    data: T
    success: Literal[True] = True


PathField: TypeAlias = Union[int, str]
PathInput: TypeAlias = Union[PathField, List[PathField]]


@dataclass
class ErrorDetails:
    path: List[PathField]
    errors: List[str]

    @staticmethod
    def from_msg(msg: str, path: Optional[PathInput] = None) -> "ErrorDetails":
        """
        Helper function to initiate a ErrorDetails from a single error message to reduce boilerplate
        """
        return ErrorDetails(
            path=(path if type(path) is list else [path]) if path else [], errors=[msg]
        )

    @staticmethod
    def missing_field(field: str, path: Optional[PathInput] = None) -> "ErrorDetails":
        """
        Helper function to template out details for missing field
        """
        return ErrorDetails(
            path=(path if type(path) is list else [path]) if path else [],
            errors=[f"Missing field: {field}"],
        )


@dataclass
class ParseError:
    details: List[ErrorDetails]
    success: Literal[False] = False

    @staticmethod
    def from_msg(msg: str, path: Optional[PathInput] = None) -> "ParseError":
        """
        Helper function to initiate a ParseError from a single error message to reduce boilerplate
        """
        return ParseError(details=[ErrorDetails.from_msg(msg, path)])

    @staticmethod
    def missing_field(field: str, path: Optional[PathInput] = None) -> "ParseError":
        """
        Helper function to template out details for missing field
        """
        return ParseError(details=[ErrorDetails.missing_field(field, path)])

    def prepend_path(self, path: List[PathField]) -> "ParseError":
        """Prepend path of error with additional prefix"""
        for err in self.details:
            err.path = path + err.path
        return self


ParseResult: TypeAlias = Union[ParseSuccess[T], ParseError]


def parse_radar(sensor: dict) -> ParseResult:
    return ParseError.from_msg("not implemented")


def to_lidar_frame(lidar_frame: BS5.LidarSensorFrame) -> ParseResult[LidarSensorFrame]:
    return ParseSuccess(
        LidarSensorFrame(
            timestamp=lidar_frame.timestamp,
            points=LidarSensorPoints(
                positions=lidar_frame.points.positions.reshape(-1, 3),
                colors=lidar_frame.points.colors.reshape(-1, 3)
                if lidar_frame.points.colors is not None
                else None,
                timestamps=lidar_frame.points.timestamps,
                intensities=lidar_frame.points.intensities,
            ),
        )
    )


def handle_dacite(
    fn: Callable[[], T], error_details: List[ErrorDetails]
) -> Optional[T]:
    try:
        return fn()
    except dacite.AggregatedError as e:
        error_details.extend([convert_error(err) for err in e.errors])
    except dacite.DaciteFieldError as e:
        error_details.append(convert_error(e))
    return None


def handle_result(
    res: ParseResult[T], error_details: List[ErrorDetails], path: List[PathField] = []
) -> Optional[T]:
    if res.success:
        return res.data
    else:
        error_details.extend(
            res.details if not path else res.prepend_path(path).details
        )
        return None


def parse_lidar(sensor: dict) -> ParseResult[LidarSensor]:
    error_details: List[ErrorDetails] = []

    # Cast to BS5 dataclass first
    try:
        result = dacite.from_dict(
            data_class=BS5.LidarSensor,
            data=sensor,
            config=CFG,
        )
    except dacite.AggregatedError as e:
        error_details.extend([convert_error(err) for err in e.errors])
        return ParseError(error_details)

    except dacite.DaciteFieldError as e:
        error_details.append(convert_error(e))
        return ParseError(error_details)

    bs5_lidar = result

    # pose path
    pose_path = handle_result(to_pose_path(bs5_lidar.poses), error_details)

    # lidar frames
    frames: List[LidarSensorFrame] = []
    for idx, _frame in enumerate(bs5_lidar.frames):
        frame = handle_result(to_lidar_frame(_frame), error_details, ["frames", idx])
        if frame:
            frames.append(frame)

    if len(error_details) > 0:
        return ParseError(details=error_details)

    assert pose_path is not None
    return ParseSuccess(
        LidarSensor(
            id=bs5_lidar.id,
            poses=pose_path,
            frames=frames,
            parent_id=bs5_lidar.parent_id,
            coordinates=bs5_lidar.coordinates,
        )
    )


def to_intrinsics(intrinsics: BS5.CameraIntrinsics) -> ParseResult[CameraIntrinsics]:
    distortion = None
    if intrinsics.distortion:
        distortion = CameraDistortion.from_values(
            intrinsics.distortion.model, intrinsics.distortion.params
        )
    input_values = asdict(intrinsics)
    del input_values["distortion"]
    return ParseSuccess(CameraIntrinsics(**input_values, distortion=distortion))


def to_pose_path(pose_path: BS5.PosePath) -> ParseResult[PosePath]:
    error_details = []
    try:
        return ParseSuccess(PosePath(pose_path.values, pose_path.timestamps))
    except Exception as e:
        error_details.append(
            ErrorDetails.from_msg(
                f"Unable to instantiate PosePath. Error: {e}", path="poses"
            )
        )
        return ParseError(error_details)


def convert_error(e: dacite.DaciteFieldError) -> ErrorDetails:
    return ErrorDetails(
        path=e.field_path.split(".") if e.field_path else [], errors=[str(e)]
    )


def parse_camera(sensor: dict) -> ParseResult[CameraSensor]:
    error_details: List[ErrorDetails] = []

    # Cast to BS5 dataclass first
    try:
        result = dacite.from_dict(
            data_class=BS5.CameraSensor,
            data=sensor,
            config=CFG,
        )
    except dacite.AggregatedError as e:
        error_details.extend([convert_error(err) for err in e.errors])
        return ParseError(error_details)

    except dacite.DaciteFieldError as e:
        error_details.append(convert_error(e))
        return ParseError(error_details)

    bs5_camera = result

    # camera intrinsics
    intrinsics = handle_result(
        to_intrinsics(bs5_camera.intrinsics), error_details, path=["intrinsics"]
    )

    # camera content
    if (not bs5_camera.video and not bs5_camera.images) or (
        bs5_camera.video and bs5_camera.images
    ):
        error_details.append(
            ErrorDetails.from_msg('Exactly one of "images" or "video" expected')
        )

    # pose path
    pose_path = handle_result(to_pose_path(bs5_camera.poses), error_details)

    if len(error_details) > 0:
        return ParseError(details=error_details)

    assert pose_path is not None
    assert intrinsics is not None
    return ParseSuccess(
        CameraSensor(
            id=bs5_camera.id,
            poses=pose_path,
            intrinsics=intrinsics,
            parent_id=bs5_camera.parent_id,
        )
    )


def parse_sensor(sensor: dict) -> ParseResult[Sensor]:
    error_details: List[ErrorDetails] = []

    # type
    sensor_type = sensor.get("type")
    if not sensor_type:
        error_details.append(ErrorDetails.missing_field("type"))

    parsed_sensor: Optional[Sensor] = None
    if sensor_type == "camera":
        parsed_sensor = handle_result(parse_camera(sensor), error_details)
    elif sensor_type == "lidar":
        parsed_sensor = handle_result(parse_lidar(sensor), error_details)
    elif sensor_type == "radar":
        parsed_sensor = handle_result(parse_radar(sensor), error_details)
    else:
        error_details.append(
            ErrorDetails(
                path=["type"], errors=[f"Invalid sensor type provided: {sensor_type}"]
            )
        )

    if len(error_details) > 0:
        return ParseError(details=error_details)

    assert parsed_sensor is not None
    return ParseSuccess(data=parsed_sensor)


class SceneParser:
    """
    Parses a given bs5 file.
    """

    def __init__(self, url: str) -> None:
        self.url = url

    def parse(self) -> ParseResult[Scene]:
        # header = parse_header(self.url)
        header = read_file(self.url)

        error_details: List[ErrorDetails] = []

        # version
        version = header.get("version")
        if version is None:
            return ParseError.missing_field("version")

        if not header["version"].startswith("1.0") and not header["version"].startswith(
            "5.1"
        ):
            return ParseError.from_msg(
                f"Invalid version provided: {header['version']}", path=["version"]
            )

        # sensors
        sensors = []
        _sensors = header.get("sensors")
        if _sensors:
            if type(_sensors) != list:
                return ParseError.from_msg("Sensors must be a list", path=["sensors"])

            for idx, sensor in enumerate(_sensors):
                sensor = handle_result(
                    parse_sensor(sensor), error_details, path=["sensors", idx]
                )
                if sensor:
                    sensors.append(sensor)

        # time_offset
        fields = BS5.Scene.__dataclass_fields__
        time_offset = handle_dacite(
            lambda: dacite.cast_field(header, field=fields["time_offset"], config=CFG),
            error_details,
        )

        # time_unit
        time_unit = handle_dacite(
            lambda: dacite.cast_field(header, field=fields["time_unit"], config=CFG),
            error_details,
        )

        # Additional scene level validations
        if len(error_details) == 0:
            scene = Scene(sensors=sensors, time_offset=time_offset, time_unit=time_unit)
            return ParseSuccess(data=scene)

        return ParseError(details=error_details)
