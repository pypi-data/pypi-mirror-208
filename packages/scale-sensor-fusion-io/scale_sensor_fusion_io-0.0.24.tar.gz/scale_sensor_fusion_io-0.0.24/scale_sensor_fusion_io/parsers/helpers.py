# from enum import Enum
# from typing_extensions import TypeAlias
# from typing import Any, List, Type, Literal, Optional, Union, Tuple, TypeVar, Generic
# from scale_json_binary import read_file
# from scale_sensor_fusion_io.models import (
#     PosePath,
#     Scene,
#     SensorID,
#     AnnotationID,
#     CameraSensor,
#     CameraIntrinsics,
#     Sensor,
#     LidarSensor,
#     LidarSensorFrame,
#     LidarSensorPoints,
#     RadarSensor,
# )
# 
# from dataclasses import dataclass, field, asdict
# from scale_sensor_fusion_io.spec import BS5
# 
# import dacite
# import ujson
# 
# from scale_sensor_fusion_io.parsers.dacite_internal.types import is_instance
# from scale_sensor_fusion_io.parsers import dacite_internal
# 
# from scale_sensor_fusion_io.models.sensors.camera.camera_sensor import CameraDistortion
# 
# def parse_parent_id(sensor: dict) -> ParseResult[Optional[SensorID]]:
#     """Parse parent id from sensor object"""
#     parent_id = sensor.get("parent_id")
#     if parent_id and not (type(parent_id) == int or type(parent_id) == str):
#         return ParseError.from_msg(
#             f"Invalid sensor id provided: {parent_id}. Only int or string supported",
#             path="parent_id",
#         )
# 
#     return ParseSuccess(parent_id)
# 
# 
# def parse_sensor_id(sensor: dict) -> ParseResult[SensorID]:
#     """Parse sensor id from sensor object"""
#     # sensor id
#     sensor_id = sensor.get("id")
#     if not sensor_id:
#         return ParseError.from_msg(f"Missing field: id", path="id")
# 
#     if not (type(sensor_id) == int or type(sensor_id) == str):
#         return ParseError.from_msg(
#             f"Invalid sensor id provided: {sensor_id}. Only int or string supported",
#             path="id",
#         )
# 
#     return ParseSuccess(sensor_id)
# 
# 
# def parse_pose_path(sensor: dict) -> ParseResult[PosePath]:
#     """
#     Parse pose_path from sensor object
#     """
#     error_details = []
#     poses = sensor.get("poses")
#     if not poses:
#         return ParseError.missing_field("poses")
# 
#     values = poses.get("values")
#     if values is None:
#         error_details.append(
#             ErrorDetails.missing_field("values", path=["poses", "values"])
#         )
# 
#     timestamps = poses.get("timestamps")
#     if timestamps is None:
#         error_details.append(
#             ErrorDetails.missing_field("timestamps", path=["poses", "timestamps"])
#         )
# 
#     try:
#         pose_path = PosePath(values, timestamps)
#     except Exception as e:
#         error_details.append(
#             ErrorDetails.from_msg(
#                 f"Unable to instantiate PosePath. Error: {e}", path="poses"
#             )
#         )
# 
#     if len(error_details) > 0:
#         return ParseError(details=error_details)
#     return ParseSuccess(pose_path)
# 
# 
# 
# def parse_camera_intrinsics(intrinsics: dict) -> ParseResult[CameraIntrinsics]:
#     error_details = []
# 
#     CUSTOM_CHECK = ["distortion"]
# 
#     # for field_key, field_data in BS5.CameraIntrinsics.__dataclass_fields__.items():
#     #     if field_key in CUSTOM_CHECK:
#     #         continue
# 
#     #     if not is_instance(intrinsics.get(field_key), field_data.type):
#     #         error_details.append(ErrorDetails.wrong_type(field_key))
# 
#     # print(BS5.CameraIntrinsics(**intrinsics))
# 
#     init_values = intrinsics
#     # fx = intrinsics.get("fx")
#     # if fx is None:
#     #     error_details.append(ErrorDetails.missing_field("fx"))
# 
#     # fy = intrinsics.get("fy")
#     # if fy is None:
#     #     error_details.append(ErrorDetails.missing_field("fy"))
# 
#     # cx = intrinsics.get("cx")
#     # if cx is None:
#     #     error_details.append(ErrorDetails.missing_field("cx"))
# 
#     # cy = intrinsics.get("cy")
#     # if cy is None:
#     #     error_details.append(ErrorDetails.missing_field("cy"))
# 
#     # width = intrinsics.get("width")
#     # if width is None:
#     #     error_details.append(ErrorDetails.missing_field("width"))
# 
#     # height = intrinsics.get("height")
#     # if height is None:
#     #     error_details.append(ErrorDetails.missing_field("height"))
# 
#     _distortion = intrinsics.get("distortion")
#     distortion = None
#     if _distortion:
#         model = _distortion.get("model")
#         if model is None:
#             error_details.append(
#                 ErrorDetails.missing_field("model", path=["distortion"])
#             )
# 
#         params = _distortion.get("params")
#         if params is None:
#             error_details.append(
#                 ErrorDetails.missing_field("params", path=["distortion"])
#             )
# 
#         if model and params:
#             distortion = CameraDistortion.from_values(model, params)
#             init_values["distortion"] = distortion
# 
#     if len(error_details) > 0:
#         return ParseError(details=error_details)
#     return ParseSuccess(data=CameraIntrinsics(**init_values))

