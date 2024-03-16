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

class MaskDilation:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseMskBtn_MDJZ.clicked.connect(lambda: self.ChooseOpenMaskFile())
        self.ui.loadMskBtn_MDJZ.clicked.connect(lambda: self.LoadData())
        self.ui.plotBtn_MDJZ.clicked.connect(lambda: self.PlotOVerlap())
        self.ui.dilBtn_MDJZ.clicked.connect(lambda: self.DilChoice())
        self.ui.saveBtn_MDJZ.clicked.connect(lambda: self.SaveFile())
        self.ui.saveDirBtn_MDJZ.clicked.connect(lambda: self.ChooseSaveDir())

        self.InitDilation()

    def InitDilation(self):
        # initial definition
        self.displayData = None
        self.displayDataBase = None
        self.inMsk = None
        self.MskDil = None
        self.MskDilEdge = None
        self.MskDilFill = None

    def ChooseOpenMaskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.MaskPathTxt_MDJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def LoadData(self):
        # load two data
        self.inMsk = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.MaskPathTxt_MDJZ.toPlainText()
        )
        # update display data
        self.displayDataBase = self.inMsk.OriData

        # update message
        self.UpdateMsgLog(
            msg="Load:\n{}".format(
                self.ui.MaskPathTxt_MDJZ.toPlainText()
            )
        )

    def PlotOVerlap(self):
        # get inputs
        slicDir = self.ui.plotAixsLineTxt_LC.text()
        title = Preprocess_Mask.StrToLst(strIn=self.ui.plotTitleTxt_MDJZ.toPlainText())["listOut"]
        plotRange = Preprocess_Mask.StrToLst(strIn=self.ui.plotThresTxt_MDJZ.toPlainText())["booleanOut"]
        minLst = Preprocess_Mask.StrToLst(strIn=self.ui.plotMinTxt_MDJZ.toPlainText())["floatOut"]
        maxLst = Preprocess_Mask.StrToLst(strIn=self.ui.plotMaxTxt_MDJZ.toPlainText())["floatOut"]

        msg = "slicDir: {}".format(slicDir) + \
              "\ntitle: {}".format(title) + \
              "\nplotRange: {}".format(plotRange) + \
              "\nminLst: {}".format(minLst) + \
              "\nmaxLst: {}".format(maxLst)

        Use_Plt.slider3Display(matData1=self.displayDataBase,
                               matData2=self.displayData,
                               matData3=[0],
                               fig3OverLap=True,
                               ShareX=True,
                               ShareY=True,
                               ask23MatData=False,
                               wait=False,
                               slicDiect=slicDir,
                               title=title,
                               plotRange=plotRange,
                               winMin=minLst,
                               winMax=maxLst)

        # update message
        self.UpdateMsgLog(
            msg="Plotting:\n" + msg
        )
        print("Plotting:\n" + msg)

    def VoxelDilation(self):
        # input range
        direction = self.ui.voxelDilBtnGrp_MDJZ.checkedButton().text()
        disk = int(self.ui.voxelDilLineTxt_MDJZ.text())
        binaryMsk = self.ui.voxelDilThresBtnGrp_MDJZ.checkedButton().text() == "Yes"
        binaryThres = int(self.ui.voxelDilThresLineTxt_MDJZ.text())

        msg = "direction: {}".format(direction) + \
              "\ndisk: {}".format(disk) + \
              "\nbinaryMsk: {}".format(binaryMsk) + \
              "\nbinaryThres: {}".format(binaryThres)

        # Dilation
        outMsg, self.MskDil = Image_Process_Functions.DiskDilate(
            dataMat=self.inMsk.OriData,
            Thres=binaryThres,
            dilateIncre=disk,
            binaryMsk=binaryMsk,
            axisChoice=direction
        )

        # Get edge and fill original mask
        rtrnInfo = Image_Process_Functions.RemoveFillEdge(
            inMsk=self.MskDil,
            fillMsk=self.inMsk.OriData
        )

        self.MskDilEdge = rtrnInfo["edgeMask"]
        self.MskDilFill = rtrnInfo["fillMask"]

        # update display data
        self.displayData = self.MskDilEdge

        # update message
        self.UpdateMsgLog(
            msg="Complete Voxel Dilation: Get Edge + Fill Origin: \n{}".format(msg)
        )
        print("Complete Voxel Dilation: Get Edge + Fill Origin: \n{}".format(msg))

    def DiameterDilation(self):
        # input range
        direction = self.ui.diamDilBtnGrp_MDJZ.checkedButton().text()
        factor = int(self.ui.diamDilLineTxt_MDJZ.text())
        binaryMsk = self.ui.voxelDilThresBtnGrp_MDJZ.checkedButton().text() == "Yes"
        binaryThres = int(self.ui.voxelDilThresLineTxt_MDJZ.text())

        msg = "direction: {}".format(direction) + \
              "\nfactor: {}".format(factor) + \
              "\nbinaryMsk: {}".format(binaryMsk) + \
              "\nbinaryThres: {}".format(binaryThres)

        # Dilation
        outMsg, self.MskDil = Image_Process_Functions.DiskDilateDiameter(
            dataMat=self.inMsk.OriData,
            Thres=0,
            dilateIncreFac=factor,
            binaryMsk=True,
            axisChoice='X'
        )

        # Get edge and fill original mask
        rtrnInfo = Image_Process_Functions.RemoveFillEdge(
            inMsk=self.MskDil,
            fillMsk=self.inMsk.OriData
        )

        self.MskDilEdge = rtrnInfo["edgeMask"]
        self.MskDilFill = rtrnInfo["fillMask"]

        # update display data
        self.displayData = self.MskDilFill

        # update message
        self.UpdateMsgLog(
            msg="Complete Diameter Dilation: Get Edge + Fill Origin: \n{}".format(msg)
        )
        print("Complete Diameter Dilation: Get Edge + Fill Origin: \n{}".format(msg))

    def DilChoice(self):
        # input range
        dilChoice = self.ui.dilChoiceBtnGrp_MDJZ.checkedButton().text()

        if dilChoice == "Voxel":
            # update message
            self.UpdateMsgLog(
                msg="Choose Voxel Dilation"
            )
            print("Choose Voxel Dilation")
            self.VoxelDilation()
        elif dilChoice == "Diameter":
            # update message
            self.UpdateMsgLog(
                msg="Choose Diameter Dilation"
            )
            print("Choose Diameter Dilation")
            self.DiameterDilation()

    def ChooseSaveDir(self):

        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Save directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.saveDirPathTxt_MDJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose directory: \n{}".format(dirname))

    def SaveFile(self):
        # Get file name
        if self.ui.nameRefTxt_PSJZ.toPlainText() == "":
            name = Save_Load_File.FilenameFromPath(self.ui.mskPathTxt_MDJZ.toPlainText())
        else:
            name = Save_Load_File.ValidFileName(self.ui.nameRefTxt_MDJZ.toPlainText())

        # Set file name
        DOFilePath = Save_Load_File.DateFileName(
            Dir=self.ui.saveDirPathTxt_MDJZ.toPlainText(),
            fileName=name + "DO",
            extension=".nii.gz",
            appendDate=False
        )
        # Set file name
        EGFilePath = Save_Load_File.DateFileName(
            Dir=self.ui.saveDirPathTxt_MDJZ.toPlainText(),
            fileName=name + "EG",
            extension=".nii.gz",
            appendDate=False
        )
        # Set file name
        DFFilePath = Save_Load_File.DateFileName(
            Dir=self.ui.saveDirPathTxt_MDJZ.toPlainText(),
            fileName=name + "DF",
            extension=".nii.gz",
            appendDate=False
        )

        # Save
        Save_Load_File.MatNIFTISave(MatData=self.MskDil,
                                    imgPath=DOFilePath["CombineName"],
                                    imgInfo=self.inMsk.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.inMsk.OriData)
        Save_Load_File.MatNIFTISave(MatData=self.MskDilEdge,
                                    imgPath=EGFilePath["CombineName"],
                                    imgInfo=self.inMsk.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.inMsk.OriData)
        Save_Load_File.MatNIFTISave(MatData=self.MskDilFill,
                                    imgPath=DFFilePath["CombineName"],
                                    imgInfo=self.inMsk.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.inMsk.OriData)
        # update
        self.UpdateMsgLog(
            msg="Save: \n{} \n{} \n{}".format(
                DOFilePath["CombineName"],
                EGFilePath["CombineName"],
                DFFilePath["CombineName"]
            )
        )

    def UpdateMsgLog(self, msg=""):

        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + msg \
               + "\n################################################\n"

        if self.modelui:
            # update log and display message
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
        print(disp)
