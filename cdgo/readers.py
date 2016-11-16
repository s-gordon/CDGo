#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os


def header():
    """Set column headers for reading in CDPro algorithm output files
    :returns: python dict of continll/cdsstr headers

    """
    d = {
        'continll': ['WaveL', 'ExpCD', 'CalcCD'],
        'cdsstr': ['WaveL', 'Exptl', 'ReconCD', 'CalcCD']
    }

    return d


def compare_ibases(prefix):
    """TODO: Docstring for best_ibasis.

    :prefix: string to append to the output folders relating to the algorithm.
             Acceptable values are "continll" or "cdsstr".
    :returns: TODO

    """
    best_rmsd_text = subprocess.check_output('grep -hw RMSD %s-ibasis*/'
                                             'ProtSS.out | sort | head -n1'
                                             % (prefix), shell=True)
    lowest_rmsd = best_rmsd_text[20:24]
    ibasis = subprocess.check_output(
        'grep -l "%s" %s-ibasis*/ProtSS.out|tail -n1'
        % (lowest_rmsd, prefix), shell=True)
    d = os.path.dirname(os.path.realpath(ibasis))
    best_ibasis = d[-1]

    return float(lowest_rmsd), int(best_ibasis), d
