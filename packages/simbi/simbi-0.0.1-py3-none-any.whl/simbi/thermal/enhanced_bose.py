# -*- coding: utf-8 -*-
"""
Calculates density, integrated densities, atom numbers and trap sizes 
for thermal atoms in or released from a harmonic trap.
"""

import numpy as np
from scipy.optimize import minimize, Bounds
from scipy.constants import hbar, k, pi
from simbi.thermal.custom_polylog import polylog
from typing import Iterable, Union, Tuple, List




def get_thermal_wavelength(m: float, T: float) -> float:
    """The de Broglie wavelength."""
    return ((2 * np.pi * hbar ** 2) / (m * k * T)) ** .5

def get_fugacity(mu: float, T: float) -> float:
    """Definition of fugacity can be found in 1st chapter of Pethick & Smith
    """
    return np.exp(mu / (k * T))

def get_axis_sigma(wi: float, m: float, T: float, t: float) -> float:
    """Each trapping axis has an an associated sigma length (which goes in 
    the Gaussian part of the function) and we calculate that here (see 
    accompanying derivation document for more details)

    Args:
        wi: Trap frequency along the axis.
        m: Mass of the particle.
        T: Temperature of the cloud.
        t: Time after release from the trap.

    Returns:
        sigma: Sigma length along the axis.
    """
    sigma = ((k * T * (1 + (wi * t) ** 2)) / (m * wi ** 2)) ** .5
    return sigma

def expansion_time_prefactor(t: float, 
                             trap_freqs: tuple[float, float, float]
                             ) -> float:
    """Cloud expansion after release from the trap results in the peak 
    density being attenuated. This function calculates that attenuation 
    pre-factor

    Args:  
        t: Time after release from the trap.
        trap_freqs: The three trap frequencies.

    Returns:
        prefactor: Attenuation pre-factor.
    """
    wx, wy, wz = trap_freqs
    prefactor = ((1 + (wx * t) ** 2) * 
                 (1 + (wy * t) ** 2) * 
                 (1 + (wz * t) ** 2)) ** (-.5)
    return prefactor

def get_integrated_prefactor(m: float, T: float, mu: float, t: float,
                             trap_freqs: list = []) -> float:
    """When the density is integrated along one or more axes it adds an
    integrated prefactor to the resulting density equation. The trap_freqs
    list contains the trap frequencies only for the axes we are integrating 
    along. If the full 3D density is being calculated the prefactor is one

    Args:
        m: Mass of the particle.
        T: Temperature of the cloud.
        mu: Chemical potential of the cloud.
        t: Time after release from the trap.
        trap_freqs: List of trap frequencies along the axes which are being
            integrated over.

    Returns:
        prefactor: Integrated prefactor.
    """
    prefactor = 1
    if len(trap_freqs) > 0:
        sigmas = [get_axis_sigma(wi, m, T, t) for wi in trap_freqs]
        prefactor_list = [(2 * np.pi) ** .5 * sigma_i for sigma_i in
                            sigmas]
        prefactor = np.product(prefactor_list)
    return prefactor

def get_prefactor(efreqs: List[float], ifreqs: List[float], m: float,
                  T: float, mu: float, t: float) -> float:
    """
    Calculates all the prefactor needed for the density in one, two, or three dimensions.

    Parameters:
        efreqs: Trap frequencies along the axes which are not 
            integrated over when calculating the density.
        ifreqs: Trap frequencies along the axes which are 
            being integrated.
        m: Mass of the particles.
        T: Temperature.
        mu: Chemical potential.
        t: Time.
        
    Returns:
        prefactor: The total calculated prefactor.
    """
    all_freqs = list(efreqs) + list(ifreqs)
    dbw = get_thermal_wavelength(m, T)
    expansion_prefactor = expansion_time_prefactor(t, all_freqs)
    integrated_prefactor = get_integrated_prefactor(m, T, mu, t,
                                                            ifreqs)
    prefactor = (1 / dbw ** 3) * expansion_prefactor * integrated_prefactor
    return prefactor

def get_gaussian(coords: Iterable[np.ndarray], 
                 trap_freqs: list[float], 
                 m: float,
                 T: float, 
                 t: float) -> np.ndarray:
    """
    Calculates the 1D, 2D, or 3D Gaussian function which goes in the 
        polylog function.

    Parameters:
        coords: List of coordinate arrays, e.g., [X, Y, Z].
        trap_freqs: Trap frequencies which match the coordinate arrays in 
            `coords` (i.e., along the same axis).
        m: Mass of the particles.
        T: Temperature.
        t: Time.

    Returns:
        np.ndarray: Value of the N-dimensional Gaussian function at the 
            coordinate positions given.
    """
    sigmas = [get_axis_sigma(wi, m, T, t) for wi in trap_freqs]
    exponents = np.zeros(coords[0].shape)
    for Xi, sigma_i in zip(coords, sigmas):
        exponents -= .5 * (Xi / sigma_i) ** 2
    return np.exp(exponents)

