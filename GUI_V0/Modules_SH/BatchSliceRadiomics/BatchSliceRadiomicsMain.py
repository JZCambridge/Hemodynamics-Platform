import os
import shutil
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
from Modules_YL.BatchCoronary import BatchCoronaryMain
from Modules_YL.BatchCoronary import BranchDictionary


class BatchSliceRadiomics:
    def __init__(self, UI=None, Hedys=None):
        # UI update
        self.ui = None
        if UI:
            self.ui = UI

            # Button connection
            self.ui.LoadFolderPath_Btn_BSRJZ.clicked.connect(lambda: self.ChooseWorkingDir())
            self.ui.ChooseCPRExePathBtn_2_BPP.clicked.connect(lambda: self.ChooseCPRExePath())
            self.ui.ChooseLumenCorrectionPathBtn_BPP.clicked.connect(lambda: self.ChooseLumenCorretionPath())
            self.ui.RunBtn_CPP.clicked.connect(lambda: self.mainFunction())
        else:
            self.UpdateMsgLog('No UI')

        # set overall structure
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            self.model = Hedys
            self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
        else:
            self.UpdateMsgLog('No Platform!')

    # init process:
    def initProcess(self):
        self.WorkingDir = None
        self.CopyOriginDir = None
        self.CPREXEPath = None  # cpr exe path

        self.DCMDirList = []
        self.CTANewFilePathList = None
        self.CTANewPathList = None
        self.CTADirList = []  # store the cta location, include file name

        self.leftCenterlineJsonList = []  # centerline L json file positions
        self.rightCenterlineJsonList = []  # centerline R json file positions

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
        self.OriVolumePathList = []  # store the absolute paths of OriVolume folder list
        self.FinalMaskPathList = []  # store the absolute paths of final mask file path list
        self.StlFilePathList = []  # store the absolute paths of stl file path list

        self.DictionaryPath = None  # store the absolute path of branch that required
        self.BatchDCMTablePath = None  # store the absolute path of branch that required
        self.JasonUpdateTablePath = None  # store the absolute path of Jason update
        self.FilterMaskTable = []  # store the columns of filter mask single branch
        self.FilterMaskTablePath = None
        self.XsectionTable = []
        self.XsectionTablePath = None
        self.XsectionFixTable = []
        self.XsectionFixTablePath = None
        self.LCProcessPath = None
        self.XsectionFixExtTable = []
        self.XsectionFixExtTablePath = None
        self.OriVolumeTable = []
        self.OriVolumeTablePath = None
        self.SSTable = []
        self.SSTablePath = None
        self.SGTable = []  #
        self.SGTablePath = None  # store the stl generate table path

        self.TableDir = None
        self.CTANewFilePathList = None

    # if ui inserted, Check box status to pend if certain process shall be running
    def CheckCheckBoxStatus(self):
        self.CopyFileFlag = self.ui.CopyFile_CB_BSRJZ.isChecked()
        self.ScanFileFlag = self.ui.ScanFile_CB_BSRJZ.isChecked()
        self.CreateFolderFlag = self.ui.CreateFolders_CB_BSRJZ.isChecked()
        self.BranchDictFlag = self.ui.BranchDict_CB_BSRJZ.isChecked()
        self.GenerateTFlag = self.ui.GenerateTable_CB_BSRJZ.isChecked()
        self.FMFlag = self.ui.FM_CB_BSRJZ.isChecked()
        self.XsecFlag = self.ui.Xsection_CB_BSRJZ.isChecked()
        self.LCFlag = self.ui.LumenCorrection_CB_BSRJZ.isChecked()

    def timmer(func):
        def warpper(self, *args, **kwargs):
            start_time = time.time()
            func(self)
            stop_time = time.time()
            print('{} run time is {}'.format(func.__name__, stop_time - start_time))

        return warpper

    '''
    ##############################################################################
    # Choose files and folders
    ##############################################################################
    '''

    def ChooseWorkingDir(self):
        dirname = Save_Load_File.OpenDirPathQt(dispMsg='Working Directory',
                                               fileObj=self.ui,
                                               qtObj=True)
        self.ui.LoadFolderPath_Txt_BSRJZ.setPlainText(dirname)

    def ChooseCopyOriginDir(self):
        dirname = Save_Load_File.OpenDirPathQt(dispMsg='Copying from Which Directory?',
                                               fileObj=self.ui,
                                               qtObj=True)
        self.ui.CopyOriginFolderPath_Txt_BSRJZ.setPlainText(dirname)

    # used to choose CPR exe path
    def ChooseCPRExePath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load CPR Exe file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.CPRExePath_Txt_BPP.setPlainText(filename)

    # used to choose lumen correction path
    def ChooseLumenCorretionPath(self):
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg='Load Lumen Correction file',
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.LumenCorrectionPath_Txt_BPP.setPlainText(filename)

    '''
    ##############################################################################
    # Other functions
    ##############################################################################
    '''

    def ScanDCMDir(self):
        for root, dirs, files in os.walk(self.WorkingDir):
            for file in files:
                if file.endswith('.dcm') or file.endswith('.DCM') or (".DCM" in file):
                    self.DCMDirList.append(root)
                    break

    def ScanCTADir(self):
        # non-transverse get current folders
        childDirs = Save_Load_File.ReturnFoldersFullPath(dirPath=self.WorkingDir,
                                                         folderSearch=None,
                                                         traverse=False)
        # check dirs
        for childDir in childDirs:
            for root, dirs, files in os.walk(childDir):
                for file in files:
                    if "CTA.nii.gz" in file:
                        if childDir not in self.DCMDirList:
                            self.DCMDirList.append(Save_Load_File.standardFolderSeperation(childDir))

                        break

    def CreateFoldersDCM(self):
        # create necessary folders under all folders
        for dir in self.DCMDirList:
            self.CreateFolders(CasePath=dir)

    # input path then create structured folder under this folder
    def CreateFolders(self, CasePath=None):
        CTADir = os.path.join(CasePath, 'CTA')
        PreProcPath = os.path.join(CasePath, 'Preproc')
        OriDataPath = os.path.join(PreProcPath, 'OriData')
        BranchPath = os.path.join(OriDataPath, 'Branches')
        CSVPath = os.path.join(PreProcPath, 'CSV')
        XsectionPath = os.path.join(PreProcPath, 'Xsection')

        BatchCoronaryMain.BatchCoronary.CreateSingleFolder(self.TableDir)
        BatchCoronaryMain.BatchCoronary.CreateSingleFolder(CTADir)
        BatchCoronaryMain.BatchCoronary.CreateSingleFolder(PreProcPath)
        BatchCoronaryMain.BatchCoronary.CreateSingleFolder(OriDataPath)
        BatchCoronaryMain.BatchCoronary.CreateSingleFolder(BranchPath)
        BatchCoronaryMain.BatchCoronary.CreateSingleFolder(CSVPath)
        BatchCoronaryMain.BatchCoronary.CreateSingleFolder(XsectionPath)

    # store the required path information as list
    def StoreListInformation(self):
        for path in self.DCMDirList:
            self.OriDataPathList.append(os.path.join(path, 'Preproc/OriData'))
            self.CSVPathList.append(os.path.join(path, 'Preproc/CSV'))
            self.BranchPathList.append(os.path.join(path, 'Preproc/OriData/Branches'))
            self.XsectionPathList.append(os.path.join(path, 'Preproc/Xsection'))
            self.OriVolumePathList.append(os.path.join(path, 'Preproc/OriVolume'))

        # CTA path
        self.CTADirList = [os.path.join(x, 'CTA\CTA.nii.gz') for x in self.DCMDirList]

        # generate table paths
        self.DictionaryPath = os.path.join(self.TableDir, 'coronarySegments.json')
        self.FilterMaskTablePath = os.path.join(self.TableDir, 'FilterMask.csv')
        self.XsectionTablePath = os.path.join(self.TableDir, 'Xsection.csv')
        self.XsectionFixTablePath = os.path.join(self.TableDir, 'XsectionFix.csv')
        self.LCProcessPath = os.path.join(self.TableDir, 'LCProcess.csv')

    @staticmethod
    # generate windows command line
    def CopyCommand(source=None, dst=None):
        source = source.replace('/', '\\')
        dst = dst.replace('/', '\\')

        shutil.copy(source, dst)

        cmd = 'copy {} {}'.format(source, dst)
        cmd = cmd.replace('/', '\\')
        return cmd

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
        if self.ui.pmdCx_CB_BSRJZ.isChecked(): branchLst.append("LCx")
        if self.ui.pmdLAD_CB_BSRJZ.isChecked(): branchLst.append("mLAD")
        if self.ui.pmdRCA_CB_BSRJZ.isChecked(): branchLst.append("mRCA")

        # ignore coordinate list
        ignoreCoordsLst = Preprocess_Mask.StrToLst(strIn=self.ui.ignoreCheck_Txt_BSRJZ.toPlainText())["listOut"]

        print("Selected branches:\n{}".format(branchLst))

        BranchDictionary.WriteDic(Outpath=self.DictionaryPath, branchLst=branchLst)
        for CSVPath in self.CSVPathList:
            # validate which branch can be used for each case
            tempJsonList = self.ReturnJsonList(CSVPath)
            UseJsonPath = os.path.join(CSVPath, 'coronarySegmentsUse.json')
            BranchDictionary.ValidateUse(dicPath=self.DictionaryPath,
                                         jsonList=tempJsonList,
                                         outputPath=UseJsonPath,
                                         ignoreCoordsLst=ignoreCoordsLst,
                                         checkParent=False, checkSecondary=False)

    # create Filter Mask Object and batch process
    def GenerateTable(self, resampleDepth='0.1', cpus='2', CPRAngle='0', maskXsection=False):
        # define table column titles
        FM_Head = ['MaskPath', 'MaskVal', 'NewMaskVal', 'OutputFolder', 'FileNameRef']

        Xsection_Head = ['inputDir', 'inputCSVDir', 'outputDir', 'outputCSVDir', 'resampleDepth',
                         'CPRAngle', 'cpus', 'casePath', 'EXEPath']

        Case_Head = ['Interpolation', 'OutCSV', 'inputImagePath', 'inputCSVPath', 'outputImagePath', 'outputCSVPath']

        XsecFix_Head = ['Image Path', 'Mask Path', 'Process Path', 'Fill Original Value', 'Output Directory',
                        'Output Name']

        # parameters
        ## Xsection case file
        interpolation_xsimg = '0'  # linear interpolation
        outputCSV_xsimg = '0'  # no output
        interpolation_xsmsk = '1'  # nearest neighbour
        outputCSV_xsmsk = '1'  # csv output

        # print results
        print('Resample Depth: ', resampleDepth)
        print('CPUs: ', cpus)
        print('Mask Xsection: ', maskXsection)

        for CSVPath in self.CSVPathList:
            loopIndex = self.CSVPathList.index(CSVPath)
            tmpMaskPath = os.path.join(self.OriDataPathList[loopIndex], 'sc_labelled_coronary_segment.nii.gz')
            tmpOutputPath = self.BranchPathList[loopIndex]

            # initialize case table
            tempCaseTable = []
            tempBranchList = []
            tempBranchLblist = []

            # validate the existence of json file first
            UseJsonPath = os.path.join(CSVPath, 'coronarySegmentsUse.json')
            with open(UseJsonPath) as f:
                case = json.load(f)

            for branch in case:
                if branch['use']:
                    # store used branch for later Stack Segmentation use
                    tempBranchList.append(branch['original_volume_mask_fix'].replace('.nii.gz', 'Val.nii.gz'))
                    tempBranchLblist.append(str(branch['label'][0]))

                    # filter mask table
                    tempFMColumn = [tmpMaskPath, str(branch['label']), '1', tmpOutputPath, branch['original_branch']]
                    self.FilterMaskTable.append(tempFMColumn)

                    # generate image Xsection table columns for branches for each case
                    tempCaseColumn1 = [interpolation_xsimg,
                                       outputCSV_xsimg,
                                       'CTA.nii.gz',
                                       branch['original_csv'],
                                       branch['cross_section_image_LI'],
                                       branch['3D_csv']]
                    tempCaseTable.append(tempCaseColumn1)

                    # generate mask Xsection table columns for branches for each case
                    if maskXsection:
                        tempCaseColumn2 = [interpolation_xsmsk,
                                           outputCSV_xsmsk,
                                           branch['original_branch'] + 'Val.nii.gz',
                                           branch['original_csv'],
                                           branch['cross_section_mask_NN'],
                                           branch['3D_csv']]
                        tempCaseTable.append(tempCaseColumn2)

                    # insert columns into xsection fix table
                    XsecCTAPath = os.path.join(self.XsectionPathList[loopIndex], branch['cross_section_image_LI'])
                    XsecMaskPath = os.path.join(self.XsectionPathList[loopIndex], branch['cross_section_image_LI'])
                    tmpXsecFixColumn = [XsecCTAPath,
                                        XsecMaskPath,
                                        self.LCProcessPath,
                                        'No',
                                        self.XsectionPathList[loopIndex],
                                        branch['original_csv'].replace('.csv', '6mm')]

                    self.XsectionFixTable.append(tmpXsecFixColumn)
                else:
                    continue

            # Xsection generation case table csv file for each case
            caseFilePath = os.path.join(CSVPath, 'case.csv')
            case_df = pd.DataFrame(tempCaseTable, columns=Case_Head)
            case_df.to_csv(caseFilePath, index=None)

            # add record to overall Xsection table
            self.XsectionTable.append([self.BranchPathList[loopIndex],
                                       CSVPath,
                                       self.XsectionPathList[loopIndex],
                                       self.XsectionPathList[loopIndex],
                                       resampleDepth,
                                       CPRAngle,
                                       cpus,
                                       caseFilePath,
                                       self.CPREXEPath])

        # generate csv used for batch filter mask processing
        FM_df = pd.DataFrame(self.FilterMaskTable, columns=FM_Head)
        FM_df.to_csv(self.FilterMaskTablePath, index=None)
        # generate csv used for Batch Xsection
        Xsec_df = pd.DataFrame(self.XsectionTable, columns=Xsection_Head)
        Xsec_df.to_csv(self.XsectionTablePath, index=None)
        # generate csv used for Batch Lumen Correction
        XsecFix_df = pd.DataFrame(self.XsectionFixTable, columns=XsecFix_Head)
        XsecFix_df.to_csv(self.XsectionFixTablePath, index=None)

    def BatchFilterMask(self):
        self.model.filterMask.BatchProcessing(self.FilterMaskTablePath)

    # create Xsection Object and batch process
    def BatchXsection(self):
        self.model.centerlineXsection.BatchConvert(InputCSVPath=self.XsectionTablePath)

    # create Lumen Correction Object and batch process
    def BatchLumenCorrection(self):
        # lumen correction
        cmd1 = self.CopyCommand(
            self.ui.LumenCorrectionPath_Txt_BSRJZ.toPlainText(),
            self.TableDir
        )
        print(cmd1)

        self.model.lumenCorrect.BatchCorrect(CSVPath=self.XsectionFixTablePath)


    '''
    ##############################################################################
    # Main Function
    ##############################################################################
    '''

    def mainFunction(self):
        # initialisation
        self.initProcess()

        # Process Check
        self.CheckCheckBoxStatus()

        # get file/fodler paths
        if self.ui:
            self.WorkingDir = self.ui.LoadFolderPath_Txt_BSRJZ.toPlainText()
            self.CopyOriginDir = self.ui.CopyOriginFolderPath_Txt_BSRJZ.toPlainText()
            self.CPREXEPath = self.ui.CPRExePath_Txt_BSRJZ.toPlainText()
        else:
            self.UpdateMsgLog('No UI')

        # create overall table directory
        self.TableDir = os.path.join(self.WorkingDir, 'Table')

        # copy files from initial directory first and work in the new directory
        if self.CopyFileFlag:
            self.UpdateMsgLog('Copy Files Start')
            Save_Load_File.BatchCopyFiles(fromFolder=self.CopyOriginDir,
                                          toFolder=self.WorkingDir,
                                          fileRefs=Preprocess_Mask.StrToLst(self.ui.fileRefs_Txt_BSRJZ.toPlainText())["listOut"],
                                          numberLimit=int(self.ui.numberLimit_Txt_BSRJZ.toPlainText()))
            self.UpdateMsgLog('Copy Files Done')

        # get all case folders & create folders
        if self.ScanFileFlag:
            self.UpdateMsgLog('Scan DCM Folders Start')
            self.ScanDCMDir()
            print("Find DCM folders")
            print(str(self.DCMDirList))
            self.UpdateMsgLog('Scan DCM Folders Stop')
        else:
            self.UpdateMsgLog('Scan CTA Folders Start')
            self.ScanCTADir()
            print("Find CTA folders")
            print(str(self.DCMDirList))
            self.UpdateMsgLog('Scan CTA Folders Stop')

        # create folders
        if self.CreateFolderFlag:
            self.UpdateMsgLog('Create Folders Start')
            self.CreateFoldersDCM()
            self.UpdateMsgLog('Create Folders Done')

        # create all paths
        self.StoreListInformation()

        # create branch to be used json file
        if self.BranchDictFlag:
            self.UpdateMsgLog('Write Branch Dictionary start')
            self.CheckWriteDict()
            self.UpdateMsgLog('Write Branch Dictionary done')

        # generate table
        if self.GenerateTFlag:
            self.UpdateMsgLog('Generate Table start')
            print(self.BranchPathList)
            self.GenerateTable(resampleDepth=self.ui.resampleDepthLineTxt_BSRJZ.text(),
                               cpus=self.ui.cpusLineTxt_BSRJZ.text(),
                               maskXsection=self.ui.maskXsection_CB_BSRJZ.isChecked())
            self.UpdateMsgLog('Generate Table done')

        # Filter mask
        if self.FMFlag:
            self.BatchFilterMask()

        if self.XsecFlag:
            self.UpdateMsgLog('Xsection start')
            self.BatchXsection()
            self.UpdateMsgLog('Xsection Done')

        if self.LCFlag:
            self.UpdateMsgLog('Lumen Correction Start')
            self.BatchLumenCorrection()
            self.UpdateMsgLog('Lumen Correction Done')

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
