#!/usr/bin/env python

import os
import re
import sys
import logging
import argparse
import subprocess
from datetime import datetime
import numpy as np
import shutil
import seaborn as sns
import time
import matplotlib.pyplot as plt
import pandas as pd
import more_itertools
import StringIO
import cdgo
from mathops import sum_squares_residuals
from mathops import r_squared
from mathops import rms_error
from mathops import millidegrees_to_epsilon
from readers import read_protss
from readers import read_continll
from readers import read_cdsstr

notes = (
    "\n"
    "CDGo is research software. If you use CDGo in your research, please \n"
    "acknowledge it appropriately. E.g.:\n"
    "\t...using the software package CDPro (Sreerama and Woody, 2000) as \n"
    '\t(available from https://github.com/s-gordon/CDGo)\n\n'
    'Any use of CDGo in research should also cite the software package\n'
    'CDPro (found http://sites.bmb.colostate.edu/sreeram/CDPro/):\n'
    '\tSreerama, N., & Woody, R. W. (2000). Estimation of protein \n'
    '\tsecondary structure from circular dichroism spectra: comparison of \n'
    '\tCONTIN, SELCON, and CDSSTR methods with an expanded reference set. \n'
    '\tAnalytical biochemistry, 287(2), 252-260.\n\n'
    'Use of individual protein reference databases should also be credited\n'
    'appropriately. For a full listing of each database and the \n'
    'appropriate citation, please use the following link:\n'
    '\thttp://sites.bmb.colostate.edu/sreeram/CDPro/\n')
now = datetime.now()

print(notes)


def parse_num_list(string):
    """Docstring for parse_num_list

    :string:
    :returns: list of integers

    """
    m = re.match(r'(\d+)(?:-(\d+))?$', string)
    # ^ (or use .split('-'). anyway you like.)
    if not m:
        raise argparse.ArgumentTypeError(
            "'" + string +
            "' is not a range of number. Expected forms like '0-5' or '2'.")
    start = m.group(1)
    end = m.group(2) or start
    return list(range(int(start, 10), int(end, 10) + 1))


# Argparse
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


parser = MyParser(description='Run CDPro automatically.',
                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-C',
                    action="store",
                    dest="cdpro_dir",
                    default="/Users/sgordon/.wine/drive_c/Program Files/CDPro",
                    help="CDPro executable directory")
parser.add_argument('-i',
                    action="store",
                    dest="cdpro_input",
                    required=True,
                    help="Aviv-format protein sample CD \
                    spectra file.")
parser.add_argument('--mol_weight',
                    action="store",
                    required=True,
                    type=float,
                    help="Molecular weight (Da)")
parser.add_argument('--pathlength',
                    action="store",
                    required=False,
                    type=float,
                    default=0.1,
                    help="Pathlength of cuvette (cm).")
parser.add_argument('--number_residues',
                    action="store",
                    required=True,
                    type=int,
                    help="Residues")
parser.add_argument('--concentration',
                    action="store",
                    required=True,
                    type=float,
                    help="Concentration (mg/ml)")
parser.add_argument('--buffer',
                    action="store",
                    required=False,
                    dest="buffer",
                    help="Buffer file for blank.")
parser.add_argument('--cdsstr',
                    action="store_true",
                    required=False,
                    help="""
                    Use CDSSTR algorithm for fitting.

                    If you use CDSSTR for your work please cite the
                    following:

                    Sreerama, N. and Woody, R.W. (2000) Estimation of protein
                    secondary structure from CD spectra: Comparison of CONTIN,
                    SELCON and CDSSTR methods with an expanded reference set.
                    Anal. Biochem. 287(2), 252-260.
                    """)
parser.add_argument('--db_range',
                    type=parse_num_list,
                    default="1-10",
                    help="""
                    CDPro ibasis range to use. Accepted values are
                    between 1 and 10 inclusive.

                    Acceptable values are ranges (e.g. 2-5) or integers
                    (e.g. 2).
                    """)
