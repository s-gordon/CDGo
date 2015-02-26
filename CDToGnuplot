#!/usr/bin/perl
#
# Read an Aviv output file from stdin.
# Output a two column stream (wavelength	delta e).
#
# Automatically discard values with dynode above 600.
#    -- checking the error would probably be better.
# Number of residues, molecular weight and concentration are required to calculate Delta e.
# Buffer data is subtracted if specified   
#  

use Getopt::Std;

# This file documents Tie::File version 0.97
use Tie::File;


my %opts;

getopts('r:m:c:b:', \%opts);


if(!$opts{"r"} || !$opts{"m"} || !$opts{"c"} )
{
    die("$0 -r <# residues> -m <mol. weight (Da)> -c <concentration (mg/ml)> [-b <buffer data>] < AvivFile     > OutputFile\n");
}

#   ; 347/38013.4*.150 =           ~0.00136925399990529655
#           ~
#
#	    $mrc=1.30547981309470147618;

# Mean Residue Concentration:
$mrc=$opts{"r"}/$opts{"m"}*$opts{"c"};



my $BufferVals = ();

if(defined($opts{"b"}))
{
    #print "Reading ", $opts{"b"}, "\n";
    tie @Buffer, 'Tie::File', $opts{"b"} or die("could not open ",$opts{""},"\n");

    for (@Buffer) { 
	if(/^(\d+\.\d+)\s+(\d+\.\d+)/)
	{
	    $BufferVals[$1*1000] = $2; # $1 has three decimal places.. -need an integer for the array index.
	    #print "Adding BufferVals[$1*1000]:  = $2\n"; 
	}
    }
}


while(<>)
{
	s/^/#/;
	if( /^#\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)/
	    && $4 <= 600) 
	{
            #print "$1\t".($2/$mrc)."\t$3\t$4\n";
	    $CD_Signal = $2 - $BufferVals[$1*1000];

	    print "$1\t".($CD_Signal/$mrc/3298)."\t$4\n"; # \Delta\epsilon = [\theta]/3298
	}
}
