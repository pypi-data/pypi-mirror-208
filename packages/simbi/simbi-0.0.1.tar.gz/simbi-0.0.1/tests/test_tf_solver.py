import numpy as np
import sys
import pytest
sys.path.append('../')
from simbi.bec.tf_ode_solver import solve_expansion_ODE

class CigarThomasFermiExpansion():
    """Although the general coupled ODEs for the expansion of the BEC in
    the Thomas-Fermi regime are not analytically solvable, if the BEC is
    cigar shaped then a set of analytic equations can be found for the 
    expansion coefficients."""
    
    
    def calculate_tau(self, t, w0r):
        return t * w0r
    
    
    def r_cigar(self, t, w0r):
        tau = self.calculate_tau(t, w0r)
        return (1 + tau**2)**.5
    
    
    def z_cigar(self, t, w0r, w0z):
        lambd = w0z / w0r
        tau = self.calculate_tau(t, w0r)
        return 1 + lambd**2 * (tau * np.arctan(tau) - np.log((1 + tau**2)**.5))

@pytest.fixture
def init_trap_parameters():
    w0r = 2 * np.pi * 1000
    w0x = 1 * w0r
    w0y = w0r
    w0z = 2 * np.pi * 10
    return w0x, w0y, w0z, w0r

@pytest.fixture
def init_time_parameters():
    tmax = .01
    tmin = 0
    t = np.linspace(tmin, tmax, 1000)
    return t

def test_expansion_calculations(init_trap_parameters, init_time_parameters):
    w0x, w0y, w0z, w0r = init_trap_parameters
    t = init_time_parameters
    ctfe =  CigarThomasFermiExpansion()
    #Get expansion coefficients from the ODE solver
    bx, by, bz, _ = solve_expansion_ODE(t, w0x, w0y, w0z)

    #make sure calculated coefficients match expected coefficients
    assert np.allclose(bx, ctfe.r_cigar(t, w0r), rtol=1e-1)
    assert np.allclose(by, ctfe.r_cigar(t, w0r), rtol=1e-1)
    assert np.allclose(bz, ctfe.z_cigar(t, w0r, w0z), rtol=1e-1)
