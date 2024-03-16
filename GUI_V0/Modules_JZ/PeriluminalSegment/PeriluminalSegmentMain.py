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

class PeriluminalSegment:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseCTABtn_PSJZ.clicked.connect(lambda: self.ChooseOpenCTAFile())
        self.ui.chooseMskBtn_PSJZ.clicked.connect(lambda: self.ChooseOpenMskFile())
        self.ui.loadImgBtn_PSJZ.clicked.connect(lambda: self.LoadData())
        self.ui.plotOverBtn_PSJZ.clicked.connect(lambda: self.PlotOVerlap())
        self.ui.HUThresBtn_PSJZ.clicked.connect(lambda: self.ThresholdFilter())
        self.ui.gradFilterBtn_PSJZ.clicked.connect(lambda: self.GradientFilter())
        self.ui.gradPlotBtn_PSJZ.clicked.connect(lambda: self.PlotGradient())
        self.ui.periCorrectBtn_PSJZ.clicked.connect(lambda: self.PerilumenChoose())
        self.ui.periCorrectPlotBtn_PSJZ.clicked.connect(lambda: self.PlotFill())
        self.ui.actConBtn_PSJZ.clicked.connect(lambda: self.ActiveContour())
        self.ui.smoothBtn_PSJZ.clicked.connect(lambda: self.SplineSmooth())
        self.ui.chooseDirBtn_PSJZ.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.saveBtn_PSJZ.clicked.connect(lambda: self.SaveFile())

        self.InitPeriluminalSegment()

    def InitPeriluminalSegment(self):
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

    def ChooseOpenCTAFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.CTAPathTxt_PSJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseOpenMskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load image segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.mskPathTxt_PSJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def LoadData(self):
        # load two data
        self.CTA = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.CTAPathTxt_PSJZ.toPlainText()
        )
        self.inLumMsk = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.mskPathTxt_PSJZ.toPlainText()
        )
        # update display data
        self.displayData = self.inLumMsk.OriData

        # update message
        self.UpdateMsgLog(msg="Load:\n{} \n{}".format(
            self.ui.CTAPathTxt_PSJZ.toPlainText(),
            self.ui.mskPathTxt_PSJZ.toPlainText()
        )
        )

    def PlotOVerlap(self):
        # get inputs
        slicDir = self.ui.plotAixsLineTxt_LC.text()
        title = Preprocess_Mask.StrToLst(strIn=self.ui.plotTitleTxt_PSJZ.toPlainText())["listOut"]
        plotRange = Preprocess_Mask.StrToLst(strIn=self.ui.plotThresTxt_PSJZ.toPlainText())["booleanOut"]
        minLst = Preprocess_Mask.StrToLst(strIn=self.ui.plotMinTxt_PSJZ.toPlainText())["floatOut"]
        maxLst = Preprocess_Mask.StrToLst(strIn=self.ui.plotMaxTxt_PSJZ.toPlainText())["floatOut"]

        Use_Plt.slider3Display(matData1=self.CTA.OriData,
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

    def ThresholdFilter(self):
        # input range
        thresMin = Preprocess_Mask.StrToLst(strIn=self.ui.thresMinLineTxt_PSJZ.text())["floatOut"]
        thresMax = Preprocess_Mask.StrToLst(strIn=self.ui.thresMaxLineTxt_PSJZ.text())["floatOut"]

        # filter data
        self.CTAThres, _ = Image_Process_Functions.FilterData(rangStarts=thresMin,
                                                              rangStops=thresMax,
                                                              dataMat=self.CTA.OriData,
                                                              funType="boundary")

        # update display data
        self.displayData = self.CTAThres

        # update message
        self.UpdateMsgLog(
            msg="Complete gradient filtering: {} ~ {}".format(thresMin, thresMax)
        )
        print("Complete gradient filtering: {} ~ {}".format(thresMin, thresMax))

    def GradientFilter(self):
        # input range
        gradThres = float(self.ui.gradThresLineTxt_PSJZ.text())
        LOGThresMin = float(self.ui.LOGthresMinLineTxt_PSJZ.text())
        LOGThresMax = float(self.ui.LOGthresMaxLineTxt_PSJZ.text())
        gradGauss = self.ui.gradGuassBtnGrp_PSJZ.checkedButton().text() == "Yes"
        gradGaussDisk = int(self.ui.gradGaussDiskMaxLineTxt_PSJZ.text())
        gradGaussSD = int(self.ui.gradGaussSDMaxLineTxt_PSJZ.text())
        LOGGauss = self.ui.LOGBtnGrp_PSJZ.checkedButton().text() == "Yes"
        LOGGaussDisk = int(self.ui.LOGGaussDiskMaxLineTxt_PSJZ.text())
        LOGGaussSD = int(self.ui.LOGGaussSDMaxLineTxt_PSJZ.text())
        lumenDilation = int(self.ui.wallDilLineTxt_PSJZ.text())
        closeConnect = int(self.ui.closeConnectLineTxt_PSJZ.text())
        openConnect = int(self.ui.openConnectLineTxt_PSJZ.text())
        closeDisk = int(self.ui.closeDiskLineTxt_PSJZ.text())
        openDisk = int(self.ui.openDiskLineTxt_PSJZ.text())

        msg = "gradThres: {}".format(gradThres) + \
              "\nLOGThresMin: {}".format(LOGThresMin) + \
              "\nLOGThresMax: {}".format(LOGThresMax) + \
              "\ngradGauss: {}".format(gradGauss) + \
              "\ngradGaussDisk: {}".format(gradGaussDisk) + \
              "\ngradGaussSD: {}".format(gradGaussSD) + \
              "\nLOGGauss: {}".format(LOGGauss) + \
              "\nLOGGaussDisk: {}".format(LOGGaussDisk) + \
              "\nLOGGaussSD: {}".format(LOGGaussSD) + \
              "\nlumenDilation: {}".format(lumenDilation) + \
              "\ncloseConnect: {}".format(closeConnect) + \
              "\nopenConnect: {}".format(openConnect) + \
              "\ncloseDisk: {}".format(closeDisk) + \
              "\nopenDisk: {}".format(openDisk)

        # looping for gradient and fill
        ## empty for stacking
        dataShp = numpy.shape(self.inLumMsk.OriData)
        self.CTAGrad = numpy.zeros(dataShp)
        self.CTALOG = numpy.zeros(dataShp)
        self.CTAGradLOG = numpy.zeros(dataShp)
        self.fillClose = numpy.zeros(dataShp)
        self.fillOpenClose = numpy.zeros(dataShp)
        ## gradient and fill
        for imgSlice in range(dataShp[0]):
            # slice
            lumMskSlice = (self.inLumMsk.OriData[imgSlice] != 0) * 1  # binary the input mask
            CTASlice = self.CTAThres[imgSlice]

            # jump zero mask
            if numpy.sum(lumMskSlice) == 0:
                # print("Jump zero mask slice: " + str(imgSlice))
                continue

            # Gradient object creation
            periMsk = Image_Process_Functions.GradientMat(
                dataMat=CTASlice,
                gradBlur=gradGauss,
                LOGBlur=LOGGauss,
                gradBlurK=gradGaussDisk,
                gradBlurSD=gradGaussSD,
                LOGBlurK=LOGGaussDisk,
                LOGBlurSD=LOGGaussSD,
                gradThres=gradThres,
                lplStrt=LOGThresMin,
                lplStop=LOGThresMax
            )

            # Gradient filter
            periMsk.Filter()
            ## Stcking grad and LOG
            self.CTAGrad[imgSlice] = periMsk.gradMatXY
            self.CTALOG[imgSlice] = periMsk.lplDataMat
            self.CTAGradLOG[imgSlice] = periMsk.filterGradientXYMskLoG

            # fill in wall, open, close, connectivity
            ## Fill lumen + lumen dilation + opening + closing
            periMsk.FillOpenClsoeGradient(
                fillMat=lumMskSlice,
                dilateDisk=lumenDilation,
                diskSize=openDisk
            )
            ## Filled lumen mask connectivity filter
            periMsk.ConnectAreaFilterCenterGradient(
                fillMat=lumMskSlice,
                connectType=closeConnect,
                diskSize=closeDisk
            )
            ## Filled + Opened + Closed lumen mask connectivity filter
            periMsk.ConnectFillOpenCloseCenter(
                fillMat=lumMskSlice,
                connectType=openConnect
            )

            # Stacking results
            self.fillClose[imgSlice] = periMsk.connectGradFillClose
            self.fillOpenClose[imgSlice] = periMsk.connectFillOpenClose

            print("Complete slice: {}/{}".format(imgSlice, dataShp[0]))

        # update display data
        self.displayData = self.CTAGradLOG

        # update message
        self.UpdateMsgLog(
            msg="Complete gradient filtering\n" + msg
        )
        print("Complete gradient filtering\n" + msg)

    def PlotGradient(self):
        # get inputs
        slicDir = "X"
        title = ["Gradient", "Laplacian (of Gaussian)", "Filtering Plot"]
        plotRange = [False, False, False]
        minLst = [0]
        maxLst = [0]

        Use_Plt.slider3Display(matData1=self.CTAGrad,
                               matData2=self.CTALOG,
                               matData3=self.CTAGradLOG,
                               fig3OverLap=False,
                               ShareX=True,
                               ShareY=True,
                               ask23MatData=False,
                               wait=False,
                               slicDiect=slicDir,
                               title=title,
                               plotRange=plotRange,
                               winMin=minLst,
                               winMax=maxLst)

    def PerilumenChoose(self):
        # input
        maxPrilumAreaFac = float(self.ui.maxPrilumAreaFac.text())

        ## empty for stacking
        dataShp = numpy.shape(self.inLumMsk.OriData)
        self.periLumGrad = numpy.zeros(dataShp)

        # Get average lumen area
        ## 0, 1 lum mask
        binaryLumMsk = (self.inLumMsk.OriData != 0) * 1
        ## volume
        lumVol = numpy.sum(binaryLumMsk)
        ## non-empty slices
        height = 0
        for i in range(dataShp[0]):
            if numpy.sum(binaryLumMsk[i]) != 0:
                height += 1
            else:
                continue
        msg = "Non-zero slices = height: {}".format(height)
        print(msg)
        ## area
        aveLumArea = lumVol / height
        maxPrilumArea = aveLumArea * maxPrilumAreaFac

        # filling area
        for imgSlice in range(dataShp[0]):
            # get fill and close results
            fillClose = self.fillClose[imgSlice]

            # jump for empty
            if numpy.sum(fillClose) == 0:
                continue

            # decide to fill
            if numpy.sum(fillClose) < maxPrilumArea:
                # fill
                self.periLumGrad[imgSlice] = fillClose
                print(
                    "Slice: {}/{} stack fill+close mask area: {}/{}".format(
                        imgSlice,
                        dataShp[0],
                        numpy.sum(fillClose),
                        maxPrilumArea
                    )
                )
            else:
                # check fill open and close one
                fillOpenClose = self.fillOpenClose[imgSlice]
                if numpy.sum(fillOpenClose) < maxPrilumArea:
                    # fill
                    self.periLumGrad[imgSlice] = fillOpenClose
                    print(
                        "Slice: {}/{} stack fill+OPEN+close mask area: {}/{}".format(
                            imgSlice,
                            dataShp[0],
                            numpy.sum(fillOpenClose),
                            maxPrilumArea
                        )
                    )
                else:
                    # dilate lumen mask to max area
                    ## Create disk
                    selem = skimage.morphology.disk(1)

                    fillMsk = binaryLumMsk[imgSlice]

                    while True:
                        fillMskCheck = skimage.morphology.dilation(fillMsk, selem)
                        if numpy.sum(fillMskCheck) > maxPrilumArea:
                            # fill keep area less than maximum
                            self.periLumGrad[imgSlice] = fillMsk
                            msg += "\nSlice: {}/{} stack fill+OPEN+close mask area: {}/{}".format(
                                imgSlice,
                                dataShp[0],
                                numpy.sum(fillMsk),
                                maxPrilumArea
                            )
                            print(
                                "Slice: {}/{} stack fill+OPEN+close mask area: {}/{}".format(
                                    imgSlice,
                                    dataShp[0],
                                    numpy.sum(fillMsk),
                                    maxPrilumArea
                                )
                            )
                            break
                        else:
                            fillMsk = fillMskCheck

        # update display data
        self.displayData = self.periLumGrad

        # update message
        self.UpdateMsgLog(
            msg="Complete area filtering \n" + msg
        )
        print("Complete area filtering \n" + msg)

    def PlotFill(self):
        # get inputs
        slicDir = "X"
        title = ["Fill lumen + Closing", "Fill lumen + Opening + Closing", "Periluminal Mask"]
        plotRange = [False, False, False]
        minLst = [0]
        maxLst = [0]

        Use_Plt.slider3Display(matData1=self.fillClose,
                               matData2=self.fillOpenClose,
                               matData3=self.displayData,
                               fig3OverLap=False,
                               ShareX=True,
                               ShareY=True,
                               ask23MatData=False,
                               wait=False,
                               slicDiect=slicDir,
                               title=title,
                               plotRange=plotRange,
                               winMin=minLst,
                               winMax=maxLst)

    def ActiveContour(self):
        # get input
        IGGAlpha = float(self.ui.IGGAlphaLineTxt_PSJZ.text())
        initRadius = int(self.ui.initRadiusLineTxt_PSJZ.text())
        areaThres = int(self.ui.areaThresLineTxt_PSJZ.text())
        balloonForce = int(self.ui.balloonForceLineTxt_PSJZ.text())
        smoothFac = int(self.ui.smoothFacLineTxt_PSJZ.text())
        interaction = int(self.ui.interationLineTxt_PSJZ.text())
        ACThres = float(self.ui.ACThresLineTxt_PSJZ.text())
        dilateRadius = int(self.ui.dilateRadiusLineTxt_PSJZ.text())
        cpus = int(self.ui.cpuLineTxt_PSJZ.text())

        msg = "IGGAlpha: {}".format(IGGAlpha) + \
              "\ninitRadius: {}".format(initRadius) + \
              "\nareaThres: {}".format(areaThres) + \
              "\nballoonForce: {}".format(balloonForce) + \
              "\nsmoothFac: {}".format(smoothFac) + \
              "\ninteraction: {}".format(interaction) + \
              "\nACThres: {}".format(ACThres) + \
              "\ndilateRadius: {}".format(dilateRadius) + \
              "\ncpus: {}\n".format(cpus)
        print(msg)

        # multi
        rtrnInfo = Image_Process_Functions.ImgDilateActCon(
            self.periLumGrad,
            initRadius,
            dilateRadius,
            cpus,
            areaThres,
            IGGAlpha,
            interaction,
            ACThres,
            smoothFac,
            balloonForce,
            self.periLumGrad
        )

        self.activeContourOnes = rtrnInfo["activeContourOneMask"]

        # update display data
        self.displayData = self.activeContourOnes

        # update message
        self.UpdateMsgLog(msg=msg + rtrnInfo["message"])

    def SplineSmooth(self):
        # get input
        radialSamplingSize = int(self.ui.radialSamplingSizeLineTxt_PSJZ.text())
        initRadialSplineOrder = int(self.ui.initRadialSplineOrderLineTxt_PSJZ.text())
        vertSplineSmoothFac = float(self.ui.vertSplineSmoothFacLineTxt_PSJZ.text())
        vertRadialSplineOrder = int(self.ui.vertRadialSplineOrderLineTxt_PSJZ.text())
        resampleFac = int(self.ui.resampleFacLineTxt_PSJZ.text())
        planeSplineSmoothFac = float(self.ui.planeSplineSmoothFacLineTxt_PSJZ.text())
        planeSmoothOrder = int(self.ui.planeSmoothOrderLineTxt_PSJZ.text())
        initSplineSmooth = int(self.ui.initSplineSmoothLineTxt_PSJZ.text())

        msg = "radialSamplingSize: {}".format(radialSamplingSize) + \
              "\ninitRadialSplineOrder: {}".format(initRadialSplineOrder) + \
              "\nvertSplineSmoothFac: {}".format(vertSplineSmoothFac) + \
              "\nvertRadialSplineOrder: {}".format(vertRadialSplineOrder) + \
              "\nresampleFac: {}".format(resampleFac) + \
              "\nplaneSplineSmoothFac: {}".format(planeSplineSmoothFac) + \
              "\nplaneSmoothOrder: {}\n".format(planeSmoothOrder)
        print(msg)

        # use current output if no active contour
        if self.activeContourOnes is None:
            print("No active contour results")
            rtrnInfo = Image_Process_Functions.SplineSmooth3D(
                maskData=self.periLumGrad,
                radialSamplingSize=radialSamplingSize,
                initSplineSmooth=initSplineSmooth,
                initRadialSplineOrder=initRadialSplineOrder,
                vertRadialSplineOrder=vertRadialSplineOrder,
                vertSplineSmoothFac=vertSplineSmoothFac,
                resInt=resampleFac,
                planeSmoothOrder=planeSmoothOrder,
                planeSplineSmoothFac=planeSplineSmoothFac
            )
            # Need to enclose lumen
            lumenDilation = int(self.ui.wallDilLineTxt_PSJZ.text())
            # dilate lumen mask
            ## Create disk
            selem = skimage.morphology.disk(lumenDilation)
            ## empty for stacking
            dataShp = numpy.shape(self.inLumMsk.OriData)
            dilLum = numpy.zeros(dataShp)
            ## dilation
            for imgSlice in range(dataShp[0]):
                # slice
                lumMskSlice = (self.inLumMsk.OriData[imgSlice] != 0) * 1  # binary the input mask

                # jump empty
                if numpy.sum(lumMskSlice) == 0:
                    continue

                # dilation
                dilLum[imgSlice] = skimage.morphology.dilation(lumMskSlice, selem)

            # update display data
            self.displayData = (rtrnInfo['SmoothMask'] + dilLum > 0) * 1

            # update message
            self.UpdateMsgLog(msg=msg + rtrnInfo["errorMessage"] + rtrnInfo["message"])

        else:
            # spline smooth
            rtrnInfo = Image_Process_Functions.SplineSmooth3D(
                maskData=self.activeContourOnes,
                radialSamplingSize=radialSamplingSize,
                initSplineSmooth=initSplineSmooth,
                initRadialSplineOrder=initRadialSplineOrder,
                vertRadialSplineOrder=vertRadialSplineOrder,
                vertSplineSmoothFac=vertSplineSmoothFac,
                resInt=resampleFac,
                planeSmoothOrder=planeSmoothOrder,
                planeSplineSmoothFac=planeSplineSmoothFac
            )

            # Need to enclose lumen
            lumenDilation = int(self.ui.wallDilLineTxt_PSJZ.text())
            # dilate lumen mask
            ## Create disk
            selem = skimage.morphology.disk(lumenDilation)
            ## empty for stacking
            dataShp = numpy.shape(self.inLumMsk.OriData)
            dilLum = numpy.zeros(dataShp)
            ## dilation
            for imgSlice in range(dataShp[0]):
                # slice
                lumMskSlice = (self.inLumMsk.OriData[imgSlice] != 0) * 1  # binary the input mask

                # jump empty
                if numpy.sum(lumMskSlice) == 0:
                    continue

                # dilation
                dilLum[imgSlice] = skimage.morphology.dilation(lumMskSlice, selem)

            # update display data
            self.displayData = (rtrnInfo['SmoothMask'] + dilLum > 0) * 1
            self.smoothMsk = (rtrnInfo['SmoothMask'] + dilLum > 0) * 1

            # update message
            self.UpdateMsgLog(msg=msg + rtrnInfo["errorMessage"] + rtrnInfo["message"])

    def ChooseSaveDir(self):

        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_PSJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose directory: \n{}".format(dirname))

    def SaveFile(self):
        # Get file name
        if self.ui.nameRefTxt_PSJZ.toPlainText() == "":
            name = Save_Load_File.FilenameFromPath(self.ui.mskPathTxt_PSJZ.toPlainText())
        else:
            name = Save_Load_File.ValidFileName(self.ui.nameRefTxt_PSJZ.toPlainText())

        # Set file name
        GFFilePath = Save_Load_File.DateFileName(
            Dir=self.ui.saveDirPathTxt_PSJZ.toPlainText(),
            fileName=name + "GF",
            extension=".nii.gz",
            appendDate=False
        )
        # Set file name
        ACFilePath = Save_Load_File.DateFileName(
            Dir=self.ui.saveDirPathTxt_PSJZ.toPlainText(),
            fileName=name + "AC",
            extension=".nii.gz",
            appendDate=False
        )
        # Set file name
        SMFilePath = Save_Load_File.DateFileName(
            Dir=self.ui.saveDirPathTxt_PSJZ.toPlainText(),
            fileName=name + "SM",
            extension=".nii.gz",
            appendDate=False
        )

        print(GFFilePath)
        print(ACFilePath)
        print(SMFilePath)

        # Save
        Save_Load_File.MatNIFTISave(MatData=self.periLumGrad,
                                    imgPath=GFFilePath["CombineName"],
                                    imgInfo=self.CTA.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.CTA.OriData)
        Save_Load_File.MatNIFTISave(MatData=self.activeContourOnes,
                                    imgPath=ACFilePath["CombineName"],
                                    imgInfo=self.CTA.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.CTA.OriData)
        Save_Load_File.MatNIFTISave(MatData=self.smoothMsk,
                                    imgPath=SMFilePath["CombineName"],
                                    imgInfo=self.CTA.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.CTA.OriData)
        # update
        self.UpdateMsgLog(
            msg="Save: \n{} \n{} \n{}".format(
                GFFilePath["CombineName"],
                ACFilePath["CombineName"],
                SMFilePath["CombineName"]
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
