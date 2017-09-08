#!/usr/bin/env python
# AUTHOR:   Shane Gordon
# ROLE:     TODO (some explanation)
# CREATED:  2015-06-06 13:12:10

import os
import re
import sys
import logging
import argparse
import subprocess
import numpy as np
import shutil
import seaborn as sns
import time
import matplotlib.pyplot as plt
import pandas as pd
import more_itertools
from readers import compare_ibases


def allowed_ibasis_val(x):
    x = int(x)
    if 1 < x > 10:
        raise argparse.ArgumentTypeError(
            "Acceptable ibases are between 1 and 10"
        )
    sys.exit(2)
    return x


# Argparse
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


parser = MyParser(description='Run CDPro automatically.',
                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-C', action="store", dest="cdpro_dir",
                    default="/Users/sgordon/.wine/drive_c/Program Files/CDPro",
                    help="CDPro executable directory")
parser.add_argument('-i', action="store", dest="cdpro_input",
                    required=True, help="CDPro executable directory")
parser.add_argument('--mol_weight', action="store", required=True,
                    type=float,
                    help="Molecular weight (Da)")
parser.add_argument('--number_residues', action="store", required=True,
                    type=int, help="Residues")
parser.add_argument('--concentration', action="store", required=True,
                    type=float, help="Concentration (mg/ml)")
parser.add_argument('--buffer', action="store", required=False,
                    dest="buffer", help="Buffer file for blank.")
parser.add_argument('--cdsstr', action="store_true", required=False,
                    help="Use CDSSTR algorithm for fitting.")
parser.add_argument('--continll', action="store_true", required=False,
                    help="""
                    Use CONTINLL algorithm for fitting.

                    If you use CONTINLL for your work please cite the
                    following:

                    [1] Sreerama, N., & Woody, R. W. (2000). Estimation of
                    protein secondary structure from circular dichroism
                    spectra: comparison of CONTIN, SELCON, and CDSSTR methods
                    with an expanded reference set. Analytical biochemistry,
                    287(2), 252-260.

                    [2]
                    """)

parser.add_argument('-v', '--verbose', action="store_true",
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


def read_aviv(f, save_line_no=False, last_line_no=False):
    """Wrapper function to read in raw Aviv CD data files

    :f: TODO
    :returns: TODO

    """

    df = pd.read_csv(f, sep='  ', skiprows=18, header=0, engine='python')
    if last_line_no is False:
        line_no = df[df['X'].str.contains("\$ENDDATA")].index.tolist()
        line_no = line_no[0]
    else:
        line_no = last_line_no
    df = df.iloc[0:line_no]

    # Subsample the resulting dataframe to exclude irrelevant cols
    df = df[['X', 'CD_Signal', 'CD_Dynode']]

    # Set row names (indices) to col X (i.e. wavelength)
    df = df.set_index('X')

    # Throw away data when the dynode voltage peaks beyond 600
    df = df[(df.CD_Dynode < 600)]
    return df, line_no if save_line_no is True else df


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


def cdpro_input_header(firstvalue, lastvalue, factor):
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
              "# CDDATA (Long->Short Wavelength; 260 - 178 LIMITS \n"
              ).format(first=lastvalue, last=firstvalue)
    return header


def cdpro_input_footer():
    """
    :returns: Multiline string mimicking cdpro input footer

    """

    footer = ("#                                                  \n"
              "#  IGuess  Str1   Str2   Str3   Str4   Str5    Str6\n"
              "        0                                          \n"
              )
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


def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def list_params(df):
    """Get key list params.

    :df: pandas dataframe
    :returns: list max, min, and step size of the pandas indices
    """
    df = df.index.astype(float)
    max = df.max()
    min = df.min()
    step = df[-1] - df[-2]
    return min, max, step