parser.add_argument('--continll',
                    action="store_true",
                    required=False,
                    help="""
                    Use CONTINLL algorithm for fitting.

                    If you use CONTINLL for your work please cite the
                    following:

                    Sreerama, N., & Woody, R. W. (2000). Estimation of
                    protein secondary structure from circular dichroism
                    spectra: comparison of CONTIN, SELCON, and CDSSTR methods
                    with an expanded reference set. Analytical biochemistry,
                    287(2), 252-260.
                    """)

parser.add_argument('-v',
                    '--verbose',
                    action="store_true",
                    help="Increase verbosity")

result = parser.parse_args()
"""
If verbosity set, change logging to debug.
Else leave at info
"""
if result.verbose:
    logging.basicConfig(format='%(levelname)s:\t%(message)s',
                        level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s:\t%(message)s',
                        level=logging.INFO)


def logfile(fname, parser, **kwargs):
    """Docstring for logfile
    :fname: output logfile name
    :parser: argparse parser object

    :returns: None
    """
    with open(fname, 'w') as f:
        f.write(
            "Logfile for CDGo. See below details of the arguments provided." +
            "\n\n")
        f.write(notes + "\n\n")
        f.write('Date: {}\n'.format(now.strftime("%Y-%m-%d %H:%M")))
        f.write('CDGo Version: {}\n'.format(cdgo.__version__))
        f.write('CDPro path: {}\n'.format(parser.cdpro_dir))
        f.write('Input file: {}\n'.format(parser.cdpro_input))
        f.write('Protein molecular weight: {}\n'.format(parser.mol_weight))
        f.write('Cuvette pathlength (cm): {}\n'.format(parser.pathlength))
        f.write('Number of residues: {}\n'.format(parser.number_residues))
        f.write('Protein concentration: {}\n'.format(parser.concentration))
        f.write('Buffer file: {}\n'.format(parser.buffer))
        f.write('iBasis range: {}\n'.format(parser.db_range))
        f.write('CONTINLL?: {}\n'.format(parser.continll))
        f.write('CDSSTR?: {}\n'.format(parser.cdsstr))
        for key, value in kwargs.items():
            f.write('{}: {}\n'.format(key, value))


def read_line(f, line_no):
    """TODO: Docstring for read_line.

    :f: file name
    :line_no: single line number to read
    :returns: line

    """

    with open(f) as fp:
        for i, line in enumerate(fp):
            if i == line_no:
                l = line
    return l


def read_multi_aviv(f):
    """Wrapper function to read in raw Aviv CD data files

    :f: TODO
    :returns: TODO

    """

    # check file summary for experiment type
    # if the exp type is not wavelength, throw an error and exit
    exp_type = read_line(f, 1)
    # delimit with colon + space
    exp_type = exp_type.split(': ')[1]
    # remove trailing newlines and carriage returns
    exp_type = exp_type.rstrip("\r\n")
    if exp_type != "Wavelength":
        logging.error(
            ("The experiment type for one or more of input files is {e}.\n"
             "Only wavelength experiments are allowed at this time. Please\n"
             "check your inputs and try again.").format(e=exp_type))
        sys.exit(2)
    else:
        logging.debug("Experiment type for file {f} is {e}.".format(
            f=f, e=exp_type))

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


