#!/usr/bin/env python

import logging
import ntpath
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
from datetime import datetime
from multiprocessing import Pool

import matplotlib.pyplot as plt
import more_itertools
import pandas as pd
import seaborn as sns
from tabulate import tabulate

from .init_logging import logfile
from .io import AvivReader, cdpro_input_header
from .mathops import r_squared, rms_error, sum_squares_residuals
from .readers import read_cdsstr, read_continll, read_protss

logger = logging.getLogger(__name__)


def cdproalg(src, ibasis, odir, continll, cdsstr, input_head, input_body):
    df = pd.DataFrame()
    tmpdir = tempfile.mkdtemp()
    inp_conf = os.path.join(tmpdir, 'input')
    try:
        for f in os.listdir(os.path.join(src)):
            abs_fname = os.path.join(src, f)
            if os.path.isfile(abs_fname):
                shutil.copy(abs_fname, tmpdir)
        cdpro_input_writer(input_body, input_head, fname=inp_conf)
        replace_input(inp_conf, inp_conf, ibasis)
        logger.info('ibasis %s', ibasis)
        if continll is True:
            df = df.append(run_continll(ibasis, odir, tmpdir))
        if cdsstr is True:
            df = df.append(run_cdsstr(ibasis, odir, tmpdir))
    finally:
        shutil.rmtree(tmpdir)
    return df


def print_citation_info():
    [logger.info(line) for line in notes()]


def prettify_pandas_table(df):
    return tabulate(df, headers='keys', tablefmt='psql')


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


def cdpro_input_footer():
    """
    :returns: Multiline string mimicking cdpro input footer

    """

    footer = ("#                                                  \n"
              "#  IGuess  Str1   Str2   Str3   Str4   Str5    Str6\n"
              "        0                                          \n")
    return footer


def notes():
    head = """\
        CDGo is research software. If you use CDGo in your research, please
        acknowledge it appropriately. E.g.: \"...using the software package
        CDPro (Sreerama and Woody, 2000,) as (available from
        https://github.com/s-gordon/CDGo)\"
    """
    body_first = """\
        Any use of CDGo in research should also cite the software package
        CDPro (found http://sites.bmb.colostate.edu/sreeram/CDPro/):
        """
    body_second = """\
        Sreerama, N., & Woody, R. W. (2000). Estimation of protein
        secondary structure from circular dichroism spectra: comparison of
        CONTIN, SELCON, and CDSSTR methods with an expanded reference set.
        Analytical biochemistry, 287(2), 252-260.
        """
    foot = """
        Use of individual protein reference databases should also be credited
        appropriately. For a full listing of each database and the
        appropriate citation, please use the following link:
        http://sites.bmb.colostate.edu/sreeram/CDPro/
        """
    n = textwrap.wrap(textwrap.dedent(head), 80) + [""] + \
        textwrap.wrap(textwrap.dedent(body_first), 80) + [""] + \
        textwrap.wrap(textwrap.dedent(body_second), 80) + [""] + \
        textwrap.wrap(textwrap.dedent(foot), 80)
    return n


def check_cdpro_install(d):
    """
    :d: cdpro installation path
    :returns: TODO

    """
    # define essential files within cdpro installation to check
    ef = [
        "BASIS", "BASISPG.SMP", "BASIS.SMP", "betaalfa", "betaplus",
        "betaslsh", "CALCCD.SMP", "CDDATA.23", "CDDATA.29", "CDDATA.37",
        "CDDATA.42", "CDDATA.43", "CDDATA.48", "CDDATA.50", "CDDATA.56",
        "CDDATA.AA", "CDDATA.AB", "CDDATA.BB", "CDDATA.CA", "CDDATA.DN",
        "CDDATA.P2", "CRDATA.EXE", "CDSSTR.EXE", "CDsstr.SMP", "Contincd.smp",
        "Continll.exe", "Continll.SMP", "CLUSTER.EXE", "CLUSTER.smp",
        "CLUSTMP", "dentalfa", "dentbeta", "dentplus", "dentslsh", "SSDATA.23",
        "SSDATA.29", "SSDATA.37", "SSDATA.42", "SSDATA.43", "SSDATA.48",
        "SSDATA.50", "SSDATA.56", "SSDATA.AA", "SSDATA.AB", "SSDATA.BB",
        "SSDATA.CA", "SSDATA.DN", "SSDATA.P2", "plusalfa", "ProtSS.SMP",
        "SELCON3.EXE", "selcon3.out", "Selcon3.SMP", "slshalfa", "slshplus"
    ]
    present = True
    for f in ef:
        if os.path.isfile(os.path.join(d, f)) is not True:
            logger.info("File {} not found in CDPro directory {}.".format(
                f, d))
            if present is not False:
                present = False
    return present


