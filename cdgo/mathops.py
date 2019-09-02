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


def sum_squares_total(obs):
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
    ss_tot = sum_squares_total(obs)
    return 1 - (ss_res / ss_tot)


def millidegrees_to_epsilon(df, mol_wt, n_residues, p_conc, L=0.1):
    """TODO

    df: single column pandas dataframe
    mol_wt: average molecular weight of protein (Da)
    n_residues: number of residues in the protein
    p_conc: protein concentration (g/L)
    L: Cuvette path length (cm)
    returns: pandas dataframe in units of molar extinction (delta epsilon)
    """
    # peptides bonds equivalent to number of residues - 1
    pep = n_residues - 1
    # epsilon conversion factor
    eps_f = mol_wt / (10 * L * pep * p_conc * 3298)
    #
    return (df * eps_f).map(lambda x: '%1.3f' % x)
