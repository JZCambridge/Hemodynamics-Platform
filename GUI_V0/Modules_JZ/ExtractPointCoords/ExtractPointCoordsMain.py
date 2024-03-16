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
import Matrix_Math
import SITK_Numpy
import Preprocess_Mask
import CFD_FEA_Post_Process
import Pd_Funs
##############################################################################

##############################################################################
# Standard library
import numpy
from datetime import datetime
from PySide2.QtUiTools import QUiLoader
##############################################################################

class ExtractPointCoords:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseMaskPathBtn_MCJZ.clicked.connect(lambda: self.ChooseMaskPath())
        self.ui.chooseOutDirBtn_MCJZ.clicked.connect(lambda: self.ChooseOutDir())
        self.ui.convertBtn_MCJZ.clicked.connect(lambda: self.CoordinateExtraction())
        self.ui.chooseCSVPathBtn_MCJZ.clicked.connect(lambda: self.ChooseOpenCSVFile())
        self.ui.batchBtn_MCJZ.clicked.connect(lambda: self.BatchExtract())

    def ChooseMaskPath(self):
        # Save data
        filePaths = Save_Load_File.OpenFilePathQt(
            dispMsg="Choose mask files",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.filePathsTxt_MCJZ.appendPlainText(filePaths)

        # update message
        self.UpdateMsgLog(msg="Choose Mask Files: \n{}".format(filePaths))

    def ChooseOutDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose output directories",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.dirPathTxt_MCJZ.appendPlainText(dirname + ", \n")

        # update message
        self.UpdateMsgLog(msg="Choose output directory: \n{}".format(dirname))

    def ChooseOpenCSVFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; Table files (*.csv *.txt) ;; More table files (*.xlsx *.xls *.xlsm)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.csvPathTxt_MCJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose table file:\n{}".format(filename))

    def BatchExtract(self,CSVPath=None):
        if CSVPath:
            dfPath = CSVPath
        else:
            dfPath = self.ui.csvPathTxt_MCJZ.toPlainText()

        # load DF
        df = Pd_Funs.OpenDF(
            inPath=dfPath,
            header=0,
            usecols=None
        )

        # batch coordinate
        self.CoordinateExtraction(
            filePaths=df['filePaths'],
            dirPaths=df['dirPaths']
        )

    def CoordinateExtraction(self, filePaths=None, dirPaths=None):
        # get inputs
        if filePaths is None:
            filePaths = Preprocess_Mask.StrToLst(strIn=self.ui.filePathsTxt_MCJZ.toPlainText())["listOut"]
        if dirPaths is None:
            dirPaths = Preprocess_Mask.StrToLst(strIn=self.ui.dirPathTxt_MCJZ.toPlainText())["listOut"]

        msg = "filePaths: {}".format(filePaths) + \
              "\ndirPaths: {}".format(dirPaths)

        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # looping each case:
        for filePath, dirPath in zip(filePaths, dirPaths):
            # check files exist and create folder
            if not os.path.isfile(filePath):
                self.UpdateMsgLog(
                    "File does not exist!!\n" + filePath
                )
                return
            # file name
            fileName = Save_Load_File.FilenameFromPath(filePath)
            # directory
            Save_Load_File.checkCreateDir(path=dirPath)

            # load file
            mask = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=filePath
            )

            # get all labels
            labels = numpy.array(Matrix_Math.matToListNoDulication(matData=mask.OriData))
            labelsNoZero = labels[numpy.where(labels != 0)]
            self.UpdateMsgLog("Labels are: " + str(labelsNoZero))

            # spcaing
            spacing = numpy.diag(numpy.asarray(mask.OriImag.GetSpacing()))

            # loop all labels
            for lbl in labelsNoZero:
                self.UpdateMsgLog('Working in label = ' + str(lbl))
                # extract position
                tissueXYZ = SITK_Numpy.SITK_NP_Arr()
                tissueXYZ.InSITKArr(SITKArr=mask.OriData)
                tissueXYZ.PositionMaskValues(
                    value=[lbl],
                    valueEnd=[0],
                    compare="equal"
                )
                tissueXYZ.PositionXYZ()
                tissueXYZ.Actual3DCoors(inSpace=spacing)

                # save results
                self.UpdateMsgLog('output:' + str(fileName + str(lbl)).replace('.', '_'))
                rtrnInfo = CFD_FEA_Post_Process.SaveDictOrArr(
                    inMat=tissueXYZ.Actual3DCoors,
                    fileName=str(fileName + str(lbl)).replace('.', '_'),
                    folderPath=dirPath,
                    addTime=False,
                    outNotNpyFile=True
                )
                self.UpdateMsgLog(rtrnInfo["Message"])

    def UpdateMsgLog(self, msg=""):

        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + str(msg) \
               + "\n################################################\n"

        if self.modelui:
            # update log and display message
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
        print(disp)
