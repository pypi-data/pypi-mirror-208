import numpy as np
import sys
import pytest
sys.path.append('../')
from simbi.bec import thomas_fermi as tfd
from simbi import coordinate_handler as ch

@pytest.fixture
def init_values():
    '''Some sensible experimental parameters'''
    a0 = 5.29177210903 * 10**(-11)
    a = 10**2 * a0
    m = 1.4192261 * 10**(-25)
    wx = 2 * np.pi * 350
    wy = 2 * np.pi * 300
    wz = 2 * np.pi * 30
    nbec = 10000
    t = .001
    return (wx, wy, wz), m, a, nbec, t


def test_density_calculations(init_values):

    #get initial parameters and trap sizes in meters
    trap_freqs, m, a, nbec, t = init_values
    mu = tfd.chemical_potential(trap_freqs, m, a, nbec)

    mu = 1.7695240085629032e-28
    _, _, tf_radii = tfd.get_radii(trap_freqs, m, a, mu, t)

    #setup coordinates for calculating densities in one, two and three dimensions
    _, coord_maps, diff_elements, clength = ch.get_coordinates(tf_radii, 2, multi=True)
    coords_3d, coords_2d, coords_1d = coord_maps
    dv, da, dx = diff_elements

    #get density and integrated densities
    density_3d = tfd.bec_density(coords_3d, trap_freqs, m, a, mu, t)
    density_2d = tfd.bec_density(coords_2d, trap_freqs, m, a, mu, t)
    density_1d = tfd.bec_density(coords_1d, trap_freqs, m, a, mu, t)

    #make sure analytic atom number matches atom number calculated from densities
    analytic_atom_number = tfd.bec_atom_number(trap_freqs, m, a, mu)
    intg_atom_num_3d = ch.integrate_array(density_3d, dv)
    intg_atom_num_2d = ch.integrate_array(density_2d, da)
    intg_atom_num_1d = ch.integrate_array(density_1d, dx)

    assert np.isclose(analytic_atom_number, intg_atom_num_3d, rtol=1e-5)
    assert np.isclose(analytic_atom_number, intg_atom_num_2d, rtol=1e-5)
    assert np.isclose(analytic_atom_number, intg_atom_num_1d, rtol=1e-5)
