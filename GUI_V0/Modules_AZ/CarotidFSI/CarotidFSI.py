import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
import Save_Load_File
import Qtfunction
import pdfunction

import time
import json
import shutil
import pandas as pd

class CarotidFSIMain():
    def __init__(self, UI = None, Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI

            self.ui.PushButton_LoadFolder_OCZ.clicked.connect(lambda: self.LoadFolder())
            self.ui.PushButton_ParameterPath_OCZ.clicked.connect(lambda: self.ParameterPathcsv())
            self.ui.PushButton_ModulesChoose_OCZ.clicked.connect(lambda: self.ModulesChoosecsv())
            self.ui.PushButton_CarotidFSI_OCZ.clicked.connect(lambda: self.CarotidFSI())
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            self.model = Hedys

        self.initCarotidFSI()

    # init process:
    def initCarotidFSI(self):
        if self.modelui:
            self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
        self.LoadFolderPath = ''
        self.ParameterPath = ''
        self.ModulesChoosePath = ''

        self.Parameterdf = pd.DataFrame()
        self.ModulesChoosedf = pd.DataFrame()
        self.CFD_FilterLumentabledf = pd.DataFrame()
        self.CFD_MaskToStltabledf = pd.DataFrame()
        self.CFD_MeshCuttabledf = pd.DataFrame()
        self.CFD_Meshtabledf = pd.DataFrame()
        self.CFD_FindFacetabledf = pd.DataFrame()
        self.CFD_GenerateInputtabledf = pd.DataFrame()
        self.CFD_DataOutputtabledf = pd.DataFrame()
        self.CFD_PostNpytabledf = pd.DataFrame()
        self.CFD_Paraviewtabledf = pd.DataFrame()
        self.CFD_SaveVtutabledf = pd.DataFrame()
        self.solid_WallMaskToStltabledf = pd.DataFrame()
        self.solid_WallSmoothtabledf = pd.DataFrame()
        self.solid_WallStackLumentabledf = pd.DataFrame()
        self.solid_WallCuttabledf = pd.DataFrame()
        self.solid_WallFillGaptabledf = pd.DataFrame()
        self.solid_WallMeshtabledf = pd.DataFrame()
        self.solid_WallFindFacetabledf = pd.DataFrame()
        self.solid_TissueCootabledf = pd.DataFrame()
        self.solid_TissueElemIdtabledf = pd.DataFrame()
        self.solid_GenerateInputtabledf = pd.DataFrame()
        self.solid_NodeMatchingtabledf = pd.DataFrame()
        self.solid_Npytabledf = pd.DataFrame()
        self.solid_SaveVtutabledf = pd.DataFrame()

        self.caselist = []

    def LoadFolder(self):
        dirname = Save_Load_File.OpenDirPathQt(dispMsg='Working Directory',
                                               fileObj=self.ui,
                                               qtObj=True)
        self.ui.TextEdit_LoadFolder_OCZ.setPlainText(dirname)

    def ParameterPathcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.TextEdit_ParameterPath_OCZ.setPlainText('{}'.format(filename))

    def ModulesChoosecsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui,qtObj=True)
        # set filename
        self.ui.TextEdit_ModulesChoose_OCZ.setPlainText('{}'.format(filename))

    def Getcaselist(self):
        self.caselist = []
        for root, dirs, files in os.walk(self.LoadFolderPath):
            for file in files:
                if file == 'parameter.json':
                    self.caselist.append(root.replace('\\', '/'))
        if self.caselist == []:
            for root, dirs, files in os.walk(self.LoadFolderPath):
                for file in files:
                    if file.endswith('.nii.gz'):
                        casedirpath = '/'.join([root.replace('\\', '/'), file.replace('.nii.gz', '')])
                        self.CreateFolder(casedirpath)
                        self.caselist.append(casedirpath)

                        oriMaskpath = '/'.join([root.replace('\\', '/'), file])
                        caseMaskpath = '/'.join([casedirpath, 'Mask.nii.gz'])
                        self.CopyFile(oriMaskpath, caseMaskpath)
        print('caselist', self.caselist)

    def CreateFolder(self, dirpath):
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
            print('Create ', dirpath, ' done')

    def CopyFile(self, source, dst):
        shutil.copyfile(source, dst)
        print('Copy ', source, ' to ', dst)

    def DfToDict(self, df, casedir):
        dictreplacecasedir = {}
        for i in range(len(df)):
            if df.iloc[i].str.count(casedir).sum() > 0:
                series = df.iloc[i]
                seriesreplacecasedir = series.str.replace(casedir, '')
                seriestodict = pd.Series()
                for j in range(len(series)):
                    if type(series[j]) == str:
                        seriestodict[series.index[j]] = seriesreplacecasedir[j]
                    else:
                        seriestodict[series.index[j]] = series[j]
                dictreplacecasedir = seriestodict.to_dict()
                print('dictreplacecasedir', dictreplacecasedir)
        return dictreplacecasedir

    def savejsondict(self, casejsonpath, jsondict):
        jsonloaddict = {}
        if os.path.exists(casejsonpath):
            with open(casejsonpath) as fp:
                jsonloaddict = json.load(fp)
        for key, value in jsondict.items():
            jsonloaddict[key] = value
        with open(casejsonpath, 'w') as fp:
            fp.truncate()
            json.dump(jsonloaddict, fp)
        print('save ', jsondict, ' to ', casejsonpath)

    def CarotidFSI(self):
        self.initCarotidFSI()

        self.LoadFolderPath = self.ui.TextEdit_LoadFolder_OCZ.toPlainText()
        self.ParameterPath = self.ui.TextEdit_ParameterPath_OCZ.toPlainText()
        self.ModulesChoosePath = self.ui.TextEdit_ModulesChoose_OCZ.toPlainText()
        print('LoadFolderPath', self.LoadFolderPath)
        print('ParameterPath', self.ParameterPath)
        print('ModulesChoosePath', self.ModulesChoosePath)

        if os.path.exists(self.ParameterPath):
            self.Parameterdf = pdfunction.readexcel(self.ParameterPath)
        if os.path.exists(self.ModulesChoosePath):
            self.ModulesChoosedf = pdfunction.readexcel(self.ModulesChoosePath)

        self.Getcaselist()

        self.Tabledir = '/'.join([self.LoadFolderPath, 'Table'])
        self.CreateFolder(self.Tabledir)

        CFD_FilterLumentablepath = '/'.join([self.Tabledir, 'CFD_FilterLumen.csv'])
        CFD_MaskToStltablepath = '/'.join([self.Tabledir, 'CFD_MaskToStl.csv'])
        CFD_MeshCuttablepath = '/'.join([self.Tabledir, 'CFD_MeshCut.csv'])
        CFD_Meshtablepath = '/'.join([self.Tabledir, 'CFD_Mesh.csv'])
        CFD_FindFacetablepath = '/'.join([self.Tabledir, 'CFD_FindFace.csv'])
        CFD_GenerateInputtablepath = '/'.join([self.Tabledir, 'CFD_GenerateInput.csv'])
        CFD_DataOutputtablepath = '/'.join([self.Tabledir, 'CFD_Npy.csv'])
        CFD_PostNpytablepath = '/'.join([self.Tabledir, 'CFD_PostNpy.csv'])
        CFD_Paraviewtablepath = '/'.join([self.Tabledir, 'CFD_Paraview.csv'])
        CFD_SaveVtutablepath = '/'.join([self.Tabledir, 'CFD_SaveVtu.csv'])
        solid_WallMaskToStltablepath = '/'.join([self.Tabledir, 'solid_WallMaskToStl.csv'])
        solid_WallSmoothtablepath = '/'.join([self.Tabledir, 'solid_WallSmooth.csv'])
        solid_WallStackLumentablepath = '/'.join([self.Tabledir, 'solid_WallStackLumen.csv'])
        solid_WallCuttablepath = '/'.join([self.Tabledir, 'solid_WallCut.csv'])
        solid_WallFillGaptablepath = '/'.join([self.Tabledir, 'solid_WallFillGap.csv'])
        solid_WallMeshtablepath = '/'.join([self.Tabledir, 'solid_WallMesh.csv'])
        solid_WallFindFacetablepath = '/'.join([self.Tabledir, 'solid_WallFindFace.csv'])
        solid_TissueCootablepath = '/'.join([self.Tabledir, 'solid_TissueCoo.csv'])
        solid_TissueElemIdtablepath = '/'.join([self.Tabledir, 'solid_TissueElemId.csv'])
        solid_GenerateInputtablepath = '/'.join([self.Tabledir, 'solid_GenerateInput.csv'])
        solid_NodeMatchingtablepath = '/'.join([self.Tabledir, 'solid_NodeMatching.csv'])
        solid_Npytablepath = '/'.join([self.Tabledir, 'solid_Npy.csv'])
        solid_SaveVtutablepath = '/'.join([self.Tabledir, 'solid_SaveVtu.csv'])

        #get parameter from table
        CFD_FilterLumentabledfload = pd.DataFrame()
        if os.path.exists(CFD_FilterLumentablepath):
            CFD_FilterLumentabledfload = pdfunction.readexcel(CFD_FilterLumentablepath)
        CFD_MaskToStltabledfload = pd.DataFrame()
        if os.path.exists(CFD_MaskToStltablepath):
            CFD_MaskToStltabledfload = pdfunction.readexcel(CFD_MaskToStltablepath)
        CFD_MeshCuttabledfload = pd.DataFrame()
        if os.path.exists(CFD_MeshCuttablepath):
            CFD_MeshCuttabledfload = pdfunction.readexcel(CFD_MeshCuttablepath)
        CFD_Meshtabledfload = pd.DataFrame()
        if os.path.exists(CFD_Meshtablepath):
            CFD_Meshtabledfload = pdfunction.readexcel(CFD_Meshtablepath)
        CFD_FindFacetabledfload = pd.DataFrame()
        if os.path.exists(CFD_FindFacetablepath):
            CFD_FindFacetabledfload = pdfunction.readexcel(CFD_FindFacetablepath)
        CFD_GenerateInputtabledfload = pd.DataFrame()
        if os.path.exists(CFD_GenerateInputtablepath):
            CFD_GenerateInputtabledfload = pdfunction.readexcel(CFD_GenerateInputtablepath)
        CFD_DataOutputtabledfload = pd.DataFrame()
        if os.path.exists(CFD_DataOutputtablepath):
            CFD_DataOutputtabledfload = pdfunction.readexcel(CFD_DataOutputtablepath)
        CFD_PostNpytabledfload = pd.DataFrame()
        if os.path.exists(CFD_PostNpytablepath):
            CFD_PostNpytabledfload = pdfunction.readexcel(CFD_PostNpytablepath)
        CFD_Paraviewtabledfload = pd.DataFrame()
        if os.path.exists(CFD_Paraviewtablepath):
            CFD_Paraviewtabledfload = pdfunction.readexcel(CFD_Paraviewtablepath)
        CFD_SaveVtutabledfload = pd.DataFrame()
        if os.path.exists(CFD_SaveVtutablepath):
            CFD_SaveVtutabledfload = pdfunction.readexcel(CFD_SaveVtutablepath)
        solid_WallMaskToStltabledfload = pd.DataFrame()
        if os.path.exists(solid_WallMaskToStltablepath):
            solid_WallMaskToStltabledfload = pdfunction.readexcel(solid_WallMaskToStltablepath)
        solid_WallSmoothtabledfload = pd.DataFrame()
        if os.path.exists(solid_WallSmoothtablepath):
            solid_WallSmoothtabledfload = pdfunction.readexcel(solid_WallSmoothtablepath)
        solid_WallStackLumentabledfload = pd.DataFrame()
        if os.path.exists(solid_WallStackLumentablepath):
            solid_WallStackLumentabledfload = pdfunction.readexcel(solid_WallStackLumentablepath)
        solid_WallCuttabledfload = pd.DataFrame()
        if os.path.exists(solid_WallCuttablepath):
            solid_WallCuttabledfload = pdfunction.readexcel(solid_WallCuttablepath)
        solid_WallFillGaptabledfload = pd.DataFrame()
        if os.path.exists(solid_WallFillGaptablepath):
            solid_WallFillGaptabledfload = pdfunction.readexcel(solid_WallFillGaptablepath)
        solid_WallMeshtabledfload = pd.DataFrame()
        if os.path.exists(solid_WallMeshtablepath):
            solid_WallMeshtabledfload = pdfunction.readexcel(solid_WallMeshtablepath)
        solid_WallFindFacetabledfload = pd.DataFrame()
        if os.path.exists(solid_WallFindFacetablepath):
            solid_WallFindFacetabledfload = pdfunction.readexcel(solid_WallFindFacetablepath)
        solid_TissueCootabledfload = pd.DataFrame()
        if os.path.exists(solid_TissueCootablepath):
            solid_TissueCootabledfload = pdfunction.readexcel(solid_TissueCootablepath)
        solid_TissueElemIdtabledfload = pd.DataFrame()
        if os.path.exists(solid_TissueElemIdtablepath):
            solid_TissueElemIdtabledfload = pdfunction.readexcel(solid_TissueElemIdtablepath)
        solid_GenerateInputtabledfload = pd.DataFrame()
        if os.path.exists(solid_GenerateInputtablepath):
            solid_GenerateInputtabledfload = pdfunction.readexcel(solid_GenerateInputtablepath)
        solid_NodeMatchingtabledfload = pd.DataFrame()
        if os.path.exists(solid_NodeMatchingtablepath):
            solid_NodeMatchingtabledfload = pdfunction.readexcel(solid_NodeMatchingtablepath)
        solid_Npytabledfload = pd.DataFrame()
        if os.path.exists(solid_Npytablepath):
            solid_Npytabledfload = pdfunction.readexcel(solid_Npytablepath)
        solid_SaveVtutabledfload = pd.DataFrame()
        if os.path.exists(solid_SaveVtutablepath):
            solid_SaveVtutabledfload = pdfunction.readexcel(solid_SaveVtutablepath)

        ModulesChoosedict = dict(zip(self.ModulesChoosedf['Modules'], self.ModulesChoosedf['Choose']))
        for i in range(len(self.caselist)):
            casedir = self.caselist[i]
            casejsonpath = '/'.join([casedir, 'parameter.json'])
            caseCFDdir = '/'.join([casedir, 'CFD'])
            caseLumenMaskdir = '/'.join([caseCFDdir, 'LumenMask'])
            caseMaskToStldir = '/'.join([caseCFDdir, 'MaskToStl'])
            caseMeshCutdir = '/'.join([caseCFDdir, 'MeshCut'])
            caseMeshdir = '/'.join([caseCFDdir, 'Mesh'])
            caseFindFacedir = '/'.join([caseCFDdir, 'FindFace'])
            casetimefunctiondir = '/'.join([caseCFDdir, 'timefunction'])
            caseGenerateInputdir = '/'.join([caseCFDdir, 'GenerateInput'])
            caseresultdir = '/'.join([caseCFDdir, 'result'])
            casePostprocessingdir = '/'.join([casedir, 'CFDPostprocessing'])
            caseNpydir = '/'.join([casePostprocessingdir, 'Npy'])
            casepostNpydir = '/'.join([casePostprocessingdir, 'postNpy'])
            caseParaviewdir = '/'.join([casePostprocessingdir, 'Paraview'])
            caseVtudir = '/'.join([casePostprocessingdir, 'Vtu'])
            casesoliddir = '/'.join([casedir, 'solid'])
            caseWallMaskdir = '/'.join([casesoliddir, 'WallMask'])
            caseWallStldir = '/'.join([casesoliddir, 'WallStl'])
            caseWallSmoothdir = '/'.join([casesoliddir, 'WallSmooth'])
            caseWallStackLumendir = '/'.join([casesoliddir, 'WallStackLumen'])
            caseWallCutdir = '/'.join([casesoliddir, 'WallCut'])
            caseWallFillGapdir = '/'.join([casesoliddir, 'WallFillGap'])
            caseWallMeshdir = '/'.join([casesoliddir, 'WallMesh'])
            caseWallFindFacedir = '/'.join([casesoliddir, 'WallFindFace'])
            caseTissueCoodir = '/'.join([casesoliddir, 'TissueCoo'])
            caseTissueElemIddir = '/'.join([casesoliddir, 'TissueElemId'])
            casesolidGenerateInputdir = '/'.join([casesoliddir, 'GenerateInput'])
            caseNodeMatchingdir = '/'.join([casesoliddir, 'NodeMatching'])
            casesolidresultdir = '/'.join([casesoliddir, 'result'])
            casesolidPostprocessingdir = '/'.join([casedir, 'solidPostprocessing'])
            casesolidNpydir = '/'.join([casesolidPostprocessingdir, 'Npy'])
            casesolidVtudir = '/'.join([casesolidPostprocessingdir, 'Vtu'])

            # Create folder
            self.CreateFolder(casedir)
            self.CreateFolder(caseCFDdir)
            self.CreateFolder(caseLumenMaskdir)
            self.CreateFolder(caseMaskToStldir)
            self.CreateFolder(caseMeshCutdir)
            self.CreateFolder(caseMeshdir)
            self.CreateFolder(caseFindFacedir)
            self.CreateFolder(casetimefunctiondir)
            self.CreateFolder(caseGenerateInputdir)
            self.CreateFolder(caseresultdir)
            self.CreateFolder(casePostprocessingdir)
            self.CreateFolder(caseNpydir)
            self.CreateFolder(casepostNpydir)
            self.CreateFolder(caseParaviewdir)
            self.CreateFolder(caseVtudir)
            self.CreateFolder(casesoliddir)
            self.CreateFolder(caseWallMaskdir)
            self.CreateFolder(caseWallStldir)
            self.CreateFolder(caseWallSmoothdir)
            self.CreateFolder(caseWallStackLumendir)
            self.CreateFolder(caseWallCutdir)
            self.CreateFolder(caseWallFillGapdir)
            self.CreateFolder(caseWallMeshdir)
            self.CreateFolder(caseWallFindFacedir)
            self.CreateFolder(caseTissueCoodir)
            self.CreateFolder(caseTissueElemIddir)
            self.CreateFolder(casesolidGenerateInputdir)
            self.CreateFolder(caseNodeMatchingdir)
            self.CreateFolder(casesolidresultdir)
            self.CreateFolder(casesolidPostprocessingdir)
            self.CreateFolder(casesolidNpydir)
            self.CreateFolder(casesolidVtudir)

            # update parameter json
            if 'update parameter json' in ModulesChoosedict:
                if ModulesChoosedict['update parameter json']:
                    jsondict = {'ParameterInput': {}, 'CFD_FilterLumen': {}, 'CFD_MaskToStl': {}, 'CFD_MeshCut': {},
                                'CFD_Mesh': {}, 'CFD_FindFace': {}, 'CFD_GenerateInput': {}, 'CFD_DataOutput': {},
                                'CFD_PostNpy': {}, 'CFD_Paraview': {}, 'CFD_SaveVtu': {}, 'solid_WallMaskToStl': {},
                                'solid_WallSmooth': {}, 'solid_WallStackLumen': {}, 'solid_WallCut': {},
                                'solid_WallFillGap': {}, 'solid_WallMesh': {}, 'solid_WallFindFace': {},
                                'solid_TissueCoo': {}, 'solid_TissueElemId': {}, 'solid_GenerateInput': {},
                                'solid_NodeMatching': {}, 'solid_Npy': {}, 'solid_SaveVtu': {}}
                    if not self.Parameterdf.empty:
                        jsondict['ParameterInput'] = dict(zip(self.Parameterdf['parameter'], self.Parameterdf['value']))
                    if not CFD_FilterLumentabledfload.empty:
                        jsondict['CFD_FilterLumen'] = self.DfToDict(CFD_FilterLumentabledfload, casedir)
                    if not CFD_MaskToStltabledfload.empty:
                        jsondict['CFD_MaskToStl'] = self.DfToDict(CFD_MaskToStltabledfload, casedir)
                    if not CFD_MeshCuttabledfload.empty:
                        jsondict['CFD_MeshCut'] = self.DfToDict(CFD_MeshCuttabledfload, casedir)
                    if not CFD_Meshtabledfload.empty:
                        jsondict['CFD_Mesh'] = self.DfToDict(CFD_Meshtabledfload, casedir)
                    if not CFD_FindFacetabledfload.empty:
                        jsondict['CFD_FindFace'] = self.DfToDict(CFD_FindFacetabledfload, casedir)
                    if not CFD_GenerateInputtabledfload.empty:
                        jsondict['CFD_GenerateInput'] = self.DfToDict(CFD_GenerateInputtabledfload, casedir)
                    if not CFD_DataOutputtabledfload.empty:
                        jsondict['CFD_DataOutput'] = self.DfToDict(CFD_DataOutputtabledfload, casedir)
                    if not CFD_PostNpytabledfload.empty:
                        jsondict['CFD_PostNpy'] = self.DfToDict(CFD_PostNpytabledfload, casedir)
                    if not CFD_Paraviewtabledfload.empty:
                        jsondict['CFD_Paraview'] = self.DfToDict(CFD_Paraviewtabledfload, casedir)
                    if not CFD_SaveVtutabledfload.empty:
                        jsondict['CFD_SaveVtu'] = self.DfToDict(CFD_SaveVtutabledfload, casedir)
                    if not solid_WallMaskToStltabledfload.empty:
                        jsondict['solid_WallMaskToStl'] = self.DfToDict(solid_WallMaskToStltabledfload, casedir)
                    if not solid_WallSmoothtabledfload.empty:
                        jsondict['solid_WallSmooth'] = self.DfToDict(solid_WallSmoothtabledfload, casedir)
                    if not solid_WallStackLumentabledfload.empty:
                        jsondict['solid_WallStackLumen'] = self.DfToDict(solid_WallStackLumentabledfload, casedir)
                    if not solid_WallCuttabledfload.empty:
                        jsondict['solid_WallCut'] = self.DfToDict(solid_WallCuttabledfload, casedir)
                    if not solid_WallFillGaptabledfload.empty:
                        jsondict['solid_WallFillGap'] = self.DfToDict(solid_WallFillGaptabledfload, casedir)
                    if not solid_WallMeshtabledfload.empty:
                        jsondict['solid_WallMesh'] = self.DfToDict(solid_WallMeshtabledfload, casedir)
                    if not solid_WallFindFacetabledfload.empty:
                        jsondict['solid_WallFindFace'] = self.DfToDict(solid_WallFindFacetabledfload, casedir)
                    if not solid_TissueCootabledfload.empty:
                        jsondict['solid_TissueCoo'] = self.DfToDict(solid_TissueCootabledfload, casedir)
                    if not solid_TissueElemIdtabledfload.empty:
                        jsondict['solid_TissueElemId'] = self.DfToDict(solid_TissueElemIdtabledfload, casedir)
                    if not solid_GenerateInputtabledfload.empty:
                        jsondict['solid_GenerateInput'] = self.DfToDict(solid_GenerateInputtabledfload, casedir)
                    if not solid_NodeMatchingtabledfload.empty:
                        jsondict['solid_NodeMatching'] = self.DfToDict(solid_NodeMatchingtabledfload, casedir)
                    if not solid_Npytabledfload.empty:
                        jsondict['solid_Npy'] = self.DfToDict(solid_Npytabledfload, casedir)
                    if not solid_SaveVtutabledfload.empty:
                        jsondict['solid_SaveVtu'] = self.DfToDict(solid_SaveVtutabledfload, casedir)
                    # save
                    self.savejsondict(casejsonpath, jsondict)

            # load parameter from json
            parameterdict = {'ParameterInput': {}, 'CFD_FilterLumen': {}, 'CFD_MaskToStl': {}, 'CFD_MeshCut': {},
                             'CFD_Mesh': {}, 'CFD_FindFace': {}, 'CFD_GenerateInput': {}, 'CFD_DataOutput': {},
                             'CFD_PostNpy': {}, 'CFD_Paraview': {}, 'CFD_SaveVtu': {}, 'solid_WallMaskToStl': {},
                             'solid_WallSmooth': {}, 'solid_WallStackLumen': {}, 'solid_WallCut': {},
                             'solid_WallFillGap': {}, 'solid_WallMesh': {}, 'solid_WallFindFace': {},
                             'solid_TissueCoo': {}, 'solid_TissueElemId': {}, 'solid_GenerateInput': {},
                             'solid_NodeMatching': {}, 'solid_Npy': {}, 'solid_SaveVtu': {}}
            if not self.Parameterdf.empty:
                parameterdict['ParameterInput'] = dict(zip(self.Parameterdf['parameter'], self.Parameterdf['value']))
            if 'load parameter from json' in ModulesChoosedict:
                if ModulesChoosedict['load parameter from json']:
                    if os.path.exists(casejsonpath):
                        with open(casejsonpath) as f:
                            parameterdict = json.load(f)
            print('parameterdict', parameterdict)

            # copy reference table
            if 'Set(FindFace)' in parameterdict['ParameterInput']:
                if 'UpdateSet(FindFace)' in parameterdict['ParameterInput']:
                    if parameterdict['ParameterInput']['UpdateSet(FindFace)'] == True:
                        self.CopyFile(parameterdict['ParameterInput']['Set(FindFace)'], caseFindFacedir + '/set.csv')
                if not os.path.exists(caseFindFacedir + '/set.csv'):
                    self.CopyFile(parameterdict['ParameterInput']['Set(FindFace)'], caseFindFacedir + '/set.csv')
            if 'TimeStep(GenerateInput)' in parameterdict['ParameterInput']:
                if 'UpdateTimeStep(FindFace)' in parameterdict['ParameterInput']:
                    if parameterdict['ParameterInput']['UpdateTimeStep(FindFace)'] == True:
                        self.CopyFile(parameterdict['ParameterInput']['TimeStep(GenerateInput)'],
                                      caseGenerateInputdir + '/TimeStep.csv')
                if not os.path.exists(caseGenerateInputdir + '/TimeStep.csv'):
                    self.CopyFile(parameterdict['ParameterInput']['TimeStep(GenerateInput)'],
                                  caseGenerateInputdir + '/TimeStep.csv')
            if 'TimeFunction(GenerateInput)' in parameterdict['ParameterInput']:
                if 'UpdateTimeFunction(GenerateInput)' in parameterdict['ParameterInput']:
                    if parameterdict['ParameterInput']['UpdateTimeFunction(GenerateInput)'] == True:
                        for root, dirs, files in os.walk(
                                parameterdict['ParameterInput']['TimeFunction(GenerateInput)']):
                            for file in files:
                                self.CopyFile(root + '/' + file, casetimefunctiondir + '/' + file)
                if len(os.listdir(casetimefunctiondir)) == 0:
                    for root, dirs, files in os.walk(parameterdict['ParameterInput']['TimeFunction(GenerateInput)']):
                        for file in files:
                            self.CopyFile(root + '/' + file, casetimefunctiondir + '/' + file)
            if 'Set_solid(FindFace)' in parameterdict['ParameterInput']:
                if 'UpdateSet_solid(FindFace)' in parameterdict['ParameterInput']:
                    if parameterdict['ParameterInput']['UpdateSet_solid(FindFace)'] == True:
                        self.CopyFile(parameterdict['ParameterInput']['Set_solid(FindFace)'],
                                      caseWallFindFacedir + '/set_solid.csv')
                if not os.path.exists(caseWallFindFacedir + '/set_solid.csv'):
                    self.CopyFile(parameterdict['ParameterInput']['Set_solid(FindFace)'],
                                  caseWallFindFacedir + '/set_solid.csv')

            # update CFD_FilterLumentable
            self.CFD_FilterLumentabledf.loc[i, 'MaskPath'] = '/'.join([casedir, 'Mask.nii.gz'])
            self.CFD_FilterLumentabledf.loc[i, 'MaskVal'] = 1
            self.CFD_FilterLumentabledf.loc[i, 'NewMaskVal'] = 1
            self.CFD_FilterLumentabledf.loc[i, 'OutputFolder'] = caseLumenMaskdir
            self.CFD_FilterLumentabledf.loc[i, 'FileNameRef'] = 'Lumen'
            for key, value in parameterdict['CFD_FilterLumen'].items():
                self.CFD_FilterLumentabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_FilterLumentabledf.loc[i, key] = casedir + value

            # update CFD_MaskToStltable
            if 'STL Generate Exe Path' in parameterdict['ParameterInput']:
                self.CFD_MaskToStltabledf.loc[i, 'EXEPath'] = parameterdict['ParameterInput']['STL Generate Exe Path']
            self.CFD_MaskToStltabledf.loc[i, 'InputFilePath'] = '/'.join([caseLumenMaskdir, 'LumenVal.nii.gz'])
            self.CFD_MaskToStltabledf.loc[i, 'OutputFilePath'] = '/'.join([caseMaskToStldir, 'RawData.stl'])
            for key, value in parameterdict['CFD_MaskToStl'].items():
                self.CFD_MaskToStltabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_MaskToStltabledf.loc[i, key] = casedir + value

            # update CFD_MeshCuttable
            self.CFD_MeshCuttabledf.loc[i, 'MeshCut'] = True
            self.CFD_MeshCuttabledf.loc[i, 'InputStl(MeshCut)'] = '/'.join([caseMaskToStldir, 'RawData.stl'])
            self.CFD_MeshCuttabledf.loc[i, 'OutputFolder(MeshCut)'] = caseMeshCutdir
            for key, value in parameterdict['CFD_MeshCut'].items():
                self.CFD_MeshCuttabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_MeshCuttabledf.loc[i, key] = casedir + value

            # update CFD_Meshtabledf
            self.CFD_Meshtabledf.loc[i, 'Mesh'] = True
            self.CFD_Meshtabledf.loc[i, 'InputStl(Mesh)'] = '/'.join([caseMeshCutdir, 'lumenCut.stl'])
            if 'Mesh Exe Path' in parameterdict['ParameterInput']:
                self.CFD_Meshtabledf.loc[i, 'MeshExe'] = parameterdict['ParameterInput']['Mesh Exe Path']
            self.CFD_Meshtabledf.loc[i, 'OutputFolder(Mesh)'] = caseMeshdir
            for key, value in parameterdict['CFD_Mesh'].items():
                self.CFD_Meshtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_Meshtabledf.loc[i, key] = casedir + value

            # update CFD_FindFacetabledf
            self.CFD_FindFacetabledf.loc[i, 'FindFace'] = True
            self.CFD_FindFacetabledf.loc[i, 'InputNas(FindFace)'] = '/'.join([caseMeshdir, 'FluidMeshInit.nas'])
            self.CFD_FindFacetabledf.loc[i, 'OutputFolder(FindFace)'] = caseFindFacedir
            self.CFD_FindFacetabledf.loc[i, 'Set(FindFace)'] = '/'.join([caseFindFacedir, 'set.csv'])
            self.CFD_FindFacetabledf.loc[i, 'Tolerance(FindFace)'] = 45
            if 'Tolerance(FindFace)' in parameterdict['ParameterInput']:
                self.CFD_FindFacetabledf.loc[i, 'Tolerance(FindFace)'] = parameterdict[
                    'ParameterInput']['Tolerance(FindFace)']
            for key, value in parameterdict['CFD_FindFace'].items():
                self.CFD_FindFacetabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_FindFacetabledf.loc[i, key] = casedir + value

            # update CFD_GenerateInputtabledf
            self.CFD_GenerateInputtabledf.loc[i, 'GenerateInput'] = True
            self.CFD_GenerateInputtabledf.loc[i, 'InputNas(GenerateInput)'] = '/'.join([caseFindFacedir, 'CFD.nas'])
            self.CFD_GenerateInputtabledf.loc[i, 'OutputFolder(GenerateInput)'] = caseGenerateInputdir
            self.CFD_GenerateInputtabledf.loc[i, 'TimeFunction(GenerateInput)'] = casetimefunctiondir
            self.CFD_GenerateInputtabledf.loc[i, 'EndingArea(GenerateInput)'] = '/'.join([caseFindFacedir, 'area.csv'])
            if 'AUI Path' in parameterdict['ParameterInput']:
                self.CFD_GenerateInputtabledf.loc[i, 'AUIPath'] = parameterdict['ParameterInput']['AUI Path']
            self.CFD_GenerateInputtabledf.loc[i, 'TimeStep(GenerateInput)'] = '/'.join([
                caseGenerateInputdir, 'TimeStep.csv'])
            self.CFD_GenerateInputtabledf.loc[i, 'CompIfoPath(GenerateInput)'] = '/'.join([
                caseFindFacedir, 'CompIfo.csv'])
            for key, value in parameterdict['CFD_GenerateInput'].items():
                self.CFD_GenerateInputtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_GenerateInputtabledf.loc[i, key] = casedir + value

            # update CFD_DataOutputtabledf
            self.CFD_DataOutputtabledf.loc[i, 'DataOutput'] = True
            self.CFD_DataOutputtabledf.loc[i, 'Idb Path(DataOutput)'] = '/'.join([caseGenerateInputdir, 'CFD.idb'])
            self.CFD_DataOutputtabledf.loc[i, 'Por Path(DataOutput)'] = '/'.join([caseresultdir, 'CFD.por'])
            self.CFD_DataOutputtabledf.loc[i, 'OutputFolder(DataOutput)'] = caseNpydir
            if 'AUI Path' in parameterdict['ParameterInput']:
                self.CFD_DataOutputtabledf.loc[i, 'AUI Path(DataOutput)'] = parameterdict['ParameterInput']['AUI Path']
            self.CFD_DataOutputtabledf.loc[i, 'TimeStart(DataOutput)'] = 1.6
            self.CFD_DataOutputtabledf.loc[i, 'TimeStop(DataOutput)'] = 2.4
            for key, value in parameterdict['CFD_DataOutput'].items():
                self.CFD_DataOutputtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_DataOutputtabledf.loc[i, key] = casedir + value

            # update CFD_PostNpytabledf
            self.CFD_PostNpytabledf.loc[i, 'CFD Post-processing'] = True
            self.CFD_PostNpytabledf.loc[i, 'InputFolder(CFD Post-processing)'] = caseNpydir
            self.CFD_PostNpytabledf.loc[i, 'OutputFolder(CFD Post-processing)'] = casepostNpydir
            self.CFD_PostNpytabledf.loc[i, 'TimeStart(CFD Post-processing)'] = 1.6
            self.CFD_PostNpytabledf.loc[i, 'TimeStop(CFD Post-processing)'] = 2.4
            for key, value in parameterdict['CFD_PostNpy'].items():
                self.CFD_PostNpytabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_PostNpytabledf.loc[i, key] = casedir + value

            # update CFD_Paraviewtabledf
            self.CFD_Paraviewtabledf.loc[i, 'Paraview_processing'] = True
            self.CFD_Paraviewtabledf.loc[i, 'Nodecoo(Paraview_processing)'] = '/'.join([
                caseNpydir, 'Fluid_Nodecoo_Dic.npy'])
            self.CFD_Paraviewtabledf.loc[i, 'TetraElmnt(Paraview_processing)'] = '/'.join([
                caseNpydir, 'Fluid_TetraElmnt_NdIfo_Dic.npy'])
            self.CFD_Paraviewtabledf.loc[i, 'HexElmnt(Paraview_processing)'] = '/'.join([
                caseNpydir, 'Fluid_HexElmnt_NdIfo_Dic.npy'])
            self.CFD_Paraviewtabledf.loc[i, 'Times(Paraview_processing)'] = '/'.join([
                caseNpydir, 'Fluid_Times_Dic.npy'])
            self.CFD_Paraviewtabledf.loc[i, 'ParamsDic(Paraview_processing)'] = '/'.join([
                caseNpydir, 'Fluid_lst_ParamsDic.npy'])
            self.CFD_Paraviewtabledf.loc[i, 'PostResults(Paraview_processing)'] = '/'.join([
                casepostNpydir, 'fluid_PostResults_Dict_dict.npy'])
            self.CFD_Paraviewtabledf.loc[i, 'WSSParamDict(Paraview_processing)'] = '/'.join([
                casepostNpydir, 'fluid_TimeAvePressureDict_dict.npy'])
            self.CFD_Paraviewtabledf.loc[i, 'WssDict(Paraview_processing)'] = '/'.join([
                casepostNpydir, 'fluid_PostResults_WssDict_dict.npy'])
            self.CFD_Paraviewtabledf.loc[i, 'FFRIQRAverageValue(Paraview_processing)'] = ''
            self.CFD_Paraviewtabledf.loc[i, 'OutputFolder(Paraview_processing)'] = caseParaviewdir
            for key, value in parameterdict['CFD_PostNpy'].items():
                self.CFD_Paraviewtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_Paraviewtabledf.loc[i, key] = casedir + value

            # update CFD_SaveVtutabledf
            self.CFD_SaveVtutabledf.loc[i, 'Savevtu'] = True
            self.CFD_SaveVtutabledf.loc[i, 'OutputFolder(Savevtu)'] = caseVtudir
            self.CFD_SaveVtutabledf.loc[i, 'nasPath(Savevtu)'] = '/'.join([caseFindFacedir, '3Dmesh.nas'])
            self.CFD_SaveVtutabledf.loc[i, 'ndInterestDictPath(Savevtu)'] = '/'.join([
                casepostNpydir, 'ndInterestDict_dict.npy'])
            self.CFD_SaveVtutabledf.loc[i, 'ParamsNpyPath(Savevtu)'] = casepostNpydir
            self.CFD_SaveVtutabledf.loc[i, 'savevtuName(Savevtu)'] = 'CFDresult'
            self.CFD_SaveVtutabledf.loc[i, 'addFFR(Savevtu)'] = False
            self.CFD_SaveVtutabledf.loc[i, 'savesingle(Savevtu)'] = False
            self.CFD_SaveVtutabledf.loc[i, 'ParamsPath(Savevtu)'] = '/'.join([caseNpydir, 'Fluid_lst_ParamsDic.npy'])
            self.CFD_SaveVtutabledf.loc[i, 'pvdName(Savevtu)'] = 'CFDresult'
            self.CFD_SaveVtutabledf.loc[i, 'SavePVD(Savevtu)'] = True
            self.CFD_SaveVtutabledf.loc[i, 'SaveFFRvtu(Savevtu)'] = False
            self.CFD_SaveVtutabledf.loc[i, 'Savevtufile(Savevtu)'] = True
            for key, value in parameterdict['CFD_SaveVtu'].items():
                self.CFD_SaveVtutabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.CFD_SaveVtutabledf.loc[i, key] = casedir + value

            # update solid_WallMaskToStltabledf
            if 'STL Generate Exe Path' in parameterdict['ParameterInput']:
                self.solid_WallMaskToStltabledf.loc[i, 'EXEPath'] = parameterdict[
                    'ParameterInput']['STL Generate Exe Path']
            self.solid_WallMaskToStltabledf.loc[i, 'InputFilePath'] = '/'.join([caseWallMaskdir, 'WallVal.nii.gz'])
            self.solid_WallMaskToStltabledf.loc[i, 'OutputFilePath'] = '/'.join([caseWallStldir, 'WallStl.stl'])
            for key, value in parameterdict['solid_WallMaskToStl'].items():
                self.solid_WallMaskToStltabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_WallMaskToStltabledf.loc[i, key] = casedir + value

            # update solid_WallSmoothtabledf
            self.solid_WallSmoothtabledf.loc[i, 'Mesh'] = True
            self.solid_WallSmoothtabledf.loc[i, 'InputStl(Mesh)'] = '/'.join([caseWallStldir, 'WallStl.stl'])
            if 'Mesh Exe Path' in parameterdict['ParameterInput']:
                self.solid_WallSmoothtabledf.loc[i, 'MeshExe'] = parameterdict['ParameterInput']['Mesh Exe Path']
            self.solid_WallSmoothtabledf.loc[i, 'OutputFolder(Mesh)'] = caseWallSmoothdir
            self.solid_WallSmoothtabledf.loc[i, 'Carotid(Mesh)'] = True
            self.solid_WallSmoothtabledf.loc[i, 'MeshSmooth(Mesh)'] = True
            self.solid_WallSmoothtabledf.loc[i, 'IterationsSmooth(Mesh)'] = 15
            self.solid_WallSmoothtabledf.loc[i, 'Relaxation(Mesh)'] = 0.5
            self.solid_WallSmoothtabledf.loc[i, 'Boundarysmoothing(Mesh)'] = 0
            self.solid_WallSmoothtabledf.loc[i, 'Normalize(Mesh)'] = 1
            self.solid_WallSmoothtabledf.loc[i, 'SmoothName(Mesh)'] = 'WallSmooth'
            self.solid_WallSmoothtabledf.loc[i, 'SurfaceClipper(Mesh)'] = False
            self.solid_WallSmoothtabledf.loc[i, 'FlowExtension(Mesh)'] = False
            self.solid_WallSmoothtabledf.loc[i, 'SurfaceRemesh(Mesh)'] = False
            self.solid_WallSmoothtabledf.loc[i, 'TetralMeshGeneration(Mesh)'] = False
            self.solid_WallSmoothtabledf.loc[i, 'ConvertMeshType(Mesh)'] = False
            for key, value in parameterdict['solid_WallSmooth'].items():
                self.solid_WallSmoothtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_WallSmoothtabledf.loc[i, key] = casedir + value

            # update solid_WallStackLumentabledf
            self.solid_WallStackLumentabledf.loc[i, 'InPath'] = '/'.join([caseWallSmoothdir, 'WallSmooth.stl'])
            self.solid_WallStackLumentabledf.loc[i, 'InPath2'] = '/'.join([caseFindFacedir, 'Lumen.stl'])
            self.solid_WallStackLumentabledf.loc[i, 'OutPath'] = '/'.join([caseWallStackLumendir, 'WallStack.stl'])
            for key, value in parameterdict['solid_WallStackLumen'].items():
                self.solid_WallStackLumentabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_WallStackLumentabledf.loc[i, key] = casedir + value

            # update solid_WallCuttabledf
            self.solid_WallCuttabledf.loc[i, 'MeshCut'] = True
            self.solid_WallCuttabledf.loc[i, 'InputStl(MeshCut)'] = '/'.join([caseWallStackLumendir, 'WallStack.stl'])
            self.solid_WallCuttabledf.loc[i, 'OutputFolder(MeshCut)'] = caseWallCutdir
            for key, value in parameterdict['solid_WallCut'].items():
                self.solid_WallCuttabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_WallCuttabledf.loc[i, key] = casedir + value

            # update solid_WallFillGaptabledf
            self.solid_WallFillGaptabledf.loc[i, 'MeshFillGap'] = True
            self.solid_WallFillGaptabledf.loc[i, 'InputStl(MeshFillGap)'] = '/'.join([caseWallCutdir, 'lumenCut.stl'])
            self.solid_WallFillGaptabledf.loc[i, 'OutputFolder(MeshFillGap)'] = '/'.join([
                caseWallFillGapdir, 'FillGap.stl'])
            self.solid_WallFillGaptabledf.loc[i, 'Connectivity(MeshFillGap)'] = True
            self.solid_WallFillGaptabledf.loc[i, 'ConnectivityFloder(MeshFillGap)'] = '/'.join([
                caseWallFillGapdir, 'FillGapConnectivity.stl'])
            for key, value in parameterdict['solid_WallFillGap'].items():
                self.solid_WallFillGaptabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_WallFillGaptabledf.loc[i, key] = casedir + value

            # update solid_WallMeshtabledf
            self.solid_WallMeshtabledf.loc[i, 'Mesh'] = True
            self.solid_WallMeshtabledf.loc[i, 'InputStl(Mesh)'] = '/'.join([
                caseWallFillGapdir, 'FillGapConnectivity.stl'])
            if 'Mesh Exe Path' in parameterdict['ParameterInput']:
                self.solid_WallMeshtabledf.loc[i, 'MeshExe'] = parameterdict['ParameterInput']['Mesh Exe Path']
            self.solid_WallMeshtabledf.loc[i, 'OutputFolder(Mesh)'] = caseWallMeshdir
            self.solid_WallMeshtabledf.loc[i, 'Carotid(Mesh)'] = True
            self.solid_WallMeshtabledf.loc[i, 'MeshSmooth(Mesh)'] = False
            self.solid_WallMeshtabledf.loc[i, 'SurfaceClipper(Mesh)'] = False
            self.solid_WallMeshtabledf.loc[i, 'FlowExtension(Mesh)'] = False
            self.solid_WallMeshtabledf.loc[i, 'SurfaceRemesh(Mesh)'] = False
            self.solid_WallMeshtabledf.loc[i, 'TetralMeshGeneration(Mesh)'] = True
            self.solid_WallMeshtabledf.loc[i, 'RadiousAdaptive(Mesh)'] = False
            self.solid_WallMeshtabledf.loc[i, 'EdgelengthMesh(Mesh)'] = 1
            self.solid_WallMeshtabledf.loc[i, 'EdgelengthFactorMesh(Mesh)'] = 0.3
            self.solid_WallMeshtabledf.loc[i, 'MinedgelengthMesh(Mesh)'] = 0.3
            self.solid_WallMeshtabledf.loc[i, 'MaxedgelengthMesh(Mesh)'] = 4
            self.solid_WallMeshtabledf.loc[i, 'BoundarylayerBool(Mesh)'] = 0
            self.solid_WallMeshtabledf.loc[i, 'Sublayers(Mesh)'] = 3
            self.solid_WallMeshtabledf.loc[i, 'Sublayerratio(Mesh)'] = 1.2
            self.solid_WallMeshtabledf.loc[i, 'skipremeshing(Mesh)'] = 1
            self.solid_WallMeshtabledf.loc[i, 'skipcapping(Mesh)'] = 1
            self.solid_WallMeshtabledf.loc[i, 'remeshcapsonly(Mesh)'] = 1
            self.solid_WallMeshtabledf.loc[i, 'FirstLayerThickness(Mesh)'] = 0.1
            self.solid_WallMeshtabledf.loc[i, 'BoundarylayeroncapsBool(Mesh)'] = 0
            self.solid_WallMeshtabledf.loc[i, 'MeshName(Mesh)'] = 'solid.vtu'
            self.solid_WallMeshtabledf.loc[i, 'ConvertMeshType(Mesh)'] = True
            self.solid_WallMeshtabledf.loc[i, 'ConvertMeshName(Mesh)'] = 'solid.nas'
            for key, value in parameterdict['solid_WallMesh'].items():
                self.solid_WallMeshtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_WallMeshtabledf.loc[i, key] = casedir + value

            # update solid_WallFindFacetabledf
            self.solid_WallFindFacetabledf.loc[i, 'FindFace'] = True
            self.solid_WallFindFacetabledf.loc[i, 'InputNas(FindFace)'] = '/'.join([caseWallMeshdir, 'solid.nas'])
            self.solid_WallFindFacetabledf.loc[i, 'OutputFolder(FindFace)'] = caseWallFindFacedir
            self.solid_WallFindFacetabledf.loc[i, 'Set(FindFace)'] = '/'.join([caseWallFindFacedir, 'set_solid.csv'])
            self.solid_WallFindFacetabledf.loc[i, 'Tolerance(FindFace)'] = 45
            for key, value in parameterdict['solid_WallFindFace'].items():
                self.solid_WallFindFacetabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_WallFindFacetabledf.loc[i, key] = casedir + value

            # update solid_TissueCootabledf
            self.solid_TissueCootabledf.loc[i, 'filePaths'] = '/'.join([caseWallMaskdir, 'WallVal.nii.gz'])
            self.solid_TissueCootabledf.loc[i, 'dirPaths'] = caseTissueCoodir
            for key, value in parameterdict['solid_TissueCoo'].items():
                self.solid_TissueCootabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_TissueCootabledf.loc[i, key] = casedir + value

            # update solid_TissueElemIdtabledf
            self.solid_TissueElemIdtabledf.loc[i, 'TissueElemAssign'] = True
            self.solid_TissueElemIdtabledf.loc[i, 'CooFolder(TissueElemAssign)'] = '/'.join([
                caseWallFindFacedir, '3Dmesh.nas'])
            self.solid_TissueElemIdtabledf.loc[i, 'NpyFolder(TissueElemAssign)'] = caseTissueCoodir
            self.solid_TissueElemIdtabledf.loc[i, 'OutputFolder(TissueElemAssign)'] = caseTissueElemIddir
            for key, value in parameterdict['solid_TissueElemId'].items():
                self.solid_TissueElemIdtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_TissueElemIdtabledf.loc[i, key] = casedir + value

            # update solid_GenerateInputtabledf
            self.solid_GenerateInputtabledf.loc[i, 'GenerateInput'] = True
            self.solid_GenerateInputtabledf.loc[i, 'CompIfoPath(GenerateInput)'] = '/'.join([
                caseWallFindFacedir, 'CompIfo.csv'])
            self.solid_GenerateInputtabledf.loc[i, 'InputNas(GenerateInput)'] = '/'.join([
                caseWallFindFacedir, 'CFD.nas'])
            self.solid_GenerateInputtabledf.loc[i, 'OutputFolder(GenerateInput)'] = casesolidGenerateInputdir
            self.solid_GenerateInputtabledf.loc[i, 'TissueElemIdPath(GenerateInput)'] = caseTissueElemIddir
            if 'AUI Path' in parameterdict['ParameterInput']:
                self.solid_GenerateInputtabledf.loc[i, 'AUIPath'] = parameterdict['ParameterInput']['AUI Path']
            self.solid_GenerateInputtabledf.loc[i, 'TimeStep(GenerateInput)'] = '/'.join([
                caseGenerateInputdir, 'TimeStep.csv'])
            for key, value in parameterdict['solid_GenerateInput'].items():
                self.solid_GenerateInputtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_GenerateInputtabledf.loc[i, key] = casedir + value

            # update solid_NodeMatchingtabledf
            self.solid_NodeMatchingtabledf.loc[i, 'NodeMatching'] = True
            self.solid_NodeMatchingtabledf.loc[i, 'solidin(NodeMatching)'] = '/'.join([
                casesolidGenerateInputdir, 'Wall.in'])
            self.solid_NodeMatchingtabledf.loc[i, 'SolidIdb(NodeMatching)'] = '/'.join([
                casesolidGenerateInputdir, 'Wall.idb'])
            self.solid_NodeMatchingtabledf.loc[i, 'SolidCompIfo(NodeMatching)'] = '/'.join([
                caseWallFindFacedir, 'CompIfo.csv'])
            self.solid_NodeMatchingtabledf.loc[i, 'Offesetvalue(NodeMatching)'] = 2
            self.solid_NodeMatchingtabledf.loc[i, 'GroupNum(NodeMatching)'] = 10
            self.solid_NodeMatchingtabledf.loc[i, 'fluidlumenset(NodeMatching)'] = 51
            self.solid_NodeMatchingtabledf.loc[i, 'PressureID(NodeMatching)'] = 90
            self.solid_NodeMatchingtabledf.loc[i, 'EleFaceSetPrefix(NodeMatching)'] = 99
            self.solid_NodeMatchingtabledf.loc[i, 'TimeFunctionPrefix(NodeMatching)'] = 9
            self.solid_NodeMatchingtabledf.loc[i, 'LoadPrefix(NodeMatching)'] = 1
            if 'AUI Path' in parameterdict['ParameterInput']:
                self.solid_NodeMatchingtabledf.loc[i, 'AUIPath'] = parameterdict['ParameterInput']['AUI Path']
            self.solid_NodeMatchingtabledf.loc[i, 'fluidIdb(NodeMatching)'] = '/'.join([
                caseGenerateInputdir, 'CFD.idb'])
            self.solid_NodeMatchingtabledf.loc[i, 'fluidPor(NodeMatching)'] = '/'.join([caseresultdir, 'CFD.por'])
            self.solid_NodeMatchingtabledf.loc[i, 'OutputFolder(NodeMatching)'] = caseNodeMatchingdir
            for key, value in parameterdict['solid_NodeMatching'].items():
                self.solid_NodeMatchingtabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_NodeMatchingtabledf.loc[i, key] = casedir + value

            # update solid_Npytabledf
            self.solid_Npytabledf.loc[i, 'OutputFolder(DataOutput)'] = casesolidNpydir
            self.solid_Npytabledf.loc[i, 'DataOutput'] = True
            self.solid_Npytabledf.loc[i, 'Fluid(DataOutput)'] = False
            self.solid_Npytabledf.loc[i, 'Idb Path(DataOutput)'] = '/'.join([casesolidGenerateInputdir, 'Wall.idb'])
            self.solid_Npytabledf.loc[i, 'Por Path(DataOutput)'] = '/'.join([casesolidresultdir, 'Wall.por'])
            if 'AUI Path' in parameterdict['ParameterInput']:
                self.solid_Npytabledf.loc[i, 'AUI Path(DataOutput)'] = parameterdict['ParameterInput']['AUI Path']
            self.solid_Npytabledf.loc[i, 'TimeStart(DataOutput)'] = 1.6
            self.solid_Npytabledf.loc[i, 'TimeStop(DataOutput)'] = 2.4
            for key, value in parameterdict['solid_Npy'].items():
                self.solid_Npytabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_Npytabledf.loc[i, key] = casedir + value

            # update solid_SaveVtutabledf
            self.solid_SaveVtutabledf.loc[i, 'OutputFolder(Savevtu)'] = casesolidVtudir
            self.solid_SaveVtutabledf.loc[i, 'Savevtu'] = True
            self.solid_SaveVtutabledf.loc[i, 'nasPath(Savevtu)'] = '/'.join([
                caseWallFindFacedir, '3Dmesh.nas'])
            self.solid_SaveVtutabledf.loc[i, 'ParamsPath(Savevtu)'] = '/'.join([
                casesolidNpydir, 'Solid_lst_ParamsDic.npy'])
            self.solid_SaveVtutabledf.loc[i, 'pvdName(Savevtu)'] = 'solid'
            self.solid_SaveVtutabledf.loc[i, 'Fluidpvd(Savevtu)'] = False
            self.solid_SaveVtutabledf.loc[i, 'Solidpvd(Savevtu)'] = True
            self.solid_SaveVtutabledf.loc[i, 'getSigmaP1(Savevtu)'] = True
            self.solid_SaveVtutabledf.loc[i, 'getEffectivestress(Savevtu)'] = True
            self.solid_SaveVtutabledf.loc[i, 'getSolidmaxshearstress(Savevtu)'] = True
            self.solid_SaveVtutabledf.loc[i, 'getSigmaNorm2(Savevtu)'] = True
            self.solid_SaveVtutabledf.loc[i, 'PVDbinary(Savevtu)'] = False
            self.solid_SaveVtutabledf.loc[i, 'SavePVD(Savevtu)'] = True
            self.solid_SaveVtutabledf.loc[i, 'SaveFFRvtu(Savevtu)'] = False
            self.solid_SaveVtutabledf.loc[i, 'Savevtufile(Savevtu)'] = False
            for key, value in parameterdict['solid_SaveVtu'].items():
                self.solid_SaveVtutabledf.loc[i, key] = value
                if type(value) == str:
                    if value.startswith('/'):
                        self.solid_SaveVtutabledf.loc[i, key] = casedir + value

            self.CopyFile('/'.join([casedir, 'Mask.nii.gz']), '/'.join([caseWallMaskdir, 'WallVal.nii.gz']))

        if 'Generate Table' in ModulesChoosedict:
            if ModulesChoosedict['Generate Table']:
                self.CFD_FilterLumentabledf.to_csv(CFD_FilterLumentablepath, index=None)
                self.CFD_MaskToStltabledf.to_csv(CFD_MaskToStltablepath, index=None)
                self.CFD_MeshCuttabledf.to_csv(CFD_MeshCuttablepath, index=None)
                self.CFD_Meshtabledf.to_csv(CFD_Meshtablepath, index=None)
                self.CFD_FindFacetabledf.to_csv(CFD_FindFacetablepath, index=None)
                self.CFD_GenerateInputtabledf.to_csv(CFD_GenerateInputtablepath, index=None)
                self.CFD_DataOutputtabledf.to_csv(CFD_DataOutputtablepath, index=None)
                self.CFD_PostNpytabledf.to_csv(CFD_PostNpytablepath, index=None)
                self.CFD_Paraviewtabledf.to_csv(CFD_Paraviewtablepath, index=None)
                self.CFD_SaveVtutabledf.to_csv(CFD_SaveVtutablepath, index=None)
                self.solid_WallMaskToStltabledf.to_csv(solid_WallMaskToStltablepath, index=None)
                self.solid_WallSmoothtabledf.to_csv(solid_WallSmoothtablepath, index=None)
                self.solid_WallStackLumentabledf.to_csv(solid_WallStackLumentablepath, index=None)
                self.solid_WallCuttabledf.to_csv(solid_WallCuttablepath, index=None)
                self.solid_WallFillGaptabledf.to_csv(solid_WallFillGaptablepath, index=None)
                self.solid_WallMeshtabledf.to_csv(solid_WallMeshtablepath, index=None)
                self.solid_WallFindFacetabledf.to_csv(solid_WallFindFacetablepath, index=None)
                self.solid_TissueCootabledf.to_csv(solid_TissueCootablepath, index=None)
                self.solid_TissueElemIdtabledf.to_csv(solid_TissueElemIdtablepath, index=None)
                self.solid_GenerateInputtabledf.to_csv(solid_GenerateInputtablepath, index=None)
                self.solid_NodeMatchingtabledf.to_csv(solid_NodeMatchingtablepath, index=None)
                self.solid_Npytabledf.to_csv(solid_Npytablepath, index=None)
                self.solid_SaveVtutabledf.to_csv(solid_SaveVtutablepath, index=None)
        if 'Filter Mask' in ModulesChoosedict:
            if ModulesChoosedict['Filter Mask']:
                self.model.filterMask.BatchProcessing(CFD_FilterLumentablepath)
        if 'Mask to Stl' in ModulesChoosedict:
            if ModulesChoosedict['Mask to Stl']:
                self.model.maskSTL.BatchConvert(CSVPath=CFD_MaskToStltablepath, choice=3)
        if 'Mesh Cut' in ModulesChoosedict:
            if ModulesChoosedict['Mesh Cut']:
                self.model.MeshCut.batchrun(CSVPath=CFD_MeshCuttablepath)
        if 'Mesh' in ModulesChoosedict:
            if ModulesChoosedict['Mesh']:
                self.model.Meshgeneration.batchrun(CSVPath=CFD_Meshtablepath)
        if 'Find Face' in ModulesChoosedict:
            if ModulesChoosedict['Find Face']:
                self.model.SplitFaceElem.batchrun(CSVPath=CFD_FindFacetablepath)
        if 'Generate Input' in ModulesChoosedict:
            if ModulesChoosedict['Generate Input']:
                self.model.Finfilegneration.batchrun(CSVPath=CFD_GenerateInputtablepath)
        if 'Data Output' in ModulesChoosedict:
            if ModulesChoosedict['Data Output']:
                self.model.adina_DataOutput.batchrun(CSVPath=CFD_DataOutputtablepath)
        if 'Post Npy' in ModulesChoosedict:
            if ModulesChoosedict['Post Npy']:
                self.model.CFDParameters.batchrun(CSVPath=CFD_PostNpytablepath)
        if 'Paraview Save' in ModulesChoosedict:
            if ModulesChoosedict['Paraview Save']:
                self.model.ParaviewPostProcessing.batchrun(CSVPath=CFD_Paraviewtablepath)
        if 'Save Vtu' in ModulesChoosedict:
            if ModulesChoosedict['Save Vtu']:
                self.model.SaveVTU.batchrun(CSVPath=CFD_SaveVtutablepath)
        if 'solid_WallMaskToStl' in ModulesChoosedict:
            if ModulesChoosedict['solid_WallMaskToStl']:
                self.model.maskSTL.BatchConvert(CSVPath=solid_WallMaskToStltablepath, choice=3)
        if 'solid_WallSmooth' in ModulesChoosedict:
            if ModulesChoosedict['solid_WallSmooth']:
                self.model.Meshgeneration.batchrun(CSVPath=solid_WallSmoothtablepath)
        if 'solid_WallStackLumen' in ModulesChoosedict:
            if ModulesChoosedict['solid_WallStackLumen']:
                self.model.StackSTL.batchrun(CSVPath=solid_WallStackLumentablepath)
        if 'solid_WallCut' in ModulesChoosedict:
            if ModulesChoosedict['solid_WallCut']:
                self.model.MeshCut.batchrun(CSVPath=solid_WallCuttablepath)
        if 'solid_WallFillGap' in ModulesChoosedict:
            if ModulesChoosedict['solid_WallFillGap']:
                self.model.MeshFillGap.batchrun(CSVPath=solid_WallFillGaptablepath)
        if 'solid_WallMesh' in ModulesChoosedict:
            if ModulesChoosedict['solid_WallMesh']:
                self.model.Meshgeneration.batchrun(CSVPath=solid_WallMeshtablepath)
        if 'solid_WallFindFace' in ModulesChoosedict:
            if ModulesChoosedict['solid_WallFindFace']:
                self.model.SplitFaceElem.batchrun(CSVPath=solid_WallFindFacetablepath)
        if 'solid_TissueCoo' in ModulesChoosedict:
            if ModulesChoosedict['solid_TissueCoo']:
                self.model.extractPointCoords.BatchExtract(CSVPath=solid_TissueCootablepath)
        if 'solid_TissueElemId' in ModulesChoosedict:
            if ModulesChoosedict['solid_TissueElemId']:
                self.model.TissueElemAssign.batchrun(CSVPath=solid_TissueElemIdtablepath)
        if 'solid_GenerateInput' in ModulesChoosedict:
            if ModulesChoosedict['solid_GenerateInput']:
                self.model.Finfilegneration.batchsolidrun(CSVPath=solid_GenerateInputtablepath)
        if 'solid_NodeMatching' in ModulesChoosedict:
            if ModulesChoosedict['solid_NodeMatching']:
                self.model.NodeMatching.batchrun(CSVPath=solid_NodeMatchingtablepath)
        if 'solid_Npy' in ModulesChoosedict:
            if ModulesChoosedict['solid_Npy']:
                self.model.adina_DataOutput.batchrun(CSVPath=solid_Npytablepath)
        if 'solid_SaveVtu' in ModulesChoosedict:
            if ModulesChoosedict['solid_SaveVtu']:
                self.model.SaveVTU.batchrun(CSVPath=solid_SaveVtutablepath)
        if self.modelui:
            self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)