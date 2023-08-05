# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 15:27:11 2022

@author: hofer
"""

import numpy as np

def get_1Dcoordinates(max_coords: list, 
                      scalar: int=1, clength: int=200
                      ) -> tuple[list[np.ndarray], int]:  
    """
    Calculates 1D coordinates for each dimension.

    Args:
        max_coords: List of maximum coordinates for each dimension.
        scalar: Scalar for maximum coordinates.
        clength: Coordinate length.

    Returns:
        coords_1d: List of 1D coordinates for each dimension.
        clength: Coordinate length.
    """
    new_max_coords = [maxv * scalar for maxv in max_coords]
    coords_1d = [np.linspace(-maxv, maxv, clength) for maxv in new_max_coords]
    return coords_1d, clength

        
def get_differential_elements(coord_list: list[np.ndarray]) -> list[float]:
    """
    Calculates differential elements for numeric integration

    Args:
        coord_list: List of coordinates for each dimension.

    Returns:
        dx_nd: List of differential elements for each dimension.
    """
    dim = len(coord_list)
    dx_1d = [coords[1] - coords[0] for coords in coord_list]
    dx_nd = [np.prod(dx_1d[:dim-i]) for i in range(len(dx_1d))]
    return dx_nd


def get_coordinates(max_coords: list[float],
                    scalar: int=1, clength: int=200, multi: bool=False
                    ) -> tuple[list[np.ndarray], list[np.ndarray], 
                                list[float], int]:
    """
    Gets coordinates for each dimension.

    Args:
        max_coords: List of maximum coordinates for each dimension.
        scalar: Scalar for maximum coordinates.
        clength: Coordinate length.

    Returns:
        coords_1d: List of 1D coordinates for each dimension.
        coord_maps: List of coordinate maps for each dimension.
        differential_elements: List of differential elements for each dimension.
        clength: Coordinate length.
    """
    dim = len(max_coords)
    coords_1d, _ = get_1Dcoordinates(max_coords, scalar, clength)
    differential_elements = get_differential_elements(coords_1d)
    coord_maps = [np.meshgrid(*coords_1d[:dim-i]) for i in range(len(coords_1d))]
    if multi:
        return coords_1d, coord_maps, differential_elements, clength
    else:
        return coords_1d, coord_maps[0], differential_elements[0], clength
        

def integrate_array(iarray, differential_element):
    return np.sum(iarray) * differential_element