def check_dir(dir):
    """
    Check whether directory dir exists.
    If true continue. Else exit.
    """
    if not os.path.isdir(dir):
        logger.error('Path %s not found', dir)
        logger.error('Aborting')
        sys.exit()


def delete_dir(dir):
    """
    Check whether directory dir exists.
    If true delete and remake.
    """
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


def check_wine():
    """Verify that program is in path
    returns: True if wine is in path
    """
    logger.debug('Checking for \"{}\"'.format("wine"))
    try:
        subprocess.check_call(['wine --version>/dev/null'], shell=True)
        return True
    except subprocess.CalledProcessError:
        logger.error("\"wine\" is not in PATH. Please install and try again.")
        return False


def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def cd_output_style(style_1, style_2, algorithm):
    if os.path.isfile(style_1) is True:
        logger.debug('{algorithm} format is {style}'.format(
            algorithm=algorithm, style=style_1))
        return style_1
    elif os.path.isfile(style_2) is True:
        logger.debug('{algorithm} format is {style}'.format(
            algorithm=algorithm, style=style_2))
        return style_2
    else:
        sys.exit(2)


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


def date_string():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def unique_dir(s):
    """
    s: string to append
    """
    if os.path.exists(s):
        return "{}-{}".format(s, date_string())
    else:
        return s


def run_continll(ibasis_idx, opath, wd):
    """
    if continll switch is True, run the continll algorithm and pull
    secondary structure assignments

    ibasisID: ibasis index [1-10] to use with continll
    returns:
    """
    if find_platform() != "Windows":
        continll_cmd = [
            "echo | WINEDEBUG=-all wine Continll.exe " +
            ">stdout || echo -n \"(crashed)\""
        ]
    else:
        continll_cmd = ["echo", ".", "|", "Continll.exe", ">stdout"]

    continll_outdir = ('{}/continll-ibasis{}'.format(opath, ibasis_idx))

    # if ProtSS found, remove
    if os.path.isfile(os.path.join(wd, "ProtSS.out")):
        os.remove(os.path.join(wd, "ProtSS.out"))
        logger.info("{} found in {}. Removing.".format("ProtSS.out", wd))

    logger.info('Running CONTINLL')
    subprocess.call(continll_cmd, shell=True, cwd=wd)
    continll_out = cd_output_style(os.path.join(wd, "CONTINLL.OUT"),
                                   os.path.join(wd, "continll.out"),
                                   os.path.join(wd, "continll"))

    logger.debug("Making directory {}".format(continll_outdir))
    make_dir(continll_outdir)
    for f in [
            os.path.join(wd, "CONTIN.CD"),
            os.path.join(wd, "CONTIN.OUT"),
            os.path.join(wd, continll_out),
            os.path.join(wd, "BASIS.PG"),
            os.path.join(wd, "ProtSS.out"),
            os.path.join(wd, "SUMMARY.PG"),
            os.path.join(wd, "stdout")
    ]:
        shutil.copy(f, "{}/".format(continll_outdir))
        logger.debug("Moving {} to {}".format(f, continll_outdir))

    if os.path.isfile(os.path.join(wd, "input")):
        shutil.copy(os.path.join(wd, "input"), "{}/".format(continll_outdir))
        logger.debug("Moving input to {}".format(continll_outdir))
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
        db, 'continll', ss['ahelix'], ss['bstrand'], ss['turn'], ss['unord'],
        rmsd, ss_res, r2
    ]],
                      index=[ibasis_idx])
    # append fit values and stats to dataframe
    return df


