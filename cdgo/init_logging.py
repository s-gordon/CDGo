#!/usr/bin/env python

import logging
import textwrap
from cdgo import __version__ as cdgoversion

logging.basicConfig(format='%(levelname)s:\t%(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)
"""
If verbosity set, change logging to debug.
Else leave at info
"""


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


def set_log_level(args, log):
    """Set log level for output from argparse input

    args: argparse parser including "verbose" arg
    log: logger from logging
    returns:

    """

    if not args.verbose:
        log.setLevel(logging.WARNING)
    elif args.verbose == 1:
        log.setLevel(logging.INFO)
    elif args.verbose >= 2:
        log.setLevel(logging.DEBUG)


def logfile(fname, **kwargs):
    """Docstring for logfile
    :fname: output logfile name
    :parser: argparse parser object

    :returns: None
    """
    with open(fname, 'w') as f:
        f.write(
            "Logfile for CDGo. See below details of the arguments provided." +
            "\n\n")
        # f.write(notes + "\n\n")
        # f.write('Date: {}\n'.format(now.strftime("%Y-%m-%d %H:%M")))
        f.write('CDGo Version: {}\n'.format(cdgoversion))
        [f.write(i + "\n") for i in notes()]
        for key, value in list(kwargs.items()):
            f.write('{}: {}\n'.format(key, value))
