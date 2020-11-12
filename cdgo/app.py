#!/usr/bin/env python


import logging
import sys
from tkinter import (END, NSEW, Button, Checkbutton, DoubleVar, E,
                     IntVar, Label, Tk, W, filedialog, scrolledtext, ttk)

from cdgo.core import check_cdpro_install, print_citation_info, run


class Spinbox(ttk.Entry):

    def __init__(self, master=None, **kw):
        ttk.Entry.__init__(self, master, "ttk::spinbox", **kw)

    def set(self, value):
        self.tk.call(self._w, "set", value)


class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


class TkGUI():

    """Docstring for TkGUI. """

    def __init__(self, master, ypad=5, xpad=5):
        """TODO: to be defined.

        :master: TODO

        """
        master.title("CDGo")
        self._master = master
        self._master.maxsize(1500, 1000)
        self._master.minsize(1000, 700)
        self.ypad = ypad
        self.xpad = xpad

    def build(self):
        ibasis_options = [
            "1-5 (soluble proteins)",
            "6-7 (soluble and denatured proteins)",
            "8 (tertiary class specific)",
            "9-10 (soluble and membrane proteins)",
            "1-10 (all)"
        ]
        self.ibasis_options = ibasis_options

        # Add text widget to display logging info
        self.st = scrolledtext.ScrolledText(self._master, state='disabled')
        self.st.configure(font='TkFixedFont')
        self.st.grid(column=3, row=1, rowspan=20, sticky=NSEW)

        # Create textLogger
        text_handler = TextHandler(self.st)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(text_handler)

        # default values
        def_protein_conc = 0.1
        def_nresidues = 300
        def_mw = 3e5
        def_pathlength = 0.1

        self.cdproPathInstructLabel = Label(self._master, text="Select path to CDPro:")
        self.cdproPathInstructButton = Button(self._master, text="Browse", command=self.fileDialogSetCDProPath)
        self.cdproPathChosenLabel = Label(self._master, text="", wraplength=300)
        self.cdproPathInstructLabel.grid(column=1, row=1, sticky=W, pady=self.ypad, padx=self.xpad)
        self.cdproPathInstructButton.grid(column=2, row=1, sticky=W, pady=self.ypad, padx=self.xpad)
        self.cdproPathChosenLabel.grid(column=1, row=2, sticky=W, pady=self.ypad, padx=self.xpad)

        self.proteinSpectrumFileNameLabel = Label(self._master, text="Select protein spectrum file:")
        self.proteinSpectrumFileNameButton = Button(self._master, text="Browse", command=self.fileDialogProteinSpectrumFile)
        self.proteinSpectrumFileNameChosenLabel = Label(self._master, text="", wraplength=300)
        self.proteinSpectrumFileNameLabel.grid(column=1, row=3, sticky=W, pady=self.ypad, padx=self.xpad)
        self.proteinSpectrumFileNameButton.grid(column=2, row=3, sticky=W, pady=self.ypad, padx=self.xpad)
        self.proteinSpectrumFileNameChosenLabel.grid(column=1, row=4, sticky=W, pady=self.ypad, padx=self.xpad)

        self.bufferSpectrumFileNameLabel = Label(self._master, text="Select buffer spectrum file:")
        self.bufferSpectrumFileNameButton = Button(self._master, text="Browse", command=self.fileDialogBufferSpectrumFile)
        self.bufferSpectrumFileNameChosenLabel = Label(self._master, text="", wraplength=300)
        self.bufferSpectrumFileNameLabel.grid(column=1, row=5, sticky=W, pady=self.ypad, padx=self.xpad)
        self.bufferSpectrumFileNameButton.grid(column=2, row=5, sticky=W, pady=self.ypad, padx=self.xpad)
        self.bufferSpectrumFileNameChosenLabel.grid(column=1, row=6, sticky=W, pady=self.ypad, padx=self.xpad)

        self.proteinconc = DoubleVar()
        # initialize with sensible default value
        self.proteinconc.set(def_protein_conc)
        self.proteinConcLabel = Label(self._master, text="Protein concentration (g/L):")
        self.proteinConcSpinBox = Spinbox(self._master, width=10)
        self.proteinConcSpinBox.config(from_=0.01, to=10, format="%.2f", textvariable=self.proteinconc, increment=0.01)
        self.proteinConcLabel.grid(column=1, row=7, sticky=W, pady=self.ypad, padx=self.xpad)
        self.proteinConcSpinBox.grid(column=2, row=7, sticky=W, pady=self.ypad, padx=self.xpad)

        self.nresidues = IntVar()
        self.nresidues.set(def_nresidues)
        self.spinBoxNumberResiduesLabel = Label(self._master, text="Number of residues:")
        self.spinBoxNumberResidues = Spinbox(self._master, width=10)
        self.spinBoxNumberResidues.config(from_=1, to=1000, textvariable=self.nresidues, increment=1)
        self.spinBoxNumberResidues.grid(column=2, row=8, sticky=W, pady=self.ypad, padx=self.xpad)
        self.spinBoxNumberResiduesLabel.grid(column=1, row=8, sticky=W, pady=self.ypad, padx=self.xpad)

        self.proteinmw = DoubleVar()
        self.proteinmw.set(def_mw)
        self.spinBoxProteinMWLabel = Label(self._master, text="Molecular weight (Da):")
        self.spinBoxProteinMW = Spinbox(self._master, width=10)
        self.spinBoxProteinMW.config(from_=1, to=100000, increment=1, textvariable=self.proteinmw)
        self.spinBoxProteinMWLabel.grid(column=1, row=10, sticky=W, pady=self.ypad, padx=self.xpad)
        self.spinBoxProteinMW.grid(column=2, row=10, sticky=W, pady=self.ypad, padx=self.xpad)

        self.pathlength = DoubleVar()
        self.pathlength.set(def_pathlength)
        self.spinBoxPathlengthLabel = Label(self._master, text="Cuvette pathlength (cm):")
        self.spinBoxPathlength = Spinbox(self._master, width=10)
        self.spinBoxPathlength.config(from_=0.1, to=1, increment=0.1, textvariable=self.pathlength)
        self.spinBoxPathlengthLabel.grid(column=1, row=11, sticky=W, pady=self.ypad, padx=self.xpad)
        self.spinBoxPathlength.grid(column=2, row=11, sticky=W, pady=self.ypad, padx=self.xpad)

        self.comboBoxIbasisLabel = Label(self._master, text="Protein iBasis set:")
        self.comboBoxIbasis = ttk.Combobox(self._master, width=36, state='readonly')
        self.comboBoxIbasis['values'] = self.ibasis_options
        self.comboBoxIbasis.bind('<<ComboboxSelected>>', self.ibasisFieldChange)
        self.comboBoxIbasis.current(0)
        self.dbRange = range(1, 6)
        self.comboBoxIbasisLabel.grid(column=1, row=12, sticky=W, pady=self.ypad, padx=self.xpad)
        self.comboBoxIbasis.grid(column=2, row=12, sticky=W, pady=self.ypad, padx=self.xpad)

        self.continll_switch = IntVar()
        self.cdsstr_switch = IntVar()
        self.continll_switch.set(0)
        self.cdsstr_switch.set(0)
        self.CONTINLLCheckButton = Checkbutton(self._master, text=" CONTINLL", variable=self.continll_switch, command=self.clickContinllCheckBox)
        self.CDSSTRCheckButton = Checkbutton(self._master, text=" CDSSTR", variable=self.cdsstr_switch, command=self.clickCdsstrCheckBox)
        self.CONTINLLCheckButton.grid(column=1, row=13, sticky=W, pady=self.ypad, padx=self.xpad)
        self.CDSSTRCheckButton.grid(column=2, row=13, sticky=W, pady=self.ypad, padx=self.xpad)

        self.parallel_switch = IntVar()
        self.parallel_switch.set(0)
        self.parallelCheckButton = Checkbutton(
            self._master, text="Run in parallel?",
            variable=self.parallel_switch,
            command=self.clickParallelCheckBox)
        self.parallelCheckButton.grid(column=1, row=14, sticky=W, pady=self.ypad, padx=self.xpad)

        self.ok_button = Button(self._master, text="OK", command=self.accept)
        self.ok_button.grid(column=1, row=15, sticky=W, padx=self.xpad, pady=self.ypad)
        self.close_button = Button(self._master, text="Close", command=self.reject)
        self.close_button.grid(column=1, row=15, sticky=E, padx=self.xpad, pady=self.ypad)

        logging.info(print_citation_info())

    def ibasisFieldChange(self, event):
        ct = self.comboBoxIbasis.get()
        logging.info("Ibasis range set to: {}".format(ct))
        if ct == self.ibasis_options[0]:
            self.dbRange = range(1, 6)
        elif ct == self.ibasis_options[1]:
            self.dbRange = range(6, 8)
        elif ct == self.ibasis_options[2]:
            self.dbRange = [8]
        elif ct == self.ibasis_options[3]:
            self.dbRange = range(9, 11)
        elif ct == self.ibasis_options[4]:
            self.dbRange = range(1, 11)
        else:
            logging.info(ct)

    def ibasisSelectionChange(self):
        ct = self.comboBoxIbasis.currentText()
        logging.info("Ibasis range set to: {}".format(ct))
        if ct == self.comboBoxIbasis.itemText(0):
            self.dbRange = range(1, 6)
        elif ct == self.comboBoxIbasis.itemText(1):
            self.dbRange = range(6, 8)
        elif ct == self.comboBoxIbasis.itemText(2):
            self.dbRange = [8]
        elif ct == self.comboBoxIbasis.itemText(3):
            self.dbRange = range(9, 11)
        elif ct == self.comboBoxIbasis.itemText(4):
            self.dbRange = range(1, 11)
        else:
            logging.info(ct)


    def fileDialogSetCDProPath(self):
        label = self.cdproPathChosenLabel
        try:
            dir = filedialog.askdirectory(
                initialdir='',
                title="Select path to CDPro installation.")
            if check_cdpro_install(dir) is True:
                logging.info("CDPro installation found at {}".format(dir))
                logging.info("CDPro path set to \"{}\"".format(dir))
                label.configure(text=dir)
                self.cdproPath = dir
            else:
                logging.info(
                    "CDPro installation not found at {}".format(dir))
        except TypeError:
            logging.info("Nothing selected.")


    def fileDialogProteinSpectrumFile(self):
        label = self.proteinSpectrumFileNameChosenLabel
        ftypes = [("Aviv spectrum files", "*.dat")]
        try:
            proteinSpectrumFileName = filedialog.askopenfilename(
                initialdir='',
                title="Select a spectrum file",
                filetypes=ftypes)
            if proteinSpectrumFileName:
                label.configure(text=proteinSpectrumFileName)
                logging.info("Protein spectrum set to \"{}\"".format(proteinSpectrumFileName))
                self.proteinSpectrumFileName = proteinSpectrumFileName
        except TypeError:
            logging.info("Nothing selected.")


    def fileDialogBufferSpectrumFile(self):
        label = self.bufferSpectrumFileNameChosenLabel
        ftypes = [("Aviv spectrum files", "*.dat")]
        try:
            bufferSpectrumFileName = filedialog.askopenfilename(
                initialdir='',
                title="Select a spectrum file",
                filetypes=ftypes)
            if bufferSpectrumFileName:
                label.configure(text=bufferSpectrumFileName)
                logging.info("Buffer spectrum set to \"{}\"".format(bufferSpectrumFileName))
                self.bufferSpectrumFileName = bufferSpectrumFileName
        except TypeError:
            logging.info("Nothing selected.")


    def clickContinllCheckBox(self):
        if self.continll_switch.get() == 1:
            logging.info("CONTINLL enabled")
        else:
            logging.info("CONTINLL disabled")


    def clickCdsstrCheckBox(self):
        if self.cdsstr_switch.get() == 1:
            logging.info("CDSSTR enabled")
        else:
            logging.info("CDSSTR disabled")


    def clickParallelCheckBox(self):
        if self.parallel_switch.get() == 1:
            logging.info("Parallel execution enabled")
        else:
            logging.info("Parallel execution disabled")


    def accept(self):
        if self.proteinSpectrumFileName is None:
            logging.info("Protein spectrum file not set.")
        else:
            logging.info("Running CDGo...")
            self.process()

    def reject(self):
        logging.info("Quitting")
        self._master.quit()


    def returnState(self, switch):
        if switch.get() == 0:
            return False
        else:
            return True


    def process(self):
        cdpro = self.cdproPath
        proteinSpecName = self.proteinSpectrumFileName
        bufferSpecName = self.bufferSpectrumFileName
        mw = self.proteinmw.get()
        nres = self.nresidues.get()
        concentration = self.proteinconc.get()
        dbRange = self.dbRange
        pl = self.pathlength.get()
        # check state of continll switch
        continll = self.returnState(self.continll_switch)
        cdsstr = self.returnState(self.cdsstr_switch)
        parallel = self.returnState(self.parallel_switch)
        run(proteinSpecName, bufferSpecName, cdpro, mw, pl, nres,
            concentration, dbRange, continll, cdsstr, parallel)


def main():
    root = Tk()
    root.grid_columnconfigure(3, weight=1)
    gui = TkGUI(root)
    gui.build()
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Exiting now.")
        sys.exit(1)


if __name__ == "__main__":
    main()
