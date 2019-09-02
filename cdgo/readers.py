#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd


def format_val(v):
    """Takes in float and formats as str with 1 decimal place

    :v: float
    :returns: str

    """
    return '{:.1f}%'.format(v)


def split_string(s):
    """Docstring for split_string.

    Take space-delimited string and split into list using re.

    :s: space-delimited string
    :returns: list

    """

    return re.split('\s+', s)


def dec_to_percent(n):
    """Docstring for dec_to_percent

    :n: float value or list as fraction
    :returns: value or list multiplied by 10e2
    """

    return n * 100


def header():
    """Set column headers for reading in CDPro algorithm output files
    :returns: python dict of continll/cdsstr headers

    """
    d = {
        'continll': ['WaveL', 'ExpCD', 'CalcCD'],
        'cdsstr': ['WaveL', 'Exptl', 'ReconCD', 'CalcCD']
    }

    return d


def read_protss(f):
    """TODO: Docstring for read_protss_new.

    :f: protss assignment file output by CONTINLL or CDSSTR
    :returns: pandas dataframe

    """

    # define ibasis string names
    refsets = {
        'SP29': 1,
        'SP22X': 2,
        'SP37': 3,
        'SP43': 4,
        'SP37A': 5,
        'SDP42': 6,
        'SDP48': 7,
        'CLSTR': 8,
        'SMP50': 9,
        'SMP56': 10,
    }
    """
    group ibasis datasets according to the style of output secondary
    structures. Certain structures (e.g. helical elements) are summed.
    """
    ibasis_group_1 = {
        'members': ['SP29', 'SP37', 'SP43', 'SDP42', 'SDP48', 'CLSTR', 'SMP50',
                    'SMP56'],
        'ss': ['H(r)', 'H(d)', 'S(r)', 'S(d)', 'Trn', 'Unrd']
    }
    ibasis_group_2 = {
        'members': ['SP22X'],
        'ss': ['H', '3/10', 'S', 'Turn', 'PP2', 'Unrd']
    }
    ibasis_group_3 = {
        'members': ['SP37A'],
        'ss': ['H', 'S', 'Turn', 'PP2', 'Unrd']
    }

    # parse protss input file for specific lines relating to fits and sec struc
    with open(f) as fp:
        for i, line in enumerate(fp):
            if i == 4:
                # ibasis set name
                dname = split_string(line)[4]
                if dname in iter(refsets.keys()):
                    d_int = refsets[dname]
            elif i == 6:
                # rmsd value
                ss = split_string(line)[3:-1]
                ss = [float(num) for num in ss]
            # elif i == 7:
            #     # rmsd value
            #     qfit = split_string(line)[2]
            #     rmsd = (float(qfit))

    """
    """
    if dname in ibasis_group_1['members']:
        ahelix = format_val(dec_to_percent((ss[0] + ss[1])/np.sum(ss)))
        bstrand = format_val(dec_to_percent(ss[2] + ss[3])/np.sum(ss))
        turn = format_val(dec_to_percent(ss[4]/np.sum(ss)))
        unord = format_val(dec_to_percent(ss[5]/np.sum(ss)))
        ss = {
            'ahelix': ahelix,
            'bstrand': bstrand,
            'turn': turn,
            'unord': unord
        }
    elif dname in ibasis_group_2['members']:
        ahelix = format_val(dec_to_percent((ss[0] + ss[1])/np.sum(ss)))
        bstrand = format_val(dec_to_percent(ss[2]/np.sum(ss)))
        turn = format_val(dec_to_percent(ss[3]/np.sum(ss)))
        unord = format_val(dec_to_percent((ss[4] + ss[5])/np.sum(ss)))
        ss = {
            'ahelix': ahelix,
            'bstrand': bstrand,
            'turn': turn,
            'unord': unord
        }
    elif dname in ibasis_group_3['members']:
        ahelix = format_val(dec_to_percent(ss[0]/np.sum(ss)))
        bstrand = format_val(dec_to_percent(ss[1]/np.sum(ss)))
        turn = format_val(dec_to_percent(ss[2]/np.sum(ss)))
        unord = format_val(dec_to_percent((ss[3] + ss[4])/np.sum(ss)))
        ss = {
            'ahelix': ahelix,
            'bstrand': bstrand,
            'turn': turn,
            'unord': unord
        }
    # return dname, d_int, ss, rmsd
    return dname, d_int, ss


def read_continll(f):
    """TODO: Docstring for read_continll.

    :f: TODO
    :returns: pandas dataframe

    """
    df = pd.read_csv(f, sep=r"\s*", engine='python', index_col='WaveL')
    return df


def read_cdsstr(f):
    """TODO: Docstring for read_continll.

    :f: file name
    :returns: pandas dataframe

    """
    df = pd.read_csv(f, sep=r"\s*", engine='python', index_col='WaveL')
    return df
