import os
from typing import Any, List

import cv2
import ffmpeg
import numpy as np
import numpy.typing as npt
import skvideo.io


class VideoWriter:
    def __init__(
        self,
        target_file: str,
        quality: int = 26,
        fps: int = 10,
    ):
        self.target_file = target_file
        self.fps = fps
        self.quality = quality
        self.count = 0

    def writeFrame(self, im: Any) -> None:
        self.writer.writeFrame(im)
        self.count += 1

    def __enter__(self) -> "VideoWriter":
        self.writer = skvideo.io.FFmpegWriter(
            self.target_file,
            inputdict={"-r": str(self.fps)},
            outputdict={
                "-vcodec": "libx264",
                "-pix_fmt": "yuv420p",
                "-x264-params": "keyint=2:scenecut=0",
                "-crf": str(self.quality),
            },
        )
        # ttysetattr etc goes here before opening and returning the file object
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        if self.count > 0:
            self.writer.close()


def generate_video(
    image_files: List[str], target_file: str = "tmp.mp4"
) -> npt.NDArray[np.uint8]:
    with VideoWriter(target_file) as writer:
        for image_file in image_files:
            writer.writeFrame(cv2.imread(image_file))
    return np.fromfile(target_file, dtype=np.uint8)


def write_audio_and_video(audio_file: str, video_file: str, output_file: str) -> None:
    if not os.path.isfile(audio_file) or not os.path.isfile(video_file):
        raise ValueError("Audio or video file does not exist")

    input_video = ffmpeg.input(video_file)
    input_audio = ffmpeg.input(audio_file)
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
        output_file, loglevel="error"
    ).overwrite_output().run()
