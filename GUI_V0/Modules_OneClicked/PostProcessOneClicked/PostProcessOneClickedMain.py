import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_AZ')
sys.path.insert(0, '../Functions_JZ')
import pdfunction
import Save_Load_File

import re
import time
import numpy as np

class PostProcessOneClicked():
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.PushButton_CSV_PPOC_Z.clicked.connect(lambda: self.batchprogresscsv())
        self.ui.PushButton_run_PPOC_Z.clicked.connect(lambda: self.batchProgress())

        self.mudule = Hedys

    def batchprogresscsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui,qtObj=True)
        # set filename
        self.ui.TextEdit_CSV_PPOC_Z.setPlainText('{}'.format(filename))

    def batchProgress(self):
        inpath = self.ui.TextEdit_CSV_PPOC_Z.toPlainText()
        self.ui.plainTextEdit_BatchTable_DatO.setPlainText('{}'.format(inpath))
        self.ui.plainTextEdit_BatchTable_CFDP.setPlainText('{}'.format(inpath))
        self.ui.batchTablePathTxt_MR.setPlainText('{}'.format(inpath))
        self.ui.plainTextEdit_BatchTable_FFR.setPlainText('{}'.format(inpath))
        self.ui.plainTextEdit_BatchTable_PP.setPlainText('{}'.format(inpath))
        self.ui.plainTextEdit_BatchTable_SVZ.setPlainText('{}'.format(inpath))
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')
            try:
                OutputFloder = info["OutputFolder"]
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
            except:
                pass
        self.mudule.adina_DataOutput.batchrun()
        self.mudule.CFDParameters.batchrun()
        try:
            self.mudule.mapResults.Batch()
        except:
            pass
        self.mudule.FFR.batchrun()
        self.mudule.ParaviewPostProcessing.batchrun()
        self.mudule.SaveVTU.batchrun()

        #     DataOutput = False
        #     CFD_Post_processing = False
        #     MapResults = False
        #     FFRCalculation = False
        #     Paraview_processing = False
        #     Savevtu = False
        #
        #     try:
        #         if info["DataOutput"]:
        #             DataOutput = info["DataOutput"]
        #     except:
        #         pass
        #     try:
        #         if info["CFD Post-processing"]:
        #             CFD_Post_processing = info["CFD Post-processing"]
        #     except:
        #         pass
        #     try:
        #         if info["MapResults"]:
        #             MapResults = info["MapResults"]
        #     except:
        #         pass
        #     try:
        #         if info["FFRCalculation"]:
        #             FFRCalculation = info["FFRCalculation"]
        #     except:
        #         pass
        #     try:
        #         if info["Paraview_processing"]:
        #             Paraview_processing = info["Paraview_processing"]
        #     except:
        #         pass
        #     try:
        #         if info["Savevtu"]:
        #             Savevtu = info["Savevtu"]
        #     except:
        #         pass
        #     print('OutputFloder', OutputFloder)
        #     print('DataOutput',DataOutput)
        #     print('CFD_Post_processing',CFD_Post_processing)
        #     print('MapResults',MapResults)
        #     print('FFRCalculation',FFRCalculation)
        #     print('Paraview_processing', Paraview_processing)
        #     print('Savevtu', Savevtu)
        #
        #     # ##################### DataOutput
        #     if DataOutput:
                # # change inputfloder and outputfloder
                # OutputFloder = info["OutputFolder"] + '/Npy'
                # print('DataOutput OutputFloder=', OutputFloder)
                # DataOutputPORFloder = ''
                # DataOutputIDBFloder = ''
                # TimeStart = ''
                # TimeStop = ''
                # AUIFloder = ''
                # try:
                #     if info["Idb Path(DataOutput)"]:
                #         DataOutputIDBFloder = info["Idb Path(DataOutput)"]
                # except:
                #     pass
                # try:
                #     if info["Por Path(DataOutput)"]:
                #         DataOutputPORFloder = info["Por Path(DataOutput)"]
                # except:
                #     pass
                # try:
                #     if info["TimeStart(DataOutput)"]:
                #         TimeStart = info["TimeStart(DataOutput)"]
                # except:
                #     pass
                # try:
                #     if info["TimeStop(DataOutput)"]:
                #         TimeStop = info["TimeStop(DataOutput)"]
                # except:
                #     pass
                # try:
                #     if info["AUI Path(DataOutput)"]:
                #         AUIFloder = info["AUI Path(DataOutput)"]
                # except:
                #     pass
                # # make dir
                # if not os.path.exists(OutputFloder):
                #     os.mkdir(OutputFloder)
                # # change tab
                # self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.DateOutput)
                # # set ui
                # if DataOutputIDBFloder:
                #     self.ui.SolidRdBtn.setChecked(True)
                #     if DataOutputPORFloder:
                #         self.ui.FluidRdBtn.setChecked(True)
                #         self.ui.plainTextEdit_DatO.setPlainText('{}\n{}'.format(DataOutputPORFloder,DataOutputIDBFloder))
                #     else:
                #         self.ui.plainTextEdit_DatO.setPlainText('{}'.format(DataOutputIDBFloder))
                # if TimeStart:
                #     self.ui.lineEdit_TimeStartDatO.setText('{}'.format(TimeStart))
                # if TimeStop:
                #     self.ui.lineEdit_TimeEndDatO.setText('{}'.format(TimeStop))
                # self.ui.plainTextEdit_DatO3.setPlainText('{}/'.format(OutputFloder))
                # if AUIFloder:
                #     self.ui.plainTextEdit_DatO2.setPlainText('{}'.format(AUIFloder))
                # name = re.findall('.+/(.+)\.idb',self.ui.plainTextEdit_DatO.toPlainText())
                # self.ui.plainTextEdit_DatO4.setPlainText('{0}/{1}.eno\n{0}/{1}.coo\n{0}/{1}.nos\n{0}/{1}.lst\n{0}/{1}.str\n{0}/{1}.elf'.format(OutputFloder,name[-1]))
                # # Touched function
                # self.mudule.adina_DataOutput.Choose_AnalysisType()
                # self.mudule.adina_DataOutput.LoadIdbPorFile()
                # self.mudule.adina_DataOutput.TimeRange()
                # self.mudule.adina_DataOutput.GenertPloFile()
                # self.mudule.adina_DataOutput.Loading_PloFile()
                # self.mudule.adina_DataOutput.GetResultParamsMAT()
                # self.mudule.adina_DataOutput.InitDataOutput()
                # kill AUI.exe
                # os.system('taskkill /f /im AUI.exe')

            # if CFD_Post_processing:
                # postprocessinginputfloder = ''
                # TimeStart = ''
                # TimeStop = ''
                # TimeFile = ''
                # HexaElementFile = ''
                # TetraElementFile = ''
                # NodeCoordinateFile = ''
                # ElementFaceGroupFile = ''
                # StressTimeFile = ''
                # ListTimeFile = ''
                # FaceSetRef = ''
                # FaceSetNumber = ''
                # if DataOutput:
                #     # change inputfloder and outputfloder
                #     postprocessinginputfloder = info["OutputFolder"] + '/Npy'
                # try:
                #     if info["InputFolder(CFD Post-processing)"]:
                #         postprocessinginputfloder = info["InputFolder(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["TimeStart(CFD Post-processing)"]:
                #         TimeStart = info["TimeStart(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["TimeStop(CFD Post-processing)"]:
                #         TimeStop = info["TimeStop(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["TimeFile(CFD Post-processing)"]:
                #         TimeFile = info["TimeFile(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["HexaElementFile(CFD Post-processing)"]:
                #         HexaElementFile = info["HexaElementFile(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["TetraElementFile(CFD Post-processing)"]:
                #         TetraElementFile = info["TetraElementFile(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["NodeCoordinateFile(CFD Post-processing)"]:
                #         NodeCoordinateFile = info["NodeCoordinateFile(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["ElementFaceGroupFile(CFD Post-processing)"]:
                #         ElementFaceGroupFile = info["ElementFaceGroupFile(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["StressTimeFile(CFD Post-processing)"]:
                #         StressTimeFile = info["StressTimeFile(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["ListTimeFile(CFD Post-processing)"]:
                #         ListTimeFile = info["ListTimeFile(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["FaceSetRef(CFD Post-processing)"]:
                #         FaceSetRef = info["FaceSetRef(CFD Post-processing)"]
                # except:
                #     pass
                # try:
                #     if info["FaceSetNumber(CFD Post-processing)"]:
                #         FaceSetNumber = info["FaceSetNumber(CFD Post-processing)"]
                # except:
                #     pass
                # OutputFloder = info["OutputFolder"] + '/PostNpy'
                # print('CFD_Post_processing InputFloder=', postprocessinginputfloder)
                # print('CFD_Post_processing OutputFloder=', OutputFloder)
                # # make dir
                # if not os.path.exists(OutputFloder):
                #     os.mkdir(OutputFloder)
                # # change tab
                # self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.PostProcessing)
                # # set ui
                # self.ui.loadDirPathTxt_CFDP.setPlainText('{}'.format(postprocessinginputfloder))
                # if TimeStart:
                #     self.ui.timeStartLineTxt_CFDP.setText('{}'.format(TimeStart))
                # if TimeStop:
                #     self.ui.timeStopLineTxt_CFDP.setText('{}'.format(TimeStop))
                # if TimeFile:
                #     self.ui.timeLineTxt_CFDP.setText('{}'.format(TimeFile))
                # if HexaElementFile:
                #     self.ui.hexaElemLineTxt_CFDP.setText('{}'.format(HexaElementFile))
                # if TetraElementFile:
                #     self.ui.tetraElemLineTxt_CFDP.setText('{}'.format(TetraElementFile))
                # if NodeCoordinateFile:
                #     self.ui.ndCooLineTxt_CFDP.setText('{}'.format(NodeCoordinateFile))
                # if ElementFaceGroupFile:
                #     self.ui.elfElemGrpLineTxt_CFDP.setText('{}'.format(ElementFaceGroupFile))
                # if StressTimeFile:
                #     self.ui.timeStrsLineTxt_CFDP.setText('{}'.format(StressTimeFile))
                # if ListTimeFile:
                #     self.ui.timeLstLineTxt_CFDP.setText('{}'.format(ListTimeFile))
                # if FaceSetRef:
                #     self.ui.faceSetLineTxt_CFDP.setText('{}'.format(FaceSetRef))
                # if FaceSetNumber:
                #     self.ui.faceSetNumberLineTxt_CFDP.setText('{}'.format(FaceSetNumber))
                # self.ui.saveDirPathTxt_CFDP.setPlainText('{}'.format(OutputFloder))
                # # Touched function
                # self.mudule.CFDParameters.LoadFile()
                # self.mudule.CFDParameters.CalcSave()
                # self.mudule.CFDParameters.InitCFDParameters()

            # if MapResults:
                # InputFloder = ''
                # Npynames = ''
                # CTMasknames = ''
                # MapResultsInputMask = ''
                # ExtractSkin = False
                # ExcludingLabels = ''
                # Filterzeros = True
                # Radius = ''
                # NearestNeighbourLeafSize = ''
                # Processors = ''
                # # change inputfloder and outputfloder
                # if CFD_Post_processing:
                #     InputFloder = info["OutputFolder"] + '/PostNpy'
                # try:
                #     if info["Mask Path(MapResults)"]:
                #         MapResultsInputMask = info["Mask Path(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["InputFolder(MapResults)"]:
                #         InputFloder = info["InputFolder(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["Npy Names(MapResults)"]:
                #         Npynames = info["Npy Names(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["CT Mask Names(MapResults)"]:
                #         CTMasknames = info["CT Mask Names(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["Extract Skin(MapResults)"]:
                #         ExtractSkin = info["Extract Skin(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["Excluding Labels(MapResults)"]:
                #         ExcludingLabels = info["Excluding Labels(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["Filter zeros(MapResults)"]:
                #         Filterzeros = info["Filter zeros(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["Radius(MapResults)"]:
                #         Radius = info["Radius(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["Nearest Neighbour Leaf Size(MapResults)"]:
                #         NearestNeighbourLeafSize = info["Nearest Neighbour Leaf Size(MapResults)"]
                # except:
                #     pass
                # try:
                #     if info["Processors(MapResults)"]:
                #         Processors = info["Processors(MapResults)"]
                # except:
                #     pass
                # OutputFloder = info["OutputFolder"] + '/MapCT'
                # print('MapResults InputFloder=', InputFloder)
                # print('MapResults OutputFloder=', OutputFloder)
                # # make dir
                # if not os.path.exists(OutputFloder):
                #     os.mkdir(OutputFloder)
                # # change tab
                # self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.ResultsMapping)
                # # set ui
                # self.ui.loadDirPathTxt_MR.setPlainText('{}'.format(InputFloder))
                # self.ui.saveDirPathTxt_MR.setPlainText('{}'.format(OutputFloder))
                # self.ui.radioButton_137.setChecked(True)
                # if ExtractSkin:
                #     self.ui.radioButton_136.setChecked(True)
                # if ExcludingLabels:
                #     self.ui.radiusLineTxt_MR_4.setPlainText('{}'.format(ExcludingLabels))
                #
                # self.ui.radioButton_127.setChecked(True)
                # if Filterzeros:
                #     self.ui.radioButton_126.setChecked(True)
                # if Radius:
                #     self.ui.radiusLineTxt_MR.setPlainText('{}'.format(Radius))
                # if NearestNeighbourLeafSize:
                #     self.ui.leafSizeLineTxt_MR.setPlainText('{}'.format(NearestNeighbourLeafSize))
                # if Processors:
                #     self.ui.cpuLineTxt_MR.setPlainText('{}'.format(Processors))
                # if MapResultsInputMask:
                #     self.ui.loadImgPathTxt_MR.setPlainText('{}'.format(MapResultsInputMask))
                # if Npynames:
                #     self.ui.refNPYPathTxt_MR.setPlainText('{}'.format(Npynames))
                # if CTMasknames:
                #     self.ui.outImgPathTxt_MR.setPlainText('{}'.format(CTMasknames))
                # # Touched function
                # self.mudule.mapResults.Convert()
                # self.mudule.mapResults.InitMapResults()

            # if FFRCalculation:
                # InputFloder = ''
                # InputMask = ''
                # KeepValues = ''
                # # change inputfloder and outputfloder
                # if MapResults:
                #     InputFloder = info["OutputFolder"] + '/MapCT/CTTimeAvePressure.nii.gz'
                # try:
                #     if info["Load Value image for FFR Folder(FFRCalculation)"]:
                #         InputFloder = info["Load Value image for FFR Folder(FFRCalculation)"]
                # except:
                #     pass
                # try:
                #     if info["InputMask(FFRCalculation)"]:
                #         InputMask = info["InputMask(FFRCalculation)"]
                # except:
                #     pass
                # try:
                #     if info["Keep Values(FFRCalculation)"]:
                #         KeepValues = info["Keep Values(FFRCalculation)"]
                # except:
                #     pass
                # OutputFloder = info["OutputFolder"] + '/FFR'
                # print('FFRCalculation InputFloder=', InputFloder)
                # print('FFRCalculation OutputFloder=', OutputFloder)
                # # make dir
                # if not os.path.exists(OutputFloder):
                #     os.mkdir(OutputFloder)
                # # change tab
                # self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.FFRCalculation)
                # # set ui
                # self.ui.loadImgPathTxt_FFR.setPlainText('{}'.format(InputFloder))
                # self.ui.saveImgPathTxt_FFR.setPlainText('{}'.format(OutputFloder + '/FFR.nii.gz'))
                # if KeepValues:
                #     self.ui.valListTxt_FFR.setPlainText('{}'.format(KeepValues))
                # if InputMask:
                #     self.ui.loadMskPathTxt_FFR.setPlainText('{}'.format(InputMask))
                # # Touched function
                # self.mudule.FFR.LoadData()
                # self.mudule.FFR.FilterVals()
                # self.mudule.FFR.FRRCalcSave()
                # self.mudule.FFR.InitFFRCalcs()

            # if Paraview_processing:
                # Nodecoo = ''
                # TetraElmnt = ''
                # HexElmnt = ''
                # Times = ''
                # ParamsDic = ''
                # PostResults = ''
                # WSSParamDict = ''
                # WssDict = ''
                # FFRIQRAverageValue = ''
                # # change inputfloder and outputfloder
                # if DataOutput:
                #     Nodecoo = info["OutputFolder"] + '/Npy/Fluid_Nodecoo_Dic.npy'
                #     TetraElmnt = info["OutputFolder"] + '/Npy/Fluid_TetraElmnt_NdIfo_Dic.npy'
                #     HexElmnt = info["OutputFolder"] + '/Npy/Fluid_HexElmnt_NdIfo_Dic.npy'
                #     Times = info["OutputFolder"] + '/Npy/Fluid_Times_Dic.npy'
                #     ParamsDic = info["OutputFolder"] + '/Npy/Fluid_lst_ParamsDic.npy'
                # if CFD_Post_processing:
                #     PostResults = info["OutputFolder"] + '/PostNpy/fluid_PostResults_Dict_dict.npy'
                #     WSSParamDict = info["OutputFolder"] + '/PostNpy/fluid_TimeAvePressureDict_dict.npy'
                #     WssDict = info["OutputFolder"] + '/PostNpy/fluid_PostResults_WssDict_dict.npy'
                # if FFRCalculation:
                #     FFRIQRAverageValue = info["OutputFolder"] + '/FFR/CTFFRIQRAverageValue.npy'
                # try:
                #     if info["Nodecoo(Paraview_processing)"]:
                #         Nodecoo = info["Nodecoo(Paraview_processing)"]
                # except:
                #     pass
                # try:
                #     if info["TetraElmnt(Paraview_processing)"]:
                #         TetraElmnt = info["TetraElmnt(Paraview_processing)"]
                # except:
                #     pass
                # try:
                #     if info["HexElmnt(Paraview_processing)"]:
                #         HexElmnt = info["HexElmnt(Paraview_processing)"]
                # except:
                #     pass
                # try:
                #     if info["Times(Paraview_processing)"]:
                #         Times = info["Times(Paraview_processing)"]
                # except:
                #     pass
                # try:
                #     if info["ParamsDic(Paraview_processing)"]:
                #         ParamsDic = info["ParamsDic(Paraview_processing)"]
                # except:
                #     pass
                # try:
                #     if info["PostResults(Paraview_processing)"]:
                #         PostResults = info["PostResults(Paraview_processing)"]
                # except:
                #     pass
                # try:
                #     if info["WSSParamDict(Paraview_processing)"]:
                #         WSSParamDict = info["WSSParamDict(Paraview_processing)"]
                # except:
                #     pass
                # try:
                #     if info["WssDict(Paraview_processing)"]:
                #         WssDict = info["WssDict(Paraview_processing)"]
                # except:
                #     pass
                # try:
                #     if info["FFRIQRAverageValue(Paraview_processing)"]:
                #         FFRIQRAverageValue = info["FFRIQRAverageValue(Paraview_processing)"]
                # except:
                #     pass
                # OutputFloder = info["OutputFolder"] + '/Paraview'
                # print('Paraview_processing OutputFloder=', OutputFloder)
                # # make dir
                # if not os.path.exists(OutputFloder):
                #     os.mkdir(OutputFloder)
                # # change tab
                # self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.PostProcessing_YC)
                # # set ui
                # if Nodecoo:
                #     self.ui.lineEdit_ChooseNodeCoordinate_PP.setText('{}'.format(Nodecoo))
                # if TetraElmnt:
                #     self.ui.lineEdit_tetraElem_PP.setText('{}'.format(TetraElmnt))
                # if HexElmnt:
                #     self.ui.lineEdit_label_Hexelem_PP.setText('{}'.format(HexElmnt))
                # if Times:
                #     self.ui.lineEdit_time_PP.setText('{}'.format(Times))
                # if ParamsDic:
                #     self.ui.lineEdit_Lst_Parameters_PP.setText('{}'.format(ParamsDic))
                # if PostResults:
                #     self.ui.lineEdit_postresults_PP.setText('{}'.format(PostResults))
                # if WSSParamDict:
                #     self.ui.lineEdit_WSSParameter_PP.setText('{}'.format(WSSParamDict))
                # if WssDict:
                #     self.ui.lineEdit_WSS_PP.setText('{}'.format(WssDict))
                # if FFRIQRAverageValue:
                #     self.ui.lineEdit_FFRIQRAverageValue_PP.setText('{}'.format(FFRIQRAverageValue))
                # self.ui.lineEdit_ExportPath_PP.setText('{}/'.format(OutputFloder))
                # time.sleep(1)
                # # Touched function
                # self.mudule.ParaviewPostProcessing.Fillist()
                # self.mudule.ParaviewPostProcessing.VTUExport()
                # self.mudule.ParaviewPostProcessing.InitPostProcessing()

            # if Savevtu:
                # inPath = ''
                # ndInterestPath = ''
                # ParamsNpyPath = ''
                # npyName = ''
                # useclac = ''
                # pointarrayname = ''
                # savevtuPath = ''
                # savevtuName = ''
                # addFFR = False
                # savesingle = False
                # TAPnpyPath = ''
                # FFRValuePath = ''
                # FFRarrayName = ''
                # vtubinary = True
                # FFRSavePath = ''
                # FFRSavename = ''
                # FFRbinary = True
                # ParamsPath = ''
                # savePVDPath = ''
                # pvdName = ''
                # velocityName = ''
                # nodalpressureName = ''
                # maxshearstressName = ''
                # getvelocity = True
                # getnodalpressure = True
                # getmaxshearstress = True
                # PVDbinary = True
                # SavePVD = False
                # SaveFFRvtu = False
                # Savevtufile = False
                #
                # try:
                #     if info["nasPath(Savevtu)"]:
                #         inPath = info["nasPath(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["ndInterestDictPath(Savevtu)"]:
                #         ndInterestPath = info["ndInterestDictPath(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["ParamsNpyPath(Savevtu)"]:
                #         ParamsNpyPath = info["ParamsNpyPath(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["npyName(Savevtu)"]:
                #         npyName = info["npyName(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["useclac(Savevtu)"]:
                #         useclac = info["useclac(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["pointarrayname(Savevtu)"]:
                #         pointarrayname = info["pointarrayname(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["savevtuPath(Savevtu)"]:
                #         savevtuPath = info["savevtuPath(Savevtu)"]
                # except:
                #     savevtuPath = info["OutputFolder"] + '/Vtu'
                # try:
                #     if info["savevtuName(Savevtu)"]:
                #         savevtuName = info["savevtuName(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["addFFR(Savevtu)"],np.bool_):
                #         addFFR = info["addFFR(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["savesingle(Savevtu)"],np.bool_):
                #         savesingle = info["savesingle(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["TAPnpyPath(Savevtu)"]:
                #         TAPnpyPath = info["TAPnpyPath(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["FFRValuePath(Savevtu)"]:
                #         FFRValuePath = info["FFRValuePath(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["FFRarrayName(Savevtu)"]:
                #         FFRarrayName = info["FFRarrayName(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["vtubinary(Savevtu)"],np.bool_):
                #         vtubinary = info["vtubinary(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["FFRSavePath(Savevtu)"]:
                #         FFRSavePath = info["FFRSavePath(Savevtu)"]
                # except:
                #     FFRSavePath = info["OutputFolder"] + '/Vtu'
                # try:
                #     if info["FFRSavename(Savevtu)"]:
                #         FFRSavename = info["FFRSavename(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["FFRbinary(Savevtu)"],np.bool_):
                #         FFRbinary = info["FFRbinary(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["ParamsPath(Savevtu)"]:
                #         ParamsPath = info["ParamsPath(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["savePVDPath(Savevtu)"]:
                #         savePVDPath = info["savePVDPath(Savevtu)"]
                # except:
                #     savePVDPath = info["OutputFolder"] + '/Vtu'
                # try:
                #     if info["pvdName(Savevtu)"]:
                #         pvdName = info["pvdName(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["velocityName(Savevtu)"]:
                #         velocityName = info["velocityName(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["nodalpressureName(Savevtu)"]:
                #         nodalpressureName = info["nodalpressureName(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if info["maxshearstressName(Savevtu)"]:
                #         maxshearstressName = info["maxshearstressName(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["getvelocity(Savevtu)"],np.bool_):
                #         getvelocity = info["getvelocity(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["getnodalpressure(Savevtu)"],np.bool_):
                #         getnodalpressure = info["getnodalpressure(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["getmaxshearstress(Savevtu)"],np.bool_):
                #         getmaxshearstress = info["getmaxshearstress(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["PVDbinary(Savevtu)"],np.bool_):
                #         PVDbinary = info["PVDbinary(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["SavePVD(Savevtu)"],np.bool_):
                #         SavePVD = info["SavePVD(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["SaveFFRvtu(Savevtu)"],np.bool_):
                #         SaveFFRvtu = info["SaveFFRvtu(Savevtu)"]
                # except:
                #     pass
                # try:
                #     if isinstance(info["Savevtufile(Savevtu)"],np.bool_):
                #         Savevtufile = info["Savevtufile(Savevtu)"]
                # except:
                #     pass
                # OutputFloder = info["OutputFolder"] + '/Vtu'
                # print('Savevtu OutputFloder=', OutputFloder)
                # # make dir
                # if not os.path.exists(OutputFloder):
                #     os.mkdir(OutputFloder)
                # # change tab
                # self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.Savevtu)
                # # set ui
                # if inPath:
                #     self.ui.plainTextEdit_nasPath_SVZ.setPlainText('{}'.format(inPath))
                # if ParamsPath:
                #     self.ui.plainTextEdit_ParamsPath_SVZ.setPlainText('{}'.format(ParamsPath))
                # self.ui.checkBox_velocity_SVZ.setChecked(getvelocity)
                # if velocityName:
                #     self.ui.plainTextEdit_velocity_SVZ.setPlainText('{}'.format(velocityName))
                # self.ui.checkBox_nodalpressure_SVZ.setChecked(getnodalpressure)
                # if nodalpressureName:
                #     self.ui.plainTextEdit_nodalpressure_SVZ.setPlainText('{}'.format(nodalpressureName))
                # self.ui.checkBox_maxshearstress_SVZ.setChecked(getmaxshearstress)
                # if maxshearstressName:
                #     self.ui.plainTextEdit_maxshearstress_SVZ.setPlainText('{}'.format(maxshearstressName))
                # if savePVDPath:
                #     self.ui.plainTextEdit_pvdPath_SVZ.setPlainText('{}'.format(savePVDPath))
                # if pvdName:
                #     self.ui.plainTextEdit_pvdName_VPZ.setPlainText('{}'.format(pvdName))
                # self.ui.checkBox_PVDbinary_SVZ.setChecked(PVDbinary)
                # if ndInterestPath:
                #     self.ui.plainTextEdit_ndInterestPath_SVZ.setPlainText('{}'.format(ndInterestPath))
                # if ParamsNpyPath:
                #     self.ui.plainTextEdit_ParamsNpyPath_SVZ.setPlainText('{}'.format(ParamsNpyPath))
                # if npyName:
                #     self.ui.plainTextEdit_npyName_SVZ.setPlainText('{}'.format(npyName))
                # if useclac:
                #     self.ui.plainTextEdit_useclac_SVZ.setPlainText('{}'.format(useclac))
                # if pointarrayname:
                #     self.ui.plainTextEdit_pointarrayname_SVZ.setPlainText('{}'.format(pointarrayname))
                # if savevtuPath:
                #     self.ui.plainTextEdit_Savevtu_SVZ.setPlainText('{}'.format(savevtuPath))
                # if savevtuName:
                #     self.ui.plainTextEdit_vtuname_SVZ.setPlainText('{}'.format(savevtuName))
                # self.ui.checkBox_vtubinary_SVZ.setChecked(vtubinary)
                # self.ui.checkBox_addFFR_SVZ.setChecked(addFFR)
                # self.ui.checkBox_savesingle_SVZ.setChecked(savesingle)
                # if TAPnpyPath:
                #     self.ui.plainTextEdit_TAPnpyPath_SVZ.setPlainText('{}'.format(TAPnpyPath))
                # if FFRValuePath:
                #     self.ui.plainTextEdit_FFRValuePath_SVZ.setPlainText('{}'.format(FFRValuePath))
                # if FFRarrayName:
                #     self.ui.plainTextEdit_FFRarrayName_SVZ.setPlainText('{}'.format(FFRarrayName))
                # if FFRSavePath:
                #     self.ui.plainTextEdit_FFRSavePath_SVZ.setPlainText('{}'.format(FFRSavePath))
                # if FFRSavename:
                #     self.ui.plainTextEdit_FFRname_SVZ.setPlainText('{}'.format(FFRSavename))
                # self.ui.checkBox_FFRbinary_SVZ.setChecked(FFRbinary)
                # # Touched function
                # if SavePVD:
                #     self.mudule.SaveVTU.savepvd()
                # if SaveFFRvtu:
                #     self.mudule.SaveVTU.saveFFRvtu()
                # if Savevtufile:
                #     self.mudule.SaveVTU.savevtu()

        # change tab
        self.ui.QStackedWidget_Module.setCurrentWidget(self.ui.OneClicked)