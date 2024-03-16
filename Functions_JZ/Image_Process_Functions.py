# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 20:00:28 2020

@author: yingmohuanzhou
"""

import sys
import os

# Set current folder as working directory
# Get the current working direcory: os.getcwd()
# Change the current working direcory: os.chdir()
# os.chdir(os.getcwd())

import Post_Image_Process_Functions
import Save_Load_File
import Use_Plt
import VTK_Functions
import Matrix_Math
import Image_Process_Functions
import Pd_Funs
import SITK_Numpy

"""
##############################################################################
#Filter matrix data return mask and masked matrix
##############################################################################
"""
import numpy
import vtk


def FilterData(
        rangStarts=[0],
        rangStops=[0],
        dataMat=[0],
        funType="single value",
        ConvertVTKType=False,
        InDataType=numpy.float64
):
    # initial value
    dataMatMsked = None
    dataMatMsks = None

    # convert vtk to numpy
    if ConvertVTKType:
        DataType = VTK_Functions.VTK_Numpy(InDataType,
                                           VTK_to_Numpy=True)
    else:
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
    if funType == "single value greater" or funType == "single_value_greater":
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

    return mskVals, mskOnes  # dataMatMsked - values, dataMatMsks - 0 and 1


"""
##############################################################################
#Func: filter direction and slices
##############################################################################
"""
import numpy
import time


def FilterDirectionSlices(
        inMat,
        directions,
        sliceStarts,
        sliceStops,
        rangStarts,
        rangStops,
        funTypes,
):
    # initiation
    # time
    strtT = time.time()
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["outputMat"] = None
    rtrnInfo["outputOnes"] = None
    rtrnInfo["message"] = ""

    # none:
    if inMat is None:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "ERROR: None input"
        return rtrnInfo
    else:
        rtrnInfo["outputMat"] = (inMat != 0) * 1  # binarinise data

    # shape and dtype
    inMatShp = numpy.shape(inMat)
    inMatDType = inMat.dtype.type

    # compare same shape
    checkLstShp = Post_Image_Process_Functions.CompareListDimension(
        lsts=[
            sliceStarts,
            sliceStops,
            rangStarts,
            rangStops,
        ]
    )
    if checkLstShp["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "Check: does not have the same length of the list inputs!"

    # loop each list element
    # single direction and mask
    directUpdate = True
    funTypeUpdate = True
    if not numpy.shape(directions):
        direction = directions
        directUpdate = False
        rtrnInfo["message"] += "Single direction input\n"
    if not numpy.shape(funTypes):
        funType = funTypes
        funTypeUpdate = False
        rtrnInfo["message"] += "Single funTypes input\n"

    for case in range(len(sliceStarts)):
        # all type
        sliceStart = int(sliceStarts[case])
        sliceStop = int(sliceStops[case])
        rangStart = rangStarts[case]
        rangStop = rangStops[case]

        # dealing with direction & mask
        if directUpdate: direction = directions[case]
        if funTypeUpdate: funType = funTypes[case]

        # flip results
        if direction == 'X' or direction == 'x':
            pass
        elif direction == 'Y' or direction == 'y':
            rtrnInfo["outputMat"] = Matrix_Math.FilpAxes(
                inMat=rtrnInfo["outputMat"],
                axisInitial="X",
                axisFinal="Y"
            )
            inMat = Matrix_Math.FilpAxes(
                inMat=inMat,
                axisInitial="X",
                axisFinal="Y"
            )
        elif direction == 'Z' or direction == 'z':
            rtrnInfo["outputMat"] = Matrix_Math.FilpAxes(
                inMat=rtrnInfo["outputMat"],
                axisInitial="X",
                axisFinal="Z"
            )
            inMat = Matrix_Math.FilpAxes(
                inMat=inMat,
                axisInitial="X",
                axisFinal="Z"
            )
        else:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: wrong direction: {}".format(directions)
            raise KeyError("ERROR: rotation failure! None type returned!")
        # dealing error
        if inMat is None or rtrnInfo["outputMat"] is None:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: rotation failure!"
            raise TypeError("ERROR: rotation failure! None type returned!")

        # range correction
        if sliceStart > sliceStop:
            temp = sliceStart
            sliceStart = sliceStop
            sliceStop = temp
            print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
        if sliceStart < 0:
            sliceStart = 0
            print("Slice start cannot be less than zero: auto change to 0!")
        if direction == 'X' and sliceStop >= inMatShp[0]:
            sliceStop = inMatShp[0] - 1
            print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))
        elif direction == 'Y' and sliceStop >= inMatShp[1]:
            sliceStop = inMatShp[1] - 1
            print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))
        elif direction == 'Z' and sliceStop >= inMatShp[2]:
            sliceStop = inMatShp[2] - 1
            print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

        # filter data
        val, rtrnInfo["outputMat"][sliceStart:sliceStop + 1] = FilterData(
            rangStarts=[rangStart],
            rangStops=[rangStop],
            dataMat=inMat[sliceStart:sliceStop + 1],
            funType=funType
        )

        # rotate bask
        # flip results
        if direction == 'X' or direction == 'x':
            pass
        elif direction == 'Y' or direction == 'y':
            rtrnInfo["outputMat"] = Matrix_Math.FilpAxes(
                inMat=rtrnInfo["outputMat"],
                axisInitial="Y",
                axisFinal="X"
            )
        elif direction == 'Z' or direction == 'z':
            rtrnInfo["outputMat"] = Matrix_Math.FilpAxes(
                inMat=rtrnInfo["outputMat"],
                axisInitial="Z",
                axisFinal="X"
            )
        else:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: wrong direction: {}".format(directions)
            raise KeyError("ERROR: rotation failure! None type returned!")
        # dealing error
        if inMat is None or rtrnInfo["outputMat"] is None:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: rotation failure!"
            raise TypeError("ERROR: rotation failure! None type returned!")

    # convert data type
    rtrnInfo["outputMat"] = numpy.array(rtrnInfo["outputMat"], dtype=inMatDType)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Slice filtering time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete slicewise filtering: {}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Distance calculation
##############################################################################
"""
import numpy
from scipy import ndimage


def DistanceMask(matData,
                 thres=0):
    # booleanise data
    matDataTF = matData > thres

    # disatance mask
    matDataTFShp = numpy.shape(matDataTF)
    matDataDist = numpy.zeros(matDataTF)

    for imgSlice in range(matDataTFShp[0]):
        # image slice
        imgTF = matDataTF[imgSlice]

        # Exact Euclidean distance transform https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.distance_transform_edt.html#scipy.ndimage.distance_transform_edt
        distance = ndimage.distance_transform_edt(imgTF)

        # stack slice
        matDataDist[imgSlice] = distance

    return matDataDist


"""
##############################################################################
# Function to print three largest elements in array
##############################################################################
"""
import sys


def print3largest(arr):
    # Function to print three largest elements

    # initialise
    first = None
    second = None
    third = None

    # arr size
    arrSize = numpy.shape(arr)
    arr_size = arrSize[0]
    # There should be atleast three
    # elements
    if (arr_size < 3):
        print("Array size < 3")
        if arr_size == 1:
            first = arr[0]
        elif arr_size == 2:
            first = arr[0]
            second = arr[1]

    # Create inital value
    third = first = second = -sys.maxsize

    for i in range(0, arr_size):
        # If current element is greater
        # than first
        if (arr[i] > first):
            third = second
            second = first
            first = arr[i]

            # If arr[i] is in between first
        # and second then update second
        elif (arr[i] > second):
            third = second
            second = arr[i]

        elif (arr[i] > third):
            third = arr[i]

    print("Three largest elements are",
          first, second, third)

    return first, second, third


"""
##############################################################################
# Connectivity for 2D and 3D can keep up to 3 largest areas
##############################################################################
"""
import skimage.measure
import numpy


def ConnectivityFilter(matData, connectType=1, keepNumber=1, FilterArea='first'):
    # initial values
    mskVals = None
    mskOnes = None
    dataMatMsks = None
    inMatDataMsked = None

    # filter area correct:
    if FilterArea not in ["first", "second", "third"]:
        print(FilterArea + " not defined \nUse 'first' instead!")
        FilterArea = "first"

    # Binary mat data
    matDataOnes = 1 * (matData > 0)

    # Connectivity: label connected regions of an integer array
    # https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.label
    label, num = skimage.measure.label(matDataOnes,
                                       connectivity=connectType,
                                       return_num=True)  # connectivity 1 to input.ndim

    # Measure properties of labeled image regions
    # https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.regionprops
    region = skimage.measure.regionprops(label)

    # num_list is the "label" number list
    num_list = [i for i in range(1, num + 1)]
    print(num_list)
    # Match area with the num_list
    area_list = [region[i - 1].area for i in num_list]
    print(area_list)

    # find first three largest area/volume
    firstV, secondV, thirdV = print3largest(area_list)

    # Filter from the first largest
    if FilterArea == 'first':
        if keepNumber == 1:
            # find label value and replace
            # Find area
            firstPosi = numpy.where(area_list == firstV)
            # Find label
            firstVVal = num_list[firstPosi[0][0]]
            # Mask out other region
            dataMatMsked, dataMatMsks = FilterData(rangStarts=[firstVVal],
                                                   dataMat=label,
                                                   funType="single value")
            # Filter the original mat
            inMatDataMsked = numpy.multiply(dataMatMsks, matData)
            print("Filtered with connectivity = " + str(connectType) + "\n Leave first 'ONE' area/volume")

        elif keepNumber == 2:
            # find label value and replace
            firstPosi = numpy.where(area_list == firstV)
            firstVVal = num_list[firstPosi[0][0]]
            secondPosi = numpy.where(area_list == secondV)
            secondVVal = num_list[secondPosi[0][0]]
            # Mask out other region
            dataMatMsked, dataMatMsks = FilterData(rangStarts=[firstVVal, secondVVal],
                                                   dataMat=label,
                                                   funType="single value")
            # Filter the original mat
            inMatDataMsked = numpy.multiply(dataMatMsks, matData)
            print("Filtered with connectivity = " + str(connectType) + "\n Leave first 'TWO' area/volume")

        elif keepNumber == 3:
            # find label value and replace
            firstPosi = numpy.where(area_list == firstV)
            firstVVal = num_list[firstPosi[0][0]]
            secondPosi = numpy.where(area_list == secondV)
            secondVVal = num_list[secondPosi[0][0]]
            thirdPosi = numpy.where(area_list == thirdV)
            thirdVVal = num_list[thirdPosi[0][0]]
            # Mask out other region
            dataMatMsked, dataMatMsks = FilterData(rangStarts=[firstVVal, secondVVal, thirdVVal],
                                                   dataMat=label,
                                                   funType="single value")
            # Filter the original mat
            inMatDataMsked = numpy.multiply(dataMatMsks, matData)
            print("Filtered with connectivity = " + str(connectType) + "\n Leave first 'THREE' area/volume")

    # Filter from the second largest
    if FilterArea == 'second':
        if keepNumber == 1:
            # find label value and replace
            # Find area
            firstPosi = numpy.where(area_list == secondV)
            # Find label
            firstVVal = num_list[firstPosi[0][0]]
            # Mask out other region
            dataMatMsked, dataMatMsks = FilterData(rangStarts=[firstVVal],
                                                   dataMat=label,
                                                   funType="single value")
            # Filter the original mat
            inMatDataMsked = numpy.multiply(dataMatMsks, matData)
            print("Filtered with connectivity = " + str(connectType) + "\n Leave first 'ONE' area/volume")

        elif keepNumber == 2:
            # find label value and replace
            firstPosi = numpy.where(area_list == secondV)
            firstVVal = num_list[firstPosi[0][0]]
            secondPosi = numpy.where(area_list == thirdV)
            secondVVal = num_list[secondPosi[0][0]]
            # Mask out other region
            dataMatMsked, dataMatMsks = FilterData(rangStarts=[firstVVal, secondVVal],
                                                   dataMat=label,
                                                   funType="single value")
            # Filter the original mat
            inMatDataMsked = numpy.multiply(dataMatMsks, matData)
            print("Filtered with connectivity = " + str(connectType) + "\n Leave first 'TWO' area/volume")

        elif keepNumber >= 3:
            print("Not support filter 3 largeest areas from the 2nd largest")

    # Filter from the third largest
    if FilterArea == 'third':
        if keepNumber == 1:
            # find label value and replace
            # Find area
            firstPosi = numpy.where(area_list == thirdV)
            # Find label
            firstVVal = num_list[firstPosi[0][0]]
            # Mask out other region
            dataMatMsked, dataMatMsks = FilterData(rangStarts=[firstVVal],
                                                   dataMat=label,
                                                   funType="single value")
            # Filter the original mat
            inMatDataMsked = numpy.multiply(dataMatMsks, matData)
            print("Filtered with connectivity = " + str(connectType) + "\n Leave first 'ONE' area/volume")

        elif keepNumber >= 2:
            print("Not support filter 2 largeest areas from the 3rd largest")

    # return values
    mskOnes = dataMatMsks
    mskVals = inMatDataMsked

    return mskOnes, mskVals


"""
##############################################################################
#Func: Connectivity filter volume with smoothing
##############################################################################
"""


def ConnectivityAreaVolFilter(
        matData,
        connectType,
        FilterThres,
        smooth=False,
        radialSamplingSize=None,
        initSplineSmooth=None,
        initRadialSplineOrder=None,
        vertRadialSplineOrder=None,
        vertSplineSmoothFac=None,
        resInt=None,
        planeSmoothOrder=None,
        planeSplineSmoothFac=None
):
    # binary data
    matData = (matData != 0) * 1

    # Connectivity: label connected regions of an integer array
    # https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.label
    label, num = skimage.measure.label(
        matData,
        connectivity=connectType,
        return_num=True
    )  # connectivity 1 to input.ndim

    # Measure properties of labeled image regions
    # https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.regionprops
    region = skimage.measure.regionprops(label)

    # num_list is the "label" number list
    num_list = [i for i in range(1, num + 1)]
    # Match area with the num_list
    area_list = [region[i - 1].area for i in num_list]

    print("num_list = \n" + str(num_list))
    print("area_list = \n" + str(area_list))
    print("numpy.min(label): " + str(numpy.min(label)))
    print("numpy.max(label): " + str(numpy.max(label)))
    print("num: " + str(num))

    # Filter Area/volume
    matDataShp = numpy.shape(matData)
    valStck = numpy.zeros(matDataShp)
    mskStck = numpy.zeros(matDataShp)
    smoothStck = numpy.zeros(matDataShp)

    for i in range(num):  # No more background issue!!!!

        # Compare area
        if area_list[i] >= FilterThres:
            lblVal = num_list[i]

            # Mask out other region
            _, dataMatMsks = FilterData(
                rangStarts=[lblVal],
                dataMat=label,
                funType="single value"
            )

            print("area_list[i] = " + str(area_list[i]))

            # smooth with spline
            if smooth:
                print("smooth")
                smoothMsk = SplineSmooth3D(
                    maskData=dataMatMsks,
                    radialSamplingSize=radialSamplingSize,
                    initSplineSmooth=initSplineSmooth,
                    initRadialSplineOrder=initRadialSplineOrder,
                    vertRadialSplineOrder=vertRadialSplineOrder,
                    vertSplineSmoothFac=vertSplineSmoothFac,
                    resInt=resInt,
                    planeSmoothOrder=planeSmoothOrder,
                    planeSplineSmoothFac=planeSplineSmoothFac
                )
                smoothStck += smoothMsk['SmoothMask']

            # Filter the original mat
            inMatDataMsked = numpy.multiply(dataMatMsks, matData)

            # stack values
            valStck = valStck + inMatDataMsked
            mskStck = mskStck + dataMatMsks

    # binary data out
    smoothStck = (smoothStck != 0) * 1
    mskStck = (mskStck != 0) * 1

    print("Filtered with connectivity = " + str(connectType) +
          "\n greater and equal: " + str(FilterThres))

    return valStck, mskStck, smoothStck


"""
##############################################################################
# Create a plane with centerpoint and empty plane with slicing direction
##############################################################################
"""
import numpy


def PlaneCenterPoint(matData, SliceAlong=0, flatPlane2D=True):
    # Check dimentions
    while SliceAlong > 2:
        print("Only support to 3 dimensions")
        SliceAlong = input("input inter from 0, 1, 2: ")

    # shape
    matDataShape = numpy.shape(matData)

    # volume
    if not flatPlane2D:
        # slice perpendicular to 0 direction [1]*[2] plane
        if SliceAlong == 0:
            # Set edges
            Length = matDataShape[1]
            Width = matDataShape[2]
        if SliceAlong == 1:
            # Set edges
            Length = matDataShape[0]
            Width = matDataShape[2]
        if SliceAlong == 2:
            # Set edges
            Length = matDataShape[0]
            Width = matDataShape[1]
    elif flatPlane2D:
        # Set edges
        Length = matDataShape[0]
        Width = matDataShape[1]

    # Create plane
    emptyPlan = numpy.zeros([Length, Width])
    centerPlan = emptyPlan.copy()
    # Find mid point with ceil
    # move down 1 as start from 0,0
    midLength = int(numpy.ceil(Length / 2) - 1)
    midWidth = int(numpy.ceil(Width / 2) - 1)
    # center plane mask centerpoint
    centerPlan[midLength, midWidth] = 1
    centerPointList = [midLength, midWidth]

    return emptyPlan, centerPointList, centerPlan


"""
##############################################################################
# Gradient calculation
##############################################################################
"""
import numpy
import cv2


def GradientCalcs(dataMat, Blur=False, Blurksize=(3, 3), GsnSigma=2):
    # Gradient calculation
    # Gaussian blur
    while True:
        if not Blur:
            imgData = dataMat
            break
        elif Blur:
            imgData = cv2.GaussianBlur(dataMat, Blurksize, GsnSigma)
            break
        else:
            print("Wrong 'Blur' parameter type in (True/False): ")

    # Create gradient Scharr kernel
    # Must have data type to caculation
    verScharr = numpy.array([[3., 0., -3.], [10., 0., -10.], [3., 0., -3.]], dtype="float64")
    horiScharr = numpy.transpose(verScharr)

    # Grdient
    scharrX = cv2.filter2D(imgData, -1, verScharr).astype('int64')  # -1 same data type
    scharrY = cv2.filter2D(imgData, -1, horiScharr).astype('int64')
    scharrXY = numpy.sqrt(numpy.power(scharrX, 2) + numpy.power(scharrY, 2))
    print("Complete gradient convolution")

    return scharrXY, scharrX, scharrY


"""
##############################################################################
# 2nd Gradient/Laplacian of Gaussian calculation
##############################################################################
"""
import numpy
import cv2


def LapGradientCalcs(dataMat,
                     Blur=True,
                     Blurksize=(3, 3),
                     GsnSigma=2):
    # Gradient calculation
    # Gaussian blur
    while True:
        if not Blur:
            imgData = dataMat
            break
        elif Blur:
            imgData = cv2.GaussianBlur(dataMat, Blurksize, GsnSigma)
            break
        else:
            input("Wrong 'Blur' parameter type in (True/False): ")

    # Laplacian
    lplDataMat = cv2.Laplacian(imgData, cv2.CV_64F)

    print("Complete Laplacian of Gaussian")

    return lplDataMat


"""
##############################################################################
# Filled mask with other data and close with disk
##############################################################################
"""
import numpy
import cv2
import skimage.morphology


def FillClose(toCloseMat, fillMat="", diskSize=2):
    # Filled mask with other data and close with disk
    # Fill or not
    toCloseMatShape = numpy.shape(toCloseMat)
    if fillMat != "":
        # check same shape
        if toCloseMatShape != numpy.shape(fillMat):
            Save_Load_File.WarnExit("Not same size input\n" + str(toCloseMatShape) + "\n" + str(numpy.shape(fillMat)))
    else:
        fillMat = numpy.zeros(toCloseMatShape)
        print("NO fill input")

    # Fill
    filledMat = numpy.zeros(toCloseMatShape)
    filledMat = fillMat + toCloseMat
    # Binarinise
    DataMsked, filledMatMsk = FilterData(rangStarts=[0],
                                         dataMat=filledMat,
                                         funType="single value greater")

    # Create disk
    selem = skimage.morphology.disk(diskSize)

    # closing
    filledMatClose = skimage.morphology.closing(filledMatMsk, selem)

    print("Finish closing with diskSize: " + str(diskSize))

    return filledMatMsk, filledMatClose


"""
##############################################################################
# Filled mask with other data and open with disk
##############################################################################
"""
import numpy
import cv2
import skimage.morphology


def FillOpenClose(toCloseMat, fillMat="", dilateDisk=1, diskSize=1):
    # Filled mask with other data and close with disk
    # Fill or not
    toCloseMatShape = numpy.shape(toCloseMat)
    if fillMat != "":
        # check same shape
        if toCloseMatShape != numpy.shape(fillMat):
            Save_Load_File.WarnExit("Not same size input\n" + str(toCloseMatShape) + "\n" + str(numpy.shape(fillMat)))
    else:
        fillMat = numpy.zeros(toCloseMatShape)
        print("NO fill input")

    # dilate fill mat
    selemFill = skimage.morphology.disk(dilateDisk)
    fillMat = skimage.morphology.dilation(fillMat, selemFill)

    # Fill
    filledMat = numpy.zeros(toCloseMatShape)
    filledMat = fillMat + toCloseMat

    # Binarinise
    DataMsked, filledMatMsk = FilterData(rangStarts=[0],
                                         dataMat=filledMat,
                                         funType="single value greater")

    # Create disk
    selem = skimage.morphology.disk(diskSize)

    # closing
    filledMatOpen = skimage.morphology.opening(filledMatMsk, selem)
    filledMatClose = skimage.morphology.closing(filledMatOpen, selem)
    print("Finish opening and closeing with diskSize: " + str(diskSize))

    return filledMatMsk, filledMatOpen, filledMatClose


"""
##############################################################################
# Connectivity filter with area include the center point
##############################################################################
"""
import skimage.measure


def ConnectAreaFilterCenter(dataMat,
                            refDataMat,
                            connectType=2
                            ):
    # create empty and center point
    emptyPlan, centerPointList, centerPlan = PlaneCenterPoint(
        matData=dataMat,
        flatPlane2D=True
    )

    # Connectivity
    labelDataMat, num = skimage.measure.label(
        dataMat,
        connectivity=connectType,
        return_num=True
    )

    # Must not filter out the background value
    checkBackround = numpy.sum(numpy.multiply(centerPlan, refDataMat > 0))
    cenVal = 0  # in label background is also '0'
    if checkBackround != 0:
        # centerpoint vlaue
        cenVal = numpy.sum(numpy.multiply(centerPlan, labelDataMat))
    elif checkBackround == 0:
        # find the original lumen mask label value
        # background zero
        labelDataMat0 = numpy.multiply(refDataMat, labelDataMat)

        # filter value is the non-zero mean FLOOR in the original lumen mask
        cenVals = numpy.multiply(refDataMat, labelDataMat0)
        cenVal = numpy.floor(cenVals[numpy.nonzero(cenVals)].mean())

    # Filter of cenVal
    dataMatMsked_lbl, dataMatMsk_lbl = FilterData(rangStarts=[cenVal],
                                                  dataMat=labelDataMat,
                                                  funType="single value")
    print("Connectivity filter with label = " + str(cenVal))
    print("Area left: " + str(numpy.sum(dataMatMsk_lbl)))

    return dataMatMsk_lbl


"""
##############################################################################
# Active contour
##############################################################################
"""
import skimage.segmentation


def ActContourSmth(dataMat,
                   balloonForce=-1,
                   smoothFac=3,
                   iterNo=500,
                   contourThres=0.69):
    # Active contour
    print("Active contour smoothing")
    # lumen shape
    dataMat_shape = numpy.shape(dataMat)
    # create empty for stacking
    dataMatSmooth = numpy.zeros(dataMat_shape)
    # # Initial level set
    init_ls10 = skimage.segmentation.disk_level_set(image_shape=numpy.shape(dataMat[0]), radius=10)
    # Initial level set
    # init_ls = skimage.segmentation.checkerboard_level_set(numpy.shape(coroMskToSmooth[0]), 20)

    for imgSlice in range(dataMat_shape[0]):
        dataMat_slice = dataMat[imgSlice]

        # jump no mask
        if numpy.sum(dataMat_slice) == 0:
            print("Jump zero mask slice: " + str(imgSlice))
            continue

        # gradient
        gimage = skimage.segmentation.inverse_gaussian_gradient(dataMat_slice)

        # active contour
        ls = skimage.segmentation.morphological_geodesic_active_contour(gimage=gimage,
                                                                        iterations=iterNo,
                                                                        init_level_set=init_ls10,
                                                                        threshold=contourThres,
                                                                        smoothing=smoothFac,
                                                                        balloon=balloonForce)
        # stcking results
        dataMatSmooth[imgSlice] = ls
        print("Finish slice: " + str(imgSlice))
        print(numpy.sum(ls))

    print("Complete smoothing")

    return dataMatSmooth


"""
##############################################################################
# WaterShade
##############################################################################
"""
import skimage.segmentation
import skimage.feature
import numpy
from scipy import ndimage


