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
import psutil

# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
# Import functions
import pdfunction
import Save_Load_File
import Image_Process_Functions
import Post_Image_Process_Functions
import Preprocess_Mask
import Use_Plt
import CFD_FEA_Post_Process
import Matrix_Math
##############################################################################

##############################################################################
# Standard library
from datetime import datetime
import time
import numpy
import threading
import gc

##############################################################################

class CFDParameters:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            
        self.ui.chooseDirBtn_CFDP.clicked.connect(lambda: self.ChooseLoadDir())
        self.ui.loadDataBtn_CFDP.clicked.connect(lambda: self.LoadFile())
        self.ui.saveDirBtn_CFDP.clicked.connect(lambda: self.ChooseSaveDir())
        self.ui.calcDirBtn_CFDP.clicked.connect(lambda: self.CalcSave())
        self.ui.pushButton_BatchTable_CFDP.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_CFDP.clicked.connect(lambda: self.batchrun())
        self.ui.chooseTableSavePath_CFDP.clicked.connect(lambda: self.ChooseSaveFilePoint())
        self.ui.singlePointExtraction_CFDP.clicked.connect(lambda: self.OutputPointSeries())

        self.InitCFDParameters()

    def InitCFDParameters(self):
        # initial definition
        self.timeData = None
        self.hexaElem = None
        self.tetraElem = None
        self.ndCoo = None
        self.elfElemGrp = None
        self.timeStrs = None
        self.timeLst = None

        # RAM
        # you can have the percentage of used RAM
        self.UpdateMsgLog(str(psutil.virtual_memory().percent))

        # you can calculate percentage of available memory
        self.UpdateMsgLog(str(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total))

    def ChooseLoadDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Load data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.loadDirPathTxt_CFDP.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose loading dir:\n{}".format(dirname))

    def ChooseSaveDir(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.saveDirPathTxt_CFDP.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose saving dir:\n{}".format(dirname))

    def LoadFile(self):
        # get all file name
        overPath = self.ui.loadDirPathTxt_CFDP.toPlainText()
        timePath = overPath + "/" + self.ui.timeLineTxt_CFDP.text()
        hexaElemPath = overPath + "/" + self.ui.hexaElemLineTxt_CFDP.text()
        tetraElemPath = overPath + "/" + self.ui.tetraElemLineTxt_CFDP.text()
        ndCooPath = overPath + "/" + self.ui.ndCooLineTxt_CFDP.text()
        elfElemGrpPath = overPath + "/" + self.ui.elfElemGrpLineTxt_CFDP.text()
        timeStrsPath = overPath + "/" + self.ui.timeStrsLineTxt_CFDP.text()
        timeLstPath = overPath + "/" + self.ui.timeLstLineTxt_CFDP.text()

        # update message
        self.UpdateMsgLog(msg="Files to load:"
                              "\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
            timePath,
            hexaElemPath,
            tetraElemPath,
            ndCooPath,
            elfElemGrpPath,
            timeStrsPath,
            timeLstPath
        )
        )

        self.timeData, \
            self.hexaElem, \
            self.tetraElem, \
            self.ndCoo, \
            self.elfElemGrp, \
            self.timeStrs, \
            self.timeLst = \
            CFD_FEA_Post_Process.LoadNpyFile(
                timePath,
                hexaElemPath,
                tetraElemPath,
                ndCooPath,
                elfElemGrpPath,
                timeStrsPath,
                timeLstPath)

    def ThreadCalcSave(self):
        # Run with thread
        thread = threading.Thread(target=self.CalcSave,
                                  args=())
        thread.start()

        # thread.join()

    """
    ##############################################################################
    # Calculate & save numpy resutls
    ##############################################################################
    """
    def CalcSave(self):
        # input
        faceSetRef = self.ui.faceSetLineTxt_CFDP.text() + self.ui.faceSetNumberLineTxt_CFDP.text()
        saveDirPath = self.ui.saveDirPathTxt_CFDP.toPlainText()
        timeStart = float(self.ui.timeStartLineTxt_CFDP.text())
        timeStop = float(self.ui.timeStopLineTxt_CFDP.text())

        CFD_FEA_Post_Process.CalcandSave(faceSetRef,
                                         saveDirPath,
                                         timeStart,
                                         timeStop,
                                         self.timeData,
                                         self.hexaElem,
                                         self.tetraElem,
                                         self.ndCoo,
                                         self.elfElemGrp,
                                         self.timeStrs,
                                         self.timeLst)

    """
    ##############################################################################
    # Output point results
    ##############################################################################
    """

    def ChooseSaveFilePoint(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save table directory",
                                                fileObj=self.ui,
                                                qtObj=True)

        # set filename
        self.ui.pointTableSavePathTxt_CFDP.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose saving table dir:\n{}".format(dirname))

    def OutputPointSeries(self):
        # input
        faceSetRef = self.ui.faceSetLineTxt_CFDP.text() + self.ui.faceSetNumberLineTxt_CFDP.text()
        saveTablePath = self.ui.pointTableSavePathTxt_CFDP.toPlainText()
        fileRef = self.ui.pointFileRefLineTxt_CFDP.text()
        timeStart = float(self.ui.timeStartLineTxt_CFDP.text())
        timeStop = float(self.ui.timeStopLineTxt_CFDP.text())

        pointX = float(self.ui.pointXLineTxt_CFDP.text())
        pointY = float(self.ui.pointYLineTxt_CFDP.text())
        pointZ = float(self.ui.pointZLineTxt_CFDP.text())

        print(pointX)
        print(pointY)
        print(pointZ)

        CFD_FEA_Post_Process.PointTimeSeriesExtract(faceSetRef,
                                                    saveTablePath,
                                                    fileRef,
                                                    timeStart,
                                                    timeStop,
                                                    self.timeData,
                                                    self.hexaElem,
                                                    self.tetraElem,
                                                    self.ndCoo,
                                                    self.elfElemGrp,
                                                    self.timeStrs,
                                                    self.timeLst,
                                                    X=pointX,
                                                    Y=pointY,
                                                    Z=pointZ)

    """
    ##############################################################################
    # Batch processing
    ##############################################################################
    """
    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_CFDP.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_CFDP.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            CFD_Post_processing = False
            try:
                if info["CFD Post-processing"]:
                    CFD_Post_processing = info["CFD Post-processing"]
            except:
                pass
            if CFD_Post_processing:
                postprocessinginputfloder = ''
                postprocessingoutputfloder = ''
                TimeStart = ''
                TimeStop = ''
                TimeFile = ''
                HexaElementFile = ''
                TetraElementFile = ''
                NodeCoordinateFile = ''
                ElementFaceGroupFile = ''
                StressTimeFile = ''
                ListTimeFile = ''
                FaceSetRef = ''
                FaceSetNumber = ''
                try:
                    if info["InputFolder(CFD Post-processing)"]:
                        postprocessinginputfloder = info["InputFolder(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["TimeStart(CFD Post-processing)"]:
                        TimeStart = info["TimeStart(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["TimeStop(CFD Post-processing)"]:
                        TimeStop = info["TimeStop(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["TimeFile(CFD Post-processing)"]:
                        TimeFile = info["TimeFile(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["HexaElementFile(CFD Post-processing)"]:
                        HexaElementFile = info["HexaElementFile(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["TetraElementFile(CFD Post-processing)"]:
                        TetraElementFile = info["TetraElementFile(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["NodeCoordinateFile(CFD Post-processing)"]:
                        NodeCoordinateFile = info["NodeCoordinateFile(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["ElementFaceGroupFile(CFD Post-processing)"]:
                        ElementFaceGroupFile = info["ElementFaceGroupFile(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["StressTimeFile(CFD Post-processing)"]:
                        StressTimeFile = info["StressTimeFile(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["ListTimeFile(CFD Post-processing)"]:
                        ListTimeFile = info["ListTimeFile(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["FaceSetRef(CFD Post-processing)"]:
                        FaceSetRef = info["FaceSetRef(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["FaceSetNumber(CFD Post-processing)"]:
                        FaceSetNumber = info["FaceSetNumber(CFD Post-processing)"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        postprocessingoutputfloder = info["OutputFolder"] + '/PostNpy'
                except:
                    pass
                try:
                    if info["OutputFolder(CFD Post-processing)"]:
                        postprocessingoutputfloder = info["OutputFolder(CFD Post-processing)"]
                except:
                    pass
                print('CFD_Post_processing InputFloder=', postprocessinginputfloder)
                print('CFD_Post_processing OutputFloder=', postprocessingoutputfloder)
                # make dir
                if not os.path.exists(postprocessingoutputfloder):
                    os.mkdir(postprocessingoutputfloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                if postprocessinginputfloder:
                    self.ui.loadDirPathTxt_CFDP.setPlainText('{}'.format(postprocessinginputfloder))
                if TimeStart:
                    self.ui.timeStartLineTxt_CFDP.setText('{}'.format(TimeStart))
                if TimeStop:
                    self.ui.timeStopLineTxt_CFDP.setText('{}'.format(TimeStop))
                if TimeFile:
                    self.ui.timeLineTxt_CFDP.setText('{}'.format(TimeFile))
                if HexaElementFile:
                    self.ui.hexaElemLineTxt_CFDP.setText('{}'.format(HexaElementFile))
                if TetraElementFile:
                    self.ui.tetraElemLineTxt_CFDP.setText('{}'.format(TetraElementFile))
                if NodeCoordinateFile:
                    self.ui.ndCooLineTxt_CFDP.setText('{}'.format(NodeCoordinateFile))
                if ElementFaceGroupFile:
                    self.ui.elfElemGrpLineTxt_CFDP.setText('{}'.format(ElementFaceGroupFile))
                if StressTimeFile:
                    self.ui.timeStrsLineTxt_CFDP.setText('{}'.format(StressTimeFile))
                if ListTimeFile:
                    self.ui.timeLstLineTxt_CFDP.setText('{}'.format(ListTimeFile))
                if FaceSetRef:
                    self.ui.faceSetLineTxt_CFDP.setText('{}'.format(FaceSetRef))
                if FaceSetNumber:
                    self.ui.faceSetNumberLineTxt_CFDP.setText('{}'.format(FaceSetNumber))
                if postprocessingoutputfloder:
                    self.ui.saveDirPathTxt_CFDP.setPlainText('{}'.format(postprocessingoutputfloder))
                # Touched function
                self.LoadFile()
                self.CalcSave()


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