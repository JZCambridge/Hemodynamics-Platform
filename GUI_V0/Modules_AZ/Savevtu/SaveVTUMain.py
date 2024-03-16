import sys
import os
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
# Import functions
import pdfunction
import Save_Load_File
import Preprocess_Mask

import numpy as np
import pyvista as pv
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *

class SaveVTUorPVD():
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.pushButton_choosenas_SVZ.clicked.connect(lambda: self.choosenaspath())
        self.ui.pushButton_chooseParama_SVZ.clicked.connect(lambda: self.chooseparamasdictpath())
        self.ui.pushButton_choosepvdPath_SVZ.clicked.connect(lambda: self.choosesavepvdpath())
        self.ui.pushButton_chooseTAPnpy_SVZ.clicked.connect(lambda: self.chooseTAPnpypath())
        self.ui.pushButton_chooseFFRValue_SVZ.clicked.connect(lambda: self.chooseFFRvaluepath())
        self.ui.pushButton_chooseFFRsave_SVZ.clicked.connect(lambda: self.choosesaveFFRvtupath())
        self.ui.pushButton_choosendInterest_SVZ.clicked.connect(lambda: self.choosendInterestpath())
        self.ui.pushButton_chooseParamsNpy_SVZ.clicked.connect(lambda: self.chooseparamasnpypath())
        self.ui.pushButton_Savevtu_SVZ.clicked.connect(lambda: self.choosesavevtupath())
        self.ui.pushButton_savepvd_SVZ.clicked.connect(lambda: self.savepvd())
        self.ui.pushButton_saveFFRvtu_SVZ.clicked.connect(lambda: self.saveFFRvtu())
        self.ui.pushButton_savevtu_SVZ.clicked.connect(lambda: self.savevtu())
        self.ui.pushButton_BatchTable_SVZ.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_SVZ.clicked.connect(lambda: self.batchrun())
        self.ui.checkBox_Fluidpvd_SVZ.clicked.connect(lambda: self.clickfluid())
        self.ui.checkBox_Solidpvd_SVZ.clicked.connect(lambda: self.clicksolid())

    def clickfluid(self):
        if self.ui.checkBox_Fluidpvd_SVZ.isChecked():
            self.ui.checkBox_Solidpvd_SVZ.setChecked(False)

    def clicksolid(self):
        if self.ui.checkBox_Solidpvd_SVZ.isChecked():
            self.ui.checkBox_Fluidpvd_SVZ.setChecked(False)

    def savevtu(self):
        inPath = self.ui.plainTextEdit_nasPath_SVZ.toPlainText()
        ndInterestPath = self.ui.plainTextEdit_ndInterestPath_SVZ.toPlainText()
        ParamsNpyPath = self.ui.plainTextEdit_ParamsNpyPath_SVZ.toPlainText()
        npyName = Preprocess_Mask.StrToLst(strIn=self.ui.plainTextEdit_npyName_SVZ.toPlainText())["listOut"]
        useclac = Preprocess_Mask.StrToLst(strIn=self.ui.plainTextEdit_useclac_SVZ.toPlainText())["intOut"]
        pointarrayname = Preprocess_Mask.StrToLst(strIn=self.ui.plainTextEdit_pointarrayname_SVZ.toPlainText())["listOut"]
        savevtuPath = self.ui.plainTextEdit_Savevtu_SVZ.toPlainText()
        savevtuName = self.ui.plainTextEdit_vtuname_SVZ.toPlainText()
        addFFR = self.ui.checkBox_addFFR_SVZ.isChecked()
        savesingle = self.ui.checkBox_savesingle_SVZ.isChecked()
        TAPnpyPath = self.ui.plainTextEdit_TAPnpyPath_SVZ.toPlainText()
        FFRValuePath = self.ui.plainTextEdit_FFRValuePath_SVZ.toPlainText()
        FFRarrayName = self.ui.plainTextEdit_FFRarrayName_SVZ.toPlainText()
        vtubinary = self.ui.checkBox_vtubinary_SVZ.isChecked()
        print('inPath', inPath)
        print('ndInterestPath', ndInterestPath)
        print('ParamsNpyPath', ParamsNpyPath)
        print('npyName', npyName)
        print('useclac', useclac)
        print('pointarrayname', pointarrayname)
        print('savevtuPath', savevtuPath)
        print('savevtuName', savevtuName)
        print('addFFR', addFFR)
        print('savesingle', savesingle)
        print('TAPnpyPath', TAPnpyPath)
        print('FFRValuePath', FFRValuePath)
        print('FFRarrayName', FFRarrayName)
        print('vtubinary', vtubinary)

        if not os.path.exists(savevtuPath):
            os.mkdir(savevtuPath)

        model = pv.read(inPath)
        npyPath=[ParamsNpyPath + '/' + i for i in npyName]
        if addFFR:
            npyPath.append(TAPnpyPath)
            useclac.append(2)
            pointarrayname.append(FFRarrayName)
        if 1 in useclac:
            Interest = np.load(ndInterestPath, allow_pickle=True)
            NodeToCalcs = Interest.item()['NodeToCalcs']
            clac = np.where(NodeToCalcs == 1)[0]
        for i in range(len(npyPath)):
            npyLoad = np.load(npyPath[i], allow_pickle=True)
            if useclac[i] == 1:
                npyadd = NodeToCalcs
                npyadd[npyadd != 1] = None
                npyuse = npyLoad[:, 4]
                if len(npyLoad) == len(NodeToCalcs):
                    npyuse = npyuse[clac]
                npyadd[clac] = npyuse
            elif useclac[i] == 2:
                FFRValue = np.load(FFRValuePath, allow_pickle=True)
                npyadd = npyLoad[:, 4] / FFRValue
            else:
                npyadd = npyLoad[:, 4]
            model.point_data[pointarrayname[i]] = npyadd.copy()
            # print(pointarrayname[i],model.point_data[pointarrayname[i]])
            if savesingle:
                model.save(savevtuPath + '/' + pointarrayname[i] + '.vtu',binary=vtubinary)
        model.save(savevtuPath + '/' + savevtuName + '.vtu',binary=vtubinary)

    def saveFFRvtu(self):
        inPath = self.ui.plainTextEdit_nasPath_SVZ.toPlainText()
        TAPnpyPath = self.ui.plainTextEdit_TAPnpyPath_SVZ.toPlainText()
        FFRValuePath = self.ui.plainTextEdit_FFRValuePath_SVZ.toPlainText()
        FFRarrayName = self.ui.plainTextEdit_FFRarrayName_SVZ.toPlainText()
        FFRSavePath = self.ui.plainTextEdit_FFRSavePath_SVZ.toPlainText()
        FFRSavename = self.ui.plainTextEdit_FFRname_SVZ.toPlainText()
        FFRbinary = self.ui.checkBox_FFRbinary_SVZ.isChecked()
        print('inPath', inPath)
        print('TAPnpyPath', TAPnpyPath)
        print('FFRValuePath', FFRValuePath)
        print('FFRarrayName', FFRarrayName)
        print('FFRSavePath', FFRSavePath)
        print('FFRSavename', FFRSavename)
        print('FFRbinary', FFRbinary)

        if not os.path.exists(FFRSavePath):
            os.mkdir(FFRSavePath)

        model = pv.read(inPath)
        FFRValue = np.load(FFRValuePath, allow_pickle=True)
        TAPnpy = np.load(TAPnpyPath, allow_pickle=True)
        FFRnpy = TAPnpy[:, 4] / FFRValue
        model.point_data[FFRarrayName] = FFRnpy
        SavePath = FFRSavePath + '/' + FFRSavename + '.vtu'
        model.save(SavePath, binary=FFRbinary)

    def savepvd(self):
        inPath = self.ui.plainTextEdit_nasPath_SVZ.toPlainText()
        ParamsPath = self.ui.plainTextEdit_ParamsPath_SVZ.toPlainText()
        savePVDPath = self.ui.plainTextEdit_pvdPath_SVZ.toPlainText()
        PVDbinary = self.ui.checkBox_PVDbinary_SVZ.isChecked()
        pvdName = self.ui.plainTextEdit_pvdName_VPZ.toPlainText()
        Fluid = self.ui.checkBox_Fluidpvd_SVZ.isChecked()
        getvelocity = self.ui.checkBox_velocity_SVZ.isChecked()
        getnodalpressure = self.ui.checkBox_nodalpressure_SVZ.isChecked()
        getmaxshearstress = self.ui.checkBox_maxshearstress_SVZ.isChecked()
        velocityName = self.ui.plainTextEdit_velocity_SVZ.toPlainText()
        nodalpressureName = self.ui.plainTextEdit_nodalpressure_SVZ.toPlainText()
        maxshearstressName = self.ui.plainTextEdit_maxshearstress_SVZ.toPlainText()
        Solid = self.ui.checkBox_Solidpvd_SVZ.isChecked()
        getSigmaP1 = self.ui.checkBox_SigmaP1_SVZ.isChecked()
        getEffectivestress = self.ui.checkBox_Effectivestress_SVZ.isChecked()
        getSolidmaxshearstress = self.ui.checkBox_Solidmaxshearstress_SVZ.isChecked()
        getSigmaNorm2 = self.ui.checkBox_SigmaNorm2_SVZ.isChecked()
        SigmaP1Name = self.ui.plainTextEdit_SigmaP1_SVZ.toPlainText()
        EffectivestressName = self.ui.plainTextEdit_Effectivestress_SVZ.toPlainText()
        SolidmaxshearstressName = self.ui.plainTextEdit_Solidmaxshearstress_SVZ.toPlainText()
        SigmaNorm2Name = self.ui.plainTextEdit_SigmaNorm2_SVZ.toPlainText()
        print('inPath', inPath)
        print('ParamsPath', ParamsPath)
        print('savePVDPath', savePVDPath)
        print('PVDbinary', PVDbinary)
        print('pvdName', pvdName)
        print('Fluid', Fluid)
        print('getvelocity', getvelocity)
        print('getnodalpressure', getnodalpressure)
        print('getmaxshearstress', getmaxshearstress)
        print('velocityName', velocityName)
        print('nodalpressureName', nodalpressureName)
        print('maxshearstressName', maxshearstressName)
        print('Solid', Solid)
        print('getSigmaP1', getSigmaP1)
        print('getEffectivestress', getEffectivestress)
        print('getSolidmaxshearstress', getSolidmaxshearstress)
        print('getSigmaNorm2', getSigmaNorm2)
        print('SigmaP1Name', SigmaP1Name)
        print('EffectivestressName', EffectivestressName)
        print('SolidmaxshearstressName', SolidmaxshearstressName)
        print('SigmaNorm2Name', SigmaNorm2Name)

        model = pv.read(inPath)
        Params = np.load(ParamsPath, allow_pickle=True).item()
        vtusavedir = savePVDPath + '/' + pvdName
        if not os.path.exists(savePVDPath):
            os.mkdir(savePVDPath)
        if not os.path.exists(vtusavedir):
            os.mkdir(vtusavedir)
        f = open(savePVDPath + '/' + pvdName + '.pvd', 'w')
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="Collection" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n')
        f.write('  <Collection>\n')
        for number in Params['range']:
            timestep = str(Params['timeRange'][number - 1])
            key_str = 'lst_ParamsMat' + timestep
            if Fluid:
                if getvelocity:
                    model.point_data[velocityName] = Params[key_str][:, 0:3]
                if getnodalpressure:
                    model.point_data[nodalpressureName] = Params[key_str][:, 3]
                if getmaxshearstress:
                    model.point_data[maxshearstressName] = Params[key_str][:, 4]
            if Solid:
                if getSigmaP1:
                    model.point_data[SigmaP1Name] = Params[key_str][:, 0]
                if getEffectivestress:
                    model.point_data[EffectivestressName] = Params[key_str][:, 1]
                if getSolidmaxshearstress:
                    model.point_data[SolidmaxshearstressName] = Params[key_str][:, 2]
                if getSigmaNorm2:
                    model.point_data[SigmaNorm2Name] = Params[key_str][:, 3]
            vtusavepath = vtusavedir + '/' + str(number) + ".vtu"
            model.save(vtusavepath,binary=PVDbinary)
            f.write('    <DataSet timestep="{}" part="0" file="{}/{}.vtu"/>\n'.format(timestep, pvdName, number))
        f.write('  </Collection>\n')
        f.write('</VTKFile>\n')
        f.close()

    def choosenaspath(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose nas or vtu file",
                                                 fileTypes="All files (*.*);; nas files(*.nas);;vtu files(*.vtu)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_nasPath_SVZ.setPlainText('{}'.format(filename))

    def chooseparamasdictpath(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose npy file",
                                                 fileTypes="All files (*.*);; npy files(*.npy)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_ParamsPath_SVZ.setPlainText('{}'.format(filename))

    def choosesavepvdpath(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.plainTextEdit_pvdPath_SVZ.setPlainText(dirname)

    def chooseTAPnpypath(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose npy file",
                                                 fileTypes="All files (*.*);; npy files(*.npy)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_TAPnpyPath_SVZ.setPlainText('{}'.format(filename))

    def chooseFFRvaluepath(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose npy file",
                                                 fileTypes="All files (*.*);; npy files(*.npy)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_FFRValuePath_SVZ.setPlainText('{}'.format(filename))

    def choosesaveFFRvtupath(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.plainTextEdit_FFRSavePath_SVZ.setPlainText(dirname)

    def choosendInterestpath(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose npy file",
                                                 fileTypes="All files (*.*);; npy files(*.npy)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_ndInterestPath_SVZ.setPlainText('{}'.format(filename))

    def chooseparamasnpypath(self):
        # choose
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.plainTextEdit_ParamsNpyPath_SVZ.setPlainText('{}'.format(dirname))

    def choosesavevtupath(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.plainTextEdit_Savevtu_SVZ.setPlainText(dirname)

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_SVZ.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_SVZ.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            Savevtu = False
            try:
                if info["Savevtu"]:
                    Savevtu = info["Savevtu"]
            except:
                pass
            if Savevtu:
                inPath = ''
                ndInterestPath = ''
                ParamsNpyPath = ''
                npyName = ''
                useclac = ''
                pointarrayname = ''
                savevtuPath = ''
                savevtuName = ''
                addFFR = False
                savesingle = False
                TAPnpyPath = ''
                FFRValuePath = ''
                FFRarrayName = ''
                vtubinary = True
                FFRSavePath = ''
                FFRSavename = ''
                FFRbinary = True
                ParamsPath = ''
                savePVDPath = ''
                pvdName = ''
                Fluid = True
                velocityName = ''
                nodalpressureName = ''
                maxshearstressName = ''
                getvelocity = True
                getnodalpressure = True
                getmaxshearstress = True
                Solid = False
                getSigmaP1 = True
                getEffectivestress = True
                getSolidmaxshearstress = True
                getSigmaNorm2 = True
                SigmaP1Name = ''
                EffectivestressName = ''
                SolidmaxshearstressName = ''
                SigmaNorm2Name = ''
                PVDbinary = True
                SavePVD = False
                SaveFFRvtu = False
                Savevtufile = False

                try:
                    if info["nasPath(Savevtu)"]:
                        inPath = info["nasPath(Savevtu)"]
                except:
                    pass
                try:
                    if info["ndInterestDictPath(Savevtu)"]:
                        ndInterestPath = info["ndInterestDictPath(Savevtu)"]
                except:
                    pass
                try:
                    if info["ParamsNpyPath(Savevtu)"]:
                        ParamsNpyPath = info["ParamsNpyPath(Savevtu)"]
                except:
                    pass
                try:
                    if info["npyName(Savevtu)"]:
                        npyName = info["npyName(Savevtu)"]
                except:
                    pass
                try:
                    if info["useclac(Savevtu)"]:
                        useclac = info["useclac(Savevtu)"]
                except:
                    pass
                try:
                    if info["pointarrayname(Savevtu)"]:
                        pointarrayname = info["pointarrayname(Savevtu)"]
                except:
                    pass
                try:
                    if info["savevtuPath(Savevtu)"]:
                        savevtuPath = info["savevtuPath(Savevtu)"]
                except:
                    try:
                        if info["OutputFolder"]:
                            savevtuPath = info["OutputFolder"] + '/Vtu'
                    except:
                        try:
                            if info["OutputFolder(Savevtu)"]:
                                savevtuPath = info["OutputFolder(Savevtu)"]
                        except:
                            pass
                try:
                    if info["savevtuName(Savevtu)"]:
                        savevtuName = info["savevtuName(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["addFFR(Savevtu)"], np.bool_):
                        addFFR = info["addFFR(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["savesingle(Savevtu)"], np.bool_):
                        savesingle = info["savesingle(Savevtu)"]
                except:
                    pass
                try:
                    if info["TAPnpyPath(Savevtu)"]:
                        TAPnpyPath = info["TAPnpyPath(Savevtu)"]
                except:
                    pass
                try:
                    if info["FFRValuePath(Savevtu)"]:
                        FFRValuePath = info["FFRValuePath(Savevtu)"]
                except:
                    pass
                try:
                    if info["FFRarrayName(Savevtu)"]:
                        FFRarrayName = info["FFRarrayName(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["vtubinary(Savevtu)"], np.bool_):
                        vtubinary = info["vtubinary(Savevtu)"]
                except:
                    pass
                try:
                    if info["FFRSavePath(Savevtu)"]:
                        FFRSavePath = info["FFRSavePath(Savevtu)"]
                except:
                    try:
                        if info["OutputFolder"]:
                            FFRSavePath = info["OutputFolder"] + '/Vtu'
                    except:
                        try:
                            if info["OutputFolder(Savevtu)"]:
                                FFRSavePath = info["OutputFolder(Savevtu)"]
                        except:
                            pass
                try:
                    if info["FFRSavename(Savevtu)"]:
                        FFRSavename = info["FFRSavename(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["FFRbinary(Savevtu)"], np.bool_):
                        FFRbinary = info["FFRbinary(Savevtu)"]
                except:
                    pass
                try:
                    if info["ParamsPath(Savevtu)"]:
                        ParamsPath = info["ParamsPath(Savevtu)"]
                except:
                    pass
                try:
                    if info["savePVDPath(Savevtu)"]:
                        savePVDPath = info["savePVDPath(Savevtu)"]
                except:
                    try:
                        if info["OutputFolder"]:
                            savePVDPath = info["OutputFolder"] + '/Vtu'
                    except:
                        try:
                            if info["OutputFolder(Savevtu)"]:
                                savePVDPath = info["OutputFolder(Savevtu)"]
                        except:
                            pass
                try:
                    if info["pvdName(Savevtu)"]:
                        pvdName = info["pvdName(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["Fluidpvd(Savevtu)"], np.bool_):
                        Fluid = info["Fluidpvd(Savevtu)"]
                except:
                    pass
                try:
                    if info["velocityName(Savevtu)"]:
                        velocityName = info["velocityName(Savevtu)"]
                except:
                    pass
                try:
                    if info["nodalpressureName(Savevtu)"]:
                        nodalpressureName = info["nodalpressureName(Savevtu)"]
                except:
                    pass
                try:
                    if info["maxshearstressName(Savevtu)"]:
                        maxshearstressName = info["maxshearstressName(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["getvelocity(Savevtu)"], np.bool_):
                        getvelocity = info["getvelocity(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["getnodalpressure(Savevtu)"], np.bool_):
                        getnodalpressure = info["getnodalpressure(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["getmaxshearstress(Savevtu)"], np.bool_):
                        getmaxshearstress = info["getmaxshearstress(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["Solidpvd(Savevtu)"], np.bool_):
                        Solid = info["Solidpvd(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["getSigmaP1(Savevtu)"], np.bool_):
                        getSigmaP1 = info["getSigmaP1(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["getEffectivestress(Savevtu)"], np.bool_):
                        getEffectivestress = info["getEffectivestress(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["getSolidmaxshearstress(Savevtu)"], np.bool_):
                        getSolidmaxshearstress = info["getSolidmaxshearstress(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["getSigmaNorm2(Savevtu)"], np.bool_):
                        getSigmaNorm2 = info["getSigmaNorm2(Savevtu)"]
                except:
                    pass
                try:
                    if info["SigmaP1Name(Savevtu)"]:
                        SigmaP1Name = info["SigmaP1Name(Savevtu)"]
                except:
                    pass
                try:
                    if info["EffectivestressName(Savevtu)"]:
                        EffectivestressName = info["EffectivestressName(Savevtu)"]
                except:
                    pass
                try:
                    if info["SolidmaxshearstressName(Savevtu)"]:
                        SolidmaxshearstressName = info["SolidmaxshearstressName(Savevtu)"]
                except:
                    pass
                try:
                    if info["SigmaNorm2Name(Savevtu)"]:
                        SigmaNorm2Name = info["SigmaNorm2Name(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["PVDbinary(Savevtu)"], np.bool_):
                        PVDbinary = info["PVDbinary(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["SavePVD(Savevtu)"], np.bool_):
                        SavePVD = info["SavePVD(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["SaveFFRvtu(Savevtu)"], np.bool_):
                        SaveFFRvtu = info["SaveFFRvtu(Savevtu)"]
                except:
                    pass
                try:
                    if isinstance(info["Savevtufile(Savevtu)"], np.bool_):
                        Savevtufile = info["Savevtufile(Savevtu)"]
                except:
                    pass
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                if inPath:
                    self.ui.plainTextEdit_nasPath_SVZ.setPlainText('{}'.format(inPath))
                if ParamsPath:
                    self.ui.plainTextEdit_ParamsPath_SVZ.setPlainText('{}'.format(ParamsPath))
                self.ui.checkBox_Fluidpvd_SVZ.setChecked(Fluid)
                self.ui.checkBox_velocity_SVZ.setChecked(getvelocity)
                if velocityName:
                    self.ui.plainTextEdit_velocity_SVZ.setPlainText('{}'.format(velocityName))
                self.ui.checkBox_nodalpressure_SVZ.setChecked(getnodalpressure)
                if nodalpressureName:
                    self.ui.plainTextEdit_nodalpressure_SVZ.setPlainText('{}'.format(nodalpressureName))
                self.ui.checkBox_maxshearstress_SVZ.setChecked(getmaxshearstress)
                if maxshearstressName:
                    self.ui.plainTextEdit_maxshearstress_SVZ.setPlainText('{}'.format(maxshearstressName))
                self.ui.checkBox_Solidpvd_SVZ.setChecked(Solid)
                self.ui.checkBox_SigmaP1_SVZ.setChecked(getSigmaP1)
                if SigmaP1Name:
                    self.ui.plainTextEdit_SigmaP1_SVZ.setPlainText('{}'.format(SigmaP1Name))
                self.ui.checkBox_Effectivestress_SVZ.setChecked(getEffectivestress)
                if EffectivestressName:
                    self.ui.plainTextEdit_Effectivestress_SVZ.setPlainText('{}'.format(EffectivestressName))
                self.ui.checkBox_Solidmaxshearstress_SVZ.setChecked(getSolidmaxshearstress)
                if SolidmaxshearstressName:
                    self.ui.plainTextEdit_Solidmaxshearstress_SVZ.setPlainText('{}'.format(SolidmaxshearstressName))
                self.ui.checkBox_SigmaNorm2_SVZ.setChecked(getSigmaNorm2)
                if SigmaNorm2Name:
                    self.ui.plainTextEdit_SigmaNorm2_SVZ.setPlainText('{}'.format(SigmaNorm2Name))
                if savePVDPath:
                    self.ui.plainTextEdit_pvdPath_SVZ.setPlainText('{}'.format(savePVDPath))
                if pvdName:
                    self.ui.plainTextEdit_pvdName_VPZ.setPlainText('{}'.format(pvdName))
                self.ui.checkBox_PVDbinary_SVZ.setChecked(PVDbinary)
                if ndInterestPath:
                    self.ui.plainTextEdit_ndInterestPath_SVZ.setPlainText('{}'.format(ndInterestPath))
                if ParamsNpyPath:
                    self.ui.plainTextEdit_ParamsNpyPath_SVZ.setPlainText('{}'.format(ParamsNpyPath))
                if npyName:
                    self.ui.plainTextEdit_npyName_SVZ.setPlainText('{}'.format(npyName))
                if useclac:
                    self.ui.plainTextEdit_useclac_SVZ.setPlainText('{}'.format(useclac))
                if pointarrayname:
                    self.ui.plainTextEdit_pointarrayname_SVZ.setPlainText('{}'.format(pointarrayname))
                if savevtuPath:
                    self.ui.plainTextEdit_Savevtu_SVZ.setPlainText('{}'.format(savevtuPath))
                if savevtuName:
                    self.ui.plainTextEdit_vtuname_SVZ.setPlainText('{}'.format(savevtuName))
                self.ui.checkBox_vtubinary_SVZ.setChecked(vtubinary)
                self.ui.checkBox_addFFR_SVZ.setChecked(addFFR)
                self.ui.checkBox_savesingle_SVZ.setChecked(savesingle)
                if TAPnpyPath:
                    self.ui.plainTextEdit_TAPnpyPath_SVZ.setPlainText('{}'.format(TAPnpyPath))
                if FFRValuePath:
                    self.ui.plainTextEdit_FFRValuePath_SVZ.setPlainText('{}'.format(FFRValuePath))
                if FFRarrayName:
                    self.ui.plainTextEdit_FFRarrayName_SVZ.setPlainText('{}'.format(FFRarrayName))
                if FFRSavePath:
                    self.ui.plainTextEdit_FFRSavePath_SVZ.setPlainText('{}'.format(FFRSavePath))
                if FFRSavename:
                    self.ui.plainTextEdit_FFRname_SVZ.setPlainText('{}'.format(FFRSavename))
                self.ui.checkBox_FFRbinary_SVZ.setChecked(FFRbinary)
                # Touched function
                if SavePVD:
                    self.savepvd()
                if SaveFFRvtu:
                    self.saveFFRvtu()
                if Savevtufile:
                    self.savevtu()

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys_uisplit\GUI_V0\ui\Savevtu.ui")
    stats = SaveVTUorPVD(UI=ui)
    stats.ui.show()
    app.exec_()