def WaterShadeMsk(dataMat, Threshold=0):
    # Now we want to separate the two objects in image
    # Input convert to boolean
    image = dataMat > Threshold
    # Generate the markers as local maxima of the distance to the background
    distance = ndimage.distance_transform_edt(image)
    coords = skimage.feature.peak_local_max(distance, footprint=numpy.ones((3, 3)), labels=image)
    mask = numpy.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers, _ = ndimage.label(mask)
    labels = skimage.segmentation.watershed(-distance, markers, mask=image)

    return labels


"""
##############################################################################
# WaterShade filter with center label
##############################################################################
"""
import skimage.segmentation
import skimage.feature
import numpy
from scipy import ndimage


def WaterShadeMskCenterFilter(dataMat, refDataMat, Threshold=0):
    # water shade labels
    labels = WaterShadeMsk(dataMat, Threshold=0)

    # create center plane
    emptyPlan, centerPointList, centerPlan = PlaneCenterPoint(matData=dataMat,
                                                              SliceAlong=0,
                                                              flatPlan=True)

    # Center point cannot be '0' background of the combine lumen mask
    checkBackround = numpy.sum(numpy.multiply(centerPlan, refDataMat))
    cenVal = 0  # in label background is also '0'
    if checkBackround != 0:
        # centerpoint vlaue
        cenVal = numpy.sum(numpy.multiply(centerPlan, labels))
    elif checkBackround == 0:
        # find the original lumen mask label value
        # background zero
        labels0 = numpy.multiply(refDataMat, labels)

        # filter value is the non-zero mean FLOOR in the original lumen mask
        cenVals = numpy.multiply(refDataMat, labels0)
        cenVal = numpy.floor(cenVals[numpy.nonzero(cenVals)].mean())

    # filter based on center plane
    WSCenterMsked, WSCenterMsk = FilterData(rangStarts=[cenVal],
                                            dataMat=labels,
                                            funType="single value")

    print("Finish water sahding with final area = " + str(numpy.sum(WSCenterMsk)))

    return labels, WSCenterMsked, WSCenterMsk


"""
##############################################################################
#Func: Two erosion keep the area difference the same 
##############################################################################
"""
import skimage.morphology
import numpy
import skimage.measure
import time


def ShrinkTwoMasks(
        outMask,
        inMask,
        outThresGreater,
        inThresGreater,
        shrkFac,
        minInA=4,
        minDilDisk=1,
        closeDisk=20
):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["insideMaskCentroidX"] = None
    rtrnInfo["insideMaskCentroidY"] = None
    rtrnInfo["outerShrinkRatio"] = 1
    rtrnInfo["innerShrinkRatio"] = 1
    rtrnInfo["outerShrinkMask"] = None
    rtrnInfo["innerShrinkMask"] = None
    rtrnInfo["innerMaskAreaOriginal"] = None
    rtrnInfo["outerMaskAreaOriginal"] = None
    rtrnInfo["differenceMaskAreaOriginal"] = None
    rtrnInfo["innerShrinkMaskArea"] = None
    rtrnInfo["outerShrinkMaskArea"] = None
    rtrnInfo["differenceShrinkMaskArea"] = None
    rtrnInfo["message"] = ''

    # binary both masks
    inMask = (inMask > inThresGreater) * 1
    outMask = (outMask > outThresGreater) * 1

    # closing disk
    # Create disk
    selem = skimage.morphology.disk(closeDisk)

    # make sure only single mask in inMask and outMask
    ## label
    inLabels, inNums = skimage.measure.label(inMask, return_num=True)
    outLabels, outNums = skimage.measure.label(outMask, return_num=True)
    ## only one label
    while True:
        if inNums > 1 or outNums > 1:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] += 'Cannot have more than 1 connected region!!! Force to connect'
            print('Cannot have more than 1 connected region!!! Force to connect')
            ## fixing to close
            if inNums > 1:
                rtrnInfo["errorMessage"] += '\nInner have more than 1 connected region - fixed once'
                # closing
                inMask = skimage.morphology.closing(inMask, selem)
                # morphology
                inLabels, inNums = skimage.measure.label(inMask, return_num=True)
                print('Inner have more than 1 connected region - fixed once')
            elif outNums > 1:
                rtrnInfo["errorMessage"] += '\nOuter have more than 1 connected region - fixed once'
                # closing
                outMask = skimage.morphology.closing(outMask, selem)
                # morphology
                outLabels, outNums = skimage.measure.label(outMask, return_num=True)
                print('Outer have more than 1 connected region - fixed once')
        else:
            break

    # region props for information
    # !!! list start from 0 label start from 1!!!
    inRegions = skimage.measure.regionprops(inLabels)
    outRegions = skimage.measure.regionprops(outLabels)
    inBubble = inRegions[0]
    outBubble = outRegions[0]

    # get information
    ## Centroid coordinate tuple (row, col)!!
    rtrnInfo["insideMaskCentroidY"], rtrnInfo["insideMaskCentroidX"] = inBubble.centroid
    inA = inBubble.area
    outA = outBubble.area
    outP = outBubble.perimeter

    # shrink any way do not think about perimeter - outmask greater than thresholding ratio!!!
    # outer area decrease > 50% out perimeter
    # if (outA - outAShrK) < (0.5 * outP):
    #     # Shrinkage not possible
    #     rtrnInfo["error"] = True
    #     rtrnInfo["errorMessage"] += 'No Shrinkage! Area reducing: {} < 0.5 * Perimeter: {}'.format(
    #         outA - outAShrK,
    #         0.5 * outP
    #     )
    #     print(rtrnInfo["errorMessage"])
    #     # output
    #     rtrnInfo["outerShrinkMask"] = outMask
    #     rtrnInfo["innerShrinkMask"] = inMask
    #     return rtrnInfo

    # shrinking
    ## maintaning same area if possible
    outAShrK = outA * (1 - shrkFac)
    diffA = outA - inA

    ## corrosion outer area
    inCorMsk = inMask
    outCorMsk = outMask

    ## minimum outer area & inner outer difference to enclose inner
    minInAside = numpy.rint(numpy.sqrt(numpy.abs(minInA)))
    print("Input inner square side: area = {} // side = {}".format(minInA, minInAside))
    ### dealing with zero:
    if minInAside == 0:
        minInAside = 1
        print("Correct inner square side 0 to 1")
    ### min outside area max of two situaion: square or line
    minOutA = numpy.max([(minInAside + 2) ** 2, minInA * 3])  ## full enclosed square case max of two

    ## disk
    selem = skimage.morphology.disk(1)

    ## errosion until less than outAShrK but fully enclosed minInA
    while True:  # numpy.sum(outCorMsk) > outAShrK: - Exit just under the threholding !!!
        ## errosion
        outCorMskTmp = skimage.morphology.erosion(
            image=outCorMsk,
            selem=selem
        )
        ## Exit just greater than thresholding !!!!!
        if numpy.sum(outCorMskTmp) < outAShrK:
            break
        elif numpy.sum(outCorMskTmp) < minOutA:  ## check min area !!!
            # update
            msg = "Erosion outer mask = {} < minOutA = {} STOP erosion!" \
                  "\nFinal outer mask area = {}\n" \
                  "".format(
                numpy.sum(outCorMskTmp),
                minOutA,
                numpy.sum(outCorMsk)
            )
            print(msg)
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] += msg
            break
        else:
            ## update
            outCorMsk = outCorMskTmp

    ## inner errosion keep diffA cannot be too small
    outCorMskA = numpy.sum(outCorMsk)
    while (outCorMskA - numpy.sum(inCorMsk)) < diffA:  ## - Exit just under the threholding !!!
        # erosion
        inCorMskTmp = skimage.morphology.erosion(
            image=inCorMsk,
            selem=selem
        )
        # need to be great than minInA
        if numpy.sum(inCorMskTmp) < minInA:
            # update
            msg = "Erosion inner mask = {} < minInA = {} STOP erosion!" \
                  "\nFinal inner mask area = {}\n" \
                  "".format(
                numpy.sum(inCorMskTmp),
                minInA,
                numpy.sum(inCorMsk)
            )
            print(msg)
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] += msg
            break
        else:
            # correct
            inCorMsk = inCorMskTmp

    ## make sure inner shrinked mask is inside the outer shrinked mask
    # keep inside inside!
    ## disk
    selem2 = skimage.morphology.disk(minDilDisk)
    ## 2 dilation
    inCorMskDil = skimage.morphology.dilation(
        image=inCorMsk,
        selem=selem2
    )
    ## combine
    outCorMsk = ((outCorMsk + inCorMskDil) > 0) * 1

    # update
    msg = "Inside mask is forced inside by Dilation of {} pixels!!" \
          "\nFinal outer mask area = {}" \
          "".format(minDilDisk, numpy.sum(outCorMsk))
    print(msg)

    # output results
    rtrnInfo["outerShrinkRatio"] = numpy.sum(outCorMsk) / outA
    rtrnInfo["innerShrinkRatio"] = numpy.sum(inCorMsk) / inA
    rtrnInfo["outerShrinkMask"] = outCorMsk
    rtrnInfo["innerShrinkMask"] = inCorMsk
    rtrnInfo["innerMaskAreaOriginal"] = inA
    rtrnInfo["outerMaskAreaOriginal"] = outA
    rtrnInfo["differenceMaskAreaOriginal"] = diffA
    rtrnInfo["innerShrinkMaskArea"] = numpy.sum(inCorMsk)
    rtrnInfo["outerShrinkMaskArea"] = numpy.sum(outCorMsk)
    rtrnInfo["differenceShrinkMaskArea"] = rtrnInfo["outerShrinkMaskArea"] - rtrnInfo["innerShrinkMaskArea"]
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Shrink time: {} s------".format(rtrnInfo["processTime"])

    msg = "//////Final shrinkage//////" \
          "\nOuter shrinking: ori_A = {} -> new_A = {} // ratio={:.2f}" \
          "\nInner shrinking: ori_A = {} -> new_A = {} // ratio={:.2f}" \
          "\nOri_diffA = {} -> New_diffA = {}" \
          "\nShrinking error = {}" \
          "\nError Message: {}" \
          "\n{}".format(
        rtrnInfo["outerMaskAreaOriginal"],
        rtrnInfo["outerShrinkMaskArea"],
        rtrnInfo["outerShrinkRatio"],
        rtrnInfo["innerMaskAreaOriginal"],
        rtrnInfo["innerShrinkMaskArea"],
        rtrnInfo["innerShrinkRatio"],
        rtrnInfo["differenceMaskAreaOriginal"],
        rtrnInfo["differenceShrinkMaskArea"],
        rtrnInfo["error"],
        rtrnInfo["errorMessage"],
        rtrnInfo["processTimeMessage"]
    )

    rtrnInfo["message"] += msg
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: 3D dilation correction fully enclose
##############################################################################
"""


def Dilation3DEnclose(
        outMask,
        inMask1,
        inMask1Thres,
        inMask2,
        inMask2Thres,
        dilDisk
):
    # shape
    outMaskShp = numpy.shape(outMask)

    # dilation correct
    errMsg1, inMask1Dil = DiskDilate(
        dataMat=inMask1,
        Thres=inMask1Thres,
        dilateIncre=dilDisk,
        binaryMsk=True,
        axisChoice='3D'
    )

    # 2nd
    if inMask2 is not None:
        errMsg2, inMask2Dil = DiskDilate(
            dataMat=inMask2,
            Thres=inMask2Thres,
            dilateIncre=dilDisk,
            binaryMsk=True,
            axisChoice='3D'
        )
    if inMask2 is None:
        inMask2Dil = numpy.zeros(outMaskShp)

    # 3d Dilate out mask
    dilOutMsk = ((outMask + inMask2Dil + inMask1Dil) != 0) * 1

    # slicing corresction
    for slc in range(outMaskShp[0]):
        # correction baseb on outmask
        if numpy.sum(outMask[slc]) == 0:
            dilOutMsk[slc] = outMask[slc]

    return dilOutMsk


"""
##############################################################################
#Func: mask extension with/without circle
##############################################################################
"""
import skimage.morphology
import numpy
import skimage.measure
import time


def MaskExtensionCircle(
        inMask,
        direct,
        slcStrt,
        slcStp,
        refSlc,
        circle
):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["shrinkMask"] = None
    rtrnInfo["message"] = ''
    rtrnInfo["ExtendedMask"] = None
    strtSlc = None
    stopSlc = None
    refMsk = None

    # check empty total mask
    if numpy.sum(1 * (inMask != 0)) == 0:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += 'Extension: Input Mask is empty!!'
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    # correction start and finsh slice
    # !!! Assume looking ITK_SANP so 1 slice ahead!!!
    ## convert 0 to 1
    if slcStrt == 0: slcStrt = 1
    if slcStp == 0: slcStp = 1
    if refSlc == 0: refSlc = 1

    ## compare shape
    inMaskShp = numpy.shape(inMask)

    ## cannot be greater
    # get reference mask
    # !!! Assume looking ITK_SANP so 1 slice ahead!!!
    if direct == "X" or direct == "x":
        if slcStrt > inMaskShp[0]: slcStrt = inMaskShp[0]
        if slcStp > inMaskShp[0]: slcStp = inMaskShp[0]
    elif direct == "Y" or direct == "y":
        if slcStrt > inMaskShp[1]: slcStrt = inMaskShp[1]
        if slcStp > inMaskShp[1]: slcStp = inMaskShp[1]
    elif direct == "Z" or direct == "z":
        if slcStrt > inMaskShp[2]: slcStrt = inMaskShp[2]
        if slcStp > inMaskShp[2]: slcStp = inMaskShp[2]
    else:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += 'Unknown direction: {}'.format(
            direct
        )
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    ## set up range
    if slcStrt > slcStp:
        strtSlc = int(slcStp - 1)
        stopSlc = int(slcStrt)
    elif slcStrt <= slcStp:
        strtSlc = int(slcStrt - 1)
        stopSlc = int(slcStp)

    ## check refSlc
    if direct == "X" or direct == "x":
        if refSlc > inMaskShp[0]:
            rtrnInfo["error"] = True
        else:
            refSlc = int(refSlc)
    elif direct == "Y" or direct == "y":
        if refSlc > inMaskShp[1]:
            rtrnInfo["error"] = True
        else:
            refSlc = int(refSlc)
    elif direct == "Z" or direct == "z":
        if refSlc > inMaskShp[2]:
            rtrnInfo["error"] = True
        else:
            refSlc = int(refSlc)

    if rtrnInfo["error"]:
        rtrnInfo["errorMessage"] += 'Too large reference slice'.format(
            refSlc
        )
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    # get reference mask
    # !!! Assume looking ITK_SANP so 1 slice ahead!!!
    if direct == "X" or direct == "x":
        refMsk = inMask[int(refSlc) - 1]
    elif direct == "Y" or direct == "y":
        refMsk = inMask[:, refSlc - 1, :]
    elif direct == "Z" or direct == "z":
        refMsk = inMask[:, :, refSlc - 1]
    else:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += 'Unknown direction: {}'.format(
            direct
        )
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    if numpy.sum(refMsk) == 0:
        print('Empty Slice!!!')
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += 'Empty mask in slice: {} direction: {} \nForce to fill!'.format(
            refSlc,
            direct
        )

        # force to find a non-empty slice
        # search in the nearer direction
        findSlcFlg = False
        if numpy.abs(refSlc - strtSlc) >= numpy.abs(refSlc - stopSlc):
            while not findSlcFlg:
                refSlc += 1
                if refSlc > stopSlc: break

                # find mask
                if direct == "X" or direct == "x":
                    refMsk = inMask[int(refSlc) - 1]
                elif direct == "Y" or direct == "y":
                    refMsk = inMask[:, refSlc - 1, :]
                elif direct == "Z" or direct == "z":
                    refMsk = inMask[:, :, refSlc - 1]

                if numpy.sum(refMsk) != 0: findSlcFlg = True

            while not findSlcFlg:
                refSlc -= 1
                if refSlc < strtSlc: break

                # find mask
                if direct == "X" or direct == "x":
                    refMsk = inMask[int(refSlc) - 1]
                elif direct == "Y" or direct == "y":
                    refMsk = inMask[:, refSlc - 1, :]
                elif direct == "Z" or direct == "z":
                    refMsk = inMask[:, :, refSlc - 1]

                if numpy.sum(refMsk) != 0: findSlcFlg = True
        else:
            while not findSlcFlg:
                refSlc -= 1
                if refSlc < strtSlc: break

                # find mask
                if direct == "X" or direct == "x":
                    refMsk = inMask[int(refSlc) - 1]
                elif direct == "Y" or direct == "y":
                    refMsk = inMask[:, refSlc - 1, :]
                elif direct == "Z" or direct == "z":
                    refMsk = inMask[:, :, refSlc - 1]

                if numpy.sum(refMsk) != 0: findSlcFlg = True

            while not findSlcFlg:
                refSlc += 1
                if refSlc > stopSlc: break

                # find mask
                if direct == "X" or direct == "x":
                    refMsk = inMask[int(refSlc) - 1]
                elif direct == "Y" or direct == "y":
                    refMsk = inMask[:, refSlc - 1, :]
                elif direct == "Z" or direct == "z":
                    refMsk = inMask[:, :, refSlc - 1]

                if numpy.sum(refMsk) != 0: findSlcFlg = True

        # check find slices
        if findSlcFlg:
            rtrnInfo["errorMessage"] += "\nFind ref slice in: {}\n".format(refSlc)
        else:
            rtrnInfo["errorMessage"] += "\nSomething WRONG!!"
            return rtrnInfo

    # stacking if not circle fitting
    outMask = inMask
    if not circle:
        if direct == "X" or direct == "x":
            for slc in range(strtSlc, stopSlc):
                outMask[slc] = refMsk
        elif direct == "Y" or direct == "y":
            for slc in range(strtSlc, stopSlc):
                outMask[:, slc, :] = refMsk
        elif direct == "Z" or direct == "z":
            for slc in range(strtSlc, stopSlc):
                outMask[:, :, slc] = refMsk

    # circle
    else:
        # create circle
        circleMsk = numpy.zeros(numpy.shape(refMsk))
        # label slice
        labels = skimage.measure.label(refMsk)

        # region propos for information
        regions = skimage.measure.regionprops(labels)
        bubble = regions[0]  ## assume only one!
        # region information
        y0, x0 = bubble.centroid
        d = bubble.major_axis_length
        # draw circle
        coords = skimage.draw.disk((y0, x0), d / 2, shape=numpy.shape(refMsk))
        circleMsk[coords] = 1 * numpy.nanmedian(refMsk[numpy.where(refMsk != 0)])

        # stacking
        if direct == "X" or direct == "x":
            for slc in range(strtSlc, stopSlc):
                outMask[slc] = circleMsk
        elif direct == "Y" or direct == "y":
            for slc in range(strtSlc, stopSlc):
                outMask[:, slc, :] = circleMsk
        elif direct == "Z" or direct == "z":
            for slc in range(strtSlc, stopSlc):
                outMask[:, :, slc] = circleMsk

    # return information
    rtrnInfo["errorMessage"] += "Fill slices: {} -- {}".format(strtSlc, stopSlc)
    rtrnInfo["ExtendedMask"] = outMask
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Extending Mask time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "\n{}".format(rtrnInfo["processTimeMessage"])
    print("{}".format(rtrnInfo["processTimeMessage"]))

    return rtrnInfo


"""
##############################################################################
#Func: Shrink mask based on inner and outer mask and shrink ratio
##############################################################################
"""
import skimage.morphology
import numpy
import skimage.measure
import time


def ShrinkReferenceMask(
        outMask,
        inMask,
        compMsk,
        inShrkFac,
        outShrkFac,
        inMskCenX,
        inMskCenY,
        closeDisk=2,
        openDisk=1,
        inDilDisk=2
):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["shrinkMask"] = None
    rtrnInfo["message"] = ''

    # find inner and outer contour
    ## list of (n,2)-ndarrays,  n (row, column) = (y, x) coordinates
    contourCoordsOutMsk = skimage.measure.find_contours(
        image=outMask,
        level=None,
        fully_connected='low',
        positive_orientation='low',
        mask=None
    )
    contourCoordsInMsk = skimage.measure.find_contours(
        image=inMask,
        level=None,
        fully_connected='low',
        positive_orientation='low',
        mask=None
    )

    # convert to rho, theta
    ## convert to polar after move to center (row, column) = (y, x) !!!
    countourInX = contourCoordsInMsk[0][:, 1]
    countourInY = contourCoordsInMsk[0][:, 0]
    countourInX_Trans = countourInX - inMskCenX
    countourInY_Trans = countourInY - inMskCenY
    contourPolarInRhos, contourPolarInThetas = cart2pol(countourInX_Trans, countourInY_Trans)
    ## convert to polar after move to center (row, column) = (y, x) !!!
    countourOutX = contourCoordsOutMsk[0][:, 1]
    countourOutY = contourCoordsOutMsk[0][:, 0]
    countourOutX_Trans = countourOutX - inMskCenX
    countourOutY_Trans = countourOutY - inMskCenY
    contourPolarOutRhos, contourPolarOutThetas = cart2pol(countourOutX_Trans, countourOutY_Trans)

    # get all nonzero components in comp mask
    compMskCoords = numpy.where(compMsk != 0)  ## !! (y, x)
    compVals = compMsk[compMskCoords]
    compX = compMskCoords[1]
    compY = compMskCoords[0]
    ## convert to polar after move to center (row, column) = (y, x) !!!
    compX_Trans = compX - inMskCenX
    compY_Trans = compY - inMskCenY
    compRhos, compThetas = cart2pol(compX_Trans, compY_Trans)

    # empty mask for stacking
    nwCompMsk = numpy.zeros(numpy.shape(compMsk))

    if outShrkFac == 1:  # dealing with no shrinkage
        nwCompMsk = compMsk
    else:  # shrinkage
        # For each point find the shrink factor and fill correspodning position
        for pnt in range(len(compThetas)):
            # component value, rho, theta
            compRho = compRhos[pnt]
            compTheta = compThetas[pnt]
            compVal = compVals[pnt]

            # find nearest theta in outmask and inmask and rho
            idxIn, closeInVal = Matrix_Math.FindNearest(array=contourPolarInThetas, value=compTheta)
            closeInRho = contourPolarInRhos[idxIn]
            idxOut, closeOutVal = Matrix_Math.FindNearest(array=contourPolarOutThetas, value=compTheta)
            closeOutRho = contourPolarOutRhos[idxOut]
            # print("Current theta = {}, closest closeInRho = {} and closest closeOutRho = {}".format(
            #     compTheta, closeInVal, closeOutVal
            # ))

            # linear interpolation of current radial shrinking factor
            shrkFac = numpy.interp(
                x=compRho,
                xp=[closeInRho, closeOutRho],
                fp=[inShrkFac, outShrkFac]
            )  ## x-coordinate sequence is expected to be increasing
            # print("Interpretation: "
            #       "\ninMaskRho = {} inMaskFactor = {}"
            #       "\ninMaskRho = {} inMaskFactor = {}"
            #       "\nResultant factor = {}".format(
            #     closeInRho, inShrkFac, closeOutRho, outShrkFac, shrkFac,
            # ))

            # rho shrinkage
            compRhoShrk = compRho * shrkFac

            # back to x,y with center inMskCenX, inMskCenY
            compXNw, compYNw = pol2cart(rho=compRhoShrk, theta=compTheta)
            row = int(numpy.rint(compYNw) + inMskCenX)
            colm = int(numpy.rint(compXNw) + inMskCenY)
            # print("rint: row = {}; column = {}".format(row, colm))

            # fill values
            nwCompMsk[row, colm] = compVal

        # closing
        selemC = skimage.morphology.disk(closeDisk)
        selemO = skimage.morphology.disk(openDisk)
        nwCompMsk = skimage.morphology.closing(nwCompMsk, selemC)
        nwCompMsk = skimage.morphology.opening(nwCompMsk, selemO)  # improve smoothing

    # dealing with regions
    nwCompMskOne = (nwCompMsk > 0) * 1
    # Dealing with inner component shrinked mask is outside the outer shrinked mask
    inOUt = ((nwCompMskOne - outMask) > 0) * 1
    if numpy.sum(inOUt) > 0:  ## inside out
        # keep inside inside!
        ## disk
        selem2 = skimage.morphology.disk(inDilDisk)
        ## dilation
        inCorMskDil = skimage.morphology.dilation(
            image=inOUt,
            selem=selem2
        )
        ## combine
        outMask = ((outMask + inCorMskDil) > 0) * 1

        # update
        msg = "Inside component mask is outside!! Force inside by Dilation of 2 pixels!!" \
              "\nFinal outer mask area = {}" \
              "".format(numpy.sum(outMask))
        print(msg)
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += msg

    # Dealing with inner component shrinked mask is overlap with the inner shrinked mask
    # inner dilation
    ## disk
    selem3 = skimage.morphology.disk(inDilDisk)
    ## dilation
    inMskDil = skimage.morphology.dilation(
        image=inMask,
        selem=selem3
    )
    ## remove component
    overMask = ((nwCompMskOne + inMskDil) > 1) * 1
    nwCompMsOneDiff = ((nwCompMskOne - overMask) > 0) * 1
    nwCompMsk = numpy.multiply(nwCompMsOneDiff, nwCompMsk)
    ## improve wall
    outMask = ((outMask + inMskDil) > 0) * 1

    # update
    msg = "Inside component mask is forced to avoid overlap to inner by inner dilation = {}!!" \
          "\nFinal compnent mask area = {}" \
          "\nFinal outer mask area = {}".format(inDilDisk, numpy.sum(nwCompMsk), numpy.sum(outMask))
    print(msg)

    # return information
    rtrnInfo["shrinkComponentMask"] = nwCompMsk
    rtrnInfo["shrinkNewOutMask"] = outMask
    rtrnInfo["shrinkNewInMask"] = inMask

    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Shrinking mask time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
# Opening, closing, dilation, erosion, 2d and 3d
##############################################################################
"""
import numpy


