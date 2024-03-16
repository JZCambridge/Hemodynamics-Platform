"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by
Jin ZHENG JZ410 (29Mar21)
"""
import sys
import os
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, '../QSSFil/QSS_IMG')
# from qt_material import apply_stylesheet
##############################################################################
# Import functions self-written
from Modules_JZ.FilterMask import FilterMaskMain
from Modules_YC.Centerline_Extraction import Centerline_ExtractionMain
from Modules_JZ.CenterlineXsection import CenterlineXsectionMain
from Modules_AZ.TissueElemAssign import TissueElemAssignMain
from Modules_OneClicked.PostProcessOneClicked import PostProcessOneClickedMain
from Modules_OneClicked.SolidOneClicked import SolidOneClickedMain
from Modules_JZ.LumenCorrect import LumenCorrectMain
from Modules_JZ.ConvertDataType import ConvertDataTypeMain
from Modules_JZ.CenterlineJSONUpdate import CenterlineJSONUpdateMain
from Modules_JZ.XsectionOriVolume import XsectionOriVolumeMain
from Modules_JZ.StackSegment import StackSegmentMain
from Modules_JZ.MaskSTL import MaskSTLMain
from Modules_YC.DataOutput import ADINA_DataOutputMain
from Modules_JZ.CalcCFDResult import CalcCFDResultMain
from Modules_JZ.MapResults import MapResultsMain
from Modules_JZ.FFRCalcs import FFRCalcsMain
from Modules_JZ.Results3DView import Results3DViewMain
from Modules_JZ.AreaVolumeCalcs import AreaVolumeCalcsMain
from Modules_JZ.PeriluminalSegment import PeriluminalSegmentMain
from Modules_JZ.TissueSegmentSmooth import TissueSegmentSmoothMain
from Modules_YC.TissueMaterialAssignment import TissueMaterialAssignmentMain
from Modules_JZ.MaskDilation import MaskDilationMain
from Modules_JZ.MaskShrinkage import MaskShrinkageMain
from Modules_JZ.ExtractPointCoords import ExtractPointCoordsMain
from Modules_JZ.MaskExtension import MaskExtensionMain
from Modules_YC.Generate_InputFile import Generate_In_File
from Modules_YC.NodeMatching import NodeMatchingMain
from Modules_JZ.CPRMPR import CPRMPRMain
from Modules_JZ.ImageDisplay import ImageDisplayMain
from Modules_JZ.RadialDisplay import RadialDisplayMain
from Modules_JZ.SegmentInfoExtract import SegmentInfoExtractMain
from Modules_JZ.InitQTVTK import InitQTVTKMain
from Modules_JZ.StraightCPRPointStats import StraightCPRPointStatsMain
from Modules_JZ.Extract2DSlices import Extract2DSlicesMain
from Modules_AZ.SplitFaceElem import SplitFaceElemMain
from Modules_YL.CenterlineGeneration import CenterlineGenerationMain
from Modules_YL.OneClick2Stl import OneClick2StlMain
from Modules_YC.Visulization import PostProcessingMain
from Modules_YC.MeshGenerating import MeshGeneratingMain
from Modules_OneClicked.CarotidOneClicked import CarotidOneClickedMain
from Modules_YL.MeshCut import CuttingMeshTest
from Modules_YL.BatchCoronary import BatchCoronaryMain
from Modules_YL.BatchCoronary import BatchCoronaryFSI
from Modules_AZ.Savevtu import SaveVTUMain
from Modules_AZ.VisualizationPyvista import VisualizationPyvistaMain
from Modules_AZ.VTUDataExtraction import VTUDataExtractionMain
from Modules_AZ.StackSTL import StackSTLMain
from Modules_AZ.MeshCap import MeshFillGapMain
from Modules_AZ.BloodPressureAndHeartRate import BloodPressureAndHeartRateMain
from Modules_AZ.CenterlineToCutPlane import CenterlineToCutPlane
from Modules_AZ.CarotidFSI import CarotidFSI
from Modules_SH.BatchSliceRadiomics import BatchSliceRadiomicsMain
##############################################################################

##############################################################################
# Standard libs
import re
import sys
import multiprocessing
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
##############################################################################
class GUIMain:
    def __init__(self,uiPath):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui = QUiLoader().load(uiPath)
        # Read Qss file
        style_file = "../Base/QSSFil/Ubuntu.qss" # Combinear  Ubuntu
        with open(style_file, "r", encoding="UTF-8") as file:
            style_sheet = file.read()
            # Load Qss file
            self.ui.setStyleSheet(style_sheet)

        end_pageuiPath = re.sub('main.ui', 'end_page.ui', uiPath)
        self.end_pageui = QUiLoader().load(end_pageuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.end_pageui.centralwidget)

        CenterLineGenerationuiPath = re.sub('main.ui', 'CenterLineGeneration.ui', uiPath)
        self.CenterLineGenerationui = QUiLoader().load(CenterLineGenerationuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.CenterLineGenerationui.centralwidget)
        self.CenterlineGeneration = CenterlineGenerationMain.CenterlineEx(
            UI=self.CenterLineGenerationui, Hedys=self)

        SavevtuuiPath = re.sub('main.ui', 'Savevtu.ui', uiPath)
        self.Savevtuui = QUiLoader().load(SavevtuuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.Savevtuui.centralwidget)
        self.SaveVTU = SaveVTUMain.SaveVTUorPVD(UI=self.Savevtuui, Hedys=self)

        CenterlineToCutPlaneuiPath = re.sub('main.ui', 'CenterlineToCutPlane.ui', uiPath)
        self.CenterlineToCutPlaneui = QUiLoader().load(CenterlineToCutPlaneuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.CenterlineToCutPlaneui.centralwidget)
        self.CenterlineToCutPlane = CenterlineToCutPlane.CenterlineToCutPlane(
            UI=self.CenterlineToCutPlaneui, Hedys=self)

        VisualizationPyVistauiPath = re.sub('main.ui', 'VisualizationPyVista.ui', uiPath)
        self.VisualizationPyVistaui = QUiLoader().load(VisualizationPyVistauiPath)
        self.ui.QStackedWidget_Module.addWidget(self.VisualizationPyVistaui.centralwidget)
        self.VisualizationPyVista = VisualizationPyvistaMain.VisualizationPyVista(
            UI=self.VisualizationPyVistaui, Hedys=self)

        VTUDataExtractionuiPath = re.sub('main.ui', 'VTUDataExtraction.ui', uiPath)
        self.VTUDataExtractionui = QUiLoader().load(VTUDataExtractionuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.VTUDataExtractionui.centralwidget)
        self.VTUDataExtraction = VTUDataExtractionMain.VTUDataExtraction(UI=self.VTUDataExtractionui, Hedys=self)

        OneClickCFDuiPath = re.sub('main.ui', 'OneClickCFD.ui', uiPath)
        self.OneClickCFDui = QUiLoader().load(OneClickCFDuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.OneClickCFDui.centralwidget)
        self.OneClickCFD = OneClick2StlMain.OneClickCFD(UI=self.OneClickCFDui, Hedys=self)

        FilterMaskuiPath = re.sub('main.ui', 'FilterMask.ui', uiPath)
        self.FilterMaskui = QUiLoader().load(FilterMaskuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.FilterMaskui.centralwidget)
        self.filterMask = FilterMaskMain.FilterMask(UI=self.FilterMaskui, Hedys=self)

        CenterlineExtractionuiPath = re.sub('main.ui', 'CenterlineExtraction.ui', uiPath)
        self.CenterlineExtractionui = QUiLoader().load(CenterlineExtractionuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.CenterlineExtractionui.centralwidget)
        self.CenterlineExtraction = Centerline_ExtractionMain.Centerline_Extraction(UI=self.CenterlineExtractionui, Hedys=self)

        CenterlineJSONUpdateuiPath = re.sub('main.ui', 'UpdateCenterlineJson.ui', uiPath)
        self.CenterlineJSONUpdateui = QUiLoader().load(CenterlineJSONUpdateuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.CenterlineJSONUpdateui.centralwidget)
        self.CenterlineJSONUpdate = CenterlineJSONUpdateMain.CenterlineJSONUpdate(
            UI=self.CenterlineJSONUpdateui, Hedys=self)

        CenterlineXsecuiPath = re.sub('main.ui', 'CenterlineXsec.ui', uiPath)
        self.CenterlineXsecui = QUiLoader().load(CenterlineXsecuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.CenterlineXsecui.centralwidget)
        self.centerlineXsection = CenterlineXsectionMain.Xsection(UI=self.CenterlineXsecui, Hedys=self)

        LumenCorrectuiPath = re.sub('main.ui', 'LumenCorrect.ui', uiPath)
        self.LumenCorrectui = QUiLoader().load(LumenCorrectuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.LumenCorrectui.centralwidget)
        self.lumenCorrect = LumenCorrectMain.LumCorrect(UI=self.LumenCorrectui, Hedys=self)

        ConvertDatatypeuiPath = re.sub('main.ui', 'ConvertDatatype.ui', uiPath)
        self.ConvertDatatypeui = QUiLoader().load(ConvertDatatypeuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.ConvertDatatypeui.centralwidget)
        self.convertDataType = ConvertDataTypeMain.ConvertData(UI=self.ConvertDatatypeui, Hedys=self)

        XsetionOriVolumeuiPath = re.sub('main.ui', 'XsetionOriVolume.ui', uiPath)
        self.XsetionOriVolumeui = QUiLoader().load(XsetionOriVolumeuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.XsetionOriVolumeui.centralwidget)
        self.oriVolume = XsectionOriVolumeMain.OriVolume(UI=self.XsetionOriVolumeui, Hedys=self)

        StackSegmentationuiPath = re.sub('main.ui', 'StackSegmentation.ui', uiPath)
        self.StackSegmentationui = QUiLoader().load(StackSegmentationuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.StackSegmentationui.centralwidget)
        self.stackSegment = StackSegmentMain.StackSegment(UI=self.StackSegmentationui, Hedys=self)

        SegmentationExtensionuiPath = re.sub('main.ui', 'SegmentationExtension.ui', uiPath)
        self.SegmentationExtensionui = QUiLoader().load(SegmentationExtensionuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.SegmentationExtensionui.centralwidget)
        self.maskExtension = MaskExtensionMain.MaskExtension(UI=self.SegmentationExtensionui, Hedys=self)

        MeshCutuiPath = re.sub('main.ui', 'MeshCut.ui', uiPath)
        self.MeshCutui = QUiLoader().load(MeshCutuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.MeshCutui.centralwidget)
        self.MeshCut = CuttingMeshTest.Interaction(UI=self.MeshCutui, Hedys=self)

        STLGenerationuiPath = re.sub('main.ui', 'STLGeneration.ui', uiPath)
        self.STLGenerationui = QUiLoader().load(STLGenerationuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.STLGenerationui.centralwidget)
        self.maskSTL = MaskSTLMain.MaskSTL(UI=self.STLGenerationui, Hedys=self)

        BatchPreProcessinguiPath = re.sub('main.ui', 'BatchPreProcessing.ui', uiPath)
        self.BatchPreProcessingui = QUiLoader().load(BatchPreProcessinguiPath)
        self.ui.QStackedWidget_Module.addWidget(self.BatchPreProcessingui.centralwidget)
        self.BatchPreproc = BatchCoronaryMain.BatchCoronary(UI=self.BatchPreProcessingui, Hedys=self)

        BatchCoronaryFSIuiPath = re.sub('main.ui', 'BatchCoronaryFSI.ui', uiPath)
        self.BatchCoronaryFSIui = QUiLoader().load(BatchCoronaryFSIuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.BatchCoronaryFSIui.centralwidget)
        self.BatchCoronaryFSI = BatchCoronaryFSI.BatchCoronary(UI=self.BatchCoronaryFSIui, Hedys=self)

        MurraysLawuiPath = re.sub('main.ui', 'MurraysLaw.ui', uiPath)
        self.MurraysLawui = QUiLoader().load(MurraysLawuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.MurraysLawui.centralwidget)
        self.areaVolCalcs = AreaVolumeCalcsMain.AreaVolCalcs(UI=self.MurraysLawui, Hedys=self)

        BloodPressureAndHeartRateuiPath = re.sub('main.ui', 'BloodPressureAndHeartRate.ui', uiPath)
        self.BloodPressureAndHeartRateui = QUiLoader().load(BloodPressureAndHeartRateuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.BloodPressureAndHeartRateui.centralwidget)
        self.BloodPressureAndHeartRate = BloodPressureAndHeartRateMain.AreaVolCalcs(
            UI=self.BloodPressureAndHeartRateui, Hedys=self)

        PeriluminalSegmentationuiPath = re.sub('main.ui', 'PeriluminalSegmentation.ui', uiPath)
        self.PeriluminalSegmentationui = QUiLoader().load(PeriluminalSegmentationuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.PeriluminalSegmentationui.centralwidget)
        self.periluminal = PeriluminalSegmentMain.PeriluminalSegment(UI=self.PeriluminalSegmentationui, Hedys=self)

        TissueSegmentationSmoothuiPath = re.sub('main.ui', 'TissueSegmentationSmooth.ui', uiPath)
        self.TissueSegmentationSmoothui = QUiLoader().load(TissueSegmentationSmoothuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.TissueSegmentationSmoothui.centralwidget)
        self.tissueSegment = TissueSegmentSmoothMain.TissueSegment(UI=self.TissueSegmentationSmoothui, Hedys=self)

        MaskDilationuiPath = re.sub('main.ui', 'MaskDilation.ui', uiPath)
        self.MaskDilationui = QUiLoader().load(MaskDilationuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.MaskDilationui.centralwidget)
        self.maskDilation = MaskDilationMain.MaskDilation(UI=self.MaskDilationui, Hedys=self)

        MaskShrinkinguiPath = re.sub('main.ui', 'MaskShrinking.ui', uiPath)
        self.MaskShrinkingui = QUiLoader().load(MaskShrinkinguiPath)
        self.ui.QStackedWidget_Module.addWidget(self.MaskShrinkingui.centralwidget)
        self.maskShrink = MaskShrinkageMain.MaskShrink(UI=self.MaskShrinkingui, Hedys=self)

        MaskCoordinateuiPath = re.sub('main.ui', 'MaskCoordinate.ui', uiPath)
        self.MaskCoordinateui = QUiLoader().load(MaskCoordinateuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.MaskCoordinateui.centralwidget)
        self.extractPointCoords = ExtractPointCoordsMain.ExtractPointCoords(UI=self.MaskCoordinateui, Hedys=self)

        TissueElemAssignuiPath = re.sub('main.ui', 'TissueElemAssign.ui', uiPath)
        self.TissueElemAssignui = QUiLoader().load(TissueElemAssignuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.TissueElemAssignui.centralwidget)
        self.TissueElemAssign = TissueElemAssignMain.TissueElemAssign(UI=self.TissueElemAssignui, Hedys=self)

        PreProcessinguiPath = re.sub('main.ui', 'PreProcessing.ui', uiPath)
        self.PreProcessingui = QUiLoader().load(PreProcessinguiPath)
        self.ui.QStackedWidget_Module.addWidget(self.PreProcessingui.centralwidget)

        StackSTLuiPath = re.sub('main.ui', 'StackSTL.ui', uiPath)
        self.StackSTLui = QUiLoader().load(StackSTLuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.StackSTLui.centralwidget)
        self.StackSTL = StackSTLMain.StackSTL(UI=self.StackSTLui, Hedys=self)

        MeshFillGapuiPath = re.sub('main.ui', 'MeshFillGap.ui', uiPath)
        self.MeshFillGapui = QUiLoader().load(MeshFillGapuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.MeshFillGapui.centralwidget)
        self.MeshFillGap = MeshFillGapMain.MeshFillGap(UI=self.MeshFillGapui, Hedys=self)

        MeshuiPath = re.sub('main.ui', 'Mesh.ui', uiPath)
        self.Meshui = QUiLoader().load(MeshuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.Meshui.centralwidget)
        self.Meshgeneration = MeshGeneratingMain.MeshGenerating(UI=self.Meshui, Hedys=self)

        Generate_InputFileuiPath = re.sub('main.ui', 'Generate_InputFile.ui', uiPath)
        self.Generate_InputFileui = QUiLoader().load(Generate_InputFileuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.Generate_InputFileui.centralwidget)
        self.RTissueMaterialAssignment = TissueMaterialAssignmentMain.TissueMaterialAssignment(
            UI=self.Generate_InputFileui, Hedys=self)
        self.Finfilegneration = Generate_In_File.GenerateInputFile(UI=self.Generate_InputFileui, Hedys=self)

        face_and_boundaryconditionsuiPath = re.sub('main.ui', 'face_and_boundaryconditions.ui', uiPath)
        self.face_and_boundaryconditionsui = QUiLoader().load(face_and_boundaryconditionsuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.face_and_boundaryconditionsui.centralwidget)
        self.SplitFaceElem = SplitFaceElemMain.SplitFaceElem(UI=self.face_and_boundaryconditionsui, Hedys=self)

        OneClickeduiPath = re.sub('main.ui', 'OneClicked.ui', uiPath)
        self.OneClickedui = QUiLoader().load(OneClickeduiPath)
        self.ui.QStackedWidget_Module.addWidget(self.OneClickedui.centralwidget)
        # self.CotdOneClick = CarotidOneClickedMain.CarotidOneClicked(UI=self.OneClickedui, Hedys=self)
        # self.PostProcessOneClick = PostProcessOneClickedMain.PostProcessOneClicked(UI=self.OneClickedui, Hedys=self)
        # self.SolidOneClick = SolidOneClickedMain.CarotidSolidOneClicked(UI=self.OneClickedui, Hedys=self)
        self.CarotidFSI = CarotidFSI.CarotidFSIMain(UI=self.OneClickedui, Hedys=self)

        SolveruiPath = re.sub('main.ui', 'Solver.ui', uiPath)
        self.Solverui = QUiLoader().load(SolveruiPath)
        self.ui.QStackedWidget_Module.addWidget(self.Solverui.centralwidget)

        DateOutputuiPath = re.sub('main.ui', 'DateOutput.ui', uiPath)
        self.DateOutputui = QUiLoader().load(DateOutputuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.DateOutputui.centralwidget)
        self.adina_DataOutput = ADINA_DataOutputMain.ADINA_DataOutput(UI=self.DateOutputui, Hedys=self)

        NodeMatchinguiPath = re.sub('main.ui', 'NodeMatching.ui', uiPath)
        self.NodeMatchingui = QUiLoader().load(NodeMatchinguiPath)
        self.ui.QStackedWidget_Module.addWidget(self.NodeMatchingui.centralwidget)
        self.NodeMatching = NodeMatchingMain.NodeMatching(UI=self.NodeMatchingui, Hedys=self)

        PostProcessing_YCuiPath = re.sub('main.ui', 'PostProcessing_YC.ui', uiPath)
        self.PostProcessing_YCui = QUiLoader().load(PostProcessing_YCuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.PostProcessing_YCui.centralwidget)
        self.ParaviewPostProcessing = PostProcessingMain.PostProcessing(UI=self.PostProcessing_YCui, Hedys=self)

        PostProcessinguiPath = re.sub('main.ui', 'PostProcessing.ui', uiPath)
        self.PostProcessingui = QUiLoader().load(PostProcessinguiPath)
        self.ui.QStackedWidget_Module.addWidget(self.PostProcessingui.centralwidget)
        self.CFDParameters = CalcCFDResultMain.CFDParameters(UI=self.PostProcessingui, Hedys=self)

        ResultsMappinguiPath = re.sub('main.ui', 'ResultsMapping.ui', uiPath)
        self.ResultsMappingui = QUiLoader().load(ResultsMappinguiPath)
        self.ui.QStackedWidget_Module.addWidget(self.ResultsMappingui.centralwidget)
        self.mapResults = MapResultsMain.MapResults(UI=self.ResultsMappingui, Hedys=self)

        FFRCalculationuiPath = re.sub('main.ui', 'FFRCalculation.ui', uiPath)
        self.FFRCalculationui = QUiLoader().load(FFRCalculationuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.FFRCalculationui.centralwidget)
        self.FFR = FFRCalcsMain.FFRCalcs(UI=self.FFRCalculationui, Hedys=self)

        Plot3DViewuiPath = re.sub('main.ui', 'Plot3DView.ui', uiPath)
        self.Plot3DViewui = QUiLoader().load(Plot3DViewuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.Plot3DViewui.centralwidget)
        self.view3D = Results3DViewMain.Results3DView(UI=self.Plot3DViewui, Hedys=self)

        CPR_MPRGenerationuiPath = re.sub('main.ui', 'CPR_MPRGeneration.ui', uiPath)
        self.CPR_MPRGenerationui = QUiLoader().load(CPR_MPRGenerationuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.CPR_MPRGenerationui.centralwidget)
        self.CPRMPR = CPRMPRMain.CPRMPR(UI=self.CPR_MPRGenerationui, Hedys=self)

        Image_DisplayuiPath = re.sub('main.ui', 'Image_Display.ui', uiPath)
        self.FAI_Image_Displayui = QUiLoader().load(Image_DisplayuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.FAI_Image_Displayui.centralwidget)
        self.imageDisplay = ImageDisplayMain.ImageDisplay(UI=self.FAI_Image_Displayui, Hedys=self)

        PostProcessingRadialDisplayuiPath = re.sub('main.ui', 'PostProcessingRadialDisplay.ui', uiPath)
        self.PostProcessingRadialDisplayui = QUiLoader().load(PostProcessingRadialDisplayuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.PostProcessingRadialDisplayui.centralwidget)
        self.radialDisplay = RadialDisplayMain.RadialDisplay(UI=self.PostProcessingRadialDisplayui, Hedys=self)

        StraightCPRPointStatsuiPath = re.sub('main.ui', 'StraightCPRPointStats.ui', uiPath)
        self.StraightCPRPointStatsui = QUiLoader().load(StraightCPRPointStatsuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.StraightCPRPointStatsui.centralwidget)
        self.StraightCPRPointStats = StraightCPRPointStatsMain.StraightCPRPointStats(
            UI=self.StraightCPRPointStatsui, Hedys=self)

        BatchSliceRadiomicsuiPath = re.sub('main.ui', 'BatchSliceRadiomics.ui', uiPath)
        self.BatchSliceRadiomicsui = QUiLoader().load(BatchSliceRadiomicsuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.BatchSliceRadiomicsui.centralwidget)
        self.BatchSliceRadiomics = BatchSliceRadiomicsMain.BatchSliceRadiomics(UI=self.BatchSliceRadiomicsui, Hedys=self)

        Extract2DSlicesuiPath = re.sub('main.ui', 'Extract2DSlices.ui', uiPath)
        self.Extract2DSlicesui = QUiLoader().load(Extract2DSlicesuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.Extract2DSlicesui.centralwidget)
        self.Extract2DSlices = Extract2DSlicesMain.Extract2DSlices(
            UI=self.Extract2DSlicesui, Hedys=self)

        SegmentationInformationExtractionuiPath = re.sub('main.ui', 'SegmentationInformationExtraction.ui', uiPath)
        self.SegmentationInformationExtractionui = QUiLoader().load(SegmentationInformationExtractionuiPath)
        self.ui.QStackedWidget_Module.addWidget(self.SegmentationInformationExtractionui.centralwidget)
        self.extractImgInfo = SegmentInfoExtractMain.SegmentInforExtract(
            UI=self.SegmentationInformationExtractionui, Hedys=self)

        # Initialisation of image display
        self.qtVtkInit = InitQTVTKMain.InitQTVTK(self)
        self.ui.InitDispBtn_VTKQT.clicked.connect(lambda: self.qtVtkInit.ShowQTVTK())

        # ParaView set up
        self.ui.QComboBox_Modules.currentIndexChanged.connect(lambda: self.VisualizationParaview())

    def VisualizationParaview(self):
        if self.ui.QComboBox_Modules.currentText() == 'VisualizationParaview':
            # # ########################VisualizationParaview #####################################
            os.system('chcp 437')
            exePath = os.path.abspath('..\Base\VisualizationParaviewZTest\VisualizationParaviewZTest.exe')
            exeuiPath = os.path.join(self.current_dir, 'ui\VisualizationParaview.ui')
            uiPath = os.path.join(self.current_dir, 'ui\main.ui')
            # cmd =r"..\Base\VisualizationParaviewZTest\VisualizationParaviewZTest.exe .\ui\main.ui"
            cmd = '{0} {1} {2}'.format(exePath, exeuiPath, uiPath)
            os.system(cmd)

# Create main
if __name__ == "__main__":
    multiprocessing.freeze_support()
    # if IDE has already created a QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    window = GUIMain(uiPath='./ui/main.ui')
    window.ui.show()
    sys.exit(app.exec_()) # exit when close QT loop
