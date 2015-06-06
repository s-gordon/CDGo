#!/usr/bin/env python
# AUTHOR:   Shane Gordon
# FILE:     RunAlgorithms.py
# ROLE:     TODO (some explanation)
# CREATED:  2015-06-06 13:12:10
# MODIFIED: 2015-06-06 14:29:27

import os
import sys
import logging
import argparse
import subprocess

# Logging
logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.DEBUG)

# Argparse
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


parser=MyParser(description='Run CDPro automatically.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-C', action="store", dest="cdpro_dir", 
        default="/Users/sgordon/.wine/drive_c/Program Files/CDPro", 
        help="CDPro executable directory")
parser.add_argument('-i', action="store", dest="cdpro_input", 
        required=True, help="CDPro executable directory")

result = parser.parse_args()

def check_dir(dir):
    """
    Check whether directory dir exists.
    If true. continue. Else exit.
    """
    if not os.path.isdir(dir):
        logging.error('Path %s not found', dir)
        logging.error('Aborting')
        sys.exit()

def check_cmd(cmd):
    try:
        subprocess.check_call(['%s' % cmd])
    except subprocess.CalledProcessError:
        pass # handle errors in the called executable
    except OSError:
        logging.error('Command %s not found' % cmd)
        sys.exit()

cmd_exists("wine")