def thermal_density(coords: Iterable[np.ndarray], 
                trap_freqs: list[float],
                m: float,
                T: float,
                mu: float,
                t: float) -> np.ndarray:
    """
    Calculates atomic density for a thermal cloud in a harmonic trap or 
    released from a harmonic trap. The density integrated along one or two
    axes can also be calculated.

    Parameters:
        coords: List of coordinate arrays, i.e., [X, Y, Z].
        efreqs: Trap frequencies along the axes which are not integrated over when
            calculating the density.
        ifreqs: Trap frequencies along the axes which are being integrated.

    Returns:
        density: Atomic density or integrated atomic density.
    """
    num_dims = len(coords)
    efreqs = trap_freqs[:num_dims]
    ifreqs = trap_freqs[num_dims:]
    prefactor = get_prefactor(efreqs, ifreqs, m, T, mu, t)
    fugacity = get_fugacity(mu, T)
    gaussian = get_gaussian(coords, efreqs, m, T, t)
    gamma = (3 + len(ifreqs)) / 2
    g_gam = polylog(fugacity * gaussian, gamma)
    density = prefactor * g_gam
    return density


def thermal_atom_number(trap_freqs:list[float], mu: float, T: float) -> float:
    """The total atom number, analytically calculated.

    Args:
        trap_freqs: The trapping frequencies in each direction
        mu: The chemical potential of the system
        T: The temperature of the system

    Returns:
        excited_atom_number: The total number of excited atoms in the system
    """
    pre_factor = ((k * T) / hbar) ** 3
    wx, wy, wz = trap_freqs
    trap_mean = wx * wy * wz
    fugacity = get_fugacity(mu, T)

    if isinstance(fugacity, np.ndarray):
        g3 = polylog(fugacity, 3)
    else:
        g3 = polylog(np.array([fugacity]), 3)[0]

    return pre_factor * (1 / trap_mean) * g3

def get_sigmas(trap_freqs: list[float], 
                m: float, 
                T: float, 
                mu: float, 
                t: float
                ) -> Tuple[list[float], list[float]]:
    """Calculates in-trap sigmas and sigmas after expansion

    Args:
        trap_freqs: The trapping frequencies in each direction
        m: The mass of each particle
        T: The temperature of the system
        mu: The chemical potential of the system
        t (float, optional): The time in the simulation. Defaults to 0.

    Returns:
        init_sigmas: The sigmas of the cloud in the trap
        t_sigmas: The sigmas of the cloud after expansion
    """
    init_sigmas = [get_axis_sigma(wi, m, T, 0) for wi in trap_freqs]
    t_sigmas = [get_axis_sigma(wi, m, T, t) for wi in trap_freqs]
    return init_sigmas, t_sigmas

def get_temperature(trap_freqs: list[float], 
                    mu: float, 
                    nex: float, 
                    tol: float = 1e-10):
    """Calculates the temperature of the system given a total excited atom
    number and the chemical potential.

    Args:
        trap_freqs: The trapping frequencies in each direction
        mu: The chemical potential of the system
        nex: The total number of excited atoms in the system
        tol (float, optional): The tolerance of the minimization. 
            Defaults to 1e-10.

    Returns:
        T: The temperature of the system
    """
    f = lambda T: ((thermal_atom_number(trap_freqs, mu, T *1e-4) - nex)) ** 2
    # bounds = Bounds(10E-9, np.inf)
    bounds = Bounds(10e-5, np.inf)
    res = minimize(f, x0=1e-2, bounds=bounds, tol=tol)
    return res['x'][0] * 1e-4, res

def get_mu(trap_freqs: list[float], 
           T: float, 
           nex: float, 
           tol: float=1e-10
           ) -> Tuple[float, object]:
    """Calculates the chemical potential of the system given a total 
        excited atom number and the temperature.

    Args:
        trap_freqs: The trapping frequencies in each direction
        T: The temperature of the system
        nex: The total number of excited atoms in the system
        tol (float, optional): The tolerance of the minimization. 
            Defaults to 1e-10.

    Returns:
        mu: The chemical potential of the system
        res, object: The result of the minimization
    """
    f = lambda mu: (thermal_atom_number(trap_freqs, mu,T) - nex)**2
    bounds = Bounds(-np.inf, 0)
    res = minimize(f, x0=1E-28, bounds=bounds, tol=tol)
    return res['x'], res