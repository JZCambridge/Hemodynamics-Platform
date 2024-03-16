# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 09:49:43 2021

@author: yingmohuanzhou
"""
import Image_Process_Functions
import Save_Load_File
import Use_Plt
import VTK_Functions
import Preprocess_Mask
import Post_Image_Process_Functions

"""
##############################################################################
#Func: Matrix to list and remove duplicates
##############################################################################
"""
import numpy


def matToListNoDulication(matData):
    # check it is array
    if not isinstance(matData, numpy.ndarray):
        raise ValueError(dispMsg="Input is not numpy.ndarray!! STOP!")

    # to list
    matList = matData.flatten().tolist()
    # print(matList)

    # remove duplication
    matListNoDupli = set(matList)
    print("Matrix list contains elements:\n" + str(matListNoDupli))

    return list(matListNoDupli)


"""
##############################################################################
#Func: Find nearest value and index in a array
##############################################################################
"""
import numpy


def FindNearest(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return idx, array[idx]


"""
##############################################################################
#Func: matrix flip axis
##############################################################################
"""
import numpy


def FilpAxes(
        inMat,
        axisInitial,
        axisFinal
):
    # convert data type
    if not isinstance(inMat, numpy.ndarray):
        inMat = numpy.array(inMat)

    # flip Y>X, Z>X, Z>Y
    if (axisInitial == 'X' or axisInitial == 'x' or axisInitial == 0) \
            and (axisFinal == 'Y' or axisFinal == 'y' or axisFinal == 1):
        outMat = numpy.swapaxes(inMat, 0, 1)
        print('Flip axes {} -> {} Shape {} -> {} Func numpy.swapaxes(inMat, 0, 1)'.format(
            axisInitial,
            axisFinal,
            numpy.shape(inMat),
            numpy.shape(outMat)))
    elif (axisInitial == 'X' or axisInitial == 'x' or axisInitial == 0) \
            and (axisFinal == 'Z' or axisFinal == 'z' or axisFinal == 2):
        outMat = numpy.swapaxes(numpy.swapaxes(inMat, 1, 2), 0, 1)  # Z->Y->X
        print('Flip axes {} -> {} Shape {} -> {} Func numpy.swapaxes(numpy.swapaxes(inMat, 1, 2), 0, 1)'.format(
            axisInitial,
            axisFinal,
            numpy.shape(inMat),
            numpy.shape(outMat)))
    elif (axisInitial == 'Y' or axisInitial == 'y' or axisInitial == 1) \
            and (axisFinal == 'Z' or axisFinal == 'z' or axisFinal == 2):
        outMat = numpy.swapaxes(inMat, 1, 2)  # Y->Z
        print('Flip axes {} -> {} Shape {} -> {} Func numpy.swapaxes(inMat, 1, 2)'.format(
            axisInitial,
            axisFinal,
            numpy.shape(inMat),
            numpy.shape(outMat)))

    # flip back
    elif (axisInitial == 'Y' or axisInitial == 'y' or axisInitial == 1) \
            and (axisFinal == 'X' or axisFinal == 'x' or axisFinal == 0):
        outMat = numpy.swapaxes(inMat, 1, 0)
        print('Flip axes {} -> {} Shape {} -> {} Func numpy.swapaxes(inMat, 1, 0)'.format(
            axisInitial,
            axisFinal,
            numpy.shape(inMat),
            numpy.shape(outMat)))
    elif (axisInitial == 'Z' or axisInitial == 'z' or axisInitial == 2) \
            and (axisFinal == 'X' or axisFinal == 'x' or axisFinal == 0):
        outMat = numpy.swapaxes(numpy.swapaxes(inMat, 1, 0), 2, 1)  # X'->Y'->Z'
        print('Flip axes {} -> {} Shape {} -> {} Func numpy.swapaxes(numpy.swapaxes(inMat, 1, 0), 2, 1)'.format(
            axisInitial,
            axisFinal,
            numpy.shape(inMat),
            numpy.shape(outMat)))
    elif axisInitial == 'Z' or axisInitial == 'z' or axisInitial == 2 \
            and axisFinal == 'Y' or axisFinal == 'y' or axisFinal == 1:
        outMat = numpy.swapaxes(inMat, 2, 1)  # Z'->Y'
        print('Flip axes {} -> {} Shape {} -> {} Func numpy.swapaxes(inMat, 2, 1)'.format(
            axisInitial,
            axisFinal,
            numpy.shape(inMat),
            numpy.shape(outMat)))
    else:
        print('ERROR: unkonwn flipping order from {} to {}'.format(axisInitial, axisFinal))
        outMat = None

    return outMat


"""
##############################################################################
#Func: Extract intensity stats of image 3D (2d slices only)
##############################################################################
"""
import numpy
import time
import scipy.stats
import pandas


def IntensityStats3DImgSlice(
        inImg,
        inMask,
        slicingDirect,
        saveCsv,
        outDir,
        outNameRef,
        filterThres=False,
        thresStart=[0],
        thresStp=[0],
        outRefName=""
):
    # init
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ''
    rtrnInfo["statics"] = {}

    # 3D data
    comapare3D = Post_Image_Process_Functions.CompareArrayDimension(
        dataMat=inImg,
        shapeD=3
    )
    if comapare3D["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += comapare3D["errorMessage"]
        print("Error: {}".format(rtrnInfo["errorMessage"]))
        return rtrnInfo

    # same shape
    compareArr = Post_Image_Process_Functions.CompareArrShape(
        dataMat1=inImg,
        dataMat2=inMask,
        DialogWarn=False
    )
    if compareArr["error"]:
        compareArr["error"] = True
        rtrnInfo["errorMessage"] += compareArr["errorMessage"]
        print("Error: {}".format(rtrnInfo["errorMessage"]))
        return rtrnInfo

    # filter data
    if filterThres:
        inImg, inOnes = Image_Process_Functions.FilterData(
            rangStarts=thresStart,
            rangStops=thresStp,
            dataMat=inImg,
            funType="boundary"
        )
        inMask = numpy.multiply(inMask, inOnes)

    # get shape
    imgShp = numpy.shape(inImg)
    # slicing direction
    if slicingDirect == "X" or slicingDirect == "x":
        # initialising array
        slicingDirect = "X"
        slices = numpy.ones([imgShp[0], 1]) * -1
        nanmin = numpy.zeros([imgShp[0], 1])
        nanmax = numpy.zeros([imgShp[0], 1])
        ptp = numpy.zeros([imgShp[0], 1])
        Q1 = numpy.zeros([imgShp[0], 1])
        Q3 = numpy.zeros([imgShp[0], 1])
        IQR = numpy.zeros([imgShp[0], 1])
        nanmedian = numpy.zeros([imgShp[0], 1])
        nanmean = numpy.zeros([imgShp[0], 1])
        nanstd = numpy.zeros([imgShp[0], 1])
        nanvar = numpy.zeros([imgShp[0], 1])
        kurtosis = numpy.zeros([imgShp[0], 1])
        skew = numpy.zeros([imgShp[0], 1])

        # loop trhough slices
        for i in range(imgShp[0]):
            # image
            mask = inMask[i]

            # jump
            if numpy.sum(mask) == 0:
                continue
            else:
                img = inImg[i]

                # array
                imgArr = img[mask != 0]

                # stats
                slices[i] = i
                nanmin[i] = numpy.nanmin(imgArr)
                nanmax[i] = numpy.nanmax(imgArr)
                ptp[i] = nanmax[i] - nanmin[i]
                Q1[i] = numpy.nanpercentile(imgArr, 25)
                Q3[i] = numpy.nanpercentile(imgArr, 75)
                IQR[i] = Q3[i] - Q1[i]
                nanmedian[i] = numpy.nanmedian(imgArr)
                nanmean[i] = numpy.nanmean(imgArr)
                nanstd[i] = numpy.nanstd(imgArr, ddof=1)
                nanvar[i] = numpy.nanvar(imgArr, ddof=1)
                kurtosis[i] = scipy.stats.kurtosis(imgArr, nan_policy='omit')
                skew[i] = scipy.stats.skew(imgArr, nan_policy='omit')

    elif slicingDirect == "Y" or slicingDirect == "y":
        # initialising array
        slicingDirect = "Y"
        slices = numpy.ones([imgShp[1], 1]) * -1
        nanmin = numpy.zeros([imgShp[1], 1])
        nanmax = numpy.zeros([imgShp[1], 1])
        ptp = numpy.zeros([imgShp[1], 1])
        Q1 = numpy.zeros([imgShp[1], 1])
        Q3 = numpy.zeros([imgShp[1], 1])
        IQR = numpy.zeros([imgShp[1], 1])
        nanmedian = numpy.zeros([imgShp[1], 1])
        nanmean = numpy.zeros([imgShp[1], 1])
        nanstd = numpy.zeros([imgShp[1], 1])
        nanvar = numpy.zeros([imgShp[1], 1])
        kurtosis = numpy.zeros([imgShp[1], 1])
        skew = numpy.zeros([imgShp[1], 1])

        # loop trhough slices
        for i in range(imgShp[1]):
            # image
            mask = inMask[:, i, :]

            # jump
            if numpy.sum(mask) == 0:
                continue
            else:
                img = inImg[:, i, :]

                # array
                imgArr = img[mask != 0]

                # stats
                slices[i] = i
                nanmin[i] = numpy.nanmin(imgArr)
                nanmax[i] = numpy.nanmax(imgArr)
                ptp[i] = nanmax[i] - nanmin[i]
                Q1[i] = numpy.nanpercentile(imgArr, 25)
                Q3[i] = numpy.nanpercentile(imgArr, 75)
                IQR[i] = Q3[i] - Q1[i]
                nanmedian[i] = numpy.nanmedian(imgArr)
                nanmean[i] = numpy.nanmean(imgArr)
                nanstd[i] = numpy.nanstd(imgArr, ddof=1)
                nanvar[i] = numpy.nanvar(imgArr, ddof=1)
                kurtosis[i] = scipy.stats.kurtosis(imgArr, nan_policy='omit')
                skew[i] = scipy.stats.skew(imgArr, nan_policy='omit')

    elif slicingDirect == "Z" or slicingDirect == "z":
        # initialising array
        slicingDirect = "Z"
        slices = numpy.zeros([imgShp[2], 1]) * -1
        nanmin = numpy.zeros([imgShp[2], 1])
        nanmax = numpy.zeros([imgShp[2], 1])
        ptp = numpy.zeros([imgShp[2], 1])
        Q1 = numpy.zeros([imgShp[2], 1])
        Q3 = numpy.zeros([imgShp[2], 1])
        IQR = numpy.zeros([imgShp[2], 1])
        nanmedian = numpy.zeros([imgShp[2], 1])
        nanmean = numpy.zeros([imgShp[2], 1])
        nanstd = numpy.zeros([imgShp[2], 1])
        nanvar = numpy.zeros([imgShp[2], 1])
        kurtosis = numpy.zeros([imgShp[2], 1])
        skew = numpy.zeros([imgShp[2], 1])

        # loop trhough slices
        for i in range(imgShp[2]):
            # image
            mask = inMask[:, :, i]

            # jump
            if numpy.sum(mask) == 0:
                continue
            else:
                img = inImg[:, :, i]

                # array
                imgArr = img[mask != 0]

                # stats
                slices[i] = i
                nanmin[i] = numpy.nanmin(imgArr)
                nanmax[i] = numpy.nanmax(imgArr)
                ptp[i] = nanmax[i] - nanmin[i]
                Q1[i] = numpy.nanpercentile(imgArr, 25)
                Q3[i] = numpy.nanpercentile(imgArr, 75)
                IQR[i] = Q3[i] - Q1[i]
                nanmedian[i] = numpy.nanmedian(imgArr)
                nanmean[i] = numpy.nanmean(imgArr)
                nanstd[i] = numpy.nanstd(imgArr, ddof=1)
                nanvar[i] = numpy.nanvar(imgArr, ddof=1)
                kurtosis[i] = scipy.stats.kurtosis(imgArr, nan_policy='omit')
                skew[i] = scipy.stats.skew(imgArr, nan_policy='omit')

    else:
        compareArr["error"] = True
        rtrnInfo["errorMessage"] += "Slicing direction unkonwn: {}".format(slicingDirect)
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    # reforming array
    slicesOut = slices[slices > -1] + 1  # image start from "1" numpy slice from "0"
    nanmin = nanmin[slices > -1]
    nanmax = nanmax[slices > -1]
    ptp = ptp[slices > -1]
    Q1 = Q1[slices > -1]
    Q3 = Q3[slices > -1]
    IQR = IQR[slices > -1]
    nanmedian = nanmedian[slices > -1]
    nanmean = nanmean[slices > -1]
    nanstd = nanstd[slices > -1]
    nanvar = nanvar[slices > -1]
    kurtosis = kurtosis[slices > -1]
    skew = skew[slices > -1]

    # statics
    rtrnInfo["statics"] = {
        outRefName + "_slices": slicesOut,
        outRefName + "_nanmin": nanmin,
        outRefName + "_nanmax": nanmax,
        outRefName + "_ptp": ptp,
        outRefName + "_Q1": Q1,
        outRefName + "_Q3": Q3,
        outRefName + "_IQR": IQR,
        outRefName + "_nanmedian": nanmedian,
        outRefName + "_nanmean": nanmean,
        outRefName + "_nanstd": nanstd,
        outRefName + "_nanvar": nanvar,
        outRefName + "_kurtosis": kurtosis,
        outRefName + "_skew": skew
    }

    if saveCsv:
        if filterThres:
            # create path
            csvPath = Save_Load_File.DateFileName(
                Dir=outDir,
                fileName=outNameRef + "_IF2" + slicingDirect,
                extension=".csv",
                appendDate=False
            )
        else:
            # create path
            csvPath = Save_Load_File.DateFileName(
                Dir=outDir,
                fileName=outNameRef + "_It2" + slicingDirect,
                extension=".csv",
                appendDate=False
            )

        # dataframe save csv
        csvDF = pandas.DataFrame.from_dict(rtrnInfo["statics"])
        # save
        csvDF.to_csv(csvPath["CombineName"], index=False)

        print('csvDF: \n{}'.format(csvDF))
        print("Save: \n{}".format(csvPath["CombineName"]))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------2D intensity stats calculation time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: Extract intensity stats of image 3D (3D overall)
##############################################################################
"""


def SliceNumberCorrect(
        sliceStart,
        sliceStop,
        boundaryStart,
        boundaryStop,
):
    # print(sliceStart,
    #       sliceStop,
    #       boundaryStart,
    #       boundaryStop)
    # flip boundary
    if boundaryStart > boundaryStop:
        temp = boundaryStop
        boundaryStop = boundaryStart
        boundaryStart = temp
        print("Flip boundary to {} - {}:".format(boundaryStart, boundaryStop))

    # flip slice
    if sliceStop < sliceStart:
        temp = sliceStop
        sliceStop = sliceStart
        sliceStart = temp
        print("Flip slices to {} - {}:".format(sliceStart, sliceStop))

    if sliceStop > boundaryStop:
        print("Reduce slice stop from {} to {} ".format(sliceStop, boundaryStop))
        sliceStop = boundaryStop

    if sliceStart < boundaryStart:
        print("Reduce slice start from {} to {} ".format(sliceStart, boundaryStart))
        sliceStart = boundaryStart

    sliceStartOut = sliceStart
    sliceStopOut = sliceStop

    # print(sliceStartOut, sliceStopOut)

    return sliceStartOut, sliceStopOut


"""
##############################################################################
#Func: Extract intensity stats of image 3D (3D overall)
##############################################################################
"""
import numpy
import time
import scipy.stats
import pandas
import sklearn.neighbors


