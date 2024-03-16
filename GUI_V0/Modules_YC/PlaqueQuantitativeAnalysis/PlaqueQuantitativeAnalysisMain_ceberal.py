# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：PlaqueQuantitativeAnalysis.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/8/15 14:13 
'''
########################################################################################################################
import sys
import os
# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../../Functions_YC')
sys.path.insert(0, '../../Functions_JZ')
# Import functions
import Save_Load_File
import Image_Process_Functions
import Post_Image_Process_Functions
import Preprocess_Mask
import Use_Plt
import VTK_Functions
import VTK_Numpy
import QT_GUI
from FileDisposing import *
########################################################################################################################
# Standard library
import cv2
import copy
import json
import time

import numpy
#numpy.set_printoptions(threshold=numpy.inf)
import numpy as np
from scipy import spatial
import scipy.stats
from scipy.spatial import KDTree
import scipy.ndimage
import  SimpleITK

import skimage.measure
import skimage.segmentation
import skimage.morphology
from skimage.draw import line
from skimage import measure, color
from skimage.filters import sobel
from skimage.filters import gaussian
from skimage.morphology import (erosion, dilation, opening, closing,  # noqa
                                white_tophat)
from skimage.segmentation import (morphological_chan_vese,
                                  morphological_geodesic_active_contour,
                                  inverse_gaussian_gradient,
                                  checkerboard_level_set)
import skimage.segmentation
import skimage.feature

from multiprocessing import Pool
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
########################################################################################################################
# Standard libs
import numpy
from scipy.interpolate import splprep, splev

import numpy as np
import math
import matplotlib.pyplot as plt
########################################################################################################################
def fillhole(Mask):
    Mask_fillhole = []
    for slicenum in range(0, len(Mask)):
        MskSliceArryfillhole = skimage.morphology.closing(Mask[slicenum],
                                                  selem=None)  # dilation  and  erosion
        Mask_fillhole.append(MskSliceArryfillhole)
    return Mask_fillhole

########################################################################################################################
def Linedefine(point, angle):
     '''
     point - Tuple (x, y)
     angle - Angle you want your end point at in degrees.
     return
     point , slope ,intercept
     '''
     # unpack the first point
     x, y = point
     slope_k = math.tan(math.radians(angle))
     if angle not in [90,270]:
         intercept_b = y - slope_k*x
     else:
         slope_k = float("inf")
         intercept_b = float("inf")
         print("the intercept_b is infinite")
     return slope_k, intercept_b
########################################################################################################################
def ComponentContourExtraction(MskSliceArry , ObjectRegionLabel,Connectivity):
    '''
         Arguements:
         MskSliceArry - origin image
         ObjectLabel - a list contain labels of the object region
         Closed_contour - specify whether shape is a closed contour (if passed True), or just a curve

         return:
         countour point , area , countour width
         '''
    # ********************************************binary image***************************************************
    LabellList = [0,1,2,3,4,5,6,7,8,9]
    ObjectRegionLabel.sort()
    contoursInfo = {}
    MaskOnes = numpy.zeros_like(MskSliceArry)
    LumenMaskOnes = numpy.zeros_like(MskSliceArry)
    LumenMaskOnes[MskSliceArry == 1] = 1
    try:
        if 0 in ObjectRegionLabel:
            TmpMaskOnes = numpy.zeros_like(MskSliceArry)
            TmpMaskOnes[MskSliceArry > 0] = 1
            # ************************************fill the incorrect hole ***********************************
            TmpMaskOnes_closing = skimage.morphology.closing(TmpMaskOnes,
                                                             selem=None)  # dilation  and  erosion
            # **********************************fill the hole*********************************
            TmpMaskFilledOnes = scipy.ndimage.morphology.binary_fill_holes(
                TmpMaskOnes_closing,
                structure=None,
                output=None,
                origin=0
            )
            MaskOnes = TmpMaskFilledOnes - TmpMaskOnes
        else:
            for labelcont in range(len(ObjectRegionLabel)):
                if ObjectRegionLabel[labelcont] not in LabellList:
                    MaskOnes[MskSliceArry == ObjectRegionLabel[labelcont]] = 0
                else:
                    MaskOnes[MskSliceArry == ObjectRegionLabel[labelcont]] = 1
    except:
        print("Component Contour Extraction Error,Please make sure the integrity of the component")

    # ****************************************** contours finding *****************************************************
    MaskOnes_binary_image = MaskOnes.astype(numpy.uint8)

    MaskOnes_contours, _ = cv2.findContours(MaskOnes_binary_image,
                                                      cv2.RETR_TREE,
                                                      cv2.CHAIN_APPROX_SIMPLE)

    # ****************************************** contours Property*****************************************************
    contourInfo = {}
    contourInfo['label'] = []
    contourInfo['area'] = []
    contourInfo['centroid'] = []
    contourInfo['height'] = []
    contourInfo['width'] = []
    contourInfo['coordinates'] = []
    contourarea =0

    # ****************************************** filter the smaller  area *****************************************************
    try:
        if Connectivity == 1:
            orderlist = []
            for Mccont in range(len(MaskOnes_contours)):
                contourarea = cv2.contourArea(MaskOnes_contours[Mccont])
                orderlist.append(contourarea)
            max_index = orderlist.index(max(orderlist))

            rect = cv2.minAreaRect(MaskOnes_contours[max_index])
            rect_label = 1
            rect_centroid = rect[0]
            rect_width = rect[1][0]
            rect_height = rect[1][1]
            rect_area = cv2.contourArea(MaskOnes_contours[max_index])

            contourInfo['label'].append(rect_label)
            contourInfo['area'].append(rect_area)
            contourInfo['label'] = []
            contourInfo['centroid'].append(rect_centroid)
            contourInfo['height'].append(rect_height)
            contourInfo['width'].append(rect_width)
            contourInfo['coordinates'].append(MaskOnes_contours[max_index])
        else:
            for cont in range(len(MaskOnes_contours)):
                rect = cv2.minAreaRect(MaskOnes_contours[cont])
                rect_label = cont
                rect_centroid = rect[0]
                rect_width = rect[1][0]
                rect_height = rect[1][1]
                rect_area = cv2.contourArea(MaskOnes_contours[cont])

                contourInfo['label'].append(rect_label)
                contourInfo['area'].append(rect_area)
                contourInfo['centroid'].append(rect_centroid)
                contourInfo['height'].append(rect_height)
                contourInfo['width'].append(rect_width)
                contourInfo['coordinates'].append(MaskOnes_contours[cont])
    except:
        print("layer is blank")
    # for cont in range(len(MaskOnes_contours)):
    #     rect = cv2.minAreaRect(MaskOnes_contours[cont])
    #     rect_label = cont
    #     rect_centroid = rect[0]
    #     rect_width = rect[1][0]
    #     rect_height = rect[1][1]
    #     rect_area = cv2.contourArea(MaskOnes_contours[cont])
    #
    #     contourInfo['label'].append(rect_label)
    #     contourInfo['area'].append(rect_area)
    #     contourInfo['centroid'].append(rect_centroid)
    #     contourInfo['height'].append(rect_height)
    #     contourInfo['width'].append(rect_width)
    #     contourInfo['coordinates'].append(MaskOnes_contours[cont])

    return MaskOnes, contourInfo
########################################################################################################################
def splinefitting(contour):
    smoothened = []
    #print("###################contour.T", type(contour), contour.T)
    x, y = contour.T
    #Convert from numpy arrays to normal arrays
    # x = x.tolist()[0]
    # y = y.tolist()[0]

    tck, u = splprep([x, y], u=None, s=2, per=True)
    #
    u_new = numpy.linspace(u.min(), u.max(), num=50)
    #
    x_new, y_new = splev(u_new, tck, der=0)
    # Convert it back to numpy format for opencv to be able to display it
    res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
    smoothened.append(numpy.asarray(res_array, dtype=numpy.int32))

    return smoothened
    ########################################################################################################################
def IntersectionLineContour(contour,centroid,anglesize):
    #print("############################## start ######################################")
    IntersectionPoints = []
    # ****************the boundingRect  of the contour*********************************
    x, y, w, h = cv2.boundingRect(contour)  #################choose the contour
    #print("boundingrectinfo",x,y,w,h)
    # ****************the intersect points  of line and boundingRect********************
    for angle in range(0, 360, anglesize):
        infinite_angle = [90,270]
        #print("math.isinf(abs(slope_k + intercept_b))",math.isinf(abs(slope_k + intercept_b)))
        if angle not in infinite_angle:
            slope_k, intercept_b = Linedefine(centroid, angle)
            pa, pb = (x, int(slope_k * x + intercept_b)), \
                     ((x + w), int(slope_k * (x + w) + intercept_b))
        else:
            pa, pb = (int(centroid[0]), y), (int(centroid[0]), y + h)
        # cv2.circle(current_subbranch, pa, 2, (0, 255, 255), 2)
        # cv2.circle(current_subbranch, pb, 2, (0, 255, 255), 2)
        # cv2.putText(current_subbranch, 'A', (pa[0] - 10, pa[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        # cv2.putText(current_subbranch, 'B', (pb[0] + 10, pb[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        # cv2.line(current_subbranch, pa, pb, (255, 255, 0), 1)
        #print("############################################\npa, pb =",pa, pb, angle)
        oneAngelIntersectionPoints = []
        tmponeAngelIntersectionPoints = []
        onepixeldist =1
        for pt in zip(*line(*pa, *pb)):
            dist = cv2.pointPolygonTest(contour, (int(pt[0]), int(pt[1])), True)
            if cv2.pointPolygonTest(contour, (int(pt[0]), int(pt[1])), False) == 0:  # 若点在轮廓上
                # cv2.circle(contour, pt, 2, (0, 0, 255), 2)
                #print("pt on the edge", pt)
                tmponeAngelIntersectionPoints.append(pt)
            elif cv2.pointPolygonTest(contour, (int(pt[0]), int(pt[1])), False) > 0:
                if dist <= 1:
                    #print("pt near the edge", pt)
                    tmponeAngelIntersectionPoints.append(pt)
        try:
            oneAngelIntersectionPoints.append(tmponeAngelIntersectionPoints[0])
            oneAngelIntersectionPoints.append(tmponeAngelIntersectionPoints[-1])
            #print("oneAngelIntersectionPoints",oneAngelIntersectionPoints)
            IntersectionPoints.append(oneAngelIntersectionPoints)
        except:
            print("############################### Functiong :Intersection Points ####################"
                  "\nlist index out of range, this layer may have more than one contours of the same component ")


            # try:
            #     dist = cv2.pointPolygonTest(contour, pt, True)
            #     if cv2.pointPolygonTest(contour, pt, False) == 0:  # 若点在轮廓上
            #         # cv2.circle(contour, pt, 2, (0, 0, 255), 2)
            #         print("##############pt on the edge",pt)
            #         tmponeAngelIntersectionPoints.append(pt)
            #     elif cv2.pointPolygonTest(contour, pt, False) > 0:
            #         if dist <= onepixeldist:
            #             tmponeAngelIntersectionPoints.append(pt)
            # except:
            #     print("pt is not on edge",pt)

        # **************** intersect points  sorting********************
        # if tmponeAngelIntersectionPoints[0][0]<tmponeAngelIntersectionPoints[1][0]:
        #     oneAngelIntersectionPoints[0] = tmponeAngelIntersectionPoints[1]
        #     oneAngelIntersectionPoints[1] = tmponeAngelIntersectionPoints[0]
        # else:
        #     oneAngelIntersectionPoints = tmponeAngelIntersectionPoints

    #print("############################## end ######################################")
    return IntersectionPoints
########################################################################################################################
def KNNMatching(InitMat, ObjctMat, IniStartColumnNum, IniEndColumnNum, ObjStartColumnNum, ObjEndColumnNum,IniReturnColumnNum):
    ############################################find the nearest node###################################################
    # ********************************* the nearst node index  ********************************************************#
    MatchedRows_num = []
    # **************************** ***** the nearst distance  **********************************************************#
    min_distance = []
    # ********************************* the  Matched Rows datas in ObjctMat ******************************************#
    MatchedRows = []
    # ********************************* one culumn of  Matched Rows datas in ObjctMat  *******************************#
    MatchedRows_1stColumn = []
    # ******************* the initial datas including all information like pressure coordinates elementid  ************#
    tree = KDTree(InitMat[:,IniStartColumnNum : IniEndColumnNum+1])  #ObjctMat[:,0]is the NodeID of wall elements
    #print(ObjctMat)
    for i in range(len(ObjctMat)):
        dist, InitMatRowsQueryed = tree.query(ObjctMat[i,ObjStartColumnNum : ObjEndColumnNum+1], k=1)
        MatchedRows_num.append(InitMatRowsQueryed)
        MatchedRows.append(InitMat[InitMatRowsQueryed,:])
        MatchedRows_1stColumn.append(InitMat[InitMatRowsQueryed, IniReturnColumnNum]) #return nodeid
        min_distance.append(dist)
    # np.savetxt('min_num.txt', min_num, delimiter=',')
    # np.savetxt('min_dist.txt', min_dist, delimiter=',')
    # np.savetxt('ObjctMat.txt', ObjctMat, delimiter=',')
    # print('min_num',min_num)
    # print('min_dist', min_dist)
    return MatchedRows_num, min_distance, MatchedRows, MatchedRows_1stColumn
########################################################################################################################
app = QApplication([])
MainWindow = QMainWindow()
FileDialog = QFileDialog(MainWindow)
class PlaqueQuantitativAnalysis:
    """
    Description:

    Quantitative analysis of plaque.

    Parameters
    ----------
    libname : str
        Name of the library, which can have 'lib' as a prefix,
        but without an extension.
    loader_path : str
        Where the library can be found.

    Returns
    -------
    ctypes.cdll[libpath] : library object
       A ctypes library object

    Raises
    ------
    OSError
        If there is no library with the expected extension, or the
        library is defective and cannot be loaded.
    """
    def __init__(self,InputFilePath,OutputFilePath, init_SliceNum, end_SliceNum):
        #analysis region init_SliceNum, end_SliceNum
        self.init_SliceNum = init_SliceNum -1
        self.end_SliceNum = end_SliceNum -1
        #workpath
        self.InputFilePath =InputFilePath #r'E:\Carotid\nii\P78RLabelcopy.nii.gz'
        #self.InputFilePath =r'E:\Carotid\nii\P78RLabelcopy.nii.gz'
        self.OutputFilePath = OutputFilePath
        #self.OutputFilePath = r'E:\tst.json'
        self.IntDataType = None
        self.FloatDataType = None
        # initial definition
        self.spacing_x = None
        self.spacing_y = None
        self.spacing_z = None
        self.outputData = None
        self.outputDatafillhole = None
        self.outputDataOnes = None
        self.CTA = None
        self.inMsk = None
        self.BranchNumsList = None
        self.BranchSliceGroup_ResetLabelDict = None
        self.slicesNum = None
        self.BranchGroupMask = None
        self.LumenGroup = None
        self.BranchGroup = None
        self.Lumen_contours = None
        self.subLumen_contours = None
        self.contourspline = None
        self.sliceCCentroid = None
        self.sliceIntersectPointsInfo = None
        #wall property
        self.wallthicknessInfo = None
        self.AverWallThickness =None
        self.WallThicknessRange =None
        self.singleAnglewallthickness = None
        self.stenosisInfo = None
        self.WallEqDiameterInfo = None
        self.LumenEqDiameterInfo = None

        #component volumn and area
        self.TotalCalcificationArea = None
        self.TotalCalcificationVolumn = None

        self.TotalLipidArea = None
        self.TotalLipidVolumn = None

        self.TotalPlaqueArea = None
        self.TotalPlaqueVolumn = None

        self.TotalHemorrhageArea = None
        self.TotalHemorrhageVolumn = None

        self.TotalLumenArea = None
        self.AverLumenArea = None
        self.LumenAreaRange = None
        self.WallAreaInfo = None
        #component height
        self.PlaqueHeight = None

        self.BranchGroupFibrousIntegrity = None

        self.BranchGroupSliceLumenMaskAreadict = None
        self.BranchGroupSlicePlaqueMaskAreadict = None
        self.BranchGroupslicePlaqueAreaBooldict = None
        self.stenosisWidthInfo = None
        self.stenosisPositionInfo = None
        self.BranchGroupreferenceWallEquivalentDiameterIndex = None
        self.BranchGroupreferenceWallEquivalentDiameter = None
        self.BranchGroupStenosisDegree = None
        self.StenosisDegreeList = []
        self.stenosisdegree = None
        self.ReconstructionIndex =None
        self.walleccentricity = None

        self.BranchGroupReconstructionIndex = None

        self.PlaqueAnalysisInfo = {}
        #self.PlaqueAnalysisInfo["PlaqueBurden"] = PlaqueBurden


        print("#################################################################\n"
              "########### the default label of each component #################\n"
              "1 - Lumen\n"
              "2 - Healthy Wall + other/wall\n"
              "3 - Calcification\n"
              "4 - Lipid\n"
              "5 - Loose matrix(fibrous tisue)\n"
              "6 - Hemorrhage - Fresh\n"
              "7 - Hemorrhage - Recent\n"
              "8 - non-evaluated (NE)\n"
              "#################################################################\n")

    def LoadData(self):
        # load two data
        # CTAPath = Opening_File(FileDialog, "NIFTI/NRRD files(*.nii.gz *.nrrd)")
        # self.CTA = Save_Load_File.OpenLoadNIFTI(
        #     GUI = False,
        #     filePath = CTAPath
        # )
        # mskPath = Opening_File(FileDialog, "NIFTI/NRRD files(*.nii.gz *.nrrd)")
        self.inMsk = Save_Load_File.OpenLoadNIFTI(
            GUI = False,
            #filePath = mskPath
            filePath = self.InputFilePath
        )
        # update display data
        self.outputData = copy.deepcopy(self.inMsk.OriData)
        self.IntDataType = self.inMsk.OriData.dtype
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
        itkImag = SimpleITK.ReadImage(self.InputFilePath)
        # get voxel spacing (for 3-D image)
        spacing = itkImag.GetSpacing()
        self.spacing_x = spacing[0]
        self.spacing_y = spacing[1]
        self.spacing_z = spacing[2]
        #print("spacing",self.spacing_x, self.spacing_y, self.spacing_z)


    def FillIncorrectHole(self):
        self.outputDatafillhole = []
        self.outputDatafillhole = fillhole(self.outputData)

    #dataMatMsks = dataMatTFMsks.astype(DataType)


    """
    ############################################################################
    # Visualisation
    ############################################################################
    """
    def PlotOVerlap(self):
        # get inputs
        #slicDir = self.ui.plotAixsLineTxt_LC.text()
        slicDir = 'X'
        #title = Preprocess_Mask.StrToLst(strIn=self.ui.plotTitleTxt_LC.toPlainText())["listOut"]
        titleStr = 'CTA, Lumen_mask, Mask_overlap'
        title = Preprocess_Mask.StrToLst(strIn=titleStr)["listOut"]
        #plotRange = Preprocess_Mask.StrToLst(strIn=self.ui.plotThresTxt_LC.toPlainText())["booleanOut"]
        plotRangeStr = 'True, False, True'
        plotRange = Preprocess_Mask.StrToLst(strIn=plotRangeStr)["booleanOut"]
        #minLst = Preprocess_Mask.StrToLst(strIn=self.ui.plotMinTxt_LC.toPlainText())["floatOut"]
        minLstStr = '0, 0, 0'
        minLst = Preprocess_Mask.StrToLst(strIn=minLstStr)["floatOut"]
        #maxLst = Preprocess_Mask.StrToLst(strIn=self.ui.plotMaxTxt_LC.toPlainText())["floatOut"]
        maxLstStr = '800, 5, 800'
        maxLst = Preprocess_Mask.StrToLst(strIn=maxLstStr)["floatOut"]
        #cursorChoice = self.ui.cursorChoiceBtnGrp_LC.checkedButton().text() == 'Yes'
        cursorChoice = 'No'

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
        maskChoice = "Original Mask"
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

        # layout frame
        # add dock
        # dock = QT_GUI.CreateDockWidget(
        #     parent=MainWindow,
        #     name="Lum3D_" + str(self.i),
        #     position='Right'
        # )
        # frame = dock.GetFrame()
        # layout = dock.GetLayout()
        # self.i += 1

        # visualisation
        VTK_Functions.DisplayOverlayNifti(
            ActFile_Data=[oriMask, currentMask],
            ThresUp=[1000, 1000],
            ThresBot=[1, 1],
            opacityChoice=[0.5, 0.5],
            colorChoice=['Green', 'Red'],
            ThresDType=numpy.float64,
            CaseRef=["Original mask is GREEN, current mask in RED"],
            qt=False
            # qtFrame=frame,
            # qtLayout=layout
        )

    def BranchSplited(self):

        self.BranchNumsList = []
        self.BranchSliceGroup_ResetLabelDict = {}
        BranchGroupMask = {}
        self.LumenGroup = []
        self.BranchGroup = {}
        if self.init_SliceNum :
            self.init_SliceNum = 0
        if self.end_SliceNum :
            self.end_SliceNum = len(self.outputDataOnes)
        for slicenum in range(self.init_SliceNum ,self.end_SliceNum):
            # print("#########################################################")
            # numpy.all(self.outputDatafillhole[slicenum] == 0)
            # ********************fill the incorrect hole **********************
            MskSliceArry = self.outputDatafillhole[slicenum]
            self.IntDataType = numpy.uint8
            self.FloatDataType = numpy.float64
            #print("MskSliceArry", MskSliceArry.dtype)
            Lumen_binary_image, LumenContourInfo = \
                ComponentContourExtraction(MskSliceArry,
                                           [2],######add by yang
                                           0)
            #print("Lumen_binary_image", Lumen_binary_image.dtype)
            self.LumenGroup.append(Lumen_binary_image)
            SliceBranchNums = len(LumenContourInfo['area'])
            self.BranchNumsList.append(SliceBranchNums)
        ####return self.BranchNumsList
        #print("self.BranchNumsList", self.BranchNumsList)
        BranchNums = sum(list(set(self.BranchNumsList)))

        for BNcont in range(BranchNums):
            BranchGroupMask['branch' + str(BNcont + 1)] = []
            self.BranchGroup['branch' + str(BNcont + 1)] = []

        for slicenum in range(self.init_SliceNum ,self.end_SliceNum):
            BranchSliceGroup_ResetLabel = []
            MskSliceArry = self.outputDatafillhole[slicenum]

            MaskSliceOnes, MaskSliceContourInfo = \
                ComponentContourExtraction(MskSliceArry,
                                           [1, 2, 3, 4, 5, 6, 7, 8], 1)

            #print("MaskSliceOnes", MaskSliceOnes.dtype)
            # plt.figure()
            # plt.imshow(self.outputData[slicenum])

            #********************************************** reset label to 1 or 2**************************************************area_splited BranchNumsSum
            if self.BranchNumsList[slicenum] == 0:
                self.StenosisDegreeList.append(1)
                print('Vascular occlusion')

            elif self.BranchNumsList[slicenum] == 1:
                area_splited_ResetLabel = copy.deepcopy(MskSliceArry)
                #print("area_splited_ResetLabel", area_splited_ResetLabel.dtype)
                area_splited_ResetLabel[area_splited_ResetLabel != 0] = 1
                BranchSliceGroup_ResetLabel.append(area_splited_ResetLabel)

                self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] = \
                    area_splited_ResetLabel

            elif self.BranchNumsList[slicenum] > 1:
                #print("current slicenum",slicenum ,self.BranchNumsList[slicenum])
                # ***************************************area pre-cutting *************************************************
                tmpsliceWaterShade = \
                    Image_Process_Functions.WaterShadeMsk(MaskSliceOnes,
                                                          Threshold=0)  # image process function row 1054   return slice including numbers of labels
                sliceWaterShade = tmpsliceWaterShade.astype(self.IntDataType)
                #print("sliceWaterShade", sliceWaterShade.dtype)
                # plt.figure()
                # plt.imshow(sliceWaterShade)

                sliceWaterShade_props = measure.regionprops(sliceWaterShade) # all label's property   sliceWaterShade_props
                area_splited = copy.deepcopy(sliceWaterShade)
                #print("area_splited", area_splited)
                # ****************************************** area cutting **************************************************
                labelNewSaving = []  #saving the labels corresponding to the two largest areas
                BrachInfoList = []   # saving brach information including label, area, centroid
                labellist =[]
                centroidlist = []
                # ********************************************** KNN *******************************************************
                inimat = numpy.zeros((self.BranchNumsList[slicenum], 3))  ###(label, centroid_x, centroid_y)
                #print("inimat", inimat.dtype)
                objmat = numpy.zeros((len(sliceWaterShade_props) - self.BranchNumsList[slicenum], 3))
                label_registration = numpy.zeros((len(sliceWaterShade_props) - self.BranchNumsList[slicenum], 2))  # saving the old labels and correspondent new ones
                area_splited_retainTwolabels = copy.deepcopy(sliceWaterShade)
                # tmparea_splited_retainTwolabels = numpy.zeros_like(MskSliceArry)
                # print("tmparea_splited_retainTwolabels", tmparea_splited_retainTwolabels.dtype)
                # area_splited_retainTwolabels = tmparea_splited_retainTwolabels.astype(self.IntDataType)
                # print("area_splited_retainTwolabels", area_splited_retainTwolabels.dtype)
                #area_splited_retainTwolabels = numpy.zeros_like(sliceWaterShade)
                if len(sliceWaterShade_props) > self.BranchNumsList[slicenum]:  # multiple label_nums in one slice exp: label num =8  self.BranchNumsList[slicenum] =2
                    for Prop in sliceWaterShade_props:
                        tmpcoordinate = []
                        branchDict = {}
                        branchDict['label'] = Prop['label']
                        labellist.append(Prop['label'])

                        branchDict['area'] = Prop['area']

                        branchDict['centroid'] = Prop['centroid']
                        tmpcoordinate.append(Prop['centroid'][0])
                        tmpcoordinate.append(Prop['centroid'][1])
                        centroidlist.append(tmpcoordinate)
                        #print("centroidlist", centroidlist)
                        BrachInfoList.append(branchDict)
                    #print("centroidlist", centroidlist)
                    # test points
                    pts = numpy.asarray(centroidlist)

                    # two points which are fruthest apart will occur as vertices of the convex hull
                    candidates = pts[spatial.ConvexHull(pts).vertices]

                    # get distances between each pair of candidate points
                    dist_mat = spatial.distance_matrix(candidates, candidates)

                    # get indices of candidates that are furthest apart
                    i, j = np.unravel_index(dist_mat.argmax(), dist_mat.shape)

                    #print("candidates[i], candidates[j]", candidates[i], candidates[j])

                    tmpBrachInfoList_sorted = sorted(BrachInfoList, key=lambda p: ((p['centroid'][0] - candidates[i][0]) ** 2 + (p['centroid'][1] - candidates[i][1]) ** 2),
                                                  reverse=True)  # Preserve the labels corresponding to the two largest areas

                    tmpBrachInfoList_sorted[1], tmpBrachInfoList_sorted[-1] = tmpBrachInfoList_sorted[-1], tmpBrachInfoList_sorted[1]
                    BrachInfoList_sorted = tmpBrachInfoList_sorted
                    #print('BrachInfoList_sorted', BrachInfoList_sorted, '\nlablenum', len(sliceWaterShade_props))

                    for cont in range(self.BranchNumsList[slicenum]):  # inimat: saving the selected two label info
                        inimat[cont, 0] = BrachInfoList_sorted[cont]['label']
                        labelNewSaving.append(inimat[cont, 0])
                        inimat[cont, 1] = BrachInfoList_sorted[cont]['centroid'][0]
                        inimat[cont, 2] = BrachInfoList_sorted[cont]['centroid'][1]

                    for cont in range(self.BranchNumsList[slicenum], len(BrachInfoList_sorted)):  # objmat: saving the remaining label info
                        objmat[cont - self.BranchNumsList[slicenum], 0] = BrachInfoList_sorted[cont]['label']
                        objmat[cont - self.BranchNumsList[slicenum], 1] = BrachInfoList_sorted[cont]['centroid'][0]
                        objmat[cont - self.BranchNumsList[slicenum], 2] = BrachInfoList_sorted[cont]['centroid'][1]
                    #print('inimat', inimat, '\nobjmat', objmat)
                    MatchedinimatRows_num, inimatmin_distance, MatchedinimatRows, MatchedinimatNodesID = KNNMatching(
                        inimat,
                        objmat,
                        1, 2,
                        1, 2,
                        0)
                    #print('MatchedinimatRows_num', MatchedinimatRows_num, '\ninimatmin_distance', inimatmin_distance,
                           #'\nMatchedinimatRows', MatchedinimatRows, '\nMatchedinimatNodesID', MatchedinimatNodesID)

                    # *************************************** save old label and new label *****************************
                    if MatchedinimatRows_num:
                        for cont in range(len(MatchedinimatRows_num)):  # label_registration: (new label , old label)
                            label_registration[cont][0] = inimat[MatchedinimatRows_num[cont], 0]  # label new
                            label_registration[cont][1] = objmat[cont][0]  # label old
                            area_splited_retainTwolabels[area_splited == int(objmat[cont][0])] = int(inimat[
                                MatchedinimatRows_num[cont], 0]) # area_splited :WallWaterShaded original date
                            #print("inimat[MatchedinimatRows_num[cont], 0]", inimat[
                                #MatchedinimatRows_num[cont], 0])
                            #print("objmat[cont][0]",objmat[cont][0])
                        #print("area_splited_retainTwolabels", area_splited_retainTwolabels)
                        #print('label_registration', label_registration)

                    labelNewSaving.sort()  # rising
                    # print("############label" + str(slicenum), labelNewSaving)


                    area_splited_ResetLabel = numpy.zeros_like(area_splited_retainTwolabels)
                    for cont in range(0, self.BranchNumsList[slicenum]):
                        # ***********************************reset area_splited's label*********************************
                        tmps = copy.deepcopy(area_splited_retainTwolabels)  # tmps: reatain one labels of two
                        tmps[tmps != labelNewSaving[cont]] = 0
                        tmps[tmps == labelNewSaving[cont]] = cont + 1
                        area_splited_ResetLabel += tmps
                    BranchSliceGroup_ResetLabel.append(area_splited_ResetLabel)
                    self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] = area_splited_ResetLabel
                    # # **********************************assign single  branch to different matrix*********************
                    # names['Branch' + str(cont)] = copy.deepcopy(area_splited)
                    # names['Branch' + str(cont)][names['Branch' + str(cont)] != labelNewSaving[cont]] = 0
                    # names['Branch' + str(cont)][names['Branch' + str(cont)] != 0] = 1
                    # oriSlicecutting = numpy.multiply(names['Branch' + str(cont)], MskSliceArry)
                    # BranchSliceGroup.append(oriSlicecutting)
                else:
                    area_splited_retainTwolabels = sliceWaterShade
                    self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] = area_splited_retainTwolabels
            #     plt.figure()
            #     plt.imshow(BranchSliceGroup_ResetLabel)
            # plt.show()


                #*******************************************************************************************************


        # ******************************************branch grouping*****************************************************
        for slicenum in range(self.init_SliceNum ,self.end_SliceNum):
            if self.BranchNumsList[slicenum] == 1:
                BranchGroupMask['branch' + str(self.BranchNumsList[slicenum])].append(
                    self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)])
                self.BranchGroup['branch' + str(self.BranchNumsList[slicenum])].append(self.outputDatafillhole[slicenum])
            elif self.BranchNumsList[slicenum] == 2:
                if slicenum < len(self.BranchNumsList) - 1:
                    twolayer_label1area_Subtract = self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)][
                                                       self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] == 1] \
                                                   - self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum + 1)][
                                                       self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] == 1]
                    if numpy.sum(numpy.abs(twolayer_label1area_Subtract)) \
                            == numpy.sum(self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)][
                                             self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] == 1]):
                        # Exchange the label of the next layer
                        subtmp = tmps1 = tmps2 = numpy.zeros_like(self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum + 1)])
                        tmps1[self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum + 1)] == 2] = 1
                        tmps2[self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum + 1)] == 1] = 2
                        subtmp = tmps1 + tmps2
                        self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum + 1)] = subtmp
                # repair unclosing area self.LumenGroup
                tmps1_r = numpy.zeros_like(self.outputDataOnes[slicenum])
                tmps2_r = numpy.zeros_like(self.outputDataOnes[slicenum])
                tmps1_r[self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] == 1] = 1
                tmps2_r[self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] == 2] = 2

                footprint = skimage.morphology.disk(1)#################????????????????????????????????????????????????????????????? Lumen ==0
                footprint1 = skimage.morphology.square(3)#################????????????????????????????????????????????????????????????? Lumen == 0
                tmps1_rdilation = skimage.morphology.dilation(self.LumenGroup[slicenum], footprint)
                tmps1_rerosion = tmps1_r + tmps1_rdilation - self.LumenGroup[slicenum]
                tmps1_rerosion[tmps1_rerosion>0] = 1
                tmps1_rerosion = skimage.morphology.opening(tmps1_rerosion,
                                           footprint1)  # dilation  and  erosion


                #tmps1_rerosion = tmps1_r - self.LumenGroup[slicenum]
                tmps2_rdilation = skimage.morphology.dilation(self.LumenGroup[slicenum] * 2,footprint)
                tmps2_rerosion = tmps2_r + tmps2_rdilation - self.LumenGroup[slicenum] *2
                tmps2_rerosion[tmps2_rerosion > 0] = 2
                tmps2_rerosion = skimage.morphology.opening(tmps2_rerosion,
                                           footprint1)

                self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)] = tmps1_rerosion + tmps2_rerosion

                # save the current layer to  BranchGroupMask
                BranchGroupMask['branch' + str(self.BranchNumsList[slicenum])].append(tmps1_rerosion)  # BranchGroupMask is a logical matrix here
                BranchGroupMask['branch' + str(self.BranchNumsList[slicenum] + 1)].append(tmps2_rerosion)
                # self.BranchGroup['branch' + str(self.BranchNumsList[slicenum])].append(
                #     numpy.multiply(self.outputDatafillhole[slicenum],
                #                    tmps1_rerosion )
                #                                                                         )
                # self.BranchGroup['branch' + str(self.BranchNumsList[slicenum] + 1)].append(
                #     numpy.multiply(self.outputDatafillhole[slicenum],
                #                    tmps2_rerosion*0.5 )

                self.BranchGroup['branch' + str(self.BranchNumsList[slicenum])].append(
                    numpy.multiply(self.outputDatafillhole[slicenum],
                                   tmps1_rerosion)
                )
                self.BranchGroup['branch' + str(self.BranchNumsList[slicenum] + 1)].append(
                    numpy.multiply(self.outputDatafillhole[slicenum],
                                   tmps2_rerosion * 0.5)
                                                                                         )
    def IntersectPoints(self):
        self.contourspline = []
        self.sliceCCentroid = {}
        self.sliceCCentroid['branch1'] = []
        self.sliceCCentroid['branch2'] = []
        self.sliceCCentroid['branch3'] = []
        self.sliceIntersectPointsInfo = {}
        self.stenosisInfo ={}
        sliceStenosislist = []
        self.WallEqDiameterInfo = {}
        self.LumenEqDiameterInfo = {}
        self.WallAreaInfo = {}


        for BGcont in range(len(self.BranchGroup)):
            slicewallArealist = []
            sliceWallEqDiameterlist = []
            sliceLumenEqDiameterlist = []
            for slicenum in range(len(self.BranchGroup['branch' + str(BGcont + 1)])):
                tmpbranch = fillhole(self.BranchGroup['branch' + str(BGcont + 1)])
                #tmpbranch = (self.BranchGroup['branch' + str(BGcont + 1)])
                current_subbranch = tmpbranch[slicenum]
                # ************************** contour of wall inner and outer contour **********************************************
                WallMaskOnes, WallcontourInfo = ComponentContourExtraction(current_subbranch, [1,2,3,4,5,6,7,8],1)########?????????
                Lumen_binary_image, LumenContourInfo = ComponentContourExtraction(current_subbranch, [2],1)
                # print("#LumenContourInfo",len(LumenContourInfo['centroid']))
                slicewallArea = WallcontourInfo['area'][0]
                sliceWallEqDiameter = numpy.sqrt(4 * slicewallArea/ numpy.pi)
                slicewallArealist.append(slicewallArea)
                sliceWallEqDiameterlist.append(sliceWallEqDiameter)

                slicelumenArea = LumenContourInfo['area'][0]
                sliceLumenEqDiameter = numpy.sqrt(4 * slicelumenArea / numpy.pi)
                sliceLumenEqDiameterlist.append(sliceLumenEqDiameter)

                sliceStenosis = (slicewallArea - slicelumenArea)/slicewallArea
                sliceStenosislist.append(sliceStenosis)

                #print("#LumenContourInfo",len(LumenContourInfo['centroid']))
                # ************************** the center of lumen inner  centroid ****************************************
                Ccentroid_x = LumenContourInfo['centroid'][0][0]
                Ccentroid_y = LumenContourInfo['centroid'][0][1]
                Ccentroid = (Ccentroid_x, Ccentroid_y)
                self.sliceCCentroid['branch' + str(BGcont + 1)].append(Ccentroid)

                # ***************************************intersect points*********************************
                tmpIntersectionPoints = []
                walltmpContour = WallcontourInfo['coordinates'][0]
                wallIntersectionPoints = IntersectionLineContour(walltmpContour, Ccentroid, 30)
                tmpIntersectionPoints.append(wallIntersectionPoints)
                lumentmpContour = LumenContourInfo['coordinates'][0]
                lumenIntersectionPoints = IntersectionLineContour(lumentmpContour, Ccentroid, 30)
                tmpIntersectionPoints.append(lumenIntersectionPoints)
                # ***************************************spline*********************************
                # for WCcont in range(len(WallcontourInfo['coordinates'])):
                #     tmpContour = WallcontourInfo['coordinates'][WCcont]
                #     currentContour = numpy.reshape(tmpContour,(-1, 2))
                #     splinecoor = splinefitting(currentContour)
                #     self.contourspline.append(splinecoor)
                #     tmpsplinecoor = numpy.reshape(splinecoor, (-1, 1, 2))#convert array dimension from 2 to 3
                #     #cv2.drawContours(current_subbranch, splinecoor[WCcont], -1, (255, 255, 255), 1)
                #     print("##########################" + ' branch ' + str(BGcont + 1) + " slice "+str(slicenum) +" Ccentroid " +str(Ccentroid)+ "##########################" )
                #
                #     IntersectionPoints = IntersectionLineContour(tmpContour,Ccentroid,120)
                #     print("IntersectionPoints",
                #           IntersectionPoints
                #           )
                #     tmpIntersectionPoints.append(IntersectionPoints)
                # ***************************************spline*********************************
                self.sliceIntersectPointsInfo['branch_' + str(BGcont + 1) + "/layer_" + str(slicenum) ] = tmpIntersectionPoints
            # ***************************************stenosisInfo*********************************
            self.stenosisInfo['branch' + str(BGcont + 1)] = sliceStenosislist
            # ***************************************wall area*********************************
            self.WallAreaInfo['branch' + str(BGcont + 1)] = slicewallArealist
            # ***************************************equivalent diameter*********************************
            self.WallEqDiameterInfo['branch' + str(BGcont + 1)] = sliceWallEqDiameterlist
            self.LumenEqDiameterInfo['branch' + str(BGcont + 1)] = sliceLumenEqDiameterlist


        print("stenosisInfo", self.stenosisInfo)
        print("WallAreaInfo", self.WallAreaInfo)
        print("WallEqDiameterInfo", self.WallEqDiameterInfo)
        print("LumenEqDiameterInfo", self.LumenEqDiameterInfo)
        # ***************************************PlaqueBurden*********************************
        sliceStenosislist.sort()
        PlaqueBurden = sliceStenosislist[-1]
        print("PlaqueBurden",PlaqueBurden)
        self.PlaqueAnalysisInfo["PlaqueBurden"]= PlaqueBurden

        #plt.show()

    def CarotidParameters(self):
        self.TotalPlaqueMaskArea = 0
        self.TotalCalcificationMaskArea = 0
        self.TotalLipidMaskArea = 0
        self.TotalHemorrhageMaskArea = 0
        self.TotalLumenMaskArea = 0
        self.PlaqueHeight = 0
        self.slicesNum = sum(self.BranchNumsList)
        self.BranchGroupSliceLumenMaskAreadict ={}
        self.BranchGroupSlicePlaqueMaskAreadict ={}
        self.BranchGroupslicePlaqueAreaBooldict = {}
        self.LumenAreaRange = []
        PlaqueMaskHeight =0
        for slicenum in range(self.init_SliceNum ,self.end_SliceNum):
      # ************************************plaque height ***********************************
            MskSliceArry = self.outputDatafillhole[slicenum]
            PlaqueOnematrix, sonePlaquecontourInfo = ComponentContourExtraction(MskSliceArry, [ 3, 4, 6, 7, 8], 0)##add by yang
            PlaqueOnematrixsum = numpy.sum(PlaqueOnematrix)
            if PlaqueOnematrixsum:
                PlaqueMaskHeight+=1
        self.PlaqueHeight = PlaqueMaskHeight * self.spacing_z
        print("PlaqueHeight", self.PlaqueHeight)
        self.PlaqueAnalysisInfo["PlaqueHeight"] = self.PlaqueHeight

        self.BranchGroupFibrousIntegrity = {}

        for BGcont in range(len(self.BranchGroup)):
            sliceLumenMaskArealist = []
            slicePlaqueMaskArealist = []
            slicePlaqueAreaBoollist = []
            # tmpSliceWallArealist = self.WallAreaInfo['branch' + str(BGcont + 1)]
            # tmpSliceWallArealistSorted = tmpSliceWallArealist.sort()
            # tmpSliceWallArealargest = tmpSliceWallArealistSorted[-1]

            for slicenum in range(len(self.BranchGroup['branch' + str(BGcont + 1)])):
                currentslice = self.BranchGroup['branch' + str(BGcont + 1)][slicenum]

                sliceLumenOnes, sliceLumencontourInfo = ComponentContourExtraction(currentslice, [2], 0)
                sliceLumenArea = sum(sliceLumencontourInfo['area'])
                sliceLumenMaskArealist.append(sliceLumenArea)
                self.TotalLumenMaskArea += sliceLumenArea

                sliceWallOnes, sliceWallcontourInfo = ComponentContourExtraction(currentslice, [1,3,4,5,6,7,8],0)
                sliceWallArea = sum(sliceWallcontourInfo['area'])

                slicePlaqueOnes, slicePlaquecontourInfo= ComponentContourExtraction(currentslice, [3,4,6,7,8],0)
                slicePlaqueArea = sum(slicePlaquecontourInfo['area'])

                # ************************************where has the plaque ***********************************
                if slicePlaqueArea >0:
                    slicePlaqueAreaBool = 1
                else:
                    slicePlaqueAreaBool = 0
                slicePlaqueAreaBoollist.append(slicePlaqueAreaBool)
                slicePlaqueMaskArealist.append(sliceLumenArea)
                self.TotalPlaqueMaskArea += slicePlaqueArea

                sliceCalcificationOnes, sliceCalcificationcontourInfo = ComponentContourExtraction(currentslice, [3],0)
                sliceCalcificationArea = sum(sliceCalcificationcontourInfo['area'])
                self.TotalCalcificationMaskArea += sliceCalcificationArea

                sliceLipidOnes, sliceLipidcontourInfo = ComponentContourExtraction(currentslice, [4],0)
                sliceLipidArea = sum(sliceLipidcontourInfo['area'])

                sliceHemorrhageOnes, sliceHemorrhagecontourInfo = ComponentContourExtraction(currentslice, [6,7],0)
                sliceHemorrhageArea = sum(sliceHemorrhagecontourInfo['area'])
                self.TotalHemorrhageMaskArea += sliceHemorrhageArea

                sliceFibrousArea, sliceFibrouscontourInfo = ComponentContourExtraction(currentslice, [5],0)

                sliceFibrousArea = sum(sliceFibrouscontourInfo['area'])
                if len(sliceFibrouscontourInfo['area']) ==0 :
                    tmpFibrousIntegrity = "None"
                elif len(sliceFibrouscontourInfo['area']) >1:
                    tmpFibrousIntegrity = "true"
                else:
                    tmpFibrousIntegrity = "false"
                self.BranchGroupFibrousIntegrity['branch' + str(BGcont + 1) + ' layer' + str(slicenum)] = tmpFibrousIntegrity
                #print("FibrousIntegrity",tmpFibrousIntegrity)
                print("len(sliceFibrouscontourInfo['area']",len(sliceFibrouscontourInfo['area']))

            self.BranchGroupSliceLumenMaskAreadict['branch' + str(BGcont + 1)] = sliceLumenMaskArealist
            self.BranchGroupSlicePlaqueMaskAreadict['branch' + str(BGcont + 1)] = slicePlaqueMaskArealist
            self.BranchGroupslicePlaqueAreaBooldict['branch' + str(BGcont + 1)] = slicePlaqueAreaBoollist
        self.PlaqueAnalysisInfo["FibrousIntegrity"] = self.BranchGroupFibrousIntegrity
        print("BranchGroupFibrousIntegrity", self.BranchGroupFibrousIntegrity)


        self.TotalCalcificationArea = self.TotalCalcificationMaskArea * self.spacing_x * self.spacing_y
        self.TotalCalcificationVolumn = self.TotalCalcificationMaskArea * self.spacing_x * self.spacing_y * self.spacing_z
        self.PlaqueAnalysisInfo["CalcificationVolumn"] = self.TotalCalcificationVolumn
        print("CalcificationVolumn",self.TotalCalcificationVolumn)

        self.TotalLipidArea = self.TotalLipidMaskArea * self.spacing_x * self.spacing_y
        self.TotalLipidVolumn = self.TotalLipidMaskArea * self.spacing_x * self.spacing_y * self.spacing_z
        print("LipidVolumn", self.TotalLipidVolumn)
        self.PlaqueAnalysisInfo["LipidVolumn"] = self.TotalLipidVolumn

        self.TotalHemorrhageArea = self.TotalHemorrhageMaskArea * self.spacing_x * self.spacing_y
        self.TotalHemorrhageVolumn = self.TotalHemorrhageMaskArea  * self.spacing_x * self.spacing_y * self.spacing_z
        print("HemorrhageVolumn", self.TotalHemorrhageVolumn)
        self.PlaqueAnalysisInfo["HemorrhageVolumn"] = self.TotalHemorrhageVolumn

        self.TotalPlaqueArea = self.TotalPlaqueMaskArea * self.spacing_x * self.spacing_y
        self.TotalPlaqueVolumn = self.TotalPlaqueMaskArea * self.spacing_x * self.spacing_y * self.spacing_z
        print("PlaqueVolumn", self.TotalPlaqueVolumn)
        self.PlaqueAnalysisInfo["PlaqueVolumn"] = self.TotalPlaqueVolumn

        self.TotalLumenArea = self.TotalLumenMaskArea * self.spacing_x * self.spacing_y
        self.AverLumenArea = self.TotalLumenArea / self.slicesNum
        print("AverLumenArea", self.AverLumenArea)
        self.PlaqueAnalysisInfo["AverLumenArea"] = self.AverLumenArea

        AlllumenMaskArealist =[]
        for BGcont in range(len(self.BranchGroup)):
            AlllumenMaskArealist += self.BranchGroupSliceLumenMaskAreadict['branch' + str(BGcont + 1)]
        AlllumenMaskArealist.sort(reverse=False)#asceding order
        self.LumenAreaRange.append(AlllumenMaskArealist[0] * self.spacing_x * self.spacing_y)
        self.LumenAreaRange.append(AlllumenMaskArealist[-1] * self.spacing_x * self.spacing_y)
        print("LumenAreaRange",self.LumenAreaRange)
        self.PlaqueAnalysisInfo["LumenAreaRange"] = self.LumenAreaRange


        print("BranchGroupslicePlaqueAreaBooldict", self.BranchGroupslicePlaqueAreaBooldict)

        # ******************************************the degree of stenosis****************************************** maximal stenosis degree
        tmpsliceLumenEqDiameterlist = []
        tmpslicePlaqueBoollist = []
        self.stenosisWidthInfo = {}
        self.stenosisPositionInfo = {}
        self.BranchGroupreferenceWallEquivalentDiameterIndex = {}
        self.BranchGroupreferenceWallEquivalentDiameter = {}
        self.BranchGroupReconstructionIndex = {}
        self.BranchGroupStenosisDegree = {}

        ReconstructionIndexlist = []
        tmpSliceWallArealistSorted =[]
        for BGcont in range(len(self.BranchGroup)):
            # ********************************* minimum lumen equivalent diameter***********************************
            tmpsliceLumenEqDiameterlist = self.LumenEqDiameterInfo['branch' + str(BGcont + 1)]
            tmpsliceWallEqDiameterlist = self.WallEqDiameterInfo['branch' + str(BGcont + 1)]
            tmpslicePlaqueBoollist = self.BranchGroupslicePlaqueAreaBooldict['branch' + str(BGcont + 1)]

            tmpSliceWallArealist = self.WallAreaInfo['branch' + str(BGcont + 1)]
            tmpSliceWallArea_atPlaque = numpy.multiply(tmpSliceWallArealist, tmpslicePlaqueBoollist)

            tmpSliceWallArealist.sort()
            tmpSliceWallArealargest = tmpSliceWallArealist[-1]

            tmpSliceWallArea_atPlaque.sort()
            tmpSliceWallArea_atPlaquelargest = tmpSliceWallArea_atPlaque[-1]


            # ********************************* minimum lumen equivalent diameter***********************************
            for slicenum in range(len(self.BranchGroup['branch' + str(BGcont + 1)])):
                if tmpslicePlaqueBoollist[slicenum] == 0:
                    tmpsliceLumenEqDiameterlist[slicenum] = pow(10,5)
            min_index = tmpsliceLumenEqDiameterlist.index(min(tmpsliceLumenEqDiameterlist))
            if tmpsliceLumenEqDiameterlist[min_index] < pow(10,5):
                minimumLumenEqDiameter = tmpsliceLumenEqDiameterlist[min_index]
                self.stenosisWidthInfo['branch' + str(BGcont + 1)] = minimumLumenEqDiameter
                self.stenosisPositionInfo['branch' + str(BGcont + 1)] = min_index
            else:
                # ********************************* the stenosis is defined as the lumen with plaque(not include fibrous cap)***********************************
                self.stenosisWidthInfo['branch' + str(BGcont + 1)] = 0
                self.stenosisPositionInfo['branch' + str(BGcont + 1)] = []

            # ********************************* reference wall equivalent diameter***********************************
            referenceWallEquivalentDiameterIndex = pow(10, 5)
            if sum(tmpslicePlaqueBoollist) != 0:
                PBoolcont = min_index
                ContinueCondition = 1
                ContinueConditionNew = 1
                while PBoolcont <= len(self.BranchGroup['branch' + str(BGcont + 1)])-1 and ContinueCondition ==1:
                    if tmpslicePlaqueBoollist[PBoolcont] != 0:
                        PBoolcont += 1
                    else:
                        referenceWallEquivalentDiameterIndex = PBoolcont
                        ContinueCondition = 0
                print("ContinueCondition", ContinueCondition)
                if ContinueCondition ==1:
                    PBoolcont = min_index
                    while PBoolcont >=0 and ContinueConditionNew == 1:
                        if tmpslicePlaqueBoollist[PBoolcont] != 0:
                            PBoolcont -= 1
                        else:
                            referenceWallEquivalentDiameterIndex = PBoolcont
                            ContinueConditionNew = 0
                print("ContinueConditionNew", ContinueConditionNew)
            else:
                print('branch' + str(BGcont + 1) + " is normal")

            if referenceWallEquivalentDiameterIndex >= pow(10, 5):
                self.BranchGroupreferenceWallEquivalentDiameterIndex[
                    'branch' + str(BGcont + 1)] = 'branch' + str(BGcont + 1) + " is normal"
                self.BranchGroupreferenceWallEquivalentDiameter['branch' + str(BGcont + 1)] = 'branch' + str(BGcont + 1) + " is normal"
                self.StenosisDegreeList.append(0)
                self.BranchGroupStenosisDegree['branch' + str(BGcont + 1)] = 'branch' + str(BGcont + 1) + " is normal"
                ReconstructionIndexlist.append(1)
                self.BranchGroupReconstructionIndex['branch' + str(BGcont + 1)] = 1
            else:
                self.BranchGroupreferenceWallEquivalentDiameterIndex['branch' + str(BGcont + 1)] = \
                    referenceWallEquivalentDiameterIndex

                self.BranchGroupreferenceWallEquivalentDiameter['branch' + str(BGcont + 1)] = \
                tmpsliceWallEqDiameterlist[referenceWallEquivalentDiameterIndex]

                self.StenosisDegreeList.append(minimumLumenEqDiameter / tmpsliceWallEqDiameterlist[referenceWallEquivalentDiameterIndex])

                self.BranchGroupStenosisDegree['branch' + str(BGcont + 1)] = \
                    minimumLumenEqDiameter / tmpsliceWallEqDiameterlist[referenceWallEquivalentDiameterIndex]

                ReconstructionIndexlist.append(tmpSliceWallArea_atPlaquelargest/tmpSliceWallArealist[referenceWallEquivalentDiameterIndex])
                self.BranchGroupReconstructionIndex['branch' + str(BGcont + 1)] = tmpSliceWallArea_atPlaquelargest/tmpSliceWallArealist[referenceWallEquivalentDiameterIndex]


        self.StenosisDegreeList.sort()
        self.stenosisdegree = self.StenosisDegreeList[-1]
        ReconstructionIndexlist.sort()
        self.ReconstructionIndex = ReconstructionIndexlist[-1]

        print("stenosisWidthInfo: ", self.stenosisWidthInfo)
        print("stenosisPositionInfo: ", self.stenosisPositionInfo)
        print("BranchGroupreferenceWallEquivalentDiameterIndex: ", self.BranchGroupreferenceWallEquivalentDiameterIndex)
        print("BranchGroupreferenceWallEquivalentDiameter: ", self.BranchGroupreferenceWallEquivalentDiameter)
        print("BranchGroupStenosisDegree: ", self.BranchGroupStenosisDegree)

        print("stenosisdegree: ", self.stenosisdegree)
        self.PlaqueAnalysisInfo["stenosisdegree"] = self.stenosisdegree

        print("ReconstructionIndex: ", self.ReconstructionIndex)
        self.PlaqueAnalysisInfo["ReconstructionIndex"] = self.ReconstructionIndex

    def wallProperty(self):
        self.wallthicknessInfo = {}
        self.WallThicknessRange = []
        wallmaskthicknesslist = []
        walleccentricitylist = []
        for BGcont in range(len(self.BranchGroup)):

            slicewallthickness = {}
            for slicenum in range(len(self.BranchGroup['branch' + str(BGcont + 1)])):
                slicewallintersectpointsdict = self.sliceIntersectPointsInfo[
                    'branch_' + str(BGcont + 1) + "/layer_" + str(slicenum)]
                # print("slicewallintersectpointsdict", 'branch_' + str(BGcont + 1) + "/layer_" + str(slicenum),slicewallintersectpointsdict)
                # print("slicewallintersectpointsdict__",'branch_' + str(BGcont + 1) + "/layer_" + str(slicenum), slicewallintersectpointsdict)
                contourintersectpointsinfoA = slicewallintersectpointsdict[0]
                contourintersectpointsinfoB = slicewallintersectpointsdict[1]
                # print("contourintersectpointsinfoA",contourintersectpointsinfoA)
                # print("contourintersectpointsinfoB",contourintersectpointsinfoB)
                singleAnglewallthickness = {}
                singleAnglewalleccentricity = []
                for pointcont in range(len(contourintersectpointsinfoA)):  # intersect points num of each angel is 2
                    pa_1 = contourintersectpointsinfoA[pointcont][0]
                    pa_2 = contourintersectpointsinfoA[pointcont][1]
                    pb_1 = contourintersectpointsinfoB[pointcont][0]
                    pb_2 = contourintersectpointsinfoB[pointcont][1]
                    # singleAngleWallthicknessA = numpy.sqrt(
                    #     numpy.square(abs(pb_1[0] - pa_1[0]) +1) + numpy.square(abs(pb_1[1] - pa_1[1]) +1))
                    singleAngleWallthicknessA = numpy.sqrt(
                        numpy.square(abs(pb_1[0] - pa_1[0])) + numpy.square(abs(pb_1[1] - pa_1[1])))
                    if singleAngleWallthicknessA ==0:
                        singleAngleWallthicknessA = 1
                        #print("singleAngleWallthicknessA ==0")
                    # singleAngleWallthicknessB = numpy.sqrt(
                    #     numpy.square(abs(pb_2[0] - pa_2[0]) +1) + numpy.square(abs(pb_2[1] - pa_2[1]) +1))
                    singleAngleWallthicknessB = numpy.sqrt(
                        numpy.square(abs(pb_2[0] - pa_2[0])) + numpy.square(abs(pb_2[1] - pa_2[1])))
                    if singleAngleWallthicknessB ==0:
                        singleAngleWallthicknessB = 1
                        # print("pb_2[0] - pa_2[0] + 1) + numpy.square(pb_2[1] - pa_2[1]",pb_2, pa_2)
                        # print("singleAngleWallthicknessB ==0")
                        # print('branch_' + str(BGcont + 1) + "/layer_" + str(slicenum))

                    singleAnglewallthickness["angle_" + str(pointcont * 360 / len(contourintersectpointsinfoA))] = [
                        singleAngleWallthicknessA, singleAngleWallthicknessB]
                    wallmaskthicknesslist.append(singleAngleWallthicknessA)
                    wallmaskthicknesslist.append(singleAngleWallthicknessB)

                    walleccentricity = numpy.maximum(singleAngleWallthicknessA, singleAngleWallthicknessB)/numpy.minimum(singleAngleWallthicknessA, singleAngleWallthicknessB)
                    #singleAnglewalleccentricity["angle_" + str(pointcont * 360 / len(contourintersectpointsinfoA))] = walleccentricity
                    walleccentricitylist.append(walleccentricity)


                slicewallthickness['layer_' + str(slicenum)] = singleAnglewallthickness
            self.wallthicknessInfo['branch' + str(BGcont + 1)] = slicewallthickness
        wallmaskthicknesslist.sort()
        walleccentricitylist.sort()
        print("wallmaskthicknesslist", wallmaskthicknesslist)

        self.AverWallThickness = sum(wallmaskthicknesslist) / len(wallmaskthicknesslist) * self.spacing_x
        self.WallThicknessRange.append(wallmaskthicknesslist[0] * self.spacing_x)
        self.WallThicknessRange.append(wallmaskthicknesslist[-1] * self.spacing_x)
        self.walleccentricity = walleccentricitylist[-1]
        print("wallthicknessInfo", self.wallthicknessInfo)

        self.PlaqueAnalysisInfo["AverWallThickness"] = self.AverWallThickness
        print("AverWallThickness", self.AverWallThickness)

        self.PlaqueAnalysisInfo["WallThicknessRange"] = self.WallThicknessRange
        print("WallThicknessRange", self.WallThicknessRange)

        self.PlaqueAnalysisInfo["walleccentricity"] = self.walleccentricity
        print("walleccentricity", self.walleccentricity)


    def JsonFileOutput(self):
        json_str = json.dumps(PQA.PlaqueAnalysisInfo)
        with open(self.OutputFilePath, 'w') as json_file:
        #with open(r'E:\tst.json', 'w') as json_file:
            json_file.write(json_str)

    def carotidplt(self):
        #pass self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum + 1)]
        for slicenum in range(0, len(self.BranchGroup['branch1'])):
            BranchSliceofall = self.BranchGroup['branch1'][slicenum]
            plt.figure()
            plt.imshow(BranchSliceofall)
        plt.show()

        # for slicenum in range(0, len(self.BranchSliceGroup_ResetLabelDict)):
        #     BranchSliceofall = self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)]
        #     plt.figure()
        #     plt.imshow(BranchSliceofall)
        # plt.show()

        # for slicenum in range(0, len(self.BranchSliceGroup_ResetLabelDict)):
        #     BranchSliceofall = self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum)]
        #     plt.figure()
        #     plt.imshow(BranchSliceofall)
        # plt.show()





# if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
#     work_dir = sys.argv[1]
#     output_dir = sys.argv[2]
work_dir = r"E:\cerebral_artery\output0915\output\CAIGUIXIANG_1115\OAxQIRfsT1.nii.gz"
#work_dir = r"E:\Carotid\nii\R_plaque_classify_8class_decrop2.nii.gz"
output_dir = r"E:\cerebral_artery\output0915\output\CAIGUIXIANG_1115\tst1.json"

#PQA = PlaqueQuantitativAnalysis(work_dir, output_dir)
PQA = PlaqueQuantitativAnalysis(work_dir, output_dir,1,8)
PQA.LoadData()
PQA.FillIncorrectHole()
PQA.BranchSplited()
PQA.IntersectPoints()


#PQA.inMsk.OriData.shape
#print(PQA.outputData)
#PQA.outputDataOnes.shape
#PQA.PlotOVerlap()
#PQA.VTK3D()


PQA.CarotidParameters()
PQA.wallProperty()
PQA.JsonFileOutput()
#PQA.carotidplt()
print("PlaqueAnalysisInfo:", PQA.PlaqueAnalysisInfo)


# a=(10,15)
# plot_point(a,30,5000)
MainWindow.show()
app.exec_()