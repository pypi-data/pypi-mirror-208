# -*- coding: utf-8 -*-
"""
These functions are modified from the mpmath library to work with numpy arrays.
"""
import numpy as np
from scipy.special import zeta, gamma, spence

EPS = np.finfo(np.float64).eps


def polylog_series_np(z, s):

    zshape = z.shape
    l = np.zeros(zshape)
    k = 1.0 * np.ones(zshape)
    zk = z.copy()
    count = 0
    while 1:
        term = zk / k**s
        tmask = np.abs(term) < EPS
        if np.all(tmask):
            break
        term = np.where(tmask, 0, term)
        l += term
        zk *= z
        k += 1
        count += 1
    return l


def polylog_general_np(z, s):
    """The SciPy gamma and zeta functions give infinity if the values for 
    s is an integer. We can thus add a small number to s to avoid this while 
    still getting approximately the correct answer when compared to 
    Mathematica.
    """
    s += 1e-6
    v = 0
    u = np.log(z)
    t = 1
    k = 0
    while 1:
        term = zeta(s - k) * t
        tmask = np.abs(term) < EPS
        if np.all(tmask):
            break
        term = np.where(tmask, 0, term)
        v += term
        k += 1
        t *= u
        t /= k
    return gamma(1 - s) * (-u)**(s - 1) + v


def polylog_no(z, s):
    if s == 0:
        return z / (1 - z)
    if s == 1:
        return -np.log(1 - z)
    if s == 2:
        return spence(1 - z)
    if s == -1:
        return z / (1 - z)**2
    
    val = 1.1 * np.ones(z.shape)
    mask = z < 0.24
    val[mask] = polylog_series_np(z[mask], s)
    val[~mask] = polylog_general_np(z[~mask], s)
    return val


def polylog(z, s):
    condlist = [z == 1]
    funclist = [lambda z, s: zeta(s) * np.ones(z.shape), polylog_no]
    return np.piecewise(z, condlist, funclist, s)