def IntensityStats3DImg(
        startSlice,
        finishSlice,
        inMasks,
        inImgs,
        outRefNames,
        slicingDirect,
        saveCsv,
        outDir,
        outNameRef,
        filterThres=False,
        thresStart=[0],
        thresStp=[0],
        contour=False,
        ballRadius=2
):
    # init
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ''
    rtrnInfo["statics"] = {}

    # compare list
    rtrnInfo0 = Post_Image_Process_Functions.CompareListDimension(
        [inMasks, inImgs, outRefNames]
    )
    if rtrnInfo0["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += rtrnInfo0["errorMessage"]
        print("Error: {}".format(rtrnInfo["errorMessage"]))
        return rtrnInfo

    # initialising array
    nanmin = numpy.zeros([len(inMasks), 1])
    nanmax = numpy.zeros([len(inMasks), 1])
    ptp = numpy.zeros([len(inMasks), 1])
    Q1 = numpy.zeros([len(inMasks), 1])
    Q3 = numpy.zeros([len(inMasks), 1])
    IQR = numpy.zeros([len(inMasks), 1])
    nanmedian = numpy.zeros([len(inMasks), 1])
    nanmean = numpy.zeros([len(inMasks), 1])
    nanstd = numpy.zeros([len(inMasks), 1])
    nanvar = numpy.zeros([len(inMasks), 1])
    kurtosis = numpy.zeros([len(inMasks), 1])
    skew = numpy.zeros([len(inMasks), 1])

    # start & finish slices
    if not isinstance(startSlice, list):
        startSlices = [startSlice] * len(inMasks)
    else:
        startSlices = startSlice
    if not isinstance(finishSlice, list):
        finishSlices = [finishSlice] * len(inMasks)
    else:
        finishSlices = finishSlice

    # compare list
    rtrnInfo0 = Post_Image_Process_Functions.CompareListDimension(
        [startSlices, finishSlices, outRefNames]
    )
    if rtrnInfo0["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += rtrnInfo0["errorMessage"]
        print("Error: {}".format(rtrnInfo["errorMessage"]))
        return rtrnInfo

    for inMask, inImg, i, startSlice, finishSlice in \
            zip(
                inMasks,
                inImgs,
                range(len(inMasks)),
                startSlices,
                finishSlices
            ):
        # load
        if isinstance(inMask, str):
            inMask = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=inMask
            ).OriData
        if isinstance(inImg, str):
            inImg = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=inImg
            ).OriData

        # filter data
        if filterThres:
            inImg, inOnes = Image_Process_Functions.FilterData(
                rangStarts=thresStart,
                rangStops=thresStp,
                dataMat=inImg,
                funType="boundary"
            )
            inMask = numpy.multiply(inMask, inOnes)

        # get shape
        imgShp = numpy.shape(inImg)
        # slicing direction
        if slicingDirect == "X" or slicingDirect == "x":
            # convert slices
            startSlice, finishSlice = SliceNumberCorrect(
                sliceStart=startSlice,
                sliceStop=finishSlice,
                boundaryStart=0,
                boundaryStop=imgShp[0],
            )

            # create mask/ contour mask
            useMask = numpy.zeros(imgShp)
            if contour:
                # fill
                for slc in range(startSlice, finishSlice):
                    if numpy.sum(inMask[slc]) == 0:
                        continue
                    contourCoords = skimage.measure.find_contours(
                        image=inMask[slc],
                        level=None,
                        fully_connected='low',
                        positive_orientation='low',
                        mask=None
                    )
                    # # empty slice
                    # coutourSlc = numpy.zeros([imgShp[1], imgShp[2]])

                    # fill
                    useMask[slc][contourCoords[0][:, 0].astype(int), contourCoords[0][:, 1].astype(int)] = 1
            else:
                useMask = inMask[startSlice:finishSlice]

            # Non-zero matching
            # create ball nearest neighbour
            imgCoordsN0 = numpy.where(inImg != 0)  # [depthZ, RowY, ColumnX].T
            imgCoordsN0 = numpy.array([imgCoordsN0[0], imgCoordsN0[1], imgCoordsN0[2]])  # convert to array
            imgN0 = inImg[numpy.where(inImg != 0)]
            tree = sklearn.neighbors.BallTree(imgCoordsN0.T, leaf_size=imgShp[0] / 4)

            # contour
            useMaskCoordsN0 = numpy.where(useMask != 0)  # [depthZ, RowY, ColumnX].T
            useMaskCoordsN0Depth = useMaskCoordsN0[0]
            useMaskCoordsN0Row = useMaskCoordsN0[1]
            useMaskCoordsN0Column = useMaskCoordsN0[2]
            useMaskCoordsN0 = numpy.array(
                [useMaskCoordsN0[0], useMaskCoordsN0[1], useMaskCoordsN0[2]])  # convert to array

            ## nearest neighbour
            (ind, dist) = tree.query_radius(
                useMaskCoordsN0.T,
                r=ballRadius,
                return_distance=True,
                sort_results=True
            )

            ## fill
            useImg = numpy.zeros(imgShp)
            # print(useMaskCoordsN0Depth)
            # print(numpy.shape(useMaskCoordsN0Depth))
            for pnt in range(numpy.shape(useMaskCoordsN0Depth)[0]):
                # closest indices
                if ind[pnt].size != 0:  # NOT empty array
                    useImg[useMaskCoordsN0Depth[pnt], useMaskCoordsN0Row[pnt], useMaskCoordsN0Column[pnt]] = imgN0[
                        ind[pnt][0]]
                    # print('mask point: {} match image point: {} with value ={}'
                    #       .format([useMaskCoordsN0Depth[pnt], useMaskCoordsN0Row[pnt], useMaskCoordsN0Column[pnt]],
                    #               ind[pnt][0],
                    #               imgN0[ind[pnt][0]]))

            # stats
            # array
            imgArr = useImg[useMask != 0]
            # print(imgArr)
            # print(numpy.shape(imgArr))

            # stats
            nanmin[i] = numpy.nanmin(imgArr)
            nanmax[i] = numpy.nanmax(imgArr)
            ptp[i] = nanmax[i] - nanmin[i]
            Q1[i] = numpy.nanpercentile(imgArr, 25)
            Q3[i] = numpy.nanpercentile(imgArr, 75)
            IQR[i] = Q3[i] - Q1[i]
            nanmedian[i] = numpy.nanmedian(imgArr)
            nanmean[i] = numpy.nanmean(imgArr)
            nanstd[i] = numpy.nanstd(imgArr, ddof=1)
            nanvar[i] = numpy.nanvar(imgArr, ddof=1)
            kurtosis[i] = scipy.stats.kurtosis(imgArr, nan_policy='omit')
            skew[i] = scipy.stats.skew(imgArr, nan_policy='omit')

    # statics
    rtrnInfo["statics"] = {
        "Ref": outRefNames,
        "Min": numpy.concatenate(nanmin),
        "Max": numpy.concatenate(nanmax),
        "PTP": numpy.concatenate(ptp),
        "Q1": numpy.concatenate(Q1),
        "Q3": numpy.concatenate(Q3),
        "IQR": numpy.concatenate(IQR),
        "Median": numpy.concatenate(nanmedian),
        "Mean": numpy.concatenate(nanmean),
        "STD": numpy.concatenate(nanstd),
        "Variance": numpy.concatenate(nanvar),
        "Kurtosis": numpy.concatenate(kurtosis),
        "Skew": numpy.concatenate(skew)
    }

    if saveCsv:
        if filterThres:
            # create path
            csvPath = Save_Load_File.DateFileName(
                Dir=outDir,
                fileName=outNameRef + "_3DIF2" + slicingDirect,
                extension=".csv",
                appendDate=False
            )
        else:
            # create path
            csvPath = Save_Load_File.DateFileName(
                Dir=outDir,
                fileName=outNameRef + "_3DIt2" + slicingDirect,
                extension=".csv",
                appendDate=False
            )

        # print(numpy.shape(outRefNames))
        # print(numpy.shape(nanmin))
        # print(numpy.shape(nanmax))
        # print(numpy.shape(ptp))
        # print(numpy.shape(Q1))
        # print(numpy.shape(Q3))
        # print(numpy.shape(nanmedian))
        # print(numpy.shape(nanmean))
        # print(numpy.shape(nanstd))
        # print(numpy.shape(nanvar))
        # print(numpy.shape(kurtosis))
        # print(numpy.shape(skew))

        # dataframe save csv
        csvDF = pandas.DataFrame(rtrnInfo["statics"])
        # save
        csvDF.to_csv(csvPath["CombineName"], index=False)

        print('csvDF: \n{}'.format(csvDF))
        print("Save: \n{}".format(csvPath["CombineName"]))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------3D intensity stats calculation time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: Create contour mask
