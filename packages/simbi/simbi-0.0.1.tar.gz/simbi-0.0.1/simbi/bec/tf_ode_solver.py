# -*- coding: utf-8 -*-
"""
The expansion of the BEC in the Thomas-Fermi regime cannot be analytically
solved. However, the hydrodynamic equations dictating it's expansion result
in three coupled second order differential equations which are fairly easily 
solved. This class solves these equations for given trap parameters and
expansion time.
"""
import numpy as np
import scipy.integrate as integrate
from typing import Union, Tuple, Iterable

__all__ = ['expansion_solver']

def expansion_solver(t: Union[np.ndarray, float], 
                     w0x: float, w0y: float, w0z: float
                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Wrapper for SolveExpansionODE function. Basically watches out for 
    non-numpy array inputs for t and for t=0 values.
    
    Args:
        t: Expansion times (s) we're solving the coupled ODEs for.
        w0x: The trap frequency for the first axis.
        w0y: The trap frequency for the second axis.
        w0z: The trap frequency for the third axis.

    Returns:
        Expansion scalars for the first axis.
        Expansion scalars for the second axis.
        Expansion scalars for the third axis.
    """
    #if we're given a int of float instead of np array
    if type(t) != np.ndarray: 
        t = np.array([t])
        single_val = True
    else:
        single_val = False
        
    #if we're at time zero there is no expansion
    if np.all(t == 0): 
        return 1, 1, 1
    else:
        bx, by, bz, sivp = solve_expansion_ODE(t, w0x, w0y, w0z)
        if single_val:
            bx, by, bz = bx[0], by[0], bz[0]
        return bx, by, bz
    
    
def solve_expansion_ODE(t: np.ndarray, 
                        w0x: float, w0y: float, w0z: float
                        ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, 
                                    object]:
    """
    Solves the coupled ODEs for the given times and the given trap frequencies.

    Args:
        t: Expansion times (s) we're solving the coupled ODEs for.
        w0x: The trap frequency for the first axis.
        w0y: The trap frequency for the second axis.
        w0z: The trap frequency for the third axis.

    Returns:
        Expansion scalars for the first axis.
        Expansion scalars for the second axis.
        Expansion scalars for the third axis.
        Full scipy ODE solving object
    """
    t_span = [0, np.amax(t)]

    """initial conditions for the differential equations. Initial expansion
    coefficients are all one and initial expansion velocities are 0 if we
    consider t=0 release from the trap.
    """
    init = [1, 1, 1, 0, 0, 0]
    params = (w0x, w0y, w0z)
    sivp = integrate.solve_ivp(first_order_equation_derivs, t_span, 
                                init, args=(params,), method='LSODA', t_eval=t)
    
    svals = sivp['y'] 
    return svals[0], svals[1], svals[2], sivp
    

def first_order_equation_derivs(t: np.ndarray,
                                ode_vars,
                                params: Iterable[float]
                                ) -> Iterable[float]:
    """
    Converts the three second-order differential equations into 6
    first order differential equations.

    Args:
        t: Time (s) we're solving the coupled ODEs for.
        ode_vars: The variables we're solving the coupled ODEs for.
        params: The trap frequencies for the three axes.
    """
    bx, by, bz, bxdot, bydot, bzdot = ode_vars
    w0x, w0y, w0z = params
    
    bxdot_dt: float = w0x**2 / (bx**2 * by * bz)
    bydot_dt: float = w0y**2 / (by**2 * bx * bz)
    bzdot_dt: float = w0z**2 / (bz**2 * bx * by)
    
    return [bxdot, bydot, bzdot, bxdot_dt, bydot_dt, bzdot_dt]
    