def OpenCloseDilateErrodeSlices(
        dataMat,
        funcChoose,
        Thres,
        dilateIncre,
        binaryMsk,
        axisChoice,
        iterateDilate,
        sliceStarts,
        sliceStops,
        diameter
):
    # initiation
    inMat = dataMat
    direction = axisChoice

    # time
    strtT = time.time()
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["outMask"] = dataMat
    rtrnInfo["message"] = ""

    # none:
    if inMat is None:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "ERROR: None input"
        return rtrnInfo

    # shape and dtype
    inMatShp = numpy.shape(inMat)
    try:
        inMatDtype = inMat.dtype.type
    except:
        rtrnInfo["message"] += "Use default data type: numpy.int16 \n"
        inMatDtype = numpy.int16

    # compare same shape
    checkLstShp = Post_Image_Process_Functions.CompareListDimension(
        lsts=[
            sliceStarts,
            sliceStops
        ]
    )
    if checkLstShp["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "Check slices does not have the same length of the list inputs"

    # loop each case
    for case in range(len(sliceStarts)):
        # all tpye
        sliceStart = int(sliceStarts[case])
        sliceStop = int(sliceStops[case])

        # mask of slice
        if direction == 'X' or direction == 'x' or direction == '3d' or direction == '3D':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[0]:
                sliceStop = inMatShp[0] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            # morphology
            print("father: {} & {}".format(numpy.shape(inMat[sliceStart:sliceStop + 1]),
                                           numpy.sum(inMat[sliceStart:sliceStop + 1])))
            morphology = OpenCloseDilateErrode(
                dataMat=inMat[sliceStart:sliceStop + 1],
                funcChoose=funcChoose,
                Thres=Thres,
                dilateIncre=dilateIncre,
                binaryMsk=binaryMsk,
                axisChoice=axisChoice,
                iterateDilate=iterateDilate,
                diameter=diameter
            )
            # dealing error
            if morphology["error"]:
                rtrnInfo["error"] = True
                rtrnInfo["message"] += morphology["message"]
                return rtrnInfo
            else:
                print("son: {} & {}".format(numpy.shape(morphology["outMask"]), numpy.sum(morphology["outMask"])))
                rtrnInfo["outMask"][sliceStart:sliceStop + 1] = morphology["outMask"]
                print("son new: {} & {}".format(numpy.shape(rtrnInfo["outMask"]), numpy.sum(rtrnInfo["outMask"])))

        elif direction == 'Y' or direction == 'y':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[1]:
                sliceStop = inMatShp[1] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

                # morphology
                morphology = OpenCloseDilateErrode(
                    dataMat=inMat[:, sliceStart:sliceStop + 1, :],
                    funcChoose=funcChoose,
                    Thres=Thres,
                    dilateIncre=dilateIncre,
                    binaryMsk=binaryMsk,
                    axisChoice=axisChoice,
                    iterateDilate=iterateDilate,
                    diameter=diameter
                )
                # dealing error
                if morphology["error"]:
                    rtrnInfo["error"] = True
                    rtrnInfo["message"] += morphology["message"]
                    return rtrnInfo
                else:
                    rtrnInfo["outMask"][:, sliceStart:sliceStop + 1, :] = morphology["outMask"]

        elif direction == 'Z' or direction == 'z':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[2]:
                sliceStop = inMatShp[2] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

                # morphology
                morphology = OpenCloseDilateErrode(
                    dataMat=inMat[:, :, sliceStart:sliceStop + 1],
                    funcChoose=funcChoose,
                    Thres=Thres,
                    dilateIncre=dilateIncre,
                    binaryMsk=binaryMsk,
                    axisChoice=axisChoice,
                    iterateDilate=iterateDilate,
                    diameter=diameter
                )
                # dealing error
                if morphology["error"]:
                    rtrnInfo["error"] = True
                    rtrnInfo["message"] += morphology["message"]
                    return rtrnInfo
                else:
                    rtrnInfo["outMask"][:, :, sliceStart:sliceStop + 1] = morphology["outMask"]

        else:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: wrong direction: {}".format(directions)
            return rtrnInfo

    # find ranges
    rtrnInfo["outMask"] = numpy.array(rtrnInfo["outMask"], dtype=inMatDtype)
    print("son new new: {} & {}".format(numpy.shape(rtrnInfo["outMask"]), numpy.sum(rtrnInfo["outMask"])))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Multislices morphology time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete multislices morphology \n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
# Opening, closing, dilation, erosion, 2d and 3d
##############################################################################
"""
import skimage.morphology
import numpy
import time


def OpenCloseDilateErrode(
        dataMat,
        funcChoose,
        Thres=0,
        dilateIncre=2,
        binaryMsk=True,
        axisChoice='X',
        iterateDilate=False,
        diameter=False
):
    # initiation
    ## time
    strtT = time.time()
    ## return
    rtrnInfo = {
        "processTime": None,
        "processTimeMessage": "",
        "Message": "",
        "errorMessage": "",
        "error": False,
        "outMask": None
    }
    DimMsg = ""

    # Return failed for dimension less than 2D
    dimRes = Post_Image_Process_Functions.CompareArrayDimension(
        dataMat=dataMat,
        shapeD=3
    )

    if dimRes["dimensions"] < 2:
        DimMsg = "Input dimension error: input dimension is " + str(dimRes["dimensions"])
        print(DimMsg)
        rtrnInfo["error"] = True
        rtrnInfo["Message"] += DimMsg
        return rtrnInfo

    # Binarise data
    if binaryMsk:
        thresArr = dataMat > Thres
        images = numpy.array(thresArr)
    else:
        images = numpy.array(dataMat)

    # Disk
    selem = None
    if iterateDilate:
        if axisChoice == '3D':
            selem = skimage.morphology.ball(radius=1)
        else:
            selem = skimage.morphology.disk(1)
    elif not diameter:
        if axisChoice == '3D':
            selem = skimage.morphology.ball(radius=dilateIncre)
        else:
            selem = skimage.morphology.disk(dilateIncre)

    # create empty mask
    dataMatShape = numpy.shape(dataMat)
    dataMatDilate = numpy.zeros(dataMatShape)

    # for 3D data
    if dimRes["equalCompareDimension"]:
        DimMsg = DimMsg + "Slicing: " + str(axisChoice)
        # slice direction
        if axisChoice == 'X':
            for imgSlice in range(dataMatShape[0]):
                # each slice
                image = images[imgSlice]
                dialateSlice = numpy.zeros(numpy.shape(image))

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # diameter dilation
                if diameter:
                    # create circle
                    dialateSlice = numpy.zeros(numpy.shape(image))
                    # label slice
                    labels = skimage.measure.label(image)
                    # region props for information
                    regions = skimage.measure.regionprops(labels)
                    # each region
                    for bubble in regions:
                        # region information
                        y0, x0 = bubble.centroid
                        d = bubble.major_axis_length
                        lbl = bubble.label
                        # draw circle
                        coords = skimage.draw.disk((y0, x0), (dilateIncre * d / 2), shape=numpy.shape(image))
                        dialateSlice[coords] = 1 * numpy.nanmedian(image[numpy.where(labels == lbl)])

                else:
                    # Function
                    dialateSlice = ImgOpenCloseDilateErode(
                        funcChoose=funcChoose,
                        image=image,
                        selem=selem,
                        iterateDilate=iterateDilate,
                        dilateIncre=dilateIncre
                    )

                # Stacking
                dataMatDilate[imgSlice] = dialateSlice

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[0])

        # slice direction
        elif axisChoice == 'Y':
            for imgSlice in range(dataMatShape[1]):
                # each slice
                image = images[:, imgSlice, :]
                dialateSlice = numpy.zeros(numpy.shape(image))

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # diameter dilation
                if diameter:
                    # create circle
                    dialateSlice = numpy.zeros(numpy.shape(image))
                    # label slice
                    labels = skimage.measure.label(image)
                    # region props for information
                    regions = skimage.measure.regionprops(labels)
                    # each region
                    for bubble in regions:
                        # region information
                        y0, x0 = bubble.centroid
                        d = bubble.major_axis_length
                        lbl = bubble.label
                        # draw circle
                        coords = skimage.draw.disk((y0, x0), (dilateIncre * d / 2), shape=numpy.shape(image))
                        dialateSlice[coords] = 1 * numpy.nanmedian(image[numpy.where(labels == lbl)])

                else:
                    # Function
                    dialateSlice = ImgOpenCloseDilateErode(
                        funcChoose=funcChoose,
                        image=image,
                        selem=selem,
                        iterateDilate=iterateDilate,
                        dilateIncre=dilateIncre
                    )

                # Stacking
                dataMatDilate[:, imgSlice, :] = dialateSlice

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[1])

        # slice direction
        elif axisChoice == 'Z':
            for imgSlice in range(dataMatShape[2]):
                # each slice
                image = images[:, :, imgSlice]
                dialateSlice = numpy.zeros(numpy.shape(image))

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # diameter dilation
                if diameter:
                    # create circle
                    dialateSlice = numpy.zeros(numpy.shape(image))
                    # label slice
                    labels = skimage.measure.label(image)
                    # region props for information
                    regions = skimage.measure.regionprops(labels)
                    # each region
                    for bubble in regions:
                        # region information
                        y0, x0 = bubble.centroid
                        d = bubble.major_axis_length
                        lbl = bubble.label
                        # draw circle
                        coords = skimage.draw.disk((y0, x0), (dilateIncre * d / 2), shape=numpy.shape(image))
                        dialateSlice[coords] = 1 * numpy.nanmedian(image[numpy.where(labels == lbl)])

                else:
                    # Function
                    dialateSlice = ImgOpenCloseDilateErode(
                        funcChoose=funcChoose,
                        image=image,
                        selem=selem,
                        iterateDilate=iterateDilate,
                        dilateIncre=dilateIncre
                    )

                # Stacking
                dataMatDilate[:, :, imgSlice] = dialateSlice

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[2])

        # slice direction
        elif axisChoice == '3D':
            image = dataMat
            # Function
            dataMatDilate = ImgOpenCloseDilateErode(
                funcChoose=funcChoose,
                image=image,
                selem=selem,
                iterateDilate=iterateDilate,
                dilateIncre=dilateIncre
            )
            # Convert to integers
            dataMatDilate = dataMatDilate * 1

            DimMsg = DimMsg + "\nComplete 3D slices"

        else:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: wrong direction: {}".format(directions)
            return rtrnInfo

    # return information
    rtrnInfo["outMask"] = dataMatDilate
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------{} calculation time: {} s------".format(
        funcChoose,
        rtrnInfo["processTime"]
    )
    rtrnInfo["Message"] += DimMsg
    rtrnInfo["Message"] += "\nComplete image morphology: \n {}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["Message"])

    return rtrnInfo


"""
##############################################################################
#Func: image dilation, errosion, open, close
##############################################################################
"""


def ImgOpenCloseDilateErode(
        funcChoose,
        image,
        selem,
        iterateDilate,
        dilateIncre
):
    # select function
    dialateSlice = None
    if funcChoose == 'Dilation':
        # Dilates
        if not iterateDilate:
            # Morphological dilation sets a pixel at (i,j) to
            # the maximum over all pixels in the neighborhood centered at (i,j).
            # Dilation enlarges bright regions and shrinks dark regions.
            dialateSlice = skimage.morphology.dilation(
                image=image,
                selem=selem
            )
        else:
            for i in range(dilateIncre):
                image = skimage.morphology.dilation(
                    image=image,
                    selem=selem
                )
            dialateSlice = image

    elif funcChoose == 'Erosion':
        # Erosion
        if not iterateDilate:
            # Morphological dilation sets a pixel at (i,j) to
            # the maximum over all pixels in the neighborhood centered at (i,j).
            # Dilation enlarges bright regions and shrinks dark regions.
            dialateSlice = skimage.morphology.erosion(
                image=image,
                selem=selem
            )
        else:
            for i in range(dilateIncre):
                image = skimage.morphology.erosion(
                    image=image,
                    selem=selem
                )
            dialateSlice = image

    elif funcChoose == 'Closing':
        # Closing
        if not iterateDilate:
            # Morphological dilation sets a pixel at (i,j) to
            # the maximum over all pixels in the neighborhood centered at (i,j).
            # Dilation enlarges bright regions and shrinks dark regions.
            dialateSlice = skimage.morphology.closing(
                image=image,
                selem=selem
            )
        else:
            for i in range(dilateIncre):
                image = skimage.morphology.closing(
                    image=image,
                    selem=selem
                )
            dialateSlice = image

    elif funcChoose == 'Opening':
        # Opening
        if not iterateDilate:
            # Morphological dilation sets a pixel at (i,j) to
            # the maximum over all pixels in the neighborhood centered at (i,j).
            # Dilation enlarges bright regions and shrinks dark regions.
            dialateSlice = skimage.morphology.opening(
                image=image,
                selem=selem
            )
        else:
            for i in range(dilateIncre):
                image = skimage.morphology.opening(
                    image=image,
                    selem=selem
                )
            dialateSlice = image
    else:
        print("Error: do not find functino for <{}>".format(funcChoose))

    return dialateSlice


"""
##############################################################################
#Func: remove and fill mask
##############################################################################
"""
import numpy
import time


def RemoveFillEdge(
        inMsk,
        fillMsk
):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["edgeMask"] = None
    rtrnInfo["fillMask"] = None
    rtrnInfo["message"] = ''

    # check the same shape
    compareShp = Post_Image_Process_Functions.CompareArrShape(
        dataMat1=inMsk,
        dataMat2=fillMsk,
        DialogWarn=False
    )
    if compareShp["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = compareShp["errorMessage"]
        return rtrnInfo

    # create empty mat
    mskDilation2DSubtract = numpy.zeros(numpy.shape(inMsk))
    mskDilation2DOri = numpy.zeros(numpy.shape(inMsk))
    edgeOnes = numpy.zeros(numpy.shape(inMsk))

    # Binarinise
    matDataOriOnes = (fillMsk > 0) * 1
    matDataDilateOnes = (inMsk > 0) * 1

    # Subtract for edge
    edgeOnes = ((matDataDilateOnes - matDataOriOnes) > 0) * 1
    # print("edgeOnes: {}".format(numpy.sum(edgeOnes)))
    # edge mask
    mskDilation2DSubtract = numpy.multiply(edgeOnes, inMsk)
    # print("mskDilation2DSubtract: {}".format(numpy.sum(mskDilation2DSubtract)))
    # Fill with origin
    mskDilation2DOri = mskDilation2DSubtract + fillMsk

    # return information
    rtrnInfo["edgeMask"] = mskDilation2DSubtract
    rtrnInfo["fillMask"] = mskDilation2DOri
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Fill Origin Mask time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "\n{}".format(rtrnInfo["processTimeMessage"])
    print("{}".format(rtrnInfo["processTimeMessage"]))

    return rtrnInfo


"""
##############################################################################
# Dilation
##############################################################################
"""
import skimage.morphology
import numpy


def DiskDilate(
        dataMat,
        Thres=0,
        dilateIncre=2,
        binaryMsk=True,
        axisChoice='X',
        iterateDilate=False
):
    # Comparing
    DimErr = False
    DimMsg = ""

    # Return failed for dimension less than 2D
    dimRes = Post_Image_Process_Functions.CompareArrayDimension(
        dataMat=dataMat,
        shapeD=3
    )

    if dimRes["dimensions"] < 2:
        DimErr = True
        DimMsg = "Input dimension error: input dimension is " + str(dimRes["dimensions"])
        print(DimMsg)
        return [DimErr, DimMsg], 0

    # Binarise data
    if binaryMsk:
        thresArr = dataMat > Thres
        images = numpy.array(thresArr)
    else:
        images = numpy.array(dataMat)

    # Disk
    selem1 = skimage.morphology.disk(1)
    selem = skimage.morphology.disk(dilateIncre)
    ball = skimage.morphology.ball(radius=dilateIncre)

    # create empty mask
    dataMatShape = numpy.shape(dataMat)
    dataMatDilate = numpy.zeros(dataMatShape)

    # for 3D data
    if dimRes["equalCompareDimension"]:
        DimMsg = DimMsg + "Slicing: " + str(axisChoice)
        # slice direction
        if axisChoice == 'X':
            for imgSlice in range(dataMatShape[0]):
                # each slice
                image = images[imgSlice]
                dialateSlice = numpy.zeros(numpy.shape(image))

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # Dilates
                if not iterateDilate:
                    # Morphological dilation sets a pixel at (i,j) to
                    # the maximum over all pixels in the neighborhood centered at (i,j).
                    # Dilation enlarges bright regions and shrinks dark regions.
                    dialateSlice = skimage.morphology.dilation(image=image,
                                                               selem=selem)
                else:
                    for i in range(dilateIncre):
                        image = skimage.morphology.dilation(image=image,
                                                            selem=selem1)

                    dialateSlice = image

                # Stacking
                dataMatDilate[imgSlice] = dialateSlice

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[0])

        # slice direction
        if axisChoice == 'Y':
            for imgSlice in range(dataMatShape[1]):
                # each slice
                image = images[:, imgSlice, :]
                dialateSlice = numpy.zeros(numpy.shape(image))

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # Dilates
                if not iterateDilate:
                    # Morphological dilation sets a pixel at (i,j) to
                    # the maximum over all pixels in the neighborhood centered at (i,j).
                    # Dilation enlarges bright regions and shrinks dark regions.
                    dialateSlice = skimage.morphology.dilation(image=image,
                                                               selem=selem)
                else:
                    for i in range(dilateIncre):
                        image = skimage.morphology.dilation(image=image,
                                                            selem=selem1)

                    dialateSlice = image

                # Stacking
                dataMatDilate[:, imgSlice, :] = dialateSlice

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[1])

        # slice direction
        if axisChoice == 'Z':
            for imgSlice in range(dataMatShape[2]):
                # each slice
                image = images[:, :, imgSlice]
                dialateSlice = numpy.zeros(numpy.shape(image))

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # Dilates
                if not iterateDilate:
                    # Morphological dilation sets a pixel at (i,j) to
                    # the maximum over all pixels in the neighborhood centered at (i,j).
                    # Dilation enlarges bright regions and shrinks dark regions.
                    dialateSlice = skimage.morphology.dilation(image=image,
                                                               selem=selem)
                else:
                    for i in range(dilateIncre):
                        image = skimage.morphology.dilation(image=image,
                                                            selem=selem1)

                    dialateSlice = image

                # Stacking
                dataMatDilate[:, :, imgSlice] = dialateSlice

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[2])

        # slice direction
        if axisChoice == '3D':
            image = dataMat
            # Dilates
            # Morphological dilation sets a pixel at (i,j) to
            # the maximum over all pixels in the neighborhood centered at (i,j).
            # Dilation enlarges bright regions and shrinks dark regions.
            dataMatDilate = skimage.morphology.binary_dilation(image=image,
                                                               selem=ball)

            # Convert to integers
            dataMatDilate = dataMatDilate * 1

            DimMsg = DimMsg + "\nComplete 3D slices"

    print("Complete dilation")
    return [DimErr, DimMsg], dataMatDilate


"""
##############################################################################
#Func: Diameter Dilation
##############################################################################
"""
import skimage.morphology
import numpy
import skimage.measure


def DiskDilateDiameter(
        dataMat,
        Thres=0,
        dilateIncreFac=2,
        binaryMsk=True,
        axisChoice='X'
):
    # Comparing
    DimErr = False
    DimMsg = ""

    # Return failed for dimension less than 2D
    dimRes = Post_Image_Process_Functions.CompareArrayDimension(
        dataMat=dataMat,
        shapeD=3
    )

    if dimRes["dimensions"] < 2:
        DimErr = True
        DimMsg = "Input dimension error: input dimension is " + str(dimRes["dimensions"])
        print(DimMsg)
        return [DimErr, DimMsg], 0

    # Binarise data
    if binaryMsk:
        thresArr = dataMat > Thres
        images = numpy.array(thresArr)
    else:
        images = numpy.array(dataMat)

    # create empty mask
    dataMatShape = numpy.shape(dataMat)
    dataMatDilate = numpy.zeros(dataMatShape)

    # for 3D data
    if dimRes["equalCompareDimension"]:
        DimMsg = DimMsg + "Slicing: " + str(axisChoice)
        # slice direction
        if axisChoice == 'X':
            for imgSlice in range(dataMatShape[0]):
                # each slice
                image = images[imgSlice]

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # Dilation of each segment
                # empty for stacking each label region
                dilImg = numpy.zeros(numpy.shape(image))

                # label slice
                labels, nums = skimage.measure.label(image, return_num=True)

                # region props for information
                # !!! list start from 0 label start from 1!!!
                regions = skimage.measure.regionprops(labels)

                # dilate each label regio with MAX!! diameter
                for num in range(nums):
                    # label is +1
                    lbl = num + 1

                    # region bubble
                    bubble = regions[num]
                    maxD = int(bubble.major_axis_length)
                    diskD = dilateIncreFac * maxD

                    # mask out image
                    imgMsk = (labels == lbl) * 1
                    mskImg = numpy.multiply(imgMsk, image)

                    # dilation
                    # Morphological dilation sets a pixel at (i,j) to
                    # the maximum over all pixels in the neighborhood centered at (i,j).
                    # Dilation enlarges bright regions and shrinks dark regions.
                    selem = skimage.morphology.disk(diskD)
                    mskImgDil = skimage.morphology.dilation(
                        image=mskImg,
                        selem=selem
                    )

                    # stacking image keep the NEW mask!!
                    mskImgDilOnes = 1 * (mskImgDil != 0)
                    dilImgOnes = 1 * (dilImg != 0)
                    ## difference to remove dilImag
                    dilImgOnesKeep = ((dilImgOnes - mskImgDilOnes) > 0) * 1
                    dilImg = numpy.multiply(dilImgOnesKeep, dilImg) + mskImgDil

                    print(
                        "Finish X slice: {}/{} - Label {}/{}".format(
                            imgSlice,
                            dataMatShape[0],
                            lbl,
                            nums
                        )
                    )

                # Stacking
                dataMatDilate[imgSlice] = dilImg

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[0])

        # slice direction
        if axisChoice == 'Y':
            for imgSlice in range(dataMatShape[1]):
                # each slice
                image = images[:, imgSlice, :]

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # Dilation of each segment
                # empty for stacking each label region
                dilImg = numpy.zeros(numpy.shape(image))

                # label slice
                labels, nums = skimage.measure.label(image, return_num=True)

                # region props for information
                # !!! list start from 0 label start from 1!!!
                regions = skimage.measure.regionprops(labels)

                # dilate each label regio with MAX!! diameter
                for num in range(nums):
                    # label is +1
                    lbl = num + 1

                    # region bubble
                    bubble = regions[num]
                    maxD = bubble.major_axis_length
                    diskD = dilateIncreFac * maxD

                    # mask out image
                    imgMsk = (labels == lbl) * 1
                    mskImg = numpy.multiply(imgMsk, image)

                    # dilation
                    # Morphological dilation sets a pixel at (i,j) to
                    # the maximum over all pixels in the neighborhood centered at (i,j).
                    # Dilation enlarges bright regions and shrinks dark regions.
                    selem = skimage.morphology.disk(diskD)
                    mskImgDil = skimage.morphology.dilation(
                        image=mskImg,
                        selem=selem
                    )

                    # stacking image keep the NEW mask!!
                    mskImgDilOnes = 1 * (mskImgDil != 0)
                    dilImgOnes = 1 * (dilImg != 0)
                    ## difference to remove dilImag
                    dilImgOnesKeep = ((dilImgOnes - mskImgDilOnes) > 0) * 1
                    dilImg = numpy.multiply(dilImgOnesKeep, dilImg) + mskImgDil

                    print(
                        "Finish Y slice: {}/{} - Label {}/{}".format(
                            imgSlice,
                            dataMatShape[1],
                            lbl,
                            nums
                        )
                    )

                # Stacking
                dataMatDilate[imgSlice] = dilImg

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[1])

        # slice direction
        if axisChoice == 'Z':
            for imgSlice in range(dataMatShape[2]):
                # each slice
                image = images[:, :, imgSlice]

                # jump empty
                if numpy.sum(image) == 0:
                    # print("jump empty slice: " + str(imgSlice))
                    continue

                # Dilation of each segment
                # empty for stacking each label region
                dilImg = numpy.zeros(numpy.shape(image))

                # label slice
                labels, nums = skimage.measure.label(image, return_num=True)

                # region props for information
                # !!! list start from 0 label start from 1!!!
                regions = skimage.measure.regionprops(labels)

                # dilate each label regio with MAX!! diameter
                for num in range(nums):
                    # label is +1
                    lbl = num + 1

                    # region bubble
                    bubble = regions[num]
                    maxD = bubble.major_axis_length
                    diskD = dilateIncreFac * maxD

                    # mask out image
                    imgMsk = (labels == lbl) * 1
                    mskImg = numpy.multiply(imgMsk, image)

                    # dilation
                    # Morphological dilation sets a pixel at (i,j) to
                    # the maximum over all pixels in the neighborhood centered at (i,j).
                    # Dilation enlarges bright regions and shrinks dark regions.
                    selem = skimage.morphology.disk(diskD)
                    mskImgDil = skimage.morphology.dilation(
                        image=mskImg,
                        selem=selem
                    )

                    # stacking image keep the NEW mask!!
                    mskImgDilOnes = 1 * (mskImgDil != 0)
                    dilImgOnes = 1 * (dilImg != 0)
                    ## difference to remove dilImag
                    dilImgOnesKeep = ((dilImgOnes - mskImgDilOnes) > 0) * 1
                    dilImg = numpy.multiply(dilImgOnesKeep, dilImg) + mskImgDil

                    print(
                        "Finish Z slice: {}/{} - Label {}/{}".format(
                            imgSlice,
                            dataMatShape[2],
                            lbl,
                            nums
                        )
                    )

                # Stacking
                dataMatDilate[imgSlice] = dilImg

            DimMsg = DimMsg + "\nComplete slices: " + str(dataMatShape[2])

    print("Complete diameter dilation")
    return [DimErr, DimMsg], dataMatDilate


"""
##############################################################################
# Circle with radius of the image major axis + fully enclosed
##############################################################################
"""
import skimage.measure
import skimage.draw
import numpy
import copy
import skimage.morphology
import matplotlib.pyplot as plt


def CircleMajorAxis(dataMat,
                    Threshold=0,
                    jumpBPlotSlice=False,
                    jumpBPlotSliceRange=[0],
                    FullEnCls=False):
    # Fit a circle with ellipse major axis
    # binarise image
    images = dataMat > Threshold
    # create empty mask
    dataMatShape = numpy.shape(dataMat)
    cirMajAxs = numpy.zeros(dataMatShape)
    cirMajAxCrrs = numpy.zeros(dataMatShape)
    cirMajAxCrr6s = numpy.zeros(dataMatShape)
    cirFullEnclss = numpy.zeros(dataMatShape)
    cirDilates = numpy.zeros(dataMatShape)

    # for 3D data
    dataMatShapeShape = numpy.shape(dataMatShape)
    if dataMatShapeShape[0] == 3:
        # Create memory
        rArr = numpy.zeros(dataMatShape[0])
        rArrCorr = rArr
        rArrCorr6 = rArr
        coordsArr = numpy.zeros([dataMatShape[0], 2])  # rows = slices, column = 2 y0, x0!!!
        coordsArrCorr = coordsArr
        coordsArrCorr6 = coordsArr

        """
        #Initial circle fitting
        #Correct rMaj > 2 * rMin
        #Jump a range of slice
        """
        print("////////////////")
        print("Circle")
        for imgSlice in range(dataMatShape[0]):
            # each slice
            image = images[imgSlice]
            cirMajAx = numpy.zeros(numpy.shape(image))

            # jump empty
            if numpy.sum(image) == 0:
                # print("jump empty slice: " + str(imgSlice))
                continue

            # label slice
            labels = skimage.measure.label(image)

            # region propos for information
            regions = skimage.measure.regionprops(labels)

            # slice centerpoint label
            # create center plane
            emptyPlan, centerPointList, centerPlan = PlaneCenterPoint(matData=image,
                                                                      SliceAlong=0,
                                                                      flatPlan=True)
            # filter based on center plane
            cenVal = int(numpy.sum(numpy.multiply(centerPlan, labels)))

            # Background is not labeled
            # print("center label: " + str(cenVal)) !!! list start from 0 label start from 1!!!
            bubble = regions[cenVal - 1]

            # region information
            y0, x0 = bubble.centroid  # Centroid coordinate tuple (row, col)!!
            r = bubble.major_axis_length / 2.
            rMin = bubble.minor_axis_length / 2.

            # Jump initial not circular correction
            if jumpBPlotSlice:
                if not imgSlice in jumpBPlotSliceRange:  # jump slice in the range

                    # Penalise very elliptical one with previous radious
                    if r >= 2 * rMin:
                        print("Ellipse Correction Maj: " + str(r) + " Min: " + str(rMin))
                        # choose from minimum r previous or 2 * rMin
                        if rArr[imgSlice - 1] == 0:
                            r = 2 * rMin
                        else:
                            r = numpy.min([rArr[imgSlice - 1], (2 * rMin)])

            if not jumpBPlotSlice:
                # Penalise very elliptical one with previous radious
                if r >= 2 * rMin:
                    print("Ellipse Correction Maj: " + str(r) + " Min: " + str(rMin))
                    # choose from minimum r previous or 2 * rMin
                    if rArr[imgSlice - 1] == 0:
                        r = 2 * rMin
                    else:
                        r = numpy.min([rArr[imgSlice - 1], (2 * rMin)])

            # Satcking values
            rArr[imgSlice] = r
            coordsArr[imgSlice][0] = y0
            coordsArr[imgSlice][1] = x0  # !!!center may need correction!

            # plot circle
            coords = skimage.draw.disk((y0, x0), r, shape=numpy.shape(image))  # input(row follow by column!!!)
            cirMajAx[coords] = 1  # Coordinate is (Row, Colm)!!!!

            # stacking data
            cirMajAxs[imgSlice] = cirMajAx

            print("Circle \nSlice: " + str(imgSlice) + "center:\n" + str((y0, x0)) + " \n Radius:\n" + str(r))

        print("Cir%%%%%%%%%%%%%%%%")

        """
        #Circle correction
        #The radius up and down 2%
        #Position is also corrected
        """
        print("////////////////")
        print("Circle up/down correct")
        # Maj axis circle correction base on slice up and down
        UDPercent = 0.02
        rArrCorr = copy.deepcopy(rArr)
        coordsArrCorr = copy.deepcopy(coordsArr)
        for imgSlice in range(dataMatShape[0]):
            # cannot correct first and last layer
            if imgSlice < 3 or imgSlice > (dataMatShape[0] - 3):
                # update slice
                cirMajAxCrrs[imgSlice] = cirMajAxs[imgSlice]
                continue

            # Jump empty slice if there is not slice in up/down 6 slice range
            EmptySliceFlg = False
            if numpy.sum(cirMajAxs[imgSlice]) == 0:
                EmptySliceFlg = True
                # fill single empty slice
                UpEmptyFlg = True
                DownEmptyFlg = True

                # Check 6 slices up and down
                for i in range(3):
                    if numpy.sum(cirMajAxs[imgSlice - i]) != 0:
                        rUpNear = rArrCorr[imgSlice - i]
                        yUpNear = coordsArrCorr[imgSlice - i][0]
                        xUpNear = coordsArrCorr[imgSlice - i][1]
                        UpEmptyFlg = False
                        break
                # No previous slice
                if UpEmptyFlg:
                    print("No previous non-empty jump slice: " + str(imgSlice))
                    continue

                for i in range(3):
                    if numpy.sum(cirMajAxs[imgSlice + i]) != 0:
                        rDownNear = rArrCorr[imgSlice - i]
                        yDownNear = coordsArrCorr[imgSlice + i][0]
                        xDownNear = coordsArrCorr[imgSlice + i][1]
                        DownEmptyFlg = False
                        break
                        # No later slice
                if DownEmptyFlg:
                    print("No later non-empty jump slice: " + str(imgSlice))
                    continue

                # filling bilinear results for empty slice
                if not UpEmptyFlg and not DownEmptyFlg:
                    # Current slice
                    corrShape = numpy.shape(cirMajAxs[imgSlice])
                    cirMajAxCrr = numpy.zeros(corrShape)

                    # Bilinear
                    # average
                    rAve = (rUpNear + rDownNear) / 2
                    yAve = (yUpNear + yDownNear) / 2
                    xAve = (xUpNear + xDownNear) / 2

                    # update circle
                    coords = skimage.draw.disk((yAve, xAve),
                                               rAve,
                                               shape=corrShape)  # input(row follow by column!!!)
                    cirMajAxCrr[coords] = 1  # Coordinate is (Row, Colm)!!!!

                    # update slice
                    cirMajAxCrrs[imgSlice] = cirMajAxCrr

                    rArrCorr[imgSlice] = rAve
                    coordsArrCorr[imgSlice][0] = yAve
                    coordsArrCorr[imgSlice][1] = xAve

                    print("Encounter single empty slice and filled : " + str(imgSlice))
                    # print("Rows, Colomns = " + str((yAve, xAve)))

                    # plt.figure()
                    # plt.imshow(cirMajAxCrrs[imgSlice])
                    # plt.imshow(cirMajAxCrrs[imgSlice-1], alpha = 0.3)
                    # plt.imshow(cirMajAxCrrs[imgSlice+1], alpha = 0.3)
                    # plt.show()
                    # plt.pause(30)

                # jump later steps
                continue

            # double secure to jump later steps
            if EmptySliceFlg:
                continue

            # Current slice
            corrShape = numpy.shape(cirMajAxs[imgSlice])
            cirMajAxCrr = numpy.zeros(corrShape)

            # correction
            rUp = rArrCorr[imgSlice - 1]
            rCurr = rArrCorr[imgSlice]
            rDown = rArrCorr[imgSlice + 1]

            # Jump empty slice and slice between empty ones
            if rUp == 0 and rDown == 0:
                print("Jump single non-empty slice: " + str(imgSlice))
                continue

            # Both smaller or greater 5%
            if (rCurr < (1 - UDPercent) * rUp and rCurr < (1 - UDPercent) * rDown or
                    rCurr > (1 + UDPercent) * rUp and rCurr > (1 + UDPercent) * rDown):
                print("Slice: " + str(imgSlice))
                print("Correction rCurr = " + str(rCurr))
                print("rUp = " + str(rUp))
                print("rDown = " + str(rDown))

                # Dealing with first non-empty and last non-empty
                if rUp == 0:
                    # All equals to bottom
                    rAve = rDown
                    yAve = coordsArrCorr[imgSlice + 1][0]
                    xAve = coordsArrCorr[imgSlice + 1][1]

                elif rDown == 0:
                    # All equals to up
                    rAve = rUp
                    yAve = coordsArrCorr[imgSlice - 1][0]
                    xAve = coordsArrCorr[imgSlice - 1][1]

                else:  # not the first ot last slice
                    # average
                    rAve = (rUp + rDown) / 2
                    print("rAve = " + str(rAve))
                    yAve = (coordsArrCorr[imgSlice - 1][0] + coordsArrCorr[imgSlice + 1][0]) / 2
                    xAve = (coordsArrCorr[imgSlice - 1][1] + coordsArrCorr[imgSlice + 1][1]) / 2

                # update circle
                coords = skimage.draw.disk((yAve, xAve),
                                           rAve,
                                           shape=corrShape)  # input(row follow by column!!!)
                cirMajAxCrr[coords] = 1  # Coordinate is (Row, Colm)!!!!

                # print("Rows, Colomns = " + str((yAve, xAve)))
                # update slice
                cirMajAxCrrs[imgSlice] = cirMajAxCrr

                rArrCorr[imgSlice] = rAve
                coordsArrCorr[imgSlice][0] = yAve
                coordsArrCorr[imgSlice][1] = xAve

                # print("Check change values in slice: " + str(imgSlice))
                # print("rArrCorr[imgSlice] = ")
                # print(rArrCorr[imgSlice])
                # print("rArr[imgSlice] = ")
                # print(rArr[imgSlice])

            else:
                # update slice
                cirMajAxCrrs[imgSlice] = cirMajAxs[imgSlice]

        print("UD%%%%%%%%%%%%%%%%")

        """
        #Circle correction
        #3 slices up and down 0%
        #Position is also corrected
        """
        print("////////////////")
        print("Circle 6-slice correction")
        # Maj axis circle correction base on slices 3 up and 3 down
        UD6Percent = 0.00
        rArrCorr6 = copy.deepcopy(rArrCorr)
        coordsArrCorr6 = copy.deepcopy(coordsArrCorr)
        for imgSlice in range(dataMatShape[0]):
            # cannot correct first and last layer
            if imgSlice < 3 or imgSlice > (dataMatShape[0] - 4):
                # update slice
                cirMajAxCrr6s[imgSlice] = cirMajAxCrrs[imgSlice]
                continue

            # Jump empty slice
            if numpy.sum(cirMajAxCrrs[imgSlice]) == 0:
                # print("Jump empty slice: " + str(imgSlice))
                continue

            # Current slice
            corrShape = numpy.shape(cirMajAxCrrs[imgSlice])
            cirMajAxCrr6 = numpy.zeros(corrShape)

            # correction
            rCurr = rArrCorr6[imgSlice]
            rUpDown = numpy.array([rArrCorr6[imgSlice - 3],
                                   rArrCorr6[imgSlice - 2],
                                   rArrCorr6[imgSlice - 1],
                                   rArrCorr6[imgSlice + 1],
                                   rArrCorr6[imgSlice + 2],
                                   rArrCorr6[imgSlice + 3]])
            yUpDown = numpy.array([coordsArrCorr6[imgSlice - 3][0],
                                   coordsArrCorr6[imgSlice - 2][0],
                                   coordsArrCorr6[imgSlice - 1][0],
                                   coordsArrCorr6[imgSlice + 1][0],
                                   coordsArrCorr6[imgSlice + 2][0],
                                   coordsArrCorr6[imgSlice + 3][0]])
            xUpDown = numpy.array([coordsArrCorr6[imgSlice - 3][1],
                                   coordsArrCorr6[imgSlice - 2][1],
                                   coordsArrCorr6[imgSlice - 1][1],
                                   coordsArrCorr6[imgSlice + 1][1],
                                   coordsArrCorr6[imgSlice + 2][1],
                                   coordsArrCorr6[imgSlice + 3][1]])

            # Jump empty slice more than 3 slices
            if numpy.sum(rUpDown == 0) > 3:
                print("Jump slice with up and down more than 3 empty slice: " + str(imgSlice))
                continue

            # Both smaller or greater define %
            rUpDown_M15_NonZero = (rUpDown * (1 + UD6Percent)) < rCurr
            rUpDown_M15 = numpy.sum(rUpDown_M15_NonZero)
            rUpDown_L15_NonZero = (rUpDown * (1 - UD6Percent)) > rCurr
            rUpDown_L15 = numpy.sum(rUpDown_L15_NonZero)

            if rUpDown_M15 > 3:
                print("Slice: " + str(imgSlice))
                print("Correct LARGE rCurr = " + str(rCurr))
                print("rUpDown = " + str(rUpDown))

                # average nonzero
                rUpDown_M15_NonZero_Vals = numpy.multiply(rUpDown_M15_NonZero, rUpDown)
                rAve = rUpDown_M15_NonZero_Vals[numpy.nonzero(rUpDown_M15_NonZero_Vals)].mean()
                print("rAve = " + str(rAve))
                yUpDown_M15_NonZero_Vals = numpy.multiply(rUpDown_M15_NonZero, yUpDown)
                yAve = yUpDown_M15_NonZero_Vals[numpy.nonzero(yUpDown_M15_NonZero_Vals)].mean()

                xUpDown_M15_NonZero_Vals = numpy.multiply(rUpDown_M15_NonZero, xUpDown)
                xAve = xUpDown_M15_NonZero_Vals[numpy.nonzero(xUpDown_M15_NonZero_Vals)].mean()

                # update circle
                coords = skimage.draw.disk((yAve, xAve),
                                           rAve,
                                           shape=corrShape)  # input(row follow by column!!!)
                cirMajAxCrr6[coords] = 1  # Coordinate is (Row, Colm)!!!!

                # print("Rows, Colomns = " + str((coordsArr[imgSlice][0], coordsArr[imgSlice][1])))
                # update slice
                cirMajAxCrr6s[imgSlice] = cirMajAxCrr6
                rArrCorr6[imgSlice] = rAve
                coordsArrCorr6[imgSlice][0] = yAve
                coordsArrCorr6[imgSlice][1] = xAve

            elif rUpDown_L15 > 3:
                print("Slice: " + str(imgSlice))
                print("Correct SMALL rCurr = " + str(rCurr))
                print("rUpDown = " + str(rUpDown))

                # average nonzero
                rUpDown_L15_NonZero_Vals = numpy.multiply(rUpDown_L15_NonZero, rUpDown)
                rAve = rUpDown_L15_NonZero_Vals[numpy.nonzero(rUpDown_L15_NonZero_Vals)].mean()
                print("rAve = " + str(rAve))
                yUpDown_L15_NonZero_Vals = numpy.multiply(rUpDown_L15_NonZero, yUpDown)
                yAve = yUpDown_L15_NonZero_Vals[numpy.nonzero(yUpDown_L15_NonZero_Vals)].mean()

                xUpDown_L15_NonZero_Vals = numpy.multiply(rUpDown_L15_NonZero, xUpDown)
                xAve = xUpDown_L15_NonZero_Vals[numpy.nonzero(xUpDown_L15_NonZero_Vals)].mean()

                # update circle
                coords = skimage.draw.disk((yAve, xAve),
                                           rAve,
                                           shape=corrShape)  # input(row follow by column!!!)
                cirMajAxCrr6[coords] = 1  # Coordinate is (Row, Colm)!!!!

                # print("Rows, Colomns = " + str((coordsArr[imgSlice][0], coordsArr[imgSlice][1])))
                # update slice
                cirMajAxCrr6s[imgSlice] = cirMajAxCrr6
                rArrCorr6[imgSlice] = rAve
                coordsArrCorr6[imgSlice][0] = yAve
                coordsArrCorr6[imgSlice][1] = xAve

            else:
                # update slice
                cirMajAxCrr6s[imgSlice] = cirMajAxCrrs[imgSlice]

        print("6UD%%%%%%%%%%%%%%%%")

        """
        #Circle correction failure
        #fill with non-zeros slice
        #Position is also corrected
        """
        # Filling all left empty plane
        # Show warning
        WarnFlg = True
        # Average values
        rAve = rArrCorr6[numpy.nonzero(rArrCorr6)].mean()
        yArr = coordsArrCorr6[:, 0]
        xArr = coordsArrCorr6[:, 1]
        yAve = yArr[numpy.nonzero(yArr)].mean()
        xAve = xArr[numpy.nonzero(xArr)].mean()
        # Find non-zero elements
        rNonZero = numpy.nonzero(rArrCorr6)

        # Correct each slice
        for imgSlice in range(rNonZero[0][0], rNonZero[0][-1]):  # first non-zero slice to the last
            # find zero slice
            if rArrCorr6[imgSlice] == 0:
                # warning
                if WarnFlg:
                    if Save_Load_File.JumpOrExit(dispMsg="Filling emprty slices (6 slice smooth failed)!!!"):
                        # !!!for long case just use up circle!!!
                        rAve = rArrCorr6[imgSlice - 1]
                        yAve = yArr[imgSlice - 1]
                        xAve = xArr[imgSlice - 1]
                        print("yAve: " + str(yAve) + " xAve: " + str(xAve) + " rAve: " + str(rAve))
                        WarnFlg = False
                    else:
                        # do not want correction
                        break

                # Filling circle
                planeShape = numpy.shape(cirMajAxCrr6s[imgSlice])
                emptyPlane = numpy.zeros(planeShape)
                # update circle
                coords = skimage.draw.disk((yAve, xAve),
                                           rAve,
                                           shape=planeShape)  # input(row follow by column!!!)
                emptyPlane[coords] = 1  # Coordinate is (Row, Colm)!!!!

                # update slice
                rArrCorr6[imgSlice] = rAve
                coordsArrCorr6[imgSlice][0] = yAve
                coordsArrCorr6[imgSlice][1] = xAve
                cirMajAxCrr6s[imgSlice] = emptyPlane
                print("Fill Slice: " + str(imgSlice))

        print("%%%%%%%%%%%%%%%%")
        # #fully enclose
        # if not FullEnCls:
        #     cirFullEnclss[imgSlice] = cirMajAx
        # elif FullEnCls:
        #     #Current slice area
        #     sliceA = numpy.sum(image)
        #     #Current circle
        #     cirFullEncls = cirMajAx

        #     while True:
        #         #comparing area
        #         encloseA = numpy.sum(numpy.multiply(image, cirFullEncls))

        #         if sliceA <= encloseA:
        #             break

        #         #empty cirFullEncls
        #         cirFullEncls = numpy.zeros(numpy.shape(image))
        #         #increase radius by 1
        #         r += 1

        #         #plot circle
        #         coords = skimage.draw.disk((y0, x0), r, shape = numpy.shape(image)) #input(row follow by column!!!)
        #         cirFullEncls[coords] = 1 #Coordinate is (Row, Colm)!!!!

        #     #Stacking
        #     cirFullEnclss[imgSlice] = cirFullEncls

    if dataMatShapeShape[0] == 2:
        image = images
        cirMajAx = cirMajAxs

        # label slice
        labels = skimage.measure.label(image)

        # region propos for information
        regions = skimage.measure.regionprops(labels)

        # slice centerpoint label
        # create center plane
        emptyPlan, centerPointList, centerPlan = PlaneCenterPoint(matData=image,
                                                                  SliceAlong=0,
                                                                  flatPlan=True)
        # filter based on center plane
        cenVal = numpy.sum(numpy.multiply(centerPlan, labels))

        # first region is the '1' mask (for 0 and 1 case)
        bubble = regions[cenVal]

        # region information
        y0, x0 = bubble.centroid  # Centroid coordinate tuple (row, col)!!
        r = bubble.major_axis_length / 2.

        # plot circle
        coords = skimage.draw.disk((y0, x0), r, shape=numpy.shape(image))  # input(row follow by column!!!)
        cirMajAx[coords] = 1  # Coordinate is (Row, Colm)!!!!

        # stacking data
        cirMajAxs = cirMajAx

        print("Plot circle with center:\n" + str(y0, x0) + "Radius:\n" + str(r))

    return cirMajAxs, cirMajAxCrrs, cirMajAxCrr6s


"""
##############################################################################
# Stacking results with different value
##############################################################################
"""
import numpy


def StackingValues(dataMats,
                   Thress,
                   values,
                   Overlap=False):
    # check all shape is the same length
    dataMatsShape = numpy.shape(dataMats)
    ThressShape = numpy.shape(Thress)
    valuesShape = numpy.shape(values)

    # error
    if dataMatsShape[0] != ThressShape[0] or dataMatsShape[0] != valuesShape[0]:
        Save_Load_File.WarnExit(dispMsg="Not mathing length STOP!" + "\n" +
                                        "dataMatsShape" + str(dataMatsShape) + "\n" +
                                        "ThressShape" + str(ThressShape) + "\n" +
                                        "valuesShape" + str(valuesShape))

    # Create empty mask
    stckMat = numpy.zeros(numpy.shape(dataMats[0]))

    # Overlapping region keep the first input
    if not Overlap:
        # first mask
        FirstMsk = numpy.zeros(numpy.shape(dataMats[0]))
        FirstMsk = dataMats[0] > Thress[0]

        # Stacking first
        stckMat = FirstMsk * values[0]

        # stacking later
        for i in range(1, dataMatsShape[0]):
            # Following mask
            FollowMsk = dataMats[i] > Thress[i]

            # Overlapping
            OverMsk = numpy.multiply(FollowMsk, FirstMsk)

            # Correct
            FollowCorrMsk = FollowMsk - OverMsk

            # Update first mask
            FirstMsk = FollowCorrMsk + FirstMsk

            # Stacking
            stckMat = stckMat + FollowCorrMsk * values[i]

            print("Complete stacking without overlapping")
    elif Overlap:
        # stacking later
        for i in range(dataMatsShape[0]):
            # Following mask
            FollowMsk = dataMats[i] > Thress[i]

            # Stacking
            stckMat = stckMat + FollowMsk * values[i]

            print("Complete stacking with overlapping")

    # save results

    return stckMat


"""
##############################################################################
# Class for gradient and fill and connectivity
##############################################################################
"""


class GradientMat:
    def __init__(self,
                 dataMat,
                 gradBlur=False,
                 LOGBlur=False,
                 gradBlurK=3,
                 gradBlurSD=2,
                 LOGBlurK=3,
                 LOGBlurSD=2,
                 gradThres=1000,
                 lplStrt=-200,
                 lplStop=200):

        # Set initialising value
        self.gradThres = gradThres
        self.lplStrt = lplStrt
        self.lplStop = lplStop
        self.filterGradientXYMsk = None
        self.lplDataMatMskRe = None
        self.filterGradientXYMskLoG = None
        self.filledMatMsk = None
        self.filledMatClose = None
        self.connectFillOpenClose = None

        # Calcs gradient
        self.gradMatXY, _, _ = GradientCalcs(
            dataMat=dataMat,
            Blur=gradBlur,
            Blurksize=(gradBlurK, gradBlurK),
            GsnSigma=gradBlurSD
        )
        # Calculate Laplacian
        self.lplDataMat = LapGradientCalcs(
            dataMat=dataMat,
            Blur=LOGBlur,
            Blurksize=(LOGBlurK, LOGBlurK),
            GsnSigma=LOGBlurSD
        )

    def DispChosThres(self, dispFlg=False):
        if dispFlg:
            print("Check for gradient threshold value")
            # plot
            Use_Plt.PlotSixFigs(matData1=self.gradMatXY,
                                matData2=self.gradMatX,
                                matData3=self.gradMatY,
                                matData4=self.lplDataMat,
                                matData5=self.lplDataMatMsk,
                                matData6=[0],
                                fig3OverLap=False,
                                ShareX=True,
                                ShareY=True,
                                ask2to5MatData=False,
                                title=["XY Gradient", "X Gradient", "Y Gradient", "LoG", "LoG with 0",
                                       "Choose value for gradient thresholding"],
                                plotRange=[False, False, False, False, False, False])

            ans = input("Set gradient threshold ('no' for default 1000):")
            if ans != "n" and ans != "N" and ans != "no" and ans != "No" and ans != "NO":
                self.gradThres = int(ans)

            ans = input("Set laplacian start/bottom threshold ('no' for default -50):")
            if ans != "n" and ans != "N" and ans != "no" and ans != "No" and ans != "NO":
                self.lplStrt = int(ans)

            ans = input("Set laplacian stop/top threshold ('no' for default 0):")
            if ans != "n" and ans != "N" and ans != "no" and ans != "No" and ans != "NO":
                self.lplStop = int(ans)

            return self.gradThres, self.lplStrt, self.lplStop

    def Filter(self):
        # Filer gradient
        _, self.filterGradientXYMsk = FilterData(
            rangStarts=[self.gradThres],
            dataMat=self.gradMatXY,
            funType="single value greater"
        )

        # FilterLaplacian
        _, self.lplDataMatMskRe = FilterData(
            rangStarts=[self.lplStrt],
            rangStops=[self.lplStop],
            dataMat=self.lplDataMat,
            funType="boundary"
        )

        # filtered gradient with LoG
        self.filterGradientXYMskLoG = numpy.multiply(self.filterGradientXYMsk, self.lplDataMatMskRe)

    def FillOpenClsoeGradient(self, fillMat="", dilateDisk=1, diskSize=2):
        # fill and close gradient mask
        # GradientMat.Filter(self)
        self.filledMatMsk, \
        filledMatOpen, \
        self.filledMatClose = FillOpenClose(
            self.filterGradientXYMsk,
            fillMat=fillMat,
            dilateDisk=dilateDisk,
            diskSize=diskSize
        )

    def ConnectAreaFilterCenterGradient(self,
                                        fillMat="",
                                        connectType=1,
                                        diskSize=2):
        # print("Start ConnectAreaFilterCenterGradient")
        # self.refOriMsk = fillMat
        # # call fill
        # GradientMat.FillOpenClsoeGradient(self, fillMat=fillMat)
        # # print("Complete another gradient thresholding")

        # Only doing with Fill connectivity filter first
        self.connectGradFill = ConnectAreaFilterCenter(
            dataMat=self.filledMatMsk,
            refDataMat=fillMat,
            connectType=connectType
        )
        # print("Complete connectivty calculations")
        # Close connectivity
        filledMatMsk, self.connectGradFillClose = FillClose(
            toCloseMat=self.connectGradFill,
            fillMat=fillMat,
            diskSize=diskSize)
        # print("Complete closing the connectivity")

    def ConnectFillOpenCloseCenter(self, fillMat, connectType):
        # print("Start ConnectAreaFilterCenterGradient")

        # Connectivity for the center area
        self.connectFillOpenClose = ConnectAreaFilterCenter(
            dataMat=self.filledMatClose,
            refDataMat=fillMat,
            connectType=connectType
        )

        print("Complete FillOpenClose with connectivity")

    def ConnectAreaWaterShade(self):
        # water shading
        self.labels, self.WSCenterMsked, self.WSCenterMsk = WaterShadeMskCenterFilter(dataMat=self.connectFillOpenClose,
                                                                                      refDataMat=self.refOriMsk,
                                                                                      Threshold=0)


"""
##############################################################################
# Class for active contour smoothing
##############################################################################
"""


class ActiveSmth:
    def __init__(self,
                 dataMat,
                 balloonForce=-1,
                 smoothFac=1,
                 iterNo=800,
                 contourThres=0.8):
        self.dataMat = dataMat
        self.balloonForce = balloonForce
        self.smoothFac = smoothFac
        self.iterNo = iterNo
        self.contourThres = contourThres

    def ActiveSmooth(self):
        self.dataMatSmooth = ActContourSmth(self.dataMat,
                                            self.balloonForce,
                                            self.smoothFac,
                                            self.iterNo,
                                            self.contourThres)

    def PlotShowSmth(self):
        # Visualise
        # may be jump
        if Save_Load_File.JumpOrExit(dispMsg="Show active contour smoothing results?"):
            # show in axial slice
            Use_Plt.slider3Display(matData1=self.dataMat,
                                   matData2=self.dataMatSmooth,
                                   matData3=[0],
                                   fig3OverLap=True,
                                   ShareX=True,
                                   ShareY=True,
                                   ask23MatData=True,
                                   title=["CTA", "Coronary mask", "Overlapping"],
                                   plotRange=[False, False, False],
                                   winMin=[-50, 0, -50],
                                   winMax=[1000, 100, 1000])

    def PlotShowOver(self, overlayData):
        # Visualise
        # may be jump
        if Save_Load_File.JumpOrExit(dispMsg="Show active contour smoothing results over CTA?"):
            # show in axial slice
            Use_Plt.slider3Display(matData1=overlayData,
                                   matData2=self.dataMatSmooth,
                                   matData3=[0],
                                   fig3OverLap=True,
                                   ShareX=True,
                                   ShareY=True,
                                   ask23MatData=True,
                                   title=["CTA", "Coronary mask", "Overlapping"],
                                   plotRange=[True, False, True],
                                   winMin=[-50, 0, -50],
                                   winMax=[800, 100, 800])

    def ChangeBallon(self):
        if Save_Load_File.JumpOrExit(dispMsg="Change Ballon force? Only -1, 0 ,1"):
            self.balloonForce = int(input("Change Ballon force? Only -1, 0 ,1: "))

    def ChangeSmthFactor(self):
        if Save_Load_File.JumpOrExit(dispMsg="Change Smooth factor? Only 1-4"):
            self.smoothFac = int(input("Change Smooth factor? Only 1-4: "))

    def ChangeIterationNo(self):
        if Save_Load_File.JumpOrExit(dispMsg="Change iteration numbers?"):
            self.smoothFac = int(input("Change interation numbers (integer only): "))

    def SaveNifti(self, imgInfo):
        # Save results
        if Save_Load_File.JumpOrExit(dispMsg="Carry on saving results?"):
            SmthDataPath = Save_Load_File.SaveFilePath(
                dispMsg="Save avtive contour smoothing periluminal mask Nifiti file?")
            Save_Load_File.MatNIFTISave(MatData=self.dataMatSmooth, imgPath=SmthDataPath, imgInfo=imgInfo)


"""
##############################################################################
# Class for fitting circle and ellipse
##############################################################################
"""


class FitCircleEllipse:
    def __init__(self,
                 dataMat,
                 imgThres=0,
                 overlayData=[0]):
        self.dataMat = dataMat
        self.imgThres = imgThres
        self.overlayData = overlayData

    def FitMajCir(self,
                  jumpBPlotSlice=False,
                  jumpBPlotSliceRange=[0],
                  overlayData=[0]):
        # fit circle
        self.MajCir, self.MajCirCrt, self.MajCirCrt6 = CircleMajorAxis(dataMat=self.dataMat,
                                                                       Threshold=self.imgThres,
                                                                       jumpBPlotSlice=False,
                                                                       jumpBPlotSliceRange=[0])

        # overlay data
        # cannot be 1d >> new data added
        overlayDataShpShp = numpy.shape(numpy.shape(overlayData))
        if overlayDataShpShp[0] != 1:
            self.overlayData = overlayData

        # show
        FitCircleEllipse.PlotShowOver(self,
                                      overlayData=self.overlayData,
                                      mask=self.MajCirCrt6,
                                      dispMsg="Plot Major axis corrected 6 circle with overlaying?")

        # FitCircleEllipse.PlotShowOver(self,
        #                               overlayData = self.overlayData,
        #                               mask = self.MajCirCrt,
        #                               dispMsg = "Plot Major axis corrected circle with overlaying?")

        # FitCircleEllipse.PlotShowOver(self,
        #                               overlayData = self.overlayData,
        #                               mask = self.MajCir,
        #                               dispMsg = "Plot Major axis circle with overlaying?")

    def AllDilation(self, dilateIncre=2):

        self.dilateIncre = dilateIncre
        # input dilation
        msg, self.InputDilate = DiskDilate(dataMat=self.dataMat,
                                           Thres=0,
                                           dilateIncre=self.dilateIncre)

        # 6 slice smooth dilation
        msg, self.MajCirCrt6Dilate = DiskDilate(dataMat=self.MajCirCrt6,
                                                Thres=0,
                                                dilateIncre=self.dilateIncre)
        # show
        FitCircleEllipse.PlotShowOver(self,
                                      overlayData=self.overlayData,
                                      mask=self.MajCirCrt6Dilate,
                                      dispMsg="Plot Major axis corrected 6 circle Dilation with overlaying?")

        # Updown circle dilation
        msg, self.MajCirCrtDilate = DiskDilate(dataMat=self.MajCirCrt,
                                               Thres=0,
                                               dilateIncre=self.dilateIncre)

        # original circle dilation
        msg, self.MajCirDilate = DiskDilate(dataMat=self.MajCir,
                                            Thres=0,
                                            dilateIncre=self.dilateIncre)

    def PlotShowOver(self, overlayData=[0], mask=[0], dispMsg="Plot results?"):
        # Visualise
        # may be jump
        if Save_Load_File.JumpOrExit(dispMsg=dispMsg):
            # show in axial slice
            Use_Plt.slider3Display(matData1=overlayData,
                                   matData2=mask,
                                   matData3=[0],
                                   fig3OverLap=True,
                                   ShareX=True,
                                   ShareY=True,
                                   ask23MatData=True,
                                   title=["CTA", "Coronary mask", "Overlapping"],
                                   plotRange=[True, False, True],
                                   winMin=[-50, 0, -50],
                                   winMax=[800, 100, 1000])

    def SaveNifti(self,
                  MatData,
                  imgInfo,
                  dispMsg="Save circle/ellipse smoothing periluminal mask Nifiti file?",
                  ConType=False,
                  refMatData=[0]):
        # Convert data type
        refMatDataShpShp = numpy.shape(numpy.shape(refMatData))
        if ConType and refMatDataShpShp[0] != 1:
            print("Convert circlar mask data")
            convertData = Post_Image_Process_Functions.ConvertDType(refDataMat=refMatData,
                                                                    tConDataMat=MatData,
                                                                    inObj="Array")
            MatData = convertData.ConvertData

            # Save results
        if Save_Load_File.JumpOrExit(dispMsg="Carry on: saving results?"):
            self.DataPath = Save_Load_File.SaveFilePath(dispMsg=dispMsg)
            Save_Load_File.MatNIFTISave(MatData=MatData, imgPath=self.DataPath, imgInfo=imgInfo)


"""
##############################################################################
# Class for filtering tissue in range
##############################################################################
"""


class TissueFilter:
    def __init__(self,
                 dataMat,
                 rangStarts=[0],
                 rangStops=[0],
                 funType="single value",
                 overlayData=[0],
                 imgInfo=[0],
                 dispMsg="Tissue"):
        self.dataMat = dataMat
        self.rangStarts = rangStarts
        self.rangStops = rangStops
        self.funType = funType
        self.overlayData = overlayData
        self.imgInfo = imgInfo
        self.dispMsg = dispMsg

        # Filter
        TissueFilter.FilterData(self)

        # Save
        TissueFilter.SaveNifti(self,
                               MatData=self.filter,
                               imgInfo=self.imgInfo,
                               dispMsg=self.dispMsg)

    def FilterData(self):
        # Filter
        dataMatMsked, self.filter = FilterData(rangStarts=self.rangStarts,
                                               rangStops=self.rangStops,
                                               dataMat=self.dataMat,
                                               funType=self.funType)

    def SaveNifti(self,
                  MatData,
                  imgInfo,
                  dispMsg="Tissue"):
        # Save results
        if Save_Load_File.JumpOrExit(dispMsg="Carry on saving results?"):
            self.DataPath = Save_Load_File.SaveFilePath(dispMsg="Save tissue mask Nifiti file: " + dispMsg)
            Save_Load_File.MatNIFTISave(MatData=MatData, imgPath=self.DataPath, imgInfo=imgInfo)


"""
##############################################################################
#Func: run reconstruction EXE
##############################################################################
"""
import numpy
import time
import multiprocessing
import subprocess
from multiprocessing import Pool


def systemExe(exeStr):
    print("Processing: \n{}".format(exeStr))
    os.system('chcp 437')
    # os.system('administrator')
    os.system(exeStr)


def subprocessExe(exeLst):
    print('exeLst',exeLst)
    process = subprocess.Popen(exeLst,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    process.wait()

    print(process.stdout.read())


def ReconstructExeRun(dictIn,
                      multiP=True,
                      processors=8):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["listShape"] = None
    rtrnInfo["allKeys"] = None
    rtrnInfo["message"] = ''

    # input is dictionary
    if not isinstance(dictIn, dict):
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = "Input is not dictionary"
        return rtrnInfo

    # list of all keys
    rtrnInfo["allKeys"] = list(dictIn.keys())

    # create a list of list items
    ## is list
    isLst = [isinstance(dictIn[item], list) for item in rtrnInfo["allKeys"]]
    ## index of true
    isLstindex = numpy.where(isLst)[0]  # first array in tuple
    ## get shape of each list, dictIn[rtrnInfo["allKeys"][index]] dictionary item
    rtrnInfo["listShape"] = [numpy.shape(dictIn[rtrnInfo["allKeys"][index]])[0] for index in isLstindex]
    ## check all have the same shape
    try:
        lstShpTF = numpy.array(rtrnInfo["listShape"]) != rtrnInfo["listShape"][0]
        # if not all lists have the same shape
        if numpy.sum(lstShpTF) != 0:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "Not all list have the same shape"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    except:
        print("Cannot check lists!! No list input.")

    # use 8 cores
    if multiP:
        # 8 groups
        p = Pool(processors)

        # Run results
        rtrnInfo["message"] = "Run: \n"
        for lstI in range(rtrnInfo["listShape"][0]):  # loop each list element
            exeStr = ""
            exeLst = []
            for key in range(len(isLst)):  # each item in the dictionary
                if isLst[key]:  # get dictionary list and get element
                    exeStr = exeStr + str(dictIn[rtrnInfo["allKeys"][key]][lstI]) + ' '
                    exeLst.append(str(dictIn[rtrnInfo["allKeys"][key]][lstI]))
                if not isLst[key]:  # get dictionary item only
                    exeStr = exeStr + str(dictIn[rtrnInfo["allKeys"][key]]) + ' '
                    exeLst.append(str(dictIn[rtrnInfo["allKeys"][key]]))

            # replace the possible double backslash to single for the absolute path!!!
            exeStr = exeStr.replace('\\\\', '\\')

            print("Check input arguement:")
            print("\\\\\\\\\\\\\\\\\\\\\\")
            print(exeStr)
            print("\\\\\\\\\\\\\\\\\\\\\\")
            rtrnInfo["message"] += "\\\\\\\\\\\\\\\\\\\\\\\n {} \n\\\\\\\\\\\\\\\\\\\\\\".format(exeStr)

            # Run!! with multiple processors
            # p.apply_async(systemExe, args=(exeStr,))
            print(exeLst)
            p.apply_async(subprocessExe, args=(exeLst,))

        # wait for all processing
        # if multiP:
        p.close()
        p.join()
        print('All subprocesses done.')

    else:  # single processor
        # Run results
        rtrnInfo["message"] = "Run: \n"
        try:  # for lists
            for lstI in range(rtrnInfo["listShape"][0]):  # loop each list element
                exeStr = ""
                for key in range(len(isLst)):  # each item in the dictionary
                    if isLst[key]:  # get dictionary list and get element
                        exeStr = exeStr + str(dictIn[rtrnInfo["allKeys"][key]][lstI]) + ' '
                    if not isLst[key]:  # get dictionary item only
                        exeStr = exeStr + str(dictIn[rtrnInfo["allKeys"][key]]) + ' '

                # replace the possible double backslash to single for the absolute path!!!
                exeStr = exeStr.replace('\\\\', '\\')

                print("Check input arguement:")
                print("\\\\\\\\\\\\\\\\\\\\\\")
                print(exeStr)
                print("\\\\\\\\\\\\\\\\\\\\\\")
                rtrnInfo["message"] += "\\\\\\\\\\\\\\\\\\\\\\\n {} \n\\\\\\\\\\\\\\\\\\\\\\".format(exeStr)

                os.system(exeStr)
        except:  # no list
            exeStr = ""
            for key in range(len(isLst)):  # each item in the dictionary
                exeStr = exeStr + str(dictIn[rtrnInfo["allKeys"][key]]) + ' '

            # replace the possible double backslash to single for the absolute path!!!
            exeStr = exeStr.replace('\\\\', '\\')

            print("Check input arguement:")
            print("\\\\\\\\\\\\\\\\\\\\\\")
            print(exeStr)
            print("\\\\\\\\\\\\\\\\\\\\\\")
            rtrnInfo["message"] += "\\\\\\\\\\\\\\\\\\\\\\\n {} \n\\\\\\\\\\\\\\\\\\\\\\".format(exeStr)

            os.system(exeStr)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Running EXE time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete EXE running: \n {}".format(rtrnInfo["processTimeMessage"])
    print("Complete EXE running: \n {}".format(rtrnInfo["processTimeMessage"]))

    return rtrnInfo


"""
##############################################################################
#Func: Multiprocessor for active contour + dilation
##############################################################################
"""
import time
import skimage.measure
import numpy
import scipy.stats
import skimage.segmentation
import skimage.morphology
import multiprocessing
from multiprocessing import Pool  # Cannot in QT class!!!!


def ImgDilateActCon(
        filterThresHUOnes,
        initRadius,
        dilateRadius,
        cpus,
        areaThres,
        IGGAlpha,
        interation,
        ACThres,
        smoothFac,
        balloonForce,
        initConnectFilterOnes
):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = None
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ""
    rtrnInfo["activeContourOneMask"] = None

    # empty volume
    dataShape = numpy.shape(filterThresHUOnes)
    activeContourOnes = numpy.zeros(dataShape)

    # Initial level set
    initLS = skimage.segmentation.disk_level_set(
        image_shape=numpy.shape(activeContourOnes[0]),
        radius=initRadius
    )

    # create dilation disk
    selem = skimage.morphology.disk(radius=dilateRadius)

    # multiple processor
    p = Pool(cpus)
    results = []

    # active contour
    for imgSlice in range(dataShape[0]):
        mskFilterThres = filterThresHUOnes[imgSlice]
        # jump no mask
        if numpy.sum(mskFilterThres) == 0:
            print("Jump zero mask slice: " + str(imgSlice))
            rtrnInfo["message"] += "Jump zero mask slice: " + str(imgSlice) + "\n"
            continue

        # image processing
        print("Add image: {} of {}".format(imgSlice, dataShape[0]))
        rtrnInfo["message"] += "Add image: {} of {} \n".format(imgSlice, dataShape[0])
        results.append(
            p.apply_async(
                DilateActCon,
                args=(
                    mskFilterThres,
                    areaThres,
                    selem,
                    IGGAlpha,
                    interation,
                    initLS,
                    ACThres,
                    smoothFac,
                    balloonForce,
                    initConnectFilterOnes,
                    imgSlice
                )
            )
        )

    print("Processing all images")
    p.close()
    print("Close pool")
    p.join()
    print('All subprocesses done.')
    rtrnInfo["message"] += "Processing all images \nClose pool \nAll subprocesses done.\n"

    # stacking results
    print("Restacking slices:")
    rtrnInfo["message"] += "Restacking slices:\n"
    resultsOut = [result.get() for result in results]
    resultsShp = numpy.shape(resultsOut)
    print(resultsShp)
    for i in range(resultsShp[0]):
        imgSlice2 = resultsOut[i][0]
        activeContourOnes[imgSlice2] = resultsOut[i][1]
        print("Restack slice: {}".format(imgSlice2))
        rtrnInfo["message"] += "Restack slice: {}\n".format(imgSlice2)

    # return information
    rtrnInfo["activeContourOneMask"] = activeContourOnes

    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Running time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete multiple processor active contour and dilation running: \n {}".format(
        rtrnInfo["processTimeMessage"])
    print("Complete active contour and dilation running: \n {}".format(rtrnInfo["processTimeMessage"]))

    return rtrnInfo


"""
##############################################################################
#Func: single slice active contour or dilation
##############################################################################
"""


def DilateActCon(mskFilterThres,
                 areaThres,
                 selem,
                 IGGAlpha,
                 interation,
                 initLS,
                 ACThres,
                 smoothFac,
                 balloonForce,
                 initConnectFilterOnes,
                 imgSlice):
    # area less than area defined pixels using simple dilation radius
    if numpy.sum(mskFilterThres) <= areaThres:
        print("Slice: {} Dilation - Area: {}".format(str(imgSlice), (numpy.sum(mskFilterThres))))
        ls = skimage.morphology.dilation(image=mskFilterThres,
                                         selem=selem)

    else:
        print("Slice: {} Active contour - Area: {}".format(str(imgSlice), (numpy.sum(mskFilterThres))))
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
            print("Slice: {} Fail active contour - use dilation".format(str(imgSlice)))
            ls = skimage.morphology.dilation(image=initConnectFilterOnes[imgSlice],
                                             selem=selem)

    # stacking results
    # self.activeContourOnes[imgSlice] = ls
    print("Finish slice: {} - Resultant area: {}".format(str(imgSlice), str(numpy.sum(ls))))

    return [imgSlice, ls]


"""
##############################################################################
#Func: cartesian to polar coordinate
##############################################################################
"""


def cart2pol(x, y):
    rho = numpy.sqrt(x ** 2 + y ** 2)
    theta = numpy.arctan2(y, x)
    return rho, theta


"""
##############################################################################
#Func: polar to cartesian coordinate
##############################################################################
"""


def pol2cart(rho, theta):
    x = rho * numpy.cos(theta)
    y = rho * numpy.sin(theta)
    return x, y


"""
##############################################################################
#Func: coordinates to mask
##############################################################################
"""
import scipy.ndimage
import skimage.morphology


def fillMask(x, y, mask):
    # empty mask
    maskShp = numpy.shape(mask)
    r_mask = numpy.zeros(maskShp)

    # row column
    row = numpy.squeeze(y)
    colm = numpy.squeeze(x)

    # Closing for not touched head and tail
    r = numpy.ceil(
        numpy.sqrt(
            (row[0] - row[-1]) ** 2 + (colm[0] - colm[-1]) ** 2
        )
    )

    print("Closing radius: {}".format(r))

    # Dealing with boundaries
    ## int row and colums
    intRows = numpy.round(row).astype('int')
    intCols = numpy.round(colm).astype('int')
    # dealing with edges
    if numpy.any(intRows >= maskShp[0]) or \
            numpy.any(intCols >= maskShp[1]):
        # cannot create mask
        print("Too large row or cloumn number cannot create mask")
        return r_mask
    else:
        # Create a contour image by using the contour coordinates rounded to their nearest integer value
        r_mask[intRows, intCols] = 1

        # Closing then fill
        # Create disk
        selem = skimage.morphology.disk(r)
        # closing
        r_mask = skimage.morphology.closing(r_mask, selem)

        # Fill in the hole created by the contour boundary
        r_mask = scipy.ndimage.binary_fill_holes(r_mask)

        return r_mask


"""
##############################################################################
#Func: sorting array with/without reference array
##############################################################################
"""

import time


def sortArray(array, singleArray=True, col=0, refArray=None):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = None
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["sortRefArray"] = None
    rtrnInfo["sortArray"] = None
    rtrnInfo["message"] = ""

    # init
    idx = None
    outArray = None
    outRefArray = None

    # single array with column in array
    if singleArray:
        # first column
        list1 = array[:, col]

        # sort
        idx = numpy.argsort(list1)

        # rearrange array
        outArray = array[idx]

    elif refArray is not None:
        # sort
        refDi
        mension = numpy.shape(numpy.shape(refArray))[0]
        msg = "Sorting with reference array of dimension: {}\n".format(refDimension)
        rtrnInfo["message"] += msg
        print(msg)
        if refDimension == 2:  # not 1d array
            idx = numpy.argsort(refArray[:, col])
        elif refDimension == 1:
            idx = numpy.argsort(refArray)
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "Sorting array not implement 3d Matrix!!!"
            print(rtrnInfo["errorMessage"])

        # rearrange array
        outRefArray = refArray[idx]
        outArray = array[idx]

    elif refArray is None:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = "Sorting array need reference array!!!"
        print(rtrnInfo["errorMessage"])

    # return information
    rtrnInfo['sortArray'] = outArray
    rtrnInfo['sortRefArray'] = outRefArray

    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Sorting time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: spline with the same or new reference points
##############################################################################
"""
import skimage.measure
import skimage.segmentation
import skimage.morphology
import numpy
import scipy.interpolate


def SplineRefPoints(refPnts, inControlPnts, orderK=None, smoothS=None, newRef=False, newRefPnts=None):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["ControlPoints"] = None
    rtrnInfo["sortArray"] = None
    rtrnInfo["message"] = ""

    # init
    outControlPnts = None
    inControlPntsNN = None
    refPntsNN = None
    refPntsOld = None
    # squeeze inputs
    refPnts = numpy.squeeze(refPnts)
    inControlPnts = numpy.squeeze(inControlPnts)

    # default
    if orderK is None:
        rtrnInfo["message"] += "\nNo input of spline order K use '3'"
        orderK = 3

    if smoothS is None:
        rtrnInfo["message"] += "\nNo input of spline smooth factor use 1/2 of reference point number"
        smoothS = len(refPnts) - numpy.sqrt(len(refPnts) * 2)

    # remove NONE in array!!!
    # print(numpy.isnan(inControlPnts))
    # print(inControlPnts)
    removeNan = False
    if numpy.sum(numpy.isnan(refPnts)) > 0:
        rtrnInfo["message"] += "\n!!!!!!!!!!!!!NONE in Spline reference array!!!!!!!!!!!!!"
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += "Reference points have NONE!!! STOP!"
        removeNan = True
        print("\n!!!!!!!!!!!!!NONE in Spline reference array!!!!!!!!!!!!!")
        return rtrnInfo
    elif numpy.sum(numpy.isnan(inControlPnts)) > 0:
        rtrnInfo["message"] += "\n!!!!!!!!!!!!!NONE in Spline control value array!!!!!!!!!!!!!"
        removeNan = True
        print("\n!!!!!!!!!!!!!NONE in Spline control value array!!!!!!!!!!!!!")

        if numpy.sum(numpy.isnan(inControlPnts)) > numpy.sum(~numpy.isnan(inControlPnts)):  # too many NONEs!
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] += "Too many NONE in control points!!! STOP!"
            return rtrnInfo
    else:
        rtrnInfo["message"] += "\nNo None values"
        inControlPntsNN = inControlPnts
        refPntsNN = refPnts
        refPntsOld = refPnts

    if removeNan:
        rtrnInfo["message"] += "\n!!Remove NONE!!"
        refPntsOld = refPnts
        inControlPntsOld = inControlPnts
        # remove reference
        refPnts1 = refPntsOld[~numpy.isnan(refPntsOld)]
        inControlPnts1 = inControlPntsOld[~numpy.isnan(refPntsOld)]
        # remove control
        inControlPntsNN = inControlPnts1[~numpy.isnan(inControlPnts1)]
        refPntsNN = refPnts1[~numpy.isnan(inControlPnts1)]

        # check
        if numpy.sum(numpy.isnan(refPnts)) > 0:
            rtrnInfo["message"] += "\n!!!!!!!!!!!!!NONE Problem is NOT fixed in reference!!!!!!!!!!!!!"
        if numpy.sum(numpy.isnan(inControlPnts)) > 0:
            rtrnInfo["message"] += "\n!!!!!!!!!!!!!NONE Problem is NOT fixed in control values!!!!!!!!!!!!!"

    if not newRef:
        rtrnInfo["message"] += "\nUse old reference point for spline resampling."
        # resampling
        tck = scipy.interpolate.splrep(
            refPntsNN,
            inControlPntsNN,
            k=orderK,
            s=smoothS)
        ## get control points
        outControlPnts = numpy.squeeze(
            scipy.interpolate.splev(refPntsOld, tck))  # reduce the sameple from 2d to 1D/0D
    elif newRef and newRefPnts is not None:
        rtrnInfo["message"] += "\nUse NEW reference point for spline resampling."
        # resampling
        tck = scipy.interpolate.splrep(
            refPntsNN,
            inControlPntsNN,
            k=orderK,
            s=smoothS)
        ## get control points
        outControlPnts = numpy.squeeze(
            scipy.interpolate.splev(newRefPnts, tck))
    elif newRef and newRefPnts is not None:
        rtrnInfo["message"] += "\nUse OLD reference point for spline resampling. No NEW reference points given!!"
        # resampling
        tck = scipy.interpolate.splrep(
            refPntsNN,
            inControlPntsNN,
            k=orderK,
            s=smoothS)
        ## get control points
        outControlPnts = numpy.squeeze(
            scipy.interpolate.splev(refPntsOld, tck))  # reduce the sameple from 2d to 1D/0D

    # return information
    rtrnInfo['ControlPoints'] = outControlPnts
    rtrnInfo['ControlPointsSqueezed'] = numpy.squeeze(outControlPnts)  # reduce the sameple from 2d to 1D/0D
    # print(rtrnInfo['ControlPointsSqueezed'])

    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Spline time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: spline radial smoothing and planar smoothing
