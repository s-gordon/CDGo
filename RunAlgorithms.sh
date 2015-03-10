#!/bin/bash
#
# Call CDPro executables, somewhat more nicely.
#
# Before calling this script, convert CD spec output file to Delta epsilon with: 
#
# ``CDToGnuplot -r <# residues> -m <MW (Da)> -c <conc. (mg/ml)> [-b <buffer file>] <InFile   >OutFile''
#
# Calls ``GenerateCDProInput'' to make the CDPro input file (this would ordinarily have been done by CRDATA.EXE)
#
# CDPRO_DIR must be set to the location of the CDPro executables.
#    -- At some point i should change this to look in $PATH.
#
# Requires perl, gnuplot, wine, CDPro

# ERROR REPORTING ------------------------------------------------------------- {{{

# Taken from <http://www.linuxcommand.org/wss0150.php>

# A slicker error handling routine

# I put a variable in my scripts named PROGNAME which
# holds the name of the program being run.  You can get this
# value from the first item on the command line ($0).

PROGNAME=$(basename $0)

function error_exit
{

# ----------------------------------------------------------------
# Function for exit due to fatal program error
#   Accepts 1 argument:
#     string containing descriptive error message
# ----------------------------------------------------------------
  echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
  exit 1
}

# Example call of the error_exit function.  Note the inclusion
# of the LINENO environment variable.  It contains the current
# line number.

# echo "Example of error with line number and message"
# error_exit "$LINENO: An error has occurred."

function check_dir_exists
{
  if [ ! -d "$1" ]; then
    error_exit "$LINENO: An error has occurred. Directory $1 not found."
  fi
}

function check_file_exists
{
  if [ ! -d "$1" ]; then
    error_exit "$LINENO: An error has occurred. File $1 not found."
  fi
}

# }}}

CDPRO_DIR="/home/sgordon/.wine/drive_c/Program Files/CDPro"
check_dir_exists "$CDPRO_DIR"

#Set this if you get ``run-detectors: unable to find an interpreter for Continll.exe'' etc
#WINE=""
WINE="wine"

# Output filename case:
# I've had systems that produced either uppercase, or lowercase.
# possibly depending on whether the install was under ~/.wine (ext3/4)
OUTPUT_CASE=upper

if [ "$OUTPUT_CASE" = "upper" ]; then
  CONTINLL_OUT="CONTINLL.OUT"
  SELCON3_OUT="SELCON3.OUT"
  CDSSTR_OUT="CDsstr.out"
elif [ "$OUTPUT_CASE" = "lower" ]; then
  CONTINLL_OUT="continll.out"
  SELCON3_OUT="selcon3.out"
  CDSSTR_OUT="cdsstr.out"
else
  echo "$0: i don't understand OUTPUT_CASE='$OUTPUT_CASE'"
fi

if [ "$#" == "0" ] 
then
  echo "Usage: $0 <CDSpec-data-files>"
fi

# $0 substitutes for the name of the script being executed
SCRIPT_DIR=`dirname $0`/

GNUPLOT_BASEFILE="$SCRIPT_DIR/basefile_gnuplot.gpi"
check_file_exists $GNUPLOT_BASEFILE

