import numpy as np
import sys
import pytest
sys.path.append('../')

from simbi import bimodal as bc
from simbi import coordinate_handler as ch

@pytest.fixture
def init_values():
    a0 = 5.29177210903 * 10**(-11)
    m = 1.4192261 * 10**(-25)
    wx = 2 * np.pi * 128
    wy = 4 * wx
    wz = 10 * wx
    mu = 8.60674437635897e-30
    T = 4.67356798e-06
    t = .001
    a = 90 * a0
    trap_freqs = (wx, wy, wz)
    return a0, m, wx, wy, wz, mu, T, t, a, trap_freqs


def test_densities(init_values):
    a0, m, wx, wy, wz, mu, T, t, a, trap_freqs = init_values

    atom_numbers = bc.bimodal_atom_numbers(trap_freqs, m, T, a, mu)
    # total_atom_number, ex_atom_number, bec_atom_number, condensed_fraction = atom_numbers

    all_radii = bc.bimodal_radii(trap_freqs, m, T, a, mu, t)
    init_sigmas, t_sigmas, init_tf_radii, expans_scalars, tf_radii = all_radii

    (x,y,z), coord_maps, diff_elements, clength = ch.get_coordinates(t_sigmas, 
                                                                     6, 
                                                                     multi=True)
    coords_3d, coords_2d, coords_1d = coord_maps
    dv, da, dx = diff_elements

    densities_3d = bc.bimodal_density(coords_3d, trap_freqs, m, T, a, mu, t)
    densities_2d = bc.bimodal_density(coords_2d, trap_freqs, m, T, a, mu, t)
    densities_1d = bc.bimodal_density(coords_1d, trap_freqs, m, T, a, mu, t)
    all_densities = [densities_3d, densities_2d, densities_1d]

    # check densities
    for densities, atom_number, diff_el in zip(all_densities, atom_numbers, 
                                               diff_elements):
        for density in densities:
            assert np.isclose(atom_number, 
                              ch.integrate_array(density, diff_el), rtol=1e2)
