import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
import QT_GUI
import Preprocess_Mask
import Save_Load_File
import Image_Process_Functions
import pdfunction

import pyvista as pv
from pyvistaqt import QtInteractor
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
import threading
import ast
import time
import numpy as np

class VisualizationPyVista():
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.pushButton_chooseIn_VPVZ.clicked.connect(lambda: self.chooseIn())
        self.ui.pushButton_chooseCutInput1_VPVZ.clicked.connect(lambda: self.chooseCutInput1())
        self.ui.pushButton_chooseOutPut_VPVZ.clicked.connect(lambda: self.chooseOutput())
        self.ui.pushButton_BatchTable_VPVZ.clicked.connect(lambda: self.chooseBatchTable())
        self.ui.pushButton_LoadData_VPVZ.clicked.connect(lambda: self.LoadData())
        self.ui.pushButton_Cut_VPVZ.clicked.connect(lambda: self.Cut())
        self.ui.pushButton_Show_VPVZ.clicked.connect(lambda: self.Show())
        self.ui.pushButton_Save_VPVZ.clicked.connect(lambda: self.Save())
        self.ui.pushButton_BatchRun_VPVZ.clicked.connect(lambda: self.BatchRun())

        self.InitPyVista()

    def InitPyVista(self):
        self.pvdmodel = None
        self.mesh = {}

    def chooseIn(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose infile",
                                                 fileTypes="All files (*.*)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_InPath_VPVZ.setPlainText('{}'.format(filename))

    def chooseCutInput1(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose Cut file",
                                                 fileTypes="All files (*.*)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_CutInput1_VPVZ.setPlainText('{}'.format(filename))

    def chooseOutput(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.plainTextEdit_Output_VPVZ.setPlainText('{}'.format(dirname))

    def chooseBatchTable(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_VPVZ.setPlainText('{}'.format(filename))

    def LoadData(self):
        InPath = self.ui.plainTextEdit_InPath_VPVZ.toPlainText()
        LoadPVD = self.ui.checkBox_LoadPVD_VPVZ.isChecked()
        GetTimestep = self.ui.checkBox_GetTimestep_VPVZ.isChecked()
        SetActivateTimestep = self.ui.checkBox_SetActivateTimestep_VPVZ.isChecked()
        ActivateTimestep = self.ui.comboBox_ActiveTimestep_VPVZ.currentText()
        print('InPath',InPath)
        print('LoadPVD',LoadPVD)
        print('GetTimestep',GetTimestep)
        print('SetActivateTimestep',SetActivateTimestep)
        print('ActivateTimestep',ActivateTimestep)

        self.InitPyVista()
        if LoadPVD:
            self.pvdmodel = pv.PVDReader(InPath)
            if GetTimestep:
                Timestep = [str(j) for j in self.pvdmodel.time_values]
                print(Timestep)
                self.ui.comboBox_ActiveTimestep_VPVZ.clear()
                self.ui.comboBox_ActiveTimestep_VPVZ.addItems(Timestep)
                item, ok = QInputDialog.getItem(
                    QMainWindow(), "select activate timestep", 'timestep', Timestep, 0, False)
                if ok and item:
                    self.ui.comboBox_ActiveTimestep_VPVZ.setCurrentText(item)
            self.pvdmodel.set_active_time_value(self.pvdmodel.time_values[0])
            if SetActivateTimestep:
                self.pvdmodel.set_active_time_value(float(self.ui.comboBox_ActiveTimestep_VPVZ.currentText()))
            self.mesh['OriMesh'] = self.pvdmodel.read()[0]
        else:
            self.mesh['OriMesh'] = pv.read(InPath)
        # print(self.mesh['OriMesh'].array_names)
        self.ui.comboBox_setscalars_VPVZ.clear()
        self.ui.comboBox_setscalars_VPVZ.addItems(self.mesh['OriMesh'].array_names)
        self.ui.comboBox_CurrentMesh_VPVZ.clear()
        self.ui.comboBox_CurrentMesh_VPVZ.addItems(['OriMesh'])

    def Cut(self):
        CurrentMesh = self.ui.comboBox_CurrentMesh_VPVZ.currentText()
        CutMethod = self.ui.comboBox_CutType_VPVZ.currentText()
        invert = self.ui.checkBox_CutInvert_VPVZ.isChecked()
        Shape1 = self.ui.plainTextEdit_CutInput1_VPVZ.toPlainText()
        Shape2 = self.ui.plainTextEdit_CutInput2_VPVZ.toPlainText()
        print('CurrentMesh', CurrentMesh)
        print('CutMethod', CutMethod)
        print('invert', invert)
        print('Shape1', Shape1)
        print('Shape2', Shape2)

        if CutMethod == 'Surface':
            Shape = Preprocess_Mask.StrToLst(strIn=Shape2)["listOut"]
            if Shape[0] == 'Mask':
                DirShape1 = os.path.dirname(Shape1)
                inMsk = Save_Load_File.OpenLoadNIFTI(GUI=False, filePath=Shape1)
                imageMorph = Image_Process_Functions.OpenCloseDilateErrodeSlices(
                    dataMat=inMsk.OriData,
                    funcChoose='Dilation',
                    Thres=0,
                    dilateIncre=int(Shape[1]),
                    binaryMsk=False,
                    axisChoice='3D',
                    iterateDilate='No',
                    sliceStarts=[0],
                    sliceStops=[9999],
                    diameter=int(Shape[1])
                )
                Save_Load_File.MatNIFTISave(MatData=imageMorph["outMask"],
                                            imgPath=os.path.join(DirShape1, 'Dilation_pv.nii.gz'),
                                            imgInfo=inMsk.OriImag,
                                            ConvertDType=True,
                                            refDataMat=inMsk.OriData)
                exeInDict = {}
                exeInDict["EXEPath"] = Shape[2]
                exeInDict["choice"] = 3
                exeInDict["inFilePath1"] = DirShape1+'/Dilation_pv.nii.gz'
                exeInDict["outFilePath1"] = DirShape1+'/Dilation_pv.stl'
                exeInDict["inFilePath2"] = 'Second Mask Path'
                exeInDict["outFilePath2"] = 'First STL path'
                thread = threading.Thread(target=Image_Process_Functions.ReconstructExeRun, args=(exeInDict, False))
                thread.start()
                time.sleep(10)
                Surface = pv.read(exeInDict['outFilePath1'])
            else:
                Surface = pv.read(Shape1)
            for i in range(1000):
                CutName = 'Surfacecut'+str(i+1)
                if CutName not in self.mesh.keys():
                    self.ui.comboBox_CurrentMesh_VPVZ.addItem(CutName)
                    break
            self.mesh[CutName] = self.mesh[CurrentMesh].clip_surface(Surface, invert=invert)
            self.ui.comboBox_CurrentMesh_VPVZ.setCurrentText(CutName)
        elif CutMethod == 'Box':
            for i in range(1000):
                CutName = 'Boxcut'+str(i+1)
                if CutName not in self.mesh.keys():
                    self.ui.comboBox_CurrentMesh_VPVZ.addItem(CutName)
                    break
            self.mesh[CutName] = self.mesh[CurrentMesh].clip_box(bounds=ast.literal_eval(Shape1), invert=invert)
            self.ui.comboBox_CurrentMesh_VPVZ.setCurrentText(CutName)
        elif CutMethod == 'Plane':
            for i in range(1000):
                CutName = 'Planecut' + str(i + 1)
                if CutName not in self.mesh.keys():
                    self.ui.comboBox_CurrentMesh_VPVZ.addItem(CutName)
                    break
            self.mesh[CutName] = self.mesh[CurrentMesh].clip(
                normal=ast.literal_eval(Shape1), origin=ast.literal_eval(Shape2))
            self.ui.comboBox_CurrentMesh_VPVZ.setCurrentText(CutName)
        elif CutMethod == 'Slice':
            for i in range(1000):
                CutName = 'Slicecut' + str(i + 1)
                if CutName not in self.mesh.keys():
                    self.ui.comboBox_CurrentMesh_VPVZ.addItem(CutName)
                    break
            self.mesh[CutName] = self.mesh[CurrentMesh].slice(
                normal=ast.literal_eval(Shape1), origin=ast.literal_eval(Shape2))
            self.ui.comboBox_CurrentMesh_VPVZ.setCurrentText(CutName)

        # pl = pv.Plotter()
        # pl.add_mesh(self.mesh[CutName], color='white', show_edges=True)
        # pl.show()

    def Show(self):
        pldict={'color': None, 'style': None, 'scalars': None, 'clim': None, 'show_edges': None, 'edge_color': None,
                'point_size': 5.0, 'line_width': None, 'opacity': 1.0, 'flip_scalars': False, 'lighting': None,
                'n_colors': 256, 'interpolate_before_map': True, 'cmap': None, 'label': None, 'reset_camera': None,
                'scalar_bar_args': None, 'show_scalar_bar': None, 'multi_colors': False, 'name': None, 'texture': None,
                'render_points_as_spheres': None, 'render_lines_as_tubes': False, 'smooth_shading': None,
                'split_sharp_edges': False, 'ambient': 0.0, 'diffuse': 1.0, 'specular': 0.0, 'specular_power': 100.0,
                'nan_color': None, 'nan_opacity': 1.0, 'culling': None, 'rgb': None, 'categories': False,
                'silhouette': False, 'use_transparency': False, 'below_color': None, 'above_color': None,
                'annotations': None, 'pickable': True, 'preference': 'point', 'log_scale': False, 'pbr': False,
                'metallic': 0.0, 'roughness': 0.5, 'render': True, 'component': None}

        PlotMethod = self.ui.comboBox_CutType_VPVZ.currentText()
        CurrentMesh = self.ui.comboBox_CurrentMesh_VPVZ.currentText()
        if self.ui.checkBox_meshcolor_VPVZ.isChecked():
            pldict['color'] = self.ui.plainTextEdit_Color_VPVZ.toPlainText()
        pldict['style'] = self.ui.comboBox_Style_VPVZ.currentText()
        if self.ui.checkBox_setscalars_VPVZ.isChecked():
            pldict['scalars'] = self.ui.comboBox_setscalars_VPVZ.currentText()
        if self.ui.checkBox_ChangeDisplayRange_VPVZ.isChecked():
            pldict['clim'] = ast.literal_eval(self.ui.plainTextEdit_DisplayRange_VPVZ.toPlainText())
        pldict['show_edges'] = self.ui.checkBox_show_edges_VPVZ.isChecked()
        if self.ui.checkBox_edge_color_VPVZ.isChecked():
            pldict['edge_color'] = self.ui.plainTextEdit_edge_color_VPVZ.toPlainText()
        if self.ui.checkBox_point_size_VPVZ.isChecked():
            pldict['point_size'] = self.ui.doubleSpinBox_point_size_VPVZ.value()
        if self.ui.checkBox_line_width_VPVZ.isChecked():
            pldict['line_width'] = self.ui.doubleSpinBox_line_width_VPVZ.value()
        if self.ui.checkBox_opacity_VPVZ.isChecked():
            pldict['opacity'] = self.ui.doubleSpinBox_opacity_VPVZ.value()
        if self.ui.checkBox_n_colors_VPVZ.isChecked():
            pldict['n_colors'] = self.ui.spinBox_n_colors_VPVZ.value()
        if self.ui.checkBox_colormap_VPVZ.isChecked():
            pldict['cmap'] = self.ui.plainTextEdit_colormap_VPVZ.toPlainText()
        pldict['flip_scalars'] = self.ui.checkBox_flip_scalars_VPVZ.isChecked()
        if self.ui.checkBox_lighting_VPVZ.isChecked():
            pldict['lighting'] = False
        pldict['label'] = self.ui.plainTextEdit_label_VPVZ.toPlainText()
        pldict['name'] = self.ui.plainTextEdit_name_VPVZ.toPlainText()
        pldict['reset_camera'] = self.ui.checkBox_reset_camera_VPVZ.isChecked()
        pldict['show_scalar_bar'] = self.ui.checkBox_show_scalar_bar_VPVZ.isChecked()
        pldict['render_lines_as_tubes'] = self.ui.checkBox_render_lines_as_tubes_VPVZ.isChecked()
        pldict['render_points_as_spheres'] = self.ui.checkBox_render_points_as_spheres_VPVZ.isChecked()
        pldict['smooth_shading'] = self.ui.checkBox_smooth_shading_VPVZ.isChecked()
        pldict['split_sharp_edges'] = self.ui.checkBox_split_sharp_edges_VPVZ.isChecked()
        if self.ui.checkBox_nan_color_VPVZ.isChecked():
            pldict['nan_color'] = self.ui.plainTextEdit_nan_color_VPVZ.toPlainText()
        if self.ui.checkBox_specular_power_VPVZ.isChecked():
            pldict['specular_power'] = self.ui.doubleSpinBox_specular_power_VPVZ.value()
        if self.ui.checkBox_nan_opacity_VPVZ.isChecked():
            pldict['nan_opacity'] = self.ui.doubleSpinBox_nan_opacity_VPVZ.value()
        pldict['interpolate_before_map'] = self.ui.checkBox_interpolate_before_map_VPVZ.isChecked()
        background_color = self.ui.plainTextEdit_background_color_VPVZ.toPlainText()
        if self.ui.checkBox_specular_VPVZ.isChecked():
            pldict['specular'] = self.ui.doubleSpinBox_specular_VPVZ.value()
        if self.ui.checkBox_diffuse_VPVZ.isChecked():
            pldict['diffuse'] = self.ui.doubleSpinBox_diffuse_VPVZ.value()
        if self.ui.checkBox_ambient_VPVZ.isChecked():
            pldict['ambient'] = self.ui.doubleSpinBox_ambient_VPVZ.value()
        Shape1 = self.ui.plainTextEdit_CutInput1_VPVZ.toPlainText()
        Shape2 = self.ui.plainTextEdit_CutInput2_VPVZ.toPlainText()
        invert = self.ui.checkBox_CutInvert_VPVZ.isChecked()
        print('PlotMethod', PlotMethod)
        print('CurrentMesh', CurrentMesh)
        print('background_color', background_color)
        print('pldict', pldict)
        print('Shape1', Shape1)
        print('Shape2', Shape2)
        print('invert', invert)

        if self.modelui:
            ui = self.modelui
        else:
            ui = self.ui
        dock = QT_GUI.CreateDockWidget(parent=ui, name="Initial Display", position='Right')
        frame = dock.GetFrame()
        layout = dock.GetLayout()
        pl = QtInteractor(frame)
        layout.addWidget(pl)
        frame.setLayout(layout)
        if self.ui.checkBox_background_color_VPVZ.isChecked():
            pl.background_color = background_color

        if PlotMethod == 'Surface':
            pl.add_mesh(self.mesh[CurrentMesh], color=pldict['color'], style=pldict['style'], scalars=pldict['scalars'],
                        clim=pldict['clim'], show_edges=pldict['show_edges'], edge_color=pldict['edge_color'],
                        point_size=pldict['point_size'], line_width=pldict['line_width'], opacity=pldict['opacity'],
                        flip_scalars=pldict['flip_scalars'], lighting=pldict['lighting'], n_colors=pldict['n_colors'],
                        interpolate_before_map=pldict['interpolate_before_map'], cmap=pldict['cmap'],
                        label=pldict['label'], reset_camera=pldict['reset_camera'],
                        scalar_bar_args=pldict['scalar_bar_args'], show_scalar_bar=pldict['show_scalar_bar'],
                        multi_colors=pldict['multi_colors'], name=pldict['name'], texture=pldict['texture'],
                        render_points_as_spheres=pldict['render_points_as_spheres'],
                        render_lines_as_tubes=pldict['render_lines_as_tubes'], smooth_shading=pldict['smooth_shading'],
                        split_sharp_edges=pldict['split_sharp_edges'], ambient=pldict['ambient'],
                        diffuse=pldict['diffuse'], specular=pldict['specular'], specular_power=pldict['specular_power'],
                        nan_color=pldict['nan_color'], nan_opacity=pldict['nan_opacity'], culling=pldict['culling'],
                        rgb=pldict['rgb'], categories=pldict['categories'], silhouette=pldict['silhouette'],
                        use_transparency=pldict['use_transparency'], below_color=pldict['below_color'],
                        above_color=pldict['above_color'], annotations=pldict['annotations'],
                        pickable=pldict['pickable'], preference=pldict['preference'], log_scale=pldict['log_scale'],
                        pbr=pldict['pbr'], metallic=pldict['metallic'], roughness=pldict['roughness'],
                        render=pldict['render'], component=pldict['component'])
        elif PlotMethod == 'Plane':
            pl.add_mesh_clip_plane(self.mesh[CurrentMesh], invert=invert, normal=ast.literal_eval(Shape1),
                                   color=pldict['color'], style=pldict['style'], scalars=pldict['scalars'],
                                   clim=pldict['clim'], show_edges=pldict['show_edges'],
                                   edge_color=pldict['edge_color'], point_size=pldict['point_size'],
                                   line_width=pldict['line_width'], opacity=pldict['opacity'],
                                   flip_scalars=pldict['flip_scalars'], lighting=pldict['lighting'],
                                   n_colors=pldict['n_colors'], interpolate_before_map=pldict['interpolate_before_map'],
                                   cmap=pldict['cmap'], label=pldict['label'], reset_camera=pldict['reset_camera'],
                                   scalar_bar_args=pldict['scalar_bar_args'], show_scalar_bar=pldict['show_scalar_bar'],
                                   multi_colors=pldict['multi_colors'], name=pldict['name'], texture=pldict['texture'],
                                   render_points_as_spheres=pldict['render_points_as_spheres'],
                                   render_lines_as_tubes=pldict['render_lines_as_tubes'],
                                   smooth_shading=pldict['smooth_shading'],
                                   split_sharp_edges=pldict['split_sharp_edges'], ambient=pldict['ambient'],
                                   diffuse=pldict['diffuse'], specular=pldict['specular'],
                                   specular_power=pldict['specular_power'], nan_color=pldict['nan_color'],
                                   nan_opacity=pldict['nan_opacity'], culling=pldict['culling'], rgb=pldict['rgb'],
                                   categories=pldict['categories'], silhouette=pldict['silhouette'],
                                   use_transparency=pldict['use_transparency'], below_color=pldict['below_color'],
                                   above_color=pldict['above_color'], annotations=pldict['annotations'],
                                   pickable=pldict['pickable'], preference=pldict['preference'],
                                   log_scale=pldict['log_scale'], pbr=pldict['pbr'], metallic=pldict['metallic'],
                                   roughness=pldict['roughness'], render=pldict['render'],
                                   component=pldict['component'])
            for i in range(1000):
                CutName = 'Planecut'+str(i+1)
                if CutName not in self.mesh.keys():
                    self.ui.comboBox_CurrentMesh_VPVZ.addItem(CutName)
                    break
            self.mesh[CutName] = pl.plane_clipped_meshes[-1]
            self.ui.comboBox_CurrentMesh_VPVZ.setCurrentText(CutName)
        elif PlotMethod == 'Slice':
            pl.add_mesh_slice(self.mesh[CurrentMesh], normal=ast.literal_eval(Shape1), color=pldict['color'],
                              style=pldict['style'], scalars=pldict['scalars'], clim=pldict['clim'],
                              show_edges=pldict['show_edges'], edge_color=pldict['edge_color'],
                              point_size=pldict['point_size'], line_width=pldict['line_width'],
                              opacity=pldict['opacity'], flip_scalars=pldict['flip_scalars'],
                              lighting=pldict['lighting'], n_colors=pldict['n_colors'],
                              interpolate_before_map=pldict['interpolate_before_map'], cmap=pldict['cmap'],
                              label=pldict['label'], reset_camera=pldict['reset_camera'],
                              scalar_bar_args=pldict['scalar_bar_args'], show_scalar_bar=pldict['show_scalar_bar'],
                              multi_colors=pldict['multi_colors'], name=pldict['name'], texture=pldict['texture'],
                              render_points_as_spheres=pldict['render_points_as_spheres'],
                              render_lines_as_tubes=pldict['render_lines_as_tubes'],
                              smooth_shading=pldict['smooth_shading'], split_sharp_edges=pldict['split_sharp_edges'],
                              ambient=pldict['ambient'], diffuse=pldict['diffuse'], specular=pldict['specular'],
                              specular_power=pldict['specular_power'], nan_color=pldict['nan_color'],
                              nan_opacity=pldict['nan_opacity'], culling=pldict['culling'], rgb=pldict['rgb'],
                              categories=pldict['categories'], silhouette=pldict['silhouette'],
                              use_transparency=pldict['use_transparency'], below_color=pldict['below_color'],
                              above_color=pldict['above_color'], annotations=pldict['annotations'],
                              pickable=pldict['pickable'], preference=pldict['preference'],
                              log_scale=pldict['log_scale'], pbr=pldict['pbr'], metallic=pldict['metallic'],
                              roughness=pldict['roughness'], render=pldict['render'], component=pldict['component'])
            for i in range(1000):
                CutName = 'Slicecut'+str(i+1)
                if CutName not in self.mesh.keys():
                    self.ui.comboBox_CurrentMesh_VPVZ.addItem(CutName)
                    break
            self.mesh[CutName] = pl.plane_sliced_meshes[-1]
            self.ui.comboBox_CurrentMesh_VPVZ.setCurrentText(CutName)
        elif PlotMethod == 'Box':
            pl.add_mesh_clip_box(self.mesh[CurrentMesh], invert=invert, color=pldict['color'], style=pldict['style'],
                                 scalars=pldict['scalars'], clim=pldict['clim'], show_edges=pldict['show_edges'],
                                 edge_color=pldict['edge_color'], point_size=pldict['point_size'],
                                 line_width=pldict['line_width'], opacity=pldict['opacity'],
                                 flip_scalars=pldict['flip_scalars'], lighting=pldict['lighting'],
                                 n_colors=pldict['n_colors'], interpolate_before_map=pldict['interpolate_before_map'],
                                 cmap=pldict['cmap'], label=pldict['label'], scalar_bar_args=pldict['scalar_bar_args'],
                                 show_scalar_bar=pldict['show_scalar_bar'], multi_colors=pldict['multi_colors'],
                                 name=pldict['name'], texture=pldict['texture'],
                                 render_points_as_spheres=pldict['render_points_as_spheres'],
                                 render_lines_as_tubes=pldict['render_lines_as_tubes'],
                                 smooth_shading=pldict['smooth_shading'], split_sharp_edges=pldict['split_sharp_edges'],
                                 ambient=pldict['ambient'], diffuse=pldict['diffuse'], specular=pldict['specular'],
                                 specular_power=pldict['specular_power'], nan_color=pldict['nan_color'],
                                 nan_opacity=pldict['nan_opacity'], culling=pldict['culling'], rgb=pldict['rgb'],
                                 categories=pldict['categories'], silhouette=pldict['silhouette'],
                                 use_transparency=pldict['use_transparency'], below_color=pldict['below_color'],
                                 above_color=pldict['above_color'], annotations=pldict['annotations'],
                                 pickable=pldict['pickable'], preference=pldict['preference'],
                                 log_scale=pldict['log_scale'], pbr=pldict['pbr'], metallic=pldict['metallic'],
                                 roughness=pldict['roughness'], render=pldict['render'], component=pldict['component'])
            for i in range(1000):
                CutName = 'Boxcut'+str(i+1)
                if CutName not in self.mesh.keys():
                    self.ui.comboBox_CurrentMesh_VPVZ.addItem(CutName)
                    break
            self.mesh[CutName] = pl.box_clipped_meshes[-1]
            self.ui.comboBox_CurrentMesh_VPVZ.setCurrentText(CutName)

    def Save(self):
        CurrentMesh = self.ui.comboBox_CurrentMesh_VPVZ.currentText()
        OutputFloder = self.ui.plainTextEdit_Output_VPVZ.toPlainText()
        OutputName = self.ui.plainTextEdit_SaveName_VPVZ.toPlainText()
        OutputType = self.ui.comboBox_SaveType_VPVZ.currentText()
        binary = self.ui.checkBox_binary_VPVZ.isChecked()
        print('CurrentMesh', CurrentMesh)
        print('OutputFloder',OutputFloder)
        print('OutputName',OutputName)
        print('OutputType',OutputType)

        if OutputType == 'pvd':
            self.mesh[CurrentMesh].extract_surface().save(OutputFloder+'/'+OutputName+'.stl')
            if self.pvdmodel:
                surface = pv.read(OutputFloder+'/'+OutputName+'.stl')
                vtusavedir = OutputFloder + '/' + OutputName
                if not os.path.exists(vtusavedir):
                    os.mkdir(vtusavedir)
                f = open(OutputFloder + '/' + OutputName + '.pvd', 'w')
                f.write('<?xml version="1.0"?>\n')
                f.write('<VTKFile type="Collection" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n')
                f.write('  <Collection>\n')
                n = 0
                for number in self.pvdmodel.time_values:
                    n = n+1
                    self.pvdmodel.set_active_time_value(number)
                    model = self.pvdmodel.read()[0]
                    clipped = model.clip_surface(surface, invert=True)
                    vtusavepath = vtusavedir + '/' + str(n) + ".vtu"
                    clipped.save(vtusavepath, binary=binary)
                    f.write('    <DataSet timestep="{}" part="0" file="{}/{}.vtu"/>\n'.format(number, OutputName, n))
                f.write('  </Collection>\n')
                f.write('</VTKFile>\n')
                f.close()
        else:
            self.mesh[CurrentMesh].save(OutputFloder+'/'+OutputName+'.'+OutputType, binary=binary)

    def BatchRun(self):
        inpath = self.ui.plainTextEdit_BatchTable_VPVZ.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for linenum in range(len(DF)):
            # get line of table
            print('get info in line', linenum)
            info = DF.iloc[linenum].fillna('')

            InPath = ''
            LoadPVD = True
            LoadData = True
            CutMethod = 'Surface'
            CurrentMesh = 'OriMesh'
            Shape1 = ''
            Shape2 = ''
            invert = True
            OutputFloder = ''
            OutputName = ''
            Savetype = 'pvd'
            binary = True

            try:
                if info["InPath"]:
                    InPath = info["InPath"]
            except:
                pass
            try:
                if isinstance(info["LoadPVD"], np.bool_):
                    LoadPVD = info["LoadPVD"]
            except:
                pass
            try:
                if isinstance(info["LoadData"], np.bool_):
                    LoadData = info["LoadData"]
            except:
                pass
            try:
                if info["CutMethod"]:
                    CutMethod = info["CutMethod"]
            except:
                pass
            try:
                if info["CurrentMesh"]:
                    CurrentMesh = info["CurrentMesh"]
            except:
                pass
            try:
                if info["Shape1"]:
                    Shape1 = info["Shape1"]
            except:
                pass
            try:
                if info["Shape2"]:
                    Shape2 = info["Shape2"]
            except:
                pass
            try:
                if isinstance(info["invert"], np.bool_):
                    invert = info["invert"]
            except:
                pass
            try:
                if info["OutputFloder"]:
                    OutputFloder = info["OutputFloder"]
            except:
                pass
            try:
                if info["OutputName"]:
                    OutputName = info["OutputName"]
            except:
                pass
            try:
                if info["Savetype"]:
                    Savetype = info["Savetype"]
            except:
                pass
            try:
                if isinstance(info["binary"], np.bool_):
                    binary = info["binary"]
            except:
                pass
            # set ui
            self.ui.plainTextEdit_InPath_VPVZ.setPlainText('{}'.format(InPath))
            self.ui.checkBox_LoadPVD_VPVZ.setChecked(LoadPVD)
            self.ui.checkBox_GetTimestep_VPVZ.setChecked(False)
            self.ui.checkBox_SetActivateTimestep_VPVZ.setChecked(False)
            if LoadData:
                self.LoadData()

            self.ui.comboBox_CurrentMesh_VPVZ.setCurrentText(CurrentMesh)
            self.ui.comboBox_CutType_VPVZ.setCurrentText(CutMethod)
            self.ui.checkBox_CutInvert_VPVZ.setChecked(invert)
            self.ui.plainTextEdit_CutInput1_VPVZ.setPlainText('{}'.format(Shape1))
            self.ui.plainTextEdit_CutInput2_VPVZ.setPlainText('{}'.format(Shape2))
            self.ui.plainTextEdit_Output_VPVZ.setPlainText('{}'.format(OutputFloder))
            self.ui.plainTextEdit_SaveName_VPVZ.setPlainText('{}'.format(OutputName))
            self.ui.comboBox_SaveType_VPVZ.setCurrentText(Savetype)
            self.ui.checkBox_binary_VPVZ.setChecked(binary)
            self.Cut()
            self.Save()

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\VisualizationPyVista.ui")
    stats = VisualizationPyVista(UI=ui)
    stats.ui.show()
    app.exec_()