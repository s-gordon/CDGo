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

## Who do I talk to? ##
* Shane Gordon
* Tao Nelson

## Contributors
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

### CONTINLL ###

### CDSSTR ###

### Everything Else ###

Generally refer to the website for
[CDPro](http://sites.bmb.colostate.edu/sreeram/CDPro/).

## Licence
See LICENSE.md
