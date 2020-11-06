#!/usr/bin/env python

import unittest
import numpy as np
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from cdgo import mathops


class TestResidualOps(unittest.TestCase):

    def setUp(self):
        self.func = mathops.residuals
        self.df1 = DataFrame(np.random.uniform(0, 20, 1000))
        self.df2 = DataFrame(np.random.uniform(0, 20, 1000))

    def test_is_true(self):
        self.assertTrue(True)

    def test_subtract_1(self):
        assert_frame_equal(
            self.func(self.df1, self.df2), self.df1-self.df2)

    def test_subtract_2(self):
        assert_frame_equal(
            self.func(self.df2, self.df1), self.df2-self.df1)

    def test_subtract_3(self):
        assert_frame_equal(
            self.func(self.df2, 1), self.df2-1)

    def test_subtract_4(self):
        assert_frame_equal(
            self.func(1, self.df1), 1-self.df1)


# class TestUnitConversion(unittest.TestCase):
#     def setUp(self):
#         self.func = mathops.millidegrees_to_epsilon
#         md = DataFrame(np.random.uniform(5, 20, 80))
#         self.mol_weight = 3e5
#         self.pathlength = 0.1
#         self.npeptides = 300
#         self.conc = 0.1
#         self.md = md

    # def test_millideg_to_epsilon(self):
    #     eps = self.md * (self.mol_weight / (
    #         10 * self.pathlength * self.npeptides * self.conc * 3298))
    #     assert_frame_equal(
    #         self.func(
    #             self.md, self.mol_weight, self.npeptides, self.conc,
    #             L=self.pathlength),
    #         eps)


if __name__ == "__main__":
    unittest.main()
