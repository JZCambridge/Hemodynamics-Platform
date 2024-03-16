import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
import Save_Load_File
import Elemfunction
import Qtfunction
import vtkfunction
import pdfunction
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *

class SplitFaceElem():
    def __init__(self, UI = None, Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.pushButton_inputcsv_SF.clicked.connect(lambda: self.inputcsv())
        self.ui.pushButton_inputnas_SF.clicked.connect(lambda: self.inputnas())
        self.ui.pushButton_findfaceandsplit_SF.clicked.connect(lambda: self.findfaceandsplit())
        self.ui.pushButton_vtk_SF.clicked.connect(lambda: self.vtklookcomp())
        self.ui.pushButton_initializationtable_SF.clicked.connect(lambda: self.initializationtable())
        self.ui.pushButton_pasteTrue_SF.clicked.connect(lambda: self.pasteTrue())
        self.ui.pushButton_pasteFalse_SF.clicked.connect(lambda: self.pasteFalse())
        self.ui.pushButton_pasteLine_SF.clicked.connect(lambda: self.pasteLine())
        self.ui.pushButton_pasteLumen_SF.clicked.connect(lambda: self.pasteLumen())
        self.ui.pushButton_outputfolder_SF.clicked.connect(lambda: self.outputfolder())
        self.ui.pushButton_calculateandsave_SF.clicked.connect(lambda: self.calculateandsave())
        self.ui.pushButton_BatchTable_SF.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_SF.clicked.connect(lambda: self.batchrun())

    def inputcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.textEdit_inputcsv_SF.setPlainText('{}'.format(filename))

    def inputnas(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose nas file",
                                                 fileTypes="All files (*.*);; nas files(*.nas)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.textEdit_inputnas_SF.setPlainText('{}'.format(filename))

    def findfaceandsplit(self, BatchProcess='False'):
        InputnasPath = self.ui.textEdit_inputnas_SF.toPlainText()
        self.Nodearray, self.NodeDict, self.CTETRAelemarray, self.CPENTAelemarray, self.Elemarray = \
            Elemfunction.readnas(InputnasPath)
        if not self.Elemarray.any():
            self.Elemarray = Elemfunction.findface(self.CTETRAelemarray, self.CPENTAelemarray)
        self.NormalDict, self.Quadnormaldict, self.Quadnodedict = Elemfunction.faceelemnormal(
            self.Elemarray, self.NodeDict)
        toleranceface = self.ui.spinBox_tolerance_SF.value()
        self.Comp_elemDict = Elemfunction.splitfaceelem(self.Elemarray, self.NormalDict, toleranceface)
        self.CompIfo = Elemfunction.compinitialize(self.Comp_elemDict)
        self.Comp_nodeDict = Elemfunction.splitnode(self.Comp_elemDict)
        OutputPath = self.ui.textEdit_outputfolder_SF.toPlainText()
        Elemfunction.savestl(
            OutputPath, self.Comp_elemDict, self.NormalDict, self.Quadnormaldict, self.Quadnodedict, self.NodeDict)
        self.ui.tableWidget_SF.setRowCount(len(self.CompIfo))
        Qtfunction.writetable(self.ui.tableWidget_SF, self.CompIfo)
        vtkfunction.showface(OutputPath, self.Comp_nodeDict, self.ui, self.modelui, BatchProcess)

    def vtklookcomp(self):
        OutputPath = self.ui.textEdit_outputfolder_SF.toPlainText()
        vtkfunction.showface(OutputPath, self.Comp_nodeDict, self.ui, self.modelui)

    def initializationtable(self):
        Qtfunction.writetable(self.ui.tableWidget_SF, self.CompIfo)

    def pasteTrue(self):
        Qtfunction.updatetableitem(self.ui.tableWidget_SF, 'True')

    def pasteFalse(self):
        Qtfunction.updatetableitem(self.ui.tableWidget_SF, 'False')

    def pasteLine(self):
        cunt = 0
        currentrow = self.ui.tableWidget_SF.currentRow()
        string = self.ui.tableWidget_SF.item(currentrow, cunt).text()
        lineinfo = Qtfunction.chooselineinfo(self.ui.textEdit_inputcsv_SF)
        Qtfunction.updatetableline(self.ui.tableWidget_SF, cunt, string, lineinfo)

    def pasteLumen(self):
        cunt = 6
        string = 'True'
        lineinfo = Qtfunction.chooselineinfo(self.ui.textEdit_inputcsv_SF)
        Qtfunction.updatetableline(self.ui.tableWidget_SF, cunt, string, lineinfo)

    def outputfolder(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Save directory",
                                               fileObj=self.ui,
                                               qtObj=True)
        # set filename
        self.ui.textEdit_outputfolder_SF.setPlainText(dirname)

    def calculateandsave(self):
        self.CompIfo = Qtfunction.readtable(self.ui.tableWidget_SF)
        self.CenterpointDict = Elemfunction.centerpoint(self.Comp_nodeDict, self.NodeDict)
        self.SysDict = Elemfunction.localsystem(self.Comp_nodeDict, self.CompIfo, self.NormalDict, self.Comp_elemDict,
                                                self.Nodearray, self.CenterpointDict, self.NodeDict)
        self.ElemAreaDict = Elemfunction.elemArea(self.NormalDict, self.Quadnormaldict)
        self.CompAreaDict = Elemfunction.compArea(self.CompIfo, self.Comp_elemDict, self.ElemAreaDict)
        OutputPath = self.ui.textEdit_outputfolder_SF.toPlainText()
        csvname = self.ui.textEdit_outputcsv_SF.toPlainText()
        nasname = self.ui.textEdit_outputnas_SF.toPlainText()
        Elemfunction.savecompIfo(self.CompIfo, OutputPath)
        Elemfunction.saveLumen(self.CompIfo, OutputPath)
        Elemfunction.saveareaCSV(OutputPath, csvname, self.CompIfo, self.CompAreaDict)
        Elemfunction.savenas(OutputPath, nasname, self.SysDict, self.NodeDict, self.Comp_nodeDict, self.CompIfo,
                             self.CTETRAelemarray, self.CPENTAelemarray, self.Comp_elemDict)

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_SF.setPlainText('{}'.format(filename))

    def batchrun(self,CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_SF.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')
            FindFace = False
            try:
                if info["FindFace"]:
                    FindFace = info["FindFace"]
            except:
                pass
            if FindFace:
                InputFloder = ''
                FindFaceSet = ''
                FindFaceTolerance = ''
                OutputFloder = ''
                try:
                    if info["InputFolder"]:
                        InputFloder = info["InputFolder"]
                except:
                    pass
                try:
                    if info["InputNas(FindFace)"]:
                        InputFloder = info["InputNas(FindFace)"]
                except:
                    pass
                try:
                    if info["Set(FindFace)"]:
                        FindFaceSet = info["Set(FindFace)"]
                except:
                    pass
                try:
                    if info["Tolerance(FindFace)"]:
                        FindFaceTolerance = info["Tolerance(FindFace)"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        OutputFloder = info["OutputFolder"] + '/FindFace'
                except:
                    pass
                try:
                    if info["OutputFolder(FindFace)"]:
                        OutputFloder = info["OutputFolder(FindFace)"]
                except:
                    pass
                print('FindFace InputFolder =', InputFloder)
                print('FindFace OutputFolder =', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                if FindFaceSet:
                    self.ui.textEdit_inputcsv_SF.setPlainText('{}'.format(FindFaceSet))
                self.ui.textEdit_inputnas_SF.setPlainText('{}'.format(InputFloder))
                if FindFaceTolerance:
                    self.ui.spinBox_tolerance_SF.setValue(FindFaceTolerance)
                self.ui.textEdit_outputfolder_SF.setPlainText('{}'.format(OutputFloder))
                self.ui.textEdit_outputcsv_SF.setPlainText('{}'.format('area'))
                self.ui.textEdit_outputnas_SF.setPlainText('{}'.format('CFD'))
                # Touched function
                self.findfaceandsplit('True')
                self.calculateandsave()

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\face_and_boundaryconditions.ui")
    stats = SplitFaceElem(UI=ui)
    stats.ui.show()
    app.exec_()