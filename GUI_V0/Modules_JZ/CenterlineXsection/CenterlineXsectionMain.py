# -*- coding: utf-8 -*-
"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by
Jin ZHENG JZ410 (29Mar21)
"""

##############################################################################
# Import functions from JZ410
import sys
import os

# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
# Import functions
import Save_Load_File
import Image_Process_Functions
import Preprocess_Mask
import Pd_Funs
##############################################################################

##############################################################################
# Standard libs
from datetime import datetime
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader


##############################################################################

class Xsection:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
            self.ui.chooseEXEBtn_CX.clicked.connect(lambda: self.ChooseOpenFile())
            self.ui.chooseLoadDirBtn_CX.clicked.connect(lambda: self.ChooseLoadDir())
            self.ui.chooseSaveDirBtn_CX.clicked.connect(lambda: self.ChooseSaveDir())
            self.ui.ConvertBtn_CX.clicked.connect(lambda: self.convert())
            self.ui.chooseBatchTableBtn_CX.clicked.connect(lambda: self.ChooseOpenCSVFile())
            self.ui.batchConvertBtn_CX.clicked.connect(lambda: self.BatchConvert())
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.exeInDict = {}
        self.InitiateExeDict()

    def InitiateExeDict(self):
        self.exeInDict["EXEPath"] = None
        self.exeInDict["InputImagePath"] = None
        self.exeInDict["CenterLinePath"] = None
        self.exeInDict["OutputImagePath"] = None
        self.exeInDict["OutputPointsPath"] = None
        self.exeInDict["ResampleDepth"] = None
        self.exeInDict["CPRAngle"] = None  # degrees
        self.exeInDict["Type"] = 0  # default
        self.exeInDict["Interpolation"] = None  # 0 linear & 1 NN
        self.exeInDict["OutCSV"] = None  # 0 linear & 1 NN

    def ChooseOpenFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Choose C++ EXE file",
            fileTypes="All files (*.*);; EXE files(*.exe)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadExePathTxt_CX.setPlainText('{}'.format(filename))

    def ChooseLoadDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Load data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.loadDirPathTxt_CX.setPlainText(dirname)

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_CX.setPlainText(dirname)

    def ChooseOpenCSVFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; Table files (*.csv *.txt) ;; More table files (*.xlsx *.xls *.xlsm)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.dfHeadPathTxt_CX.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose table file:\n{}".format(filename))

    def convert(self):
        # convert everything to list/str
        self.exeInDict["EXEPath"] = self.ui.loadExePathTxt_CX.toPlainText()  # !!!
        inputDir = [self.ui.loadDirPathTxt_CX.toPlainText()]
        inputImagePath = Preprocess_Mask.StrToLst(
            strIn=self.ui.inImgPathTxt_CX.toPlainText()
        )["listOut"]
        inputCSVPath = Preprocess_Mask.StrToLst(
            strIn=self.ui.inCSVPathTxt_CX.toPlainText()
        )["listOut"]
        outputDir = [self.ui.saveDirPathTxt_CX.toPlainText()]
        outputImagePath = Preprocess_Mask.StrToLst(
            strIn=self.ui.outImgPathTxt_CX.toPlainText()
        )["listOut"]
        outputCSVPath = Preprocess_Mask.StrToLst(
            strIn=self.ui.outCSVPathTxt_CX.toPlainText()
        )["listOut"]
        self.exeInDict["Interpolation"] = Preprocess_Mask.StrToLst(
            strIn=self.ui.InterPTxt_CX.toPlainText()
        )["floatOut"]
        self.exeInDict["OutCSV"] = Preprocess_Mask.StrToLst(
            strIn=self.ui.outCSVTxt_CX.toPlainText()
        )["floatOut"]
        self.exeInDict["ResampleDepth"] = float(self.ui.ResampLineTxt_CX.text())
        self.exeInDict["CPRAngle"] = float(self.ui.CPRLineTxt_CX.text())  # degrees
        # self.exeInDict["CPRAngle"] = float(self.ui.CPRLineTxt_CX.text())  # degrees
        cpus = int(self.ui.cpuLineTxt_CX.text())

        # create output folder
        # delete by az
        # Save_Load_File.checkCreateDir(path=outputDir)
        # Save_Load_File.checkCreateDir(path=outputCSVPath)

        # combine lists
        self.exeInDict["InputImagePath"] = Save_Load_File.AppendLists(inputDir, inputImagePath, sep="/")["combineList"]
        self.exeInDict["CenterLinePath"] = Save_Load_File.AppendLists(inputDir, inputCSVPath, sep="/")["combineList"]
        self.exeInDict["OutputImagePath"] = Save_Load_File.AppendLists(outputDir, outputImagePath, sep="/")[
            "combineList"]
        self.exeInDict["OutputPointsPath"] = Save_Load_File.AppendLists(outputDir, outputCSVPath, sep="/")[
            "combineList"]

        # reconstruction exe
        Image_Process_Functions.ReconstructExeRun(self.exeInDict,
                                                  multiP=True,
                                                  processors=cpus)

    def BatchConvert(self, InputCSVPath=None):
        # input
        if InputCSVPath:
            dfHeadPath = InputCSVPath
        else:
            dfHeadPath = self.ui.dfHeadPathTxt_CX.toPlainText()
        # load DF
        dfHead = Pd_Funs.OpenDF(
            inPath=dfHeadPath,
            header=0,
            usecols=None
        )

        # Looping through cases
        for inputDir, \
            inputCSVDir, \
            outputDir, \
            outputCSVDir, \
            ResampleDepth, \
            CPRAngle, \
            cpus, \
            casePath, \
            EXEPath \
                in zip(
            dfHead['inputDir'].tolist(),
            dfHead['inputCSVDir'].tolist(),
            dfHead['outputDir'].tolist(),
            dfHead['outputCSVDir'].tolist(),
            dfHead['resampleDepth'].tolist(),
            dfHead['CPRAngle'].tolist(),
            dfHead['cpus'].tolist(),
            dfHead['casePath'].tolist(),
            dfHead['EXEPath'].tolist()
        ):
            # load DF
            dfCase = Pd_Funs.OpenDF(
                inPath=casePath,
                header=0,
                usecols=None,
                index_col=None
            )

            # dictionary element
            self.exeInDict["EXEPath"] = EXEPath
            self.exeInDict["Interpolation"] = dfCase['Interpolation'].tolist()
            self.exeInDict["OutCSV"] = dfCase['OutCSV'].tolist()
            self.exeInDict["ResampleDepth"] = float(ResampleDepth)
            self.exeInDict["CPRAngle"] = float(CPRAngle)

            # list
            inputImagePath = dfCase['inputImagePath'].tolist()
            inputCSVPath = dfCase['inputCSVPath'].tolist()
            outputImagePath = dfCase['outputImagePath'].tolist()
            outputCSVPath = dfCase['outputCSVPath'].tolist()

            # create out dirs
            Save_Load_File.checkCreateDir(path=outputDir)
            Save_Load_File.checkCreateDir(path=outputCSVDir)

            # combine lists
            self.exeInDict["InputImagePath"] = Save_Load_File.AppendLists(
                [inputDir], inputImagePath, sep="/")["combineList"]
            self.exeInDict["CenterLinePath"] = Save_Load_File.AppendLists(
                [inputCSVDir], inputCSVPath, sep="/")["combineList"]
            self.exeInDict["OutputImagePath"] = Save_Load_File.AppendLists(
                [outputDir], outputImagePath, sep="/")["combineList"]
            self.exeInDict["OutputPointsPath"] = Save_Load_File.AppendLists(
                [outputCSVDir], outputCSVPath, sep="/")["combineList"]

            # update message
            self.UpdateMsgLog(msg="Working in self.exeInDict:\n{}".format(self.exeInDict))

            # reconstruction exe
            Image_Process_Functions.ReconstructExeRun(
                self.exeInDict,
                multiP=True,
                processors=cpus
            )

            # clear dictionary
            self.InitiateExeDict()

    def UpdateMsgLog(self, msg=""):
        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + msg \
               + "\n############################\n"

        # update log and display message
        if self.modelui:
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
        print(msg)