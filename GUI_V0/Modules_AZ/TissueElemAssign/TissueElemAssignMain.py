import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')

import Save_Load_File
import Preprocess_Mask
import Elemfunction
import pdfunction

import numpy as np
from scipy.spatial import KDTree
import re
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMessageBox

class TissueElemAssign():
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            
        self.ui.chooseNasPath_TEAZA.clicked.connect(lambda: self.choosenas())
        self.ui.chooseNpyPath_TEAZA.clicked.connect(lambda: self.chooseNpy())
        self.ui.chooseSavePath_TEAZA.clicked.connect(lambda: self.chooseSave())
        self.ui.Run_TEAZA.clicked.connect(lambda: self.runelemid())
        self.ui.pushButton_BatchTable_TEAZA.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_TEAZA.clicked.connect(lambda: self.batchrun())

    def choosenas(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose nas file",
                                                 fileTypes="All files (*.*);; nas files(*.nas)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.NasPath_TEAZA.setPlainText('{}'.format(filename))

    def chooseNpy(self):
        # choose
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Choose directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.NpyPath_TEAZA.setPlainText('{}'.format(dirname))

    def chooseSave(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.SavePath_TEAZA.setPlainText(dirname)

    def runelemid(self):
        InputnasPath = self.ui.NasPath_TEAZA.toPlainText()
        TissueCooDir = self.ui.NpyPath_TEAZA.toPlainText()
        SaveDir = self.ui.SavePath_TEAZA.toPlainText()
        Nodearray, NodeDict, CTETRAelemarray, CPENTAelemarray, Elemarray = Elemfunction.readnas(InputnasPath)
        # load  tissue files path
        TissueCooPath = []
        if os.path.isdir(TissueCooDir):
            for home, dirs, files in os.walk(TissueCooDir):
                for filename in files:
                    if '_2dndarr.npy' in filename:
                        TissueCooPath.append(TissueCooDir+'/'+filename)
        else:
            TissueCooPath=Preprocess_Mask.StrToLst(TissueCooDir)['listOut']
            print(TissueCooPath)

        tree = KDTree(Nodearray[:,1:4])
        for filePath in TissueCooPath:
            TissueCoo=np.load(filePath)
            nodeid=[]
            for j in TissueCoo:
                dist, InitMatRowsQueryed = tree.query(j, k=1)
                nodeid.append(Nodearray[InitMatRowsQueryed][0])
            nodeidunique=np.unique(nodeid)
            elemarrayid = []
            for RecurNum in range(len(nodeidunique)):
                try:
                    RowNumReturnTuple = np.where(nodeidunique[RecurNum] == CTETRAelemarray)
                    for RowNum in range(len(RowNumReturnTuple[0])):
                        elemarrayid.append(CTETRAelemarray[RowNumReturnTuple[0][RowNum]][0])
                except:
                    continue
            elemarrayidunique = np.unique(elemarrayid)
            filename=re.split('/',filePath)[-1]
            savename=filename.replace('.npy','.txt')
            np.savetxt(SaveDir+'/'+savename,elemarrayidunique,delimiter=',',fmt='%i')
            print('done')

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_TEAZA.setPlainText('{}'.format(filename))

    def batchrun(self,CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_TEAZA.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')
            TissueElemAssign = False
            try:
                if info["TissueElemAssign"]:
                    TissueElemAssign = info["TissueElemAssign"]
            except:
                pass
            if TissueElemAssign:
                InputFolder = ''
                InputNpyFolder = ''
                OutputFolder = ''
                # change inputFolder and outputFolder
                try:
                    if info["CooFolder(TissueElemAssign)"]:
                        InputFolder = info["CooFolder(TissueElemAssign)"]
                except:
                    pass
                try:
                    if info["NpyFolder(TissueElemAssign)"]:
                        InputNpyFolder = info["NpyFolder(TissueElemAssign)"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        OutputFolder = info["OutputFolder"] + '/TissueElemId'
                except:
                    pass
                try:
                    if info["OutputFolder(TissueElemAssign)"]:
                        OutputFolder = info["OutputFolder(TissueElemAssign)"]
                except:
                    pass
                print('FindFace InputFolder=', InputFolder)
                print('FindFace OutputFolder=', OutputFolder)
                # make dir
                if not os.path.exists(OutputFolder):
                    os.mkdir(OutputFolder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                self.ui.NasPath_TEAZA.setPlainText('{}'.format(InputFolder))
                self.ui.NpyPath_TEAZA.setPlainText('{}'.format(InputNpyFolder))
                self.ui.SavePath_TEAZA.setPlainText('{}'.format(OutputFolder))
                # Touched function
                self.runelemid()

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys_uisplit\GUI_V0\ui\TissueElemAssign.ui")
    stats = TissueElemAssign(UI=ui)
    stats.ui.show()
    app.exec_()