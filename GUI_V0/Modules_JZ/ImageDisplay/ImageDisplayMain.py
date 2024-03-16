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
import Matrix_Math
import Use_Plt
##############################################################################

##############################################################################
# Standard libs
import os
from datetime import datetime
import copy
import scipy.interpolate
import matplotlib.pyplot as plt
import sklearn.neighbors
import skimage.measure
import numpy


##############################################################################

class ImageDisplay:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            
        self.ui.chooseImageFileBtn_IDJZ.clicked.connect(lambda: self.ChooseBackImage())
        self.ui.chooseMaskDirBtn_IDJZ.clicked.connect(lambda: self.ChooseMaskDir())
        self.ui.chooseContourDirBtn_IDJZ.clicked.connect(lambda: self.ChooseContourDir())
        self.ui.chooseSaveFileBtn_IDJZ.clicked.connect(lambda: self.ChooseSaveFile())
        self.ui.plotBtn_IDJZ.clicked.connect(lambda: self.ImageDisp())

        self.InitImage()

    def InitImage(self):
        # initial definition
        self.paramImg = None
        self.outputDirNameRef = None
        self.nameRef = None

    def ChooseBackImage(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.ImagePathTxt_IDJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose background image file:\n{}".format(filename))

    def ChooseMaskDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose mask directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.maskDirPathTxt_IDJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose reference image segmentation dir:\n{}".format(dirname))

    def ChooseContourDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose mask directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.contourDirPathTxt_IDJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose reference image segmentation dir:\n{}".format(dirname))

    def ChooseSaveFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(
            dispMsg="Choose save image file",
            fileObj=self.ui,
            fileTypes="All files (*.*);; "
                      "Img files (*.png *.jpg) ;; "
                      "Graphic files (*.svg, *.eps, *.ps, *.pdf, *.tex) ",
            qtObj=True
        )

        # set filename
        self.ui.saveFilePathTxt_IDJZ.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving image file path:\n{}".format(filename))

    def ImageDisp(self):
        # convert everything to list/str
        ## background image
        imagePath = self.ui.ImagePathTxt_IDJZ.toPlainText()
        backMinVal = float(self.ui.backMinValLineTxt_IDJZ.text())
        backMaxVal = float(self.ui.backMaxValLineTxt_IDJZ.text())
        backColorMap = self.ui.backColorMapLineTxt_IDJZ.text()
        plotTitle = self.ui.plotTitleLineTxt_IDJZ.text()
        colorBar = self.ui.colorbarBtnGrp_IDJZ.checkedButton().text() == "Yes"
        colorBarTitle = self.ui.colorBarTitleLineTxt_IDJZ.text()
        showAxes = self.ui.showAxesBtnGrp_IDJZ.checkedButton().text() == "Yes"
        XLbl = self.ui.XLblLineTxt_IDJZ.text()
        YLbl = self.ui.YLblLineTxt_IDJZ.text()

        ## Masks
        showMask = self.ui.showMaskBtn_IDJZ. isChecked()
        maskDir = self.ui.maskDirPathTxt_IDJZ.toPlainText()
        maskFiles = Preprocess_Mask.StrToLst(self.ui.maskFilesTxt_IDJZ.toPlainText())["listOut"]
        maskStarts = Preprocess_Mask.StrToLst(self.ui.maskStartsTxt_IDJZ.toPlainText())["floatOut"]
        maskStops = Preprocess_Mask.StrToLst(self.ui.maskStopsTxt_IDJZ.toPlainText())["floatOut"]
        cmapChoices = Preprocess_Mask.StrToLst(self.ui.cmapChoicesTxt_IDJZ.toPlainText())["listOut"]
        maskLengeds = Preprocess_Mask.StrToLst(self.ui.maskLengedsTxt_IDJZ.toPlainText())["listOut"]
        maskSigma = float(self.ui.maskSigmaLineTxt_IDJZ.text())
        maskTransparency = float(self.ui.maskTransparencyLineTxt_IDJZ.text())
        maskLegendX = float(self.ui.maskLegendXLineTxt_IDJZ.text())
        maskLegendY = float(self.ui.maskLegendYLineTxt_IDJZ.text())
        maskLegendLoc = self.ui.maskLegendLocLineTxt_IDJZ.text()

        ## contour
        showContour = self.ui.showContourBtn_IDJZ.isChecked()
        contourDir = self.ui.contourDirPathTxt_IDJZ.toPlainText()
        contourFiles = Preprocess_Mask.StrToLst(self.ui.contourFilesTxt_IDJZ.toPlainText())["listOut"]
        contourStarts = Preprocess_Mask.StrToLst(self.ui.contourStartsTxt_IDJZ.toPlainText())["floatOut"]
        contourStops = Preprocess_Mask.StrToLst(self.ui.contourStopsTxt_IDJZ.toPlainText())["floatOut"]
        contourColors = Preprocess_Mask.StrToLst(self.ui.contourColorsTxt_IDJZ.toPlainText())["listOut"]
        contourLineWidths = Preprocess_Mask.StrToLst(self.ui.contourLineWidthsTxt_IDJZ.toPlainText())["floatOut"]
        contourRefs = Preprocess_Mask.StrToLst(self.ui.contourRefsTxt_IDJZ.toPlainText())["listOut"]
        contourSigma = float(self.ui.contourSigmaLineTxt_IDJZ.text())
        contourLevel = float(self.ui.contourLevelLineTxt_IDJZ.text())
        contourLegendX = float(self.ui.contourLegendXLineTxt_IDJZ.text())
        contourLegendY = float(self.ui.contourLegendYLineTxt_IDJZ.text())
        contourLegendLoc = self.ui.contourLegendLocLineTxt_IDJZ.text()

        ## plots
        fontSize = int(self.ui.fontSizeLineTxt_IDJZ.text())
        resampleFac = int(self.ui.resampleFacLineTxt_IDJZ.text())
        splineOrder = int(self.ui.splineOrderLineTxt_IDJZ.text())
        legend = self.ui.legendBtnGrp_IDJZ.checkedButton().text() == "Yes"

        ## output
        imgOutPath = self.ui.saveFilePathTxt_IDJZ.toPlainText()

        ## resizing
        resizeX = False
        resizeY = False
        imageResize = self.ui.imageSizeCBox_IDJZ.currentText() == 'Image Setting'
        matrixResize = self.ui.imageSizeCBox_IDJZ.currentText() == 'Matrix Setting'

        xSliceStart = 0
        xSliceFinish = 0
        ySliceStart = 0
        ySliceFinish = 0
        if imageResize or matrixResize:
            try:
                xSliceStart = float(self.ui.xSliceStartLineTxt_IDJZ.text())
                xSliceFinish = float(self.ui.xSliceFinishLineTxt_IDJZ.text())
                if imageResize:
                    resizeX = True
            except:
                if imageResize:
                    resizeX = False
                # update message
                self.UpdateMsgLog(msg="No assigment of X resizing")
            try:
                ySliceStart = float(self.ui.ySliceStartLineTxt_IDJZ.text())
                ySliceFinish = float(self.ui.ySliceFinishLineTxt_IDJZ.text())
                if imageResize:
                    resizeY = True
            except:
                if imageResize:
                    resizeY = False
                # update message
                self.UpdateMsgLog(msg="No assigment of Y resizing")

        ## 3D slicing
        threeDDir = self.ui.threeDDirBtnGrp_IDJZ.checkedButton().text()
        threeDImage = self.ui.threeDImageBtnGrp_IDJZ.checkedButton().text() == 'Yes'
        sliceNumber = int(self.ui.sliceNumberLineTxt_IDJZ.text())

        msg = 'threeDDir: {} \n'.format(threeDDir) + \
              'threeDImage: {} \n'.format(threeDImage) + \
              'sliceNumber: {} \n'.format(sliceNumber)

        self.UpdateMsgLog(msg)

        # Mask
        if showMask:
            # Compare list length
            compareShp = Post_Image_Process_Functions.CompareListDimension(
                lsts=[
                    maskFiles,
                    maskStarts,
                    maskStops,
                    cmapChoices,
                    maskLengeds
                ]
            )

            if compareShp["error"]:
                # update message
                self.UpdateMsgLog(msg=compareShp["errorMessage"])
                self.UpdateMsgLog(msg='maskFiles' + " : {}".format(maskFiles) + '\n' + \
                                      'maskStarts' + " : {}".format(maskStarts) + '\n'+ \
                                      'maskStops' + " : {}".format(maskStops) + '\n'+ \
                                      'cmapChoices' + " : {}".format(cmapChoices) + '\n'+ \
                                      'maskLengeds' + " : {}".format(maskLengeds) + '\n'
                                  )
                return

            # stacking contour and masks
            inMasks = []
            maskLen = len(maskFiles)
            for i in range(maskLen):
                # input file
                maskPath = Save_Load_File.AppendLists(
                    [maskDir],
                    [maskFiles[i]],
                    sep="/"
                )["combineList"][0]

                # load data
                mask = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=maskPath
                )

                # 3d to 2d
                if threeDImage:
                    if threeDDir == "X":
                        maskImage = mask.OriData[sliceNumber]
                    elif threeDDir == "Y":
                        maskImage = mask.OriData[:, sliceNumber, :]
                    elif threeDDir == "Z":
                        maskImage = mask.OriData[:, :, sliceNumber]
                else:
                    maskImage = mask.OriData

                # resize
                if matrixResize:
                    maskImageShp = numpy.shape(maskImage)
                    xsliceStartOut, xsliceStopOut = Matrix_Math.SliceNumberCorrect(
                        sliceStart=xSliceStart,
                        sliceStop=xSliceFinish,
                        boundaryStart=0,
                        boundaryStop=maskImageShp[0],
                    )
                    ysliceStartOut, ysliceStopOut = Matrix_Math.SliceNumberCorrect(
                        sliceStart=ySliceStart,
                        sliceStop=ySliceFinish,
                        boundaryStart=0,
                        boundaryStop=maskImageShp[1],
                    )
                    maskImage = maskImage[
                                int(xsliceStartOut):int(xsliceStopOut),
                                int(ysliceStartOut):int(ysliceStopOut)
                                ]

                # compare shape and stack
                if i != 0:
                    ## check same shape
                    compareShp = Post_Image_Process_Functions.CompareArrShape(
                        dataMat1=inMasks[0],
                        dataMat2=maskImage,
                        DialogWarn=False
                    )
                    # stack data
                    ## Not same shape
                    if compareShp["error"]:
                        # update message
                        self.UpdateMsgLog(
                            msg=compareShp["errorMessage"]
                        )
                        return
                    else:
                        inMasks.append(maskImage)
                else:
                    inMasks.append(maskImage)
        else:
            inMasks = None
            self.UpdateMsgLog(msg="Do not show Mask!")

        # contour
        if showContour:
            # Compare list length
            compareShp = Post_Image_Process_Functions.CompareListDimension(
                lsts=[
                    contourFiles,
                    contourStarts,
                    contourStops,
                    contourColors,
                    contourLineWidths,
                    contourRefs
                ]
            )
            if compareShp["error"]:
                # update message
                self.UpdateMsgLog(msg=compareShp["errorMessage"])
                self.UpdateMsgLog(msg='contourFiles' + " : {}".format(contourFiles) + '\n' + \
                                      'contourStarts' + " : {}".format(contourStarts) + '\n' + \
                                      'contourStops' + " : {}".format(contourStops) + '\n' + \
                                      'contourColors' + " : {}".format(contourColors) + '\n' + \
                                      'contourLineWidths' + " : {}".format(contourLineWidths) + '\n' + \
                                      'contourRefs' + " : {}".format(contourRefs) + '\n'
                                  )
                return

            # stacking contour
            contourMasks = []
            contourLen = len(contourFiles)
            for i in range(contourLen):
                # input file
                contourPath = Save_Load_File.AppendLists(
                    [contourDir],
                    [contourFiles[i]],
                    sep="/"
                )["combineList"][0]

                # load data
                contour = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=contourPath
                )

                # 3d to 2d
                if threeDImage:
                    if threeDDir == "X":
                        contourImage = contour.OriData[sliceNumber]
                    elif threeDDir == "Y":
                        contourImage = contour.OriData[:, sliceNumber, :]
                    elif threeDDir == "Z":
                        contourImage = contour.OriData[:, :, sliceNumber]
                else:
                    contourImage = contour.OriData

                # resize
                if matrixResize:
                    contourImageShp = numpy.shape(contourImage)
                    xsliceStartOut, xsliceStopOut = Matrix_Math.SliceNumberCorrect(
                        sliceStart=xSliceStart,
                        sliceStop=xSliceFinish,
                        boundaryStart=0,
                        boundaryStop=contourImageShp[0],
                    )
                    ysliceStartOut, ysliceStopOut = Matrix_Math.SliceNumberCorrect(
                        sliceStart=ySliceStart,
                        sliceStop=ySliceFinish,
                        boundaryStart=0,
                        boundaryStop=contourImageShp[1],
                    )
                    contourImage = contourImage[
                                   int(xsliceStartOut):int(xsliceStopOut),
                                   int(ysliceStartOut):int(ysliceStopOut)
                                   ]

                # compare shape and stack
                if i != 0:
                    ## check same shape
                    compareShp = Post_Image_Process_Functions.CompareArrShape(
                        dataMat1=contourMasks[0],
                        dataMat2=contourImage,
                        DialogWarn=False
                    )
                    # stack data
                    ## Not same shape
                    if compareShp["error"]:
                        # update message
                        self.UpdateMsgLog(
                            msg=compareShp["errorMessage"]
                        )
                        return
                    else:
                        contourMasks.append(contourImage)
                else:
                    contourMasks.append(contourImage)

        else:
            contourMasks = None
            self.UpdateMsgLog(msg="Do not show Mask!")

        # load back image
        backImg = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=imagePath
        )

        # 3d to 2d
        if threeDImage:
            if threeDDir == "X":
                backImage = backImg.OriData[sliceNumber]
            elif threeDDir == "Y":
                backImage = backImg.OriData[:, sliceNumber, :]
            elif threeDDir == "Z":
                backImage = backImg.OriData[:, :, sliceNumber]
        else:
            backImage = backImg.OriData

        # resize
        if matrixResize:
            backImageShp = numpy.shape(backImage)
            xsliceStartOut, xsliceStopOut = Matrix_Math.SliceNumberCorrect(
                sliceStart=xSliceStart,
                sliceStop=xSliceFinish,
                boundaryStart=0,
                boundaryStop=backImageShp[0],
            )
            ysliceStartOut, ysliceStopOut = Matrix_Math.SliceNumberCorrect(
                sliceStart=ySliceStart,
                sliceStop=ySliceFinish,
                boundaryStart=0,
                boundaryStop=backImageShp[1],
            )
            backImage = backImage[
                        int(xsliceStartOut):int(xsliceStopOut),
                        int(ysliceStartOut):int(ysliceStopOut)
                        ]

        if threeDImage:
            msg = '3D image input! \n' + \
                  'backImage: {} \n'.format(numpy.shape(backImage))

            if showMask: msg += 'inMasks: {} \n'.format(numpy.shape(inMasks))

            if showContour: msg += 'contourMasks: {} \n'.format(numpy.shape(contourMasks))

            self.UpdateMsgLog(msg)

        # plot and save
        plot = Use_Plt.PlotMasksContours(
            backImg=backImage,
            backColorMap=backColorMap,
            backMinVal=backMinVal,
            backMaxVal=backMaxVal,
            colorBarTitle=colorBarTitle,
            plotTitle=plotTitle,
            resampleFac=resampleFac,
            inMasks=inMasks,
            maskLengeds=maskLengeds,
            maskStarts=maskStarts,
            maskStops=maskStops,
            maskSigma=maskSigma,
            cmapChoices=cmapChoices,
            maskTransparency=maskTransparency,
            contourMasks=contourMasks,
            contourStarts=contourStarts,
            contourStops=contourStops,
            contourSigma=contourSigma,
            contourLevel=contourLevel,
            contourColors=contourColors,
            contourLineWidths=contourLineWidths,
            contourRefs=contourRefs,
            fontSize=fontSize,
            legend=legend,
            colorBar=colorBar,
            showAxes=showAxes,
            XLbl=XLbl,
            YLbl=YLbl,
            saveImg=True,
            imgOutPath=imgOutPath,
            maskLegendX=maskLegendX,
            maskLegendY=maskLegendY,
            maskLegendLoc=maskLegendLoc,
            contourLegendX=contourLegendX,
            contourLegendY=contourLegendY,
            contourLegendLoc=contourLegendLoc,
            resizeX=resizeX,
            xSliceStart=xSliceStart,
            xSliceFinish=xSliceFinish,
            resizeY=resizeY,
            ySliceStart=ySliceStart,
            ySliceFinish=ySliceFinish,
            splineOrder=splineOrder,
            showMask=showMask,
            showContour=showContour
        )

        # update message
        self.UpdateMsgLog(
            msg=plot["message"]
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
        print(msg)