def single_line_scatter(datafile, fit_label, exp_label, ax,
                        flip=True, x_col_name='WaveL',
                        calc_col='CalcCD', xlabel='Wavelength (nm)',
                        ylabel='$\Delta\epsilon$ ($M^{-1}{\cdot}cm^{-1}$)'):
    """Docstring for single_line_scatter

    """

    df = pd.read_table(datafile, skipinitialspace=True, sep=r"\s*",
                       engine='python')

    # Invert data vertically to compensate for CDPro output
    if flip is True:
        df = df.iloc[::-1]

    try:
        df.plot(x=x_col_name, y='ExpCD', style='.', ax=ax, label=exp_label)
    except KeyError:
        try:
            df.plot(x=x_col_name, y='Exptl', style='.', ax=ax, label=exp_label)
        except KeyError as e:
            logging.error(e)

    df.plot(x=x_col_name, y=calc_col, style='-', ax=ax, label=fit_label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # plt.savefig(outfile, bbox_inches='tight')


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


def double_line_scatter(datafile1, datafile2, fit_label1, fit_label2,
                        exp_label,
                        df1_headers, df2_headers, outfile='output.png',
                        flip=True, xlabel='Wavelength (nm)',
                        ylabel='$\Delta\epsilon$ ($M^{-1}{\cdot}cm^{-1}$)'):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    df1 = pd.read_table(datafile1, skipinitialspace=True, sep=r"\s*",
                        engine='python', usecols=df1_headers)
    df2 = pd.read_table(datafile2, skipinitialspace=True, sep=r"\s*",
                        engine='python', usecols=df2_headers)

    # Invert data vertically to compensate for CDPro output
    if flip is True:
        df1 = df1.iloc[::-1]
        df2 = df2.iloc[::-1]

    df1.plot(x='WaveL', y='ExpCD', style='o', ax=ax, label=exp_label)
    df1.plot(x='WaveL', y='CalcCD', style='-', ax=ax, label=fit_label1)
    df2.plot(x='WaveL', y='CalcCD', style='-', ax=ax, label=fit_label2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.savefig(outfile, bbox_inches='tight')


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


def millidegrees_to_epsilon(df, mrc):
    """TODO

    df: single column pandas dataframe
    mrc: mean residue concentration conversion factor
    returns:
    """
    return (df * mrc/3298).map(lambda x: '%1.3f' % x)


def alg_eval(alg):
    """TODO

    alg: algorithm to use for fitting. Acceptable values are "continll" and
         "cdsstr"
    returns:

    """

    if alg == "continll":
        f = 'CONTIN.CD'
    elif alg == "cdsstr":
        f = 'reconCD.out'

    protss = compare_ibases(alg)
    topfit = protss.ix[protss['rmsd'].idxmin()]
    best_rmsd = topfit['rmsd']
    best_ibasis = topfit['dset_int']
    ibasis_dir = topfit['protss'][0:-11]

    # best_rmsd, best_ibasis, ibasis_dir = compare_ibases(alg)
    logging.info('Best %s RMSD: %s' % (alg, best_rmsd))

    with open('best-%s' % (alg), 'w') as fl:
        fl.write(str(best_ibasis))
        fl.close

    logging.info('Best ibasis for %s: %s' % (alg, best_ibasis))
    plot = '%s/%s' % (ibasis_dir, f)
    label = '{} ibasis {}: RMSD={}'.format(alg,
                                           best_ibasis,
                                           best_rmsd)
    # outfile = 'CDSpec-{}-{}-best{}.png'.format(
    #     result.cdpro_input,
    #     time.strftime("%Y%m%d"),
    #     alg
    # )
    # single_line_scatter(plot, label, 'Exp', ax, outfile=outfile)
    return plot, label


def dec_to_percent(n):
    """Docstring for dec_to_percent

    :n: float value or list as fraction
    :returns: value or list multiplied by 10e2
    """

    return n * 100


def format_val(v):
    """Takes in float and formats as str with 1 decimal place

    :v: float
    :returns: str

    """
    return '{:.1f}%'.format(v)


def find_line(fname, pattern):
    """Docstring for find_line

    :fname: file name
    :pattern:
    :returns:

    """
    with open(fname) as search:
        for line in search:
            line = line.strip()  # remove '\n' at EOL
            if pattern in line:
                o = line.split()[2:]  # output ss as list
                o = [float(i) for i in o]  # convert to float
            if 'Ref. Prot. Set' in line:
                db = line.split()[3]  # split db to get int
            if 'RMSD(Exp-Calc)' in line and 'NRMSD(Exp-Calc)' not in line:
                rmsd = line.split()[1]  # split line to get rmsd
                rmsd = float(rmsd)
                rmsd = '{:.3f}'.format(rmsd)
    return o, db, rmsd


def read_protss_assignment(f):
    """read in ProtSS file from CDPro and parse sec struc assignments

    :f: TODO
    :ibasis: ibasis reference for ProtSS
    :returns: TODO
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

    """
    for each ibasis, parse through output and collect secondary structure
    lines using pattern 'Fractions'. Split output into list, removing the first
    two (irrelevant) entries.
    """
    ss, db, rmsd = find_line(f, 'Fractions')
    if db in ibasis_group_1['members']:
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
    elif db in ibasis_group_2['members']:
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
    elif db in ibasis_group_3['members']:
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
    return ss, db, rmsd


def main():
    """Docstring for main

    :returns: None
    """

    # read in data files for dataset (dat) and reference buffer for subtraction
    # (buf)
    dat, lline = read_aviv(result.cdpro_input, save_line_no=True)
    buf = read_aviv(result.buffer, save_line_no=False, last_line_no=lline)[0]

    # subtract signal for reference from sample
    df = (dat - buf).dropna()

    # convert into units of mre
    mrc = result.mol_weight / (result.number_residues * result.concentration)

    # Convert from the input units of millidegrees to the standard delta
    # epsilon
    epsilon = millidegrees_to_epsilon(df['CD_Signal'], mrc)
    max, min, step = list_params(epsilon)

    # Remap the df index to floats. Required for drop_indices
    epsilon.index = epsilon.index.map(float)
    # drop bad datapoints
    epsilon = drop_indices(epsilon)
    # force inverse sorting
    epsilon = epsilon.sort_index(ascending=False)    # force inverse sorting

    head = cdpro_input_header(max, min, 1)

    body = list(more_itertools.chunked(epsilon, 10))
    cdpro_input_writer(body, head)

    check_cmd('wine')

    check_dir(result.cdpro_dir)

    base_dir = os.path.dirname(os.path.realpath(result.cdpro_input))

    cdpro_out_dir = "%s/%s-CDPro" % (base_dir, result.cdpro_input)
    delete_dir(cdpro_out_dir)
    logging.debug('Processing %s into %s' % (result.cdpro_input,
                                             cdpro_out_dir))
    shutil.copy("input", "%s/input" % (result.cdpro_dir))
    os.chdir(result.cdpro_dir)
    ss_assignments = pd.DataFrame()

    for ibasis in (range(1, 11)):

        logging.info('ibasis %s', ibasis)

        replace_input('input', 'input', ibasis)

        ss_col_head = ['ibasis', 'alg', 'ahelix', 'bstrand', 'turn', 'unord',
                       'rmsd']

        if result.continll is True:
            logging.debug('Running CONTINLL')
            subprocess.call(['echo | WINEDEBUG=-all wine Continll.exe > stdout || echo -n "\
                             (crashed)"'], shell=True)
            continll_outdir = ('%s/continll-ibasis%s' % (cdpro_out_dir,
                                                         ibasis))
            continll_out = cd_output_style("CONTINLL.OUT", "continll.out",
                                           "continll")
            make_dir(continll_outdir)
            for f in ["CONTIN.CD", "CONTIN.OUT", "%s" % (continll_out),
                      "BASIS.PG", "ProtSS.out", "SUMMARY.PG", "stdout"]:
                shutil.move(f, "%s/" % (continll_outdir))
                if os.path.isfile("input"):
                    shutil.copy("input", "%s/" % (continll_outdir))

            ss, db, rmsd = read_protss_assignment(
                '{}/ProtSS.out'.format(continll_outdir)
            )
            df = pd.DataFrame(
                [[db, 'continll', ss['ahelix'], ss['bstrand'], ss['turn'],
                  ss['unord'], rmsd]], index=[ibasis]
            )
            ss_assignments = ss_assignments.append(df)

        if result.cdsstr is True:
            logging.debug('Running CDSSTR')
            subprocess.call(['echo | WINEDEBUG=-all wine CDSSTR.EXE > stdout || echo -n "\
                             (crashed)"'], shell=True)
            cdsstr_outdir = ('%s/cdsstr-ibasis%s' % (cdpro_out_dir, ibasis))
            make_dir(cdsstr_outdir)
            cdsstr_out = cd_output_style("CDsstr.out", "cdsstr.out", "CDSSTR")

            for f in ["reconCD.out", "ProtSS.out", "%s" % (cdsstr_out),
                      "stdout"]:
                shutil.move(f, "%s/" % (cdsstr_outdir))
            if os.path.isfile("input"):
                shutil.copy("input", "%s/" % (cdsstr_outdir))

            ss, db, rmsd = read_protss_assignment(
                '{}/ProtSS.out'.format(cdsstr_outdir),
            )
            df = pd.DataFrame(
                [[db, 'cdsstr', ss['ahelix'], ss['bstrand'], ss['turn'],
                  ss['unord'], rmsd]], index=[ibasis]
            )
            ss_assignments = ss_assignments.append(df)

    os.chdir(cdpro_out_dir)

    set_style()

    if result.continll is True:
        continll_plot, continll_label = alg_eval('continll')

    if result.cdsstr is True:
        cdsstr_plot, cdsstr_label = alg_eval('cdsstr')

    # Print the matplotlib overlay
    logging.debug('Plotting fit overlays')

    outfile = 'CDSpec-{}-{}-Overlay.png'.format(
        result.cdpro_input, time.strftime("%Y%m%d"))

    fig, ax = plt.subplots(nrows=1, ncols=1)

    if result.continll is True:
        single_line_scatter(
            continll_plot, continll_label, 'CONTINLL Exp', ax
        )

    if result.cdsstr is True:
        single_line_scatter(
            cdsstr_plot, cdsstr_label, 'CDSSTR Exp', ax
        )

    ax.legend()
    plt.savefig(outfile, bbox_inches='tight')

    ss_assignments.columns = ss_col_head
    ss_assignments.to_csv(
        '{}/secondary_structure_summary.csv'.format(cdpro_out_dir)
    )
    logging.info('\n{}\n'.format(ss_assignments))


if __name__ == '__main__':
    main()