##############################################################################
"""
import cv2
import skimage.draw
import skimage.morphology


def CreateContourMask(
        inMask,
        sliceStart,
        sliceFinish,
        multiContour=False,
        fillValue=False,
        inMaskBakground=0,
        skimagMethod=True,
        openCvMethod=False
):
    # create use mask
    useMask = numpy.zeros(numpy.shape(inMask))

    # convert slices ONLY dealing with x axis!
    startSlice, finishSlice = SliceNumberCorrect(
        sliceStart=sliceStart,
        sliceStop=sliceFinish,
        boundaryStart=0,
        boundaryStop=numpy.shape(inMask)[0],
    )

    # fill
    for slc in range(startSlice, finishSlice + 1):
        if numpy.sum(inMask[slc]) == 0:
            continue

        oriMask = 1 * (inMask[slc] != 0)

        # # closing for good contour
        # footprint = skimage.morphology.disk(2)
        # opened = skimage.morphology.opening(oriMask, footprint)
        # if numpy.sum(opened) == 0:
        #     opened = oriMask

        # no opening
        opened = oriMask

        # Method
        if skimagMethod:
            contourCoords = skimage.measure.find_contours(
                image=opened,
                level=1 / 2,
                fully_connected='low',
                positive_orientation='low',
                mask=None
            )

            # # fill
            # if not multiContour:
            #     useMask[slc][contourCoords[0][:, 0].astype(int), contourCoords[0][:, 1].astype(int)] = 1
            # else:
            #     for conCase in range(numpy.shape(contourCoords)[0]):
            #         useMask[slc][contourCoords[conCase][:, 0].astype(int), contourCoords[conCase][:, 1].astype(int)] = 1

            # polygon boundary
            if not multiContour:
                # polygon
                r = contourCoords[0][:, 0]  # .astype(int)
                c = contourCoords[0][:, 1]  # .astype(int)
                rr, cc = skimage.draw.polygon_perimeter(r, c, shape=numpy.shape(inMask[slc]), clip=False)
                useMask[slc][rr, cc] = 1
            else:
                for conCase in range(numpy.shape(contourCoords)[0]):
                    # polygon
                    r = contourCoords[conCase][:, 0]  # .astype(int)
                    c = contourCoords[conCase][:, 1]  # .astype(int)
                    rr, cc = skimage.draw.polygon_perimeter(r, c, shape=numpy.shape(inMask[slc]), clip=False)
                    useMask[slc][rr, cc] = 1

        if openCvMethod:
            # CV2 contour
            # Need to convert to CV_8UC1 == numpy.uint8
            contourBase = copy.deepcopy(opened)
            contourBase = contourBase.astype(numpy.uint8)
            contours, hierarchy = cv2.findContours(contourBase,
                                                   cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE,
                                                   offset=(0, 0))

            # fill
            if not multiContour:
                useMask[slc][contours[0][:, :, 0].astype(int), contours[0][:, :, 1].astype(int)] = 1
            else:
                for conCase in range(numpy.shape(contours)[0]):
                    useMask[slc][contours[conCase][:, :, 0].astype(int), contours[conCase][:, :, 1].astype(int)] = 1

    # !!! contour only fill the mask edges
    # Probably no need Disabled here
    # useMask = useMask * (inMask != inMaskBakground) * 1

    # change value
    if fillValue:
        useMask = numpy.multiply(useMask, inMask)

    print('Complete Contour Mask')

    return useMask


"""
##############################################################################
#Func: Ball tree 3d Mask fill
##############################################################################
"""


def NonZeroBallFill(
        inImg,
        inMask,
        ballRadius,
        imgExcludeValues,
        maskExcludeValues
):
    # Non-zero matching
    rtrnInfo = Post_Image_Process_Functions.CompareArrShape(
        dataMat1=inImg,
        dataMat2=inMask
    )
    if rtrnInfo["error"]:
        raise ValueError("Ball tree match got images not the same shape!!")

    # excluding values
    imgCoordsN0 = numpy.ones(numpy.shape(inImg))
    if isinstance(imgExcludeValues, list):
        for excludeValue in imgExcludeValues:
            imgCoordsN0 = numpy.multiply(imgCoordsN0, numpy.where(inImg != excludeValue))
    else:
        imgCoordsN0 = numpy.where(inImg != imgExcludeValues)  # [depthZ, RowY, ColumnX].T

    # create ball nearest neighbour
    imgN0 = inImg[imgCoordsN0]
    imgCoordsN0 = numpy.array(
        [imgCoordsN0[0],
         imgCoordsN0[1],
         imgCoordsN0[2]]
    )  # convert to array

    # create tree
    imgShp = numpy.shape(inImg)
    tree = sklearn.neighbors.BallTree(imgCoordsN0.T, leaf_size=imgShp[0] / 4)

    # mask exclusion
    useMaskCoordsN0 = numpy.ones(numpy.shape(inImg))
    if isinstance(maskExcludeValues, list):
        for excludeValue in maskExcludeValues:
            useMaskCoordsN0 = numpy.multiply(useMaskCoordsN0, numpy.where(inMask != excludeValue))
    else:
        useMaskCoordsN0 = numpy.where(inMask != maskExcludeValues)  # [depthZ, RowY, ColumnX].T

    # contour
    useMaskCoordsN0Depth = useMaskCoordsN0[0]
    useMaskCoordsN0Row = useMaskCoordsN0[1]
    useMaskCoordsN0Column = useMaskCoordsN0[2]
    useMaskCoordsN0 = numpy.array(
        [useMaskCoordsN0[0],
         useMaskCoordsN0[1],
         useMaskCoordsN0[2]]
    )  # convert to array

    ## nearest neighbour
    (ind, dist) = tree.query_radius(
        useMaskCoordsN0.T,
        r=ballRadius,
        return_distance=True,
        sort_results=True
    )

    ## fill
    useImg = numpy.zeros(numpy.shape(inImg))
    # print(useMaskCoordsN0Depth)
    # print(numpy.shape(useMaskCoordsN0Depth))
    for pnt in range(numpy.shape(useMaskCoordsN0Depth)[0]):
        # closest indices
        if ind[pnt].size != 0:  # NOT empty array
            useImg[
                useMaskCoordsN0Depth[pnt],
                useMaskCoordsN0Row[pnt],
                useMaskCoordsN0Column[pnt]
            ] = imgN0[
                ind[pnt][0]
            ]

            # message
            msg = "\nMask point: depth = {}, Row = {}, Column = {} " \
                  "Parameter point: depth = {}, Row = {}, Column = {} " \
                  "Value: {}".format(
                useMaskCoordsN0Depth[pnt],
                useMaskCoordsN0Row[pnt],
                useMaskCoordsN0Column[pnt],
                imgCoordsN0[:, ind[pnt][0]][0],
                imgCoordsN0[:, ind[pnt][0]][1],
                imgCoordsN0[:, ind[pnt][0]][2],
                imgN0[ind[pnt][0]]
            )
            # print(msg)

    print('Complete Ball Match')

    return useImg


"""
##############################################################################
#Func: Extract intensity stats from 3D image points
##############################################################################
"""


def IntensityStats3DImgPoints(
        startSlices,
        finishSlices,
        inMasks,
        inImgs,
        columnPrefixs,
        slicingDirect,
        caseNameRef,
        saveCsv=False,
        outDir="",
        outNameRef="",
        filterThres=False,
        thresStart=[0],
        thresStp=[0],
        contours=[0],
        ballRadius=2,
        compareOriImg=True,
        inOriMasks=[],
        inOriImgs=[],
        index=0,
        saveDiffImage=False,
        percentile=99.5,
        absVal=False,
        outPut995=True,
        outPut99=True,
        outPutABS=True,
        outPutABS995=True,
        outPutABS99=True,
        sameMask=True,
        startRows=[0],
        finishRows=[0],
        startColumns=[0],
        finishColumns=[0],
        noCompare=True,
        outMin=True,
        outMax=True,
        outPTP=True,
        outQ1=True,
        outQ3=True,
        outIQR=True,
        outMedian=True,
        outMean=True,
        outSTD=True,
        outVar=True,
        outKurt=True,
        outSkew=True,
        outMode=True,
        outRMS=True,
        outHMean=True,
        outGMean=True,
        outTriMean=True,
        outDecile1=True,
        outDecile2=True,
        outDecile3=True,
        outDecile4=True,
        outDecile6=True,
        outDecile7=True,
        outDecile8=True,
        outDecile9=True,
        outSE=True,
        outEnergy=True,
        outEntropy=True
):
    # init
    # time
    strtT = time.time()

    # string case ref
    caseNameRef = str(caseNameRef)

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ''
    rtrnInfo["dataFrame"] = None
    rtrnInfo["statics"] = {}
    rtrnInfo["statics"]['Ref'] = caseNameRef

    # compare list
    rtrnInfo0 = Post_Image_Process_Functions.CompareListDimension(
        [inMasks,
         inImgs,
         columnPrefixs]
    )
    if rtrnInfo0["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += rtrnInfo0["errorMessage"]
        print("Error: {}".format(rtrnInfo["errorMessage"]))
        return rtrnInfo

    # start & finish slices
    if not isinstance(startSlices, list):
        startSlices = [startSlices] * len(inMasks)
    else:
        startSlices = startSlices
    if not isinstance(finishSlices, list):
        finishSlices = [finishSlices] * len(inMasks)
    else:
        finishSlices = finishSlices
    if not isinstance(startRows, list):
        startRows = [startRows] * len(inMasks)
    else:
        startRows = startRows
    if not isinstance(finishRows, list):
        finishRows = [finishRows] * len(inMasks)
    else:
        finishRows = finishRows
    if not isinstance(startColumns, list):
        startColumns = [startColumns] * len(inMasks)
    else:
        startColumns = startColumns
    if not isinstance(finishColumns, list):
        finishColumns = [finishColumns] * len(inMasks)
    else:
        finishColumns = finishColumns

    # compare list
    rtrnInfo0 = Post_Image_Process_Functions.CompareListDimension(
        [startSlices,
         finishSlices,
         columnPrefixs]
    )
    if rtrnInfo0["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += rtrnInfo0["errorMessage"]
        print("Error: {}".format(rtrnInfo["errorMessage"]))
        return rtrnInfo

    if compareOriImg and not sameMask:
        for inMask, \
            inImg, \
            inOriMask, \
            inOriImg, \
            columnPrefix, \
            startSlice, \
            finishSlice, \
            startColumn, \
            finishColumn, \
            startRow, \
            finishRow, \
            contour in \
                zip(
                    inMasks,
                    inImgs,
                    inOriMasks,
                    inOriImgs,
                    columnPrefixs,
                    startSlices,
                    finishSlices,
                    startColumns,
                    finishColumns,
                    startRows,
                    finishRows,
                    contours
                ):
            # load
            if isinstance(inMask, str):
                inMask = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inMask
                ).OriData
            if isinstance(inImg, str):
                refImg = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inImg
                )
                inImg = refImg.OriData
            if isinstance(inOriMask, str):
                inOriMask = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inOriMask
                ).OriData
            if isinstance(inOriImg, str):
                inOriImg = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inOriImg
                ).OriData

            # filter data
            if filterThres:
                inImg, inOnes = Image_Process_Functions.FilterData(
                    rangStarts=thresStart,
                    rangStops=thresStp,
                    dataMat=inImg,
                    funType="boundary"
                )
                inMask = numpy.multiply(inMask, inOnes)
                inOriImg, inOnes = Image_Process_Functions.FilterData(
                    rangStarts=thresStart,
                    rangStops=thresStp,
                    dataMat=inOriImg,
                    funType="boundary"
                )
                inOriMask = numpy.multiply(inOriMask, inOnes)

            # get shape
            imgShp = numpy.shape(inImg)
            # slicing direction
            if slicingDirect == "X" or slicingDirect == "x":
                # convert slices
                startSlice, finishSlice = SliceNumberCorrect(
                    sliceStart=startSlice,
                    sliceStop=finishSlice,
                    boundaryStart=0,
                    boundaryStop=imgShp[0],
                )

                # create mask/ contour mask
                if contour:
                    # contour with slices
                    useMaskInit = CreateContourMask(
                        inMask=inMask,
                        sliceStart=startSlice,
                        sliceFinish=finishSlice,
                        multiContour=False,
                        fillValue=False
                    )
                    useOriMaskInit = CreateContourMask(
                        inMask=inOriMask,
                        sliceStart=startSlice,
                        sliceFinish=finishSlice,
                        multiContour=False,
                        fillValue=False
                    )
                else:
                    useMaskInit = inMask
                    useOriMaskInit = inOriMask

                # cut region
                useMask = Image_Process_Functions.CutVOI(
                    inArr=useMaskInit,
                    startSlices=[startSlice],
                    finishSlices=[finishSlice],
                    startRows=[startRow],
                    finishRows=[finishRow],
                    startColumns=[startColumn],
                    finishColumns=[finishColumn]
                )
                useOriMask = Image_Process_Functions.CutVOI(
                    inArr=useOriMaskInit,
                    startSlices=[startSlice],
                    finishSlices=[finishSlice],
                    startRows=[startRow],
                    finishRows=[finishRow],
                    startColumns=[startColumn],
                    finishColumns=[finishColumn]
                )

                # Non-zero matching
                useImg = NonZeroBallFill(
                    inImg=inImg,
                    inMask=useMask,
                    ballRadius=ballRadius,
                    imgExcludeValues=0,
                    maskExcludeValues=0
                )
                useOriImg = NonZeroBallFill(
                    inImg=inOriImg,
                    inMask=useOriMask,
                    ballRadius=ballRadius,
                    imgExcludeValues=0,
                    maskExcludeValues=0
                )

                # save diagnosis image
                if saveDiffImage:
                    # diagnosis image
                    imageRatioImg = numpy.divide(
                        (useOriImg - useImg),
                        useOriImg,
                        where=(useOriImg != 0)
                    ) * 100

                    # create directory
                    Save_Load_File.checkCreateDir(outDir)

                    # Set file name
                    valDiffFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'PerDiff',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    useMaskFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'useMask',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    useOriMaskFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'useOriMask',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    valOriFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'BaseImg',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    valCompareFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'CompareImg',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    useMaskInitFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'useMaskInit',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    useOriMaskInitFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'useOriMaskInit',
                        extension=".nii.gz",
                        appendDate=False
                    )

                    # save
                    Save_Load_File.MatNIFTISave(
                        MatData=imageRatioImg,
                        imgPath=valDiffFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useOriImg,
                        imgPath=valOriFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useImg,
                        imgPath=valCompareFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useMask,
                        imgPath=useMaskFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useOriMask,
                        imgPath=useOriMaskFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useMaskInit,
                        imgPath=useMaskInitFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useOriMaskInit,
                        imgPath=useOriMaskInitFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )

                # stats
                imgArr = useImg[useMask != 0]
                imgOriArr = useOriImg[useOriMask != 0]
                imgArrRatios = (imgOriArr - imgArr) / imgOriArr * 100

                # out dictionary str
                outSuff = 'Diff_'

                # absolute value
                if absVal:
                    imgArrRatiosUse = numpy.absolute(imgArrRatios)
                    outSuff += 'abs'
                else:
                    imgArrRatiosUse = imgArrRatios

                # percentile
                imgArrRatiosUse = KeepTwoTailofRange(
                    inArr=imgArrRatiosUse,
                    perntageKeep=percentile
                )
                outSuff += str(percentile)

                # replace 0 in array for special 1/x calculation
                imgArrRatiosUse_0r1 = copy.deepcopy(imgArrRatiosUse)
                imgArrRatiosUse_0r1 = numpy.abs(imgArrRatiosUse_0r1)
                imgArrRatiosUse_0r1[imgArrRatiosUse_0r1 == 0] = 1

                # stats
                if outMin:
                    rtrnInfo["statics"][columnPrefix + '_Min' + '_' + outSuff] = numpy.nanmin(imgArrRatiosUse)
                if outMax:
                    rtrnInfo["statics"][columnPrefix + '_Max' + '_' + outSuff] = numpy.nanmax(imgArrRatiosUse)
                if outPTP:
                    rtrnInfo["statics"][columnPrefix + '_PTP' + '_' + outSuff] = rtrnInfo["statics"][
                        columnPrefix + '_Max' + '_' + outSuff] - rtrnInfo["statics"][
                        columnPrefix + '_Min' + '_' + outSuff]
                if outQ1:
                    rtrnInfo["statics"][columnPrefix + '_Q1' + '_' + outSuff] = numpy.nanpercentile(imgArrRatiosUse, 25)
                if outQ3:
                    rtrnInfo["statics"][columnPrefix + '_Q3' + '_' + outSuff] = numpy.nanpercentile(imgArrRatiosUse, 75)
                if outIQR:
                    rtrnInfo["statics"][columnPrefix + '_IQR' + '_' + outSuff] = rtrnInfo["statics"][
                        columnPrefix + '_Q3' + '_' + outSuff] - rtrnInfo["statics"][
                        columnPrefix + '_Q1' + '_' + outSuff]
                if outMedian:
                    rtrnInfo["statics"][columnPrefix + '_Median' + '_' + outSuff] = numpy.nanmedian(imgArrRatiosUse)
                if outMode:
                    rtrnInfo["statics"][columnPrefix + '_Mode' + '_' + outSuff] = scipy.stats.mode(
                        imgArrRatiosUse, nan_policy='omit')[0][0]
                if outMean:
                    rtrnInfo["statics"][columnPrefix + '_Mean' + '_' + outSuff] = numpy.nanmean(imgArrRatiosUse)
                if outRMS:
                    rtrnInfo["statics"][columnPrefix + '_RMS' + '_' + outSuff] = numpy.sqrt(numpy.nanmean(
                        imgArrRatiosUse ** 2))
                if outHMean:
                    rtrnInfo["statics"][columnPrefix + '_HMean' + '_' + outSuff] = scipy.stats.hmean(
                        imgArrRatiosUse_0r1)
                if outGMean:
                    rtrnInfo["statics"][columnPrefix + '_GMean' + '_' + outSuff] = scipy.stats.gmean(
                        imgArrRatiosUse_0r1)
                if outTriMean:
                    rtrnInfo["statics"][columnPrefix + '_TriMean' + '_' + outSuff] = (numpy.nanpercentile(
                        imgArrRatiosUse, 25) + 2 * numpy.nanpercentile(imgArrRatiosUse, 50) + numpy.nanpercentile(
                        imgArrRatiosUse, 75)) / 4
                if outDecile1:
                    rtrnInfo["statics"][columnPrefix + '_Decile1' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 10)
                if outDecile2:
                    rtrnInfo["statics"][columnPrefix + '_Decile2' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 20)
                if outDecile3:
                    rtrnInfo["statics"][columnPrefix + '_Decile3' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 30)
                if outDecile4:
                    rtrnInfo["statics"][columnPrefix + '_Decile4' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 40)
                if outDecile6:
                    rtrnInfo["statics"][columnPrefix + '_Decile6' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 60)
                if outDecile7:
                    rtrnInfo["statics"][columnPrefix + '_Decile7' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 70)
                if outDecile8:
                    rtrnInfo["statics"][columnPrefix + '_Decile8' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 80)
                if outDecile9:
                    rtrnInfo["statics"][columnPrefix + '_Decile9' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 90)
                if outSTD:
                    rtrnInfo["statics"][columnPrefix + '_STD' + '_' + outSuff] = numpy.nanstd(imgArrRatiosUse, ddof=1)
                if outVar:
                    rtrnInfo["statics"][columnPrefix + '_Variance' + '_' + outSuff] = numpy.nanvar(
                        imgArrRatiosUse, ddof=1)
                if outKurt:
                    rtrnInfo["statics"][columnPrefix + '_Kurtosis' + '_' + outSuff] = scipy.stats.kurtosis(
                        imgArrRatiosUse, nan_policy='omit')
                if outSkew:
                    rtrnInfo["statics"][columnPrefix + '_Skew' + '_' + outSuff] = scipy.stats.skew(
                        imgArrRatiosUse, nan_policy='omit')
                if outSE:
                    rtrnInfo["statics"][columnPrefix + '_SE' + '_' + outSuff] = scipy.stats.sem(
                        imgArrRatiosUse, nan_policy='omit')
                if outEnergy:
                    rtrnInfo["statics"][columnPrefix + '_Energy' + '_' + outSuff] = numpy.nansum(imgArrRatiosUse ** 2)
                if outEntropy:
                    rtrnInfo["statics"][columnPrefix + '_Entropy' + '_' + outSuff] = scipy.stats.entropy(
                        imgArrRatiosUse)
                
                # 99.5 percentile
                if outPut995:
                    imgArrRatiosPerc995 = KeepTwoTailofRange(
                        inArr=imgArrRatios,
                        perntageKeep=99.5
                    )

                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPerc995_0r1 = copy.deepcopy(imgArrRatiosPerc995)
                    imgArrRatiosPerc995_0r1 = numpy.abs(imgArrRatiosPerc995_0r1)
                    imgArrRatiosPerc995_0r1[imgArrRatiosPerc995_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_995'] = numpy.nanmin(imgArrRatiosPerc995)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_995'] = numpy.nanmax(imgArrRatiosPerc995)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_995'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_995'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_995']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_995'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_995'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_995']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_995'] = numpy.nanmedian(imgArrRatiosPerc995)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_995'] = scipy.stats.mode(
                            imgArrRatiosPerc995, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_995'] = numpy.nanmean(imgArrRatiosPerc995)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_995'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatiosPerc995 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_995'] = scipy.stats.hmean(
                            imgArrRatiosPerc995_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_995'] = scipy.stats.gmean(
                            imgArrRatiosPerc995_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_995'] = (numpy.nanpercentile(
                            imgArrRatiosPerc995, 25) + 2 * numpy.nanpercentile(
                            imgArrRatiosPerc995, 50) + numpy.nanpercentile(imgArrRatiosPerc995, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_995'] = numpy.nanstd(
                            imgArrRatiosPerc995, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_995'] = numpy.nanvar(
                            imgArrRatiosPerc995, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_995'] = scipy.stats.kurtosis(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_995'] = scipy.stats.skew(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_995'] = scipy.stats.sem(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_995'] = numpy.nansum(
                            imgArrRatiosPerc995 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_995'] = scipy.stats.entropy(
                            imgArrRatiosPerc995)

                # 99 percentile
                if outPut99:
                    imgArrRatiosPerc99 = KeepTwoTailofRange(
                        inArr=imgArrRatios,
                        perntageKeep=99
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPerc99_0r1 = copy.deepcopy(imgArrRatiosPerc99)
                    imgArrRatiosPerc99_0r1 = numpy.abs(imgArrRatiosPerc99_0r1)
                    imgArrRatiosPerc99_0r1[imgArrRatiosPerc99_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_99'] = numpy.nanmin(imgArrRatiosPerc99)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_99'] = numpy.nanmax(imgArrRatiosPerc99)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_99'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_99'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_99']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_99'] = numpy.nanpercentile(imgArrRatiosPerc99, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_99'] = numpy.nanpercentile(imgArrRatiosPerc99, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_99'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_99'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_99']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_99'] = numpy.nanmedian(imgArrRatiosPerc99)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_99'] = scipy.stats.mode(
                            imgArrRatiosPerc99, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_99'] = numpy.nanmean(imgArrRatiosPerc99)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_99'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatiosPerc99 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_99'] = scipy.stats.hmean(
                            imgArrRatiosPerc99_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_99'] = scipy.stats.gmean(
                            imgArrRatiosPerc99_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_99'] = (numpy.nanpercentile(
                            imgArrRatiosPerc99, 25) + 2 * numpy.nanpercentile(
                            imgArrRatiosPerc99, 50) + numpy.nanpercentile(imgArrRatiosPerc99, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_99'] = numpy.nanstd(
                            imgArrRatiosPerc99, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_99'] = numpy.nanvar(
                            imgArrRatiosPerc99, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_99'] = scipy.stats.kurtosis(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_99'] = scipy.stats.skew(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_99'] = scipy.stats.sem(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_99'] = numpy.nansum(
                            imgArrRatiosPerc99 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_99'] = scipy.stats.entropy(
                            imgArrRatiosPerc99)

                # absolute values
                if outPutABS:
                    imgArrRatios_abs = numpy.absolute(imgArrRatios)
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs_0r1 = copy.deepcopy(imgArrRatios_abs)
                    imgArrRatiosPercabs_0r1 = numpy.abs(imgArrRatiosPercabs_0r1)
                    imgArrRatiosPercabs_0r1[imgArrRatiosPercabs_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs'] = numpy.nanmin(imgArrRatios_abs)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs'] = numpy.nanmax(imgArrRatios_abs)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_abs'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs'] = numpy.nanpercentile(imgArrRatios_abs, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs'] = numpy.nanpercentile(imgArrRatios_abs, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_abs'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs'] = numpy.nanmedian(imgArrRatios_abs)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs'] = scipy.stats.mode(
                            imgArrRatios_abs, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs'] = numpy.nanmean(imgArrRatios_abs)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_abs ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs'] = scipy.stats.hmean(
                            imgArrRatiosPercabs_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs'] = scipy.stats.gmean(
                            imgArrRatiosPercabs_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs'] = (numpy.nanpercentile(
                            imgArrRatios_abs, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_abs, 50) + numpy.nanpercentile(imgArrRatios_abs, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs'] = numpy.nanstd(
                            imgArrRatios_abs, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs'] = numpy.nanvar(
                            imgArrRatios_abs, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs'] = scipy.stats.kurtosis(
                            imgArrRatios_abs, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs'] = scipy.stats.skew(
                            imgArrRatios_abs, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs'] = scipy.stats.sem(
                            imgArrRatios_abs, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs'] = numpy.nansum(
                            imgArrRatios_abs ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs'] = scipy.stats.entropy(
                            imgArrRatios_abs)

                # 99.5 percentile abs
                if outPutABS995:
                    imgArrRatios_abs = numpy.absolute(imgArrRatios)
                    imgArrRatios_absPerc995 = KeepTwoTailofRange(
                        inArr=imgArrRatios_abs,
                        perntageKeep=99.5
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs995_0r1 = copy.deepcopy(imgArrRatios_absPerc995)
                    imgArrRatiosPercabs995_0r1 = numpy.abs995(imgArrRatiosPercabs995_0r1)
                    imgArrRatiosPercabs995_0r1[imgArrRatiosPercabs995_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs995'] = numpy.nanmin(imgArrRatios_absPerc995)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs995'] = numpy.nanmax(imgArrRatios_absPerc995)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs995'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_abs995'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs995']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs995'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_abs995'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs995']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs995'] = numpy.nanmedian(
                            imgArrRatios_absPerc995)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs995'] = scipy.stats.mode(
                            imgArrRatios_absPerc995, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs995'] = numpy.nanmean(imgArrRatios_absPerc995)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs995'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_absPerc995 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs995'] = scipy.stats.hmean(
                            imgArrRatiosPercabs995_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs995'] = scipy.stats.gmean(
                            imgArrRatiosPercabs995_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs995'] = (numpy.nanpercentile(
                            imgArrRatios_absPerc995, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_absPerc995, 50) + numpy.nanpercentile(imgArrRatios_absPerc995, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs995'] = numpy.nanstd(
                            imgArrRatios_absPerc995, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs995'] = numpy.nanvar(
                            imgArrRatios_absPerc995, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs995'] = scipy.stats.kurtosis(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs995'] = scipy.stats.skew(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs995'] = scipy.stats.sem(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs995'] = numpy.nansum(
                            imgArrRatios_absPerc995 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs995'] = scipy.stats.entropy(
                            imgArrRatios_absPerc995)

                # 99 percentile abs
                if outPutABS99:
                    imgArrRatios_abs = numpy.absolute(imgArrRatios)
                    imgArrRatios_absPerc99 = KeepTwoTailofRange(
                        inArr=imgArrRatios_abs,
                        perntageKeep=99
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs99_0r1 = copy.deepcopy(imgArrRatios_absPerc99)
                    imgArrRatiosPercabs99_0r1 = numpy.abs99(imgArrRatiosPercabs99_0r1)
                    imgArrRatiosPercabs99_0r1[imgArrRatiosPercabs99_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs99'] = numpy.nanmin(imgArrRatios_absPerc99)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs99'] = numpy.nanmax(imgArrRatios_absPerc99)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs99'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_abs99'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs99']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs99'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_abs99'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs99']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs99'] = numpy.nanmedian(
                            imgArrRatios_absPerc99)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs99'] = scipy.stats.mode(
                            imgArrRatios_absPerc99, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs99'] = numpy.nanmean(imgArrRatios_absPerc99)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs99'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_absPerc99 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs99'] = scipy.stats.hmean(
                            imgArrRatiosPercabs99_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs99'] = scipy.stats.gmean(
                            imgArrRatiosPercabs99_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs99'] = (numpy.nanpercentile(
                            imgArrRatios_absPerc99, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_absPerc99, 50) + numpy.nanpercentile(imgArrRatios_absPerc99, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs99'] = numpy.nanstd(
                            imgArrRatios_absPerc99, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs99'] = numpy.nanvar(
                            imgArrRatios_absPerc99, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs99'] = scipy.stats.kurtosis(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs99'] = scipy.stats.skew(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs99'] = scipy.stats.sem(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs99'] = numpy.nansum(
                            imgArrRatios_absPerc99 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs99'] = scipy.stats.entropy(
                            imgArrRatios_absPerc99)

    elif compareOriImg and sameMask:
        for inMask, \
            inImg, \
            inOriImg, \
            columnPrefix, \
            startSlice, \
            finishSlice, \
            startColumn, \
            finishColumn, \
            startRow, \
            finishRow, \
            contour in \
                zip(
                    inMasks,
                    inImgs,
                    inOriImgs,
                    columnPrefixs,
                    startSlices,
                    finishSlices,
                    startColumns,
                    finishColumns,
                    startRows,
                    finishRows,
                    contours
                ):
            # load
            if isinstance(inMask, str):
                inMask = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inMask
                ).OriData
            if isinstance(inImg, str):
                refImg = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inImg
                )
                inImg = refImg.OriData
            if isinstance(inOriImg, str):
                inOriImg = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inOriImg
                ).OriData

            # filter data
            if filterThres:
                inImg, inOnes = Image_Process_Functions.FilterData(
                    rangStarts=thresStart,
                    rangStops=thresStp,
                    dataMat=inImg,
                    funType="boundary"
                )
                inMask = numpy.multiply(inMask, inOnes)
                inOriImg, inOnes = Image_Process_Functions.FilterData(
                    rangStarts=thresStart,
                    rangStops=thresStp,
                    dataMat=inOriImg,
                    funType="boundary"
                )

            # get shape
            imgShp = numpy.shape(inImg)
            # slicing direction
            if slicingDirect == "X" or slicingDirect == "x":
                # convert slices
                startSlice, finishSlice = SliceNumberCorrect(
                    sliceStart=startSlice,
                    sliceStop=finishSlice,
                    boundaryStart=0,
                    boundaryStop=imgShp[0],
                )

                # create mask/ contour mask
                if contour:
                    # contour with slices
                    useMaskInit = CreateContourMask(
                        inMask=inMask,
                        sliceStart=startSlice,
                        sliceFinish=finishSlice,
                        multiContour=True,
                        fillValue=False
                    )
                else:
                    useMaskInit = inMask

                # cut region
                useMask = Image_Process_Functions.CutVOI(
                    inArr=useMaskInit,
                    startSlices=[startSlice],
                    finishSlices=[finishSlice],
                    startRows=[startRow],
                    finishRows=[finishRow],
                    startColumns=[startColumn],
                    finishColumns=[finishColumn]
                )

                # Non-zero matching
                useImg = NonZeroBallFill(
                    inImg=inImg,
                    inMask=useMask,
                    ballRadius=ballRadius,
                    imgExcludeValues=0,
                    maskExcludeValues=0
                )
                useOriImg = NonZeroBallFill(
                    inImg=inOriImg,
                    inMask=useMask,
                    ballRadius=ballRadius,
                    imgExcludeValues=0,
                    maskExcludeValues=0
                )

                # save
                if saveDiffImage:
                    imageRatioImg = numpy.divide(
                        (useOriImg - useImg),
                        useOriImg,
                        where=(useOriImg != 0)
                    ) * 100

                    # create directory
                    Save_Load_File.checkCreateDir(outDir)

                    # Set file name
                    valDiffFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'PerDiff',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    valOriFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'BaseImg',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    useMaskFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'useMask',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    valCompareFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'CompareImg',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    useMaskInitFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'useMaskInit',
                        extension=".nii.gz",
                        appendDate=False
                    )

                    # save
                    Save_Load_File.MatNIFTISave(
                        MatData=imageRatioImg,
                        imgPath=valDiffFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useOriImg,
                        imgPath=valOriFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useImg,
                        imgPath=valCompareFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useMask,
                        imgPath=useMaskFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useMaskInit,
                        imgPath=useMaskInitFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )

                # stats
                imgArr = useImg[useMask != 0]
                imgOriArr = useOriImg[useMask != 0]
                print('imgArr', imgArr)
                print('imgOriArr', imgOriArr)
                imgArrRatios = (imgOriArr - imgArr) / imgOriArr * 100
                print('imgOriArr - imgArr', imgOriArr - imgArr)
                print(numpy.min(imgArrRatios))
                print(numpy.nanmin(imgArrRatios))

                # out dictionary str
                outSuff = 'Diff_'

                # absolute value
                if absVal:
                    imgArrRatiosUse = numpy.absolute(imgArrRatios)
                    outSuff += 'abs'
                else:
                    imgArrRatiosUse = imgArrRatios

                # percentile
                imgArrRatiosUse = KeepTwoTailofRange(
                    inArr=imgArrRatiosUse,
                    perntageKeep=percentile
                )
                outSuff += str(percentile)

                # replace 0 in array for special 1/x calculation
                imgArrRatiosUse_0r1 = copy.deepcopy(imgArrRatiosUse)
                imgArrRatiosUse_0r1 = numpy.abs(imgArrRatiosUse_0r1)
                imgArrRatiosUse_0r1[imgArrRatiosUse_0r1 == 0] = 1

                # stats
                if outMin:
                    rtrnInfo["statics"][columnPrefix + '_Min' + '_' + outSuff] = numpy.nanmin(imgArrRatiosUse)
                if outMax:
                    rtrnInfo["statics"][columnPrefix + '_Max' + '_' + outSuff] = numpy.nanmax(imgArrRatiosUse)
                if outPTP:
                    rtrnInfo["statics"][columnPrefix + '_PTP' + '_' + outSuff] = rtrnInfo["statics"][
                        columnPrefix + '_Max' + '_' + outSuff] - rtrnInfo["statics"][
                        columnPrefix + '_Min' + '_' + outSuff]
                if outQ1:
                    rtrnInfo["statics"][columnPrefix + '_Q1' + '_' + outSuff] = numpy.nanpercentile(imgArrRatiosUse, 25)
                if outQ3:
                    rtrnInfo["statics"][columnPrefix + '_Q3' + '_' + outSuff] = numpy.nanpercentile(imgArrRatiosUse, 75)
                if outIQR:
                    rtrnInfo["statics"][columnPrefix + '_IQR' + '_' + outSuff] = rtrnInfo["statics"][
                        columnPrefix + '_Q3' + '_' + outSuff] - rtrnInfo["statics"][
                        columnPrefix + '_Q1' + '_' + outSuff]
                if outMedian:
                    rtrnInfo["statics"][columnPrefix + '_Median' + '_' + outSuff] = numpy.nanmedian(imgArrRatiosUse)
                if outMode:
                    rtrnInfo["statics"][columnPrefix + '_Mode' + '_' + outSuff] = scipy.stats.mode(
                        imgArrRatiosUse, nan_policy='omit')[0][0]
                if outMean:
                    rtrnInfo["statics"][columnPrefix + '_Mean' + '_' + outSuff] = numpy.nanmean(imgArrRatiosUse)
                if outRMS:
                    rtrnInfo["statics"][columnPrefix + '_RMS' + '_' + outSuff] = numpy.sqrt(numpy.nanmean(
                        imgArrRatiosUse ** 2))
                if outHMean:
                    rtrnInfo["statics"][columnPrefix + '_HMean' + '_' + outSuff] = scipy.stats.hmean(
                        imgArrRatiosUse_0r1)
                if outGMean:
                    rtrnInfo["statics"][columnPrefix + '_GMean' + '_' + outSuff] = scipy.stats.gmean(
                        imgArrRatiosUse_0r1)
                if outTriMean:
                    rtrnInfo["statics"][columnPrefix + '_TriMean' + '_' + outSuff] = (numpy.nanpercentile(
                        imgArrRatiosUse, 25) + 2 * numpy.nanpercentile(imgArrRatiosUse, 50) + numpy.nanpercentile(
                        imgArrRatiosUse, 75)) / 4
                if outDecile1:
                    rtrnInfo["statics"][columnPrefix + '_Decile1' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 10)
                if outDecile2:
                    rtrnInfo["statics"][columnPrefix + '_Decile2' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 20)
                if outDecile3:
                    rtrnInfo["statics"][columnPrefix + '_Decile3' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 30)
                if outDecile4:
                    rtrnInfo["statics"][columnPrefix + '_Decile4' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 40)
                if outDecile6:
                    rtrnInfo["statics"][columnPrefix + '_Decile6' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 60)
                if outDecile7:
                    rtrnInfo["statics"][columnPrefix + '_Decile7' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 70)
                if outDecile8:
                    rtrnInfo["statics"][columnPrefix + '_Decile8' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 80)
                if outDecile9:
                    rtrnInfo["statics"][columnPrefix + '_Decile9' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 90)
                if outSTD:
                    rtrnInfo["statics"][columnPrefix + '_STD' + '_' + outSuff] = numpy.nanstd(
                        imgArrRatiosUse, ddof=1)
                if outVar:
                    rtrnInfo["statics"][columnPrefix + '_Variance' + '_' + outSuff] = numpy.nanvar(
                        imgArrRatiosUse, ddof=1)
                if outKurt:
                    rtrnInfo["statics"][columnPrefix + '_Kurtosis' + '_' + outSuff] = scipy.stats.kurtosis(
                        imgArrRatiosUse, nan_policy='omit')
                if outSkew:
                    rtrnInfo["statics"][columnPrefix + '_Skew' + '_' + outSuff] = scipy.stats.skew(
                        imgArrRatiosUse, nan_policy='omit')
                if outSE:
                    rtrnInfo["statics"][columnPrefix + '_SE' + '_' + outSuff] = scipy.stats.sem(
                        imgArrRatiosUse, nan_policy='omit')
                if outEnergy:
                    rtrnInfo["statics"][columnPrefix + '_Energy' + '_' + outSuff] = numpy.nansum(
                        imgArrRatiosUse ** 2)
                if outEntropy:
                    rtrnInfo["statics"][columnPrefix + '_Entropy' + '_' + outSuff] = scipy.stats.entropy(
                        imgArrRatiosUse)

                # 99.5 percentile
                if outPut995:
                    imgArrRatiosPerc995 = KeepTwoTailofRange(
                        inArr=imgArrRatios,
                        perntageKeep=99.5
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPerc995_0r1 = copy.deepcopy(imgArrRatiosPerc995)
                    imgArrRatiosPerc995_0r1 = numpy.abs(imgArrRatiosPerc995_0r1)
                    imgArrRatiosPerc995_0r1[imgArrRatiosPerc995_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_995'] = numpy.nanmin(imgArrRatiosPerc995)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_995'] = numpy.nanmax(imgArrRatiosPerc995)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_995'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_995'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_995']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_995'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_995'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_995']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_995'] = numpy.nanmedian(imgArrRatiosPerc995)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_995'] = scipy.stats.mode(
                            imgArrRatiosPerc995, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_995'] = numpy.nanmean(imgArrRatiosPerc995)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_995'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatiosPerc995 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_995'] = scipy.stats.hmean(
                            imgArrRatiosPerc995_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_995'] = scipy.stats.gmean(
                            imgArrRatiosPerc995_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_995'] = (numpy.nanpercentile(
                            imgArrRatiosPerc995, 25) + 2 * numpy.nanpercentile(
                            imgArrRatiosPerc995, 50) + numpy.nanpercentile(imgArrRatiosPerc995, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_995'] = numpy.nanstd(
                            imgArrRatiosPerc995, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_995'] = numpy.nanvar(
                            imgArrRatiosPerc995, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_995'] = scipy.stats.kurtosis(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_995'] = scipy.stats.skew(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_995'] = scipy.stats.sem(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_995'] = numpy.nansum(
                            imgArrRatiosPerc995 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_995'] = scipy.stats.entropy(
                            imgArrRatiosPerc995)

                # 99 percentile
                if outPut99:
                    imgArrRatiosPerc99 = KeepTwoTailofRange(
                        inArr=imgArrRatios,
                        perntageKeep=99
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPerc99_0r1 = copy.deepcopy(imgArrRatiosPerc99)
                    imgArrRatiosPerc99_0r1 = numpy.abs(imgArrRatiosPerc99_0r1)
                    imgArrRatiosPerc99_0r1[imgArrRatiosPerc99_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_99'] = numpy.nanmin(imgArrRatiosPerc99)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_99'] = numpy.nanmax(imgArrRatiosPerc99)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_99'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_99'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_99']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_99'] = numpy.nanpercentile(imgArrRatiosPerc99, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_99'] = numpy.nanpercentile(imgArrRatiosPerc99, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_99'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_99'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_99']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_99'] = numpy.nanmedian(imgArrRatiosPerc99)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_99'] = scipy.stats.mode(
                            imgArrRatiosPerc99, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_99'] = numpy.nanmean(imgArrRatiosPerc99)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_99'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatiosPerc99 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_99'] = scipy.stats.hmean(
                            imgArrRatiosPerc99_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_99'] = scipy.stats.gmean(
                            imgArrRatiosPerc99_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_99'] = (numpy.nanpercentile(
                            imgArrRatiosPerc99, 25) + 2 * numpy.nanpercentile(
                            imgArrRatiosPerc99, 50) + numpy.nanpercentile(imgArrRatiosPerc99, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_99'] = numpy.nanstd(
                            imgArrRatiosPerc99, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_99'] = numpy.nanvar(
                            imgArrRatiosPerc99, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_99'] = scipy.stats.kurtosis(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_99'] = scipy.stats.skew(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_99'] = scipy.stats.sem(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_99'] = numpy.nansum(
                            imgArrRatiosPerc99 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_99'] = scipy.stats.entropy(
                            imgArrRatiosPerc99)

                # absolute values
                if outPutABS:
                    imgArrRatios_abs = numpy.absolute(imgArrRatios)
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs_0r1 = copy.deepcopy(imgArrRatios_abs)
                    imgArrRatiosPercabs_0r1 = numpy.abs(imgArrRatiosPercabs_0r1)
                    imgArrRatiosPercabs_0r1[imgArrRatiosPercabs_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs'] = numpy.nanmin(imgArrRatios_abs)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs'] = numpy.nanmax(imgArrRatios_abs)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_abs'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs'] = numpy.nanpercentile(imgArrRatios_abs, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs'] = numpy.nanpercentile(imgArrRatios_abs, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_abs'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs'] = numpy.nanmedian(imgArrRatios_abs)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs'] = scipy.stats.mode(
                            imgArrRatios_abs, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs'] = numpy.nanmean(imgArrRatios_abs)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_abs ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs'] = scipy.stats.hmean(
                            imgArrRatiosPercabs_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs'] = scipy.stats.gmean(
                            imgArrRatiosPercabs_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs'] = (numpy.nanpercentile(
                            imgArrRatios_abs, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_abs, 50) + numpy.nanpercentile(imgArrRatios_abs, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs'] = numpy.nanstd(
                            imgArrRatios_abs, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs'] = numpy.nanvar(
                            imgArrRatios_abs, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs'] = scipy.stats.kurtosis(
                            imgArrRatios_abs, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs'] = scipy.stats.skew(
                            imgArrRatios_abs, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs'] = scipy.stats.sem(
                            imgArrRatios_abs, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs'] = numpy.nansum(
                            imgArrRatios_abs ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs'] = scipy.stats.entropy(
                            imgArrRatios_abs)

                # 99.5 percentile abs
                if outPutABS995:
                    imgArrRatios_abs = numpy.absolute(imgArrRatios)
                    imgArrRatios_absPerc995 = KeepTwoTailofRange(
                        inArr=imgArrRatios_abs,
                        perntageKeep=99.5
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs995_0r1 = copy.deepcopy(imgArrRatios_absPerc995)
                    imgArrRatiosPercabs995_0r1 = numpy.abs995(imgArrRatiosPercabs995_0r1)
                    imgArrRatiosPercabs995_0r1[imgArrRatiosPercabs995_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs995'] = numpy.nanmin(imgArrRatios_absPerc995)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs995'] = numpy.nanmax(imgArrRatios_absPerc995)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs995'] = rtrnInfo["statics"][
                            columnPrefix + '_Max_Diff_abs995'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs995']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs995'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_abs995'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs995']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs995'] = numpy.nanmedian(
                            imgArrRatios_absPerc995)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs995'] = scipy.stats.mode(
                            imgArrRatios_absPerc995, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs995'] = numpy.nanmean(imgArrRatios_absPerc995)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs995'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_absPerc995 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs995'] = scipy.stats.hmean(
                            imgArrRatiosPercabs995_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs995'] = scipy.stats.gmean(
                            imgArrRatiosPercabs995_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs995'] = (numpy.nanpercentile(
                            imgArrRatios_absPerc995, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_absPerc995, 50) + numpy.nanpercentile(imgArrRatios_absPerc995, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs995'] = numpy.nanstd(
                            imgArrRatios_absPerc995, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs995'] = numpy.nanvar(
                            imgArrRatios_absPerc995, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs995'] = scipy.stats.kurtosis(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs995'] = scipy.stats.skew(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs995'] = scipy.stats.sem(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs995'] = numpy.nansum(
                            imgArrRatios_absPerc995 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs995'] = scipy.stats.entropy(
                            imgArrRatios_absPerc995)

                # 99 percentile abs
                if outPutABS99:
                    imgArrRatios_abs = numpy.absolute(imgArrRatios)
                    imgArrRatios_absPerc99 = KeepTwoTailofRange(
                        inArr=imgArrRatios_abs,
                        perntageKeep=99
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs99_0r1 = copy.deepcopy(imgArrRatios_absPerc99)
                    imgArrRatiosPercabs99_0r1 = numpy.abs99(imgArrRatiosPercabs99_0r1)
                    imgArrRatiosPercabs99_0r1[imgArrRatiosPercabs99_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs99'] = numpy.nanmin(imgArrRatios_absPerc99)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs99'] = numpy.nanmax(imgArrRatios_absPerc99)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs99'] = rtrnInfo["statics"][
                         columnPrefix + '_Max_Diff_abs99'] - rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs99']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs99'] = rtrnInfo["statics"][
                            columnPrefix + '_Q3_Diff_abs99'] - rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs99']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs99'] = numpy.nanmedian(
                            imgArrRatios_absPerc99)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs99'] = scipy.stats.mode(
                            imgArrRatios_absPerc99, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs99'] = numpy.nanmean(imgArrRatios_absPerc99)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs99'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_absPerc99 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs99'] = scipy.stats.hmean(
                            imgArrRatiosPercabs99_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs99'] = scipy.stats.gmean(
                            imgArrRatiosPercabs99_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs99'] = (numpy.nanpercentile(
                            imgArrRatios_absPerc99, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_absPerc99, 50) + numpy.nanpercentile(imgArrRatios_absPerc99, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs99'] = numpy.nanstd(
                            imgArrRatios_absPerc99, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs99'] = numpy.nanvar(
                            imgArrRatios_absPerc99, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs99'] = scipy.stats.kurtosis(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs99'] = scipy.stats.skew(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs99'] = scipy.stats.sem(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs99'] = numpy.nansum(
                            imgArrRatios_absPerc99 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs99'] = scipy.stats.entropy(
                            imgArrRatios_absPerc99)

    elif noCompare:
        for inMask, \
            inImg, \
            columnPrefix, \
            startSlice, \
            finishSlice, \
            startColumn, \
            finishColumn, \
            startRow, \
            finishRow, \
            contour in \
                zip(
                    inMasks,
                    inImgs,
                    columnPrefixs,
                    startSlices,
                    finishSlices,
                    startColumns,
                    finishColumns,
                    startRows,
                    finishRows,
                    contours
                ):
            # load
            if isinstance(inMask, str):
                inMask = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inMask
                ).OriData
            if isinstance(inImg, str):
                refImg = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=inImg
                )
                inImg = refImg.OriData

            # filter data
            if filterThres:
                inImg, inOnes = Image_Process_Functions.FilterData(
                    rangStarts=thresStart,
                    rangStops=thresStp,
                    dataMat=inImg,
                    funType="boundary"
                )
                inMask = numpy.multiply(inMask, inOnes)

            # get shape
            imgShp = numpy.shape(inImg)
            # slicing direction
            if slicingDirect == "X" or slicingDirect == "x":
                # convert slices
                startSlice, finishSlice = SliceNumberCorrect(
                    sliceStart=startSlice,
                    sliceStop=finishSlice,
                    boundaryStart=0,
                    boundaryStop=imgShp[0],
                )

                # create mask/ contour mask
                if contour:
                    # contour with slices
                    useMaskInit = CreateContourMask(
                        inMask=inMask,
                        sliceStart=startSlice,
                        sliceFinish=finishSlice,
                        multiContour=False,
                        fillValue=False
                    )
                else:
                    useMaskInit = inMask

                # cut region
                useMask = Image_Process_Functions.CutVOI(
                    inArr=useMaskInit,
                    startSlices=[startSlice],
                    finishSlices=[finishSlice],
                    startRows=[startRow],
                    finishRows=[finishRow],
                    startColumns=[startColumn],
                    finishColumns=[finishColumn]
                )

                # Non-zero matching
                useImg = NonZeroBallFill(
                    inImg=inImg,
                    inMask=useMask,
                    ballRadius=ballRadius,
                    imgExcludeValues=0,
                    maskExcludeValues=0
                )

                # save
                if saveDiffImage:
                    # create directory
                    Save_Load_File.checkCreateDir(outDir)

                    # Set file name
                    valCompareFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'MatchImg',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    useMaskFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'useMask',
                        extension=".nii.gz",
                        appendDate=False
                    )
                    useMaskInitFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=caseNameRef + columnPrefix + 'useMaskInit',
                        extension=".nii.gz",
                        appendDate=False
                    )

                    # save
                    Save_Load_File.MatNIFTISave(
                        MatData=useImg,
                        imgPath=valCompareFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useMask,
                        imgPath=useMaskFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=useMaskInit,
                        imgPath=useMaskInitFilePath["CombineName"],
                        imgInfo=refImg.OriImag,
                        ConvertDType=False
                    )

                # stats
                # array
                imgArr = useImg[useMask != 0]
                # print(imgArr)
                # print(numpy.shape(imgArr))

                # out dictionary str
                outSuff = 'Ori_'

                # absolute value
                if absVal:
                    imgArrUse = numpy.absolute(imgArr)
                    outSuff += 'abs'
                else:
                    imgArrUse = imgArr

                # percentile
                imgArrRatiosUse = KeepTwoTailofRange(
                    inArr=imgArrUse,
                    perntageKeep=percentile
                )
                outSuff += str(percentile)

                # replace 0 in array for special 1/x calculation
                imgArrRatiosUse_0r1 = copy.deepcopy(imgArrRatiosUse)
                imgArrRatiosUse_0r1 = numpy.abs(imgArrRatiosUse_0r1)
                imgArrRatiosUse_0r1[imgArrRatiosUse_0r1 == 0] = 1

                # stats
                if outMin:
                    rtrnInfo["statics"][columnPrefix + '_Min' + '_' + outSuff] = numpy.nanmin(imgArrRatiosUse)
                if outMax:
                    rtrnInfo["statics"][columnPrefix + '_Max' + '_' + outSuff] = numpy.nanmax(imgArrRatiosUse)
                if outPTP:
                    rtrnInfo["statics"][columnPrefix + '_PTP' + '_' + outSuff] = rtrnInfo["statics"][
                                                                                     columnPrefix + '_Max' + '_' + outSuff] - \
                                                                                 rtrnInfo["statics"][
                                                                                     columnPrefix + '_Min' + '_' + outSuff]
                if outQ1:
                    rtrnInfo["statics"][columnPrefix + '_Q1' + '_' + outSuff] = numpy.nanpercentile(imgArrRatiosUse, 25)
                if outQ3:
                    rtrnInfo["statics"][columnPrefix + '_Q3' + '_' + outSuff] = numpy.nanpercentile(imgArrRatiosUse, 75)
                if outIQR:
                    rtrnInfo["statics"][columnPrefix + '_IQR' + '_' + outSuff] = rtrnInfo["statics"][
                                                                                     columnPrefix + '_Q3' + '_' + outSuff] - \
                                                                                 rtrnInfo["statics"][
                                                                                     columnPrefix + '_Q1' + '_' + outSuff]
                if outMedian:
                    rtrnInfo["statics"][columnPrefix + '_Median' + '_' + outSuff] = numpy.nanmedian(imgArrRatiosUse)
                if outMode:
                    rtrnInfo["statics"][columnPrefix + '_Mode' + '_' + outSuff] = scipy.stats.mode(
                        imgArrRatiosUse, nan_policy='omit')[0][0]
                if outMean:
                    rtrnInfo["statics"][columnPrefix + '_Mean' + '_' + outSuff] = numpy.nanmean(imgArrRatiosUse)
                if outRMS:
                    rtrnInfo["statics"][columnPrefix + '_RMS' + '_' + outSuff] = numpy.sqrt(numpy.nanmean(
                        imgArrRatiosUse ** 2))
                if outHMean:
                    rtrnInfo["statics"][columnPrefix + '_HMean' + '_' + outSuff] = scipy.stats.hmean(
                        imgArrRatiosUse_0r1)
                if outGMean:
                    rtrnInfo["statics"][columnPrefix + '_GMean' + '_' + outSuff] = scipy.stats.gmean(
                        imgArrRatiosUse_0r1)
                if outTriMean:
                    rtrnInfo["statics"][columnPrefix + '_TriMean' + '_' + outSuff] = (numpy.nanpercentile(
                        imgArrRatiosUse, 25) + 2 * numpy.nanpercentile(imgArrRatiosUse, 50) + numpy.nanpercentile(
                        imgArrRatiosUse, 75)) / 4
                if outDecile1:
                    rtrnInfo["statics"][columnPrefix + '_Decile1' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 10)
                if outDecile2:
                    rtrnInfo["statics"][columnPrefix + '_Decile2' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 20)
                if outDecile3:
                    rtrnInfo["statics"][columnPrefix + '_Decile3' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 30)
                if outDecile4:
                    rtrnInfo["statics"][columnPrefix + '_Decile4' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 40)
                if outDecile6:
                    rtrnInfo["statics"][columnPrefix + '_Decile6' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 60)
                if outDecile7:
                    rtrnInfo["statics"][columnPrefix + '_Decile7' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 70)
                if outDecile8:
                    rtrnInfo["statics"][columnPrefix + '_Decile8' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 80)
                if outDecile9:
                    rtrnInfo["statics"][columnPrefix + '_Decile9' + '_' + outSuff] = numpy.nanpercentile(
                        imgArrRatiosUse, 90)
                if outSTD:
                    rtrnInfo["statics"][columnPrefix + '_STD' + '_' + outSuff] = numpy.nanstd(imgArrRatiosUse, ddof=1)
                if outVar:
                    rtrnInfo["statics"][columnPrefix + '_Variance' + '_' + outSuff] = numpy.nanvar(
                        imgArrRatiosUse, ddof=1)
                if outKurt:
                    rtrnInfo["statics"][columnPrefix + '_Kurtosis' + '_' + outSuff] = scipy.stats.kurtosis(
                        imgArrRatiosUse, nan_policy='omit')
                if outSkew:
                    rtrnInfo["statics"][columnPrefix + '_Skew' + '_' + outSuff] = scipy.stats.skew(
                        imgArrRatiosUse, nan_policy='omit')
                if outSE:
                    rtrnInfo["statics"][columnPrefix + '_SE' + '_' + outSuff] = scipy.stats.sem(
                        imgArrRatiosUse, nan_policy='omit')
                if outEnergy:
                    rtrnInfo["statics"][columnPrefix + '_Energy' + '_' + outSuff] = numpy.nansum(imgArrRatiosUse ** 2)
                if outEntropy:
                    rtrnInfo["statics"][columnPrefix + '_Entropy' + '_' + outSuff] = scipy.stats.entropy(
                        imgArrRatiosUse)

                # 99.5 percentile
                if outPut995:
                    imgArrRatiosPerc995 = KeepTwoTailofRange(
                        inArr=imgArrUse,
                        perntageKeep=99.5
                    )

                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPerc995_0r1 = copy.deepcopy(imgArrRatiosPerc995)
                    imgArrRatiosPerc995_0r1 = numpy.abs(imgArrRatiosPerc995_0r1)
                    imgArrRatiosPerc995_0r1[imgArrRatiosPerc995_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_995'] = numpy.nanmin(imgArrRatiosPerc995)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_995'] = numpy.nanmax(imgArrRatiosPerc995)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_995'] = rtrnInfo["statics"][
                                                                                  columnPrefix + '_Max_Diff_995'] - \
                                                                              rtrnInfo["statics"][
                                                                                  columnPrefix + '_Min_Diff_995']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_995'] = rtrnInfo["statics"][
                                                                                  columnPrefix + '_Q3_Diff_995'] - \
                                                                              rtrnInfo["statics"][
                                                                                  columnPrefix + '_Q1_Diff_995']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_995'] = numpy.nanmedian(imgArrRatiosPerc995)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_995'] = scipy.stats.mode(
                            imgArrRatiosPerc995, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_995'] = numpy.nanmean(imgArrRatiosPerc995)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_995'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatiosPerc995 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_995'] = scipy.stats.hmean(
                            imgArrRatiosPerc995_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_995'] = scipy.stats.gmean(
                            imgArrRatiosPerc995_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_995'] = (numpy.nanpercentile(
                            imgArrRatiosPerc995, 25) + 2 * numpy.nanpercentile(
                            imgArrRatiosPerc995, 50) + numpy.nanpercentile(imgArrRatiosPerc995, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_995'] = numpy.nanpercentile(
                            imgArrRatiosPerc995, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_995'] = numpy.nanstd(
                            imgArrRatiosPerc995, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_995'] = numpy.nanvar(
                            imgArrRatiosPerc995, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_995'] = scipy.stats.kurtosis(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_995'] = scipy.stats.skew(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_995'] = scipy.stats.sem(
                            imgArrRatiosPerc995, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_995'] = numpy.nansum(
                            imgArrRatiosPerc995 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_995'] = scipy.stats.entropy(
                            imgArrRatiosPerc995)

                # 99 percentile
                if outPut99:
                    imgArrRatiosPerc99 = KeepTwoTailofRange(
                        inArr=imgArrUse,
                        perntageKeep=99
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPerc99_0r1 = copy.deepcopy(imgArrRatiosPerc99)
                    imgArrRatiosPerc99_0r1 = numpy.abs(imgArrRatiosPerc99_0r1)
                    imgArrRatiosPerc99_0r1[imgArrRatiosPerc99_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_99'] = numpy.nanmin(imgArrRatiosPerc99)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_99'] = numpy.nanmax(imgArrRatiosPerc99)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_99'] = rtrnInfo["statics"][
                                                                                 columnPrefix + '_Max_Diff_99'] - \
                                                                             rtrnInfo["statics"][
                                                                                 columnPrefix + '_Min_Diff_99']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_99'] = numpy.nanpercentile(imgArrRatiosPerc99, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_99'] = numpy.nanpercentile(imgArrRatiosPerc99, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_99'] = rtrnInfo["statics"][
                                                                                 columnPrefix + '_Q3_Diff_99'] - \
                                                                             rtrnInfo["statics"][
                                                                                 columnPrefix + '_Q1_Diff_99']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_99'] = numpy.nanmedian(imgArrRatiosPerc99)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_99'] = scipy.stats.mode(
                            imgArrRatiosPerc99, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_99'] = numpy.nanmean(imgArrRatiosPerc99)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_99'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatiosPerc99 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_99'] = scipy.stats.hmean(
                            imgArrRatiosPerc99_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_99'] = scipy.stats.gmean(
                            imgArrRatiosPerc99_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_99'] = (numpy.nanpercentile(
                            imgArrRatiosPerc99, 25) + 2 * numpy.nanpercentile(
                            imgArrRatiosPerc99, 50) + numpy.nanpercentile(imgArrRatiosPerc99, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_99'] = numpy.nanpercentile(
                            imgArrRatiosPerc99, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_99'] = numpy.nanstd(
                            imgArrRatiosPerc99, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_99'] = numpy.nanvar(
                            imgArrRatiosPerc99, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_99'] = scipy.stats.kurtosis(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_99'] = scipy.stats.skew(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_99'] = scipy.stats.sem(
                            imgArrRatiosPerc99, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_99'] = numpy.nansum(
                            imgArrRatiosPerc99 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_99'] = scipy.stats.entropy(
                            imgArrRatiosPerc99)

                # absolute values
                if outPutABS:
                    imgArrRatios_abs = numpy.absolute(imgArrUse)
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs_0r1 = copy.deepcopy(imgArrRatios_abs)
                    imgArrRatiosPercabs_0r1 = numpy.abs(imgArrRatiosPercabs_0r1)
                    imgArrRatiosPercabs_0r1[imgArrRatiosPercabs_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs'] = numpy.nanmin(imgArrRatios_abs)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs'] = numpy.nanmax(imgArrRatios_abs)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs'] = rtrnInfo["statics"][
                                                                                  columnPrefix + '_Max_Diff_abs'] - \
                                                                              rtrnInfo["statics"][
                                                                                  columnPrefix + '_Min_Diff_abs']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs'] = numpy.nanpercentile(imgArrRatios_abs, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs'] = numpy.nanpercentile(imgArrRatios_abs, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs'] = rtrnInfo["statics"][
                                                                                  columnPrefix + '_Q3_Diff_abs'] - \
                                                                              rtrnInfo["statics"][
                                                                                  columnPrefix + '_Q1_Diff_abs']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs'] = numpy.nanmedian(imgArrRatios_abs)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs'] = scipy.stats.mode(
                            imgArrRatios_abs, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs'] = numpy.nanmean(imgArrRatios_abs)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_abs ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs'] = scipy.stats.hmean(
                            imgArrRatiosPercabs_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs'] = scipy.stats.gmean(
                            imgArrRatiosPercabs_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs'] = (numpy.nanpercentile(
                            imgArrRatios_abs, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_abs, 50) + numpy.nanpercentile(imgArrRatios_abs, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs'] = numpy.nanpercentile(
                            imgArrRatios_abs, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs'] = numpy.nanstd(
                            imgArrRatios_abs, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs'] = numpy.nanvar(
                            imgArrRatios_abs, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs'] = scipy.stats.kurtosis(
                            imgArrRatios_abs, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs'] = scipy.stats.skew(
                            imgArrRatios_abs, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs'] = scipy.stats.sem(
                            imgArrRatios_abs, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs'] = numpy.nansum(
                            imgArrRatios_abs ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs'] = scipy.stats.entropy(
                            imgArrRatios_abs)

                # 99.5 percentile abs
                if outPutABS995:
                    imgArrRatios_abs = numpy.absolute(imgArrUse)
                    imgArrRatios_absPerc995 = KeepTwoTailofRange(
                        inArr=imgArrRatios_abs,
                        perntageKeep=99.5
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs995_0r1 = copy.deepcopy(imgArrRatios_absPerc995)
                    imgArrRatiosPercabs995_0r1 = numpy.abs995(imgArrRatiosPercabs995_0r1)
                    imgArrRatiosPercabs995_0r1[imgArrRatiosPercabs995_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs995'] = numpy.nanmin(imgArrRatios_absPerc995)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs995'] = numpy.nanmax(imgArrRatios_absPerc995)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs995'] = rtrnInfo["statics"][
                                                                                     columnPrefix + '_Max_Diff_abs995'] - \
                                                                                 rtrnInfo["statics"][
                                                                                     columnPrefix + '_Min_Diff_abs995']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs995'] = rtrnInfo["statics"][
                                                                                     columnPrefix + '_Q3_Diff_abs995'] - \
                                                                                 rtrnInfo["statics"][
                                                                                     columnPrefix + '_Q1_Diff_abs995']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs995'] = numpy.nanmedian(
                            imgArrRatios_absPerc995)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs995'] = scipy.stats.mode(
                            imgArrRatios_absPerc995, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs995'] = numpy.nanmean(imgArrRatios_absPerc995)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs995'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_absPerc995 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs995'] = scipy.stats.hmean(
                            imgArrRatiosPercabs995_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs995'] = scipy.stats.gmean(
                            imgArrRatiosPercabs995_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs995'] = (numpy.nanpercentile(
                            imgArrRatios_absPerc995, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_absPerc995, 50) + numpy.nanpercentile(imgArrRatios_absPerc995, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs995'] = numpy.nanpercentile(
                            imgArrRatios_absPerc995, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs995'] = numpy.nanstd(
                            imgArrRatios_absPerc995, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs995'] = numpy.nanvar(
                            imgArrRatios_absPerc995, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs995'] = scipy.stats.kurtosis(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs995'] = scipy.stats.skew(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs995'] = scipy.stats.sem(
                            imgArrRatios_absPerc995, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs995'] = numpy.nansum(
                            imgArrRatios_absPerc995 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs995'] = scipy.stats.entropy(
                            imgArrRatios_absPerc995)

                # 99 percentile abs
                if outPutABS99:
                    imgArrRatios_abs = numpy.absolute(imgArrUse)
                    imgArrRatios_absPerc99 = KeepTwoTailofRange(
                        inArr=imgArrRatios_abs,
                        perntageKeep=99
                    )
                    # replace 0 in array for special 1/x calculation
                    imgArrRatiosPercabs99_0r1 = copy.deepcopy(imgArrRatios_absPerc99)
                    imgArrRatiosPercabs99_0r1 = numpy.abs99(imgArrRatiosPercabs99_0r1)
                    imgArrRatiosPercabs99_0r1[imgArrRatiosPercabs99_0r1 == 0] = 1
                    # print(imgArrRatiosPerc)
                    # stats
                    if outMin:
                        rtrnInfo["statics"][columnPrefix + '_Min_Diff_abs99'] = numpy.nanmin(imgArrRatios_absPerc99)
                    if outMax:
                        rtrnInfo["statics"][columnPrefix + '_Max_Diff_abs99'] = numpy.nanmax(imgArrRatios_absPerc99)
                    if outPTP:
                        rtrnInfo["statics"][columnPrefix + '_PTP_Diff_abs99'] = rtrnInfo["statics"][
                                                                                    columnPrefix + '_Max_Diff_abs99'] - \
                                                                                rtrnInfo["statics"][
                                                                                    columnPrefix + '_Min_Diff_abs99']
                    if outQ1:
                        rtrnInfo["statics"][columnPrefix + '_Q1_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 25)
                    if outQ3:
                        rtrnInfo["statics"][columnPrefix + '_Q3_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 75)
                    if outIQR:
                        rtrnInfo["statics"][columnPrefix + '_IQR_Diff_abs99'] = rtrnInfo["statics"][
                                                                                    columnPrefix + '_Q3_Diff_abs99'] - \
                                                                                rtrnInfo["statics"][
                                                                                    columnPrefix + '_Q1_Diff_abs99']
                    if outMedian:
                        rtrnInfo["statics"][columnPrefix + '_Median_Diff_abs99'] = numpy.nanmedian(
                            imgArrRatios_absPerc99)
                    if outMode:
                        rtrnInfo["statics"][columnPrefix + '_Mode_Diff_abs99'] = scipy.stats.mode(
                            imgArrRatios_absPerc99, nan_policy='omit')[0][0]
                    if outMean:
                        rtrnInfo["statics"][columnPrefix + '_Mean_Diff_abs99'] = numpy.nanmean(imgArrRatios_absPerc99)
                    if outRMS:
                        rtrnInfo["statics"][columnPrefix + '_RMS_Diff_abs99'] = numpy.sqrt(numpy.nanmean(
                            imgArrRatios_absPerc99 ** 2))
                    if outHMean:
                        rtrnInfo["statics"][columnPrefix + '_HMean_Diff_abs99'] = scipy.stats.hmean(
                            imgArrRatiosPercabs99_0r1)
                    if outGMean:
                        rtrnInfo["statics"][columnPrefix + '_GMean_Diff_abs99'] = scipy.stats.gmean(
                            imgArrRatiosPercabs99_0r1)
                    if outTriMean:
                        rtrnInfo["statics"][columnPrefix + '_TriMean_Diff_abs99'] = (numpy.nanpercentile(
                            imgArrRatios_absPerc99, 25) + 2 * numpy.nanpercentile(
                            imgArrRatios_absPerc99, 50) + numpy.nanpercentile(imgArrRatios_absPerc99, 75)) / 4
                    if outDecile1:
                        rtrnInfo["statics"][columnPrefix + '_Decile1_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 10)
                    if outDecile2:
                        rtrnInfo["statics"][columnPrefix + '_Decile2_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 20)
                    if outDecile3:
                        rtrnInfo["statics"][columnPrefix + '_Decile3_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 30)
                    if outDecile4:
                        rtrnInfo["statics"][columnPrefix + '_Decile4_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 40)
                    if outDecile6:
                        rtrnInfo["statics"][columnPrefix + '_Decile6_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 60)
                    if outDecile7:
                        rtrnInfo["statics"][columnPrefix + '_Decile7_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 70)
                    if outDecile8:
                        rtrnInfo["statics"][columnPrefix + '_Decile8_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 80)
                    if outDecile9:
                        rtrnInfo["statics"][columnPrefix + '_Decile9_Diff_abs99'] = numpy.nanpercentile(
                            imgArrRatios_absPerc99, 90)
                    if outSTD:
                        rtrnInfo["statics"][columnPrefix + '_STD_Diff_abs99'] = numpy.nanstd(
                            imgArrRatios_absPerc99, ddof=1)
                    if outVar:
                        rtrnInfo["statics"][columnPrefix + '_Variance_Diff_abs99'] = numpy.nanvar(
                            imgArrRatios_absPerc99, ddof=1)
                    if outKurt:
                        rtrnInfo["statics"][columnPrefix + '_Kurtosis_Diff_abs99'] = scipy.stats.kurtosis(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outSkew:
                        rtrnInfo["statics"][columnPrefix + '_Skew_Diff_abs99'] = scipy.stats.skew(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outSE:
                        rtrnInfo["statics"][columnPrefix + '_SE_Diff_abs99'] = scipy.stats.sem(
                            imgArrRatios_absPerc99, nan_policy='omit')
                    if outEnergy:
                        rtrnInfo["statics"][columnPrefix + '_Energy_Diff_abs99'] = numpy.nansum(
                            imgArrRatios_absPerc99 ** 2)
                    if outEntropy:
                        rtrnInfo["statics"][columnPrefix + '_Entropy_Diff_abs99'] = scipy.stats.entropy(
                            imgArrRatios_absPerc99)

    # Dataframe
    print(rtrnInfo["statics"])
    print(type(rtrnInfo["statics"]))
    rtrnInfo["dataFrame"] = pandas.DataFrame(rtrnInfo["statics"], index=[index])

    if saveCsv:
        if filterThres:
            # create path
            csvPath = Save_Load_File.DateFileName(
                Dir=outDir,
                fileName=outNameRef + "_3DIF2" + slicingDirect,
                extension=".csv",
                appendDate=False
            )
        else:
            # create path
            csvPath = Save_Load_File.DateFileName(
                Dir=outDir,
                fileName=outNameRef + "_3DIt2" + slicingDirect,
                extension=".csv",
                appendDate=False
            )

        # save
        rtrnInfo["dataFrame"].to_csv(csvPath["CombineName"], index=False)

        print('csvDF: \n{}'.format(csvDF))
        print("Save: \n{}".format(csvPath["CombineName"]))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------3D intensity points stats calculation time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: keep two-tail range (e.g 99.5% of data)
##############################################################################
"""
import sys
import copy


