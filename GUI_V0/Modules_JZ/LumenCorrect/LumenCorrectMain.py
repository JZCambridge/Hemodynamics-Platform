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
from PySide2.QtUiTools import QUiLoader


##############################################################################

class LumCorrect:
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        # load
        self.ui.chooseCTABtn_LC.clicked.connect(lambda: self.ChooseOpenCTAFile())
        self.ui.chooseMskBtn_LC.clicked.connect(lambda: self.ChooseOpenMskFile())
        self.ui.loadBtn_LC.clicked.connect(lambda: self.LoadData())
        # plot
        self.ui.plotBtn_LC.clicked.connect(lambda: self.PlotOVerlap())
        self.ui.quickPlotBtn_LC.clicked.connect(lambda: self.PlotOVerlap())
        self.ui.plot3DBtn_LC.clicked.connect(lambda: self.VTK3D())
        self.ui.quickPlot3DBtn_LC.clicked.connect(lambda: self.VTK3D())
        # segmentation
        self.ui.initConnectivityBtn_LC.clicked.connect(lambda: self.ConnectivityFilter())
        self.ui.ImageBasicProcessingBtn_LC.clicked.connect(lambda: self.ImageBasicProcessing())
        self.ui.Gaussian3DBtn_LC.clicked.connect(lambda: self.Gaussian3D())
        self.ui.SegmentFilterThresBtn_LC.clicked.connect(lambda: self.SegmentFilterThres())
        self.ui.FindSlicesBtn_LC.clicked.connect(lambda: self.FindSlicesConnectivity())
        self.ui.ManualFillBtn_LC.clicked.connect(lambda: self.ManualFill())
        self.ui.SkinBtn_LC.clicked.connect(lambda: self.Skin())
        # Update
        self.ui.updateMaskBtn_LC.clicked.connect(lambda: self.updateSegmentation())
        self.ui.storeMaskBtn_LC.clicked.connect(lambda: self.intermediateStore())
        # Image Segmentation
        self.ui.thresholdBtn_LC.clicked.connect(lambda: self.ThresholdFilter())
        self.ui.thresholdFilterBtn_LC.clicked.connect(lambda: self.ConnectFilterThres())
        self.ui.actConBtn_LC.clicked.connect(lambda: self.ActiveContour())
        self.ui.ACWEBtn_LC.clicked.connect(lambda: self.ACWE())
        self.ui.ImageSegmentationFilterBtn_LC.clicked.connect(lambda: self.ImageSegmentationFilter())
        # fill value
        self.ui.fillValBtn_LC.clicked.connect(lambda: self.OneToValMak())
        # save
        self.ui.chooseDirBtn_LC.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.saveBtn_LC.clicked.connect(lambda: self.SaveFile())
        self.ui.clearLogBtn_LC.clicked.connect(lambda: self.ClearLog())
        # Batch process
        self.ui.batchTableBtn_LC.clicked.connect(lambda: self.ChooseBatchFile())
        self.ui.batchProcessBtn_LC.clicked.connect(lambda: self.BatchCorrect())
            
        self.InitProcess()

    def InitProcess(self):
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

    def ChooseOpenCTAFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.CTAPathTxt_LC.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose image file:\n{}".format(filename))

    def ChooseOpenMskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load image segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.mskPathTxt_LC.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose segmentation file:\n{}".format(filename))

    def LoadData(self, CTAPath=None, inMskPath=None):
        # load two data
        if CTAPath is None:
            self.CTA = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.CTAPathTxt_LC.toPlainText()
            )
            CTAPath = self.ui.CTAPathTxt_LC.toPlainText()
        else:
            self.CTA = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=CTAPath
            )

        if inMskPath is None:
            self.inMsk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.mskPathTxt_LC.toPlainText()
            )
            inMskPath = self.ui.mskPathTxt_LC.toPlainText()
        else:
            self.inMsk = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=inMskPath
            )

        # update display data
        self.outputData = copy.deepcopy(self.inMsk.OriData)
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16
            )

        # update message
        self.UpdateMsgLog(
            msg="Load file:\n{} \n{}".format(
                CTAPath,
                inMskPath
            )
        )

    """
    ##############################################################################
    # Visualisation
    ##############################################################################
    """

    def PlotOVerlap(self):
        # get inputs
        slicDir = self.ui.plotAixsLineTxt_LC.text()
        title = Preprocess_Mask.StrToLst(strIn=self.ui.plotTitleTxt_LC.toPlainText())["listOut"]
        plotRange = Preprocess_Mask.StrToLst(strIn=self.ui.plotThresTxt_LC.toPlainText())["booleanOut"]
        minLst = Preprocess_Mask.StrToLst(strIn=self.ui.plotMinTxt_LC.toPlainText())["floatOut"]
        maxLst = Preprocess_Mask.StrToLst(strIn=self.ui.plotMaxTxt_LC.toPlainText())["floatOut"]
        cursorChoice = self.ui.cursorChoiceBtnGrp_LC.checkedButton().text() == 'Yes'

        Use_Plt.slider3Display(
            matData1=self.CTA.OriData,
            matData2=self.outputData,
            matData3=[0],
            fig3OverLap=True,
            ShareX=True,
            ShareY=True,
            ask23MatData=False,
            wait=True,
            slicDiect=slicDir,
            title=title,
            plotRange=plotRange,
            winMin=minLst,
            winMax=maxLst,
            cursorChoice=cursorChoice
        )

    def VTK3D(self):
        # Choose original mask
        maskChoice = self.ui.oriMaskChoiceCBox_LC.currentText()
        oriMaskData = self.inMsk.OriData

        # update mask
        if maskChoice == "Original Mask":
            oriMaskData = self.inMsk.OriData
        elif maskChoice == "Segmentation Connectivity Filter":
            oriMaskData = self.ConnectivityFilterData
        elif maskChoice == "Segmentation Morphology":
            oriMaskData = self.ImageBasicProcessingData
        elif maskChoice == "Segmentation Gaussian 3D":
            oriMaskData = self.Gaussian3DData
        elif maskChoice == "Segmentation Thresholding":
            oriMaskData = self.SegmentFilterThresData
        elif maskChoice == "Image ACWE (without edge)":
            oriMaskData = self.ACWEData
        elif maskChoice == "Image Segmentation Thresholding":
            oriMaskData = self.ImageSegmentationFilterData
        elif maskChoice == "Image Thresholding Mask":
            oriMaskData = self.thresHUOnes
        elif maskChoice == "Image Connectivity Filter":
            oriMaskData = self.thresHUOnes
        elif maskChoice == "Image Active Contour":
            oriMaskData = self.activeContourFOnes
        elif maskChoice == "Segmentation Add Original Mask":
            oriMaskData = self.AddOriMaskData
        elif maskChoice == "Segmentation Munaul Fill":
            oriMaskData = self.ManualFillData
        elif maskChoice == "Intermediate Mask":
            oriMaskData = self.intermediateData
        elif maskChoice == "Segmentation 2D Connectivity":
            oriMaskData = self.filterThresHUOnes

        # filtered original mask
        oriMask = VTK_Numpy.vtkImageImportFromArray()
        oriMask.SetArray(imArray=oriMaskData)
        oriMask.SetDataSpacing(self.inMsk.OriImag.GetSpacing())
        oriMask.SetDataOrigin(self.inMsk.OriImag.GetOrigin())
        oriMask.Update()

        # current data
        currentMask = VTK_Numpy.vtkImageImportFromArray()
        currentMask.SetArray(imArray=self.outputData)
        currentMask.SetDataSpacing(self.inMsk.OriImag.GetSpacing())
        currentMask.SetDataOrigin(self.inMsk.OriImag.GetOrigin())
        currentMask.Update()

        if self.modelui:
            ui=self.modelui
        else:
            ui=self.ui

        # layout frame
        # add dock
        dock = QT_GUI.CreateDockWidget(
            parent=ui,
            name="Lum3D_" + str(self.i),
            position='Right'
        )
        frame = dock.GetFrame()
        layout = dock.GetLayout()
        self.i += 1

        # visualisation
        VTK_Functions.DisplayOverlayNifti(
            ActFile_Data=[oriMask, currentMask],
            ThresUp=[1000, 1000],
            ThresBot=[1, 1],
            opacityChoice=[0.5, 0.5],
            colorChoice=['Green', 'Red'],
            ThresDType=numpy.float64,
            CaseRef=["Original mask is GREEN, current mask in RED"],
            qt=True,
            qtFrame=frame,
            qtLayout=layout
        )

    """
    ##############################################################################
    # Pure segmentation based correction
    ##############################################################################
    """

    def ConnectivityFilter(self, FilterAreaChoice=None, connectIn=None):
        # input
        if FilterAreaChoice is None:
            FilterAreaChoice = self.ui.connectChoicLineTxt_LC.text()
        if connectIn is None:
            connectIn = int(self.ui.connectTypeLineTxt_LC.text())

        # message
        msg = "FilterAreaChoice: {}".format(FilterAreaChoice) + \
              "\nconnectIn: {}".format(connectIn)

        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # connectivity filter
        initConnectFilterOnes, initConnectFilterVals = Image_Process_Functions.ConnectivityFilter(
            matData=self.outputData,
            connectType=connectIn,
            keepNumber=1,
            FilterArea=FilterAreaChoice
        )

        # convert data type
        try:
            initConnectFilterVals = numpy.array(
                initConnectFilterVals,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            initConnectFilterVals = numpy.array(
                initConnectFilterVals,
                dtype=numpy.int16
            )

        # update fill mask value
        if self.initConnectFilterVals is None:
            self.initConnectFilterVals = copy.deepcopy(initConnectFilterVals)

        # update display data
        self.outputData = copy.deepcopy(initConnectFilterVals)
        self.ConnectivityFilterData = copy.deepcopy(initConnectFilterVals)
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16
            )

        # update
        self.UpdateMsgLog(
            msg="Complete segmentation 3D connectivity filter"
        )

    def ImageBasicProcessing(
            self,
            axisChoice=None,
            diaChoice=None,
            funcChoose=None,
            dilateIncre=None,
            sliceStarts=None,
            sliceStops=None
    ):

        # input
        if axisChoice is None: axisChoice = self.ui.directionBtnGrp_LC.checkedButton().text()
        if diaChoice is None: diaChoice = self.ui.unitChoiceCBox_LC.currentText()
        if funcChoose is None: funcChoose = self.ui.morphology_LC.checkedButton().text()
        if dilateIncre is None: dilateIncre = int(self.ui.dilateIncre_LC.text())
        if sliceStarts is None: sliceStarts = \
            Preprocess_Mask.StrToLst(strIn=self.ui.sliceStartsIBPTxt_LC.toPlainText())["floatOut"]
        if sliceStops is None: sliceStops = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStopsIBPTxt_LC.toPlainText())[
            "floatOut"]

        # message
        msg = "axisChoice: {}".format(axisChoice) + \
              "\ndiaChoice: {}".format(diaChoice) + \
              "\ndilateIncre: {}".format(dilateIncre) + \
              "\nfuncChoose: {}".format(funcChoose) + \
              "\nrangeStarts: {}".format(sliceStarts) + \
              "\nrangeStops: {}".format(sliceStops)

        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # dilation choice
        ## iteration
        iterateDilate = diaChoice == "iteration"
        if iterateDilate: print("Use Iteration!")

        ## diameter
        diameter = diaChoice == "diameter"
        if diameter: print("Use Diameter!")

        ## mm
        if diaChoice == "mm":
            spacing = self.inMsk.OriImag.GetSpacing()
            spacing_z = spacing[0]  # numpy array has flipped X and Z
            spacing_y = spacing[1]
            spacing_x = spacing[2]

            print("Convert {} mm".format(dilateIncre))

            if axisChoice == 'X':
                verticalDivide = spacing_y
                horizontalDivide = spacing_z
                dilateIncre = round(dilateIncre / ((verticalDivide + horizontalDivide) * 0.5))
            elif axisChoice == 'Y':
                verticalDivide = spacing_x
                horizontalDivide = spacing_z
                dilateIncre = round(dilateIncre / ((verticalDivide + horizontalDivide) * 0.5))
            elif axisChoice == 'Z':
                verticalDivide = spacing_x
                horizontalDivide = spacing_y
                dilateIncre = round(dilateIncre / ((verticalDivide + horizontalDivide) * 0.5))
            else:
                dilateIncre = round(dilateIncre / ((spacing_x + spacing_z + spacing_y) / 3))

            print("To {} voxels".format(dilateIncre))

        # function
        imageMorph = Image_Process_Functions.OpenCloseDilateErrodeSlices(
            dataMat=self.outputData,
            funcChoose=funcChoose,
            Thres=0,
            dilateIncre=dilateIncre,
            binaryMsk=False,
            axisChoice=axisChoice,
            iterateDilate=iterateDilate,
            sliceStarts=sliceStarts,
            sliceStops=sliceStops,
            diameter=diameter
        )

        # dealing error
        if imageMorph["error"]:
            # update
            self.UpdateMsgLog(
                msg="ERROR! \n{}".format(imageMorph["message"])
            )
            return

        # update output
        self.outputData = copy.deepcopy(imageMorph["outMask"])
        self.ImageBasicProcessingData = imageMorph["outMask"]
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16
            )

        # update
        self.UpdateMsgLog(
            msg="Complete segmentation morphological Process\n" + imageMorph["message"]
        )

    # extract skin
    def Skin(self, valRange=None):
        # input
        if valRange is not None:
            valRange = Preprocess_Mask.StrToLst(strIn=self.ui.valsLineTxt_LC.text())["floatOut"]

        # skin
        self.outputDataOnes, self.outputData = Image_Process_Functions.GetSkin(
            inArr=self.outputData,
            filterVals=valRange
        )

        # update
        self.UpdateMsgLog(
            msg="Complete Skin Extraction"
        )

    def Gaussian3D(self):
        # input
        maskValue = int(self.ui.maskValueGauss_LC.text())
        sigma = int(self.ui.sigmaGauss_LC.text())

        # message
        msg = "maskValue: {}".format(maskValue) + \
              "\nsigma: {}".format(sigma)

        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # function
        self.Gaussian3DData = scipy.ndimage.gaussian_filter(
            input=self.outputData * maskValue,
            sigma=sigma
        )

        # update output
        self.outputData = copy.deepcopy(self.Gaussian3DData)
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16
            )

        # update
        self.UpdateMsgLog(
            msg="Complete Gaussian 3D smoothing"
        )

    def SegmentFilterThres(self):
        # input
        funType = self.ui.funTypeCBox_LC.currentText()
        rangStarts = Preprocess_Mask.StrToLst(
            strIn=self.ui.SegmentFilterRangStartsTxt_LC.toPlainText()
        )["floatOut"]
        rangStops = Preprocess_Mask.StrToLst(
            strIn=self.ui.SegmentFilterRangStopsTxt_LC.toPlainText()
        )["floatOut"]

        # message
        msg = "funType: {}".format(funType) + \
              "\nrangStarts: {}".format(rangStarts) + \
              "\nrangStops: {}".format(rangStops)

        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # function
        mskVals, mskOnes = Image_Process_Functions.FilterData(
            rangStarts=rangStarts,
            rangStops=rangStops,
            dataMat=self.outputData,
            funType=funType,
            ConvertVTKType=False,
            InDataType=numpy.float64
        )

        # update output
        self.outputData = copy.deepcopy(mskOnes)
        self.SegmentFilterThresData = mskOnes
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16
            )

        # update
        self.UpdateMsgLog(
            msg="Complete Segmentation threshold filtering"
        )

    def FindSlicesConnectivity(self):
        # input
        compareType = self.ui.compareTypeCBox_LC.currentText()
        direction = self.ui.findSliceDirectBtnGrp_LC.checkedButton().text()
        sliceStarts = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStartsFindSlcTxt_LC.toPlainText())["floatOut"]
        sliceStops = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStopsFindSlcTxt_LC.toPlainText())["floatOut"]
        rangeStarts = Preprocess_Mask.StrToLst(strIn=self.ui.rangeStartsTxt_LC.toPlainText())["floatOut"]
        rangeStops = Preprocess_Mask.StrToLst(strIn=self.ui.rangeStopsTxt_LC.toPlainText())["floatOut"]

        # message
        msg = "compareType: {}".format(compareType) + \
              "\ndirection: {}".format(direction) + \
              "\nsliceStarts: {}".format(sliceStarts) + \
              "\nsliceStops: {}".format(sliceStops) + \
              "\nrangeStarts: {}".format(rangeStarts) + \
              "\nrangeStops: {}".format(rangeStops)
        # update
        self.UpdateMsgLog(
            msg=msg
        )
        if compareType == "connectivity":
            rtrnInfo = Image_Process_Functions.FindConnectivity(
                inMat=self.outputData,
                directions=direction,
                sliceStarts=sliceStarts,
                sliceStops=sliceStops,
                connectivities=rangeStarts,
                greaterVals=rangeStops
            )
        else:
            rtrnInfo = Image_Process_Functions.FindSlicesArea(
                inMat=self.outputData,
                directions=direction,
                compareTypes=compareType,
                sliceStarts=sliceStarts,
                sliceStops=sliceStops,
                rangeStarts=rangeStarts,
                rangeStops=rangeStops
            )
        # dealing error
        if rtrnInfo["error"]:
            # update
            self.UpdateMsgLog(
                msg="ERROR! \n{}".format(rtrnInfo["message"])
            )
            return

        # update txt:
        self.ui.FindSlicesTxt_LC.setPlainText('{}'.format(rtrnInfo["compareResults"]))

        # update
        self.UpdateMsgLog(
            msg="Compare slice area complete. \n{} \n{}".format(rtrnInfo["message"], rtrnInfo["compareResults"])
        )

    def ManualFill(
            self,
            maskType=None,
            actualUnit=None,
            fillReplaceMask=None,
            direction=None,
            horizontalLengths=None,
            verticalLengths=None,
            sliceStarts=None,
            sliceStops=None,
            posititionFirsts=None,
            positionSeconds=None,
    ):
        # input
        if maskType is None:
            maskType = self.ui.maskTypeCBox_LC.currentText()
        if actualUnit is None:
            actualUnit = self.ui.unitTypeCBox_LC.currentText()
        if fillReplaceMask is None:
            fillReplaceMask = self.ui.fillReplaceMaskCBox_LC.currentText()
        if direction is None:
            direction = self.ui.manFillDirectBtnGrp_LC.checkedButton().text()
        if horizontalLengths is None:
            horizontalLengths = Preprocess_Mask.StrToLst(strIn=self.ui.horizontalLengthsTxt_LC.toPlainText())[
                "floatOut"]
        if verticalLengths is None:
            verticalLengths = Preprocess_Mask.StrToLst(strIn=self.ui.verticalLengthsTxt_LC.toPlainText())["floatOut"]
        if sliceStarts is None:
            sliceStarts = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStartsTxt_LC.toPlainText())["floatOut"]
        else:
            sliceStarts = [i - 1 for i in sliceStarts]  # ITK_SNAP start from 1
        if sliceStops is None:
            sliceStops = Preprocess_Mask.StrToLst(strIn=self.ui.sliceStopsTxt_LC.toPlainText())["floatOut"]
        else:
            sliceStops = [i - 1 for i in sliceStops]  # ITK_SNAP start from 1
        if posititionFirsts is None:
            posititionFirsts = Preprocess_Mask.StrToLst(strIn=self.ui.posititionFirstsTxt_LC.toPlainText())["floatOut"]
        else:
            posititionFirsts = [i - 1 for i in posititionFirsts]  # ITK_SNAP start from 1
        if positionSeconds is None:
            positionSeconds = Preprocess_Mask.StrToLst(strIn=self.ui.positionSecondsTxt_LC.toPlainText())["floatOut"]
        else:
            positionSeconds = [i - 1 for i in positionSeconds]  # ITK_SNAP start from 1

        # message
        msg = "maskType: {}".format(maskType) + \
              "\nfillReplaceMask: {}".format(fillReplaceMask) + \
              "\ndirection: {}".format(direction) + \
              "\nhorizontalLengths: {}".format(horizontalLengths) + \
              "\nverticalLengths: {}".format(verticalLengths) + \
              "\nsliceStarts: {}".format(sliceStarts) + \
              "\nsliceStops: {}".format(sliceStops) + \
              "\nposititionFirsts: {}".format(posititionFirsts) + \
              "\npositionSeconds: {}".format(positionSeconds)
        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # function
        # man fill
        if maskType == 'rectangle' or \
                maskType == 'ellipse':

            # actual units?
            horizontalDivide = 1
            verticalDivide = 1

            if actualUnit == 'mm':
                spacing = self.inMsk.OriImag.GetSpacing()
                spacing_z = spacing[0]  # numpy array has flipped X and Z
                spacing_y = spacing[1]
                spacing_x = spacing[2]

                if direction == 'X':
                    verticalDivide = spacing_y
                    horizontalDivide = spacing_z
                elif direction == 'Y':
                    verticalDivide = spacing_x
                    horizontalDivide = spacing_z
                elif direction == 'Z':
                    verticalDivide = spacing_x
                    horizontalDivide = spacing_y

            rtrnInfo = Image_Process_Functions.FillMask3D(
                inMat=self.outputData,
                directions=direction,
                maskTypes=maskType,
                verticalLengths=[x / verticalDivide for x in verticalLengths],
                horizontalLengths=[x / horizontalDivide for x in horizontalLengths],
                sliceStarts=sliceStarts,
                sliceStops=sliceStops,
                posititionFirsts=posititionFirsts,
                positionSeconds=positionSeconds
            )
            # dealing error
            if rtrnInfo["error"]:
                # update
                self.UpdateMsgLog(
                    msg="ERROR! \n{}".format(rtrnInfo["message"])
                )
                return

        elif maskType == 'add' or \
                maskType == 'replace':
            # choose mask
            fillReplaceMask = self.inMsk.OriData

            # update mask
            if maskType == "Original Mask":
                fillReplaceMask = self.inMsk.OriData
            elif maskType == "Segmentation Connectivity Filter":
                fillReplaceMask = self.ConnectivityFilterData
            elif maskType == "Segmentation Morphology":
                fillReplaceMask = self.ImageBasicProcessingData
            elif maskType == "Segmentation Gaussian 3D":
                fillReplaceMask = self.Gaussian3DData
            elif maskType == "Segmentation Thresholding":
                fillReplaceMask = self.SegmentFilterThresData
            elif maskType == "Image ACWE (without edge)":
                fillReplaceMask = self.ACWEData
            elif maskType == "Image Segmentation Thresholding":
                fillReplaceMask = self.ImageSegmentationFilterData
            elif maskType == "Image Thresholding Mask":
                fillReplaceMask = self.thresHUOnes
            elif maskType == "Image Connectivity Filter":
                fillReplaceMask = self.thresHUOnes
            elif maskType == "Image Active Contour":
                fillReplaceMask = self.activeContourFOnes
            elif maskType == "Segmentation Add Original Mask":
                fillReplaceMask = self.AddfillReplaceMask
            elif maskType == "Segmentation Munaul Fill":
                fillReplaceMask = self.ManualFillData
            elif maskType == "Intermediate Mask":
                fillReplaceMask = self.intermediateData
            elif maskType == "Segmentation 2D Connectivity":
                fillReplaceMask = self.filterThresHUOnes

            # replace
            rtrnInfo = Image_Process_Functions.FillReplaceMask3D(
                inMat=self.outputData,
                inReplaceAddMat=fillReplaceMask,
                directions=direction,
                maskTypes=maskType,
                sliceStarts=sliceStarts,
                sliceStops=sliceStops
            )

            # dealing error
            if rtrnInfo["error"]:
                # update
                self.UpdateMsgLog(
                    msg="ERROR! \n{}".format(rtrnInfo["message"])
                )
                return

        # update output
        self.outputData = copy.deepcopy(rtrnInfo['outMask'])
        self.ManualFillData = rtrnInfo['outMask']
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16
            )

        # update
        self.UpdateMsgLog(
            msg="Manual Fill/Replace Complete: \n{}".format(rtrnInfo["message"])
        )

    def ConnectFilterThres(self,
                           connectIn=None,
                           direction=None,
                           sliceStarts=None,
                           sliceStops=None,
                           centerPlane=None,
                           useRef=None,
                           disk=None,
                           diskRow=None,
                           diskColm=None,
                           diskRadius=None,
                           ):  # working with one mask!
        # input
        if connectIn is None:
            connectIn = int(self.ui.connectThresTypeLineTxt_LC.text())
        if direction is None:
            direction = self.ui.ConnectFilterThresDirectBtnGrp_LC.checkedButton().text()
        if sliceStarts is None:
            sliceStarts = Preprocess_Mask.StrToLst(strIn=self.ui.ConnectFilterThresSliceStartsTxt_LC.toPlainText())[
                "floatOut"]
        if sliceStops is None:
            sliceStops = Preprocess_Mask.StrToLst(strIn=self.ui.ConnectFilterThresSliceStopsTxt_LC.toPlainText())[
                "floatOut"]
        if centerPlane is None:
            centerPlane = self.ui.ConnectFilterThresCenterPlaneBtnGrp_LC.checkedButton().text() == 'Yes'
        if useRef is None:
            useRef = self.ui.ConnectFilterThresUseRefBtnGrp_LC.checkedButton().text() == 'Original Mask'
        if disk is None:
            disk = self.ui.ConnectFilterThresUseRefBtnGrp_LC.checkedButton().text() == 'Disk'
        if diskRow is None:
            diskRow = int(self.ui.ConnectFilterThresDiskRowLineTxt_LC.text())
        if diskColm is None:
            diskColm = int(self.ui.ConnectFilterThresDiskColmLineTxt_LC.text())
        if diskRadius is None:
            diskRadius = int(self.ui.ConnectFilterThresDiskRadiusLineTxt_LC.text())

        # message
        msg = "connectIn: {}".format(connectIn) + \
              "\ndirection: {}".format(direction) + \
              "\nsliceStarts: {}".format(sliceStarts) + \
              "\nsliceStops: {}".format(sliceStops) + \
              "\ncenterPlane: {}".format(centerPlane) + \
              "\ncenterPlane: {}".format(centerPlane) + \
              "\nuseRef: {}".format(useRef) + \
              "\ndisk: {}".format(disk) + \
              "\ndiskRow: {}".format(diskRow) + \
              "\ndiskColm: {}".format(diskColm) + \
              "\ndiskRadius: {}".format(diskRadius)

        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # connectivity filter
        rtnInfo = Image_Process_Functions.ConnectivityDirectionSlices(
            inMat=self.outputData,
            directions=direction,
            sliceStarts=sliceStarts,
            sliceStops=sliceStops,
            connectivtyTypes=connectIn,
            centerplane=centerPlane,
            disk=disk,
            diskRows=diskRow,
            diskColms=diskColm,
            diskRadii=diskRadius,
            useRef=useRef,
            refMat=self.inMsk.OriData
        )

        # convert data type & update display data
        try:
            self.filterThresHUOnes = numpy.array(
                (rtnInfo["outputMat"] != 0) * self.outputData,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.filterThresHUOnes = numpy.array(
                (rtnInfo["outputMat"] != 0) * self.outputData,
                dtype=numpy.int16
            )
        self.outputData = copy.deepcopy(self.filterThresHUOnes)
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16
            )

        # update
        self.UpdateMsgLog(
            msg="Complete 2D Connectivity Filter \n{}".format(rtnInfo["message"])
        )

    """
    ##############################################################################
    # Update segmentation
    ##############################################################################
    """

    def updateSegmentation(self):
        # print("IN update")
        # get segmentation name
        maskChoice = self.ui.maskChoiceCBox_LC.currentText()
        # update mask
        if maskChoice == "Original Mask":
            self.outputData = copy.deepcopy(self.inMsk.OriData)
        elif maskChoice == "Segmentation Connectivity Filter":
            self.outputData = copy.deepcopy(self.ConnectivityFilterData)
        elif maskChoice == "Segmentation Morphology":
            self.outputData = copy.deepcopy(self.ImageBasicProcessingData)
        elif maskChoice == "Segmentation Gaussian 3D":
            self.outputData = copy.deepcopy(self.Gaussian3DData)
        elif maskChoice == "Segmentation Thresholding":
            self.outputData = copy.deepcopy(self.SegmentFilterThresData)
        elif maskChoice == "Image ACWE (without edge)":
            self.outputData = copy.deepcopy(self.ACWEData)
        elif maskChoice == "Image Segmentation Thresholding":
            self.outputData = copy.deepcopy(self.ImageSegmentationFilterData)
        elif maskChoice == "Image Thresholding Mask":
            self.outputData = copy.deepcopy(self.thresHUOnes)
        elif maskChoice == "Image Connectivity Filter":
            self.outputData = copy.deepcopy(self.thresHUOnes)
        elif maskChoice == "Image Active Contour":
            self.outputData = copy.deepcopy(self.activeContourFOnes)
        elif maskChoice == "Segmentation Add Original Mask":
            self.outputData = copy.deepcopy(self.AddOriMaskData)
        elif maskChoice == "Segmentation Munaul Fill":
            self.outputData = copy.deepcopy(self.ManualFillData)
        elif maskChoice == "Intermediate Mask":
            self.outputData = copy.deepcopy(self.intermediateData)
        elif maskChoice == "Segmentation 2D Connectivity":
            self.outputData = copy.deepcopy(self.filterThresHUOnes)

        # update
        self.UpdateMsgLog(
            msg="Reset working data to: \n{}".format(maskChoice)
        )

    def intermediateStore(self):
        # intermediate storage
        self.intermediateData = copy.deepcopy(self.outputData)

        # update
        self.UpdateMsgLog(
            msg="Put a mask into the intermediate storage!"
        )

    """
    ##############################################################################
    # Image and segmentation
    ##############################################################################
    """

    def ACWE(self, iteration=None, smooth=None, lambda1=None, lambda2=None):
        # input
        if iteration is None: iteration = int(self.ui.iterationACWE_LC.text())
        if smooth is None: smooth = int(self.ui.smoothACWE_LC.text())
        if lambda1 is None: lambda1 = int(self.ui.lambda1ACWE_LC.text())
        if lambda2 is None: lambda2 = int(self.ui.lambda2ACWE_LC.text())

        # message
        msg = "iteration: {}".format(iteration) + \
              "\nsmooth: {}".format(smooth) + \
              "\nlambda1: {}".format(lambda1) + \
              "\nlambda2: {}".format(lambda2)

        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # function
        self.ACWEData = skimage.segmentation.morphological_chan_vese(
            image=self.CTA.OriData,
            iterations=iteration,
            init_level_set=self.outputData,
            smoothing=smooth,
            lambda1=lambda1,
            lambda2=lambda2
        )

        # update output and convert dtype
        self.ACWEData = numpy.array(self.ACWEData, dtype=self.CTA.OriData.dtype.type)
        self.outputData = copy.deepcopy(self.ACWEData)
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16
            )

        # update
        self.UpdateMsgLog(
            msg="Complete active contour without edge"
        )

    def ImageSegmentationFilter(
            self,
            funType=None,
            rangStarts=None,
            rangStops=None,
            direction=None,
            sliceStarts=None,
            sliceStops=None,
    ):

        # input
        if funType is None:
            funType = self.ui.funTypeImageCBox_LC.currentText()
        if rangStarts is None:
            rangStarts = Preprocess_Mask.StrToLst(
                strIn=self.ui.ImageFilterRangStartsTxt_LC.toPlainText()
            )["floatOut"]
        if rangStops is None:
            rangStops = Preprocess_Mask.StrToLst(
                strIn=self.ui.ImageFilterRangStopsTxt_LC.toPlainText()
            )["floatOut"]
        if direction is None:
            direction = self.ui.ImageSegmentationFilterDirectBtnGrp_LC.checkedButton().text()
        if sliceStarts is None:
            sliceStarts = Preprocess_Mask.StrToLst(
                strIn=self.ui.ImageSegmentationFiltersliceStartsTxt_LC.toPlainText()
            )["floatOut"]
        if sliceStops is None:
            sliceStops = Preprocess_Mask.StrToLst(
                strIn=self.ui.ImageSegmentationFiltersliceStopsTxt_LC.toPlainText()
            )["floatOut"]

        # message
        msg = "funType: {}".format(funType) + \
              "\ndirection: {}".format(direction) + \
              "\nsliceStarts: {}".format(sliceStarts) + \
              "\nsliceStops: {}".format(sliceStops) + \
              "\nrangStops: {}".format(rangStops) + \
              "\nrangStarts: {}".format(rangStarts)

        # update
        self.UpdateMsgLog(
            msg=msg
        )

        # function
        maskBinary = (self.outputData != 0) * 1
        maskCTA = numpy.multiply(maskBinary, self.CTA.OriData)

        # filter
        rtrnInfo = Image_Process_Functions.FilterDirectionSlices(
            inMat=maskCTA,
            directions=direction,
            sliceStarts=sliceStarts,
            sliceStops=sliceStops,
            rangStarts=rangStarts,
            rangStops=rangStops,
            funTypes=funType,
        )

        # update output & convert dtype
        self.outputDataOnes = Post_Image_Process_Functions.ConvertDType(
            refDataMat=self.CTA.OriData,
            tConDataMat=rtrnInfo["outputMat"]
        ).ConvertData
        self.outputData = Post_Image_Process_Functions.ConvertDType(
            refDataMat=self.CTA.OriData,
            tConDataMat=numpy.multiply(self.outputDataOnes, self.outputData)
        ).ConvertData
        self.ImageSegmentationFilterData = copy.deepcopy(self.outputData)

        # update
        self.UpdateMsgLog(
            msg="Complete Image Segmentation Filter: \n{}".format(rtrnInfo["message"])
        )

    def ThresholdFilter(self):
        # input range
        thresMin = Preprocess_Mask.StrToLst(strIn=self.ui.thresMinLineTxt_LC.text())["floatOut"]
        thresMax = Preprocess_Mask.StrToLst(strIn=self.ui.thresMaxLineTxt_LC.text())["floatOut"]

        # filter data
        _, initThresHUOnes = Image_Process_Functions.FilterData(
            rangStarts=thresMin,
            rangStops=thresMax,
            dataMat=self.CTA.OriData,
            funType="boundary"
        )

        # Add initial mask to take care of the distal low HU part
        # Filter to 0 and 1
        _, self.thresHUOnes = Image_Process_Functions.FilterData(
            rangStarts=[0],
            dataMat=initThresHUOnes + self.ConnectivityFilterData,
            funType="single value greater"
        )

        # update display data
        self.outputData = self.thresHUOnes

    def ActiveContour(self):
        # get input
        IGGAlpha = float(self.ui.IGGAlphaLineTxt_LC.text())
        initRadius = int(self.ui.initRadiusLineTxt_LC.text())
        areaThres = int(self.ui.areaThresLineTxt_LC.text())
        balloonForce = int(self.ui.balloonForceLineTxt_LC.text())
        smoothFac = int(self.ui.smoothFacLineTxt_LC.text())
        interation = int(self.ui.interationLineTxt_LC.text())
        ACThres = float(self.ui.ACThresLineTxt_LC.text())
        dilateRadius = int(self.ui.dilateRadiusLineTxt_LC.text())
        cpus = int(self.ui.cpuLineTxt_LC.text())

        print("IGGAlpha:{}".format(IGGAlpha))
        print("initRadius:{}".format(initRadius))
        print("areaThres:{}".format(areaThres))
        print("balloonForce:{}".format(balloonForce))
        print("smoothFac:{}".format(smoothFac))
        print("interation:{}".format(interation))
        print("ACThres:{}".format(ACThres))
        print("dilateRadius:{}".format(dilateRadius))
        print("CPUs:{}".format(cpus))

        # multi
        multiProcess = True  # False #True
        if multiProcess:
            rtrnInfo = Image_Process_Functions.ImgDilateActCon(
                self.filterThresHUOnes,
                initRadius,
                dilateRadius,
                cpus,
                areaThres,
                IGGAlpha,
                interation,
                ACThres,
                smoothFac,
                balloonForce,
                self.initConnectFilterOnes
            )

            self.activeContourOnes = rtrnInfo["activeContourOneMask"]

        if not multiProcess:
            # time
            strtT = time.time()

            # return information
            rtrnInfo = {}
            rtrnInfo["error"] = False
            rtrnInfo["errorMessage"] = None
            rtrnInfo["processTime"] = None
            rtrnInfo["processTimeMessage"] = None
            rtrnInfo["message"] = ""

            # empty volume
            dataShape = numpy.shape(self.filterThresHUOnes)
            self.activeContourOnes = numpy.zeros(dataShape)

            # Initial level set
            initLS = skimage.segmentation.disk_level_set(
                image_shape=numpy.shape(self.activeContourOnes[0]),
                radius=initRadius
            )

            # create dilation disk
            selem = skimage.morphology.disk(radius=dilateRadius)

            # active contour
            for imgSlice in range(dataShape[0]):
                mskFilterThres = self.filterThresHUOnes[imgSlice]
                # jump no mask
                if numpy.sum(mskFilterThres) == 0:
                    print("Jump zero mask slice: " + str(imgSlice))
                    continue

                # area less than area defined pixels using simple dilation radius
                if numpy.sum(mskFilterThres) <= areaThres:
                    print("Dilation - Area: " + str(numpy.sum(mskFilterThres)))
                    ls = skimage.morphology.dilation(image=mskFilterThres,
                                                     selem=selem)

                else:
                    print("Active Contour - Area: " + str(numpy.sum(mskFilterThres)))
                    # gradient
                    gimage = skimage.segmentation.inverse_gaussian_gradient(mskFilterThres, alpha=IGGAlpha)
                    # active contour
                    ls = skimage.segmentation.morphological_geodesic_active_contour(gimage=gimage,
                                                                                    iterations=interation,
                                                                                    init_level_set=initLS,
                                                                                    threshold=ACThres,
                                                                                    smoothing=smoothFac,
                                                                                    balloon=balloonForce)

                    if numpy.sum(ls) == 0:  # active contour failure use original filtered mask to dilate
                        ls = skimage.morphology.dilation(image=self.initConnectFilterOnes[imgSlice],
                                                         selem=selem)

                # stacking results
                self.activeContourOnes[imgSlice] = ls
                print("Finish slice: {} - Resultant area: {}".format(str(imgSlice), str(numpy.sum(ls))))

                # return information
                stpT = time.time()
                rtrnInfo["processTime"] = stpT - strtT
                rtrnInfo["processTimeMessage"] = "------Running time: {} s------".format(rtrnInfo["processTime"])
                rtrnInfo["message"] += "Complete single processor active contour and dilation running: \n {}".format(
                    rtrnInfo["processTimeMessage"])
                print("Complete active contour and dilation running: \n {}".format(rtrnInfo["processTimeMessage"]))

        # just in case fill orginal filtered mask again
        # filling original lumen mask for the area that cannot be filled with active contour
        activeContourCombo = self.activeContourOnes + self.initConnectFilterOnes
        # Filter to 0 and 1
        _, self.activeContourFOnes = Image_Process_Functions.FilterData(
            rangStarts=[0],
            dataMat=activeContourCombo,
            funType="single value greater"
        )

        # update display data
        self.outputData = self.activeContourFOnes

        # update message
        self.UpdateMsgLog(msg=rtrnInfo["message"])

    """
    ##############################################################################
    # Fill value
    ##############################################################################
    """

    def OneToValMak(self):
        # use current ouput if no active contour
        if self.outputData is None:
            self.UpdateMsgLog("No output data!")
        else:
            # convert with values
            # reference the connectivity filter first
            if self.initConnectFilterVals is None:
                print("Use original mask fill values")
                self.activeContourFVals = Post_Image_Process_Functions.ConvertValMsk(
                    inMat=self.outputData,
                    valRefMat=self.inMsk.OriData
                )
            else:
                self.activeContourFVals = Post_Image_Process_Functions.ConvertValMsk(
                    inMat=self.outputData,
                    valRefMat=self.initConnectFilterVals
                )

            # update display/save data
            self.outputDataOnes = (self.outputData != 0) * 1
            self.outputData = self.activeContourFVals

            # update
            self.UpdateMsgLog("Complete Fill Original Value")

    """
    ##############################################################################
    # Batch Process
    ##############################################################################
    """

    def ChooseBatchFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load csv file',
            fileTypes="All files (*.*);; Table files (*.csv *.txt) ;; More table files (*.xlsx *.xls *.xlsm)",
            fileObj=self.ui,
            qtObj=True
        )
        # set filename
        self.ui.batchTablePathTxt_LC.setPlainText(filename)

        # update
        self.UpdateMsgLog(
            msg="Choose Batch Table File: {}".format(filename)
        )

    def BatchCorrect(self, CSVPath=None):
        # input
        if CSVPath:
            batchDataFrame = Pd_Funs.OpenDF(CSVPath, header=0)
        else:
            batchDataFrame = Pd_Funs.OpenDF(self.ui.batchTablePathTxt_LC.toPlainText(), header=0)
        # loop cases
        for CTAPath, \
            inMskPath, \
            processPath, \
            fillValue, \
            saveDir, \
            saveName, \
            rowNumber \
                in zip(
            batchDataFrame["Image Path"].tolist(),
            batchDataFrame["Mask Path"].tolist(),
            batchDataFrame["Process Path"].tolist(),
            batchDataFrame["Fill Original Value"].tolist(),
            batchDataFrame["Output Directory"].tolist(),
            batchDataFrame["Output Name"].tolist(),
            range(len(batchDataFrame["Output Name"].tolist()))
        ):

            try:
                # load data
                self.LoadData(CTAPath=CTAPath, inMskPath=inMskPath)
            except Exception as e:
                print('Load Failure{}'.format(inMskPath))
                continue

            # load process
            processDataFrame = Pd_Funs.OpenDF(processPath, header=0)

            # loop each column
            for col in range(len(processDataFrame.columns)):
                # try:
                # update
                self.UpdateMsgLog("Processing column: {}".format(col))
                # 3D connectivity filter
                if "3D Connectivity Filter" in processDataFrame.columns[col]:
                    # update
                    self.UpdateMsgLog(
                        msg="Working on {}".format(processDataFrame.columns[col])
                    )

                    self.ConnectivityFilter(
                        FilterAreaChoice=processDataFrame.iloc[0, col],  # "first", "second", "third"
                        connectIn=int(processDataFrame.iloc[1, col])  # 1 to 3
                    )

                # 2D connectivity filter
                if "2D Connectivity Filter" in processDataFrame.columns[col]:
                    # update
                    self.UpdateMsgLog(
                        msg="Working on {}".format(processDataFrame.columns[col])
                    )

                    self.ConnectFilterThres(
                        connectIn=int(processDataFrame.iloc[0, col]),  # 1 to 2
                        direction=processDataFrame.iloc[1, col],  # X, Y, Z
                        sliceStarts=Preprocess_Mask.StrToLst(processDataFrame.iloc[2, col])["intOut"],
                        # int number seprated by ','
                        sliceStops=Preprocess_Mask.StrToLst(processDataFrame.iloc[3, col])["intOut"],
                        # float number seprated by ','
                        centerPlane=processDataFrame.iloc[4, col] == 'Yes',  # Yes, No
                        useRef=processDataFrame.iloc[5, col] == 'Original Mask',  # Original Mask
                        disk=processDataFrame.iloc[5, col] == 'Disk',  # Disk
                        diskRow=int(processDataFrame.iloc[6, col]),  # int number
                        diskColm=int(processDataFrame.iloc[7, col]),  # int number
                        diskRadius=int(processDataFrame.iloc[8, col])  # int number
                    )

                # active contour
                if "Active Contour Without Edge" in processDataFrame.columns[col]:
                    # update
                    self.UpdateMsgLog(
                        msg="Working on {}".format(processDataFrame.columns[col])
                    )

                    self.ACWE(
                        iteration=int(processDataFrame.iloc[0, col]),  # int number
                        smooth=int(processDataFrame.iloc[1, col]),  # int number
                        lambda1=int(processDataFrame.iloc[2, col]),  # int number
                        lambda2=int(processDataFrame.iloc[3, col])  # int number
                    )

                # Morphology
                if "Morphological Process" in processDataFrame.columns[col]:
                    # update
                    self.UpdateMsgLog(
                        msg="Working on {}".format(processDataFrame.columns[col])
                    )

                    self.ImageBasicProcessing(
                        axisChoice=processDataFrame.iloc[0, col],  # X, Y, Z 3D
                        diaChoice=str(processDataFrame.iloc[1, col]),  # Yes, No
                        funcChoose=processDataFrame.iloc[2, col],  # Opening, Closing, Dilation, Erosion
                        dilateIncre=int(processDataFrame.iloc[3, col]),  # int number
                        sliceStarts=Preprocess_Mask.StrToLst(processDataFrame.iloc[4, col])["intOut"],  # int number
                        sliceStops=Preprocess_Mask.StrToLst(processDataFrame.iloc[5, col])["intOut"]  # int number
                    )

                # Segmentation filter
                if "Image Segmentation Filter" in processDataFrame.columns[col]:
                    # update
                    self.UpdateMsgLog(
                        msg="Working on {}".format(processDataFrame.columns[col])
                    )

                    self.ImageSegmentationFilter(
                        funType=processDataFrame.iloc[0, col],
                        # boundary, single value, not single value, single value greater, single value less, outside boundary
                        rangStarts=Preprocess_Mask.StrToLst(processDataFrame.iloc[1, col])["floatOut"],
                        # float number seprated by ','v
                        rangStops=Preprocess_Mask.StrToLst(processDataFrame.iloc[2, col])["floatOut"],
                        # float number seprated by ','
                        direction=processDataFrame.iloc[3, col],  # X, Y, Z
                        sliceStarts=Preprocess_Mask.StrToLst(processDataFrame.iloc[4, col])["intOut"],
                        # int number seprated by ','
                        sliceStops=Preprocess_Mask.StrToLst(processDataFrame.iloc[5, col])["intOut"]
                        # int number seprated by ','
                    )

                # Segmentation filter
                if "Image Segmentation Filter" in processDataFrame.columns[col]:
                    # update
                    self.UpdateMsgLog(
                        msg="Working on {}".format(processDataFrame.columns[col])
                    )

                    self.ImageSegmentationFilter(
                        funType=processDataFrame.iloc[0, col],
                        # boundary, single value, not single value, single value greater, single value less, outside boundary
                        rangStarts=Preprocess_Mask.StrToLst(processDataFrame.iloc[1, col])["floatOut"],
                        # float number seprated by ','
                        rangStops=Preprocess_Mask.StrToLst(processDataFrame.iloc[2, col])["floatOut"],
                        # float number seprated by ','
                        direction=processDataFrame.iloc[3, col],  # X, Y, Z
                        sliceStarts=Preprocess_Mask.StrToLst(processDataFrame.iloc[4, col])["intOut"],
                        # int number seprated by ','
                        sliceStops=Preprocess_Mask.StrToLst(processDataFrame.iloc[5, col])["intOut"]
                        # int number seprated by ','
                    )

                # Segmentation filter
                if "Extract Skin" in processDataFrame.columns[col]:
                    # update
                    self.UpdateMsgLog(
                        msg="Working on {}".format(processDataFrame.columns[col])
                    )

                    self.Skin(valRange=Preprocess_Mask.StrToLst(processDataFrame.iloc[0, col])["floatOut"])

                # Man fill
                if "Manual Fill Mask" in processDataFrame.columns[col]:
                    # update
                    self.UpdateMsgLog(
                        msg="Working on {}".format(processDataFrame.columns[col])
                    )

                    # slices in the main table
                    if processDataFrame.iloc[6, col] == "Main Table":
                        sliceStarts = Preprocess_Mask.StrToLst(batchDataFrame["Manual Fill Slice Start"][rowNumber])[
                            "intOut"]
                    else:
                        sliceStarts = Preprocess_Mask.StrToLst(processDataFrame.iloc[6, col])["intOut"]

                    if processDataFrame.iloc[7, col] == "Main Table":
                        sliceStops = Preprocess_Mask.StrToLst(batchDataFrame["Manual Fill Slice Stop"][rowNumber])[
                            "intOut"]
                    else:
                        sliceStops = Preprocess_Mask.StrToLst(processDataFrame.iloc[7, col])["intOut"]

                    # !!! account '10,000' string
                    self.ManualFill(
                        maskType=processDataFrame.iloc[0, col],
                        actualUnit=processDataFrame.iloc[1, col],
                        fillReplaceMask=processDataFrame.iloc[2, col],
                        direction=processDataFrame.iloc[3, col],
                        horizontalLengths=Preprocess_Mask.StrToLst(processDataFrame.iloc[4, col])["floatOut"],
                        verticalLengths=Preprocess_Mask.StrToLst(processDataFrame.iloc[5, col])["floatOut"],
                        sliceStarts=sliceStarts,
                        sliceStops=sliceStops,
                        posititionFirsts=Preprocess_Mask.StrToLst(processDataFrame.iloc[8, col])["intOut"],
                        positionSeconds=Preprocess_Mask.StrToLst(processDataFrame.iloc[9, col])["intOut"],
                    )
                else:
                    self.UpdateMsgLog(
                        msg="Do not find {} \n {}".format(processDataFrame.columns[col],
                                                          processDataFrame.columns[col] == "Manual Fill Mask")
                    )

                # except Exception as e:
                #                     print('{} step failed'.format(processDataFrame.columns[col]))
                #                     break
            # output fill value
            if Save_Load_File.CheckTrue(parameter=fillValue):
                # update
                self.UpdateMsgLog(
                    msg="Working on {}".format("Fill Original Value")
                )

                self.OneToValMak()

            # save
            self.SaveFile(directPath=saveDir, nameRef=saveName)

            # clear log
            self.ClearLog()

            # init
            self.InitProcess()

    """
    ##############################################################################
    # Output
    ##############################################################################
    """

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_LC.setPlainText(dirname)

        # update
        self.UpdateMsgLog(
            msg="Choose output directory: \n{}".format(dirname)
        )

    def SaveFile(self, directPath=None, nameRef=None):
        # Get file name
        if nameRef is None:
            if self.ui.nameRefTxt_LC.toPlainText() == "":
                nameRef = Save_Load_File.FilenameFromPath(self.ui.mskPathTxt_LC.toPlainText())
            else:
                nameRef = Save_Load_File.ValidFileName(self.ui.nameRefTxt_LC.toPlainText())

        # get directory
        if directPath is None:
            directPath = self.ui.saveDirPathTxt_LC.toPlainText()

        # create dir
        Save_Load_File.checkCreateDir(path=directPath)

        # Set file name
        oneFilePath = Save_Load_File.DateFileName(
            Dir=directPath,
            fileName=nameRef + "One",
            extension=".nii.gz",
            appendDate=False
        )
        # Set file name
        valFilePath = Save_Load_File.DateFileName(
            Dir=directPath,
            fileName=nameRef + "Val",
            extension=".nii.gz",
            appendDate=False
        )

        # Save
        if self.outputDataOnes is not None:
            print(numpy.shape(self.outputDataOnes))
            print(numpy.shape(self.CTA.OriData))
            Save_Load_File.MatNIFTISave(
                MatData=self.outputDataOnes,
                imgPath=oneFilePath["CombineName"],
                imgInfo=self.CTA.OriImag,
                ConvertDType=True,
                refDataMat=self.CTA.OriData
            )

        print(numpy.shape(self.outputData))
        print(numpy.shape(self.CTA.OriData))
        Save_Load_File.MatNIFTISave(
            MatData=self.outputData,
            imgPath=valFilePath["CombineName"],
            imgInfo=self.CTA.OriImag,
            ConvertDType=True,
            refDataMat=self.CTA.OriData
        )

        # output log for lumen correction section
        ## Set file name
        logFilePath = Save_Load_File.DateFileName(
            Dir=directPath,
            fileName=nameRef + "LumenCorrectLog",
            extension=".txt",
            appendDate=False
        )
        Save_Load_File.WriteTXT(
            path=logFilePath["CombineName"],
            txt=self.outLog,
            mode="append"
        )

        # update
        if self.outputDataOnes is not None:
            self.UpdateMsgLog(
                msg="Save: \n{} \n{} \n{}".format(
                    oneFilePath["CombineName"],
                    valFilePath["CombineName"],
                    logFilePath["CombineName"]
                )
            )
        else:
            self.UpdateMsgLog(
                msg="Save: \n{} \n{}".format(
                    valFilePath["CombineName"],
                    logFilePath["CombineName"]
                )
            )

    def ClearLog(self):
        # clear log
        self.outLog = ""
        # update
        self.UpdateMsgLog(
            msg="Clear Log!"
        )

    def UpdateMsgLog(self, msg=""):
        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + msg \
               + "\n############################\n"

        # update log and display message
        if self.modelui:
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
            self.outLog += disp
        print(disp)
