# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 12:34:17 2022

@author: hofer
"""
import numpy as np

from simbi.thermal import enhanced_bose as tc
from simbi.bec import thomas_fermi as tfd
        
        
def bimodal_density(coords: list[np.ndarray], 
                    trap_freqs: np.ndarray, 
                    m: float, 
                    T: float, 
                    a: float, 
                    mu: float, 
                    t: float = 0
                    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns the total density, thermal density, and BEC density.

    Args:
        coords: The coordinates in m. Should be a list of coordinates, where 
            each element is a numpy array corresponding to a dimension (i.e.
            coords[0] is the x coordinates, coords[1] is the y coordinates. The 
            number of elements in the list determines whether a 1D, 2D, or 3D
            density is calculated.
        trap_freqs: The trap frequencies in Hz.
        m: The mass of the atoms in kg.
        T: The temperature of the thermal cloud in Kelvin.
        a: The s-wave scattering length in m.
        mu: The chemical potential of the BEC in Joules.
        t: The time since the trap was turned off in s.

    Returns:
        total_density: The total density.
        thermal_density: The thermal density.
        bec_density: The BEC density.
    """

    thermal_density = tc.thermal_density(coords, trap_freqs, m, T, -mu, t)
    bec_density = tfd.bec_density(coords, trap_freqs, m, a, mu, t)
    total_density = thermal_density + bec_density
    return total_density, thermal_density, bec_density

def bimodal_atom_numbers(trap_freqs: np.ndarray, 
                         m: float, 
                         T: float, 
                         a: float, 
                         mu: float, 
                         verbose: bool = False
                         ) -> tuple[float, float, float, float]:
    """Returns the total atom number, thermal atom number, BEC atom number, and
    condensed fraction.

    Args:
        trap_freqs: The trap frequencies in Hz.
        m: The mass of the atoms in kg.
        T: The temperature of the thermal cloud in Kelvin.
        a: The s-wave scattering length in m.
        mu: The chemical potential of the BEC in Joules.
        verbose: If True, prints the total atom number, condensed fraction,
            thermal atom number, and BEC atom number.

    Returns:
        total_number: The total atom number.
        thermal_number: The thermal atom number.
        bec_number: The BEC atom number.
        condensed_fraction: The condensed fraction.
    """

    thermal_number = tc.thermal_atom_number(trap_freqs, -mu, T)
    bec_number = tfd.bec_atom_number(trap_freqs, m, a, mu)
    total_number = thermal_number + bec_number
    condensed_fraction = bec_number / total_number
    if verbose:
        print("Total atom number: ", total_number)
        print("Condensed fraction: ", condensed_fraction)
        print("Thermal atom number: ", thermal_number)
        print("BEC atom number: ", bec_number)
    return total_number, thermal_number, bec_number, condensed_fraction


def bimodal_radii(trap_freqs: np.ndarray, m: float, T: float, a: float, mu: float,
                  t: float = 0) -> tuple[list[float], list[float], list[float],
                                     list[float], list[float]]:
    """Returns the radii of the thermal and BEC clouds.

    Args:
        trap_freqs: The trap frequencies in Hz.
        m: The mass of the atoms in kg.
        T: The temperature of the thermal cloud in Kelvin.
        a: The s-wave scattering length in m.
        mu: The chemical potential of the BEC in Joules.
        t: The time since the trap was turned off in seconds.

    Returns:
        init_sigmas: The initial radii of the thermal cloud in m.
        t_sigmas: The radii of the thermal cloud at time t in m.
        init_tf_radii: The initial radii of the BEC in m.
        expans_scalars: The expansion scalars of the BEC.
        t_tf_radii: The radii of the BEC at time t in m.
    """
    init_sigmas, t_sigmas = tc.get_sigmas(trap_freqs, m, T, -mu, t)
    radii_output = tfd.get_radii(trap_freqs, m, a, mu, t)
    init_tf_radii, expans_scalars, t_tf_radii = radii_output
    return init_sigmas, t_sigmas, init_tf_radii, expans_scalars, t_tf_radii


def mu_temperature(trap_freqs: list[float, float, float], m: float, a: float,
                    ntot: float, cf: float) -> tuple[float, float]:
    """Given trap parameters, BEC parameters, and total atom number
    and condensed fraction, return the chemical potential and temperature
    of the thermal cloud.

    Args:
        trap_freqs: The trap frequencies in Hz.
        m: The mass of the atoms in kg.
        a: The s-wave scattering length in m.
        ntot: The total atom number.
        cf: The condensed fraction.

    Returns:
        mu: The chemical potential of the thermal cloud.
        temperature: The temperature of the thermal cloud.
    """
    nbec = cf * ntot
    mu = tfd.chemical_potential(trap_freqs, m, a, nbec)
    nex = ntot - nbec
    temperature, res = tc.get_temperature(trap_freqs, -mu, nex)
    return mu, temperature