##############################################################################
"""
import skimage.measure
import skimage.segmentation
import skimage.morphology
import numpy
import scipy.interpolate
import matplotlib.pyplot as plt
import time


def SplineSmooth3D(
        maskData,
        radialSamplingSize,
        initSplineSmooth,
        initRadialSplineOrder,
        vertRadialSplineOrder,
        vertSplineSmoothFac,
        resInt,
        planeSmoothOrder,
        planeSplineSmoothFac
):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["SmoothMask"] = None
    rtrnInfo["message"] = ""

    # cubic spline to get k control points
    initSplineSmooth = initSplineSmooth  # no smooth interpolation
    # print("initSplineSmooth = {}".format(initSplineSmooth))

    # empty volume to stacking radial inital control point
    maskDataShape = numpy.shape(maskData)
    initVertialControl = numpy.zeros([maskDataShape[0], radialSamplingSize])
    verticalSlices = numpy.zeros([maskDataShape[0], 1])
    sliceContourpoints = numpy.zeros([maskDataShape[0], 1])
    sliceCentroid = numpy.zeros([maskDataShape[0], 2])

    # sampling theta
    sampleTheta = numpy.linspace(start=-numpy.pi, stop=numpy.pi, num=radialSamplingSize, endpoint=False)

    # get inital radial control points at each depth with little smoothing
    for imgSlice in range(maskDataShape[0]):
        # image data
        img = maskData[imgSlice]

        # jump empty slice
        if numpy.sum(img) == 0:
            msg = "Empty slice: {}".format(imgSlice)
            # print(msg)
            continue

        # get contour of image https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.find_contours
        ## list of (n,2)-ndarrays,  n (row, column) = (y, x) coordinates
        contourCoords = skimage.measure.find_contours(
            image=img,
            level=None,
            fully_connected='low',
            positive_orientation='low',
            mask=None
        )

        # find center
        ## label the image with connectivity
        label_img = skimage.measure.label(img)
        ## get each region information
        regions = skimage.measure.regionprops_table(label_img, properties=['label', 'centroid'])
        ## get labelled img all labels include 0
        unqiNum, count = numpy.unique(label_img, return_counts=True)
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
        contourPolarRho, contourPolarTheta = cart2pol(countourX_Trans, countourY_Trans)

        # get contour points
        sliceContourpoints[imgSlice] = numpy.shape(contourCoords[0])[0]
        msg = "Slice: {} " \
              "\ncontour points: {}" \
              "\nCentroid: {}".format(imgSlice, sliceContourpoints[imgSlice], sliceCentroid[imgSlice])
        # print(msg)

        # cubic B-spline representation of a 1-D curvev !! xb <= x <= xe
        # sort data in order
        contourPolar = numpy.array([contourPolarTheta, contourPolarRho])
        sortContourPolar = sortArray(contourPolar.T, singleArray=True, col=0, refArray=None)['sortArray']
        sortContourPolarTheta = sortContourPolar[:, 0]
        sortContourPolarRho = sortContourPolar[:, 1]

        ## get control points
        sampleRhoRtrnInfo = SplineRefPoints(
            refPnts=sortContourPolarTheta,
            inControlPnts=sortContourPolarRho,
            orderK=initRadialSplineOrder,
            smoothS=initSplineSmooth,
            newRef=True,
            newRefPnts=sampleTheta
        )
        ## dealing with error
        if not sampleRhoRtrnInfo["error"]:
            sampleRho = sampleRhoRtrnInfo['ControlPointsSqueezed']
        elif sampleRhoRtrnInfo["error"]:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = sampleRhoRtrnInfo["errorMessage"]
            return rtrnInfo

        ## stacking data
        verticalSlices[imgSlice] = imgSlice
        initVertialControl[imgSlice] = sampleRho

    # Remove whole zero rows
    verticalSlicesNon0 = verticalSlices[~numpy.all(verticalSlices == 0, axis=1)]
    initVertialControlNon0 = initVertialControl[~numpy.all(initVertialControl == 0, axis=1)]
    sliceCentroidNon0 = sliceCentroid[~numpy.all(sliceCentroid == 0, axis=1)]

    # Check errors: check same size
    if numpy.shape(verticalSlicesNon0)[0] != numpy.shape(initVertialControlNon0)[0]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += "\n!!Control points are not the same size!!"
        print("!!Control points are not the same size!!")
    # check none
    totalInitVertialControlNon0 = numpy.sum(~numpy.all(initVertialControl == 0, axis=1))
    totalInitVertialControlNotNan = numpy.sum(~numpy.all(initVertialControl == None, axis=1))
    if totalInitVertialControlNotNan / totalInitVertialControlNon0 < 0.8:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += "\n!!More than 80% of slices are NONE!!"
        print("!!More than 80% of slices are NONE!!")
        return rtrnInfo

    # vertical spline choice
    m0 = numpy.shape(verticalSlicesNon0)[0]
    vertSplineSmooth = int(m0 * vertSplineSmoothFac)
    # [0, int(m0/20), int(m0/10), int(m0/7), int(m0/4), int(m0/2), int(m0-numpy.sqrt(m0*2)), int(m0)] # m0 / 2 is good!!

    # vertical row sorting into order
    sortVertical = sortArray(
        array=numpy.concatenate((sliceCentroidNon0, initVertialControlNon0), axis=1),
        singleArray=False,
        col=0,
        refArray=verticalSlicesNon0
    )
    sortVertSlcN0 = sortVertical['sortArray'][:, 2:]
    sortCentroidN0 = sortVertical['sortArray'][:, 0:2]  # sorted centroid
    sortVertCntrlN0 = sortVertical['sortRefArray']

    # empty fro satcking
    VertialControl = numpy.zeros(numpy.shape(sortVertSlcN0))
    centroidControl = numpy.zeros(numpy.shape(sortCentroidN0))

    # centroid smoothing
    ## x0
    x0RtrnInfo = SplineRefPoints(
        refPnts=sortVertCntrlN0,
        inControlPnts=sortCentroidN0[:, 0],
        orderK=vertRadialSplineOrder,
        smoothS=vertSplineSmooth,
        newRef=False,
        newRefPnts=None
    )
    ### dealing with error
    if not x0RtrnInfo["error"]:
        centroidControl[:, 0] = x0RtrnInfo['ControlPointsSqueezed']
    elif x0RtrnInfo["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = x0RtrnInfo["errorMessage"]
        return rtrnInfo

    ## y0
    y0RtrnInfo = SplineRefPoints(
        refPnts=sortVertCntrlN0,
        inControlPnts=sortCentroidN0[:, 1],
        orderK=vertRadialSplineOrder,
        smoothS=vertSplineSmooth,
        newRef=False,
        newRefPnts=None
    )
    ### dealing with error
    if not y0RtrnInfo["error"]:
        centroidControl[:, 1] = y0RtrnInfo['ControlPointsSqueezed']
    elif y0RtrnInfo["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = y0RtrnInfo["errorMessage"]
        return rtrnInfo

    # vertical resampling
    for radialDir in range(len(sampleTheta)):
        # single direction vertical points
        verticalPnts = sortVertSlcN0[:, radialDir]

        print(sortVertCntrlN0)
        print(verticalPnts)

        # resampling
        VertialControlRtrnInfo = SplineRefPoints(
            refPnts=sortVertCntrlN0,
            inControlPnts=verticalPnts,
            orderK=vertRadialSplineOrder,
            smoothS=vertSplineSmooth,
            newRef=False,
            newRefPnts=None
        )
        ### dealing with error
        if not VertialControlRtrnInfo["error"]:
            VertialControl[:, radialDir] = VertialControlRtrnInfo['ControlPointsSqueezed']
        elif VertialControlRtrnInfo["error"]:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = VertialControlRtrnInfo["errorMessage"]
            return rtrnInfo

    # create empty volume
    smoothMask = numpy.zeros(maskDataShape)

    # slice resampling
    for ver in range(len(sortVertCntrlN0)):
        # get info
        Rho = VertialControl[ver]
        slc = int(sortVertCntrlN0[ver][0])  # need integer input
        ## centroid
        x0 = centroidControl[ver][0]
        y0 = centroidControl[ver][1]
        ## resample contour points
        pnts = int(sliceContourpoints[slc]) * resInt
        planeTheta = numpy.linspace(start=-numpy.pi, stop=numpy.pi, num=pnts, endpoint=False)

        # resampling based on the current points
        planeRadialSpline = int(planeSplineSmoothFac * sliceContourpoints[slc])

        # resampling
        planeRhoRtrnInfo = SplineRefPoints(
            refPnts=sampleTheta,
            inControlPnts=Rho,
            orderK=planeSmoothOrder,
            smoothS=planeRadialSpline,
            newRef=True,
            newRefPnts=planeTheta
        )
        ### dealing with error
        if not planeRhoRtrnInfo["error"]:
            planeRho = planeRhoRtrnInfo['ControlPoints']
        elif planeRhoRtrnInfo["error"]:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = planeRhoRtrnInfo["errorMessage"]
            return rtrnInfo

        # convert back to cartesian
        # ## vertial smooth
        # xOriVer, yOriVer = pol2cart(Rho, sampleTheta)
        # xVer = xOriVer + x0
        # yVer = yOriVer + y0

        ## smoothed results
        xOri, yOri = pol2cart(planeRho, planeTheta)
        x = xOri + x0
        y = yOri + y0

        # new mask
        smoothMask[slc] = fillMask(x=x, y=y, mask=smoothMask[slc])

        # msg
        msg = "Complete horizontal slice: {}".format(slc)
        print(msg)

    # return information
    rtrnInfo['SmoothMask'] = smoothMask

    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Spline Smoothing time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete spling volume smoothing\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: Fill mask to 3D image
##############################################################################
"""
import skimage.draw
import skimage.segmentation
import skimage.morphology
import numpy
import time


