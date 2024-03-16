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

class MaskShrink:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseLumMskBtn_MSKJZ.clicked.connect(lambda: self.ChooseLumMaskFile())
        self.ui.choosePeriMskBtn_MSKJZ.clicked.connect(lambda: self.ChoosePeriMaskFile())
        self.ui.chooseTissMskBtn_MSKJZ.clicked.connect(lambda: self.ChooseTissueMaskFile())
        self.ui.saveDirBtn_MSKJZ.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.shrinkSaveBtn_MSKJZ.clicked.connect(lambda: self.Shrink())

        self.InitShrink()

    def InitShrink(self):
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

    def ChooseLumMaskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load inner mask segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.lumPathTxt_MSKJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChoosePeriMaskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load periluminal mask segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.periPathTxt_MSKJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseTissueMaskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load tissue VALUE mask segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.tissuePathTxt_MSKJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def LoadData(self):
        # input
        self.tissueShrk = self.ui.shrkChoiceBtnGrp_MSKJZ.checkedButton().text() == "With Tissue"

        # load data
        if not self.tissueShrk:
            self.lumMsk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.lumPathTxt_MSKJZ.toPlainText()
            )
            self.periMsk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.periPathTxt_MSKJZ.toPlainText()
            )

            # update message
            self.UpdateMsgLog(
                msg="Not shrinking tissue!!! \nLoad:\n{} \n{}".format(
                    self.ui.lumPathTxt_MSKJZ.toPlainText(),
                    self.ui.periPathTxt_MSKJZ.toPlainText()
                )
            )
        else:
            self.lumMsk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.lumPathTxt_MSKJZ.toPlainText()
            )
            self.periMsk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.periPathTxt_MSKJZ.toPlainText()
            )
            self.tissueMsk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.tissuePathTxt_MSKJZ.toPlainText()
            )

            # update message
            self.UpdateMsgLog(
                msg="Not shrinking tissue!!! \nLoad:\n{} \n{}".format(
                    self.ui.lumPathTxt_MSKJZ.toPlainText(),
                    self.ui.periPathTxt_MSKJZ.toPlainText(),
                    self.ui.tissuePathTxt_MSKJZ.toPlainText()
                )
            )

    def Shrink(self):
        # get inputs
        slicDir = self.ui.sliceDirBtnGrp_MSKJZ.checkedButton().text()
        outShrkFac = float(self.ui.shrkFacLineTxt_MSKJZ.text())
        inThres = float(self.ui.inThresLineTxt_MSKJZ.text())
        outThres = float(self.ui.outThresLineTxt_MSKJZ.text())
        minInA = float(self.ui.minInALineTxt_MSKJZ.text())
        minDilDisk = float(self.ui.minDilDiskLineTxt_MSKJZ.text())
        closeDisk = float(self.ui.closeDiskLineTxt_MSKJZ.text())
        openDisk = float(self.ui.openDiskLineTxt_MSKJZ.text())
        minThickDisk = float(self.ui.minThickDiskLineTxt_MSKJZ.text())
        msg = "slicDir: {}".format(slicDir) + \
              "\noutShrkFac: {}".format(outShrkFac) + \
              "\ninThres: {}".format(inThres) + \
              "\noutThres: {}".format(outThres) + \
              "\ncloseDisk: {}".format(closeDisk)

        print(msg)

        # load
        self.LoadData()

        # compare shape
        compareShp = Post_Image_Process_Functions.CompareArrShape(
            dataMat1=self.lumMsk.OriData,
            dataMat2=self.periMsk.OriData,
            DialogWarn=False
        )
        ## Not same shape
        if compareShp["error"]:
            # update message
            self.UpdateMsgLog(
                msg=compareShp["errorMessage"]
            )
            return
            ## for tissue
        if self.tissueShrk:
            compareShp = Post_Image_Process_Functions.CompareArrShape(
                dataMat1=self.lumMsk.OriData,
                dataMat2=self.tissueMsk.OriData,
                DialogWarn=False
            )
            ## Not same shape
            if compareShp["error"]:
                # update message
                self.UpdateMsgLog(
                    msg=compareShp["errorMessage"]
                )
                return

        # create empty
        lumMskShp = numpy.shape(self.lumMsk.OriData)
        self.lumMskShrk = numpy.zeros(lumMskShp)
        self.periMskShrk = numpy.zeros(lumMskShp)
        self.tissueMskShrk = numpy.zeros(lumMskShp)

        # slicing and shrink
        if slicDir == "X":
            for imgSlc in range(lumMskShp[0]):
                # slice
                lumMsk = self.lumMsk.OriData[imgSlc]
                periMsk = self.periMsk.OriData[imgSlc]

                # jump zero slice
                if numpy.sum(periMsk) == 0:
                    continue

                # shrink
                lumPeriShrk = Image_Process_Functions.ShrinkTwoMasks(
                    outMask=periMsk,
                    inMask=lumMsk,
                    outThresGreater=outThres,
                    inThresGreater=inThres,
                    shrkFac=outShrkFac,
                    minInA=minInA,
                    minDilDisk=minDilDisk
                )

                # Show error
                if lumPeriShrk["error"]:
                    msg = "ERROR in Shrinkage!!!" + lumPeriShrk["errorMessage"]
                    self.UpdateMsgLog(
                        msg=msg
                    )
                    print(msg)
                print("X direction Slice: {}/{} finish Lumen and Periluminal region shrinkage".format(
                    imgSlc, lumMskShp[0]
                ))

                # shirk tissue
                if self.tissueShrk:
                    tissueMsk = self.tissueMsk.OriData[imgSlc]

                    # jump
                    jumpFlg = False
                    if numpy.sum(tissueMsk) == 0:
                        jumpFlg = True

                    # not jump non-empty tissue
                    if not jumpFlg:
                        print("############Tissue Shrinkage###########")
                        tissueShrk = Image_Process_Functions.ShrinkReferenceMask(
                            outMask=lumPeriShrk["outerShrinkMask"],
                            inMask=lumPeriShrk["innerShrinkMask"],
                            compMsk=tissueMsk,
                            inShrkFac=lumPeriShrk["innerShrinkRatio"],
                            outShrkFac=lumPeriShrk["outerShrinkRatio"],
                            inMskCenX=lumPeriShrk["insideMaskCentroidX"],
                            inMskCenY=lumPeriShrk["insideMaskCentroidY"],
                            closeDisk=closeDisk,
                            openDisk=openDisk,
                            inDilDisk=minThickDisk
                        )
                        print("X direction Slice: {}/{} finish Tissue region shrinkage".format(
                            imgSlc, lumMskShp[0]
                        ))
                        # stacking
                        self.lumMskShrk[imgSlc] = tissueShrk["shrinkNewInMask"]
                        self.periMskShrk[imgSlc] = tissueShrk["shrinkNewOutMask"]
                        self.tissueMskShrk[imgSlc] = tissueShrk["shrinkComponentMask"]
                    else:
                        # stacking
                        self.lumMskShrk[imgSlc] = lumPeriShrk["innerShrinkMask"]
                        self.periMskShrk[imgSlc] = lumPeriShrk["outerShrinkMask"]
                else:
                    # stacking
                    self.lumMskShrk[imgSlc] = lumPeriShrk["innerShrinkMask"]
                    self.periMskShrk[imgSlc] = lumPeriShrk["outerShrinkMask"]

        if slicDir == "Y":
            for imgSlc in range(lumMskShp[1]):
                # slice
                lumMsk = self.lumMsk.OriData[:, imgSlc, :]
                periMsk = self.periMsk.OriData[:, imgSlc, :]

                # jump zero slice
                if numpy.sum(periMsk) == 0:
                    continue

                # shrink
                lumPeriShrk = Image_Process_Functions.ShrinkTwoMasks(
                    outMask=periMsk,
                    inMask=lumMsk,
                    outThresGreater=outThres,
                    inThresGreater=inThres,
                    shrkFac=outShrkFac,
                    minInA=minInA,
                    minDilDisk=minDilDisk
                )
                print("Y direction Slice: {}/{} finish Lumen and Periluminal region shrinkage".format(
                    imgSlc, lumMskShp[1]
                ))

                # shirk tissue
                if self.tissueShrk:
                    tissueMsk = self.tissueMsk.OriData[:, imgSlc, :]

                    # jump
                    jumpFlg = False
                    if numpy.sum(tissueMsk) == 0:
                        jumpFlg = True

                    # not jump non-empty tissue
                    if not jumpFlg:
                        tissueShrk = Image_Process_Functions.ShrinkReferenceMask(
                            outMask=lumPeriShrk["outerShrinkMask"],
                            inMask=lumPeriShrk["innerShrinkMask"],
                            compMsk=tissueMsk,
                            inShrkFac=lumPeriShrk["innerShrinkRatio"],
                            outShrkFac=lumPeriShrk["outerShrinkRatio"],
                            inMskCenX=lumPeriShrk["insideMaskCentroidX"],
                            inMskCenY=lumPeriShrk["insideMaskCentroidY"],
                            closeDisk=closeDisk,
                            openDisk=openDisk,
                            inDilDisk=minThickDisk
                        )
                        print("Y direction Slice: {}/{} finish Tissue region shrinkage".format(
                            imgSlc, lumMskShp[1]
                        ))
                        # stacking
                        self.lumMskShrk[:, imgSlc, :] = tissueShrk["shrinkNewInMask"]
                        self.periMskShrk[:, imgSlc, :] = tissueShrk["shrinkNewOutMask"]
                        self.tissueMskShrk[:, imgSlc, :] = tissueShrk["shrinkComponentMask"]
                    else:
                        # stacking
                        self.lumMskShrk[:, imgSlc, :] = lumPeriShrk["innerShrinkMask"]
                        self.periMskShrk[:, imgSlc, :] = lumPeriShrk["outerShrinkMask"]
                else:
                    # stacking
                    self.lumMskShrk[:, imgSlc, :] = lumPeriShrk["innerShrinkMask"]
                    self.periMskShrk[:, imgSlc, :] = lumPeriShrk["outerShrinkMask"]

        if slicDir == "Z":
            for imgSlc in range(lumMskShp[2]):
                # slice
                lumMsk = self.lumMsk.OriData[:, :, imgSlc]
                periMsk = self.periMsk.OriData[:, :, imgSlc]

                # jump zero slice
                if numpy.sum(periMsk) == 0:
                    continue

                # shrink
                lumPeriShrk = Image_Process_Functions.ShrinkTwoMasks(
                    outMask=periMsk,
                    inMask=lumMsk,
                    outThresGreater=outThres,
                    inThresGreater=inThres,
                    shrkFac=outShrkFac,
                    minInA=minInA,
                    minDilDisk=minDilDisk
                )
                print("Z direction Slice: {}/{} finish Lumen and Periluminal region shrinkage".format(
                    imgSlc, lumMskShp[2]
                ))

                # shirk tissue
                if self.tissueShrk:
                    tissueMsk = self.tissueMsk.OriData[:, :, imgSlc]

                    # jump
                    jumpFlg = False
                    if numpy.sum(tissueMsk) == 0:
                        jumpFlg = True

                    # not jump non-empty tissue
                    if not jumpFlg:
                        tissueShrk = Image_Process_Functions.ShrinkReferenceMask(
                            outMask=lumPeriShrk["outerShrinkMask"],
                            inMask=lumPeriShrk["innerShrinkMask"],
                            compMsk=tissueMsk,
                            inShrkFac=lumPeriShrk["innerShrinkRatio"],
                            outShrkFac=lumPeriShrk["outerShrinkRatio"],
                            inMskCenX=lumPeriShrk["insideMaskCentroidX"],
                            inMskCenY=lumPeriShrk["insideMaskCentroidY"],
                            closeDisk=closeDisk,
                            openDisk=openDisk,
                            inDilDisk=minThickDisk
                        )
                        print("Y direction Slice: {}/{} finish Tissue region shrinkage".format(
                            imgSlc, lumMskShp[2]
                        ))
                        # stacking
                        self.lumMskShrk[:, :, imgSlc] = tissueShrk["shrinkNewInMask"]
                        self.periMskShrk[:, :, imgSlc] = tissueShrk["shrinkNewOutMask"]
                        self.tissueMskShrk[:, :, imgSlc] = tissueShrk["shrinkComponentMask"]
                    else:
                        # stacking
                        self.lumMskShrk[:, :, imgSlc] = lumPeriShrk["innerShrinkMask"]
                        self.periMskShrk[:, :, imgSlc] = lumPeriShrk["outerShrinkMask"]
                else:
                    # stacking
                    self.lumMskShrk[:, :, imgSlc] = lumPeriShrk["innerShrinkMask"]
                    self.periMskShrk[:, :, imgSlc] = lumPeriShrk["outerShrinkMask"]

        # update message
        self.UpdateMsgLog(
            msg="Complete shrinkage:\n" + msg
        )
        print("Complete shrinkage:\n" + msg)

        # 3D Enclose
        self.periMskShrk = Image_Process_Functions.Dilation3DEnclose(
            outMask=self.periMskShrk,
            inMask1=self.lumMskShrk,
            inMask1Thres=0,
            inMask2=self.tissueMskShrk,
            inMask2Thres=0,
            dilDisk=minDilDisk
        )

        # save
        print("Save files")
        self.SaveFile()

        # filtering tissue
        if self.tissueShrk:
            print("Filtering and save tissues")
            self.FilterTissue()

            # update message
            self.UpdateMsgLog(
                msg="Complete Saving!"
            )
            print("Complete Saving!")

    def FilterTissue(self):
        # input range
        tissueVals = Preprocess_Mask.StrToLst(strIn=self.ui.tissueValsTxt_MSKJZ.toPlainText())["floatOut"]
        tissueRefs = Preprocess_Mask.StrToLst(strIn=self.ui.tissueRefsTxt_MSKJZ.toPlainText())["listOut"]

        msg = "tissueVals: {}".format(tissueVals) + \
              "\ntissueRefs: {}".format(tissueRefs)

        # check same size
        # compare shape
        compareShp = Post_Image_Process_Functions.CompareArrShape(
            dataMat1=tissueVals,
            dataMat2=tissueRefs,
            DialogWarn=False
        )
        ## Not same shape
        if compareShp["error"]:
            # update message
            self.UpdateMsgLog(
                msg=compareShp["errorMessage"]
            )
            return

        # filtering and save separately
        for val in range(len(tissueVals)):
            tissueVal = tissueVals[val]
            tissueRef = tissueRefs[val]

            # filtering
            tissueMskVals, tissueMskOnes = Image_Process_Functions.FilterData(
                rangStarts=[tissueVal],
                rangStops=[0],
                dataMat=self.tissueMskShrk,
                funType="single value",
                ConvertVTKType=False,
                InDataType=numpy.float64
            )

            # save
            # Set file name
            self.dir = self.ui.saveDirPathTxt_MSKJZ.toPlainText()
            tissOnePath = Save_Load_File.DateFileName(
                Dir=self.dir,
                fileName=self.name + tissueRef + "SK_FO",
                extension=".nii.gz",
                appendDate=False
            )
            # Set file name
            tissValPath = Save_Load_File.DateFileName(
                Dir=self.dir,
                fileName=self.name + tissueRef + "SK_FV",
                extension=".nii.gz",
                appendDate=False
            )

            # Save
            Save_Load_File.MatNIFTISave(MatData=tissueMskOnes,
                                        imgPath=tissOnePath["CombineName"],
                                        imgInfo=self.lumMsk.OriImag,
                                        ConvertDType=True,
                                        refDataMat=self.lumMsk.OriData)
            Save_Load_File.MatNIFTISave(MatData=tissueMskVals,
                                        imgPath=tissValPath["CombineName"],
                                        imgInfo=self.lumMsk.OriImag,
                                        ConvertDType=True,
                                        refDataMat=self.lumMsk.OriData)

            # update
            self.UpdateMsgLog(
                msg="Save: \n{} \n{}".format(
                    tissOnePath["CombineName"],
                    tissValPath["CombineName"]
                )
            )

        # update message
        self.UpdateMsgLog(
            msg="Complete tissue filtering: \n{}".format(msg)
        )
        print("Complete tissue filtering: \n{}".format(msg))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Save directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.saveDirPathTxt_MSKJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose directory: \n{}".format(dirname))

    def SaveFile(self):
        # Get file name
        if self.ui.nameRefTxt_MSKJZ.toPlainText() == "":
            self.name = Save_Load_File.FilenameFromPath(self.ui.lumPathTxt_MSKJZ.toPlainText())
        else:
            self.name = Save_Load_File.ValidFileName(self.ui.nameRefTxt_MSKJZ.toPlainText())

        # Set file name
        self.dir = self.ui.saveDirPathTxt_MSKJZ.toPlainText()
        lumFilePath = Save_Load_File.DateFileName(
            Dir=self.dir,
            fileName=self.name + "SK_FO",
            extension=".nii.gz",
            appendDate=False
        )
        # Set file name
        periFilePath = Save_Load_File.DateFileName(
            Dir=self.dir,
            fileName=self.name + "PlmSK_FO",
            extension=".nii.gz",
            appendDate=False
        )

        # Save
        Save_Load_File.MatNIFTISave(MatData=self.lumMskShrk,
                                    imgPath=lumFilePath["CombineName"],
                                    imgInfo=self.lumMsk.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.lumMsk.OriData)
        Save_Load_File.MatNIFTISave(MatData=self.periMskShrk,
                                    imgPath=periFilePath["CombineName"],
                                    imgInfo=self.lumMsk.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.lumMsk.OriData)

        # update
        self.UpdateMsgLog(
            msg="Save: \n{} \n{}".format(
                lumFilePath["CombineName"],
                periFilePath["CombineName"]
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