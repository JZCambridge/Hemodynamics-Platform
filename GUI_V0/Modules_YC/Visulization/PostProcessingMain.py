# -*- coding: UTF-8 -*-
'''
@Project ：GUI
@File    ：PostProcessing.py
@IDE     ：PyCharm
@Author  ：YangChen's Piggy
@Date    ：2021/10/27 12:04
'''
import os
import sys
import numpy
import re
import operator
# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_YC')
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
# Import functions
import pdfunction
import Save_Load_File
# import Preprocess_Mask
from datetime import datetime
from CFD_FEA_Post_Process import *
import Paraview_PostProcessing
import time

# Standard libs
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox,QWidget, QTableWidget, QHBoxLayout, \
    QVBoxLayout, QApplication, QTableWidgetItem, QAbstractItemView,QTabWidget,\
    QDialog,QComboBox, QProgressBar,  QLabel, QStatusBar,QLineEdit, QHeaderView
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from FileDisposing import *

class PostProcessing:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
        
        self.ui.pushButton_ChooseNodeCoordinate_PP.clicked.connect(lambda: self.ChooseNodeCoordinateFil())
        self.ui.pushButton_tetraElem_PP.clicked.connect(lambda: self.ChooseTetraelemFil())
        self.ui.pushButton_label_Hexelem_PP.clicked.connect(lambda: self.ChooseHexelemFil())
        self.ui.pushButton_time_PP.clicked.connect(lambda: self.ChooseTimeFil())
        self.ui.pushButton_Lst_Parameters_PP.clicked.connect(lambda: self.ChooseLstParametersFil())
        self.ui.pushButton_postresults_PP.clicked.connect(lambda: self.ChooseFluidPostResltsFil())
        self.ui.pushButton_WSSParameter_PP.clicked.connect(lambda: self.ChooseWSSParametersFil())
        self.ui.pushButton_WSS_PP.clicked.connect(lambda: self.ChooseWSSFil())
        self.ui.pushButton_TimeAverPressure_PP.clicked.connect(lambda: self.ChooseTAPFil())
        self.ui.pushButton_FFRIQRAverageValue_PP.clicked.connect(lambda: self.ChooseFFRIQRAverValueFil())
        self.ui.pushButton_ExportPath_PP.clicked.connect(lambda: self.VTUSavePath())
        self.ui.ResutlsExprot_PP.clicked.connect(lambda: self.Fillist())
        self.ui.ResutlsExprot_PP.clicked.connect(lambda: self.VTUExport())
        self.ui.pushButton_BatchTable_PP.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_PP.clicked.connect(lambda: self.batchrun())
        
        self.InitPostProcessing()

    def InitPostProcessing(self):
        self.filelst = None

    def ChooseNodeCoordinateFil(self):
        # **************** choose node coordinate file**************************
        NodeCoordinateFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_ChooseNodeCoordinate_PP.setText(NodeCoordinateFilAbsPth)

    def ChooseTetraelemFil(self):
        # **************** choose tetra element file**************************
        TetraelementFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_tetraElem_PP.setText(TetraelementFilAbsPth)

    def ChooseHexelemFil(self):
        # **************** choose hextra element file **************************
        HexelementFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_label_Hexelem_PP.setText(HexelementFilAbsPth)

    def ChooseTimeFil(self):
        # ********************* choose time file *******************************
        TimeFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_time_PP.setText(TimeFilAbsPth)

    def ChooseLstParametersFil(self):
        # **************** choose parameters list file *************************
        LstParametersFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_Lst_Parameters_PP.setText(LstParametersFilAbsPth)

    def ChooseFluidPostResltsFil(self):
        # **************** choose fluid post results file **********************
        FluidPostResultsFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_postresults_PP.setText(FluidPostResultsFilAbsPth)

    def ChooseWSSParametersFil(self):
        # ********** choose wall shear stress parameters file ******************
        WallShearStressParametersFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_WSSParameter_PP.setText(WallShearStressParametersFilAbsPth)

    def ChooseWSSFil(self):
        # **************** choose wall shear stress file ***********************
        WallShearStressFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_WSS_PP.setText(WallShearStressFilAbsPth)

    def ChooseTAPFil(self):
        # **************** choose wall shear stress file ***********************
        TimeAveragePressureFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_TimeAverPressure_PP.setText(TimeAveragePressureFilAbsPth)

    def ChooseFFRIQRAverValueFil(self):
        # **************** choose wall shear stress file ***********************
        FFRIQRAverValueFilAbsPth = Opening_File(self.ui," (*.npy)")
        self.ui.lineEdit_FFRIQRAverageValue_PP.setText(FFRIQRAverValueFilAbsPth)

    def VTUSavePath(self):
        VTUSaveDir = Opening_FileDialog(self.ui)
        self.ui.lineEdit_ExportPath_PP.setText(VTUSaveDir)

    def Fillist(self):
        self.filelst = []
        self.filelst.append(self.ui.lineEdit_ChooseNodeCoordinate_PP.text())
        self.filelst.append(self.ui.lineEdit_tetraElem_PP.text())
        self.filelst.append(self.ui.lineEdit_label_Hexelem_PP.text())
        self.filelst.append(self.ui.lineEdit_time_PP.text())
        self.filelst.append(self.ui.lineEdit_Lst_Parameters_PP.text())
        self.filelst.append(self.ui.lineEdit_postresults_PP.text())
        self.filelst.append(self.ui.lineEdit_WSSParameter_PP.text())
        self.filelst.append(self.ui.lineEdit_WSS_PP.text())
        self.filelst.append(self.ui.lineEdit_TimeAverPressure_PP.text())

    def VTUExport(self):
        if self.ui.lineEdit_FFRIQRAverageValue_PP.text():
            FFRIQRAverageValue = numpy.load(self.ui.lineEdit_FFRIQRAverageValue_PP.text())
        else:
            FFRIQRAverageValue = 0
        Paraview_PostProcessing.XMLVtkFileGeneration(self.filelst,
                                                   dataSavePath=self.ui.lineEdit_ExportPath_PP.text(),
                                                   vtkDescription="TENOKE HEDYS",
                                                   FFR = FFRIQRAverageValue,
                                                   vtkFileFormat="ASCII",
                                                   vtkTitle="Description:\n",
                                                   DataSetFormat="UnstructuredGrid"
                                                   )



    def UpdateMsgLog(self, msg=""):
        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + msg \
               + "\n################################################\n"

