#!/usr/bin/env python

import argparse
import logging
import re
import sys
from datetime import datetime

from .init_logging import set_log_level
from .core import run

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logger.addHandler(ch)

now = datetime.now()


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
                    action="count",
                    help="""
                    Increase verbosity. Repeat up to two times for increased
                    output (INFO, DEBUG)
                    """)


def main():
    """Docstring for main

    :returns: None
    """
    args = parser.parse_args()
    set_log_level(args, logger)
    run(args.cdpro_input,
        args.buffer,
        args.cdpro_dir,
        args.mol_weight,
        args.pathlength,
        args.number_residues,
        args.concentration,
        args.db_range,
        continll=args.continll,
        cdsstr=args.cdsstr)


if __name__ == '__main__':
    main()
