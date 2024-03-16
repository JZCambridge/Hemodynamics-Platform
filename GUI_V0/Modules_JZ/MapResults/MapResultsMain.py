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
import SITK_Numpy
import Preprocess_Mask
import Pd_Funs
##############################################################################

##############################################################################
# Standard libs
import os
from datetime import datetime
import numpy


##############################################################################

class MapResults:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            
        self.ui.chooseFileBtn_MR.clicked.connect(lambda: self.ChooseOpenFile())
        self.ui.chooseDirBtn_MR.clicked.connect(lambda: self.ChooseLoadDir())
        self.ui.saveDirBtn_MR.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.convertMatchBtn_MR.clicked.connect(lambda: self.Convert())
        self.ui.batchDF3DBtn_MR.clicked.connect(lambda: self.ChooseBatchFile())
        self.ui.batchBtn_MR.clicked.connect(lambda: self.Batch())
        
        self.InitMapResults()

    def InitMapResults(self):
        # initial definition
        self.maskData = None
        self.MaskArray = None
        self.maskPath = None

    def ChooseOpenFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Choose segmentation to map results on",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadImgPathTxt_MR.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def LoadData(self, filePath=None):
        # load two data
        if filePath is not None:
            self.maskData = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=filePath
            )
            self.maskPath = filePath
        else:
            self.maskData = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.loadImgPathTxt_MR.toPlainText()
            )
            self.maskPath = self.ui.loadImgPathTxt_MR.toPlainText()

        # update message
        self.UpdateMsgLog(msg="Load file:\n{}".format(self.ui.loadImgPathTxt_MR.toPlainText()))

    def ExtractSkin(self, valRange=None):
        # input
        if valRange is not None:
            valRange = Preprocess_Mask.StrToLst(strIn=self.ui.valsLineTxt_MR.text())["floatOut"]

        outArrOnes, outArrVals = Image_Process_Functions.GetSkin(
            inArr=self.maskData.OriData,
            filterVals=valRange
        )

        # save
        # extract file name
        fileName = Save_Load_File.FilenameFromPath(fullPath=self.maskPath)
        dirName, _ = Save_Load_File.ParentDir(path=self.maskPath)
        print(self.maskPath)
        print(self.ui.loadImgPathTxt_MR.toPlainText())
        print(fileName)

        Save_Load_File.MatNIFTISave(
            MatData=outArrOnes,
            imgPath=dirName + '/' + fileName + 'SkinOne.nii.gz',
            imgInfo=self.maskData.OriImag,
            ConvertDType=True,
            refDataMat=self.maskData.OriData
        )
        Save_Load_File.MatNIFTISave(
            MatData=outArrVals,
            imgPath=dirName + '/' + fileName + 'SkinVal.nii.gz',
            imgInfo=self.maskData.OriImag,
            ConvertDType=True,
            refDataMat=self.maskData.OriData
        )

        # update and reload
        self.maskData = None
        self.maskData = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=dirName + '/' + fileName + 'SkinOne.nii.gz'
        )

    def MaskTo3D(self, extractSkin=None, filePath=None, valRange=None):
        # load data
        self.LoadData(filePath=filePath)

        # extract skin
        if extractSkin is None:
            if Save_Load_File.CheckTrue(parameter=self.ui.extractSkinBtnGrp_MR.checkedButton().text()):
                self.ExtractSkin(valRange=valRange)
        elif isinstance(extractSkin, str):
            if Save_Load_File.CheckTrue(parameter=extractSkin):
                self.ExtractSkin(valRange=valRange)

        # SITK to array
        self.MaskArray = SITK_Numpy.SITK_NP_Arr()
        # image and array
        self.MaskArray.InSITKImag(SITKImag=self.maskData.OriImag)
        # mask pixels
        self.MaskArray.PositionMaskValues()
        # flip array
        self.MaskArray.PositionXYZ()
        # convert to 3D space
        self.MaskArray.Actual3DCoors()

        # show message
        msg = "Convert voxel space to actual 3D space: "
        msg += "Voxel position array shape: " + str(numpy.shape(self.MaskArray.inPosition))
        msg += " Spacing array shape: " + str(numpy.shape(self.MaskArray.inSpace))
        msg += "\n--- 3D conversion time: %s seconds ---" % (self.MaskArray.multiT)
        self.UpdateMsgLog(msg=msg)

    def ChooseLoadDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Load data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.loadDirPathTxt_MR.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose loading dir:\n{}".format(dirname))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_MR.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose saving dir:\n{}".format(dirname))

    def Convert(self,
                filePath=None,
                extractSkin=None,
                valRange=None,
                inputDir=None,
                inputNPYPath=None,
                leafSize=None,
                cpus=None,
                filterZero=None,
                radius=None,
                outputDir=None,
                outputImgPath=None,
                ):

        # mask to 3D
        self.MaskTo3D(extractSkin=extractSkin, filePath=filePath, valRange=valRange)

        # input to list/str
        if outputImgPath is None:
            inputDir = [self.ui.loadDirPathTxt_MR.toPlainText()]
        if inputNPYPath is None:
            inputNPYPath = Preprocess_Mask.StrToLst(strIn=self.ui.refNPYPathTxt_MR.toPlainText())["listOut"]

        # forming input lists
        inputPaths = Save_Load_File.AppendLists(inputDir, inputNPYPath, sep="/")["combineList"]

        if leafSize is None:
            leafSize = int(self.ui.leafSizeLineTxt_MR.text())
        if cpus is None:
            cpus = int(self.ui.cpuLineTxt_MR.text())
        if filterZero is None:
            filterZero = Save_Load_File.CheckTrue(parameter=self.ui.filterZeroChoiceBtnGrp_MR.checkedButton().text())
        if radius is None:
            radius = float(self.ui.radiusLineTxt_MR.text())

        # output to lst
        if outputDir is None:
            outputDir = [self.ui.saveDirPathTxt_MR.toPlainText()]
        if outputImgPath is None:
            outputImgPath = Preprocess_Mask.StrToLst(strIn=self.ui.outImgPathTxt_MR.toPlainText())["listOut"]

        # forming output lists
        outputPaths = Save_Load_File.AppendLists(outputDir, outputImgPath, sep="/")[
            "combineList"]

        # create directory
        Save_Load_File.checkCreateDir(path=outputDir[0])

        # compare size
        compareSize = Post_Image_Process_Functions.CompareArrShape(
            dataMat1=inputPaths,
            dataMat2=outputPaths,
            DialogWarn=False
        )

        # update message
        msg = "inputDir: {}".format(inputDir) + \
              "\ninputNPYPath: {}".format(inputNPYPath) + \
              "\ninputPaths: {}".format(inputPaths) + \
              "\nleafSize: {}".format(leafSize) + \
              "\ncpus: {}".format(cpus) + \
              "\nfilterZero: {}".format(filterZero) + \
              "\nradius: {}".format(radius)
        # update message
        print(msg)
        self.UpdateMsgLog(msg=msg)

        if compareSize["error"]:
            # update message
            self.UpdateMsgLog(msg=compareSize["errorMessage"] + "\nNeed Same lists size input!")
        else:
            # update message
            self.UpdateMsgLog(msg=compareSize["errorMessage"])
            self.UpdateMsgLog(msg="Run multiprocessor creating masks!")
            # start output
            matchResults = Post_Image_Process_Functions.MultiProKNN(
                inputPaths=inputPaths,
                outputPaths=outputPaths,
                leafSize=leafSize,
                cpus=cpus,
                mask3DCoors_XYZ=self.MaskArray.Actual3DCoors,
                maskCTCoors_ZYX=self.MaskArray.SITKArrCoors_ZYX,
                maskIn=self.maskData,
                filterZero=filterZero,
                radius=radius,
                outPutLog=False,
                outLogPath=''  # 'G:/Work_Data/PaperXuZhou_26Aug21/Results/AllT1/CheckMap/check.txt'
            )

            # update message
            self.UpdateMsgLog(msg=matchResults["Message"])

    def ChooseBatchFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load csv file',
            fileTypes="All files (*.*);; Table files (*.csv *.txt) ;; More table files (*.xlsx *.xls *.xlsm)",
            fileObj=self.ui,
            qtObj=True
        )
        # set filename
        self.ui.batchTablePathTxt_MR.setPlainText(filename)

        # update
        self.UpdateMsgLog(
            msg="Choose Batch Table File: {}".format(filename)
        )

    def Batch(self, DFPath=None):
        # Input
        if DFPath is None:
            DFPath = self.ui.batchTablePathTxt_MR.toPlainText()

        # DF
        batchDataFrame = Pd_Funs.OpenDF(DFPath, header=0)

        # loop cases
        for filePath, \
            extractSkin, \
            valRange, \
            inputDir, \
            inputNPYPath, \
            leafSize, \
            cpus, \
            filterZero, \
            radius, \
            outputDir, \
            extractSkin, \
            outputImgPath \
                in zip(
            batchDataFrame["Mask Path"].tolist(),
            batchDataFrame["Extract Skin"].tolist(),
            batchDataFrame["Value Exclusion"].tolist(),
            batchDataFrame["Input Directory"].tolist(),
            batchDataFrame["Input NPY Path"].tolist(),
            batchDataFrame["Leaf Size"].tolist(),
            batchDataFrame["CPU"].tolist(),
            batchDataFrame["Filter Zero"].tolist(),
            batchDataFrame["Match Ball Radius"].tolist(),
            batchDataFrame["Output Directory"].tolist(),
            batchDataFrame["Extract Skin"].tolist(),
            batchDataFrame["Output Image File"].tolist()
        ):

            self.Convert(
                filePath=filePath,
                extractSkin=extractSkin,
                valRange=Preprocess_Mask.StrToLst(strIn=valRange)["floatOut"],
                inputDir=[inputDir],
                inputNPYPath=Preprocess_Mask.StrToLst(strIn=inputNPYPath)["listOut"],
                leafSize=int(leafSize),
                cpus=int(cpus),
                filterZero=Save_Load_File.CheckTrue(filterZero),
                radius=float(radius),
                outputDir=[outputDir],
                outputImgPath=Preprocess_Mask.StrToLst(strIn=outputImgPath)["listOut"],
                )

            self.InitMapResults()


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
