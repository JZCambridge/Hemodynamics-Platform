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
from PySide2.QtUiTools import QUiLoader


##############################################################################

class ConvertData:
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseCTABtn_CDT.clicked.connect(lambda: self.ChooseOpenCTAFile())
        self.ui.chooseMskBtn_CDT.clicked.connect(lambda: self.ChooseOpenMskFile())
        self.ui.saveMskBtn_CDT.clicked.connect(lambda: self.ChooseSaveFile())
        self.ui.convertSaveMskBtn_CDT.clicked.connect(lambda: self.LoadSaveFile())
        self.ui.chooseTableCDTBtn_CDT.clicked.connect(lambda: self.ChooseTableFileCDT())
        self.ui.batchCDTBtn_CDT.clicked.connect(lambda: self.BatchCDT())
        self.ui.chooseTableDCMBtn_CDT.clicked.connect(lambda: self.ChooseTableFileDCM())
        self.ui.batchDCMBtn_CDT.clicked.connect(lambda: self.BatchDICOMconvertNIFTI())

    """
    ##############################################################################
    # Batch CDT
    ##############################################################################
    """

    def ChooseOpenCTAFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.CTAPathTxt_CDT.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose:\n{}".format(
            self.ui.CTAPathTxt_CDT.toPlainText()
        )
        )

    def ChooseOpenMskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load image segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.mskPathTxt_CDT.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose:\n{}".format(
            self.ui.mskPathTxt_CDT.toPlainText()
        )
        )

    def ChooseSaveFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Output mask file path",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                                                           "STL files (*.stl) ;; "
                                                           "Img files (*.png *.jpg) ;; "
                                                           "Graphic files (*.svg, *.eps, *.ps, *.pdf, *.tex) ",

                                                 qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_CDT.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving file path:\n{}".format(self.ui.saveDirPathTxt_CDT.toPlainText()))

    def ChooseTableFileCDT(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="output table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt *.csv *.xlsx *.xls *.xlsm *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.batchCDTPathTxt_CDT.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose batch convert datatype Table file path:\n{}".format(
                self.ui.batchCDTPathTxt_CDT.toPlainText()
            )
        )

    def LoadSaveFile(self,
                     CTAFilePath=None,
                     mskFilePath=None,
                     outFilePath=None,
                     convertRAI=None):
        # load two data
        if CTAFilePath is None: CTAFilePath = self.ui.CTAPathTxt_CDT.toPlainText()

        if mskFilePath is None: mskFilePath = self.ui.mskPathTxt_CDT.toPlainText()

        if convertRAI is None:
            convertRAI = self.ui.convertRAICheckBox_CDT.isChecked()
        else:
            convertRAI = Save_Load_File.CheckTrue(parameter=convertRAI)

        # load
        CTA = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=CTAFilePath,
            convertOrient=convertRAI,
            Orient="LPS"
        )
        inMsk = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=mskFilePath,
            convertOrient=convertRAI,
            Orient="LPS"
        )
        # update message
        self.UpdateMsgLog(msg="Loading:\n{} \n{}".format(
            CTAFilePath,
            mskFilePath
        )
        )

        # Save
        if outFilePath is None:
            rtrnInfo = Save_Load_File.MatNIFTISave(MatData=inMsk.OriData,
                                                   imgPath=self.ui.saveDirPathTxt_CDT.toPlainText(),
                                                   imgInfo="",
                                                   # imgInfo=CTA.OriImag,
                                                   ConvertDType=True,
                                                   refDataMat=CTA.OriData)
        else:
            rtrnInfo = Save_Load_File.MatNIFTISave(MatData=inMsk.OriData,
                                                   imgPath=outFilePath,
                                                   imgInfo="",
                                                   # imgInfo=CTA.OriImag,
                                                   ConvertDType=True,
                                                   refDataMat=CTA.OriData)

        # update message
        self.UpdateMsgLog(msg=rtrnInfo["message"])

    def BatchCDT(self):
        # input
        batchFilePath = self.ui.batchCDTPathTxt_CDT.toPlainText()

        # batch files
        dataFrameBatch = Pd_Funs.OpenDF(
            inPath=batchFilePath,
            header=0
        )

        # default for RAI
        if not ('convertRAI' in dataFrameBatch.columns):
            dataFrameBatch['convertRAI'] = [1] * len(dataFrameBatch['CTAFilePath'].tolist())

        # loop all files
        for CTAFilePath, \
                mskFilePath, \
                outFilePath, \
                convertRAI \
                in zip(
            dataFrameBatch['CTAFilePath'].tolist(), \
                dataFrameBatch['maskFilePath'].tolist(), \
                dataFrameBatch['outputFilePath'].tolist(), \
                dataFrameBatch['convertRAI'].tolist() \
                ):
            self.LoadSaveFile(
                CTAFilePath=CTAFilePath,
                mskFilePath=mskFilePath,
                outFilePath=outFilePath,
                convertRAI=convertRAI
            )

    """
    ##############################################################################
    # Batch DICOM to NIFTI
    ##############################################################################
    """

    def ChooseTableFileDCM(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="output table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt *.csv *.xlsx *.xls *.xlsm *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.batchDCMPathTxt_CDT.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose batch convert datatype Table file path:\n{}".format(
                self.ui.batchDCMPathTxt_CDT.toPlainText()
            )
        )

    def BatchDICOMconvertNIFTI(self,
                               tablePath=None,
                               refImg=None):
        # input
        if tablePath is None:
            batchFilePath = self.ui.batchDCMPathTxt_CDT.toPlainText()
        else:
            batchFilePath = tablePath

        # batch files
        dataFrameBatch = Pd_Funs.OpenDF(
            inPath=batchFilePath,
            header=0
        )

        # convert DICOM Series
        # refIn = False
        # if refImg is not None:
        #     refIn = Save_Load_File.CheckTrue(refImg)
        #     print(refIn)
        # else:
        #     refIn = self.ui.convertReferenceCheckBox_CDT.isChecked()
        #     print('Wrong')

        if ('referenceImagePath' in dataFrameBatch.columns):

            # default for RAI
            if not ('convertRAI' in dataFrameBatch.columns):
                dataFrameBatch['convertRAI'] = [1] * len(dataFrameBatch['DICOMDirectoryPath'].tolist())
                print("Auto create 'convertRAI'")

            if not ('convertDataType' in dataFrameBatch.columns):
                dataFrameBatch['convertDataType'] = [1] * len(dataFrameBatch['DICOMDirectoryPath'].tolist())
                print("Auto create 'convertDataType'")

            for DCMDirectPath, \
                    refernecePath, \
                    outputPath, \
                    convertDataType, \
                    convertOrient \
                    in zip(
                dataFrameBatch["DICOMDirectoryPath"].tolist(),
                dataFrameBatch["referenceImagePath"].tolist(),
                dataFrameBatch["outputPath"].tolist(),
                dataFrameBatch["convertDataType"].tolist(),
                dataFrameBatch["convertRAI"].tolist()
            ):
                # convert
                DCMConvertor = Save_Load_File.ReadWriteDCM(fileDirect=DCMDirectPath, outfilePath=outputPath)
                DCMConvertor.ReadDCMSeries()
                if Save_Load_File.CheckTrue(convertOrient): DCMConvertor.ConvertOrientation(orientation="LPS")
                DCMConvertor.SaveDCMSeries()

                # update
                self.UpdateMsgLog("Converting DCM Files:\n" + DCMConvertor.message)

                # convert and save
                oriImage = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=outputPath
                )
                inMsk = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=refernecePath
                )
                rtrnInfo = Save_Load_File.MatNIFTISave(MatData=oriImage.OriData,
                                                       imgPath=outputPath,
                                                       imgInfo=inMsk.OriImag,
                                                       ConvertDType=convertDataType,
                                                       refDataMat=inMsk.OriData)
                # update message
                self.UpdateMsgLog(msg=rtrnInfo["message"])

        else:
            # default for RAI
            if not ('convertRAI' in dataFrameBatch.columns):
                dataFrameBatch['convertRAI'] = [1] * len(dataFrameBatch['DICOMDirectoryPath'].tolist())
                print("Auto create 'convertRAI'")

            for DCMDirectPath, \
                    outputPath, \
                    convertOrient \
                    in zip(
                dataFrameBatch["DICOMDirectoryPath"].tolist(),
                dataFrameBatch["OutputPath"].tolist(),
                dataFrameBatch["convertRAI"].tolist()
            ):
                # convert
                DCMConvertor = Save_Load_File.ReadWriteDCM(fileDirect=DCMDirectPath, outfilePath=outputPath)
                DCMConvertor.ReadDCMSeries()
                if Save_Load_File.CheckTrue(convertOrient): DCMConvertor.ConvertOrientation(orientation="LPS")
                DCMConvertor.SaveDCMSeries()

                # update
                self.UpdateMsgLog("Converting DCM Files:" + DCMConvertor.message)

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