for DataFile in "$@"; do
  DataDir=`basename "${DataFile}"`-CDPro
  mkdir -p "$DataDir"
  echo "Processing ${DataFile} into $DataDir:"
  ${SCRIPT_DIR}GenerateCDProInput < "${DataFile}" >| input
  cp input "$CDPRO_DIR/"
  cd "$CDPRO_DIR/"
  pwd

  for i in {1..10}; do  # (ibasese)
    echo -n "ibasis $i ";  
    perl -pni -e 's/^(\s+\d\s+)\d+()$/${1}'$i'${2}/' input ;
    echo -n "continll"   
    echo | $WINE Continll.exe > stdout || echo -n " (crashed)"
    mkdir -p "$OLDPWD/$DataDir/continll-ibasis$i"
    mv CONTIN.CD CONTIN.OUT $CONTINLL_OUT BASIS.PG ProtSS.out SUMMARY.PG stdout "$OLDPWD/$DataDir/continll-ibasis$i" 
    cp input "$OLDPWD/$DataDir/continll-ibasis$i" 

    echo -n ", selcon3"
    echo | $WINE SELCON3.EXE > stdout 
    mkdir -p "$OLDPWD/$DataDir/selcon3-ibasis$i"

    if grep -q 'Program CRASHED -- No SOLUTIONS were Obtained' $SELCON3_OUT; then
      echo -n " (crashed)"; 
    else
      if [ -f ProtSS.out ]; then
        mv ProtSS.out "$OLDPWD/$DataDir/selcon3-ibasis$i"
      else
        echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
        exit 1
      fi
    fi
    mv CalcCD.OUT $SELCON3_OUT stdout "$OLDPWD/$DataDir/selcon3-ibasis$i"
    cp input "$OLDPWD/$DataDir/selcon3-ibasis$i"
    echo -n , cdsstr
    echo | $WINE CDSSTR.EXE > stdout || echo -n " (crashed)"; 

    mkdir -p "$OLDPWD/$DataDir/cdsstr-ibasis$i"
    mv reconCD.out ProtSS.out $CDSSTR_OUT stdout "$OLDPWD/$DataDir/cdsstr-ibasis$i"
    cp input "$OLDPWD/$DataDir/cdsstr-ibasis$i"
    echo .
  done

  cd "$OLDPWD"
  cd "$DataDir/"

  #
  # What are the best fits ?
  #
  # This works ok, but doesn't try to resolve situations 
  # where multiple ibasese have the same RMSD.
  #
  plotlines=""
  for i in continll selcon3 cdsstr; do
    BEST_RMSD_LINE=`/bin/grep -hw RMSD $i-ibasis*/ProtSS.out | sort | head -n1`
    BEST_RMSD=`echo ${BEST_RMSD_LINE##*RMSD(Exp-Calc): }`
    BEST_RMSD=${BEST_RMSD%%?}

    ibasis_filename=`grep -l  "$BEST_RMSD" $i-ibasis*/ProtSS.out|tail -n1` # only return  one 
    echo $ibasis_dirname
    ibasis_dirname=`dirname ${ibasis_filename}`
    ibasis=${ibasis_dirname##*-ibasis}

    echo "Best $i is RMSD: ${BEST_RMSD} (ibasis $ibasis)"
    grep -B1 ^Frac "$ibasis_dirname/stdout"
    grep -l  "$BEST_RMSD" $i-ibasis*/ProtSS.out

    if [ "$i" = "continll" ]; then
      echo $ibasis > best-continll
      ContinllPlot=", '$ibasis_dirname/CONTIN.CD' index 0 using 1:3 w l smooth csplines title \"$i ibasis $ibasis: RMSD=${BEST_RMSD}\""
    elif [ "$i" = "selcon3" ]; then
      echo $ibasis > best-selcon3
      Selcon3Plot=", '$ibasis_dirname/CalcCD.OUT' index 0 using 1:3 w l smooth csplines title \"$i ibasis $ibasis: RMSD=${BEST_RMSD}\"" 
    elif  [ "$i" = "cdsstr" ]; then
      echo $ibasis > best-cdsstr
      CdsstrPlot=", '$ibasis_dirname/reconCD.out' index 0 using 1:4 w l smooth csplines title \"$i ibasis $ibasis: RMSD=${BEST_RMSD}\""
    fi
  done

  # Print the gnuplot file:
  gnuplot -e "Assay=\"CDSpec-$DataFile-`date +\"%Y%m%d\"`-Overlay\"" \
          -e "DataFile=\"../$DataFile\"" \
          -e "set title \"CD Spec ($DataFile): Absorbance Vs Wavelength\"" \
          $GNUPLOT_BASEFILE \
          -e "plot DataFile index 0 using 1:2 w p pt 7 ps 0.4 lc rgb \"black\" notitle $ContinllPlot $Selcon3Plot $CdsstrPlot" \

  #Print the best-continll file:
  gnuplot -e "Assay=\"CDSpec-$DataFile-`date +\"%Y%m%d\"`-bestContinll\"" \
          -e "DataFile=\"../$DataFile\"" \
          -e "set title \"CD Spec ($DataFile): Absorbance Vs Wavelength\"" \
          $GNUPLOT_BASEFILE \
          -e "plot DataFile index 0 using 1:2 notitle $ContinllPlot"

  #Print the best-Selcon3 file:
  gnuplot -e "Assay=\"CDSpec-$DataFile-`date +\"%Y%m%d\"`-bestSelcon3\"" \
          -e "DataFile=\"../$DataFile\"" \
          -e "set title \"CD Spec ($DataFile): Absorbance Vs Wavelength\"" \
          $GNUPLOT_BASEFILE \
          -e "plot DataFile index 0 using 1:2 notitle $Selcon3Plot"

  #Print the best-CdsstrPlot file:
  gnuplot -e "Assay=\"CDSpec-$DataFile-`date +\"%Y%m%d\"`-bestCdsstrPlot\"" \
          -e "DataFile=\"../$DataFile\"" \
          -e "set title \"CD Spec ($DataFile): Absorbance Vs Wavelength\"" \
          $GNUPLOT_BASEFILE \
          -e "plot DataFile index 0 using 1:2 notitle $CdsstrPlot"
    cd ..

done
