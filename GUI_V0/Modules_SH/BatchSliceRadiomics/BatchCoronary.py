import os
import sys
import pandas as pd
import re
import json
import pyparsing
import time
from datetime import datetime
import numpy

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
import Save_Load_File
import Preprocess_Mask
import Pd_Funs
# Import functions self-written
from Modules_YL.BatchCoronary import BranchDictionary
from Modules_YL.BatchCoronary import BatchCoronary


class BatchCoronary:
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI

            self.ui.LoadFolderPath_Btn_BPP.clicked.connect(lambda: self.ChooseWorkingDir())
            self.ui.ChooseCGExePathBtn_1_BPP.clicked.connect(lambda: self.ChooseCGExePath())
            self.ui.ChooseCPRExePathBtn_2_BPP.clicked.connect(lambda: self.ChooseCPRExePath())
            self.ui.ChooseSTLExePath_2_BPP.clicked.connect(lambda: self.ChooseSTLExePath())
            self.ui.ChooseLumenCorrectionPathBtn_BPP.clicked.connect(lambda: self.ChooseLumenCorretionPath())
            self.ui.ChooseOriVolumeCorrectionPathBtn_BPP.clicked.connect(lambda: self.ChooseOriVolumeCorretionPath())
            self.ui.ChooseAVCPathBtn_BPP.clicked.connect(lambda: self.ChooseAVCPath())
            self.ui.ChooseBloodPressureAndHeartRatePathBtn_BPP.clicked.connect(
                lambda: self.ChooseBloodPressureAndHeartRatePath())
            self.ui.MeshExePathBtn_BPP.clicked.connect(lambda: self.ChooseMeshExePath())
            self.ui.ChooseAUIPathBtn_BPP.clicked.connect(lambda: self.ChooseAUIExePath())
            self.ui.ChoosesetPathBtn_BPP.clicked.connect(lambda: self.ChooseSetCsvPath())
            self.ui.RunBtn_CPP.clicked.connect(lambda: self.mainFunction())
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            self.model = Hedys

        self.initProcess()

    # init process:
    def initProcess(self):
        if self.modelui:
            self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
        self.WorkingDir = None
        self.DCMDirList = []
        self.CTANewFilePathList = None
        self.CTANewPathList = None
        self.CTADirList = []  # store the cta location, include file name


        self.leftCenterlineJsonList = [] # centerline L json file positions
        self.rightCenterlineJsonList = [] # centerline R json file positions

        self.CTAPathList = []  # store the cta location, exclude file name
        self.XsecFixCTAPathList = []  # store the cta located in XsectionFix folder, include the file name
        self.OriVolCTAPathList = []  # store the cta located in OriVolume folder, include the file name
        self.CSVPathList = []  # store the csv directory path lists
        self.OriDataPathList = []
        self.BranchPathList = []  # store the absolute paths of branch folder list
        self.AortaPathList = []  # store the absolute paths of aorta mask file list
        self.AortaFixedPathList = []  # store the list of absolute paths list of aorta mask after lumen correction
        self.NewAortaPathList = []  # store the new absolute paths of aorta mask file list
        self.XsectionPathList = []  # store the absolute paths of Xsection folder list
        self.XsectionFixPathList = []  # store the absolute paths of XsectionFix folder list
        self.XsectionFixExtPathList = []  # store the absolute paths of XsectionFix extension folder list
        self.OriVolumePathList = []  # store the absolute paths of OriVolume folder list
        self.FinalMaskPathList = []  # store the absolute paths of final mask file path list
        self.StlFilePathList = []  # store the absolute paths of stl file path list
        self.ArVolCalPathList = []  # Murray's law results

        self.DictionaryPath = None  # store the absolute path of branch that required
        self.BatchDCMTablePath = None  # store the absolute path of branch that required
        self.JasonUpdateTablePath = None # store the absolute path of Jason update
        self.FilterMaskTable = []  # store the columns of filter mask single branch
        self.FilterMaskTablePath = None
        self.XsectionTable = []
        self.XsectionTablePath = None
        self.XsectionFixTable = []
        self.XsectionFixTablePath = None
        self.LCProcessPath = None
        self.AortaFixTablePath = None  # store the absolute path of Aorta fix table
        self.XsectionFixExtTable = []
        self.XsectionFixExtTablePath = None
        self.OriVolumeTable = []
        self.OriVolumeTablePath = None
        self.SSTable = []
        self.SSTablePath = None
        self.SGTable = []  #
        self.SGTablePath = None  # store the stl generate table path
        self.AVCTable = []  # Murray's Law batch
        self.AVCTablePath = None
        self.OCProcessPath = None
        self.OriVolumeFixTable = []
        self.OriVolumeFixTablePath = None
        self.CFD_MeshTable = []
        self.CFD_MeshTablePath = None
        self.CFD_STLcutTable = []
        self.CFD_STLcutTablePath = None
        self.CFD_STLmeshTable = []
        self.CFD_STLmeshTablePath = None
        self.CFD_FindFaceTable = []
        self.CFD_FindFaceTablePath = None
        self.CFD_setTablePath = None
        self.CFD_GenerateInTable = []
        self.CFD_GenerateInTablePath = None
        self.CFD_PostProgressTable = []
        self.CFD_PostProgressTablePath = None
        self.DataOutputTable = []
        self.DataOutputTablePath = None
        self.PostNpyTable = []
        self.PostNpyTablePath = None
        self.Map_ResultTable = []
        self.Map_ResultTablePath = None
        self.FFRCalculationTable = []
        self.FFRCalculationTablePath = None
        self.ParaviewTable = []
        self.ParaviewTablePath = None
        self.SaveVtuTable = []
        self.SaveVtuTablePath = None

        self.STLFolderList = []  # store the absolute paths of STL folder list
        self.MeshFolderList = []
        self.MeshFilePathList = []
        self.TableDir = None
        self.CTANewFilePathList = None

        # self.CPREXEPath = 'D:\CPP\CPR_NoCSV_16Jul21\CPRProject.exe' # *****need to change
        self.CPREXEPath = None  # *****need to change
        self.STLEXEPath = None  # ****need to change
        self.CGEXEPath = None

        # status that if certain process executed
        self.GTFlag = True  # generate table flag
        self.D2NFlag = True  # dicom to nifti flag
        self.CGFlag = True  # centerline generation flag
        self.FMFlag = True  # filter mask flag
        self.XsecFlag = True  # Xsection Flag
        self.LCFlag = True  # lumen correction flag
        self.ExtFlag = True  # Extension Flag
        self.XsecOriFlag = True  # Xsection Orivolume flag
        self.SSFlag = True  # stack segmentation flag
        self.M2SFlag = True  # mask 2 stl flag
        self.ArVolCalFlag = True  # area volume calculation
        self.CenterlineEFlag = True  # centerline extraction
        self.GenerateTFlag = True
        self.BranchDictFlag = True
        self.OriVolumeFixFlag = True
        self.getFFRresult = True
        self.MeshCut = True
        self.Mesh = True
        self.FindFace = True
        self.GenerateInput = True
        self.DataOutput = True
        self.CFD_PostProcessing = True
        self.MapResult = True
        self.FFRcalculation = True
        self.Paraview_processing = True
        self.SaveVTU = True
        self.VisualizationPyVista = True
        self.VTUdataExtraction = True
        self.VisualizationParaview = True

    def timmer(func):
        def warpper(self, *args, **kwargs):
            start_time = time.time()
            func(self)
            stop_time = time.time()
            print('{} run time is {}'.format(func.__name__, stop_time - start_time))

        return warpper

    def ChooseWorkingDir(self):
        dirname = Save_Load_File.OpenDirPathQt(dispMsg='Working Directory',
                                               fileObj=self.ui,
                                               qtObj=True
                                               )
        self.ui.LoadFolderPath_Txt_BPP.setPlainText(dirname)

    # used to choose CG exe path
    def ChooseCGExePath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load Centerline Generation Exe file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.CGExePath_Txt_BPP.setPlainText(filename)

    # used to choose Blood Pressure And Heart Rate path
    def ChooseBloodPressureAndHeartRatePath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load Centerline Generation Exe file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.BloodPressureAndHeartRatePath_Txt_BPP.setPlainText(filename)

    # used to choose Mesh exe path
    def ChooseMeshExePath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load Centerline Generation Exe file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.MeshExePath_Txt_BPP.setPlainText(filename)

    # used to choose AUI exe path
    def ChooseAUIExePath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load Centerline Generation Exe file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.AUIPath_Txt_BPP.setPlainText(filename)

    # used to choose set path
    def ChooseSetCsvPath(self):
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        self.ui.setPath_Txt_BPP.setPlainText(filename)

    # used to choose CPR exe path
    def ChooseCPRExePath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load CPR Exe file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.CPRExePath_Txt_BPP.setPlainText(filename)

    # used to choose STL generation exe path
    def ChooseSTLExePath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load STL Generate Exe file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.STLGExePath_Txt_BPP.setPlainText(filename)

    # used to choose lumen correction path
    def ChooseLumenCorretionPath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load Lumen Correction file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.LumenCorrectionPath_Txt_BPP.setPlainText(filename)

    # used to choose lumen correction path
    def ChooseOriVolumeCorretionPath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load OriVolume Correction file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.OriVolumePath_Txt_BPP.setPlainText(filename)

    # used to choose lumen correction path
    def ChooseAVCPath(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose Murray's law information directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.AVCPath_Txt_BPP.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose Murray's law information directory:\n{}".format(dirname))

    # if ui inserted, check check box status to pend if certain process shall be running
    def CheckCheckBoxStatus(self):
        if not self.ui.GenerateTable_CB_CPP.isChecked():
            self.GTFlag = False
        if not self.ui.DCM2Nifti_CB_CPP.isChecked():
            self.D2NFlag = False
        if not self.ui.CG_CB_CPP.isChecked():
            self.CGFlag = False
        if not self.ui.FM_CB_CPP.isChecked():
            self.FMFlag = False
        if not self.ui.Xsection_CB_CPP.isChecked():
            self.XsecFlag = False
        if not self.ui.LumenCorrection_CB_CPP.isChecked():
            self.LCFlag = False
        if not self.ui.Extension_CB_CPP.isChecked():
            self.ExtFlag = False
        self.XsecOriFlag = self.ui.XsecOriVolume_CB_CPP.isChecked()
        self.SSFlag = self.ui.SS_CB_CPP.isChecked()
        self.M2SFlag = self.ui.Mask2STL_CB_CPP.isChecked()
        self.ArVolCalFlag = self.ui.ArVolCal_CB_CPP.isChecked()
        self.CenterlineEFlag = self.ui.CenterlineE_CB_CPP.isChecked()
        self.UpdateJasonFlag = self.ui.UpdateJason_CB_CPP.isChecked()
        self.GenerateTFlag = self.ui.GenerateTable_CB_CPP.isChecked()
        self.BranchDictFlag = self.ui.BranchDict_CB_CPP.isChecked()
        self.OriVolumeFixFlag = self.ui.OriVolumeFix_CB_CPP.isChecked()
        self.getFFRresult = self.ui.getFFR_BPP.isChecked()
        self.getIFRresult = self.ui.getIFR_BPP.isChecked()
        self.MeshCut = self.ui.MeshCut_CB_CPP.isChecked()
        self.Mesh = self.ui.Mesh_CB_CPP.isChecked()
        self.FindFace = self.ui.FindFace_CB_CPP.isChecked()
        self.GenerateInput = self.ui.GenerateInput_CB_CPP.isChecked()
        self.DataOutput = self.ui.DataOutput_CB_CPP.isChecked()
        self.CFD_PostProcessing = self.ui.CFD_PostProcessing_CB_CPP.isChecked()
        self.MapResult = self.ui.MapResult_CB_CPP.isChecked()
        self.FFRcalculation = self.ui.FFRcalculation_CB_CPP.isChecked()
        self.Paraview_processing = self.ui.Paraviewprocessing_CB_CPP.isChecked()
        self.SaveVTU = self.ui.SaveVTU_CB_CPP.isChecked()
        self.VisualizationPyVista = self.ui.VisualizationPyVista_CB_CPP.isChecked()
        self.VTUdataExtraction = self.ui.VTUdataExtraction_CB_CPP.isChecked()
        self.VisualizationParaview = self.ui.VisualizationParaview_CB_CPP.isChecked()

    def ScanDCMDir(self):
        for root, dirs, files in os.walk(self.WorkingDir):
            for file in files:
                if file.endswith('.dcm') or file.endswith('.DCM') or (".DCM" in file):
                    self.DCMDirList.append(root)
                    break

        # CTA path
        self.CTADirList = [os.path.join(x, 'CTA\CTA.nii.gz') for x in self.DCMDirList]

    @staticmethod
    def CreateSingleFolder(path):
        try:
            os.mkdir(path)
        except Exception as e:
            pass

    # input path then create structured folder under this folder
    def CreateFolders(self, CasePath=None):
        CTADir = os.path.join(CasePath, 'CTA')
        if not os.path.exists(CTADir):
            os.mkdir(CTADir)

        PreProcPath = os.path.join(CasePath, 'Preproc')
        OriDataPath = os.path.join(PreProcPath, 'OriData')
        BranchPath = os.path.join(OriDataPath, 'Branches')
        CSVPath = os.path.join(PreProcPath, 'CSV')
        XsectionPath = os.path.join(PreProcPath, 'Xsection')
        XsectionFixPath = os.path.join(PreProcPath, 'XsectionFix')
        XsectionFixExtPath = os.path.join(PreProcPath, 'XsectionFixExt')
        OriVolPath = os.path.join(PreProcPath, 'OriVolume')

        CFDPath = os.path.join(CasePath, 'CFD')
        FFRPath = os.path.join(CasePath, 'FFR')
        STLPath = os.path.join(CFDPath, 'STL')
        ArVolCalPath = os.path.join(CFDPath, 'MurraysLaw')

        TablePath = os.path.join(CasePath, 'Table_Preproc')
        CFDTablePath = os.path.join(CasePath, 'Table_CFD')
        CFDResultPath = os.path.join(CFDPath, 'result')
        FFRResultPath = os.path.join(FFRPath, 'result')
        PostProcessingPath = os.path.join(CasePath, 'PostProgress')
        FFRPostProcessingPath = os.path.join(CasePath, 'FFRPostProgress')
        IFRPostProcessingPath = os.path.join(CasePath, 'IFRPostProgress')

        self.CreateSingleFolder(self.TableDir)
        self.CreateSingleFolder(PreProcPath)
        self.CreateSingleFolder(OriDataPath)
        self.CreateSingleFolder(BranchPath)
        self.CreateSingleFolder(OriVolPath)
        self.CreateSingleFolder(CSVPath)
        self.CreateSingleFolder(XsectionPath)
        self.CreateSingleFolder(XsectionFixPath)
        self.CreateSingleFolder(XsectionFixExtPath)
        self.CreateSingleFolder(CFDPath)
        self.CreateSingleFolder(FFRPath)
        self.CreateSingleFolder(CFDResultPath)
        self.CreateSingleFolder(FFRResultPath)
        self.CreateSingleFolder(STLPath)
        self.CreateSingleFolder(ArVolCalPath)
        self.CreateSingleFolder(TablePath)
        self.CreateSingleFolder(CFDTablePath)
        self.CreateSingleFolder(PostProcessingPath)
        self.CreateSingleFolder(FFRPostProcessingPath)
        self.CreateSingleFolder(IFRPostProcessingPath)

    # store the required path information as list
    def StoreListInformation(self):
        for path in self.DCMDirList:
            self.OriDataPathList.append(os.path.join(path, 'Preproc/OriData'))
            self.CSVPathList.append(os.path.join(path, 'Preproc/CSV'))
            self.BranchPathList.append(os.path.join(path, 'Preproc/OriData/Branches'))
            self.XsectionPathList.append(os.path.join(path, 'Preproc/Xsection'))
            self.XsectionFixPathList.append(os.path.join(path, 'Preproc/XsectionFix'))
            self.XsectionFixExtPathList.append(os.path.join(path, 'Preproc/XsectionFixExt'))
            self.OriVolumePathList.append(os.path.join(path, 'Preproc/OriVolume'))
            self.STLFolderList.append(os.path.join(path, 'CFD/STL'))
            self.ArVolCalPathList.append(os.path.join(path, 'CFD/MurraysLaw'))
            self.MeshFolderList.append(os.path.join(path, 'CFD/Mesh'))
            pass

        # store the final mask path using orivolume path list
        self.FinalMaskPathList = [os.path.join(x, 'OriVolumeCAVal.nii.gz') for x in self.OriVolumePathList]
        self.StlFilePathList = [os.path.join(x, 'Raw.stl') for x in self.STLFolderList]
        self.MeshFilePathList = [os.path.join(x, 'FluidMeshInit.nas') for x in self.MeshFolderList]
        # store the aorta path list
        self.AortaPathList = [os.path.join(x, 'AortaVal.nii.gz') for x in self.BranchPathList]
        # iteration of store Aorta mask after lumen correction
        self.AortaFixedPathList = [os.path.join(x, 'AortaFixVal.nii.gz') for x in self.XsectionFixPathList]

        # generate table paths
        self.DictionaryPath = os.path.join(self.TableDir, 'coronarySegments.json')
        self.FilterMaskTablePath = os.path.join(self.TableDir, 'FilterMask.csv')
        self.AortaFixTablePath = os.path.join(self.TableDir, 'AortaLCFix.csv')
        self.XsectionTablePath = os.path.join(self.TableDir, 'Xsection.csv')
        self.XsectionFixTablePath = os.path.join(self.TableDir, 'XsectionFix.csv')
        self.OriVolumeFixTablePath = os.path.join(self.TableDir, 'OriVolumeFix.csv')
        self.LCProcessPath = os.path.join(self.TableDir, 'LCProcess.csv')
        self.OCProcessPath = os.path.join(self.TableDir, 'OCProcess.csv')
        self.XsectionFixExtTablePath = os.path.join(self.TableDir, 'Extension.csv')
        self.OriVolumeTablePath = os.path.join(self.TableDir, 'XsectionOriVolume.csv')
        self.SSTablePath = os.path.join(self.TableDir, 'SS.csv')
        self.SGTablePath = os.path.join(self.TableDir, 'SG.csv')
        self.AVCTablePath = os.path.join(self.TableDir, 'MurraysLaw.csv')
        self.BatchDCMTablePath = os.path.join(self.TableDir, 'BatchDCM.csv')
        self.JasonUpdateTablePath = os.path.join(self.TableDir, 'JasonUpdate.csv')
        self.CFD_MeshTablePath = os.path.join(self.TableDir, 'CFD_Mesh.csv')
        self.CFD_STLcutTablePath = os.path.join(self.TableDir, 'CFD_STLcut.csv')
        self.CFD_STLmeshTablePath = os.path.join(self.TableDir, 'CFD_STLmesh.csv')
        self.CFD_FindFaceTablePath = os.path.join(self.TableDir, 'CFD_FindFace.csv')
        self.CFD_setTablePath = os.path.join(self.TableDir, 'set.csv')
        self.CFD_GenerateInTablePath = os.path.join(self.TableDir, 'CFD_GenerateIn.csv')
        self.CFD_PostProgressTablePath = os.path.join(self.TableDir, 'CFD_PostProgress.csv')
        self.DataOutputTablePath = os.path.join(self.TableDir, 'CFD_DataOutput.csv')
        self.PostNpyTablePath = os.path.join(self.TableDir, 'CFD_PostNpy.csv')
        self.Map_ResultTablePath = os.path.join(self.TableDir, 'CFD_Map_Result.csv')
        self.FFRCalculationTablePath = os.path.join(self.TableDir, 'CFD_FFRCalculation.csv')
        self.ParaviewTablePath = os.path.join(self.TableDir, 'CFD_Paraview.csv')
        self.SaveVtuTablePath = os.path.join(self.TableDir, 'CFD_SaveVtu.csv')

    @staticmethod
    # generate windows command line
    def CopyCommand(source=None, dst=None):

        import shutil

        source = source.replace('/', '\\')
        dst = dst.replace('/', '\\')

        shutil.copy(source, dst)

        cmd = 'copy {} {}'.format(source, dst)
        cmd = cmd.replace('/', '\\')
        return cmd

    @staticmethod
    def WriteAortaFixCsv(dstPath=None):
        header = ['3D Connectivity Filter', 'Morphological Process']
        first_col = ['first', '1']
        second_col = ['3D', 'No', 'Closing', '6', '0', '2000']
        csv = []
        csv.append(first_col)
        csv.append(second_col)
        df = pd.DataFrame(data=csv, columns=None, index=None)
        df = df.T
        df.columns = header
        df.to_csv(dstPath, index=False)

    # generate table used for batch generate nifti
    def GenerateCTATable(self):
        CSVIndex = ['DICOMDirectoryPath', 'OutputPath']
        Data = [self.DCMDirList, self.CTADirList]
        print(self.DCMDirList)

        df = pd.DataFrame(data=Data, columns=None, index=None)
        df = df.T
        df.columns = CSVIndex

        df.to_csv(self.BatchDCMTablePath, index=False, mode='w')

    def BatchDCM2Nifti(self):
        self.model.convertDataType.BatchDICOMconvertNIFTI(tablePath=self.BatchDCMTablePath, refImg=False)

    # Move CTA file to specified folder, then generate centerline and mask
    def BatchCenterlineGen(self):
        df = pd.DataFrame(data=self.OriDataPathList,columns=['FolderPath'])

        BatchCCTablePath = os.path.join(self.TableDir, 'BatchCenterlineGeneration.csv')
        df.to_csv(BatchCCTablePath, index=False)

        self.model.CenterlineGeneration.InitCenterlineEx(exePath=self.CGEXEPath, TablePath=BatchCCTablePath)
        self.model.CenterlineGeneration.BatchViaExcel()

    # copy centerline json file to specified folder
    @timmer
    def CopyCenterlineJson(self):
        leftOldList = [os.path.join(self.OriDataPathList[i], 'L_coronary_centerline_network.json')
                       for i in range(len(self.OriDataPathList))]
        rightOldList = [os.path.join(self.OriDataPathList[i], 'R_coronary_centerline_network.json')
                        for i in range(len(self.OriDataPathList))]
        leftOldListT = [os.path.join(self.OriDataPathList[i], 'L_coronary_centerline_network.json.txt')
                        for i in range(len(self.OriDataPathList))]
        rightOldListT = [os.path.join(self.OriDataPathList[i], 'R_coronary_centerline_network.json.txt')
                         for i in range(len(self.OriDataPathList))]

        leftList = [z.replace('OriData', 'CSV') for z in self.OriDataPathList]
        rightList = [z.replace('OriData', 'CSV') for z in self.OriDataPathList]

        # new json file positions
        self.leftCenterlineJsonList = [os.path.join(path, 'L_coronary_centerline_network.json') for path in leftList]
        self.rightCenterlineJsonList = [os.path.join(path, 'R_coronary_centerline_network.json') for path in rightList]

        for i in range(len(self.OriDataPathList)):
            try:
                cmd1 = self.CopyCommand(leftOldList[i], leftList[i])
                print(cmd1)
            except:
                print("!!!FAIL copy: \n{} \n{}".format(leftOldList[i], leftList[i]))

            try:
                cmd2 = self.CopyCommand(rightOldList[i], rightList[i])
                print(cmd2)
            except:
                print("!!!FAIL copy: \n{} \n{}".format(rightOldList[i], rightList[i]))

            try:
                cmd3 = self.CopyCommand(leftOldListT[i], leftList[i])
                print(cmd3)
            except:
                print("!!!FAIL copy: \n{} \n{}".format(leftOldListT[i], leftList[i]))

            try:
                cmd4 = self.CopyCommand(rightOldListT[i], rightList[i])
                print(cmd4)
            except:
                print("!!!FAIL copy: \n{} \n{}".format(rightOldListT[i], rightList[i]))

            # os.system(cmd1)

            # os.system(cmd2)

            # os.system(cmd3)

            # os.system(cmd4)

    # copy cta file from cta folder to branches folder
    def CopyCTA(self):
        self.CTANewFilePathList = [y.replace('\\CTA\\', '\\PreProc\\OriData\\', 1) for y in self.CTADirList]
        self.CTANewPathList = [y.replace('CTA\\CTA.nii.gz', 'PreProc\\OriData', 1) for y in self.CTADirList]

        # copy cta.nii.gz to Preproc/OriData folder
        for i in range(len(self.CTANewFilePathList)):
            cmd = self.CopyCommand(self.CTADirList[i], self.CTANewPathList[i])
            print(cmd)
            # os.system(cmd)

        print('self.CTANewFilePathList', self.CTANewFilePathList)

        self.BranchPathList = [x.replace('\\CTA.nii.gz', '\\Branches') for x in self.CTANewFilePathList]
        self.CTAPathList = [x.replace('\\CTA\\', '\\Preproc\\OriData\\Branches\\', 1) for x in self.CTADirList]

        for dstCTAPath in self.CTAPathList:
            if not os.path.exists(dstCTAPath):
                cmd = self.CopyCommand(self.CTADirList[self.CTAPathList.index(dstCTAPath)], dstCTAPath)
                # os.system(cmd)
            else:
                pass
        # copy cta file from cta folder to XsectionFix folder
        self.XsecFixCTAPathList = [y.replace('\\CTA\\', '\\Preproc\\XsectionFixExt\\', 1) for y in self.CTADirList]
        for dstFixCTAPath in self.XsecFixCTAPathList:
            if not os.path.exists(dstFixCTAPath):
                cmd = self.CopyCommand(self.CTADirList[self.XsecFixCTAPathList.index(dstFixCTAPath)], dstFixCTAPath)
                # os.system(cmd)
            else:
                pass

        # copy cta file from cta folder to OriVolume folder
        self.OriVolCTAPathList = [z.replace('\\CTA\\', '\\Preproc\\OriVolume\\', 1) for z in self.CTADirList]
        for dstOriVolCTAPath in self.OriVolCTAPathList:
            if not os.path.exists(dstOriVolCTAPath):
                cmd = self.CopyCommand(self.CTADirList[self.OriVolCTAPathList.index(dstOriVolCTAPath)],
                                       dstOriVolCTAPath)
                # os.system(cmd)
            else:
                pass

    # copy aorta file which extracted from final label file to Orivolume folder
    def CopyAorta2OriVolumeFolder(self):
        # self.AortaPathList = [os.path.join(x, 'AortaVal.nii.gz') for x in self.BranchPathList]
        # self.NewAortaPathList = [x.replace('OriData/Branches', 'OriVolume') for x in self.AortaPathList]
        self.AortaPathList = [os.path.join(x, 'AortaFixVal.nii.gz') for x in self.XsecFixCTAPathList]
        self.AortaPathList = [x.replace('XsectionFixExt\CTA.nii.gz', 'XsectionFix') for x in self.AortaPathList]
        self.NewAortaPathList = [x.replace('XsectionFix', 'OriVolume') for x in self.AortaPathList]
        print(self.AortaPathList)
        print(self.NewAortaPathList)
        for oldPath, newPath in zip(self.AortaPathList, self.NewAortaPathList):
            if not os.path.exists(newPath):
                cmd = self.CopyCommand(oldPath, newPath)
                print(cmd)
                os.system(cmd)

    # input the root directory, extract all the centerlines into the same folder with json files
    def BatchExtractCenterline(self):
        # ExtractionClass = self.model.CenterlineExtraction()
        # ExtractionClass = Centerline_ExtractionMain.Centerline_Extraction()
        for dir in self.CSVPathList:
            print("extract centerline in: {}".format(dir))
            # ExtractionClass.BatchCenterlineProcessing(dir=dir)
            self.model.CenterlineExtraction.BatchCenterlineProcessing(dir=dir)

    # generate table used for batch Jason update
    def GenerateJsonUpdateTable(self):
        # heading
        CSVIndex = ["CSVDirectory", "JsonFile", "UpdateType"]

        # check csv and left and right same length
        if not ((len(self.CSVPathList) == len(self.leftCenterlineJsonList))
                and (len(self.CSVPathList) == len(self.rightCenterlineJsonList))):

            print('!!!Warning Jason file list is not the same length as the CSV folder list')

        CSVFolderLst = []
        JsonFileLst = []
        UpdateTypeLst = []

        for i in range(len(self.CSVPathList)):
            # append results
            # left
            CSVFolderLst.append(self.CSVPathList[i])
            JsonFileLst.append(self.leftCenterlineJsonList[i])
            UpdateTypeLst.append("Replace with CSV")
            # right
            CSVFolderLst.append(self.CSVPathList[i])
            JsonFileLst.append(self.rightCenterlineJsonList[i])
            UpdateTypeLst.append("Replace with CSV")

        Data = [CSVFolderLst, JsonFileLst, UpdateTypeLst]

        # print to check results
        for j in range(numpy.min([10, len(self.CSVPathList)])):
            print(CSVFolderLst[j], JsonFileLst[j], UpdateTypeLst[j])

        df = pd.DataFrame(data=Data, columns=None, index=None)
        df = df.T
        df.columns = CSVIndex

        df.to_csv(self.JasonUpdateTablePath, index=False, mode='w')

    # Batch Jason Update
    def BatchJsonUpdate(self):
        self.model.CenterlineJSONUpdate.BatchUpdateJson(tablePath=self.JasonUpdateTablePath)

    # input path, join path with json file, return a list include l and r json file path
    @staticmethod
    def ReturnJsonList(CSVPath=None):
        tempJsonList = []
        tempJsonPath1 = os.path.join(CSVPath, 'L_coronary_centerline_network.json')
        tempJsonPath2 = os.path.join(CSVPath, 'R_coronary_centerline_network.json')
        tempJsonList.append(tempJsonPath1)
        tempJsonList.append(tempJsonPath2)

        return tempJsonList

    # write branch processing dictionary
    def CheckWriteDict(self):
        # input list
        branchLst = []
        if self.ui.LM_CB_CPP.isChecked(): branchLst.append("LM")
        if self.ui.IMB_CB_CPP.isChecked(): branchLst.append("IMB")
        if self.ui.pLAD_CB_CPP.isChecked(): branchLst.append("pLAD")
        if self.ui.pLCX_CB_CPP.isChecked(): branchLst.append("pCx")
        if self.ui.mLAD_CB_CPP.isChecked(): branchLst.append("mLAD")
        if self.ui.dLAD_CB_CPP.isChecked(): branchLst.append("dLAD")
        if self.ui.D1_CB_CPP.isChecked(): branchLst.append("D1")
        if self.ui.D2_CB_CPP.isChecked(): branchLst.append("D2")
        if self.ui.mLCX_CB_CPP.isChecked(): branchLst.append("LCx")
        if self.ui.dLCX_CB_CPP.isChecked(): branchLst.append("L-PDA")
        if self.ui.OM1_CB_CPP.isChecked(): branchLst.append("OM1")
        if self.ui.OM2_CB_CPP.isChecked(): branchLst.append("OM2")
        if self.ui.pRCA_CB_CPP.isChecked(): branchLst.append("pRCA")
        if self.ui.mRCA_CB_CPP.isChecked(): branchLst.append("mRCA")
        if self.ui.dRCA_CB_CPP.isChecked(): branchLst.append("dRCA")
        if self.ui.V_CB_CPP.isChecked(): branchLst.append("V")
        if self.ui.AM_CB_CPP.isChecked(): branchLst.append("AM")
        if self.ui.CB_CB_CPP.isChecked(): branchLst.append("CB")

        # ignore coordinate list
        ignoreCoordsLst = Preprocess_Mask.StrToLst(strIn=self.ui.ignoreCheck_Txt_BPP.toPlainText())["listOut"]

        if not branchLst:  # empty list
            branchLst = ['LM', "pLAD", "pCx", "pRCA", "mRCA"]
            self.UpdateMsgLog("No Selection in branches use standard five branches:\n{}".format(branchLst))
        else:
            self.UpdateMsgLog("Selected branches:\n{}".format(branchLst))

        BranchDictionary.WriteDic(Outpath=self.DictionaryPath, branchLst=branchLst)
        for CSVPath in self.CSVPathList:
            # validate which branch can be used for each case
            tempJsonList = self.ReturnJsonList(CSVPath)
            UseJsonPath = os.path.join(CSVPath, 'coronarySegmentsUse.json')
            BranchDictionary.ValidateUse(dicPath=self.DictionaryPath, jsonList=tempJsonList, outputPath=UseJsonPath,
                                         ignoreCoordsLst=ignoreCoordsLst)

    # create Filter Mask Object and batch process
    def GenerateTable(self):
        # define table column titles
        FM_Head = ['MaskPath', 'MaskVal', 'NewMaskVal', 'OutputFolder', 'FileNameRef']

        Xsection_Head = ['inputDir', 'inputCSVDir', 'outputDir', 'outputCSVDir', 'resampleDepth', 'CPRAngle', 'cpus',
                         'casePath', 'EXEPath']

        Case_Head = ['Interpolation', 'OutCSV', 'inputImagePath', 'inputCSVPath', 'outputImagePath', 'outputCSVPath']

        XsecFix_Head = ['Image Path', 'Mask Path', 'Process Path', 'Fill Original Value', 'Output Directory',
                        'Output Name']

        Extension_Head = ['Input Mask Path', 'Output Mask Path', 'First Automation', 'First Direction',
                          'First Use Circle', 'First Slice Start', 'First Slice Stop', 'First Reference Slice',
                          'First Reference Mask Depth', 'First Extension Total Slices', 'Second Extension',
                          'Second Automation', 'Second Direction', 'Second Use Circle', 'Second Slice Start',
                          'Second Slice Stop', 'Second Reference Slice', 'Second Reference Mask Depth',
                          'Second Extension Total Slices']

        OriVolume_Head = ['LoadFolder', 'RefImgName', 'XsecImgName', 'OriVolCSV', 'FillDistance', 'Processors',
                          'OutputFolder', 'OutImgName', 'Interpolation']

        XsecFixOri_Head = ['Image Path', 'Mask Path', 'Process Path', 'Fill Original Value', 'Output Directory',
                           'Output Name']

        SS_Head = ['RefImgPath', 'LoadFolder', 'RefSegmentationName', 'ThresholdValues', 'NewValues',
                   'OutputFolder', 'OutRefName']

        SG_Head = ['EXEPath', 'InputFilePath', 'OutputFilePath']

        AVCParam_Head = ['Total Inflow', 'Threshold', 'Step', 'Output Folder', 'Exponential', 'Multiple']

        AVCBranM_Head = ['Name Reference', 'Branch Label', 'Mask Path', 'Start Slice', 'Finish Slice', 'Mask Label',
                         'Area Choice', 'Reference File']

        AVCBatch_Head = ["Branch Map Path", "Parameters Path"]

        CFD_Mesh_Head = ["InputFolder", "OutputFolder", "MeshCut", "Mesh", "MeshExe", "FindFace", "Tolerance(FindFace)",
                         "Set(FindFace)", "GenerateInput", "AUIPath", "TimeFunction(GenerateInput)"]

        CFD_STLcut_Head = ["MeshCut", "InputStl(MeshCut)", "OutputFolder"]

        CFD_STLmesh_Head = ["Mesh", "InputStl(Mesh)", "MeshExe", "OutputFolder"]

        CFD_FindFace_Head = ["FindFace", "InputNas(FindFace)", "OutputFolder", "Set(FindFace)", "Tolerance(FindFace)"]

        CFD_GenerateIn_Head = ["GenerateInput", "InputNas(GenerateInput)", "OutputFolder",
                               "TimeFunction(GenerateInput)", "EndingArea(GenerateInput)", "AUIPath"]

        CFD_Postprogress_Head = ["OutputFolder", "DataOutput", "Idb Path(DataOutput)", "Por Path(DataOutput)",
                                 "AUI Path(DataOutput)", "TimeStart(DataOutput)", "TimeStop(DataOutput)",
                                 "CFD Post-processing", "TimeStart(CFD Post-processing)",
                                 "TimeStop(CFD Post-processing)", "Mask Path", "Extract Skin", "Value Exclusion",
                                 "Input Directory", "Input NPY Path", "Leaf Size", "CPU", "Filter Zero",
                                 "Match Ball Radius", "Output Directory", "Extract Skin", "Output Image File",
                                 "FFRCalculation", "InputMask(FFRCalculation)", "Keep Values(FFRCalculation)",
                                 "Paraview_processing", "Savevtu", "nasPath(Savevtu)", "ndInterestDictPath(Savevtu)",
                                 "ParamsNpyPath(Savevtu)", "savevtuName(Savevtu)", "addFFR(Savevtu)",
                                 "savesingle(Savevtu)", "TAPnpyPath(Savevtu)", "FFRValuePath(Savevtu)",
                                 "FFRarrayName(Savevtu)", "FFRSavename(Savevtu)", "ParamsPath(Savevtu)",
                                 "pvdName(Savevtu)", "SavePVD(Savevtu)", "SaveFFRvtu(Savevtu)", "Savevtufile(Savevtu)"]

        CFD_DataOutput_Head = ["OutputFolder", "DataOutput", "Idb Path(DataOutput)", "Por Path(DataOutput)",
                               "AUI Path(DataOutput)", "TimeStart(DataOutput)", "TimeStop(DataOutput)"]

        CFD_PostNpy_Head = ["OutputFolder", "CFD Post-processing", "InputFolder(CFD Post-processing)",
                            "TimeStart(CFD Post-processing)", "TimeStop(CFD Post-processing)"]

        CFD_Map_Result_Head = ["Mask Path", "Extract Skin", "Value Exclusion", "Input Directory", "Input NPY Path",
                               "Leaf Size", "CPU", "Filter Zero", "Match Ball Radius", "Output Directory",
                               "Extract Skin", "Output Image File"]

        CFD_FFRCalculation_Head = ["OutputFolder", "FFRCalculation", "InputMask(FFRCalculation)",
                                   "Keep Values(FFRCalculation)", "Load Value image for FFR Folder(FFRCalculation)"]

        CFD_Paraview_Head = ["OutputFolder", "Paraview_processing", "Nodecoo(Paraview_processing)",
                             "TetraElmnt(Paraview_processing)", "HexElmnt(Paraview_processing)",
                             "Times(Paraview_processing)", "ParamsDic(Paraview_processing)",
                             "PostResults(Paraview_processing)", "WSSParamDict(Paraview_processing)",
                             "WssDict(Paraview_processing)", "FFRIQRAverageValue(Paraview_processing)"]

        CFD_Savevtu_Head = ["OutputFolder", "Savevtu", "nasPath(Savevtu)", "ndInterestDictPath(Savevtu)",
                            "ParamsNpyPath(Savevtu)", "savevtuName(Savevtu)", "addFFR(Savevtu)", "savesingle(Savevtu)",
                            "TAPnpyPath(Savevtu)", "FFRValuePath(Savevtu)", "FFRarrayName(Savevtu)",
                            "FFRSavename(Savevtu)", "ParamsPath(Savevtu)", "pvdName(Savevtu)", "SavePVD(Savevtu)",
                            "SaveFFRvtu(Savevtu)", "Savevtufile(Savevtu)"]

        ## parameters
        resampleDepth = '0.1'
        CPRAngle = '0'
        cpus = '2'
        fillDistance = '0.8'
        processors = '4'
        interpolation = '1'
        # Murray's Law
        startSlc_AVC = '0'
        stopSlc_AVC = '10000'
        areaChc_AVC = 'averageArea'
        refFile_RCA_AVC = self.ui.AVCPath_Txt_BPP.toPlainText() + '/RCA.csv'
        # aorOut_AVC = self.ui.AVCPath_Txt_BPP.toPlainText() + '/Aor_in.txt'
        # aorIn_AVC = self.ui.AVCPath_Txt_BPP.toPlainText() + '/Aor_out.txt'
        # aorOutFFR_AVC = self.ui.AVCPath_Txt_BPP.toPlainText() + '/Aor_outFFR.txt'
        refFile_LCA_AVC = self.ui.AVCPath_Txt_BPP.toPlainText() + '/LCA.csv'
        refFile_N_AVC = 'N'
        totInflow_AVC = "3261.670409"
        diffThres_AVC = "0.01"
        step_AVC = "126"
        exo_AVC = "2.6"
        mul_AVC = "1,4.1667"
        # CFD_Mesh
        Tolerance_FindFace_Mesh = 45
        MeshExe = self.ui.MeshExePath_Txt_BPP.toPlainText()
        AUIExe = self.ui.AUIPath_Txt_BPP.toPlainText()
        # CFD_Postprogress
        TimeStart_DataOutput = 4.5
        TimeStop_DataOutput = 5.4
        TimeStart_IFR = 5.2
        TimeStop_IFR = 5.4
        FFR_KeepValue = 4

        for CSVPath in self.CSVPathList:
            loopIndex = self.CSVPathList.index(CSVPath)
            tmpMaskPath = os.path.join(self.OriDataPathList[loopIndex], 'sc_labelled_coronary_segment.nii.gz')
            AortaMaskPath = os.path.join(self.OriDataPathList[loopIndex], 'sc_final_labelmap2.nii.gz')
            tmpOutputPath = self.BranchPathList[loopIndex]
            # initialize case table
            tempCaseTable = []
            tempBranchList = []
            tempBranchLblist = []
            AVCBranMTable = []  # Murray's Law batch
            DCMDirPath = self.DCMDirList[loopIndex]

            # # validate which branch can be used for each case
            # tempJsonList = self.ReturnJsonList(CSVPath)
            UseJsonPath = os.path.join(CSVPath, 'coronarySegmentsUse.json')
            # BranchDictionary.ValidateUse(dicPath=self.DictionaryPath, jsonList=tempJsonList, outputPath=UseJsonPath)

            ## Aorta
            # filter aorta which label value is 4
            self.FilterMaskTable.append([AortaMaskPath, '4', '1', tmpOutputPath, 'Aorta'])
            # Aorta lumen correction
            tmpAortaXsecFixColumn = [self.AortaPathList[loopIndex], self.AortaPathList[loopIndex],
                                     self.AortaFixTablePath, 'Yes', self.XsectionFixPathList[loopIndex], 'AortaFix']
            self.XsectionFixTable.append(tmpAortaXsecFixColumn)
            # stack segmentation
            tempBranchList.append('AortaFixVal.nii.gz')
            tempBranchLblist.append(str(4))

            # validate the existence of json file first
            with open(UseJsonPath) as f:
                case = json.load(f)

            for branch in case:
                if branch['use']:

                    # store used branch for later Stack Segmentation use
                    tempBranchList.append(branch['original_volume_mask_fix'].replace('.nii.gz', 'Val.nii.gz'))
                    tempBranchLblist.append(str(branch['label'][0]))

                    # filter mask table
                    tempFMColumn = [tmpMaskPath, str(branch['label'][0]), '1', tmpOutputPath, branch['original_branch']]
                    self.FilterMaskTable.append(tempFMColumn)

                    # generate Xsection table columns for branches for ease case
                    tempCaseColumn1 = ['1',
                                       '0',
                                       'CTA.nii.gz',
                                       branch['original_csv'],
                                       # os.path.join(self.CSVPathList[loopIndex], branch['original_csv']),
                                       branch['cross_section_image_NN'],
                                       branch['3D_csv']]
                    tempCaseColumn2 = ['1',
                                       '1',
                                       branch['original_branch'] + 'Val.nii.gz',
                                       branch['original_csv'],
                                       # os.path.join(self.CSVPathList[loopIndex], branch['original_csv']),
                                       branch['cross_section_mask_NN'], branch['3D_csv']]

                    tempCaseTable.append(tempCaseColumn1)
                    tempCaseTable.append(tempCaseColumn2)

                    # insert columns into xsection fix table
                    XsecCTAPath = os.path.join(self.XsectionPathList[loopIndex], branch['cross_section_image_NN'])
                    XsecMaskPath = os.path.join(self.XsectionPathList[loopIndex], branch['cross_section_mask_NN'])
                    tmpXsecFixColumn = [XsecCTAPath, XsecMaskPath, self.LCProcessPath, 'Yes',
                                        self.XsectionFixPathList[loopIndex],
                                        branch['cross_section_mask_fix'].replace('Val.nii.gz', '')]

                    self.XsectionFixTable.append(tmpXsecFixColumn)

                    # insert columns into extension table
                    tmpExtInputMaskPath = os.path.join(self.XsectionFixPathList[loopIndex],
                                                       branch['cross_section_mask_fix'])
                    tmpExtOutputMaskPath = os.path.join(self.XsectionFixExtPathList[loopIndex],
                                                        branch['cross_section_mask_fix_extension'])
                    tmpExtColumn = [tmpExtInputMaskPath, tmpExtOutputMaskPath, 'Yes', 'X', 'No', '0', '0', '0', '46',
                                    '169', 'Yes', 'Yes', 'X', 'No', '0', '0', '0', '66', '169']
                    self.XsectionFixExtTable.append(tmpExtColumn)

                    tmpOriColumn = [self.XsectionFixExtPathList[loopIndex],
                                    'CTA.nii.gz',
                                    branch['cross_section_mask_fix_extension'],
                                    os.path.join(self.XsectionPathList[loopIndex], branch['3D_csv']),
                                    fillDistance,
                                    processors,
                                    self.OriVolumePathList[loopIndex],
                                    branch['original_volume_mask_fix'],
                                    interpolation]
                    self.OriVolumeTable.append(tmpOriColumn)

                    ## area volume calculation branch map
                    refFile_AVC = refFile_N_AVC
                    if branch['branch_name'] == 'pRCA':
                        refFile_AVC = refFile_RCA_AVC
                    elif branch['branch_name'] == 'LM':
                        refFile_AVC = refFile_LCA_AVC

                    tmpAVCBranchMCol = [
                        branch['branch_name'],
                        branch["branch_label"],
                        tmpExtInputMaskPath,
                        startSlc_AVC,
                        stopSlc_AVC,
                        str(branch['label'][0]),
                        areaChc_AVC,
                        refFile_AVC
                    ]
                    AVCBranMTable.append(tmpAVCBranchMCol)

                    # insert columns into OriVolume fix table
                    OriVCTAPath = os.path.join(self.OriVolumePathList[loopIndex], "CTA.nii.gz")
                    OriVMaskPath = os.path.join(self.OriVolumePathList[loopIndex], branch['original_volume_mask_fix'])
                    tmpOriVFixColumn = [OriVCTAPath,
                                        OriVMaskPath,
                                        self.OCProcessPath,
                                        'Yes',
                                        self.OriVolumePathList[loopIndex],
                                        branch['original_volume_mask_fix'].replace('.nii.gz', '')]

                    self.OriVolumeFixTable.append(tmpOriVFixColumn)

                else:
                    continue

            ## create centerline to xsection two tables
            # case table csv file for each case
            caseFilePath = os.path.join(CSVPath, 'case.csv')
            case_df = pd.DataFrame(tempCaseTable, columns=Case_Head)
            case_df.to_csv(caseFilePath, index=None)

            # add record to overall Xsection table
            self.XsectionTable.append([self.BranchPathList[loopIndex], CSVPath, self.XsectionPathList[loopIndex],
                                       self.XsectionPathList[loopIndex], resampleDepth, CPRAngle, cpus,
                                       caseFilePath, self.CPREXEPath])

            # create Stack Segmentation Column for each case
            tmpSSColumn = [os.path.join(self.OriDataPathList[loopIndex], 'CTA.nii.gz'),
                           self.OriVolumePathList[loopIndex],
                           ','.join(tempBranchList),
                           '0',
                           ','.join(tempBranchLblist),
                           self.OriVolumePathList[loopIndex],
                           'OriVolumeCA']
            self.SSTable.append(tmpSSColumn)

            # mask to stl table
            tmpSGColumn = [self.STLEXEPath, self.FinalMaskPathList[loopIndex], self.StlFilePathList[loopIndex]]
            self.SGTable.append(tmpSGColumn)

            # CFD table
            tmpCFDColumn = [self.StlFilePathList[loopIndex], os.path.join(DCMDirPath, 'CFD'), True, True, MeshExe,
                            True, Tolerance_FindFace_Mesh, self.CFD_setTablePath, True, AUIExe,
                            os.path.join(self.ArVolCalPathList[loopIndex], 'Flow_1_0')]
            tmpFFRColumn = [self.MeshFilePathList[loopIndex], os.path.join(DCMDirPath, 'FFR'), False, False, MeshExe,
                            True, Tolerance_FindFace_Mesh, self.CFD_setTablePath, True, AUIExe,
                            os.path.join(self.ArVolCalPathList[loopIndex], 'Flow_4_1667')]
            self.CFD_MeshTable.append(tmpCFDColumn)
            if self.getFFRresult:
                self.CFD_MeshTable.append(tmpFFRColumn)

            # STLcut table
            tmpSTLcutColumn = [True, os.path.join(DCMDirPath, 'CFD/STL/Raw.stl'), os.path.join(DCMDirPath, 'CFD')]
            self.CFD_STLcutTable.append(tmpSTLcutColumn)

            # STLmesh table
            tmpSTLmeshColumn = [True, os.path.join(DCMDirPath, 'CFD/MeshCut/lumenCut.stl'), MeshExe,
                                os.path.join(DCMDirPath, 'CFD')]
            self.CFD_STLmeshTable.append(tmpSTLmeshColumn)

            # FindFace table
            tmpFindFaceColumn = [True, os.path.join(DCMDirPath, 'CFD/Mesh/FluidMeshInit.nas'),
                                 os.path.join(DCMDirPath, 'CFD'), self.CFD_setTablePath, Tolerance_FindFace_Mesh]
            tmpFFRFindFaceColumn = [True, os.path.join(DCMDirPath, 'CFD/Mesh/FluidMeshInit.nas'),
                                    os.path.join(DCMDirPath, 'FFR'), self.CFD_setTablePath, Tolerance_FindFace_Mesh]
            self.CFD_FindFaceTable.append(tmpFindFaceColumn)
            if self.getFFRresult:
                self.CFD_FindFaceTable.append(tmpFFRFindFaceColumn)

            # GenerateIn table
            tmpGenerateInColumn = [True, os.path.join(DCMDirPath, 'CFD/FindFace/CFD.nas'),
                                   os.path.join(DCMDirPath, 'CFD'),
                                   os.path.join(self.ArVolCalPathList[loopIndex], 'Flow_1_0'),
                                   os.path.join(DCMDirPath, 'CFD/FindFace/area.csv'), AUIExe]
            tmpFFRGenerateInColumn = [True, os.path.join(DCMDirPath, 'FFR/FindFace/CFD.nas'),
                                      os.path.join(DCMDirPath, 'FFR'),
                                      os.path.join(self.ArVolCalPathList[loopIndex], 'Flow_4_1667'),
                                      os.path.join(DCMDirPath, 'FFR/FindFace/area.csv'), AUIExe]
            self.CFD_GenerateInTable.append(tmpGenerateInColumn)
            if self.getFFRresult:
                self.CFD_GenerateInTable.append(tmpFFRGenerateInColumn)

            # PostProgress table
            tmpPostProgressColumn = [os.path.join(DCMDirPath, 'PostProgress'), True,
                                     os.path.join(DCMDirPath, 'CFD/ADINA/CFD.idb'),
                                     os.path.join(DCMDirPath, 'CFD/result/CFD.por'), AUIExe, TimeStart_DataOutput,
                                     TimeStop_DataOutput, True, TimeStart_DataOutput, TimeStop_DataOutput,
                                     os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'),
                                     False, 100, os.path.join(DCMDirPath, 'PostProgress/PostNpy'),'ndCooOSI_2dndarr.npy,'
                                     'ndCooRRT_2dndarr.npy,ndCooTAWSS_2dndarr.npy,ndCooTAWSS_VectorMag_2dndarr.npy,'
                                     'ndTimeAvePressureCoo_2dndarr.npy,ndTimeIQRPressureCoo_2dndarr.npy,'
                                     'ndTimeKurtosisPressureCoo_2dndarr.npy,ndTimeMaxPressureCoo_2dndarr.npy,'
                                     'ndTimeMedianPressureCoo_2dndarr.npy,ndTimeMinPressureCoo_2dndarr.npy,'
                                     'ndTimePTPPressureCoo_2dndarr.npy,ndTimeQ1PressureCoo_2dndarr.npy,'
                                     'ndTimeQ3PressureCoo_2dndarr.npy,ndTimeSkewPressureCoo_2dndarr.npy,'
                                     'ndTimeSTDPressureCoo_2dndarr.npy,ndTimeVarPressureCoo_2dndarr.npy,'
                                     'ndTimeIQRWSSCoo_2dndarr.npy,ndTimeKurtosisWSSCoo_2dndarr.npy,'
                                     'ndTimeMaxWSSCoo_2dndarr.npy,ndTimeMedianWSSCoo_2dndarr.npy,'
                                     'ndTimeMinWSSCoo_2dndarr.npy,ndTimePTPWSSCoo_2dndarr.npy,'
                                     'ndTimeQ1WSSCoo_2dndarr.npy,ndTimeQ3WSSCoo_2dndarr.npy,'
                                     'ndTimeSkewWSSCoo_2dndarr.npy,ndTimeSTDWSSCoo_2dndarr.npy,'
                                     'ndTimeVarWSSCoo_2dndarr.npy', 666, 5, True, 1,
                                     os.path.join(DCMDirPath, 'PostProgress/MapCT'), False, 'CTOSI.nii.gz,'
                                     'CTRRT.nii.gz,CTTAWSS.nii.gz,CTTAWSS_VectorMag.nii.gz,CTTimeAvePressure.nii.gz,'
                                     'CTTimeIQRPressure.nii.gz,CTTimeKurtosisPressure.nii.gz,CTTimeMaxPressure.nii.gz,'
                                     'CTTimeMedianPressure.nii.gz,CTTimeMinPressure.nii.gz,CTTimePTPPressure.nii.gz,'
                                     'CTTimeQ1Pressure.nii.gz,CTTimeQ3Pressure.nii.gz,CTTimeSkewPressure.nii.gz,'
                                     'CTTimeSTDPressure.nii.gz,CTTimeVarPressure.nii.gz,CTTimeIQRWSS.nii.gz,'
                                     'CTTimeKurtosisWSS.nii.gz,CTTimeMaxWSS.nii.gz,CTTimeMedianWSS.nii.gz,'
                                     'CTTimeMinWSS.nii.gz,CTTimePTPWSS.nii.gz,CTTimeQ1WSS.nii.gz,'
                                     'CTTimeQ3WSS.nii.gz,CTTimeSkewWSS.nii.gz,CTTimeSTDWSS.nii.gz,CTTimeVarWSS.nii.gz',
                                     True, self.OriVolumePathList[loopIndex], FFR_KeepValue, True, True,
                                     os.path.join(DCMDirPath, 'CFD/FindFace/3Dmesh.nas'),
                                     os.path.join(DCMDirPath, 'PostProgress/PostNpy/ndInterestDict_dict.npy'),
                                     os.path.join(DCMDirPath, 'PostProgress/PostNpy'), 'CFDresult', True, False,
                                     os.path.join(DCMDirPath, 'PostProgress/PostNpy/ndTimeAvePressureCoo_2dndarr.npy'),
                                     os.path.join(DCMDirPath, 'PostProgress/FFR/CTFFRIQRAverageValue.npy'), 'PDPA', '',
                                     os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_lst_ParamsDic.npy'), 'CFDresult',
                                     True, False, True]
            tmpFFRPostProgressColumn = [os.path.join(DCMDirPath, 'FFRPostProgress'), True,
                                        os.path.join(DCMDirPath, 'FFR/ADINA/CFD.idb'),
                                        os.path.join(DCMDirPath, 'FFR/result/CFD.por'), AUIExe, TimeStart_DataOutput,
                                        TimeStop_DataOutput, True, TimeStart_DataOutput, TimeStop_DataOutput,
                                        os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'), False,
                                        100, os.path.join(DCMDirPath, 'FFRPostProgress/PostNpy'),
                                        'ndCooOSI_2dndarr.npy,ndCooRRT_2dndarr.npy,ndCooTAWSS_2dndarr.npy,'
                                        'ndCooTAWSS_VectorMag_2dndarr.npy,ndTimeAvePressureCoo_2dndarr.npy,'
                                        'ndTimeIQRPressureCoo_2dndarr.npy,ndTimeKurtosisPressureCoo_2dndarr.npy,'
                                        'ndTimeMaxPressureCoo_2dndarr.npy,ndTimeMedianPressureCoo_2dndarr.npy,'
                                        'ndTimeMinPressureCoo_2dndarr.npy,ndTimePTPPressureCoo_2dndarr.npy,'
                                        'ndTimeQ1PressureCoo_2dndarr.npy,ndTimeQ3PressureCoo_2dndarr.npy,'
                                        'ndTimeSkewPressureCoo_2dndarr.npy,ndTimeSTDPressureCoo_2dndarr.npy,'
                                        'ndTimeVarPressureCoo_2dndarr.npy,ndTimeIQRWSSCoo_2dndarr.npy,'
                                        'ndTimeKurtosisWSSCoo_2dndarr.npy,ndTimeMaxWSSCoo_2dndarr.npy,'
                                        'ndTimeMedianWSSCoo_2dndarr.npy,ndTimeMinWSSCoo_2dndarr.npy,'
                                        'ndTimePTPWSSCoo_2dndarr.npy,ndTimeQ1WSSCoo_2dndarr.npy,'
                                        'ndTimeQ3WSSCoo_2dndarr.npy,ndTimeSkewWSSCoo_2dndarr.npy,'
                                        'ndTimeSTDWSSCoo_2dndarr.npy,ndTimeVarWSSCoo_2dndarr.npy', 666, 5, True, 1,
                                        os.path.join(DCMDirPath, 'FFRPostProgress/MapCT'), False,
                                        'CTOSI.nii.gz,CTRRT.nii.gz,CTTAWSS.nii.gz,CTTAWSS_VectorMag.nii.gz,'
                                        'CTTimeAvePressure.nii.gz,CTTimeIQRPressure.nii.gz,'
                                        'CTTimeKurtosisPressure.nii.gz,CTTimeMaxPressure.nii.gz,'
                                        'CTTimeMedianPressure.nii.gz,CTTimeMinPressure.nii.gz,'
                                        'CTTimePTPPressure.nii.gz,CTTimeQ1Pressure.nii.gz,CTTimeQ3Pressure.nii.gz,'
                                        'CTTimeSkewPressure.nii.gz,CTTimeSTDPressure.nii.gz,CTTimeVarPressure.nii.gz,'
                                        'CTTimeIQRWSS.nii.gz,CTTimeKurtosisWSS.nii.gz,CTTimeMaxWSS.nii.gz,'
                                        'CTTimeMedianWSS.nii.gz,CTTimeMinWSS.nii.gz,CTTimePTPWSS.nii.gz,'
                                        'CTTimeQ1WSS.nii.gz,CTTimeQ3WSS.nii.gz,CTTimeSkewWSS.nii.gz,'
                                        'CTTimeSTDWSS.nii.gz,CTTimeVarWSS.nii.gz', True,
                                        self.OriVolumePathList[loopIndex], FFR_KeepValue, True, True,
                                        os.path.join(DCMDirPath, 'PostProgress/Vtu/CFDresult.vtu'), '', '', '', '', '',
                                        os.path.join(DCMDirPath, 'FFRPostProgress/PostNpy/ndTimeAvePressureCoo_2dndarr.npy'),
                                        os.path.join(DCMDirPath, 'FFRPostProgress/FFR/CTFFRIQRAverageValue.npy'),
                                        'FFR', 'FFRresult', '', '', False, True, False]
            tmpiFRPostProgressColumn = [os.path.join(DCMDirPath, 'IFRPostProgress'), True,
                                        os.path.join(DCMDirPath, 'CFD/ADINA/CFD.idb'),
                                        os.path.join(DCMDirPath, 'CFD/result/CFD.por'), AUIExe, TimeStart_DataOutput,
                                        TimeStop_DataOutput, True, TimeStart_IFR, TimeStop_IFR,
                                        os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'), False,
                                        100, os.path.join(DCMDirPath, 'IFRPostProgress/PostNpy'),
                                        'ndCooOSI_2dndarr.npy,ndCooRRT_2dndarr.npy,ndCooTAWSS_2dndarr.npy,'
                                        'ndCooTAWSS_VectorMag_2dndarr.npy,ndTimeAvePressureCoo_2dndarr.npy,'
                                        'ndTimeIQRPressureCoo_2dndarr.npy,ndTimeKurtosisPressureCoo_2dndarr.npy,'
                                        'ndTimeMaxPressureCoo_2dndarr.npy,ndTimeMedianPressureCoo_2dndarr.npy,'
                                        'ndTimeMinPressureCoo_2dndarr.npy,ndTimePTPPressureCoo_2dndarr.npy,'
                                        'ndTimeQ1PressureCoo_2dndarr.npy,ndTimeQ3PressureCoo_2dndarr.npy,'
                                        'ndTimeSkewPressureCoo_2dndarr.npy,ndTimeSTDPressureCoo_2dndarr.npy,'
                                        'ndTimeVarPressureCoo_2dndarr.npy,ndTimeIQRWSSCoo_2dndarr.npy,'
                                        'ndTimeKurtosisWSSCoo_2dndarr.npy,ndTimeMaxWSSCoo_2dndarr.npy,'
                                        'ndTimeMedianWSSCoo_2dndarr.npy,ndTimeMinWSSCoo_2dndarr.npy,'
                                        'ndTimePTPWSSCoo_2dndarr.npy,ndTimeQ1WSSCoo_2dndarr.npy,'
                                        'ndTimeQ3WSSCoo_2dndarr.npy,ndTimeSkewWSSCoo_2dndarr.npy,'
                                        'ndTimeSTDWSSCoo_2dndarr.npy,ndTimeVarWSSCoo_2dndarr.npy', 666, 5, True, 1,
                                        os.path.join(DCMDirPath, 'IFRPostProgress/MapCT'), False, 'CTOSI.nii.gz,'
                                        'CTRRT.nii.gz,CTTAWSS.nii.gz,CTTAWSS_VectorMag.nii.gz,CTTimeAvePressure.nii.gz,'
                                        'CTTimeIQRPressure.nii.gz,CTTimeKurtosisPressure.nii.gz,'
                                        'CTTimeMaxPressure.nii.gz,CTTimeMedianPressure.nii.gz,CTTimeMinPressure.nii.gz,'
                                        'CTTimePTPPressure.nii.gz,CTTimeQ1Pressure.nii.gz,CTTimeQ3Pressure.nii.gz,'
                                        'CTTimeSkewPressure.nii.gz,CTTimeSTDPressure.nii.gz,CTTimeVarPressure.nii.gz,'
                                        'CTTimeIQRWSS.nii.gz,CTTimeKurtosisWSS.nii.gz,CTTimeMaxWSS.nii.gz,'
                                        'CTTimeMedianWSS.nii.gz,CTTimeMinWSS.nii.gz,CTTimePTPWSS.nii.gz,'
                                        'CTTimeQ1WSS.nii.gz,CTTimeQ3WSS.nii.gz,CTTimeSkewWSS.nii.gz,'
                                        'CTTimeSTDWSS.nii.gz,CTTimeVarWSS.nii.gz', True,
                                        self.OriVolumePathList[loopIndex], FFR_KeepValue, True, True,
                                        os.path.join(DCMDirPath, 'FFRPostProgress/Vtu/FFRresult.vtu'), '', '', '', '', '',
                                        os.path.join(DCMDirPath, 'IFRPostProgress/PostNpy/ndTimeAvePressureCoo_2dndarr.npy'),
                                        os.path.join(DCMDirPath, 'IFRPostProgress/FFR/CTFFRIQRAverageValue.npy'),
                                        'IFR', 'IFRresult', '', '', False, True, False]
            self.CFD_PostProgressTable.append(tmpPostProgressColumn)
            if self.getFFRresult:
                self.CFD_PostProgressTable.append(tmpFFRPostProgressColumn)
            if self.getIFRresult:
                self.CFD_PostProgressTable.append(tmpiFRPostProgressColumn)

            # DataOutput table
            tmpDataOutputColumn = [os.path.join(DCMDirPath, 'PostProgress'), True,
                                   os.path.join(DCMDirPath, 'CFD/ADINA/CFD.idb'),
                                   os.path.join(DCMDirPath, 'CFD/result/CFD.por'), AUIExe, TimeStart_DataOutput,
                                   TimeStop_DataOutput]
            tmpFFRDataOutputColumn = [os.path.join(DCMDirPath, 'FFRPostProgress'), True,
                                      os.path.join(DCMDirPath, 'FFR/ADINA/CFD.idb'),
                                      os.path.join(DCMDirPath, 'FFR/result/CFD.por'), AUIExe, TimeStart_DataOutput,
                                      TimeStop_DataOutput]
            self.DataOutputTable.append(tmpDataOutputColumn)
            if self.getFFRresult:
                self.DataOutputTable.append(tmpFFRDataOutputColumn)

            # PostNpy table
            tmpPostNpyColumn = [os.path.join(DCMDirPath, 'PostProgress'), True,
                                os.path.join(DCMDirPath, 'PostProgress/Npy'), TimeStart_DataOutput, TimeStop_DataOutput]
            tmpFFRPostNpyColumn = [os.path.join(DCMDirPath, 'FFRPostProgress'), True,
                                   os.path.join(DCMDirPath, 'FFRPostProgress/Npy'), TimeStart_DataOutput,
                                   TimeStop_DataOutput]
            tmpIFRPostNpyColumn = [os.path.join(DCMDirPath, 'IFRPostProgress'), True,
                                   os.path.join(DCMDirPath, 'PostProgress/Npy'), TimeStart_IFR, TimeStop_IFR]
            self.PostNpyTable.append(tmpPostNpyColumn)
            if self.getFFRresult:
                self.PostNpyTable.append(tmpFFRPostNpyColumn)
            if self.getIFRresult:
                self.PostNpyTable.append(tmpIFRPostNpyColumn)

            # Map_Result table
            # tmpMap_ResultColumn = [os.path.join(DCMDirPath,'PostProgress'),True,
            #                        os.path.join(self.OriVolumePathList[loopIndex],'OriVolumeCAVal.nii.gz'),
            #                        os.path.join(DCMDirPath,'PostProgress/PostNpy')]
            # tmpFFRMap_ResultColumn = [os.path.join(DCMDirPath,'FFRPostProgress'),True,
            #                           os.path.join(self.OriVolumePathList[loopIndex],'OriVolumeCAVal.nii.gz'),
            #                           os.path.join(DCMDirPath,'FFRPostProgress/PostNpy')]
            tmpMap_ResultColumn = [os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'), False, 100,
                                   os.path.join(DCMDirPath, 'PostProgress/PostNpy'), 'ndCooOSI_2dndarr.npy,'
                                   'ndCooRRT_2dndarr.npy,ndCooTAWSS_2dndarr.npy,ndCooTAWSS_VectorMag_2dndarr.npy,'
                                   'ndTimeAvePressureCoo_2dndarr.npy,ndTimeDecile1PressureCoo_2dndarr.npy,'
                                   'ndTimeDecile1WSSCoo_2dndarr.npy,ndTimeDecile2PressureCoo_2dndarr.npy,'
                                   'ndTimeDecile2WSSCoo_2dndarr.npy,ndTimeDecile3PressureCoo_2dndarr.npy,'
                                   'ndTimeDecile3WSSCoo_2dndarr.npy,ndTimeDecile4PressureCoo_2dndarr.npy,'
                                   'ndTimeDecile4WSSCoo_2dndarr.npy,ndTimeDecile6PressureCoo_2dndarr.npy,'
                                   'ndTimeDecile6WSSCoo_2dndarr.npy,ndTimeDecile7PressureCoo_2dndarr.npy,'
                                   'ndTimeDecile7WSSCoo_2dndarr.npy,ndTimeDecile8PressureCoo_2dndarr.npy,'
                                   'ndTimeDecile8WSSCoo_2dndarr.npy,ndTimeDecile9PressureCoo_2dndarr.npy,'
                                   'ndTimeDecile9WSSCoo_2dndarr.npy,ndTimeEnergyPressureCoo_2dndarr.npy,'
                                   'ndTimeEnergyWSSCoo_2dndarr.npy,ndTimeEntropyPressureCoo_2dndarr.npy,'
                                   'ndTimeEntropyWSSCoo_2dndarr.npy,ndTimeGMeanPressureCoo_2dndarr.npy,'
                                   'ndTimeGMeanWSSCoo_2dndarr.npy,ndTimeHMeanPressureCoo_2dndarr.npy,'
                                   'ndTimeHMeanWSSCoo_2dndarr.npy,ndTimeIQRPressureCoo_2dndarr.npy,'
                                   'ndTimeIQRWSSCoo_2dndarr.npy,ndTimeKurtosisPressureCoo_2dndarr.npy,'
                                   'ndTimeKurtosisWSSCoo_2dndarr.npy,ndTimeMaxPressureCoo_2dndarr.npy,'
                                   'ndTimeMaxWSSCoo_2dndarr.npy,ndTimeMedianPressureCoo_2dndarr.npy,'
                                   'ndTimeMedianWSSCoo_2dndarr.npy,ndTimeMinPressureCoo_2dndarr.npy,'
                                   'ndTimeMinWSSCoo_2dndarr.npy,ndTimeModePressureCoo_2dndarr.npy,'
                                   'ndTimeModeWSSCoo_2dndarr.npy,ndTimePTPPressureCoo_2dndarr.npy,'
                                   'ndTimePTPWSSCoo_2dndarr.npy,ndTimeQ1PressureCoo_2dndarr.npy,'
                                   'ndTimeQ1WSSCoo_2dndarr.npy,ndTimeQ3PressureCoo_2dndarr.npy,'
                                   'ndTimeQ3WSSCoo_2dndarr.npy,ndTimeRMSPressureCoo_2dndarr.npy,'
                                   'ndTimeRMSWSSCoo_2dndarr.npy,ndTimeSEPressureCoo_2dndarr.npy,'
                                   'ndTimeSEWSSCoo_2dndarr.npy,ndTimeSkewPressureCoo_2dndarr.npy,'
                                   'ndTimeSkewWSSCoo_2dndarr.npy,ndTimeSTDPressureCoo_2dndarr.npy,'
                                   'ndTimeSTDWSSCoo_2dndarr.npy,ndTimeTriMeanPressureCoo_2dndarr.npy,'
                                   'ndTimeTriMeanWSSCoo_2dndarr.npy,ndTimeVarPressureCoo_2dndarr.npy,'
                                   'ndTimeVarWSSCoo_2dndarr.npy', 666, 5, True, 1,
                                   os.path.join(DCMDirPath, 'PostProgress/MapCT'), False, 'CTOSI.nii.gz,CTRRT.nii.gz,'
                                   'CTTAWSS.nii.gz,CTTAWSS_VectorMag.nii.gz,CTTimeAvePressure.nii.gz,'
                                   'CTTimeDecile1Pressure.nii.gz,CTTimeDecile1WSS.nii.gz,CTTimeDecile2Pressure.nii.gz,'
                                   'CTTimeDecile2WSS.nii.gz,CTTimeDecile3Pressure.nii.gz,CTTimeDecile3WSS.nii.gz,'
                                   'CTTimeDecile4Pressure.nii.gz,CTTimeDecile4WSS.nii.gz,CTTimeDecile6Pressure.nii.gz,'
                                   'CTTimeDecile6WSS.nii.gz,CTTimeDecile7Pressure.nii.gz,CTTimeDecile7WSS.nii.gz,'
                                   'CTTimeDecile8Pressure.nii.gz,CTTimeDecile8WSS.nii.gz,CTTimeDecile9Pressure.nii.gz,'
                                   'CTTimeDecile9WSS.nii.gz,CTTimeEnergyPressure.nii.gz,CTTimeEnergyWSS.nii.gz,'
                                   'CTTimeEntropyPressure.nii.gz,CTTimeEntropyWSS.nii.gz,CTTimeGMeanPressure.nii.gz,'
                                   'CTTimeGMeanWSS.nii.gz,CTTimeHMeanPressure.nii.gz,CTTimeHMeanWSS.nii.gz,'
                                   'CTTimeIQRPressure.nii.gz,CTTimeIQRWSS.nii.gz,CTTimeKurtosisPressure.nii.gz,'
                                   'CTTimeKurtosisWSS.nii.gz,CTTimeMaxPressure.nii.gz,CTTimeMaxWSS.nii.gz,'
                                   'CTTimeMedianPressure.nii.gz,CTTimeMedianWSS.nii.gz,CTTimeMinPressure.nii.gz,'
                                   'CTTimeMinWSS.nii.gz,CTTimeModePressure.nii.gz,CTTimeModeWSS.nii.gz,'
                                   'CTTimePTPPressure.nii.gz,CTTimePTPWSS.nii.gz,CTTimeQ1Pressure.nii.gz,'
                                   'CTTimeQ1WSS.nii.gz,CTTimeQ3Pressure.nii.gz,CTTimeQ3WSS.nii.gz,'
                                   'CTTimeRMSPressure.nii.gz,CTTimeRMSWSS.nii.gz,CTTimeSEPressure.nii.gz,'
                                   'CTTimeSEWSS.nii.gz,CTTimeSkewPressure.nii.gz,CTTimeSkewWSS.nii.gz,'
                                   'CTTimeSTDPressure.nii.gz,CTTimeSTDWSS.nii.gz,CTTimeTriMeanPressure.nii.gz,'
                                   'CTTimeTriMeanWSS.nii.gz,CTTimeVarPressure.nii.gz,CTTimeVarWSS.nii.gz']
            tmpFFRMap_ResultColumn = [os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'), False,
                                      100, os.path.join(DCMDirPath, 'FFRPostProgress/PostNpy'), 'ndCooOSI_2dndarr.npy,'
                                      'ndCooRRT_2dndarr.npy,ndCooTAWSS_2dndarr.npy,ndCooTAWSS_VectorMag_2dndarr.npy,'
                                      'ndTimeAvePressureCoo_2dndarr.npy,ndTimeDecile1PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile1WSSCoo_2dndarr.npy,ndTimeDecile2PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile2WSSCoo_2dndarr.npy,ndTimeDecile3PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile3WSSCoo_2dndarr.npy,ndTimeDecile4PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile4WSSCoo_2dndarr.npy,ndTimeDecile6PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile6WSSCoo_2dndarr.npy,ndTimeDecile7PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile7WSSCoo_2dndarr.npy,ndTimeDecile8PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile8WSSCoo_2dndarr.npy,ndTimeDecile9PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile9WSSCoo_2dndarr.npy,ndTimeEnergyPressureCoo_2dndarr.npy,'
                                      'ndTimeEnergyWSSCoo_2dndarr.npy,ndTimeEntropyPressureCoo_2dndarr.npy,'
                                      'ndTimeEntropyWSSCoo_2dndarr.npy,ndTimeGMeanPressureCoo_2dndarr.npy,'
                                      'ndTimeGMeanWSSCoo_2dndarr.npy,ndTimeHMeanPressureCoo_2dndarr.npy,'
                                      'ndTimeHMeanWSSCoo_2dndarr.npy,ndTimeIQRPressureCoo_2dndarr.npy,'
                                      'ndTimeIQRWSSCoo_2dndarr.npy,ndTimeKurtosisPressureCoo_2dndarr.npy,'
                                      'ndTimeKurtosisWSSCoo_2dndarr.npy,ndTimeMaxPressureCoo_2dndarr.npy,'
                                      'ndTimeMaxWSSCoo_2dndarr.npy,ndTimeMedianPressureCoo_2dndarr.npy,'
                                      'ndTimeMedianWSSCoo_2dndarr.npy,ndTimeMinPressureCoo_2dndarr.npy,'
                                      'ndTimeMinWSSCoo_2dndarr.npy,ndTimeModePressureCoo_2dndarr.npy,'
                                      'ndTimeModeWSSCoo_2dndarr.npy,ndTimePTPPressureCoo_2dndarr.npy,'
                                      'ndTimePTPWSSCoo_2dndarr.npy,ndTimeQ1PressureCoo_2dndarr.npy,'
                                      'ndTimeQ1WSSCoo_2dndarr.npy,ndTimeQ3PressureCoo_2dndarr.npy,'
                                      'ndTimeQ3WSSCoo_2dndarr.npy,ndTimeRMSPressureCoo_2dndarr.npy,'
                                      'ndTimeRMSWSSCoo_2dndarr.npy,ndTimeSEPressureCoo_2dndarr.npy,'
                                      'ndTimeSEWSSCoo_2dndarr.npy,ndTimeSkewPressureCoo_2dndarr.npy,'
                                      'ndTimeSkewWSSCoo_2dndarr.npy,ndTimeSTDPressureCoo_2dndarr.npy,'
                                      'ndTimeSTDWSSCoo_2dndarr.npy,ndTimeTriMeanPressureCoo_2dndarr.npy,'
                                      'ndTimeTriMeanWSSCoo_2dndarr.npy,ndTimeVarPressureCoo_2dndarr.npy,'
                                      'ndTimeVarWSSCoo_2dndarr.npy', 666, 5, True, 1,
                                      os.path.join(DCMDirPath, 'FFRPostProgress/MapCT'), False, 'CTOSI.nii.gz,'
                                      'CTRRT.nii.gz,CTTAWSS.nii.gz,CTTAWSS_VectorMag.nii.gz,CTTimeAvePressure.nii.gz,'
                                      'CTTimeDecile1Pressure.nii.gz,CTTimeDecile1WSS.nii.gz,'
                                      'CTTimeDecile2Pressure.nii.gz,CTTimeDecile2WSS.nii.gz,'
                                      'CTTimeDecile3Pressure.nii.gz,CTTimeDecile3WSS.nii.gz,'
                                      'CTTimeDecile4Pressure.nii.gz,CTTimeDecile4WSS.nii.gz,'
                                      'CTTimeDecile6Pressure.nii.gz,CTTimeDecile6WSS.nii.gz,'
                                      'CTTimeDecile7Pressure.nii.gz,CTTimeDecile7WSS.nii.gz,'
                                      'CTTimeDecile8Pressure.nii.gz,CTTimeDecile8WSS.nii.gz,'
                                      'CTTimeDecile9Pressure.nii.gz,CTTimeDecile9WSS.nii.gz,'
                                      'CTTimeEnergyPressure.nii.gz,CTTimeEnergyWSS.nii.gz,CTTimeEntropyPressure.nii.gz,'
                                      'CTTimeEntropyWSS.nii.gz,CTTimeGMeanPressure.nii.gz,CTTimeGMeanWSS.nii.gz,'
                                      'CTTimeHMeanPressure.nii.gz,CTTimeHMeanWSS.nii.gz,CTTimeIQRPressure.nii.gz,'
                                      'CTTimeIQRWSS.nii.gz,CTTimeKurtosisPressure.nii.gz,CTTimeKurtosisWSS.nii.gz,'
                                      'CTTimeMaxPressure.nii.gz,CTTimeMaxWSS.nii.gz,CTTimeMedianPressure.nii.gz,'
                                      'CTTimeMedianWSS.nii.gz,CTTimeMinPressure.nii.gz,CTTimeMinWSS.nii.gz,'
                                      'CTTimeModePressure.nii.gz,CTTimeModeWSS.nii.gz,CTTimePTPPressure.nii.gz,'
                                      'CTTimePTPWSS.nii.gz,CTTimeQ1Pressure.nii.gz,CTTimeQ1WSS.nii.gz,'
                                      'CTTimeQ3Pressure.nii.gz,CTTimeQ3WSS.nii.gz,CTTimeRMSPressure.nii.gz,'
                                      'CTTimeRMSWSS.nii.gz,CTTimeSEPressure.nii.gz,CTTimeSEWSS.nii.gz,'
                                      'CTTimeSkewPressure.nii.gz,CTTimeSkewWSS.nii.gz,CTTimeSTDPressure.nii.gz,'
                                      'CTTimeSTDWSS.nii.gz,CTTimeTriMeanPressure.nii.gz,CTTimeTriMeanWSS.nii.gz,'
                                      'CTTimeVarPressure.nii.gz,CTTimeVarWSS.nii.gz']
            tmpIFRMap_ResultColumn = [os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'), False,
                                      100, os.path.join(DCMDirPath, 'IFRPostProgress/PostNpy'), 'ndCooOSI_2dndarr.npy,'
                                      'ndCooRRT_2dndarr.npy,ndCooTAWSS_2dndarr.npy,ndCooTAWSS_VectorMag_2dndarr.npy,'
                                      'ndTimeAvePressureCoo_2dndarr.npy,ndTimeDecile1PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile1WSSCoo_2dndarr.npy,ndTimeDecile2PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile2WSSCoo_2dndarr.npy,ndTimeDecile3PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile3WSSCoo_2dndarr.npy,ndTimeDecile4PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile4WSSCoo_2dndarr.npy,ndTimeDecile6PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile6WSSCoo_2dndarr.npy,ndTimeDecile7PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile7WSSCoo_2dndarr.npy,ndTimeDecile8PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile8WSSCoo_2dndarr.npy,ndTimeDecile9PressureCoo_2dndarr.npy,'
                                      'ndTimeDecile9WSSCoo_2dndarr.npy,ndTimeEnergyPressureCoo_2dndarr.npy,'
                                      'ndTimeEnergyWSSCoo_2dndarr.npy,ndTimeEntropyPressureCoo_2dndarr.npy,'
                                      'ndTimeEntropyWSSCoo_2dndarr.npy,ndTimeGMeanPressureCoo_2dndarr.npy,'
                                      'ndTimeGMeanWSSCoo_2dndarr.npy,ndTimeHMeanPressureCoo_2dndarr.npy,'
                                      'ndTimeHMeanWSSCoo_2dndarr.npy,ndTimeIQRPressureCoo_2dndarr.npy,'
                                      'ndTimeIQRWSSCoo_2dndarr.npy,ndTimeKurtosisPressureCoo_2dndarr.npy,'
                                      'ndTimeKurtosisWSSCoo_2dndarr.npy,ndTimeMaxPressureCoo_2dndarr.npy,'
                                      'ndTimeMaxWSSCoo_2dndarr.npy,ndTimeMedianPressureCoo_2dndarr.npy,'
                                      'ndTimeMedianWSSCoo_2dndarr.npy,ndTimeMinPressureCoo_2dndarr.npy,'
                                      'ndTimeMinWSSCoo_2dndarr.npy,ndTimeModePressureCoo_2dndarr.npy,'
                                      'ndTimeModeWSSCoo_2dndarr.npy,ndTimePTPPressureCoo_2dndarr.npy,'
                                      'ndTimePTPWSSCoo_2dndarr.npy,ndTimeQ1PressureCoo_2dndarr.npy,'
                                      'ndTimeQ1WSSCoo_2dndarr.npy,ndTimeQ3PressureCoo_2dndarr.npy,'
                                      'ndTimeQ3WSSCoo_2dndarr.npy,ndTimeRMSPressureCoo_2dndarr.npy,'
                                      'ndTimeRMSWSSCoo_2dndarr.npy,ndTimeSEPressureCoo_2dndarr.npy,'
                                      'ndTimeSEWSSCoo_2dndarr.npy,ndTimeSkewPressureCoo_2dndarr.npy,'
                                      'ndTimeSkewWSSCoo_2dndarr.npy,ndTimeSTDPressureCoo_2dndarr.npy,'
                                      'ndTimeSTDWSSCoo_2dndarr.npy,ndTimeTriMeanPressureCoo_2dndarr.npy,'
                                      'ndTimeTriMeanWSSCoo_2dndarr.npy,ndTimeVarPressureCoo_2dndarr.npy,'
                                      'ndTimeVarWSSCoo_2dndarr.npy', 666, 5, True, 1,
                                      os.path.join(DCMDirPath, 'IFRPostProgress/MapCT'), False, 'CTOSI.nii.gz,'
                                      'CTRRT.nii.gz,CTTAWSS.nii.gz,CTTAWSS_VectorMag.nii.gz,CTTimeAvePressure.nii.gz,'
                                      'CTTimeDecile1Pressure.nii.gz,CTTimeDecile1WSS.nii.gz,'
                                      'CTTimeDecile2Pressure.nii.gz,CTTimeDecile2WSS.nii.gz,'
                                      'CTTimeDecile3Pressure.nii.gz,CTTimeDecile3WSS.nii.gz,'
                                      'CTTimeDecile4Pressure.nii.gz,CTTimeDecile4WSS.nii.gz,'
                                      'CTTimeDecile6Pressure.nii.gz,CTTimeDecile6WSS.nii.gz,'
                                      'CTTimeDecile7Pressure.nii.gz,CTTimeDecile7WSS.nii.gz,'
                                      'CTTimeDecile8Pressure.nii.gz,CTTimeDecile8WSS.nii.gz,'
                                      'CTTimeDecile9Pressure.nii.gz,CTTimeDecile9WSS.nii.gz,'
                                      'CTTimeEnergyPressure.nii.gz,CTTimeEnergyWSS.nii.gz,CTTimeEntropyPressure.nii.gz,'
                                      'CTTimeEntropyWSS.nii.gz,CTTimeGMeanPressure.nii.gz,CTTimeGMeanWSS.nii.gz,'
                                      'CTTimeHMeanPressure.nii.gz,CTTimeHMeanWSS.nii.gz,CTTimeIQRPressure.nii.gz,'
                                      'CTTimeIQRWSS.nii.gz,CTTimeKurtosisPressure.nii.gz,CTTimeKurtosisWSS.nii.gz,'
                                      'CTTimeMaxPressure.nii.gz,CTTimeMaxWSS.nii.gz,CTTimeMedianPressure.nii.gz,'
                                      'CTTimeMedianWSS.nii.gz,CTTimeMinPressure.nii.gz,CTTimeMinWSS.nii.gz,'
                                      'CTTimeModePressure.nii.gz,CTTimeModeWSS.nii.gz,CTTimePTPPressure.nii.gz,'
                                      'CTTimePTPWSS.nii.gz,CTTimeQ1Pressure.nii.gz,CTTimeQ1WSS.nii.gz,'
                                      'CTTimeQ3Pressure.nii.gz,CTTimeQ3WSS.nii.gz,CTTimeRMSPressure.nii.gz,'
                                      'CTTimeRMSWSS.nii.gz,CTTimeSEPressure.nii.gz,CTTimeSEWSS.nii.gz,'
                                      'CTTimeSkewPressure.nii.gz,CTTimeSkewWSS.nii.gz,CTTimeSTDPressure.nii.gz,'
                                      'CTTimeSTDWSS.nii.gz,CTTimeTriMeanPressure.nii.gz,CTTimeTriMeanWSS.nii.gz,'
                                      'CTTimeVarPressure.nii.gz,CTTimeVarWSS.nii.gz']
            self.Map_ResultTable.append(tmpMap_ResultColumn)
            if self.getFFRresult:
                self.Map_ResultTable.append(tmpFFRMap_ResultColumn)
            if self.getIFRresult:
                self.Map_ResultTable.append(tmpIFRMap_ResultColumn)

            # FFRCalculation table
            tmpFFRCalculationColumn = [os.path.join(DCMDirPath, 'PostProgress'), True,
                                       os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'),
                                       FFR_KeepValue,
                                       os.path.join(DCMDirPath, 'PostProgress/MapCT/CTTimeAvePressure.nii.gz')]
            tmpFFRFFRCalculationColumn = [os.path.join(DCMDirPath, 'FFRPostProgress'), True,
                                          os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'),
                                          FFR_KeepValue,
                                          os.path.join(DCMDirPath, 'FFRPostProgress/MapCT/CTTimeAvePressure.nii.gz')]
            tmpIFRFFRCalculationColumn = [os.path.join(DCMDirPath, 'IFRPostProgress'), True,
                                          os.path.join(self.OriVolumePathList[loopIndex], 'OriVolumeCAVal.nii.gz'),
                                          FFR_KeepValue,
                                          os.path.join(DCMDirPath, 'IFRPostProgress/MapCT/CTTimeAvePressure.nii.gz')]
            self.FFRCalculationTable.append(tmpFFRCalculationColumn)
            if self.getFFRresult:
                self.FFRCalculationTable.append(tmpFFRFFRCalculationColumn)
            if self.getIFRresult:
                self.FFRCalculationTable.append(tmpIFRFFRCalculationColumn)

            # Paraview table
            tmpParaviewColumn = [os.path.join(DCMDirPath, 'PostProgress'), True,
                                 os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_Nodecoo_Dic.npy'),
                                 os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_TetraElmnt_NdIfo_Dic.npy'),
                                 os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_HexElmnt_NdIfo_Dic.npy'),
                                 os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_Times_Dic.npy'),
                                 os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_lst_ParamsDic.npy'),
                                 os.path.join(DCMDirPath, 'PostProgress/postNpy/fluid_PostResults_Dict_dict.npy'),
                                 os.path.join(DCMDirPath, 'PostProgress/postNpy/fluid_TimeAvePressureDict_dict.npy'),
                                 os.path.join(DCMDirPath, 'PostProgress/postNpy/fluid_PostResults_WssDict_dict.npy'),
                                 os.path.join(DCMDirPath, 'PostProgress/FFR/CTFFRIQRAverageValue.npy')]
            tmpFFRParaviewColumn = [os.path.join(DCMDirPath, 'FFRPostProgress'), True,
                                    os.path.join(DCMDirPath, 'FFRPostProgress/Npy/Fluid_Nodecoo_Dic.npy'),
                                    os.path.join(DCMDirPath, 'FFRPostProgress/Npy/Fluid_TetraElmnt_NdIfo_Dic.npy'),
                                    os.path.join(DCMDirPath, 'FFRPostProgress/Npy/Fluid_HexElmnt_NdIfo_Dic.npy'),
                                    os.path.join(DCMDirPath, 'FFRPostProgress/Npy/Fluid_Times_Dic.npy'),
                                    os.path.join(DCMDirPath, 'FFRPostProgress/Npy/Fluid_lst_ParamsDic.npy'),
                                    os.path.join(DCMDirPath, 'FFRPostProgress/postNpy/fluid_PostResults_Dict_dict.npy'),
                                    os.path.join(DCMDirPath, 'FFRPostProgress/postNpy/fluid_TimeAvePressureDict_dict.npy'),
                                    os.path.join(DCMDirPath, 'FFRPostProgress/postNpy/fluid_PostResults_WssDict_dict.npy'),
                                    os.path.join(DCMDirPath, 'FFRPostProgress/FFR/CTFFRIQRAverageValue.npy')]
            tmpIFRParaviewColumn = [os.path.join(DCMDirPath, 'IFRPostProgress'), True,
                                    os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_Nodecoo_Dic.npy'),
                                    os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_TetraElmnt_NdIfo_Dic.npy'),
                                    os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_HexElmnt_NdIfo_Dic.npy'),
                                    os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_Times_Dic.npy'),
                                    os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_lst_ParamsDic.npy'),
                                    os.path.join(DCMDirPath, 'IFRPostProgress/postNpy/fluid_PostResults_Dict_dict.npy'),
                                    os.path.join(DCMDirPath, 'IFRPostProgress/postNpy/fluid_TimeAvePressureDict_dict.npy'),
                                    os.path.join(DCMDirPath, 'IFRPostProgress/postNpy/fluid_PostResults_WssDict_dict.npy'),
                                    os.path.join(DCMDirPath, 'IFRPostProgress/FFR/CTFFRIQRAverageValue.npy')]
            self.ParaviewTable.append(tmpParaviewColumn)
            if self.getFFRresult:
                self.ParaviewTable.append(tmpFFRParaviewColumn)
            if self.getIFRresult:
                self.ParaviewTable.append(tmpIFRParaviewColumn)

            # Savevtu table
            tmpSavevtuColumn = [os.path.join(DCMDirPath, 'PostProgress'), True,
                                os.path.join(DCMDirPath, 'CFD/FindFace/3Dmesh.nas'),
                                os.path.join(DCMDirPath, 'PostProgress/PostNpy/ndInterestDict_dict.npy'),
                                os.path.join(DCMDirPath, 'PostProgress/PostNpy'), 'CFDresult', True, False,
                                os.path.join(DCMDirPath, 'PostProgress/PostNpy/ndTimeAvePressureCoo_2dndarr.npy'),
                                os.path.join(DCMDirPath, 'PostProgress/FFR/CTFFRIQRAverageValue.npy'), 'PDPA', '',
                                os.path.join(DCMDirPath, 'PostProgress/Npy/Fluid_lst_ParamsDic.npy'), 'CFDresult',
                                True, False, True]
            tmpFFRSavevtuColumn = [os.path.join(DCMDirPath, 'FFRPostProgress'), True,
                                   os.path.join(DCMDirPath, 'PostProgress/Vtu/CFDresult.vtu'), '', '', '', '', '',
                                   os.path.join(DCMDirPath, 'FFRPostProgress/PostNpy/ndTimeAvePressureCoo_2dndarr.npy'),
                                   os.path.join(DCMDirPath, 'FFRPostProgress/FFR/CTFFRIQRAverageValue.npy'),
                                   'FFR', 'FFRresult', '', '', False, True, False]
            tmpIFRSavevtuColumn = [os.path.join(DCMDirPath, 'IFRPostProgress'), True,
                                   os.path.join(DCMDirPath, 'FFRPostProgress/Vtu/FFRresult.vtu'), '', '', '', '', '',
                                   os.path.join(DCMDirPath, 'IFRPostProgress/PostNpy/ndTimeAvePressureCoo_2dndarr.npy'),
                                   os.path.join(DCMDirPath, 'IFRPostProgress/FFR/CTFFRIQRAverageValue.npy'), 'IFR',
                                   'IFRresult', '', '', False, True, False]
            self.SaveVtuTable.append(tmpSavevtuColumn)
            if self.getFFRresult:
                self.SaveVtuTable.append(tmpFFRSavevtuColumn)
            if self.getIFRresult:
                self.SaveVtuTable.append(tmpIFRSavevtuColumn)

            ## Area volume calculation table
            # save branch table
            branchMFilePath = os.path.join(self.ArVolCalPathList[loopIndex], 'AVCBranM.csv')
            branchM_df = pd.DataFrame(AVCBranMTable, columns=AVCBranM_Head)
            branchM_df.to_csv(branchMFilePath, index=None)

            # save parameter table
            ParamFilePath = os.path.join(self.ArVolCalPathList[loopIndex], 'AVCParam.csv')
            Param_df = pd.DataFrame([[totInflow_AVC, diffThres_AVC, step_AVC, self.ArVolCalPathList[loopIndex],
                                      exo_AVC, mul_AVC]], columns=AVCParam_Head)
            Param_df.to_csv(ParamFilePath, index=None)

            # batch files
            self.AVCTable.append([branchMFilePath, ParamFilePath])

            # # copy aorta files
            # cmd1 = self.CopyCommand(aorOut_AVC, self.ArVolCalPathList[loopIndex])
            # cmd2 = self.CopyCommand(aorIn_AVC, self.ArVolCalPathList[loopIndex])
            # cmd3 = self.CopyCommand(aorOutFFR_AVC, self.ArVolCalPathList[loopIndex])
            # os.system(cmd1)
            # os.system(cmd2)
            # os.system(cmd3)
            # # self.UpdateMsgLog(str(cmd1))

        # generate csv used for batch filter mask processing
        FM_df = pd.DataFrame(self.FilterMaskTable, columns=FM_Head)
        FM_df.to_csv(self.FilterMaskTablePath, index=None)
        # generate csv used for Batch Xsection
        Xsec_df = pd.DataFrame(self.XsectionTable, columns=Xsection_Head)
        Xsec_df.to_csv(self.XsectionTablePath, index=None)
        # generate csv used for Batch Lumen Correction
        XsecFix_df = pd.DataFrame(self.XsectionFixTable, columns=XsecFix_Head)
        XsecFix_df.to_csv(self.XsectionFixTablePath, index=None)
        # generate csv used for batch extension
        XsecFixExt_df = pd.DataFrame(self.XsectionFixExtTable, columns=Extension_Head)
        XsecFixExt_df.to_csv(self.XsectionFixExtTablePath, index=None)
        # generate csv used for batch xsection original volume
        OriVolume_df = pd.DataFrame(self.OriVolumeTable, columns=OriVolume_Head)
        OriVolume_df.to_csv(self.OriVolumeTablePath, index=None)
        # stack segmentation
        SS_df = pd.DataFrame(self.SSTable, columns=SS_Head)
        SS_df.to_csv(self.SSTablePath, index=None)
        # stl generation
        SG_df = pd.DataFrame(self.SGTable, columns=SG_Head)
        SG_df.to_csv(self.SGTablePath, index=None)
        # murray's law
        AVC_df = pd.DataFrame(self.AVCTable, columns=AVCBatch_Head)
        AVC_df.to_csv(self.AVCTablePath, index=None)
        # generate csv used for Batch Lumen Correction
        XsecFix_df = pd.DataFrame(self.OriVolumeFixTable, columns=XsecFixOri_Head)
        XsecFix_df.to_csv(self.OriVolumeFixTablePath, index=None)

        CFD_Mesh_df = pd.DataFrame(self.CFD_MeshTable, columns=CFD_Mesh_Head)
        CFD_Mesh_df.to_csv(self.CFD_MeshTablePath, index=None)

        CFD_STLcut_df = pd.DataFrame(self.CFD_STLcutTable, columns=CFD_STLcut_Head)
        CFD_STLcut_df.to_csv(self.CFD_STLcutTablePath, index=None)

        CFD_STLmesh_df = pd.DataFrame(self.CFD_STLmeshTable, columns=CFD_STLmesh_Head)
        CFD_STLmesh_df.to_csv(self.CFD_STLmeshTablePath, index=None)

        CFD_FindFace_df = pd.DataFrame(self.CFD_FindFaceTable, columns=CFD_FindFace_Head)
        CFD_FindFace_df.to_csv(self.CFD_FindFaceTablePath, index=None)

        CFD_GenerateIn_df = pd.DataFrame(self.CFD_GenerateInTable, columns=CFD_GenerateIn_Head)
        CFD_GenerateIn_df.to_csv(self.CFD_GenerateInTablePath, index=None)

        CFD_PostProgress_df = pd.DataFrame(self.CFD_PostProgressTable, columns=CFD_Postprogress_Head)
        CFD_PostProgress_df.to_csv(self.CFD_PostProgressTablePath, index=None)

        CFD_DataOutput_df = pd.DataFrame(self.DataOutputTable, columns=CFD_DataOutput_Head)
        CFD_DataOutput_df.to_csv(self.DataOutputTablePath, index=None)

        CFD_PostNpy_df = pd.DataFrame(self.PostNpyTable, columns=CFD_PostNpy_Head)
        CFD_PostNpy_df.to_csv(self.PostNpyTablePath, index=None)

        CFD_Map_Result_df = pd.DataFrame(self.Map_ResultTable, columns=CFD_Map_Result_Head)
        CFD_Map_Result_df.to_csv(self.Map_ResultTablePath, index=None)

        CFD_FFRCalculation_df = pd.DataFrame(self.FFRCalculationTable, columns=CFD_FFRCalculation_Head)
        CFD_FFRCalculation_df.to_csv(self.FFRCalculationTablePath, index=None)

        CFD_Paraview_df = pd.DataFrame(self.ParaviewTable, columns=CFD_Paraview_Head)
        CFD_Paraview_df.to_csv(self.ParaviewTablePath, index=None)

        CFD_SaveVtu_df = pd.DataFrame(self.SaveVtuTable, columns=CFD_Savevtu_Head)
        CFD_SaveVtu_df.to_csv(self.SaveVtuTablePath, index=None)

    def BatchFilterMask(self):
        # FilterMaskClass = self.model.filterMask(UI=self.model.FilterMaskui,Hedys=self.model)
        # FilterMaskClass = FilterMaskMain.FilterMask()
        # FilterMaskClass.BatchProcessing(self.FilterMaskTablePath)
        self.model.filterMask.BatchProcessing(self.FilterMaskTablePath)

    # create Xsection Object and batch process
    def BatchXsection(self):
        # Xsection = self.model.centerlineXsection(UI=self.model.CenterlineXsecui,Hedys=self.model)
        # Xsection = CenterlineXsectionMain.Xsection()
        # Xsection.BatchConvert(InputCSVPath=self.XsectionTablePath)
        self.model.centerlineXsection.BatchConvert(InputCSVPath=self.XsectionTablePath)

    # create Lumen Correction Object and batch process
    def BatchLumenCorrection(self):
        # lumen correction
        cmd1 = self.CopyCommand(
            self.ui.LumenCorrectionPath_Txt_BPP.toPlainText(),
            self.TableDir
        )
        os.system(cmd1)

        # LumenCorrect = LumenCorrectMain.LumCorrect()
        # LumenCorrect.BatchCorrect(CSVPath=self.XsectionFixTablePath)
        self.model.lumenCorrect.BatchCorrect(CSVPath=self.XsectionFixTablePath)

    # create Ori-Volume Correction Object and batch process
    def BatchOriVolumeCorrection(self):
        # lumen correction
        cmd1 = self.CopyCommand(
            self.ui.OriVolumePath_Txt_BPP.toPlainText(),
            self.TableDir
        )
        os.system(cmd1)


        # OriVCorrect = LumenCorrectMain.LumCorrect()
        # OriVCorrect.BatchCorrect(CSVPath=self.OriVolumeFixTablePath)
        self.model.lumenCorrect.BatchCorrect(CSVPath=self.OriVolumeFixTablePath)

    # create Extension Object and execute batch process
    def BatchExtension(self):
        print('in')
        # Ext = MaskExtensionMain.MaskExtension()
        print(self.XsectionFixExtTablePath)
        # Ext.BatchProcess(path=self.XsectionFixExtTablePath)
        self.model.maskExtension.BatchProcess(path=self.XsectionFixExtTablePath)

    # create OriVolume Object and batch process
    def BatchXsecOriVolume(self):
        # OriVol = XsectionOriVolumeMain.OriVolume()
        # OriVol.BatchProcessing(CSVPath=self.OriVolumeTablePath, EXEPath=self.CPREXEPath)
        self.model.oriVolume.BatchProcessing(CSVPath=self.OriVolumeTablePath, EXEPath=self.CPREXEPath)

    # create SS object and batch process
    def SSSSGridMan(self):
        # copy aorta
        for loopIndex in range(len(self.XsectionFixPathList)):
            cmd1 = self.CopyCommand(
                os.path.join(self.XsectionFixPathList[loopIndex], 'AortaFixVal.nii.gz'),
                self.OriVolumePathList[loopIndex]
            )
            os.system(cmd1)

        # SS = StackSegmentMain.StackSegment()
        # SS.BatchProcessing(CSVPath=self.SSTablePath)
        self.model.stackSegment.BatchProcessing(CSVPath=self.SSTablePath)

    # create Batch Mask2STL object and execute batch process
    def BatchMaskStl(self):
        # MS = MaskSTLMain.MaskSTL()
        # MS.BatchConvert(CSVPath=self.SGTablePath, choice=3)
        self.model.maskSTL.BatchConvert(CSVPath=self.SGTablePath, choice=3)

    def BatchMurraysLaw(self):
        # areaVolCalcs = AreaVolumeCalcsMain.AreaVolCalcs(self.UI)
        # areaVolCalcs.BatchAutoType3(tablePath=self.AVCTablePath)
        self.model.areaVolCalcs.BatchAutoType3(tablePath=self.AVCTablePath)

        # copy Aorta files
        aorOut_AVC = self.ui.AVCPath_Txt_BPP.toPlainText() + '/Aor_in.txt'
        aorIn_AVC = self.ui.AVCPath_Txt_BPP.toPlainText() + '/Aor_out.txt'
        aorOutFFR_AVC = self.ui.AVCPath_Txt_BPP.toPlainText() + '/Aor_outFFR.txt'
        for loopIndex in range(len(self.ArVolCalPathList)):
            # copy to all subdirectories
            subfolderPaths = [f.path for f in os.scandir(self.ArVolCalPathList[loopIndex]) if f.is_dir()]
            for subfolder in subfolderPaths:
                # copy aorta files
                cmd1 = self.CopyCommand(aorOut_AVC, subfolder)
                cmd2 = self.CopyCommand(aorIn_AVC, subfolder)
                cmd3 = self.CopyCommand(aorOutFFR_AVC, subfolder)
                os.system(cmd1)
                os.system(cmd2)
                os.system(cmd3)
                self.UpdateMsgLog(str(cmd1))
                self.UpdateMsgLog(str(cmd2))
                self.UpdateMsgLog(str(cmd3))

        BloodPressureAndHeartRate_Head = ['Blood Pressure And Heart Rate', 'Reference CSV path', 'Output CSV path',
                                          'CalculatePressurePa', 'CalculatePressure', 'CalculateCardiacCycle',
                                          'CalculatePressureCoefficent', 'CalculateHeartRateCoefficent',
                                          'Linear Regression', 'Linear Regression Timestart',
                                          'Systolic Blood Pressure (mmHg)', 'Diastolic Blood Pressure (mmHg)',
                                          'Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Mean Blood Pressure',
                                          'Pressure Difference', 'Mean Presure Coefficient',
                                          'Pressure Difference Coefficient', 'Heart Rate', 'Cardiac Cycle',
                                          'Heart Rate Coefficient']

        BloodPressureAndHeartRatePath = self.ui.BloodPressureAndHeartRatePath_Txt_BPP.toPlainText()
        # load DFs
        dfBloodPressureAndHeartRateTable = Pd_Funs.OpenDF(inPath=BloodPressureAndHeartRatePath, header=0, usecols=None)

        inflow = ['Aor_in']
        MeanPresureCoefficient = ''
        BloodPressureCoefficient = ''
        HeartRateCoefficient = 1
        SystolicBloodPressuremmHg = 122.5
        DiastolicBloodPressuremmHg = 62.2
        HeartRate = 67
        for loopIndex in range(len(self.ArVolCalPathList)):
            BloodPressureAndHeartRate = dfBloodPressureAndHeartRateTable.iloc[loopIndex]
            # copy to all subdirectories
            subfolderPaths = [f.path for f in os.scandir(self.ArVolCalPathList[loopIndex]) if f.is_dir()]
            BloodPressureAndHeartRateTable = []
            for subfolder in subfolderPaths:
                flowpaths = [f.path for f in os.scandir(subfolder) if f.is_file()]
                try:
                    if BloodPressureAndHeartRate["Systolic Blood Pressure (mmHg)"]:
                        SystolicBloodPressuremmHg = BloodPressureAndHeartRate["Systolic Blood Pressure (mmHg)"]
                except:
                    pass
                try:
                    if BloodPressureAndHeartRate["Diastolic Blood Pressure (mmHg)"]:
                        DiastolicBloodPressuremmHg = BloodPressureAndHeartRate["Diastolic Blood Pressure (mmHg)"]
                except:
                    pass
                try:
                    if BloodPressureAndHeartRate["Heart Rate"]:
                        HeartRate = BloodPressureAndHeartRate["Heart Rate"]
                except:
                    pass
                for flowpath in flowpaths:
                    (flowpathonly, flowpathname) = os.path.split(flowpath)
                    (flowpathnameonly, flowpathnamesuffix) = os.path.splitext(flowpathname)
                    if flowpathnameonly not in inflow:
                        MeanPresureCoefficient = 1
                        BloodPressureCoefficient = 1
                    tmpBloodPressureAndHeartRateTable = [True, flowpath, flowpath, True, True, True, True, True, True,
                                                         2, SystolicBloodPressuremmHg, DiastolicBloodPressuremmHg, '',
                                                         '', '', '', MeanPresureCoefficient, BloodPressureCoefficient,
                                                         HeartRate, '', HeartRateCoefficient]
                    BloodPressureAndHeartRateTable.append(tmpBloodPressureAndHeartRateTable)

            # save branch table
            BloodPressureAndHeartRateFilePath = os.path.join(self.ArVolCalPathList[loopIndex],
                                                             'BloodPressureAndHeartRate.csv')
            BloodPressureAndHeartRate_df = pd.DataFrame(BloodPressureAndHeartRateTable,
                                                        columns=BloodPressureAndHeartRate_Head)
            BloodPressureAndHeartRate_df.to_csv(BloodPressureAndHeartRateFilePath, index=None)

    def BatchBloodPressureAndHeartRate(self):
        for loopIndex in range(len(self.ArVolCalPathList)):
            BloodPressureAndHeartRateFilePath = os.path.join(self.ArVolCalPathList[loopIndex],
                                                             'BloodPressureAndHeartRate.csv')
            self.model.BloodPressureAndHeartRate.batchBloodPressureAndHeartRate(
                tablePath=BloodPressureAndHeartRateFilePath)

    # create MeshCut Object and batch process
    def BatchMeshCut(self):
        # MeshCut = CuttingMeshTest.Interaction(self.UI)
        # MeshCut.batchrun(CSVPath=self.CFD_STLcutTablePath)
        self.model.MeshCut.batchrun(CSVPath=self.CFD_STLcutTablePath)

    # create Mesh Object and batch process
    def BatchMesh(self):
        # Mesh = MeshGeneratingMain.MeshGenerating(self.UI)
        # Mesh.batchrun(CSVPath=self.CFD_STLmeshTablePath)
        self.model.Meshgeneration.batchrun(CSVPath=self.CFD_STLmeshTablePath)

    # create FindFace Object and batch process
    def BatchFindFace(self):
        # FindFace = SplitFaceElemMain.SplitFaceElem(self.UI)
        # FindFace.batchrun(CSVPath=self.CFD_FindFaceTablePath)
        self.model.SplitFaceElem.batchrun(CSVPath=self.CFD_FindFaceTablePath)

    # create GenerateInput Object and batch process
    def BatchGenerateInput(self):
        # GenerateInput = Generate_In_File.GenerateInputFile(self.UI)
        # GenerateInput.batchrun(CSVPath=self.CFD_GenerateInTablePath)
        self.model.Finfilegneration.batchrun(CSVPath=self.CFD_GenerateInTablePath)

    # create DataOutput Object and batch process
    def BatchDataOutput(self):
        # DataOutput = ADINA_DataOutputMain.ADINA_DataOutput(self.UI)
        # DataOutput.batchrun(CSVPath=self.DataOutputTablePath)
        self.model.adina_DataOutput.batchrun(CSVPath=self.DataOutputTablePath)

    # create CFD_PostProcessing Object and batch process
    def BatchCFD_PostProcessing(self):
        # CFD_PostProcessing = CalcCFDResultMain.CFDParameters(self.UI)
        # CFD_PostProcessing.batchrun(CSVPath=self.PostNpyTablePath)
        self.model.CFDParameters.batchrun(CSVPath=self.PostNpyTablePath)

    # create MapResult Object and batch process
    def BatchMapResult(self):
        # MapResult = MapResultsMain.MapResults(self.UI)
        # MapResult.Batch(DFPath=self.Map_ResultTablePath)
        self.model.mapResults.Batch(DFPath=self.Map_ResultTablePath)

    # create FFRcalculation Object and batch process
    def BatchFFRcalculation(self):
        # FFRcalculation = FFRCalcsMain.FFRCalcs(self.UI)
        # FFRcalculation.batchrun(CSVPath=self.FFRCalculationTablePath)
        self.model.FFR.batchrun(CSVPath=self.FFRCalculationTablePath)

    # create Paraview-processing Object and batch process
    def BatchParaview_processing(self):
        # Paraview_processing = PostProcessingMain.PostProcessing(self.UI)
        # Paraview_processing.batchrun(CSVPath=self.ParaviewTablePath)
        self.model.ParaviewPostProcessing.batchrun(CSVPath=self.ParaviewTablePath)

    # create SaveVTU Object and batch process
    def BatchSaveVTU(self):
        # SaveVTU = SaveVTUMain.SaveVTUorPVD(self.UI)
        # SaveVTU.batchrun(CSVPath=self.SaveVtuTablePath)
        self.model.SaveVTU.batchrun(CSVPath=self.SaveVtuTablePath)

    def mainFunction(self):
        self.initProcess()
        if self.ui:
            self.WorkingDir = self.ui.LoadFolderPath_Txt_BPP.toPlainText()
            self.CGEXEPath = self.ui.CGExePath_Txt_BPP.toPlainText()
            self.CPREXEPath = self.ui.CPRExePath_Txt_BPP.toPlainText()
            self.STLEXEPath = self.ui.STLGExePath_Txt_BPP.toPlainText()
        else:
            self.UpdateMsgLog('No UI')

        # create overall table directory
        self.TableDir = os.path.join(self.WorkingDir, 'Table')

        # cmd english
        os.system('chcp 437')

        # check boxes
        self.CheckCheckBoxStatus()

        # get all case folders & create folders
        self.UpdateMsgLog('Scan DCM & Create Folder Start')
        self.ScanDCMDir()
        for dir in self.DCMDirList:
            self.CreateFolders(CasePath=dir)
        print(str(self.DCMDirList))
        self.UpdateMsgLog('Scan DCM & Create Folder Done')

        # create all paths
        self.StoreListInformation()

        # always create new DICOM to nifti table
        self.GenerateCTATable()

        # DCM to Nifti
        if self.D2NFlag:
            self.UpdateMsgLog('DCM to Nifti Convert Start')
            self.BatchDCM2Nifti()
            self.UpdateMsgLog('DCM to Nifti Convert Done')

        # copy CTA need to be done
        self.CopyCTA()

        # centerline generation
        if self.CGFlag:
            self.BatchCenterlineGen()
            self.UpdateMsgLog('batch centerline generation done')

        # copy Jason for same lists
        self.UpdateMsgLog('Copy JASON Start')
        self.CopyCenterlineJson()
        self.UpdateMsgLog('Copy JASON done')

        # center line extraction
        if self.CenterlineEFlag:
            self.UpdateMsgLog('Centerline Extraction start')
            self.BatchExtractCenterline()
            self.UpdateMsgLog('Centerline Extraction done')

        # create table for update Jason centerline
        self.GenerateJsonUpdateTable()

        # run update jason
        if self.UpdateJasonFlag:
            self.UpdateMsgLog('Jason Update start')
            self.BatchJsonUpdate()
            self.UpdateMsgLog('Jason Update done')

            # auto centerline extraction
            self.UpdateMsgLog('Centerline Extraction start')
            self.BatchExtractCenterline()
            self.UpdateMsgLog('Centerline Extraction done')

        # create branch to be used json file
        if self.BranchDictFlag:
            self.UpdateMsgLog('Write Branch Dictionary start')
            self.CheckWriteDict()
            self.UpdateMsgLog('Write Branch Dictionary done')

        # generate table
        if self.GenerateTFlag:
            self.UpdateMsgLog('Generate Table start')
            print(self.BranchPathList)
            self.GenerateTable()
            self.UpdateMsgLog('Generate Table done')

        # Filter mask
        if self.FMFlag:
            self.BatchFilterMask()
            # copy aorta
            # self.CopyAorta2OriVolumeFolder()

        if self.XsecFlag:
            self.UpdateMsgLog('Xsection start')
            self.BatchXsection()
            self.UpdateMsgLog('Xsection Done')

        if self.LCFlag:
            self.UpdateMsgLog('LC TEST')
            BatchCoronary.WriteAortaFixCsv(dstPath=self.AortaFixTablePath)
            self.UpdateMsgLog('Write Aorta Fix CSV done')

            self.BatchLumenCorrection()
            self.UpdateMsgLog('Lumen Correction Done')

        if self.ExtFlag:
            self.UpdateMsgLog('Extension Start')
            self.BatchExtension()
            self.UpdateMsgLog('Extension Done')

        if self.XsecOriFlag:
            self.BatchXsecOriVolume()
            self.UpdateMsgLog('Xsection OriVolume Done')

        if self.OriVolumeFixFlag:
            self.UpdateMsgLog('OriVolume Correction Start')
            self.BatchOriVolumeCorrection()
            self.UpdateMsgLog('OriVolume Correction Done')

        if self.SSFlag:
            self.SSSSGridMan()
            self.UpdateMsgLog('Stack Segmentation Done')

        if self.M2SFlag:
            self.BatchMaskStl()
            self.UpdateMsgLog('Mask to STL done')

        if self.ArVolCalFlag:
            self.BatchMurraysLaw()
            self.UpdateMsgLog("Murray's Law done")

        if self.ui.BloodPressureAndHeartRate_BPP.isChecked():
            self.BatchBloodPressureAndHeartRate()
            self.UpdateMsgLog("Blood Pressure And Heart Rate Input")

        if self.MeshCut:
            self.BatchMeshCut()
            self.UpdateMsgLog("MeshCut done")

        if self.Mesh:
            self.BatchMesh()
            self.UpdateMsgLog("Mesh done")

        if self.FindFace:
            cmd1 = self.CopyCommand(self.ui.setPath_Txt_BPP.toPlainText(),self.TableDir)
            os.system(cmd1)
            self.BatchFindFace()
            self.UpdateMsgLog("FindFace done")

        if self.GenerateInput:
            self.BatchGenerateInput()
            self.UpdateMsgLog("GenerateInput done")

        if self.DataOutput:
            self.BatchDataOutput()
            self.UpdateMsgLog("DataOutput done")

        if self.CFD_PostProcessing:
            self.BatchCFD_PostProcessing()
            self.UpdateMsgLog("CFD_PostProcessing done")

        if self.MapResult:
            self.BatchMapResult()
            self.UpdateMsgLog("MapResult done")

        if self.FFRcalculation:
            self.BatchFFRcalculation()
            self.UpdateMsgLog("FFRcalculation done")

        if self.Paraview_processing:
            self.BatchParaview_processing()
            self.UpdateMsgLog("Paraview_processing done")

        if self.SaveVTU:
            self.BatchSaveVTU()
            self.UpdateMsgLog("SaveVTU done")

        # init process
        self.initProcess()

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


if __name__ == '__main__':
    a = BatchCoronary()
    a.mainFunction()
