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

class CarotidSolidOneClicked():
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.PushButton_CSV_SCOC_Z.clicked.connect(lambda: self.batchprogresscsv())
        self.ui.PushButton_run_SCOC_Z.clicked.connect(lambda: self.batchProgress())
        self.mudule = Hedys

    def batchprogresscsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui,qtObj=True)
        # set filename
        self.ui.TextEdit_CSV_SCOC_Z.setPlainText('{}'.format(filename))

    def batchProgress(self):
        inpath = self.ui.TextEdit_CSV_SCOC_Z.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for linenum in range(len(DF)):
            # get line of table
            print('get info in line', linenum)
            info = DF.iloc[linenum].fillna('')

            InputFloder = info.InputFloder
            OutputFloder = info.OutputFloder
            MaskToStl = False
            MeshCut = False
            Mesh = False
            FindFace = False
            MaskCoordinates = False
            TissueElemAssign = False
            NodeMatching = False
            GenerateInput = False

            try:
                if info.MaskToStl:
                    MaskToStl = info.MaskToStl
            except:
                pass
            try:
                if info.MeshCut:
                    MeshCut = info.MeshCut
            except:
                pass
            try:
                if info.Mesh:
                    Mesh = info.Mesh
            except:
                pass
            try:
                if info.FindFace:
                    FindFace = info.FindFace
            except:
                pass
            try:
                if info.MaskCoordinates:
                    MaskCoordinates = info.MaskCoordinates
            except:
                pass
            try:
                if info.TissueElemAssign:
                    TissueElemAssign = info.TissueElemAssign
            except:
                pass
            try:
                if info.NodeMatching:
                    NodeMatching = info.NodeMatching
            except:
                pass
            try:
                if info.GenerateInput:
                    GenerateInput = info.GenerateInput
            except:
                pass

            print('InputFloder=',InputFloder)
            print('OutputFloder=',OutputFloder)
            print('MaskToStl=',MaskToStl)
            print('MeshCut=',MeshCut)
            print('Mesh=',Mesh)
            print('FindFace=',FindFace)
            print('MaskCoordinates=',MaskCoordinates)
            print('TissueElemAssign=',TissueElemAssign)
            print('GenerateInput=',GenerateInput)
            print('NodeMatching=', NodeMatching)
            # make dir
            if not os.path.exists(OutputFloder):
                os.mkdir(OutputFloder)

            # ##################### One Click from mask to stl
            if MaskToStl:
                InputFloder = info.InputFloder
                MaskToStlExe = ''
                # change inputfloder and outputfloder
                try:
                    if info.MaskToStlExe:
                        MaskToStlExe = info.MaskToStlExe
                except:
                    pass
                # change outputfloder
                OutputFloder = info.OutputFloder + '/MaskToStl'
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

            # ##################### MeshCut
            if MeshCut:
                InputFloder = info.InputFloder
                # change inputfloder and outputfloder
                if MaskToStl:
                    InputFloder = info.OutputFloder+'/MaskToStl/Wallstack.stl'
                try:
                    if info.MeshCutInputStl:
                        InputFloder = info.MeshCutInputStl
                except:
                    pass
                OutputFloder = info.OutputFloder + '/MeshCut'
                print('MeshCut InputFloder=', InputFloder)
                print('MeshCut OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.MeshCut)
                # set ui
                self.ui.StlPathTxt_MC_1.setPlainText('{}'.format(InputFloder))
                self.ui.SaveNameTxt_MC_1.setPlainText('{}'.format(OutputFloder + '/WallCut.stl'))
                # Touched function
                self.mudule.MeshCut.Excute()
                self.mudule.MeshCut.Save()

            # ##################### MaskCoordinates
            if MaskCoordinates:
                InputFloder = info.InputFloder
                # change inputfloder and outputfloder
                if MaskToStl:
                    InputFloder = info.InputFloder
                try:
                    if info.MaskCoordinatesInputMask:
                        InputFloder = info.MaskCoordinatesInputMask
                except:
                    pass
                OutputFloder = info.OutputFloder + '/MaskCoordinates'
                print('FindFace InputFloder=', InputFloder)
                print('FindFace OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.MaskCoordinate)
                # set ui
                self.ui.filePathsTxt_MCJZ.setPlainText('{}'.format(InputFloder))
                self.ui.dirPathTxt_MCJZ.setPlainText('{}'.format(OutputFloder))
                # Touched function
                self.mudule.extractPointCoords.CoordinateExtraction()

            # ##################### mesh
            if Mesh:
                InputFloder = info.InputFloder
                MeshExe=''
                # change inputfloder and outputfloder
                if MaskToStl:
                    InputFloder = info.OutputFloder + '/MaskToStl' + '/Wallstack.stl'
                if MeshCut:
                    InputFloder = info.OutputFloder + '/MeshCut' + '/WallCut.stl'
                try:
                    if info.MeshInputStl:
                        InputFloder = info.MeshInputStl
                except:
                    pass
                try:
                    if info.MeshExe:
                        MeshExe = info.MeshExe
                except:
                    pass
                OutputFloder = info.OutputFloder + '/Mesh'
                print('Mesh InputFloder=', InputFloder)
                print('Mesh OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.Mesh)
                # set ui
                if MeshExe:
                    self.ui.meshexepath_MS.setPlainText('{}'.format(MeshExe))
                self.ui.stlpath_MS.setPlainText('{}'.format(InputFloder))
                self.ui.plainTextEdit_saveClippedfil_MS.setPlainText('')
                self.ui.plainTextEdit_saveextensionfil_MS.setPlainText('')
                self.ui.lineEdit_boundarylayerbool_MS.setText('0')
                self.ui.checkBox_SurfaceClipper_MS.setChecked(False)
                self.ui.checkBox_FlowExtension_MS.setChecked(False)
                self.ui.radioButton_EdgeLengthAdaptive_MS.setChecked(True)
                self.ui.plainTextEdit_savemeshpath_MS.setPlainText('{}'.format(OutputFloder+'/WallMeshInit.vtu'))
                self.ui.plainTextEdit_MeshTypeConver_MS.setPlainText('{}'.format(OutputFloder+'/WallMeshInit.nas'))
                # Touched function
                self.mudule.Meshgeneration.VmtkSurfaceReader()
                self.mudule.Meshgeneration.VmtkBranchClipper()
                self.mudule.Meshgeneration.VmtkFlowExtension()
                self.mudule.Meshgeneration.Vmtk_MeshGenerating()
                self.mudule.Meshgeneration.RunVmtk_Script()
                self.mudule.Meshgeneration.convertMeshType()

            # ##################### FaceElemSplit
            if FindFace:
                InputFloder = info.InputFloder
                FindFaceSet = ''
                FindFaceTolerance = ''
                # change inputfloder and outputfloder
                if Mesh:
                    InputFloder = info.OutputFloder + '/Mesh' + '/WallMeshInit.nas'
                try:
                    if info.FindFaceInputNas:
                        InputFloder = info.FindFaceInputNas
                except:
                    pass
                try:
                    if info.FindFaceSet:
                        FindFaceSet = info.FindFaceSet
                except:
                    pass
                try:
                    if info.FindFaceTolerance:
                        FindFaceTolerance = info.FindFaceTolerance
                except:
                    pass
                OutputFloder = info.OutputFloder + '/FindFace'
                print('FindFace InputFloder=', InputFloder)
                print('FindFace OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.face_and_boundaryconditions)
                # set ui
                if FindFaceSet:
                    self.ui.textEdit_inputcsv_SF.setPlainText('{}'.format(FindFaceSet))
                self.ui.textEdit_inputnas_SF.setPlainText('{}'.format(InputFloder))
                if FindFaceTolerance:
                    self.ui.spinBox_tolerance_SF.setValue(FindFaceTolerance)
                self.ui.textEdit_outputfolder_SF.setPlainText('{}'.format(OutputFloder))
                self.ui.textEdit_outputcsv_SF.setPlainText('{}'.format('area'))
                self.ui.textEdit_outputnas_SF.setPlainText('{}'.format('Wall'))
                # Touched function
                self.mudule.SplitFaceElem.findfaceandsplit('True')
                self.mudule.SplitFaceElem.calculateandsave()

            # ##################### TissueElemAssign
            if TissueElemAssign:
                InputFloder = info.InputFloder
                InputNpyFloder=''
                # change inputfloder and outputfloder
                if FindFace:
                    InputFloder = info.OutputFloder + '/FindFace/Wall.nas'
                if MaskCoordinates:
                    InputNpyFloder = info.OutputFloder + '/MaskCoordinates'
                try:
                    if info.TissueElemAssignCooFloder:
                        InputFloder = info.TissueElemAssignCooFloder
                except:
                    pass
                try:
                    if info.TissueElemAssignNpyFloder:
                        InputNpyFloder = info.TissueElemAssignNpyFloder
                except:
                    pass
                OutputFloder = info.OutputFloder + '/TissueElemId'
                print('FindFace InputFloder=', InputFloder)
                print('FindFace OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.TissueElemAssign)
                # set ui
                self.ui.NasPath_TEAZA.setPlainText('{}'.format(InputFloder))
                self.ui.NpyPath_TEAZA.setPlainText('{}'.format(InputNpyFloder))
                self.ui.SavePath_TEAZA.setPlainText('{}'.format(OutputFloder))
                # Touched function
                self.mudule.TissueElemAssign.runelemid()

            # ##################### GenerateInputFiles
            if GenerateInput:
                InputFloder = info.InputFloder
                # change inputfloder and outputfloder
                TissueElemIdPath=''
                solidcompid='1'
                FSBOUNDARY='53'
                boundarylist=[]
                Materiallist=[]
                if FindFace:
                    InputFloder = info.OutputFloder + '/FindFace' + '/Wall.nas'
                    # Component Without Timefunction  LumneInlet:
                    CompIfo = Qtfunction.readtable(self.ui.tableWidget_SF)
                    for i in CompIfo:
                        if i[4] == 'PSOLID':
                            solidcompid = i[1]
                        else:
                            if i[5] == 'True':
                                boundarylist.append([])
                                boundarylist[-1].append('All')
                                boundarylist[-1].append(i[1])
                            if i[6] == 'True':
                                boundarylist.append([])
                                boundarylist[-1].append('Pressure')
                                boundarylist[-1].append(i[1])
                            if i[3] == 'False' and i[6] == 'False':
                                FSBOUNDARY=i[1]
                    # 嵌套列表去重
                    boundarylist = [list(t) for t in set(tuple(_) for _ in boundarylist)]
                if TissueElemAssign:
                    TissueElemIdPath=info.OutputFloder+'/TissueElemId'
                try:
                    if info.GenerateInputNas:
                        InputFloder = info.GenerateInputNas
                except:
                    pass
                try:
                    if info.GenerateInputBoundaryset:
                        boundaryDF = pdfunction.readexcel(info.GenerateInputBoundaryset)
                        boundarylist = boundaryDF.values.tolist()
                except:
                    pass
                try:
                    if info.GenerateInputFSBOUNDARY:
                        FSBOUNDARY = info.GenerateInputFSBOUNDARY
                except:
                    pass
                try:
                    if info.GenerateInputTissueElemIdPath:
                        TissueElemIdPath = info.GenerateInputTissueElemIdPath
                except:
                    pass
                if TissueElemIdPath:
                    TissueElemIdPathlist=[]
                    for home,dirs,files in os.walk(TissueElemIdPath):
                        for filename in files:
                            if '_2dndarr.txt' in filename.split('/')[-1]:
                                TissueElemIdPathlist.append(filename)
                    for i in TissueElemIdPathlist:
                        if i.endswith('2_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('Coronary')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append(solidcompid)
                            # Materiallist[-1].append('5')
                            Materiallist[-1].append(TissueElemIdPath+'/'+i)
                        if i.endswith('3_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('Calcium')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append('6')
                            Materiallist[-1].append(TissueElemIdPath+'/'+i)
                        if i.endswith('4_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('Thrombus')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append('7')
                            Materiallist[-1].append(TissueElemIdPath+'/'+i)
                        if i.endswith('5_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('Lipid')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append('8')
                            Materiallist[-1].append(TissueElemIdPath+'/'+i)
                        if i.endswith('6_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('FibrousCap')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append('9')
                            Materiallist[-1].append(TissueElemIdPath+'/'+i)
                try:
                    if info.GenerateInputMaterialset:
                        MaterialDF = pdfunction.readexcel(info.GenerateInputMaterialset)
                        Materiallist = MaterialDF.values.tolist()
                except:
                    pass
                OutputFloder = info.OutputFloder + '/ADINA'
                print('GenerateInput InputFloder=', InputFloder)
                print('GenerateInput OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.Generate_InputFile)
                self.ui.tabWidget_GI1.setCurrentWidget(self.ui.Solid_GI)
                # set ui
                self.ui.plainTextEdit_GI2.setPlainText('{}'.format(InputFloder))
                if Materiallist:
                    self.ui.ApplyMaterialGI4_2.setRowCount(len(Materiallist))
                    self.ui.ApplyMaterialGI4_2.setColumnCount(len(Materiallist[0]))
                    for i in range(len(Materiallist)):
                        for j in range(len(Materiallist[i])):
                            item = QTableWidgetItem('{0}'.format(Materiallist[i][j]))
                            self.ui.ApplyMaterialGI4_2.setItem(i, j, item)
                if boundarylist:
                    self.ui.SBoundary_GI.setRowCount(len(boundarylist))
                    self.ui.SBoundary_GI.setColumnCount(len(boundarylist[0]))
                    for i in range(len(boundarylist)):
                        for j in range(len(boundarylist[i])):
                            item = QTableWidgetItem('{0}'.format(boundarylist[i][j]))
                            self.ui.SBoundary_GI.setItem(i, j, item)
                if FSBOUNDARY:
                    self.ui.lineEditGI_2.setText('{}'.format(FSBOUNDARY))
                if info.GenerateInputTimeStep:
                    TimeStep = pdfunction.readexcel(info.GenerateInputTimeStep)
                    TimeSteplist = TimeStep.values.tolist()
                    self.ui.Timestep_GI.setRowCount(len(TimeStep))
                    for i in range(self.ui.Timestep_GI.rowCount()):
                        for j in range(self.ui.Timestep_GI.columnCount()):
                            if j == 0:
                                number = int(TimeSteplist[i][j])
                            else:
                                number = TimeSteplist[i][j]
                            self.ui.Timestep_GI.setItem(i, j, QTableWidgetItem('{0}'.format(number)))
                self.ui.DatPath_GI.setPlainText('{}'.format(OutputFloder + '/Wall.dat'))
                self.ui.IdbPath_GI.setPlainText('{}'.format(OutputFloder + '/Wall.idb'))
                self.ui.InPath_GI.setPlainText('{}'.format(OutputFloder + '/Wall.in'))
                self.ui.AUIPath_GI.setPlainText('{}'.format(info.GenerateInputAUI))
                # Touched function Solid
                self.mudule.Finfilegneration.ImportNasFile()
                self.mudule.Finfilegneration.GIAnalysisModule()
                self.mudule.Finfilegneration.SolidMaster()
                self.mudule.Finfilegneration.SlargeDeformation()
                self.mudule.Finfilegneration.GIApplyMaterial()
                self.mudule.Finfilegneration.SBoundaryCondition()
                self.mudule.Finfilegneration.SFSIBoundary()
                self.mudule.Finfilegneration.Timestep()
                self.mudule.Finfilegneration.SResultsOutput()
                self.mudule.Finfilegneration.Saveidbdatfil()
                self.mudule.Finfilegneration.SaveSInFil()
                self.mudule.Finfilegneration.GILoading_INFile()

            # ##################### NodeMatching
            if NodeMatching:
                try:
                    NodeMatching=int(info.NodeMatching)
                except:
                    NodeMatching=1
                for i in range(NodeMatching):
                    InputFloder = info.InputFloder
                    NodeMatchingInletAndOutletSet=''
                    NodeMatchingOffesetvalue=''
                    NodeMatchingGroupNum=''
                    NodeMatchingfluidlumenset=''
                    NodeMatchingsolidlumenset=''
                    NodeMatchingPressureID=''
                    NodeMatchingEleFaceSetPrefix=''
                    NodeMatchingTimeFunctionPrefix=''
                    NodeMatchingLoadPrefix=''
                    NodeMatchingAUI=''
                    NodeMatchingIdb=''
                    NodeMatchingPor=''
                    NodeMatchingin=info.OutputFloder + '/NodeMatching'+str(i-1)+'/WallWithPressure'+str(i-1)+'.in'
                    # change inputfloder and outputfloder
                    if GenerateInput:
                        InputFloder = info.OutputFloder + '/ADINA/Wall.idb'
                        if i == 0:
                            NodeMatchingin=info.OutputFloder + '/ADINA/Wall.in'
                    if FindFace:
                        InletAndOutlet = []
                        CompIfo = Qtfunction.readtable(self.ui.tableWidget_SF)
                        for j in CompIfo:
                            if not j[4] == 'PSOLID':
                                if j[5] == 'True':
                                    InletAndOutlet.append(j[1])
                                if j[6] == 'True':
                                    NodeMatchingsolidlumenset=j[1]
                        NodeMatchingInletAndOutletSet=','.join(InletAndOutlet)
                    try:
                        if info['NodeMatchingin'+str(i)]:
                            NodeMatchingin = info['NodeMatchingin'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingSolidIdb'+str(i)]:
                            InputFloder = info['NodeMatchingSolidIdb'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingInletAndOutletSet'+str(i)]:
                            NodeMatchingInletAndOutletSet = info['NodeMatchingInletAndOutletSet'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingOffesetvalue'+str(i)]:
                            NodeMatchingOffesetvalue = ['NodeMatchingOffesetvalue'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingGroupNum'+str(i)]:
                            NodeMatchingGroupNum = info['NodeMatchingGroupNum'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingfluidlumenset'+str(i)]:
                            NodeMatchingfluidlumenset = info['NodeMatchingfluidlumenset'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingsolidlumenset'+str(i)]:
                            NodeMatchingsolidlumenset = info['NodeMatchingsolidlumenset'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingPressureID'+str(i)]:
                            NodeMatchingPressureID = info['NodeMatchingPressureID'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingEleFaceSetPrefix'+str(i)]:
                            NodeMatchingEleFaceSetPrefix = info['NodeMatchingEleFaceSetPrefix'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingTimeFunctionPrefix'+str(i)]:
                            NodeMatchingTimeFunctionPrefix = info['NodeMatchingTimeFunctionPrefix'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingLoadPrefix'+str(i)]:
                            NodeMatchingLoadPrefix = info['NodeMatchingLoadPrefix'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingAUI'+str(i)]:
                            NodeMatchingAUI = info['NodeMatchingAUI'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingIdb'+str(i)]:
                            NodeMatchingIdb = info['NodeMatchingIdb'+str(i)]
                    except:
                        pass
                    try:
                        if info['NodeMatchingPor'+str(i)]:
                            NodeMatchingPor = info['NodeMatchingPor'+str(i)]
                    except:
                        pass
                    OutputFloder = info.OutputFloder + '/NodeMatching'+str(i)
                    print('NodeMatching InputFloder=', InputFloder)
                    print('NodeMatching OutputFloder=', OutputFloder)
                    # make dir
                    if not os.path.exists(OutputFloder):
                        os.mkdir(OutputFloder)
                    # change tab
                    self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.NodeMatching1)
                    # set ui
                    self.ui.plainTextEditNM5.setPlainText('{}'.format(InputFloder))
                    self.ui.plainTextEdit_SaveFluidPloFile_NM.setPlainText('{}/'.format(OutputFloder))
                    self.ui.plainTextEdit_SaveSolidPloFile_NM.setPlainText('{}/'.format(OutputFloder))
                    if NodeMatchingIdb:
                        self.ui.fluidfile_NM2.setPlainText('{}'.format(NodeMatchingIdb))
                    if NodeMatchingPor:
                        self.ui.plainTextEdit_NM3.setPlainText('{}'.format(NodeMatchingPor))
                    if NodeMatchingAUI:
                        self.ui.plainTextEdit_NM1.setPlainText('{}'.format(NodeMatchingAUI))
                    if NodeMatchingfluidlumenset:
                        self.ui.fluidset_NM1.setText('{}'.format(NodeMatchingfluidlumenset))
                    if NodeMatchingsolidlumenset:
                        self.ui.lumenset_NM.setText('{}'.format(NodeMatchingsolidlumenset))
                    if NodeMatchingInletAndOutletSet:
                        self.ui.lineEditNM.setText('{}'.format(NodeMatchingInletAndOutletSet))
                    if NodeMatchingOffesetvalue:
                        self.ui.lineEdit_NM2.setText('{}'.format(NodeMatchingOffesetvalue))
                    if NodeMatchingGroupNum:
                        self.ui.lineEdit_NM3.setText('{}'.format(NodeMatchingGroupNum))
                    if NodeMatchingPressureID:
                        self.ui.lineEdit_PressureID_NM.setText('{}'.format(NodeMatchingPressureID))
                    if NodeMatchingEleFaceSetPrefix:
                        self.ui.lineEdit_EleFaceSetPrefix_NM.setText('{}'.format(NodeMatchingEleFaceSetPrefix))
                    if NodeMatchingTimeFunctionPrefix:
                        self.ui.lineEdit_TimeFunctionPrefix_NM.setText('{}'.format(NodeMatchingTimeFunctionPrefix))
                    if NodeMatchingLoadPrefix:
                        self.ui.lineEdit_LoadPrefix_NM.setText('{}'.format(NodeMatchingLoadPrefix))
                    # Touched function
                    self.mudule.NodeMatching.export_fluid_data()
                    self.mudule.NodeMatching.export_solid_data()
                    self.mudule.NodeMatching.submit_fd_to_adina()
                    self.mudule.NodeMatching.submit_sd_to_adina()
                    self.mudule.NodeMatching.strip_data()
                    self.mudule.NodeMatching.run()
                    # stack in
                    infile = open(NodeMatchingin, 'r')
                    intxt = infile.read()
                    infile.close()
                    AddGroup = open(OutputFloder + '/AddGroup.plo', 'r')
                    AddGrouptxt = AddGroup.read()
                    AddGroup.close()
                    f = open(OutputFloder + '/WallWithPressure' + str(i) + '.in', 'w')
                    f.write(intxt + '/n' + AddGrouptxt)
                    f.close()
        # change tab
        self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.OneClicked)