def KeepTwoTailofRange(
        inArr,
        perntageKeep
):
    if perntageKeep < 0 or perntageKeep > 100:
        raise ValueError("Inpurt percentile 0<x=<100")

    # up/low bound
    tailPer = (100 - perntageKeep) / 2
    upB = perntageKeep + tailPer
    lowB = tailPer

    # array remove infinite and nan
    inArrWork = copy.deepcopy(inArr)
    inArrWork = inArrWork[~numpy.isnan(inArrWork)]  # remove nan
    inArrWork = inArrWork[numpy.isfinite(inArrWork)]  # remove infinite

    # empty array raise error
    if inArr.size == 0:
        raise ValueError("Inpurt array are all infinity or nan!!! \n", inArr)

    # get percentile values
    [lowBVal, upBVal] = numpy.nanpercentile(inArrWork, [lowB, upB])

    # out array filter
    outArr = inArrWork[numpy.where(numpy.logical_and(inArrWork >= lowBVal, inArrWork <= upBVal))]
    # print full
    # numpy.set_printoptions(threshold=sys.maxsize)
    print('Upper bound: {} & lower bound: {} '
          '\nArray contain Nan numbers: {} and infinity: {} '
          '\nSize reduction from {} to {}'.format(
        upBVal,
        lowBVal,
        numpy.sum(numpy.isnan(inArr)),
        numpy.sum(~numpy.isfinite(inArr)),
        numpy.shape(inArr),
        numpy.shape(outArr)
    )
    )

    return outArr


