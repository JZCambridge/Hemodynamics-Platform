import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
# Import functions
import Save_Load_File
import Pd_Funs

import numpy
import pandas
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
##############################################################################

class AreaVolCalcs:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI

            self.ui.BloodPressureAndHeartRateTableBtn_AVC.clicked.connect(lambda: self.ChooseTableFile())
            self.ui.chooseReferenceTableBtn_AVC.clicked.connect(lambda: self.chooseReferenceTable())
            self.ui.CalculatePressurePaBtn_AVC.clicked.connect(lambda: self.CalculatePressurePa())
            self.ui.CalculatePressureBtn_AVC.clicked.connect(lambda: self.CalculatePressure())
            self.ui.CalculateCardiacCycleBtn_AVC.clicked.connect(lambda: self.CalculateCardiacCycle())
            self.ui.CalculatePressureCoefficentBtn_AVC.clicked.connect(lambda: self.CalculatePressureCoefficent())
            self.ui.CalculateHeartRateCoefficentBtn_AVC.clicked.connect(lambda: self.CalculateHeartRateCoefficent())
            self.ui.choosesaveTableBtn_AVC.clicked.connect(lambda: self.choosesaveTable())
            self.ui.BloodPressureAndHeartRateBtn_AVC.clicked.connect(lambda: self.BloodPressureAndHeartRate())
            self.ui.BatchBloodPressureAndHeartRateBtn_AVC.clicked.connect(lambda: self.batchBloodPressureAndHeartRate())

        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

    def ChooseTableFile(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Input table path", fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; All files (*.*);; ", qtObj=True)

        # set filename
        self.ui.BloodPressureAndHeartRatePathTxt_AVC.setPlainText(filename)

    def chooseReferenceTable(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Input table path",fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; All files (*.*);; ",qtObj=True)

        # set filename
        self.ui.ReferenceTableTxt_AVC.setPlainText(filename)

    def choosesaveTable(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(
            dispMsg="output table path",fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; All files (*.*);; ",qtObj=True)

        # set filename
        self.ui.saveTableTxt_AVC.setPlainText(filename)

    def CalculatePressurePa(self):
        SystolicBloodPressure_mmHg = float(self.ui.lineEdit_SystolicBloodPressurePa_AVC.text())
        DiastolicBloodPressure_mmHg = float(self.ui.lineEdit_DiastolicBloodPressurePa_AVC.text())
        print('SystolicBloodPressure_mmHg', SystolicBloodPressure_mmHg)
        print('DiastolicBloodPressure_mmHg', DiastolicBloodPressure_mmHg)
        SystolicBloodPressure = SystolicBloodPressure_mmHg * 133.3223684
        DiastolicBloodPressure = DiastolicBloodPressure_mmHg * 133.3223684
        self.ui.lineEdit_SystolicBloodPressure_AVC.setText(str(SystolicBloodPressure))
        self.ui.lineEdit_DiastolicBloodPressure_AVC.setText(str(DiastolicBloodPressure))

    def CalculatePressure(self):
        SystolicBloodPressure = float(self.ui.lineEdit_SystolicBloodPressure_AVC.text())
        DiastolicBloodPressure = float(self.ui.lineEdit_DiastolicBloodPressure_AVC.text())
        print('SystolicBloodPressure', SystolicBloodPressure)
        print('DiastolicBloodPressure', DiastolicBloodPressure)
        MeanBloodPressure = (SystolicBloodPressure + DiastolicBloodPressure)/2
        PressureDifference = abs(SystolicBloodPressure - DiastolicBloodPressure)
        self.ui.lineEdit_MeanBloodPressure_AVC.setText(str(MeanBloodPressure))
        self.ui.lineEdit_PressureDifference_AVC.setText(str(PressureDifference))

    def CalculateCardiacCycle(self):
        HeartRate = int(self.ui.lineEdit_HeartRate_AVC.text())
        print('HeartRate', HeartRate)
        CardiacCycle = 60 / HeartRate
        self.ui.lineEdit_CardiacCycle_AVC.setText(str(CardiacCycle))

    def CalculatePressureCoefficent(self):
        ReferencePressureDifference = float(self.ui.lineEdit_ReferencePressureDifference_AVC.text())
        PressureDifference = float(self.ui.lineEdit_PressureDifference_AVC.text())
        ReferenceMeanBloodPressure = float(self.ui.lineEdit_ReferenceMeanBloodPressure_AVC.text())
        MeanBloodPressure = float(self.ui.lineEdit_MeanBloodPressure_AVC.text())
        print('ReferencePressureDifference', ReferencePressureDifference)
        print('PressureDifference', PressureDifference)
        print('ReferenceMeanBloodPressure', ReferenceMeanBloodPressure)
        print('MeanBloodPressure', MeanBloodPressure)
        BloodPressureDifferenceCoefficient = PressureDifference/ReferencePressureDifference
        MeanBloodPressureCoefficient = MeanBloodPressure/ReferenceMeanBloodPressure
        self.ui.lineEdit_PressureDifferenceCoefficient_AVC.setText(str(BloodPressureDifferenceCoefficient))
        self.ui.lineEdit_MeanPressureCoefficient_AVC.setText(str(MeanBloodPressureCoefficient))

    def CalculateHeartRateCoefficent(self):
        ReferenceCardiacCycle = float(self.ui.lineEdit_ReferenceCardiacCycle_AVC.text())
        CardiacCycle = float(self.ui.lineEdit_CardiacCycle_AVC.text())
        print('ReferenceCardiacCycle', ReferenceCardiacCycle)
        print('CardiacCycle', CardiacCycle)
        HeartRateCoefficient = CardiacCycle/ReferenceCardiacCycle
        self.ui.lineEdit_HeartRateCoefficient_AVC.setText(str(HeartRateCoefficient))

    def BloodPressureAndHeartRate(self):
        LinearRegression = self.ui.checkBox_LinearRegression_AVC.isChecked()
        LinearRegressionTimestart = float(self.ui.lineEdit_LinearRegressionTimestart_AVC.text())
        MeanBloodPressureCoefficient = float(self.ui.lineEdit_MeanPressureCoefficient_AVC.text())
        PressureDifferenceCoefficient = float(self.ui.lineEdit_PressureDifferenceCoefficient_AVC.text())
        HeartRateCoefficient = float(self.ui.lineEdit_HeartRateCoefficient_AVC.text())
        ReferenceTablePath = self.ui.ReferenceTableTxt_AVC.toPlainText()
        SaveTablePath = self.ui.saveTableTxt_AVC.toPlainText()
        print('LinearRegression', LinearRegression)
        print('LinearRegressionTimestart', LinearRegressionTimestart)
        print('MeanBloodPressureCoefficient', MeanBloodPressureCoefficient)
        print('PressureDifferenceCoefficient', PressureDifferenceCoefficient)
        print('HeartRateCoefficient', HeartRateCoefficient)
        print('ReferenceTablePath', ReferenceTablePath)
        print('SaveTablePath', SaveTablePath)

        # load
        if '.csv' in ReferenceTablePath:
            pdIn = pandas.read_csv(ReferenceTablePath, sep=',', header=None)
        elif '.txt' in ReferenceTablePath:
            pdIn = pandas.read_csv(ReferenceTablePath, sep='\t', header=None)
        elif '.xlsx' in ReferenceTablePath:
            pdIn = pandas.read_excel(ReferenceTablePath, header=None)
        elif '.xls' in ReferenceTablePath:
            pdIn = pandas.read_excel(ReferenceTablePath, header=None)
        elif '.xlsm' in ReferenceTablePath:
            pdIn = pandas.read_excel(ReferenceTablePath, header=None)
        elif '.xlsb' in ReferenceTablePath:
            pdIn = pandas.read_excel(ReferenceTablePath, header=None)
        elif '.odf' in ReferenceTablePath:
            pdIn = pandas.read_excel(ReferenceTablePath, header=None)

        pdIn = pdIn.dropna(axis=0, how='all')
        pdUse = pdIn[pdIn[pdIn.columns[0]] > LinearRegressionTimestart]
        MeanBloodPressure = (pdUse[pdUse.columns[1]].max()+pdUse[pdUse.columns[1]].min())/2
        LinerRegressionNomber = len(pdIn) - len(pdUse)
        pdIn[pdIn.columns[1]] = pdIn[pdIn.columns[1]] - MeanBloodPressure
        pdIn[pdIn.columns[1]] = pdIn[pdIn.columns[1]] * PressureDifferenceCoefficient
        pdIn[pdIn.columns[1]] = pdIn[pdIn.columns[1]] + (MeanBloodPressure*MeanBloodPressureCoefficient)
        if LinearRegression:
            for i in range(LinerRegressionNomber):
                Coefficient = pdIn[pdIn.columns[0]][i]/pdIn[pdIn.columns[0]][LinerRegressionNomber-1]
                pdIn[pdIn.columns[1]][i] = pdIn[pdIn.columns[1]][LinerRegressionNomber-1]*Coefficient
        pdIn[pdIn.columns[0]] = pdIn[pdIn.columns[0]] * HeartRateCoefficient
        # output
        if '.csv' in SaveTablePath:
            pdIn.to_csv(SaveTablePath, sep=',', index=False, header=None)
        elif '.txt' in SaveTablePath:
            pdIn.to_csv(SaveTablePath, sep='\t', index=False, header=None)
        elif '.xlsx' in SaveTablePath:
            pdIn.to_excel(SaveTablePath, index=False, header=None)
        elif '.xls' in SaveTablePath:
            pdIn.to_excel(SaveTablePath, index=False, header=None)
        elif '.xlsm' in SaveTablePath:
            pdIn.to_excel(SaveTablePath, index=False, header=None)
        elif '.xlsb' in SaveTablePath:
            pdIn.to_excel(SaveTablePath, index=False, header=None)
        elif '.odf' in SaveTablePath:
            pdIn.to_excel(SaveTablePath, index=False, header=None)

    def batchBloodPressureAndHeartRate(self,tablePath=None):
        if tablePath:
            inPath = tablePath
        else:
            inPath = self.ui.BloodPressureAndHeartRatePathTxt_AVC.toPlainText()

        dfBloodPressureAndHeartRate = Pd_Funs.OpenDF(inPath=inPath, header=0, usecols=None)

        # Blood Pressure And Heart Rate
        for i in range(len(dfBloodPressureAndHeartRate)):
            # get line of table
            print('get info in line', i)
            info = dfBloodPressureAndHeartRate.iloc[i].fillna('')

            BloodPressureAndHeartRate = False
            try:
                if info["Blood Pressure And Heart Rate"]:
                    BloodPressureAndHeartRate = info["Blood Pressure And Heart Rate"]
            except:
                pass
            if BloodPressureAndHeartRate:
                ReferenceCSVpath = ''
                OutputCSVpath = ''
                CalculatePressurePa = False
                CalculatePressure = False
                CalculateCardiacCycle = False
                CalculatePressureCoefficent = False
                CalculateHeartRateCoefficent = False
                LinearRegression = False
                LinearRegressionTimestart = ''
                ReferenceMeanBloodPressure = ''
                ReferencePressureDifference = ''
                SystolicBloodPressuremmHg = ''
                DiastolicBloodPressuremmHg = ''
                SystolicBloodPressure = ''
                DiastolicBloodPressure = ''
                MeanBloodPressure = ''
                PressureDifference = ''
                MeanPresureCoefficient = ''
                PressureDifferenceCoefficient = ''
                HeartRate = ''
                CardiacCycle = ''
                ReferenceCardiacCycle = ''
                HeartRateCoefficient = ''
                try:
                    if info["Reference CSV path"]:
                        ReferenceCSVpath = info["Reference CSV path"]
                except:
                    pass
                try:
                    if info["Output CSV path"]:
                        OutputCSVpath = info["Output CSV path"]
                except:
                    pass
                try:
                    if isinstance(info["CalculatePressurePa"], numpy.bool_):
                        CalculatePressurePa = info["CalculatePressurePa"]
                except:
                    pass
                try:
                    if isinstance(info["CalculatePressure"], numpy.bool_):
                        CalculatePressure = info["CalculatePressure"]
                except:
                    pass
                try:
                    if isinstance(info["CalculateCardiacCycle"], numpy.bool_):
                        CalculateCardiacCycle = info["CalculateCardiacCycle"]
                except:
                    pass
                try:
                    if isinstance(info["CalculatePressureCoefficent"], numpy.bool_):
                        CalculatePressureCoefficent = info["CalculatePressureCoefficent"]
                except:
                    pass
                try:
                    if isinstance(info["CalculateHeartRateCoefficent"], numpy.bool_):
                        CalculateHeartRateCoefficent = info["CalculateHeartRateCoefficent"]
                except:
                    pass
                try:
                    if isinstance(info["Linear Regression"], numpy.bool_):
                        LinearRegression = info["Linear Regression"]
                except:
                    pass
                try:
                    if info["Linear Regression Timestart"]:
                        LinearRegressionTimestart = info["Linear Regression Timestart"]
                except:
                    pass
                try:
                    if info["Reference Mean Blood Pressure"]:
                        ReferenceMeanBloodPressure = info["Reference Mean Blood Pressure"]
                except:
                    pass
                try:
                    if info["Reference Pressure Difference"]:
                        ReferencePressureDifference = info["Reference Pressure Difference"]
                except:
                    pass
                try:
                    if info["Systolic Blood Pressure (mmHg)"]:
                        SystolicBloodPressuremmHg = info["Systolic Blood Pressure (mmHg)"]
                except:
                    pass
                try:
                    if info["Diastolic Blood Pressure (mmHg)"]:
                        DiastolicBloodPressuremmHg = info["Diastolic Blood Pressure (mmHg)"]
                except:
                    pass
                try:
                    if info["Systolic Blood Pressure"]:
                        SystolicBloodPressure = info["Systolic Blood Pressure"]
                except:
                    pass
                try:
                    if info["Diastolic Blood Pressure"]:
                        DiastolicBloodPressure = info["Diastolic Blood Pressure"]
                except:
                    pass
                try:
                    if info["Mean Blood Pressure"]:
                        MeanBloodPressure = info["Mean Blood Pressure"]
                except:
                    pass
                try:
                    if info["Pressure Difference"]:
                        PressureDifference = info["Pressure Difference"]
                except:
                    pass
                try:
                    if info["Mean Presure Coefficient"]:
                        MeanPresureCoefficient = info["Mean Presure Coefficient"]
                except:
                    pass
                try:
                    if info["Pressure Difference Coefficient"]:
                        PressureDifferenceCoefficient = info["Pressure Difference Coefficient"]
                except:
                    pass
                try:
                    if info["Heart Rate"]:
                        HeartRate = info["Heart Rate"]
                except:
                    pass
                try:
                    if info["Cardiac Cycle"]:
                        CardiacCycle = info["Cardiac Cycle"]
                except:
                    pass
                try:
                    if info["Reference Cardiac Cycle"]:
                        ReferenceCardiacCycle = info["Reference Cardiac Cycle"]
                except:
                    pass
                try:
                    if info["Heart Rate Coefficient"]:
                        HeartRateCoefficient = info["Heart Rate Coefficient"]
                except:
                    pass
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                if ReferenceCSVpath:
                    self.ui.ReferenceTableTxt_AVC.setPlainText('{}'.format(ReferenceCSVpath))
                if OutputCSVpath:
                    self.ui.saveTableTxt_AVC.setPlainText('{}'.format(OutputCSVpath))
                self.ui.checkBox_LinearRegression_AVC.setChecked(LinearRegression)
                if LinearRegressionTimestart:
                    self.ui.lineEdit_LinearRegressionTimestart_AVC.setText('{}'.format(LinearRegressionTimestart))
                if ReferenceMeanBloodPressure:
                    self.ui.lineEdit_ReferenceMeanBloodPressure_AVC.setText('{}'.format(ReferenceMeanBloodPressure))
                if ReferencePressureDifference:
                    self.ui.lineEdit_ReferencePressureDifference_AVC.setText('{}'.format(ReferencePressureDifference))
                if SystolicBloodPressuremmHg:
                    self.ui.lineEdit_SystolicBloodPressurePa_AVC.setText('{}'.format(SystolicBloodPressuremmHg))
                if DiastolicBloodPressuremmHg:
                    self.ui.lineEdit_DiastolicBloodPressurePa_AVC.setText('{}'.format(DiastolicBloodPressuremmHg))
                if CalculatePressurePa:
                    self.CalculatePressurePa()
                if SystolicBloodPressure:
                    self.ui.lineEdit_SystolicBloodPressure_AVC.setText('{}'.format(SystolicBloodPressure))
                if DiastolicBloodPressure:
                    self.ui.lineEdit_DiastolicBloodPressure_AVC.setText('{}'.format(DiastolicBloodPressure))
                if CalculatePressure:
                    self.CalculatePressure()
                if MeanBloodPressure:
                    self.ui.lineEdit_MeanBloodPressure_AVC.setText('{}'.format(MeanBloodPressure))
                if PressureDifference:
                    self.ui.lineEdit_PressureDifference_AVC.setText('{}'.format(PressureDifference))
                if CalculatePressureCoefficent:
                    self.CalculatePressureCoefficent()
                if MeanPresureCoefficient:
                    self.ui.lineEdit_MeanPressureCoefficient_AVC.setText('{}'.format(MeanPresureCoefficient))
                if PressureDifferenceCoefficient:
                    self.ui.lineEdit_PressureDifferenceCoefficient_AVC.setText('{}'.format(PressureDifferenceCoefficient))
                if HeartRate:
                    self.ui.lineEdit_HeartRate_AVC.setText('{}'.format(HeartRate))
                if CalculateCardiacCycle:
                    self.CalculateCardiacCycle()
                if CardiacCycle:
                    self.ui.lineEdit_CardiacCycle_AVC.setText('{}'.format(CardiacCycle))
                if ReferenceCardiacCycle:
                    self.ui.lineEdit_ReferenceCardiacCycle_AVC.setText('{}'.format(ReferenceCardiacCycle))
                if CalculateHeartRateCoefficent:
                    self.CalculateHeartRateCoefficent()
                if HeartRateCoefficient:
                    self.ui.lineEdit_HeartRateCoefficient_AVC.setText('{}'.format(HeartRateCoefficient))
                # Touched function
                self.BloodPressureAndHeartRate()

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\BloodPressureAndHeartRate.ui")
    stats = AreaVolCalcs(UI=ui)
    stats.ui.show()
    app.exec_()