def FillMask3D(
        inMat,
        directions,
        maskTypes,
        verticalLengths,
        horizontalLengths,
        sliceStarts,
        sliceStops,
        posititionFirsts,
        positionSeconds,
        binary=True,
        fillOriginal=True
):
    # initiation
    # time
    strtT = time.time()
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["outMask"] = None
    rtrnInfo["message"] = ""

    # shape
    inMatShp = numpy.shape(inMat)
    try:
        inMatDtype = inMat.dtype.type
    except:
        rtrnInfo["message"] += "Use default data type: numpy.int16 \n"
        inMatDtype = numpy.int16

    # compare same shape
    checkLstShp = Post_Image_Process_Functions.CompareListDimension(
        lsts=[
            horizontalLengths,
            verticalLengths,
            sliceStarts,
            sliceStops,
            posititionFirsts,
            positionSeconds
        ]
    )
    if checkLstShp["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "FillMask3D does not have the same length of the list inputs"

    # binary input
    if binary:
        inMat = 1 * (inMat != 0)

    # no initial mask
    if not fillOriginal:
        inMat=numpy.zeros(numpy.shape(inMat))

    # loop each list element
    # single direction and mask
    directUpdate = True
    maskUpdate = True
    if not numpy.shape(directions):
        direction = directions
        directUpdate = False
        rtrnInfo["message"] = "Single direction input\n"
    if not numpy.shape(maskTypes):
        maskType = maskTypes
        maskUpdate = False
        rtrnInfo["message"] = "Single mask input\n"

    for case in range(len(horizontalLengths)):
        # all tpye
        horizontalLength = int(horizontalLengths[case])
        verticalLength = int(verticalLengths[case])
        sliceStart = int(sliceStarts[case])
        sliceStop = int(sliceStops[case])
        posititionFirst = int(posititionFirsts[case])
        positionSecond = int(positionSeconds[case])

        print("###################################")
        print('sliceStart')
        print(sliceStart)
        print('sliceStop')
        print(sliceStop)

        # dealing with direction & mask
        if directUpdate: direction = directions[case]
        if maskUpdate: maskType = maskTypes[case]

        if direction == 'X' or direction == 'x':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[0]:
                sliceStop = inMatShp[0] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            # create empty slice
            segmentation = numpy.zeros((inMatShp[1], inMatShp[2]))
            # create mask
            if maskType == 'rectangle':
                rr, cc = skimage.draw.rectangle(
                    start=(positionSecond, posititionFirst),  # ([plane,] row, column)
                    end=(positionSecond + verticalLength, posititionFirst + horizontalLength),  # ([plane,] row, column)
                    shape=(inMatShp[1], inMatShp[2])
                )  # rr cc
                segmentation[rr.astype(int), cc.astype(int)] = 1
            elif maskType == 'ellipse':
                rr, cc = skimage.draw.ellipse(
                    r=positionSecond,
                    c=posititionFirst,
                    r_radius=verticalLength / 2,
                    c_radius=horizontalLength / 2,
                    shape=(inMatShp[1], inMatShp[2])
                )
                segmentation[rr.astype(int), cc.astype(int)] = 1

            # stack segmentation
            for slc in range(sliceStart, sliceStop + 1):
                print("slc: {}".format(slc))
                inMat[slc] = segmentation

        elif direction == 'Y' or direction == 'y':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[1]:
                sliceStop = inMatShp[1] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            # create empty slice
            segmentation = numpy.zeros((inMatShp[0], inMatShp[2]))
            # create mask
            if maskType == 'rectangle':
                rr, cc = skimage.draw.rectangle(
                    start=(positionSecond, posititionFirst),  # ([plane,] row, column)
                    end=(positionSecond + verticalLength, posititionFirst + horizontalLength),  # ([plane,] row, column)
                    shape=(inMatShp[0], inMatShp[2])
                )
                segmentation[rr.astype(int), cc.astype(int)] = 1
            elif maskType == 'ellipse':
                rr, cc = skimage.draw.ellipse(
                    r=positionSecond,
                    c=posititionFirst,
                    r_radius=verticalLength / 2,
                    c_radius=horizontalLength / 2,
                    shape=(inMatShp[0], inMatShp[2])
                )
                segmentation[rr.astype(int), cc.astype(int)] = 1

            # stack segmentation
            for slc in range(sliceStart, sliceStop + 1):
                inMat[:, slc, :] = segmentation

        elif direction == 'Z' or direction == 'z':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[2]:
                sliceStop = inMatShp[2] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            # create empty slice
            segmentation = numpy.zeros((inMatShp[0], inMatShp[1]))
            # create mask
            if maskType == 'rectangle':
                rr, cc = skimage.draw.rectangle(
                    start=(positionSecond, posititionFirst),  # ([plane,] row, column)
                    end=(positionSecond + verticalLength, posititionFirst + horizontalLength),  # ([plane,] row, column)
                    shape=(inMatShp[0], inMatShp[1])
                )
                segmentation[rr, cc] = 1
            elif maskType == 'ellipse':
                rr, cc = skimage.draw.ellipse(
                    r=positionSecond,
                    c=posititionFirst,
                    r_radius=verticalLength / 2,
                    c_radius=horizontalLength / 2,
                    shape=(inMatShp[0], inMatShp[1])
                )
                segmentation[rr.astype(int), cc.astype(int)] = 1

            # stack segmentation
            for slc in range(sliceStart, sliceStop + 1):
                inMat[:, :, slc] = segmentation

    # return information
    rtrnInfo['outMask'] = numpy.array(inMat, dtype=inMatDtype)

    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Fill in mask time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete mask fill in\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: Fill & replace mask from reference mask to 3D image
##############################################################################
"""
import numpy
import time


def FillReplaceMask3D(
        inMat,
        inReplaceAddMat,
        directions,
        maskTypes,
        sliceStarts,
        sliceStops
):
    # initiation
    # time
    strtT = time.time()
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["outMask"] = None
    rtrnInfo["message"] = ""

    # chedck none empty
    if inMat is None or \
            inReplaceAddMat is None:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "None Mask Input!!"
        return rtrnInfo

    # compare shape
    compareShp = Post_Image_Process_Functions.CompareArrShape(
        dataMat1=inMat,
        dataMat2=inReplaceAddMat,
        DialogWarn=False)
    if compareShp['error']:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += compareShp["errorMessage"]
        return rtrnInfo

    # shape and dtype
    inMatShp = numpy.shape(inMat)
    try:
        inMatDtype = inMat.dtype.type
    except:
        rtrnInfo["message"] += "Use default data type: numpy.int16 \n"
        inMatDtype = numpy.int16

    # compare same shape
    checkLstShp = Post_Image_Process_Functions.CompareListDimension(
        lsts=[
            sliceStarts,
            sliceStops
        ]
    )
    if checkLstShp["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "Fill/Replace does not have the same length of the list inputs"

    # loop each list element
    # single direction and mask
    directUpdate = True
    maskUpdate = True
    if not numpy.shape(directions):
        direction = directions
        directUpdate = False
        rtrnInfo["message"] = "Single direction input\n"
    if not numpy.shape(maskTypes):
        maskType = maskTypes
        maskUpdate = False
        rtrnInfo["message"] = "Single mask input\n"

    for case in range(len(sliceStarts)):
        # all tpye
        sliceStart = int(sliceStarts[case])
        sliceStop = int(sliceStops[case])

        # dealing with direction & mask
        if directUpdate: direction = directions[case]
        if maskUpdate: maskType = maskTypes[case]

        if direction == 'X' or direction == 'x':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[0]:
                sliceStop = inMatShp[0] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            if maskType == 'add':
                # stack segmentation
                for slc in range(sliceStart, sliceStop + 1):
                    inMat[slc] = numpy.array(
                        ((inMat[slc] + inReplaceAddMat[slc]) != 0) * 1,
                        dtype=inMatDtype
                    )
            elif maskType == 'replace':
                for slc in range(sliceStart, sliceStop + 1):
                    inMat[slc] = inReplaceAddMat[slc]

        elif direction == 'Y' or direction == 'y':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[1]:
                sliceStop = inMatShp[1] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            if maskType == 'add':
                # stack segmentation
                for slc in range(sliceStart, sliceStop + 1):
                    inMat[:, slc, :] = numpy.array(
                        ((inMat[:, slc, :] + inReplaceAddMat[:, slc, :]) != 0) * 1,
                        dtype=inMatDtype
                    )
            elif maskType == 'replace':
                for slc in range(sliceStart, sliceStop + 1):
                    inMat[:, slc, :] = inReplaceAddMat[:, slc, :]

        elif direction == 'Z' or direction == 'z':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[2]:
                sliceStop = inMatShp[2] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            if maskType == 'add':
                # stack segmentation
                for slc in range(sliceStart, sliceStop + 1):
                    inMat[:, :, slc] = numpy.array(
                        ((inMat[:, :, slc] + inReplaceAddMat[:, :, slc]) != 0) * 1,
                        dtype=inMatDtype
                    )
            elif maskType == 'replace':
                for slc in range(sliceStart, sliceStop + 1):
                    inMat[:, :, slc] = inReplaceAddMat[:, :, slc]

    # return information
    rtrnInfo['outMask'] = inMat

    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Fill/Replace mask time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete mask fill/replace in\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: compare mask area/volume with value
##############################################################################
"""
import numpy


def compareMaskAreaVolumeValue(
        inMat,
        compareType,
        rangeStart,
        rangeStop,
        binary=True,
):
    # binary
    if binary:
        checkMat = 1 * (inMat != 0)
    else:
        checkMat = inMat

    # sum
    compareVal = numpy.sum(checkMat)
    # print(compareVal)

    # compare
    compareResult = None
    if compareType == "single value":
        compareResult = compareVal == rangeStart

    elif compareType == "not single value":
        compareResult = compareVal != rangeStart

    elif compareType == "boundary":
        if rangeStart > rangeStop:  # flip wrong range
            temp = rangeStart
            rangeStart = rangeStop
            rangeStop = temp
        compareResult = rangeStart <= compareVal <= rangeStop

    elif compareType == "outside boundary":
        if rangeStart > rangeStop:  # flip wrong range
            temp = rangeStart
            rangeStart = rangeStop
            rangeStop = temp
        compareResult = compareVal <= rangeStart or compareVal >= rangeStop

    elif compareType == "single value greater":
        compareResult = compareVal > rangeStart

    elif compareType == "single value less":
        compareResult = compareVal < rangeStart

    return compareResult


"""
##############################################################################
#Func: identify groups of continuous numbers in a list
##############################################################################
"""
import more_itertools


def find_ranges(iterable):
    """Yield range of consecutive numbers."""
    for group in more_itertools.consecutive_groups(iterable):
        group = list(group)
        if len(group) == 1:
            yield group[0]
        else:
            yield group[0], group[-1]


"""
##############################################################################
#Func: find mask slices of value
##############################################################################
"""
import numpy
import time


def FindSlicesArea(
        inMat,
        directions,
        compareTypes,
        sliceStarts,
        sliceStops,
        rangeStarts,
        rangeStops
):
    # initiation
    # time
    strtT = time.time()
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["compareResults"] = []
    rtrnInfo["message"] = ""

    # none:
    if inMat is None:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "ERROR: None input"
        return rtrnInfo

    # shape and dtype
    inMatShp = numpy.shape(inMat)

    # compare same shape
    checkLstShp = Post_Image_Process_Functions.CompareListDimension(
        lsts=[
            sliceStarts,
            sliceStops,
            rangeStarts,
            rangeStarts
        ]
    )
    if checkLstShp["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "Check slices does not have the same length of the list inputs"

    # loop each list element
    # single direction and mask
    directUpdate = True
    compareUpdate = True
    if not numpy.shape(directions):
        direction = directions
        directUpdate = False
        rtrnInfo["message"] += "Single direction input\n"
    if not numpy.shape(compareTypes):
        compareType = compareTypes
        compareUpdate = False
        rtrnInfo["message"] += "Single compare input\n"

    for case in range(len(rangeStarts)):
        # all tpye
        sliceStart = int(sliceStarts[case])
        sliceStop = int(sliceStops[case])
        rangeStart = int(rangeStarts[case])
        rangeStop = int(rangeStops[case])

        # dealing with direction & mask
        if directUpdate: direction = directions[case]
        if compareUpdate: compareType = compareTypes[case]

        # mask of slice
        if direction == 'X' or direction == 'x':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[0]:
                sliceStop = inMatShp[0] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            for slc in range(sliceStart, sliceStop + 1):
                maskCheck = inMat[slc]
                # compare
                compare = compareMaskAreaVolumeValue(
                    inMat=maskCheck,
                    compareType=compareType,
                    rangeStart=rangeStart,
                    rangeStop=rangeStop,
                    binary=True,
                )
                if compare:
                    rtrnInfo["compareResults"].append(slc)
                else:
                    continue

        elif direction == 'Y' or direction == 'y':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[1]:
                sliceStop = inMatShp[1] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            for slc in range(sliceStart, sliceStop + 1):
                maskCheck = inMat[:, slc, :]
                # compare
                compare = compareMaskAreaVolumeValue(
                    inMat=maskCheck,
                    compareType=compareType,
                    rangeStart=rangeStart,
                    rangeStop=rangeStop,
                    binary=True,
                )
                if compare:
                    rtrnInfo["compareResults"].append(slc)
                else:
                    continue

        elif direction == 'Z' or direction == 'z':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[2]:
                sliceStop = inMatShp[2] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            for slc in range(sliceStart, sliceStop + 1):
                maskCheck = inMat[:, :, slc]
                # compare
                compare = compareMaskAreaVolumeValue(
                    inMat=maskCheck,
                    compareType=compareType,
                    rangeStart=rangeStart,
                    rangeStop=rangeStop,
                    binary=True,
                )
                if compare:
                    rtrnInfo["compareResults"].append(slc)
                else:
                    continue
        else:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: wrong direction: {}".format(directions)
            return rtrnInfo

    # find ranges
    rtrnInfo["compareResults"] = list(find_ranges(rtrnInfo["compareResults"]))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Check mask time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete mask check\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: find mask slices connectivity
##############################################################################
"""
import numpy
import time
import skimage.measure


def FindConnectivity(
        inMat,
        directions,
        sliceStarts,
        sliceStops,
        connectivities,
        greaterVals=1
):
    # initiation
    # time
    strtT = time.time()
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["compareResults"] = []
    rtrnInfo["message"] = ""

    # none:
    if inMat is None:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "ERROR: None input"
        return rtrnInfo

    # shape and dtype
    inMatShp = numpy.shape(inMat)

    # compare same shape
    checkLstShp = Post_Image_Process_Functions.CompareListDimension(
        lsts=[
            sliceStarts,
            sliceStops
        ]
    )
    if checkLstShp["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "Check slices does not have the same length of the list inputs"

    # loop each list element
    # single direction and mask
    directUpdate = True
    connectivityUpdate = True
    greaterValUpdate = True
    if not numpy.shape(directions):
        direction = directions
        directUpdate = False
        rtrnInfo["message"] += "Single direction input\n"
    if not numpy.shape(connectivities):
        connectivity = connectivities
        connectivityUpdate = False
        rtrnInfo["message"] += "Single connectivity input\n"
    if not numpy.shape(greaterVals):
        greaterVal = greaterVals
        greaterValUpdate = False
        rtrnInfo["message"] += "Single connectivity number input\n"

    for case in range(len(sliceStarts)):
        # all type
        sliceStart = int(sliceStarts[case])
        sliceStop = int(sliceStops[case])

        # dealing with direction & mask
        if directUpdate: direction = directions[case]
        if connectivityUpdate: connectivity = connectivities[case]
        if greaterValUpdate: greaterVal = greaterVals[case]

        # mask of slice
        if direction == 'X' or direction == 'x':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[0]:
                sliceStop = inMatShp[0] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            for slc in range(sliceStart, sliceStop + 1):
                maskCheck = inMat[slc]
                # compare
                if numpy.sum(maskCheck) == 0:
                    continue
                else:
                    labels, num = skimage.measure.label(
                        maskCheck,
                        background=None,
                        return_num=True,
                        connectivity=connectivity
                    )
                    if num > greaterVal:
                        rtrnInfo["compareResults"].append(slc)
                    else:
                        continue

        elif direction == 'Y' or direction == 'y':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[1]:
                sliceStop = inMatShp[1] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            for slc in range(sliceStart, sliceStop + 1):
                maskCheck = inMat[:, slc, :]
                # compare
                if numpy.sum(maskCheck) == 0:
                    continue
                else:
                    labels, num = skimage.measure.label(
                        maskCheck,
                        background=None,
                        return_num=True,
                        connectivity=connectivity
                    )
                    if num > greaterVal:
                        rtrnInfo["compareResults"].append(slc)
                    else:
                        continue

        elif direction == 'Z' or direction == 'z':
            # dealing with slice
            if sliceStart > sliceStop:
                temp = sliceStart
                sliceStart = sliceStop
                sliceStop = temp
                print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
            if sliceStart < 0:
                sliceStart = 0
                print("Slice start cannot be less than zero: auto change to 0!")
            if sliceStop >= inMatShp[2]:
                sliceStop = inMatShp[2] - 1
                print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

            for slc in range(sliceStart, sliceStop + 1):
                maskCheck = inMat[:, :, slc]
                # compare
                if numpy.sum(maskCheck) == 0:
                    continue
                else:
                    labels, num = skimage.measure.label(
                        maskCheck,
                        background=None,
                        return_num=True,
                        connectivity=connectivity
                    )
                    if num > greaterVal:
                        rtrnInfo["compareResults"].append(slc)
                    else:
                        continue

        else:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: wrong direction: {}".format(directions)
            return rtrnInfo

    # find ranges
    rtrnInfo["compareResults"] = list(find_ranges(rtrnInfo["compareResults"]))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Check mask conectivity time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete connectivty check\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: connectivity filter 2d Center/Rectangle/Median
##############################################################################
"""
import numpy
import skimage.measure
import scipy.stats


def conectivity2DCenterRectangleMedian(
        inMat,
        connectivtyType=1,
        centerplane=False,
        disk=False,
        diskRow=0,  # Row=Y, Columns=X
        diskColm=0,
        radius=1,
        useRef=False,
        refMat=None
):
    # create empty
    inMatShp = numpy.shape(inMat)
    outMat = numpy.zeros(inMatShp)

    # binarinise
    inMat = 1 * (inMat != 0)
    if useRef and refMat is not None:
        refMat = 1 * (refMat != 0)

    # center plane
    if centerplane:
        _, _, centerPlane = PlaneCenterPoint(
            matData=inMat,
            SliceAlong=0,
            flatPlane2D=False
        )

    # reference mask filtering without reference mask
    if useRef and refMat is None:
        raise TypeError("Reference Matrix is Nonetype!")

    for slice in range(inMatShp[0]):
        segmetnation = inMat[slice]

        # Jump empty slice
        if numpy.sum(segmetnation) == 0:
            continue
        else:
            msg = "Working on slice: {}. ".format(slice)

        # connectivity
        lblMsk = skimage.measure.label(segmetnation, connectivity=connectivtyType, return_num=False)
        keepVal = 0  # in label background is '0'

        # center plane
        centerPlaneFailure = True
        if centerplane:
            # check center point is not background
            checkBackround = numpy.sum(numpy.multiply(centerPlane, segmetnation))
            if checkBackround != 0:
                # centerpoint vlaue
                keepVal = numpy.sum(numpy.multiply(centerPlane, lblMsk))
                centerPlaneFailure = False
                msg += "Filter with center value."
            elif not useRef and not rectangle:
                msg += "Center plane FAIL use median value."
                keepVal = scipy.stats.mode(lblMsk[numpy.nonzero(lblMsk)])[0][0]

        # reference mask filtering
        if (useRef and not centerplane) or \
                (useRef and centerplane and centerPlaneFailure):
            refMsk = refMat[slice]

            # check reference mask is not empty
            refVals = numpy.multiply(refMsk, lblMsk)

            # find mode in the reference mask
            if numpy.sum(refVals) != 0:
                keepVal = scipy.stats.mode(refVals[numpy.nonzero(refVals)])[0][0]
                msg += "Filter with reference mask median value."
            else:
                keepVal = scipy.stats.mode(lblMsk[numpy.nonzero(lblMsk)])[0][0]
                msg += "Reference mask FAIL overall median value."

        # disk
        if (disk and not centerplane and not useRef) or \
                (disk and centerplane and centerPlaneFailure):
            diskMsk = numpy.zeros(numpy.shape(segmetnation))

            rr, cc = skimage.draw.disk(
                (int(diskRow), int(diskColm)),
                radius=int(radius),
                shape=numpy.shape(segmetnation)
            )

            diskMsk[rr, cc] = 1

            # check reference mask is not empty
            refVals = numpy.multiply(diskMsk, lblMsk)

            # find mode in the reference mask
            if numpy.sum(refVals) != 0:
                keepVal = scipy.stats.mode(refVals[numpy.nonzero(refVals)])[0][0]
                msg += "Filter with rectangle mask median value."
            else:
                keepVal = scipy.stats.mode(lblMsk[numpy.nonzero(lblMsk)])[0][0]
                msg += "Rectangle mask FAIL overall median value."

        # Filter of values
        _, filterOnes = FilterData(
            rangStarts=[keepVal],
            dataMat=lblMsk,
            funType="single value"
        )
        # Stack slice
        outMat[slice] = filterOnes
        # print(msg)

    return outMat


"""
##############################################################################
# Func: connectivity filter direction and slices
##############################################################################
"""
import numpy
import time


def ConnectivityDirectionSlices(
        inMat,
        directions,
        sliceStarts,
        sliceStops,
        connectivtyTypes,
        centerplane,
        disk,
        diskRows,
        diskColms,
        diskRadii,
        useRef,
        refMat=None
):
    # initiation
    # time
    strtT = time.time()
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["outputMat"] = None
    rtrnInfo["message"] = ""

    # none:
    if inMat is None:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "ERROR: None input"
        return rtrnInfo
    elif useRef and refMat is None:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "ERROR: None refernce mask input"
        return rtrnInfo
    elif useRef:
        # binary
        workMat = (inMat != 0) * 1  # binarinise data
        rtrnInfo["outputMat"] = (inMat != 0) * 1  # binarinise data
        refMat = (refMat != 0) * 1
    else:
        # binary
        workMat = (inMat != 0) * 1  # binarinise data
        rtrnInfo["outputMat"] = (inMat != 0) * 1  # binarinise data

    # shape and dtype
    inMatShp = numpy.shape(inMat)
    inMatDType = inMat.dtype.type

    # compare same shape
    checkLstShp = Post_Image_Process_Functions.CompareListDimension(
        lsts=[
            sliceStarts,
            sliceStops
        ]
    )
    if checkLstShp["error"]:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "Check: does not have the same length of the list inputs!"

    # loop each list element
    # single direction and mask
    connectivtyTypesUpdate = True
    directionsUpdate = True
    diskRadiiUpdate = True
    if not numpy.shape(connectivtyTypes):
        connectivtyType = connectivtyTypes
        connectivtyTypesUpdate = False
        rtrnInfo["message"] += "Single connectivity type input\n"
    if not numpy.shape(directions):
        direction = directions
        directionsUpdate = False
        rtrnInfo["message"] += "Single direction input\n"
    if not numpy.shape(diskRadii):
        diskRadius = diskRadii
        diskRow = diskRows
        diskColm = diskColms
        diskRadiiUpdate = False
        rtrnInfo["message"] += "Single Radius and Center input\n"

    for case in range(len(sliceStarts)):
        # all type
        sliceStart = int(sliceStarts[case])
        sliceStop = int(sliceStops[case])

        # dealing with direction & mask
        if directionsUpdate: direction = directions[case]
        if connectivtyTypesUpdate: connectivtyType = connectivtyTypes[case]
        if diskRadiiUpdate:
            diskRadius = diskRadii[case]
            diskRow = diskRows[case]
            diskColm = diskColms[case]

        # flip results
        if direction == 'X' or direction == 'x':
            pass
        elif direction == 'Y' or direction == 'y':
            rtrnInfo["outputMat"] = Matrix_Math.FilpAxes(
                inMat=rtrnInfo["outputMat"],
                axisInitial="X",
                axisFinal="Y"
            )
            workMat = Matrix_Math.FilpAxes(
                inMat=workMat,
                axisInitial="X",
                axisFinal="Y"
            )
            refMat = Matrix_Math.FilpAxes(
                inMat=refMat,
                axisInitial="X",
                axisFinal="Y"
            )
        elif direction == 'Z' or direction == 'z':
            rtrnInfo["outputMat"] = Matrix_Math.FilpAxes(
                inMat=rtrnInfo["outputMat"],
                axisInitial="X",
                axisFinal="Z"
            )
            workMat = Matrix_Math.FilpAxes(
                inMat=workMat,
                axisInitial="X",
                axisFinal="Z"
            )
            refMat = Matrix_Math.FilpAxes(
                inMat=refMat,
                axisInitial="X",
                axisFinal="Z"
            )
        else:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: wrong direction: {}".format(directions)
            raise KeyError("ERROR: rotation failure! None type returned!")
        # dealing error
        if workMat is None or rtrnInfo["outputMat"] is None or refMat is None:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: rotation failure!"
            raise TypeError("ERROR: rotation failure! None type returned!")

        # range correction
        if sliceStart > sliceStop:
            temp = sliceStart
            sliceStart = sliceStop
            sliceStop = temp
            print("Flip slice range to: {} to {}".format(sliceStart, sliceStop))
        if sliceStart < 0:
            sliceStart = 0
            print("Slice start cannot be less than zero: auto change to 0!")
        if direction == 'X' and sliceStop >= inMatShp[0]:
            sliceStop = inMatShp[0] - 1
            print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))
        elif direction == 'Y' and sliceStop >= inMatShp[1]:
            sliceStop = inMatShp[1] - 1
            print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))
        elif direction == 'Z' and sliceStop >= inMatShp[2]:
            sliceStop = inMatShp[2] - 1
            print("Slice stop cannot be greater than max slice number auto change to {}!".format(sliceStop))

        # filter data
        rtrnInfo["outputMat"][sliceStart:sliceStop + 1] = conectivity2DCenterRectangleMedian(
            inMat=workMat[sliceStart:sliceStop + 1],
            connectivtyType=connectivtyType,
            centerplane=centerplane,
            disk=disk,
            diskRow=diskRow,  # Row=Y, Columns=X
            diskColm=diskColm,
            radius=diskRadius,
            useRef=useRef,
            refMat=refMat
        )

        # rotate bask
        # flip results
        if direction == 'X' or direction == 'x':
            pass
        elif direction == 'Y' or direction == 'y':
            rtrnInfo["outputMat"] = Matrix_Math.FilpAxes(
                inMat=rtrnInfo["outputMat"],
                axisInitial="Y",
                axisFinal="X"
            )
        elif direction == 'Z' or direction == 'z':
            rtrnInfo["outputMat"] = Matrix_Math.FilpAxes(
                inMat=rtrnInfo["outputMat"],
                axisInitial="Z",
                axisFinal="X"
            )
        else:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: wrong direction: {}".format(directions)
            raise KeyError("ERROR: rotation failure! None type returned!")
        # dealing error
        if inMat is None or rtrnInfo["outputMat"] is None:
            rtrnInfo["error"] = True
            rtrnInfo["message"] += "ERROR: rotation failure!"
            raise TypeError("ERROR: rotation failure! None type returned!")

    # convert data type
    rtrnInfo["outputMat"] = numpy.array(rtrnInfo["outputMat"], dtype=inMatDType)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Slice connectivity filtering time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete slice-wise connectivity filtering: {}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