"""
##############################################################################
#Func: Extract intensity stats from input lists
##############################################################################
"""
import numpy
import time
import scipy.stats
import pandas


def StatsLists(
        inLsts,
        saveCsv,
        outDir,
        outNameRef,
        refSlices=None,
        outRefName=""
):
    # init
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ''
    rtrnInfo["statics"] = {}

    # same shape
    if refSlices is not None \
            and len(inLsts) != len(refSlices):
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += "Input not the same size!"
        print("Error: {}".format(rtrnInfo["errorMessage"]))
        return rtrnInfo

    # get shape
    SliceLen = len(inLsts)
    # initialising array
    slices = numpy.ones([SliceLen, 1]) * -1
    nanmin = numpy.zeros([SliceLen, 1])
    nanmax = numpy.zeros([SliceLen, 1])
    ptp = numpy.zeros([SliceLen, 1])
    Q1 = numpy.zeros([SliceLen, 1])
    Q3 = numpy.zeros([SliceLen, 1])
    IQR = numpy.zeros([SliceLen, 1])
    nanmedian = numpy.zeros([SliceLen, 1])
    nanmean = numpy.zeros([SliceLen, 1])
    nanstd = numpy.zeros([SliceLen, 1])
    nanvar = numpy.zeros([SliceLen, 1])
    kurtosis = numpy.zeros([SliceLen, 1])
    skew = numpy.zeros([SliceLen, 1])

    # loop trhough slices
    for i in range(SliceLen):
        # image
        listArr = inLsts[i]

        # jump
        if listArr.size == 0:
            continue
        else:
            # stats
            slices[i] = refSlices[i]
            nanmin[i] = numpy.nanmin(listArr)
            nanmax[i] = numpy.nanmax(listArr)
            ptp[i] = nanmax[i] - nanmin[i]
            Q1[i] = numpy.nanpercentile(listArr, 25)
            Q3[i] = numpy.nanpercentile(listArr, 75)
            IQR[i] = Q3[i] - Q1[i]
            nanmedian[i] = numpy.nanmedian(listArr)
            nanmean[i] = numpy.nanmean(listArr)
            nanstd[i] = numpy.nanstd(listArr, ddof=1)
            nanvar[i] = numpy.nanvar(listArr, ddof=1)
            kurtosis[i] = scipy.stats.kurtosis(listArr, nan_policy='omit')
            skew[i] = scipy.stats.skew(listArr, nan_policy='omit')

    # reforming array
    slicesOut = slices[slices > -1] + 1  # image start from "1" numpy slice from "0"
    nanmin = nanmin[slices > -1]
    nanmax = nanmax[slices > -1]
    ptp = ptp[slices > -1]
    Q1 = Q1[slices > -1]
    Q3 = Q3[slices > -1]
    IQR = IQR[slices > -1]
    nanmedian = nanmedian[slices > -1]
    nanmean = nanmean[slices > -1]
    nanstd = nanstd[slices > -1]
    nanvar = nanvar[slices > -1]
    kurtosis = kurtosis[slices > -1]
    skew = skew[slices > -1]

    # statics
    rtrnInfo["statics"] = {
        outRefName + "_slices": slicesOut,
        outRefName + "_nanmin": nanmin,
        outRefName + "_nanmax": nanmax,
        outRefName + "_ptp": ptp,
        outRefName + "_Q1": Q1,
        outRefName + "_Q3": Q3,
        outRefName + "_IQR": IQR,
        outRefName + "_nanmedian": nanmedian,
        outRefName + "_nanmean": nanmean,
        outRefName + "_nanstd": nanstd,
        outRefName + "_nanvar": nanvar,
        outRefName + "_kurtosis": kurtosis,
        outRefName + "_skew": skew
    }

    if saveCsv:
        # create path
        csvPath = Save_Load_File.DateFileName(
            Dir=outDir,
            fileName=outNameRef + "_Stat",
            extension=".csv",
            appendDate=False
        )

        # dataframe save csv
        csvDF = pandas.DataFrame.from_dict(rtrnInfo["statics"])
        # save
        csvDF.to_csv(csvPath["CombineName"], index=False)

        print('csvDF: \n{}'.format(csvDF))
        print("Save: \n{}".format(csvPath["CombineName"]))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------List intensity stats calculation time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: Extract shape stats of image 3D (2D)
