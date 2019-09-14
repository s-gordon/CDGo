#!/usr/bin/env python

import sys
import re
import pandas as pd
import numpy as np
from .init_logging import logger
from .mathops import millidegrees_to_epsilon
try:
    from io import StringIO  # python2
except ImportError:
    from io import StringIO  # python3


def drop_indices(df):
    """TODO: Docstring for drop_indices.

    :df: pandas dataframe with float-based index
    :returns: pandas dataframe subsampled to exclude rows with indices not
              evenly divisible by 1

    """
    # Establish what indices we want to discard. Namely, we want to get rid of
    # non-integers, as CDPro discards these.
    bad_indices = ~df.index.isin(np.arange(159.5, 260.5, 1))

    # Subsample the input dataframe, removing integers that match the condition
    # above
    df = df[bad_indices]

    return df


def list_params(df):
    """Get key list params.

    :df: pandas dataframe
    :returns: list max, min, and step size of the pandas indices
    """
    df = df.index.astype(float)
    try:
        max = df.max()
        min = df.min()
        step = df[-1] - df[-2]
    except IndexError:
        logger.error(
            "Bad input data. Please check that data is correctly formatted")
        sys.exit(2)
    return min, max, step


def aviv_raw_input_to_pandas(input):
    """TODO: Docstring for aviv_raw_input_conv.

    :input: aviv output as string. One dataset per string.
    :returns: pandas dataframe containing aviv data

    """
    # read input to dataframe, delimiting with spaces
    # discard first line, containing config jargon
    df = pd.read_csv(StringIO(input),
                     sep="  ",
                     skiprows=1,
                     header=0,
                     engine="python")
    # Set row names (indices) to col X (i.e. wavelength)
    df = df.set_index('X')
    # Throw away data when the dynode voltage peaks beyond 600
    # Dynode voltage cutoff as CLI flag?
    df = df[(df.CD_Dynode < 600)]
    # Subsample the resulting dataframe to exclude irrelevant cols
    return df[['CD_Signal']]


def read_line(f, line_no):
    """TODO: Docstring for read_line.

    :f: file name
    :line_no: single line number to read
    :returns: line

    """

    with open(f) as fp:
        for i, line in enumerate(fp):
            if i == line_no:
                entry = line
    return entry


def cdpro_input_header(firstvalue, lastvalue):
    """
    :returns: Multiline string mimicking cdpro output

    """

    firstvalue = '{:0.4f}'.format(firstvalue)
    lastvalue = '{:0.4f}'.format(lastvalue)
    header = ("#                                                  \n"
              "# PRINT    IBasis                                  \n"
              "      1         0\n"
              "#                                                  \n"
              "#  ONE Title Line                                  \n"
              " Title\n"
              "#                                                  \n"
              "#     WL_Begin     WL_End       Factor             \n"
              "      {first}      {last}      1.0000\n"
              "#                                                  \n"
              "# CDDATA (Long->Short Wavelength; 260 - 178 LIMITS \n").format(
                  first=lastvalue, last=firstvalue)
    return header


def read_multi_aviv(f):
    # check file summary for experiment type
    # if the exp type is not wavelength, throw an error and exit
    # delimit with colon + space
    # remove trailing newlines and carriage returns
    exp_type = read_line(f, 1).split(': ')[1].rstrip("\r\n")
    if exp_type != "Wavelength":
        logger.error(
            ("The experiment type for one or more of input files is {e}.\n"
             "Only wavelength experiments are allowed at this time.\n"
             "Please check your inputs and try again.").format(e=exp_type))
        sys.exit(2)
    else:
        logger.info("Experiment type for file {f} is {e}.".format(f=f,
                                                                  e=exp_type))

    # read data into buffer
    stream = open(f, 'r')
    # dos 2 linux format. change carriage returns
    input = stream.read().replace('\r\n', '\n')

    # regex find exp data components and assign to new var d
    d = re.findall(
        "(?<=\$MDCDATA).*?(?=\$MDCNAME)|(?<=\$MDCDATA).*?(?=\$ENDDATA)", input,
        re.DOTALL)

    # create new list and populate it with processed aviv data
    # each data set is an item in the new list
    ds_list = []
    for ds in d:
        ds_list.append(aviv_raw_input_to_pandas(ds))
    result = pd.concat([i for i in ds_list], axis=1, sort=False, names=[1, 2])
    result.columns = ["Set{}".format(idx) for idx in range(len(d))]

    # record number reps in new dataframe
    nreps = len(d)

    # drop any wavelengths not present in all data sets
    result = result.dropna()

    # calculate average and std. Append as new cols.
    result["ave"] = result.mean(axis=1)
    result["std"] = result.std(axis=1)
    result.nreps = nreps
    return result


class AvivReader(object):
    """Docstring for AvivReader. """
    def __init__(self, protFileName, bufferFileName, mol_weight,
                 number_residues, prot_concentration, pathlength):
        """TODO: to be defined. """
        self.protFileName = protFileName
        self.bufferFileName = bufferFileName
        self.mw = mol_weight
        self.number_residues = number_residues
        self.conc = prot_concentration
        self.pl = pathlength
        self.protSpectrum = read_multi_aviv(protFileName)
        self.bufferSpectrum = read_multi_aviv(bufferFileName)

    def subBufferSpectrum(self):
        """
        subtract signal for reference from sample
        """
        ps = self.protSpectrum
        bs = self.bufferSpectrum
        sub = ps["ave"] - bs["ave"]
        # drop mismatched wavelengths
        sub = sub.dropna()
        self.sub = sub

    def mreToEps(self):
        """
        Convert from the input units of millidegrees to the standard delta
        epsilon, dropping nan lines
        Convert both the average (df) and standard dev (dat["std"])
        """
        sub = self.sub
        ps = self.protSpectrum
        mw = self.mw
        nres = self.number_residues
        conc = self.conc
        pl = self.pl
        sub_epsilon = millidegrees_to_epsilon(sub, mw, nres, conc, pl)
        std_epsilon = millidegrees_to_epsilon(ps["std"], mw, nres, conc, pl)
        epsilon = pd.concat([sub_epsilon, std_epsilon], axis=1).dropna()
        # Remap the df index to floats. Required for drop_indices
        epsilon.index = epsilon.index.map(float)
        # force inverse sorting
        epsilon = epsilon.sort_index(ascending=False)  # force inverse sorting
        # derermine min, max, and step of wavelengths recorded
        epsilon["wl"] = epsilon.index
        epsilon["ave"] = epsilon["ave"].astype(float)
        epsilon["std"] = epsilon["std"].astype(float)
        max, min, step = list_params(epsilon["ave"])
        self.max = max
        self.min = min
        self.step = step
        self.epsilon = epsilon
        # drop bad datapoints
        epsilon_ints = drop_indices(epsilon)
        self.epsilon_ints = epsilon_ints
