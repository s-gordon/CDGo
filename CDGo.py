#!/usr/bin/env python
# AUTHOR:   Shane Gordon
# ROLE:     TODO (some explanation)
# CREATED:  2015-06-06 13:12:10

import os
import sys
import logging
import argparse
import subprocess
import shutil
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

mpl.pyplot.style.use('ggplot')


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
parser.add_argument('-v', '--verbose',  action="store_true",
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


def check_cmd(cmd):
    try:
        subprocess.check_call(['%s' % cmd], shell=True)
    except subprocess.CalledProcessError:
        pass  # handle errors in the called executable
    except OSError:
        logging.error('Command %s not found' % cmd)
        sys.exit()


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


def single_line_scatter(datafile, fit_label, exp_label, outfile='output.png',
                        flip=True, x_col_name='WaveL', y1_col_name='ExpCD',
                        y2_col_name='CalcCD', xlabel='Wavelength (nm)',
                        ylabel='$\Delta\epsilon$ ($M^{-1}{\cdot}cm^{-1}$)'):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    df = pd.read_table(datafile, skipinitialspace=True, sep=r"\s*",
                       engine='python')
    # Invert data vertically to compensate for CDPro output
    if flip is True:
        df = df.iloc[::-1]
    df.plot(x=x_col_name, y=y1_col_name, style='o', ax=ax, label=exp_label)
    df.plot(x=x_col_name, y=y2_col_name, style='-', ax=ax, label=fit_label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.savefig(outfile, bbox_inches='tight')


def double_line_scatter(datafile1, datafile2, fit_label1, fit_label2, exp_label,
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


def main():

    # Column headers for continll and cdsstr
    continll_headers = ['WaveL', 'ExpCD', 'CalcCD']
    cdsstr_headers = ['WaveL', 'Exptl', 'ReconCD', 'CalcCD']

    cmds = ["wine"]

    for command in cmds:
        check_cmd(command)

    check_dir(result.cdpro_dir)

    # continll_out = cd_output_style("CONTINLL.OUT", "continll.out")
    # cdsstr_out = cd_output_style("CDsstr.out", "cdsstr.out")
    base_dir = os.path.dirname(os.path.realpath(result.cdpro_input))

    script_dir = sys.path[0]

    cdpro_out_dir = "%s/%s-CDPro" % (base_dir, result.cdpro_input)
    delete_dir(cdpro_out_dir)
    logging.debug('Processing %s into %s' % (result.cdpro_input, cdpro_out_dir))
    subprocess.call(
        ['%s/GenerateCDProInput < "%s" >| input' % (script_dir,
                                                    result.cdpro_input)],
        shell=True)
    shutil.copy("input", "%s/input" % (result.cdpro_dir))
    os.chdir(result.cdpro_dir)
    # for ibasis in range(1, 11):
    for ibasis in range(1, 2):
        logging.info('ibasis %s', ibasis)
        subprocess.call(["sed -i '/PRINT/!b;n;c\      0\\t\\t%s' input &&\
                         tr -d '^M' < input >> temp_input && mv temp_input\
                         input" % (ibasis)], shell=True)
        logging.debug('Running CONTINLL')
        subprocess.call(['echo | wine Continll.exe > stdout || echo -n "\
                         (crashed)"'], shell=True)
        continll_outdir = ('%s/continll-ibasis%s' % (cdpro_out_dir, ibasis))
        continll_out = cd_output_style("CONTINLL.OUT", "continll.out",
                                       "continll")
        make_dir(continll_outdir)
        for f in ["CONTIN.CD", "CONTIN.OUT", "%s" % (continll_out), "BASIS.PG",
                  "ProtSS.out", "SUMMARY.PG", "stdout"]:
            print(f, "%s/" % (continll_outdir))
            shutil.move(f, "%s/" % (continll_outdir))
        if os.path.isfile("input"):
            shutil.copy("input", "%s/" % (continll_outdir))
        logging.debug('Running CDSSTR')
        subprocess.call(
            ['echo | wine CDSSTR.EXE > stdout || echo -n " (crashed)"'],
            shell=True)
        cdsstr_outdir = ('%s/cdsstr-ibasis%s' % (cdpro_out_dir, ibasis))
        make_dir(cdsstr_outdir)
        cdsstr_out = cd_output_style("CDsstr.out", "cdsstr.out", "CDSSTR")

        for f in ["reconCD.out", "ProtSS.out", "%s" % (cdsstr_out), "stdout"]:
            shutil.move(f, "%s/" % (cdsstr_outdir))
        if os.path.isfile("input"):
            shutil.copy("input", "%s/" % (cdsstr_outdir))

    os.chdir(cdpro_out_dir)
    for algorithm in ["continll", "cdsstr"]:
        best_rmsd_line = subprocess.check_output(
            'grep -hw RMSD %s-ibasis*/ProtSS.out | sort | head -n1' % (
                algorithm), shell=True)
        best_rmsd = best_rmsd_line[20:24]
        ibasis_f = subprocess.check_output(
            'grep -l "%s" %s-ibasis*/ProtSS.out|tail -n1' % (
                best_rmsd, algorithm), shell=True)
        logging.info('Best %s RMSD: %s' % (algorithm, best_rmsd))
        ibasis_dir = os.path.dirname(os.path.realpath(ibasis_f))
        best_ibasis = ibasis_dir[-1]
        logging.info('Best ibasis for %s: %s' % (algorithm, best_ibasis))

        if algorithm == "continll":
            subprocess.call('echo %s > best-%s' % (best_ibasis, algorithm),
                            shell=True)
            continll_plot = '%s/CONTIN.CD' % ibasis_dir
            continll_label = '{} ibasis {}: RMSD={}'.format(algorithm,
                                                            best_ibasis,
                                                            best_rmsd)
            outfile = 'CDSpec-{}-{}-bestContinll.png'.format(
                result.cdpro_input, time.strftime("%Y%m%d"))
            single_line_scatter(continll_plot, continll_label, 'Exp',
                                outfile=outfile)
        elif algorithm == "cdsstr":
            subprocess.call('echo %s > best-%s' % (best_ibasis, algorithm),
                            shell=True)
            cdsstr_plot = '%s/reconCD.out' % ibasis_dir
            cdsstr_label = '{} ibasis {}: RMSD={}'.format(algorithm,
                                                          best_ibasis,
                                                          best_rmsd)
            outfile = 'CDSpec-{}-{}-bestCDSSTR.png'.format(
                result.cdpro_input, time.strftime("%Y%m%d"))
            single_line_scatter(cdsstr_plot, cdsstr_label, 'Exp',
                                outfile=outfile, x_col_name='WaveL',
                                y1_col_name='Exptl', y2_col_name='CalcCD')

    # Print the matplotlib overlay
    logging.debug('Plotting fit overlays')

    outfile = 'CDSpec-{}-{}-Overlay.png'.format(
        result.cdpro_input, time.strftime("%Y%m%d"))
    double_line_scatter(continll_plot, cdsstr_plot, continll_label,
                        cdsstr_label, exp_label='Exp',
                        df1_headers=continll_headers,
                        df2_headers=cdsstr_headers,
                        outfile=outfile)

if __name__ == '__main__':
    main()
