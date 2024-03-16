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
sys.path.insert(0, '../Functions_AZ')
# Import functions
import pdfunction
import Save_Load_File
import Image_Process_Functions
import Post_Image_Process_Functions
import Preprocess_Mask
import Use_Plt
##############################################################################

##############################################################################
# Standard library
import numpy
from datetime import datetime
import time
import threading


##############################################################################

class FFRCalcs:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
        
        self.ui.chooseValFileBtn_FFR.clicked.connect(lambda: self.ChooseOpenValueFile())
        self.ui.chooseMskFileBtn_FFR.clicked.connect(lambda: self.ChooseOpenMskFile())
        self.ui.loadFileBtn_FFR.clicked.connect(lambda: self.LoadData())
        self.ui.showXBtn_FFR.clicked.connect(lambda: self.PlotOVerlap('X'))
        self.ui.showYBtn_FFR.clicked.connect(lambda: self.PlotOVerlap('Y'))
        self.ui.showZBtn_FFR.clicked.connect(lambda: self.PlotOVerlap('Z'))
        self.ui.filterDataBtn_FFR.clicked.connect(lambda: self.FilterVals())
        self.ui.plotFilterBtn_FFR.clicked.connect(lambda: self.PlotFilter())
        self.ui.saveFileBtn_FFR.clicked.connect(lambda: self.SaveFilePath())
        self.ui.FFRFileBtn_FFR.clicked.connect(lambda: self.FRRCalcSave())
        self.ui.pushButton_BatchTable_FFR.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_FFR.clicked.connect(lambda: self.batchrun())
        
        self.InitFFRCalcs()

    def InitFFRCalcs(self):
        # initial definition
        self.outputData = None
        self.inValMsk = None
        self.inValMskROI = None
        self.inMsk = None
        self.mskOnes = None

    def ChooseOpenValueFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadImgPathTxt_FFR.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose loading value image file:{}".format(self.ui.loadImgPathTxt_FFR.toPlainText()))

    def ChooseOpenMskFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load medical image",
            fileTypes="All files (*.*);; NIFTI/NRRD files (*.nii.gz *.nrrd)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.loadMskPathTxt_FFR.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose loading value image file:{}".format(self.ui.loadMskPathTxt_FFR.toPlainText()))

    def LoadData(self):
        # load two data
        self.inValMsk = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.loadImgPathTxt_FFR.toPlainText()
        )
        self.inMsk = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.loadMskPathTxt_FFR.toPlainText()
        )
        # update message
        self.UpdateMsgLog(msg="Load:{}\n{}".format(self.ui.loadImgPathTxt_FFR.toPlainText(),
                                                   self.ui.loadMskPathTxt_FFR.toPlainText()))

    def PlotOVerlap(self, slicDir="X"):
        # get inputs
        title = ['Slicing in selected direction', "Segmentation", "Overlap"]
        # !! cannot use threading
        Use_Plt.slider3Display(matData1=self.inValMsk.OriData,
                               matData2=self.inMsk.OriData,
                               ask23MatData=False,
                               wait=False,
                               slicDiect=slicDir,
                               title=title)

    def SaveFilePath(self):
        fileName = Save_Load_File.SaveFilePathQT(
            dispMsg="Select save FFR file path",
            fileObj=self.ui,
            fileTypes="All files (*.*);; "
                      "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                      "STL files (*.stl) ;; "
                      "Img files (*.png *.jpg) ;; "
                      "Graphic files (*.svg, *.eps, *.ps, *.pdf, *.tex) ",
            qtObj=True
        )
        # set filename
        self.ui.saveImgPathTxt_FFR.setPlainText(fileName)

        # update message
        self.UpdateMsgLog(msg="Choose save FFR image file:{}".format(self.ui.saveImgPathTxt_FFR.toPlainText()))

    def FRRCalcSave(self):
        # get input
        sliceDirection = self.ui.FFRBtnGrp_FFR.checkedButton().text()
        startSlice = int(self.ui.startSliceLineTxt_FFR.text())
        finishSlice = int(self.ui.finishSliceLineTxt_FFR.text())  # Add 1 slice for the range() problem
        savePath = self.ui.saveImgPathTxt_FFR.toPlainText()
        print("sliceDirection:{}".format(sliceDirection))
        print("startSlice:{}".format(startSlice))
        print("finishSlice:{}".format(finishSlice))

        # update message
        self.UpdateMsgLog(
            msg="Slice direction:{}\n".format(sliceDirection)
                + "Start slice:{}\n".format(startSlice)
                + "Finish slice:{}\n".format(finishSlice)
        )

        # flip range if wrong
        if startSlice > finishSlice:
            finishSlice = int(self.ui.startSliceLineTxt_FFR.text())
            startSlice = int(self.ui.finishSliceLineTxt_FFR.text())
            # update message
            self.UpdateMsgLog(
                msg="Input range is wrong way round, flipped automatically!\n"
                    + "Start slice:{}\n".format(startSlice)
                    + "Finish slice:{}".format(finishSlice)
            )
            print("Input range is wrong way round, flipped automatically!\n"
                  + "Start slice:{}\n".format(startSlice)
                  + "Finish slice:{}".format(finishSlice))

        # check data
        msg = "Mean calcs data info: " \
              + "\nmax: {}".format(numpy.max(self.inValMskROI)) \
              + "\nmin: {}".format(numpy.min(self.inValMskROI)) \
              + "\nInput to calculate:" \
              + "\nmax: {}".format(numpy.max(self.inValMsk.OriData)) \
              + "\nmin: {}".format(numpy.min(self.inValMsk.OriData))
        self.UpdateMsgLog(msg)
        print(msg)

        # threading
        # Run with thread
        thread = threading.Thread(target=Post_Image_Process_Functions.ImageValueRatio,
                                  args=(
                                      self.inValMsk.OriData,
                                      self.inValMskROI,
                                      startSlice,
                                      finishSlice,
                                      sliceDirection,
                                      True,
                                      savePath,
                                      self.inValMsk.OriImag
                                  )
                                  )
        thread.start()

    def FilterVals(self):
        # list of value to mask out
        valLst = Preprocess_Mask.StrToLst(
            strIn=self.ui.valListTxt_FFR.toPlainText()
        )["floatOut"]

        # filter
        _, self.mskOnes = Image_Process_Functions.FilterData(rangStarts=valLst,
                                                             dataMat=self.inMsk.OriData,
                                                             funType="single value",
                                                             ConvertVTKType=False)

        # filter data
        self.inValMskROI = numpy.multiply(self.inValMsk.OriData, self.mskOnes)

        self.UpdateMsgLog(
            msg="Input values image are masked with segmentation vals: {}".format(valLst)
        )

    def PlotFilter(self, slicDir="X"):
        # get inputs
        title = ['Filter Data', "Filter", "Overlap"]
        # !! cannot use threading
        Use_Plt.slider3Display(matData1=self.inValMskROI,
                               matData2=self.mskOnes,
                               ask23MatData=False,
                               wait=False,
                               slicDiect=slicDir,
                               title=title)

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

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_FFR.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_FFR.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            FFRCalculation = False
            try:
                if info["FFRCalculation"]:
                    FFRCalculation = info["FFRCalculation"]
            except:
                pass
            if FFRCalculation:
                InputFloder = ''
                InputMask = ''
                KeepValues = ''
                OutputFloder = ''
                # change inputfloder and outputfloder
                try:
                    if info["Load Value image for FFR Folder(FFRCalculation)"]:
                        InputFloder = info["Load Value image for FFR Folder(FFRCalculation)"]
                except:
                    pass
                try:
                    if info["InputMask(FFRCalculation)"]:
                        InputMask = info["InputMask(FFRCalculation)"]
                except:
                    pass
                try:
                    if info["Keep Values(FFRCalculation)"]:
                        KeepValues = info["Keep Values(FFRCalculation)"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        OutputFloder = info["OutputFolder"] + '/FFR'
                except:
                    pass
                try:
                    if info["OutputFolder(FFRCalculation)"]:
                        OutputFloder = info["OutputFolder(FFRCalculation)"]
                except:
                    pass
                print('FFRCalculation InputFloder=', InputFloder)
                print('FFRCalculation OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                self.ui.loadImgPathTxt_FFR.setPlainText('{}'.format(InputFloder))
                self.ui.saveImgPathTxt_FFR.setPlainText('{}'.format(OutputFloder + '/FFR.nii.gz'))
                if KeepValues:
                    self.ui.valListTxt_FFR.setPlainText('{}'.format(KeepValues))
                if InputMask:
                    self.ui.loadMskPathTxt_FFR.setPlainText('{}'.format(InputMask))
                # Touched function
                self.LoadData()
                self.FilterVals()
                self.FRRCalcSave()
                self.InitFFRCalcs()