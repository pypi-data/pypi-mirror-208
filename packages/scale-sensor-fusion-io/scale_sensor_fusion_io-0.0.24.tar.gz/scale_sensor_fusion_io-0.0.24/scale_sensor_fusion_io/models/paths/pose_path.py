from __future__ import annotations

from functools import reduce
from typing import Iterator, Union, Optional

import numpy as np
import numpy.typing as npt
import pandas as pd
from numpy.typing import ArrayLike
from scipy.interpolate import interp1d
from scipy.spatial.transform import Rotation

IDENTITY = (0, 0, 0, 0, 0, 0, 1)


def transform_points(points: npt.NDArray, transform: npt.NDArray):
    """Applies a transformation to points.

    Args:
        points (npt.NDArray): An array of 3D points with shape (N, 3), where N is the number of points.
        transform (npt.NDArray): A 3x4 transformation matrix.

    Returns:
        npt.NDArray: An array of transformed 3D points with shape (N, 3).
    """
    return points @ transform[:3, :3].T + transform[:3, 3]


class PosePath(pd.DataFrame):
    """PosePath class representing a list of poses at given timestamps, extending pandas DataFrame."""

    XYZ = ["x", "y", "z"]
    QUAT = ["qx", "qy", "qz", "qw"]
    COLUMNS = XYZ + QUAT

    def __init__(
        self, data: Union[ArrayLike, pd.DataFrame], index: Optional[ArrayLike] = None
    ):
        """Initializes the PosePath object.

        Args:
            data (Union[ArrayLike, pd.DataFrame]): An array or DataFrame of poses with shape (N, 7), where N is the number of poses.
            index (ArrayLike, optional): An array-like object representing the index for the PosePath DataFrame. Defaults to None.
        """
        super().__init__(data=data, index=index, columns=PosePath.COLUMNS, dtype=float)

    def copy(self) -> PosePath:
        """Creates a copy of the current PosePath object.

        Returns:
            PosePath: A new PosePath object with copied data and index.
        """
        return PosePath(self.values.copy(), index=self.index)

    @classmethod
    def from_rt(
        cls,
        rotation: Rotation,
        translation: ArrayLike,
        index: Optional[ArrayLike] = None,
    ) -> PosePath:
        """Creates a PosePath object from rotations and translations.

        Args:
            rotation (Rotation): A Rotation object representing the rotations.
            translation (ArrayLike): An array-like object of translations with shape (N, 3), where N is the number of translations.
            index (ArrayLike, optional): An array-like object representing the index for the PosePath DataFrame. Defaults to None.

        Returns:
            PosePath: A PosePath object with the given rotation and translation.
        """
        positions = np.asarray(translation).reshape((-1, 3))
        headings = rotation.as_quat().reshape((-1, 4))
        assert len(headings) == len(positions)
        return PosePath(np.hstack([positions, headings]), index=index)

    @classmethod
    def from_csv(cls, file: str) -> PosePath:
        """Creates a PosePath object from a CSV file.

        Args:
            file (str): The path to the CSV file.

        Returns:
            PosePath: A PosePath object with data read from the CSV file.
        """
        return PosePath(pd.read_csv(file, index_col=0))

    @classmethod
    def identity(cls, n: int = 1, index: Optional[ArrayLike] = None) -> PosePath:
        """Create a PosePath object with identity poses.

        Args:
            n (int, optional): The number of identity poses. Defaults to 1.
            index (ArrayLike, optional): An array-like object representing the index for the PosePath DataFrame. Defaults to None.

        Returns:
            PosePath: A PosePath object with identity poses.
        """
        return PosePath(np.tile(IDENTITY, n).reshape((n, 7)), index=index)

    @classmethod
    def from_matrix(
        cls, matrix: ArrayLike, index: Optional[ArrayLike] = None
    ) -> PosePath:
        """Creates a PosePath object from transformation matrices.

        Args:
            matrix (ArrayLike): A 3D array-like object of transformation matrices with shape (N, 4, 4), where N is the number of matrices.
            index (ArrayLike, optional): An array-like object representing the index for the PosePath DataFrame. Defaults to None.

        Returns:
            PosePath: A PosePath object with poses represented by the given transformation matrices.
        """
        matrix = np.asarray(matrix).reshape((-1, 4, 4))
        return PosePath.from_rt(
            Rotation.from_matrix(matrix[:, :3, :3]), matrix[:, :3, 3], index=index
        )

    def as_matrix(self) -> npt.NDArray:
        """Convert the PosePath object to transformation matrices.

        Returns:
            npt.NDArray: A 3D array of transformation matrices with shape (N, 4, 4), where N is the number of poses.
        """
        matrix = np.tile(np.eye(4), (len(self), 1, 1))
        matrix[:, :3, :3] = Rotation.from_quat(self.headings).as_matrix()
        matrix[:, :3, 3] = self.positions
        return matrix

    @classmethod
    def from_euler(
        self, seq: str, angles: ArrayLike, degrees: bool = False
    ) -> PosePath:
        """Creates a PosePath object from Euler angles.

        Args:
            seq (str): The Euler sequence of axes, such as 'xyz', 'zyx', etc.
            angles (ArrayLike): An array-like object of Euler angles with shape (N, len(seq)), where N is the number of poses.
            degrees (bool, optional): If True, angles are in degrees. Defaults to False.

        Returns:
            PosePath: A PosePath object with poses represented by the given Euler angles.
        """
        angles = np.asarray(angles).reshape((-1, len(seq)))
        path = PosePath.identity(n=len(angles))
        path.headings = Rotation.from_euler(seq, angles, degrees).as_quat()
        return path

    def as_euler(self, seq: str, degrees: bool = False) -> npt.NDArray:
        """Converts the PosePath object to Euler angles.

        Args:
            seq (str): The Euler sequence of axes, such as 'xyz', 'zyx', etc.
            degrees (bool, optional): If True, angles are in degrees. Defaults to False.

        Returns:
            np.ndarray: An array of Euler angles with shape (N, len(seq)), where N is the number of poses.
        """
        return Rotation.from_quat(self.headings).as_euler(seq, degrees=degrees)

    @classmethod
    def from_positions(cls, positions: ArrayLike) -> PosePath:
        """Creates a PosePath object with given positions.

        Args:
            positions (ArrayLike): An array-like object of positions with shape (N, 3), where N is the number of positions.

        Returns:
            PosePath: A PosePath object with poses represented by the given positions and identity orientations.
        """
        positions = np.asarray(positions).reshape((-1, 3))
        path = PosePath.identity(len(positions))
        path.positions = positions
        return path

    @property
    def positions(self) -> npt.NDArray:
        """Gets the positions of the poses.

        Returns:
            npt.NDArray: An array of positions with shape (N, 3), where N is the number of poses.
        """
        return self.values[:, 0:3]

    @positions.setter
    def positions(self, values: ArrayLike) -> None:
        """Set the positions of the poses.

        Args:
            values (ArrayLike): Anarray-like object of positions with shape (N, 3), where N is the number of positions.
        """
        self.values[:, 0:3] = np.asarray(values).reshape((-1, 3))

    @property
    def headings(self) -> npt.NDArray:
        """Gets the orientations (headings) of the poses in quaternions.

        Returns:
            npt.NDArray: An array of quaternions with shape (N, 4), where N is the number of poses.
        """
        return self.values[:, 3:7]

    @headings.setter
    def headings(self, values: ArrayLike) -> None:
        """Sets the orientations (headings) of the poses in quaternions.

        Args:
            values (ArrayLike): An array-like object of quaternions with shape (N, 4), where N is the number of orientations.
        """
        self.values[:, 3:7] = np.asarray(values).reshape((-1, 4))

    # Operations
    def interpolate(self, index: ArrayLike, fill_value="nearest") -> PosePath:
        """Interpolate the PosePath object at the given index.

        Args:
            index (ArrayLike): An array-like object representing the index for the interpolated poses.
            fill_value (optional): The fill value for out-of-bounds data. Defaults to np.nan.

        Returns:
            PosePath: A PosePath object with poses interpolated at the given index.
        """
        if np.array_equal(self.index, index):
            return self.copy()

        if len(self.index) == 1:
            return PosePath(self.take([0] * len(index)).values, index=index)

        x = self.index
        y = np.hstack([self.positions, self.as_euler("zyx")])

        if fill_value == "nearest":
            fill_value = (y[0], y[-1])

        if fill_value == "identity":
            fill_value = np.zeros(6)

        interpolator = interp1d(
            x=x, y=y, bounds_error=False, fill_value=fill_value, axis=0
        )
        values = interpolator(index)

        result = PosePath.from_rt(
            Rotation.from_euler("zyx", values[:, 3:]), values[:, :3], index=index
        )

        return result

    def invert(self) -> PosePath:
        """Creates a new PosePath instance with inverted poses.

        Returns:
            PosePath: A PosePath object with inverted poses.
        """
        inv_rotations = Rotation.from_quat(self.headings).inv()
        inv_positions = -inv_rotations.apply(self.positions)
        return PosePath.from_rt(inv_rotations, inv_positions, index=self.index)

    def __matmul__(self, other: Union[PosePath, ArrayLike]) -> PosePath:
        """Matrix multiplication of the PosePath object with another PosePath object or a transformation matrix.

        Args:
            other (Union['PosePath', ArrayLike]): Another PosePath object or a transformation matrix/array.

        Returns:
            PosePath: A PosePath object with poses resulting from the matrix multiplication.
        """
        if isinstance(other, PosePath):
            resampled = other.interpolate(self.index)
            return PosePath.from_matrix(
                self.as_matrix() @ resampled.as_matrix(), index=self.index
            )

        if isinstance(other, np.ndarray):
            return PosePath.from_matrix(self.as_matrix() @ other, index=self.index)

    def __rmatmul__(self, other: Union[PosePath, ArrayLike]) -> PosePath:
        """Right matrix multiplication of the PosePath object with another PosePath object or a transformation matrix.

        Args:
            other (Union['PosePath', ArrayLike]): Another PosePath object or a transformation matrix/array.

        Returns:
            PosePath: A PosePath object with poses resulting from the matrix multiplication.
        """
        if isinstance(other, PosePath):
            resampled = other.interpolate(self.index)
            return PosePath.from_matrix(
                resampled.as_matrix() @ self.as_matrix(), index=self.index
            )

        if isinstance(other, np.ndarray):
            return PosePath.from_matrix(other @ self.as_matrix(), index=self.index)

    @classmethod
    def multiply(cls, paths: Iterator[PosePath]) -> PosePath:
        """Composes multiple PosePath objects.

        Args:
            paths (Iterator['PosePath']): An iterator of PosePath objects.

        Returns:
            PosePath: A PosePath object with poses resulting from the matrix multiplication of the given PosePath objects.
        """
        return reduce(cls.__rmatmul__, paths)

    def transform_points(self, points: ArrayLike) -> npt.NDArray:
        """Transform points using the poses in the PosePath object.

        This method takes an array-like object of points and transforms them using the poses in the PosePath object.
        The input points must have a shape of (N, 3), where N is the number of points. The output is an array of
        transformed points with the same shape as the input points.

        The following scenarios are considered:
        - If the PosePath object has only one pose, this method applies the transformation to all points.
        - If the input points have only one point, this method applies all poses to transform that single point.
        - If the number of input points is equal to the number of poses in the PosePath object, this method applies
        each pose to transform the corresponding point (i.e., pose i transforms point i).

        Args:
            points (ArrayLike): An array-like object of points with shape (N, 3), where N is the number of points.

        Returns:
            npt.NDArray: An array of transformed points with shape (N, 3), where N is the number of points.

        Raises:
            ValueError: If the number of input points and poses do not satisfy the mentioned conditions.
        """
        points = np.asarray(points).reshape((-1, 3))
        if len(self) == 1:
            transform = self[:1].as_matrix()[0]
            return transform_points(points, transform)

        if len(points) == 1:
            return np.array([transform_points(points[0], t) for t in self.as_matrix()])

        if len(points) == len(self):
            return np.array(
                [transform_points(points[i], t) for i, t in enumerate(self.as_matrix())]
            )

        raise ValueError(
            "Expected equal numbers of poses and points, or a single pose, or a single point."
        )

    def apply_interpolated_transform_to_points(
        self, points: ArrayLike, timestamps: ArrayLike, resolution: float = 1e6
    ) -> npt.NDArray:
        """
        Applies interpolated transformations from the PosePath to the given points based on their corresponding timestamps and the specified resolution.

        This method groups points that have timestamps closer than the provided resolution value and applies the same transformation
        to each point within the group, improving performance by reducing the number of separate interpolations and transformations required.

        Parameters
        ----------
        points : ArrayLike
            An array-like object containing the 3D points to be transformed, with shape (N, 3), where N is the number of points.
        timestamps : ArrayLike
            An array-like object containing the timestamps corresponding to each point in the points array, with shape (N,).
        resolution : float, optional, default: 1e6
            The time resolution for grouping points. Points with timestamps closer than this value will receive the same transform.

        Returns
        -------
        npt.NDArray
            A numpy array containing the transformed points, with shape (N, 3).
        """
        points = np.asarray(points).reshape((-1, 3))

        # Create intervals and groups
        timestamps = pd.Series(timestamps)
        intervals = (timestamps / resolution).astype(int)
        groups = timestamps.groupby(intervals)

        # Get groups timestamps and interpolate poses
        interval_timestamps = groups.mean()

        # Resample poses to generate the transforms
        transforms = self.interpolate(interval_timestamps).as_matrix()

        transformed_points = np.vstack(
            [
                transform_points(points[group.index], transforms[index])
                for index, [_, group] in enumerate(groups)
            ]
        )

        return transformed_points

    def make_relative(self) -> PosePath:
        """Creates a new PosePath object with poses relative to the first pose.

        Returns:
            PosePath: A new PosePath object with poses relative to the first pose in the original PosePath object.
        """
        inv_first = self[:1].invert().as_matrix()[0]
        return inv_first @ self

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if isinstance(result, pd.Series):
            return result
        elif isinstance(result, pd.DataFrame) and np.array_equal(
            result.columns, PosePath.COLUMNS
        ):
            return PosePath(result)
        return result