# Func: Arr remove empty slices
##############################################################################
"""
import numpy
import time


def RemoveEmptySlices(
        files,
        lbls,
        sliceStarts=None,
        sliceStops=None
):
    # load data
    arrLst = []
    for case in range(len(files)):
        # load data
        mask = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=files[case]
        )

        # Filter value
        dataFilterVals, dataFilterOnes = FilterData(
            rangStarts=[lbls[case]],
            dataMat=mask.OriData,
            funType="single value"
        )

        # slices
        if sliceStarts is None and sliceStops is None:
            sliceStart = 0
            sliceStop = numpy.shape(dataFilterOnes)[0]
        else:
            sliceStart, sliceStop = Matrix_Math.SliceNumberCorrect(
                sliceStart=sliceStarts[case],
                sliceStop=sliceStops[case],
                boundaryStart=0,
                boundaryStop=numpy.shape(dataFilterOnes)[0],
            )

        # remove empty masks
        nonZeroArr = numpy.zeros(numpy.shape(dataFilterOnes))
        nonZeroArrSlc = 0
        for slc in range(sliceStart, sliceStop):
            if numpy.sum(dataFilterOnes[slc]) != 0:
                nonZeroArr[nonZeroArrSlc] = dataFilterOnes[slc]
                nonZeroArrSlc += 1

        # area choice
        arrLst.append(nonZeroArr[0: nonZeroArrSlc - 1])

    print("Remove Empty Slices Complete")

    return arrLst


"""
##############################################################################
# Func: cut volume of interest SITK -> numpy array
##############################################################################
"""
import numpy


def CutVOI(
        inArr,
        startSlices=None,
        finishSlices=None,
        startRows=None,
        finishRows=None,
        startColumns=None,
        finishColumns=None
):
    # create empty out array
    arrShp = numpy.shape(inArr)
    outArr = numpy.zeros(arrShp)
    outArrOnes = numpy.ones(arrShp)

    # directions
    '''
    inArr[
        startSlices:finishSlices,
        startColumns:finishColumns,
        startRows:finishRows
    ]
    STIK image: x-columns, y-rows, z-depth
    SITK numpy array: z-depth, y-rows, x-columns   
    '''
    # direction slices X/depth
    if startSlices is not None and finishSlices is not None:
        # convert slices
        outArrOnesTmp = numpy.zeros(arrShp)
        for startSlice, finishSlice in zip(startSlices, finishSlices):
            # check slices
            startSlice, finishSlice = Matrix_Math.SliceNumberCorrect(
                sliceStart=startSlice,
                sliceStop=finishSlice,
                boundaryStart=0,
                boundaryStop=arrShp[0],
            )
            # cut
            outArrOnesTmp[startSlice:finishSlice + 1] = 1

        # multiply
        outArrOnes = numpy.multiply(outArrOnes, outArrOnesTmp)

    # dreiction column
    if startColumns is not None and finishColumns is not None:
        # convert columns
        outArrOnesTmp = numpy.zeros(arrShp)
        for startColumn, finishColumn in zip(startColumns, finishColumns):
            # check slices
            startColumn, finishColumn = Matrix_Math.SliceNumberCorrect(
                sliceStart=startColumn,
                sliceStop=finishColumn,
                boundaryStart=0,
                boundaryStop=arrShp[1],
            )
            # cut
            outArrOnesTmp[:, :, startColumn:finishColumn + 1] = 1

        # multiply
        outArrOnes = numpy.multiply(outArrOnes, outArrOnesTmp)

    # dreiction row
    if startRows is not None and finishRows is not None:
        # convert rows
        outArrOnesTmp = numpy.zeros(arrShp)
        for startRow, finishRow in zip(startRows, finishRows):
            # check slices
            startRow, finishRow = Matrix_Math.SliceNumberCorrect(
                sliceStart=startRow,
                sliceStop=finishRow,
                boundaryStart=0,
                boundaryStop=arrShp[2],
            )
            # cut
            outArrOnesTmp[:, startRow:finishRow + 1, :] = 1

        # multiply
        outArrOnes = numpy.multiply(outArrOnes, outArrOnesTmp)

    # output
    outArr = numpy.multiply(outArrOnes, inArr)

    return outArr


"""
##############################################################################
# Func: get array/matrix skin 1 voxel
##############################################################################
"""
import numpy


def GetSkin(
        inArr,
        filterVals=[]
):
    # create empty out array
    arrShp = numpy.shape(inArr)
    excludeMask = numpy.zeros(arrShp)

    # exclude mask
    if isinstance(filterVals, list):
        if len(filterVals) != 0:
            for val in filterVals:
                excludeMask += 1 * (inArr == val)
    # make sure exclude mask is 1
    excludeMask = 1 * (excludeMask != 0)

    # skin
    ## inarr to one mask only
    inArrOnes = 1 * (inArr != 0)
    rtrnInfo = OpenCloseDilateErrode(
        dataMat=inArrOnes,
        funcChoose='Erosion',
        Thres=0,
        dilateIncre=1,
        binaryMsk=True,
        axisChoice='3D',
        iterateDilate=False
    )

    skinMaskAll = inArrOnes - rtrnInfo["outMask"]

    # select wanted mask
    outArrOnes = numpy.multiply(skinMaskAll, 1 * ((inArrOnes - excludeMask) != 0))
    outArrVals = numpy.multiply(outArrOnes, inArr)

    # print(numpy.sum(inArr))
    # print(numpy.sum(excludeMask))
    # print(numpy.sum(inArrOnes))
    # print(numpy.sum(rtrnInfo["outMask"]))
    # print(numpy.sum(skinMaskAll))
    # print(numpy.sum(outArrOnes))
    # print(numpy.sum(outArrVals))

    return outArrOnes, outArrVals


"""
##############################################################################
# Func: get mask centroid
##############################################################################
"""
import skimage.measure


def MaskCentroid(inMask):
    inMaskLabel, inMaskNum = skimage.measure.label(inMask,
                                                   connectivity=1,
                                                   return_num=True)
    inMaskRegion = skimage.measure.regionprops(inMaskLabel)

    # !!! list start from 0 label start from 1!!!
    inMaskBubble = inMaskRegion[0]
    inMaskRow, inMaskColm = inMaskBubble.centroid

    return inMaskRow, inMaskColm


"""
##############################################################################
# Func: match 3d array mask for each x slice
##############################################################################
"""
import numpy


def MatchXSliceCentroid(
        referenceMat,
        inMat
):
    # binary mask
    _, referenceMatOnes = FilterData(rangStarts=[0],
                                     dataMat=referenceMat,
                                     funType="single value greater")
    _, inMatOnes = FilterData(rangStarts=[0],
                              dataMat=inMat,
                              funType="single value greater")

    # create empty output mat
    outMat = numpy.zeros(numpy.shape(inMatOnes))

    for slc in range(numpy.shape(inMatOnes)[0]):
        # get slices
        inMask = inMatOnes[slc]
        inRefMask = referenceMatOnes[slc]

        if numpy.sum(inMask) == 0 or numpy.sum(inRefMask) == 0:
            outMat[slc] = inMask
            continue
        else:
            # get centroid
            inMaskRow, inMaskColm = MaskCentroid(inMask)
            inRefMaskRow, inRefMaskColm = MaskCentroid(inRefMask)

            # centroid difference
            rowDiff = inRefMaskRow - inMaskRow
            colmDiff = inRefMaskColm - inMaskColm

            # non-zero rows & columns
            (inMaskRows, inMaskColms) = numpy.where(inMask != 0)

            # shift and fill
            # empty mat
            outMask = numpy.zeros(numpy.shape(inMask))

            # fill
            inMaskRowsCorrect = numpy.array(inMaskRows + rowDiff, dtype=int)
            inMaskColmsCorrect = numpy.array(inMaskColms + colmDiff, dtype=int)
            outMask[(inMaskRowsCorrect, inMaskColmsCorrect)] = 1

            # stack mask
            outMat[slc] = outMask

    print("Complete slice centroid correction")

    return outMat


"""
##############################################################################
# Func: single line connection of coordinates
##############################################################################
"""
import sklearn.neighbors
import networkx


def ConnectSingleLine(
        coordinates
):
    # https: // stackoverflow.com / questions / 37742358 / sorting - points - to - form - a - continuous - line  #
    # Create 2-NN graph between nodes
    clf = sklearn.neighbors.NearestNeighbors(n_neighbors=2)
    clf.fit(coordinates)
    G = clf.kneighbors_graph()  # sparse matrix

    # construct a graph from this sparse matrix
    T = networkx.from_scipy_sparse_matrix(G)

    # create a path through all the nodes (passing through each of them exactly once) given a starting node
    paths = [list(networkx.dfs_preorder_nodes(T, i)) for i in range(len(coordinates))]

    # find the one that minimizes the distances between the connections (optimization problem)
    mindist = numpy.inf
    minidx = 0

    for i in range(len(coordinates)):
        p = paths[i]  # order of nodes
        ordered = coordinates[p]  # ordered nodes
        # find cost of that order by the sum of euclidean distances between points (i) and (i+1)
        cost = (((ordered[:-1] - ordered[1:]) ** 2).sum(1)).sum()
        # print(cost)
        if cost < mindist:
            mindist = cost
            minidx = i

    print('minidx: \n{}'.format(minidx))

    orderCoordinate = coordinates[paths[minidx]]

    msg = "Reorder: \n{} \n To: \n{}".format(coordinates, orderCoordinate)
    # print(msg)

    return orderCoordinate


"""
##############################################################################
# Func: Find first and last
##############################################################################
"""
import numpy


def NoneEmptySlices(
        inMat,
        sliceSum=0
):
    # get all none empty slices
    slicesNonEmpty = [False] * numpy.shape(inMat)[0]

    print("sliceSum")
    print(sliceSum)

    # for each slice
    for slc in range(numpy.shape(inMat)[0]):
        sliceBinary = 1 * (inMat[slc] > 0)
        slicesNonEmpty[slc] = bool(numpy.sum(sliceBinary) > sliceSum)
        # if numpy.sum(inMat[slc]) != 0:
        #     print("Slice: {} - {}".format(slc, True))

    # extract slice
    outSlices = numpy.array(range(numpy.shape(inMat)[0]))[slicesNonEmpty]

    msg = "Non-empty slices: \n{} \nTotal slice: {}".format(outSlices, numpy.shape(inMat)[0])
    print(msg)

    return outSlices


"""
##############################################################################
# Func: Single segment shrink for centerline coordinate with resampling
##############################################################################
"""
import numpy
import scipy.ndimage
import skimage.morphology
import skimage.measure
import pandas
import matplotlib.pyplot as plt
import scipy.interpolate


def CenterlineGeneration(
        inPath,
        resampleNo,
        labelThresStarts=[0],
        labelThresStops=[0],
        ThresTypes="single value greater",
        SaveIntermediate=True,
        diagPath="",
        fileSuff="",
        pltVis=False
):
    # load mask
    oriMask = Save_Load_File.OpenLoadNIFTI(
        GUI=False,
        filePath=inPath
    )

    # binary data
    _, oriMaskOnes = Image_Process_Functions.FilterData(rangStarts=labelThresStarts,
                                                        rangStops=labelThresStops,
                                                        dataMat=oriMask.OriData,
                                                        funType=ThresTypes)

    # create diagnosis path
    diagCreate = Save_Load_File.checkCreateDir(diagPath)

    if diagCreate["error"]:
        fullParentDir, _ = Save_Load_File.ParentDir(path=inPath)
        diagPath = fullParentDir

    # save
    if SaveIntermediate:
        # Set file name
        OnesTempPath = Save_Load_File.DateFileName(
            Dir=diagPath,
            fileName="FilterOnes" + fileSuff,
            extension=".nii.gz",
            appendDate=False
        )
        # save
        Save_Load_File.MatNIFTISave(
            MatData=oriMaskOnes,
            imgPath=OnesTempPath["CombineName"],
            imgInfo=oriMask.OriImag,
            ConvertDType=True,
            refDataMat=oriMask.OriData
        )

    # skeleton
    skeleton = skimage.morphology.skeletonize_3d(oriMaskOnes)

    # Set file name
    skeletonPath = Save_Load_File.DateFileName(
        Dir=diagPath,
        fileName="Skeleton" + fileSuff,
        extension=".nii.gz",
        appendDate=False
    )
    # save
    Save_Load_File.MatNIFTISave(
        MatData=skeleton,
        imgPath=skeletonPath["CombineName"],
        imgInfo=oriMask.OriImag,
        ConvertDType=True,
        refDataMat=oriMask.OriData
    )

    # convert to actual coordinate with actual XYZ sequence
    # load skeleton
    skeletonMask = Save_Load_File.OpenLoadNIFTI(
        GUI=False,
        filePath=skeletonPath["CombineName"]
    )
    # SITK to array
    maskArray = SITK_Numpy.SITK_NP_Arr()
    # image and array
    maskArray.InSITKImag(SITKImag=skeletonMask.OriImag)
    # mask pixels
    maskArray.PositionMaskValues()
    # flip array
    maskArray.PositionXYZ()
    # convert to 3D space
    maskArray.Actual3DCoors()

    print(numpy.sum(maskArray.Actual3DCoors - maskArray.SITKArrCoors_XYZ))
    print(skeletonMask.OriImag.GetSpacing())

    # connecting single line for voxels without spacing
    ## with spacing may cause problem due to inheterogenity
    orderCoors = Image_Process_Functions.ConnectSingleLine(
        coordinates=maskArray.SITKArrCoors_XYZ
    )

    # make to xx, yy, zz
    coorLen = len(orderCoors)
    xx = numpy.zeros(coorLen)
    yy = numpy.zeros(coorLen)
    zz = numpy.zeros(coorLen)

    for i in range(coorLen):
        xx[i] = orderCoors[i][0]
        yy[i] = orderCoors[i][1]
        zz[i] = orderCoors[i][2]

    # spline 3D
    tck, u = scipy.interpolate.splprep([xx, yy, zz], s=3, t=5)
    x_knots, y_knots, z_knots = scipy.interpolate.splev(tck[0], tck)
    u_fine = numpy.linspace(0, 1, resampleNo)
    x_fine, y_fine, z_fine = scipy.interpolate.splev(u_fine, tck)

    # xx, yy, zz to list [[x, y, z], ..]
    smoothLen = len(x_fine)
    smoothCoors = [None] * smoothLen
    for i in range(smoothLen):
        smoothCoors[i] = [x_fine[i], y_fine[i], z_fine[i]]

    # new spacing
    # SITK to array
    maskArraySmooth = SITK_Numpy.SITK_NP_Arr()
    # image and array
    maskArraySmooth.InSITKImag(SITKImag=skeletonMask.OriImag)
    # convert to 3D space
    maskArraySmooth.Actual3DCoors(inPosition=smoothCoors)

    # # plot to visualise
    if pltVis:
        coorLen = len(orderCoors)
        xx = numpy.zeros(smoothLen)
        yy = numpy.zeros(smoothLen)
        zz = numpy.zeros(smoothLen)

        for i in range(smoothLen):
            xx[i] = maskArrayOrder.Actual3DCoors[i][0]
            yy[i] = maskArrayOrder.Actual3DCoors[i][1]
            zz[i] = maskArrayOrder.Actual3DCoors[i][2]

        xx0 = numpy.zeros(coorLen)
        yy0 = numpy.zeros(coorLen)
        zz0 = numpy.zeros(coorLen)

        for i in range(coorLen):
            xx0[i] = maskArray.Actual3DCoors[i][0]
            yy0[i] = maskArray.Actual3DCoors[i][1]
            zz0[i] = maskArray.Actual3DCoors[i][2]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.plot(xx, yy, zz, color='b', marker="o")
        ax.plot(xx0, yy0, zz0, color='r', marker="*")

    return maskArraySmooth.Actual3DCoors


"""
##############################################################################
# Func: Single segment shrink for centerline coordinate from manual
##############################################################################
"""
import numpy


def StartPointCube(
        inPath,
        outName="",
        outDir="",
        size_surface=14
):
    # load mask
    oriMask = Save_Load_File.OpenLoadNIFTI(
        GUI=False,
        filePath=inPath
    )

    # skeleton
    skeleton = skimage.morphology.skeletonize_3d(oriMask.OriData)

    # SITK to array
    maskArray = SITK_Numpy.SITK_NP_Arr()
    ## image and array
    maskArray.InSITKArr(SITKArr=skeleton)
    ## mask pixels
    maskArray.PositionMaskValues()
    ## flip array
    maskArray.PositionXYZ()

    # order coordinates
    orderCoordinates = ConnectSingleLine(maskArray.SITKArrCoors_ZYX)
    # print(orderCoordinates)
    # vmtk.run()

    # create start cubes
    two_surface = numpy.zeros(numpy.shape(oriMask.OriData))

    # get unit vector
    firstPoint = orderCoordinates[0]
    secondPoint = orderCoordinates[1]
    v = secondPoint - firstPoint
    v_unit = v / numpy.linalg.norm(v)

    # get ball
    ball = Matrix_Math.BallMatrix(int(size_surface / 2))

    # iterate for at least 75% of the volume
    volumeFlag = True

    ## original volume
    oriVolume = numpy.sum(oriMask.OriData != 0)

    while volumeFlag:
        # shift ball place
        out_surface = Matrix_Math.PutShapeMatrix(
            ShapeMat=ball,
            DestMat=two_surface,
            Origin=firstPoint,
            direction=v_unit,
            distance=int(size_surface / 2) - 2  # make sure intersect
        )

        # check overlap
        overlap = numpy.multiply(1 * (oriMask.OriData != 0), 1 * (out_surface != 0))
        left_overlap = 1 * (oriMask.OriData != 0) - 1 * (overlap != 0)

        if numpy.sum(left_overlap) < 0.6 * oriVolume:
            print("Volume overlap is {} less than 0.6 original volume {}".format(numpy.sum(left_overlap), oriVolume))
            size_surface = size_surface - 2  # diameter shrink by 2
        else:
            volumeFlag = False

    # x = orderCoordinates[0][0]
    # y = orderCoordinates[0][1]
    # z = orderCoordinates[0][2]
    #
    # if z >= size_surface:
    #     kernel = numpy.ones([size_surface * 2 + 1, size_surface * 2 + 1, size_surface * 2 + 1])
    #
    #     # two_surface[x - size_surface:x + (size_surface + 1), y - size_surface:y + (size_surface + 1),
    #     # z - size_surface:z + (size_surface + 1)] = kernel
    #
    #     two_surface[x - size_surface:x + (size_surface + 1), y - size_surface:y + (size_surface + 1),
    #     z - (size_surface - 1):z + (size_surface + 2)] = kernel
    #
    # else:
    #     kernel = numpy.ones([size_surface * 2 + 1, size_surface * 2 + 1, size_surface + 1])
    #
    #     two_surface[x - size_surface:x + (size_surface + 1), y - size_surface:y + (size_surface + 1),
    #     z:z + (size_surface + 1)] = kernel

    # save
    segmentPath = Save_Load_File.DateFileName(
        Dir=outDir,
        fileName=outName + '_intersect',
        extension=".nii.gz",
        appendDate=False
    )
    Save_Load_File.MatNIFTISave(
        MatData=out_surface,
        imgPath=segmentPath["CombineName"],
        imgInfo=oriMask.OriImag,
        ConvertDType=True,
        refDataMat=oriMask.OriData
    )

    return None


"""
##############################################################################
# Func: Single segment shrink for centerline coordinate from manual
##############################################################################
"""
import numpy
import scipy.ndimage
import pandas


def ManCenterlineGeneration(
        inPath,
        rangeStarts=[0],
        rangeStops=[0],
        funType="single value greater",
        SaveIntermediate=True,
        outDir="",
        connectType=1,
        labelDict=None,
        vmtkFun=True,
        exePath="",
        size_surface=14,
        voxThres=269
):
    # outout dict
    outDictLst = []

    # check output
    if outDir != "":
        _ = Save_Load_File.checkCreateDir(outDir)
    else:
        # out dir
        outDir, _ = Save_Load_File.ParentDir(path=inPath)

    # load mask
    oriMask = Save_Load_File.OpenLoadNIFTI(
        GUI=False,
        filePath=inPath
    )

    # filter
    mskVals, _ = Image_Process_Functions.FilterData(
        rangStarts=rangeStarts,
        rangStops=rangeStops,
        dataMat=oriMask.OriData,
        funType=funType,
        ConvertVTKType=False,
        InDataType=numpy.float64
    )

    # get all values
    lstVals = [int(x) for x in Matrix_Math.matToListNoDulication(mskVals)]
    # remove 0
    lstVals.remove(0)

    # each label
    for lbl in lstVals:
        # find each connected volume
        ## filter
        # binary data
        _, oriMaskOnes = Image_Process_Functions.FilterData(rangStarts=[lbl],
                                                            rangStops=[lbl],
                                                            dataMat=mskVals,
                                                            funType="single value")

        # connectivity
        labelMap, num = skimage.measure.label(
            oriMaskOnes,
            connectivity=connectType,
            return_num=True
        )

        # for each bit of the same label
        for lblVal in range(1, num + 1):
            # out dictionary
            outDict = {}

            # Filter out
            _, singleMask = FilterData(
                rangStarts=[lblVal],
                dataMat=labelMap,
                funType="single value"
            )

            # suffix
            if labelDict is None:
                lblref = str(lbl)
            else:
                try:
                    lblref = labelDict[str(int(lbl))]
                except:
                    lblref = str(lbl)
            if num == 1:
                suff = lblref
            else:
                suff = lblref + str(lblVal)

            # centerline
            print("{} Volume: {}".format(suff, numpy.sum(1 * (singleMask != 0))))
            if vmtkFun and (numpy.sum(1 * (singleMask != 0)) > voxThres):
                print("Use VMTK for centerline")

                ## save nifti
                segmentPath = Save_Load_File.DateFileName(
                    Dir=outDir,
                    fileName="seg_" + suff,
                    extension=".nii.gz",
                    appendDate=False
                )
                Save_Load_File.MatNIFTISave(
                    MatData=singleMask,
                    imgPath=segmentPath["CombineName"],
                    imgInfo=oriMask.OriImag,
                    ConvertDType=True,
                    refDataMat=oriMask.OriData
                )

                # create start cubes
                StartPointCube(
                    inPath=segmentPath["CombineName"],
                    outName=suff,
                    outDir=outDir,
                    size_surface=size_surface
                )

                ## vmtk
                saveCSV = 0
                if SaveIntermediate:
                    deleteInter = 0
                else:
                    deleteInter = 1

                vmtkDict = Image_Process_Functions.centerline_calculation(
                    exePath=exePath,
                    niftiname="seg_" + suff + ".nii.gz",
                    fileRef=suff,
                    outDir=outDir,
                    niftiname_intersect=suff + '_intersect.nii.gz',
                    smoothing_iteration=3000,
                    saveCSV=saveCSV,
                    deleteInter=deleteInter
                )

                # centerline
                # list of dictionary of coordinates
                orderCoordinateLst = []
                for point in vmtkDict["ordered_ijk"]:
                    coordDict = {}
                    coordDict["X"] = int(point[0])
                    coordDict["Y"] = int(point[1])
                    coordDict["Z"] = int(point[2])
                    orderCoordinateLst.append(coordDict)

                # output
                outDict["coordinates"] = vmtkDict["ordered_ijk"]
                outDict["coordinatesXYZ"] = orderCoordinateLst
                outDict["label"] = lbl
                outDict["branch_name"] = suff
                outDict["function"] = "vmtk_centerline"
                outDictLst.append(outDict)

                # output dataframe
                if SaveIntermediate:
                    # csv
                    dfOut = pandas.DataFrame(vmtkDict["ordered_ijk"])

                    ## Set file name
                    DfOutFilePath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName=suff,
                        extension=".csv",
                        appendDate=False
                    )
                    outTablePath = DfOutFilePath["CombineName"]
                    ## save
                    Pd_Funs.SaveDF(
                        outPath=outTablePath,
                        pdIn=dfOut,
                        header=False,
                        index=False
                    )

                    # save skeleton
                    skeletonMat = numpy.zeros(numpy.shape(singleMask))

                    for point in vmtkDict["ordered_ijk"]: skeletonMat[point[2], point[1], point[0]] = 1

                    ## Set file name
                    skeletonPath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName="Skeleton_" + suff,
                        extension=".nii.gz",
                        appendDate=False
                    )
                    ## save
                    Save_Load_File.MatNIFTISave(
                        MatData=skeletonMat,
                        imgPath=skeletonPath["CombineName"],
                        imgInfo=oriMask.OriImag,
                        ConvertDType=True,
                        refDataMat=oriMask.OriData
                    )

            else:
                print("Use Skelentonization for centerline")

                ## skeleton
                skeleton = skimage.morphology.skeletonize_3d(oriMaskOnes)

                # save
                if SaveIntermediate:
                    ## save nifti
                    segmentPath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName="seg_" + suff,
                        extension=".nii.gz",
                        appendDate=False
                    )
                    Save_Load_File.MatNIFTISave(
                        MatData=singleMask,
                        imgPath=segmentPath["CombineName"],
                        imgInfo=oriMask.OriImag,
                        ConvertDType=True,
                        refDataMat=oriMask.OriData
                    )

                    ## Set file name
                    skeletonPath = Save_Load_File.DateFileName(
                        Dir=outDir,
                        fileName="Skeleton_" + suff,
                        extension=".nii.gz",
                        appendDate=False
                    )
                    ## save
                    Save_Load_File.MatNIFTISave(
                        MatData=skeleton,
                        imgPath=skeletonPath["CombineName"],
                        imgInfo=oriMask.OriImag,
                        ConvertDType=True,
                        refDataMat=oriMask.OriData
                    )

                    ## load skeleton
                    skeletonMask = Save_Load_File.OpenLoadNIFTI(
                        GUI=False,
                        filePath=skeletonPath["CombineName"]
                    )
                    ## SITK to array
                    maskArray = SITK_Numpy.SITK_NP_Arr()
                    ## image and array
                    maskArray.InSITKImag(SITKImag=skeletonMask.OriImag)
                    ## mask pixels
                    maskArray.PositionMaskValues()
                    ## flip array
                    maskArray.PositionXYZ()
                else:
                    ## SITK to array
                    maskArray = SITK_Numpy.SITK_NP_Arr()
                    ## image and array
                    maskArray.InSITKArr(SITKArr=skeleton)
                    ## mask pixels
                    maskArray.PositionMaskValues()
                    ## flip array
                    maskArray.PositionXYZ()

                # order the points jump if not three points
                if numpy.sum(skeleton != 0) < 3:
                    print("33333333333333333333numpy.sum(skeleton) < 3")
                    print("33333333333333333333 Points < 3 JUMP!")
                    continue
                else:
                    print("000000000000000--{}".format(numpy.sum(skeleton != 0)))
                    orderCoordinates = ConnectSingleLine(maskArray.SITKArrCoors_XYZ)

                    # list of dictionary of coordinates
                    orderCoordinateLst = []
                    for point in orderCoordinates:
                        coordDict = {}
                        coordDict["X"] = int(point[0])
                        coordDict["Y"] = int(point[1])
                        coordDict["Z"] = int(point[2])
                        orderCoordinateLst.append(coordDict)

                    # output
                    outDict["coordinates"] = orderCoordinates
                    outDict["coordinatesXYZ"] = orderCoordinateLst
                    outDict["label"] = lbl
                    outDict["branch_name"] = suff
                    outDict["function"] = "skeletonize"
                    outDictLst.append(outDict)

                    # output dataframe
                    if SaveIntermediate:
                        dfOut = pandas.DataFrame(orderCoordinates)

                        # Set file name
                        DfOutFilePath = Save_Load_File.DateFileName(
                            Dir=outDir,
                            fileName=suff,
                            extension=".csv",
                            appendDate=False
                        )
                        outTablePath = DfOutFilePath["CombineName"]

                        # save
                        Pd_Funs.SaveDF(
                            outPath=outTablePath,
                            pdIn=dfOut,
                            header=False,
                            index=False
                        )

    return outDictLst


"""
##############################################################################
# Func: Single segment vmtk centerline coordinate
##############################################################################
"""

import os
import numpy
import subprocess


def centerline_calculation(
        exePath,
        niftiname,
        fileRef,
        outDir,
        niftiname_intersect,
        smoothing_iteration=3000,
        saveCSV=1,
        deleteInter=1
):
    print("CMD Input:")
    print(
        exePath,
        niftiname,
        fileRef,
        outDir,
        niftiname_intersect,
        str(smoothing_iteration),
        str(saveCSV),
        str(deleteInter)
    )

    subprocess.call([
        exePath,
        niftiname,
        fileRef,
        outDir,
        niftiname_intersect,
        str(smoothing_iteration),
        str(saveCSV),
        str(deleteInter)
    ])

    # read npy dictionary
    ## file
    OutFilePath = outDir + '\centreline_' + fileRef + '.npy'

    ## load
    outDict = numpy.load(OutFilePath, allow_pickle=True).item()

    print('Load NPY Dictionary')
    print(outDict["ordered_ijk"])

    return outDict

"""
##############################################################################
# Func: replace segments with disks
##############################################################################
"""

def replaceSegmentDisks(
        inMaskPaths,
        diskDiameterMM,
        outMaskRef,
        sliceStart,
        sliceSum=3
        ):
    # load
    for inMaskPath in inMaskPaths:
        # load files
        mskData = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=inMaskPath
        )

        # find non-empty slices
        slices = NoneEmptySlices(
            inMat=mskData.OriData,
            sliceSum=sliceSum
        )

        # jump slices
        slicesUse = slices[slices > sliceStart]

        # spacing
        spacing = mskData.OriImag.GetSpacing()
        spacing_z = spacing[0]  # numpy array has flipped X and Z
        spacing_y = spacing[1]
        spacing_x = spacing[2]

        if spacing_z == spacing_y:
            spacing = spacing_z
        else:
            spacing = (spacing_z ** 2 + spacing_y ** 2) ** 0.5

        # diameter
        diameter = diskDiameterMM / spacing

        # shape
        inMatShp = numpy.shape(mskData.OriData)

        # fill mask
        fillMaskDict = FillMask3D(
                inMat=mskData.OriData,
                directions='x',
                maskTypes='ellipse',
                verticalLengths=[diameter],
                horizontalLengths=[diameter],
                sliceStarts=[slicesUse[0]],
                sliceStops=[slicesUse[-1]],
                posititionFirsts=[round(inMatShp[1]/2)],
                positionSeconds=[round(inMatShp[2]/2)],
                binary=True,
                fillOriginal=False
        )

        # parent directory
        fullParentDir, _ = Save_Load_File.ParentDir(
            path=inMaskPath
        )

        # Set file name
        outFilePath = Save_Load_File.DateFileName(
            Dir=fullParentDir,
            fileName=outMaskRef + "_" + str(diskDiameterMM) + "M",
            extension=".nii.gz",
            appendDate=False
        )

        # save
        Save_Load_File.MatNIFTISave(
            MatData=fillMaskDict['outMask'],
            imgPath=outFilePath["CombineName"],
            imgInfo=mskData.OriImag,
            ConvertDType=True,
            refDataMat=mskData.OriData
        )

"""
##############################################################################
#FAI calculation
##############################################################################
"""
import numpy

def FAICaculation(imgPath,
                  maskPath,
                  ThresType='boundary',
                    ThresStart=[-190],
                    ThresStop=[-30]
                  ):
    # load data
    CTAData = Save_Load_File.OpenLoadNIFTI(
        GUI=False,
        filePath=imgPath
    )
    mskData = Save_Load_File.OpenLoadNIFTI(
        GUI=False,
        filePath=maskPath
    )

    # filter data
    inImg, inOnes = Image_Process_Functions.FilterData(
        rangStarts=ThresStart,
        rangStops=ThresStop,
        dataMat=CTAData.OriData,
        funType=ThresType
    )
    _, inMaskOnes = Image_Process_Functions.FilterData(
        rangStarts=[0],
        rangStops=[0],
        dataMat=mskData.OriData,
        funType='single value greater'
    )

    inMask = numpy.multiply(inMaskOnes, inOnes)

    # array
    imgArr = inImg[inMask != 0]

    # get average
    FAI = numpy.nanmean(imgArr)

    return FAI