# def parse_lidar_frame(frame: dict) -> ParseResult[LidarSensorFrame]:
#     error_details: List[ErrorDetails] = []
# 
#     timestamp = frame.get("timestamp")
#     if timestamp is None:
#         error_details.append(ErrorDetails.missing_field("timestamp"))
# 
#     points = frame.get("points")
#     if points is None:
#         error_details.append(ErrorDetails.missing_field("points"))
# 
#     return ParseSuccess(
#         LidarSensorFrame(
#             timestamp=timestamp,
#             points=points,
#         )
#     )
# 
# 
# def parse_lidar(sensor: dict) -> ParseResult[LidarSensor]:
#     error_details: List[ErrorDetails] = []
# 
#     # frames
#     _frames = sensor.get("frames")
#     if _frames is None:
#         error_details.append(ErrorDetails.missing_field("frames"))
#     if type(_frames) != list:
#         error_details.append(
#             ErrorDetails.from_msg("frames must be a list", path="frames")
#         )
#     else:
#         for idx, frame in enumerate(_frames):
#             result = parse_lidar_frame(frame)
#             if result.success:
#                 frames = result.data
#             else:
#                 error_details.extend(result.prepend_path(["frames", idx]).details)
# 
#     # coordinates
#     coordinates = sensor.get("coordinates")
#     if coordinates is None:
#         error_details.append(ErrorDetails.missing_field("coordinates"))
#     if coordinates != "ego" and coordinates != "world":
#         error_details.append(
#             ErrorDetails.from_msg(
#                 f"Coordinates must be either 'ego' or 'world'. Provided '{coordinates}'",
#                 path="coordinates",
#             )
#         )
# 
#     # parent id
#     result = parse_parent_id(sensor)
#     if result.success:
#         parent_id = result.data
#     else:
#         error_details.extend(result.details)
# 
#     # sensor id
#     result = parse_sensor_id(sensor)
#     if result.success:
#         sensor_id = result.data
#     else:
#         error_details.extend(result.details)
# 
#     # pose path
#     result = parse_pose_path(sensor)
#     if result.success:
#         pose_path = result.data
#     else:
#         error_details.extend(result.details)
# 
#     if len(error_details) > 0:
#         return ParseError(details=error_details)
# 
#     return ParseSuccess(
#         LidarSensor(
#             id=sensor_id,
#             poses=pose_path,
#             frames=frames,
#             parent_id=parent_id,
#             coordinates=coordinates,
#         )
#     )
# 
# 