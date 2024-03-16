# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 10:16:52 2020

@author: yingmohuanzhou
"""
# Load library


"""
##############################################################################
#Class: Vertical cut and only remove aorta
##############################################################################
"""
import numpy
import copy
import skimage.measure
import matplotlib.pyplot as plt


class VerticalCutRemove:
    def __init__(self,
                 cutMat="",
                 refMat="",
                 centerCom=0,
                 width=3):
        self.cutMat = cutMat
        self.refMat = refMat
        self.centerCom = centerCom
        self.width = width

    def CompareData(self, mat1, mat2):
        # Comparing shapes
        self.mat1Shape = numpy.shape(mat1)
        self.mat2Shape = numpy.shape(mat2)

        # Compare data shape
        if self.mat1Shape == self.mat2Shape:
            self.sameShp = True
        else:
            self.sameShp = False

    def CreateVertMsk(self, noDetph, noRows, noColms, centerCom=0, width=3):
        # Create empty plane
        self.emptyVol = numpy.zeros([noDetph, noRows, noColms])

        # Create vertical mask
        self.verticalVol = copy.deepcopy(self.emptyVol)
        self.verticalVol[:, :, (centerCom - width): (centerCom + width)] = 1

    def CentroidCoor(self, mask):
        # label
        labels = skimage.measure.label(mask)

        # region propos for information
        regions = skimage.measure.regionprops(labels)

        # bubble with [0] as the first label
        self.bubble = regions[0]

        # region information
        self.Depth, self.Row, self.Col = self.bubble.centroid  # Centroid coordinate tuple (row, col)!!

    def CutFilter(self):
        # Compare shape
        self.CompareData(mat1=self.cutMat,
                         mat2=self.refMat)

        if not self.sameShp:
            Save_Load_File.WarnExit(dispMsg="Not same shape! First Mat: \n" +
                                            str(self.mat1Shape) +
                                            "Second Mat: \n" +
                                            str(self.mat2Shape))

        # Filter volume
        self.CreateVertMsk(noDetph=self.mat1Shape[0],
                           noRows=self.mat1Shape[1],
                           noColms=self.mat1Shape[2],
                           centerCom=self.centerCom,
                           width=self.width)

        # slicing date
        self.cutPart = numpy.multiply(self.verticalVol, self.cutMat)
        self.refPart = numpy.multiply(self.verticalVol, self.refMat)

        # #labelling part
        # self.cutPartLbl = skimage.measure.label(self.cutPart, connectivity = 1)

        # #Show results
        # plt.figure()
        # plt.imshow(self.cutPartLbl[:, self.centerCom, :])
        # plt.show()

        # #Find centroid of artoa
        # self.CentroidCoor(mask = self.refPart)

        # #Centroid value
        # self.cenVal = self.cutPartLbl[int(self.Depth), int(self.Row), int(self.Col)]
        # print("Center value: " + str(self.cenVal))

        # #making mask
        # self.cutSlice = 1.0 * (self.cutPart == self.cenVal)
        # self.cutSlice.astype(numpy.float64)
        # self.cutMsk = 1 - (self.cutSlice)

        # #Mask mat
        # self.removeMat = numpy.multiply(self.cutMsk, self.cutMat)

        self.cutSlice, self.cutSliceMsked = Image_Process_Functions.ConnectivityFilter(matData=self.cutPart,
                                                                                       connectType=1, keepNumber=1,
                                                                                       FilterArea='first')

        self.removeMat = self.cutMat - self.cutSliceMsked

        self.removeMat = numpy.float64(self.removeMat)
        self.cutSlice = numpy.float64(self.cutSlice)


"""
##############################################################################
#Func: convert string into split values (floats & string)
##############################################################################
"""
import time
import re


def StrToLst(strIn):
    # timing
    time0 = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = None
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["listOut"] = None
    rtrnInfo["floatOut"] = None
    rtrnInfo["booleanOut"] = None
    rtrnInfo["intOut"] = None

    # print(strIn)
    # replace string characters ^ [NOT] \. [.] \w [word] \+ \- [Keep + -]
    strInSpaces = re.sub("[^\:\+\-\.\(\)\w\/\_\\\]", ' ', str(strIn))
    # print(strInSpaces)
    # replace multiple spaces ' +' to single space ' '
    strInSingSpace = re.sub(' +', ' ', strInSpaces)
    # print(strInSingSpace)
    # string list split by space
    rtrnInfo["listOut"] = strInSingSpace.split()
    # print(rtrnInfo["listOut"])
    # floats
    rtrnInfo["floatOut"] = []
    rtrnInfo["intOut"] = []
    rtrnInfo["booleanOut"] = []
    for item in rtrnInfo["listOut"]:
        if item == "None":
            rtrnInfo["floatOut"].append(None)
            rtrnInfo["intOut"].append(None)
            rtrnInfo["booleanOut"].append(None)
        else:
            try:
                rtrnInfo["floatOut"].append(float(item))
            except:
                pass
            try:
                rtrnInfo["intOut"].append(int(item))
            except:
                pass
            try:
                rtrnInfo["booleanOut"].append(item == 'True')
            except:
                pass

    # time
    time1 = time.time()
    diffT10 = time1 - time0

    rtrnInfo["processTime"] = diffT10
    rtrnInfo["processTimeMessage"] = "------StrToLst calculation time: {} s------".format(diffT10)

    return rtrnInfo