#
# vtkFile = Paraview_PostProcessing.XMLVtkFileGeneration([r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\Npy\Fluid_Nodecoo_Dic.npy",
#                              r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\Npy\Fluid_TetraElmnt_NdIfo_Dic.npy",
#                              r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\Npy\Fluid_HexElmnt_NdIfo_Dic.npy",
#                              r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\Npy\Fluid_lst_ParamsDic.npy",
#                              r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\Npy\Fluid_Times_Dic.npy",
#                              r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\PostNpy\fluid_PostResults_Dict_dict.npy",
#                              r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\PostNpy\solid_PostResults__WSSParamDict_dict.npy",
#                              r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\PostNpy\solid_PostResults_WssDict_dict.npy"],
#                             dataSavePath = r"E:\paraview\tiantan_postprocessing\PostProgress\PostProgress\vtkdata",
#                             vtkDescription="TENOKE HEDYS",
#                             vtkFileFormat="ASCII",
#                             vtkTitle="Description:\n",
#                             DataSetFormat="UnstructuredGrid"
#                                )
#
#

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_PP.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_PP.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            Paraview_processing = False
            try:
                if info["Paraview_processing"]:
                    Paraview_processing = info["Paraview_processing"]
            except:
                pass

            if Paraview_processing:
                Nodecoo = ''
                TetraElmnt = ''
                HexElmnt = ''
                Times = ''
                ParamsDic = ''
                PostResults = ''
                WSSParamDict = ''
                WssDict = ''
                FFRIQRAverageValue = ''
                OutputFloder = ''
                # change inputfloder and outputfloder
                try:
                    if info["Nodecoo(Paraview_processing)"]:
                        Nodecoo = info["Nodecoo(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["TetraElmnt(Paraview_processing)"]:
                        TetraElmnt = info["TetraElmnt(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["HexElmnt(Paraview_processing)"]:
                        HexElmnt = info["HexElmnt(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["Times(Paraview_processing)"]:
                        Times = info["Times(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["ParamsDic(Paraview_processing)"]:
                        ParamsDic = info["ParamsDic(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["PostResults(Paraview_processing)"]:
                        PostResults = info["PostResults(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["WSSParamDict(Paraview_processing)"]:
                        WSSParamDict = info["WSSParamDict(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["WssDict(Paraview_processing)"]:
                        WssDict = info["WssDict(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["FFRIQRAverageValue(Paraview_processing)"]:
                        FFRIQRAverageValue = info["FFRIQRAverageValue(Paraview_processing)"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        OutputFloder = info["OutputFolder"] + '/Paraview'
                except:
                    pass
                try:
                    if info["OutputFolder(Paraview_processing)"]:
                        OutputFloder = info["OutputFolder(Paraview_processing)"]
                except:
                    pass
                print('Paraview_processing OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                if Nodecoo:
                    self.ui.lineEdit_ChooseNodeCoordinate_PP.setText('{}'.format(Nodecoo))
                if TetraElmnt:
                    self.ui.lineEdit_tetraElem_PP.setText('{}'.format(TetraElmnt))
                if HexElmnt:
                    self.ui.lineEdit_label_Hexelem_PP.setText('{}'.format(HexElmnt))
                if Times:
                    self.ui.lineEdit_time_PP.setText('{}'.format(Times))
                if ParamsDic:
                    self.ui.lineEdit_Lst_Parameters_PP.setText('{}'.format(ParamsDic))
                if PostResults:
                    self.ui.lineEdit_postresults_PP.setText('{}'.format(PostResults))
                if WSSParamDict:
                    self.ui.lineEdit_WSSParameter_PP.setText('{}'.format(WSSParamDict))
                if WssDict:
                    self.ui.lineEdit_WSS_PP.setText('{}'.format(WssDict))
                if FFRIQRAverageValue:
                    self.ui.lineEdit_FFRIQRAverageValue_PP.setText('{}'.format(FFRIQRAverageValue))
                if OutputFloder:
                    self.ui.lineEdit_ExportPath_PP.setText('{}/'.format(OutputFloder))
                time.sleep(1)
                # Touched function
                self.Fillist()
                self.VTUExport()
                self.InitPostProcessing()