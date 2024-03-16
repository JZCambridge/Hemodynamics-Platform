#
# #-------------------------------------------------------------------------------
# import os
# import sys
# import meshio
# # Set current folder as working directory
# # Get the current working directory: os.getcwd()
# # Change the current working directory: os.chdir()
# os.chdir(os.getcwd())
# sys.path.insert(0, '../Functions_YC')
# # Import functions
# #from TableEditYC import Demo
# import numpy as np
# import os.path
# import re
# import csv
#
# # Standard libs
# from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox,QWidget, QTableWidget, QHBoxLayout, QVBoxLayout, QApplication, QTableWidgetItem, QAbstractItemView,QTabWidget,\
#     QDialog,QComboBox, QProgressBar,  QLabel, QStatusBar,QLineEdit, QHeaderView
# from PySide2.QtCore import QFile
# from FileDisposing import *
# class MeshGenerating:
#     def __init__(self, UI):
#         self.ui = UI.ui
#         self.VmtkScript = None
#         self.PypePath = None
#         self.VmtkSurfaceReaderScript = None
#         self.VmtkBranchClipperScript = None
#         self.VmtkFlowExtensionScript = None
#         self.Vmtk_MeshGeneratingScript = None
#         self.VmtkMeshMethod = None
#         self.BranchClipperType = None
#
#     def Choose_Meshexe(self):
#         PypePath = Opening_File(self.ui, "exe (*.exe)")
#         self.ui.meshexepath_MS.setPlainText(PypePath)
#
#     def Choose_StlFil(self):
#         StlPath = Opening_File(self.ui, "stl (*.stl);; vtp (*.vtp)")
#         self.ui.stlpath_MS.setPlainText(StlPath)
#
#     def Choose_SaveClippedfil(self):
#         SaveClippedfilPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
#                                     "stl (*.stl);; vtp (*.vtp)")[0] #, "vtp (*.vtp)")
#         self.ui.plainTextEdit_saveClippedfil_MS.setPlainText(SaveClippedfilPath)
#
#     def Choose_SaveFlowExtensionFil(self):
#         SaveFlowExtensionPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
#                                     "stl (*.stl);; vtp (*.vtp)")[0] #, "vtp (*.vtp)")
#         self.ui.plainTextEdit_saveextensionfil_MS.setPlainText(SaveFlowExtensionPath)
#
#     def Choose_SaveMeshFil(self):
#         SaveMeshPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
#                                     "vtu (*.vtu)")[0]
#         self.ui.plainTextEdit_savemeshpath_MS.setPlainText(SaveMeshPath)
#
#     def Choose_ConvertMeshFil(self):
#         ConvertMeshPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
#                                     "Nastran (*.nas)")[0]
#         self.ui.plainTextEdit_MeshTypeConver_MS.setPlainText(ConvertMeshPath)
#
#     def VmtkSurfaceReader(self):
#         self.VmtkScript = ''
#         self.VmtkSurfaceReaderScript = ''
#         self.VmtkSurfaceReaderScript = " vmtksurfacereader  -ifile  " \
#                                        + self.ui.stlpath_MS.toPlainText()
#         self.VmtkScript += self.VmtkSurfaceReaderScript
#
#     def VmtkSurfaceWriter(self):
#         self.VmtkSurfaceWriterScript = ''
#         self.VmtkSurfaceWriterScript = " --pipe vmtksurfacewriter -ofile " \
#                                        + self.ui.plainTextEdit_saveextensionfil_MS.toPlainText()
#
#     def VmtkBranchClipper(self):
#         self.VmtkBranchClipperScript = ''
#         self.BranchClipperType = self.ui.BranchClipperType_MS.checkedButton().text()
#         if self.ui.checkBox_SurfaceClipper_MS.isChecked():
#             if self.BranchClipperType == "CubeClipper":
#                 self.VmtkBranchClipperScript = ' --pipe vmtksurfaceclipper   ' \
#                 ' --pipe vmtksurfaceconnectivity -cleanoutput 1   '
#             else:
#                 self.VmtkBranchClipperScript =  " --pipe vmtkcenterlines " \
#                             " --pipe vmtkendpointextractor  " \
#                             " --pipe vmtkbranchclipper " \
#                             " --pipe vmtksurfaceconnectivity -cleanoutput 1 "
#         self.VmtkScript += self.VmtkBranchClipperScript
#         if self.ui.plainTextEdit_saveClippedfil_MS.toPlainText():
#             self.VmtkScript += " --pipe vmtksurfacewriter -ofile " \
#                             + self.ui.plainTextEdit_saveClippedfil_MS.toPlainText()
#
#     def VmtkFlowExtension(self):
#         self.VmtkFlowExtensionScript = ''
#         if self.ui.checkBox_FlowExtension_MS.isChecked():
#             #self.VmtkFlowExtensionScript =  " --pipe vmtkcenterlines -seedselector openprofiles " \
#             self.VmtkFlowExtensionScript =  \
#             " --pipe vmtkflowextensions  -adaptivelength %d -extensionratio %f " \
#             " -extensionmode %s -normalestimationratio %f -interactive 0 "\
#             %(int(self.ui.adaptivelengthtextedit_MS.text()),
#             float(self.ui.lineEdit_extensionratio_MS.text()),
#             self.ui.lineEdit_extensionmode_MS.text(),
#             float(self.ui.lineEdit_Normalestimationratio_MS.text() ))
#         self.VmtkScript += self.VmtkFlowExtensionScript
#         if self.ui.plainTextEdit_saveextensionfil_MS.toPlainText():
#             self.VmtkScript += " --pipe vmtksurfacewriter -ofile " \
#                             + self.ui.plainTextEdit_saveextensionfil_MS.toPlainText()
#
#     def Vmtk_MeshGenerating(self):
#         # ************* vmtk script*********************************************
#         self.Vmtk_MeshGeneratingScript = ''
#         if self.ui.checkBox_meshgeneration_MS.isChecked():
#             self.VmtkMeshMethod = self.ui.VmtkMeshMethod_MS.checkedButton().text()
#             print("self.VmtkMeshMethod",self.VmtkMeshMethod)
#             if self.VmtkMeshMethod == "RadiousAdaptive":
#                 self.Vmtk_MeshGeneratingScript += \
#                     " --pipe vmtkcenterlines -endpoints 1 -seedselector openprofiles   " \
#                     " --pipe vmtkdistancetocenterlines -useradius 1  " \
#                     " --pipe vmtkmeshgenerator -elementsizemode edgelengtharray " \
#                     " -edgelengtharray DistanceToCenterlines"
#             else:
#                 self.Vmtk_MeshGeneratingScript += " --pipe vmtkmeshgenerator "
#             self.Vmtk_MeshGeneratingScript += \
#                                     " -edgelength %f -edgelengthfactor %f -maxedgelength %f " \
#                                     " -minedgelength %f  " \
#                                     " -remeshcapsonly 1 -boundarylayer %d  " \
#                                     " -boundarylayeroncaps %d -sublayers %d  " \
#                                     " -sublayerratio %f -thicknessfactor %f" \
#                                     %(float(self.ui.lineEdit_edgelength_MS.text()),
#                                     float(self.ui.lineEdit_edgelengthfactor_MS.text()),
#                                     float(self.ui.lineEdit_maxedgelength_MS.text()),
#                                     float(self.ui.lineEdit_minedgelength_MS.text()),
#                                     int(self.ui.lineEdit_boundarylayerbool_MS.text()),
#                                     int(self.ui.lineEdit_boudarylayercap_MS.text()),
#                                     int(self.ui.lineEdit_Sublayers_MS.text()),
#                                     float(self.ui.lineEdit_SubalayerRatio_MS.text()),
#                                     float(self.ui.lineEdit_firstlayerthickness_MS.text() ))
#             self.Vmtk_MeshGeneratingScript += " -ofile  " \
#                                               + self.ui.plainTextEdit_savemeshpath_MS.toPlainText()
#             self.VmtkScript += self.Vmtk_MeshGeneratingScript
#
#     def convertMeshType(self):
#         # convert mesh type from vtu to nas
#         if self.ui.checkBox_ConvertMeshType_MS.isChecked():
#             mesh = meshio.read(self.ui.plainTextEdit_savemeshpath_MS.toPlainText())
#             meshio.write(self.ui.plainTextEdit_MeshTypeConver_MS.toPlainText(), mesh)
#
#     def RunVmtk_Script(self):
#         self.PypePath = self.ui.meshexepath_MS.toPlainText()
#         print("self.PypePath",self.PypePath,"self.VmtkScript",self.VmtkScript)
#         Batchscript = self.PypePath + ' ' + "\"" + self.VmtkScript + "\""
#         print("Batchscript",Batchscript)
#         os.system(Batchscript)
#
#
#
#

