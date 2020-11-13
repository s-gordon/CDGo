#!/usr/bin/env python


import unittest
try:
    from tkinter import Tk  # python3
except ImportError:
    from Tkinter import Tk  # python2

from cdgo import app


class GUIWidgetUnitTests(unittest.TestCase):

    """Docstring for GUIUnitTests(unittest.TestCase). """

    def setUp(self):
        global _app
        _app = Tk()
        _app.grid_columnconfigure(3, weight=1)
        self.gui = app.TkGUI(_app)
        self.gui.build()

    def tearDown(self):
        self.gui = None

    def test_widget_defaults(self):
        """
        Test the GUI in the native state.
        Check that defaults are as intended.
        """
        self.assertEqual(self.gui.comboBoxIbasis.get(), self.gui.ibasis_options[0])
        self.assertEqual(self.gui.nresidues.get(), 300)
        self.assertEqual(self.gui.proteinmw.get(), 3e5)
        self.assertEqual(self.gui.parallel_switch.get(), 0)
        self.assertEqual(self.gui.cdsstr_switch.get(), 0)
        self.assertEqual(self.gui.continll_switch.get(), 0)
        self.assertEqual(self.gui.pathlength.get(), 0.1)

    def test_change_ibasis_combobox(self):
        """
        check that changing the ibasis selection updates the ibasis option
        """
        lsize = len(self.gui.ibasis_options)
        for n in range(lsize):
            self.gui.comboBoxIbasis.current(n)
            self.assertEqual(self.gui.comboBoxIbasis.get(), self.gui.ibasis_options[n])

    def test_continll_toggle(self):
        """
        Test changing the state of the CONTINLL checkbox widget.
        """
        # initialize as false for testing
        self.gui.continll_switch.set(0)
        self.gui.CONTINLLCheckButton.invoke()
        self.assertEqual(self.gui.continll_switch.get(), 0)

        # toggle to true
        self.gui.continll_switch.set(1)
        self.assertEqual(self.gui.continll_switch.get(), 1)

        # toggle to false
        self.gui.continll_switch.set(0)
        self.assertEqual(self.gui.continll_switch.get(), 0)

    def test_cdsstr_toggle(self):
        """
        Test changing the state of the CONTINLL checkbox widget.
        """
        # initialize as false for testing
        self.gui.cdsstr_switch.set(0)
        self.gui.CONTINLLCheckButton.invoke()
        self.assertEqual(self.gui.cdsstr_switch.get(), 0)

        # toggle to true
        self.gui.cdsstr_switch.set(1)
        self.assertEqual(self.gui.cdsstr_switch.get(), 1)

        # toggle to false
        self.gui.cdsstr_switch.set(0)
        self.assertEqual(self.gui.cdsstr_switch.get(), 0)

    def test_parallel_toggle(self):
        """
        Test changing the state of the CONTINLL checkbox widget.
        """
        # initialize as false for testing
        self.gui.parallel_switch.set(0)
        self.gui.CONTINLLCheckButton.invoke()
        self.assertEqual(self.gui.parallel_switch.get(), 0)

        # toggle to true
        self.gui.parallel_switch.set(1)
        self.assertEqual(self.gui.parallel_switch.get(), 1)

        # toggle to false
        self.gui.parallel_switch.set(0)
        self.assertEqual(self.gui.parallel_switch.get(), 0)


if __name__ == "__main__":
    unittest.main()
