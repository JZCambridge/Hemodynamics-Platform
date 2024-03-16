import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
# Import functions
import Save_Load_File
import pdfunction

import pandas as pd
import numpy as np
import math
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
##############################################################################

class CenterlineToCutPlane:
    def __init__(self, UI = None, Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI

            self.ui.pushButton_ChooseCenterlinePath_CLTCP.clicked.connect(lambda: self.ChooseCenterlinePath())
            self.ui.pushButton_ChooseCenterlineCooPath_CLTCP.clicked.connect(lambda: self.ChooseCenterlineCooPath())
            self.ui.pushButton_ChooseResampleCenterlinePath_CLTCP.clicked.connect(lambda: self.ChooseResamplePath())
            self.ui.pushButton_ChooseCutPlaneorigin_CLTCP.clicked.connect(lambda: self.ChooseCutPlaneorigin())
            self.ui.pushButton_ChooseCutPlanenormal_CLTCP.clicked.connect(lambda: self.ChooseCutPlanenormal())
            self.ui.pushButton_BatchTable_CLTCP.clicked.connect(lambda: self.ChooseBatchTable())
            self.ui.pushButton_LoadCenterline_CLTCP.clicked.connect(lambda: self.LoadCenterline())
            self.ui.pushButton_CenterlineCoordinate_CLTCP.clicked.connect(lambda: self.CenterlineCoordinate())
            self.ui.pushButton_ResampleCenterline_CLTCP.clicked.connect(lambda: self.ResampleCenterline())
            self.ui.pushButton_GetCutPlane_CLTCP.clicked.connect(lambda: self.GetCutPlane())
            self.ui.pushButton_BatchRun_CLTCP.clicked.connect(lambda: self.BatchRun())

        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.InitCenterlineToCutPlane()

    def InitCenterlineToCutPlane(self):
        self.Centerline = None

    def ChooseCenterlinePath(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose Centerline Path",
                                                 fileTypes="All files (*.*)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.textEdit_CenterlinePath_CLTCP.setPlainText('{}'.format(filename))

    def ChooseBatchTable(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose Batch Table Path",
                                                 fileTypes="All files (*.*)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_CLTCP.setPlainText('{}'.format(filename))

    def ChooseCenterlineCooPath(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Output Centerline Coordinate file path",
                                                 fileTypes="All files (*.*) ;; csv files (*.csv) ;; ",
                                                 fileObj=self.ui, qtObj=True)

        # set filename
        self.ui.textEdit_CenterlineCoordinatePath_CLTCP.setPlainText(filename)

    def ChooseResamplePath(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Output Resample Centerline file path",
                                                 fileTypes="All files (*.*) ;; csv files (*.csv) ;; ",
                                                 fileObj=self.ui, qtObj=True)

        # set filename
        self.ui.textEdit_ResampleCenterlinePath_CLTCP.setPlainText(filename)

    def ChooseCutPlaneorigin(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Output Cut Plane origin file path",
                                                 fileTypes="All files (*.*);; csv files (*.csv) ;; ",
                                                 fileObj=self.ui, qtObj=True)

        # set filename
        self.ui.textEdit_SaveCutPlaneoriginPath_CLTCP.setPlainText(filename)

    def ChooseCutPlanenormal(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Output Cut Plane normal file path",
                                                 fileTypes="All files (*.*);; csv files (*.csv) ;; ",
                                                 fileObj=self.ui, qtObj=True)

        # set filename
        self.ui.textEdit_SaveCutPlanenormalPath_CLTCP.setPlainText(filename)

    def LoadCenterline(self):
        self.InitCenterlineToCutPlane()
        CenterlinePath = self.ui.textEdit_CenterlinePath_CLTCP.toPlainText()
        print('CenterlinePath', CenterlinePath)

        DF = pd.read_csv(CenterlinePath, header=None)
        self.Centerline = DF.values

    def CenterlineCoordinate(self):
        SpaceX = self.ui.doubleSpinBox_SpaceX_CLTCP.value()
        SpaceY = self.ui.doubleSpinBox_SpaceY_CLTCP.value()
        SpaceZ = self.ui.doubleSpinBox_SpaceZ_CLTCP.value()
        SaveCenterlineCoordinate = self.ui.checkBox_SaveCenterlineCoordinate_CLTCP.isChecked()
        CenterlineCoordinatePath = self.ui.textEdit_CenterlineCoordinatePath_CLTCP.toPlainText()
        print('Space', SpaceX, SpaceY, SpaceZ)
        print('SaveCenterlineCoordinate', SaveCenterlineCoordinate)
        print('CenterlineCoordinatePath', CenterlineCoordinatePath)
        space = np.array([SpaceX, SpaceY, SpaceZ])
        self.Centerline = self.Centerline * space
        if SaveCenterlineCoordinate:
            Centerlinedf = pd.DataFrame(self.Centerline)
            Centerlinedf.to_csv(CenterlineCoordinatePath, header=None, index=None)

    def ResampleCenterline(self):
        ResampleNumber = self.ui.spinBox_ResampleNumber_CLTCP.value()
        CenterlinePointNumber = self.ui.checkBox_CenterlinePointNumber_CLTCP.isChecked()
        SaveResampleCenterline = self.ui.checkBox_SaveResampleCenterline_CLTCP.isChecked()
        ResampleCenterlinePath = self.ui.textEdit_ResampleCenterlinePath_CLTCP.toPlainText()
        print('ResampleNumber', ResampleNumber)
        print('CenterlinePointNumber', CenterlinePointNumber)
        print('SaveResampleCenterline', SaveResampleCenterline)
        print('ResampleCenterlinePath', ResampleCenterlinePath)

        if CenterlinePointNumber:
            ResampleNumber = len(self.Centerline) - 1
        PB = np.zeros(self.Centerline.shape)  # 求和前各项
        pis = []  # 插补点
        for u in np.arange(0, 1 + 1 / ResampleNumber, 1 / ResampleNumber):
            for i in range(0, self.Centerline.shape[0]):
                PB[i] = (math.factorial(self.Centerline.shape[0] - 1) / (math.factorial(i) * math.factorial(
                    self.Centerline.shape[0] - 1 - i))) * (u ** i) * (1 - u) ** (
                    self.Centerline.shape[0] - 1 - i) * self.Centerline[i]
            pi = sum(PB).tolist()  # 求和得到一个插补点
            pis.append(pi)
        self.Centerline = np.array(pis)
        if SaveResampleCenterline:
            Centerlinedf = pd.DataFrame(self.Centerline)
            Centerlinedf.to_csv(ResampleCenterlinePath, header=None, index=None)

    def GetCutPlane(self):
        CutPlaneDistance = self.ui.doubleSpinBox_CutPlaneDistance_CLTCP.value()
        SaveCutPlaneorigin = self.ui.checkBox_SaveCutPlaneorigin_CLTCP.isChecked()
        CutPlaneoriginPath = self.ui.textEdit_SaveCutPlaneoriginPath_CLTCP.toPlainText()
        SaveCutPlanenormal = self.ui.checkBox_SaveCutPlanenormal_CLTCP.isChecked()
        CutPlanenormalPath = self.ui.textEdit_SaveCutPlanenormalPath_CLTCP.toPlainText()
        print('CutPlaneDistance', CutPlaneDistance)
        print('SaveCutPlaneorigin', SaveCutPlaneorigin)
        print('CutPlaneoriginPath', CutPlaneoriginPath)
        print('SaveCutPlanenormal', SaveCutPlanenormal)
        print('CutPlanenormalPath', CutPlanenormalPath)

        normal = np.zeros(self.Centerline.shape)
        distance = [0]
        step = 10
        length = 0
        usepoint = []
        usenormal = []
        for i in range(1, self.Centerline.shape[0]):
            normal[i] = self.Centerline[i] - self.Centerline[i-1]
            distance.append(np.linalg.norm(normal[i]))
            length = length + distance[i]
            if length > step:
                if length - step > step:
                    length = 0
                else:
                    length = length - step
                usepoint.append(list(self.Centerline[i]))
                usenormal.append(list(normal[i]))
        if SaveCutPlaneorigin:
            CutPlaneorigin = pd.DataFrame(usepoint)
            CutPlaneorigin.to_csv(CutPlaneoriginPath, header=None, index=None)
        if SaveCutPlanenormal:
            CutPlanenormal = pd.DataFrame(usenormal)
            CutPlanenormal.to_csv(CutPlanenormalPath, header=None, index=None)

    def BatchRun(self):
        inpath = self.ui.plainTextEdit_BatchTable_CLTCP.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for linenum in range(len(DF)):
            # get line of table
            print('get info in line', linenum)
            info = DF.iloc[linenum].fillna('')

            CenterlineToCutPlane = False
            try:
                if info["Centerline To Cut Plane"]:
                    CenterlineToCutPlane = info["Centerline To Cut Plane"]
            except:
                pass
            if CenterlineToCutPlane:
                CenterlinePath = ''
                CenterlineCoordinate = False
                SpaceX = 0.43
                SpaceY = 0.43
                SpaceZ = 0.5
                SaveCenterlineCoordinate = False
                CenterlineCoordinatePath = ''
                ResampleCenterline = False
                ResampleNumber = 1000
                UseCenterlinePointNumber = False
                SaveResampleCenterline = False
                ResampleCenterlinePath = ''
                GetCutPlane = False
                CutPlaneDistance = 1
                SaveCutPlaneorigin = False
                CutPlaneoriginPath = ''
                SaveCutPlanenormal = False
                CutPlanenormalPath = ''

                try:
                    if info["Centerline Path"]:
                        CenterlinePath = info["Centerline Path"]
                except:
                    pass
                try:
                    if isinstance(info["Centerline Coordinate"], np.bool_):
                        CenterlineCoordinate = info["Centerline Coordinate"]
                except:
                    pass
                try:
                    if info["SpaceX"]:
                        SpaceX = info["SpaceX"]
                except:
                    pass
                try:
                    if info["SpaceY"]:
                        SpaceY = info["SpaceY"]
                except:
                    pass
                try:
                    if info["SpaceZ"]:
                        SpaceZ = info["SpaceZ"]
                except:
                    pass
                try:
                    if isinstance(info["Save Centerline Coordinate"], np.bool_):
                        SaveCenterlineCoordinate = info["Save Centerline Coordinate"]
                except:
                    pass
                try:
                    if info["Centerline Coordinate Path"]:
                        CenterlineCoordinatePath = info["Centerline Coordinate Path"]
                except:
                    pass
                try:
                    if isinstance(info["Resample Centerline"], np.bool_):
                        ResampleCenterline = info["Resample Centerline"]
                except:
                    pass
                try:
                    if info["ResampleNumber"]:
                        ResampleNumber = info["ResampleNumber"]
                except:
                    pass
                try:
                    if isinstance(info["Use Centerline Point Number"], np.bool_):
                        UseCenterlinePointNumber = info["Use Centerline Point Number"]
                except:
                    pass
                try:
                    if isinstance(info["Save Resample Centerline"], np.bool_):
                        SaveResampleCenterline = info["Save Resample Centerline"]
                except:
                    pass
                try:
                    if info["Resample Centerline Path"]:
                        ResampleCenterlinePath = info["Resample Centerline Path"]
                except:
                    pass
                try:
                    if isinstance(info["Get Cut Plane"], np.bool_):
                        GetCutPlane = info["Get Cut Plane"]
                except:
                    pass
                try:
                    if info["CutPlaneDistance"]:
                        CutPlaneDistance = info["CutPlaneDistance"]
                except:
                    pass
                try:
                    if isinstance(info["Save Cut Plane origin"], np.bool_):
                        SaveCutPlaneorigin = info["Save Cut Plane origin"]
                except:
                    pass
                try:
                    if info["Cut Plane origin Path"]:
                        CutPlaneoriginPath = info["Cut Plane origin Path"]
                except:
                    pass
                try:
                    if isinstance(info["Save Cut Plane normal"], np.bool_):
                        SaveCutPlanenormal = info["Save Cut Plane normal"]
                except:
                    pass
                try:
                    if info["Cut Plane normal Path"]:
                        CutPlanenormalPath = info["Cut Plane normal Path"]
                except:
                    pass
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                if CenterlinePath:
                    self.ui.textEdit_CenterlinePath_CLTCP.setPlainText('{}'.format(CenterlinePath))
                if SpaceX:
                    self.ui.doubleSpinBox_SpaceX_CLTCP.setValue(SpaceX)
                if SpaceY:
                    self.ui.doubleSpinBox_SpaceY_CLTCP.setValue(SpaceY)
                if SpaceZ:
                    self.ui.doubleSpinBox_SpaceZ_CLTCP.setValue(SpaceZ)
                self.ui.checkBox_SaveCenterlineCoordinate_CLTCP.setChecked(SaveCenterlineCoordinate)
                if CenterlineCoordinatePath:
                    self.ui.textEdit_CenterlineCoordinatePath_CLTCP.setPlainText('{}'.format(CenterlineCoordinatePath))
                if ResampleNumber:
                    self.ui.spinBox_ResampleNumber_CLTCP.setValue(ResampleNumber)
                self.ui.checkBox_CenterlinePointNumber_CLTCP.setChecked(UseCenterlinePointNumber)
                self.ui.checkBox_SaveResampleCenterline_CLTCP.setChecked(SaveResampleCenterline)
                if ResampleCenterlinePath:
                    self.ui.textEdit_ResampleCenterlinePath_CLTCP.setPlainText('{}'.format(ResampleCenterlinePath))
                if CutPlaneDistance:
                    self.ui.doubleSpinBox_CutPlaneDistance_CLTCP.setValue(CutPlaneDistance)
                self.ui.checkBox_SaveCutPlaneorigin_CLTCP.setChecked(SaveCutPlaneorigin)
                if CutPlaneoriginPath:
                    self.ui.textEdit_SaveCutPlaneoriginPath_CLTCP.setPlainText('{}'.format(CutPlaneoriginPath))
                self.ui.checkBox_SaveCutPlanenormal_CLTCP.setChecked(SaveCutPlanenormal)
                if CutPlanenormalPath:
                    self.ui.textEdit_SaveCutPlanenormalPath_CLTCP.setPlainText('{}'.format(CutPlanenormalPath))
                # Touched function
                self.LoadCenterline()
                if CenterlineCoordinate:
                    self.CenterlineCoordinate()
                if ResampleCenterline:
                    self.ResampleCenterline()
                if GetCutPlane:
                    self.GetCutPlane()

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\CenterlineToCutPlane.ui")
    stats = CenterlineToCutPlane(UI=ui)
    stats.ui.show()
    app.exec_()