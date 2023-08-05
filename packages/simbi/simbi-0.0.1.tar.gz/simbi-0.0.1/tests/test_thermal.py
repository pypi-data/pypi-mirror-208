import numpy as np
import sys
import pytest
sys.path.append('../')
from simbi.thermal import enhanced_bose as tc
from simbi import coordinate_handler as ch

@pytest.fixture
def init_values():
    '''Some sensible experimental parameters'''
    m = 1.4192261 * 10**(-25)
    wx = 2 * np.pi * 1000
    wy = 1.5 * wx
    wz = 1.5 * wx
    T = 30 * 10 ** (-6)
    mu = 10 ** (-28)
    t = .001
    return (wx, wy, wz), m, T, -mu, t


def test_density_calculations(init_values):
    #get initial parameters and trap sizes in meters
    trap_freqs, m, T, mu, t = init_values
    _, t_sigmas = tc.get_sigmas(trap_freqs, m, T, mu, t)

    #setup coordinates for calculating densities in one, two and three dimensions
    _, coord_maps, diff_elements, clength = ch.get_coordinates(t_sigmas, 6, 
                                                               multi=True)
    coords_3d, coords_2d, coords_1d = coord_maps
    dv, da, dx = diff_elements

    #get density and integrated densities
    density_3d = tc.thermal_density(coords_3d, trap_freqs, m, T, mu, t)
    density_2d = tc.thermal_density(coords_2d, trap_freqs, m, T, mu, t)
    density_1d = tc.thermal_density(coords_1d, trap_freqs, m, T, mu, t)

    #make sure analytic atom number matches atom number calculated from densities
    analytic_atom_number = tc.thermal_atom_number(trap_freqs, mu, T)
    intg_atom_num_3d = ch.integrate_array(density_3d, dv)
    intg_atom_num_2d = ch.integrate_array(density_2d, da)
    intg_atom_num_1d = ch.integrate_array(density_1d, dx)
    print(analytic_atom_number)
    print(intg_atom_num_3d)
    print(intg_atom_num_2d)
    print(intg_atom_num_1d)

    # assert not np.isnan(analytic_atom_number)
    # assert not np.any(np.isnan(intg_atom_num_3d))
    # assert not np.any(np.isnan(intg_atom_num_2d))
    # assert not np.any(np.isnan(intg_atom_num_1d))

    assert np.isclose(analytic_atom_number, intg_atom_num_3d, rtol=1e1)
    assert np.isclose(analytic_atom_number, intg_atom_num_2d, rtol=1e1)
    assert np.isclose(analytic_atom_number, intg_atom_num_1d, rtol=1e1)