def run_cdsstr(ibasis_idx, opath, wd):
    """
    if cdsstr switch is True, run the cdsstr algorithm and pull
    secondary structure assignments

    ibasisID: ibasis index [1-10]
    returns:
    """
    if find_platform() != "Windows":
        cdsstr_cmd = [
            "echo | WINEDEBUG=-all wine CDSSTR.EXE " +
            ">stdout || echo -n \"(crashed)\""
        ]
    else:
        cdsstr_cmd = ["echo", ".", "|", "CDSSTR.EXE", ">stdout"]
    cdsstr_outdir = ('{}/cdsstr-ibasis{}'.format(opath, ibasis_idx))

    # if ProtSS found, remove
    if os.path.isfile(os.path.join(wd, "ProtSS.out")):
        os.remove(os.path.join(wd, "ProtSS.out"))
        logger.debug("{} found in {}. Removing.".format("ProtSS.out", wd))

    logger.info('Running CDSSTR')
    subprocess.call(cdsstr_cmd, shell=True, cwd=wd)
    cdsstr_out = cd_output_style(os.path.join(wd, "CDsstr.out"),
                                 os.path.join(wd, "cdsstr.out"),
                                 os.path.join(wd, "CDSSTR"))

    logger.debug("Making directory {}".format(cdsstr_outdir))
    make_dir(cdsstr_outdir)
    for f in [
            os.path.join(wd, "reconCD.out"),
            os.path.join(wd, "ProtSS.out"),
            os.path.join(wd, cdsstr_out),
            os.path.join(wd, "stdout")
    ]:
        shutil.copy(f, "{}/".format(cdsstr_outdir))
        logger.debug("Moving {} to {}".format(f, cdsstr_outdir))

    if os.path.isfile(os.path.join(wd, "input")):
        shutil.copy(os.path.join(wd, "input"), "{}/".format(cdsstr_outdir))
        logger.debug("Moving input to {}".format(cdsstr_outdir))
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
        db, 'cdsstr', ss['ahelix'], ss['bstrand'], ss['turn'], ss['unord'],
        rmsd, ss_res, r2
    ]],
                      index=[ibasis_idx])
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
        logger.error("Unknown algorithm reference {} supplied.".format(col))
        sys.exit(2)
    # select only rows with alg value equal to col
    df = df.loc[df['alg'] == col]
    # select row with lowest rmsd value as top
    top = df.loc[df['rmsd'].idxmin()]
    logger.info('best ibasis for {a}: {i}'.format(a=col, i=top.name))
    # full file name and path for plot file
    fname = '{a}-ibasis{i}/{f}'.format(a=col, i=top.name, f=fit_fname)
    # plot label for matplotlib
    flab = '{alg} ibasis {ib} (RMSD: {rmsd})'.format(alg=col,
                                                     ib=top.name,
                                                     rmsd=top['rmsd'])
    # plot on supplied axis
    single_line_scatter(fname, flab, ax)


def find_platform():
    return platform.system()


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


