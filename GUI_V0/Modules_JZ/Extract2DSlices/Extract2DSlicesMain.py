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
import Preprocess_Mask
import Use_Plt
import VTK_Functions
import VTK_Numpy
import QT_GUI
import Pd_Funs
import Matrix_Math
##############################################################################

##############################################################################
# Standard library
import skimage.measure
import numpy
import scipy.stats
import skimage.segmentation
import skimage.morphology
from multiprocessing import Pool
from datetime import datetime
import time
import scipy.ndimage
import copy
import pandas


##############################################################################

class Extract2DSlices:
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.DirPathFDBtn_E2SJZ.clicked.connect(lambda: self.ChooseOpenDirFD())
        self.ui.DirPathESBtn_E2SJZ.clicked.connect(lambda: self.ChooseOpenDirES())
        self.ui.DirPathRTBtn_E2SJZ.clicked.connect(lambda: self.ChooseOpenDirRT())
        self.ui.DirPathACBtn_E2SJZ.clicked.connect(lambda: self.ChooseOpenDirAC())
        self.ui.FillDisksBtn_E2SJZ.clicked.connect(lambda: self.FillDisks())
        self.ui.Extract2DSlicesBtn_E2SJZ.clicked.connect(lambda: self.Extract2DSlices())
        self.ui.RadiomicsTableBtn_E2SJZ.clicked.connect(lambda: self.Radiomics2DTable())
        self.ui.RadiomicsTableBtn_E2SJZ.clicked.connect(lambda: self.Radiomics2DTable())
        self.ui.AreaCalculationBtn_E2SJZ.clicked.connect(lambda: self.AreaCalculation())

    '''
    ##############################################################################
    # Fill Disks
    ##############################################################################
    '''

    def ChooseOpenDirFD(self):
        # Open folder
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadDirPathFDTxt_E2SJZ.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose directory:\n{}".format(dirname))

    def FillDisks(self):
        # Inputs
        inMskDir = self.ui.loadDirPathFDTxt_E2SJZ.toPlainText()
        searchFolderStrLst = Preprocess_Mask.StrToLst(self.ui.searchFolderStrsFDTxt_E2SJZ.toPlainText())["listOut"]
        searchFileStrLst = Preprocess_Mask.StrToLst(self.ui.searchFileStrsFDTxt_E2SJZ.toPlainText())["listOut"]
        sliceStartLst = Preprocess_Mask.StrToLst(self.ui.sliceStartsFDTxt_E2SJZ.toPlainText())["intOut"]
        minimumAreaLst = Preprocess_Mask.StrToLst(self.ui.minimumAreasFDTxt_E2SJZ.toPlainText())["intOut"]
        diskSizeLst = Preprocess_Mask.StrToLst(self.ui.diskSizesFDTxt_E2SJZ.toPlainText())["intOut"]

        # Search all files
        for folder in searchFolderStrLst:
            for i in range(len(searchFileStrLst)):
                # file and slice
                file = searchFileStrLst[i]
                sliceStart = sliceStartLst[i]
                minimumArea = minimumAreaLst[i]

                # find all files
                allFiles = Save_Load_File.ReturnFilesFullPath(
                    dirPath=inMskDir,
                    fileRef=file,
                    folderSearch=folder,
                    traverse=True
                )

                # update message
                # self.UpdateMsgLog(
                #     msg="Find files:\n{}".format(allFiles)
                # )

                # filling disks
                for diameter in diskSizeLst:
                    Image_Process_Functions.replaceSegmentDisks(
                        inMaskPaths=allFiles,
                        diskDiameterMM=diameter,
                        outMaskRef=Save_Load_File.FilenameFromPath(file),
                        sliceStart=sliceStart,
                        sliceSum=minimumArea
                    )

    '''
    ##############################################################################
    # Extract 2D slices
    ##############################################################################
    '''

    def ChooseOpenDirES(self):
        # Open folder
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadDirPathESTxt_E2SJZ.setPlainText(dirname)

    def Extract2DSlices(self):
        # Inputs
        inMskDir = self.ui.loadDirPathESTxt_E2SJZ.toPlainText()
        searchFolderStrLst = Preprocess_Mask.StrToLst(self.ui.searchFolderStrsESTxt_E2SJZ.toPlainText())["listOut"]
        searchFileStrLst = Preprocess_Mask.StrToLst(self.ui.searchFileStrsESTxt_E2SJZ.toPlainText())["listOut"]
        searchFileRefMaskStrLst = Preprocess_Mask.StrToLst(self.ui.searchFileReMskStrsESTxt_E2SJZ.toPlainText())[
            "listOut"]
        filterMethodLst = Preprocess_Mask.StrToLst(self.ui.filterMethodESTxt_E2SJZ.toPlainText())["listOut"]
        thresStartLst = Preprocess_Mask.StrToLst(self.ui.thresStartESTxt_E2SJZ.toPlainText())["intOut"]
        thresStopLst = Preprocess_Mask.StrToLst(self.ui.thresStopESTxt_E2SJZ.toPlainText())["intOut"]

        # Search all files
        for folder in searchFolderStrLst:
            for i in range(len(searchFileStrLst)):
                # file and slice
                file = searchFileStrLst[i]
                fileRef = searchFileRefMaskStrLst[i]
                filter = filterMethodLst[i]
                thresStart = thresStartLst[i]
                thresStop = thresStopLst[i]

                # find all files
                allFiles = Save_Load_File.ReturnFilesFullPath(
                    dirPath=inMskDir,
                    fileRef=file,
                    folderSearch=folder,
                    traverse=True
                )

                # update message
                self.UpdateMsgLog(
                    msg="Find files:\n{}".format(allFiles)
                )

                # output
                for inFile in allFiles:
                    # file index
                    fileNameIndex = inFile.index(file)

                    # ref file name
                    if fileRef == 'none' or fileRef == 'None':
                        refFilePath = None
                    else:
                        refFilePath = inFile[:fileNameIndex] + fileRef + ".nii.gz"

                    # filling disks
                    Post_Image_Process_Functions.Extract2DSlicesRef(
                        inFile=inFile,
                        refFile=refFilePath,
                        filterMethod=filter,
                        thresStart=thresStart,
                        thresStop=thresStop
                    )

    '''
    ##############################################################################
    # Create 2D radiomics table
    ##############################################################################
    '''

    def ChooseOpenDirRT(self):
        # Open folder
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadDirPathRTTxt_E2SJZ.setPlainText(dirname)

    def Radiomics2DTable(self):
        # Inputs
        searchDir = self.ui.loadDirPathRTTxt_E2SJZ.toPlainText()
        IDstr = self.ui.IDstrRTTxt_E2SJZ.toPlainText()
        searchFolderStrLst = Preprocess_Mask.StrToLst(self.ui.searchFolderStrsRTTxt_E2SJZ.toPlainText())["listOut"]
        radiomicsFolderStr = self.ui.radiomicsFolderStrRTTxt_E2SJZ.toPlainText()
        searchFolderRefImgStrLst = Preprocess_Mask.StrToLst(self.ui.searchFolderReImgStrsRTTxt_E2SJZ.toPlainText())[
            "listOut"]
        searchFileRefImgStrLst = Preprocess_Mask.StrToLst(self.ui.searchFileReImgStrsRTTxt_E2SJZ.toPlainText())[
            "listOut"]
        searchFolderRefMskStrLst = Preprocess_Mask.StrToLst(self.ui.searchFolderReMskStrsRTTxt_E2SJZ.toPlainText())[
            "listOut"]
        searchFileRefMskStrLst = Preprocess_Mask.StrToLst(self.ui.searchFileReMskStrsRTTxt_E2SJZ.toPlainText())[
            "listOut"]
        raiomicsTableRefStrLst = Preprocess_Mask.StrToLst(self.ui.RadiomicsTableStrsRTTxt_E2SJZ.toPlainText())[
            "listOut"]

        # find all folder in folder string & create radiomics folder
        folderSearchLst = []
        radiomicsFolder = []
        IDLst = []
        for folder in searchFolderStrLst:
            folderFullPath = Save_Load_File.ReturnFoldersFullPath(
                dirPath=searchDir,
                folderSearch=folder,
                traverse=True
            )
            self.UpdateMsgLog(msg="Folders under: \n{} \nare \n{}".format(searchDir, folderFullPath))

            # append
            folderSearchLst += folderFullPath

            # radiomics folders
            for folderFull in folderFullPath:
                radiomicsFullPath = folderFull.replace(folder, radiomicsFolderStr)

                # create folder
                print(radiomicsFullPath)
                Save_Load_File.checkCreateDir(path=radiomicsFullPath)

                # append
                radiomicsFolder.append(radiomicsFullPath)

                # get ID
                IDtemp = radiomicsFullPath.replace(IDstr, '')
                IDtemp = IDtemp.replace(radiomicsFolderStr, '')
                IDtemp = IDtemp.replace('//', '\\')
                IDtemp = IDtemp.replace('/', '\\')

                # find first "/"
                indices = Save_Load_File.FindIndicesStr(s=IDtemp, ch='\\')

                IDtemp = IDtemp[(indices[0]+1):indices[1]]

                self.UpdateMsgLog(msg="Get ID: {}".format(IDtemp))

                IDLst.append(IDtemp)

        # record of paths
        overallDict = {}
        for key in raiomicsTableRefStrLst:
            overallDict[key] = []

        # create radiomics tables
        for searchFolderNum in range(len(folderSearchLst)):  # search folder
            # folders IDs
            searchFolder = folderSearchLst[searchFolderNum]
            radiomcisFolder = radiomicsFolder[searchFolderNum]
            IDFind = IDLst[searchFolderNum]

            for folderNum in range(len(searchFolderRefImgStrLst)):
                # folders
                ImgFolder = searchFolderRefImgStrLst[folderNum]
                MskFolder = searchFolderRefMskStrLst[folderNum]
                imgRef = searchFileRefImgStrLst[folderNum]
                mskRef = searchFileRefMskStrLst[folderNum]
                radiomicsTableRef = raiomicsTableRefStrLst[folderNum]

                # find folders
                imgFolderFullPath = Save_Load_File.ReturnFoldersFullPath(
                    dirPath=searchFolder,
                    folderSearch=ImgFolder,
                    traverse=True
                )
                self.UpdateMsgLog(msg="Folders under: \n{} \nare \n{}".format(searchFolder, imgFolderFullPath))

                mskFolderFullPath = Save_Load_File.ReturnFoldersFullPath(
                    dirPath=searchFolder,
                    folderSearch=MskFolder,
                    traverse=True
                )
                self.UpdateMsgLog(msg="Folders under: \n{} \nare \n{}".format(searchFolder, mskFolderFullPath))

                # find all find file
                imgFiles = [f for f in os.listdir(imgFolderFullPath[0]) if os.path.isfile(os.path.join(imgFolderFullPath[0],f))]
                mskFiles = [f for f in os.listdir(mskFolderFullPath[0]) if os.path.isfile(os.path.join(mskFolderFullPath[0],f))]

                # files number
                imgFilesTmp = [s.replace(imgRef, "") for s in imgFiles]
                imgFilesTmp = [s.replace(".nii.gz", "") for s in imgFilesTmp]
                fileNums = [int(s) for s in imgFilesTmp]
                fileNumsSort = sorted(fileNums)


                # check all files
                imgFilesOut = []
                mskFilesOut = []
                SliceLst = []
                for num in fileNumsSort:
                    # check all files exists
                    mskFile = mskRef + str(num) + ".nii.gz"
                    if mskFile in mskFiles:
                        imgFileFull = os.path.join(imgFolderFullPath[0], (imgRef + str(num) + ".nii.gz")).replace('/', '\\')
                        imgFilesOut.append(imgFileFull)
                        mskFileFull = os.path.join(mskFolderFullPath[0], (mskRef + str(num) + ".nii.gz")).replace('/','\\')
                        mskFilesOut.append(mskFileFull)
                        SliceLst.append(num)
                    else:
                        self.UpdateMsgLog(msg="Cannot find slice: {} -- {}".format(num, mskFile))

                # Table output
                outDf = pandas.DataFrame(
                    {'ID': SliceLst,
                     'Image': imgFilesOut,
                     'Mask': mskFilesOut
                     })
                tableName = radiomicsTableRef + "_" + str(IDFind) + ".csv"
                outputPath = radiomcisFolder + "\\" + tableName
                Pd_Funs.SaveDF(
                    outPath=outputPath,
                    pdIn=outDf,
                    header=True,
                    index=False
                )

                # record path
                overallDict[radiomicsTableRef].append(outputPath.replace('/', '\\'))

        # output dict
        ## create folder
        outOcerallPath = searchDir + "//RadiomicsTable2D"
        Save_Load_File.checkCreateDir(path=(outOcerallPath))

        ## output
        outOverallTablePath = outOcerallPath + "//Radiomics2DOverall.csv"
        Pd_Funs.SaveDF(
            outPath=outOverallTablePath,
            pdIn=pandas.DataFrame(overallDict),
            header=True,
            index=False
        )


    '''
    ##############################################################################
    # Calculate area
    ##############################################################################
    '''
    def ChooseOpenDirAC(self):
        # Open folder
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadDirPathACTxt_E2SJZ.setPlainText(dirname)

    def AreaCalculation(self):
        # Inputs
        inMskDir = self.ui.loadDirPathACTxt_E2SJZ.toPlainText()
        searchFolderStrLst = Preprocess_Mask.StrToLst(self.ui.searchFolderStrsACTxt_E2SJZ.toPlainText())["listOut"]
        searchFileStrLst = Preprocess_Mask.StrToLst(self.ui.searchFileStrsACTxt_E2SJZ.toPlainText())["listOut"]
        searchFileRefMaskStrLst = Preprocess_Mask.StrToLst(self.ui.searchFileReMskStrsACTxt_E2SJZ.toPlainText())[
            "listOut"]

        autoLumenHU = self.ui.autoLumenHUAC_CB_E2SJZ.isChecked()
        lumenMin = int(self.ui.lumenMinACTxt_E2SJZ.toPlainText())
        lumenMax = int(self.ui.lumenMaxACTxt_E2SJZ.toPlainText())
        CaMin = int(self.ui.CaMinACTxt_E2SJZ.toPlainText())
        CaMax = int(self.ui.CaMaxACTxt_E2SJZ.toPlainText())
        IAPMin = int(self.ui.IAPMinACTxt_E2SJZ.toPlainText())
        IAPMax = int(self.ui.IAPMaxACTxt_E2SJZ.toPlainText())
        LAPMin = int(self.ui.LAPMinACTxt_E2SJZ.toPlainText())
        LAPMax = int(self.ui.LAPMaxACTxt_E2SJZ.toPlainText())

        # Search all files
        for folder in searchFolderStrLst:
            for i in range(len(searchFileStrLst)):
                # file and slice
                file = searchFileStrLst[i]
                fileRef = searchFileRefMaskStrLst[i]

                # find all files
                allFiles = Save_Load_File.ReturnFilesFullPath(
                    dirPath=inMskDir,
                    fileRef=file,
                    folderSearch=folder,
                    traverse=True
                )

                # update message
                self.UpdateMsgLog(
                    msg="Find files:\n{}".format(allFiles)
                )

                # output
                for imgFile in allFiles:
                    # file index
                    fileNameIndex = imgFile.index(file)

                    # ref file name
                    if fileRef == 'none' or fileRef == 'None':
                        mskFilePath = None
                    else:
                        mskFilePath = imgFile[:fileNameIndex] + fileRef + ".nii.gz"

                    # output folder
                    outFolderPath = imgFile[:fileNameIndex] + fileRef + '_AC'

                    # get lumen HU range
                    if autoLumenHU:
                        lumenHU = Post_Image_Process_Functions.GetHURange(imgPath=imgFile,
                                                                            mskPath=mskFilePath,
                                                                            range=50)
                        # give an upper & lower bound!!! 20%
                        lumenMin = int(int(lumenHU[0]) * 0.79)
                        lumenMax = int(int(lumenHU[1]) * 1.23)
                        self.UpdateMsgLog(msg='Auto Lumen Range: ' + str(lumenMin) + " - " + str(lumenMax))

                        # update
                        if CaMin > lumenMax: CaMin = lumenMax
                        if IAPMax > lumenMin: lumenMin = IAPMax


                    # Calculate different slice wise area in the ROI
                    Post_Image_Process_Functions.AreaCaculation(imgPath=imgFile,
                                                                mskPath=mskFilePath,
                                                                filterMethods=['boundary', 'boundary', 'boundary', 'boundary', 'boundary', 'boundary'],
                                                                thresStarts=[lumenMin, CaMin, IAPMin, LAPMin, lumenMin, LAPMin],
                                                                thresStops=[lumenMax, CaMax, IAPMax, LAPMax, CaMax, lumenMax],
                                                                columnRefs=['Lumen', 'Ca', 'IAP', 'LAP', 'LumCa', 'LumIAPLAP'],
                                                                outputFolder=outFolderPath,
                                                                outputRef='All')

                    # # lumen
                    # Post_Image_Process_Functions.AreaCaculation(imgPath=imgFile,
                    #                                        mskPath=mskFilePath,
                    #                                        filterMethod='boundary',
                    #                                        thresStart=[lumenMin],
                    #                                        thresStop=[lumenMax],
                    #                                        outputFolder=outFolderPath,
                    #                                        outputRef='Lumen')
                    #
                    # # Ca
                    # Post_Image_Process_Functions.AreaCaculation(imgPath=imgFile,
                    #                                        mskPath=mskFilePath,
                    #                                        filterMethod='boundary',
                    #                                        thresStart=[CaMin],
                    #                                        thresStop=[CaMax],
                    #                                        outputFolder=outFolderPath,
                    #                                        outputRef='Ca')
                    #
                    # # IAP
                    # Post_Image_Process_Functions.AreaCaculation(imgPath=imgFile,
                    #                                        mskPath=mskFilePath,
                    #                                        filterMethod='boundary',
                    #                                        thresStart=[IAPMin],
                    #                                        thresStop=[IAPMax],
                    #                                        outputFolder=outFolderPath,
                    #                                        outputRef='IAP')
                    #
                    # # LAP
                    # Post_Image_Process_Functions.AreaCaculation(imgPath=imgFile,
                    #                                        mskPath=mskFilePath,
                    #                                        filterMethod='boundary',
                    #                                        thresStart=[LAPMin],
                    #                                        thresStop=[LAPMax],
                    #                                        outputFolder=outFolderPath,
                    #                                        outputRef='LAP')
                    #
                    # # lumen + Ca
                    # Post_Image_Process_Functions.AreaCaculation(imgPath=imgFile,
                    #                                        mskPath=mskFilePath,
                    #                                        filterMethod='boundary',
                    #                                        thresStart=[lumenMin],
                    #                                        thresStop=[CaMax],
                    #                                        outputFolder=outFolderPath,
                    #                                        outputRef='LumCa')
                    #
                    # # Lumen IAP LAP
                    # Post_Image_Process_Functions.AreaCaculation(imgPath=imgFile,
                    #                                        mskPath=mskFilePath,
                    #                                        filterMethod='boundary',
                    #                                        thresStart=[LAPMin],
                    #                                        thresStop=[lumenMax],
                    #                                        outputFolder=outFolderPath,
                    #                                        outputRef='LumIAPLAP')

                    self.UpdateMsgLog(msg='Complete: ' + imgFile[fileNameIndex:])







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
        # self.outLog += disp
        print(msg)



