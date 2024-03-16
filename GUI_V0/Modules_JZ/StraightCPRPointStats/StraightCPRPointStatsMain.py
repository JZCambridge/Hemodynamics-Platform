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
import Use_Plt
import VTK_Functions
import VTK_Numpy
import QT_GUI
import Pd_Funs
import Matrix_Math
##############################################################################

##############################################################################
# Standard library
import skimage.measure
import numpy
import scipy.stats
import skimage.segmentation
import skimage.morphology
from multiprocessing import Pool
from datetime import datetime
import time
import scipy.ndimage
import copy
import pandas


##############################################################################

class StraightCPRPointStats:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.CSVPathBtn_SCPSJZ.clicked.connect(lambda: self.ChooseOpenCSVFile())
        self.ui.CalculateBtn_SCPSJZ.clicked.connect(lambda: self.FunctionChoose())

        self.InitPointStats()

    def InitPointStats(self):
        # initial definition
        self.outputData = None
        self.outputDataOnes = None
        self.CTA = None
        self.inMsk = None
        self.i = 0

        self.ConnectivityFilterData = None
        self.initConnectFilterVals = None
        self.ImageBasicProcessingData = None
        self.Gaussian3DData = None
        self.SegmentFilterThresData = None
        self.ManualFillData = None

        self.ACWEData = None
        self.ImageSegmentationFilterData = None
        self.thresHUOnes = None
        self.filterThresHUOnes = None
        self.activeContourOnes = None
        self.activeContourFOnes = None
        self.activeContourFVals = None

        self.intermediateData = None

        self.AddfillReplaceMask = None

        self.outLog = ""

    def FunctionChoose(self):
        # init
        funChoice = self.ui.funCBox_SCPSJZ.currentText()

        if funChoice == "Region Stats":
            self.CalculateStats()
        elif funChoice == "Point Data":
            self.ExtractPointValue()

    def ChooseOpenCSVFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; Table files (*.csv *.txt) ;; More table files (*.xlsx *.xls *.xlsm)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.CSVPathTxt_SCPSJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose table file:\n{}".format(filename))

    def ExtractPointValue(self):
        # init
        caseCSVFile = self.ui.CSVPathTxt_SCPSJZ.toPlainText()

        # read cases
        dfCases = Pd_Funs.OpenDF(
            inPath=caseCSVFile,
            header=0,
            usecols=None
        )

        for OutDir, \
            OutFileName, \
            ReferenceCSV, \
            parameterNos \
                in zip(
            dfCases['OutDirs'].tolist(),
            dfCases['OutFileNames'].tolist(),
            dfCases['ReferenceCSVs'].tolist(),
            dfCases['Parameters'].tolist()
        ):

            # load each csv case
            dfCase = Pd_Funs.OpenDF(
                inPath=ReferenceCSV,
                header=0,
                usecols=None,
                index_col=None
            )

            # df output
            dfOut = pandas.DataFrame()

            for row in dfCase.index:
                columnPrefixs = []
                inOriImgs = []
                # lists of files and references
                for i in range(int(parameterNos)):
                    columnPrefixs.append(dfCase["Parameter" + str(i)][row])
                    inOriImgs.append(dfCase["ParameterFiles" + str(i)][row])

                series = Matrix_Math.ExtractPointValue(
                    positionDepths=dfCase['positionDepths'][row],
                    positionRows=dfCase['positionRows'][row],
                    positionColumns=dfCase['positionColumns'][row],
                    positionDepthsSecond=dfCase['positionDepthsSecond'][row],
                    positionRowsSecond=dfCase['positionRowsSecond'][row],
                    positionColumnsSecond=dfCase['positionColumnsSecond'][row],
                    inFiles=inOriImgs,
                    columnPrefixs=columnPrefixs,
                    caseNameRef=dfCase["CaseReferences"][row],
                    index=row,
                    saveCSV=False,
                    outDir="",
                    outNameRef=""
                )

                if row == 0:
                    dfOut = series["dataFrame"].copy()
                else:
                    dfOut = dfOut.append(series["dataFrame"])

            # save
            outFile = OutDir + "/" + OutFileName + ".csv"
            Pd_Funs.SaveDF(
                outPath=outFile,
                pdIn=dfOut,
                header=True,
                index=False
            )

    def CalculateStats(self):
        # get inputs
        tableFile = self.ui.CSVPathTxt_SCPSJZ.toPlainText()
        compareOriImg = self.ui.compareOriImgCheckBox_SCPSJZ.isChecked()
        absVal = self.ui.absValCheckBox_SCPSJZ.isChecked()
        outPut995 = self.ui.outPut995CheckBox_SCPSJZ.isChecked()
        outPut99 = self.ui.outPut99CheckBox_SCPSJZ.isChecked()
        outPutABS = self.ui.outPutABSCheckBox_SCPSJZ.isChecked()
        outPutABS995 = self.ui.outPutABS995CheckBox_SCPSJZ.isChecked()
        outPutABS99 = self.ui.outPutABS99CheckBox_SCPSJZ.isChecked()
        saveDiffImage = self.ui.saveDiffImageCheckBox_SCPSJZ.isChecked()
        sameMask = self.ui.sameMaskCheckBox_SCPSJZ.isChecked()
        direction = self.ui.directionCBox_SCPSJZ.currentText()
        ballRadius = float(self.ui.ballRadiusLineTxt_SCPSJZ.text())
        noCompare = self.ui.noCompareCheckBox_SCPSJZ.isChecked()
        percentile = float(self.ui.percentileLineTxt_SCPSJZ.text())

        # load DF
        dfCases = Pd_Funs.OpenDF(
            inPath=tableFile,
            header=0,
            usecols=None
        )

        if saveDiffImage:
            outCheckDirs = dfCases['OutCheckDirs'].tolist()
        else:
            outCheckDirs = [None] * len(dfCases['OutDirs'].tolist())

        for OutDir, \
            OutFileName, \
            ReferenceCSV, \
            parameterNos, \
            outCheckDir, \
            outMin, \
            outMax, \
            outPTP, \
            outQ1, \
            outQ3, \
            outIQR, \
            outMedian, \
            outMean, \
            outSTD, \
            outVar, \
            outKurt, \
            outSkew, \
            outMode, \
            outRMS, \
            outHMean, \
            outGMean, \
            outTriMean, \
            outDecile1, \
            outDecile2, \
            outDecile3, \
            outDecile4, \
            outDecile6, \
            outDecile7, \
            outDecile8, \
            outDecile9, \
            outSE, \
            outEnergy, \
            outEntropy \
                in zip(
            dfCases['OutDirs'].tolist(),
            dfCases['OutFileNames'].tolist(),
            dfCases['ReferenceCSVs'].tolist(),
            dfCases['Parameters'].tolist(),
            outCheckDirs,
            dfCases['Min'].tolist(),
            dfCases['Max'].tolist(),
            dfCases['PTP'].tolist(),
            dfCases['Q1'].tolist(),
            dfCases['Q3'].tolist(),
            dfCases['IQR'].tolist(),
            dfCases['Median'].tolist(),
            dfCases['Mean'].tolist(),
            dfCases['STD'].tolist(),
            dfCases['Variance'].tolist(),
            dfCases['Kurtosis'].tolist(),
            dfCases['Skew'].tolist(),
            dfCases['Mode'].tolist(),
            dfCases['RMS'].tolist(),
            dfCases['HMean'].tolist(),
            dfCases['GMean'].tolist(),
            dfCases['TriMean'].tolist(),
            dfCases['Decile1'].tolist(),
            dfCases['Decile2'].tolist(),
            dfCases['Decile3'].tolist(),
            dfCases['Decile4'].tolist(),
            dfCases['Decile6'].tolist(),
            dfCases['Decile7'].tolist(),
            dfCases['Decile8'].tolist(),
            dfCases['Decile9'].tolist(),
            dfCases['SE'].tolist(),
            dfCases['Energy'].tolist(),
            dfCases['Entropy'].tolist()
        ):

            # load each csv case
            dfCase = Pd_Funs.OpenDF(
                inPath=ReferenceCSV,
                header=0,
                usecols=None,
                index_col=None
            )

            # df output
            dfOut = pandas.DataFrame()

            for row in dfCase.index:
                inMasks = []
                inImgs = []
                columnPrefixs = []
                inOriMasks = []
                inOriImgs = []
                contours = []
                startSlices = []
                finishSlices = []
                startRows = []
                finishRows = []
                startColumns = []
                finishColumns = []

                # lists of files and references
                for i in range(int(parameterNos)):
                    columnPrefixs.append(dfCase["Parameter" + str(i)][row])
                    inOriImgs.append(dfCase["BaseParameterFiles" + str(i)][row])
                    inOriMasks.append(dfCase["BaseMaskFiles" + str(i)][row])
                    inImgs.append(dfCase["CompareParameterFiles" + str(i)][row])
                    inMasks.append(dfCase["CompareMaskFiles" + str(i)][row])
                    contours.append(int(dfCase["Contours" + str(i)][row]))
                    startSlices.append(int(dfCase["StartSlices" + str(i)][row]) - 1)
                    finishSlices.append(int(dfCase["FinishSlices" + str(i)][row]) - 1)
                    startRows.append(int(dfCase["StartRows" + str(i)][row]) - 1)
                    finishRows.append(int(dfCase["FinishRows" + str(i)][row]) - 1)
                    startColumns.append(int(dfCase["StartColumns" + str(i)][row]) - 1)
                    finishColumns.append(int(dfCase["FinishColumns" + str(i)][row]) - 1)

                series = Matrix_Math.IntensityStats3DImgPoints(
                    startSlices=startSlices,
                    finishSlices=finishSlices,
                    startRows=startRows,
                    finishRows=finishRows,
                    startColumns=startColumns,
                    finishColumns=finishColumns,
                    inMasks=inMasks,
                    inImgs=inImgs,
                    columnPrefixs=columnPrefixs,
                    slicingDirect=direction,
                    caseNameRef=dfCase["CaseReferences"][row],
                    contours=contours,
                    ballRadius=ballRadius,
                    compareOriImg=compareOriImg,
                    inOriMasks=inOriMasks,
                    inOriImgs=inOriImgs,
                    index=row,
                    outDir=outCheckDir,
                    saveDiffImage=saveDiffImage,
                    outPut995=outPut995,
                    outPut99=outPut99,
                    outPutABS=outPutABS,
                    outPutABS995=outPutABS995,
                    outPutABS99=outPutABS99,
                    sameMask=sameMask,
                    absVal=absVal,
                    percentile=percentile,
                    noCompare=noCompare,
                    outMin=int(outMin) == 1,
                    outMax=int(outMax) == 1,
                    outPTP=int(outPTP) == 1,
                    outQ1=int(outQ1) == 1,
                    outQ3=int(outQ3) == 1,
                    outIQR=int(outIQR) == 1,
                    outMedian=int(outMedian) == 1,
                    outMean=int(outMean) == 1,
                    outSTD=int(outSTD) == 1,
                    outVar=int(outVar) == 1,
                    outKurt=int(outKurt) == 1,
                    outSkew=int(outSkew) == 1,
                    outMode=int(outMode) == 1,
                    outRMS=int(outRMS) == 1,
                    outHMean=int(outHMean) == 1,
                    outGMean=int(outGMean) == 1,
                    outTriMean=int(outTriMean) == 1,
                    outDecile1=int(outDecile1) == 1,
                    outDecile2=int(outDecile2) == 1,
                    outDecile3=int(outDecile3) == 1,
                    outDecile4=int(outDecile4) == 1,
                    outDecile6=int(outDecile6) == 1,
                    outDecile7=int(outDecile7) == 1,
                    outDecile8=int(outDecile8) == 1,
                    outDecile9=int(outDecile9) == 1,
                    outSE=int(outSE) == 1,
                    outEnergy=int(outEnergy) == 1,
                    outEntropy=int(outEntropy) == 1
                )

                if row == 0:
                    dfOut = series["dataFrame"].copy()
                else:
                    dfOut = dfOut.append(series["dataFrame"])

            # save
            outFile = OutDir + "/" + OutFileName + ".csv"
            Pd_Funs.SaveDF(
                outPath=outFile,
                pdIn=dfOut,
                header=True,
                index=False
            )

            # update message
            self.UpdateMsgLog(
                msg="Output file:\n{}".format(
                    outFile
                )
            )

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
        self.outLog += disp
        print(msg)