def aviv_raw_input_to_pandas(input):
    """TODO: Docstring for aviv_raw_input_conv.

    :input: aviv output as string. One dataset per string.
    :returns: pandas dataframe containing aviv data

    """
    # read input to dataframe, delimiting with spaces
    # discard first line, containing config jargon
    df = pd.read_csv(StringIO.StringIO(input),
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


def replace_input(input, output, ibasis):
    """
    return: None
    """

    pattern = '# PRINT(.*\n)\s+(\S+)(.*)'
    replace = '# PRINT    IBasis\n      0         {}'.format(ibasis)
    f = open(input, 'r')
    lines = f.read()
    f.close()
    r = re.sub(pattern, replace, lines)

    with open(output, 'w') as o:
        for line in r:
            o.write(line)


def set_style():
    """
    Set the global style for seaborn plots
    """
    sns.set(style="darkgrid")


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


def cdpro_input_footer():
    """
    :returns: Multiline string mimicking cdpro input footer

    """

    footer = ("#                                                  \n"
              "#  IGuess  Str1   Str2   Str3   Str4   Str5    Str6\n"
              "        0                                          \n")
    return footer


def check_dir(dir):
    """
    Check whether directory dir exists.
    If true continue. Else exit.
    """
    if not os.path.isdir(dir):
        logging.error('Path %s not found', dir)
        logging.error('Aborting')
        sys.exit()


def delete_dir(dir):
    """
    Check whether directory dir exists.
    If true delete and remake.
    """
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


def check_cmd(*kwargs):
    """Verify that exe in accessible

    exe: absolute path to exe file, or entry within PATH
    returns: None
    """
    for exe in kwargs:
        try:
            subprocess.check_call(['%s --version>/dev/null' % exe], shell=True)
        except subprocess.CalledProcessError:
            logging.error('Command %s not found or not in path' % exe)
            sys.exit(2)


def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def cd_output_style(style_1, style_2, algorithm):
    if os.path.isfile(style_1) is True:
        logging.debug('{algorithm} style is {style}'.format(
            algorithm=algorithm, style=style_1))
        return style_1
    elif os.path.isfile(style_2) is True:
        logging.debug('{algorithm} style is {style}'.format(
            algorithm=algorithm, style=style_2))
        return style_2
    else:
        sys.exit(2)


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
        logging.error(
            "Bad input data. Please check that data is correctly formatted")
        sys.exit(2)
    return min, max, step


def single_line_scatter(datafile,
                        fit_label,
                        ax,
                        flip=True,
                        x_col_name='WaveL',
                        calc_col='CalcCD'):
    """Docstring for single_line_scatter

    """

    df = pd.read_csv(datafile,
                     skipinitialspace=True,
                     sep=r"\s*",
                     engine='python')

    # Invert data vertically to compensate for CDPro output
    if flip is True:
        df = df.iloc[::-1]

    df.plot(x=x_col_name, y=calc_col, style='-', ax=ax, label=fit_label)


def cdpro_input_writer(body, head, fname='input'):
    """TODO: Docstring for cdpro_input_writer.

    :body: CDPro input body text. Contains n rows of length 10, where the final
           line may be up to 10 items
    :head: CDPro input header information
    :returns: None

    """

    f = open(fname, 'w')
    f.write(head)
    for line in body:
        # Separate list items by two spaces and append newline
        f.write('  ' + '  '.join(str(x) for x in line) + '\n')
    f.write(cdpro_input_footer())
    f.close()


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


def best_fit(df, col, ax):
    """TODO: Docstring for best_fit.

    :df: TODO
    :col: value for dataframe column 'alg' with which to subsample
    :returns: TODO

    """
    if col == 'continll':
        fit_fname = "CONTIN.CD"
    elif col == 'cdsstr':
        fit_fname = 'reconCD.out'
    else:
        logging.error("Unknown algorithm reference {} supplied.".format(col))
        sys.exit(2)
    # select only rows with alg value equal to col
    df = df.loc[df['alg'] == col]
    # select row with lowest rmsd value as top
    top = df.ix[df['rmsd'].idxmin()]
    logging.info('best ibasis for {a}: {i}'.format(a=col, i=top.name))
    # full file name and path for plot file
    fname = '{a}-ibasis{i}/{f}'.format(a=col, i=top.name, f=fit_fname)
    # plot label for matplotlib
    flab = '{alg} ibasis {ib} (RMSD: {rmsd})'.format(alg=col,
                                                     ib=top.name,
                                                     rmsd=top['rmsd'])
    # plot on supplied axis
    single_line_scatter(fname, flab, ax)


def main():
    """Docstring for main

    :returns: None
    """

    # shell commands for continll and cdsstr
    continll_cmd = ('echo | WINEDEBUG=-all wine Continll.exe > stdout || '
                    'echo -n "(crashed)"')
    cdsstr_cmd = ('echo | WINEDEBUG=-all wine CDSSTR.EXE > stdout || '
                  '"echo -n (crashed)"')

    # read in data files for dataset (dat) and reference buffer for subtraction
    # (buf)
    dat = read_multi_aviv(result.cdpro_input)
    buf = read_multi_aviv(result.buffer)

    logging.debug("Replicates in sample dataset: {}".format(dat.nreps))
    logging.debug("Replicates in reference dataset: {}".format(buf.nreps))

    # subtract signal for reference from sample
    df = (dat["ave"] - buf["ave"])
    # drop mismatched wavelengths
    df = df.dropna()

    # Convert from the input units of millidegrees to the standard delta
    # epsilon, dropping nan lines
    # Convert both the average (df) and standard dev (dat["std"])
    epsilon = pd.concat([
        millidegrees_to_epsilon(df,
                                result.mol_weight,
                                result.number_residues,
                                result.concentration,
                                L=result.pathlength),
        millidegrees_to_epsilon(dat["std"],
                                result.mol_weight,
                                result.number_residues,
                                result.concentration,
                                L=result.pathlength)
    ],
                        axis=1).dropna()

    # derermine min, max, and step of wavelengths recorded
    max, min, step = list_params(epsilon["ave"])
    # Remap the df index to floats. Required for drop_indices
    epsilon.index = epsilon.index.map(float)
    # force inverse sorting
    epsilon = epsilon.sort_index(ascending=False)  # force inverse sorting
    # drop bad datapoints
    epsilon_ints = drop_indices(epsilon)

    head = cdpro_input_header(max, min)

    body = list(more_itertools.chunked(epsilon_ints["ave"], 10))
    cdpro_input_writer(body, head)

    check_cmd('wine')

    check_dir(result.cdpro_dir)

    base_dir = os.path.dirname(os.path.realpath(result.cdpro_input))

    cdpro_out_dir = "%s/%s-CDPro" % (base_dir, result.cdpro_input)
    delete_dir(cdpro_out_dir)
    logging.debug('Processing %s into %s' %
                  (result.cdpro_input, cdpro_out_dir))
    # log args into to logfile lname
    lname = '{p}/input.log'.format(p=cdpro_out_dir)
    logfile(lname, result, reps_sample=dat.nreps, reps_reference=buf.nreps)
    shutil.copy("input", "%s/input" % (result.cdpro_dir))
    os.chdir(result.cdpro_dir)
    ss_assign = pd.DataFrame()

    for ibasis in result.db_range:

        logging.info('ibasis %s', ibasis)

        replace_input('input', 'input', ibasis)

        ss_col_head = [
            'ibasis', 'alg', 'ahelix', 'bstrand', 'turn', 'unord', 'rmsd',
            'ss_res', 'r2'
        ]

        if result.continll is True:
            """
            if continll switch is True, run the continll algorithm and pull
            secondary structure assignments
            """
            logging.debug('Running CONTINLL')
            subprocess.call([continll_cmd], shell=True)

            continll_outdir = ('%s/continll-ibasis%s' %
                               (cdpro_out_dir, ibasis))
            continll_out = cd_output_style("CONTINLL.OUT", "continll.out",
                                           "continll")

            make_dir(continll_outdir)
            for f in [
                    "CONTIN.CD", "CONTIN.OUT", continll_out, "BASIS.PG",
                    "ProtSS.out", "SUMMARY.PG", "stdout"
            ]:
                shutil.move(f, "%s/" % (continll_outdir))
                if os.path.isfile("input"):
                    shutil.copy("input", "%s/" % (continll_outdir))
            # read in fit values and stats
            db, int, ss = read_protss('{}/ProtSS.out'.format(continll_outdir))
            """
            read in continll output
            returns stats about fit such as rms error, sum-of-squares
            residuals, etc
            """
            p = read_continll('{}/CONTIN.CD'.format(continll_outdir))
            ss_res = sum_squares_residuals(p['CalcCD'], p['ExpCD'])
            r2 = r_squared(p['CalcCD'], p['ExpCD'])
            rmsd = rms_error(p['CalcCD'], p['ExpCD'])

            # define new dataframe with output from read_protss
            df = pd.DataFrame([[
                db, 'continll', ss['ahelix'], ss['bstrand'], ss['turn'],
                ss['unord'], rmsd, ss_res, r2
            ]],
                              index=[ibasis])
            # append fit values and stats to dataframe
            ss_assign = ss_assign.append(df)

        if result.cdsstr is True:
            """
            if cdsstr switch is True, run the cdsstr algorithm and pull
            secondary structure assignments
            """
            logging.debug('Running CDSSTR')
            subprocess.call([cdsstr_cmd], shell=True)
            cdsstr_outdir = ('%s/cdsstr-ibasis%s' % (cdpro_out_dir, ibasis))
            make_dir(cdsstr_outdir)
            cdsstr_out = cd_output_style("CDsstr.out", "cdsstr.out", "CDSSTR")

            for f in ["reconCD.out", "ProtSS.out", cdsstr_out, "stdout"]:
                shutil.move(f, "%s/" % (cdsstr_outdir))
            if os.path.isfile("input"):
                shutil.copy("input", "%s/" % (cdsstr_outdir))
            # read in fit values and stats
            db, int, ss = read_protss('{}/ProtSS.out'.format(cdsstr_outdir))
            """
            read in continll output
            returns stats about fit such as rms error, sum-of-squares
            residuals, etc
            """
            p = read_cdsstr('{}/reconCD.out'.format(cdsstr_outdir))
            ss_res = sum_squares_residuals(p['CalcCD'], p['Exptl'])
            r2 = r_squared(p['CalcCD'], p['Exptl'])
            rmsd = rms_error(p['CalcCD'], p['Exptl'])

            df = pd.DataFrame([[
                db, 'cdsstr', ss['ahelix'], ss['bstrand'], ss['turn'],
                ss['unord'], rmsd, ss_res, r2
            ]],
                              index=[ibasis])
            # append fit values and stats to dataframe
            ss_assign = ss_assign.append(df)

    os.chdir(cdpro_out_dir)

    set_style()

    # assign column headings
    ss_assign.columns = ss_col_head

    # round floats to 3 decimal places for certain columns
    ss_assign.rmsd = ss_assign.rmsd.round(3)
    ss_assign.ss_res = ss_assign.ss_res.round(3)
    ss_assign.r2 = ss_assign.r2.round(3)

    # Print the matplotlib overlay
    logging.debug('Plotting fit overlays')

    outfile = 'CDSpec-{}-{}-Overlay.png'.format(result.cdpro_input,
                                                time.strftime("%Y%m%d"))

    ax = plt.subplots(nrows=1, ncols=1)[1]

    if result.continll is True:
        best_fit(ss_assign, 'continll', ax)

    if result.cdsstr is True:
        best_fit(ss_assign, 'cdsstr', ax)

    epsilon["ave"] = epsilon["ave"].astype(float)
    epsilon["std"] = epsilon["std"].astype(float)
    epsilon["wl"] = epsilon.index

    epsilon.plot.scatter(ax=ax,
                         x="wl",
                         y="ave",
                         yerr="std",
                         label="exp",
                         color="black")
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('$\Delta\epsilon$ ($M^{-1}{\cdot}cm^{-1}$)')
    ax.legend()
    plt.savefig(outfile, bbox_inches='tight')

    # save epsilon-format exp data to csv file for later plotting
    epsilon.to_csv('{}/exp_data_delta_epsilon.csv'.format(cdpro_out_dir))

    ss_assign.to_csv(
        '{}/secondary_structure_summary.csv'.format(cdpro_out_dir))
    logging.info('\n{}\n'.format(ss_assign))


if __name__ == '__main__':
    main()
