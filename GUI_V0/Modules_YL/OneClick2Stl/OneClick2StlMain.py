import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
import Save_Load_File
from Modules_JZ.FilterMask import FilterMaskMain
from Modules_JZ.MaskSTL import MaskSTLMain
from PySide2.QtUiTools import QUiLoader
import time

class OneClickCFD:
    def __init__(self, UI = None, Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            self.model = Hedys

        self.ui.ChooseMaskPathBtn_1_OC.clicked.connect(lambda: self.ChooseMaskPath())
        self.ui.ChooseOutDirBtn_1_OC.clicked.connect(lambda: self.ChooseOutputDir())
        self.ui.ChooseExeBtn_1_OC.clicked.connect(lambda: self.ChooseExePath())
        self.ui.ExcuteBtn_1_OC.clicked.connect(lambda: self.Mask2Stl())

        self.InitMask2Stl()

    def InitMask2Stl(self):
        self.MaskPath = None
        self.OutDir = None
        self.LumenPath = None
        self.EXEPath = None
        self.WallStlPath = None
        self.LumenStlPath =None

    def ChooseMaskPath(self):
        self.MaskPath = Save_Load_File.OpenFilePathQt(
            dispMsg='Load CTA Path',
            fileTypes='All files (*.*);; nifti files(*.nii.gz)',
            fileObj=self.ui,
            qtObj=True
        )

        self.ui.MaskPathTxt_1_OC.setPlainText(self.MaskPath)

    def ChooseOutputDir(self):
        self.OutDir = Save_Load_File.OpenDirPathQt(
            dispMsg='Choose Save Directory',
            fileObj=self.ui,
            qtObj=True
        )

        self.ui.OutputDirTxt_2_OC.setPlainText(self.OutDir)

    def ChooseExePath(self):
        self.EXEPath = Save_Load_File.OpenFilePathQt(
            dispMsg='Load MaskRecon Exe file',
            fileTypes='All files (*.*);; EXE files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        self.ui.MaskReconExePathTxt_1_OC.setPlainText(self.EXEPath)


    def Mask2Stl(self):
        self.OutDir = self.ui.OutputDirTxt_2_OC.toPlainText()
        self.MaskPath = self.ui.MaskPathTxt_1_OC.toPlainText()

        # filter lumen part, which is label 2
        filter = FilterMaskMain.FilterMask()
        # filter = self.model.filterMask()
        filter.LoadImage(path=self.MaskPath)
        filter.FilterValues(labelLst=[1], newVal=1)
        self.LumenPath = filter.SaveFile(OutDir=self.OutDir, NameRef='Lumen')

        # choose exe path
        # self.ChooseExePath()

        self.ui.MaskReconExePathTxt_1_OC.toPlainText()

        # StlMain = MaskSTLMain.MaskSTL(UI=self.UI)
        StlMain = self.model.maskSTL()
        # self.LumenStlPath = os.path.join(self.OutDir, 'lumen.stl')
        # self.WallStlPath = os.path.join(self.OutDir, 'Wall.stl')
        self.LumenStlPath = self.OutDir + '/lumen.stl'
        self.WallStlPath = self.OutDir + '/Wall.stl'

        print(self.MaskPath)
        print(self.LumenPath)
        print(self.WallStlPath)
        print(self.LumenStlPath)

        StlMain.STLGenerate(oneClick=True, inputPath=self.LumenPath, outputPath=self.LumenStlPath)
        time.sleep(5)
        
        StlMain.STLGenerate(oneClick=True, inputPath=self.MaskPath, outputPath=self.WallStlPath)

        # StlMain.STLGenerate(oneClick=True, WallPath=self.MaskPath, WallStlPath=self.WallStlPath, LumenPath=self.LumenPath, LumenStlPath=self.LumenStlPath)





