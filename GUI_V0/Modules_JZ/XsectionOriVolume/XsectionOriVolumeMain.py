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
import Pd_Funs

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
# Import functions
import Save_Load_File
import Image_Process_Functions
import Preprocess_Mask
##############################################################################

##############################################################################
# Standard libs
import os
from datetime import datetime
from PySide2.QtUiTools import QUiLoader

##############################################################################

class OriVolume:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseEXEBtn_XOV.clicked.connect(lambda: self.ChooseOpenFile(flag=0))
        self.ui.chooseLoadDirBtn_XOV.clicked.connect(lambda: self.ChooseLoadDir())
        self.ui.chooseSaveDirBtn_XOV.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.ConvertBtn_XOV.clicked.connect(lambda: self.convert())
        self.ui.ChooseReconExePathBtn_CX.clicked.connect(lambda: self.ChooseOpenFile(flag=1))
        self.ui.ChooseBatchTableBtn_CX.clicked.connect(lambda: self.ChooseTablePath())
        self.ui.BatchProcessingBtn_CX.clicked.connect(lambda: self.BatchProcessing())
        
        # initial definition
        self.exeInDict = {}
        self.exeInDict["EXEPath"] = None
        self.exeInDict["ReferenceImagePath"] = None
        self.exeInDict["XsectionImagePath"] = None
        self.exeInDict["MapPointsPath"] = None
        self.exeInDict["OutputImagePath"] = None
        self.exeInDict["DistanceFill"] = None
        self.exeInDict["UnusedInput"] = 0
        self.exeInDict["Type"] = 1  # default
        self.exeInDict["Interpolation"] = None  # 0 linear & 1 NN
        self.DataFrame = None

    def ChooseOpenFile(self, flag=0):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Choose C++ EXE file",
            fileTypes="All files (*.*);; EXE files(*.exe)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        if flag == 0:
            self.ui.loadExePathTxt_XOV.setPlainText(filename)
        else:
            self.ui.ExePathTxt_CX.setPlainText(filename)
        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    # choose batch table path
    def ChooseTablePath(self):
        tablePath = Save_Load_File.OpenFilePathQt(
            dispMsg='Choose Batch Excel File',
            fileTypes='All files (*.*);; (Excel files(*.csv *.xlsx))',
            fileObj=self.ui,
            qtObj=True
        )

        self.ui.BatchTablePathTxt_CX.setPlainText(tablePath)

    def ChooseLoadDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Load data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.loadDirPathTxt_VOX.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose loading dir:\n{}".format(dirname))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_XOV.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose saving dir:\n{}".format(dirname))

    def ExtractInfo(self, key=None, num=0):
        return Preprocess_Mask.StrToLst(strIn=self.DataFrame[key][num])['listOut']

    def BatchProcessing(self, CSVPath=None, EXEPath=None):
        if EXEPath:
            self.exeInDict['EXEPath'] = EXEPath
        else:
            self.exeInDict['EXEPath'] = self.ui.ExePathTxt_CX.toPlainText()
        if CSVPath:
            self.DataFrame = Pd_Funs.OpenDF(CSVPath, header=0)
        else:
            self.DataFrame = Pd_Funs.OpenDF(self.ui.BatchTablePathTxt_CX.toPlainText(), header=0)

        for i in range(len(self.DataFrame)):
            inputDir = [self.DataFrame['LoadFolder'][i]]

            refImagePath = self.ExtractInfo(key='RefImgName', num=i)

            inputImagePath = self.ExtractInfo(key='XsecImgName', num=i)

            # inputCSVPath = self.ExtractInfo(key='OriVolCSV', num=i)
            inputCSVPath = [self.DataFrame['OriVolCSV'][i]]

            outputDir = [self.DataFrame['OutputFolder'][i]]
            outputName = self.ExtractInfo(key='OutImgName', num=i)
            self.exeInDict['Interpolation'] = self.ExtractInfo(key='Interpolation', num=i)
            self.exeInDict['DistanceFill'] = float(self.DataFrame['FillDistance'][i])
            cpus = int(self.DataFrame['Processors'][i])

            self.exeInDict["ReferenceImagePath"] = Save_Load_File.AppendLists(inputDir, refImagePath, sep="\\")[
                "combineList"]
            self.exeInDict["XsectionImagePath"] = Save_Load_File.AppendLists(inputDir, inputImagePath, sep="\\")[
                "combineList"]
            # self.exeInDict["MapPointsPath"] = Save_Load_File.AppendLists(inputDir, inputCSVPath, sep="\\")["combineList"]
            print(self.exeInDict)
            print(inputCSVPath)
            self.exeInDict["MapPointsPath"] = inputCSVPath
            self.exeInDict["OutputImagePath"] = Save_Load_File.AppendLists(outputDir, outputName, sep="\\")[
                "combineList"]

            print(Image_Process_Functions.ReconstructExeRun(self.exeInDict,
                                                            multiP=True,
                                                            processors=cpus))



    def convert(self):
        # convert everything to list/str
        self.exeInDict["EXEPath"] = self.ui.loadExePathTxt_XOV.toPlainText()  # !!!
        inputDir = [self.ui.loadDirPathTxt_VOX.toPlainText()]
        refImagePath = Preprocess_Mask.StrToLst(strIn=self.ui.refImgPathTxt_VOX.toPlainText())["listOut"]
        inputImagePath = Preprocess_Mask.StrToLst(strIn=self.ui.inImgPathTxt_VOX.toPlainText())["listOut"]
        inputCSVPath = Preprocess_Mask.StrToLst(strIn=self.ui.inCSVPathTxt_VOX.toPlainText())["listOut"]
        outputDir = [self.ui.saveDirPathTxt_XOV.toPlainText()]
        outputImagePath = Preprocess_Mask.StrToLst(strIn=self.ui.outImgPathTxt_VOX.toPlainText())["listOut"]
        self.exeInDict["Interpolation"] = Preprocess_Mask.StrToLst(
            strIn=self.ui.InterPTxt_VOX.toPlainText()
        )["floatOut"]
        self.exeInDict["DistanceFill"] = float(self.ui.fillDistanceLineTxt_XOV.text())
        cpus = int(self.ui.cpuLineTxt_XOV.text())

        # combine lists
        self.exeInDict["ReferenceImagePath"] = Save_Load_File.AppendLists(inputDir, refImagePath, sep="/")[
            "combineList"]
        self.exeInDict["XsectionImagePath"] = Save_Load_File.AppendLists(inputDir, inputImagePath, sep="/")[
            "combineList"]
        self.exeInDict["MapPointsPath"] = Save_Load_File.AppendLists(inputDir, inputCSVPath, sep="/")["combineList"]
        self.exeInDict["OutputImagePath"] = Save_Load_File.AppendLists(outputDir, outputImagePath, sep="/")[
            "combineList"]

        # print(inputDir)
        # print(inputImagePath)
        # print(inputCSVPath)
        # print(outputDir)
        # print(outputImagePath)
        # print(outputCSVPath)
        # print(self.exeInDict)

        # reconstruction exe
        rtrnInfo = Image_Process_Functions.ReconstructExeRun(self.exeInDict,
                                                             multiP=True,
                                                             processors=cpus)

        # update message
        self.UpdateMsgLog(msg="Run EXE:\n{}".format(rtrnInfo["message"]))

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
        else:
            pass