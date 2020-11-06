#!/usr/bin/env python


import unittest
from cdgo import cli
import numpy as np


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.pathlength = np.random.uniform(0.1, 10, 1)[0]
        self.concentration = np.random.uniform(0.1, 10, 1)[0]
        self.number_residues = np.random.randint(low=50, high=500, size=1)[0]
        self.mol_weight = np.random.uniform(5000, 500000, 1)[0]
        self.cdpro_path = '/path/to/cdpro'
        self.buffer = '/path/to/buffer'
        self.sample = '/path/to/sample'
        self.parser = cli.parse_args(
            [
                '-C', self.cdpro_path,
                '--pathlength', str(self.pathlength),
                '--number_residues', str(self.number_residues),
                '--mol_weight', str(self.mol_weight),
                '--concentration', str(self.concentration),
                '--buffer', self.buffer,
                '-i', self.sample,
            ])
        self.parser_cdsstr = cli.parse_args(
            [
                '-C', self.cdpro_path,
                '--pathlength', str(self.pathlength),
                '--number_residues', str(self.number_residues),
                '--mol_weight', str(self.mol_weight),
                '--concentration', str(self.concentration),
                '--buffer', self.buffer,
                '-i', self.sample,
                '--cdsstr'
            ])
        self.parser_continll = cli.parse_args(
            [
                '-C', self.cdpro_path,
                '--pathlength', str(self.pathlength),
                '--number_residues', str(self.number_residues),
                '--mol_weight', str(self.mol_weight),
                '--concentration', str(self.concentration),
                '--buffer', self.buffer,
                '-i', self.sample,
                '--continll'
            ])
        self.parser_continll_cdsstr = cli.parse_args(
            [
                '-C', self.cdpro_path,
                '--pathlength', str(self.pathlength),
                '--number_residues', str(self.number_residues),
                '--mol_weight', str(self.mol_weight),
                '--concentration', str(self.concentration),
                '--buffer', self.buffer,
                '-i', self.sample,
                '--cdsstr',
                '--continll'
            ])

    def test_cli_options(self):
        self.assertEqual(self.parser.pathlength, self.pathlength)
        self.assertEqual(self.parser.concentration, self.concentration)
        self.assertEqual(self.parser.mol_weight, self.mol_weight)
        self.assertEqual(self.parser.number_residues, self.number_residues)
        self.assertEqual(self.parser.buffer, self.buffer)
        self.assertEqual(self.parser.cdpro_input, self.sample)
        self.assertEqual(self.parser.cdsstr, False)
        self.assertEqual(self.parser.continll, False)

    def test_cli_toggles(self):
        self.assertEqual(self.parser_cdsstr.cdsstr, True)
        self.assertEqual(self.parser_cdsstr.continll, False)
        self.assertEqual(self.parser_continll.cdsstr, False)
        self.assertEqual(self.parser_continll.continll, True)
        self.assertEqual(self.parser_continll_cdsstr.cdsstr, True)
        self.assertEqual(self.parser_continll_cdsstr.continll, True)


if __name__ == "__main__":
    unittest.main()
