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
import Post_Image_Process_Functions
import Preprocess_Mask
import Use_Plt
##############################################################################

##############################################################################
# Standard library
from datetime import datetime
import time
import threading
from PySide2.QtUiTools import QUiLoader
##############################################################################

class MaskSTL:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        if self.ui:
            self.ui.chooseEXEBtn_MSTL.clicked.connect(lambda: self.ChooseOpenEXEFile())
            self.ui.chooseIn1Btn_MSTL.clicked.connect(lambda: self.ChooseFirstMskFile())
            self.ui.chooseOut1Btn_MSTL.clicked.connect(lambda: self.ChooseSaveComboFile())
            self.ui.chooseIn2Btn_MSTL.clicked.connect(lambda: self.ChooseSecondMskFile())
            self.ui.chooseOut2Btn_MSTL.clicked.connect(lambda: self.ChooseSaveFirstFile())
            self.ui.STLBtn_MSTL.clicked.connect(lambda: self.STLGenerate())
            self.ui.pushButton_BatchTable_MSTL.clicked.connect(lambda: self.batchcsv())
            self.ui.pushButton_BatchRun_MSTL.clicked.connect(lambda: self.BatchConvert())

        # initial definition
        self.exeInDict = {}
        self.exeInDict["EXEPath"] = ""
        self.exeInDict["choice"] = 0
        self.exeInDict["inFilePath1"] = ""
        self.exeInDict["outFilePath1"] = ""
        self.exeInDict["inFilePath2"] = ""
        self.exeInDict["outFilePath2"] = ""
        self.DataFrame = None

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_MSTL.setPlainText('{}'.format(filename))

    def ChooseOpenEXEFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Choose C++ EXE file",
            fileTypes="All files (*.*);; EXE files(*.exe)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadExePathTxt_MSTL.setPlainText('"{}"'.format(filename))

        # update message
        self.UpdateMsgLog(msg="Choose EXE:\n{}".format(
            self.ui.loadExePathTxt_MSTL.toPlainText()
        )
        )

    def ChooseFirstMskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load (first) image segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.mskFirstPathTxt_MSTL.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose (first) segmentation:\n{}".format(
            self.ui.mskFirstPathTxt_MSTL.toPlainText()
        )
        )

    def ChooseSaveComboFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Output (combined) STL file path",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "STL files (*.stl) ;; ",
                                                 qtObj=True)

        # set filename
        self.ui.saveComboPathTxt_MSTL.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving combined STL file path:\n{}".format(self.ui.saveComboPathTxt_MSTL.toPlainText()))

    def ChooseSecondMskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load second image segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.mskSecondPathTxt_MSTL.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose second segmentation:\n{}".format(
            self.ui.mskSecondPathTxt_MSTL.toPlainText()
        )
        )

    def ChooseSaveFirstFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Output first STL file path",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "STL files (*.stl) ;; ",
                                                 qtObj=True)

        # set filename
        self.ui.saveFirstPathTxt_MSTL.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving first STL file path:\n{}".format(self.ui.saveFirstPathTxt_MSTL.toPlainText()))

    # if oneClick=True, means one click CFD call this modules
    def STLGenerate(self, oneClick=False, inputPath=None, outputPath=None):
    # def STLGenerate(self, oneClick=False, WallPath=None, WallStlPath=None, LumenPath=None, LumenStlPath=None):

        if not oneClick:
            self.exeInDict["EXEPath"] = self.ui.loadExePathTxt_MSTL.toPlainText()
            choiceIn = self.ui.smoothBtnGrp_MSTL.checkedButton().text()
            self.exeInDict["inFilePath1"] = self.ui.mskFirstPathTxt_MSTL.toPlainText()
            self.exeInDict["outFilePath1"] = self.ui.saveComboPathTxt_MSTL.toPlainText()
            self.exeInDict["inFilePath2"] = self.ui.mskSecondPathTxt_MSTL.toPlainText()
            self.exeInDict["outFilePath2"] = self.ui.saveFirstPathTxt_MSTL.toPlainText()

            # which to run
            if choiceIn == "Two Files Smoothing":
                self.exeInDict["choice"] = 2
            elif choiceIn == "Single File Smoothing":
                self.exeInDict["choice"] = 1
            elif choiceIn == "Single File No Smoothing":
                self.exeInDict["choice"] = 3

        else:
            self.exeInDict['EXEPath'] = self.ui.MaskReconExePathTxt_1_OC.toPlainText()

            self.exeInDict['inFilePath1'] = inputPath
            self.exeInDict['outFilePath1'] = outputPath
            self.exeInDict["inFilePath2"] = 'Second Mask Path'
            self.exeInDict["outFilePath2"] = 'First STL path'

            self.exeInDict['choice'] = 1
        # update message
        self.UpdateMsgLog(
            msg="Input:\n{}".format(self.exeInDict))

        # Run with thread
        thread = threading.Thread(target=Image_Process_Functions.ReconstructExeRun,
                                  args=(self.exeInDict, False))
        thread.start()

    def BatchConvert(self, CSVPath=None, choice=3):
        if CSVPath:
            self.DataFrame = Pd_Funs.OpenDF(CSVPath, header=0)
        else:
            self.DataFrame = Pd_Funs.OpenDF(self.ui.plainTextEdit_BatchTable_MSTL.toPlainText(), header=0)
        for i in range(len(self.DataFrame)):
            self.exeInDict['EXEPath'] = self.DataFrame['EXEPath'][i]
            self.exeInDict['inFilePath1'] = self.DataFrame['InputFilePath'][i]
            self.exeInDict['outFilePath1'] = self.DataFrame['OutputFilePath'][i]
            self.exeInDict['inFilePath2'] = 'Anything'
            self.exeInDict['outFilePath2'] = 'Anything'
            self.exeInDict['choice'] = choice
            thread = threading.Thread(target=Image_Process_Functions.ReconstructExeRun,
                                      args=(self.exeInDict, False))
            thread.start()
            time.sleep(5)

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
        print(disp)

if __name__ == '__main__':
    a = MaskSTL()
    a.BatchConvert(CSVPath=r"E:\Coronary\b7_junzong\49-6000010357-1\solidbatch\Table\3WallSTL.csv", choice=3)