##############################################################################
"""
import numpy
import time
import skimage.measure
import pandas


def VolumeStats3DImgSlice(
        inMask,
        slicingDirect,
        saveCsv,
        outDir,
        outNameRef,
        outRefName=""
):
    # init
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ''
    rtrnInfo["statics"] = {}

    # 3D data
    comapare3D = Post_Image_Process_Functions.CompareArrayDimension(
        dataMat=inMask,
        shapeD=3
    )
    if comapare3D["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += comapare3D["errorMessage"]
        print("Error: {}".format(rtrnInfo["errorMessage"]))
        return rtrnInfo

    # get shape
    imgShp = numpy.shape(inMask)
    # slicing direction
    if slicingDirect == "X" or slicingDirect == "x":
        # initialising array
        slicingDirect = "X"
        slices = numpy.ones([imgShp[0], 1]) * -1
        area = numpy.zeros([imgShp[0], 1])
        centroid_row = numpy.zeros([imgShp[0], 1])
        centroid_column = numpy.zeros([imgShp[0], 1])
        convex_area = numpy.zeros([imgShp[0], 1])
        eccentricity = numpy.zeros([imgShp[0], 1])
        equivalent_diameter = numpy.zeros([imgShp[0], 1])
        euler_number = numpy.zeros([imgShp[0], 1])
        extent = numpy.zeros([imgShp[0], 1])
        feret_diameter_max = numpy.zeros([imgShp[0], 1])
        filled_area = numpy.zeros([imgShp[0], 1])
        major_axis_length = numpy.zeros([imgShp[0], 1])
        minor_axis_length = numpy.zeros([imgShp[0], 1])
        orientation = numpy.zeros([imgShp[0], 1])
        perimeter = numpy.zeros([imgShp[0], 1])
        perimeter_crofton = numpy.zeros([imgShp[0], 1])
        solidity = numpy.zeros([imgShp[0], 1])

        # loop trhough slices
        for i in range(imgShp[0]):
            # image
            mask = (inMask[i] != 0) * 1

            # jump
            if numpy.sum(mask) == 0:
                continue
            else:
                # label slice
                labels, nums = skimage.measure.label(mask, return_num=True)

                # region props for information
                # !!! list start from 0 label start from 1!!!
                regions = skimage.measure.regionprops(labels)

                # stats
                slices[i] = i
                ## single label return everything
                if nums == 1:
                    bubble = regions[0]

                    area[i] = bubble.area
                    centroid_row[i] = bubble.centroid[0]
                    centroid_column[i] = bubble.centroid[1]
                    convex_area[i] = bubble.convex_area
                    eccentricity[i] = bubble.eccentricity
                    equivalent_diameter[i] = bubble.equivalent_diameter
                    euler_number[i] = bubble.euler_number
                    extent[i] = bubble.extent
                    feret_diameter_max[i] = bubble.feret_diameter_max
                    filled_area[i] = bubble.filled_area
                    major_axis_length[i] = bubble.major_axis_length
                    minor_axis_length[i] = bubble.minor_axis_length
                    orientation[i] = bubble.orientation
                    perimeter[i] = bubble.perimeter
                    perimeter_crofton[i] = bubble.perimeter_crofton
                    solidity[i] = bubble.solidity
                else:
                    # addtion for area and perimeter
                    for num in range(nums):
                        # region bubble
                        bubble = regions[num]

                        area[i] += bubble.area
                        perimeter[i] += bubble.perimeter

    elif slicingDirect == "Y" or slicingDirect == "y":
        # initialising array
        slicingDirect = "Y"
        slices = numpy.ones([imgShp[1], 1]) * -1
        area = numpy.zeros([imgShp[1], 1])
        centroid_row = numpy.zeros([imgShp[1], 1])
        centroid_column = numpy.zeros([imgShp[1], 1])
        convex_area = numpy.zeros([imgShp[1], 1])
        eccentricity = numpy.zeros([imgShp[1], 1])
        equivalent_diameter = numpy.zeros([imgShp[1], 1])
        euler_number = numpy.zeros([imgShp[1], 1])
        extent = numpy.zeros([imgShp[1], 1])
        feret_diameter_max = numpy.zeros([imgShp[1], 1])
        filled_area = numpy.zeros([imgShp[1], 1])
        major_axis_length = numpy.zeros([imgShp[1], 1])
        minor_axis_length = numpy.zeros([imgShp[1], 1])
        orientation = numpy.zeros([imgShp[1], 1])
        perimeter = numpy.zeros([imgShp[1], 1])
        perimeter_crofton = numpy.zeros([imgShp[1], 1])
        solidity = numpy.zeros([imgShp[1], 1])

        # loop trhough slices
        for i in range(imgShp[1]):
            # image
            mask = (inMask[:, i, :] != 0) * 1

            # jump
            if numpy.sum(mask) == 0:
                continue
            else:
                # label slice
                labels, nums = skimage.measure.label(mask, return_num=True)

                # region props for information
                # !!! list start from 0 label start from 1!!!
                regions = skimage.measure.regionprops(labels)

                # stats
                slices[i] = i
                ## single label return everything
                if nums == 1:
                    bubble = regions[0]

                    area[i] = bubble.area
                    centroid_row[i] = bubble.centroid[0]
                    centroid_column[i] = bubble.centroid[1]
                    convex_area[i] = bubble.convex_area
                    eccentricity[i] = bubble.eccentricity
                    equivalent_diameter[i] = bubble.equivalent_diameter
                    euler_number[i] = bubble.euler_number
                    extent[i] = bubble.extent
                    feret_diameter_max[i] = bubble.feret_diameter_max
                    filled_area[i] = bubble.filled_area
                    major_axis_length[i] = bubble.major_axis_length
                    minor_axis_length[i] = bubble.minor_axis_length
                    orientation[i] = bubble.orientation
                    perimeter[i] = bubble.perimeter
                    perimeter_crofton[i] = bubble.perimeter_crofton
                    solidity[i] = bubble.solidity
                else:
                    # addtion for area and perimeter
                    for num in range(nums):
                        # region bubble
                        bubble = regions[num]

                        area[i] += bubble.area
                        perimeter[i] += bubble.perimeter

    elif slicingDirect == "Z" or slicingDirect == "z":
        # initialising array
        slicingDirect = "Z"
        slices = numpy.ones([imgShp[2], 1]) * -1
        area = numpy.zeros([imgShp[2], 1])
        centroid_row = numpy.zeros([imgShp[2], 1])
        centroid_column = numpy.zeros([imgShp[2], 1])
        convex_area = numpy.zeros([imgShp[2], 1])
        eccentricity = numpy.zeros([imgShp[2], 1])
        equivalent_diameter = numpy.zeros([imgShp[2], 1])
        euler_number = numpy.zeros([imgShp[2], 1])
        extent = numpy.zeros([imgShp[2], 1])
        feret_diameter_max = numpy.zeros([imgShp[2], 1])
        filled_area = numpy.zeros([imgShp[2], 1])
        major_axis_length = numpy.zeros([imgShp[2], 1])
        minor_axis_length = numpy.zeros([imgShp[2], 1])
        orientation = numpy.zeros([imgShp[2], 1])
        perimeter = numpy.zeros([imgShp[2], 1])
        perimeter_crofton = numpy.zeros([imgShp[2], 1])
        solidity = numpy.zeros([imgShp[2], 1])

        # loop trhough slices
        for i in range(imgShp[2]):
            # image
            mask = (inMask[:, :, i] != 0) * 1

            # jump
            if numpy.sum(mask) == 0:
                continue
            else:
                # label slice
                labels, nums = skimage.measure.label(mask, return_num=True)

                # region props for information
                # !!! list start from 0 label start from 1!!!
                regions = skimage.measure.regionprops(labels)

                # stats
                slices[i] = i
                ## single label return everything
                if nums == 1:
                    bubble = regions[0]

                    area[i] = bubble.area
                    centroid_row[i] = bubble.centroid[0]
                    centroid_column[i] = bubble.centroid[1]
                    convex_area[i] = bubble.convex_area
                    eccentricity[i] = bubble.eccentricity
                    equivalent_diameter[i] = bubble.equivalent_diameter
                    euler_number[i] = bubble.euler_number
                    extent[i] = bubble.extent
                    feret_diameter_max[i] = bubble.feret_diameter_max
                    filled_area[i] = bubble.filled_area
                    major_axis_length[i] = bubble.major_axis_length
                    minor_axis_length[i] = bubble.minor_axis_length
                    orientation[i] = bubble.orientation
                    perimeter[i] = bubble.perimeter
                    perimeter_crofton[i] = bubble.perimeter_crofton
                    solidity[i] = bubble.solidity
                else:
                    # addtion for area and perimeter
                    for num in range(nums):
                        # region bubble
                        bubble = regions[num]

                        area[i] += bubble.area
                        perimeter[i] += bubble.perimeter

    else:
        compareArr["error"] = True
        rtrnInfo["errorMessage"] += "Slicing direction unkonwn: {}".format(slicingDirect)
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    # reforming array
    slicesOut = slices[slices > -1] + 1  # image start from "1" numpy slice from "0"
    area = area[slices > -1]
    centroid_row = centroid_row[slices > -1]
    centroid_column = centroid_column[slices > -1]
    convex_area = convex_area[slices > -1]
    eccentricity = eccentricity[slices > -1]
    equivalent_diameter = equivalent_diameter[slices > -1]
    euler_number = euler_number[slices > -1]
    extent = extent[slices > -1]
    feret_diameter_max = feret_diameter_max[slices > -1]
    filled_area = filled_area[slices > -1]
    major_axis_length = major_axis_length[slices > -1]
    minor_axis_length = minor_axis_length[slices > -1]
    orientation = orientation[slices > -1]
    perimeter = perimeter[slices > -1]
    perimeter_crofton = perimeter_crofton[slices > -1]
    solidity = solidity[slices > -1]

    # statics
    rtrnInfo["statics"] = {
        outRefName + "_slices": slicesOut,
        outRefName + "_area": area,
        outRefName + "_centroid_row": centroid_row,
        outRefName + "_centroid_column": centroid_column,
        outRefName + "_convex_area": convex_area,
        outRefName + "_eccentricity": eccentricity,
        outRefName + "_equivalent_diameter": equivalent_diameter,
        outRefName + "_euler_number": euler_number,
        outRefName + "_extent": extent,
        outRefName + "_feret_diameter_max": feret_diameter_max,
        outRefName + "_filled_area": filled_area,
        outRefName + "_major_axis_length": major_axis_length,
        outRefName + "_minor_axis_length": minor_axis_length,
        outRefName + "_orientation": orientation,
        outRefName + "_perimeter": perimeter,
        outRefName + "_perimeter_crofton": perimeter_crofton,
        outRefName + "_solidity": solidity
    }

    if saveCsv:
        # create path
        csvPath = Save_Load_File.DateFileName(
            Dir=outDir,
            fileName=outNameRef + "_Sp2" + slicingDirect,
            extension=".csv",
            appendDate=False
        )

        # dataframe save csv
        csvDF = pandas.DataFrame.from_dict(rtrnInfo["statics"])
        # save
        csvDF.to_csv(csvPath["CombineName"], index=False)

        print('csvDF: \n{}'.format(csvDF))
        print("Save: \n{}".format(csvPath["CombineName"]))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------2D shape stats calculation time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: Extract point value
##############################################################################
"""


