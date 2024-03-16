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

import numpy
import pandas

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
import Matrix_Math
import Pd_Funs
##############################################################################

##############################################################################
# Standard libs
import os
from datetime import datetime
import copy
import yaml

import collections
import csv
import logging
import os
import SimpleITK
import radiomics
from radiomics import featureextractor


##############################################################################

class SegmentInforExtract:
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseOpenCTADirBtn_SIEJZ.clicked.connect(lambda: self.ChooseCTADir())
        self.ui.chooseOpenMskDirBtn_SIEJZ.clicked.connect(lambda: self.ChooseMaskDir())
        self.ui.chooseSaveDirBtn_SIEJZ.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.extractBtn_SIEJZ.clicked.connect(lambda: self.Extract())

        self.ui.outDirPRBtn_SIEJZ.clicked.connect(lambda: self.ChooseOutDirPR())
        self.ui.YMALBtn_SIEJZ.clicked.connect(lambda: self.GenerateRunPR())
        self.ui.tablePRBtn_SIEJZ.clicked.connect(lambda: self.ChooseTableFile())

        self.ui.tablePathB2SBtn_SIEJZ.clicked.connect(lambda: self.ChooseTableFileB2S())
        self.ui.tableFolderPathB2SBtn_SIEJZ.clicked.connect(lambda: self.ChooseInputDirB2S())
        self.ui.BatchB2SBtn_SIEJZ.clicked.connect(lambda: self.BatchB2S())
        self.ui.StatsB2SBtn_SIEJZ.clicked.connect(lambda: self.Radiomics2DStatB2S())
        self.ui.Choose2DOutputDirB2SBtn_SIEJZ.clicked.connect(lambda: self.Choose2DOutputDirB2S())

        self.ui.TableXCBtn_SIEJZ.clicked.connect(lambda: self.ChooseTableXCPath())
        self.ui.saveTableXCBtn_SIEJZ.clicked.connect(lambda: self.ChooseSaveFile())
        self.ui.CenterlineBtn_SIEJZ.clicked.connect(lambda: self.CenterlinePhase())
        self.ui.XsectionBtn_SIEJZ.clicked.connect(lambda: self.XsectionPhase())

        self.ui.ChooseTableFileFAIBtn_SIEJZ.clicked.connect(lambda: self.ChooseTableFile_FAI())
        self.ui.ChooseSaveFileFAIBtn_SIEJZ.clicked.connect(lambda: self.ChooseSaveFile_FAI())
        self.ui.FAICalculationBtn_SIEJZ.clicked.connect(lambda: self.FAICalculation())

        self.InitPRDict()

    def InitPRDict(self):
        self.ymalDict = {
            'imageType': {},
            'featureClass': {},
            'setting': {}
        }

    """
    ##############################################################################
    # Self-written slice wise information extraction
    ##############################################################################
    """

    def ChooseCTADir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose medical image directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.CTADirPathTxt_SIEJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose medical image directory:\n{}".format(dirname))

    def ChooseMaskDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose mask directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.maskDirPathTxt_SIEJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose medical image segmentation dir:\n{}".format(dirname))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Save data directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.saveDirPathTxt_SIEJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose saving dir:\n{}".format(dirname))

    def Extract(self):
        # convert everything to list/str
        ## input files
        inCTADir = self.ui.CTADirPathTxt_SIEJZ.toPlainText()
        inMskDir = self.ui.maskDirPathTxt_SIEJZ.toPlainText()
        CTAFiles = Preprocess_Mask.StrToLst(self.ui.CTAFilesTxt_SIEJZ.toPlainText())["listOut"]
        mskFiles = Preprocess_Mask.StrToLst(self.ui.mskFilesTxt_SIEJZ.toPlainText())["listOut"]
        ## segmentation
        maskVals = Preprocess_Mask.StrToLst(self.ui.maskValsTxt_SIEJZ.toPlainText())["listOut"]  # !!!
        ## dilation
        dilDirect = self.ui.directBtnGrp_SIEJZ.checkedButton().text()
        removeSegment = self.ui.removeSegmentBtnGrp_SIEJZ.checkedButton().text() == "Yes"
        dilationType = self.ui.dilationTypeBtnGrp_SIEJZ.checkedButton().text()
        dilationTimes = self.ui.dilationTimesTxt_SIEJZ.text()
        ## dealing with dilation
        try:
            dilationTimes = int(dilationTimes)
        except:
            # update message
            self.UpdateMsgLog(
                msg="Cannot load dilation times!"
            )
            return
        ## integer
        if dilationTimes <= 0:
            # update message
            self.UpdateMsgLog(
                msg="DilationTimes is <= 0!"
            )
            return

        ## stats
        outputIntStats = self.ui.outputIntStatsBtnGrp_SIEJZ.checkedButton().text() == "Yes"
        outputShpStats = self.ui.outputShpStatsBtnGrp_SIEJZ.checkedButton().text() == "Yes"
        stats2DDirect = self.ui.stats2DBtnGrp_SIEJZ.checkedButton().text()
        noOriThres = self.ui.noOriThresStatsBtnGrp_SIEJZ.checkedButton().text() == "Yes"
        imgThres = self.ui.imgThresStatsBtnGrp_SIEJZ.checkedButton().text() == "Yes"
        thresStrt = float(self.ui.thresStrtLineTxt_SIEJZ.text())
        thresStop = float(self.ui.thresStopLineTxt_SIEJZ.text())
        ## output
        outputDirInit = self.ui.saveDirPathTxt_SIEJZ.toPlainText()
        nameRefs = Preprocess_Mask.StrToLst(strIn=self.ui.nameRefTxt_SIEJZ.toPlainText())["listOut"]

        # Compare list length
        compareShp = Post_Image_Process_Functions.CompareListDimension(
            lsts=[
                CTAFiles,
                mskFiles,
                nameRefs
            ]
        )
        if compareShp["error"]:
            # update message
            self.UpdateMsgLog(msg=compareShp["errorMessage"])
            return

        # load each case
        listLen = len(CTAFiles)
        for list in range(listLen):
            # each case
            CTAFile = CTAFiles[list]
            mskFile = mskFiles[list]
            nameRef = nameRefs[list]

            # input file
            CTAPath = Save_Load_File.AppendLists(
                [inCTADir],
                [CTAFile],
                sep="/"
            )["combineList"][0]
            mskPath = Save_Load_File.AppendLists(
                [inMskDir],
                [mskFile],
                sep="/"
            )["combineList"][0]
            # print(CTAPath)
            # print(mskPath)

            # load data
            CTAData = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=CTAPath
            )
            mskData = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=mskPath
            )

            ## check same shape
            compareShp = Post_Image_Process_Functions.CompareArrShape(
                dataMat1=CTAData.OriData,
                dataMat2=mskData.OriData,
                DialogWarn=False
            )
            ## Not same shape
            if compareShp["error"]:
                # update message
                self.UpdateMsgLog(
                    msg=compareShp["errorMessage"]
                )
                return
            else:
                # update message
                self.UpdateMsgLog(
                    msg="Load data:\n{} \n{}".format(
                        CTAPath,
                        mskPath
                    )
                )

            # Create directory with name reference
            outputDirNameRef = outputDirInit + "/" + nameRef
            ## create dir
            checkCreate = Save_Load_File.checkCreateDir(
                path=outputDirNameRef
            )
            if checkCreate["error"]:
                # update message
                self.UpdateMsgLog(
                    msg=checkCreate["errorMessage"]
                )
                return

            # each case filtering
            maskValsLen = len(maskVals)
            for item in range(maskValsLen):
                # filter value
                ## value
                maskVal = maskVals[item]

                # Create directory with name reference
                outputDirMaskVal = outputDirNameRef + "/" + "M" + maskVal
                ## create dir
                checkCreate = Save_Load_File.checkCreateDir(
                    path=outputDirMaskVal
                )
                if checkCreate["error"]:
                    # update message
                    self.UpdateMsgLog(
                        msg=checkCreate["errorMessage"]
                    )
                    return

                if maskVal == "All":  # filter all
                    mskVals, mskOnes = Image_Process_Functions.FilterData(
                        rangStarts=[0],
                        rangStops=[0],
                        dataMat=mskData.OriData,
                        funType="not single value",
                        ConvertVTKType=False
                    )
                else:
                    ## deal with non-number
                    try:
                        maskValInt = int(maskVal)
                    except:
                        # update message
                        self.UpdateMsgLog(
                            msg="Cannot load segmentation values!"
                        )
                        return

                    ## integer
                    if maskValInt < 0:
                        # update message
                        self.UpdateMsgLog(
                            msg="Warning segmentation value is <= 0!"
                        )

                    # filter data
                    mskVals, mskOnes = Image_Process_Functions.FilterData(
                        rangStarts=[maskValInt],
                        rangStops=[0],
                        dataMat=mskData.OriData,
                        funType="single value",
                        ConvertVTKType=False
                    )

                # loop through dilation
                oldMask = copy.deepcopy(mskVals)
                previousMask = copy.deepcopy(mskVals)
                currentMask = copy.deepcopy(mskVals)
                for dilation in range(dilationTimes + 1):  # start from 0
                    # create folder
                    # Create directory with name reference
                    outputDir = outputDirMaskVal + "/" + "D" + str(dilation)
                    ## create dir
                    checkCreate = Save_Load_File.checkCreateDir(
                        path=outputDir
                    )
                    if checkCreate["error"]:
                        # update message
                        self.UpdateMsgLog(
                            msg=checkCreate["errorMessage"]
                        )
                        return

                    if dilation == 0:  # original volume extract information
                        # mask information all inside
                        maskCTAData = (currentMask != 0) * CTAData.OriData

                        # filtering
                        if noOriThres:
                            print("Remove original image with thresholding")
                            maskCTAData, _ = Image_Process_Functions.FilterData(
                                rangStarts=[thresStrt],
                                rangStops=[thresStop],
                                dataMat=maskCTAData,
                                funType="boundary"
                            )

                        # output and save
                        ## Set file name
                        CTAOutPath = Save_Load_File.DateFileName(
                            Dir=outputDir,
                            fileName=nameRef + "CTA" + maskVal + "_" + "KIN"
                                     + str(dilation) + dilDirect,
                            extension=".nii.gz",
                            appendDate=False
                        )
                        mskOutPath = Save_Load_File.DateFileName(
                            Dir=outputDir,
                            fileName=nameRef + "Msk" + maskVal + "_" + "KIN"
                                     + str(dilation) + dilDirect,
                            extension=".nii.gz",
                            appendDate=False
                        )

                        # Save
                        Save_Load_File.MatNIFTISave(
                            MatData=maskCTAData,
                            imgPath=CTAOutPath["CombineName"],
                            imgInfo=CTAData.OriImag,
                            ConvertDType=True,
                            refDataMat=CTAData.OriData
                        )
                        Save_Load_File.MatNIFTISave(
                            MatData=currentMask,
                            imgPath=mskOutPath["CombineName"],
                            imgInfo=CTAData.OriImag,
                            ConvertDType=True,
                            refDataMat=CTAData.OriData
                        )

                        # stats
                        if outputIntStats:
                            Matrix_Math.IntensityStats3DImgSlice(
                                inImg=CTAData.OriData,
                                inMask=currentMask,
                                slicingDirect=stats2DDirect,
                                saveCsv=True,
                                outDir=outputDir,
                                outNameRef=nameRef + "CTA" + maskVal + "_" + "KIN"
                                           + "{}".format(dilation) + dilDirect,
                                filterThres=noOriThres,
                                thresStart=[thresStrt],
                                thresStp=[thresStop],
                                outRefName=nameRef + "CTA" + maskVal + "_" + "KIN"
                                           + "{}".format(dilation) + dilDirect
                            )
                        if outputShpStats:
                            Matrix_Math.VolumeStats3DImgSlice(
                                inMask=currentMask,
                                slicingDirect=stats2DDirect,
                                saveCsv=True,
                                outDir=outputDir,
                                outNameRef=nameRef + "CTA" + maskVal + "_" + "KIN"
                                           + "{}".format(dilation) + dilDirect,
                                outRefName=nameRef + "CTA" + maskVal + "_" + "KIN"
                                           + "{}".format(dilation) + dilDirect
                            )
                    else:
                        # dilation
                        if dilationType == "Voxel":
                            ## store mask
                            previousMask = copy.deepcopy(currentMask)
                            ## dilation
                            err, currentMask = Image_Process_Functions.DiskDilate(
                                dataMat=oldMask,
                                Thres=0,
                                dilateIncre=dilation,
                                binaryMsk=False,
                                axisChoice=dilDirect
                            )
                            # mask information all inside
                            maskCTAData = (currentMask != 0) * CTAData.OriData

                            # filtering
                            if imgThres:
                                print("Remove image with thresholding")
                                maskCTAData, _ = Image_Process_Functions.FilterData(
                                    rangStarts=[thresStrt],
                                    rangStops=[thresStop],
                                    dataMat=maskCTAData,
                                    funType="boundary"
                                )

                            # output and save
                            ## Set file name
                            CTAOutPath = Save_Load_File.DateFileName(
                                Dir=outputDir,
                                fileName=nameRef + "CTA" + maskVal + "_" + "KIV"
                                         + str(dilation) + dilDirect,
                                extension=".nii.gz",
                                appendDate=False
                            )
                            mskOutPath = Save_Load_File.DateFileName(
                                Dir=outputDir,
                                fileName=nameRef + "Msk" + maskVal + "_" + "KIV"
                                         + str(dilation) + dilDirect,
                                extension=".nii.gz",
                                appendDate=False
                            )
                            # Save
                            Save_Load_File.MatNIFTISave(
                                MatData=maskCTAData,
                                imgPath=CTAOutPath["CombineName"],
                                imgInfo=CTAData.OriImag,
                                ConvertDType=True,
                                refDataMat=CTAData.OriData
                            )
                            Save_Load_File.MatNIFTISave(
                                MatData=currentMask,
                                imgPath=mskOutPath["CombineName"],
                                imgInfo=CTAData.OriImag,
                                ConvertDType=True,
                                refDataMat=CTAData.OriData
                            )

                            # Remove inside
                            if removeSegment:
                                # only remove initial mask
                                removeOldMask = Image_Process_Functions.RemoveFillEdge(
                                    inMsk=currentMask,
                                    fillMsk=oldMask
                                )["edgeMask"]
                                ## mask information all inside
                                removeOldCTAData = (removeOldMask != 0) * CTAData.OriData

                                # filtering
                                if imgThres:
                                    print("Remove image with thresholding")
                                    removeOldCTAData, _ = Image_Process_Functions.FilterData(
                                        rangStarts=[thresStrt],
                                        rangStops=[thresStop],
                                        dataMat=removeOldCTAData,
                                        funType="boundary"
                                    )

                                ## output and save
                                ### Set file name
                                CTAOutPath = Save_Load_File.DateFileName(
                                    Dir=outputDir,
                                    fileName=nameRef + "CTA" + maskVal + "_" + "RIV"
                                             + str(dilation) + dilDirect,
                                    extension=".nii.gz",
                                    appendDate=False
                                )
                                mskOutPath = Save_Load_File.DateFileName(
                                    Dir=outputDir,
                                    fileName=nameRef + "Msk" + maskVal + "_" + "RIV"
                                             + str(dilation) + dilDirect,
                                    extension=".nii.gz",
                                    appendDate=False
                                )
                                # Save
                                Save_Load_File.MatNIFTISave(
                                    MatData=removeOldCTAData,
                                    imgPath=CTAOutPath["CombineName"],
                                    imgInfo=CTAData.OriImag,
                                    ConvertDType=True,
                                    refDataMat=CTAData.OriData
                                )
                                Save_Load_File.MatNIFTISave(
                                    MatData=removeOldMask,
                                    imgPath=mskOutPath["CombineName"],
                                    imgInfo=CTAData.OriImag,
                                    ConvertDType=True,
                                    refDataMat=CTAData.OriData
                                )
                                ## stats
                                if outputIntStats:
                                    Matrix_Math.IntensityStats3DImgSlice(
                                        inImg=CTAData.OriData,
                                        inMask=removeOldMask,
                                        slicingDirect=stats2DDirect,
                                        saveCsv=True,
                                        outDir=outputDir,
                                        outNameRef=nameRef + "CTA" + maskVal + "_" + "RIV"
                                                   + str(dilation) + dilDirect,
                                        filterThres=imgThres,
                                        thresStart=[thresStrt],
                                        thresStp=[thresStop],
                                        outRefName=nameRef + "CTA" + maskVal + "_" + "RIV"
                                                   + str(dilation) + dilDirect
                                    )

                                # single layer
                                removePreviousMask = Image_Process_Functions.RemoveFillEdge(
                                    inMsk=currentMask,
                                    fillMsk=previousMask
                                )["edgeMask"]
                                ## mask information all inside
                                removePreviousCTAData = (removePreviousMask != 0) * CTAData.OriData

                                # filtering
                                if imgThres:
                                    print("Remove image with thresholding")
                                    removePreviousCTAData, _ = Image_Process_Functions.FilterData(
                                        rangStarts=[thresStrt],
                                        rangStops=[thresStop],
                                        dataMat=removePreviousCTAData,
                                        funType="boundary"
                                    )

                                ## output and save
                                ### Set file name
                                CTAOutPath = Save_Load_File.DateFileName(
                                    Dir=outputDir,
                                    fileName=nameRef + "CTA" + maskVal + "_" + "SLV"
                                             + str(dilation) + dilDirect,
                                    extension=".nii.gz",
                                    appendDate=False
                                )
                                mskOutPath = Save_Load_File.DateFileName(
                                    Dir=outputDir,
                                    fileName=nameRef + "Msk" + maskVal + "_" + "SLV"
                                             + str(dilation) + dilDirect,
                                    extension=".nii.gz",
                                    appendDate=False
                                )
                                # Save
                                Save_Load_File.MatNIFTISave(
                                    MatData=removePreviousCTAData,
                                    imgPath=CTAOutPath["CombineName"],
                                    imgInfo=CTAData.OriImag,
                                    ConvertDType=True,
                                    refDataMat=CTAData.OriData
                                )
                                Save_Load_File.MatNIFTISave(
                                    MatData=removePreviousMask,
                                    imgPath=mskOutPath["CombineName"],
                                    imgInfo=CTAData.OriImag,
                                    ConvertDType=True,
                                    refDataMat=CTAData.OriData
                                )
                                ## stats
                                if outputIntStats:
                                    Matrix_Math.IntensityStats3DImgSlice(
                                        inImg=CTAData.OriData,
                                        inMask=removePreviousCTAData,
                                        slicingDirect=stats2DDirect,
                                        saveCsv=True,
                                        outDir=outputDir,
                                        outNameRef=nameRef + "CTA" + maskVal + "_" + "SLV"
                                                   + str(dilation) + dilDirect,
                                        filterThres=imgThres,
                                        thresStart=[thresStrt],
                                        thresStp=[thresStop],
                                        outRefName=nameRef + "CTA" + maskVal + "_" + "SLV"
                                                   + str(dilation) + dilDirect
                                    )

                                # update message
                                self.UpdateMsgLog(
                                    msg="Complete remove inside"
                                )

                        elif dilationType == "Diameter":
                            print("Diamter dilation!")
                            ## store mask
                            previousMask = copy.deepcopy(currentMask)
                            ## dilation Disk
                            err, currentMask = Image_Process_Functions.DiskDilateDiameter(
                                dataMat=oldMask,
                                Thres=0,
                                dilateIncreFac=dilation,
                                binaryMsk=False,
                                axisChoice=dilDirect
                            )
                            # mask information all inside
                            maskCTAData = (currentMask != 0) * CTAData.OriData

                            # filtering
                            if imgThres:
                                print("Remove image with thresholding")
                                maskCTAData, _ = Image_Process_Functions.FilterData(
                                    rangStarts=[thresStrt],
                                    rangStops=[thresStop],
                                    dataMat=maskCTAData,
                                    funType="boundary"
                                )

                            # output and save
                            ## Set file name
                            CTAOutPath = Save_Load_File.DateFileName(
                                Dir=outputDir,
                                fileName=nameRef + "CTA" + maskVal + "_" + "KID"
                                         + str(dilation) + dilDirect,
                                extension=".nii.gz",
                                appendDate=False
                            )
                            mskOutPath = Save_Load_File.DateFileName(
                                Dir=outputDir,
                                fileName=nameRef + "Msk" + maskVal + "_" + "KID"
                                         + str(dilation) + dilDirect,
                                extension=".nii.gz",
                                appendDate=False
                            )
                            # Save
                            Save_Load_File.MatNIFTISave(
                                MatData=maskCTAData,
                                imgPath=CTAOutPath["CombineName"],
                                imgInfo=CTAData.OriImag,
                                ConvertDType=True,
                                refDataMat=CTAData.OriData
                            )
                            Save_Load_File.MatNIFTISave(
                                MatData=currentMask,
                                imgPath=mskOutPath["CombineName"],
                                imgInfo=CTAData.OriImag,
                                ConvertDType=True,
                                refDataMat=CTAData.OriData
                            )

                            # Remove inside
                            if removeSegment:
                                # only remove initial mask
                                removeOldMask = Image_Process_Functions.RemoveFillEdge(
                                    inMsk=currentMask,
                                    fillMsk=oldMask
                                )["edgeMask"]
                                ## mask information all inside
                                removeOldCTAData = (removeOldMask != 0) * CTAData.OriData

                                # filtering
                                if imgThres:
                                    print("Remove image with thresholding")
                                    removeOldCTAData, _ = Image_Process_Functions.FilterData(
                                        rangStarts=[thresStrt],
                                        rangStops=[thresStop],
                                        dataMat=removeOldCTAData,
                                        funType="boundary"
                                    )

                                ## output and save
                                ### Set file name
                                CTAOutPath = Save_Load_File.DateFileName(
                                    Dir=outputDir,
                                    fileName=nameRef + "CTA" + maskVal + "_" + "RID"
                                             + str(dilation) + dilDirect,
                                    extension=".nii.gz",
                                    appendDate=False
                                )
                                mskOutPath = Save_Load_File.DateFileName(
                                    Dir=outputDir,
                                    fileName=nameRef + "Msk" + maskVal + "_" + "RID"
                                             + str(dilation) + dilDirect,
                                    extension=".nii.gz",
                                    appendDate=False
                                )
                                # Save
                                Save_Load_File.MatNIFTISave(
                                    MatData=removeOldCTAData,
                                    imgPath=CTAOutPath["CombineName"],
                                    imgInfo=CTAData.OriImag,
                                    ConvertDType=True,
                                    refDataMat=CTAData.OriData
                                )
                                Save_Load_File.MatNIFTISave(
                                    MatData=removeOldMask,
                                    imgPath=mskOutPath["CombineName"],
                                    imgInfo=CTAData.OriImag,
                                    ConvertDType=True,
                                    refDataMat=CTAData.OriData
                                )
                                ## stats
                                if outputIntStats:
                                    Matrix_Math.IntensityStats3DImgSlice(
                                        inImg=CTAData.OriData,
                                        inMask=removeOldMask,
                                        slicingDirect=stats2DDirect,
                                        saveCsv=True,
                                        outDir=outputDir,
                                        outNameRef=nameRef + "CTA" + maskVal + "_" + "RID"
                                                   + str(dilation) + dilDirect,
                                        filterThres=imgThres,
                                        thresStart=[thresStrt],
                                        thresStp=[thresStop],
                                        outRefName=nameRef + "CTA" + maskVal + "_" + "RID"
                                                   + str(dilation) + dilDirect
                                    )

                                # single layer
                                removePreviousMask = Image_Process_Functions.RemoveFillEdge(
                                    inMsk=currentMask,
                                    fillMsk=previousMask
                                )["edgeMask"]
                                ## mask information all inside
                                removePreviousCTAData = (removePreviousMask != 0) * CTAData.OriData

                                # filtering
                                if imgThres:
                                    print("Remove image with thresholding")
                                    removePreviousCTAData, _ = Image_Process_Functions.FilterData(
                                        rangStarts=[thresStrt],
                                        rangStops=[thresStop],
                                        dataMat=removePreviousCTAData,
                                        funType="boundary"
                                    )

                                ## output and save
                                ### Set file name
                                CTAOutPath = Save_Load_File.DateFileName(
                                    Dir=outputDir,
                                    fileName=nameRef + "CTA" + maskVal + "_" + "SLD"
                                             + str(dilation) + dilDirect,
                                    extension=".nii.gz",
                                    appendDate=False
                                )
                                mskOutPath = Save_Load_File.DateFileName(
                                    Dir=outputDir,
                                    fileName=nameRef + "Msk" + maskVal + "_" + "SLD"
                                             + str(dilation) + dilDirect,
                                    extension=".nii.gz",
                                    appendDate=False
                                )
                                # Save
                                Save_Load_File.MatNIFTISave(
                                    MatData=removePreviousCTAData,
                                    imgPath=CTAOutPath["CombineName"],
                                    imgInfo=CTAData.OriImag,
                                    ConvertDType=True,
                                    refDataMat=CTAData.OriData
                                )
                                Save_Load_File.MatNIFTISave(
                                    MatData=removePreviousMask,
                                    imgPath=mskOutPath["CombineName"],
                                    imgInfo=CTAData.OriImag,
                                    ConvertDType=True,
                                    refDataMat=CTAData.OriData
                                )
                                ## stats
                                if outputIntStats:
                                    Matrix_Math.IntensityStats3DImgSlice(
                                        inImg=CTAData.OriData,
                                        inMask=removePreviousCTAData,
                                        slicingDirect=stats2DDirect,
                                        saveCsv=True,
                                        outDir=outputDir,
                                        outNameRef=nameRef + "CTA" + maskVal + "_" + "SL"
                                                   + str(dilation) + dilDirect,
                                        filterThres=imgThres,
                                        thresStart=[thresStrt],
                                        thresStp=[thresStop],
                                        outRefName=nameRef + "CTA" + maskVal + "_" + "SL"
                                                   + str(dilation) + dilDirect
                                    )

                                # update message
                                self.UpdateMsgLog(
                                    msg="Complete remove inside"
                                )

                        # update message
                        self.UpdateMsgLog(
                            msg="Complete dilation: {}".format(dilation)
                        )

                # update message
                self.UpdateMsgLog(
                    msg="Complete mask Value: {}".format(maskVal)
                )

            # update message
            self.UpdateMsgLog(
                msg="Complete file: {}".format(CTAFile)
            )

    """
    ##############################################################################
    # PyRadiomics
    ##############################################################################
    """

    def ChooseOutDirPR(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose medical image directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.OutDirPathPRTxt_SIEJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose medical image directory:\n{}".format(dirname))

    def ChooseTableFile(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Case table path?",
            fileObj=self.ui,
            fileTypes="Table (*.csv) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.caseTablePathPRTxt_SIEJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose case Table file path:\n{}".format(
                self.ui.caseTablePathPRTxt_SIEJZ.toPlainText()
            )
        )

    def GenerateRunPR(self, outputDir=None, caseTable=None):
        # get labels
        lbls = Preprocess_Mask.StrToLst(strIn=self.ui.lblsPRLineTxt_SIEJZ.text())["intOut"]

        # get output directory
        if outputDir is None: outputDir = self.ui.OutDirPathPRTxt_SIEJZ.toPlainText()
        if caseTable is None: caseTable = self.ui.caseTablePathPRTxt_SIEJZ.toPlainText()

        # params file
        paramPrefix = 'params'

        for lbl in lbls:
            # fill dictionary
            self.FillYMALDictionary()

            # label
            self.ymalDict['setting']['label'] = int(lbl)

            # output
            outYAML = os.path.join(outputDir, (paramPrefix + str(lbl) + '.yaml'))

            with open(outYAML, 'w') as outfile:
                yaml.dump(self.ymalDict, outfile, default_flow_style=False)

            # update
            self.UpdateMsgLog('Create: \n{} Content: \n{}'.format(outYAML, self.ymalDict))

            # reseting
            self.InitPRDict()

            # run PyRadiomics
            outputFilepath = os.path.join(outputDir, 'radiomics_features_lbl' + str(lbl) + '.csv')
            progress_filename = os.path.join(outputDir, 'pyrad_log_lbl' + str(lbl) + '.txt')

            self.PRBatch(inputCSV=caseTable, outputFilepath=outputFilepath, progress_filename=progress_filename,
                         params=outYAML)

            self.UpdateMsgLog('Complete: \n{}'.format(outputFilepath))

    def FillYMALDictionary(self):
        # init everytime
        self.InitPRDict()

        # fill dictionary
        # imageType
        if self.ui.OriginalITPR_SIEJZ.isChecked():
            self.ymalDict['imageType']['Original'] = {}
        if self.ui.LoGITPR_SIEJZ.isChecked():
            self.ymalDict['imageType']['LoG'] = {
                'sigma': Preprocess_Mask.StrToLst(
                    strIn=self.ui.sigmaITPRLineTxt_SIEJZ.text()
                )["floatOut"]
            }
        if self.ui.WaveletITPR_SIEJZ.isChecked():
            if self.ui.WaveletDefaultITPR_SIEJZ.isChecked():
                self.ymalDict['imageType']['Wavelet'] = {}
            else:
                self.ymalDict['imageType']['Wavelet'] = {
                    'start_level': int(
                        self.ui.start_levelITPRLineTxt_SIEJZ.text()
                    ),
                    'level': int(
                        self.ui.levelITPRLineTxt_SIEJZ.text()
                    ),
                    'wavelet': str(
                        self.ui.waveletITPRLineTxt_SIEJZ.text()
                    )
                }

        # Feature class
        if self.ui.firstorderFCPR_SIEJZ.isChecked():
            if self.ui.firstorderDefaultFCPR_SIEJZ.isChecked():
                self.ymalDict['featureClass']['firstorder'] = []
            else:
                lst = []
                if self.ui.EnergyFCPR_SIEJZ.isChecked(): lst.append('Energy')
                if self.ui.TotalEnergyFCPR_SIEJZ.isChecked(): lst.append('TotalEnergy')
                if self.ui.EntropyFCPR_SIEJZ.isChecked(): lst.append('Entropy')
                if self.ui.MinimumFCPR_SIEJZ.isChecked(): lst.append('Minimum')
                if self.ui.FC10PercentilePR_SIEJZ.isChecked(): lst.append('10Percentile')
                if self.ui.FC90PercentilePR_SIEJZ.isChecked(): lst.append('90Percentile')
                if self.ui.MaximumFCPR_SIEJZ.isChecked(): lst.append('Maximum')
                if self.ui.MeanFCPR_SIEJZ.isChecked(): lst.append('Mean')
                if self.ui.MedianFCPR_SIEJZ.isChecked(): lst.append('Median')
                if self.ui.InterquartileRangeFCPR_SIEJZ.isChecked(): lst.append('InterquartileRange')
                if self.ui.RangeFCPR_SIEJZ.isChecked(): lst.append('Range')
                if self.ui.MeanAbsoluteDeviationFCPR_SIEJZ.isChecked(): lst.append('MeanAbsoluteDeviation')
                if self.ui.RobustMeanAbsoluteDeviationFCPR_SIEJZ.isChecked(): lst.append('RobustMeanAbsoluteDeviation')
                if self.ui.RootMeanSquaredFCPR_SIEJZ.isChecked(): lst.append('RootMeanSquared')
                if self.ui.StandardDeviationFCPR_SIEJZ.isChecked(): lst.append('StandardDeviation')
                if self.ui.SkewnessFCPR_SIEJZ.isChecked(): lst.append('Skewness')
                if self.ui.KurtosisFCPR_SIEJZ.isChecked(): lst.append('Kurtosis')
                if self.ui.VarianceFCPR_SIEJZ.isChecked(): lst.append('Variance')
                if self.ui.UniformityFCPR_SIEJZ.isChecked(): lst.append('Uniformity')
                self.ymalDict['featureClass']['firstorder'] = lst

        if self.ui.shapeFCPR_SIEJZ.isChecked():
            if self.ui.shapeDefaultFCPR_SIEJZ.isChecked():
                self.ymalDict['featureClass']['shape'] = []
            else:
                lst = []
                if self.ui.MeshVolumeFCPR_SIEJZ.isChecked(): lst.append('MeshVolume')
                if self.ui.VoxelVolumeFCPR_SIEJZ.isChecked(): lst.append('VoxelVolume')
                if self.ui.SurfaceAreaFCPR_SIEJZ.isChecked(): lst.append('SurfaceArea')
                if self.ui.SurfaceVolumeRatioFCPR_SIEJZ.isChecked(): lst.append('SurfaceVolumeRatio')
                if self.ui.SphericityFCPR_SIEJZ.isChecked(): lst.append('Sphericity')
                if self.ui.Compactness1FCPR_SIEJZ.isChecked(): lst.append('Compactness1')
                if self.ui.Compactness2FCPR_SIEJZ.isChecked(): lst.append('Compactness2')
                if self.ui.SphericalDisproportionFCPR_SIEJZ.isChecked(): lst.append('SphericalDisproportion')
                if self.ui.Maximum3DDiameterFCPR_SIEJZ.isChecked(): lst.append('Maximum3DDiameter')
                if self.ui.Maximum2DDiameterSliceFCPR_SIEJZ.isChecked(): lst.append('Maximum2DDiameterSlice')
                if self.ui.Maximum2DDiameterColumnFCPR_SIEJZ.isChecked(): lst.append('Maximum2DDiameterColumn')
                if self.ui.Maximum2DDiameterRowFCPR_SIEJZ.isChecked(): lst.append('Maximum2DDiameterRow')
                if self.ui.MajorAxisLengthFCPR_SIEJZ.isChecked(): lst.append('MajorAxisLength')
                if self.ui.MinorAxisLengthFCPR_SIEJZ.isChecked(): lst.append('MinorAxisLength')
                if self.ui.LeastAxisLengthFCPR_SIEJZ.isChecked(): lst.append('LeastAxisLength')
                if self.ui.ElongationFCPR_SIEJZ.isChecked(): lst.append('Elongation')
                if self.ui.FlatnessFCPR_SIEJZ.isChecked(): lst.append('Flatness')
                self.ymalDict['featureClass']['shape'] = lst

        if self.ui.shape2DFCPR_SIEJZ.isChecked():
            if self.ui.shape2DDefaultFCPR_SIEJZ.isChecked():
                self.ymalDict['featureClass']['shape2D'] = []
            else:
                lst = []
                if self.ui.MeshSurfaceFCPR_SIEJZ.isChecked(): lst.append('MeshSurface')
                if self.ui.PixelSurfaceFCPR_SIEJZ.isChecked(): lst.append('PixelSurface')
                if self.ui.PerimeterFCPR_SIEJZ.isChecked(): lst.append('Perimeter')
                if self.ui.PerimeterSurfaceRatioFCPR_SIEJZ.isChecked(): lst.append('PerimeterSurfaceRatio')
                if self.ui.Sphericity2DFCPR_SIEJZ.isChecked(): lst.append('Sphericity')
                if self.ui.SphericalDisproportionFCPR_SIEJZ.isChecked(): lst.append('SphericalDisproportion')
                if self.ui.MaximumDiameterFCPR_SIEJZ.isChecked(): lst.append('MaximumDiameter')
                if self.ui.MajorAxisLengthFCPR_SIEJZ.isChecked(): lst.append('MajorAxisLength')
                if self.ui.MinorAxisLengthFCPR_SIEJZ.isChecked(): lst.append('MinorAxisLength')
                if self.ui.ElongationSliceFCPR_SIEJZ.isChecked(): lst.append('Elongation')
                self.ymalDict['featureClass']['shape2D'] = lst

        if self.ui.GLCMFCPR_SIEJZ.isChecked():
            if self.ui.GLCMDefaultFCPR_SIEJZ.isChecked():
                self.ymalDict['featureClass']['glcm'] = []

        if self.ui.NGTDMFCPR_SIEJZ.isChecked():
            if self.ui.NGTDMDefaultFCPR_SIEJZ.isChecked():
                self.ymalDict['featureClass']['ngtdm'] = []

        if self.ui.GLSZMFCPR_SIEJZ.isChecked():
            if self.ui.GLSZMDefaultFCPR_SIEJZ.isChecked():
                self.ymalDict['featureClass']['glszm'] = []

        if self.ui.GLRLMFCPR_SIEJZ.isChecked():
            if self.ui.GLRLMDefaultFCPR_SIEJZ.isChecked():
                self.ymalDict['featureClass']['glrlm'] = []

        if self.ui.GLDMFCPR_SIEJZ.isChecked():
            if self.ui.GLDMDefaultFCPR_SIEJZ.isChecked():
                self.ymalDict['featureClass']['gldm'] = []

        # Setting
        # normalization
        if self.ui.normalSPR_SIEJZ.isChecked():
            self.ymalDict['setting']['normalize'] = True
            if self.ui.normalizeScaleSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['normalizeScale'] = float(self.ui.normalizeScaleSPRLineTxt_SIEJZ.text())
            if self.ui.removeOutliersSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['removeOutliers'] = float(self.ui.removeOutliersSPRLineTxt_SIEJZ.text())

        # Bin
        if self.ui.binWidthPR_SIEJZ.isChecked():
            self.ymalDict['setting']['binWidth'] = int(self.ui.binWidthPRLineTxt_SIEJZ.text())
        if self.ui.binCountSPR_SIEJZ.isChecked():
            self.ymalDict['setting']['binCount'] = int(self.ui.binCountPRLineTxt_SIEJZ.text())

        # Resampling
        if self.ui.resampleSPR_SIEJZ.isChecked():
            if self.ui.resampledPixelSpacingSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['resampledPixelSpacing'] = \
                Preprocess_Mask.StrToLst(strIn=self.ui.resampledPixelSpacingSPRLineTxt_SIEJZ.text())["floatOut"]
            if self.ui.padDistanceSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['padDistance'] = int(self.ui.padDistanceSPRLineTxt_SIEJZ.text())
            if self.ui.preCropSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['preCrop'] = True
            if self.ui.interpolatorSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['interpolator'] = self.ui.interpolatorSPRCBox_SIEJZ.currentText()

        # Force 2D
        if self.ui.force2DSPR_SIEJZ.isChecked():
            self.ymalDict['setting']['force2D'] = True
            self.ymalDict['setting']['force2Ddimension'] = int(self.ui.force2DdimensionSPRLineTxt_SIEJZ.text())

        # Mask validation
        if self.ui.maskValidationSPR_SIEJZ.isChecked():
            if self.ui.correctMaskSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['correctMask'] = True
            if self.ui.geometryToleranceSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['geometryTolerance'] = float(self.ui.geometryToleranceSPRLineTxt_SIEJZ.text())
            if self.ui.minimumROISizeSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['minimumROISize'] = int(self.ui.minimumROISizeSPRLineTxt_SIEJZ.text())
            if self.ui.minimumROIDimensionsSPR_SIEJZ.isChecked():
                self.ymalDict['setting']['minimumROIDimensions'] = int(
                    self.ui.minimumROIDimensionsSPRLineTxt_SIEJZ.text())

    def PRBatch(self, inputCSV, outputFilepath, progress_filename, params):
        # run
        Matrix_Math.PyRadiomicsBatch(inputCSV, outputFilepath, progress_filename, params)

        # # Configure logging
        # rLogger = logging.getLogger('radiomics')
        #
        # # Set logging level
        # # rLogger.setLevel(logging.INFO)  # Not needed, default log level of logger is INFO
        #
        # # Create handler for writing to log file
        # handler = logging.FileHandler(filename=progress_filename, mode='w')
        # handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s'))
        # rLogger.addHandler(handler)
        #
        # # Initialize logging for batch log messages
        # logger = rLogger.getChild('batch')
        #
        # # Set verbosity level for output to stderr (default level = WARNING)
        # radiomics.setVerbosity(logging.INFO)
        #
        # logger.info('pyradiomics version: %s', radiomics.__version__)
        # logger.info('Loading CSV')
        #
        # flists = []
        # try:
        #     with open(inputCSV, 'r') as inFile:
        #         cr = csv.DictReader(inFile, lineterminator='\n')
        #         flists = [row for row in cr]
        # except Exception:
        #     logger.error('CSV READ FAILED', exc_info=True)
        #
        # logger.info('Loading Done')
        # logger.info('Patients: %d', len(flists))
        #
        # if os.path.isfile(params):
        #     extractor = featureextractor.RadiomicsFeatureExtractor(params)
        # else:  # Parameter file not found, use hardcoded settings instead
        #     settings = {}
        #     settings['binWidth'] = 25
        #     settings['resampledPixelSpacing'] = None  # [3,3,3]
        #     settings['interpolator'] = SimpleITK.sitkBSpline
        #     settings['enableCExtensions'] = True
        #
        #     extractor = featureextractor.RadiomicsFeatureExtractor(**settings)
        #     # extractor.enableInputImages(wavelet= {'level': 2})
        #
        # logger.info('Enabled input images types: %s', extractor.enabledImagetypes)
        # logger.info('Enabled features: %s', extractor.enabledFeatures)
        # logger.info('Current settings: %s', extractor.settings)
        #
        # headers = None
        #
        # for idx, entry in enumerate(flists, start=1):
        #
        #     logger.info("(%d/%d) Processing Patient (Image: %s, Mask: %s)", idx, len(flists), entry['Image'],
        #                 entry['Mask'])
        #
        #     imageFilepath = entry['Image']
        #     maskFilepath = entry['Mask']
        #     label = entry.get('Label', None)
        #
        #     if str(label).isdigit():
        #         label = int(label)
        #     else:
        #         label = None
        #
        #     if (imageFilepath is not None) and (maskFilepath is not None):
        #         featureVector = collections.OrderedDict(entry)
        #         featureVector['Image'] = os.path.basename(imageFilepath)
        #         featureVector['Mask'] = os.path.basename(maskFilepath)
        #
        #         try:
        #             featureVector.update(extractor.execute(imageFilepath, maskFilepath, label))
        #
        #             with open(outputFilepath, 'a') as outputFile:
        #                 writer = csv.writer(outputFile, lineterminator='\n')
        #                 if headers is None:
        #                     headers = list(featureVector.keys())
        #                     writer.writerow(headers)
        #
        #                 row = []
        #                 for h in headers:
        #                     row.append(featureVector.get(h, "N/A"))
        #                 writer.writerow(row)
        #         except Exception:
        #             logger.error('FEATURE EXTRACTION FAILED', exc_info=True)


    """
    ##############################################################################
    # PyRadiomics Batch 2D Slices 
    ##############################################################################
    """

    def ChooseTableFileB2S(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Batch table path?",
            fileObj=self.ui,
            fileTypes="Table (*.csv) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.caseTablePathB2STxt_SIEJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose batch table file path:\n{}".format(
                self.ui.caseTablePathB2STxt_SIEJZ.toPlainText()
            )
        )

    def Choose2DOutputDirB2S(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose 2D slice radiomics directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.outputFolderPathB2STxt_SIEJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose 2D slice radiomics directory: \n{}".format(dirname))

    def BatchB2S(self):
        # input table
        batchTablePath = self.ui.caseTablePathB2STxt_SIEJZ.toPlainText()
        outputFolder = self.ui.outputFolderPathB2STxt_SIEJZ.toPlainText()

        # read DF
        batchRadiomics2D = Pd_Funs.OpenDF(
            inPath=batchTablePath,
            header=0,
            usecols=None,
            index_col=None
        )

        # create initial folder if empty
        if outputFolder == '': outputFolder, _ = Save_Load_File.ParentDir(path=batchTablePath)

        # output radiomics 2D table
        radiomics2DFolderPath = os.path.join(outputFolder, "RadiomicsSlices")
        # create folder
        Save_Load_File.checkCreateDir(radiomics2DFolderPath)

        # radiomics for each column
        for folderRef in list(batchRadiomics2D):
            print(batchRadiomics2D)
            # column folder
            columnFolderPath = os.path.join(outputFolder, folderRef)
            # create folder
            Save_Load_File.checkCreateDir(columnFolderPath)

            # each case
            caseFiles = batchRadiomics2D[folderRef].tolist()

            # output log
            caseDict = {
                "ID":[],
                "Path":[]
            }

            for caseFile in caseFiles:
                # get file name:
                caseName = Save_Load_File.FilenameFromPath(caseFile)

                # create output folder
                caseFolderPath = os.path.join(columnFolderPath, caseName)
                Save_Load_File.checkCreateDir(caseFolderPath)

                # radiomics
                self.GenerateRunPR(outputDir=caseFolderPath, caseTable=caseFile)

                # log
                ## _ indices
                indices = Save_Load_File.FindIndicesStr(s=caseName, ch="_")
                caseDict["ID"].append(caseName[(indices[-1] + 1):])
                caseDict["Path"].append(caseFolderPath.replace("/", "\\"))

            ## output
            outTablelOGPath = radiomics2DFolderPath + "//" + folderRef +".csv"
            Pd_Funs.SaveDF(
                outPath=outTablelOGPath,
                pdIn=pandas.DataFrame(caseDict),
                header=True,
                index=False
            )

    def ChooseInputDirB2S(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose 2D slice table directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.inDirPathB2STxt_SIEJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose 2D slice table directory: \n{}".format(dirname))

    def Radiomics2DStatB2S(self):
        # input
        statDirPath = self.ui.inDirPathB2STxt_SIEJZ.toPlainText()
        searchFiles = Preprocess_Mask.StrToLst(strIn=self.ui.searchFilesB2STxt_SIEJZ.toPlainText())["listOut"]
        outSuffs = Preprocess_Mask.StrToLst(strIn=self.ui.outSuffsB2STxt_SIEJZ.toPlainText())["listOut"]
        ignoreRefs = Preprocess_Mask.StrToLst(strIn=self.ui.ignoreRefsB2STxt_SIEJZ.toPlainText())["listOut"]

        # get all csv files
        allTableFullPaths = Save_Load_File.ReturnFilesFullPath(
            dirPath=statDirPath,
            fileRef=".csv",
            folderSearch=None,
            traverse=False
        )
        self.UpdateMsgLog(
            msg="Files under: {} are \n{}".format(statDirPath, allTableFullPaths)
        )

        # loop
        for overallTablePath in allTableFullPaths:
            # get file name
            overallTableName = Save_Load_File.FilenameFromPath(fullPath=overallTablePath)

            # load DF
            radiomics2DDF = Pd_Funs.OpenDF(
                inPath=overallTablePath,
                header=0,
                usecols=None,
                index_col=None
            )
            print(radiomics2DDF)

            # loop each labelled file
            for fileNum in range(len(searchFiles)):
                searchFile = searchFiles[fileNum]
                outSuff = outSuffs[fileNum]

                # output dictionary
                outDict = {}
                for ID, searchPath in zip(radiomics2DDF['ID'].tolist(), radiomics2DDF['Path'].tolist()):
                    # file
                    searchFileFullPath = os.path.join(searchPath, searchFile)

                    # load df
                    radiomicsCaseDF = Pd_Funs.OpenDF(
                        inPath=searchFileFullPath,
                        header=0,
                        usecols=None,
                        index_col=None
                    )

                    # create empty dictionary
                    outDict[ID] = {}

                    # each column statistics
                    for columnName in list(radiomicsCaseDF):
                        # filter labels
                        jumpFlg = False
                        for ref in ignoreRefs:
                            if ref in columnName:
                                jumpFlg = True

                        # jump loop
                        if jumpFlg:
                            continue
                        else:
                            self.UpdateMsgLog(msg="Working on: {}".format(columnName))

                        # statistics
                        caseDic = Matrix_Math.LstArrStats(
                            ArrLst=numpy.array(radiomicsCaseDF[columnName].tolist()),
                            refStr=columnName
                        )["statics"]

                        # # check all dictionary keys
                        # if not all(k in caseDic.keys() for k in outDict.keys()):
                        #     for key in caseDic.keys():
                        #         if key not in outDict.keys():
                        #             # create new key
                        #             outDict[key] = []
                        # else:
                        #     # append results
                        #     for key in caseDic.keys():
                        #         outDict[key].append(caseDic[key])

                        # append
                        outDict[ID] = {**outDict[ID], **caseDic}

                # save dataframe
                ## create directory
                Save_Load_File.checkCreateDir(statDirPath + "\\" + "Statics")
                outPath = statDirPath + "\\Statics\\" + overallTableName + outSuff + ".csv"
                outDF = pandas.DataFrame.from_dict(outDict, orient='index')
                outDF.insert(loc=0, column='ID', value=radiomics2DDF['ID'].tolist())

                Pd_Funs.SaveDF(
                    outPath=outPath,
                    pdIn=outDF,
                    header=True,
                    index=False
                )


    """
    ##############################################################################
    # Cross-section & Centerline
    ##############################################################################
    """

    # choose batch table path
    def ChooseTableXCPath(self):
        tablePath = Save_Load_File.OpenFilePathQt(
            dispMsg='Choose Batch Excel File',
            fileTypes='All files (*.*);; (Excel files(*.csv *.xlsx))',
            fileObj=self.ui,
            qtObj=True
        )

        self.ui.TablePathXCTxt_SIEJZ.setPlainText(tablePath)

        # update message
        self.UpdateMsgLog(msg="Choose Xsection & Centerline table file path:\n{}".format(tablePath))

    def ChooseSaveFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(
            dispMsg="Choose save image file",
            fileObj=self.ui,
            fileTypes="All files (*.*);; "
                      "CSV files (*.csv) ;; ",
            qtObj=True
        )

        # set filename
        self.ui.OutTablePathXCTxt_SIEJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving Xsection & Centerline table file path:\n{}".format(filename))

    def XsectionPhase(self):
        # input information
        tablePath = self.ui.TablePathXCTxt_SIEJZ.toPlainText()
        outTablePath = self.ui.OutTablePathXCTxt_SIEJZ.toPlainText()
        twoPhase = self.ui.PhaseXCCBox_SIEJZ.currentText() == "Two Phase"
        SaveIntermediate = self.ui.SaveIntermediateXCCheckBox_SIEJZ.isChecked()
        labelThresStarts = [
            Preprocess_Mask.StrToLst(strIn=self.ui.thresStrt1XCLineTxt_SIEJZ.text())["intOut"],
            Preprocess_Mask.StrToLst(strIn=self.ui.thresStrt2XCLineTxt_SIEJZ.text())["intOut"]
        ]
        labelThresStops = [
            Preprocess_Mask.StrToLst(strIn=self.ui.thresStop1XCLineTxt_SIEJZ.text())["intOut"],
            Preprocess_Mask.StrToLst(strIn=self.ui.thresStop2XCLineTxt_SIEJZ.text())["intOut"]
        ]
        ThresTypes = [
            self.ui.thresType1XCCBox_SIEJZ.currentText(),
            self.ui.thresType2XCCBox_SIEJZ.currentText()
        ]

        # run
        Post_Image_Process_Functions.XsectionMorphology(
            tablePath=tablePath,
            twoPhase=twoPhase,
            labelThresStarts=labelThresStarts,
            labelThresStops=labelThresStops,
            ThresTypes=ThresTypes,
            SaveIntermediate=SaveIntermediate,
            outTablePath=outTablePath
        )

    def CenterlinePhase(self):
        # input information
        tablePath = self.ui.TablePathXCTxt_SIEJZ.toPlainText()
        outTablePath = self.ui.OutTablePathXCTxt_SIEJZ.toPlainText()
        twoPhase = self.ui.PhaseXCCBox_SIEJZ.currentText() == "Two Phase"
        SaveIntermediate = self.ui.SaveIntermediateXCCheckBox_SIEJZ.isChecked()
        labelThresStarts = [
            Preprocess_Mask.StrToLst(strIn=self.ui.thresStrt1XCLineTxt_SIEJZ.text())["intOut"],
            Preprocess_Mask.StrToLst(strIn=self.ui.thresStrt2XCLineTxt_SIEJZ.text())["intOut"]
        ]
        labelThresStops = [
            Preprocess_Mask.StrToLst(strIn=self.ui.thresStop1XCLineTxt_SIEJZ.text())["intOut"],
            Preprocess_Mask.StrToLst(strIn=self.ui.thresStop2XCLineTxt_SIEJZ.text())["intOut"]
        ]
        ThresTypes = [
            self.ui.thresType1XCCBox_SIEJZ.currentText(),
            self.ui.thresType2XCCBox_SIEJZ.currentText()
        ]

        # run
        Post_Image_Process_Functions.CenterLineInfo(
            tablePath=tablePath,
            twoPhase=twoPhase,
            labelThresStarts=labelThresStarts,
            labelThresStops=labelThresStops,
            ThresTypes=ThresTypes,
            SaveIntermediate=SaveIntermediate,
            outTablePath=outTablePath
        )

    """
    ##############################################################################
    # FAI calculation
    ##############################################################################
    """
    def ChooseTableFile_FAI(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Case table path?",
            fileObj=self.ui,
            fileTypes="Table (*.csv) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.caseTablePathFAITxt_SIEJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose case Table file path:\n{}".format(
                self.ui.caseTablePathFAITxt_SIEJZ.toPlainText()
            )
        )

    def ChooseSaveFile_FAI(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(
            dispMsg="Choose save image file",
            fileObj=self.ui,
            fileTypes="All files (*.*);; "
                      "CSV files (*.csv) ;; ",
            qtObj=True
        )

        # set filename
        self.ui.OutTablePathFAITxt_SIEJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving table file path:\n{}".format(filename))

    def FAICalculation(self):
        # input
        inTablePath = self.ui.caseTablePathFAITxt_SIEJZ.toPlainText()
        outTablePath = self.ui.OutTablePathFAITxt_SIEJZ.toPlainText()
        labelThresStart = Preprocess_Mask.StrToLst(strIn=self.ui.thresStrtFAILineTxt_SIEJZ.text())["intOut"]
        labelThresStop = Preprocess_Mask.StrToLst(strIn=self.ui.thresStopFAILineTxt_SIEJZ.text())["intOut"]
        ThresType = self.ui.thresTypeFAICBox_SIEJZ.currentText()

        # load DF
        workDF = Pd_Funs.OpenDF(
            inPath=inTablePath,
            header=0,
            usecols=None,
            index_col=None
        )

        # loop each case
        caseDict = {'ID': [], 'FAI': []}

        # loop each case
        for fileNum in range(len(workDF['ID'])):
            # calculate FAI
            FAI = Image_Process_Functions.FAICaculation(
                imgPath=workDF['Image'][fileNum],
                maskPath=workDF['Mask'][fileNum],
                ThresType=ThresType,
                ThresStart=labelThresStart,
                ThresStop=labelThresStop)

            caseDict['ID'].append(workDF['ID'][fileNum])
            caseDict['FAI'].append(FAI)

        # output
        Pd_Funs.SaveDF(
            outPath=outTablePath,
            pdIn=pandas.DataFrame(caseDict),
            header=True,
            index=False
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
        print(disp)
