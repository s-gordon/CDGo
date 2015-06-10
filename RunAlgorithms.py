#!/usr/bin/env python
# AUTHOR:   Shane Gordon
# FILE:     RunAlgorithms.py
# ROLE:     TODO (some explanation)
# CREATED:  2015-06-06 13:12:10
# MODIFIED: 2015-06-10 16:54:30

import os
import sys
import logging
import argparse
import subprocess
import shutil
import time

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

def delete_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def check_cmd(cmd):
    try:
        subprocess.check_call(['%s' % cmd])
    except subprocess.CalledProcessError:
        pass # handle errors in the called executable
    except OSError:
        logging.error('Command %s not found' % cmd)
        sys.exit()

def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

cmds = ["wine"]

for command in cmds:
	check_cmd(command)

check_dir(result.cdpro_dir)

continll_out = "CONTINLL.OUT"
selcon3_out = "SELCON3.OUT"
cdsstr_out = "CDsstr.out"
base_dir = os.path.dirname(os.path.realpath(result.cdpro_input))

script_dir = sys.path[0]
gnuplot_basefile = "%s/basefile_gnuplot.gpi" % (script_dir)

cdpro_out_dir = "%s/%s-CDPro" % (base_dir, result.cdpro_input)
delete_dir(cdpro_out_dir)
logging.info('Processing %s into %s' % (result.cdpro_input, cdpro_out_dir))
subprocess.call(['%s/GenerateCDProInput < "%s" >| input' % (script_dir, result.cdpro_input)], shell=True)
shutil.copy("input", "%s/input" % (result.cdpro_dir))
os.chdir(result.cdpro_dir)
for ibasis in range(1,11):
	logging.info('ibasis %s', ibasis)
	subprocess.call(["sed -i '/PRINT/!b;n;c\      0\\t\\t%s' input && tr -d '^M' < input >> temp_input && mv temp_input input" % (ibasis)], shell=True)
	# subprocess.call(["perl -pni -e 's/^(\s+\d\s+)\d+(^M)$/${1}'%s'${2}/' input" % (ibasis)], shell=True)
	# print("perl -pni -e 's/^(\s+\d\s+)\d+(^M)$/${1}'%s'${2}/' input" % (ibasis))
	logging.info('Running CONTINLL')
	subprocess.call(['echo | wine Continll.exe > stdout || echo -n " (crashed)"'], shell=True)
	continll_outdir = ('%s/continll-ibasis%s' % (cdpro_out_dir, ibasis))
	make_dir(continll_outdir)
	for f in ["CONTIN.CD", "CONTIN.OUT", "%s" % (continll_out), "BASIS.PG", "ProtSS.out", "SUMMARY.PG", "stdout"]:
		shutil.move(f, "%s/" % (continll_outdir))
	if os.path.isfile("input"):
		shutil.copy("input", "%s/" % (continll_outdir))
	logging.info('Running CDSSTR')
	subprocess.call(['echo | wine CDSSTR.EXE > stdout || echo -n " (crashed)"'], shell=True)
	cdsstr_outdir = ('%s/cdsstr-ibasis%s' % (cdpro_out_dir, ibasis))
	make_dir(cdsstr_outdir)
	for f in ["reconCD.out", "ProtSS.out", "%s" % (cdsstr_out), "stdout"]:
		shutil.move(f, "%s/" % (cdsstr_outdir))
	if os.path.isfile("input"):
		shutil.copy("input", "%s/" % (cdsstr_outdir))
	logging.info('Running SELCON')
	subprocess.call(['echo | wine SELCON3.EXE > stdout'], shell=True)
	
	selcon3_outdir = ('%s/selcon3-ibasis%s' % (cdpro_out_dir, ibasis))
	selcon_quality = 1
	with open('%s' % (selcon3_out)) as fp:
		for line in fp:
			if line.find('Program CRASHED -- No SOLUTIONS were Obtained') == 1:
				logging.error('SELCON3 crashed')
				selcon_quality = 0

	if selcon_quality != 0:
		make_dir(selcon3_outdir)
		for f in ["CalcCD.OUT", "ProtSS.out", "%s" % (selcon3_out), "stdout"]:
			shutil.move(f, "%s/" % (selcon3_outdir))
		if os.path.isfile("input"):
			shutil.copy("input", "%s/" % (selcon3_outdir))