#-------------------------------------------------------------------------------
import os
import sys
import meshio
import numpy
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

#from TableEditYC import Demo
import numpy as np
import os.path
import re
import csv

# Standard libs
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox,QWidget, QTableWidget, QHBoxLayout, QVBoxLayout, QApplication, QTableWidgetItem, QAbstractItemView,QTabWidget,\
    QDialog,QComboBox, QProgressBar,  QLabel, QStatusBar,QLineEdit, QHeaderView
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from FileDisposing import *
class MeshGenerating:
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chos_meshexe_MS.clicked.connect(lambda: self.Choose_Meshexe())
        self.ui.chos_stlfil_MS.clicked.connect(lambda: self.Choose_StlFil())
        self.ui.saveSmoothfil_MS.clicked.connect(lambda: self.Choose_SaveSmoothedfil())
        self.ui.saveClippedfil_MS.clicked.connect(lambda: self.Choose_SaveClippedfil())
        self.ui.saveextensionfil_MS.clicked.connect(lambda: self.Choose_SaveFlowExtensionFil())
        self.ui.SurfaceMeshfil_MS.clicked.connect(lambda: self.Choose_SaveReMeshFil())
        self.ui.save_meshfilPath_MS.clicked.connect(lambda: self.Choose_SaveMeshFil())
        self.ui.save_MeshTypeConver_MS.clicked.connect(lambda: self.Choose_ConvertMeshFil())
        self.ui.pushButton_generatemesh_MS.clicked.connect(lambda: self.VmtkSurfaceReader())
        self.ui.pushButton_generatemesh_MS.clicked.connect(lambda: self.VmtkSmooth())
        self.ui.pushButton_generatemesh_MS.clicked.connect(lambda: self.VmtkBranchClipper())
        self.ui.pushButton_generatemesh_MS.clicked.connect(lambda: self.VmtkFlowExtension())
        self.ui.pushButton_generatemesh_MS.clicked.connect(lambda: self.VmtkSurfaceRemesh())
        self.ui.pushButton_generatemesh_MS.clicked.connect(lambda: self.Vmtk_MeshGenerating())
        self.ui.pushButton_generatemesh_MS.clicked.connect(lambda: self.RunVmtk_Script())
        self.ui.pushButton_generatemesh_MS.clicked.connect(lambda: self.convertMeshType())
        self.ui.pushButton_BatchTable_MS.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_MS.clicked.connect(lambda: self.batchrun())
        
        self.InitMesh()

    def InitMesh(self):
        self.VmtkScript = None
        self.PypePath = None
        self.VmtkSurfaceReaderScript = None
        self.VmtkSmoothScript = None
        self.VmtkBranchClipperScript = None
        self.VmtkFlowExtensionScript = None
        self.Vmtk_MeshGeneratingScript = None
        self.VmtkMeshMethod = None
        self.BranchClipperType = None

    def Choose_Meshexe(self):
        PypePath = Opening_File(self.ui, "exe (*.exe)")
        self.ui.meshexepath_MS.setPlainText(PypePath)

    def Choose_StlFil(self):
        StlPath = Opening_File(self.ui, "stl (*.stl);; vtp (*.vtp)")
        self.ui.stlpath_MS.setPlainText(StlPath)

    def Choose_SaveSmoothedfil(self):
        SaveSmoothedfilPath = Opening_File(self.ui, "stl (*.stl);; vtp (*.vtp)")
        self.ui.plainTextEdit_saveSmoothfil_MS.setPlainText(SaveSmoothedfilPath)

    def Choose_SaveClippedfil(self):
        SaveClippedfilPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
                                    "stl (*.stl);; vtp (*.vtp)")[0] #, "vtp (*.vtp)")
        self.ui.plainTextEdit_saveClippedfil_MS.setPlainText(SaveClippedfilPath)

    def Choose_SaveFlowExtensionFil(self):
        SaveFlowExtensionPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
                                    "stl (*.stl);; vtp (*.vtp)")[0] #, "vtp (*.vtp)")
        self.ui.plainTextEdit_saveextensionfil_MS.setPlainText(SaveFlowExtensionPath)

    def Choose_SaveReMeshFil(self):
        SaveReMeshPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
                                    "vtu (*.vtu)")[0]
        self.ui.plainTextEdit_SurfaceMeshfil_MS.setPlainText(SaveReMeshPath)

    def Choose_SaveMeshFil(self):
        SaveMeshPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
                                    "vtu (*.vtu)")[0]
        self.ui.plainTextEdit_savemeshpath_MS.setPlainText(SaveMeshPath)

    def Choose_ConvertMeshFil(self):
        ConvertMeshPath = QFileDialog.getSaveFileName(self.ui, "Save file", "",
                                    "Nastran (*.nas)")[0]
        self.ui.plainTextEdit_MeshTypeConver_MS.setPlainText(ConvertMeshPath)

    def VmtkSurfaceReader(self):
        self.VmtkScript = ''
        self.VmtkSurfaceReaderScript = ''
        self.VmtkSurfaceReaderScript = " vmtksurfacereader  -ifile  " \
                                       + self.ui.stlpath_MS.toPlainText()
        self.VmtkScript += self.VmtkSurfaceReaderScript

    def VmtkSurfaceWriter(self):
        self.VmtkSurfaceWriterScript = ''
        self.VmtkSurfaceWriterScript = " --pipe vmtksurfacewriter -ofile " \
                                       + self.ui.plainTextEdit_saveextensionfil_MS.toPlainText()

    def VmtkSmooth(self):
        self.VmtkSmoothScript = ''
        if self.ui.checkBox_MeshSmooth_MS.isChecked():
            smoothMethod = self.ui.buttonGroup_smoothMethod.checkedButton().text()
            self.VmtkSmoothScript +=  " --pipe vmtksurfacesmoothing"\
                                      " -iterations %d -method "%(int(float(self.ui.iterationsTextedit_MS.text()))) \
                                      + smoothMethod \
                                      + " -relaxation %f -boundarysmoothing %d  -normalize %d  "\
                                      %(float(self.ui.lineEdit_relaxation_MS.text()),
                                        int(float(self.ui.lineEdit_boudarysmoothing_MS.text())),
                                        int(float(self.ui.lineEdit_Normalize_MS.text())))
        self.VmtkScript += self.VmtkSmoothScript
        if self.ui.plainTextEdit_saveSmoothfil_MS.toPlainText():
            self.VmtkScript += " --pipe vmtksurfacewriter -ofile " \
                            +self.ui.plainTextEdit_saveSmoothfil_MS.toPlainText()

    def VmtkBranchClipper(self):
        self.VmtkBranchClipperScript = ''
        self.BranchClipperType = self.ui.BranchClipperType_MS.checkedButton().text()
        if self.ui.checkBox_SurfaceClipper_MS.isChecked():
            if self.BranchClipperType == "CubeClipper":
                self.VmtkBranchClipperScript += ' --pipe vmtksurfaceclipper   ' \
                ' --pipe vmtksurfaceconnectivity -cleanoutput 1   '
            else:
                self.VmtkBranchClipperScript +=  " --pipe vmtkcenterlines " \
                            " --pipe vmtkendpointextractor  " \
                            " --pipe vmtkbranchclipper " \
                            " --pipe vmtksurfaceconnectivity -cleanoutput 1 "
        self.VmtkScript += self.VmtkBranchClipperScript
        if self.ui.plainTextEdit_saveClippedfil_MS.toPlainText():
            self.VmtkScript += " --pipe vmtksurfacewriter -ofile " \
                            + self.ui.plainTextEdit_saveClippedfil_MS.toPlainText()

    def VmtkFlowExtension(self):
        self.VmtkFlowExtensionScript = ''
        if self.ui.checkBox_FlowExtension_MS.isChecked():
            #self.VmtkFlowExtensionScript =  " --pipe vmtkcenterlines -seedselector openprofiles " \
            self.VmtkFlowExtensionScript +=  \
            " --pipe vmtkflowextensions  -adaptivelength %d -extensionratio %f " \
            " -extensionmode %s -normalestimationratio %f -interactive 0 "\
            %(int(float(self.ui.adaptivelengthtextedit_MS.text())),
            float(self.ui.lineEdit_extensionratio_MS.text()),
            self.ui.lineEdit_extensionmode_MS.text(),
            float(self.ui.lineEdit_Normalestimationratio_MS.text() ))
        self.VmtkScript += self.VmtkFlowExtensionScript
        if self.ui.plainTextEdit_saveextensionfil_MS.toPlainText():
            self.VmtkScript += " --pipe vmtksurfacewriter -ofile " \
                            + self.ui.plainTextEdit_saveextensionfil_MS.toPlainText()

    def VmtkSurfaceRemesh(self):
        print("start remesh1")
        self.VmtkSurfaceRemeshScript = ''
        surfaceRtargetEdgeLength =  0.25 * numpy.sqrt(3) * numpy.square(float(self.ui.lineEdit_SurfaceMeshEdgeLength_MS.text()))
        surfaceRminEdgelength = 0.25 * numpy.sqrt(3) * numpy.square(float(self.ui.minEdgelengthtextedit_MS.text()))
        surfaceRmaxEdgelength = 0.25 * numpy.sqrt(3) * numpy.square(float(self.ui.lineEdit_maxEdgelength_MS.text()))
        print("edgelength", surfaceRtargetEdgeLength, surfaceRminEdgelength, surfaceRmaxEdgelength )
        if self.ui.checkBox_remesh_MS.isChecked():  #0.25 * 3.0**0.5 * self.MaxEdgeLength**2
            print("start remesh2")
            self.VmtkSurfaceRemeshScript +=  \
            " --pipe vmtksurfaceremeshing  -elementsizemode area -area %f  " \
            "-minarea %f  -maxarea %f -areafactor %f -iterations %d " \
            "-connectivityiterations %d  -relaxation %f  " \
            %(surfaceRtargetEdgeLength,
            surfaceRminEdgelength,
            surfaceRmaxEdgelength,
            float(self.ui.lineEdit_SurfaceMeshEdgeFactor_MS.text()),
            int(float(self.ui.lineEdit_sufaceIteration_MS.text())),
            int(float(self.ui.lineEdit_sufaceConnectivity_MS.text())),
            float(self.ui.sufaceRelaxationtextedit_MS.text()))
        self.VmtkScript += self.VmtkSurfaceRemeshScript
        print(self.VmtkScript)
        if self.ui.plainTextEdit_SurfaceMeshfil_MS.toPlainText():
            self.VmtkScript += " --pipe vmtksurfacewriter -ofile " \
                            +self.ui.plainTextEdit_SurfaceMeshfil_MS.toPlainText()

    def Vmtk_MeshGenerating(self):
        # ************* vmtk script*********************************************
        self.Vmtk_MeshGeneratingScript = ''
        if self.ui.checkBox_meshgeneration_MS.isChecked():
            self.VmtkMeshMethod = self.ui.VmtkMeshMethod_MS.checkedButton().text()
            print("self.VmtkMeshMethod",self.VmtkMeshMethod)
            if self.VmtkMeshMethod == "RadiousAdaptive":
                self.Vmtk_MeshGeneratingScript += \
                    " --pipe vmtkcenterlines -endpoints 1 -seedselector openprofiles   " \
                    " --pipe vmtkdistancetocenterlines -useradius 1  " \
                    " --pipe vmtkmeshgenerator -elementsizemode edgelengtharray " \
                    " -edgelengtharray DistanceToCenterlines"
            else:
                self.Vmtk_MeshGeneratingScript += " --pipe vmtkmeshgenerator "
            self.Vmtk_MeshGeneratingScript += \
                                    " -edgelength %f -edgelengthfactor %f -maxedgelength %f " \
                                    " -minedgelength %f  " \
                                    " -skipremeshing %d -skipcapping %d  " \
                                    " -remeshcapsonly %d -boundarylayer %d  " \
                                    " -boundarylayeroncaps %d -sublayers %d  " \
                                    " -sublayerratio %f -thicknessfactor %f" \
                                    %(float(self.ui.lineEdit_edgelength_MS.text()),
                                    float(self.ui.lineEdit_edgelengthfactor_MS.text()),
                                    float(self.ui.lineEdit_maxedgelength_MS.text()),
                                    float(self.ui.lineEdit_minedgelength_MS.text()),
                                    int(float(self.ui.lineEdit_skipremeshing_MS.text())),
                                    int(float(self.ui.lineEdit_skipcapping_MS.text())),
                                    int(float(self.ui.lineEdit_remeshcapsonly_MS.text())),
                                    int(float(self.ui.lineEdit_boundarylayerbool_MS.text())),
                                    int(float(self.ui.lineEdit_boudarylayercap_MS.text())),
                                    int(float(self.ui.lineEdit_Sublayers_MS.text())),
                                    float(self.ui.lineEdit_SubalayerRatio_MS.text()),
                                    float(self.ui.lineEdit_firstlayerthickness_MS.text()))
            self.Vmtk_MeshGeneratingScript += " -ofile  " \
                                              + self.ui.plainTextEdit_savemeshpath_MS.toPlainText()
            self.VmtkScript += self.Vmtk_MeshGeneratingScript

    def convertMeshType(self):
        # convert mesh type from vtu to nas
        if self.ui.checkBox_ConvertMeshType_MS.isChecked():
            mesh = meshio.read(self.ui.plainTextEdit_savemeshpath_MS.toPlainText())
            meshio.write(self.ui.plainTextEdit_MeshTypeConver_MS.toPlainText(), mesh)

    def RunVmtk_Script(self):
        self.PypePath = self.ui.meshexepath_MS.toPlainText()
        print("self.PypePath",self.PypePath,"self.VmtkScript",self.VmtkScript)
        Batchscript = self.PypePath + ' ' + "\"" + self.VmtkScript + "\""
        print("Batchscript",Batchscript)
        os.system(Batchscript)

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_MS.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_MS.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')
            Mesh = False
            try:
                if info["Mesh"]:
                    Mesh = info["Mesh"]
            except:
                pass
            if Mesh:
                InputFolder = ''
                OutputFolder = ''
                MeshExe = ''
                Carotid = True
                MeshSmooth = True
                laplace = True
                IterationsSmooth = 15
                Relaxation = 0.5
                Boundarysmoothing = 0
                Normalize = 1
                SmoothName = 'smooth'
                SurfaceClipper = True
                CubeClipper = True
                ClipperName = 'clipped'
                FlowExtension = True
                AdaptivelengthBool = 1
                Extensionratio = 3
                Extensionmode = 'boundarynormal'
                Normalestimationratio = 10
                ExtensionName = 'extension'
                SurfaceRemesh = True
                EdgeLengthRemesh = 1
                EdgelengthFactorRemesh = 1
                MinedgelengthRemesh = 0.3
                MaxedgelengthRemesh = 4
                IterationsRemesh = 3
                connectivityiterations = 20
                Relaxations = 0.5
                SurfaceRemeshName = 'surface'
                TetralMeshGeneration = True
                RadiousAdaptive = True
                EdgelengthMesh = 1
                EdgelengthFactorMesh = 0.3
                MinedgelengthMesh = 0.3
                MaxedgelengthMesh = 4
                BoundarylayerBool = 1
                Sublayers = 3
                Sublayerratio = 1.2
                skipremeshing = 0
                skipcapping = 0
                remeshcapsonly = 0
                FirstLayerThickness = 0.1
                BoundarylayeroncapsBool = 0
                MeshName = 'FluidMeshInit.vtu'
                ConvertMeshType = True
                ConvertMeshName = 'FluidMeshInit.nas'

                try:
                    if info["InputFolder"]:
                        InputFolder = info["InputFolder"]
                except:
                    pass
                try:
                    if info["InputStl(Mesh)"]:
                        InputFolder = info["InputStl(Mesh)"]
                except:
                    pass
                try:
                    if info["MeshExe"]:
                        MeshExe = info["MeshExe"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        OutputFolder = info["OutputFolder"] + '/Mesh'
                except:
                    pass
                try:
                    if info["OutputFolder(Mesh)"]:
                        OutputFolder = info["OutputFolder(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Carotid(Mesh)"], np.bool_):
                        Carotid = info["Carotid(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["MeshSmooth(Mesh)"], np.bool_):
                        MeshSmooth = info["MeshSmooth(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["laplace(Mesh)"], np.bool_):
                        laplace = info["laplace(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["IterationsSmooth(Mesh)"], (np.int64, np.float64)):
                        IterationsSmooth = info["IterationsSmooth(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Relaxation(Mesh)"], (np.int64, np.float64)):
                        Relaxation = info["Relaxation(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Boundarysmoothing(Mesh)"], (np.int64, np.float64)):
                        Boundarysmoothing = info["Boundarysmoothing(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Normalize(Mesh)"], (np.int64, np.float64)):
                        Normalize = info["Normalize(Mesh)"]
                except:
                    pass
                try:
                    if info["SmoothName(Mesh)"]:
                        SmoothName = info["SmoothName(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["SurfaceClipper(Mesh)"], np.bool_):
                        SurfaceClipper = info["SurfaceClipper(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["CubeClipper(Mesh)"], np.bool_):
                        CubeClipper = info["CubeClipper(Mesh)"]
                except:
                    pass
                try:
                    if info["ClipperName(Mesh)"]:
                        ClipperName = info["ClipperName(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["FlowExtension(Mesh)"], np.bool_):
                        FlowExtension = info["FlowExtension(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["AdaptivelengthBool(Mesh)"], (np.int64, np.float64)):
                        AdaptivelengthBool = info["AdaptivelengthBool(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Extensionratio(Mesh)"], (np.int64, np.float64)):
                        Extensionratio = info["Extensionratio(Mesh)"]
                except:
                    pass
                try:
                    if info["Extensionmode(Mesh)"]:
                        Extensionmode = info["Extensionmode(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Normalestimationratio(Mesh)"], (np.int64, np.float64)):
                        Normalestimationratio = info["Normalestimationratio(Mesh)"]
                except:
                    pass
                try:
                    if info["ExtensionName(Mesh)"]:
                        ExtensionName = info["ExtensionName(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["SurfaceRemesh(Mesh)"], np.bool_):
                        SurfaceRemesh = info["SurfaceRemesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["EdgeLengthRemesh(Mesh)"], (np.int64, np.float64)):
                        EdgeLengthRemesh = info["EdgeLengthRemesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["EdgelengthFactorRemesh(Mesh)"], (np.int64, np.float64)):
                        EdgelengthFactorRemesh = info["EdgelengthFactorRemesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["MinedgelengthRemesh(Mesh)"], (np.int64, np.float64)):
                        MinedgelengthRemesh = info["MinedgelengthRemesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["MaxedgelengthRemesh(Mesh)"], (np.int64, np.float64)):
                        MaxedgelengthRemesh = info["MaxedgelengthRemesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["IterationsRemesh(Mesh)"], (np.int64, np.float64)):
                        IterationsRemesh = info["IterationsRemesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["connectivityiterations(Mesh)"], (np.int64, np.float64)):
                        connectivityiterations = info["connectivityiterations(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Relaxations(Mesh)"], (np.int64, np.float64)):
                        Relaxations = info["Relaxations(Mesh)"]
                except:
                    pass
                try:
                    if info["SurfaceRemeshName(Mesh)"]:
                        SurfaceRemeshName = info["SurfaceRemeshName(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["TetralMeshGeneration(Mesh)"], np.bool_):
                        TetralMeshGeneration = info["TetralMeshGeneration(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["RadiousAdaptive(Mesh)"], np.bool_):
                        RadiousAdaptive = info["RadiousAdaptive(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["EdgelengthMesh(Mesh)"], (np.int64, np.float64)):
                        EdgelengthMesh = info["EdgelengthMesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["EdgelengthFactorMesh(Mesh)"], (np.int64, np.float64)):
                        EdgelengthFactorMesh = info["EdgelengthFactorMesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["MinedgelengthMesh(Mesh)"], (np.int64, np.float64)):
                        MinedgelengthMesh = info["MinedgelengthMesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["MaxedgelengthMesh(Mesh)"], (np.int64, np.float64)):
                        MaxedgelengthMesh = info["MaxedgelengthMesh(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["BoundarylayerBool(Mesh)"], (np.int64, np.float64)):
                        BoundarylayerBool = info["BoundarylayerBool(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Sublayers(Mesh)"], (np.int64, np.float64)):
                        Sublayers = info["Sublayers(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["Sublayerratio(Mesh)"], (np.int64, np.float64)):
                        Sublayerratio = info["Sublayerratio(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["skipremeshing(Mesh)"], (np.int64, np.float64)):
                        skipremeshing = info["skipremeshing(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["skipcapping(Mesh)"], (np.int64, np.float64)):
                        skipcapping = info["skipcapping(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["remeshcapsonly(Mesh)"], (np.int64, np.float64)):
                        remeshcapsonly = info["remeshcapsonly(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["FirstLayerThickness(Mesh)"], (np.int64, np.float64)):
                        FirstLayerThickness = info["FirstLayerThickness(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["BoundarylayeroncapsBool(Mesh)"], np.int64):
                        BoundarylayeroncapsBool = info["BoundarylayeroncapsBool(Mesh)"]
                except:
                    pass
                try:
                    if info["MeshName(Mesh)"]:
                        MeshName = info["MeshName(Mesh)"]
                except:
                    pass
                try:
                    if isinstance(info["ConvertMeshType(Mesh)"], np.bool_):
                        ConvertMeshType = info["ConvertMeshType(Mesh)"]
                except:
                    pass
                try:
                    if info["ConvertMeshName(Mesh)"]:
                        ConvertMeshName = info["ConvertMeshName(Mesh)"]
                except:
                    pass

                SmoothSavePath = OutputFolder + '/' + SmoothName + '.stl'
                ClipperSavePath = OutputFolder + '/' + ClipperName + '.stl'
                ExtensionSavePath = OutputFolder + '/' + ExtensionName + '.stl'
                SurfaceRemeshSavePath = OutputFolder + '/' + SurfaceRemeshName + '.stl'
                MeshSavePath = OutputFolder + '/' + MeshName
                ConvertMeshSavePath = OutputFolder + '/' + ConvertMeshName
                print('Mesh InputFolder=', InputFolder)
                print('Mesh OutputFolder=', OutputFolder)
                # make dir
                if not os.path.exists(OutputFolder):
                    os.mkdir(OutputFolder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                if MeshExe:
                    self.ui.meshexepath_MS.setPlainText('{}'.format(MeshExe))
                self.ui.stlpath_MS.setPlainText('{}'.format(InputFolder))

                self.ui.Coronary__MS.setChecked(True)
                if Carotid:
                    self.ui.Carotid__MS.setChecked(True)

                self.ui.plainTextEdit_saveSmoothfil_MS.setPlainText('')
                self.ui.checkBox_MeshSmooth_MS.setChecked(False)
                if MeshSmooth:
                    self.ui.checkBox_MeshSmooth_MS.setChecked(True)
                    self.ui.radioButton_taubin_MS.setChecked(True)
                    if laplace:
                        self.ui.radioButton_Laplace_MS.setChecked(True)
                    self.ui.iterationsTextedit_MS.setText('{}'.format(IterationsSmooth))
                    self.ui.lineEdit_relaxation_MS.setText('{}'.format(Relaxation))
                    self.ui.lineEdit_boudarysmoothing_MS.setText('{}'.format(Boundarysmoothing))
                    self.ui.lineEdit_Normalize_MS.setText('{}'.format(Normalize))
                    self.ui.plainTextEdit_saveSmoothfil_MS.setPlainText('{}'.format(SmoothSavePath))

                self.ui.plainTextEdit_saveClippedfil_MS.setPlainText('')
                self.ui.checkBox_SurfaceClipper_MS.setChecked(False)
                if SurfaceClipper:
                    self.ui.checkBox_SurfaceClipper_MS.setChecked(True)
                    self.ui.radioButton_Automatic_MS.setChecked(True)
                    if CubeClipper:
                        self.ui.radioButton_CUbeClipper_MS.setChecked(True)
                    self.ui.plainTextEdit_saveClippedfil_MS.setPlainText('{}'.format(ClipperSavePath))

                self.ui.plainTextEdit_saveextensionfil_MS.setPlainText('')
                self.ui.checkBox_FlowExtension_MS.setChecked(False)
                if FlowExtension:
                    self.ui.checkBox_FlowExtension_MS.setChecked(True)
                    self.ui.adaptivelengthtextedit_MS.setText('{}'.format(AdaptivelengthBool))
                    self.ui.lineEdit_extensionratio_MS.setText('{}'.format(Extensionratio))
                    self.ui.lineEdit_extensionmode_MS.setText('{}'.format(Extensionmode))
                    self.ui.lineEdit_Normalestimationratio_MS.setText('{}'.format(Normalestimationratio))
                    self.ui.plainTextEdit_saveextensionfil_MS.setPlainText('{}'.format(ExtensionSavePath))

                self.ui.plainTextEdit_SurfaceMeshfil_MS.setPlainText('')
                self.ui.checkBox_remesh_MS.setChecked(False)
                if SurfaceRemesh:
                    self.ui.checkBox_remesh_MS.setChecked(True)
                    self.ui.lineEdit_SurfaceMeshEdgeLength_MS.setText('{}'.format(EdgeLengthRemesh))
                    self.ui.lineEdit_SurfaceMeshEdgeFactor_MS.setText('{}'.format(EdgelengthFactorRemesh))
                    self.ui.minEdgelengthtextedit_MS.setText('{}'.format(MinedgelengthRemesh))
                    self.ui.lineEdit_maxEdgelength_MS.setText('{}'.format(MaxedgelengthRemesh))
                    self.ui.lineEdit_sufaceIteration_MS.setText('{}'.format(IterationsRemesh))
                    self.ui.lineEdit_sufaceConnectivity_MS.setText('{}'.format(connectivityiterations))
                    self.ui.sufaceRelaxationtextedit_MS.setText('{}'.format(Relaxations))
                    self.ui.plainTextEdit_SurfaceMeshfil_MS.setPlainText('{}'.format(SurfaceRemeshSavePath))

                self.ui.plainTextEdit_savemeshpath_MS.setPlainText('')
                self.ui.checkBox_meshgeneration_MS.setChecked(False)
                if TetralMeshGeneration:
                    self.ui.checkBox_meshgeneration_MS.setChecked(True)
                    self.ui.radioButton_EdgeLengthAdaptive_MS.setChecked(True)
                    if RadiousAdaptive:
                        self.ui.radioButton_RadiousAdaptive_MS.setChecked(True)
                    self.ui.lineEdit_edgelength_MS.setText('{}'.format(EdgelengthMesh))
                    self.ui.lineEdit_edgelengthfactor_MS.setText('{}'.format(EdgelengthFactorMesh))
                    self.ui.lineEdit_minedgelength_MS.setText('{}'.format(MinedgelengthMesh))
                    self.ui.lineEdit_maxedgelength_MS.setText('{}'.format(MaxedgelengthMesh))
                    self.ui.lineEdit_boundarylayerbool_MS.setText('{}'.format(BoundarylayerBool))
                    self.ui.lineEdit_Sublayers_MS.setText('{}'.format(Sublayers))
                    self.ui.lineEdit_SubalayerRatio_MS.setText('{}'.format(Sublayerratio))
                    self.ui.lineEdit_skipremeshing_MS.setText('{}'.format(skipremeshing))
                    self.ui.lineEdit_skipcapping_MS.setText('{}'.format(skipcapping))
                    self.ui.lineEdit_remeshcapsonly_MS.setText('{}'.format(remeshcapsonly))
                    self.ui.lineEdit_firstlayerthickness_MS.setText('{}'.format(FirstLayerThickness))
                    self.ui.lineEdit_boudarylayercap_MS.setText('{}'.format(BoundarylayeroncapsBool))
                    self.ui.plainTextEdit_savemeshpath_MS.setPlainText('{}'.format(MeshSavePath))

                self.ui.plainTextEdit_MeshTypeConver_MS.setPlainText('')
                self.ui.checkBox_ConvertMeshType_MS.setChecked(False)
                if ConvertMeshType:
                    self.ui.checkBox_ConvertMeshType_MS.setChecked(True)
                    self.ui.plainTextEdit_MeshTypeConver_MS.setPlainText('{}'.format(ConvertMeshSavePath))
                # Touched function
                self.VmtkSurfaceReader()
                self.VmtkSmooth()
                self.VmtkBranchClipper()
                self.VmtkFlowExtension()
                self.VmtkSurfaceRemesh()
                self.Vmtk_MeshGenerating()
                self.RunVmtk_Script()
                self.convertMeshType()
                self.InitMesh()