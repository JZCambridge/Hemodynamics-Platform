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
import Preprocess_Mask
import Pd_Funs
##############################################################################

##############################################################################
# Standard libs
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
##############################################################################

class FilterMask:
    def __init__(self, UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseFileBtn_FM.clicked.connect(lambda: self.ChooseOpenFile())
        self.ui.loadFileBtn_FM.clicked.connect(lambda: self.LoadImage())
        self.ui.filterBtn_FM.clicked.connect(lambda: self.FilterValues())
        self.ui.chooseSaveBtn_FM.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.saveBtn_FM.clicked.connect(lambda: self.SaveFile())
        self.ui.ChooseBatchCsvBtn_FM.clicked.connect(lambda: self.ChooseCsvFile())
        self.ui.BatchProcessingBtn_FM.clicked.connect(lambda: self.BatchProcessing())
        
        self.InitFilterMask()
        
    def InitFilterMask(self):
        self.ImgDat = None
        self.plotter = None
        self.dataFilterNewVals = None
        self.dataFilterVals = None
        self.DataFrame = None

    def ChooseCsvFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load csv file',
            fileTypes='All files (*.*);; csv files(*.csv)',
            fileObj=self.ui,
            qtObj=True
        )
        # set filename
        self.ui.loadCsvPathTxt_FM.setPlainText(filename)

    def BatchProcessing(self, CSVPath=None):
        if CSVPath:
            self.DataFrame = Pd_Funs.OpenDF(CSVPath, header=0)
        else:
            self.DataFrame = Pd_Funs.OpenDF(self.ui.loadCsvPathTxt_FM.toPlainText(), header=0)
        print(self.DataFrame)
        for i in range(len(self.DataFrame)):
            self.LoadImage(path=self.DataFrame['MaskPath'][i])
            self.FilterValues(labelLst=self.DataFrame['MaskVal'][i],
                              newVal=self.DataFrame['NewMaskVal'][i])
            self.SaveFile(OutDir=self.DataFrame['OutputFolder'][i],
                          NameRef=self.DataFrame['FileNameRef'][i])

    #########################################################
    def ChooseOpenFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image or mask",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadPathTxt_FM.setPlainText(filename)

    def LoadImage(self, path=None):
        # load data
        if not path:
            self.ImgDat = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.ui.loadPathTxt_FM.toPlainText()
            )
        else:
            self.ImgDat = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=path
            )

    def FilterValues(self, labelLst=None, newVal=None):
        # get array of values
        if not labelLst:
            self.lstOut = Preprocess_Mask.StrToLst(strIn=self.ui.filterValTxt_FM.toPlainText())
        else:
            self.lstOut = Preprocess_Mask.StrToLst(strIn=str(labelLst))
        # Filter value
        self.dataFilterVals, dataFilterOnes = Image_Process_Functions.FilterData(
            rangStarts=self.lstOut["floatOut"],
            dataMat=self.ImgDat.OriData,
            funType="single value"
        )

        # set new values
        if not newVal:
            if self.ui.newValLineTxt_FM.text() == "":
                self.dataFilterNewVals = dataFilterOnes
            else:
                # get new mask value
                try:
                    factor = float(self.ui.newValLineTxt_FM.text())
                except:
                    print("Cannot get new mask value")
                    factor = 1
                # set new mask value
                self.dataFilterNewVals = dataFilterOnes * factor
        else:
            self.dataFilterNewVals = dataFilterOnes * newVal
    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.savePathTxt_FM.setPlainText(dirname)

    def SaveFile(self, OutDir=None, NameRef=None):
        # Get file name
        if not NameRef:
            if self.ui.nameRefTxt_FM.toPlainText() == "":
                name = Save_Load_File.FilenameFromPath(self.ui.loadPathTxt_FM.toPlainText())
            else:
                name = Save_Load_File.ValidFileName(self.ui.nameRefTxt_FM.toPlainText())
        else:
            name = NameRef

        if not OutDir:
            tmpDir = self.ui.savePathTxt_FM.toPlainText()
        else:
            tmpDir = OutDir
        # Set file name
        oneFilePath = Save_Load_File.DateFileName(
            Dir=tmpDir,
            fileName=name + "NVl",
            extension=".nii.gz",
            appendDate=False
        )
        # Set file name
        valFilePath = Save_Load_File.DateFileName(
            Dir=tmpDir,
            fileName=name + "Val",
            extension=".nii.gz",
            appendDate=False
        )

        print(oneFilePath)
        print(valFilePath)

        # Save
        Save_Load_File.MatNIFTISave(MatData=self.dataFilterNewVals,
                 imgPath=oneFilePath["CombineName"],
                 imgInfo=self.ImgDat.OriImag,
                 ConvertDType=True,
                 refDataMat=self.ImgDat.OriData)

        Save_Load_File.MatNIFTISave(MatData=self.dataFilterVals,
                                    imgPath=valFilePath["CombineName"],
                                    imgInfo=self.ImgDat.OriImag,
                                    ConvertDType=True,
                                    refDataMat=self.ImgDat.OriData)

        return valFilePath['CombineName']


    def ChooseSaveFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Choose path to save Mask Segmentation",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                                                           "STL files (*.stl) ;; "
                                                           "Img files (*.png *.jpg) ;; "
                                                           "Graphic files (*.svg, *.eps, *.ps, *.pdf, *.tex) ",
                                                 qtObj=True)

        # set filename
        self.ui.savePathTxt_FM.setPlainText(filename)




