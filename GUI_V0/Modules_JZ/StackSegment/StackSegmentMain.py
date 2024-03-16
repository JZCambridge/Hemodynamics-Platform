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
import Pd_Funs

# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
# Import functions
import Save_Load_File
import Image_Process_Functions
import Preprocess_Mask
import Post_Image_Process_Functions
##############################################################################

##############################################################################
# Standard libs
import os
from datetime import datetime
from PySide2.QtUiTools import QUiLoader

##############################################################################

class StackSegment:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseCTABtn_SS.clicked.connect(lambda: self.ChooseOpenFile())
        self.ui.loadBtn_SS.clicked.connect(lambda: self.LoadData())
        self.ui.chooseLoadDirBtn_SS.clicked.connect(lambda: self.ChooseLoadDir())
        self.ui.chooseSaveDirBtn_SS.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.ConvertBtn_SS.clicked.connect(lambda: self.Convert())
        self.ui.ChooseCSVPathBtn_SS.clicked.connect(lambda: self.ChooseTablePath())
        self.ui.BatchProcessingBtn_SS.clicked.connect(lambda: self.BatchProcessing())
        
        self.DataFrame = None
        self.CTA = None

    def ChooseOpenFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Choose reference medical image file",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd) ;; STL files (*.stl)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadImgPathTxt_SS.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseTablePath(self):
        TablePath = Save_Load_File.OpenFilePathQt(
            dispMsg='Choose Batch Table file',
            fileTypes='All files (*.*);; Excel Files (*.csv *.xlsx)',
            fileObj=self.ui,
            qtObj=True
        )

        self.ui.CSVPathTxt_SS.setPlainText(TablePath)

    def LoadData(self):
        # load two data
        self.CTA = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.loadImgPathTxt_SS.toPlainText()
        )
        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(self.ui.loadImgPathTxt_SS.toPlainText()))

    def ChooseLoadDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Load data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.loadDirPathTxt_SS.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose loading dir:\n{}".format(dirname))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_SS.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose saving dir:\n{}".format(dirname))

    def Convert(self):

        # input to list/str
        inputDir = [self.ui.loadDirPathTxt_SS.toPlainText()]
        inputImagePath = Preprocess_Mask.StrToLst(strIn=self.ui.refImgPathTxt_SS.toPlainText())["listOut"]
        inputPaths = Save_Load_File.AppendLists(inputDir, inputImagePath, sep="/")[
            "combineList"]  # forming input lists
        thresVals = Preprocess_Mask.StrToLst(strIn=self.ui.thresValsPathTxt_SS.toPlainText())["floatOut"]

        # output to lst
        ## Get file name
        if self.ui.nameRefTxt_SS.toPlainText() == "":
            name = Save_Load_File.FilenameFromPath(self.ui.loadDirPathTxt_SS.toPlainText())
        else:
            name = Save_Load_File.ValidFileName(self.ui.nameRefTxt_SS.toPlainText())
        ## Set file name
        oneFilePath = Save_Load_File.DateFileName(
            Dir=self.ui.saveDirPathTxt_SS.toPlainText(),
            fileName=name + "One",
            extension=".nii.gz",
            appendDate=False
        )
        # Set file name
        valFilePath = Save_Load_File.DateFileName(
            Dir=self.ui.saveDirPathTxt_SS.toPlainText(),
            fileName=name + "Val",
            extension=".nii.gz",
            appendDate=False
        )

        # Need set new values?
        newVal = self.ui.NewValBtnGrp_SS.checkedButton().text()
        if newVal == "Yes":
            # get new values
            newValLst = Preprocess_Mask.StrToLst(strIn=self.ui.newValPathTxt_SS.toPlainText())["floatOut"]
            # process
            mskAdd = Post_Image_Process_Functions.AddMask(GUI=False)
            mskAdd.AddMskKeepNew(
                loadFilePaths=inputPaths,
                values=newValLst,
                thresholds=thresVals,
                addNwVal=True
            )
            # Save
            Save_Load_File.MatNIFTISave(MatData=mskAdd.stackOnesNoOverLp,
                                        imgPath=oneFilePath["CombineName"],
                                        imgInfo=self.CTA.OriImag,
                                        ConvertDType=True,
                                        refDataMat=self.CTA.OriData)
            Save_Load_File.MatNIFTISave(MatData=mskAdd.stackNewValsNoOverLp,
                                        imgPath=valFilePath["CombineName"],
                                        imgInfo=self.CTA.OriImag,
                                        ConvertDType=True,
                                        refDataMat=self.CTA.OriData)

            # update message
            self.UpdateMsgLog(msg="{} \nSaved: \n{} \n{}".format(mskAdd.rtrnInfo["message"], oneFilePath["CombineName"],
                                                                 valFilePath["CombineName"]))


        elif newVal == "No":
            # process
            mskAdd = Post_Image_Process_Functions.AddMask(GUI=False)
            mskAdd.AddMskKeepNew(
                loadFilePaths=inputPaths,
                values=[0],
                thresholds=thresVals,
                addNwVal=False
            )
            # Save
            Save_Load_File.MatNIFTISave(MatData=mskAdd.stackOnesNoOverLp,
                                        imgPath=oneFilePath["CombineName"],
                                        imgInfo=self.CTA.OriImag,
                                        ConvertDType=True,
                                        refDataMat=self.CTA.OriData)
            Save_Load_File.MatNIFTISave(MatData=mskAdd.stackValsNoOverLp,
                                        imgPath=valFilePath["CombineName"],
                                        imgInfo=self.CTA.OriImag,
                                        ConvertDType=True,
                                        refDataMat=self.CTA.OriData)

            # update message
            self.UpdateMsgLog(msg="{} \nSaved: \n{} \n{}".format(mskAdd.rtrnInfo["message"], oneFilePath["CombineName"],
                                                                 valFilePath["CombineName"]))


        else:
            # update message
            self.UpdateMsgLog(msg="Need choose 'Yes/No' for new values!")

    def BatchProcessing(self, CSVPath=None):
        if CSVPath:
            self.DataFrame = Pd_Funs.OpenDF(CSVPath, header=0)
        else:
            self.DataFrame = Pd_Funs.OpenDF(self.ui.CSVPathTxt_SS.toPlainText(), header=0)
        # print(self.DataFrame)

        for i in range(len(self.DataFrame)):
            inputDir = [self.DataFrame['LoadFolder'][i]]
            print('1')
            self.CTA = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=self.DataFrame['RefImgPath'][i]
            )
            RefSegList = Preprocess_Mask.StrToLst(strIn=self.DataFrame['RefSegmentationName'][i])['listOut']
            inputPaths = Save_Load_File.AppendLists(inputDir, RefSegList, sep='/')['combineList']
            thresVals = Preprocess_Mask.StrToLst(self.DataFrame['ThresholdValues'][i])['floatOut']
            thresVals = thresVals * len(RefSegList)

            if not self.DataFrame['OutRefName'][i]:
                name = 'OriVolumeCA'
            else:
                name = Save_Load_File.ValidFileName(self.DataFrame['OutRefName'][i])

            oneFilePath = Save_Load_File.DateFileName(
                Dir=self.DataFrame['OutputFolder'][i],
                fileName=name+'One',
                extension='nii.gz',
                appendDate=False
            )

            valFilePath = Save_Load_File.DateFileName(
                Dir=self.DataFrame['OutputFolder'][i],
                fileName=name + 'Val',
                extension='nii.gz',
                appendDate=False
            )

            if self.DataFrame['NewValues'][i]:
                newValLst = Preprocess_Mask.StrToLst(strIn=self.DataFrame['NewValues'][i])['floatOut']
                mskAdd = Post_Image_Process_Functions.AddMask(GUI=False)
                mskAdd.AddMskKeepNew(
                    loadFilePaths=inputPaths,
                    values=newValLst,
                    thresholds=thresVals,
                    addNwVal=True
                )

                Save_Load_File.MatNIFTISave(MatData=mskAdd.stackOnesNoOverLp,
                                            imgPath=oneFilePath['CombineName'],
                                            imgInfo=self.CTA.OriImag,
                                            ConvertDType=True,
                                            refDataMat=self.CTA.OriData
                )
                Save_Load_File.MatNIFTISave(MatData=mskAdd.stackNewValsNoOverLp,
                                            imgPath=valFilePath['CombineName'],
                                            imgInfo=self.CTA.OriImag,
                                            ConvertDType=True,
                                            refDataMat=self.CTA.OriData
                )

            else:
                mskAdd = Post_Image_Process_Functions.AddMask(GUI=False)
                mskAdd.AddMskKeepNew(
                    loadFilePaths=inputPaths,
                    values=[0],
                    thresholds=thresVals,
                    addNwVal=False
                )

                Save_Load_File.MatNIFTISave(MatData=mskAdd.stackOnesNoOverLp,
                                            imgPath=oneFilePath["CombineName"],
                                            imgInfo=self.CTA.OriImag,
                                            ConvertDType=True,
                                            refDataMat=self.CTA.OriData)
                Save_Load_File.MatNIFTISave(MatData=mskAdd.stackValsNoOverLp,
                                            imgPath=valFilePath["CombineName"],
                                            imgInfo=self.CTA.OriImag,
                                            ConvertDType=True,
                                            refDataMat=self.CTA.OriData)
    def UpdateMsgLog(self, msg=""):

        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + msg \
               + "\n################################################\n"

        # update log and display message
        if self.modelui:
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
        else:
            pass
