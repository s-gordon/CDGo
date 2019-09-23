# -*- coding: utf-8 -*-

import logging
import signal
import sys

from cdgo.core import check_cdpro_install, print_citation_info, run
from PyQt5 import QtCore, QtGui, QtWidgets


def sigintHandler(*args):
    """Handler for SIGINT"""
    sys.stderr.write("\r")
    QtWidgets.QApplication.quit()


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        monofont = QtGui.QFont("monospace", 8)
        self.widget.setFont(monofont)
        self.widget.setGeometry(QtCore.QRect(460, 60, 200, 400))
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class Ui_MainWindow(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.layout = layout
        logging.getLogger().setLevel(logging.INFO)
        self.proteinSpectrumFileName = None
        self.bufferSpectrumFileName = None
        self.continllOption = False
        self.cdsstrOption = False
        self.dbRange = range(1, 6)

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        logTextBox = QPlainTextEditLogger(MainWindow)
        logging.getLogger().addHandler(logTextBox)
        self.logTextBox = logTextBox
        # self.logger = QPlainTextEditLogger(self)
        self.layout.addWidget(self.logTextBox.widget)
        self.setLayout(self.layout)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(20, 20, 430, 411))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.cdproPathInstructLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.cdproPathInstructLabel.setObjectName("cdproPathInstructLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole,
                                  self.cdproPathInstructLabel)
        self.cdproTextPath = QtWidgets.QLabel(self.formLayoutWidget)
        self.cdproTextPath.setText("")
        self.cdproTextPath.setWordWrap(True)
        self.cdproTextPath.setObjectName("cdproTextPath")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole,
                                  self.cdproTextPath)
        self.pushButtonBrowseCDProPath = QtWidgets.QPushButton(
            self.formLayoutWidget)
        self.pushButtonBrowseCDProPath.setObjectName(
            "pushButtonBrowseCDProPath")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.pushButtonBrowseCDProPath)
        self.proteinSpectrumInstructLabel = QtWidgets.QLabel(
            self.formLayoutWidget)
        self.proteinSpectrumInstructLabel.setObjectName(
            "proteinSpectrumInstructLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.proteinSpectrumInstructLabel)
        self.proteinSpectrumFileNameLabel = QtWidgets.QLabel(
            self.formLayoutWidget)
        self.proteinSpectrumFileNameLabel.setText("")
        self.proteinSpectrumFileNameLabel.setWordWrap(True)
        self.proteinSpectrumFileNameLabel.setObjectName(
            "proteinSpectrumFileNameLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.proteinSpectrumFileNameLabel)
        self.pushButtonBrowseSampleFileName = QtWidgets.QPushButton(
            self.formLayoutWidget)
        self.pushButtonBrowseSampleFileName.setObjectName(
            "pushButtonBrowseSampleFileName")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.pushButtonBrowseSampleFileName)
        self.bufferSpectrumInstructLabel = QtWidgets.QLabel(
            self.formLayoutWidget)
        self.bufferSpectrumInstructLabel.setObjectName(
            "bufferSpectrumInstructLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.bufferSpectrumInstructLabel)
        self.bufferSpectrumFileNameLabel = QtWidgets.QLabel(
            self.formLayoutWidget)
        self.bufferSpectrumFileNameLabel.setText("")
        self.bufferSpectrumFileNameLabel.setWordWrap(True)
        self.bufferSpectrumFileNameLabel.setObjectName(
            "bufferSpectrumFileNameLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.bufferSpectrumFileNameLabel)
        self.pushButtonBrowseBufFileName = QtWidgets.QPushButton(
            self.formLayoutWidget)
        self.pushButtonBrowseBufFileName.setObjectName(
            "pushButtonBrowseBufFileName")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.pushButtonBrowseBufFileName)
        self.proteinConcInstruction = QtWidgets.QLabel(self.formLayoutWidget)
        self.proteinConcInstruction.setObjectName("proteinConcInstruction")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.proteinConcInstruction)
        self.proteinConcSpinBox = QtWidgets.QDoubleSpinBox(
            self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(
            self.proteinConcSpinBox.sizePolicy().hasHeightForWidth())
        self.proteinConcSpinBox.setSizePolicy(sizePolicy)
        self.proteinConcSpinBox.setDecimals(3)
        self.proteinConcSpinBox.setMaximum(10.0)
        self.proteinConcSpinBox.setSingleStep(0.01)
        self.proteinConcSpinBox.setProperty("value", 0.1)
        self.proteinConcSpinBox.setObjectName("proteinConcSpinBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole,
                                  self.proteinConcSpinBox)
        self.numberResInstructLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.numberResInstructLabel.setObjectName("numberResInstructLabel")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole,
                                  self.numberResInstructLabel)
        self.spinBoxNumberResidues = QtWidgets.QSpinBox(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(
            self.spinBoxNumberResidues.sizePolicy().hasHeightForWidth())
        self.spinBoxNumberResidues.setSizePolicy(sizePolicy)
        self.spinBoxNumberResidues.setMaximum(1000)
        self.spinBoxNumberResidues.setMinimum(2)
        self.spinBoxNumberResidues.setProperty("value", 100.0)
        self.spinBoxNumberResidues.setObjectName("spinBoxNumberResidues")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                  self.spinBoxNumberResidues)
        self.MWInstruct = QtWidgets.QLabel(self.formLayoutWidget)
        self.MWInstruct.setObjectName("MWInstruct")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole,
                                  self.MWInstruct)
        self.doubleSpinBoxProteinMW = QtWidgets.QDoubleSpinBox(
            self.formLayoutWidget)
        self.doubleSpinBoxProteinMW.setDecimals(1)
        self.doubleSpinBoxProteinMW.setMaximum(999999.0)
        self.doubleSpinBoxProteinMW.setProperty("value", 14000.0)
        self.doubleSpinBoxProteinMW.setObjectName("doubleSpinBoxProteinMW")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole,
                                  self.doubleSpinBoxProteinMW)
        self.pathlengthInstruct = QtWidgets.QLabel(self.formLayoutWidget)
        self.pathlengthInstruct.setObjectName("pathlengthInstruct")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole,
                                  self.pathlengthInstruct)
        self.doubleSpinBoxPathlength = QtWidgets.QDoubleSpinBox(
            self.formLayoutWidget)
        self.doubleSpinBoxPathlength.setDecimals(2)
        self.doubleSpinBoxPathlength.setMaximum(10)
        self.doubleSpinBoxPathlength.setMinimum(0.01)
        self.doubleSpinBoxPathlength.setProperty("value", 0.1)
        self.doubleSpinBoxPathlength.setObjectName("doubleSpinBoxPathlength")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole,
                                  self.doubleSpinBoxPathlength)
        self.proteinIbasisInstruct = QtWidgets.QLabel(self.formLayoutWidget)
        self.proteinIbasisInstruct.setObjectName("proteinIbasisInstruct")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole,
                                  self.proteinIbasisInstruct)
        self.comboBoxIbasis = QtWidgets.QComboBox(self.formLayoutWidget)
        self.comboBoxIbasis.setObjectName("comboBoxIbasis")
        self.comboBoxIbasis.addItem("")
        self.comboBoxIbasis.addItem("")
        self.comboBoxIbasis.addItem("")
        self.comboBoxIbasis.addItem("")
        self.comboBoxIbasis.addItem("")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole,
                                  self.comboBoxIbasis)
        self.checkBoxCONTINLL = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkBoxCONTINLL.setObjectName("checkBoxCONTINLL")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole,
                                  self.checkBoxCONTINLL)
        self.checkBoxCDsstr = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkBoxCDsstr.setObjectName("checkBoxCDsstr")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.LabelRole,
                                  self.checkBoxCDsstr)

        self.checkBoxCONTINLL.setToolTip("Toggle CONTINLL function.")
        self.checkBoxCDsstr.setToolTip("Toggle CDsstr function.")
        self.doubleSpinBoxPathlength.setToolTip(
            "Select the pathlength of the cuvette used to collect data.\n" +
            "Common values include 1, 0.1, and 0.05 cm.")
        self.comboBoxIbasis.setToolTip(
            "Select subset of ibases to compare against.\n" +
            "Best to select sets that are appropriate to your protein of\n" +
            "interest, or all.")
        self.pushButtonBrowseSampleFileName.setToolTip(
            "Select protein spectrum file as input to CDGo. This must be\n" +
            "Aviv Model 420 format, as generated by the instrument.\n" +
            "Multi-scan files are supported.")
        self.pushButtonBrowseBufFileName.setToolTip(
            "Select buffer spectrum file as input to CDGo. This is used to\n" +
            "subtract absorbance of non-protein components from the\n" +
            "protein spectrum. This must be Aviv Model 420 format, as\n" +
            "generated by the instrument. Multi-scan files are supported.")
        self.pushButtonBrowseCDProPath.setToolTip(
            "Select path to CDPro installation.")

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(460, 60, 711, 381))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 307, 377))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.logTextBox.widget)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setGeometry(QtCore.QRect(20, 480, 174, 34))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel
                                          | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButtonBrowseSampleFileName.clicked.connect(
            self.setProteinSpectrumFile)
        self.pushButtonBrowseBufFileName.clicked.connect(
            self.setBufferSpectrumFile)
        self.pushButtonBrowseCDProPath.clicked.connect(self.setCDProDirectory)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.checkBoxCDsstr.stateChanged.connect(self.clickCdsstrCheckBox)
        self.checkBoxCONTINLL.stateChanged.connect(self.clickContinllCheckBox)

        self.comboBoxIbasis.currentIndexChanged.connect(
            self.ibasisSelectionChange)

        logging.info(print_citation_info())

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButtonBrowseSampleFileName.setText(
            _translate("MainWindow", "Browse"))
        self.pushButtonBrowseBufFileName.setText(
            _translate("MainWindow", "Browse"))
        self.proteinSpectrumInstructLabel.setText(
            _translate("MainWindow",
                       "Select your protein sample CD spectrum file (*.dat)"))
        self.numberResInstructLabel.setText(
            _translate("MainWindow", "Number of residues"))
        self.bufferSpectrumInstructLabel.setText(
            _translate("MainWindow",
                       "Select your buffer CD spectrum file (*.dat)"))
        self.MWInstruct.setText(
            _translate("MainWindow", "Molecular Weight (Da)"))
        self.doubleSpinBoxPathlength.setSuffix(_translate("MainWindow", " cm"))
        self.pathlengthInstruct.setText(
            _translate("MainWindow", "Cuvette pathlength (cm)"))
        self.doubleSpinBoxProteinMW.setSuffix(_translate("MainWindow", " Da"))
        self.checkBoxCONTINLL.setText(_translate("MainWindow", "CONTINLL"))
        self.checkBoxCDsstr.setText(_translate("MainWindow", "CDSSTR"))
        self.cdproPathInstructLabel.setText(
            _translate("MainWindow", "Select path to CDPro"))
        self.pushButtonBrowseCDProPath.setText(
            _translate("MainWindow", "Browse"))
        self.proteinConcInstruction.setText(
            _translate("MainWindow", "Protein concentration (g/L)"))
        self.proteinConcSpinBox.setSuffix(_translate("MainWindow", " g/L"))
        self.comboBoxIbasis.setItemText(
            0, _translate("MainWindow", "1-5 (soluble proteins)"))
        self.comboBoxIbasis.setItemText(
            1, _translate("MainWindow",
                          "6-7 (soluble and denatured proteins)"))
        self.comboBoxIbasis.setItemText(
            2, _translate("MainWindow", "8 (tertiary class specific)"))
        self.comboBoxIbasis.setItemText(
            3, _translate("MainWindow",
                          "9-10 (soluble and membrane proteins)"))
        self.comboBoxIbasis.setItemText(4,
                                        _translate("MainWindow", "1-10 (all)"))
        self.proteinIbasisInstruct.setText(
            _translate("MainWindow", "Protein iBasis set"))

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

    def accept(self):
        if self.proteinSpectrumFileName is None:
            logging.info("Protein spectrum file not set")
        else:
            logging.info("Running CDGo...")
            self.run_cdgo()

    def reject(self):
        QtCore.QCoreApplication.instance().quit()

    def setCDProDirectory(self):
        dirName = QtWidgets.QFileDialog.getExistingDirectory(
            None, "Browse for directory", ".")
        if dirName:
            self.cdproTextPath.setText(dirName)
            self.cdproTextPathDir = dirName
            logging.info(
                "CDPro installation directory set to \"{}\"".format(dirName))
            if check_cdpro_install(dirName) is True:
                logging.info("CDPro installation found at {}".format(dirName))
            else:
                logging.info(
                    "CDPro installation not found at {}".format(dirName))

    def setProteinSpectrumFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Browse", "", "Aviv spectrum file (*.dat)")
        if fileName:
            self.proteinSpectrumFileNameLabel.setText(fileName)
            logging.info(
                "Protein sample spectrum set to \"{}\"".format(fileName))
            self.proteinSpectrumFileName = fileName

    def setBufferSpectrumFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Browse", "", "Aviv spectrum file (*.dat)")
        if fileName:
            self.bufferSpectrumFileNameLabel.setText(fileName)
            logging.info("Buffer spectrum set to \"{}\"".format(fileName))
            self.bufferSpectrumFileName = fileName

    def clickContinllCheckBox(self, state):
        if state == QtCore.Qt.Checked:
            logging.info("CONTINLL enabled")
            self.continllOption = True
        else:
            logging.info("CONTINLL disabled")
            self.continllOption = False

    def clickCdsstrCheckBox(self, state):
        if state == QtCore.Qt.Checked:
            logging.info("CDSSTR enabled")
            self.cdsstrOption = True
        else:
            logging.info("CDSSTR disabled")
            self.cdsstrOption = False

    def run_cdgo(self):
        cdpro = self.cdproTextPathDir
        proteinSpecName = self.proteinSpectrumFileName
        bufferSpecName = self.bufferSpectrumFileName
        mw = self.doubleSpinBoxProteinMW.value()
        nres = self.spinBoxNumberResidues.value()
        concentration = self.proteinConcSpinBox.value()
        dbRange = self.dbRange
        pl = self.doubleSpinBoxPathlength.value()
        continll = self.continllOption
        cdsstr = self.cdsstrOption
        run(proteinSpecName, bufferSpecName, cdpro, mw, pl, nres,
            concentration, dbRange, continll, cdsstr)


def main():
    signal.signal(signal.SIGINT, sigintHandler)
    app = QtWidgets.QApplication(sys.argv)
    timer = QtCore.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.raise_()
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
