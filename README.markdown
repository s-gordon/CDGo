# CDGo: A Wrapper for Analysing Circular Dichroism Spectroscopy Data

## Installation

Easiest way to download is by using git:

```sh
git clone https://github.com/s-gordon/CDGo.git
```

Then install CDGo using your favourite python installation (v3.5++):

```sh
cd /path/to/cdgo/source
python setup.py install
```

There are several dependencies required by CDGo not found in many base python
installations. These are listed in `requirements.txt` and can be
conveniently installed using the python package manager `pip`:

```sh
pip install -r requirements.txt
```

Alternatively, Linux and Windows binaries for the GUI app can be downloaded
from the releases page.

## Dependencies

* Wine
* Python v3.5+

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

Beginning in v0.6a, support is added for Windows via pre-compiled binaries.
These are provided in the release page.

## Usage

```sh
cdgo [-h] [-C CDPRO_DIR] -i CDPRO_INPUT --mol_weight MOL_WEIGHT \
--number_residues NUMBER_RESIDUES --concentration CONCENTRATION \
--pathlength PATHLENGTH [--buffer BUFFER] [--cdsstr] [--continll] [-v]
```

```sh
cdgo --help
```

The GUI app can also be started from the command line:

```sh
cdgoapp
```

Output will be written to a folder in the same directory as the input of the
format `<input>-CDPro`. In the event that a folder would be overwritten, the
path is appended with the current date.

## Understanding CDGo Outputs

Once executed, CDGo will generate a new directory in the same path as the input
protein spectrum name, appended with `-CDPro`. In the event that this directory
already exists, the directory name will be appended with the current date.
Under this directory you should find the following structure:

```txt
── <protein-spectrum-file-name>-CDPro<-date>
│   ├── CDSpec-<protein-spectrum-file-name>-Overlay.png
│   ├── continll-ibasis1
│   │   ├── BASIS.PG
│   │   ├── CONTIN.CD
│   │   ├── CONTINLL.OUT
│   │   ├── CONTIN.OUT
│   │   ├── input
│   │   ├── ProtSS.out
│   │   ├── stdout
│   │   └── SUMMARY.PG
│   ├── exp_data_delta_epsilon.csv
│   ├── input.log
│   └── secondary_structure_summary.csv
```

`secondary_structure_summary.csv`: Summary of secondary structure elements from
each combination of CONTINLL/CDsstr and ibasis

`input.log`: logfile reporting input and output parameters given by GUI or CLI.

`exp_data_delta_epsilon.csv`: CSV-format file reporting averaged CD Signal (in
delta epsilon; `ave` column), standard deviation (in delta epsilon; `std`
column), and wavelength (`wl` column).

Each combination of CONTINLL/CDsstr and ibasis will produce a daughter
directory (e.g. `continll-ibasis1`). Within these directories you should find
the output from execution of CONTINLL or CDsstr as appropriate. See the [CDPro
website](https://sites.bmb.colostate.edu/sreeram/CDPro/) for more info.

## Ongoing Issues

### Input files with replicates ###

~~In the case where any input files from Aviv machines are passed to `CDGo`, it
will throw an error along the lines of:~~

```sh
IndexError: index -1 is out of bounds for axis 0 with size 0
```

~~This is expected, and results from `CDGo` currently being unable to handle
replicate data sets. This will change in the future, but for now you will need
to either average the input data sets manually or simply remove all but one
replicate from the input file.~~

Support for multi-scan Aviv files was added in release v0.4a. Scans are
automatically averaged and standard deviation reported.

## Who do I talk to

* Shane Gordon
* Tao Nelson (original author)

## Contributors

See contributors.txt

## Citation

For publications please cite the following resources as appropriate.

### CDGo

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

### CDPro

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

### CDSSTR

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

### Protein Reference Sets

Full details for how to reference each protein reference set are provided at
the [CDPro website](https://sites.bmb.colostate.edu/sreeram/CDPro/). Please
cite these as appropriate if used in publications.

### Everything Else

Generally refer to the website for
[CDPro](http://sites.bmb.colostate.edu/sreeram/CDPro/).

## Licence

See [LICENSE](https://github.com/s-gordon/CDGo/blob/development/LICENSE).
