import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
import Save_Load_File
import Preprocess_Mask
import pdfunction
import struct
import ast
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *

class StackSTL():
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.pushButton_inPath_SSTLZ.clicked.connect(lambda: self.chooseIn())
        self.ui.pushButton_addinPath_SSTLZ.clicked.connect(lambda: self.AddIn())
        self.ui.pushButton_outPath_SSTLZ.clicked.connect(lambda: self.chooseOut())
        self.ui.pushButton_stack_SSTLZ.clicked.connect(lambda: self.stack())
        self.ui.pushButton_batch_SSTLZ.clicked.connect(lambda: self.chooseBatchTable())
        self.ui.pushButton_batchstack_SSTLZ.clicked.connect(lambda: self.batchrun())

    def chooseBatchTable(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; csv files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_batch_SSTLZ.setPlainText('{}'.format(filename))

    def chooseIn(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose stl file",
                                                 fileTypes="All files (*.*);; stl files(*.stl)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_inPath_SSTLZ.setPlainText('{},'.format(filename))

    def AddIn(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose stl file",
                                                 fileTypes="All files (*.*);; stl files(*.stl)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_inPath_SSTLZ.appendPlainText('{},'.format(filename))

    def chooseOut(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Output STL file path",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; STL files (*.stl) ;; ",
                                                 qtObj=True)
        # set filename
        self.ui.plainTextEdit_outPath_SSTLZ.setPlainText(filename)

    def stack(self):
        infails = Preprocess_Mask.StrToLst(strIn=self.ui.plainTextEdit_inPath_SSTLZ.toPlainText())["listOut"]
        outPath = self.ui.plainTextEdit_outPath_SSTLZ.toPlainText()

        print('infails',infails)
        print('outPath',outPath)

        for infail in infails:
            stl = open(infail,'rb')
            data = stl.read()
            stl.close()
            # print(data)
            out = open(outPath, 'a')
            if data.startswith(b"solid"):
                stl = open(infail, 'r')
                data = stl.read()
                stl.close()
                out.write(data)
            else:
                out.write("solid ")
                out.write("\n")
                number = data[80:84]
                faces = struct.unpack('I', number)[0]
                for x in range(0, faces):
                    out.write("facet normal ")
                    xc = data[84 + x * 50: (84 + x * 50) + 4]
                    yc = data[88 + x * 50: (88 + x * 50) + 4]
                    zc = data[92 + x * 50: (92 + x * 50) + 4]
                    out.write(str(struct.unpack('f', xc)[0]) + " ")
                    out.write(str(struct.unpack('f', yc)[0]) + " ")
                    out.write(str(struct.unpack('f', zc)[0]) + "\n")
                    out.write("outer loop\n")
                    for y in range(1, 4):
                        out.write("vertex ")
                        xc = data[84 + y * 12 + x * 50: (84 + y * 12 + x * 50) + 4]
                        yc = data[88 + y * 12 + x * 50: (88 + y * 12 + x * 50) + 4]
                        zc = data[92 + y * 12 + x * 50: (92 + y * 12 + x * 50) + 4]
                        out.write(str(struct.unpack('f', xc)[0]) + " ")
                        out.write(str(struct.unpack('f', yc)[0]) + " ")
                        out.write(str(struct.unpack('f', zc)[0]) + "\n")
                    out.write("endloop\n")
                    out.write("endfacet\n")
                out.write(f"endsolid \n")
            out.close()

    def batchrun(self,CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_batch_SSTLZ.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for linenum in range(len(DF)):
            # get line of table
            print('get info in line', linenum)
            info = DF.iloc[linenum].fillna('')

            OutPath = ''
            InPathlist = []
            for key, value in info.items():
                if "InPath" in key:
                    InPathlist.append(value)
            InPath = ','.join(InPathlist)
            try:
                if info["OutPath"]:
                    OutPath = info["OutPath"]
            except:
                pass
            # change tab
            if self.modelui:
                self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
            # set ui
            self.ui.plainTextEdit_inPath_SSTLZ.setPlainText('{}'.format(InPath))
            self.ui.plainTextEdit_outPath_SSTLZ.setPlainText('{}'.format(OutPath))
            # Touched function
            self.stack()

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\StackSTL.ui")
    stats = StackSTL(UI=ui)
    stats.ui.show()
    app.exec_()