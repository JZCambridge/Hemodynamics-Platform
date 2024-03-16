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

class RadialDisplay:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            
        self.ui.chooseOpenParaDirBtn_RDPJZ.clicked.connect(lambda: self.ChooseParamDir())
        self.ui.chooseOpenMaskDirBtn_RDPJZ.clicked.connect(lambda: self.ChooseMaskDir())
        self.ui.saveDirBtn_RDPJZ.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.outputRadiDispBtn_RDPJZ.clicked.connect(lambda: self.RadialDisp())

        self.InitRadialDisplay()

    def InitRadialDisplay(self):
        self.paramImg = None
        self.outputDirNameRef = None
        self.nameRef = None

    def ChooseParamDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose parameter image directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.paraDirPathTxt_RDPJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose parameter image directory:\n{}".format(dirname))

    def ChooseMaskDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose mask directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.maskDirPathTxt_RDPJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose reference image segmentation dir:\n{}".format(dirname))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Save data directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.saveDirPathTxt_RDPJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose saving dir:\n{}".format(dirname))

    def RadialDisp(self):
        # convert everything to list/str
        ## input files
        inParaDir = self.ui.paraDirPathTxt_RDPJZ.toPlainText()
        inMskDir = self.ui.maskDirPathTxt_RDPJZ.toPlainText()
        paraFiles = Preprocess_Mask.StrToLst(self.ui.paraFilesTxt_RDPJZ.toPlainText())["listOut"]
        mskFiles = Preprocess_Mask.StrToLst(self.ui.mskFilesTxt_RDPJZ.toPlainText())["listOut"]
        # resampling and KNN
        resamplingPnts = Preprocess_Mask.StrToLst(self.ui.resamplePntsTxt_RDPJZ.toPlainText())["floatOut"]
        ballRadii = Preprocess_Mask.StrToLst(self.ui.ballRadiiTxt_RDPJZ.toPlainText())["floatOut"]
        ## output
        outputDirInit = self.ui.saveDirPathTxt_RDPJZ.toPlainText()
        nameRefs = Preprocess_Mask.StrToLst(strIn=self.ui.nameRefTxt_RDPJZ.toPlainText())["listOut"]
        ## plots
        colorBar = self.ui.colorBarBtnGrp_RDPJZ.checkedButton().text() == "Yes"
        colorMap = self.ui.cmapLineTxt_RDPJZ.text()
        fontSize = int(self.ui.fontLineTxt_RDPJZ.text())
        showAxes = self.ui.showAxesBtnGrp_RDPJZ.checkedButton().text() == "Yes"
        XLbls = Preprocess_Mask.StrToLst(strIn=self.ui.XLblsTxt_RDPJZ.toPlainText())["listOut"]
        YLbls = Preprocess_Mask.StrToLst(strIn=self.ui.YLblsTxt_RDPJZ.toPlainText())["listOut"]
        plotTitles = Preprocess_Mask.StrToLst(strIn=self.ui.plotTitlesTxt_RDPJZ.toPlainText())["listOut"]
        colorBarTitles = Preprocess_Mask.StrToLst(strIn=self.ui.colorBarTitlesTxt_RDPJZ.toPlainText())["listOut"]
        maxVals = Preprocess_Mask.StrToLst(strIn=self.ui.maxValsTxt_RDPJZ.toPlainText())["floatOut"]
        minVals = Preprocess_Mask.StrToLst(strIn=self.ui.minValsTxt_RDPJZ.toPlainText())["floatOut"]

        # Compare list length
        compareShp = Post_Image_Process_Functions.CompareListDimension(
            lsts=[
                paraFiles,
                mskFiles,
                nameRefs
            ]
        )
        if compareShp["error"]:
            # update message
            self.UpdateMsgLog(msg=compareShp["errorMessage"])
            return

        # load each case
        outMsg = 'Error Log: ' + datetime.now().strftime("%d/%b/%y - %H:%M:%S") + '\n'
        listLen = len(paraFiles)
        for list in range(listLen):
            # each case
            paraFile = paraFiles[list]
            mskFile = mskFiles[list]
            nameRef = nameRefs[list]
            resamplingPnt = resamplingPnts[list]
            ballRadius = ballRadii[list]

            # input file
            paraPath = Save_Load_File.AppendLists(
                [inParaDir],
                [paraFile],
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
            paraData = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=paraPath
            )
            mskData = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=mskPath
            )

            ## check same shape
            compareShp = Post_Image_Process_Functions.CompareArrShape(
                dataMat1=paraData.OriData,
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
                        paraPath,
                        mskPath
                    )
                )

            # Create directory with name reference
            self.outputDirNameRef = outputDirInit + "/" + nameRef
            self.nameRef = nameRef
            ## create dir
            checkCreate = Save_Load_File.checkCreateDir(
                path=self.outputDirNameRef
            )
            if checkCreate["error"]:
                # update message
                self.UpdateMsgLog(
                    msg=checkCreate["errorMessage"]
                )
                return

            # Data
            maskData = mskData.OriData
            CFDData = paraData.OriData

            print('Working on: {}'.format(paraFile))

            # dealing with all zeros
            if numpy.all((CFDData == 0)):
                # update message
                self.UpdateMsgLog(
                    msg="Encounter all zeros!! input: {} \n Jump!!".format(paraPath)
                )
                outMsg += 'Zero Files: {} \n'.format(paraPath)
                continue
            else:
                print("Not all data zre zeros.")


            # get non-zero CFDData and positions
            CFDCoordsN0 = numpy.where(CFDData != 0)  # [depthZ, RowY, ColumnX].T
            CFDCoordsN0 = numpy.array([CFDCoordsN0[0], CFDCoordsN0[1], CFDCoordsN0[2]])  # convert to array
            CFDN0Data = CFDData[numpy.where(CFDData != 0)]
            ## compare shape for warning
            if numpy.shape(CFDN0Data)[0] != numpy.shape(CFDCoordsN0)[1]:
                # update message
                self.UpdateMsgLog(
                    msg="Warning of not the same shape!!!"
                )
                return

            # create ball nearest neighbour
            tree = sklearn.neighbors.BallTree(CFDCoordsN0.T, leaf_size=numpy.shape(CFDN0Data)[0])

            # linear interpolation control points
            radialSamplingSize = int(resamplingPnt)
            # radius
            ballRadius = int(ballRadius)  # sqrt(3)

            # empty volume to stacking radial inital control point
            maskDataShape = numpy.shape(maskData)
            maskCFDOut = numpy.zeros(maskDataShape)
            verticalSlices = numpy.ones([maskDataShape[0], 1]) * (-1)
            sliceContourpoints = numpy.zeros([maskDataShape[0], 1])
            sliceCentroid = numpy.zeros([maskDataShape[0], 2])
            paramImg = numpy.zeros([maskDataShape[0], radialSamplingSize])
            statsLst = []

            # sampling theta
            sampleTheta = numpy.linspace(start=-numpy.pi, stop=numpy.pi, num=radialSamplingSize, endpoint=False)

            # start finsh slices:
            startSliceFlg = True
            startSlice = None
            finishSlice = None

            for imgSlice in range(maskDataShape[0]):
                # image data
                img = maskData[imgSlice]
                CFDMskImg = maskCFDOut[imgSlice]
                # empty stats array
                sliceStatsArr = numpy.array([])

                # jump empty slice
                if numpy.sum(img) == 0:
                    msg = "Empty slice: {}".format(imgSlice)
                    print(msg)
                    continue
                elif startSliceFlg:
                    startSlice = imgSlice
                    verticalSlices[imgSlice] = imgSlice
                else:
                    finishSlice = imgSlice
                    verticalSlices[imgSlice] = imgSlice

                # get contour of image https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.find_contours
                ## list of (n,2)-ndarrays,  n (row, column) = (y, x) coordinates
                contourCoords = skimage.measure.find_contours(
                    image=img,
                    level=None,
                    fully_connected='low',
                    positive_orientation='low',
                    mask=None
                )
                countourX = numpy.array(contourCoords[0][:, 1])
                countourY = numpy.array(contourCoords[0][:, 0])
                countourXShp = numpy.shape(countourX)

                # filling in values by nearest neighbour
                oriContourData = numpy.zeros(countourXShp)
                ## coordinates [depthZ, RowX, ColumnY]
                countourZ = numpy.ones(countourXShp) * imgSlice
                countourFinCoords = numpy.array([countourZ, countourY, countourX])

                ## nearest neighbour
                (ind, dist) = tree.query_radius(
                    countourFinCoords.T,
                    r=ballRadius,
                    return_distance=True,
                    sort_results=True
                )
                ## shape warning!
                if numpy.shape(ind)[0] != countourXShp[0]:
                    # update message
                    self.UpdateMsgLog(
                        msg="Warning of not the same shape!!!"
                    )
                    return

                ## matching
                for pnt in range(countourXShp[0]):
                    # closest indices
                    if ind[pnt].size != 0:  # NOT empty array
                        oriContourData[pnt] = CFDN0Data[ind[pnt][0]]

                        # Filling all connected points
                        contourRowCeil = int(numpy.ceil(countourY[pnt]))
                        contourRowFlr = int(numpy.floor(countourY[pnt]))
                        contourClmCeil = int(numpy.ceil(countourX[pnt]))
                        contourClmFlr = int(numpy.floor(countourX[pnt]))
                        CFDMskImg[contourRowCeil, contourClmCeil] = CFDN0Data[ind[pnt][0]]
                        CFDMskImg[contourRowCeil, contourClmFlr] = CFDN0Data[ind[pnt][0]]
                        CFDMskImg[contourRowFlr, contourClmCeil] = CFDN0Data[ind[pnt][0]]
                        CFDMskImg[contourRowFlr, contourClmFlr] = CFDN0Data[ind[pnt][0]]

                        # append for stats
                        sliceStatsArr = numpy.append(sliceStatsArr, CFDN0Data[ind[pnt][0]])

                        # message
                        msg = "\nMask point: depth = {}, Row = {}, Column = {}" \
                              "\nParameter point: depth = {}, Row = {}, Column = {}" \
                              "\nValue: {}".format(
                            countourZ[pnt],
                            countourY[pnt],
                            countourX[pnt],
                            CFDCoordsN0[:, ind[pnt][0]][0],
                            CFDCoordsN0[:, ind[pnt][0]][1],
                            CFDCoordsN0[:, ind[pnt][0]][2],
                            CFDN0Data[ind[pnt][0]]
                        )
                        # print(msg)
                    else:
                        # append "0" !!! matching non-zeros if not values means "0"
                        sliceStatsArr = numpy.append(sliceStatsArr, 0)

                        # message
                        msg = "\nMask point: depth = {}, Row = {}, Column = {}" \
                              "\n Cannot find point within {}".format(
                            countourZ[pnt],
                            countourY[pnt],
                            countourX[pnt],
                            ballRadius
                        )
                        # print(msg)

                # output CFD results
                maskCFDOut[imgSlice] = CFDMskImg * (img != 0) * 1

                # stats lists
                statsLst.append(sliceStatsArr)

                # find center
                ## label the image with connectivity
                label_img = skimage.measure.label(img)
                ## get each region information
                regions = skimage.measure.regionprops_table(label_img, properties=['label', 'centroid'])
                ## get labelled img all labels include 0
                unqiNum, count = numpy.unique(label_img, return_counts=True)
                # print("unqiNum = {}".format(unqiNum))
                # print("count = {}".format(count))
                ## get non-zero largest number
                unqiNum_non0 = unqiNum[numpy.where(unqiNum != 0)]
                count_non0 = count[numpy.where(unqiNum != 0)]
                ### largest count
                count_non0_max = numpy.max(count_non0)
                ### get label
                lbl_OI = unqiNum_non0[numpy.where(count_non0 == count_non0_max)][0]
                ##find centroid
                lbl_OI_index = numpy.where(regions['label'] == lbl_OI)
                y0 = regions['centroid-0'][lbl_OI_index]  # (row, column)
                x0 = regions['centroid-1'][lbl_OI_index]
                ## store centroid
                sliceCentroid[imgSlice][0] = x0
                sliceCentroid[imgSlice][1] = y0

                # convert to polar after move to center (row, column) = (y, x) !!!
                countourX = contourCoords[0][:, 1]
                countourY = contourCoords[0][:, 0]
                countourX_Trans = countourX - x0
                countourY_Trans = countourY - y0
                contourPolarRho, contourPolarTheta = Image_Process_Functions.cart2pol(countourX_Trans, countourY_Trans)

                # get contour points
                sliceContourpoints[imgSlice] = numpy.shape(contourCoords[0])[0]
                msg = "Slice: {} " \
                      "\ncontour points: {}" \
                      "\nCentroid: {}".format(imgSlice, sliceContourpoints[imgSlice], sliceCentroid[imgSlice])
                # print(msg)

                # cubic B-spline representation of a 1-D curvev !! xb <= x <= xe
                # sort data in order
                contourPolar = numpy.array([contourPolarTheta, oriContourData])
                sortContourPolar = \
                    Image_Process_Functions.sortArray(contourPolar.T, singleArray=True, col=0, refArray=None)[
                        'sortArray']
                sortContourPolarTheta = sortContourPolar[:, 0]
                sortContourPolarData = sortContourPolar[:, 1]

                # linear interpolation
                ## convert range fully
                extContourPolarTheta = sortContourPolarTheta - 2 * numpy.pi
                extContourPolarTheta = numpy.append(extContourPolarTheta, sortContourPolarTheta)
                extContourPolarTheta = numpy.append(extContourPolarTheta, sortContourPolarTheta + 2 * numpy.pi)
                extContourPolarData = numpy.append(sortContourPolarData, sortContourPolarData)
                extContourPolarData = numpy.append(extContourPolarData, sortContourPolarData)
                ## linear
                f = scipy.interpolate.interp1d(x=extContourPolarTheta, y=extContourPolarData, kind='linear')
                paramImg[imgSlice] = f(sampleTheta)

            # remove unused slices
            self.paramImg = paramImg[numpy.where(verticalSlices != -1)[0]]
            # print(numpy.shape(paramImg))
            # print(numpy.shape(self.paramImg))

            # stats
            verticalSlices = verticalSlices[verticalSlices != -1]
            Matrix_Math.StatsLists(
                inLsts=statsLst,
                saveCsv=True,
                outDir=self.outputDirNameRef,
                outNameRef=self.nameRef,
                refSlices=verticalSlices,
                outRefName=self.nameRef
            )

            # save parameter value mask
            mskOutPath = Save_Load_File.DateFileName(
                Dir=self.outputDirNameRef,
                fileName=nameRef + "_STR",
                extension=".nii.gz",
                appendDate=False
            )
            # Save
            Save_Load_File.MatNIFTISave(
                MatData=maskCFDOut,
                imgPath=mskOutPath["CombineName"],
                imgInfo=mskData.OriImag,
                ConvertDType=False
            )

            # plotting and save
            XLbl = XLbls[list]
            YLbl = YLbls[list]
            plotTitle = plotTitles[list]
            maxVal = maxVals[list]
            minVal = minVals[list]
            colorBarTitle = colorBarTitles[list]
            ## save path
            imgOutPath = Save_Load_File.DateFileName(
                Dir=self.outputDirNameRef,
                fileName=nameRef,
                extension=".jpg",
                appendDate=False
            )

            # plot
            # print(colorBarTitles)
            Use_Plt.RadialDisplay(
                Img=self.paramImg,
                colorMap=colorMap,
                minVal=minVal,
                maxVal=maxVal,
                plotTitle=plotTitle,
                fontSize=fontSize,
                colorBar=colorBar,
                showAxes=showAxes,
                XLbl=XLbl,
                YLbl=YLbl,
                saveImg=True,
                imgOutPath=imgOutPath["CombineName"],
                colorBarTitle=colorBarTitle,
                nTicks=5
            )

        # write error log
        Save_Load_File.WriteTXT(
            path=outputDirInit + '/' + 'Output.log',
            txt=outMsg,
            mode="append"
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
