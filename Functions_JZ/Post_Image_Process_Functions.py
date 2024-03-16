# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 14:07:09 2020

@author: yingmohuanzhou
"""
import Image_Process_Functions
import Save_Load_File
import Use_Plt
import VTK_Functions
import Pd_Funs
import Matrix_Math
import SITK_Numpy
import os
import VTK_Functions

# Mayavi is conflit with QT5!!!
# import Maya_Plot

"""
##############################################################################
#Fucntion array dimension comparison
##############################################################################
"""
import numpy


def CompareArrayDimension(dataMat,
                          shapeD=3):
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["greaterCompareDimension"] = False
    rtrnInfo["equalCompareDimension"] = False
    rtrnInfo["dimensions"] = None
    rtrnInfo["Message"] = ""

    # Shape Shape of the mat
    dataMat_shpshp = numpy.shape(numpy.shape(dataMat))

    # first element is the diemnsions
    dimensions = dataMat_shpshp[0]
    rtrnInfo["dimensions"] = dimensions

    # Compare equal
    if dimensions == shapeD:
        rtrnInfo["equalCompareDimension"] = True
        rtrnInfo["Message"] += "Input data dimension: {} the same as compared one."
    else:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += "Input data dimension: {} NOT {}".format(dimensions, shapeD)

    # Compare greater equal
    if dimensions > shapeD:
        rtrnInfo["greaterCompareDimension"] = True

    return rtrnInfo


"""
##############################################################################
#Func: compare all list size are the same
##############################################################################
"""
import numpy


def CompareListDimension(lsts):
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["greaterCompareDimension"] = False
    rtrnInfo["equalCompareDimension"] = False
    rtrnInfo["dimensions"] = None
    rtrnInfo["message"] = ""

    # Shape of the first item
    shape0 = numpy.shape(lsts[0])

    # compare shape
    shape = []
    shape.append(shape0)
    for lst in lsts:
        # print(lst)
        # print(numpy.shape(lst))
        shape.append(numpy.shape(lst))
        if numpy.shape(lst) != shape0:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] += "Not the same shape!! {}".format(shape)

    return rtrnInfo


"""
##############################################################################
#Fucntion compare array shape
##############################################################################
"""
import numpy


def CompareArrShape(dataMat1, dataMat2, DialogWarn=False):
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = True
    rtrnInfo["errorMessage"] = "Same shape"
    rtrnInfo["shape"] = None

    # shape
    dataMat1_Shp = numpy.shape(dataMat1)
    dataMat2_Shp = numpy.shape(dataMat2)

    # Compare
    if dataMat1_Shp == dataMat2_Shp:  # same shape
        rtrnInfo["error"] = False
        rtrnInfo["shape"] = dataMat1_Shp
        return rtrnInfo
    if dataMat1_Shp != dataMat2_Shp:
        # error message
        rtrnInfo["errorMessage"] = ("Mismatch array shapes. First array shape: \n"
                                    + str(dataMat1_Shp) +
                                    "\nSecond array shape shape: \n" +
                                    str(dataMat2_Shp))

        if DialogWarn:
            Save_Load_File.JumpOrExit("Mismatch array shapes. First array shape: \n"
                                      + str(dataMat1_Shp) +
                                      "\nSecond array shape shape: \n" +
                                      str(dataMat2_Shp) +
                                      "Ignore shape difference?")

        if not DialogWarn:
            print(rtrnInfo["errorMessage"])
            print("Ignore mismatch and carry on!")

        return rtrnInfo


"""
##############################################################################
#Func: convert one mask value based on another
##############################################################################
"""
import numpy
import scipy.stats


def ConvertValMsk(inMat, valRefMat):
    # init
    outMat = None

    # compare shape
    compareShp = CompareArrShape(inMat, valRefMat, False)

    # not the same return
    if compareShp["error"]:
        return outMat

    # Binary input mat
    _, inOnes = Image_Process_Functions.FilterData(rangStarts=[0],
                                                   dataMat=inMat,
                                                   funType="single value greater")

    # create empty volume
    outMat = numpy.zeros(compareShp["shape"])

    # 2D or 3D input
    dim = numpy.shape(compareShp["shape"])
    if dim[0] == 2:  # 2D
        print("2D Fill Vals")
        # find reference non-zero most frequent value
        val = scipy.stats.mode(valRefMat[numpy.nonzero(valRefMat)])[0][0]
        # fill
        outMat = inOnes * val
    elif dim[0] == 3:  # 3D
        print("3D Fill Vals")
        valStore = 1
        for imgSlice in range(compareShp["shape"][0]):
            # each slice
            inOnesSlice = inOnes[imgSlice]
            # jump empty
            if numpy.sum(inOnesSlice) == 0:
                continue
            valRefMatSlice = valRefMat[imgSlice]

            # find reference non-zero most frequent value
            try:
                val = scipy.stats.mode(valRefMatSlice[numpy.nonzero(valRefMatSlice)])[0][0]
                valStore = val
            except IndexError:
                val = valStore

            # fill
            outMatSlice = inOnesSlice * val

            # stacking
            outMat[imgSlice] = outMatSlice

            # print("Finish Slice: {} Fill: {} Total:{}".format(
            # imgSlice, val, numpy.sum(outMatSlice)))

    else:
        print("Unsupported dimensions: {}".format(dim[0]))

    return outMat


"""
##############################################################################
#Class covert data type to reference
##############################################################################
"""
import numpy


class ConvertDType:
    def __init__(self, refDataMat, tConDataMat, inObj="Array"):
        self.refDataMat = refDataMat
        self.tConDataMat = tConDataMat
        self.inObj = inObj
        self.rtrnInfo = {}
        self.rtrnInfo["error"] = False
        self.rtrnInfo["errorMessage"] = None
        self.rtrnInfo["processTime"] = None
        self.rtrnInfo["processTimeMessage"] = None
        self.rtrnInfo["message"] = ""

        self.ArrayConvert()

    def ArrayConvert(self):
        # input data
        if self.inObj == "Array":
            # Compare shape
            CompareArrShape(dataMat1=self.refDataMat,
                            dataMat2=self.tConDataMat,
                            DialogWarn=False)

            # convert dtype
            print("Reference type: " + str(self.refDataMat.dtype))
            convertDataOldType = self.tConDataMat.dtype
            self.ConvertData = numpy.array(self.tConDataMat, dtype=self.refDataMat.dtype.type)
            print("Converted data type: " + str(self.ConvertData.dtype))
            self.rtrnInfo["message"] += "Reference type: {} " \
                                        "\nData type before conversion: {} " \
                                        "\nData type after conversion: {}\n".format(
                self.refDataMat.dtype,
                convertDataOldType,
                self.ConvertData.dtype
            )

        # input data
        if self.inObj == "Class":
            # Compare shape
            CompareArrShape(dataMat1=self.refDataMat,
                            dataMat2=self.tConDataMat,
                            DialogWarn=False)

            # convert dtype
            print("Reference type: " + str(self.refDataMat.OriData.dtype))
            self.ConvertData = numpy.array(self.tConDataMat.OriData, dtype=self.refDataMat.OriData.dtype.type)
            print("Converted data type: " + str(self.ConvertData.dtype))

    def SaveResults(self,
                    dispMsg="Save new converted data",
                    ChooseImgInfo=False,
                    imgInfo=''):
        if not ChooseImgInfo:
            Save_Load_File.SaveNIFTI(dispMsg=dispMsg,
                                     MatData=self.ConvertData,
                                     imgInfo=self.tConDataMat.OriImag)

        if ChooseImgInfo:
            Save_Load_File.SaveNIFTI(dispMsg=dispMsg,
                                     MatData=self.ConvertData,
                                     imgInfo=imgInfo)


"""
##############################################################################
#Class Adding Mask
##############################################################################
"""
import numpy
import time


class AddMask:
    def __init__(self,
                 ThresHold=0,
                 ThresholdChoice=False,
                 BackgroundVal=30,
                 setBackgroundVal=False,
                 GUI=True):
        # initial values
        self.ThresHold = ThresHold  # default
        self.BackgroundVal = BackgroundVal
        self.ThresholdChoice = ThresholdChoice
        self.BackgroundVal = BackgroundVal
        self.volumeShape = None
        self.stackVals = None
        self.stackValsNoOverLp = None
        self.stackOnes = None
        self.stackOnesNoOverLp = None
        self.stackNewVals = None
        self.stackNewValsNoOverLp = None
        # return information
        self.rtrnInfo = {}
        self.rtrnInfo["error"] = False
        self.rtrnInfo["errorMessage"] = None
        self.rtrnInfo["processTime"] = None
        self.rtrnInfo["processTimeMessage"] = None
        self.rtrnInfo["message"] = ""

        if GUI:
            self.GUIInit()

    def GUIInit(self):
        # Import first mask and create empty volume
        self.primMsk = Save_Load_File.OpenLoadNIFTI("Load first Nifiti mask")

        # Create first stack volume
        self.volumeShape = numpy.shape(self.primMsk.OriData)
        self.stackVals = numpy.zeros(self.volumeShape)
        self.stackValsNoOverLp = numpy.zeros(self.volumeShape)
        self.stackOnes = numpy.zeros(self.volumeShape)
        self.stackOnesNoOverLp = numpy.zeros(self.volumeShape)
        self.stackNewVals = numpy.zeros(self.volumeShape)
        self.stackNewValsNoOverLp = numpy.zeros(self.volumeShape)

        # Stack vals
        self.stackVals = self.primMsk.OriData
        self.stackValsNoOverLp = self.primMsk.OriData

        # Change threshold?
        if self.ThresholdChoice:
            self.ChangeThreshold()

        # Filter for ones
        Msked, MskOnes = Image_Process_Functions.FilterData(rangStarts=[self.ThresHold],
                                                            dataMat=self.primMsk.OriData,
                                                            funType="single value greater")

        # stack ones
        self.stackOnes = MskOnes
        self.stackOnesNoOverLp = MskOnes

        # Set bkg value
        if self.setBackgroundVal:
            self.SetBkgVal()

        # stack new values
        self.stackNewVals = MskOnes * self.BackgroundVal
        self.stackNewValsNoOverLp = MskOnes * self.BackgroundVal

        print(numpy.max(self.stackNewValsNoOverLp))

    def CreateInitialVol(self, matData):
        # Create first stack volume
        self.volumeShape = numpy.shape(matData)
        self.stackVals = numpy.zeros(self.volumeShape)
        self.stackValsNoOverLp = numpy.zeros(self.volumeShape)
        self.stackOnes = numpy.zeros(self.volumeShape)
        self.stackOnesNoOverLp = numpy.zeros(self.volumeShape)
        self.stackNewVals = numpy.zeros(self.volumeShape)
        self.stackNewValsNoOverLp = numpy.zeros(self.volumeShape)

    def AddMskKeepOld(self,
                      loadFilePaths,
                      values,
                      thresholds):
        """
        #Stack keep old masks and resize new ones
        """
        loadFilePathsShp = numpy.shape(loadFilePaths)

        for path in range(loadFilePathsShp[0]):
            print("Processing: " + str(path) + " in " + str(loadFilePathsShp[0]))

            loadFilePath = loadFilePaths[path]
            NewVal = values[path]
            threshold = thresholds[path]

            # Load file
            newMsk = Save_Load_File.OpenLoadNIFTI(dispMsg="Load new Nifiti mask",
                                                  fileObj=None,
                                                  tkObj=False,
                                                  GUI=False,
                                                  filePath=loadFilePath)

            # Create volume
            if path == 0:
                self.CreateInitialVol(matData=newMsk.OriData)

            if path > 0:
                # check shape
                newMskShape = numpy.shape(newMsk.OriData)

                if newMskShape != self.volumeShape:
                    if Save_Load_File.JumpOrExit("Mismatch loading mask shapes. Stacking mask shape: \n"
                                                 + str(self.volumeShape) +
                                                 "\nLoad mask shape: \n" +
                                                 str(newMskShape) +
                                                 "\nReload another mask??" +
                                                 "\nPress No: carry on without loading new masks"):
                        continue
                    else:
                        break

            # Stack vals
            self.stackVals = self.stackVals + newMsk.OriData

            # Stack ones mask
            Msked, MskOnes = Image_Process_Functions.FilterData(rangStarts=[threshold],
                                                                dataMat=newMsk.OriData,
                                                                funType="single value greater")

            # Stacking vslues ONLY not overlay ones
            oneSubtract = numpy.zeros(self.volumeShape)
            oneSubtract = MskOnes - self.stackOnesNoOverLp
            Msked, MskOnesNoOverLp = Image_Process_Functions.FilterData(rangStarts=[0],
                                                                        dataMat=oneSubtract,
                                                                        funType="single value greater")
            # Stack ones mask
            self.stackOnes = self.stackOnes + MskOnes

            # Stack new value
            self.stackNewVals = self.stackNewVals + MskOnes * NewVal

            # Stack ones mask no overlap
            self.stackOnesNoOverLp = self.stackOnesNoOverLp + MskOnesNoOverLp

            # Satck values no overlap
            self.stackValsNoOverLp = self.stackValsNoOverLp + numpy.multiply(MskOnesNoOverLp, newMsk.OriData)

            # Stack new value with no overlap
            self.stackNewValsNoOverLp = self.stackNewValsNoOverLp + MskOnesNoOverLp * NewVal

    def AddMskKeepNew(self,
                      loadFilePaths,
                      values,
                      thresholds,
                      addNwVal=True):
        """
        #keep the New shape
        #satcking no overlap is based on remove old mask 
        #   overlapping region
        """

        # time
        strtT = time.time()

        print("Adding masks keep later/newer ones")
        loadFilePathsShp = numpy.shape(loadFilePaths)

        for path in range(loadFilePathsShp[0]):
            print("Processing: " + str(path) + " in " + str(loadFilePathsShp[0]))

            loadFilePath = loadFilePaths[path]
            threshold = thresholds[path]

            # Load file
            newMsk = Save_Load_File.OpenLoadNIFTI(dispMsg="",
                                                  fileObj=None,
                                                  tkObj=False,
                                                  GUI=False,
                                                  filePath=loadFilePath)

            # Create volume
            if path == 0:
                # create empty volumes
                self.CreateInitialVol(matData=newMsk.OriData)
            else:
                # check shape
                newMskShape = numpy.shape(newMsk.OriData)

                if newMskShape != self.volumeShape:
                    rtrnInfo["error"] = True
                    rtrnInfo["errorMessage"] = "Mismatch loading mask shapes. Stacking mask shape: \n" \
                                               + str(self.volumeShape) \
                                               + "\nLoad mask shape: \n" \
                                               + str(newMskShape)
                    return

            # Stack ones mask
            Msked, MskOnes = Image_Process_Functions.FilterData(rangStarts=[threshold],
                                                                dataMat=newMsk.OriData,
                                                                funType="single value greater")

            # Stacking vslues ONLY not overlay ones
            oneSubtract = numpy.zeros(self.volumeShape)
            oneSubtract = self.stackOnesNoOverLp - MskOnes
            Msked, MskOnesNoOverLp = Image_Process_Functions.FilterData(rangStarts=[0],
                                                                        dataMat=oneSubtract,
                                                                        funType="single value greater")

            # # stacking results with overlapping
            # # Stack vals
            # self.stackVals = self.stackVals + newMsk.OriData
            # # Stack ones mask
            # self.stackOnes = self.stackOnes + MskOnes

            # stacking results with overlapping
            ## Stack ones mask no overlap
            self.stackOnesNoOverLp = numpy.multiply(self.stackOnesNoOverLp, MskOnesNoOverLp) + MskOnes
            ## Satck values no overlap
            self.stackValsNoOverLp = newMsk.OriData + numpy.multiply(MskOnesNoOverLp, self.stackValsNoOverLp)

            # stacking new values
            if addNwVal:
                NewVal = values[path]
                # # Stack new value with overlapping
                # self.stackNewVals = self.stackNewVals + MskOnes * NewVal
                # Stack new value with no overlap
                self.stackNewValsNoOverLp = numpy.multiply(MskOnesNoOverLp,
                                                           self.stackNewValsNoOverLp) + MskOnes * NewVal

        # return information
        stpT = time.time()
        self.rtrnInfo["processTime"] = stpT - strtT
        self.rtrnInfo["processTimeMessage"] = "------Add mask keep NEW time: {} s------".format(
            self.rtrnInfo["processTime"])
        self.rtrnInfo["message"] += "Complete: \n {}".format(self.rtrnInfo["processTimeMessage"])
        print("Complete: \n {}".format(self.rtrnInfo["processTimeMessage"]))

    def AddMoreMskKeepOld(self, ThresholdChoice=False, NewValueChoice=True):
        """
        #The inital mask will keep the oritginal shape
        #satcking no overlap is based on remove new mask 
        #   overlapping region
        """
        NewVal = self.BackgroundVal
        while True:
            # Load file
            if not Save_Load_File.JumpOrExit("Load and stack one more mask?"):
                break

            newMsk = Save_Load_File.OpenLoadNIFTI("Load new Nifiti mask")

            # check shape
            newMskShape = numpy.shape(newMsk.OriData)

            if newMskShape != self.volumeShape:
                if Save_Load_File.JumpOrExit("Mismatch loading mask shapes. Stacking mask shape: \n"
                                             + str(self.volumeShape) +
                                             "\nLoad mask shape: \n" +
                                             str(newMskShape) +
                                             "\nReload another mask??" +
                                             "\nPress No: carry on without loading new masks"):
                    continue
                else:
                    break

            # Stack vals
            self.stackVals = self.stackVals + newMsk.OriData

            # Stack ones mask
            # Change threshold?
            if ThresholdChoice:
                self.ChangeThreshold()

            Msked, MskOnes = Image_Process_Functions.FilterData(rangStarts=[self.ThresHold],
                                                                dataMat=newMsk.OriData,
                                                                funType="single value greater")

            # New values for the mask
            if NewValueChoice:
                NewVal = float(input("Input new mask value: "))

            # Stacking vslues ONLY not overlay ones
            oneSubtract = numpy.zeros(self.volumeShape)
            oneSubtract = MskOnes - self.stackOnesNoOverLp
            Msked, MskOnesNoOverLp = Image_Process_Functions.FilterData(rangStarts=[0],
                                                                        dataMat=oneSubtract,
                                                                        funType="single value greater")
            # Stack ones mask
            self.stackOnes = self.stackOnes + MskOnes

            # Stack new value
            self.stackNewVals = self.stackNewVals + MskOnes * NewVal

            # Stack ones mask no overlap
            self.stackOnesNoOverLp = self.stackOnesNoOverLp + MskOnesNoOverLp

            # Satck values no overlap
            self.stackValsNoOverLp = self.stackValsNoOverLp + numpy.multiply(MskOnesNoOverLp, newMsk.OriData)

            # Stack new value with no overlap
            self.stackNewValsNoOverLp = self.stackNewValsNoOverLp + MskOnesNoOverLp * NewVal

    def AddMoreMskKeepNew(self, ThresholdChoice=False, NewValueChoice=True):
        """
        #The inital mask will keep the New shape
        #satcking no overlap is based on remove old mask 
        #   overlapping region
        """
        NewVal = 10
        while True:
            # Load file
            if not Save_Load_File.JumpOrExit("Load and stack one more mask?"):
                break

            newMsk = Save_Load_File.OpenLoadNIFTI("Load new Nifiti mask")

            # check shape
            newMskShape = numpy.shape(newMsk.OriData)

            if newMskShape != self.volumeShape:
                if Save_Load_File.JumpOrExit("Mismatch loading mask shapes. Stacking mask shape: \n"
                                             + str(self.volumeShape) +
                                             "\nLoad mask shape: \n" +
                                             str(newMskShape) +
                                             "\nReload another mask??" +
                                             "\nPress No: carry on without loading new masks"):
                    continue
                else:
                    break

            # Stack vals
            self.stackVals = self.stackVals + newMsk.OriData

            # Stack ones mask
            # Change threshold?
            if ThresholdChoice:
                self.ChangeThreshold()

            Msked, MskOnes = Image_Process_Functions.FilterData(rangStarts=[self.ThresHold],
                                                                dataMat=newMsk.OriData,
                                                                funType="single value greater")

            # New values for the mask
            if NewValueChoice:
                NewVal = float(input("Input new mask value: "))

            # Stacking vslues ONLY not overlay ones
            oneSubtract = numpy.zeros(self.volumeShape)
            oneSubtract = self.stackOnesNoOverLp - MskOnes
            Msked, MskOnesNoOverLp = Image_Process_Functions.FilterData(rangStarts=[0],
                                                                        dataMat=oneSubtract,
                                                                        funType="single value greater")

            # Use_Plt.slider3Display(matData1=MskOnes,
            #                        matData2=oneSubtract,
            #                        matData3=[0],
            #                        fig3OverLap=True,
            #                        ShareX=True,
            #                        ShareY=True,
            #                        ask23MatData=False,
            #                        OneOverTwo=True,
            #                        title=["Input", "Mask", "Overlapping"],
            #                        plotRange=[False, False, False],
            #                        winMin=[0, 0, 0],
            #                        winMax=[100, 100, 100],
            #                        cmapChoice='gray')

            # Stack new value
            self.stackNewVals = self.stackNewVals + MskOnes * NewVal

            # Stack ones mask
            self.stackOnes = self.stackOnes + MskOnes

            # Stack ones mask no overlap
            self.stackOnesNoOverLp = numpy.multiply(self.stackOnesNoOverLp, MskOnesNoOverLp) + MskOnes

            # Satck values no overlap
            self.stackValsNoOverLp = newMsk.OriData + numpy.multiply(MskOnesNoOverLp, self.stackValsNoOverLp)

            # Stack new value with no overlap
            self.stackNewValsNoOverLp = numpy.multiply(MskOnesNoOverLp, self.stackNewValsNoOverLp) + MskOnes * NewVal

    def ChangeThreshold(self):
        if Save_Load_File.JumpOrExit("Set new Threshold for the input mask?"):
            self.ThresHold = float(input("Input new threshold value: "))

    def SetBkgVal(self):
        if Save_Load_File.JumpOrExit("Set Primary mask value?"):
            self.BackgroundVal = float(input("Input new primary mask value: "))

    def DispOverLp(self, dataMat, overDataMat):
        if Save_Load_File.JumpOrExit("Display New Vals Mask No OverLp?"):
            Use_Plt.slider3Display(matData1=dataMat,
                                   matData2=overDataMat,
                                   matData3=[0],
                                   fig3OverLap=True,
                                   ShareX=True,
                                   ShareY=True,
                                   ask23MatData=False,
                                   OneOverTwo=True,
                                   title=["Input", "Mask", "Overlapping"],
                                   plotRange=[False, False, False],
                                   winMin=[0, 0, 0],
                                   winMax=[100, 100, 100],
                                   cmapChoice='gray')

    def ConvertSave(self,
                    tConDataMat,
                    imgInfo="",
                    refDataMat=None,
                    GUI=True,
                    filePath=None):
        # N0 input reference
        if refDataMat is None:  # 1d is the default
            self.NewValsNoOverLp_convertData = ConvertDType(refDataMat=self.primMsk,
                                                            tConDataMat=tConDataMat,
                                                            inObj="Array")
            # convert
            self.NewValsNoOverLp_convertData.ArrayConvert()

            # Save
            Save_Load_File.SaveNIFTI(dispMsg="Save new converted data",
                                     MatData=self.NewValsNoOverLp_convertData.ConvertData,
                                     imgInfo=self.primMsk.OriImag,
                                     GUI=GUI,
                                     filePath=filePath)
        else:
            self.NewValsNoOverLp_convertData = ConvertDType(refDataMat=refDataMat,
                                                            tConDataMat=tConDataMat,
                                                            inObj="Array")
            # convert
            self.NewValsNoOverLp_convertData.ArrayConvert()

            # Save
            Save_Load_File.SaveNIFTI(dispMsg="Save new converted data",
                                     MatData=self.NewValsNoOverLp_convertData.ConvertData,
                                     imgInfo=imgInfo,
                                     GUI=GUI,
                                     filePath=filePath)


"""
##############################################################################
# Filter thresholding values based on thresholding, 2D area and 3D volume 
##############################################################################
"""
import numpy
import copy
import skimage.morphology


class FilterValAreaVol:

    def __init__(
            self,
            oriMatData
    ):
        # init
        self.oriMatData = oriMatData
        self.oriMatDataShp = numpy.shape(self.oriMatData)
        self.oriMatDataShpShp = numpy.shape(self.oriMatDataShp)
        self.oriMatDataMsked = None
        self.areaMskOnes = numpy.zeros(self.oriMatDataShp)
        self.volMskOnes = None
        self.smoothMskOnes = None
        self.outData = None
        # self.areaVals = numpy.zeros(self.oriMatDataShp)
        # self.volVals = None

        # Check use of MaskData function
        self.msk = False
        # return information
        self.rtrnInfo = {
            "error": False,
            "message": ""
        }

    def MaskData(
            self,
            msk,
            mskRemove=None,
            remove=False,
            mskThres=0
    ):

        if remove and mskRemove is not None:
            # comparing shape
            mskShp = numpy.shape(msk)
            mskRemoveShp = numpy.shape(mskRemove)
            ## warning
            if self.oriMatDataShp != mskShp or self.oriMatDataShp != mskRemoveShp:
                print("Incorrect mask shape: \n"
                      + "mskShp: " + str(mskShp)
                      + "mskRemoveShp: " + str(mskRemoveShp)
                      + "Data shape: " + str(self.oriMatDataShp))
                self.rtrnInfo["message"] += "\nIncorrect mask shape: \n" \
                                            + "mskShp: " + str(mskShp) \
                                            + "mskRemoveShp: " + str(mskRemoveShp) \
                                            + "Data shape: " + str(self.oriMatDataShp)
                return

            # binary masks
            msk = (msk != 0) * 1
            mskRemove = (mskRemove != 0) * 1

            # remove mskRemove from msk
            _, self.Msks = Image_Process_Functions.FilterData(
                rangStarts=[mskThres],
                dataMat=msk - mskRemove,
                funType="single value greater"
            )

            # msg
            msg = "Remove reference mask"
            self.rtrnInfo["message"] = "\n" + msg
            print(msg)

        elif not remove:
            # comparing shape
            mskShp = numpy.shape(msk)
            ## warning
            if self.oriMatDataShp != mskShp:
                print("Incorrect mask shape: \n"
                      + "mskShp: " + str(mskShp)
                      + "Data shape: " + str(self.oriMatDataShp))
                self.rtrnInfo["message"] = "\nIncorrect mask shape: \n" \
                                           + "mskShp: " + str(mskShp) \
                                           + "Data shape: " + str(self.oriMatDataShp)
                return

            # Binarinise mask
            _, self.Msks = Image_Process_Functions.FilterData(
                rangStarts=[mskThres],
                dataMat=msk,
                funType="single value greater"
            )

            # msg
            msg = "NO reference mask"
            self.rtrnInfo["message"] = "\n" + msg
            print(msg)

        else:
            print("Need to provide mskRemove!!!")
            self.rtrnInfo["message"] += "\nNeed to provide mskRemove!!!"
            return

        # Masking
        self.oriMatDataMsked = numpy.multiply(self.Msks, self.oriMatData)

        # update using msk
        self.msk = True

    def FilterArea(
            self,
            rangStarts=[0],
            rangStops=[0],
            funType="single value",
            openOp=True,
            openR=1,
            closeOp=True,
            closeR=2
    ):

        # Determine the shape > 2D is for loop
        dataMat = None
        threeDFlg = False
        if self.oriMatDataShpShp[0] >= 3:
            threeDFlg = True

        # Masked or not
        if self.msk:
            dataMat = self.oriMatDataMsked
        elif not self.msk:
            dataMat = self.oriMatData

        # each slice filtering default in first/depth direction
        if threeDFlg:
            for imgSlic in range(self.oriMatDataShp[0]):
                # jump zeros
                if numpy.sum(self.Msks[imgSlic]) == 0:
                    continue

                dataSlic = dataMat[imgSlic]

                # Filter
                _, dataSlicMsks = Image_Process_Functions.FilterData(
                    rangStarts=rangStarts,
                    rangStops=rangStops,
                    dataMat=dataSlic,
                    funType=funType
                )

                # Morphology operation
                if openOp and closeOp:
                    # Fixing Disk
                    # Create disk
                    selem1 = skimage.morphology.disk(openR)
                    selem2 = skimage.morphology.disk(closeR)

                    # open with 1 pixel
                    mskOpen = skimage.morphology.opening(dataSlicMsks, selem1)

                    # close with 2 pixels
                    mskClose = skimage.morphology.closing(mskOpen, selem2)

                    # Stack values
                    self.areaMskOnes[imgSlic] = mskClose
                    # self.areaVals[imgSlic] = numpy.multiply(mskClose, dataSlic)
                    print("Filter slice: {}/{} with Open + Close".format(imgSlic, self.oriMatDataShp[0]))

                elif openOp and not closeOp:
                    # Fixing Disk
                    # Create disk
                    selem1 = skimage.morphology.disk(openR)

                    # open with 1 pixel
                    mskOpen = skimage.morphology.opening(dataSlicMsks, selem1)

                    # Stack values
                    self.areaMskOnes[imgSlic] = mskOpen
                    # self.areaVals[imgSlic] = numpy.multiply(mskOpen, dataSlic)
                    print("Filter slice: {}/{} with Open".format(imgSlic, self.oriMatDataShp[0]))

                elif not openOp and closeOp:
                    # Fixing Disk
                    # Create disk
                    selem2 = skimage.morphology.disk(closeR)

                    # close with 1 pixels
                    mskClose = skimage.morphology.closing(dataSlicMsks, selem2)

                    # Stack values
                    self.areaMskOnes[imgSlic] = mskClose
                    # self.areaVals[imgSlic] = numpy.multiply(mskClose, dataSlic)
                    print("Filter slice: {}/{} with Close".format(imgSlic, self.oriMatDataShp[0]))

                else:
                    self.areaMskOnes[imgSlic] = dataSlicMsks
                    # self.areaVals[imgSlic] = numpy.multiply(dataSlicMsks, dataSlic)
                    print("Filter slice: {}/{} no morphology".format(imgSlic, self.oriMatDataShp[0]))

    def FilterAreaVol(
            self,
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

        # volume input
        if self.oriMatDataShpShp[0] < 3:
            print("Not a 3D volume input: \n"
                  + "Data shape: " + str(self.oriMatDataShp))
            self.rtrnInfo["message"] += "\nNot a 3D volume input: \n" \
                                        + "Data shape: " + str(self.oriMatDataShp)
            return

        # Connectivity and filter
        _, self.volMskOnes, self.outData = Image_Process_Functions.ConnectivityAreaVolFilter(
            matData=self.areaMskOnes,
            connectType=connectType,
            FilterThres=FilterThres,
            smooth=smooth,
            radialSamplingSize=radialSamplingSize,
            initSplineSmooth=initSplineSmooth,
            initRadialSplineOrder=initRadialSplineOrder,
            vertRadialSplineOrder=vertRadialSplineOrder,
            vertSplineSmoothFac=vertSplineSmoothFac,
            resInt=resInt,
            planeSmoothOrder=planeSmoothOrder,
            planeSplineSmoothFac=planeSplineSmoothFac
        )

        # output
        if smooth:
            self.outData = self.outData
        else:
            self.outData = self.volMskOnes

        ## Vals
        # self.volVals = numpy.multiply(self.volMskOnes, self.oriMatData)

    def NoFilterAreaVol(self):
        # Jump connectivity
        self.volMskOnes = copy.deepcopy(self.areaMskOnes)
        self.outData = self.volMskOnes

        ## Vals
        # self.volVals = numpy.multiply(self.volMskOnes, self.oriMatData)

    def PlotFilterAreaVol(self):
        Use_Plt.slider3Display(matData1=self.oriMatDataMsked,
                               matData2=self.volMskOnes,
                               fig3OverLap=True,
                               ask23MatData=False,
                               OneOverTwo=False,
                               ContourOver=True,
                               title=["CTA", "Mask", "Contour"],
                               plotRange=[True, False, True],
                               winMin=[-50, 0, -5],
                               winMax=[200, 100, 200],
                               cmapChoice='gray')

    def Plot3D(self):
        # Add value
        # with mask
        if self.msk:
            threeDVis = self.Msks + self.volMskOnes
        if not self.msk:
            dataMatMsked, Msks = Image_Process_Functions.FilterData(rangStarts=[0],
                                                                    dataMat=self.oriMatData,
                                                                    funType="single value greater")
            threeDVis = Msks + self.volMskOnes

    def ConvertSave(self,
                    tConDataMat,
                    imgInfo,
                    refDataMat=[0],
                    dispMsg="Save new converted data"):
        # N0 input reference
        if numpy.shape(numpy.shape(refDataMat)) == 1:  # 1d is the default
            self.oneMskConvertData = ConvertDType(refDataMat=self.oriMatData,
                                                  tConDataMat=tConDataMat,
                                                  inObj="Array")
            # convert
            self.oneMskConvertData.ArrayConvert()

            # Save
            Save_Load_File.SaveNIFTI(dispMsg=dispMsg,
                                     MatData=self.oneMskConvertData.ConvertData,
                                     imgInfo=imgInfo)
        else:
            self.oneMskConvertData = ConvertDType(refDataMat=refDataMat,
                                                  tConDataMat=tConDataMat,
                                                  inObj="Array")
            # convert
            self.oneMskConvertData.ArrayConvert()

            # Save
            Save_Load_File.SaveNIFTI(dispMsg=dispMsg,
                                     MatData=self.oneMskConvertData.ConvertData,
                                     imgInfo=imgInfo)


"""
##############################################################################
#Func: Func KNN matching
##############################################################################
"""
import sklearn.neighbors
import numpy
import time


def MatchResultsMask(
        inPath,
        mask3DCoors_XYZ,
        maskCTCoors_ZYX,
        maskMat,
        outPath,
        imgInfo,
        leafSize=600,
        filterZero=False,
        radius=None,
        outPutLog=False,
        outLogPath=''
):
    """
    KNN 3D matching + value filling masks
    """
    # timing
    startT = time.time()
    # print('In MatchResultsMask KNN start time: {}'.format(startT))

    # Load data
    # np.array[ndLst, ndCoo (X, Y, Z), TAWSS] {node_numbers * 5}
    print("Load NPY path: {}".format(inPath))
    arr = numpy.load(inPath)

    # Ball tree nearest neighbour
    if filterZero:
        # set results
        modelCoors = arr[numpy.where(arr[:, 4] != 0)][:, 1:4]
        lstVals = arr[numpy.where(arr[:, 4] != 0)][:, 4]
        nodeIDs = arr[numpy.where(arr[:, 4] != 0)][:, 0]
        msg = "Filter Zeros: length {} -> {}".format(numpy.shape(arr[:, 4])[0], numpy.shape(lstVals)[0])

        # create ball nearest neighbour
        tree = sklearn.neighbors.BallTree(
            modelCoors,
            leaf_size=min(leafSize, int(numpy.ceil(numpy.shape(lstVals)[0] / 10)))
        )

        # ball tree match
        (NN_indices, NN_distances) = tree.query_radius(
            mask3DCoors_XYZ,
            r=radius,
            return_distance=True,
            sort_results=True
        )
        print(msg)
    else:
        # set results
        modelCoors = arr[:, 1:4]
        lstVals = arr[:, 4]
        # ball tree
        nbrs = sklearn.neighbors.NearestNeighbors(
            n_neighbors=1,
            algorithm='ball_tree',
            leaf_size=min(leafSize, int(numpy.ceil(numpy.shape(lstVals)[0] / 10)))
        ).fit(modelCoors)
        NN_distances, NN_indices = nbrs.kneighbors(
            mask3DCoors_XYZ
        )
        print("No filtering of zeros values")

    # timing
    KNN_time = time.time()
    # print("--- KNN time: %s seconds ---" % (KNN_time - startT))

    # Filling in empty CT
    ## Empty CT space
    val_CT = numpy.zeros(numpy.shape(maskMat))
    # print(numpy.shape(maskMat))
    # print(numpy.shape(val_CT))

    # output log
    outMsg = ""

    ## Filling
    maskPnts = numpy.shape(NN_indices)
    # print('Filling')
    for i in range(maskPnts[0]):
        # closest indices
        if NN_indices[i].size != 0:  # NOT empty array
            CT_Index = NN_indices[i][0]
            # print("Index: %s " % (CT_Index))
            CTX = maskCTCoors_ZYX[i][0]
            CTY = maskCTCoors_ZYX[i][1]
            CTZ = maskCTCoors_ZYX[i][2]
            # print(CTX, CTY, CTZ)
            # print(val_CT[CTX][CTY][CTZ])
            # print(lstVals[CT_Index])
            val_CT[CTX][CTY][CTZ] = lstVals[CT_Index]
            # print("complete: %s" % (i))

            if outPutLog and filterZero:
                # print('nodeIDs: {}'.format(numpy.shape(nodeIDs)))
                # print('modelCoors: {}'.format(numpy.shape(modelCoors)))

                msg = 'CT point: X={} ({}), Y={} ({}), Z={} ({})' \
                      ''.format(mask3DCoors_XYZ[i][0], CTZ, mask3DCoors_XYZ[i][1], CTY, mask3DCoors_XYZ[i][2], CTX) + \
                      ' Match Node={}, X={}, Y={}, Z={} >> distance={}' \
                      ''.format(nodeIDs[CT_Index], modelCoors[CT_Index][0], modelCoors[CT_Index][1],
                                modelCoors[CT_Index][2], NN_distances[i][0]) + \
                      '\n All indices: {} and distances: {} \n'.format(NN_indices[i], NN_distances[i])

                outMsg += msg

    # Save
    # print("CT mask dtype:{}".format(val_CT.dtype))
    # print('output path: ' + outPath)
    Save_Load_File.MatNIFTISave(
        MatData=val_CT,
        imgPath=outPath,
        imgInfo=imgInfo,
        ConvertDType=False,
        refDataMat=maskMat
    )  # CT is INT!!!! Data is Float!!!

    if outPutLog:
        Save_Load_File.WriteTXT(path=outLogPath, txt=outMsg, mode="write")

    # timing
    fillingT = time.time()
    print("--- Filling Map Results KNN time: %s seconds ---" % (fillingT - KNN_time))

    resultsDict = {
        "Value_CT": val_CT,
        "Start_Time": startT,
        "KNN_Time": KNN_time,
        "Fill_Time": fillingT
    }

    return resultsDict


"""
##############################################################################
# func: Multiprocessing Match KNN !! Cannot use multiprocessing in a CLASS !!
##############################################################################
"""
import numpy
import multiprocessing
from multiprocessing import Pool


def MultiProKNN(
        inputPaths,
        outputPaths,
        leafSize,
        cpus,
        mask3DCoors_XYZ,
        maskCTCoors_ZYX,
        maskIn,
        filterZero=False,
        radius=None,
        outPutLog=False,
        outLogPath=''
):
    # time
    strtT = time.time()

    # return
    rtrnInfo = {"processTime": None, "processTimeMessage": "",
                "Message": ""}

    maskMat = maskIn.OriData
    imgInfo = maskIn.OriImag

    # multiprocessors
    if cpus == 1:
        for path in range(len(inputPaths)):
            inPath = inputPaths[path]
            outPath = outputPaths[path]
            MatchResultsMask(
                inPath,
                mask3DCoors_XYZ,
                maskCTCoors_ZYX,
                maskMat,
                outPath,
                imgInfo,
                leafSize,
                filterZero,
                radius,
                outPutLog,
                outLogPath
            )
    else:
        p = Pool(cpus)
        for path in range(len(inputPaths)):
            inPath = inputPaths[path]
            outPath = outputPaths[path]
            p.apply_async(MatchResultsMask, args=(
                inPath,
                mask3DCoors_XYZ,
                maskCTCoors_ZYX,
                maskMat,
                outPath,
                imgInfo,
                leafSize,
                filterZero,
                radius,
                outPutLog,
                outLogPath
            )
                          )

        print("Processing all paths")
        p.close()
        # print("Close pool")
        p.join()
        print('All subprocesses done.')

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Running KNN & Multiprocessing time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["Message"] += "Complete KNN & Multiprocessing running: \n {}".format(rtrnInfo["processTimeMessage"])
    print("Complete KNN & Multiprocessing running: \n {}".format(rtrnInfo["processTimeMessage"]))

    return rtrnInfo


"""
##############################################################################
# Func: Image value ratio calculation
##############################################################################
"""
import numpy


def ImageValueRatio(
        inData,
        meanCalcsData,
        rangeStart,
        rangeFinish,
        sliceDirection='X',
        saveFile=False,
        savePath="",
        imgInfo=None
):
    # time
    strtT = time.time()

    # return
    rtrnInfo = {
        "processTime": None,
        "processTimeMessage": "",
        "Message": "",
        "errorMessage": "",
        "outPutRatio": None
    }

    # check 3D data
    rtrnInfo3D = CompareArrayDimension(dataMat=meanCalcsData,
                                       shapeD=3)
    if rtrnInfo3D["error"]:
        print(rtrnInfo3D["errorMessage"] + "\n STOP processing!!")
        rtrnInfo["errorMessage"] += rtrnInfo3D["errorMessage"] + "\n STOP processing!!"
        return rtrnInfo
    rtrnInfo3D = CompareArrayDimension(dataMat=inData,
                                       shapeD=3)
    if rtrnInfo3D["error"]:
        print(rtrnInfo3D["errorMessage"] + "\n STOP processing!!")
        rtrnInfo["errorMessage"] += rtrnInfo3D["errorMessage"] + "\n STOP processing!!"
        return rtrnInfo

    # Get mean denominator
    ## non-zero
    if sliceDirection == 'X':
        dataRange = meanCalcsData[numpy.where(meanCalcsData[rangeStart:rangeFinish, :, :] != 0)]
    elif sliceDirection == 'Y':
        dataRange = meanCalcsData[numpy.where(meanCalcsData[:, rangeStart:rangeFinish, :] != 0)]
    elif sliceDirection == 'Z':
        dataRange = meanCalcsData[numpy.where(meanCalcsData[:, :, rangeStart:rangeFinish] != 0)]
    else:
        rtrnInfo["errorMessage"] += "Input slicing direction: '{}' not recognised!\n STOP processing!!".format(
            sliceDirection)
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    ## mean of the interquartile range
    q75, q25 = numpy.percentile(dataRange, [75, 25])
    dataRangeIQRTF = (dataRange > 0) * 1 - (((dataRange > q75) * 1 + (dataRange < q25) * 1) > 0) * 1
    dataRangeIQR = dataRange[numpy.where(dataRangeIQRTF != 0)]
    dataRangeIQRAve = numpy.mean(dataRangeIQR)

    ## warning for 0 mean
    if dataRangeIQRAve == 0:
        rtrnInfo["errorMessage"] += "ZERO denominator!!!!\n STOP processing!!"
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    # division
    outData = numpy.zeros(numpy.shape(inData))
    outData = numpy.divide(inData, dataRangeIQRAve)
    # check extension
    dataRangeIQRAve_SavePth = ""
    if ".nii.gz" in savePath:
        head, _ = os.path.split(savePath)
        dataRangeIQRAve_SavePth += head + "/"
    else:
        dataRangeIQRAve_SavePth = savePath
    # msg
    numpy.save(dataRangeIQRAve_SavePth + "CTFFRIQRAverageValue.npy", dataRangeIQRAve)
    # save
    if saveFile:
        Save_Load_File.MatNIFTISave(MatData=outData,
                                    imgPath=savePath,
                                    imgInfo=imgInfo,
                                    ConvertDType=False)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Ratio calculation time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["Message"] += "Complete ratio calculation running: \n {}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["Message"])

    return rtrnInfo


"""
##############################################################################
# Func: Average area of 3D mat data
##############################################################################
"""

import numpy


def AverageArea(
        inData,
        thres=0
):
    # time
    strtT = time.time()

    # return
    rtrnInfo = {
        "processTime": None,
        "processTimeMessage": "",
        "Message": "",
        "errorMessage": "",
        "averageArea": None,
        "nonzeroSlices": None
    }

    # check 3D data
    rtrnInfo3D = CompareArrayDimension(dataMat=inData,
                                       shapeD=3)
    if rtrnInfo3D["error"]:
        print(rtrnInfo3D["errorMessage"] + "\n STOP processing!!")
        rtrnInfo["errorMessage"] += rtrnInfo3D["errorMessage"] + "\n STOP processing!!"
        return rtrnInfo

    # Binary
    inData = (inData > thres) * 1

    # get none zero slices and average
    inDataShape = numpy.shape(inData)
    area = []
    slices = 0
    ## X direction
    for slice in range(inDataShape[0]):
        # area
        imgSum = numpy.sum(inData[slice])

        # jump for zero area
        if imgSum == 0:
            continue
        else:
            area.append(imgSum)
            slices += 1

    ## average:
    if slices > 0:
        area = numpy.array(area)
        rtrnInfo["averageArea"] = numpy.nanmean(area)
        rtrnInfo["medianArea"] = numpy.nanmedian(area)
        rtrnInfo["Q1Area"] = numpy.percentile(area, 25)
        rtrnInfo["Q3Area"] = numpy.percentile(area, 75)
        rtrnInfo["minArea"] = numpy.nanmin(area)
        rtrnInfo["maxArea"] = numpy.nanmax(area)
    else:
        rtrnInfo["averageArea"] = 0
        rtrnInfo["medianArea"] = 0
        rtrnInfo["Q1Area"] = 0
        rtrnInfo["Q3Area"] = 0
        rtrnInfo["minArea"] = 0
        rtrnInfo["maxArea"] = 0
        rtrnInfo["errorMessage"] = "ALL slices are '0'!"
        print("ALL slices are '0'!")
        print('Sum Volume: {}'.format(numpy.sum(inData)))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Area calculation time: {} s------".format(
        rtrnInfo["processTime"])
    print(rtrnInfo["Message"])
    msg = "Complete area calculation: " + \
          "\naverageArea = {}".format(rtrnInfo["averageArea"]) + \
          "\nmedianArea = {}".format(rtrnInfo["medianArea"]) + \
          "\nQ1Area = {}".format(rtrnInfo["Q1Area"]) + \
          "\nQ3Area = {}".format(rtrnInfo["Q3Area"]) + \
          "\nminArea = {}".format(rtrnInfo["minArea"]) + \
          "\nmaxArea = {}".format(rtrnInfo["maxArea"])
    rtrnInfo["Message"] += msg

    return rtrnInfo


"""
##############################################################################
# Func: Average area of 3D mat data
##############################################################################
"""


def AreaList(
        files,
        lbls
):
    areaLst = []
    for case in range(len(files)):
        # load data
        mask = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=files[case]
        )

        # Filter value
        dataFilterVals, dataFilterOnes = Image_Process_Functions.FilterData(
            rangStarts=[lbls[case]],
            dataMat=mask.OriData,
            funType="single value"
        )

        # Average area
        areas = AverageArea(
            inData=dataFilterOnes,
            thres=0
        )

        # area choice
        areaLst.append(areas["averageArea"])

    print("Func AverageAreaList: \nAreas: ", areaLst)

    return areaLst


"""
##############################################################################
# Func: Xsection related single-/two-phase morphology
##############################################################################
"""
import numpy
import scipy.ndimage
import skimage.measure
import pandas


def XsectionMorphology(
        tablePath,
        twoPhase=True,
        labelThresStarts=[[0], [0]],
        labelThresStops=[[0], [0]],
        ThresTypes=["single value greater", "single value greater"],
        SaveIntermediate=True,
        outTablePath=""
):
    # load table
    batchDataFrame = Pd_Funs.OpenDF(tablePath, header=0)

    # two phase compare
    if twoPhase:
        # initiate
        index = 0
        dfOut = None

        for ID, \
                maskPath1, \
                startSlice1, \
                stopSlice1, \
                maskPath2, \
                startSlice2, \
                stopSlice2, \
                diagPath \
                in zip(
            batchDataFrame["Patient ID"].tolist(),
            batchDataFrame["Diastole Phase Segmentation"].tolist(),
            batchDataFrame["Diastole ROI Start Slice"].tolist(),
            batchDataFrame["Diastole ROI Stop Slice"].tolist(),
            batchDataFrame["Systole Phase Segmentation"].tolist(),
            batchDataFrame["Systole ROI Start Slice"].tolist(),
            batchDataFrame["Systole ROI Stop Slice"].tolist(),
            batchDataFrame["Diagnosis Paths"].tolist()
        ):
            # load masks
            print(maskPath1)
            oriMask1 = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=maskPath1
            )
            print(maskPath2)
            oriMask2 = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=maskPath2
            )

            # create diagnosis path
            diagCreate = Save_Load_File.checkCreateDir(diagPath)

            if diagCreate["error"]:
                fullParentDir1, ParentDir1 = Save_Load_File.ParentDir(path=maskPath1)
                diagPath = fullParentDir1

            # get actual spcaing and unit area
            spacing1 = oriMask1.OriImag.GetSpacing()
            spacing_z1 = spacing1[0]  # numpy array has flipped X and Z
            spacing_y1 = spacing1[1]
            spacing_x1 = spacing1[2]
            unitArea1 = spacing_z1 * spacing_y1

            spacing2 = oriMask2.OriImag.GetSpacing()
            spacing_z2_old = spacing2[0]  # numpy array has flipped X and Z
            spacing_y2_old = spacing2[1]
            spacing_x2_old = spacing2[2]

            # binary data
            _, oriMaskOnes1 = Image_Process_Functions.FilterData(rangStarts=labelThresStarts[0],
                                                                 rangStops=labelThresStops[0],
                                                                 dataMat=oriMask1.OriData,
                                                                 funType=ThresTypes[0])
            _, oriMaskOnes2 = Image_Process_Functions.FilterData(rangStarts=labelThresStarts[1],
                                                                 rangStops=labelThresStops[1],
                                                                 dataMat=oriMask2.OriData,
                                                                 funType=ThresTypes[1])
            # trimmed data
            # range correction
            startSlice1, stopSlice1 = Matrix_Math.SliceNumberCorrect(
                sliceStart=int(startSlice1) - 1,  # itk snap correction
                sliceStop=int(stopSlice1) - 1,
                boundaryStart=0,
                boundaryStop=numpy.shape(oriMaskOnes1)[0],
            )
            startSlice2, stopSlice2 = Matrix_Math.SliceNumberCorrect(
                sliceStart=int(startSlice2) - 1,  # itk snap correction
                sliceStop=int(stopSlice2) - 1,
                boundaryStart=0,
                boundaryStop=numpy.shape(oriMaskOnes2)[0],
            )

            # save kept slices
            trimMask1 = numpy.zeros(numpy.shape(oriMaskOnes1))
            trimMask2 = numpy.zeros(numpy.shape(oriMaskOnes2))

            # save slices with ori labels
            for slc in range(startSlice1, stopSlice1):
                if numpy.sum(oriMaskOnes1[slc]) != 0:
                    trimMask1[slc] = oriMask1.OriData[slc]
                    # print(slc)
                else:
                    continue

            for slc in range(startSlice2, stopSlice2):
                if numpy.sum(oriMaskOnes2[slc]) != 0:
                    trimMask2[slc] = oriMask2.OriData[slc]
                    # print(slc)
                else:
                    continue

            # save
            if SaveIntermediate:
                # Set file name
                maskTrim1FilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="TrimmedDia",
                    extension=".nii.gz",
                    appendDate=False
                )
                # save
                Save_Load_File.MatNIFTISave(
                    MatData=trimMask1,
                    imgPath=maskTrim1FilePath["CombineName"],
                    imgInfo=oriMask1.OriImag,
                    ConvertDType=True,
                    refDataMat=oriMask1.OriData
                )

                # Set file name
                maskTrim2FilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="TrimmedSys",
                    extension=".nii.gz",
                    appendDate=False
                )
                # save
                Save_Load_File.MatNIFTISave(
                    MatData=trimMask2,
                    imgPath=maskTrim2FilePath["CombineName"],
                    imgInfo=oriMask2.OriImag,
                    ConvertDType=True,
                    refDataMat=oriMask2.OriData
                )

            # get data
            trimMaskOnes1 = oriMaskOnes1[startSlice1:stopSlice1]
            trimMaskOnes2 = oriMaskOnes2[startSlice2:stopSlice2]

            # resample
            factors = tuple(
                numpy.divide(numpy.shape(trimMaskOnes1), numpy.shape(trimMaskOnes2)),
            )
            print('aaaa')
            print(factors)
            print('aaaa')

            resampleMaskOnes2 = scipy.ndimage.zoom(input=trimMaskOnes2,
                                                   zoom=factors,
                                                   order=0  # Nearest neighbour
                                                   )

            # change of spacing
            spacing_z2 = spacing_z2_old / factors[2]  # numpy array has flipped X and Z
            spacing_y2 = spacing_y2_old / factors[1]
            spacing_x2 = spacing_x2_old / factors[0]
            unitArea2 = spacing_z2 * spacing_y2

            # save
            if SaveIntermediate:
                # Set file name
                mask1FilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="TrimmedDiaOnes",
                    extension=".nii.gz",
                    appendDate=False
                )
                # save
                Save_Load_File.MatNIFTISave(
                    MatData=trimMaskOnes1,
                    imgPath=mask1FilePath["CombineName"]
                )

                # Set file name
                mask2FilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="ResamTrimSysOnes",
                    extension=".nii.gz",
                    appendDate=False
                )
                # save
                Save_Load_File.MatNIFTISave(
                    MatData=resampleMaskOnes2,
                    imgPath=mask2FilePath["CombineName"]
                )

            # image match centroid
            resampleMaskCorrect2 = Image_Process_Functions.MatchXSliceCentroid(
                referenceMat=trimMaskOnes1,
                inMat=resampleMaskOnes2
            )

            # save
            if SaveIntermediate:
                # Set file name
                maskCorrect2FilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="CorrCenSysOnes",
                    extension=".nii.gz",
                    appendDate=False
                )
                # save
                Save_Load_File.MatNIFTISave(
                    MatData=resampleMaskCorrect2,
                    imgPath=maskCorrect2FilePath["CombineName"]
                )

            # get each slice information
            listLength = numpy.shape(trimMaskOnes1)[0]
            majorAxisArr1 = numpy.zeros([listLength, 1])
            majorAxisArr2 = numpy.zeros([listLength, 1])
            minorAxisArr1 = numpy.zeros([listLength, 1])
            minorAxisArr2 = numpy.zeros([listLength, 1])
            majorMinorAxisArr1 = numpy.zeros([listLength, 1])
            majorMinorAxisArr2 = numpy.zeros([listLength, 1])  # majorAxisArr1/minorAxisArr1
            alphaArr = numpy.zeros([listLength, 1])  # abs(majorMinorAxisArr2 - majorMinorAxisArr1)
            areaArr1 = numpy.zeros([listLength, 1])
            areaArr2 = numpy.zeros([listLength, 1])
            betaArr = numpy.zeros([listLength, 1])  # areaArr1/areaArr2
            areaDiffArr = numpy.zeros([listLength, 1])  # areaArr1 - areaArr2
            areaSumArr = numpy.zeros([listLength, 1])  # areaArr1 + areaArr2
            gammaArr = numpy.zeros([listLength, 1])  # 2*areaDiffArr/areaSumArr
            misAreaArr = numpy.zeros([listLength, 1])  # areaArr1 not intersect areaArr2
            matchAreaArr = numpy.zeros([listLength, 1])  # areaArr1 intersect areaArr2
            deltaArr = numpy.zeros([listLength, 1])  # misAreaArr/matchAreaArr

            # check spacing and area!!!
            # check same spacing
            unitArea = 1
            if unitArea2 == unitArea1:
                unitArea = unitArea1
            elif unitArea2 / unitArea1 <= 2 or unitArea2 / unitArea1 >= 1 / 2:
                unitArea = (unitArea2 ** 2 + unitArea1 ** 2) ** 0.5
            else:
                print('======Warning!!!======')
                msg = 'Cannot determine the unit area: unitArea2: {} + unitArea1: {}' \
                          .format(unitArea2, unitArea1) + \
                      'Use unit area'
                print(msg)
                print('======Warning!!!======')
            # unit length
            unitLength2 = 1
            if spacing_z2 == spacing_y2:
                unitLength2 = spacing_z2
            elif spacing_z2 / spacing_y2 <= 2 or spacing_z2 / spacing_y2 >= 1 / 2:
                unitLength2 = (spacing_z2 ** 2 + spacing_y2 ** 2) ** 0.5
            else:
                print('======Warning!!!======')
                msg = 'Cannot determine the unit length: spacing_z2: {} + spacing_y2: {}' \
                          .format(spacing_z2, spacing_y2) + \
                      'Use unit length'
                print(msg)
                print('======Warning!!!======')
            # unit length
            unitLength1 = 1
            if spacing_z1 == spacing_y1:
                unitLength1 = spacing_z1
            elif spacing_z1 / spacing_y1 <= 2 or spacing_z1 / spacing_y1 >= 1 / 2:
                unitLength1 = (spacing_z1 ** 2 + spacing_y1 ** 2) ** 0.5
            else:
                print('======Warning!!!======')
                msg = 'Cannot determine the unit length: spacing_z1: {} + spacing_y1: {}' \
                          .format(spacing_z1, spacing_y1) + \
                      'Use unit length'
                print(msg)
                print('======Warning!!!======')

            # get all preliminary values
            for slc in range(listLength):
                # each slice
                maskSlc1 = trimMaskOnes1[slc]
                maskSlc2 = resampleMaskCorrect2[slc]

                # area
                areaArr1[slc] = numpy.sum(maskSlc1) * unitArea
                areaArr2[slc] = numpy.sum(maskSlc2) * unitArea  # second mask is corrected to first mask sapce already
                misAreaArr[slc] = numpy.sum((maskSlc1 - maskSlc2) != 0) * unitArea
                matchAreaArr[slc] = numpy.sum((maskSlc1 + maskSlc2) > 1) * unitArea

                # empty
                if numpy.sum(maskSlc1) != 0:
                    maskSlc1Label, maskSlc1Num = skimage.measure.label(maskSlc1,
                                                                       connectivity=1,
                                                                       return_num=True)
                    maskSlc1Region = skimage.measure.regionprops(maskSlc1Label)

                    # !!! list start from 0 label start from 1!!!
                    maskSlc1Bubble = maskSlc1Region[0]

                    # fill values
                    majorAxisArr1[slc] = maskSlc1Bubble.major_axis_length * unitLength1
                    minorAxisArr1[slc] = maskSlc1Bubble.minor_axis_length * unitLength1

                if numpy.sum(maskSlc2) != 0:
                    maskSlc2Label, maskSlc1Num = skimage.measure.label(maskSlc2,
                                                                       connectivity=1,
                                                                       return_num=True)
                    maskSlc2Region = skimage.measure.regionprops(maskSlc2Label)

                    # !!! list start from 0 label start from 1!!!
                    maskSlc2Bubble = maskSlc2Region[0]

                    # fill values
                    majorAxisArr2[slc] = maskSlc2Bubble.major_axis_length * unitLength2
                    minorAxisArr2[slc] = maskSlc2Bubble.minor_axis_length * unitLength2

            # calculation
            ### always 2 wrt 1!!!
            majorMinorAxisArr1 = numpy.divide(majorAxisArr1, minorAxisArr1)
            majorMinorAxisArr2 = numpy.divide(majorAxisArr2, minorAxisArr2)
            alphaArr = majorMinorAxisArr2 - majorMinorAxisArr1
            betaArr = numpy.divide(areaArr2, areaArr1)
            areaDiffArr = areaArr2 - areaArr1
            areaSumArr = areaArr2 + areaArr1
            gammaArr = 2 * numpy.divide(areaDiffArr, areaSumArr)
            deltaArr = numpy.divide(misAreaArr, matchAreaArr)

            # save raw values
            rawDict = {
                'majorAxisArr1': majorAxisArr1.flatten().tolist(),
                'majorAxisArr2': majorAxisArr2.flatten().tolist(),
                'minorAxisArr1': minorAxisArr1.flatten().tolist(),
                'minorAxisArr2': minorAxisArr2.flatten().tolist(),
                'majorMinorAxisArr1': majorMinorAxisArr1.flatten().tolist(),
                'majorMinorAxisArr2': majorMinorAxisArr2.flatten().tolist(),
                'alphaArr': alphaArr.flatten().tolist(),
                'areaArr1': areaArr1.flatten().tolist(),
                'areaArr2': areaArr2.flatten().tolist(),
                'betaArr': betaArr.flatten().tolist(),
                'areaDiffArr': areaDiffArr.flatten().tolist(),
                'areaSumArr': areaSumArr.flatten().tolist(),
                'gammaArr': gammaArr.flatten().tolist(),
                'misAreaArr': misAreaArr.flatten().tolist(),
                'matchAreaArr': matchAreaArr.flatten().tolist(),
                'deltaArr': deltaArr.flatten().tolist()
            }
            rawDF = pandas.DataFrame(rawDict)

            # save
            if SaveIntermediate:
                # Set file name
                rawInfoFilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="RawInfo",
                    extension=".csv",
                    appendDate=False
                )
                # save
                Pd_Funs.SaveDF(
                    outPath=rawInfoFilePath["CombineName"],
                    pdIn=rawDF,
                    header=True,
                    index=False
                )

            # create dictionary for all stats
            majorAxisDic1 = Matrix_Math.LstArrStats(ArrLst=majorAxisArr1, refStr="MajorAxis1")["statics"]
            majorAxisDic2 = Matrix_Math.LstArrStats(ArrLst=majorAxisArr2, refStr="MajorAxis2")["statics"]
            minorAxisDic1 = Matrix_Math.LstArrStats(ArrLst=minorAxisArr1, refStr="MinorAxis1")["statics"]
            minorAxisDic2 = Matrix_Math.LstArrStats(ArrLst=minorAxisArr2, refStr="MinorAxis2")["statics"]
            majorMinorAxisDic1 = Matrix_Math.LstArrStats(ArrLst=majorMinorAxisArr1, refStr="MajorMinorAxisRatio1")[
                "statics"]
            majorMinorAxisDic2 = Matrix_Math.LstArrStats(ArrLst=majorMinorAxisArr2, refStr="MajorMinorAxisRatio2")[
                "statics"]
            alphaDic = Matrix_Math.LstArrStats(ArrLst=alphaArr, refStr="Alpha")["statics"]
            areaDic1 = Matrix_Math.LstArrStats(ArrLst=areaArr1, refStr="Area1")["statics"]
            areaDic2 = Matrix_Math.LstArrStats(ArrLst=areaArr2, refStr="Area2")["statics"]
            betaDic = Matrix_Math.LstArrStats(ArrLst=betaArr, refStr="Beta")["statics"]
            areaDiffDic = Matrix_Math.LstArrStats(ArrLst=areaDiffArr, refStr="AreaDiff")["statics"]
            areaSumDic = Matrix_Math.LstArrStats(ArrLst=areaSumArr, refStr="AreaSum")["statics"]
            gammaDic = Matrix_Math.LstArrStats(ArrLst=gammaArr, refStr="Gamma")["statics"]
            misAreaDic = Matrix_Math.LstArrStats(ArrLst=misAreaArr, refStr="MismatchArea")["statics"]
            matchAreaDic = Matrix_Math.LstArrStats(ArrLst=matchAreaArr, refStr="MatchArea")["statics"]
            deltaDic = Matrix_Math.LstArrStats(ArrLst=deltaArr, refStr="Delta")["statics"]

            # merge dictionaries
            overallDict = Matrix_Math.MergeDictionaries(DictLst=[
                {"ID": ID},
                majorAxisDic1,
                majorAxisDic2,
                minorAxisDic1,
                minorAxisDic2,
                majorMinorAxisDic1,
                majorMinorAxisDic2,
                alphaDic,
                areaDic1,
                areaDic2,
                betaDic,
                areaDiffDic,
                areaSumDic,
                gammaDic,
                misAreaDic,
                matchAreaDic,
                deltaDic
            ]
            )

            # create DF
            df = pandas.DataFrame(overallDict, index=[index])
            index += 1

            if dfOut is None:
                dfOut = df.copy()
            else:
                dfOut = dfOut.append(df)

        # output shape information
        outputCreate = Save_Load_File.checkCreateDir(os.path.dirname(outTablePath))

        if outputCreate["error"]:
            # file name
            fullParentDir, ParentDir = Save_Load_File.ParentDir(path=tablePath)
            # Set file name
            DfOutFilePath = Save_Load_File.DateFileName(
                Dir=fullParentDir,
                fileName="XSectionMorphology",
                extension=".csv",
                appendDate=True
            )
            outTablePath = DfOutFilePath["CombineName"]

        # save
        Pd_Funs.SaveDF(
            outPath=outTablePath,
            pdIn=dfOut,
            header=True,
            index=False
        )

    # single phase
    else:
        # initiate
        index = 0
        dfOut = None

        for ID, \
                maskPath1, \
                startSlice1, \
                stopSlice1, \
                diagPath \
                in zip(
            batchDataFrame["Patient ID"].tolist(),
            batchDataFrame["Segmentation"].tolist(),
            batchDataFrame["ROI Start Slice"].tolist(),
            batchDataFrame["ROI Stop Slice"].tolist(),
            batchDataFrame["Diagnosis Paths"].tolist()
        ):
            # load masks
            print(maskPath1)
            oriMask1 = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=maskPath1
            )

            # create diagnosis path
            diagCreate = Save_Load_File.checkCreateDir(diagPath)

            if diagCreate["error"]:
                fullParentDir1, ParentDir1 = Save_Load_File.ParentDir(path=maskPath1)
                diagPath = fullParentDir1

            # get actual spcaing and unit area
            spacing1 = oriMask1.OriImag.GetSpacing()
            spacing_z1 = spacing1[0]  # numpy array has flipped X and Z
            spacing_y1 = spacing1[1]
            spacing_x1 = spacing1[2]
            unitArea1 = spacing_z1 * spacing_y1

            # unit length
            unitLength1 = 1
            if spacing_z1 == spacing_y1:
                unitLength1 = spacing_z1
            elif spacing_z1 / spacing_y1 <= 2 or spacing_z1 / spacing_y1 >= 1 / 2:
                unitLength1 = (spacing_z1 ** 2 + spacing_y1 ** 2) ** 0.5
            else:
                print('======Warning!!!======')
                msg = 'Cannot determine the unit length: spacing_z1: {} + spacing_y1: {}' \
                          .format(spacing_z1, spacing_y1) + \
                      'Use unit length'
                print(msg)
                print('======Warning!!!======')

            # binary data
            _, oriMaskOnes1 = Image_Process_Functions.FilterData(rangStarts=labelThresStarts[0],
                                                                 rangStops=labelThresStops[0],
                                                                 dataMat=oriMask1.OriData,
                                                                 funType=ThresTypes[0])

            # trimmed data
            # range correction
            startSlice1, stopSlice1 = Matrix_Math.SliceNumberCorrect(
                sliceStart=int(startSlice1) - 1,  # itk snap correction
                sliceStop=int(stopSlice1) - 1,
                boundaryStart=0,
                boundaryStop=numpy.shape(oriMaskOnes1)[0],
            )

            # save kept slices
            trimMask1 = numpy.zeros(numpy.shape(oriMaskOnes1))

            # save slices with ori labels
            for slc in range(startSlice1, stopSlice1):
                if numpy.sum(oriMaskOnes1[slc]) != 0:
                    trimMask1[slc] = oriMask1.OriData[slc]
                    # print(slc)
                else:
                    continue

            # save
            if SaveIntermediate:
                # Set file name
                maskTrim1FilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="Trimmed",
                    extension=".nii.gz",
                    appendDate=False
                )
                # save
                Save_Load_File.MatNIFTISave(
                    MatData=trimMask1,
                    imgPath=maskTrim1FilePath["CombineName"],
                    imgInfo=oriMask1.OriImag,
                    ConvertDType=True,
                    refDataMat=oriMask1.OriData
                )

            # get data
            trimMaskOnes1 = oriMaskOnes1[startSlice1:stopSlice1]

            # save
            if SaveIntermediate:
                # Set file name
                mask1FilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="KeepTrimmed",
                    extension=".nii.gz",
                    appendDate=False
                )
                # save
                Save_Load_File.MatNIFTISave(
                    MatData=trimMaskOnes1,
                    imgPath=mask1FilePath["CombineName"]
                )

            # get each slice information
            listLength = numpy.shape(trimMaskOnes1)[0]
            majorAxisArr1 = numpy.zeros([listLength, 1])
            minorAxisArr1 = numpy.zeros([listLength, 1])
            majorMinorAxisArr1 = numpy.zeros([listLength, 1])
            areaArr1 = numpy.zeros([listLength, 1])
            area_bboxArr1 = numpy.zeros([listLength, 1])
            area_convexArr1 = numpy.zeros([listLength, 1])
            filled_areaArr1 = numpy.zeros([listLength, 1])
            centroid_rowArr1 = numpy.zeros([listLength, 1])
            centroid_columnArr1 = numpy.zeros([listLength, 1])
            eccentricityArr1 = numpy.zeros([listLength, 1])
            equivalent_diameterArr1 = numpy.zeros([listLength, 1])
            euler_numberArr1 = numpy.zeros([listLength, 1])
            extentArr1 = numpy.zeros([listLength, 1])
            feret_diameter_maxArr1 = numpy.zeros([listLength, 1])
            orientationArr1 = numpy.zeros([listLength, 1])
            perimeterArr1 = numpy.zeros([listLength, 1])
            perimeter_croftonArr1 = numpy.zeros([listLength, 1])
            solidityArr1 = numpy.zeros([listLength, 1])

            # get all preliminary values
            for slc in range(listLength):
                # each slice
                maskSlc1 = trimMaskOnes1[slc]

                # empty
                if numpy.sum(maskSlc1) != 0:
                    maskSlc1Label, maskSlc1Num = skimage.measure.label(maskSlc1,
                                                                       connectivity=1,
                                                                       return_num=True)
                    maskSlc1Region = skimage.measure.regionprops(maskSlc1Label)

                    # !!! list start from 0 label start from 1!!!
                    maskSlc1Bubble = maskSlc1Region[0]

                    # fill values
                    areaArr1[slc] = maskSlc1Bubble.area * unitArea1
                    area_bboxArr1[slc] = maskSlc1Bubble.area_bbox * unitArea1
                    area_convexArr1[slc] = maskSlc1Bubble.convex_area * unitArea1
                    filled_areaArr1[slc] = maskSlc1Bubble.filled_area * unitArea1
                    majorAxisArr1[slc] = maskSlc1Bubble.major_axis_length * unitLength1
                    minorAxisArr1[slc] = maskSlc1Bubble.minor_axis_length * unitLength1
                    centroid_rowArr1[slc] = maskSlc1Bubble.centroid[0] * spacing_y1
                    centroid_columnArr1[slc] = maskSlc1Bubble.centroid[1] * spacing_z1
                    eccentricityArr1[slc] = maskSlc1Bubble.eccentricity
                    equivalent_diameterArr1[slc] = maskSlc1Bubble.equivalent_diameter * unitLength1
                    euler_numberArr1[slc] = maskSlc1Bubble.euler_number
                    extentArr1[slc] = maskSlc1Bubble.extent
                    feret_diameter_maxArr1[slc] = maskSlc1Bubble.feret_diameter_max * unitLength1
                    orientationArr1[slc] = maskSlc1Bubble.orientation
                    perimeterArr1[slc] = maskSlc1Bubble.perimeter * unitLength1
                    perimeter_croftonArr1[slc] = maskSlc1Bubble.perimeter_crofton * unitLength1
                    solidityArr1[slc] = maskSlc1Bubble.solidity

            # calculation
            majorMinorAxisArr1 = numpy.divide(majorAxisArr1, minorAxisArr1)

            # save raw values
            rawDict = {
                'majorAxis': majorAxisArr1.flatten().tolist(),
                'minorAxis': minorAxisArr1.flatten().tolist(),
                'majorMinorAxis': majorMinorAxisArr1.flatten().tolist(),
                'area': areaArr1.flatten().tolist(),
                'area_bbox': area_bboxArr1.flatten().tolist(),
                'area_convex': area_convexArr1.flatten().tolist(),
                'filled_area': filled_areaArr1.flatten().tolist(),
                'centroid_row': centroid_rowArr1.flatten().tolist(),
                'centroid_column': centroid_columnArr1.flatten().tolist(),
                'eccentricity': eccentricityArr1.flatten().tolist(),
                'equivalent_diameter': equivalent_diameterArr1.flatten().tolist(),
                'euler_number': euler_numberArr1.flatten().tolist(),
                'extent': extentArr1.flatten().tolist(),
                'feret_diameter_max': feret_diameter_maxArr1.flatten().tolist(),
                'orientation': orientationArr1.flatten().tolist(),
                'perimeter': perimeterArr1.flatten().tolist(),
                'perimeter_crofton': perimeter_croftonArr1.flatten().tolist(),
                'solidity': solidityArr1.flatten().tolist()
            }
            rawDF = pandas.DataFrame(rawDict)

            # save
            if SaveIntermediate:
                # Set file name
                rawInfoFilePath = Save_Load_File.DateFileName(
                    Dir=diagPath,
                    fileName="RawInfo",
                    extension=".csv",
                    appendDate=False
                )
                # save
                Pd_Funs.SaveDF(
                    outPath=rawInfoFilePath["CombineName"],
                    pdIn=rawDF,
                    header=True,
                    index=False
                )

            # create dictionary for all stats
            majorAxisDic1 = Matrix_Math.LstArrStats(ArrLst=majorAxisArr1, refStr="major_axis")["statics"]
            minorAxisDic1 = Matrix_Math.LstArrStats(ArrLst=minorAxisArr1, refStr="minor_axis")["statics"]
            majorMinorAxisDic1 = Matrix_Math.LstArrStats(ArrLst=majorMinorAxisArr1, refStr="major_minor_axis")[
                "statics"]
            areaDic1 = Matrix_Math.LstArrStats(ArrLst=areaArr1, refStr="area")["statics"]
            area_bboxDic = Matrix_Math.LstArrStats(ArrLst=area_bboxArr1, refStr="area_bbox")["statics"]
            area_convexDic = Matrix_Math.LstArrStats(ArrLst=area_convexArr1, refStr="area_convex")["statics"]
            filled_areaDic = Matrix_Math.LstArrStats(ArrLst=filled_areaArr1, refStr="filled_area")["statics"]
            centroid_rowDic = Matrix_Math.LstArrStats(ArrLst=centroid_rowArr1, refStr="centroid_row")["statics"]
            centroid_columnDic = Matrix_Math.LstArrStats(ArrLst=centroid_columnArr1, refStr="centroid_column")[
                "statics"]
            eccentricityDic = Matrix_Math.LstArrStats(ArrLst=eccentricityArr1, refStr="eccentricity")["statics"]
            equivalent_diameterDic = \
                Matrix_Math.LstArrStats(ArrLst=equivalent_diameterArr1, refStr="equivalent_diameter")["statics"]
            euler_numberDic = Matrix_Math.LstArrStats(ArrLst=euler_numberArr1, refStr="euler_number")["statics"]
            extentDic = Matrix_Math.LstArrStats(ArrLst=extentArr1, refStr="extent")["statics"]
            feret_diameter_maxDic = Matrix_Math.LstArrStats(ArrLst=feret_diameter_maxArr1, refStr="feret_diameter_max")[
                "statics"]
            orientationDic = Matrix_Math.LstArrStats(ArrLst=orientationArr1, refStr="orientation")["statics"]
            perimeterDic = Matrix_Math.LstArrStats(ArrLst=perimeterArr1, refStr="perimeter")["statics"]
            perimeter_croftonDic = Matrix_Math.LstArrStats(ArrLst=perimeter_croftonArr1, refStr="perimeter_crofton")[
                "statics"]
            solidityDic = Matrix_Math.LstArrStats(ArrLst=solidityArr1, refStr="solidity")["statics"]

            # merge dictionaries
            overallDict = Matrix_Math.MergeDictionaries(DictLst=[
                {"ID": ID},
                majorAxisDic1,
                minorAxisDic1,
                majorMinorAxisDic1,
                areaDic1, area_bboxDic,
                area_convexDic,
                filled_areaDic,
                centroid_rowDic,
                centroid_columnDic,
                eccentricityDic,
                equivalent_diameterDic,
                euler_numberDic,
                extentDic,
                feret_diameter_maxDic,
                orientationDic,
                perimeterDic,
                perimeter_croftonDic,
                solidityDic
            ]
            )

            # create DF
            df = pandas.DataFrame(overallDict, index=[index])
            index += 1

            if dfOut is None:
                dfOut = df.copy()
            else:
                dfOut = dfOut.append(df)

        # output shape information
        outputCreate = Save_Load_File.checkCreateDir(os.path.dirname(outTablePath))

        if outputCreate["error"]:
            # file name
            fullParentDir, ParentDir = Save_Load_File.ParentDir(path=tablePath)
            # Set file name
            DfOutFilePath = Save_Load_File.DateFileName(
                Dir=fullParentDir,
                fileName="XSectionMorphology",
                extension=".csv",
                appendDate=True
            )
            outTablePath = DfOutFilePath["CombineName"]

        # save
        Pd_Funs.SaveDF(
            outPath=outTablePath,
            pdIn=dfOut,
            header=True,
            index=False
        )


"""
##############################################################################
# Func: Centerline related single-/two-phase morphology
##############################################################################
"""
# import standard lib
import numpy
import scipy.ndimage
import skimage.morphology
import skimage.measure
import pandas
import matplotlib.pyplot as plt
import scipy.interpolate


def CenterLineInfo(
        tablePath,
        twoPhase=True,
        labelThresStarts=[[0], [0]],
        labelThresStops=[[0], [0]],
        ThresTypes=["single value greater", "single value greater"],
        SaveIntermediate=True,
        outTablePath=""
):
    # load table
    batchDataFrame = Pd_Funs.OpenDF(tablePath, header=0)

    # initiate
    index = 0
    dfOut = None
    errMsg = "Error ID: \n"

    # two pahse
    if twoPhase:
        print(batchDataFrame.columns)
        for ID, \
                maskPath1, \
                maskPath2, \
                resample, \
                diagPath \
                in zip(
            batchDataFrame["Patient ID"].tolist(),
            batchDataFrame["Diastole Phase Segmentation"].tolist(),
            batchDataFrame["Systole Phase Segmentation"].tolist(),
            batchDataFrame["Resample Point Number"].tolist(),
            batchDataFrame["Diagnosis Paths"].tolist()
        ):
            # need to remove some extreme cases
            try:
                # create diagnosis path
                diagCreate = Save_Load_File.checkCreateDir(diagPath)

                if diagCreate["error"]:
                    fullParentDir, _ = Save_Load_File.ParentDir(path=maskPath1)
                    diagPath = fullParentDir

                # resample line
                centerCoors1 = Image_Process_Functions.CenterlineGeneration(
                    inPath=maskPath1,
                    resampleNo=int(resample),
                    labelThresStarts=labelThresStarts[0],
                    labelThresStops=labelThresStops[0],
                    ThresTypes=ThresTypes[0],
                    SaveIntermediate=True,
                    diagPath=diagPath,
                    fileSuff="_Dia",
                    pltVis=False
                )

                print(maskPath2)
                centerCoors2 = Image_Process_Functions.CenterlineGeneration(
                    inPath=maskPath2,
                    resampleNo=int(resample),
                    labelThresStarts=labelThresStarts[1],
                    labelThresStops=labelThresStops[1],
                    ThresTypes=ThresTypes[1],
                    SaveIntermediate=True,
                    diagPath=diagPath,
                    fileSuff="_Sys",
                    pltVis=False
                )

                # distance
                ### always 2 wrt 1!!!
                # get difference
                centerDisp = numpy.subtract(centerCoors2, centerCoors1)

                # correction for starting point
                centerDispCorrect = numpy.subtract(centerDisp, centerDisp[0])

                # get distance
                centerDistCorrect = numpy.linalg.norm(centerDispCorrect, axis=1)
                # print(centerDistCorrect)

                # curvature & arclength
                curve1 = Matrix_Math.CurvatureRelated3D(coordinates=centerCoors1)
                curve2 = Matrix_Math.CurvatureRelated3D(coordinates=centerCoors2)

                # arc length diff
                segmentLengthDiff = curve2["arcLength"] - curve1["arcLength"]
                segmentLengthRel = numpy.divide(curve2["arcLength"], curve1["arcLength"])

                # arc tangent change diff
                segmentTangentChangeDiff = curve2["arcTangentChange"] - curve1["arcTangentChange"]
                segmentTangentChangeRel = numpy.divide(curve2["arcTangentChange"], curve1["arcTangentChange"])

                # total length difference
                segmentLengthTotalDiff = curve2["arcLengthTotal"] - curve1["arcLengthTotal"]
                segmentLengthTotalRel = numpy.divide(curve2["arcLengthTotal"], curve1["arcLengthTotal"])

                # speed diff
                speedDiff = curve2["speed"] - curve1["speed"]
                speedRel = numpy.divide(curve2["speed"], curve1["speed"])

                # curvature difference
                curvatureDiff = curve2["curvature"] - curve1["curvature"]
                curvatureRel = numpy.divide(curve2["curvature"], curve1["curvature"])

                # save raw values
                rawDict = {
                    'centerDistCorrect': centerDistCorrect.flatten().tolist(),
                    'arcLength1': curve1["arcLength"].flatten().tolist(),
                    'arcLength2': curve2["arcLength"].flatten().tolist(),
                    'segmentLengthDiff': segmentLengthDiff.flatten().tolist(),
                    'segmentLengthRel': segmentLengthRel.flatten().tolist(),
                    'arcTangentChange1': curve1["arcTangentChange"].flatten().tolist(),
                    'arcTangentChange2': curve2["arcTangentChange"].flatten().tolist(),
                    'segmentTangentChangeDiff': segmentTangentChangeDiff.flatten().tolist(),
                    'segmentTangentChangeRel': segmentTangentChangeRel.flatten().tolist(),
                    'speed1': curve1["speed"].flatten().tolist(),
                    'speed2': curve2["speed"].flatten().tolist(),
                    'speedDiff': speedDiff.flatten().tolist(),
                    'speedRel': speedRel.flatten().tolist(),
                    'curve1': curve1["curvature"].flatten().tolist(),
                    'curve2': curve2["curvature"].flatten().tolist(),
                    'curvatureDiff': curvatureDiff.flatten().tolist(),
                    'curvatureRel': curvatureRel.flatten().tolist()
                }
                rawDF = pandas.DataFrame(rawDict)

                # save
                if SaveIntermediate:
                    # Set file name
                    rawInfoFilePath = Save_Load_File.DateFileName(
                        Dir=diagPath,
                        fileName="CurvatureRawInfo",
                        extension=".csv",
                        appendDate=False
                    )
                    # save
                    Pd_Funs.SaveDF(
                        outPath=rawInfoFilePath["CombineName"],
                        pdIn=rawDF,
                        header=True,
                        index=False
                    )

                # statics
                # create dictionary for all stats
                distanceCorrectDict = Matrix_Math.LstArrStats(ArrLst=centerDistCorrect, refStr="DistanceCorrect")[
                    "statics"]
                arcLengthDict1 = Matrix_Math.LstArrStats(ArrLst=curve1["arcLength"], refStr="ArcLength1")["statics"]
                arcLengthDict2 = Matrix_Math.LstArrStats(ArrLst=curve2["arcLength"], refStr="ArcLength2")["statics"]
                arcLengthDiffDict = Matrix_Math.LstArrStats(ArrLst=segmentLengthDiff, refStr="ArcLengthDiff")["statics"]
                arcLengthRelDict = Matrix_Math.LstArrStats(ArrLst=segmentLengthRel, refStr="ArcLengthRel")["statics"]
                speedDict1 = Matrix_Math.LstArrStats(ArrLst=curve1["speed"], refStr="Speed1")["statics"]
                speedDict2 = Matrix_Math.LstArrStats(ArrLst=curve2["speed"], refStr="Speed2")["statics"]
                speedDiffDict = Matrix_Math.LstArrStats(ArrLst=speedDiff, refStr="SpeedDiff")["statics"]
                speedRelDict = Matrix_Math.LstArrStats(ArrLst=speedRel, refStr="SpeedRel")["statics"]
                curvatureDict1 = Matrix_Math.LstArrStats(ArrLst=curve1["curvature"], refStr="Curvature1")["statics"]
                curvatureDict2 = Matrix_Math.LstArrStats(ArrLst=curve2["curvature"], refStr="Curvature2")["statics"]
                curvatureDiffDict = Matrix_Math.LstArrStats(ArrLst=curvatureDiff, refStr="CurvatureDiff")["statics"]
                curvatureRelDict = Matrix_Math.LstArrStats(ArrLst=curvatureRel, refStr="CurvatureRel")["statics"]
                arcTangentChangeDict1 = \
                    Matrix_Math.LstArrStats(ArrLst=curve1["arcTangentChange"], refStr="TangentChange1")[
                        "statics"]
                arcTangentChangeDict2 = \
                    Matrix_Math.LstArrStats(ArrLst=curve2["arcTangentChange"], refStr="TangentChange2")[
                        "statics"]
                arcTangentChangeDiffDict = \
                    Matrix_Math.LstArrStats(ArrLst=segmentTangentChangeDiff, refStr="TangentChangeDiff")[
                        "statics"]
                arcTangentChangeRelDict = \
                    Matrix_Math.LstArrStats(ArrLst=segmentTangentChangeRel, refStr="TangentChangeRel")[
                        "statics"]

                # merge dictionaries
                overallDict = Matrix_Math.MergeDictionaries(DictLst=[
                    {"ID": ID},
                    distanceCorrectDict,
                    arcLengthDict1,
                    arcLengthDict2,
                    arcLengthDiffDict,
                    arcLengthRelDict,
                    {"ArcLengthTotal1": curve1["arcLengthTotal"]},
                    {"ArcLengthTotal2": curve2["arcLengthTotal"]},
                    {"ArcLengthTotalDiff": segmentLengthTotalDiff},
                    {"ArcLengthTotalRel": segmentLengthTotalRel},
                    speedDict1,
                    speedDict2,
                    speedDiffDict,
                    speedRelDict,
                    curvatureDict1,
                    curvatureDict2,
                    curvatureDiffDict,
                    curvatureRelDict,
                    arcTangentChangeDict1,
                    arcTangentChangeDict2,
                    arcTangentChangeDiffDict,
                    arcTangentChangeRelDict,
                ]
                )

                # create DF
                df = pandas.DataFrame(overallDict, index=[index])
                index += 1

                if dfOut is None:
                    dfOut = df.copy()
                else:
                    dfOut = dfOut.append(df)

            except:
                print("////WARNING/////")
                print("Cannot proceed: " + str(ID))
                print("/////////")

                errMsg += "{} \n".format(ID)

        # output shape information
        if dfOut is not None:
            # save
            Pd_Funs.SaveDF(
                outPath=outTablePath,
                pdIn=dfOut,
                header=True,
                index=False
            )

        # save error
        # file name
        fullParentDir, ParentDir = Save_Load_File.ParentDir(path=outTablePath)
        errFilePath = Save_Load_File.DateFileName(
            Dir=fullParentDir,
            fileName="ErrorID",
            extension=".txt",
            appendDate=True
        )
        Save_Load_File.WriteTXT(path=errFilePath["CombineName"], txt=errMsg, mode="append")

    # single phase
    else:
        for ID, \
                maskPath1, \
                resample, \
                diagPath \
                in zip(
            batchDataFrame["Patient ID"].tolist(),
            batchDataFrame["Segmentation"].tolist(),
            batchDataFrame["Resample Point Number"].tolist(),
            batchDataFrame["Diagnosis Paths"].tolist()
        ):
            # need to remove some extreme cases
            try:
                # create diagnosis path
                diagCreate = Save_Load_File.checkCreateDir(diagPath)

                if diagCreate["error"]:
                    fullParentDir, _ = Save_Load_File.ParentDir(path=maskPath1)
                    diagPath = fullParentDir

                # resample line
                centerCoors1 = Image_Process_Functions.CenterlineGeneration(
                    inPath=maskPath1,
                    resampleNo=int(resample),
                    labelThresStarts=labelThresStarts[0],
                    labelThresStops=labelThresStops[0],
                    ThresTypes=ThresTypes[0],
                    SaveIntermediate=True,
                    diagPath=diagPath,
                    fileSuff="_Dia",
                    pltVis=False
                )

                # distance
                ### always 2 wrt 1!!!
                # curvature & arclength
                curve1 = Matrix_Math.CurvatureRelated3D(coordinates=centerCoors1)

                # save raw values
                rawDict = {
                    'arcLength': curve1["arcLength"].flatten().tolist(),
                    'arcTangentChange': curve1["arcTangentChange"].flatten().tolist(),
                    'speed': curve1["speed"].flatten().tolist(),
                    'curve': curve1["curvature"].flatten().tolist(),
                }
                rawDF = pandas.DataFrame(rawDict)

                # save
                if SaveIntermediate:
                    # Set file name
                    rawInfoFilePath = Save_Load_File.DateFileName(
                        Dir=diagPath,
                        fileName="CurvatureRawInfo",
                        extension=".csv",
                        appendDate=False
                    )
                    # save
                    Pd_Funs.SaveDF(
                        outPath=rawInfoFilePath["CombineName"],
                        pdIn=rawDF,
                        header=True,
                        index=False
                    )

                # statics
                # create dictionary for all stats
                arcLengthDict1 = Matrix_Math.LstArrStats(ArrLst=curve1["arcLength"], refStr="ArcLength1")["statics"]
                speedDict1 = Matrix_Math.LstArrStats(ArrLst=curve1["speed"], refStr="Speed1")["statics"]
                curvatureDict1 = Matrix_Math.LstArrStats(ArrLst=curve1["curvature"], refStr="Curvature1")["statics"]
                arcTangentChangeDict1 = \
                    Matrix_Math.LstArrStats(ArrLst=curve1["arcTangentChange"], refStr="TangentChange1")[
                        "statics"]

                # merge dictionaries
                overallDict = Matrix_Math.MergeDictionaries(DictLst=[
                    {"ID": ID},
                    arcLengthDict1,
                    {"ArcLengthTotal1": curve1["arcLengthTotal"]},
                    speedDict1,
                    curvatureDict1,
                    arcTangentChangeDict1
                ]
                )

                # create DF
                df = pandas.DataFrame(overallDict, index=[index])
                index += 1

                if dfOut is None:
                    dfOut = df.copy()
                else:
                    dfOut = dfOut.append(df)

            except:
                print("////WARNING/////")
                print("Cannot proceed: " + str(ID))
                print("/////////")

                errMsg += "{} \n".format(ID)

        # output shape information
        if dfOut is not None:
            # save
            Pd_Funs.SaveDF(
                outPath=outTablePath,
                pdIn=dfOut,
                header=True,
                index=False
            )

        # save error
        # file name
        fullParentDir, ParentDir = Save_Load_File.ParentDir(path=outTablePath)
        errFilePath = Save_Load_File.DateFileName(
            Dir=fullParentDir,
            fileName="ErrorID",
            extension=".txt",
            appendDate=True
        )
        Save_Load_File.WriteTXT(path=errFilePath["CombineName"], txt=errMsg, mode="append")


"""
##############################################################################
# Func: output 2D slices
##############################################################################
"""
# import standard lib
import numpy
import scipy.ndimage
import skimage.morphology
import skimage.measure
import pandas
import matplotlib.pyplot as plt
import scipy.interpolate


def Extract2DSlicesRef(
        inFile,
        refFile,
        filterMethod,
        thresStart,
        thresStop
):
    # with reference
    if refFile is not None:
        # load in files
        refData = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=refFile
        )

        print(filterMethod)
        print(numpy.sum(refData.OriData))
        # filter ref Data
        _, maskOnes = Image_Process_Functions.FilterData(
            rangStarts=[thresStart],
            rangStops=[thresStop],
            dataMat=refData.OriData,
            funType=filterMethod,
            ConvertVTKType=False,
            InDataType=numpy.float64
        )

        print(numpy.shape(maskOnes))
        # non-empty slices
        slices = Image_Process_Functions.NoneEmptySlices(
            inMat=maskOnes,
            sliceSum=0
        )

        # save slices
        Save2DSlices(
            inFile=inFile,
            slices=slices
        )


"""
##############################################################################
# Func: save 2D slices with ranges
##############################################################################
"""


def Save2DSlices(
        inFile,
        slices,
        out2D=True
):
    # load data
    imgData = Save_Load_File.OpenLoadNIFTI(
        GUI=False,
        filePath=inFile
    )

    # create folder
    fileName = Save_Load_File.FilenameFromPath(inFile)
    fullParentDir, _ = Save_Load_File.ParentDir(path=inFile)
    overallDir = fullParentDir + "//" + fileName + "_2D"
    Save_Load_File.checkCreateDir(
        path=overallDir
    )

    # save
    for slice in slices:
        # Set file name
        outFilePath = Save_Load_File.DateFileName(
            Dir=overallDir,
            fileName=fileName + "_" + str(slice + 1),
            extension=".nii.gz",
            appendDate=False
        )

        if out2D:
            # save
            Save_Load_File.MatNIFTISave(
                MatData=imgData.OriData[slice],
                imgPath=outFilePath["CombineName"],
                imgInfo=imgData.OriImag,
                ConvertDType=True,
                refDataMat=imgData.OriData,
                out2D=True
            )
        else:
            # output
            outMat = numpy.zeros(numpy.shape(imgData.OriData))
            outMat[slice] = imgData.OriData[slice]

            # save
            Save_Load_File.MatNIFTISave(
                MatData=outMat,
                imgPath=outFilePath["CombineName"],
                imgInfo=imgData.OriImag,
                ConvertDType=True,
                refDataMat=imgData.OriData,
                out2D=False
            )


"""
##############################################################################
# Func: get HU range in the image
##############################################################################
"""
import skimage.morphology


def GetHURange(imgPath,
               mskPath,
               range):
    # read image and mask
    imgData = Save_Load_File.OpenLoadNIFTI(GUI=False, filePath=imgPath)
    mskData = Save_Load_File.OpenLoadNIFTI(GUI=False, filePath=mskPath).OriData

    # mask skeletonise
    mskSkeleton = skimage.morphology.skeletonize_3d(mskData)

    # dilate with 2 disk
    [DimErr, DimMsg], mskUse = Image_Process_Functions.DiskDilate(dataMat=mskSkeleton,
                                                                  Thres=0,
                                                                  dilateIncre=1,
                                                                  binaryMsk=True,
                                                                  axisChoice='X',
                                                                  iterateDilate=False)

    # # save
    # Save_Load_File.MatNIFTISave(
    #     MatData=mskUse,
    #     imgPath=r'F:\SCOTHEART\LI\pRCAStns\110002\Preproc\Xsection\dilate.nii.gz',
    #     imgInfo=imgData.OriImag,
    #     ConvertDType=True,
    #     refDataMat=imgData.OriData,
    #     out2D=False
    # )

    # get mask region data list
    HUFullRange = imgData.OriData[mskUse != 0]

    # keep range
    if range > 0 and range < 100:
        rangeDelta = (100 - range) / 2
        rangeUp = 100 - rangeDelta
        rangeLow = rangeDelta
    else:
        rangeUp = 100
        rangeLow = 0

    HURange = numpy.nanpercentile(HUFullRange, [rangeLow, rangeUp])

    print(HURange)

    return HURange


"""
##############################################################################
# Func: get HU range in the image
##############################################################################
"""


def AreaCaculation(imgPath,
                   mskPath,
                   filterMethods,
                   thresStarts,
                   thresStops,
                   columnRefs,
                   outputFolder,
                   outputRef):
    # load image & mask
    imgData = Save_Load_File.OpenLoadNIFTI(GUI=False, filePath=imgPath).OriData
    mskData = Save_Load_File.OpenLoadNIFTI(GUI=False, filePath=mskPath).OriData

    # 3D Threshold
    _, mskOne = Image_Process_Functions.FilterData(
        rangStarts=[0],
        rangStops=[0],
        dataMat=mskData,
        funType="single value greater"
    )

    # output data
    outDict = {'Slice': [i + 1 for i in range(numpy.shape(mskOne)[0])]} # fill slice with "+1"

    # each case
    for filterMethod, thresStart, thresStop, columnRef in zip(filterMethods,
                                                                thresStarts,
                                                                thresStops,
                                                                columnRefs):

        # 3D image analysis
        imgFiltered, _ = Image_Process_Functions.FilterData(
            rangStarts=[thresStart],
            rangStops=[thresStop],
            dataMat=imgData,
            funType=filterMethod
        )

        maskImg = numpy.multiply(mskOne, imgFiltered)

        # dictionary add term
        outDict[columnRef] = []

        # area each slice
        shape = numpy.shape(maskImg)
        for slice in range(shape[0]):
            # image
            img = maskImg[slice]

            # calclate
            outDict[columnRef].append(numpy.sum(1 * (img != 0)))

    # output result
    Save_Load_File.checkCreateDir(path=outputFolder)
    outPath = outputFolder + "//" + outputRef + "_AC.csv"
    Pd_Funs.SaveDF(
        outPath=outPath,
        pdIn=pandas.DataFrame(outDict),
        header=True,
        index=False
    )

    return outDict
