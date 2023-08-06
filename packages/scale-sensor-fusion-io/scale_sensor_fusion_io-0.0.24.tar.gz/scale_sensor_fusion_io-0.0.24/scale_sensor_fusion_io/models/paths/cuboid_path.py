import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation
from scipy.interpolate import interp1d

from typing import Union
from numpy.typing import ArrayLike


class CuboidPath(pd.DataFrame):
    """CuboidPath class representing a list of cuboids at given timestamps, extending pandas DataFrame."""

    POSITION = ["x", "y", "z"]
    ROTATION = ["yaw", "pitch", "roll"]
    DIMENSIONS = ["dx", "dy", "dz"]
    COLUMNS = POSITION + ROTATION + DIMENSIONS

    def __init__(self, data: Union[ArrayLike, pd.DataFrame], index: ArrayLike = None):
        """Initializes the CuboidPath object.

        Args:
            data (Union[ArrayLike, pd.DataFrame]): An array or DataFrame of cuboids with shape (N, 9), where N is the number of cuboids.
            index (ArrayLike, optional): An array-like object representing the index for the CuboidPath DataFrame. Defaults to None.
        """
        super().__init__(
            data=data, index=index, columns=CuboidPath.COLUMNS, dtype=float
        )

    def copy(self):
        """Creates a copy of the current CuboidPath object.

        Returns:
            CuboidPath: A new CuboidPath object with copied data and index.
        """
        return CuboidPath(self.values.copy(), index=self.index)

    @property
    def positions(self):
        return self[CuboidPath.POSITION].values

    @property
    def rotations(self):
        return self[CuboidPath.ROTATION].values

    @property
    def dimensions(self):
        return self[CuboidPath.DIMENSIONS].values

    @classmethod
    def from_csv(cls, file: str):
        """Creates a CuboidPath object from a CSV file.

        Args:
            file (str): The path to the CSV file.

        Returns:
            CuboidPath: A CuboidPath object with data read from the CSV file.
        """
        return CuboidPath(pd.read_csv(file, index_col=0))

    @classmethod
    def identity(cls, n: int = 1, index: ArrayLike = None):
        """Create a CuboidPath object with identity cuboids.

        Args:
            n (int, optional): The number of identity cuboids. Defaults to 1.
            index (ArrayLike, optional): An array-like object representing the index for the CuboidPath DataFrame. Defaults to None.

        Returns:
            CuboidPath: A CuboidPath object with identity cuboids.
        """
        identity_cuboid = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1])
        return CuboidPath(np.tile(identity_cuboid, n).reshape((n, 9)), index=index)

    @classmethod
    def from_matrix(cls, matrix: ArrayLike, index: ArrayLike = None):
        """Creates a CuboidPath object from transformation matrices.

        Args:
            matrix (ArrayLike): A 3D array-like object of transformation matrices with shape (N, 4, 4), where N is the number of matrices.
            index (ArrayLike, optional): An array-like object representing the index for the CuboidPath DataFrame. Defaults to None.

        Returns:
            CuboidPath: A CuboidPath object with cuboids represented by the given transformation matrices.
        """
        matrix = np.asarray(matrix).reshape((-1, 4, 4))
        positions = matrix[:, :3, 3]
        rotations = Rotation.from_matrix(matrix[:, :3, :3]).as_euler(
            "zyx", degrees=True
        )
        scales = np.linalg.norm(matrix[:, :3, :3], axis=0)

        cuboids = np.hstack([positions, rotations, scales])
        return CuboidPath(cuboids, index=index)

    def as_matrix(self):
        """Convert the CuboidPath object to transformation matrices.

        Returns:
            np.ndarray: A 3D array of transformation matrices with shape (N, 4, 4), where N is the number of cuboids.
        """
        positions = self.loc[:, CuboidPath.POSITION].values
        rotations = self.loc[:, CuboidPath.ROTATION].values
        dimensions = self.loc[:, CuboidPath.DIMENSIONS].values

        matrix = np.tile(np.eye(4), (len(self), 1, 1))

        rotation_matrices = Rotation.from_euler(
            "zyx", rotations, degrees=True
        ).as_matrix()
        scale_matrices = np.array([np.diag(s) for s in dimensions])

        # Combine scale and rotation
        transform_matrices = np.matmul(rotation_matrices, scale_matrices)

        matrix[:, :3, :3] = transform_matrices
        matrix[:, :3, 3] = positions

        return matrix

    # Operations
    def interpolate(self, index: ArrayLike, fill_value="nearest"):
        """Interpolate the CuboidPath object at the given index.

        Args:
            index (ArrayLike): An array-like object representing the index for the interpolated cuboids.
            fill_value (optional): The fill value for out-of-bounds data. Defaults to np.nan.

        Returns:
            CuboidPath: A CuboidPath object with poses interpolated at the given index.
        """
        if np.array_equal(self.index, index):
            return self.copy()

        if len(self.index) == 1:
            return CuboidPath(self.take([0] * len(index)).values, index=index)

        x = self.index
        y = self.values

        if fill_value == "nearest":
            fill_value = (y[0], y[-1])

        interpolator = interp1d(
            x=x, y=y, bounds_error=False, fill_value=fill_value, axis=0
        )
        values = interpolator(index)
        result = CuboidPath(values, index=index)

        return result
