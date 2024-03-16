import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
import Save_Load_File
import Qtfunction
import pdfunction

from PySide2.QtWidgets import *
import time

class CarotidOneClicked():
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.PushButton_CSV_CFDOC_Z.clicked.connect(lambda: self.batchprogresscsv())
        self.ui.PushButton_run_CFDOC_Z.clicked.connect(lambda: self.batchProgress())
        self.mudule = Hedys

    def batchprogresscsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui,qtObj=True)
        # set filename
        self.ui.TextEdit_CSV_CFDOC_Z.setPlainText('{}'.format(filename))

    def batchProgress(self):
        inpath = self.ui.TextEdit_CSV_CFDOC_Z.toPlainText()
        DF=pdfunction.readexcel(inpath)
        for linenum in range(len(DF)):
            # get line of table
            print('get info in line', linenum)
            info = DF.iloc[linenum].fillna('')

            InputFloder=info["InputFolder"]
            OutputFloder=info["OutputFolder"]

            if not os.path.exists(OutputFloder):
                os.mkdir(OutputFloder)

            MurraysLaw=False
            MaskToStl=False
            MeshCut=False
            Mesh=False
            FindFace=False
            GenerateInput=False

            try:
                if info["MurraysLaw"]:
                    MurraysLaw = info["MurraysLaw"]
            except:
                pass
            try:
                if info["MaskToStl"]:
                    MaskToStl = info["MaskToStl"]
            except:
                pass
            try:
                if info["MeshCut"]:
                    MeshCut = info["MeshCut"]
            except:
                pass
            try:
                if info["Mesh"]:
                    Mesh = info["Mesh"]
            except:
                pass
            try:
                if info["FindFace"]:
                    FindFace = info["FindFace"]
            except:
                pass
            try:
                if info["GenerateInput"]:
                    GenerateInput = info["GenerateInput"]
            except:
                pass

            print('InputFloder=',InputFloder)
            print('OutputFloder=',OutputFloder)
            print('MurraysLaw=',MurraysLaw)
            print('MaskToStl=',MaskToStl)
            print('MeshCut=',MeshCut)
            print('Mesh=',Mesh)
            print('FindFace=',FindFace)
            print('GenerateInput=',GenerateInput)

            # ##################### MurraysLaw
            if MurraysLaw:
                # change tab
                self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.MurraysLaw)
                # make dir
                if not os.path.exists(info["OutputFolder"] + '/MurraysLaw'):
                    os.mkdir(info["OutputFolder"] + '/MurraysLaw')
                try:
                    if info["MurraysLawBatchProcessTable"]:
                        # set ui
                        self.ui.batchType3PathTxt_AVC.setPlainText('{}'.format(info["MurraysLawBatchProcessTable"]))
                        # Touched function
                        self.mudule.areaVolCalcs.BatchAutoType3()
                    else:
                        raise Exception
                except:
                    # set ui
                    self.ui.parametersPathTxt_AVC.setPlainText('{}'.format(info["MurraysLawparametersPath"]))
                    self.ui.branchMapPathTxt_AVC.setPlainText('{}'.format(info["MurraysBranchMap"]))
                    # Touched function
                    self.mudule.areaVolCalcs.AutoType3()

            # ##################### One Click from mask to stl
            if MaskToStl:
                InputFloder = info["InputFolder"]
                MaskToStlExe = ''
                # change inputfloder and outputfloder
                try:
                    if info["MaskToStlExe"]:
                        MaskToStlExe = info["MaskToStlExe"]
                except:
                    pass
                # change outputfloder
                OutputFloder = info["OutputFolder"] + '/MaskToStl'
                print('MaskToStl InputFloder=', InputFloder)
                print('MaskToStl OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.OneClickCFD)
                # set ui
                self.ui.MaskPathTxt_1_OC.setPlainText('{}'.format(InputFloder))
                self.ui.OutputDirTxt_2_OC.setPlainText('{}'.format(OutputFloder))
                if MaskToStlExe:
                    self.ui.MaskReconExePathTxt_1_OC.setPlainText('{}'.format(MaskToStlExe))
                # Touched function
                self.mudule.OneClickCFD.Mask2Stl()
                time.sleep(1)
                # stack stl
                wall = open(OutputFloder + '/Wall.stl', 'r')
                walltxt = wall.read()
                wall.close()
                lumen = open(OutputFloder + '/lumen.stl', 'r')
                lumentxt = lumen.read()
                lumen.close()
                f = open(OutputFloder + '/Wallstack.stl', 'w')
                f.write(walltxt + lumentxt)
                f.close()

            # # ##################### MeshCut
            # if MeshCut:
            #     InputFloder = info["InputFolder"]
            #     # change inputfloder and outputfloder
            #     if MaskToStl:
            #         InputFloder = info["OutputFolder"] + '/MaskToStl' + '/lumen.stl'
            #     try:
            #         if info["InputStl(MeshCut)"]:
            #             InputFloder = info["InputStl(MeshCut)"]
            #     except:
            #         pass
            #     OutputFloder = info["OutputFolder"] + '/MeshCut'
            #     print('MeshCut InputFloder=', InputFloder)
            #     print('MeshCut OutputFloder=', OutputFloder)
            #     # make dir
            #     if not os.path.exists(OutputFloder):
            #         os.mkdir(OutputFloder)
            #     # change tab
            #     self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.MeshCut)
            #     # set ui
            #     self.ui.StlPathTxt_MC.setPlainText('{}'.format(InputFloder))
            #     self.ui.SaveNameTxt_MC_4.setPlainText('{}'.format(OutputFloder + '/lumenCut.stl'))
            #     # Touched function
            #     self.mudule.MeshCut.Excute()
            #     self.mudule.MeshCut.Save()

            # # ##################### mesh
            # if Mesh:
            #     InputFloder = info["InputFolder"]
            #     MeshExe = ''
            #     # change inputfloder and outputfloder
            #     if MaskToStl:
            #         InputFloder = info["OutputFolder"] + '/MaskToStl' + '/lumen.stl'
            #     if MeshCut:
            #         InputFloder = info["OutputFolder"] + '/MeshCut' + '/lumenCut.stl'
            #     try:
            #         if info["InputStl(Mesh)"]:
            #             InputFloder = info["InputStl(Mesh)"]
            #     except:
            #         pass
            #     try:
            #         if info["MeshExe"]:
            #             MeshExe = info["MeshExe"]
            #     except:
            #         pass
            #     OutputFloder = info["OutputFolder"] + '/Mesh'
            #     # OutputFloder = info["OutputFolder"]
            #     print('Mesh InputFloder=', InputFloder)
            #     print('Mesh OutputFloder=', OutputFloder)
            #     # make dir
            #     if not os.path.exists(OutputFloder):
            #         os.mkdir(OutputFloder)
            #     # change tab
            #     self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.Mesh)
            #     # set ui
            #     if MeshExe:
            #         self.ui.meshexepath_MS.setPlainText('{}'.format(MeshExe))
            #     self.ui.stlpath_MS.setPlainText('{}'.format(InputFloder))
            #     self.ui.plainTextEdit_saveSmoothfil_MS.setPlainText('{}'.format(OutputFloder+'/smooth.stl'))
            #     self.ui.plainTextEdit_saveClippedfil_MS.setPlainText('{}'.format(OutputFloder+'/clipped.stl'))
            #     self.ui.plainTextEdit_saveextensionfil_MS.setPlainText('{}'.format(OutputFloder+'/extension.stl'))
            #     self.ui.plainTextEdit_SurfaceMeshfil_MS.setPlainText('{}'.format(OutputFloder+'/surface.stl'))
            #     # self.ui.plainTextEdit_SurfaceMeshfil_MS.setPlainText('{}'.format(OutputFloder+'/STL_smooth.stl'))
            #     self.ui.plainTextEdit_savemeshpath_MS.setPlainText('{}'.format(OutputFloder+'/FluidMeshInit.vtu'))
            #     self.ui.plainTextEdit_MeshTypeConver_MS.setPlainText('{}'.format(OutputFloder+'/FluidMeshInit.nas'))
            #     # Touched function
            #     self.mudule.Meshgeneration.VmtkSurfaceReader()
            #     self.mudule.Meshgeneration.VmtkSmooth()
            #     self.mudule.Meshgeneration.VmtkBranchClipper()
            #     self.mudule.Meshgeneration.VmtkFlowExtension()
            #     self.mudule.Meshgeneration.VmtkSurfaceRemesh()
            #     self.mudule.Meshgeneration.Vmtk_MeshGenerating()
            #     self.mudule.Meshgeneration.RunVmtk_Script()
            #     self.mudule.Meshgeneration.convertMeshType()

            # # ##################### FaceElemSplit
            # if FindFace:
            #     InputFloder = info["InputFolder"]
            #     FindFaceSet = ''
            #     FindFaceTolerance = ''
            #     # change inputfloder and outputfloder
            #     if Mesh:
            #         InputFloder = info["OutputFolder"] + '/Mesh' + '/FluidMeshInit.nas'
            #     try:
            #         if info["InputNas(FindFace)"]:
            #             InputFloder = info["InputNas(FindFace)"]
            #     except:
            #         pass
            #     try:
            #         if info["Set(FindFace)"]:
            #             FindFaceSet = info["Set(FindFace)"]
            #     except:
            #         pass
            #     try:
            #         if info["Tolerance(FindFace)"]:
            #             FindFaceTolerance = info["Tolerance(FindFace)"]
            #     except:
            #         pass
            #     OutputFloder = info["OutputFolder"] + '/FindFace'
            #     print('FindFace InputFloder=', InputFloder)
            #     print('FindFace OutputFloder=', OutputFloder)
            #     # make dir
            #     if not os.path.exists(OutputFloder):
            #         os.mkdir(OutputFloder)
            #     # change tab
            #     self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.face_and_boundaryconditions)
            #     # set ui
            #     if FindFaceSet:
            #         self.ui.textEdit_inputcsv_SF.setPlainText('{}'.format(FindFaceSet))
            #     self.ui.textEdit_inputnas_SF.setPlainText('{}'.format(InputFloder))
            #     if FindFaceTolerance:
            #         self.ui.spinBox_tolerance_SF.setValue(FindFaceTolerance)
            #     self.ui.textEdit_outputfolder_SF.setPlainText('{}'.format(OutputFloder))
            #     self.ui.textEdit_outputcsv_SF.setPlainText('{}'.format('area'))
            #     self.ui.textEdit_outputnas_SF.setPlainText('{}'.format('CFD'))
            #     # Touched function
            #     self.mudule.SplitFaceElem.findfaceandsplit('True')
            #     self.mudule.SplitFaceElem.calculateandsave()

            # # ##################### GenerateInputFiles
            # if GenerateInput:
            #     InputFloder = info["InputFolder"]
            #     # change inputfloder and outputfloder
            #     Inlet = ''
            #     CopnetWithouttimefuntion = ''
            #     EndingAreaCSV = ''
            #     TimeFunctionInputFloder = ''
            #     GenerateInputTimeStep = ''
            #     AUIPath = ''
            #     if FindFace:
            #         InputFloder = info["OutputFolder"] + '/FindFace' + '/CFD.nas'
            #         # Component Without Timefunction  LumneInlet:
            #         CompIfo = Qtfunction.readtable(self.ui.tableWidget_SF)
            #         for i in CompIfo:
            #             if i[3] == 'False':
            #                 CopnetWithouttimefuntion = CopnetWithouttimefuntion + i[2] + ','
            #             if i[5] == 'True':
            #                 Inlet = Inlet + i[2] + ','
            #         # Ending Area
            #         EndingAreaCSV = info["OutputFolder"] + '/FindFace' + '/area.csv'
            #     try:
            #         if info["TimeStep(GenerateInput)"]:
            #             GenerateInputTimeStep = info["TimeStep(GenerateInput)"]
            #     except:
            #         pass
            #     try:
            #         if info["InputNas(GenerateInput)"]:
            #             InputFloder = info["InputNas(GenerateInput)"]
            #     except:
            #         pass
            #     try:
            #         if info["Component Without Timefuntion(GenerateInput)"]:
            #             CopnetWithouttimefuntion = info["Component Without Timefuntion(GenerateInput)"]
            #     except:
            #         pass
            #     try:
            #         if info["Inlet(GenerateInput)"]:
            #             Inlet = info["Inlet(GenerateInput)"]
            #     except:
            #         pass
            #     try:
            #         if info["TimeFunction(GenerateInput)"]:
            #             TimeFunctionInputFloder = info["TimeFunction(GenerateInput)"]
            #     except:
            #         pass
            #     try:
            #         if info["EndingArea(GenerateInput)"]:
            #             EndingAreaCSV = info["EndingArea(GenerateInput)"]
            #     except:
            #         pass
            #     try:
            #         if info["AUIPath"]:
            #             AUIPath = info["AUIPath"]
            #     except:
            #         pass
            #     OutputFloder = info["OutputFolder"] + '/ADINA'
            #     print('GenerateInput InputFloder=', InputFloder)
            #     print('GenerateInput OutputFloder=', OutputFloder)
            #     # make dir
            #     if not os.path.exists(OutputFloder):
            #         os.mkdir(OutputFloder)
            #     # change tab
            #     self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.Generate_InputFile)
            #     self.ui.tabWidget_GI1.setCurrentWidget(self.ui.CFD_GI)
            #     # set ui
            #     self.ui.plainTextEdit_GI2.setPlainText('{}'.format(InputFloder))
            #     if TimeFunctionInputFloder:
            #         self.ui.timefunctionpath_GI.setPlainText('{}/'.format(TimeFunctionInputFloder))
            #     if CopnetWithouttimefuntion:
            #         self.ui.CompnentsWithoutTimefunctionLineEdit_GI.setText('{}'.format(CopnetWithouttimefuntion))
            #     if Inlet:
            #         self.ui.lineEdit_Lumenset_GI.setText('{}'.format(Inlet))
            #     if EndingAreaCSV:
            #         self.ui.EndingAreaCSVPath_GI.setPlainText('{}'.format(EndingAreaCSV))
            #     if GenerateInputTimeStep:
            #         TimeStep = pdfunction.readexcel(GenerateInputTimeStep)
            #         TimeSteplist = TimeStep.values.tolist()
            #         self.ui.Timestep_GI.setRowCount(len(TimeStep))
            #         for i in range(self.ui.Timestep_GI.rowCount()):
            #             for j in range(self.ui.Timestep_GI.columnCount()):
            #                 if j == 0:
            #                     number = int(TimeSteplist[i][j])
            #                 else:
            #                     number = TimeSteplist[i][j]
            #                 self.ui.Timestep_GI.setItem(i, j, QTableWidgetItem('{0}'.format(number)))
            #     self.ui.DatPath_GI.setPlainText('{}'.format(OutputFloder + '/CFD.dat'))
            #     self.ui.IdbPath_GI.setPlainText('{}'.format(OutputFloder + '/CFD.idb'))
            #     self.ui.InPath_GI.setPlainText('{}'.format(OutputFloder + '/CFD.in'))
            #     if AUIPath:
            #         self.ui.AUIPath_GI.setPlainText('{}'.format(AUIPath))
            #
            #     # Touched function Fluid
            #     self.mudule.Finfilegneration.GIAnalysisModule()
            #     self.mudule.Finfilegneration.ImportNasFile()
            #     self.mudule.Finfilegneration.FluidMaster()
            #     self.mudule.Finfilegneration.BloodMaterial()
            #     self.mudule.Finfilegneration.ExtractEndingSetInfo()
            #     self.mudule.Finfilegneration.ParametersPreset()
            #     self.mudule.Finfilegneration.LoadingMagnitude()
            #     self.mudule.Finfilegneration.GIApplyLoad()
            #     self.mudule.Finfilegneration.WallElst()
            #     self.mudule.Finfilegneration.Timestep()
            #     self.mudule.Finfilegneration.FluidResultOutput()
            #     self.mudule.Finfilegneration.Saveidbdatfil()
            #     self.mudule.Finfilegneration.SaveFInFil()
            #     self.mudule.Finfilegneration.GILoading_INFile()

        # self.ui.plainTextEdit_BatchTable_MC.setPlainText('{}'.format(inpath))
        # self.ui.plainTextEdit_BatchTable_MS.setPlainText('{}'.format(inpath))
        # self.ui.plainTextEdit_BatchTable_SF.setPlainText('{}'.format(inpath))
        # self.ui.plainTextEdit_BatchTable_GI.setPlainText('{}'.format(inpath))
        self.mudule.MeshCut.batchrun(inpath)
        self.mudule.Meshgeneration.batchrun(inpath)
        self.mudule.SplitFaceElem.batchrun(inpath)
        self.mudule.Finfilegneration.batchrun(inpath)

        # change tab
        self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.OneClicked)