def run(ps,
        bs,
        cdpro_install_path,
        mw,
        pl,
        number_residues,
        conc,
        db,
        continll=False,
        cdsstr=False,
        parallel_execution=True):
    """
    ps: protein spectrum file, in Aviv format
    bs: buffer spectrum file, in Aviv format
    mw: protein molecular weight (in Dalton)
    pl: cuvette pathlength (in cm)
    number_residues: number of residues within protein. Number of peptide
                     bonds is equal to one less than this number
    conc: protein concentration (in g/L)
    db: ibasis range [1-10]
    continll: use continll algorithm?
    cdsstr: use cdsstr algorithm?
    """
    print_citation_info()

    # for non-windows systems, check that wine is installed and in PATH
    # if not, exit and print error
    if find_platform() != "Windows":
        if check_wine() is False:
            logger.error("\"wine\" not found in PATH. Cannot continue.")
            logger.error("Please install wine to PATH and try again.")
            return

    # read in data files for dataset (dat) and reference buffer for subtraction
    # (buf)
    spectra = AvivReader(ps, bs, mw, number_residues, conc, pl)
    spectra.subBufferSpectrum()
    spectra.mreToEps()

    logger.info("Replicates in sample dataset: {}".format(
        spectra.protSpectrum.nreps))
    logger.info("Replicates in reference dataset: {}".format(
        spectra.bufferSpectrum.nreps))

    head = cdpro_input_header(spectra.max, spectra.min)
    body = list(more_itertools.chunked(spectra.epsilon_ints["ave"], 10))
    # cdpro_input_writer(body, head)
    check_dir(cdpro_install_path)
    base_dir = os.path.dirname(os.path.realpath(ps))
    ps_name_stripped = ntpath.basename(ps)

    # set base name for output folder to place generated files
    # if folder exists, append string with date to create unique directory
    odir = unique_dir("{}/{}-CDPro".format(base_dir, ps_name_stripped))
    make_dir(odir)

    logger.debug('Processing {} into {}'.format(ps, odir))
    # log args into to logfile lname
    lname = '{p}/input.log'.format(p=odir)
    logfile(lname,
            reps_sample=spectra.protSpectrum.nreps,
            reps_reference=spectra.bufferSpectrum.nreps,
            cdpro_path=cdpro_install_path,
            protein_spectrum_input_file=ps,
            buffer_spectrum_input_file=bs,
            protein_mw=mw,
            cuvette_pathlength=pl,
            number_residues=number_residues,
            protein_concentration=conc,
            ibasis_range=[i for i in db],
            CONTINLL=continll,
            CDSSTR=cdsstr)
    # try:
    #     shutil.copy("input", "{}/input".format(cdpro_install_path))
    # except shutil.SameFileError:
    #     logger.warning("CDPro input and destination input are identical")
    #     logger.warning("Continuing.")

    ss_col_head = [
        'ibasis', 'alg', 'ahelix', 'bstrand', 'turn', 'unord', 'rmsd',
        'ss_res', 'r2'
    ]

    ibasis_list = [i for i in db]

    # optionally, execute continll and cdsstr concurrently on multiple cores
    # faster execution on modern multicore machines
    if parallel_execution is True:
        p = Pool(os.cpu_count())

        cdpro_generator = ((cdpro_install_path, i, odir, continll, cdsstr,
                            head, body) for i in ibasis_list)
        ss_assign = pd.concat(p.starmap(cdproalg, cdpro_generator))
        p.close()
        p.join()
    else:
        ss_assign = pd.DataFrame()
        for ibasis in ibasis_list:
            ss_assign = ss_assign.append(
                cdproalg(cdpro_install_path, ibasis, odir, continll, cdsstr,
                         head, body))
            logger.info('ibasis %s', ibasis)

    os.chdir(odir)

    set_style()

    # assign column headings
    ss_assign.columns = ss_col_head

    # round floats to 3 decimal places for certain columns
    ss_assign.rmsd = ss_assign.rmsd.round(3)
    ss_assign.ss_res = ss_assign.ss_res.round(3)
    ss_assign.r2 = ss_assign.r2.round(3)

    # Print the matplotlib overlay
    logger.debug('Plotting fit overlays')
    outfile = '{}/CDSpec-{}-{}-Overlay.png'.format(odir, ntpath.basename(ps),
                                                   time.strftime("%Y%m%d"))

    ax = plt.subplots(nrows=1, ncols=1)[1]

    if continll is True:
        best_fit(ss_assign, 'continll', ax)

    if cdsstr is True:
        best_fit(ss_assign, 'cdsstr', ax)

    spectra.epsilon.plot.scatter(ax=ax,
                                 x="wl",
                                 y="ave",
                                 yerr="std",
                                 label="exp",
                                 color="black")
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Δε ($M^{-1}·cm^{-1}$)')
    ax.legend()
    plt.savefig(outfile, bbox_inches='tight')

    # save epsilon-format exp data to csv file for later plotting
    spectra.epsilon.to_csv('{}/exp_data_delta_epsilon.csv'.format(odir))

    ss_assign.to_csv('{}/secondary_structure_summary.csv'.format(odir))
    logger.info('\n{}\n'.format(prettify_pandas_table(ss_assign)))
