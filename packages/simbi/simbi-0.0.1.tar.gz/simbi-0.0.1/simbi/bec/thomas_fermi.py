# -*- coding: utf-8 -*-
"""
Calculates density, integrated densities, atom numbers and trap sizes 
for atoms in a BEC using the Thomas-Fermi approximation. The atoms are in 
or are released from a harmonic trap.
"""

from simbi.bec.tf_ode_solver import expansion_solver
import numpy as np
from scipy.constants import hbar, k, pi


def get_contact_interaction_factor(a: float, m: float) -> float:
    """"Calculates the s-wave scattering contact interaction factor."""
    return (4 * np.pi * hbar**2 * a) / m


def get_trap_time_attenuation(bx: float, by: float, bz: float) -> float:
    """Expansion attenuates peak density by this scalar."""
    return 1 / (bx * by * bz)


def get_initial_tf_radius(m: float, mu: float, wi: float) -> float:
    """Calculates the in-trap Thomas-Fermi radius along a single trap axis."""
    return ((2 * mu) / (m * wi**2))**.5


def get_tf_radii(scalars: list[float], 
                 init_radii: list[float]
                ) -> list[float]:
    """Multiplies the initial Thomas-Fermi radii by the expansion scalars
    which are calculated using the TF expansion solver function.

    Args:
        scalars: Expansion scalars for the three trap axes.
        init_radii: Initial TF radii for the three trap axes.

    Returns:
        The TF radii after expansion.
    """
    tf_radii = [scalar * init_radius for scalar, init_radius in 
                zip(scalars, init_radii)]
    return tf_radii

    
def get_radii(trap_freqs: list[float], 
                m: float, a: float, 
                mu: float, t: float
                ) -> tuple[list[float], list[float], list[float]]:
    """
    Calculates all the TF radii including TF radii in the trap and after 
    expansion for time t. Expansion scalars are also returned.

    Args:
        trap_freqs: The three trap frequencies
        m: Mass of the atom.
        a: Scattering length.
        mu: The chemical potential.
        t: The expansion time since trap was turned off.

    Returns:
        init_tf_radii: Thomas-Fermi radii when the trap is turned on.
        expansion_scalars: TF radii scalars for t seconds of expansion.
        tf_radii: TF radii after expanding for t seconds.
    """
    expansion_scalars = expansion_solver(t, *trap_freqs)
    init_tf_radii = [get_initial_tf_radius(m, mu, wi) for wi in trap_freqs]
    tf_radii = get_tf_radii(expansion_scalars, init_tf_radii)
    return init_tf_radii, expansion_scalars, tf_radii
        

def bec_density(coord_list: list[np.array], 
                trap_freqs: list[float], 
                m: float, a: float, mu: float, t: float=0) -> np.array:
    """
    Calculates the density of the BEC. The number of coordinate arrays and 
    trap frequencies sets whether the full 3D density is calculated or 
    whether it should be integrated along one or two axes.

    Args:
        coord_list: N long list of N-dimensional numpy arrays
            List of coordinate arrays.
        trap_freqs: List of length N
            List of trap frequencies.
        m: Mass of the atom.
        a: Scattering length.
        mu: The chemical potential.
        t: The expansion time since trap was turned off.

    Returns:
        Density: Numpy array
            Returns the BEC atomic density in N dimensions.
    """
    init_tf_radii, expansion_scalars, tf_radii = get_radii(trap_freqs, 
                                                            m, a, mu, t)
    time_attenuation = get_trap_time_attenuation(*expansion_scalars)
    contact_factor = get_contact_interaction_factor(a, m)
    common_prefactor = (mu / contact_factor) * time_attenuation 
    
    dimension_prefactors = {3: 1, 
                            2: (4 / 3) * tf_radii[2], 
                            1: (np.pi * tf_radii[1] * tf_radii[2]) / 2}
                    
    dimension_exponents = {3: 1, 2: 3 / 2, 1: 2}
    
    num_dim = len(coord_list)
    parabola = get_parabola(coord_list, tf_radii[:num_dim])
    overall_prefactor = common_prefactor * dimension_prefactors[num_dim]
    return overall_prefactor * parabola**dimension_exponents[num_dim]

def get_parabola(coords: list[np.ndarray], 
                    trap_radii: list[float]) -> np.ndarray:
    """
    Calculates the N-dimensional upside-down parabola associated with the 
        Thomas-Fermi distribution with only positive values.

    Args:
        coords: N long list of N-dimensional numpy arrays representing 
            coordinate arrays.
        trap_radii: list of TF trap radii.

    Returns:
        parabola: N-dimensional array matching the shape of the input 
            coordinate arrays representing the parabola.
    """
    parabola = np.ones(coords[0].shape)
    for Xi, Ri in zip(coords, trap_radii):
        parabola -= Xi**2 / Ri**2
    parabola[parabola < 0] = 0
    return parabola
    
    
def bec_atom_number(trap_freqs: list[float], 
                        m: float, 
                        a: float, 
                        mu: float) -> float:
    """Calculates atom number in BEC using Thomas-Fermi approximation.

    Args:
        trap_freqs: list of trap frequencies.
        m: Mass of the atom.
        a: Scattering length.
        mu: The chemical potential.

    Returns:
        atom_number: The number of atoms in the BEC.
    """
    pre_factor: float = ((2 * m * mu) / (15 * a * hbar**2))
    powers: float = ((2 * mu) / m)**(3/2)
    trap_product: float = np.product(trap_freqs)
    atom_number = pre_factor * powers * (1 / trap_product) 
    return atom_number


def chemical_potential(trap_freqs: float, 
                       m: float, 
                       a: float, 
                       Nbec: int) -> float:
    """Calculates BEC chemical potential using Thomas-Fermi approximation.

    Args:
        trap_freqs: list of trap frequencies.
        m: Mass of the atom.
        a: Scattering length.
        Nbec: The number of atoms in the BEC.

    Returns:
        mu: The chemical potential of the BEC.
    """
    trap_product = np.product(trap_freqs)
    prefactor = (15 * hbar**2 * m**.5) / 2**(5 / 2)
    mu = (prefactor * Nbec * trap_product * a)**(2 / 5)
    return mu