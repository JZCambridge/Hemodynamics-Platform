import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
import Save_Load_File
import Matrix_Math
import pdfunction

import pyvista as pv
import numpy as np
import scipy.stats
import pandas as pd
import copy
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *

np.set_printoptions(threshold=np.inf)

class VTUDataExtraction():
    def __init__(self, UI = None, Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.pushButton_chooseIn_VDEZ.clicked.connect(lambda: self.chooseIn())
        self.ui.pushButton_chooseOutPut_VDEZ.clicked.connect(lambda: self.chooseOut())
        self.ui.pushButton_BatchTable_VDEZ.clicked.connect(lambda: self.chooseBatchTable())
        self.ui.pushButton_LoadData_VDEZ.clicked.connect(lambda: self.loadData())
        self.ui.pushButton_Save_VDEZ.clicked.connect(lambda: self.save())
        self.ui.pushButton_BatchRun_VDEZ.clicked.connect(lambda: self.batchRun())

        self.InitDataExtraction()

    def InitDataExtraction(self):
        self.pvdmodel = None
        self.mesh = None

    def chooseBatchTable(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; csv files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_VDEZ.setPlainText('{}'.format(filename))

    def chooseIn(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose pvd or vtu file",
                                                 fileTypes="All files (*.*);; pvd files(*.pvd);; vtu files(*.vtu)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_InPath_VDEZ.setPlainText('{}'.format(filename))

    def chooseOut(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.plainTextEdit_Output_VDEZ.setPlainText(dirname)

    def loadData(self):
        InPath = self.ui.plainTextEdit_InPath_VDEZ.toPlainText()
        print('InPath', InPath)

        self.InitDataExtraction()
        if InPath.endswith('.pvd'):
            self.pvdmodel = pv.PVDReader(InPath)
            Timestep = [str(j) for j in self.pvdmodel.time_values]
            self.ui.comboBox_timechoose_VDEZ.clear()
            self.ui.comboBox_timechoose_VDEZ.addItem('calculate all')
            self.ui.comboBox_timechoose_VDEZ.addItems(Timestep)
            self.pvdmodel.set_active_time_value(self.pvdmodel.time_values[0])
            self.mesh = self.pvdmodel.read()[0]
        else:
            self.mesh = pv.read(InPath)
        self.ui.comboBox_parameterchoose_VDEZ.clear()
        self.ui.comboBox_parameterchoose_VDEZ.addItem('calculate all')
        self.ui.comboBox_parameterchoose_VDEZ.addItems(self.mesh.point_data.keys())

    def save(self):
        FileID = self.ui.plainTextEdit_FileID_VDEZ.toPlainText()
        parameterchoose = self.ui.comboBox_parameterchoose_VDEZ.currentText()
        timestepchoose = self.ui.comboBox_timechoose_VDEZ.currentText()
        outputDir = self.ui.plainTextEdit_Output_VDEZ.toPlainText()
        outputName = self.ui.plainTextEdit_OutputName_VDEZ.toPlainText()
        outputPath = outputDir + '/' + outputName + '.csv'
        statschoices1 = []
        statschoices2 = []
        if self.ui.checkBox_Ori_VDEZ.isChecked():
            statschoices1.append('Ori')
        if self.ui.checkBox_Ori995_VDEZ.isChecked():
            statschoices1.append('Ori995')
        if self.ui.checkBox_Ori99_VDEZ.isChecked():
            statschoices1.append('Ori99')
        if self.ui.checkBox_Abs_VDEZ.isChecked():
            statschoices1.append('Abs')
        if self.ui.checkBox_Abs995_VDEZ.isChecked():
            statschoices1.append('Abs995')
        if self.ui.checkBox_Abs99_VDEZ.isChecked():
            statschoices1.append('Abs99')
        if self.ui.checkBox_Ori2_VDEZ.isChecked():
            statschoices2.append('Ori2')
        if self.ui.checkBox_Mean_VDEZ.isChecked():
            statschoices2.append('Mean')
        if self.ui.checkBox_Median_VDEZ.isChecked():
            statschoices2.append('Median')
        if self.ui.checkBox_STD_VDEZ.isChecked():
            statschoices2.append('STD')
        if self.ui.checkBox_Min_VDEZ.isChecked():
            statschoices2.append('Min')
        if self.ui.checkBox_Max_VDEZ.isChecked():
            statschoices2.append('Max')
        if self.ui.checkBox_PTP_VDEZ.isChecked():
            statschoices2.append('PTP')
        if self.ui.checkBox_Q1_VDEZ.isChecked():
            statschoices2.append('Q1')
        if self.ui.checkBox_Q3_VDEZ.isChecked():
            statschoices2.append('Q3')
        if self.ui.checkBox_IQR_VDEZ.isChecked():
            statschoices2.append('IQR')
        if self.ui.checkBox_Variance_VDEZ.isChecked():
            statschoices2.append('Variance')
        if self.ui.checkBox_Kurtosis_VDEZ.isChecked():
            statschoices2.append('Kurtosis')
        if self.ui.checkBox_Skew_VDEZ.isChecked():
            statschoices2.append('Skew')
        if self.ui.checkBox_Mode_VDEZ.isChecked():
            statschoices2.append('Mode')
        if self.ui.checkBox_RMS_VDEZ.isChecked():
            statschoices2.append('RMS')
        if self.ui.checkBox_HMean_VDEZ.isChecked():
            statschoices2.append('HMean')
        if self.ui.checkBox_GMean_VDEZ.isChecked():
            statschoices2.append('GMean')
        if self.ui.checkBox_TriMean_VDEZ.isChecked():
            statschoices2.append('TriMean')
        if self.ui.checkBox_Decile1_VDEZ.isChecked():
            statschoices2.append('Decile1')
        if self.ui.checkBox_Decile2_VDEZ.isChecked():
            statschoices2.append('Decile2')
        if self.ui.checkBox_Decile3_VDEZ.isChecked():
            statschoices2.append('Decile3')
        if self.ui.checkBox_Decile4_VDEZ.isChecked():
            statschoices2.append('Decile4')
        if self.ui.checkBox_Decile6_VDEZ.isChecked():
            statschoices2.append('Decile6')
        if self.ui.checkBox_Decile7_VDEZ.isChecked():
            statschoices2.append('Decile7')
        if self.ui.checkBox_Decile8_VDEZ.isChecked():
            statschoices2.append('Decile8')
        if self.ui.checkBox_Decile9_VDEZ.isChecked():
            statschoices2.append('Decile9')
        if self.ui.checkBox_SE_VDEZ.isChecked():
            statschoices2.append('SE')
        if self.ui.checkBox_Energy_VDEZ.isChecked():
            statschoices2.append('Energy')
        if self.ui.checkBox_Entropy_VDEZ.isChecked():
            statschoices2.append('Entropy')

        print('parameterchoose', parameterchoose)
        print('timestepchoose', timestepchoose)
        print('statschoices1', statschoices1)
        print('statschoices2', statschoices2)
        print('FileID', FileID)
        print('outputPath', outputPath)

        useparameters = self.mesh.point_data.keys()
        if not parameterchoose == 'calculate all':
            useparameters = [parameterchoose]

        usetimesteps = []
        if self.pvdmodel:
            if timestepchoose == 'calculate all':
                usetimesteps = self.pvdmodel.time_values
            else:
                usetimesteps = [float(timestepchoose)]

        if usetimesteps:
            for timestep in usetimesteps:
                self.pvdmodel.set_active_time_value(timestep)
                self.mesh = self.pvdmodel.read()[0]
                resultDir = calculateresult(arr=self.mesh, useparameters=useparameters, statschoices1=statschoices1,
                                            statschoices2=statschoices2)
                resultDir['ID'] = FileID + '_' + str(timestep)
                for key, value in resultDir.items():
                    if key.endswith('_Ori'):
                        saveDir = outputDir + '/' + outputName
                        if not os.path.exists(saveDir):
                            os.mkdir(saveDir)
                        savePath = saveDir + '/' + key + resultDir['ID'] + '.csv'
                        pd.DataFrame(resultDir[key]).to_csv(savePath, index=False)
                        resultDir[key] = savePath
                resultDF = pd.DataFrame(resultDir, index=[resultDir['ID']])
                self.outputCSV(resultDF=resultDF, outputPath=outputPath)
        else:
            resultDir = calculateresult(arr=self.mesh, useparameters=useparameters, statschoices1=statschoices1,
                                        statschoices2=statschoices2)
            resultDir['ID'] = FileID
            for key, value in resultDir.items():
                if key.endswith('_Ori'):
                    saveDir = outputDir + '/' + outputName
                    if not os.path.exists(saveDir):
                        os.mkdir(saveDir)
                    savePath = saveDir + '/' + key + resultDir['ID'] + '.csv'
                    pd.DataFrame(resultDir[key]).to_csv(savePath, index=False)
                    resultDir[key] = savePath
            resultDF = pd.DataFrame(resultDir, index=[resultDir['ID']])
            self.outputCSV(resultDF=resultDF, outputPath=outputPath)

    def outputCSV(self, resultDF, outputPath):
        if os.path.isfile(outputPath):
            DF = pdfunction.readexcel(outputPath)
        else:
            DF = pd.DataFrame()
        DF = DF.append(resultDF)
        DF.to_csv(outputPath, index=False)

    def batchRun(self):
        inpath = self.ui.plainTextEdit_BatchTable_VDEZ.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for linenum in range(len(DF)):
            # get line of table
            print('get info in line', linenum)
            info = DF.iloc[linenum].fillna('')

            InPath = ''
            LoadData = True
            FileID = ''
            ParameterChoose = ''
            TimestepChoose = ''
            Ori = True
            Ori995 = True
            Ori99 = True
            Abs = True
            Abs995 = True
            Abs99 = True
            Ori2 = False
            Mean = True
            Median = True
            STD = True
            Min = True
            Max = True
            PTP = True
            Q1 = True
            Q3 = True
            IQR = True
            Variance = True
            Kurtosis = True
            Skew = True
            Mode = True
            RMS = True
            HMean = True
            GMean = True
            TriMean = True
            Decile1 = True
            Decile2 = True
            Decile3 = True
            Decile4 = True
            Decile6 = True
            Decile7 = True
            Decile8 = True
            Decile9 = True
            SE = True
            Energy = True
            Entropy = True
            OutputFloder = ''
            OutputName = ''

            try:
                if info["InPath"]:
                    InPath = info["InPath"]
            except:
                pass
            try:
                if isinstance(info["LoadData"], np.bool_):
                    LoadData = info["LoadData"]
            except:
                pass
            try:
                if info["FileID"]:
                    FileID = info["FileID"]
            except:
                pass
            try:
                if info["ParameterChoose"]:
                    ParameterChoose = info["ParameterChoose"]
            except:
                pass
            try:
                if info["TimestepChoose"]:
                    TimestepChoose = info["TimestepChoose"]
            except:
                pass
            try:
                if isinstance(info["Ori"], np.bool_):
                    Ori = info["Ori"]
            except:
                pass
            try:
                if isinstance(info["Ori995"], np.bool_):
                    Ori995 = info["Ori995"]
            except:
                pass
            try:
                if isinstance(info["Ori99"], np.bool_):
                    Ori99 = info["Ori99"]
            except:
                pass
            try:
                if isinstance(info["Abs"], np.bool_):
                    Abs = info["Abs"]
            except:
                pass
            try:
                if isinstance(info["Abs995"], np.bool_):
                    Abs995 = info["Abs995"]
            except:
                pass
            try:
                if isinstance(info["Abs99"], np.bool_):
                    Abs99 = info["Abs99"]
            except:
                pass
            try:
                if isinstance(info["Ori2"], np.bool_):
                    Ori2 = info["Ori2"]
            except:
                pass
            try:
                if isinstance(info["Mean"], np.bool_):
                    Mean = info["Mean"]
            except:
                pass
            try:
                if isinstance(info["Median"], np.bool_):
                    Median = info["Median"]
            except:
                pass
            try:
                if isinstance(info["STD"], np.bool_):
                    STD = info["STD"]
            except:
                pass
            try:
                if isinstance(info["Min"], np.bool_):
                    Min = info["Min"]
            except:
                pass
            try:
                if isinstance(info["Max"], np.bool_):
                    Max = info["Max"]
            except:
                pass
            try:
                if isinstance(info["PTP"], np.bool_):
                    PTP = info["PTP"]
            except:
                pass
            try:
                if isinstance(info["Q1"], np.bool_):
                    Q1 = info["Q1"]
            except:
                pass
            try:
                if isinstance(info["Q3"], np.bool_):
                    Q3 = info["Q3"]
            except:
                pass
            try:
                if isinstance(info["IQR"], np.bool_):
                    IQR = info["IQR"]
            except:
                pass
            try:
                if isinstance(info["Variance"], np.bool_):
                    Variance = info["Variance"]
            except:
                pass
            try:
                if isinstance(info["Kurtosis"], np.bool_):
                    Kurtosis = info["Kurtosis"]
            except:
                pass
            try:
                if isinstance(info["Skew"], np.bool_):
                    Skew = info["Skew"]
            except:
                pass
            try:
                if isinstance(info["Mode"], np.bool_):
                    Mode = info["Mode"]
            except:
                pass
            try:
                if isinstance(info["RMS"], np.bool_):
                    RMS = info["RMS"]
            except:
                pass
            try:
                if isinstance(info["HMean"], np.bool_):
                    HMean = info["HMean"]
            except:
                pass
            try:
                if isinstance(info["GMean"], np.bool_):
                    GMean = info["GMean"]
            except:
                pass
            try:
                if isinstance(info["TriMean"], np.bool_):
                    TriMean = info["TriMean"]
            except:
                pass
            try:
                if isinstance(info["Decile1"], np.bool_):
                    Decile1 = info["Decile1"]
            except:
                pass
            try:
                if isinstance(info["Decile2"], np.bool_):
                    Decile2 = info["Decile2"]
            except:
                pass
            try:
                if isinstance(info["Decile3"], np.bool_):
                    Decile3 = info["Decile3"]
            except:
                pass
            try:
                if isinstance(info["Decile4"], np.bool_):
                    Decile4 = info["Decile4"]
            except:
                pass
            try:
                if isinstance(info["Decile6"], np.bool_):
                    Decile6 = info["Decile6"]
            except:
                pass
            try:
                if isinstance(info["Decile7"], np.bool_):
                    Decile7 = info["Decile7"]
            except:
                pass
            try:
                if isinstance(info["Decile8"], np.bool_):
                    Decile8 = info["Decile8"]
            except:
                pass
            try:
                if isinstance(info["Decile9"], np.bool_):
                    Decile9 = info["Decile9"]
            except:
                pass
            try:
                if isinstance(info["SE"], np.bool_):
                    SE = info["SE"]
            except:
                pass
            try:
                if isinstance(info["Energy"], np.bool_):
                    Energy = info["Energy"]
            except:
                pass
            try:
                if isinstance(info["Entropy"], np.bool_):
                    Entropy = info["Entropy"]
            except:
                pass
            try:
                if info["OutputFloder"]:
                    OutputFloder = info["OutputFloder"]
            except:
                pass
            try:
                if info["OutputName"]:
                    OutputName = info["OutputName"]
            except:
                pass

            # set ui
            self.ui.plainTextEdit_InPath_VDEZ.setPlainText('{}'.format(InPath))
            if LoadData:
                self.loadData()
            self.ui.plainTextEdit_FileID_VDEZ.setPlainText('{}'.format(FileID))
            self.ui.comboBox_parameterchoose_VDEZ.setCurrentText(ParameterChoose)
            self.ui.comboBox_timechoose_VDEZ.setCurrentText(str(TimestepChoose))
            self.ui.checkBox_Ori_VDEZ.setChecked(Ori)
            self.ui.checkBox_Ori995_VDEZ.setChecked(Ori995)
            self.ui.checkBox_Ori99_VDEZ.setChecked(Ori99)
            self.ui.checkBox_Abs_VDEZ.setChecked(Abs)
            self.ui.checkBox_Abs995_VDEZ.setChecked(Abs995)
            self.ui.checkBox_Abs99_VDEZ.setChecked(Abs99)
            self.ui.checkBox_Mean_VDEZ.setChecked(Ori2)
            self.ui.checkBox_Mean_VDEZ.setChecked(Mean)
            self.ui.checkBox_Median_VDEZ.setChecked(Median)
            self.ui.checkBox_STD_VDEZ.setChecked(STD)
            self.ui.checkBox_Min_VDEZ.setChecked(Min)
            self.ui.checkBox_Max_VDEZ.setChecked(Max)
            self.ui.checkBox_PTP_VDEZ.setChecked(PTP)
            self.ui.checkBox_Q1_VDEZ.setChecked(Q1)
            self.ui.checkBox_Q3_VDEZ.setChecked(Q3)
            self.ui.checkBox_IQR_VDEZ.setChecked(IQR)
            self.ui.checkBox_Variance_VDEZ.setChecked(Variance)
            self.ui.checkBox_Kurtosis_VDEZ.setChecked(Kurtosis)
            self.ui.checkBox_Skew_VDEZ.setChecked(Skew)
            self.ui.checkBox_Mode_VDEZ.setChecked(Mode)
            self.ui.checkBox_RMS_VDEZ.setChecked(RMS)
            self.ui.checkBox_HMean_VDEZ.setChecked(HMean)
            self.ui.checkBox_GMean_VDEZ.setChecked(GMean)
            self.ui.checkBox_TriMean_VDEZ.setChecked(TriMean)
            self.ui.checkBox_Decile1_VDEZ.setChecked(Decile1)
            self.ui.checkBox_Decile2_VDEZ.setChecked(Decile2)
            self.ui.checkBox_Decile3_VDEZ.setChecked(Decile3)
            self.ui.checkBox_Decile4_VDEZ.setChecked(Decile4)
            self.ui.checkBox_Decile6_VDEZ.setChecked(Decile6)
            self.ui.checkBox_Decile7_VDEZ.setChecked(Decile7)
            self.ui.checkBox_Decile8_VDEZ.setChecked(Decile8)
            self.ui.checkBox_Decile9_VDEZ.setChecked(Decile9)
            self.ui.checkBox_SE_VDEZ.setChecked(SE)
            self.ui.checkBox_Energy_VDEZ.setChecked(Energy)
            self.ui.checkBox_Entropy_VDEZ.setChecked(Entropy)
            self.ui.plainTextEdit_Output_VDEZ.setPlainText('{}'.format(OutputFloder))
            self.ui.plainTextEdit_OutputName_VDEZ.setPlainText('{}'.format(OutputName))
            self.save()

def calculateresult(arr,useparameters, statschoices1, statschoices2):
    pointData_Dir = {}
    if useparameters:
        for parameter in useparameters:
            pointData_npArr = arr[parameter][arr[parameter]!=np.array(None)]
            if statschoices1:
                pointData_Dir[parameter] = {}
                Ori_npArr = Matrix_Math.KeepTwoTailofRange(inArr=pointData_npArr, perntageKeep=100)
                Ori995_npArr = Matrix_Math.KeepTwoTailofRange(inArr=Ori_npArr, perntageKeep=99.5)
                Ori99_npArr = Matrix_Math.KeepTwoTailofRange(inArr=Ori_npArr, perntageKeep=99)
                Abs_npArr = np.absolute(Ori_npArr)
                Abs995_npArr = Matrix_Math.KeepTwoTailofRange(inArr=Abs_npArr, perntageKeep=99.5)
                Abs99_npArr = Matrix_Math.KeepTwoTailofRange(inArr=Abs_npArr, perntageKeep=99)
                if 'Ori' in statschoices1:
                    pointData_Dir[parameter]['Ori'] = Ori_npArr
                if 'Ori995' in statschoices1:
                    pointData_Dir[parameter]['Ori995'] = Ori995_npArr
                if 'Ori99' in statschoices1:
                    pointData_Dir[parameter]['Ori99'] = Ori99_npArr
                if 'Abs' in statschoices1:
                    pointData_Dir[parameter]['Abs'] = Abs_npArr
                if 'Abs995' in statschoices1:
                    pointData_Dir[parameter]['Abs995'] = Abs995_npArr
                if 'Abs99' in statschoices1:
                    pointData_Dir[parameter]['Abs99'] = Abs99_npArr

    resultDir = {}
    resultDir['ID'] = ''
    for parameter in pointData_Dir:
        for arrtype in pointData_Dir[parameter]:
            if statschoices2:
                # replace 0 in array for special 1/x calculation
                pointData_0r1 = copy.deepcopy(pointData_Dir[parameter][arrtype])
                pointData_0r1 = np.abs(pointData_0r1)
                pointData_0r1[pointData_0r1 == 0] = 1

                Min_npArr = np.nanmin(pointData_Dir[parameter][arrtype])
                Max_npArr = np.nanmax(pointData_Dir[parameter][arrtype])
                PTP_npArr = Max_npArr - Min_npArr
                Q1_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 25)
                Q3_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 75)
                IQR_npArr = np.abs(Q3_npArr - Q1_npArr)
                Median_npArr = np.nanmedian(pointData_Dir[parameter][arrtype])
                Mode_npArr = scipy.stats.mode(pointData_Dir[parameter][arrtype], nan_policy='omit')[0][0]
                Mean_npArr = np.nanmean(pointData_Dir[parameter][arrtype])
                RMS_npArr = np.sqrt(np.nanmean(pointData_Dir[parameter][arrtype] ** 2))
                HMean_npArr = scipy.stats.hmean(pointData_0r1)
                GMean_npArr = scipy.stats.gmean(pointData_0r1)
                TriMean_npArr = (np.nanpercentile(pointData_Dir[parameter][arrtype], 25) + 2 * np.nanpercentile(
                    pointData_Dir[parameter][arrtype], 50) + np.nanpercentile(
                    pointData_Dir[parameter][arrtype], 75)) / 4
                Decile1_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 10)
                Decile2_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 20)
                Decile3_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 30)
                Decile4_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 40)
                Decile6_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 60)
                Decile7_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 70)
                Decile8_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 80)
                Decile9_npArr = np.nanpercentile(pointData_Dir[parameter][arrtype], 90)
                STD_npArr = np.nanstd(pointData_Dir[parameter][arrtype], ddof=1)
                Variance_npArr = np.nanvar(pointData_Dir[parameter][arrtype], ddof=1)
                Kurtosis_npArr = scipy.stats.kurtosis(pointData_Dir[parameter][arrtype], nan_policy='omit')
                Skew_npArr = scipy.stats.skew(pointData_Dir[parameter][arrtype], nan_policy='omit')
                SE_npArr = scipy.stats.sem(pointData_Dir[parameter][arrtype], nan_policy='omit')
                Energy_npArr = np.nansum(pointData_Dir[parameter][arrtype] ** 2)
                Entropy_npArr = scipy.stats.entropy(pointData_Dir[parameter][arrtype])

                if 'Ori2' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Ori'] = pointData_Dir[parameter][arrtype]
                if 'Mean' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Mean'] = Mean_npArr
                if 'Median' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Median'] = Median_npArr
                if 'STD' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_STD'] = STD_npArr
                if 'Min' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Min'] = Min_npArr
                if 'Max' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Max'] = Max_npArr
                if 'PTP' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_PTP'] = PTP_npArr
                if 'Q1' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Q1'] = Q1_npArr
                if 'Q3' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Q3'] = Q3_npArr
                if 'IQR' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_IQR'] = IQR_npArr
                if 'Mode' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Mode'] = Mode_npArr
                if 'RMS' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_RMS'] = RMS_npArr
                if 'HMean' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_HMean'] = HMean_npArr
                if 'GMean' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_GMean'] = GMean_npArr
                if 'TriMean' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_TriMean'] = TriMean_npArr
                if 'Decile1' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Decile1'] = Decile1_npArr
                if 'Decile2' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Decile2'] = Decile2_npArr
                if 'Decile3' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Decile3'] = Decile3_npArr
                if 'Decile4' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Decile4'] = Decile4_npArr
                if 'Decile6' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Decile6'] = Decile6_npArr
                if 'Decile7' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Decile7'] = Decile7_npArr
                if 'Decile8' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Decile8'] = Decile8_npArr
                if 'Decile9' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Decile9'] = Decile9_npArr
                if 'Variance' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Variance'] = Variance_npArr
                if 'Kurtosis' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Kurtosis'] = Kurtosis_npArr
                if 'Skew' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Skew'] = Skew_npArr
                if 'SE' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_SE'] = SE_npArr
                if 'Energy' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Energy'] = Energy_npArr
                if 'Entropy' in statschoices2:
                    resultDir[parameter + '_' + arrtype + '_Entropy'] = Entropy_npArr

    return resultDir

if __name__ == "__main__":
    app = QApplication([])
    stats = VTUDataExtraction()
    stats.ui.show()
    app.exec_()