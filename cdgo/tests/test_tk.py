#!/usr/bin/env python

import pytest
from cdgo import app
from tkinter import Tk


@pytest.fixture()
def backend():
    global _app
    _app = Tk()
    _app.grid_columnconfigure(3, weight=1)
    gui = app.TkGUI(_app)
    gui.build()
    return gui


def test_defaults(backend):
    """Test the GUI in the native state.
    Check that defaults are as intended.

    """
    assert backend.comboBoxIbasis.get() == backend.ibasis_options[0]
    assert backend.nresidues.get() == 300
    assert backend.proteinmw.get() == 3e5
    assert backend.parallel_switch.get() == 0
    assert backend.cdsstr_switch.get() == 0
    assert backend.continll_switch.get() == 0
    assert backend.pathlength.get() == 0.1


def test_change_ibasis_combobox(backend):
    # check that changing the ibasis selection updates the ibasis option
    lsize = len(backend.ibasis_options)
    for n in range(lsize):
        backend.comboBoxIbasis.current(n)
        assert backend.comboBoxIbasis.get() == backend.ibasis_options[n]


def test_continll_checkbox_toggle(backend):
    # initialize as false for testing
    backend.continll_switch.set(False)

    # toggle to true
    backend.clickContinllCheckBox()
    assert backend.continll_switch.get() == 1

    # toggle again to false
    backend.clickContinllCheckBox()
    assert backend.continll_switch.get() == 0


def test_cdsstr_checkbox_toggle(backend):
    # initialize as false for testing
    backend.cdsstr_switch.set(False)

    # toggle to true
    backend.clickCdsstrCheckBox()
    assert backend.cdsstr_switch.get() == 1

    # toggle again to false
    backend.clickCdsstrCheckBox()
    assert backend.cdsstr_switch.get() == 0


def test_parallel_checkbox_toggle(backend):
    # initialize as false for testing
    backend.parallel_switch.set(False)

    # toggle to true
    backend.clickParallelCheckBox()
    assert backend.parallel_switch.get() == 1

    # toggle again to false
    backend.clickParallelCheckBox()
    assert backend.parallel_switch.get() == 0
