# CDGo: A Wrapper for Analysing Circular Dichroism Spectroscopy Data #

## Installation ##

Easiest way to download is by using git:

```sh
git clone https://github.com/s-gordon/CDGo.git
```

Then install CDGo using your favourite python installation (v2.7+):

```sh
cd /path/to/cdgo/source
python setup.py install
```

There are several dependencies required by CDGo not found in many base python
installations. These are listed in `requirements_dev.txt` and can be
conveniently installed using the python package manager `pip`:

```sh
pip install -r requirements_dev.txt
```

## Dependencies ##

* Wine
* Python 2.7+

Most of these can be installed through Homebrew (OSX) or your trusty Linux
package manager.

### OSX ###

```sh
brew install wine
```

### Linux (Debian) ###

```sh
apt-get install wine
```

### Linux (Fedora) ###

```sh
dnf install wine
```

### Windows ###

No installation instructions are provided for Windows. This could potentially be
extended using Cygwin, but would require configuring a complete Python
environment as well as the dependencies called for by CDGo.

Alternatively, one could set up a unix-like environment on Windows by using a
virtual machine (e.g. using VirtualBox).

## Usage ##

```sh
cdgo [-h] [-C CDPRO_DIR] -i CDPRO_INPUT --mol_weight MOL_WEIGHT \
--number_residues NUMBER_RESIDUES --concentration CONCENTRATION \
[--buffer BUFFER] [--cdsstr] [--continll] [-v]
```

```sh
cdgo --help
```

Output will be written to a folder in the same directory as the input of the
format `<input>-CDPro`.

## Ongoing Issues ##

### Input files with replicates ###

In the case where any input files from Aviv machines are passed to `CDGo`, it
will throw an error along the lines of:

```sh
IndexError: index -1 is out of bounds for axis 0 with size 0
```

This is expected, and results from `CDGo` currently being unable to handle
replicate data sets. This will change in the future, but for now you will need
to either average the input data sets manually or simply remove all but one
replicate from the input file.

## Who do I talk to ##

* Shane Gordon
* Tao Nelson (original author)

## Contributors ##

See contributors.txt

## Citation ##

### CDGo ###

CDGo is research software. If you make use of CDGo in scientific publications,
please cite it. The BibTeX reference is as follows:

```
@misc{Gordon2016CDGo,
  author = {Gordon, S. E. and Nelson, T. G.},
  title = {CDGo: A Wrapper for Analysing Circular Dichroism Spectroscopy Data},
  year = {2016},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/s-gordon/cdgo}},
  }
```

### CDPro ###

CDPro is research software. If you make use of CDGo in scientific publications,
please cite it. The BibTeX reference is as follows:

```bib
@article{Sreerama2000CDPro,
  title = {Estimation of protein secondary structure from circular dichroism
           spectra: comparison of CONTIN, SELCON, and CDSSTR methods with an
           expanded reference set},
  author = {Sreerama, Narasimha and Woody, Robert W},
  journal = {Analytical biochemistry},
  volume = {287},
  number = {2},
  pages = {252--260},
  year = {2000},
  publisher = {Elsevier}
}
```

Please refer to the
[CDPro webpage](http://sites.bmb.colostate.edu/sreeram/CDPro/) for further
details.

### CONTINLL ###

```bib
@article{Provencher:81,
   doi         = {10.1021/bi00504a006},
   url         = {https://doi.org/10.1021%2Fbi00504a006},
   year        = 1981,
   month       = {1},
   publisher   = {American Chemical Society ({ACS})},
   volume      = {20},
   number      = {1},
   pages       = {33--37},
   author      = {Stephen W. Provencher and Juergen Gloeckner},
   title       = {Estimation of globular protein secondary structure from
                  circular dichroism},
   journal     = {Biochemistry}
}

@article{van_Stokkum:90,
   doi         = {10.1016/0003-2697(90)90396-q},
   url         = {https://doi.org/10.1016%2F0003-2697%2890%2990396-q},
   year        = 1990,
   month       = {11},
   publisher   = {Elsevier {BV}},
   volume      = {191},
   number      = {1},
   pages       = {110--118},
   author      = {Ivo H.M. van Stokkum and Hans J.W. Spoelder and Michael
                  Bloemendal and Rienk van Grondelle and Frans C.A. Groen},
   title       = {Estimation of protein secondary structure and error analysis
                  from circular dichroism spectra},
   journal     = {Anal Biochem}
}

```

### CDSSTR ###

```bib
@article{Sreerama:00,
   doi         = {10.1006/abio.2000.4880},
   url         = {https://doi.org/10.1006%2Fabio.2000.4880},
   year        = 2000,
   month       = {12},
   publisher   = {Elsevier {BV}},
   volume      = {287},
   number      = {2},
   pages       = {252--260},
   author      = {Narasimha Sreerama and Robert W. Woody},
   title       = {Estimation of Protein Secondary Structure from Circular
                  Dichroism Spectra: Comparison of {CONTIN}, {SELCON}, and
                  {CDSSTR} Methods with an Expanded Reference Set},
   journal     = {Anal Biochem}
}

@article{Johnson:99,
   title       = {Analyzing protein circular dichroism spectra for accurate
                  secondary structures},
   author      = {Johnson, W Curtis},
   journal     = {Proteins: Struct, Funct, Bioinf},
   volume      = {35},
   number      = {3},
   pages       = {307--312},
   year        = {1999},
   publisher   = {Wiley Online Library}
}
```

### Everything Else ###

Generally refer to the website for
[CDPro](http://sites.bmb.colostate.edu/sreeram/CDPro/).

## Licence ##

See LICENSE.md
