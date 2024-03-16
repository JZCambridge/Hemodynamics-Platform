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

class TissueSegment:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
        
        self.ui.chooseCTABtn_TSSJZ.clicked.connect(lambda: self.ChooseCTADir())
        self.ui.choosePeriBtn_TSSJZ.clicked.connect(lambda: self.ChoosePerilumDir())
        self.ui.chooseLumBtn_TSSJZ.clicked.connect(lambda: self.ChooseLumDir())
        self.ui.saveDirBtn_TSSJZ.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.calcSaveBtn_TSSJZ.clicked.connect(lambda: self.SegmentationSmooth())

        self.InitTissueSegment()

    def InitTissueSegment(self):
        # initial definition
        self.displayData = None
        self.CTA = None
        self.CTAThres = None
        self.inLumMsk = None
        self.CTAGrad = None
        self.CTALOG = None
        self.CTAGradLOG = None
        self.fillClose = None
        self.fillOpenClose = None
        self.periLumGrad = None
        self.activeContourOnes = None
        self.smoothMsk = None

    def ChooseCTADir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Choose CTA directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.CTADirPathTxt_TSSJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose CTA directory: \n{}".format(dirname))

    def ChoosePerilumDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Choose periluminal region directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.periDirPathTxt_TSSJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose periluminal region directory: \n{}".format(dirname))

    def ChooseLumDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Choose Lumen directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.lumDirPathTxt_TSSJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose Lumen directory: \n{}".format(dirname))

    def ChooseSaveDir(self):

        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_TSSJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose directory: \n{}".format(dirname))

    def SegmentationSmooth(self):
        # get inputs
        ## File in
        CTADir = self.ui.CTADirPathTxt_TSSJZ.toPlainText()
        periDir = self.ui.periDirPathTxt_TSSJZ.toPlainText()
        lumDir = self.ui.lumDirPathTxt_TSSJZ.toPlainText()
        CTANames = Preprocess_Mask.StrToLst(strIn=self.ui.CTANameTxt_TSSJZ.toPlainText())["listOut"]
        periNames = Preprocess_Mask.StrToLst(strIn=self.ui.periNameTxt_TSSJZ.toPlainText())["listOut"]
        lumNames = Preprocess_Mask.StrToLst(strIn=self.ui.lumNameTxt_TSSJZ.toPlainText())["listOut"]
        ## HU segmentation
        outNameRefs = Preprocess_Mask.StrToLst(strIn=self.ui.outNameRefTxt_TSSJZ.toPlainText())["listOut"]
        mskVals = Preprocess_Mask.StrToLst(strIn=self.ui.mskValsTxt_TSSJZ.toPlainText())["floatOut"]
        thresMins = Preprocess_Mask.StrToLst(strIn=self.ui.thresMinsTxt_TSSJZ.toPlainText())["floatOut"]
        thresMaxs = Preprocess_Mask.StrToLst(strIn=self.ui.thresMaxsTxt_TSSJZ.toPlainText())["floatOut"]
        opens = Preprocess_Mask.StrToLst(strIn=self.ui.opensTxt_TSSJZ.toPlainText())["booleanOut"]
        openRadii = Preprocess_Mask.StrToLst(strIn=self.ui.openRadiiTxt_TSSJZ.toPlainText())["floatOut"]
        closes = Preprocess_Mask.StrToLst(strIn=self.ui.closesTxt_TSSJZ.toPlainText())["booleanOut"]
        closeRadii = Preprocess_Mask.StrToLst(strIn=self.ui.closeRadiiTxt_TSSJZ.toPlainText())["floatOut"]
        ## Connectivity
        connects = Preprocess_Mask.StrToLst(strIn=self.ui.connectsTxt_TSSJZ.toPlainText())["booleanOut"]
        connectTypes = Preprocess_Mask.StrToLst(strIn=self.ui.connectTypesTxt_TSSJZ.toPlainText())["floatOut"]
        volThresholds = Preprocess_Mask.StrToLst(strIn=self.ui.volThresholdsTxt_TSSJZ.toPlainText())["floatOut"]
        ## smooth
        smooths = Preprocess_Mask.StrToLst(strIn=self.ui.smoothsTxt_TSSJZ.toPlainText())["booleanOut"]
        radialSamplingSize = int(self.ui.radialSamplingSizeLineTxt_TSSJZ.text())
        initSplineSmooth = int(self.ui.initSplineSmoothLineTxt_TSSJZ.text())
        initRadialSplineOrder = int(self.ui.initRadialSplineOrderLineTxt_TSSJZ.text())
        vertSplineSmoothFac = float(self.ui.vertSplineSmoothFacLineTxt_TSSJZ.text())
        vertRadialSplineOrder = int(self.ui.vertRadialSplineOrderLineTxt_TSSJZ.text())
        resampleFac = int(self.ui.resampleFacLineTxt_TSSJZ.text())
        planeSplineSmoothFac = float(self.ui.planeSplineSmoothFacLineTxt_TSSJZ.text())
        planeSmoothOrder = int(self.ui.planeSmoothOrderLineTxt_TSSJZ.text())
        ## output
        outDir = self.ui.saveDirPathTxt_TSSJZ.toPlainText()
        outfileRefs = Preprocess_Mask.StrToLst(strIn=self.ui.outRefsTxt_TSSJZ.toPlainText())["listOut"]
        FEAOuts = Preprocess_Mask.StrToLst(strIn=self.ui.FEAOutsTxt_TSSJZ.toPlainText())["booleanOut"]
        wallDilateRadii = Preprocess_Mask.StrToLst(strIn=self.ui.wallDilateRadiiTxt_TSSJZ.toPlainText())["floatOut"]

        msg = "CTADir: {}".format(CTADir) + \
              "\nperiDir: {}".format(periDir) + \
              "\nlumDir: {}".format(lumDir) + \
              "\nCTANames: {}".format(CTANames) + \
              "\nperiNames: {}".format(periNames) + \
              "\nlumNames: {}".format(lumNames) + \
              "\noutNameRefs: {}".format(outNameRefs) + \
              "\nmskVals: {}".format(mskVals) + \
              "\nthresMins: {}".format(thresMins) + \
              "\nthresMaxs: {}".format(thresMaxs) + \
              "\nopens: {}".format(opens) + \
              "\nopenRadii: {}".format(openRadii) + \
              "\ncloses: {}".format(closes) + \
              "\ncloseRadii: {}".format(closeRadii) + \
              "\nconnects: {}".format(connects) + \
              "\nconnectTypes: {}".format(connectTypes) + \
              "\nvolThresholds: {}".format(volThresholds) + \
              "\nsmooths: {}".format(smooths) + \
              "\nradialSamplingSize: {}".format(initRadialSplineOrder) + \
              "\ninitSplineSmooth: {}".format(initSplineSmooth) + \
              "\ninitRadialSplineOrder: {}".format(initRadialSplineOrder) + \
              "\nvertSplineSmoothFac: {}".format(vertSplineSmoothFac) + \
              "\nvertRadialSplineOrder: {}".format(vertRadialSplineOrder) + \
              "\nresampleFac: {}".format(resampleFac) + \
              "\nplaneSplineSmoothFac: {}".format(planeSplineSmoothFac) + \
              "\nplaneSmoothOrder: {}".format(planeSmoothOrder) + \
              "\nFEAOuts: {}".format(FEAOuts) + \
              "\nwallDilateRadii: {}".format(wallDilateRadii) + \
              "\noutDir: {}".format(outDir) + \
              "\noutfileRefs: {}\n".format(outfileRefs)

        print(msg)
        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # looping each case:
        for case in range(len(CTANames)):
            # file name
            CTAName = Save_Load_File.DateFileName(
                Dir=CTADir,
                fileName=CTANames[case],
                extension=".nii.gz",
                appendDate=False
            )["CombineName"]
            periName = Save_Load_File.DateFileName(
                Dir=periDir,
                fileName=periNames[case],
                extension=".nii.gz",
                appendDate=False
            )["CombineName"]
            lumName = Save_Load_File.DateFileName(
                Dir=lumDir,
                fileName=lumNames[case],
                extension=".nii.gz",
                appendDate=False
            )["CombineName"]
            outfileRef = outfileRefs[case]
            FEAOut = FEAOuts[case]
            wallDilateRadius = wallDilateRadii[case]

            # load data
            CTA = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=CTAName
            )
            peri = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=periName
            )
            lum = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=lumName
            )

            # update message
            self.UpdateMsgLog(
                msg="Load:\n{} \n{} \n{}".format(
                    CTAName,
                    periName,
                    lumName
                )
            )

            allCompnentMsks = numpy.zeros(numpy.shape(CTA.OriData))

            # loop each segmentaion for each case
            for comp in range(len(outNameRefs)):
                # get values
                ## HU segmentation
                outNameRef = outNameRefs[comp]
                mskVal = mskVals[comp]
                thresMin = thresMins[comp]
                thresMax = thresMaxs[comp]
                open = opens[comp]
                openRadius = openRadii[comp]
                close = closes[comp]
                closeRadius = closeRadii[comp]
                ## Connectivity
                connect = connects[comp]
                connectType = connectTypes[comp]
                volThreshold = volThresholds[comp]
                ## smooth
                smooth = smooths[comp]

                # filter HU
                ## create object
                tissueMsk = Post_Image_Process_Functions.FilterValAreaVol(CTA.OriData)
                ## filter CTA and remove lumen
                tissueMsk.MaskData(
                    msk=peri.OriData,
                    mskRemove=lum.OriData,
                    remove=True,
                    mskThres=0
                )
                ## filter HU
                ### dealing with '0'!
                if thresMin < 0 and thresMax > 0:
                    msg = "thresMin = {} < 0 and thresMax = {} > 0 HAVE '0'".format(
                        thresMin,
                        thresMax
                    )
                    self.UpdateMsgLog(msg=msg)
                    print(msg)
                    tissueMsk.FilterArea(
                        rangStarts=[thresMin, 0.0000001],
                        rangStops=[-0.0000001, thresMax],
                        funType="boundary",
                        openOp=open,
                        openR=openRadius,
                        closeOp=close,
                        closeR=closeRadius
                    )
                elif thresMin > 0 and thresMax < 0:
                    msg = "thresMin = {} > 0 and thresMax = {} < 0 HAVE '0'".format(
                        thresMin,
                        thresMax
                    )
                    self.UpdateMsgLog(msg=msg)
                    print(msg)
                    tissueMsk.FilterArea(
                        rangStarts=[thresMax, 0.0000001],
                        rangStops=[-0.0000001, thresMin],
                        funType="boundary",
                        openOp=open,
                        openR=openRadius,
                        closeOp=close,
                        closeR=closeRadius
                    )
                elif thresMin == 0 and thresMax == 0:
                    # update message
                    msg = "CANNOT use 0!!! (Backgoround issue!)"
                    self.UpdateMsgLog(msg=msg)
                    print(msg)
                    return
                else:
                    msg = "thresMin = {} and thresMax = {} No '0' in the range".format(
                        thresMin,
                        thresMax
                    )
                    self.UpdateMsgLog(msg=msg)
                    print(msg)
                    tissueMsk.FilterArea(
                        rangStarts=[thresMax],
                        rangStops=[thresMin],
                        funType="boundary",
                        openOp=open,
                        openR=openRadius,
                        closeOp=close,
                        closeR=closeRadius
                    )

                ## Connectivity filter
                if connect:
                    msg = "Volume connectivity filter of volume > {}".format(
                        volThreshold
                    )
                    self.UpdateMsgLog(msg=msg)
                    print(msg)

                    tissueMsk.FilterAreaVol(
                        connectType=connectType,
                        FilterThres=volThreshold,
                        smooth=smooth,
                        radialSamplingSize=radialSamplingSize,
                        initSplineSmooth=initSplineSmooth,
                        initRadialSplineOrder=initRadialSplineOrder,
                        vertRadialSplineOrder=vertRadialSplineOrder,
                        vertSplineSmoothFac=vertSplineSmoothFac,
                        resInt=resampleFac,
                        planeSmoothOrder=planeSmoothOrder,
                        planeSplineSmoothFac=planeSplineSmoothFac
                    )
                else:
                    msg = "No volume connectivity filter"
                    self.UpdateMsgLog(msg=msg)
                    print(msg)
                    tissueMsk.NoFilterAreaVol()

                # staking for the FEA case = Smoothing case
                if FEAOut:
                    allCompnentMsks += tissueMsk.outData

                # msg
                self.UpdateMsgLog(msg=tissueMsk.rtrnInfo["message"])
                print(tissueMsk.rtrnInfo["message"])

                # output
                ## Set file name
                outFileValPath = Save_Load_File.DateFileName(
                    Dir=outDir,
                    fileName=outfileRef + outNameRef + "V",
                    extension=".nii.gz",
                    appendDate=False
                )

                outFileOnePath = Save_Load_File.DateFileName(
                    Dir=outDir,
                    fileName=outfileRef + outNameRef + "O",
                    extension=".nii.gz",
                    appendDate=False
                )

                # Save
                Save_Load_File.MatNIFTISave(MatData=tissueMsk.outData * mskVal,
                                            imgPath=outFileValPath["CombineName"],
                                            imgInfo=CTA.OriImag,
                                            ConvertDType=True,
                                            refDataMat=CTA.OriData)
                Save_Load_File.MatNIFTISave(MatData=tissueMsk.outData,
                                            imgPath=outFileOnePath["CombineName"],
                                            imgInfo=CTA.OriImag,
                                            ConvertDType=True,
                                            refDataMat=CTA.OriData)

                # update
                self.UpdateMsgLog(
                    msg="Save: \n{} \n{}".format(
                        outFileValPath["CombineName"],
                        outFileOnePath["CombineName"],
                    )
                )

            # update periluminal mask for CFD use!
            if FEAOut:
                # dilation 3D
                outMsg, mskDilation3D = Image_Process_Functions.DiskDilate(
                    dataMat=allCompnentMsks,
                    Thres=0,
                    dilateIncre=wallDilateRadius,
                    binaryMsk=True,
                    axisChoice='3D'
                )

                # new periluminal region
                nwPeri = ((peri.OriData + mskDilation3D) != 0) * 1

                # save new
                outNewPeriPath = Save_Load_File.DateFileName(
                    Dir=outDir,
                    fileName=outfileRef + "Plm_FO",
                    extension=".nii.gz",
                    appendDate=False
                )

                # Save
                Save_Load_File.MatNIFTISave(MatData=nwPeri,
                                            imgPath=outNewPeriPath["CombineName"],
                                            imgInfo=CTA.OriImag,
                                            ConvertDType=True,
                                            refDataMat=CTA.OriData)

                # update
                msg = "FEA new periluminal mask! \nSave: \n{}".format(
                        outNewPeriPath["CombineName"]
                )
                print(msg)
                self.UpdateMsgLog(
                    msg="FEA new periluminal mask! \nSave: \n{}".format(
                        outNewPeriPath["CombineName"]
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
