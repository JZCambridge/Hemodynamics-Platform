# -*- coding: UTF-8 -*-
'''
@Project ：GUI_V0
@File    ：Centerline_Extraction.py
@IDE     ：PyCharm
@Author  ：YangChen and Jin ZHENG
@Date    ：2021/6/11 11:06 update 14 Jun 22
'''

# Import functions
import os
import os.path
import json
import csv
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
import numpy as np
from datetime import datetime

# import self-writing
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_YC')
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
from FileDisposing import *
import Pd_Funs
import Save_Load_File
import Preprocess_Mask
import Image_Process_Functions
import Matrix_Math
from PySide2.QtUiTools import QUiLoader

class Centerline_Extraction:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseJsonBtn_CE.clicked.connect(lambda: self.openingJsonFile())
        self.ui.CenterlineInfosaveButton_CE.clicked.connect(lambda: self.SaveCenterlineInfo())
        self.ui.centerlinecoorDirBtn_CE.clicked.connect(lambda: self.CenterlineCoorInfoOpt())
        self.ui.ExtraBtn_CE.clicked.connect(lambda: self.CenterlineCoor_Extraction())
        self.ui.ChooseDirBtn_1_CE.clicked.connect(lambda: self.ChooseIterateDir())
        self.ui.BatchProcessBtn_1_CE.clicked.connect(lambda: self.BatchCenterlineProcessing())
        self.ui.ChooseOpenMskFileMS_CE.clicked.connect(lambda: self.ChooseOpenMskFileMS())
        self.ui.ChooseOutDirMS_CE.clicked.connect(lambda: self.ChooseOutDirMS())
        self.ui.ChooseOpenJSNFileMS_CE.clicked.connect(lambda: self.ChooseOpenJSNFileMS())
        self.ui.ChooseOpenVMTKFileMS_CE.clicked.connect(lambda: self.ChooseOpenVMTKEXEMS())
        self.ui.ExtractCenterline_CE.clicked.connect(lambda: self.ExtractCenterline())
        self.ui.pushButton_BatchTable_CE.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_CE.clicked.connect(lambda: self.batchrun())

        self.InitCenterline()

    def InitCenterline(self):
        self.JsonFilAbsPth = None
        self.CenterlineInfo_fileAbsPth = None
        self.Centerline_csv_FilDirectory = None
        self.Centerline_csv_FilDirectory = None

        self.iterateDir = None
        self.R_Collection = []
        self.L_Collection = []

    """
    ##############################################################################
    # automatic for built-in segmentation package
    ##############################################################################
    """

    def openingJsonFile(self):
        self.JsonFilAbsPth = Opening_File(self.ui, "Json (*.json)")
        self.ui.loadExePathTxt_CE.setPlainText(self.JsonFilAbsPth)

    #################################################################################
    def ChooseIterateDir(self):
        self.iterateDir = Save_Load_File.OpenDirPathQt(dispMsg='Choose directory to iterate',
                                                       fileObj=self.ui,
                                                       qtObj=True
                                                       )

        self.ui.IterateDirPathTxt_1_CE.setPlainText(self.iterateDir)

    ################################################################################
    def SaveCenterlineInfo(self):
        self.CenterlineInfo_fileAbsPth = \
            QFileDialog.getSaveFileName(self.ui, "Save Centerline file", "", "Csv Files (*.csv)")[0]
        self.ui.plainTextEdit_csvInfo_CE.setPlainText(self.CenterlineInfo_fileAbsPth)

    def CenterlineCoorInfoOpt(self):
        self.Centerline_csv_FilDirectory = Opening_FileDialog(self.ui)
        self.ui.csvCenterlineCoorOpt_CE.setPlainText(self.Centerline_csv_FilDirectory)

    def CenterlineCoor_Extraction(self, jsonPath=None):
        # If single file extraction method, program read the json file path from the ui text
        if not jsonPath:
            with open(self.ui.loadExePathTxt_CE.toPlainText()) as json_file:
                LCenterline_jsondata = json.load(json_file)

            data_file = open(self.ui.plainTextEdit_csvInfo_CE.toPlainText(), 'w', newline='')
            csvPath = self.ui.csvCenterlineCoorOpt_CE.toPlainText()

        # if batch processing method is chosen, the json file from iteration are processed to the program one by one
        else:
            with open(jsonPath) as json_file:
                LCenterline_jsondata = json.load(json_file)

            data_file = open(('.'.join(jsonPath.split('.')[:-1])) + '.csv', 'w', newline='')
            csvPath = '\\'.join(jsonPath.split('\\')[:-1]) + '\\'

        # create more extended dictionary elements
        allBranches = [x["branch_name"] for x in LCenterline_jsondata]
        print(allBranches)
        if 'pRCA' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "R-aorta"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "pRCA"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "mRCA"), None)['coordinates']
            dict = {"branch_name": 'pRCAExt','coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'mRCA' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "pRCA"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "mRCA"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "dRCA"), None)['coordinates']
            dict = {"branch_name": 'mRCAExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'dRCA' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "mRCA"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "dRCA"), None)['coordinates']
            dict = {"branch_name": 'dRCAExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'LM' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "L-aorta"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "LM"), None)['coordinates']
            dict = {"branch_name": 'LMExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'pLAD' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "LM"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "pLAD"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "mLAD"), None)['coordinates']
            dict = {"branch_name": 'pLADExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'mLAD' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "pLAD"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "mLAD"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "dLAD"), None)['coordinates']
            dict = {"branch_name": 'mLADExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'dLAD' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "mLAD"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "dLAD"), None)['coordinates']
            dict = {"branch_name": 'dLADExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'pCx' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "LM"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "pCx"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "LCx"), None)['coordinates']
            dict = {"branch_name": 'pCxExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'LCx' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "pCx"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "LCx"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "L-PDA"), None)['coordinates']
            dict = {"branch_name": 'LCxExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'L-PDA' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "LCx"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "L-PDA"), None)['coordinates']
            dict = {"branch_name": 'dLCXExt', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'pRCA' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "pRCA"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "mRCA"), None)['coordinates']
            dict = {"branch_name": 'pmRCA', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'pLAD' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "pLAD"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "mLAD"), None)['coordinates']
            dict = {"branch_name": 'pmLAD', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        if 'pCx' in allBranches:
            extCoor = next((item for item in LCenterline_jsondata if item["branch_name"] == "pCx"), None)['coordinates'] + \
                      next((item for item in LCenterline_jsondata if item["branch_name"] == "LCx"), None)['coordinates']
            dict = {"branch_name": 'pmCx', 'coordinates': extCoor}
            LCenterline_jsondata.append(dict)

        csv_writer = csv.writer(data_file)
        count = 0
        for data in LCenterline_jsondata:  # data type =list
            if count == 0:
                header = data.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(data.values())

            # the write method changed to append due to both left and right coronary file contains unknown label
            # Centerline_csv = open(self.ui.csvCenterlineCoorOpt_CE.toPlainText() + "%s.csv" % data['branch_name'], 'w', newline='')
            outPath = csvPath + "%s.csv" % data['branch_name']

            # delete old create new
            if os.path.exists(outPath): os.remove(outPath)

            # new write
            Centerline_csv = open(outPath, 'w', newline='')
            Centerline_csv_writer = csv.writer(Centerline_csv)

            count_coordinates = 0
            for coordinates in data['coordinates']:
                if count_coordinates == 0:
                    header_coordinates = coordinates.keys()
                    csv_writer.writerow(header_coordinates)
                    count_coordinates += 1
                Centerline_csv_writer.writerow(coordinates.values())
            Centerline_csv.close()
        data_file.close()

    @staticmethod
    # remove the suffix of auto-generated json file within a folder range
    def RenameJsonFile(dir=None):
        R_Collection = []
        L_Collection = []

        for (root, dirs, files) in os.walk(dir):
            R_Centerline = 'R_coronary_centerline_network.json.txt'
            L_Centerline = 'L_coronary_centerline_network.json.txt'
            newRName = '.'.join(R_Centerline.split('.')[:-1])
            newLName = '.'.join(L_Centerline.split('.')[:-1])

            if R_Centerline in files:
                if newRName not in files:
                    os.rename(os.path.join(root, R_Centerline), os.path.join(root, newRName))
                if newLName not in files:
                    os.rename(os.path.join(root, L_Centerline), os.path.join(root, newLName))

                R_Collection.append(os.path.join(root, newRName))
                L_Collection.append(os.path.join(root, newLName))
            elif newRName in files:
                R_Collection.append(os.path.join(root, newRName))
                L_Collection.append(os.path.join(root, newLName))
        return R_Collection, L_Collection

    # iterate the right and left centerline collection, extract the csv files automatically
    def BatchCenterlineProcessing(self, dir=None):
        if dir:
            self.R_Collection, self.L_Collection = self.RenameJsonFile(dir)
        else:
            self.R_Collection, self.L_Collection = self.RenameJsonFile(self.ui.IterateDirPathTxt_1_CE.toPlainText())

        for i in self.R_Collection:
            self.CenterlineCoor_Extraction(jsonPath=i)
        for j in self.L_Collection:
            self.CenterlineCoor_Extraction(jsonPath=j)

        print('Batch Centerline Extraction Processing Done, Congrats')

    """
    ##############################################################################
    # automatic for manual segmentation package
    ##############################################################################
    """

    def ChooseOutDirMS(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose output directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.OutDirPathTxtMS_CE.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose output directory:\n{}".format(dirname))

    def ChooseOpenMskFileMS(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load image segmentation",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.mskPathTxtMS_CE.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose segmentation file:\n{}".format(filename))

    def ChooseOpenJSNFileMS(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load image segmentation",
            fileTypes="All files (*.*);; JSON files (*.json)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.jsonFilePathTxtMS_CE.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose json file:\n{}".format(filename))

    def ChooseOpenVMTKEXEMS(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Choose VMTK Centerline EXE",
            fileTypes="All files (*.*);; EXE (*.exe)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.VMTKFilePathTxtMS_CE.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose EXE file:\n{}".format(filename))

    def ExtractCenterline(self,
                          infile=None,
                          outDir=None,
                          jsonFile=None,
                          funType=None,
                          vmtkFun=None,
                          exePath=None,
                          rangeStarts=None,
                          rangeStops=None,
                          SaveIntermediate=None,
                          size_surface=None,
                          voxThres=None
                          ):

        # load input
        ## mask
        if infile is None: infile = self.ui.mskPathTxtMS_CE.toPlainText()
        if outDir is None: outDir = self.ui.OutDirPathTxtMS_CE.toPlainText()
        if SaveIntermediate is None: SaveIntermediate = self.ui.SaveInterRadBtn_CE.isChecked()

        ## ref json
        if jsonFile is None: jsonFile = self.ui.jsonFilePathTxtMS_CE.toPlainText()
        ## filtering input
        if funType is None: funType = self.ui.funTypeCBox_CE.currentText()
        if rangeStarts is None:
            rangeStarts = Preprocess_Mask.StrToLst(
                strIn=self.ui.SegmentFilterRangeStartsTxt_CE.toPlainText()
            )["floatOut"]
        if rangeStops is None:
            rangeStops = Preprocess_Mask.StrToLst(
                strIn=self.ui.SegmentFilterRangeStopsTxt_CE.toPlainText()
            )["floatOut"]

        # vmtk
        if vmtkFun is None: vmtkFun = self.ui.VMTKRadBtn_CE.isChecked()
        if exePath is None: exePath = self.ui.VMTKFilePathTxtMS_CE.toPlainText()
        if size_surface is None: size_surface = int(self.ui.SurfaceSizeLineTxtMS_CE.text())
        if voxThres is None: voxThres = int(self.ui.voxThresLineTxtMS_CE.text())

        # load dictionary
        with open(jsonFile, 'r') as f:
            coronaryDictLst = json.load(f)
        f.close()

        # convert into default dictionary
        inDict = {}
        for dict in coronaryDictLst:
            inDict[str(dict["label"][0])] = dict["branch_name"]

        # extract centerline
        initDictLst = Image_Process_Functions.ManCenterlineGeneration(
            inPath=infile,
            rangeStarts=rangeStarts,
            rangeStops=rangeStops,
            funType=funType,
            SaveIntermediate=True,
            outDir=outDir,
            connectType=3,
            labelDict=inDict,
            vmtkFun=vmtkFun,
            exePath=exePath,
            size_surface=size_surface,
            voxThres=voxThres)

        # output json dictionary
        lblLst = [dict["label"][0] for dict in coronaryDictLst]
        print(lblLst)
        outDictLst = []
        for dict in initDictLst:
            # output dictionary
            dictOut = {}

            # find label
            position = lblLst.index(dict["label"])

            # output dictionary
            dictOut["branch_name"] = dict["branch_name"]
            dictOut["parenthood"] = coronaryDictLst[position]["parenthood"]
            dictOut["label"] = [dict["label"]]
            dictOut["coordinates"] = dict["coordinatesXYZ"]

            outDictLst.append(dictOut)

        print(outDictLst)

        # Set file name
        OutFilePath = Save_Load_File.DateFileName(
            Dir=outDir,
            fileName="Centerline",
            extension=".json",
            appendDate=False
        )

        # output
        with open(OutFilePath["CombineName"], 'w') as fp:
            json.dump(outDictLst, fp)
        fp.close()

        self.UpdateMsgLog("Write: \n{}".format(OutFilePath["CombineName"]))


        OutFilePathTxt = Save_Load_File.DateFileName(
            Dir=outDir,
            fileName="Centerline.json",
            extension=".txt",
            appendDate=False
        )

        # output
        Save_Load_File.WriteTXT(
            path=OutFilePathTxt["CombineName"],
            txt=str(outDictLst),
            mode="write"
        )

        self.UpdateMsgLog("Write: \n{}".format(OutFilePathTxt["CombineName"]))

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
        print(disp)

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_CE.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_CE.toPlainText()
        DF = Pd_Funs.OpenDF(inpath, header=0)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            infile = ''
            outDir = ''
            jsonFile = ''
            funType = 'single value greater'
            vmtkFun = False
            exePath = ''
            rangeStarts = 0
            rangeStops = 0
            SaveIntermediate = True
            size_surface = 20
            voxThres = 269

            try:
                if info["Mask NIFTI File"]:
                    infile = info["Mask NIFTI File"]
            except:
                pass
            try:
                if info["Output Folder"]:
                    outDir = info["Output Folder"]
            except:
                pass
            try:
                if info["Reference Dictionary JASON"]:
                    jsonFile = info["Reference Dictionary JASON"]
            except:
                pass
            try:
                if info["Filtering method"]:
                    funType = info["Filtering method"]
            except:
                pass
            try:
                if isinstance(info["use VMTK"], np.bool_):
                    vmtkFun = info["use VMTK"]
            except:
                pass
            try:
                if info["VMTK exe Path"]:
                    exePath = info["VMTK exe Path"]
            except:
                pass
            try:
                if info["rangeStarts"]:
                    rangeStarts = info["rangeStarts"]
            except:
                pass
            try:
                if info["rangeStops"]:
                    rangeStops = info["rangeStops"]
            except:
                pass
            try:
                if isinstance(info["SaveIntermediate"], np.bool_):
                    SaveIntermediate = info["SaveIntermediate"]
            except:
                pass
            try:
                if info["Surface Size"]:
                    size_surface= info["Surface Size"]
            except:
                pass
            try:
                if info["Threshold Voxel Volume"]:
                    voxThres = info["Threshold Voxel Volume"]
            except:
                pass

            # Touched function
            self.ExtractCenterline(infile,outDir,jsonFile,funType,vmtkFun,exePath,[rangeStarts],[rangeStops],
                                   SaveIntermediate,int(size_surface),int(voxThres))
            self.InitCenterline()