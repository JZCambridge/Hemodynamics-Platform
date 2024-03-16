# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：PlaqueQuantitativeAnalysis.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/10/20 11:36
'''
########################################################################################################################
import sys
import os
import time
#nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../../../Functions_YC')
sys.path.insert(0, '../../../Functions_JZ')
# Import functions
# Standard libs
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox,QWidget, QTableWidget, QHBoxLayout, QVBoxLayout, QApplication, QTableWidgetItem, QAbstractItemView,QTabWidget,\
    QDialog,QComboBox, QProgressBar,  QLabel, QStatusBar,QLineEdit, QHeaderView
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from FileDisposing import *
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
import os
import json
import nibabel
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



from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
########################################################################################################################
# Standard libs
import numpy
from scipy.interpolate import splprep, splev
from scipy import ndimage
import numpy as np
import math
import matplotlib.pyplot as plt
################################################################################
################################################################################

class ImageProcessingY:
    def __init__(self):
                # #workpath
        self.InputFileName =None
        self.OutputFilePath = None
        self.axis = None

        self.NiftiFilAbsPathList = None
        self.niftiFileSaveDir = None
        self.img_affine = None


        self.IntDataType = None
        self.FloatDataType = None
        # initial definition
        self.spacing_x = None
        self.spacing_y = None
        self.spacing_z = None
        self.outputData = None
        self.outputDataFlip = None
        self.CTA = None
        self.inMsk = None


        self.rtrnInfo = {}
        self.rtrnInfo["error"] = False
        self.rtrnInfo["errorMessage"] = ""
        self.rtrnInfo["warningMessage"] = ""
        self.rtrnInfo["processTime"] = None
        self.rtrnInfo["processTimeMessage"] = None
        self.rtrnInfo["ControlPoints"] = None
        self.rtrnInfo["sortArray"] = None
        self.rtrnInfo["message"] = ""
        self.rtrnInfo["processTime"] = None

        # time
        #strtT = time.time()
        #stpT = time.time()

        self.ui = QUiLoader().load('./ui/niftiFlipping.ui')
        self.ui.chooseFileButton_IPY.clicked.connect(
            self.ChooseNiftiFiles)
        # self.ui.chooseFileButton_IPY.clicked.connect(
        #     self.loadNiftiFilAbsPathList)

        self.ui.outputButton_IPY.clicked.connect(
            self.outputFilePathChoose)

        self.ui.Run_IPY.clicked.connect(self.runNiftiFlip)

    ####################################################################################################################
    ######################################## read the Tissue coors ###############################################
    def ChooseNiftiFiles(self):
        # ***************************** Extract the coordinates of each components ************************************#
        NiftiFil = Opening_Files(self.ui, "NiftiFile (*.nii.gz)")
        self.ui.plainTextEdit_IPY.clear()
        for listele in NiftiFil:
            listele += ','
            self.ui.plainTextEdit_IPY.appendPlainText(listele)

    def loadNiftiFilAbsPathList(self):
        # self.NiftiFilAbsPathList = Preprocess_Mask.StrToLst(
        #     strIn=self.ui.plainTextEdit_IPY.toPlainText())["listOut"]
        tempFilenamelist = self.ui.plainTextEdit_IPY.toPlainText()
        self.NiftiFilAbsPathList =tempFilenamelist.split(',')
        print( " self.NiftiFilAbsPathList",self.NiftiFilAbsPathList)
        return self.NiftiFilAbsPathList

    def outputFilePathChoose(self):
        self.niftiFileSaveDir = Opening_FileDialog(self.ui)
        self.ui.OutputplainTextEdit_IPY.setPlainText(
            self.niftiFileSaveDir)
        return self.niftiFileSaveDir

    def LoadData(self):
        #load data
        self.inMsk = Save_Load_File.OpenLoadNIFTI(
            GUI = False,
            #filePath = mskPath
            filePath = self.InputFileName
        )
        # update display data
        self.outputDataInit = copy.deepcopy(self.inMsk.OriData)
        self.outputData = self.outputDataInit
        self.IntDataType = self.inMsk.OriData.dtype
        try:
            self.outputData = numpy.array(
                self.outputDataInit,
                dtype=self.inMsk.OriData.dtype.type
            )
        except:
            self.outputData = numpy.array(
                self.outputDataInit,
                dtype=numpy.int16
            )
        self.rtrnInfo["message"] += "Load data success!\n"
        # for slicenum in range(0, len(self.outputData)):
        #     BranchSliceofallOri = self.outputData[slicenum]
            # plt.figure().suptitle('Origin' + str(slicenum))
            # plt.imshow(BranchSliceofallOri)

        # try:
        #     itkImag = SimpleITK.ReadImage(self.InputFileName)
        #     # get voxel spacing (for 3-D image)
        #     spacing = itkImag.GetSpacing()
        #     self.spacing_x = spacing[0]
        #     self.spacing_y = spacing[1]
        #     self.spacing_z = spacing[2]
        # except:
        #         self.rtrnInfo[
        #             "errorMassage"] += "Get spacing failed!\n"
        #         # self.JsonFileOutput()

    def DataMatrixFlip(self):
        self.axis = int(self.ui.FlipAxisplainTextEdit_IPY.toPlainText())
        try:
            self.outputDataFlip = numpy.flip(self.outputData, self.axis)
            # for slicenum in range(0, len(self.outputDataFlip)):
            #     BranchSliceofallFlip = self.outputDataFlip[slicenum]
            #     plt.figure().suptitle('Fliped' + str(slicenum))
            #     plt.imshow(BranchSliceofallFlip)
            # plt.show()
        except:
            print("Flip failed!")


    def NifitFileSaving(self,index):
        # self.niftiFileSaveDir = self.ui.OutputplainTextEdit_IPY.toPlainText()
        self.niftiFileSaveDir = self.ui.OutputplainTextEdit_IPY.toPlainText().split(",")[index]
        head, FilNam, FilFormat = Split_AbsFilePath(self.InputFileName)
        # #print("head",head,"FilNam",FilNam,"FilFormat",FilFormat)
        # niftiFileSaving1 = nibabel.Nifti1Image(self.outputDataFlip, affine=self.img_affine)
        # niftiFileSaving = nibabel.Nifti1Image(niftiFileSaving1, affine=self.img_affine)
        #
        # nibabel.save(niftiFileSaving, self.niftiFileSaveDir + "/" + FilNam + ".nii" + "Fliped" + ".nii.gz")
        img = SimpleITK.GetImageFromArray(self.outputDataFlip)
        SimpleITK.WriteImage(img, self.niftiFileSaveDir + "/" + FilNam.strip(".nii") + "Fliped" + ".nii.gz")
        print("success")

    def runNiftiFlip(self):
        count = 0
        self.loadNiftiFilAbsPathList()
        print("self.NiftiFilAbsPathList", self.NiftiFilAbsPathList)
        for filename in self.NiftiFilAbsPathList:
            # self.InputFileName = repr(filename)
            self.InputFileName = filename            # self.img_affine = nibabel.load(self.InputFileName).affine
            # print("self.img_affine", self.img_affine ,type(self.img_affine))
            # print("self.InputFileName", self.InputFileName)
            try:
                self.LoadData()
                self.DataMatrixFlip()
                self.NifitFileSaving(count)
            except:
                print(self.InputFileName)
            count+=1
            print(count)



    #
    # def carotidplt(self):
    #     #pass self.BranchSliceGroup_ResetLabelDict['layer' + str(slicenum + 1)]
    #     for slicenum in range(0, len(self.outputData)):
    #         BranchSliceofallOri = self.outputData[slicenum]
    #         plt.figure().suptitle('Origin' + str(slicenum))
    #         plt.imshow(BranchSliceofallOri)
    #
    #     for slicenum in range(0, len(self.outputDataFlip)):
    #         BranchSliceofallFlip = self.outputDataFlip[slicenum]
    #         plt.figure().suptitle('Fliped' + str(slicenum))
    #         plt.imshow(BranchSliceofallFlip)
    #     plt.show()


        # for cont in range(len(self.BranchSliceGroup_ResetLabelDict)):
        #     BranchSliceofall = self.BranchSliceGroup_ResetLabelDict[
        #         'layer' + str(cont)]
        #     plt.figure()
        #     plt.imshow(BranchSliceofall)
        # plt.show()


        #self.BranchSliceGroup_ResetLabelDict
    # def UpdateMsgLog(self, msg=""):
    #     # Date and time
    #     nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
    #     disp = "##############" \
    #            + nowStr \
    #            + "############## \n" \
    #            + msg \
    #            + "\n############################\n"

        # update log and display message
        # self.ui.plainTextEdit_Message.setPlainText(disp)
        # self.ui.plainTextEdit_Log.appendPlainText(disp)
        # print(disp)

app = QApplication([])
# MainWindow = QMainWindow()
# FileDialog = QFileDialog(MainWindow)
stats = ImageProcessingY()
stats.ui.show()
app.exec_()
