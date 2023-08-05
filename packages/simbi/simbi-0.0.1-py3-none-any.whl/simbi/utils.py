import numpy as np
from typing import Iterable

def rotate_coordinates2D(coordinates: list[np.ndarray],
                         theta: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Rotates coordinates by theta radians.

    Args:
        coordinates: Tuple of X and Y coordinates.
        theta: Angle in radians.

    Returns:
        Tuple of rotated X and Y coordinates.
    """
    X, Y = coordinates
    shape = X.shape
    coords = np.stack([np.ravel(X), np.ravel(Y)])
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])
    Xr, Yr = R.dot(coords)
    return np.reshape(Xr, shape), np.reshape(Yr, shape)

def translate_coordinates2D(XY_tuple: list[float, float], 
                            x0: float, 
                            y0: float
                            ) -> tuple[float, float]:
    """
    Translates coordinates by x0 and y0.

    Args:
        XY_tuple: Tuple of X and Y coordinates.
        x0: x0 coordinate.
        y0: y0 coordinate.

    Returns:
        Tuple of translated X and Y coordinates.
    """
    X, Y = XY_tuple
    X = X - x0
    Y = Y - y0
    return (X, Y)

def coordinate_transformation2D(XY_tuple: list[float, float], 
                                x0: float=0, y0: float=0, theta: float=0
                                ) -> tuple[float, float]:
    """
    Transforms coordinates by x0, y0, and theta.

    Args:
        XY_tuple: Tuple of X and Y coordinates.
        x0: x0 coordinate.
        y0: y0 coordinate.
        theta: Angle in radians.

    Returns:
        Tuple of transformed X and Y coordinates.
    """
    XY_tuple = translate_coordinates2D(XY_tuple, x0, y0)
    XY_tuple = rotate_coordinates2D(XY_tuple, theta)
    return XY_tuple