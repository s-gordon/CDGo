#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pandas as pd
from glob import glob


def split_string(s):
    """Docstring for split_string.

    Take space-delimited string and split into list using re.

    :s: space-delimited string
    :returns: list

    """

    return re.split('\s+', s)


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

    :prefix: string to prepend to the output folders relating to the algorithm.
             Acceptable values are "continll" or "cdsstr".
    :returns: TODO

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

    flist = glob('./{}-ibasis*/ProtSS.out'.format(prefix))
    dset = []
    dset_int = []
    rmsd = []
    for f in flist:
        with open(f) as fp:
            for i, line in enumerate(fp):
                if i == 4:
                    # ibasis set name
                    db = split_string(line)[4]
                    dset.append(db)
                    if db in refsets.iterkeys():
                        dset_int.append(refsets[db])
                elif i == 7:
                    # rmsd value
                    qfit = split_string(line)[2]
                    rmsd.append(float(qfit))

    d = {'dname': dset, 'dset_int': dset_int, 'rmsd': rmsd, 'protss': flist}
    df = pd.DataFrame(data=d)

    return df
