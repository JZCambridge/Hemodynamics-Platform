# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：BrainMemoryAreaScreenshot.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2022/2/10 21:43 
'''
import matplotlib.pyplot as plt
import matplotlib.widgets
import copy
##############################################################################
# Standard library
import numpy
import SimpleITK
import scipy
import scipy.ndimage
from matplotlib.transforms import Affine2D
"""
##############################################################################
# Hippocampus Visualisation
##############################################################################
"""
def LoadNifti(niiPath = None):
    # Load NIFTI as matrix
    # Output data
    if niiPath is None:
        print("please input niipath!")
    else:
        itkImag = SimpleITK.ReadImage(niiPath)
        print("image orientation", numpy.around(itkImag.GetDirection()))
        itkData = SimpleITK.GetArrayFromImage(itkImag)
        print("Load: " + niiPath)
        # get voxel spacing (for 3-D image)
        try:
            spacing = itkImag.GetSpacing()
            spacing_x = spacing[0]
            spacing_y = spacing[1]
            spacing_z = spacing[2]
            print("spacing_x: ")
            print(spacing_x)
            print("spacing_y: ")
            print(spacing_y)
            print("spacing_z: ")
            print(spacing_z)
        except:
            pass
    # Return values
    return  itkData, itkImag

def imgPlaneDirect(itkImag, AnatomicalDirect = 'Sagittal'):
    direction_ori = numpy.around(itkImag.GetDirection())  # [-0. -0. -1.  1.  0. -0.  0.  -1.  0.]
    direction_reshp = numpy.reshape(direction_ori, (3,3))
    direction = numpy.zeros_like(direction_reshp)
    direction[0] += direction_reshp[0]
    direction[1] += direction_reshp[1]
    direction[2] -= direction_reshp[2]
    direction_column = numpy.sum(direction, axis=1)

    # print("reshape",direction)
    if sum(map(abs, direction_ori)) == 3: # if the direction list is a standard list with three '1' facts
        # Sagittal plane
        if AnatomicalDirect == 'Sagittal':
            if direction[0,0] != 0:
                imgDirect = "X"
            elif direction[0,1] != 0:
                imgDirect = "Y"
            elif direction[0,2] != 0:
                imgDirect = "Z"
            angle_refer = direction_column[1] + direction_column[2]
            if angle_refer >0:
                angle_rotate = 0
            elif angle_refer ==0:
                angle_rotate = 90
            elif angle_refer <0:
                angle_rotate = 180

        # Coronal plane
        if AnatomicalDirect == 'Coronal':
            if direction[1,0] != 0:
                imgDirect = "X"
            elif direction[1,1] != 0:
                imgDirect = "Y"
            elif direction[1,2] != 0:
                imgDirect = "Z"
            angle_refer = direction_column[0] + direction_column[2]
            if angle_refer >0:
                angle_rotate = 0
            elif angle_refer ==0:
                angle_rotate = 90
            elif angle_refer <0:
                angle_rotate = 180
        # Transverse plane/Axial plane
        if AnatomicalDirect == 'Transverse':
            if direction[2,0] != 0:
                imgDirect = "X"
            elif direction[2,1] != 0:
                imgDirect = "Y"
            elif direction[2,2] != 0:
                imgDirect = "Z"
            angle_refer = direction_column[0] + direction_column[1]
            if angle_refer >0:
                angle_rotate = 0
            elif angle_refer ==0:
                angle_rotate = 90
            elif angle_refer <0:
                angle_rotate = 180
    else:
        print("Please standardlize the direction matrix! ")
    return imgDirect , angle_rotate

def FilterData(
        rangStarts=[0],
        rangStops=[0],
        dataMat=[0],
        funType="single value"):
    # initial value
    dataMatMsked = None
    dataMatMsks = None

    # convert vtk to numpy
    # if ConvertVTKType:
    #     DataType = VTK_Functions.VTK_Numpy(InDataType,
    #                                        VTK_to_Numpy=True)
    # else:
    #     DataType = dataMat.dtype.type
    DataType = dataMat.dtype.type
    # equal to single vlaues
    if funType == "single value":
        print("single value")
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))

        for rangStart in rangStarts:
            print("mask value")
            print(rangStart)
            # print("numpy.max(dataMat)")
            # print(numpy.max(dataMat))
            dataMatTFMsk = dataMat == rangStart
            # print("dataMatTFMsk")
            # print(dataMatTFMsk)
            # stack mask data
            dataMatMsks += 1 * dataMatTFMsk

        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        # print("dataMatMsks")
        # print(dataMatMsks)
        # mask ori Mat Data
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input is filtered with: " + str(rangStarts))

    # equal to single vlaues
    if funType == "not single value":
        print("not single value")
        dataMatMsks = numpy.ones(numpy.shape(dataMat))

        for rangStart in rangStarts:
            print("mask value")
            print(rangStart)
            # print("numpy.max(dataMat)")
            # print(numpy.max(dataMat))
            dataMatTFMsk = dataMat != rangStart
            # print("dataMatTFMsk")
            # print(dataMatTFMsk)
            # stack mask data
            dataMatMsks = dataMatMsks * dataMatTFMsk

        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        # print("dataMatMsks")
        # print(dataMatMsks)
        # mask ori Mat Data
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input keep without: " + str(rangStarts))

    # greater than a single vlaue
    if funType == "single value greater":
        print("single value greater")
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))

        for rangStart in rangStarts:
            print("mask value")
            print(rangStart)
            # print("numpy.max(dataMat)")
            # print(numpy.max(dataMat))
            dataMatTFMsk = dataMat > rangStart
            # print("dataMatTFMsk")
            # print(dataMatTFMsk)
            # stack mask data
            dataMatMsks += 1 * dataMatTFMsk

        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        # print("dataMatMsks")
        # print(dataMatMsks)
        # mask ori Mat Data
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input is filtered with: " + str(rangStarts))

    # less than a single vlaue
    if funType == "single value less":
        print("single value less")
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))

        for rangStart in rangStarts:
            print("mask value")
            print(rangStart)
            # print("numpy.max(dataMat)")
            # print(numpy.max(dataMat))
            dataMatTFMsk = dataMat < rangStart
            # print("dataMatTFMsk")
            # print(dataMatTFMsk)
            # stack mask data
            dataMatMsks += 1 * dataMatTFMsk

        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        # print("dataMatMsks")
        # print(dataMatMsks)
        # mask ori Mat Data
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input is filtered with: " + str(rangStarts))

    # in boundaries
    if funType == "boundary":
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))
        for rangStart, rangStop in zip(rangStarts, rangStops):  # loop simultaneously
            # Given wrong order of boundary
            if rangStart > rangStop:
                print(
                    "Boundary order wrong! Range lowest value is: " + str(rangStart) + "Range highest value is: " + str(
                        rangStop))
                print("Automatic switch boundary")
                dataMatTFMskStrt = dataMat >= rangStop  # included boundary
                dataMatTFMskStop = dataMat <= rangStart
                dataMatTFMsk = numpy.multiply(dataMatTFMskStrt, dataMatTFMskStop)
                # stack mask data
                dataMatMsks += 1 * dataMatTFMsk
            else:
                dataMatTFMskStrt = dataMat >= rangStart  # included boundary
                dataMatTFMskStop = dataMat <= rangStop
                dataMatTFMsk = numpy.multiply(dataMatTFMskStrt, dataMatTFMskStop)
                # stack mask data
                dataMatMsks += 1 * dataMatTFMsk
        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        # mask ori Mat Data
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input boundary is filtered with: " + str(rangStarts) + " " + str(rangStops))

    # in boundaries
    if funType == "outside boundary":
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))
        for rangStart, rangStop in zip(rangStarts, rangStops):  # loop simultaneously
            # Given wrong order of boundary
            if rangStart > rangStop:
                print(
                    "Boundary order wrong! Range lowest value is: " + str(rangStart) + "Range highest value is: " + str(
                        rangStop))
                print("Automatic switch boundary")
                dataMatTFMskStrt = dataMat <= rangStop  # included boundary
                dataMatTFMskStop = dataMat >= rangStart
                dataMatTFMsk = numpy.multiply(dataMatTFMskStrt, dataMatTFMskStop)
                # stack mask data
                dataMatMsks += 1 * dataMatTFMsk
            else:
                dataMatTFMskStrt = dataMat <= rangStart  # included boundary
                dataMatTFMskStop = dataMat >= rangStop
                dataMatTFMsk = numpy.multiply(dataMatTFMskStrt, dataMatTFMskStop)
                # stack mask data
                dataMatMsks += 1 * dataMatTFMsk
        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        # mask ori Mat Data
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input outside boundary is filtered with: " + str(rangStarts) + " " + str(rangStops))

    mskVals = dataMatMsked
    mskOnes = dataMatMsks

    return mskVals, mskOnes

def slider3Display(matData1=[0],
                   matData2=[0],
                   matData3=[0],
                   fig3OverLap=True,
                   ask23MatData=False,
                   OneOverTwo=False,
                   ContourOver=False,
                   slicDiect='X',
                   initSlice = 37/130,
                   plotRange=[False, False, False],
                   winMin=[0, 0, 0],
                   winMax=[100, 100, 100],
                   angle_rotation=0,
                   cmapChoice='gray',
                   imagSavPth=''):
    # Can show 3 different plots
    # Can share X and/or Y axes
    # Can overlap the 3 plots

    # return msg
    dirErrMsg = ""
    infoMsg = "Slicing along: "

    # front size
    fs = 12

    # Set slicDiect to default 'X' if no matching
    directionList = ['X', 'Y', 'Z']
    noDirectMatch = True
    for val in directionList:
        if val == slicDiect:
            noDirectMatch = False
            infoMsg += str(slicDiect)
            break
    if noDirectMatch:
        dirErrMsg = "Plotting: no direction match: " + str(
            slicDiect) + " Use default 'X'"
        print("Plotting: no direction match: " + str(
            slicDiect) + " Use default 'X'")
        slicDiect = 'X'

    # marData1 shape
    matData1Shape = numpy.shape(matData1)

    # second data
    if ask23MatData:
        print("ask23MatData error!")
    elif not ask23MatData:
        if numpy.shape(numpy.shape(matData2)) == (1,):
            # create empty one if no data and not ask to load
            matData2 = numpy.zeros(matData1Shape)

    if fig3OverLap and not ContourOver:
        print("Plot overlap no contour")

        # Check all mats are same shape
        if matData1Shape != numpy.shape(matData2) and ask23MatData:
            errMsg = "Mat 1 shape: \n" + str(matData1Shape) + "\nMat 2 shape: \n" + str(numpy.shape(matData2))
            print(errMsg)

        if matData1Shape != numpy.shape(matData2) and not ask23MatData:
            errMsg = "Mat 1 shape: \n" + str(matData1Shape) + "\nMat 2 shape: \n" + str(numpy.shape(matData2))
            print(errMsg)
            matData2 = numpy.zeros(matData1Shape)

        # Create and plot
        # slicing direction
        figsize = numpy.shape(matData1)
        if slicDiect == 'Z': #the direction is fliped in simple itk
            figMat1 = matData1[int(initSlice*figsize[0])]
            figMat2 = matData2[int(initSlice*figsize[0])]
        if slicDiect == 'Y':
            figMat1 = matData1[:, int(initSlice*figsize[1]), :]
            figMat2 = matData2[:, int(initSlice*figsize[1]), :]
        if slicDiect == 'X':
            figMat1 = matData1[:, :, int(initSlice*figsize[2])]
            figMat2 = matData2[:, :, int(initSlice*figsize[2])]
        figMat1 = numpy.rot90(figMat1, int(angle_rotation/90))
        figMat1 = Contrast_enhancement(figMat1)
        figMat2 = numpy.rot90(figMat2, int(angle_rotation/90))
        fig1, ax1 = plt.subplots(nrows=1, ncols=1)  # create figure & 1 axis

        # plot range
        if not OneOverTwo:  # !!!! intially wrong definition of on over two
            # should be TWO over ONE
            if plotRange[2]:
                ax121 = ax1.imshow(
                    figMat1,
                    vmin=winMin[0],
                    vmax=winMax[0],
                    cmap=cmapChoice
                )
            else:
                ax121 = ax1.imshow(
                    figMat1,
                    vmin=numpy.min(figMat1),
                    vmax=numpy.max(figMat1),
                    cmap=cmapChoice
                )
            # mask creation for on the non-zero region
            maskOver = numpy.ma.masked_where(figMat2 == 0, figMat2)
            ax122 = ax1.imshow(
                maskOver,
                vmin=numpy.min(figMat2),
                vmax=numpy.max(figMat2),
                alpha=0.5,
                cmap="viridis" # plasma   cividis inferno
            )
            # ax1.set_title(title, fontsize=fs)
            ax1.axis('off')

        elif OneOverTwo:
            if plotRange[2]:
                ax121 = ax1.imshow(
                    figMat2,
                    vmin=winMin[1],
                    vmax=winMax[1],
                    cmap=cmapChoice
                )
            else:
                ax121 = ax1.imshow(
                    figMat2,
                    vmin=numpy.min(figMat2),
                    vmax=numpy.max(figMat2),
                    cmap=cmapChoice
                )
            # transparent '0's
            maskOver = numpy.ma.masked_where(figMat1 == 0, figMat1)
            ax122 = ax1.imshow(
                maskOver,
                vmin=numpy.min(figMat1),
                vmax=numpy.max(figMat1),
                alpha=0.5,
                cmap="viridis"
            )
            ax1.axis('off')

        plt.show(block=True)
        fig1.savefig(imagSavPth, bbox_inches='tight',pad_inches = 0)  # save the figure to file
        # plt.savefig('E:/to.png')
        plt.close(fig1)  # close the figure window

def Contrast_enhancement(img):
    newimg = numpy.array(copy.deepcopy(img)) #this makes a real copy of img, if you dont, any change to img will change newimg too
    temp_img=numpy.array(copy.deepcopy(img))*3/2+50/255
    newimg = numpy.where(newimg<=100,temp_img,newimg)
    return newimg

class BrainMemoryAreaScreenshotMain:
    def __init__(self):
        self.InitProcess()

    def InitProcess(self):
        # initial definition
        self.CTAPath = r"E:\B_BrainVolumn\0214\outputTOZHOU\brain_preproc_img.nii.gz"
        self.Maskpath = r"E:\B_BrainVolumn\0214\outputTOZHOU\cleanup_labelmap96_src.nii.gz"
        self.imgSavePth = r"E:\B_BrainVolumn\0214\outputTOZHOU\tst.png"
        self.sliceDiect = None
        self.initSlice = 37 / 130
        self.labelLst = [13, 26]
        self.newVal = '1'
        self.angle_rotation = None
        self.outputData = None
        self.outputDataOnes = None
        self.CTA = None
        self.inMsk = None


    def LoadCTAData(self):
        # load two data
        if self.CTAPath is None:
            print("error,please input the nifity file path ")
        else:
            self.CTAOriData, self.CTAImag = LoadNifti(niiPath=self.CTAPath,)
            self.sliceDiect, self.angle_rotation = imgPlaneDirect(self.CTAImag, AnatomicalDirect='Sagittal')



    def LoadImage(self):
        # load data
        if self.Maskpath is None:
            print("error,please input the Mask file path ")
        else:
            self.ImgDatOriData,self.MskImag = LoadNifti(niiPath=self.Maskpath,)

    def FilterValues(self):
        # get array of values
        if not self.labelLst:
            self.lstOut = []
        else:
            self.lstOut = self.labelLst
        # Filter value
        self.dataFilterVals, dataFilterOnes = FilterData(
            rangStarts=self.lstOut,
            dataMat=self.ImgDatOriData,
            funType="single value"
        )

        # set new values
        if self.newVal == "":
            self.dataFilterNewVals = dataFilterOnes
        else:
            # get new mask value
            try:
                factor = float(self.newVal)
            except:
                print("Cannot get new mask value")
                factor = 1
            # set new mask value
            self.dataFilterNewVals = dataFilterOnes * factor

        self.outputData = copy.deepcopy(self.dataFilterNewVals)
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.ImgDatOriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16)

    def PlotOVerlap(self):
        # get inputs
        # Use_Plt.slider3Display(
        slider3Display(
            matData1=self.CTAOriData,
            matData2=self.outputData,
            matData3=[0],
            fig3OverLap=True,
            ask23MatData=False,
            slicDiect=self.sliceDiect,
            initSlice = self.initSlice,
            plotRange=[False, False, False],
            winMin=[300.7, 0, 300.7],
            winMax=[601.4, 255, 601.4],
            angle_rotation=self.angle_rotation,
            imagSavPth= self.imgSavePth
        )
# BMA = BrainMemoryAreaScreenshotMain()
# BMA.LoadCTAData()
# BMA.LoadImage()
# BMA.FilterValues()
# BMA.PlotOVerlap()
# print("done")