#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def residuals(fit, obs):
    """Calculate residuals for fit compared to observed data

    :fit: list of discrete fit data points
    :obs: list of observed data points
    :returns: fit minus observed data points

    """
    return fit-obs


def fit_stats(obs, fit):
    """
    https://stackoverflow.com/questions/19189362/getting-the-r-squared-
    value-using-curve-fit
    """
    resid = fit - obs
    ss_res = np.sum(resid**2)
    ss_tot = np.sum((obs - np.mean(obs))**2)
    r_squared = 1 - (ss_res / ss_tot)
    return r_squared, ss_tot, ss_res, resid


def sum_squares_total(calc, obs):
    """
    https://stackoverflow.com/questions/19189362/getting-the-r-squared-
    value-using-curve-fit
    """
    return np.sum((obs - np.mean(obs))**2)


def sum_squares_residuals(calc, obs):
    """
    https://stackoverflow.com/questions/19189362/getting-the-r-squared-
    value-using-curve-fit
    """
    resids = residuals(calc, obs)
    return np.sum(resids**2)


def rms_error(calc, obs):
    """Calculate root mean squared deviation

    :calc: calculated data from fit
    :obs: experimentally observed data
    :returns: rmsd
    """
    resids = residuals(calc, obs)
    mean_sqrd = np.mean(resids**2)
    return np.sqrt(mean_sqrd)


def r_squared(calc, obs):
    """
    https://stackoverflow.com/questions/19189362/getting-the-r-squared-
    value-using-curve-fit
    """
    ss_res = sum_squares_residuals(calc, obs)
    ss_tot = sum_squares_total(calc, obs)
    return 1 - (ss_res / ss_tot)


def millidegrees_to_epsilon(df, mrc):
    """TODO

    df: single column pandas dataframe
    mrc: mean residue concentration conversion factor
    returns:
    """
    return (df * mrc/3298).map(lambda x: '%1.3f' % x)