def ExtractPointValue(
        positionDepths,
        positionRows,
        positionColumns,
        positionDepthsSecond,
        positionRowsSecond,
        positionColumnsSecond,
        inFiles,
        columnPrefixs,
        caseNameRef,
        index=0,
        saveCSV=False,
        outDir="",
        outNameRef=""
):
    # init
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ''
    rtrnInfo["dataFrame"] = None
    rtrnInfo["statics"] = {}
    rtrnInfo["statics"]['Ref'] = caseNameRef

    # check positions are not list
    if isinstance(positionDepths, list):
        positionDepthLst = positionDepths
    elif isinstance(positionDepths, int):
        positionDepthLst = [positionDepths] * len(inFiles)
    else:
        try:
            positionDepthLst = [int(positionDepths)] * len(inFiles)
        except:
            raise ValueError("Cannot convert input: {} to integer!".format(positionDepths))

    # check positions are not list
    if isinstance(positionRows, list):
        positionRowLst = positionRows
    elif isinstance(positionRows, int):
        positionRowLst = [positionRows] * len(inFiles)
    else:
        try:
            positionRowLst = [int(positionRows)] * len(inFiles)
        except:
            raise ValueError("Cannot convert input: {} to integer!".format(positionRows))

    # check positions are not list
    if isinstance(positionColumns, list):
        positionColumnLst = positionColumns
    elif isinstance(positionColumns, int):
        positionColumnLst = [positionColumns] * len(inFiles)
    else:
        try:
            positionColumnLst = [int(positionColumns)] * len(inFiles)
        except:
            raise ValueError("Cannot convert input: {} to integer!".format(positionColumns))

    # SECONDARY
    # check positions are not list
    if isinstance(positionDepthsSecond, list):
        positionDepthSecondLst = positionDepthsSecond
    elif isinstance(positionDepthsSecond, int):
        positionDepthSecondLst = [positionDepthsSecond] * len(inFiles)
    else:
        try:
            positionDepthSecondLst = [int(positionDepthsSecond)] * len(inFiles)
        except:
            raise ValueError("Cannot convert input: {} to integer!".format(positionDepths))

    # check positions are not list
    if isinstance(positionRowsSecond, list):
        positionRowSecondLst = positionRowsSecond
    elif isinstance(positionRowsSecond, int):
        positionRowSecondLst = [positionRowsSecond] * len(inFiles)
    else:
        try:
            positionRowSecondLst = [int(positionRowsSecond)] * len(inFiles)
        except:
            raise ValueError("Cannot convert input: {} to integer!".format(positionRows))

    # check positions are not list
    if isinstance(positionColumnsSecond, list):
        positionColumnSecondLst = positionColumnsSecond
    elif isinstance(positionColumnsSecond, int):
        positionColumnSecondLst = [positionColumnsSecond] * len(inFiles)
    else:
        try:
            positionColumnSecondLst = [int(positionColumnsSecond)] * len(inFiles)
        except:
            raise ValueError("Cannot convert input: {} to integer!".format(positionColumns))

    for i in range(len(inFiles)):
        # load data
        case = inFiles[i]
        if isinstance(case, str):
            inArr = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=case
            ).OriData
        elif isinstance(case, numpy.ndarray):
            inArr = case
        else:
            raise ValueError("Cannot load: {}".format(case))

        print(numpy.shape(inArr))

        # store
        val = inArr[
            positionDepthLst[i],
            positionRowLst[i],
            positionColumnLst[i]
        ]
        if val == 0:  # no value point
            val = inArr[
                positionDepthSecondLst[i],
                positionRowSecondLst[i],
                positionColumnSecondLst[i]
            ]
            print("Encounter 0 value point：{}, {}, {}".format(positionDepthLst[i],
                                                              positionRowLst[i],
                                                              positionColumnLst[i]))
            print("Replace with value: {} point：{}, {}, {}".format(val,
                                                                   positionDepthSecondLst[i],
                                                                   positionRowSecondLst[i],
                                                                   positionColumnSecondLst[i]))

        rtrnInfo["statics"][columnPrefixs[i]] = val

    # convert data frame
    print(rtrnInfo["statics"])
    rtrnInfo["dataFrame"] = pandas.DataFrame(rtrnInfo["statics"], index=[index])

    # save csv
    if saveCSV:
        # create path
        csvPath = Save_Load_File.DateFileName(
            Dir=outDir,
            fileName=outNameRef + "_PointValue" + slicingDirect,
            extension=".csv",
            appendDate=False
        )

        # save
        rtrnInfo["dataFrame"].to_csv(csvPath["CombineName"], index=False)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------3D point extraction time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: Redistribution
