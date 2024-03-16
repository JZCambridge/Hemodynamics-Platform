import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
import Save_Load_File
import QT_GUI

import numpy as np
import ast
import time
import pandas as pd
import imageio
from matplotlib import colors
import paraview.simple as pvsimple
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
os.chdir(os.path.dirname(__file__))

class VisualizationParaview():
    def __init__(self, UIPath = None, parentsUIPath = None):
        if UIPath:
            self.ui = QUiLoader().load(UIPath)
        else:
            self.ui = QUiLoader().load('./ui/VisualizationParaview.ui')
        if parentsUIPath:
            parentsUI = QUiLoader().load(parentsUIPath)
            parentsUI.QStackedWidget_Module.addWidget(self.ui.centralwidget)
            self.modelui = parentsUI
        else:
            self.modelui = self.ui

        self.source = None

        self.ui.pushButton_choosepvd_VPZ.clicked.connect(lambda: self.choosepvd())
        self.ui.pushButton_LoadData_VPZ.clicked.connect(lambda: self.loaddata())
        self.ui.pushButton_LoadData_VPZ.clicked.connect(lambda: self.getpointarray())
        self.ui.pushButton_chooseColorPreset_VPZ.clicked.connect(lambda: self.chooseColorPreset())
        self.ui.comboBox_viewresult_VPZ.currentIndexChanged.connect(lambda: self.setColorBarTitle())
        self.ui.pushButton_chooseTimeNpy_VPZ.clicked.connect(lambda: self.choosetimenpy())
        self.ui.pushButton_chooseOutPut_VPZ.clicked.connect(lambda: self.chooseOutputFloder())
        self.ui.pushButton_showParaview_VPZ.clicked.connect(lambda: self.showParaview())
        self.ui.pushButton_showParaview_VPZ.clicked.connect(lambda: self.render())
        self.ui.pushButton_SavePicture_VPZ.clicked.connect(lambda: self.savePicture())
        self.ui.pushButton_SaveGif_VPZ.clicked.connect(lambda: self.saveGif())
        self.ui.pushButton_Render_VPZ.clicked.connect(lambda: self.render())
        self.ui.pushButton_FirstStep_VPZ.clicked.connect(lambda: self.render('FirstStep'))
        self.ui.pushButton_Play_VPZ.clicked.connect(lambda: self.render('Play'))
        self.ui.pushButton_NextStep_VPZ.clicked.connect(lambda: self.render('NextStep'))
        self.ui.pushButton_LastStep_VPZ.clicked.connect(lambda: self.render('LastStep'))
        self.ui.pushButton_GetCamera_VPZ.clicked.connect(lambda: self.getcamera())
        self.ui.lineEdit_colorBackground_VPZ.textChanged.connect(lambda: self.getRGB())
        self.ui.lineEdit_colorColorBarTitle_VPZ.textChanged.connect(lambda: self.getColorBarTitleRGB())
        self.ui.lineEdit_colorColorBarLabel_VPZ.textChanged.connect(lambda: self.getColorBarLabelRGB())
        self.ui.pushButton_Smooth_VPZ.clicked.connect(lambda: self.smooth())
        self.ui.pushButton_Clip_VPZ.clicked.connect(lambda: self.clip())
        self.ui.pushButton_ClipApply_VPZ.clicked.connect(lambda: self.clipapply())
        self.ui.pushButton_Slice_VPZ.clicked.connect(lambda: self.slice())
        self.ui.pushButton_SliceApply_VPZ.clicked.connect(lambda: self.sliceapply())
        self.ui.pushButton_BatchTable_VPZ.clicked.connect(lambda: self.chooseBatchTable())
        self.ui.pushButton_BatchRun_VPZ.clicked.connect(lambda: self.batchRun())

    def slice(self):
        Source = self.ui.comboBox_Source_VPZ.currentText()

        print('Source', Source)
        print('Sourcelist', self.source)

        # get source
        paraviewpvd = pvsimple.FindSource(Source)
        # slice name
        for i in range(1000):
            slicename = 'slice' + str(i + 1)
            if slicename not in self.source:
                self.source.append(slicename)
                print(slicename)
                break
        # create a new 'Slice'
        pvsimple.Slice(registrationName=slicename, Input=paraviewpvd)
        self.ui.comboBox_Source_VPZ.addItem(slicename)
        self.ui.comboBox_Source_VPZ.setCurrentText(slicename)
        self.sliceapply()

    def sliceapply(self):
        Source = self.ui.comboBox_Source_VPZ.currentText()
        slicetype = self.ui.comboBox_ClipType_VPZ.currentText()
        showSlice = self.ui.checkBox_ShowClip_VPZ.isChecked()
        Position_x = self.ui.lineEdit_ClipPosition_x_VPZ.text()
        Position_y = self.ui.lineEdit_ClipPosition_y_VPZ.text()
        Position_z = self.ui.lineEdit_ClipPosition_z_VPZ.text()
        Rotation_x = self.ui.lineEdit_ClipRotation_x_VPZ.text()
        Rotation_y = self.ui.lineEdit_ClipRotation_y_VPZ.text()
        Rotation_z = self.ui.lineEdit_ClipRotation_z_VPZ.text()
        Length_x = self.ui.lineEdit_ClipLenth_x_VPZ.text()
        Length_y = self.ui.lineEdit_ClipLenth_y_VPZ.text()
        Length_z = self.ui.lineEdit_ClipLenth_z_VPZ.text()

        print('Source', Source)
        print('cliptype', slicetype)
        print('showClip', showSlice)
        print('Position', Position_x, Position_y, Position_z)
        print('Rotation', Rotation_x, Rotation_y, Rotation_z)
        print('Length', Length_x, Length_y, Length_z)
        print('Sourcelist', self.source)

        # get source
        slice1 = pvsimple.FindSource(Source)
        slice1.SliceType = slicetype
        if showSlice:
            pvsimple.Show3DWidgets(proxy=slice1.SliceType)
        else:
            pvsimple.Hide3DWidgets(proxy=slice1.SliceType)
        if slicetype == 'Plane':
            slice1.SliceType.Origin = [float(Position_x), float(Position_y), float(Position_z)]
            slice1.SliceType.Normal = [float(Rotation_x), float(Rotation_y), float(Rotation_z)]
            slice1.SliceType.Offset = float(Length_x)
        elif slicetype == 'Box':
            slice1.SliceType.Position = [float(Position_x), float(Position_y), float(Position_z)]
            slice1.SliceType.Rotation = [float(Rotation_x), float(Rotation_y), float(Rotation_z)]
            slice1.SliceType.Length = [float(Length_x), float(Length_y), float(Length_z)]
        elif slicetype == 'Sphere':
            slice1.SliceType.Center = [float(Position_x), float(Position_y), float(Position_z)]
            slice1.SliceType.Radius = float(Length_x)
        elif slicetype == 'Cylinder':
            slice1.SliceType.Center = [float(Position_x), float(Position_y), float(Position_z)]
            slice1.SliceType.Axis = [float(Rotation_x), float(Rotation_y), float(Rotation_z)]
            slice1.SliceType.Radius = float(Length_x)
        self.render()

    def clip(self):
        Source = self.ui.comboBox_Source_VPZ.currentText()

        print('Source', Source)
        print('Sourcelist', self.source)

        # get source
        paraviewpvd = pvsimple.FindSource(Source)
        # clip name
        for i in range(1000):
            clipname = 'clip' + str(i + 1)
            if clipname not in self.source:
                self.source.append(clipname)
                print(clipname)
                break
        # create a new 'Clip'
        pvsimple.Clip(registrationName=clipname, Input=paraviewpvd)
        self.ui.comboBox_Source_VPZ.addItem(clipname)
        self.ui.comboBox_Source_VPZ.setCurrentText(clipname)
        self.clipapply()

    def clipapply(self):
        Source = self.ui.comboBox_Source_VPZ.currentText()
        cliptype = self.ui.comboBox_ClipType_VPZ.currentText()
        showClip = self.ui.checkBox_ShowClip_VPZ.isChecked()
        Position_x = self.ui.lineEdit_ClipPosition_x_VPZ.text()
        Position_y = self.ui.lineEdit_ClipPosition_y_VPZ.text()
        Position_z = self.ui.lineEdit_ClipPosition_z_VPZ.text()
        Rotation_x = self.ui.lineEdit_ClipRotation_x_VPZ.text()
        Rotation_y = self.ui.lineEdit_ClipRotation_y_VPZ.text()
        Rotation_z = self.ui.lineEdit_ClipRotation_z_VPZ.text()
        Length_x = self.ui.lineEdit_ClipLenth_x_VPZ.text()
        Length_y = self.ui.lineEdit_ClipLenth_y_VPZ.text()
        Length_z = self.ui.lineEdit_ClipLenth_z_VPZ.text()

        print('Source', Source)
        print('cliptype', cliptype)
        print('showClip', showClip)
        print('Position', Position_x, Position_y, Position_z)
        print('Rotation', Rotation_x, Rotation_y, Rotation_z)
        print('Length', Length_x, Length_y, Length_z)
        print('Sourcelist', self.source)

        # get source
        clip1 = pvsimple.FindSource(Source)
        clip1.ClipType = cliptype
        # print('start')
        # print(type(clip1.ClipType))
        # print(dir(clip1.ClipType))
        # print('end')
        if showClip:
            pvsimple.Show3DWidgets(proxy=clip1.ClipType)
        else:
            pvsimple.Hide3DWidgets(proxy=clip1.ClipType)
        if cliptype == 'Plane':
            clip1.ClipType.Origin = [float(Position_x), float(Position_y), float(Position_z)]
            clip1.ClipType.Normal = [float(Rotation_x), float(Rotation_y), float(Rotation_z)]
            clip1.ClipType.Offset = float(Length_x)
        elif cliptype == 'Box':
            clip1.ClipType.Position = [float(Position_x), float(Position_y), float(Position_z)]
            clip1.ClipType.Rotation = [float(Rotation_x), float(Rotation_y), float(Rotation_z)]
            clip1.ClipType.Length = [float(Length_x), float(Length_y), float(Length_z)]
        elif cliptype == 'Sphere':
            clip1.ClipType.Center = [float(Position_x), float(Position_y), float(Position_z)]
            clip1.ClipType.Radius = float(Length_x)
        elif cliptype == 'Cylinder':
            clip1.ClipType.Center = [float(Position_x), float(Position_y), float(Position_z)]
            clip1.ClipType.Axis = [float(Rotation_x), float(Rotation_y), float(Rotation_z)]
            clip1.ClipType.Radius = float(Length_x)
        self.render()

    def smooth(self):
        SmoothAngle = self.ui.spinBox_SmoothAngle_VPZ.value()
        Source = self.ui.comboBox_Source_VPZ.currentText()

        print('SmoothAngle',SmoothAngle)
        print('Source',Source)
        print('Sourcelist',self.source)

        # get source
        paraviewpvd = pvsimple.FindSource(Source)
        # create a new 'Extract Surface'
        extractSurface1 = pvsimple.ExtractSurface(registrationName='ExtractSurface1', Input=paraviewpvd)
        # smooth source name
        for i in range(1000):
            smoothsourcename = 'smooth'+str(i+1)
            if smoothsourcename not in self.source:
                self.source.append(smoothsourcename)
                print(smoothsourcename)
                break
        # smooth
        generateSurfaceNormals1 = pvsimple.GenerateSurfaceNormals(registrationName=smoothsourcename,Input=extractSurface1)
        generateSurfaceNormals1.FeatureAngle = SmoothAngle
        self.ui.comboBox_Source_VPZ.addItem(smoothsourcename)
        self.ui.comboBox_Source_VPZ.setCurrentText(smoothsourcename)
        self.render()

    def getRGB(self):
        color=self.ui.lineEdit_colorBackground_VPZ.text()
        try:
            rgb=colors.to_rgba(color)
            self.ui.doubleSpinBox_color_r_VPZ.setValue(rgb[0])
            self.ui.doubleSpinBox_color_g_VPZ.setValue(rgb[1])
            self.ui.doubleSpinBox_color_b_VPZ.setValue(rgb[2])
        except:
            pass

    def getColorBarTitleRGB(self):
        color=self.ui.lineEdit_colorColorBarTitle_VPZ.text()
        try:
            rgb=colors.to_rgba(color)
            self.ui.doubleSpinBox_colorColorBarTitle_r_VPZ.setValue(rgb[0])
            self.ui.doubleSpinBox_colorColorBarTitle_g_VPZ.setValue(rgb[1])
            self.ui.doubleSpinBox_colorColorBarTitle_b_VPZ.setValue(rgb[2])
        except:
            pass

    def getColorBarLabelRGB(self):
        color=self.ui.lineEdit_colorColorBarLabel_VPZ.text()
        try:
            rgb=colors.to_rgba(color)
            self.ui.doubleSpinBox_colorColorBarLabel_r_VPZ.setValue(rgb[0])
            self.ui.doubleSpinBox_colorColorBarLabel_g_VPZ.setValue(rgb[1])
            self.ui.doubleSpinBox_colorColorBarLabel_b_VPZ.setValue(rgb[2])
        except:
            pass

    def getcamera(self):
        Camera = pvsimple.GetActiveCamera()
        CameraPosition = list(Camera.GetPosition())
        CameraFocalPoint = list(Camera.GetFocalPoint())
        CameraViewUp = list(Camera.GetViewUp())
        CameraParallelScale = Camera.GetParallelScale()
        self.ui.lineEdit_CameraPosition_VPZ.setText('{}'.format(CameraPosition))
        self.ui.lineEdit_CameraFocalPoint_VPZ.setText('{}'.format(CameraFocalPoint))
        self.ui.lineEdit_ViewUp_VPZ.setText('{}'.format(CameraViewUp))
        self.ui.lineEdit_ParallelScale_VPZ.setText('{}'.format(CameraParallelScale))
        self.ui.plainTextEdit_CameraSet_VPZ.setPlainText('Position: {}\nFocalPoint: {}\nViewUp: {}\nParallelScale: {}'.format(CameraPosition,CameraFocalPoint,CameraViewUp,CameraParallelScale))

    def getpointarray(self):
        Source = self.ui.comboBox_Source_VPZ.currentText()
        paraviewpvd = pvsimple.FindSource(Source)
        # print(dir(paraviewpvd))
        # print(paraviewpvd.PointDataArrays)
        self.ui.comboBox_viewresult_VPZ.clear()
        try:
            self.ui.comboBox_viewresult_VPZ.addItems(paraviewpvd.PointArrayStatus)
        except:
            self.ui.comboBox_viewresult_VPZ.addItems(paraviewpvd.PointArrays)

    def render(self,animation='Render'):
        result = self.ui.comboBox_viewresult_VPZ.currentText()
        Source = self.ui.comboBox_Source_VPZ.currentText()
        NumberOfTableValues = self.ui.spinBox_NumberOfTableValues_VPZ.value()
        ColorBarType = self.ui.comboBox_ColorBarType_VPZ.currentText()
        ColorPreset = self.ui.plainTextEdit_ColorPreset_VPZ.toPlainText()
        ShowColorBar = self.ui.checkBox_ShowColorBar_VPZ.isChecked()
        ChangeDisplayRange = self.ui.checkBox_ChangeDisplayRange_VPZ.isChecked()
        SetCamera = self.ui.checkBox_SetCamera_VPZ.isChecked()
        MinimumValue = self.ui.doubleSpinBox_MinimumValue_VPZ.value()
        MaximumValue = self.ui.doubleSpinBox_MaximumValue_VPZ.value()
        ColorBarTitle = self.ui.lineEdit_ColorBarTitle_VPZ.text()
        ComponentTitle = self.ui.lineEdit_ComponentTitle_VPZ.text()
        CameraPosition = self.ui.lineEdit_CameraPosition_VPZ.text()
        CameraFocalPoint = self.ui.lineEdit_CameraFocalPoint_VPZ.text()
        CameraViewUp = self.ui.lineEdit_ViewUp_VPZ.text()
        CameraParallelScale = self.ui.lineEdit_ParallelScale_VPZ.text()
        changebackground = self.ui.checkBox_ChangeBackground_VPZ.isChecked()
        color_r = self.ui.doubleSpinBox_color_r_VPZ.value()
        color_g = self.ui.doubleSpinBox_color_g_VPZ.value()
        color_b = self.ui.doubleSpinBox_color_b_VPZ.value()
        ColorBarTitleSet = self.ui.checkBox_ChangeColorBarTitle_VPZ.isChecked()
        colorColorBarTitle_r = self.ui.doubleSpinBox_colorColorBarTitle_r_VPZ.value()
        colorColorBarTitle_g = self.ui.doubleSpinBox_colorColorBarTitle_g_VPZ.value()
        colorColorBarTitle_b = self.ui.doubleSpinBox_colorColorBarTitle_b_VPZ.value()
        ColorBarTitleFont = self.ui.comboBox_ColorBarTitleFont_VPZ.currentText()
        ColorBarTitleFontSize = self.ui.spinBox_ColorBarTitleFontSize_VPZ.value()
        ColorBarTitleOpacity = self.ui.doubleSpinBox_ColorBarTitleOpacity_VPZ.value()
        ColorBarTitleBold = self.ui.checkBox_ColorBarTitleBold_VPZ.isChecked()
        ColorBarTitleItalic = self.ui.checkBox_ColorBarTitleItalic_VPZ.isChecked()
        ColorBarTitleShadow = self.ui.checkBox_ColorBarTitleShadow_VPZ.isChecked()
        ColorBarLabelSet = self.ui.checkBox_ChangeColorBarLabel_VPZ.isChecked()
        colorColorBarLabel_r = self.ui.doubleSpinBox_colorColorBarLabel_r_VPZ.value()
        colorColorBarLabel_g = self.ui.doubleSpinBox_colorColorBarLabel_g_VPZ.value()
        colorColorBarLabel_b = self.ui.doubleSpinBox_colorColorBarLabel_b_VPZ.value()
        ColorBarLabelFont = self.ui.comboBox_ColorBarLabelFont_VPZ.currentText()
        ColorBarLabelFontSize = self.ui.spinBox_ColorBarLabelFontSize_VPZ.value()
        ColorBarLabelOpacity = self.ui.doubleSpinBox_ColorBarLabelOpacity_VPZ.value()
        ColorBarLabelBold = self.ui.checkBox_ColorBarLabelBold_VPZ.isChecked()
        ColorBarLabelItalic = self.ui.checkBox_ColorBarLabelItalic_VPZ.isChecked()
        ColorBarLabelShadow = self.ui.checkBox_ColorBarLabelShadow_VPZ.isChecked()
        SetColorBarShape = self.ui.checkBox_SetColorBarShape_VPZ.isChecked()
        ColorBarThickness = self.ui.spinBox_ColorBarThickness_VPZ.value()
        ColorBarLength = self.ui.doubleSpinBox_ColorBarLenth_VPZ.value()
        SetColorBarLocation = self.ui.checkBox_SetColorBarLocation_VPZ.isChecked()
        ColorBarLocation = self.ui.comboBox_ColorBarLocation_VPZ.currentText()
        ColorBarPosition1 = self.ui.doubleSpinBox_ColorBarLenth1_VPZ.value()
        ColorBarPosition2 = self.ui.doubleSpinBox_ColorBarLenth2_VPZ.value()

        print('result',result)
        print('Source',Source)
        print('NumberOfTableValues',NumberOfTableValues)
        print('ColorBarType',ColorBarType)
        print('ColorPreset',ColorPreset)
        print('ShowColorBar',ShowColorBar)
        print('ChangeDisplayRange',ChangeDisplayRange)
        print('SetCamera',SetCamera)
        print('MinimumValue',MinimumValue)
        print('MaximumValue',MaximumValue)
        print('ColorBarTitle',ColorBarTitle)
        print('ComponentTitle',ComponentTitle)
        print('CameraPosition',CameraPosition)
        print('CameraFocalPoint',CameraFocalPoint)
        print('CameraViewUp',CameraViewUp)
        print('CameraParallelScale',CameraParallelScale)
        print('changebackground',changebackground)
        print('colorbackground_r',color_r)
        print('colorbackground_g',color_g)
        print('colorbackground_b',color_b)
        print('ColorBarTitleSet',ColorBarTitleSet)
        print('colorColorBarTitle_r',colorColorBarTitle_r)
        print('colorColorBarTitle_g',colorColorBarTitle_g)
        print('colorColorBarTitle_b',colorColorBarTitle_b)
        print('ColorBarTitleFont',ColorBarTitleFont)
        print('ColorBarTitleFontSize',ColorBarTitleFontSize)
        print('ColorBarTitleOpacity',ColorBarTitleOpacity)
        print('ColorBarTitleBold',ColorBarTitleBold)
        print('ColorBarTitleItalic',ColorBarTitleItalic)
        print('ColorBarTitleShadow',ColorBarTitleShadow)
        print('ColorBarLabelSet',ColorBarLabelSet)
        print('colorColorBarLabel_r',colorColorBarLabel_r)
        print('colorColorBarLabel_g',colorColorBarLabel_g)
        print('colorColorBarLabel_b',colorColorBarLabel_b)
        print('ColorBarLabelFont',ColorBarLabelFont)
        print('ColorBarLabelFontSize',ColorBarLabelFontSize)
        print('ColorBarLabelOpacity',ColorBarLabelOpacity)
        print('ColorBarLabelBold',ColorBarLabelBold)
        print('ColorBarLabelItalic',ColorBarLabelItalic)
        print('ColorBarLabelShadow',ColorBarLabelShadow)
        print('SetColorBarShape',SetColorBarShape)
        print('ColorBarThickness',ColorBarThickness)
        print('ColorBarLength',ColorBarLength)
        print('SetColorBarLocation',SetColorBarLocation)
        print('ColorBarLocation',ColorBarLocation)
        print('ColorBarPosition2',ColorBarPosition2)
        print('ColorBarPosition1',ColorBarPosition1)

        # get active view
        renderView1 = pvsimple.GetActiveView()

        # find settings proxy
        # renderViewInteractionSettings = pvsimple.GetSettingsProxy('RenderViewInteractionSettings')
        # print(dir(renderViewInteractionSettings))
        # print(help(renderViewInteractionSettings))

        # hide data in view
        pvsimple.HideAll(renderView1)
        # get source
        paraviewpvd = pvsimple.FindSource(Source)
        # display source
        paraviewpvdDisplay = pvsimple.Show(paraviewpvd, renderView1)

        # bounds = paraviewpvd.GetDataInformation().GetBounds()
        # print('bounds',bounds)
        # sphere = pvsimple.Box()
        # print(type(sphere))
        # print(dir(sphere))
        # sphere.Center = [0.5*(bounds[0]+bounds[1]), 0.5*(bounds[2]+bounds[3]), 0.5*(bounds[4]+bounds[5])]
        # sphere.XLength = bounds[1]-bounds[0]
        # sphere.YLength = bounds[3]-bounds[2]
        # sphere.ZLength = bounds[5]-bounds[4]
        # pvsimple.Show(sphere)
        # pvsimple.Render()


        # set background color
        # print(dir(renderView1))
        # print(dir(renderView1.Background))
        # print(help(renderView1.Background))
        # print(renderView1.Background.GetData())
        if changebackground:
            renderView1.Background = (color_r, color_g, color_b)
            # renderView1.Background2 = (color_r, color_g, color_b)
        # reset view to fit data
        renderView1.ResetCamera()
        # set camera
        if SetCamera:
            renderView1.CameraPosition = ast.literal_eval(CameraPosition)
            renderView1.CameraFocalPoint = ast.literal_eval(CameraFocalPoint)
            renderView1.CameraViewUp = ast.literal_eval(CameraViewUp)
            renderView1.CameraParallelScale = float(CameraParallelScale)
        # set scalar coloring
        pvsimple.ColorBy(paraviewpvdDisplay, ('POINTS', result))
        # get color transfer function
        LUT = pvsimple.GetColorTransferFunction(result)
        # Properties modified
        LUT.NumberOfTableValues = NumberOfTableValues
        # Rescale transfer function
        if ChangeDisplayRange:
            LUT.RescaleTransferFunction(MinimumValue, MaximumValue)
        # import color preset
        for root, dirs, files in os.walk(ColorPreset):
            if files:
                for file in files:
                    if file == ColorBarType+'.json':
                        pvsimple.ImportPresets(filename=root+'/'+file)
                        print('import')
        # Apply a preset using its name.
        LUT.ApplyPreset(ColorBarType, True)
        # get scalar bar
        LUTColorBar = pvsimple.GetScalarBar(LUT, renderView1)
        # set scalar bar Location
        if SetColorBarLocation:
            LUTColorBar.WindowLocation = ColorBarLocation
            if ColorBarLocation == 'AnyLocation':
                LUTColorBar.Position = [ColorBarPosition1, ColorBarPosition2]
        # set scalar bar Shape
        if SetColorBarShape:
            LUTColorBar.ScalarBarThickness = ColorBarThickness
            LUTColorBar.ScalarBarLength = ColorBarLength
        # set scalar bar
        if ColorBarTitleSet:
            LUTColorBar.TitleColor = [colorColorBarTitle_r, colorColorBarTitle_g, colorColorBarTitle_b]
            LUTColorBar.TitleOpacity = ColorBarTitleOpacity
            LUTColorBar.TitleFontFamily = ColorBarTitleFont
            LUTColorBar.TitleBold = ColorBarTitleBold
            LUTColorBar.TitleItalic = ColorBarTitleItalic
            LUTColorBar.TitleShadow = ColorBarTitleShadow
            LUTColorBar.TitleFontSize = ColorBarTitleFontSize
        if ColorBarLabelSet:
            LUTColorBar.LabelColor = [colorColorBarLabel_r, colorColorBarLabel_g, colorColorBarLabel_b]
            LUTColorBar.LabelOpacity = ColorBarLabelOpacity
            LUTColorBar.LabelFontFamily = ColorBarLabelFont
            LUTColorBar.LabelBold = ColorBarLabelBold
            LUTColorBar.LabelItalic = ColorBarLabelItalic
            LUTColorBar.LabelShadow = ColorBarLabelShadow
            LUTColorBar.LabelFontSize = ColorBarLabelFontSize
        # set scalar bar Title
        LUTColorBar.Title = ColorBarTitle
        LUTColorBar.ComponentTitle = ComponentTitle
        # Hides all unused scalar bars from the view
        pvsimple.HideUnusedScalarBars(renderView1)
        # show color bar
        paraviewpvdDisplay.SetScalarBarVisibility(renderView1, ShowColorBar)
        # get animation scene
        animationScene1 = pvsimple.GetAnimationScene()
        if animation == 'Play':
            animationScene1.Play()
        elif animation == 'FirstStep':
            animationScene1.GoToFirst()
        elif animation == 'LastStep':
            animationScene1.GoToLast()
        elif animation == 'NextStep':
            animationScene1.GoToNext()
        pvsimple.Render()

    def choosepvd(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose pvd or vtu file",
                                                 fileTypes="All files (*.*);; pvd files(*.pvd);; vtu files(*.vtu)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_pvdPath_VPZ.setPlainText('{}'.format(filename))

    def choosetimenpy(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose npy file",
                                                 fileTypes="All files (*.*);; npy files(*.npy)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_TimeNpyPath_VPZ.setPlainText('{}'.format(filename))

    def chooseBatchTable(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; csv files(*.csv);; xlsx files(*.xlsx)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_VPZ.setPlainText('{}'.format(filename))

    def chooseOutputFloder(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.plainTextEdit_Output_VPZ.setPlainText(dirname)

    def chooseColorPreset(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Choose directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.plainTextEdit_ColorPreset_VPZ.setPlainText(dirname)

    def setColorBarTitle(self):
        self.ui.lineEdit_ColorBarTitle_VPZ.setText('{}'.format(self.ui.comboBox_viewresult_VPZ.currentText()))

    def savePicture(self):
        OutputFloder = self.ui.plainTextEdit_Output_VPZ.toPlainText()
        PictureName = self.ui.plainTextEdit_SavePicture_VPZ.toPlainText()
        pvsimple.WriteImage('{}/{}.png'.format(OutputFloder,PictureName))

    def loaddata(self):
        pvdPath = self.ui.plainTextEdit_pvdPath_VPZ.toPlainText()
        print('pvdPath', pvdPath)

        tmpSources = pvsimple.GetSources()
        for tmpSource in tmpSources:
            try:
                pvsimple.Delete()
            except:
                pass
        print(tmpSources)
        # load data
        pvsimple.OpenDataFile(pvdPath)
        # Renames the source.
        pvsimple.RenameSource('Model')
        self.source = ['Model']
        self.ui.comboBox_Source_VPZ.clear()
        self.ui.comboBox_Source_VPZ.addItem('Model')

    def showParaview(self):
        SeperateWindow = self.ui.checkBox_SeperateWindow_VPZ.isChecked()
        NoWindow = self.ui.checkBox_NoWindow_VPZ.isChecked()
        WindowHeight = self.ui.spinBox_WindowHeight_VPZ.value()
        WindowWidth = self.ui.spinBox_WindowWidth_VPZ.value()

        print('SeperateWindow',SeperateWindow)
        print('NoWindow',NoWindow)
        print('WindowHeight',WindowHeight)
        print('WindowWidth',WindowWidth)

        if NoWindow:
            render_view = pvsimple.GetActiveViewOrCreate('RenderView')
            render_view.GetRenderWindow().SetSize(WindowHeight, WindowWidth)
        elif SeperateWindow:
            render_view = pvsimple.GetActiveViewOrCreate('RenderView')
            pvsimple.Show3DWidgets()
            render_view.GetRenderWindow().SetSize(WindowHeight, WindowWidth)
        else:
            render_view = pvsimple.CreateRenderView()
            render_widget = QVTKRenderWindowInteractor(rw=render_view.GetRenderWindow(),iren=render_view.GetInteractor())
            render_widget.Initialize()
            dock = QT_GUI.CreateDockWidget(parent=self.modelui, name="Paraview", position='Right')
            frame = dock.GetFrame()
            layout = dock.GetLayout()
            layout.addWidget(render_widget)
            frame.setLayout(layout)

    # def saveAnimationGif(self):
    #     # save animation
    #     pvsimple.SaveAnimation('E:/Coronary/a11_30_coronary/FFR1/FFR2/PostProssingtest1229/Paraview/picture/test.avi',
    #                   ImageResolution=[960, 828],
    #                   FontScaling='Scale fonts proportionally',
    #                   OverrideColorPalette='',
    #                   StereoMode='No change',
    #                   TransparentBackground=0,
    #                   FrameRate=10,
    #                   FrameWindow=[0, 100],
    #                   # Video For Windows options
    #                   Quality='2',
    #                   CompressorFourCC='I420')

    def saveGif(self):
        OutputFolder = self.ui.plainTextEdit_Output_VPZ.toPlainText()
        GifName = self.ui.plainTextEdit_SaveGif_VPZ.toPlainText()
        TimesNpyPath = self.ui.plainTextEdit_TimeNpyPath_VPZ.toPlainText()
        GifFps = self.ui.doubleSpinBox_GifFps_VPZ.value()
        GifTime = self.ui.doubleSpinBox_GifTime_VPZ.value()

        print('OutputFolder',OutputFolder)
        print('GifName',GifName)
        print('TimesNpyPath',TimesNpyPath)
        print('GifFps',GifFps)
        print('GifTime',GifTime)

        timenpy = np.load('{}'.format(TimesNpyPath))
        if GifTime == 0:
            fps = GifFps
        else:
            fps = len(timenpy)/GifTime

        # get animation scene
        animationScene1 = pvsimple.GetAnimationScene()
        gif_images = []
        # make a folder
        os.mkdir(OutputFolder+'/'+GifName)
        for i in range(len(timenpy)):
            animationScene1.AnimationTime = timenpy[i]
            pvsimple.WriteImage('{}/{}/{}.png'.format(OutputFolder,GifName,i))
            gif_images.append(imageio.imread('{}/{}/{}.png'.format(OutputFolder,GifName,i)))
        imageio.mimsave('{}/{}.gif'.format(OutputFolder,GifName),gif_images, fps=fps)

    def batchRun(self):
        inpath = self.ui.plainTextEdit_BatchTable_VPZ.toPlainText()
        if 'csv' in inpath:
            DataFrame = pd.read_csv(inpath)
        elif 'xls' in inpath:
            DataFrame = pd.read_excel(inpath)
        else:
            raise ValueError("Cannot open dataframe of: {}".format(inpath))
        for linenum in range(len(DataFrame)):
            # get line of table
            print('get info in line', linenum)
            info = DataFrame.iloc[linenum].fillna('')

            InputPath = ''
            HideWindow = True
            SeperateWindow = True
            WindowHeight = 800
            WindowWidth = 800
            Smooth = False
            SmoothAngle = 70
            ViewResult = 'Velocity'
            ShowColorBar = True
            SetColorBarShape = False
            ColorBarThickness = 16
            ColorBarLength = 0.33
            SetColorBarLocation = False
            ColorBarLocation = 'LowerRightCorner'
            ColorBarPosition1 = 0.78
            ColorBarPosition2 = 0.02
            ChangeDisplayRange = False
            MinimumValue = 0
            MaximunValue = 10
            NumberOfTableValues = 1024
            ColorPreset = ''
            ColorBarType = 'Jet'
            ColorBarTitle = 'Velocity'
            ComponentTitle = ''
            ColorBarTitleSet = False
            ColorBarTitleColor = 'black'
            ColorBarTitleFont = 'Arial'
            ColorBarTitleFontSize = 15
            ColorBarTitleOpacity = 1
            ColorBarTitleBold = False
            ColorBarTitleItalic = False
            ColorBarTitleShadow = False
            ColorBarLabelSet = False
            ColorBarLabelColor = 'black'
            ColorBarLabelFont = 'Arial'
            ColorBarLabelFontSize = 15
            ColorBarLabelOpacity = 1
            ColorBarLabelBold = False
            ColorBarLabelItalic = False
            ColorBarLabelShadow = False
            SetCamera = False
            CameraPosition = ''
            CameraFocalPoint = ''
            CameraViewUp = ''
            CameraParallelScale = ''
            ChangeBackground = True
            BackgroundColor = 'white'
            OutputFloder = ''
            PictureName = ''
            SavePicture = True
            TimesNpyPath = ''
            GifFps = 18
            GifTime = 5
            GifName = ''
            SaveGif = True

            try:
                if info["InputPath"]:
                    InputPath = info["InputPath"]
            except:
                pass
            try:
                if isinstance(info["HideWindow"], np.bool_):
                    HideWindow = info["HideWindow"]
            except:
                pass
            try:
                if isinstance(info["SeperateWindow"], np.bool_):
                    SeperateWindow = info["SeperateWindow"]
            except:
                pass
            try:
                if info["WindowHeight"]:
                    WindowHeight = info["WindowHeight"]
            except:
                pass
            try:
                if info["WindowWidth"]:
                    WindowWidth = info["WindowWidth"]
            except:
                pass
            try:
                if isinstance(info["Smooth"], np.bool_):
                    Smooth = info["Smooth"]
            except:
                pass
            try:
                if info["SmoothAngle"]:
                    SmoothAngle = info["SmoothAngle"]
            except:
                pass
            try:
                if info["ViewResult"]:
                    ViewResult = info["ViewResult"]
            except:
                pass
            try:
                if isinstance(info["ShowColorBar"], np.bool_):
                    ShowColorBar = info["ShowColorBar"]
            except:
                pass
            try:
                if isinstance(info["SetColorBarShape"], np.bool_):
                    SetColorBarShape = info["SetColorBarShape"]
            except:
                pass
            try:
                if info["ColorBarThickness"]:
                    ColorBarThickness = info["ColorBarThickness"]
            except:
                pass
            try:
                if info["ColorBarLength"]:
                    ColorBarLength = info["ColorBarLength"]
            except:
                pass
            try:
                if isinstance(info["SetColorBarLocation"], np.bool_):
                    SetColorBarLocation = info["SetColorBarLocation"]
            except:
                pass
            try:
                if info["ColorBarLocation"]:
                    ColorBarLocation = info["ColorBarLocation"]
            except:
                pass
            try:
                if info["ColorBarPosition1"]:
                    ColorBarPosition1 = info["ColorBarPosition1"]
            except:
                pass
            try:
                if info["ColorBarPosition2"]:
                    ColorBarPosition2 = info["ColorBarPosition2"]
            except:
                pass
            try:
                if isinstance(info["ChangeDisplayRange"], np.bool_):
                    ChangeDisplayRange = info["ChangeDisplayRange"]
            except:
                pass
            try:
                if info["MinimumValue"]:
                    MinimumValue = info["MinimumValue"]
            except:
                pass
            try:
                if info["MaximunValue"]:
                    MaximunValue = info["MaximunValue"]
            except:
                pass
            try:
                if info["NumberOfTableValues"]:
                    NumberOfTableValues = info["NumberOfTableValues"]
            except:
                pass
            try:
                if info["ColorPreset"]:
                    ColorPreset = info["ColorPreset"]
            except:
                pass
            try:
                if info["ColorBarType"]:
                    ColorBarType = info["ColorBarType"]
            except:
                pass
            try:
                if info["ColorBarTitle"]:
                    ColorBarTitle = info["ColorBarTitle"]
            except:
                pass
            try:
                if info["ComponentTitle"]:
                    ComponentTitle = info["ComponentTitle"]
            except:
                pass
            try:
                if isinstance(info["ColorBarTitleSet"], np.bool_):
                    ColorBarTitleSet = info["ColorBarTitleSet"]
            except:
                pass
            try:
                if info["ColorBarTitleColor"]:
                    ColorBarTitleColor = info["ColorBarTitleColor"]
            except:
                pass
            try:
                if info["ColorBarTitleFont"]:
                    ColorBarTitleFont = info["ColorBarTitleFont"]
            except:
                pass
            try:
                if info["ColorBarTitleFontSize"]:
                    ColorBarTitleFontSize = info["ColorBarTitleFontSize"]
            except:
                pass
            try:
                if info["ColorBarTitleOpacity"]:
                    ColorBarTitleOpacity = info["ColorBarTitleOpacity"]
            except:
                pass
            try:
                if isinstance(info["ColorBarTitleBold"], np.bool_):
                    ColorBarTitleBold = info["ColorBarTitleBold"]
            except:
                pass
            try:
                if isinstance(info["ColorBarTitleItalic"], np.bool_):
                    ColorBarTitleItalic = info["ColorBarTitleItalic"]
            except:
                pass
            try:
                if isinstance(info["ColorBarTitleShadow"], np.bool_):
                    ColorBarTitleShadow = info["ColorBarTitleShadow"]
            except:
                pass
            try:
                if isinstance(info["ColorBarLabelSet"], np.bool_):
                    ColorBarLabelSet = info["ColorBarLabelSet"]
            except:
                pass
            try:
                if info["ColorBarLabelColor"]:
                    ColorBarLabelColor = info["ColorBarLabelColor"]
            except:
                pass
            try:
                if info["ColorBarLabelFont"]:
                    ColorBarLabelFont = info["ColorBarLabelFont"]
            except:
                pass
            try:
                if info["ColorBarLabelFontSize"]:
                    ColorBarLabelFontSize = info["ColorBarLabelFontSize"]
            except:
                pass
            try:
                if info["ColorBarLabelOpacity"]:
                    ColorBarLabelOpacity = info["ColorBarLabelOpacity"]
            except:
                pass
            try:
                if isinstance(info["ColorBarLabelBold"], np.bool_):
                    ColorBarLabelBold = info["ColorBarLabelBold"]
            except:
                pass
            try:
                if isinstance(info["ColorBarLabelItalic"], np.bool_):
                    ColorBarLabelItalic = info["ColorBarLabelItalic"]
            except:
                pass
            try:
                if isinstance(info["ColorBarLabelShadow"], np.bool_):
                    ColorBarLabelShadow = info["ColorBarLabelShadow"]
            except:
                pass
            try:
                if isinstance(info["SetCamera"], np.bool_):
                    SetCamera = info["SetCamera"]
            except:
                pass
            try:
                if info["CameraPosition"]:
                    CameraPosition = info["CameraPosition"]
            except:
                pass
            try:
                if info["CameraFocalPoint"]:
                    CameraFocalPoint = info["CameraFocalPoint"]
            except:
                pass
            try:
                if info["CameraViewUp"]:
                    CameraViewUp = info["CameraViewUp"]
            except:
                pass
            try:
                if info["CameraParallelScale"]:
                    CameraParallelScale = info["CameraParallelScale"]
            except:
                pass
            try:
                if isinstance(info["ChangeBackground"], np.bool_):
                    ChangeBackground = info["ChangeBackground"]
            except:
                pass
            try:
                if info["BackgroundColor"]:
                    BackgroundColor = info["BackgroundColor"]
            except:
                pass
            try:
                if info["OutputFloder"]:
                    OutputFloder = info["OutputFloder"]
            except:
                pass
            try:
                if info["PictureName"]:
                    PictureName = info["PictureName"]
            except:
                pass
            try:
                if isinstance(info["SavePicture"], np.bool_):
                    SavePicture = info["SavePicture"]
            except:
                pass
            try:
                if info["TimesNpyPath"]:
                    TimesNpyPath = info["TimesNpyPath"]
            except:
                pass
            try:
                if info["GifFps"]:
                    GifFps = info["GifFps"]
            except:
                pass
            try:
                if info["GifTime"]:
                    GifTime = info["GifTime"]
            except:
                pass
            try:
                if info["GifName"]:
                    GifName = info["GifName"]
            except:
                pass
            try:
                if isinstance(info["SaveGif"], np.bool_):
                    SaveGif = info["SaveGif"]
            except:
                pass
            #set ui
            self.ui.plainTextEdit_pvdPath_VPZ.setPlainText('{}'.format(InputPath))
            self.loaddata()
            self.getpointarray()

            self.ui.checkBox_NoWindow_VPZ.setChecked(HideWindow)
            self.ui.checkBox_SeperateWindow_VPZ.setChecked(SeperateWindow)
            self.ui.spinBox_WindowHeight_VPZ.setValue(WindowHeight)
            self.ui.spinBox_WindowWidth_VPZ.setValue(WindowWidth)
            self.ui.spinBox_SmoothAngle_VPZ.setValue(SmoothAngle)
            self.ui.comboBox_viewresult_VPZ.setCurrentText(ViewResult)
            self.ui.checkBox_ShowColorBar_VPZ.setChecked(ShowColorBar)
            self.ui.checkBox_SetColorBarShape_VPZ.setChecked(SetColorBarShape)
            self.ui.spinBox_ColorBarThickness_VPZ.setValue(ColorBarThickness)
            self.ui.doubleSpinBox_ColorBarLenth_VPZ.setValue(ColorBarLength)
            self.ui.checkBox_SetColorBarLocation_VPZ.setChecked(SetColorBarLocation)
            self.ui.comboBox_ColorBarLocation_VPZ.setCurrentText(ColorBarLocation)
            self.ui.doubleSpinBox_ColorBarLenth1_VPZ.setValue(ColorBarPosition1)
            self.ui.doubleSpinBox_ColorBarLenth2_VPZ.setValue(ColorBarPosition2)
            self.ui.checkBox_ChangeDisplayRange_VPZ.setChecked(ChangeDisplayRange)
            self.ui.doubleSpinBox_MinimumValue_VPZ.setValue(MinimumValue)
            self.ui.doubleSpinBox_MaximumValue_VPZ.setValue(MaximunValue)
            self.ui.spinBox_NumberOfTableValues_VPZ.setValue(NumberOfTableValues)
            self.ui.plainTextEdit_ColorPreset_VPZ.setPlainText('{}'.format(ColorPreset))
            self.ui.comboBox_ColorBarType_VPZ.setCurrentText(ColorBarType)
            self.ui.lineEdit_ColorBarTitle_VPZ.setText(ColorBarTitle)
            self.ui.lineEdit_ComponentTitle_VPZ.setText(ComponentTitle)
            self.ui.checkBox_ChangeColorBarTitle_VPZ.setChecked(ColorBarTitleSet)
            self.ui.lineEdit_colorColorBarTitle_VPZ.setText(ColorBarTitleColor)
            self.ui.comboBox_ColorBarTitleFont_VPZ.setCurrentText(ColorBarTitleFont)
            self.ui.spinBox_ColorBarTitleFontSize_VPZ.setValue(ColorBarTitleFontSize)
            self.ui.doubleSpinBox_ColorBarTitleOpacity_VPZ.setValue(ColorBarTitleOpacity)
            self.ui.checkBox_ColorBarTitleBold_VPZ.setChecked(ColorBarTitleBold)
            self.ui.checkBox_ColorBarTitleItalic_VPZ.setChecked(ColorBarTitleItalic)
            self.ui.checkBox_ColorBarTitleShadow_VPZ.setChecked(ColorBarTitleShadow)
            self.ui.checkBox_ChangeColorBarLabel_VPZ.setChecked(ColorBarLabelSet)
            self.ui.lineEdit_colorColorBarLabel_VPZ.setText(ColorBarLabelColor)
            self.ui.comboBox_ColorBarLabelFont_VPZ.setCurrentText(ColorBarLabelFont)
            self.ui.spinBox_ColorBarLabelFontSize_VPZ.setValue(ColorBarLabelFontSize)
            self.ui.doubleSpinBox_ColorBarLabelOpacity_VPZ.setValue(ColorBarLabelOpacity)
            self.ui.checkBox_ColorBarLabelBold_VPZ.setChecked(ColorBarLabelBold)
            self.ui.checkBox_ColorBarLabelItalic_VPZ.setChecked(ColorBarLabelItalic)
            self.ui.checkBox_ColorBarLabelShadow_VPZ.setChecked(ColorBarLabelShadow)
            self.ui.checkBox_SetCamera_VPZ.setChecked(SetCamera)
            self.ui.lineEdit_CameraPosition_VPZ.setText(CameraPosition)
            self.ui.lineEdit_CameraFocalPoint_VPZ.setText(CameraFocalPoint)
            self.ui.lineEdit_ViewUp_VPZ.setText(CameraViewUp)
            self.ui.lineEdit_ParallelScale_VPZ.setText('{}'.format(CameraParallelScale))
            self.ui.checkBox_ChangeBackground_VPZ.setChecked(ChangeBackground)
            self.ui.lineEdit_colorBackground_VPZ.setText(BackgroundColor)
            self.ui.plainTextEdit_Output_VPZ.setPlainText(OutputFloder)
            self.ui.plainTextEdit_SavePicture_VPZ.setPlainText('{}'.format(PictureName))
            self.ui.plainTextEdit_SaveGif_VPZ.setPlainText('{}'.format(GifName))
            self.ui.plainTextEdit_TimeNpyPath_VPZ.setPlainText('{}'.format(TimesNpyPath))
            self.ui.doubleSpinBox_GifFps_VPZ.setValue(GifFps)
            self.ui.doubleSpinBox_GifTime_VPZ.setValue(GifTime)

            self.showParaview()
            self.render()
            if Smooth:
                self.smooth()
            if SavePicture:
                self.savePicture()
            if SaveGif:
                self.saveGif()
            print('Done')


if __name__ == "__main__":
    app = QApplication([])
    try:
        UIPath = sys.argv[1]
    except:
        # UIPath = r"E:\GUI\Hedys_test0620\GUI_V0\ui\main.ui"
        UIPath = None
    try:
        parentsUIPath = sys.argv[2]
    except:
        parentsUIPath = None
    stats = VisualizationParaview(UIPath = UIPath,parentsUIPath = parentsUIPath)
    stats.modelui.show()
    app.exec_()