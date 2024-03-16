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
import Post_Image_Process_Functions
import Preprocess_Mask
##############################################################################

##############################################################################
# Standard libs
import os
import numpy
from datetime import datetime


##############################################################################

class CPRMPR:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            
        self.ui.chooseEXEFileBtn_CPRJZ.clicked.connect(lambda: self.ChooseOpenFile())
        self.ui.chooseInDirBtn_CPRJZ.clicked.connect(lambda: self.ChooseLoadDir())
        self.ui.saveDirBtn_CPRJZ.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.convertBtn_CPRJZ.clicked.connect(lambda: self.convert())
        
        # initial definition
        self.exeInDict = {}
        self.exeInDict["EXEPath"] = None
        self.exeInDict["InputImagePath"] = None
        self.exeInDict["CenterLinePath"] = None
        self.exeInDict["CPRImagePath"] = None
        self.exeInDict["StraightImagePath"] = None
        self.exeInDict["ResampleDepth"] = None
        self.exeInDict["CPRAngle"] = None
        self.exeInDict["Type"] = 2  # default
        self.exeInDict["Interpolation"] = None  # 0 linear & 1 NN

    def ChooseOpenFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Choose C++ EXE file",
            fileTypes="All files (*.*);; EXE files(*.exe)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadExePathTxt_CPRJZ.setPlainText('{}'.format(filename))

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseLoadDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Load data directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadDirPathTxt_CPRJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose loading dir:\n{}".format(dirname))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Save data directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.saveDirPathTxt_CPRJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose saving dir:\n{}".format(dirname))

    def convert(self):
        # convert everything to list/str
        self.exeInDict["EXEPath"] = self.ui.loadExePathTxt_CPRJZ.toPlainText()  # !!!
        inputDir = [self.ui.loadDirPathTxt_CPRJZ.toPlainText()]
        inputImagePath = Preprocess_Mask.StrToLst(strIn=self.ui.inImgPathTxt_CPRJZ.toPlainText())["listOut"]
        inputCSVPath = Preprocess_Mask.StrToLst(strIn=self.ui.inCSVPathTxt_CPRJZ.toPlainText())["listOut"]
        outputDir = [self.ui.saveDirPathTxt_CPRJZ.toPlainText()]
        CPRImagePath = Preprocess_Mask.StrToLst(strIn=self.ui.CPRImagePathTxt_CPRJZ.toPlainText())["listOut"]
        STRImagePath = Preprocess_Mask.StrToLst(strIn=self.ui.STRImagePathTxt_CPRJZ.toPlainText())["listOut"]
        self.exeInDict["Interpolation"] = Preprocess_Mask.StrToLst(
            strIn=self.ui.InterPTxt_CPRJZ.toPlainText()
        )["floatOut"]
        self.exeInDict["ResampleDepth"] = Preprocess_Mask.StrToLst(
            strIn=self.ui.ResampleDepthLineTxt_CPRJZ.text()
        )["floatOut"]
        self.exeInDict["CPRAngle"] = Preprocess_Mask.StrToLst(
            strIn=self.ui.CPRAngleLineTxt_CPRJZ.text()
        )["floatOut"]
        cpus = int(self.ui.cpuLineTxt_XOV.text())

        # compare list size
        compareShp = Post_Image_Process_Functions.CompareListDimension(
            lsts=[
                inputImagePath,
                inputCSVPath,
                CPRImagePath,
                STRImagePath,
                self.exeInDict["Interpolation"]
            ]
        )
        if compareShp["error"]:
            # update message
            self.UpdateMsgLog(msg=compareShp["errorMessage"])
            return

        # Dealing with single CPR angle and resampling depth
        if len(self.exeInDict["CPRAngle"]) == 1:
            msg = "CPR angle input size is ONE - use single value for all cases"
            self.exeInDict["CPRAngle"] = float(self.exeInDict["CPRAngle"][0])
            # update message
            self.UpdateMsgLog(msg=msg)
        else:
            msg = "CPR angle list size = {}".format(numpy.shape(self.exeInDict["CPRAngle"]))
            # update message
            self.UpdateMsgLog(msg=msg)
            # compare size
            compareShp = Post_Image_Process_Functions.CompareListDimension(
                lsts=[
                    inputImagePath,
                    self.exeInDict["CPRAngle"]
                ]
            )
            if compareShp["error"]:
                # update message
                self.UpdateMsgLog(msg=compareShp["errorMessage"])
                return

        if len(self.exeInDict["ResampleDepth"]) == 1:
            msg = "Resample Depth input size is ONE - use single value for all cases"
            self.exeInDict["ResampleDepth"] = float(self.exeInDict["ResampleDepth"][0])
            # update message
            self.UpdateMsgLog(msg=msg)
        else:
            msg = "Resample Depth list size = {}".format(numpy.shape(self.exeInDict["ResampleDepth"]))
            # update message
            self.UpdateMsgLog(msg=msg)
            # compare size
            compareShp = Post_Image_Process_Functions.CompareListDimension(
                lsts=[
                    inputImagePath,
                    self.exeInDict["ResampleDepth"]
                ]
            )
            if compareShp["error"]:
                # update message
                self.UpdateMsgLog(msg=compareShp["errorMessage"])
                return

        # combine lists
        self.exeInDict["InputImagePath"] = Save_Load_File.AppendLists(
            inputDir, inputImagePath, sep="/"
        )["combineList"]
        self.exeInDict["CenterLinePath"] = Save_Load_File.AppendLists(
            inputDir, inputCSVPath, sep="/"
        )["combineList"]
        self.exeInDict["CPRImagePath"] = Save_Load_File.AppendLists(
            outputDir, CPRImagePath, sep="/"
        )["combineList"]
        self.exeInDict["StraightImagePath"] = Save_Load_File.AppendLists(
            outputDir, STRImagePath, sep="/"
        )["combineList"]

        msg = "EXEPath: {}".format(self.exeInDict["EXEPath"]) + \
              "\nInputImagePath: {}".format(self.exeInDict["InputImagePath"]) + \
              "\nCenterLinePath: {}".format(self.exeInDict["CenterLinePath"]) + \
              "\nCPRImagePath: {}".format(self.exeInDict["CPRImagePath"]) + \
              "\nStraightImagePath: {}".format(self.exeInDict["StraightImagePath"]) + \
              "\nResampleDepth: {}".format(self.exeInDict["ResampleDepth"]) + \
              "\nCPRAngle: {}".format(self.exeInDict["CPRAngle"]) + \
              "\nType: {}".format(self.exeInDict["Type"]) + \
              "\nInterpolation: {}".format(self.exeInDict["Interpolation"])

        # reconstruction exe
        rtrnInfo = Image_Process_Functions.ReconstructExeRun(
            self.exeInDict,
            multiP=True,
            processors=cpus
        )

        # update message
        self.UpdateMsgLog(msg="Run EXE:\n{} \n{}".format(rtrnInfo["message"], msg))

    def UpdateMsgLog(self, msg=""):
        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + msg \
               + "\n############################\n"

        if self.modelui:
            # update log and display message
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
        print(msg)