##############################################################################
"""


def RedistributionLst(
        lst,
        exponent,
        totalValue
):
    # array
    inArr = numpy.array(lst)

    # exponent
    inArrExp = inArr ** exponent

    # k
    k = totalValue / numpy.sum(inArrExp)

    # output array
    outArr = inArrExp * k

    msg = 'Calcs Expo: ' + \
          'inArr: {} '.format(inArr) + \
          'inArrExp: {} '.format(inArrExp) + \
          'k: {} '.format(k) + \
          'outArr: {} '.format(outArr)
    print(msg)

    return outArr


"""
##############################################################################
# Func: Flow conservation calculation
##############################################################################
"""
import copy


def ScanConservationLst(
        arrLst,
        exponent,
        targetSum,
        targetRatio,
        totalValue,
        stepSize,
        areaChoices
):
    # create empty list
    arrLstLen = len(arrLst)
    overallAreaLst = []
    overallValDivideLst = []
    overallRatioLst = []
    satisfyRatioLst = []
    satisfyAreaLst = []
    satisfyValDivideLst = []
    legnthLst = [None] * arrLstLen

    # loop each array
    maxLength = 0
    for i in range(arrLstLen):
        length = numpy.shape(arrLst[i])[0]
        legnthLst[i] = length
        if maxLength < length:
            maxLength = length

    # loop for area
    # area arr
    areaLst = numpy.zeros(arrLstLen)

    for j in range(0, maxLength, stepSize):

        # each arr
        for case in range(arrLstLen):
            # start from 0
            startSlc = 0
            ## dealing out of the range
            # if j > legnthLst[case]:
            #     print("Encounter out of range slicestart!")
            #     continue
            # else:
            #     startSlc = j

            if (j + stepSize) > legnthLst[case]:
                stopSlc = legnthLst[case]
            else:
                stopSlc = j + stepSize

            # average area
            areaLst[case] = Post_Image_Process_Functions.AverageArea(
                inData=arrLst[case][startSlc:stopSlc],
                thres=0
            )[areaChoices[case]]

        # check target
        arrRatio = abs(1 - numpy.sum(areaLst ** exponent / targetSum ** exponent))

        # append overall
        overallRatioLst.append(arrRatio)
        overallAreaLst.append(areaLst)

        # flow distribution
        valDistribute = RedistributionLst(
            lst=areaLst,
            exponent=exponent,
            totalValue=totalValue
        )

        overallValDivideLst.append(valDistribute)

        if arrRatio <= targetRatio:
            areaLstSatisfy = copy.deepcopy(areaLst)
            satisfyAreaLst.append(areaLstSatisfy)
            satisfyRatioLst.append(arrRatio)
            satisfyValDivideLst.append(valDistribute)

            msg = 'Find case smaller than target: ' + \
                  'satisfyRatioLst: {} '.format(satisfyRatioLst) + \
                  'areaLst: {} '.format(areaLst) + \
                  'satisfyValDivideLst: {} '.format(satisfyValDivideLst) + \
                  'satisfyAreaLst: {} '.format(satisfyAreaLst)
            print(msg)

    # output
    if len(satisfyValDivideLst) != 0:
        indexMin = numpy.argmin(satisfyRatioLst)
        outAreaLst = satisfyAreaLst[indexMin]
        outValDivide = satisfyValDivideLst[indexMin]
        findRatio = satisfyRatioLst[indexMin]
        print("ScanConservationLst: Find slices for Flow Conservation!")
    else:
        if len(overallValDivideLst) != 0:
            # get minimum
            indexMin = numpy.argmin(overallRatioLst)
            outAreaLst = overallAreaLst[indexMin]
            outValDivide = overallValDivideLst[indexMin]
            findRatio = overallRatioLst[indexMin]
            print("ScanConservationLst: NOT Find slices for flow conservation!")
        else:
            raise ValueError("ScanConservationLst: No Area Calculated!!!")

    msg = 'Output: ' + \
          'outAreaLst: {} '.format(outAreaLst) + \
          'outValDivide: {} '.format(outValDivide) + \
          'findRatio: {} '.format(findRatio)
    print(msg)

    return outAreaLst, outValDivide, findRatio


"""
##############################################################################
# Func: get list of index from list
##############################################################################
"""


def ListIndex(lst, matchElement):
    indices = [i for i, x in enumerate(lst) if x == matchElement]

    return indices


"""
##############################################################################
# Func: get list of element in list from list of indecies
##############################################################################
"""


def GetElementList(lst, indices):
    # using list comprehension to
    # elements from list
    res_list = [lst[i] for i in indices]

    return res_list


"""
##############################################################################
# Func: convert list of string to something else
##############################################################################
"""


def ConvertListType(lst, type):
    results = list(map(type, lst))

    return results


"""
##############################################################################
# Func: list/array first order statistics without None
##############################################################################
"""

import copy


def LstArrStats(
        ArrLst,
        refStr=""
):
    # init
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = ""
    rtrnInfo["message"] = ""
    rtrnInfo["statics"] = {}

    # remove nan and inf
    arrLst = KeepTwoTailofRange(
        inArr=ArrLst,
        perntageKeep=100
    )

    # replace 0 in array for special 1/x calculation
    arrLst_0r1 = copy.deepcopy(arrLst)
    arrLst_0r1 = numpy.abs(arrLst_0r1)
    arrLst_0r1[arrLst_0r1 == 0] = 1

    # stats
    # spread
    rtrnInfo["statics"][refStr + '_Min'] = numpy.nanmin(arrLst)
    rtrnInfo["statics"][refStr + '_Max'] = numpy.nanmax(arrLst)
    rtrnInfo["statics"][refStr + '_PTP'] = rtrnInfo["statics"][refStr + '_Max'] - rtrnInfo["statics"][refStr + '_Min']
    rtrnInfo["statics"][refStr + '_Q1'] = numpy.nanpercentile(arrLst, 25)
    rtrnInfo["statics"][refStr + '_Q3'] = numpy.nanpercentile(arrLst, 75)
    rtrnInfo["statics"][refStr + '_IQR'] = numpy.abs(rtrnInfo["statics"][refStr + '_Q3']
                                                     - rtrnInfo["statics"][refStr + '_Q1'])
    rtrnInfo["statics"][refStr + '_Median'] = numpy.nanmedian(arrLst)
    rtrnInfo["statics"][refStr + '_Mode'] = scipy.stats.mode(arrLst, nan_policy='omit')[0][0]
    rtrnInfo["statics"][refStr + '_Mean'] = numpy.nanmean(arrLst)
    rtrnInfo["statics"][refStr + '_RMS'] = numpy.sqrt(numpy.nanmean(arrLst ** 2))
    # rtrnInfo["statics"][refStr + '_HMean'] = scipy.stats.hmean(arrLst_0r1, nan_policy='omit')
    rtrnInfo["statics"][refStr + '_HMean'] = scipy.stats.hmean(arrLst_0r1)
    # rtrnInfo["statics"][refStr + '_GMean'] = scipy.stats.gmean(arrLst_0r1, nan_policy='omit')
    rtrnInfo["statics"][refStr + '_GMean'] = scipy.stats.gmean(arrLst_0r1)
    rtrnInfo["statics"][refStr + '_TriMean'] = (numpy.nanpercentile(arrLst, 25)
                                                + 2 * numpy.nanpercentile(arrLst, 50)
                                                + numpy.nanpercentile(arrLst, 75))/4
    rtrnInfo["statics"][refStr + '_Decile1'] = numpy.nanpercentile(arrLst, 10)
    rtrnInfo["statics"][refStr + '_Decile2'] = numpy.nanpercentile(arrLst, 20)
    rtrnInfo["statics"][refStr + '_Decile3'] = numpy.nanpercentile(arrLst, 30)
    rtrnInfo["statics"][refStr + '_Decile4'] = numpy.nanpercentile(arrLst, 40)
    rtrnInfo["statics"][refStr + '_Decile5'] = numpy.nanpercentile(arrLst, 50)
    rtrnInfo["statics"][refStr + '_Decile6'] = numpy.nanpercentile(arrLst, 60)
    rtrnInfo["statics"][refStr + '_Decile7'] = numpy.nanpercentile(arrLst, 70)
    rtrnInfo["statics"][refStr + '_Decile8'] = numpy.nanpercentile(arrLst, 80)
    rtrnInfo["statics"][refStr + '_Decile9'] = numpy.nanpercentile(arrLst, 90)

    # distribution
    rtrnInfo["statics"][refStr + '_STD'] = numpy.nanstd(arrLst, ddof=1)
    rtrnInfo["statics"][refStr + '_Variance'] = numpy.nanvar(arrLst, ddof=1)
    rtrnInfo["statics"][refStr + '_Kurtosis'] = scipy.stats.kurtosis(arrLst, nan_policy='omit')
    rtrnInfo["statics"][refStr + '_Skew'] = scipy.stats.skew(arrLst, nan_policy='omit')
    rtrnInfo["statics"][refStr + '_SE'] = scipy.stats.sem(arrLst, nan_policy='omit')

    # diversity
    rtrnInfo["statics"][refStr + '_Energy'] = numpy.nansum(arrLst ** 2)
    rtrnInfo["statics"][refStr + '_Entropy'] = scipy.stats.entropy(arrLst)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Lst/Arr stats calculation time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo

"""
##############################################################################
# Func: merge dictionary lists 
##############################################################################
"""

def MergeDictionaries(DictLst):

    outDict = {}

    for dict in DictLst:
        # same key keep values in list
        for key, value in dict.items():
            if key in outDict:
                if isinstance(outDict[key], list):
                    dict[key] = outDict[key].append(value)
                else:
                    dict[key] = [outDict[key], value]

        # append the rest
        outDict = {**outDict, **dict}

    return outDict

"""
##############################################################################
# Func: curvature calculation
##############################################################################
"""

import numpy

def CurvatureRelated3D(
        coordinates
):
    # init
    # https://en.wikipedia.org/wiki/Curvature
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = ""
    rtrnInfo["message"] = ""
    rtrnInfo["curvature"] = None
    rtrnInfo["speed"] = None
    rtrnInfo["velocity"] = None
    rtrnInfo["arcLength"] = None
    rtrnInfo["arcLengthTotal"] = None

    # flip
    coorShape = numpy.shape(coordinates)
    if coorShape[0] == 3:
        coordinates = numpy.transpose(coordinates)
        coorShape = numpy.shape(coordinates)

    elif coorShape[1] != 3: # not satisfied
        raise IOError("Input is not 3D coordinate shape: {}".format(coorShape))

    # curve vector
    arcVector = coordinates[:-1] - coordinates[1:]

    # change in tangent vector
    arcTangentChange = AngleActueMatrix(v1=arcVector[:-1], v2=arcVector[1:])
    rtrnInfo["arcTangentChange"] = numpy.concatenate([[0], AngleActueMatrix(v1=arcVector[:-1], v2=arcVector[1:]), [0]])

    # arclength
    rtrnInfo["arcLength"] = numpy.concatenate([[0], numpy.linalg.norm(arcVector, axis=1)])
    rtrnInfo["arcLengthTotal"] = numpy.sum(rtrnInfo["arcLength"])

    # speed
    x_t = numpy.gradient(coordinates[:, 0])
    y_t = numpy.gradient(coordinates[:, 1])
    z_t = numpy.gradient(coordinates[:, 2])

    rtrnInfo["velocity"] = numpy.array([[x_t[i], y_t[i], z_t[i]] for i in range(x_t.size)])
    rtrnInfo["speed"] = numpy.linalg.norm(rtrnInfo["velocity"], axis=1)

    # curvature
    xx_t = numpy.gradient(x_t)
    yy_t = numpy.gradient(y_t)
    zz_t = numpy.gradient(z_t)

    xx_yy = (xx_t * y_t - x_t * yy_t) ** 2
    xx_zz = (xx_t * z_t - x_t * zz_t) ** 2
    zz_yy = (zz_t * y_t - z_t * yy_t) ** 2

    rtrnInfo["curvature"] = (xx_yy + xx_zz + zz_yy) ** 0.5 / (x_t * x_t + y_t * y_t + z_t * z_t)**1.5

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------3D curvature calculation time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo

"""
##############################################################################
# Func: 3D angle with actue only
##############################################################################
"""

def AngleActueMatrix(v1, v2):
    # v1 is your firsr vector
    # v2 is your second vector
    # print(numpy.shape(numpy.einsum('ij, ij->i', v1, v2)))
    # print(numpy.shape(numpy.linalg.norm(v1)))
    # print(numpy.shape(v1))

    # row-wise dot product
    dotProduct = numpy.einsum('ij, ij->i', v1, v2)

    #row wise magnitude
    v1Mag = numpy.linalg.norm(v1, axis=1)
    v2Mag = numpy.linalg.norm(v2, axis=1)

    # cosine need a clip range
    cos = numpy.divide(dotProduct, numpy.multiply(v1Mag, v2Mag))
    cosClip = numpy.clip(cos, -1, 1)

    angle = numpy.arccos(cosClip)

    # print(numpy.shape(angle))
    return angle

"""
##############################################################################
# Func: convert numpy to standard format for json
##############################################################################
"""
import numpy
def NumpytoJson(num):
    if isinstance(num, numpy.integer):
        return int(num)
    if isinstance(num, numpy.floating):
        return float(num)
    if isinstance(num, numpy.ndarray):
        return num.tolist()

"""
##############################################################################
# Func: create a ball with shape and size
##############################################################################
"""
import numpy

def BallMatrix(radius):
    ''' size : size of original 3D numpy matrix A.
        radius : radius of circle inside A which will be filled with ones.
    '''
    radius = int(radius)
    size = 2 * radius + 1

    ''' A : numpy.ndarray of shape size*size*size. '''
    AA = numpy.zeros((size, size, size))

    ''' (x0, y0, z0) : coordinates of center of circle inside A. '''
    x0, y0, z0 = int(numpy.floor(AA.shape[0] / 2)), \
                 int(numpy.floor(AA.shape[1] / 2)), int(numpy.floor(AA.shape[2] / 2))

    for x in range(x0 - radius, x0 + radius + 1):
        for y in range(y0 - radius, y0 + radius + 1):
            for z in range(z0 - radius, z0 + radius + 1):
                ''' deb: measures how far a coordinate in AA is far from the center. 
                        deb>=0: inside the sphere.
                        deb<0: outside the sphere.'''
                # deb = radius - abs(x0 - x) - abs(y0 - y) - abs(z0 - z)
                deb = radius - ((x0 - x) ** 2 + (y0 - y) ** 2 + (z0 - z) ** 2) ** 0.5
                if (deb) >= 0: AA[x, y, z] = 1

    return AA

"""
##############################################################################
# Func: put a shape inside the matrix with origin and distance direction
##############################################################################
"""
import numpy
import copy

def PutShapeMatrix(
        ShapeMat,
        DestMat,
        Origin,
        direction,
        distance
):
    # size of the shape
    shapeRange = numpy.shape(ShapeMat)

    # final origin position
    print('Origin: {}'.format(Origin))
    print('direction: {}'.format(direction))
    print('distance: {}'.format(distance))
    finalOri = Origin + distance * direction

    # check destination matrix range
    destinationRange = numpy.shape(DestMat)

    # use range
    rangeUse = []
    fillOriShp = True

    # origin within the range
    for point in range(len(destinationRange)):
        # check point
        if finalOri[point] < 0:
            print("Point {} less than 0! Change to 0.".format(finalOri[point]))
            finalOri[point] = 0

        if finalOri[point] > destinationRange[point]:
            print("Point {} out of the range {}! Change to {}.".format(finalOri[point], destinationRange[point], destinationRange[point]))
            finalOri[point] = destinationRange[point]

        # check the range of fill in matrix
        rangeStart = int(finalOri[point] - int(shapeRange[point]/2))
        rangeStop = int(finalOri[point] + int(shapeRange[point]/2) + 1)

        # check shape
        if rangeStart < 0:
            print("rangeStart {} less than 0! Change to 0.".format(rangeStart))
            rangeUse.append(0)
            fillOriShp = False
        else:
            rangeUse.append(rangeStart)

        if rangeStop > destinationRange[point]:
            print("Point {} out of the range {}! Change to {}.".format(rangeStop, destinationRange[point], destinationRange[point]))
            rangeUse.append(destinationRange[point])
            fillOriShp = False
        else:
            rangeUse.append(rangeStop)

    outMat = copy.deepcopy(DestMat)

    # fill shape
    print("Range: {}".format(rangeUse))
    if fillOriShp:
        outMat[rangeUse[0]:rangeUse[1], rangeUse[2]:rangeUse[3], rangeUse[4]:rangeUse[5]] = ShapeMat
    else:
        # fill in square
        for x in range([rangeUse[0], rangeUse[1]]):
            for y in range([rangeUse[2], rangeUse[3]]):
                for z in range([rangeUse[4], rangeUse[5]]):
                    outMat[x, y, z] = 1

    return outMat

"""
##############################################################################
# Func: PyRadiomics
##############################################################################
"""
import os
import radiomics
from radiomics import featureextractor
import logging
import collections
import csv
import SimpleITK


def PyRadiomicsBatch(inputCSV, outputFilepath, progress_filename, params):
    # Configure logging
    rLogger = logging.getLogger('radiomics')

    # Set logging level
    # rLogger.setLevel(logging.INFO)  # Not needed, default log level of logger is INFO

    # Create handler for writing to log file
    handler = logging.FileHandler(filename=progress_filename, mode='w')
    handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s'))
    rLogger.addHandler(handler)

    # Initialize logging for batch log messages
    logger = rLogger.getChild('batch')

    # Set verbosity level for output to stderr (default level = WARNING)
    radiomics.setVerbosity(logging.INFO)

    logger.info('pyradiomics version: %s', radiomics.__version__)
    logger.info('Loading CSV')

    flists = []
    try:
        with open(inputCSV, 'r') as inFile:
            cr = csv.DictReader(inFile, lineterminator='\n')
            flists = [row for row in cr]
    except Exception:
        logger.error('CSV READ FAILED', exc_info=True)

    logger.info('Loading Done')
    logger.info('Patients: %d', len(flists))

    if os.path.isfile(params):
        extractor = featureextractor.RadiomicsFeatureExtractor(params)
    else:  # Parameter file not found, use hardcoded settings instead
        settings = {}
        settings['binWidth'] = 25
        settings['resampledPixelSpacing'] = None  # [3,3,3]
        settings['interpolator'] = SimpleITK.sitkBSpline
        settings['enableCExtensions'] = True

        extractor = featureextractor.RadiomicsFeatureExtractor(**settings)
        # extractor.enableInputImages(wavelet= {'level': 2})

    logger.info('Enabled input images types: %s', extractor.enabledImagetypes)
    logger.info('Enabled features: %s', extractor.enabledFeatures)
    logger.info('Current settings: %s', extractor.settings)

    headers = None

    for idx, entry in enumerate(flists, start=1):

        logger.info("(%d/%d) Processing Patient (Image: %s, Mask: %s)", idx, len(flists), entry['Image'],
                    entry['Mask'])

        imageFilepath = entry['Image']
        maskFilepath = entry['Mask']
        label = entry.get('Label', None)

        if str(label).isdigit():
            label = int(label)
        else:
            label = None

        if (imageFilepath is not None) and (maskFilepath is not None):
            featureVector = collections.OrderedDict(entry)
            featureVector['Image'] = os.path.basename(imageFilepath)
            featureVector['Mask'] = os.path.basename(maskFilepath)

            try:
                featureVector.update(extractor.execute(imageFilepath, maskFilepath, label))

                with open(outputFilepath, 'a') as outputFile:
                    writer = csv.writer(outputFile, lineterminator='\n')
                    if headers is None:
                        headers = list(featureVector.keys())
                        writer.writerow(headers)

                    row = []
                    for h in headers:
                        row.append(featureVector.get(h, "N/A"))
                    writer.writerow(row)
            except Exception:
                logger.error('FEATURE EXTRACTION FAILED', exc_info=True)







