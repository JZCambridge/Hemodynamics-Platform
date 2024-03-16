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
# sys.path.append('..\\..\\..\\Functions_JZ')
# Import functions
import Save_Load_File
import Image_Process_Functions
import Post_Image_Process_Functions
import Preprocess_Mask
import Use_Plt
import Pd_Funs
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
import skimage.morphology
from PySide2.QtUiTools import QUiLoader

##############################################################################

class MaskExtension:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseDirBtn_MEXJZ.clicked.connect(lambda: self.ChooseMaskDir())
        self.ui.saveDirBtn_MEXJZ.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.calculateSveBtn_MEXJZ.clicked.connect(lambda: self.Extension())
        self.ui.pushButton_BatchRun_MEXJZ.clicked.connect(lambda: self.BatchProcess())
        self.ui.pushButton_BatchTable_MEXJZ.clicked.connect(lambda: self.batchcsv())

        # initial definition
        self.lumMsk = None
        self.periMsk = None
        self.tissueMsk = None
        self.tissueShrk = None
        self.lumMskShrk = None
        self.periMskShrk = None
        self.tissueMskShrk = None
        self.name = None
        self.dir = None


    def ChooseMaskDir(self):
        # dir
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Load segmentation directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.openDirPathTxt_MEXJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose directory: \n{}".format(dirname))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Save directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.saveDirPathTxt_MEXJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose directory: \n{}".format(dirname))

    def Extension(self):
        # input range
        ## open
        openDir = self.ui.openDirPathTxt_MEXJZ.toPlainText()
        fileNames = Preprocess_Mask.StrToLst(strIn=self.ui.fileNamesTxt_MEXJZ.toPlainText())["listOut"]
        ## save
        saveDir = self.ui.saveDirPathTxt_MEXJZ.toPlainText()
        outRefs = Preprocess_Mask.StrToLst(strIn=self.ui.outRefsTxt_MEXJZ.toPlainText())["listOut"]
        ## first ext
        direct1s = Preprocess_Mask.StrToLst(strIn=self.ui.direct1sTxt_MSKJZ.toPlainText())["listOut"]
        sliceStrt1s = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStrt1sTxt_MSKJZ.toPlainText())["floatOut"]
        sliceStop1s = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStop1sTxt_MSKJZ.toPlainText())["floatOut"]
        refSlice1s = Preprocess_Mask.StrToLst(strIn=self.ui.refSlice1sTxt_MSKJZ.toPlainText())["floatOut"]
        circle1s = Preprocess_Mask.StrToLst(strIn=self.ui.circle1sTxt_MSKJZ.toPlainText())["booleanOut"]
        ## second ext
        direct2s = Preprocess_Mask.StrToLst(strIn=self.ui.direct2sTxt_MSKJZ.toPlainText())["listOut"]
        sliceStrt2s = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStrt2sTxt_MSKJZ.toPlainText())["floatOut"]
        sliceStop2s = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStop2sTxt_MSKJZ.toPlainText())["floatOut"]
        refSlice2s = Preprocess_Mask.StrToLst(strIn=self.ui.refSlice2sTxt_MSKJZ.toPlainText())["floatOut"]
        circle2s = Preprocess_Mask.StrToLst(strIn=self.ui.circle2sTxt_MSKJZ.toPlainText())["booleanOut"]
        ext2s = Preprocess_Mask.StrToLst(strIn=self.ui.ext2sTxt_MSKJZ.toPlainText())["booleanOut"]

        # check
        msgCheck = "openDir: {}".format(openDir) + \
                   "\nfileNames: {}".format(fileNames) + \
                   "\nsaveDir: {}".format(saveDir) + \
                   "\noutRefs: {}".format(outRefs) + \
                   "\ndirect1s: {}".format(direct1s) + \
                   "\nsliceStrt1s: {}".format(sliceStrt1s) + \
                   "\nsliceStop1s: {}".format(sliceStop1s) + \
                   "\nrefSlice1s: {}".format(refSlice1s) + \
                   "\ncircle1s: {}".format(circle1s) + \
                   "\ndirect2s: {}".format(direct2s) + \
                   "\nsliceStrt2s: {}".format(sliceStrt2s) + \
                   "\nsliceStop2s: {}".format(sliceStop2s) + \
                   "\nrefSlice2s: {}".format(refSlice2s) + \
                   "\ncircle2s: {}".format(circle2s) + \
                   "\next2s: {}".format(ext2s)

        print(msgCheck)

        # compare list are the same size
        compareShp = Post_Image_Process_Functions.CompareListDimension(
            lsts=[
                fileNames,
                outRefs,
                direct1s,
                sliceStrt1s,
                sliceStop1s,
                refSlice1s,
                circle1s,
                direct2s,
                sliceStrt2s,
                sliceStop2s,
                refSlice2s,
                circle2s,
                ext2s,
            ]
        )
        if compareShp["error"]:
            msg = "NOT all lines are the same shape: \n{}".format(compareShp["errorMessage"])
            # update message
            self.UpdateMsgLog(msg=msg)
            print(msg)
            return

        # loop
        shape = numpy.shape(fileNames)
        for case in range(shape[0]):
            # all input
            fileName = fileNames[case]
            outRef = outRefs[case]
            direct1 = direct1s[case]
            sliceStrt1 = sliceStrt1s[case]
            sliceStop1 = sliceStop1s[case]
            refSlice1 = refSlice1s[case]
            circle1 = circle1s[case]
            ext2 = ext2s[case]

            # Set file name
            filePath = Save_Load_File.DateFileName(
                Dir=openDir,
                fileName=fileName,
                extension=".nii.gz",
                appendDate=False
            )
            outFilePath = Save_Load_File.DateFileName(
                Dir=saveDir,
                fileName=outRef,
                extension=".nii.gz",
                appendDate=False
            )
            # load
            msk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=filePath["CombineName"]
            )

            # extension 1st extension
            ExtMask1 = Image_Process_Functions.MaskExtensionCircle(
                inMask=msk.OriData,
                direct=direct1,
                slcStrt=sliceStrt1,
                slcStp=sliceStop1,
                refSlc=refSlice1,
                circle=circle1
            )
            if ExtMask1["error"]:
                self.UpdateMsgLog(msg="First Extension: \n" + ExtMask1["errorMessage"])
                return

                # extension 2nd extension
            if ext2:
                # input
                direct2 = direct2s[case]
                sliceStrt2 = sliceStrt2s[case]
                sliceStop2 = sliceStop2s[case]
                refSlice2 = refSlice2s[case]
                circle2 = circle2s[case]
                ExtMask2 = Image_Process_Functions.MaskExtensionCircle(
                    inMask=ExtMask1["ExtendedMask"],
                    direct=direct2,
                    slcStrt=sliceStrt2,
                    slcStp=sliceStop2,
                    refSlc=refSlice2,
                    circle=circle2
                )
                if ExtMask2["error"]:
                    self.UpdateMsgLog(msg="Second Extension: \n" + ExtMask2["errorMessage"])
                    return

                # Save
                Save_Load_File.MatNIFTISave(MatData=ExtMask2["ExtendedMask"],
                                            imgPath=outFilePath["CombineName"],
                                            imgInfo=msk.OriImag,
                                            ConvertDType=True,
                                            refDataMat=msk.OriData)
            else:  # save
                # Save
                Save_Load_File.MatNIFTISave(MatData=ExtMask1["ExtendedMask"],
                                            imgPath=outFilePath["CombineName"],
                                            imgInfo=msk.OriImag,
                                            ConvertDType=True,
                                            refDataMat=msk.OriData)

            # update
            self.UpdateMsgLog(
                msg="Complete Extesion & Save: \n{}".format(
                    outFilePath["CombineName"]
                )
            )
            print("Complete Extesion & Save: \n{}".format(
                outFilePath["CombineName"]))

        # update
        self.UpdateMsgLog(msg="Complete ALL Extesion")
        print("Complete ALL Extesion")

    def ChooseBatchFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load csv file',
            fileTypes="All files (*.*);; Table files (*.csv *.txt) ;; More table files (*.xlsx *.xls *.xlsm)",
            fileObj=self.ui,
            qtObj=True
        )
        # set filename
        self.ui.batchTablePathTxt_MEXJZ.setPlainText(filename)

        # update
        self.UpdateMsgLog(
            msg="Choose Batch Table File: {}".format(filename)
        )

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.batchTablePathTxt_MEXJZ.setPlainText('{}'.format(filename))

    def BatchProcess(self, path=None):
        # input
        if path is None:
            path = self.ui.batchTablePathTxt_MEXJZ.toPlainText()

        # load table
        batchDataFrame = Pd_Funs.OpenDF(path, header=0)

        # loop
        rows = len(batchDataFrame["Input Mask Path"].tolist())
        for case in range(rows):
            # load all parameters
            maskInPath = batchDataFrame["Input Mask Path"].tolist()[case]
            maskOutPath = batchDataFrame["Output Mask Path"].tolist()[case]
            # first
            Auto1 = Save_Load_File.CheckTrue(batchDataFrame["First Automation"].tolist()[case])
            circle1 = Save_Load_File.CheckTrue(batchDataFrame["First Automation"].tolist()[case])
            direct1 = batchDataFrame["First Direction"].tolist()[case]
            sliceStrt1 = int(batchDataFrame["First Slice Start"].tolist()[case])
            sliceStop1 = int(batchDataFrame["First Slice Stop"].tolist()[case])
            refSlice1 = int(batchDataFrame["First Reference Slice"].tolist()[case])
            refDepth1 = int(batchDataFrame["First Reference Mask Depth"].tolist()[case])
            extSlices1 = int(batchDataFrame["First Extension Total Slices"].tolist()[case])
            # second
            do2 = Save_Load_File.CheckTrue(batchDataFrame["Second Extension"].tolist()[case])
            Auto2 = Save_Load_File.CheckTrue(batchDataFrame["Second Automation"].tolist()[case])
            circle2 = Save_Load_File.CheckTrue(batchDataFrame["Second Use Circle"].tolist()[case])
            direct2 = batchDataFrame["Second Direction"].tolist()[case]
            sliceStrt2 = int(batchDataFrame["Second Slice Start"].tolist()[case])
            sliceStop2 = int(batchDataFrame["Second Slice Stop"].tolist()[case])
            refSlice2 = int(batchDataFrame["Second Reference Slice"].tolist()[case])
            refDepth2 = int(batchDataFrame["Second Reference Mask Depth"].tolist()[case])
            extSlices2 = int(batchDataFrame["Second Extension Total Slices"].tolist()[case])

            # check directory
            fullParentDir, ParentDir = Save_Load_File.ParentDir(path=maskOutPath)
            Save_Load_File.ParentDir(path=fullParentDir)

            # load data
            msk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=maskInPath
            )

            # get all nonempty slices
            nonEmptySLices = None
            if Auto1 or Auto2:
                nonEmptySLices = Image_Process_Functions.NoneEmptySlices(msk.OriData) + 1  # ITK SNAP

            # process first
            if Auto1: # automatic up extension
                # find beginning slices
                print(nonEmptySLices[0] + refDepth1)
                print(refDepth1)
                print(nonEmptySLices[-1] >= (nonEmptySLices[0] + refDepth1))
                if nonEmptySLices[-1] >= (nonEmptySLices[0] + refDepth1):
                    sliceStop1 = nonEmptySLices[0] + refDepth1
                else:
                    sliceStop1 = nonEmptySLices[-1]

                refSlice1 = sliceStop1

                # find ending slices ITK_SNAP
                if 1 <= (sliceStop1 - extSlices1):
                    sliceStrt1 = sliceStop1 - extSlices1
                else:
                    sliceStrt1 = 1

            print(sliceStrt1, refSlice1, sliceStop1)

            # process first case
            ExtMask1 = Image_Process_Functions.MaskExtensionCircle(
                inMask=msk.OriData,
                direct=direct1,
                slcStrt=sliceStrt1,
                slcStp=sliceStop1,
                refSlc=refSlice1,
                circle=circle1
            )

            self.UpdateMsgLog(msg="First Extension: \n" + ExtMask1["errorMessage"])

            # process second
            if do2:
                if Auto2:  # automatic up extension
                    # find beginning slices
                    if nonEmptySLices[-2] >= (nonEmptySLices[-1] - refDepth2):
                        sliceStrt2 = nonEmptySLices[-1] - refDepth2
                    else:
                        sliceStrt2 = nonEmptySLices[-2]

                    refSlice2 = sliceStrt2

                    # find ending slices ITK_SNAP deal in func
                    sliceStop2 = sliceStrt2 + extSlices2

                # print(sliceStrt2, refSlice2, sliceStop2)

                # second
                ExtMask2 = Image_Process_Functions.MaskExtensionCircle(
                    inMask=ExtMask1["ExtendedMask"],
                    direct=direct2,
                    slcStrt=sliceStrt2,
                    slcStp=sliceStop2,
                    refSlc=refSlice2,
                    circle=circle2
                )

                self.UpdateMsgLog(msg="Second Extension: \n" + ExtMask2["errorMessage"])

                # Save
                Save_Load_File.MatNIFTISave(MatData=ExtMask2["ExtendedMask"],
                                            imgPath=maskOutPath,
                                            imgInfo=msk.OriImag,
                                            ConvertDType=True,
                                            refDataMat=msk.OriData)
            else:  # save
                # Save
                Save_Load_File.MatNIFTISave(MatData=ExtMask1["ExtendedMask"],
                                            imgPath=maskOutPath,
                                            imgInfo=msk.OriImag,
                                            ConvertDType=True,
                                            refDataMat=msk.OriData)

            # update
            self.UpdateMsgLog(
                msg="Complete Extesion & Save: \n{}".format(maskOutPath)
            )

        # update
        self.UpdateMsgLog(msg="Complete ALL Extesion")


    def UpdateMsgLog(self, msg=""):

        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + msg \
               + "\n################################################\n"

        # update log and display message
        if self.modelui:
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
        else:
            pass
        print(disp)