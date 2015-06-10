# Make CDPro Better

## Requires
* GNUPlot
* Wine
* Perl
* Python 2.7+

Most of these can be installed through Homebrew (OSX) or your trusty Linux
package manager.

## Input

Convert Aviv output file to CDPro friendly format in delta epsilon.

Generate input for RunAlgorithms.py using the command:
```bash
./CDToGnuplot -r <# residues> -m <MW (Da)> -c <protein concentration (mg/ml)> [-b <buffer file>] < InFile >OutFile
```

Run algorithm:
```sh
./RunAlgorithms.py [-h] [-C CDPRO_DIR] -i CDPRO_INPUT [-v]
```

The `-C` option takes the absolute path to your CDPro installation directory.
