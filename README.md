# CDGo

## What is this repository for?

## How do I install it?
Easiest way to download is by using git:
```sh
git clone https://bitbucket.org/s-gordon/CDGo.git
```

There are several dependencies:
* GNUPlot
* Wine
* Perl
* Python 2.7+

Most of these can be installed through Homebrew (OSX) or your trusty Linux
package manager.

Homebrew:
```sh
brew install gnuplot wine
```

Apt:
```sh
apt-get install gnuplot wine
```

## Usage
```sh
./CDGo.py [-h] [-C CDPRO_DIR] -i CDPRO_INPUT [-v]
```

Accepts as an input file the output generated by CRDATA.exe. CRDATA can be
circumvented by using another script, CDToGnuplot:
```sh
./CDToGnuplot -r <# residues> -m <MW (Da)> -c <protein concentration (mg/ml)> [-b <buffer file>] < InFile >OutFile
```
The `-C` option takes the absolute path to your CDPro installation directory.

Output will be written to a folder in the same directory as the input of the
format `<input>-CDPro`.

## Who do I talk to?
* Shane Gordon

## Contributors
See contributors.txt

## Licence
See LICENSE.md