os.chdir(cdpro_out_dir)
for algorithm in ["continll", "cdsstr", "selcon3"]:
    best_rmsd_line = subprocess.check_output('grep -hw RMSD %s-ibasis*/ProtSS.out | sort | head -n1' % (algorithm),shell=True)
    # best_rmsd_line = subprocess.check_output('echo `grep -hw RMSD %s-ibasis*/ProtSS.out | sort | head -n1`' % (algorithm),shell=True)
    best_rmsd = best_rmsd_line[20:24]
    ibasis_f = subprocess.check_output('grep -l "%s" %s-ibasis*/ProtSS.out|tail -n1' % (best_rmsd, algorithm), shell=True)
    logging.info('Best %s RMSD: %s' % (algorithm, best_rmsd))
    ibasis_dir = os.path.dirname(os.path.realpath(ibasis_f))
    best_ibasis = ibasis_dir[-1]
    logging.info('Best ibasis for %s: %s' % (algorithm, best_ibasis))

    if algorithm == "continll":
        subprocess.call('echo %s > best-%s' % (best_ibasis, algorithm), shell=True)
        continll_plot_cmd = "\'%s/CONTIN.CD\' index 0 using 1:3 w l smooth csplines title \'%s ibasis %s: RMSD=%s\'" % (ibasis_dir, algorithm, best_ibasis, best_rmsd)
        subprocess.call('gnuplot -e "Assay=\'CDSpec-%s-%s-bestContinll\'" -e "DataFile=\'../%s\'" -e "set title \'CD Spec (%s): Absorbance Vs Wavelength\'" "%s"  -e "plot DataFile index 0 using 1:2 w p pt 7 ps 0.4 lc rgb \'black\' notitle, %s"' % (result.cdpro_input, time.strftime("%Y%m%d"), result.cdpro_input, result.cdpro_input, gnuplot_basefile, continll_plot_cmd), shell=True)
        # subprocess.call('gnuplot -e "Assay=\'CDSpec-%s-%s-bestContinll\'" -e "DataFile=\'../%s\'" -e "set title \'CD Spec (%s): Absorbance Vs Wavelength\'" "%s" -e "\"plot DataFile index 0 using 1:2 w p pt 7 ps 0.4 lc rgb \'black\' notitle, %s"' % (result.cdpro_input, time.strftime("%Y%m%d"), result.cdpro_input, result.cdpro_input, gnuplot_basefile, continll_plot_cmd))
    elif algorithm == "cdsstr":
        subprocess.call('echo %s > best-%s' % (best_ibasis, algorithm), shell=True)
        cdsstr_plot_cmd = "\'%s/reconCD.out\' index 0 using 1:3 w l smooth csplines title \'%s ibasis %s: RMSD= %s\'" % (ibasis_dir, algorithm, best_ibasis, best_rmsd)
        subprocess.call('gnuplot -e "Assay=\'CDSpec-%s-%s-bestCDsstr\'" -e "DataFile=\'../%s\'" -e "set title \'CD Spec (%s): Absorbance Vs Wavelength\'" "%s"  -e "plot DataFile index 0 using 1:2 w p pt 7 ps 0.4 lc rgb \'black\' notitle, %s"' % (result.cdpro_input, time.strftime("%Y%m%d"), result.cdpro_input, result.cdpro_input, gnuplot_basefile, cdsstr_plot_cmd), shell=True)
    elif algorithm == "selcon3":
        subprocess.call('echo %s > best-%s' % (best_ibasis, algorithm), shell=True)
        selcon3_plot_cmd = "\'%s/CalcCD.OUT\' index 0 using 1:3 w l smooth csplines title \'%s ibasis %s: RMSD= %s\'" % (ibasis_dir, algorithm, best_ibasis, best_rmsd)
        subprocess.call('gnuplot -e "Assay=\'CDSpec-%s-%s-bestSelcon3\'" -e "DataFile=\'../%s\'" -e "set title \'CD Spec (%s): Absorbance Vs Wavelength\'" "%s"  -e "plot DataFile index 0 using 1:2 w p pt 7 ps 0.4 lc rgb \'black\' notitle, %s"' % (result.cdpro_input, time.strftime("%Y%m%d"), result.cdpro_input, result.cdpro_input, gnuplot_basefile, selcon3_plot_cmd), shell=True)

# Print the gnuplot overlay
logging.info('Plotting fit overlays')
subprocess.call('gnuplot -e "Assay=\'CDSpec-%s-%s-Overlay\'" -e "DataFile=\'../%s\'" -e "set title \'CD Spec (%s): Absorbance Vs Wavelength\'" "%s"  -e "plot DataFile index 0 using 1:2 w p pt 7 ps 0.4 lc rgb \'black\' notitle, %s, %s, %s"' % (result.cdpro_input, time.strftime("%Y%m%d"), result.cdpro_input, result.cdpro_input, gnuplot_basefile, continll_plot_cmd, cdsstr_plot_cmd, selcon3_plot_cmd), shell=True)

