# -*- coding: UTF-8 -*-
'''
@Project ：Generate_In_File.py
@File    ：infilegneration_test.py
@IDE     ：PyCharm
@Author  ：YangChen's Piggy
@Date    ：2021/4/6 17:59
'''
import os
import sys
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
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from FileDisposing import *

########################################################################################################################
################################################# Tablewidget edit######################################################
def Current_TableWidget_txt(tabwidget):
    Cur_TbWgtxt = tabwidget.tabText(tabwidget.currentIndex())
    return Cur_TbWgtxt
 # ***************************************add table widget row **********************************************
def TableWidgetAddRow(tabwidget):
    tabwidget.insertRow(tabwidget.currentRow())
# ***************************************aremove table widget row **********************************************
def TableWidgetRmvRow(tabwidget):
    tabwidget.removeRow(tabwidget.currentRow())
# ***************************************aremove table widget row **********************************************
def TableWidgetClear(tabwidget):
    tabwidget.clearContents()

def TableInsertCombo(tabwidget,combolist,tabwidget_col):
    newcombobox = QComboBox()
    newcombobox.addItems(combolist)
    tabwidget_RNum = int(tabwidget.currentRow())
    tabwidget.insertRow(tabwidget_RNum)
    tabwidget.setCellWidget(tabwidget_RNum, tabwidget_col, newcombobox)

########################################################################################################################
################################################### Tabwidget edit######################################################
def TabAddTableWidget(Tab_widget,TableWidget_row,TableWidget_col,HorizontalHeaderList):
    Tab_count = Tab_widget.count()
    names = locals()
    names['Tab_add' + str(Tab_count + 1)] = QWidget()
    Tab_widget.addTab(names['Tab_add' + str(Tab_count + 1)], str(Tab_count + 1))
    Mylable = QLabel("Description:")
    MylineEdit = QLineEdit()
    MyTable = QTableWidget(TableWidget_row, TableWidget_col)
    MyTable.setHorizontalHeaderLabels(HorizontalHeaderList)
    MyTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    #MyTable.horizontalHeader().setResizeMode(QHeaderView.Stretch)
    MyTable.horizontalHeader().setStretchLastSection(True)
    MyTable.horizontalHeader().setDefaultSectionSize(145)
    MyTable.horizontalHeader().setMinimumSectionSize(66)
    MyTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    MyTable.verticalHeader().setDefaultSectionSize(20)
    MyTable.verticalHeader().setMinimumSectionSize(20)
    MyTable.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    Vlayout = QVBoxLayout()
    Hlayout1 = QHBoxLayout()
    Hlayout1.addWidget(Mylable)
    Hlayout1.addWidget(MylineEdit)
    Hlayout2 = QHBoxLayout()
    Hlayout2.addWidget(MyTable)
    Vlayout.addLayout(Hlayout1)
    Vlayout.addLayout(Hlayout2)
    names['Tab_add' + str(Tab_count + 1)].setLayout(Vlayout)

     # ********************************************delete  tab************************************************
def Tab_del(Tab_widget):
    Tab_widget.removeTab(Tab_widget.currentIndex())


########################################################################################################################
################################################# In file generation####################################################
class GenerateInputFile:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        # *********************************************choose .nas file*************************************************
        self.ui.chos_nasfil_GI1.clicked.connect(lambda: self.ChooseNasFile())
        self.ui.chos_nasfil_GI1.clicked.connect(lambda: self.ImportNasFile())
        # ******************************************choose analysis type*************************************************
        ######################################################Fluid#####################################################
        # *************************************choose CFD type and import master********************************************
        # self.ui.BtnGrp_GI.buttonClicked.connect(lambda: self.CFDType())
        self.ui.BtnGrp_GI.buttonClicked.connect(lambda: self.GIAnalysisModule())
        self.ui.BtnGrp_GI.buttonClicked.connect(lambda: self.FluidMaster())
        # ******************************************choose Blood material*************************************************
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.BloodMaterial())
        # ******************************************Presetting analysis parameters**************************************
        self.ui.PresettingButton_GI.clicked.connect(lambda: self.GIAnalysisModule())
        self.ui.PresettingButton_GI.clicked.connect(lambda: self.ImportNasFile())
        self.ui.PresettingButton_GI.clicked.connect(lambda: self.FluidMaster())
        self.ui.PresettingButton_GI.clicked.connect(lambda: self.ExtractEndingSetInfo())
        self.ui.ChoosetimefunctionEndingarea_GI.clicked.connect(lambda: self.TimefunctionEndingAreaFileChoosing())
        self.ui.PresettingButton_GI.clicked.connect(lambda: self.ParametersPreset())
        self.ui.ClearButton_GI2.clicked.connect(lambda: self.ParametersPresetClear())

        # ******************************************CFD Load magnitude*************************************************
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.LoadingMagnitude())
        self.ui.LMSInsertRow_GI.clicked.connect(lambda: self.TableWidgetAddRow(self.ui.tableWidget_GI4))
        self.ui.LMSDeltRow_GI.clicked.connect(lambda: self.TableWidgetRmvRow(self.ui.tableWidget_GI4))

        # ******************************************CFD apply Load *************************************************
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.GIApplyLoad())
        self.ui.ALInsertRow_GI.clicked.connect(lambda: self.TableWidgetAddRow(self.ui.ApplyLoad_GI))
        self.ui.AlDelRow_GI.clicked.connect(lambda: self.TableWidgetRmvRow(self.ui.ApplyLoad_GI))

        # ******************************************CFD wall boundary*************************************************
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.WallElst())

        ##################################################Solid Part##################################################
        # *************************************choose Solid type and import master********************************************
        self.ui.BtnGrp_GI2.buttonClicked.connect(lambda: self.GIAnalysisModule())
        self.ui.BtnGrp_GI2.buttonClicked.connect(lambda: self.SolidMaster())
        self.ui.BtnGrp_GI2.buttonClicked.connect(lambda: self.SlargeDeformation())
        ##################################################apply material##################################################
        # ********************************************TableInsertCombobox***********************************************
        self.ui.ADDmaterial_GI.clicked.connect(lambda: self.MaterialTableInsertCombo())
        # ********************************************TableDeleteCombobox***********************************************
        self.ui.Deletematerial_GI.clicked.connect(lambda: self.MaterialTableDeleteRow())
        self.ui.setmaterialGI6_2.clicked.connect(lambda: self.GIApplyMaterial())

        ##################################################apply boundary##################################################
        # ********************************************BTableInsertCombobox***********************************************
        self.ui.AddBoundaryConditionGI.clicked.connect(lambda: self.BTableInsertCombo())
        # ********************************************BTableDeleteCombobox***********************************************
        self.ui.DelBoundaryConditionGI.clicked.connect(lambda: self.BTableDeleteRow())
        self.ui.setBoundary_GI.clicked.connect(lambda: self.SBoundaryCondition())

        # ********************************************SFSI boundary***********************************************
        self.ui.FSIset_GI7_2.clicked.connect(lambda: self.SFSIBoundary())

        ##################################################Timefunction##################################################
        # ********************************************add timefuction tab***********************************************
        self.ui.Tab_add_GI.clicked.connect(lambda: self.TabAddTableWidget(self.ui.TimefunctionTabwidgetGI, 6, 2, ['Times', 'Values']))
        # *****************************************delete timefuction tab***********************************************
        self.ui.Tab_del_GI.clicked.connect(lambda: self.Tab_del(self.ui.TimefunctionTabwidgetGI))
        # *****************************************define timefuction tab***********************************************
        self.ui.TF_Tb1_imp_GI.clicked.connect(lambda: self.DfTimeFunction())

        # *********************************************Time step setting*************************************************
        # self.ui.pushButton_GI3.clicked.connect(lambda: self.Timestep())
        self.ui.TFInsertRow_GI.clicked.connect(lambda: self.TableWidgetAddRow(self.ui.Timestep_GI))
        self.ui.TMDElRow_GI.clicked.connect(lambda: self.TableWidgetRmvRow(self.ui.Timestep_GI))
        # *********************************************Fluid master result output*************************************************
        # self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.FluidMaster())
        # self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.DfTimeFunction())
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.Timestep())
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.FluidResultOutput())
        self.ui.ChooseIdbInDat.clicked.connect(lambda: self.Choosedatidbdatfil())
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.Saveidbdatfil())
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.SaveFInFil())
        self.ui.GenerateFluidfile_GI4.clicked.connect(lambda: self.GILoading_INFile())

        # *********************************************Solid master result output*************************************************
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.GIAnalysisModule())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.SolidMaster())

        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.SlargeDeformation())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.GIApplyMaterial())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.SBoundaryCondition())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.SFSIBoundary())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.Timestep())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.SResultsOutput())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.Saveidbdatfil())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.SaveSInFil())
        self.ui.GenerateSolidfile_GI.clicked.connect(lambda: self.GILoading_INFile())
        self.ui.pushButton_BatchTable_GI.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchFluid_GI.clicked.connect(lambda: self.batchrun())
        self.ui.pushButton_BatchSolid_GI.clicked.connect(lambda: self.batchsolidrun())

        self.InitGenerateInput()

    def InitGenerateInput(self):
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.statusLabel = QLabel()
        self.NasFilAbsPth= None
        self.componetIfoRem3D = None
        self.TimefunctionNamLst = None
        self.In_Fhead = None
        self.In_AnlyModule = None
        self.In_NasFilImprt = None
        self.DatFilAbsPth = None
        self.IdbFilAbsPth = None
        self.InFilAbsPth = None
        self.ADINA_AUI_FilDirectory = None
        ##fluid
        self.CFDTyp = None
        self.IN_FMaster = None
        self.In_FBloodMaterial = None
        self.In_FDfnVloct = None
        self.In_FPresur = None
        self.In_AplyLoad = None
        self.In_FSpcilBondryCondi = None
        self.Wall_elset = None
        self.In_FResltOutput = None

####solid
        self.SolidTyp = None
        self.In_SLagDfrmatn = None
        self.WallMaterialCombin = None
        self.EleGrpCombin = None
        self.ApplyBoundary =None
        self.FSI_Boundary = None
        self.Sresluts = None

        self.In_SaveDatFil = None
        self.In_SaveIdbFil = None


        self.cpu = None
        self.Memory = None
        self.InFilAbsPth = None

        self.TimeFDefine = None
        self.In_TimeStp = None
        self.TimefunctionfilDir = None

    # self.statusLabel = QLabel("Showing Progress")
    # self.ui.statusBar().addWidget(self.statusLabel, 1)
    # self.ui.statusBar().addWidget(self.progressBar, 2)
    #self.ui.statusBar().showMessage('Fluid Input File Generating...')
    ################################################ Analysis Module ###################################################
    ###############################################Choose Analysis Type#################################################
    def GIAnalysisModule(self):
        #************************************************ Head *********************************************************
        self.In_Fhead = "*\n" \
                   "DATABASE NEW SAVE=NO PROMPT=NO\n" \
                   "FEPROGRAM ADINA\n" \
                   "CONTROL FILEVERSION=V96"
        #print(self.In_Fhead)
        #*******************************************Choose Analysis Type************************************************
        #print(Current_TableWidget_txt(self.ui.tabWidget_GI1))
        if Current_TableWidget_txt(self.ui.tabWidget_GI1) == "CFD":
            self.In_AnlyModule_Pram = 'ADINA-F'
        else:
            self.In_AnlyModule_Pram = 'ADINA'
        self.In_AnlyModule = "*\n" \
                        "FEPROGRAM PROGRAM=" + self.In_AnlyModule_Pram
        #print(self.In_AnlyModule)

###################################################Nas File Import######################################################
    def ChooseNasFile(self):
        # *********************************************choose .nas file*************************************************
        NasFilAbsPth = Opening_File(self.ui,"Nas (*.nas)")
        self.ui.plainTextEdit_GI2.setPlainText(NasFilAbsPth)
    def ImportNasFile(self):
        # *********************************************import nas file**************************************************
        self.In_NasFilImprt = "*\n" \
                         "NASTRAN-ADIN FILENAME=,\n" \
                         "'%s',\n" \
                         "XY-YZ=YES BEAM=THREE SUBCASE=0 RBAR=DEFAULT RBE2=DEFAULT,\n" \
                         "NCTOLERA=0.000100000000000000 RBAR-MAT=0,\n" \
                         "RBAR-ARE=0.00000000000000 RBAR-DIA=0.00000000000000,\n" \
                         "RBAR-THI=0.00000000000000 RBE2-MAT=0 RBE2-ARE=0.00000000000000,\n" \
                         "RBE2-DIA=0.00000000000000 RBE2-THI=0.00000000000000,\n" \
                         "K=0.00000000000000 M=0.00000000000000 C=0.00000000000000,\n" \
                         "CONVERT-=NONE IN-NODE=4 OUT-NODE=8 SHELL=SHELL-CONDUCTION,\n" \
                         "BCELL=REP DUPLICAT=YES DEFAULT=AUI SPLIT=PRO ELFACESE=BCELL,\n" \
                         "NODESET=BCELL SOL=106 BCELL-ID=INDEX" % self.ui.plainTextEdit_GI2.toPlainText()

    ##################################################Time Function#####################################################
    # ********************************************Import time funcion file version_1 ************************************************
    # def DfTimeFunction(self):
    #     Tabnum = self.ui.TimefunctionTabwidgetGI.count()
    #     self.TimeFDefine = ''
    #     # ***************************************Import timefunction file .txt**********************************************
    #     for i in range(0,Tabnum):
    #         TimFunctnFilAbsPth = Opening_File(self.ui, "Txt (*.txt)")
    #         # *******************************************  Reading .eno file  ***************************************************
    #         os.chdir(Split_AbsFilePath(TimFunctnFilAbsPth)[0])
    #         TF_Fil = open(TimFunctnFilAbsPth, "r")
    #         TF_FilContxt = TF_Fil.read()  # type(TF_FilContxt)=str
    #         # print(TF_FilContxt)
    #         # ***************************************define timefunctions **********************************************
    #         TimeFunction = "*\n" \
    #                        "TIMEFUNCTION NAME=%d TYPE=MULTILINEAR EXPRESSI=''\n" \
    #                        "@CLEAR\n" \
    #                        "%s\n" \
    #                        "@" % (i+1, TF_FilContxt)  #####timefuncton name must be number
    #         self.TimeFDefine += TimeFunction
    #         TF_Fil.close()
    #    # print(self.TimeFDefine)


    ################################################# Time Step ############################################################
    def Timestep(self):
        TimeStp = '' ###############################################################################################################
        for i in range(0,self.ui.Timestep_GI.rowCount()):
            try:
                Stps = self.ui.Timestep_GI.item(i, 0).text() + ' ' + self.ui.Timestep_GI.item(i, 1).text() + "\n"
                TimeStp += Stps
            except:
               print('the content of item is blank')
        self.In_TimeStp = "*\n" \
                          "TIMESTEP NAME=DEFAULT\n" \
                          "@CLEAR\n" + TimeStp + "@"


    # ########################################################################################################################
    # ####################################################Fluid Part##########################################################
    ############################################# Fluid Master (oneway or CFD)##############################################CCCFFF
    def CFDType(self):
        self.CFDTyp = self.ui.BtnGrp_GI.checkedButton().text()
    def FluidMaster(self):
        self.CFDType()
        if self.CFDTyp == "CFD Only":
            FSISet = "NO"
        else:
            FSISet = "YES"
        self.IN_FMaster = "*\n" \
                     "MASTER ANALYSIS=TRANSIENT MODEX=EXECUTE TSTART=0.00000000000000,\n" \
                     "IDOF=1 TURBULEN=NO HYDRO=YES STREAM=NO TRACTB=DEFAULT,\n" \
                     "IRINT=DEFAULT AUTOMATI=NO SOLVER=DEFAULT COMPRESS=NO,\n" \
                     "FSINTERA=%s NMASS=0 MASSCOUP=NO MAP-OUTP=NONE MAP-FORM=NO,\n" \
                     "NONDIMEN=NO MAXSOLME=0 MTOTM=2 RECL=3000 ALE=GEOM-ELEM,\n" \
                     "THERMAL-=NO UPWINDIN=CONTROL-VOLUME MESHUPDA=ORIGINAL,\n" \
                     "MESHADAP=NO COUPLING=ITERATIVE POROUS-C=NO CELL-BCD=YES VOF=NO,\n" \
                     "FCBI=YES TURB-ITE=COUPLED EM-MODEL=NO ALE-CURV=YES,\n" \
                     "LS-TEMP-=HEAT-TRANSFER RESULTS=PORTHOLE" % FSISet
        #print(self.IN_FMaster)

    def BloodMaterial(self):
        ################################################# Fluid Blood Material #################################################
        self.In_FBloodMaterial = "*\n" \
                                 "MATERIAL CONSTF NAME=1 XMU=0.00350000000000000 CP=0.00000000000000,\n" \
                                 "XKCON=0.00000000000000 BETA=0.00000000000000 QB=0.00000000000000,\n" \
                                 "RHO=0.00106000000000000 TREF=0.00000000000000,\n" \
                                 "GRAV-X=0.00000000000000 GRAV-Y=0.00000000000000,\n" \
                                 "GRAV-Z=0.00000000000000 SIGMA=0.00000000000000,\n" \
                                 "KAPPA=1.00000000000000E+20 CV=0.00000000000000 MDESCRIP='blood',\n" \
                                 "STATE-EQ=0 MCURVE1=0 MCURVE2=0 MCURVE3=0"
        print(self.In_FBloodMaterial)
        # if self.ui.comboBox_GI.currentText() == "Blood":
        #     self.In_FBloodMaterial = "*\n" \
        #                         "MATERIAL CONSTF NAME=1 XMU=0.00350000000000000 CP=0.00000000000000,\n" \
        #                         "XKCON=0.00000000000000 BETA=0.00000000000000 QB=0.00000000000000,\n" \
        #                         "RHO=0.00106000000000000 TREF=0.00000000000000,\n" \
        #                         "GRAV-X=0.00000000000000 GRAV-Y=0.00000000000000,\n" \
        #                         "GRAV-Z=0.00000000000000 SIGMA=0.00000000000000,\n" \
        #                         "KAPPA=1.00000000000000E+20 CV=0.00000000000000 MDESCRIP='blood',\n" \
        #                         "STATE-EQ=0 MCURVE1=0 MCURVE2=0 MCURVE3=0"
        #     print(self.In_FBloodMaterial)
        #     # self.ui.plainTextEdit_GI1.appendPlainText(In_FBloodMaterial)
        # else:
        #     print("Please select the correct material"

    # def loadTimefunctionfilsAbsPathLst(self):
    #     self.TimefunctionfilsAbsPathLst = Preprocess_Mask.StrToLst(strIn=self.ui.TissueCoortxt_GI.toPlainText())["listOut"]
    #     # for eachitem in self.TissueCoorsAbsPathList:
    #     #     _, self.TissueCoorsFilNam, _ = Split_AbsFilePath(eachitem)
    #     #     self.TissueCoorsFilNameList.append(self.TissueCoorsFilNam)
    #     # return self.TissueCoorsAbsPathList, self.TissueCoorsFilNameList
    #     return self.TissueCoorsAbsPathList


    def ExtractEndingSetInfo(self):

        CompnentsWithoutTimefunctionStr = self.ui.CompnentsWithoutTimefunctionLineEdit_GI.text()
        CompnentsWithoutTimefunction = re.split(r'\W+',
                                          CompnentsWithoutTimefunctionStr)

        print(type(CompnentsWithoutTimefunction),CompnentsWithoutTimefunction)

        ################################################################################################################
        ################## Extract component correspondent property name and id from hypermesh nas file#################
        # *******************************************  Reading .eno file  ***************************************************
        self.NasFilAbsPth = self.ui.plainTextEdit_GI2.toPlainText()
        os.chdir(Split_AbsFilePath(self.NasFilAbsPth)[0])
        nas_Fil = open(self.NasFilAbsPth, "r")
        nas_FilContxt = nas_Fil.read()  # type(eno_FilContxt)=str

        # ********************************* split .nas file context by 'End of list'  **************************************
        nas_FilContxtSplit = re.split(
            r'\$\$    HyperMesh name and color information for generic components               \$',
            nas_FilContxt)  # the output result type by function 're.split' is a list
        # ******************** nas_FilContxt Retain Property And Component Module  **************************************
        nas_FilContxtRPCM = nas_FilContxtSplit[1]
        nas_FilContxtRPCMSplit = re.split(r'Property Definition for Surface and Volume Elements',
                                          nas_FilContxtRPCM)
        # ******************** nas_FilContxt Retain  Component Module  **************************************
        nas_FilContxtRCM = nas_FilContxtRPCMSplit[0]
        # print(nas_FilContxtRCM)
        #componetIfo = re.findall('\$\D+(\d+)\"(.+)\".+\".+\".+\n', nas_FilContxtRCM,
        componetIfo = re.findall('\$\D+\d+\".+\"\D+(\d+) \"(.+)\".+\n', nas_FilContxtRCM,
                                 re.M)  ##type(TetraElmnt_NdIfo)=list 匹配行头格式 (?:^|\n)行头内容.*
        print(componetIfo)
        self.componetIfoRem3D = []
        for TupleNum in range(0, len(componetIfo)):
            if componetIfo[TupleNum][1]  not in CompnentsWithoutTimefunction:
                self.componetIfoRem3D.append(componetIfo[TupleNum])
            elif componetIfo[TupleNum][1] == 'Lumen':
                self.ui.lineEditGI.setText(componetIfo[TupleNum][0])
            elif componetIfo[TupleNum][1] == 'Wall_in':
                self.ui.lineEditGI_2.setText(componetIfo[TupleNum][0])



        # print(type(componetIfo[0][1])) #setid:componetIfo[0][1] setname:componetIfo[0][0]
        # print(len(componetIfo))
        # print(componetIfo[0][1])
        print(self.componetIfoRem3D)
        nas_Fil.close()

    # def ChooseTimefunctionfils(self):
    #     # ***************************** Extract the coordinates of each components ************************************#
    #     Timefunctionfils = Opening_Files(MainWindow, "Timefunction (*.txt);;Timefunction (*.csv) ")
    #     self.TimefunctionNamLst = []
    #     for TFC in Timefunctionfils:
    #         _, TimefunctionNam, _ = Split_AbsFilePath(TFC)
    #         self.TimefunctionNamLst.append(TimefunctionNam)
    #     # print(self.TimefunctionNamLst)

        #################################################### Apply Load #######################################################
    def ParametersPresetClear(self):
        TableWidgetClear(self.ui.tableWidget_GI4)

    def TimefunctionEndingAreaFileChoosing(self):
        TimefunctionfilDir = Opening_FileDialog(self.ui)
        self.ui.timefunctionpath_GI.setPlainText(TimefunctionfilDir)

        EndAreaAbsPth = Opening_File(self.ui, "EndingArea (*.csv)")
        self.ui.EndingAreaCSVPath_GI.setPlainText(EndAreaAbsPth)

    def ParametersPreset(self):
        self.TimeFDefine = ''
        self.TimefunctionfilDir = self.ui.timefunctionpath_GI.toPlainText()
        self.EndAreaAbsPth = self.ui.EndingAreaCSVPath_GI.toPlainText()
        with open(self.EndAreaAbsPth, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]
        #print("rows", rows)
        EndingAreaDic ={}
        for rowNum in range(0,len(rows)):
            EndingAreaDic[rows[rowNum][0]] = rows[rowNum][2]#rows [['Aor_out', '151', '1246.906'], ['RPDA', '201', '6.287'], ['RPLB', '202', '4.932']....]#



        Lumne_inletStr = self.ui.lineEdit_Lumenset_GI.text()
        Lumne_inlet = re.split(r'\W+',  Lumne_inletStr)
        # ****************************************add rows with the same sizes of components************************
        self.ui.tableWidget_GI4.setRowCount(len(self.componetIfoRem3D))  # 设置表格的行数
        ##from nas file  read  set name and num basing in standard form
        # count  total set num and inset correspondent rows
        # fill the setnam and setnum with the component information in nas file
        for loadnum in range(0, len(self.componetIfoRem3D)):
            # **********************************************Load defining table Parameters preset************************
            #self.ui.tableWidget_GI4.item(loadnum, 1).setText(self.componetIfoRem3D[loadnum][1])
            self.ui.tableWidget_GI4.setItem(loadnum, 1, QTableWidgetItem(self.componetIfoRem3D[loadnum][1]))
            #self.ui.tableWidget_GI4.setItem(loadnum, 1, QTableWidgetItem("Aorta"))
            #
            if self.ui.tableWidget_GI4.item(loadnum, 1).text() in Lumne_inlet:
                self.ui.tableWidget_GI4.setItem(loadnum, 0, QTableWidgetItem("PRESSURE"))
                self.ui.tableWidget_GI4.setItem(loadnum, 7, QTableWidgetItem("1"))

            else:
                self.ui.tableWidget_GI4.setItem(loadnum, 0, QTableWidgetItem("VELOCITY"))
            self.ui.tableWidget_GI4.setItem(loadnum, 2, QTableWidgetItem(self.componetIfoRem3D[loadnum][0]))
            self.ui.tableWidget_GI4.setItem(loadnum, 3, QTableWidgetItem(self.componetIfoRem3D[loadnum][0])) #timefunciont
            # PresTimFunctnCsvFilAbsPth = self.TimefunctionfilDir + self.componetIfoRem3D[loadnum][1] + '.csv'
            PresTimFunctntxtFilAbsPth = self.TimefunctionfilDir + self.componetIfoRem3D[loadnum][1] + '.txt'
            # try:
            #     with open(PresTimFunctntxtFilAbsPth, "w") as my_output_file:
            #         with open(PresTimFunctnCsvFilAbsPth, "r") as my_input_file:
            #             [my_output_file.write(" ".join(row) + '\n') for row in csv.reader(my_input_file)]
            # except:
            #     QMessageBox.warning(self.ui,
            #                         '',
            #                         '{} don\'t has timefunction. Please fill LumneInlet with {} '.format(self.componetIfoRem3D[loadnum][1], self.componetIfoRem3D[loadnum][1])
            #                         )
            PresTF_Fil = open(PresTimFunctntxtFilAbsPth, "r")
            #PresTF_Fil = open(PresTimFunctnFilAbsPth, "r", encoding = "utf-8")
            PresTF_FilContxt = PresTF_Fil.read()  # type(TF_FilContxt)=str
            # print(TF_FilContxt)
            # ***************************************define timefunctions **********************************************
            TimeFunction = "*\n" \
                           "TIMEFUNCTION NAME=%d TYPE=MULTILINEAR EXPRESSI=''\n" \
                           "@CLEAR\n" \
                           "%s\n" \
                           "@" % (int(self.componetIfoRem3D[loadnum][0]), PresTF_FilContxt)  #####timefuncton name must be number
            self.TimeFDefine += TimeFunction
            self.ui.tableWidget_GI4.setItem(loadnum, 4, QTableWidgetItem(str(loadnum + 1 )))
            self.ui.tableWidget_GI4.setItem(loadnum, 5, QTableWidgetItem('0'))
            self.ui.tableWidget_GI4.setItem(loadnum, 6, QTableWidgetItem('0'))

            EndingArea = EndingAreaDic[self.ui.tableWidget_GI4.item(loadnum, 1).text()]
            if self.ui.tableWidget_GI4.item(loadnum, 1).text() in Lumne_inlet:
                self.ui.tableWidget_GI4.setItem(loadnum, 7, QTableWidgetItem("1"))
            else:
                self.ui.tableWidget_GI4.setItem(loadnum, 7, QTableWidgetItem(EndingArea))
            PresTF_Fil.close()

    def LoadingMagnitude(self):
        self.In_FDfnVloct = ''
        self.In_FPresur = ''
        ############################################### Fluid Define load magnitude###################################################
        for outletnum in range(0, self.ui.tableWidget_GI4.rowCount()):
            try:
                names = locals()
                names['outlet' + str(outletnum) + 'ID'] = int(self.ui.tableWidget_GI4.item(outletnum, 4).text())
                if self.ui.tableWidget_GI4.item(outletnum, 0).text() == 'VELOCITY':
                    print("yang velocity")
                    # names['outlet' + str(outletnum) + 'Nm'] = self.ui.tableWidget_GI4.item(outletnum, 0).text()
                    names['outlet' + str(outletnum) + 'BloodVx'] = float(self.ui.tableWidget_GI4.item(outletnum, 5).text())
                    names['outlet' + str(outletnum) + 'BloodVy'] = float(self.ui.tableWidget_GI4.item(outletnum, 6).text())
                    names['outlet' + str(outletnum) + 'BloodVz'] = 1 / float(self.ui.tableWidget_GI4.item(outletnum, 7).text())
                    names['outlet' + str(outletnum) + 'Velocity'] = "LOAD VELOCITY NAME=%s VX=%f VY=%f,\n" \
                                                       "VZ=%f VRX=FREE VRY=FREE VRZ=FREE DESCRIPT='NONE'\n" % (
                                                           names['outlet' + str(outletnum) + 'ID'],
                                                           names['outlet' + str(outletnum) + 'BloodVx'],
                                                           names['outlet' + str(outletnum) + 'BloodVy'],
                                                           names['outlet' + str(outletnum) + 'BloodVz'])
                    self.In_FDfnVloct += "*\n" + names['outlet' + str(outletnum) + 'Velocity']
                else:
                    ############################################### Fluid Define Pressure###################################################
                    PresurMagnitud = float(self.ui.tableWidget_GI4.item(outletnum, 7).text())
                    names['outlet' + str(outletnum) + 'Pressure'] = "LOAD PRESSURE NAME=%d MAGNITUD=%f DESCRIPT='NONE'\n" % (
                                                           names['outlet' + str(outletnum) + 'ID'],
                                                           PresurMagnitud)
                    print(names['outlet' + str(outletnum) + 'Pressure'])
                    self.In_FPresur += "*\n" + names['outlet' + str(outletnum) + 'Pressure']
                    # self.ui.plainTextEdit_GI1.appendPlainText(In_FPresur)
            except:
                print('the content of item is blank')
        self.In_FDfnVloct = self.In_FDfnVloct.rstrip()
        #print(self.In_FDfnVloct)
        #print(self.In_FPresur)
        #self.ui.plainTextEdit_GI1.appendPlainText(In_FDfnVloct)

    def GIApplyLoad(self):
        self.In_AplyLoad = ''
        for loadnum in range(0, self.ui.tableWidget_GI4.rowCount()):
            try:
                names = locals()
                names['load' + str(loadnum) + 'label'] = loadnum + 1
                names['load' + str(loadnum) + 'loadtyp'] = self.ui.tableWidget_GI4.item(loadnum, 0).text()
                names['load' + str(loadnum) + 'loadid_ap'] = int(self.ui.tableWidget_GI4.item(loadnum, 4).text())
                names['load' + str(loadnum) + 'elmentsetid'] = int(self.ui.tableWidget_GI4.item(loadnum, 2).text())
                names['load' + str(loadnum) + 'elmentsetnam'] = self.ui.tableWidget_GI4.item(loadnum, 1).text() #added by yang
                names['load' + str(loadnum) + 'TimeFunction'] = int(self.ui.tableWidget_GI4.item(loadnum, 3).text())
                names['load' + str(loadnum)] = "%d  '%s' %d  'ELEMENT-FACE' %d 0 %d 0.00000000000000 0,\n" \
                                               "0.00000000000000 0.00000000000000 0 0\n" % (names['load' + str(loadnum) + 'label'],
                                                                                            names['load' + str(loadnum) + 'loadtyp'],
                                                                                            names['load' + str(loadnum) + 'loadid_ap'],
                                                                                            names['load' + str(loadnum) + 'elmentsetid'],
                                                                                            names['load' + str(loadnum) + 'TimeFunction'])
                self.In_AplyLoad += names['load' + str(loadnum)]
            except:
                print('the content of item is blank')
        self.In_AplyLoad = "*\n" \
                      "APPLY-LOAD BODY=0\n" \
                      "@CLEAR\n" + self.In_AplyLoad + "@"
        print(self.In_AplyLoad)
        #self.ui.plainTextEdit_GI1.appendPlainText(In_AplyLoad)
    # **************************************GIApplyLoad(self) version_1*************************************************
    # def GIApplyLoad(self):
    #     self.In_AplyLoad = ''
    #     for loadnum in range(0, self.ui.ApplyLoad_GI.rowCount()):
    #         try:
    #             names = locals()
    #             names['load' + str(loadnum) + 'label'] = loadnum + 1
    #             names['load' + str(loadnum) + 'loadtyp'] = self.ui.ApplyLoad_GI.item(loadnum, 0).text()
    #             names['load' + str(loadnum) + 'loadid_ap'] = int(self.ui.ApplyLoad_GI.item(loadnum, 1).text())
    #             names['load' + str(loadnum) + 'elmentsetnum'] = int(self.ui.ApplyLoad_GI.item(loadnum, 2).text())
    #             names['load' + str(loadnum) + 'elmentsetnam'] = self.ui.ApplyLoad_GI.item(loadnum, 3).text() #added by yang
    #             names['load' + str(loadnum) + 'TimeFunction'] = int(self.ui.ApplyLoad_GI.item(loadnum, 4).text())
    #             names['load' + str(loadnum)] = "%d  '%s' %d  'ELEMENT-FACE' %d 0 %d 0.00000000000000 0,\n" \
    #                                            "0.00000000000000 0.00000000000000 0 0\n" % (names['load' + str(loadnum) + 'label'],
    #                                                                                         names['load' + str(loadnum) + 'loadtyp'],
    #                                                                                         names['load' + str(loadnum) + 'loadid_ap'],
    #                                                                                         names['load' + str(loadnum) + 'elmentsetnum'],
    #                                                                                         names['load' + str(loadnum) + 'TimeFunction'])
    #             self.In_AplyLoad += names['load' + str(loadnum)]
    #         except:
    #             print('the content of item is blank')
    #     self.In_AplyLoad = "*\n" \
    #                   "APPLY-LOAD BODY=0\n" \
    #                   "@CLEAR\n" + self.In_AplyLoad + "@"
    #     print(self.In_AplyLoad)
    #     #self.ui.plainTextEdit_GI1.appendPlainText(In_AplyLoad)

    ######################################Wall elementset###########################################
    def WallElst(self):
        self.Wall_elset = int(self.ui.lineEditGI.text())
        return self.CFDLumenBoundary()

    def CFDLumenBoundary(self):
        body = 0
        ##########################################Fluid Special Boundary Condition(CFD Only) ###################################CCCFFF
        if self.CFDTyp == "CFD Only":
            self.In_FSpcilBondryCondi = "*\n" \
                                      "BOUNDARY-CON WALL NAME=1 GTYPE=ELFACESET SLIPC=0.00000000000000,\n" \
                                      "MOVING=NO ALE-FACE=0 VTYPE=CONVENTIONAL VT=0.00000000000000,\n" \
                                      "NCURVT=0 DX=1.00000000000000 DY=0.00000000000000,\n" \
                                      "DZ=0.00000000000000 X0=0.00000000000000 Y0=0.00000000000000,\n" \
                                      "Z0=0.00000000000000 ALL-EXT=NO THERMAL=HEAT-FLUX,\n" \
                                      "TVALUE=0.00000000000000 NCURT=0 DESCRIPT='NONE' SLIP-BOU=0\n" \
                                      "@CLEAR\n" \
                                      "%d %d\n" \
                                      "@" % (self.Wall_elset, body)
            #print(In_FSpcilBondryCondiCfd)

        else:
            ##########################################Fluid Special Boundary Condition(oneway) #####################################CCCFFF
            self.In_FSpcilBondryCondi = "*\n" \
                                      "BOUNDARY-CON FLUID-STRUCTURE NAME=1 GTYPE=ELFACESET,\n" \
                                      "SLIPC=0.00000000000000 FSBOUNDA=1 VTYPE=CONVENTIONAL,\n" \
                                      "VT=0.00000000000000 NCURVT=0 DX=1.00000000000000,\n" \
                                      "DY=0.00000000000000 DZ=0.00000000000000 X0=0.00000000000000,\n" \
                                      "Y0=0.00000000000000 Z0=0.00000000000000 ALL-EXT=NO,\n" \
                                      "THERMAL=HEAT-FLUX TVALUE=0.00000000000000 NCURT=0 DESCRIPT='NONE'\n" \
                                      "@CLEAR\n" \
                                      "%d %d\n" \
                                      "@" % (self.Wall_elset, body)
            #print(In_FSpcilBondryCondiFsi)
        #self.ui.plainTextEdit_GI1.appendPlainText(self.In_FSpcilBondryCondi)

    # ############################################## Fluid Result Output #####################################################
    def FluidResultOutput(self):
        self.In_FResltOutput = "*\n" \
                          "RESULTS-ELEM NAME=1 GROUP=0 STRESS=YES FE-PRESS=NO OMEGA=NO,\n" \
                          "CELL-REY=YES CELL-PEC=YES EFFECTIV=DEFAULT HEAT-FLU=NO,\n" \
                          "HEAT-DIS=NO CURRENT-=NO FLOW-RES=YES BOUNDARY=NO"
        print(self.In_FResltOutput)
        #self.ui.plainTextEdit_GI1.appendPlainText(In_FResltOutput)

    ####################################################################################################################
    ##################################################### Solid Part ###################################################
    ####################################################Solid Part Type#################################################
    def SolidType(self):
        self.SolidTyp = self.ui.BtnGrp_GI2.checkedButton().text()

    ############################################# Solid Master (structure only or oneway)##########################
    def SolidMaster(self):
        self.SolidType()
        if self.SolidTyp == "OneWay":
            FSISet = "YES"
        else:
            FSISet = "No"
        self.IN_FMaster = "*\n" \
                     "MASTER ANALYSIS=STATIC MODEX=EXECUTE TSTART=0.00000000000000 IDOF=111,\n" \
                     "OVALIZAT=NONE FLUIDPOT=AUTOMATIC CYCLICPA=1 IPOSIT=AUTOMATIC,\n" \
                     "REACTION=YES INITIALS=NO FSINTERA=%s IRINT=DEFAULT CMASS=NO,\n" \
                     "SHELLNDO=AUTOMATIC AUTOMATI=ATS SOLVER=SPARSE,\n" \
                     "CONTACT-=CONSTRAINT-FUNCTION TRELEASE=0.00000000000000,\n" \
                     "RESTART-=NO FRACTURE=NO LOAD-CAS=NO LOAD-PEN=NO SINGULAR=YES,\n" \
                     "STIFFNES=0.000100000000000000 MAP-OUTP=NONE MAP-FORM=NO,\n" \
                     "NODAL-DE='' POROUS-C=NO ADAPTIVE=0 ZOOM-LAB=1 AXIS-CYC=0,\n" \
                     "PERIODIC=NO VECTOR-S=GEOMETRY EPSI-FIR=NO STABILIZ=NO,\n" \
                     "STABFACT=1.00000000000000E-10 RESULTS=PORTHOLE FEFCORR=NO,\n" \
                     "BOLTSTEP=1 EXTEND-S=YES CONVERT-=NO DEGEN=YES TMC-MODE=NO,\n" \
                     "IRSTEPS=1 INITIALT=NO TEMP-INT=NO ESINTERA=NO OP2GEOM=NO,\n" \
                     "INSITU-D=NO OP2ERCS=ELEMENT 2DPL-AX=YZ-Z OP2STR=DEFAULT,\n" \
                     "IRTIMES=0 OP2SAV=END OP2GAUSS=NO GENERALI=NO PDOF=YES\n"%FSISet
        #self.ui.plainTextEdit_GI1.appendPlainText(self.IN_FMaster)

    # #################################################Solid Large deformation ###############################################
    def SlargeDeformation(self):
        self.In_SLagDfrmatn = "*\n" \
                         "KINEMATICS DISPLACE=LARGE STRAINS=DEFAULT UL-FORMU=DEFAULT,\n" \
                         "PRESSURE=NO INCOMPAT=AUTOMATIC RIGIDLIN=NO BEAM-ALG=CURRENT,\n" \
                         "KBEAM-EI=NO BACKSTRE=YES"
        #self.ui.plainTextEdit_GI1.appendPlainText(self.In_SLagDfrmatn)

        ################################################MOONEY-RIVLIN material##################################################
    # def TableInsertCombo(self):
    #     materialcombobox = QComboBox()
    #     materialcombobox.addItems(['Aorta', 'Coronary', 'liquid'])
    #     ApplyMaterialGI4_2_RNum = int(self.ui.ApplyMaterialGI4_2.currentRow())
    #     self.ui.ApplyMaterialGI4_2.insertRow(ApplyMaterialGI4_2_RNum)
    #     self.ui.ApplyMaterialGI4_2.setCellWidget(ApplyMaterialGI4_2_RNum, 0, materialcombobox)
    def MaterialTableInsertCombo(self):
        TableInsertCombo(self.ui.ApplyMaterialGI4_2, ['Aorta', 'Coronary', 'Calcium', 'Thrombus', 'Lipid', 'FibrousCap'], 0)

    def MaterialTableDeleteRow(self):
        TableWidgetRmvRow(self.ui.ApplyMaterialGI4_2)

    def GIApplyMaterial(self):
        self.WallMaterialCombin = ''
        self.EleGrpCombin = ''
        Wall_MaterialsDict = {'Aorta': [70, 0, 6540, 5.88, 3.7996E+07, 1],
                              'Coronary': [138, 0, 3833, 18.803, 3.7996E+07, 1],
                              'Calcium': [1.147E+08, 0, 7.673E+07, 2.838E-8, 3.7996E+07, 1],
                              'Thrombus': [212, 0, 4260, 5.312, 3.7996E+07, 1],
                              'Lipid' : [46, 0, 4885, 5.426, 3.7996E+07, 1],
                              'FibrousCap': [186, 0, 5769, 18.219, 3.7996E+07, 1]}
        for i in range(0,(self.ui.ApplyMaterialGI4_2.rowCount())+1):
            try:
                if self.ui.ApplyMaterialGI4_2.item(i, 0):
                    ComponentMaterial = Wall_MaterialsDict[self.ui.ApplyMaterialGI4_2.item(i, 0).text()]
                elif self.ui.ApplyMaterialGI4_2.cellWidget(i, 0):
                    ComponentMaterial = Wall_MaterialsDict[(self.ui.ApplyMaterialGI4_2.cellWidget(i, 0)).currentText()]
                print(self.ui.ApplyMaterialGI4_2.item(i, 0), self.ui.ApplyMaterialGI4_2.cellWidget(i, 0))
                Wall_Material = "*\n"\
                                "MATERIAL MOONEY-RIVLIN NAME=%d C1=%f C2=%f,\n" \
                                "C3=0.00000000000000 C4=0.00000000000000 C5=0.00000000000000,\n" \
                                "C6=0.00000000000000 C7=0.00000000000000 C8=0.00000000000000,\n" \
                                "C9=0.00000000000000 D1=%f D2=%f,\n" \
                                "KAPPA=%f DENSITY=%f FITTING-=0,\n" \
                                "VISCOELA=0 TEMPERAT=NO TREF=0.00000000000000 RUBBER-T=0,\n" \
                                "RUBBER-V=0 RUBBER-M=0 RUBBER-O=0 MDESCRIP='NONE'\n" % ((i + 1),
                                                                                        ComponentMaterial[0],
                                                                                        ComponentMaterial[1],
                                                                                        ComponentMaterial[2],
                                                                                        ComponentMaterial[3],
                                                                                        ComponentMaterial[4],
                                                                                        ComponentMaterial[5])

                OriElementGroup = int(self.ui.ApplyMaterialGI4_2.item(i, 1).text())
                EleGroup = int(self.ui.ApplyMaterialGI4_2.item(i, 2).text())
                ELEM_EXPAND = 0   ##elemet expand

                if not self.ui.ApplyMaterialGI4_2.item(i, 3):
                    # ******************************************select tissue  file and load element ID**********************#
                    if self.ui.ApplyMaterialGI4_2.item(i, 0):
                        MaterialNam = self.ui.ApplyMaterialGI4_2.item(i, 0).text()
                    elif self.ui.ApplyMaterialGI4_2.cellWidget(i, 0):
                        MaterialNam = (self.ui.ApplyMaterialGI4_2.cellWidget(i, 0)).currentText()
                    QMessageBox.information(
                        self.ui,
                        '',
                        'Current Element group number is %d\nPlease select %s element information file' % (
                        EleGroup, MaterialNam)
                    )
                    tmpTissueFilePath = Opening_File(self.ui,"Tissue File (*.txt)")
                    self.ui.ApplyMaterialGI4_2.setItem(i, 3, QTableWidgetItem('{0}'.format(tmpTissueFilePath)))

                TissueFilePath = self.ui.ApplyMaterialGI4_2.item(i,3).text()
                print("TissueFilePath", TissueFilePath)
                with open(TissueFilePath, 'r') as TissueFil:
                    line = TissueFil.readlines()
                    TissueElementGroupInfo = ""
                    for line_list in line:
                        line_new = line_list.strip('\n') + '    %d'%OriElementGroup + '\n'
                        TissueElementGroupInfo += line_new
                #####################################################Apply material####################################################
                Wall_Property = "*\n"\
                                "EGROUP THREEDSOLID NAME=%d DISPLACE=DEFAULT STRAINS=DEFAULT MATERIAL=%d,\n" \
                                "RSINT=DEFAULT TINT=DEFAULT RESULTS=STRESSES DEGEN=DEFAUL,\n" \
                                "FORMULAT=0 STRESSRE=GLOBAL INITIALS=NONE FRACTUR=NO,\n" \
                                "CMASS=DEFAULT STRAIN-F=0 UL-FORMU=DEFAULT LVUS1=0 LVUS2=0 SED=NO,\n" \
                                "RUPTURE=ADINA INCOMPAT=YES TIME-OFF=0.00000000000000 POROUS=NO,\n" \
                                "WTMC=1.00000000000000 OPTION=NONE DESCRIPT='NONE' PRINT=DEFAULT,\n" \
                                "SAVE=DEFAULT TBIRTH=0.00000000000000 TDEATH=0.00000000000000,\n" \
                                "TMC-MATE=1 RUPTURE-=0 EM=NO JOULE=NO BOLT-NUM=0 BOLT-PLA=0,\n" \
                                "BOLT-LOA=0.00000000000000 BOLT-TOL=0.00000000000000,\n" \
                                "TETINT=DEFAULT\n" \
                                "*\n" \
                                "EDATA SUBSTRUC=0 GROUP=%d UNDEFINE=IGNORE\n" \
                                "*\n" \
                                "ELMOVE FROM=0 TO=%d OPTION=ELEM EXPAND=%d DELETE-E=YES\n" \
                                "@CLEAR\n" \
                                "%s"\
                                "@\n"  %(EleGroup, (i + 1), EleGroup, EleGroup, ELEM_EXPAND,TissueElementGroupInfo)
                self.WallMaterialCombin += Wall_Material
                self.EleGrpCombin += Wall_Property
            except:
                print('1the content of item is blank')
        # self.WallMaterialCombin = "*\n" + WallMaterialCombin
        # self.EleGrpCombin = "*\n" + EleGrpCombin
        #print(ApplyMaterial)
        #self.ui.plainTextEdit_GI1.appendPlainText(self.WallMaterialCombin)
        #self.ui.plainTextEdit_GI1.appendPlainText(self.EleGrpCombin)

    ############################################ Inlet Outlet Boundary Conditon ############################################
    def BTableInsertCombo(self):
        TableInsertCombo(self.ui.SBoundary_GI, ['All', 'Pressure'], 0)

    def BTableDeleteRow(self):
        TableWidgetRmvRow(self.ui.SBoundary_GI)

    def SBoundaryCondition(self):
        self.ApplyBoundary = ''
        for i in range(0, (self.ui.SBoundary_GI.rowCount()) + 1):
            try:
                if self.ui.SBoundary_GI.item(i, 0):
                    BoundaryType = self.ui.SBoundary_GI.item(i, 0).text()
                elif self.ui.SBoundary_GI.cellWidget(i, 0):
                    BoundaryType = (self.ui.SBoundary_GI.cellWidget(i, 0)).currentText()

                BEleSet = int(self.ui.SBoundary_GI.item(i, 1).text())
                SBoundary =     "%d  '%s'\n" %(BEleSet, BoundaryType)
                # print("BoundaryType", BoundaryType, i, SBoundary)
                print("BoundaryType", BoundaryType, i)
                self.ApplyBoundary += SBoundary
            except:
                print('the content of item is blank')
        self. ApplyBoundary = "*\n" \
                        "FIXBOUNDARY ELFACESE FIXITY=ALL\n" \
                        "@CLEAR\n" + self.ApplyBoundary + "@"
        #self.ui.plainTextEdit_GI1.appendPlainText(self.ApplyBoundary)

    def SFSIBoundary(self):
        ################################################### FSI Boundary Conditon ##############################################
        FSIBE = int(self.ui.lineEditGI_2.text())
        self.FSI_Boundary = "*\n" \
                       "FSBOUNDARY ELFACE NAME=1\n" \
                       "@CLEAR\n" \
                       "%d\n" \
                       "@" % FSIBE
        #self.ui.plainTextEdit_GI1.appendPlainText(self.FSI_Boundary)

    def SResultsOutput(self):
        ################################################### Results Output #####################################################
        self.Sresluts = "*\n" \
                  "RESULTS-ELEM NAME=1 GROUP=0 LOCATION=INTEGRATION STRESS=ALL,\n" \
                  "STRAIN=ALL INELASTI=NO THERMAL=NO ENERGY=NO ELECTROM=NO,\n" \
                  "USER-VAR=NO MISCELLA=NO"
        #self.ui.plainTextEdit_GI1.appendPlainText(self.Sresluts)

        #############################n####################   Save solid .in file #####################################################
    # def SaveSolidInFil(self):
    #     self.InFilAbsPth = QFileDialog.getSaveFileName(self.ui, "Save Input file", "", "In Files (*.in)")[0]
    #     infilcontext = self.ui.plainTextEdit_GI1.toPlainText()
    #     with open("%s" % self.InFilAbsPth, "w") as in_file:
    #         in_file.write("%s" % infilcontext)
    #     return self.InFilAbsPth
    def Choosedatidbdatfil(self):
        DatFilAbsPth = QFileDialog.getSaveFileName(self.ui, "Save Dat file", "", "Dat Files (*.dat)")[0]
        self.ui.DatPath_GI.setPlainText(DatFilAbsPth)

        IdbFilAbsPth = QFileDialog.getSaveFileName(self.ui, "Save Idb file", "", "Idb Files (*.idb)")[0]
        self.ui.IdbPath_GI.setPlainText(IdbFilAbsPth)

        InFilAbsPth = QFileDialog.getSaveFileName(self.ui, "Save Input file", "", "In Files (*.in)")[0]
        self.ui.InPath_GI.setPlainText(InFilAbsPth)

        ADINA_AUI_FilDirectory = Opening_File(self.ui, "*(AUI.exe)")
        self.ui.AUIPath_GI.setPlainText(ADINA_AUI_FilDirectory)

    def Saveidbdatfil(self):
        if Current_TableWidget_txt(self.ui.tabWidget_GI1) == "CFD":
            DatSolver = 'ADINA-F'
        else:
            DatSolver = 'ADINA'
        # DatFilAbsPth = Opening_FileDialog(self.ui)
        # QMessageBox.information(
        #     self.ui,
        #     '',
        #     'Please save Adina File!'
        # )
        self.DatFilAbsPth = self.ui.DatPath_GI.toPlainText()
        # DatFilAbsPth = QFileDialog.getSaveFileName()[0]
        print('DatFilAbsPth= ', self.DatFilAbsPth)
        print(type(self.DatFilAbsPth))
        ###################################################  Save .dat file ####################################################FFFSSS
        # DatFilAbsPth = 'D:/1adinatest/QD_Aneurysm_fluid.dat'
        self.In_SaveDatFil = "*\n" \
                         "%s OPTIMIZE=SOLVER FILE= '%s' OVERWRITE=YES OPTIMIZE=YES" % (DatSolver, self.DatFilAbsPth)
        print(self.In_SaveDatFil)
        #self.ui.plainTextEdit_GI1.appendPlainText(self.In_SaveDatFil)

        #################################################   Save .idb file #####################################################
        self.IdbFilAbsPth = self.ui.IdbPath_GI.toPlainText()
        # IdbFilAbsPth = 'D:/1adinatest/QD_Aneurysm_fluid.idb'
        self.In_SaveIdbFil = "*\n" \
                         "DATABASE SAVE PERMFILE= '%s' PROMPT=NO" % self.IdbFilAbsPth
        print(self.In_SaveIdbFil)
        #self.ui.plainTextEdit_GI1.appendPlainText(In_SaveIdbFil)

        #############################n####################   Save fluid .in file #####################################################

    def SaveFInFil(self):
        self.InFilAbsPth = self.ui.InPath_GI.toPlainText()
        self.statusLabel.setText("Fluid Input File Generating...")
        self.ui.statusBar().addWidget(self.statusLabel, 1)
        self.ui.statusBar().addWidget(self.progressBar, 2)
        self.progressBar.reset()
        self.progressBar.setRange(1, 14)
        self.ui.plainTextEdit_GI1.clear()
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_Fhead)
        self.progressBar.setValue(1)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_AnlyModule)
        self.progressBar.setValue(2)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_NasFilImprt)
        self.progressBar.setValue(3)
        self.ui.plainTextEdit_GI1.appendPlainText(self.IN_FMaster)
        self.progressBar.setValue(4)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_FBloodMaterial)
        self.progressBar.setValue(5)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_TimeStp)
        self.progressBar.setValue(6)
        #***we only set timefunction in CFD analysis,in wall analysis, we only apply pressure on the wall inner surface**
        self.ui.plainTextEdit_GI1.appendPlainText(self.TimeFDefine)
        self.progressBar.setValue(7)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_FSpcilBondryCondi)
        self.progressBar.setValue(8)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_FDfnVloct)
        self.progressBar.setValue(9)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_FPresur)
        self.progressBar.setValue(10)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_AplyLoad)
        self.progressBar.setValue(11)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_FResltOutput)
        self.progressBar.setValue(12)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_SaveDatFil)
        self.progressBar.setValue(13)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_SaveIdbFil)
        self.progressBar.setValue(14)
        infilcontext = self.ui.plainTextEdit_GI1.toPlainText()
        with open("%s" % self.InFilAbsPth, "w") as in_file:
            in_file.write("%s" % infilcontext)
        return self.InFilAbsPth


    def SaveSInFil(self):
        self.InFilAbsPth = self.ui.InPath_GI.toPlainText()
        self.statusLabel.setText("Solid Input File Generating...")
        self.ui.statusBar().addWidget(self.statusLabel, 1)
        self.ui.statusBar().addWidget(self.progressBar, 2)
        self.progressBar.reset()
        self.progressBar.setRange(1, 13)
        self.ui.plainTextEdit_GI1.clear()
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_Fhead)
        self.progressBar.setValue(1)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_AnlyModule)
        self.progressBar.setValue(2)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_NasFilImprt)
        self.progressBar.setValue(3)
        self.ui.plainTextEdit_GI1.appendPlainText(self.IN_FMaster)
        self.progressBar.setValue(4)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_SLagDfrmatn)
        self.progressBar.setValue(5)
        self.ui.plainTextEdit_GI1.appendPlainText(self.WallMaterialCombin)
        self.progressBar.setValue(6)
        self.ui.plainTextEdit_GI1.appendPlainText(self.EleGrpCombin)
        self.progressBar.setValue(7)
        self.ui.plainTextEdit_GI1.appendPlainText(self.ApplyBoundary)
        self.progressBar.setValue(8)
        self.ui.plainTextEdit_GI1.appendPlainText(self.FSI_Boundary)
        self.progressBar.setValue(9)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_TimeStp)
        self.progressBar.setValue(10)
        self.ui.plainTextEdit_GI1.appendPlainText(self.Sresluts)
        self.progressBar.setValue(11)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_SaveDatFil)
        self.progressBar.setValue(12)
        self.ui.plainTextEdit_GI1.appendPlainText(self.In_SaveIdbFil)
        self.progressBar.setValue(13)
        infilcontext = self.ui.plainTextEdit_GI1.toPlainText()
        with open("%s" % self.InFilAbsPth, "w") as in_file:
            in_file.write("%s" % infilcontext)
        return self.InFilAbsPth

    ####################################################################################################################
    ###################################### submit in file  ############################################
    def GIAUIDir(self):
        # *******************************************Obtain ADINA AUI.exe FilDirectory *********************************
        self.ADINA_AUI_FilDirectory = self.ui.AUIPath_GI.toPlainText()
    def GICpuStrorage(self):
        self.cpu = int(self.ui.lineEdit_GI1.text())
        self.Memory = int(self.ui.lineEdit_GI2.text())
        return self.cpu,self.Memory

    def GILoading_INFile(self):
        self.statusLabel.setText("Adina Files Generating...")
        self.ui.statusBar().addWidget(self.statusLabel, 1)
        self.ui.statusBar().addWidget(self.progressBar, 2)
        self.progressBar.reset()
        self.progressBar.setRange(1, 5)
        self.GIAUIDir()
        self.progressBar.setValue(1)
        self.GICpuStrorage()
        self.progressBar.setValue(2)
        ###################################### Loading  .in file in ADINA_AUI  ############################################
        # **************************** Writing a .bat(command file by windows)  to load .in  *******************************
        ADINA_AUI_Batch = self.ADINA_AUI_FilDirectory + ' -b -m %dgb -t %d '%(self.Memory,self.cpu) + self.InFilAbsPth######################################
        self.progressBar.setValue(3)
        print(ADINA_AUI_Batch)
        ADINA_AUI_Batch_FilAbsPth = self.InFilAbsPth + "ADINA_AUI_Batch.bat"
        self.progressBar.setValue(4)
        with open(ADINA_AUI_Batch_FilAbsPth, 'w') as f:
            f.write(ADINA_AUI_Batch)
        # *******************************************  run .bat to load .plo  ***********************************************
        os.system(ADINA_AUI_Batch_FilAbsPth)
        self.statusLabel.setText("Done")
        self.progressBar.setValue(5)

        # *******************  run CFD .dat with adinaf.exe ********************

        ADINA_CFD_Batch = self.ADINA_AUI_FilDirectory + ' -b -m %dgb -t %d ' % (
            self.Memory, self.cpu) + self.InFilAbsPth



        # c:\adinaNN\x64\adina.exe -b -s -mm 100mw -t 2 prob02.dat

 # def UpdateMsgLog(self, msg=""):
    #     # Date and time
    #     nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
    #     disp = "##############" \
    #            + nowStr \
    #            + "############## \n" \
    #            + msg \
    #            + "\n############################\n"
    #
    #     # update log and display message
    #     self.ui.plainTextEdit_Message.setPlainText(disp)
    #     self.ui.plainTextEdit_Log.appendPlainText(disp)

# class tstnas:
#     def ExtractEndingSetInfor(self):
#         ################################################################################################################
#         ################## Extract component correspondent property name and id from hypermesh nas file#################
#         # *******************************************  Reading .eno file  ***************************************************
#         os.chdir(Split_AbsFilePath(r"G:\Desktop\tstnastran\cfdname.nas")[0])
#         nas_Fil = open(r"G:\Desktop\tstnastran\cfdname.nas", "r")
#         nas_FilContxt = nas_Fil.read()  # type(eno_FilContxt)=str
#
#         # ********************************* split .nas file context by 'End of list'  **************************************
#         nas_FilContxtSplit = re.split(r'\$\$    HyperMesh name and color information for generic components               \$',
#                                         nas_FilContxt)  # the output result type by function 're.split' is a list
#         # ******************** nas_FilContxt Retain Property And Component Module  **************************************
#         nas_FilContxtRPCM = nas_FilContxtSplit[1]
#         nas_FilContxtRPCMSplit = re.split(r'Property Definition for Surface and Volume Elements',
#                                         nas_FilContxtRPCM)
#         # ******************** nas_FilContxt Retain  Component Module  **************************************
#         nas_FilContxtRCM = nas_FilContxtRPCMSplit[0]
#         # print(nas_FilContxtRCM)
#         componetIfo = re.findall('(?:(?:^|\n) (?:\$\D+\d+)(?:\")\D+(?:\"\D+)\d+(?:\D+\d+\D+)\n)', nas_FilContxtRCM,
#                                       re.M)  ##type(TetraElmnt_NdIfo)=list 匹配行头格式 (?:^|\n)行头内容.*
#         componetIfo = re.findall('\$.+\d+\D+(\d+)\"(\D+)\".+\d+\D+\n', nas_FilContxtRCM,
#                                  re.M)  ##type(TetraElmnt_NdIfo)=list 匹配行头格式 (?:^|\n)行头内容.*
#         print(type(componetIfo[0][1]))
#         print(len(componetIfo))
#         print(componetIfo[0][1])
#
#     def ChooseTimefunctionfils(self):
#         # ***************************** Extract the coordinates of each components ************************************#
#         Timefunctionfils = Opening_Files(MainWindow, "Timefunction (*.txt);;Timefunction (*.csv) ")
#         self.TimefunctionNamLst = []
#         for TFC in Timefunctionfils:
#             _, TimefunctionNam, _ = Split_AbsFilePath(TFC)
#             self.TimefunctionNamLst.append(TimefunctionNam)
#         #print(self.TimefunctionNamLst)
#
#     def loadTimefunctionfilsAbsPathLst(self):
#         self.TissueCoorsAbsPathList = Preprocess_Mask.StrToLst(strIn=self.ui.TissueCoortxt_GI.toPlainText())["listOut"]
#         # for eachitem in self.TissueCoorsAbsPathList:
#         #     _, self.TissueCoorsFilNam, _ = Split_AbsFilePath(eachitem)
#         #     self.TissueCoorsFilNameList.append(self.TissueCoorsFilNam)
#         #return self.TissueCoorsAbsPathList, self.TissueCoorsFilNameList
#         return self.TissueCoorsAbsPathList
#
# if __name__ == "__main__":
#     app = QApplication([])
#     MainWindow = QMainWindow()
#
#     nastst = tstnas()
#     nastst.ChooseTimefunctionfils()
#
#     MainWindow.show()
#     app.exec_()

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_GI.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_GI.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            GenerateInput = False
            try:
                if info["GenerateInput"]:
                    GenerateInput = info["GenerateInput"]
            except:
                pass
            if GenerateInput:
                InputFloder = ''
                OutputFloder = ''
                Inlet = ''
                CopnetWithouttimefuntion = ''
                EndingAreaCSV = ''
                TimeFunctionInputFloder = ''
                GenerateInputTimeStep = ''
                AUIPath = ''
                try:
                    if info["CompIfoPath(GenerateInput)"]:
                        CompIfo = pdfunction.readexcel(info["CompIfoPath(GenerateInput)"])
                        Inletlist = []
                        CopWithouttimefuntionlist = []
                        for k in range(len(CompIfo)):
                            compinfo = CompIfo.iloc[k]
                            print('compinfo', compinfo)
                            if compinfo["Type"] == 'Fluid_inlet':
                                Inletlist.append(compinfo["CompName"])
                            elif compinfo["Type"] == 'Fluid_outlet':
                                pass
                            else:
                                CopWithouttimefuntionlist.append(compinfo["CompName"])
                        Inletlist = list(set(Inletlist))
                        CopWithouttimefuntionlist = list(set(CopWithouttimefuntionlist))
                        Inlet = ','.join(Inletlist)
                        CopnetWithouttimefuntion = ','.join(CopWithouttimefuntionlist)
                except:
                    pass
                try:
                    if info["InputFolder"]:
                        InputFloder = info["InputFolder"]
                except:
                    pass
                try:
                    if info["InputNas(GenerateInput)"]:
                        InputFloder = info["InputNas(GenerateInput)"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        OutputFloder = info["OutputFolder"] + '/ADINA'
                except:
                    pass
                try:
                    if info["OutputFolder(GenerateInput)"]:
                        OutputFloder = info["OutputFolder(GenerateInput)"]
                except:
                    pass
                try:
                    if info["TimeStep(GenerateInput)"]:
                        GenerateInputTimeStep = info["TimeStep(GenerateInput)"]
                except:
                    pass
                try:
                    if info["Component Without Timefuntion(GenerateInput)"]:
                        CopnetWithouttimefuntion = info["Component Without Timefuntion(GenerateInput)"]
                except:
                    pass
                try:
                    if info["Inlet(GenerateInput)"]:
                        Inlet = info["Inlet(GenerateInput)"]
                except:
                    pass
                try:
                    if info["TimeFunction(GenerateInput)"]:
                        TimeFunctionInputFloder = info["TimeFunction(GenerateInput)"]
                except:
                    pass
                try:
                    if info["EndingArea(GenerateInput)"]:
                        EndingAreaCSV = info["EndingArea(GenerateInput)"]
                except:
                    pass
                try:
                    if info["AUIPath"]:
                        AUIPath = info["AUIPath"]
                except:
                    pass

                print('GenerateInput InputFloder=', InputFloder)
                print('GenerateInput OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                self.ui.tabWidget_GI1.setCurrentWidget(self.ui.CFD_GI)
                # set ui
                self.ui.plainTextEdit_GI2.setPlainText('{}'.format(InputFloder))
                if TimeFunctionInputFloder:
                    self.ui.timefunctionpath_GI.setPlainText('{}/'.format(TimeFunctionInputFloder))
                if CopnetWithouttimefuntion:
                    self.ui.CompnentsWithoutTimefunctionLineEdit_GI.setText('{}'.format(CopnetWithouttimefuntion))
                if Inlet:
                    self.ui.lineEdit_Lumenset_GI.setText('{}'.format(Inlet))
                if EndingAreaCSV:
                    self.ui.EndingAreaCSVPath_GI.setPlainText('{}'.format(EndingAreaCSV))
                if GenerateInputTimeStep:
                    TimeStep = pdfunction.readexcel(GenerateInputTimeStep)
                    TimeSteplist = TimeStep.values.tolist()
                    self.ui.Timestep_GI.setRowCount(len(TimeStep))
                    for k in range(self.ui.Timestep_GI.rowCount()):
                        for j in range(self.ui.Timestep_GI.columnCount()):
                            if j == 0:
                                number = int(TimeSteplist[k][j])
                            else:
                                number = TimeSteplist[k][j]
                            self.ui.Timestep_GI.setItem(k, j, QTableWidgetItem('{0}'.format(number)))
                self.ui.DatPath_GI.setPlainText('{}'.format(OutputFloder + '/CFD.dat'))
                self.ui.IdbPath_GI.setPlainText('{}'.format(OutputFloder + '/CFD.idb'))
                self.ui.InPath_GI.setPlainText('{}'.format(OutputFloder + '/CFD.in'))
                if AUIPath:
                    self.ui.AUIPath_GI.setPlainText('{}'.format(AUIPath))

                # Touched function Fluid
                self.GIAnalysisModule()
                self.ImportNasFile()
                self.FluidMaster()
                self.BloodMaterial()
                self.ExtractEndingSetInfo()
                self.ParametersPreset()
                self.LoadingMagnitude()
                self.GIApplyLoad()
                self.WallElst()
                self.Timestep()
                self.FluidResultOutput()
                self.Saveidbdatfil()
                self.SaveFInFil()
                self.GILoading_INFile()
                self.InitGenerateInput()

    def batchsolidrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_GI.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            GenerateInput = False
            try:
                if info["GenerateInput"]:
                    GenerateInput = info["GenerateInput"]
            except:
                pass
            if GenerateInput:
                InputFloder = ''
                OutputFloder = ''
                TissueElemIdPath = ''
                solidcompid = '1'
                FSBOUNDARY = '53'
                boundarylist = []
                Materiallist = []
                GenerateInputTimeStep = ''
                AUIPath = ''
                if info["CompIfoPath(GenerateInput)"]:
                    CompIfo = pdfunction.readexcel(info["CompIfoPath(GenerateInput)"])
                    for k in range(len(CompIfo)):
                        compinfo = CompIfo.iloc[k]
                        print('compinfo',compinfo)
                        if compinfo["Property"] == 'PSOLID':
                            solidcompid = compinfo[0]
                        else:
                            if compinfo["Type"] == 'Solid_outlet':
                                boundarylist.append([])
                                boundarylist[-1].append('All')
                                boundarylist[-1].append(compinfo[0])
                            if compinfo["Type"] == 'Solid_inlet':
                                boundarylist.append([])
                                boundarylist[-1].append('All')
                                boundarylist[-1].append(compinfo[0])
                            if compinfo["Type"] == 'Solid_inlumen':
                                boundarylist.append([])
                                boundarylist[-1].append('Pressure')
                                boundarylist[-1].append(compinfo[0])
                            if compinfo["Type"] == 'Solid_outlumen':
                                FSBOUNDARY = compinfo[0]
                    # 嵌套列表去重
                    boundarylist = [list(t) for t in set(tuple(_) for _ in boundarylist)]
                try:
                    if info["InputFolder"]:
                        InputFloder = info["InputFolder"]
                except:
                    pass
                try:
                    if info["InputNas(GenerateInput)"]:
                        InputFloder = info["InputNas(GenerateInput)"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        OutputFloder = info["OutputFolder"] + '/ADINA'
                except:
                    pass
                try:
                    if info["OutputFolder(GenerateInput)"]:
                        OutputFloder = info["OutputFolder(GenerateInput)"]
                except:
                    pass
                try:
                    if info["Boundaryset(GenerateInput)"]:
                        boundaryDF = pdfunction.readexcel(info["Boundaryset(GenerateInput)"])
                        boundarylist = boundaryDF.values.tolist()
                except:
                    pass
                try:
                    if info["FSBOUNDARY(GenerateInput)"]:
                        FSBOUNDARY = info["FSBOUNDARY(GenerateInput)"]
                except:
                    pass
                try:
                    if info["TissueElemIdPath(GenerateInput)"]:
                        TissueElemIdPath = info["TissueElemIdPath(GenerateInput)"]
                except:
                    pass
                if TissueElemIdPath:
                    TissueElemIdPathlist = []
                    for home, dirs, files in os.walk(TissueElemIdPath):
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
                            Materiallist[-1].append(TissueElemIdPath + '/' + i)
                        if i.endswith('3_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('Calcium')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append('6')
                            Materiallist[-1].append(TissueElemIdPath + '/' + i)
                        if i.endswith('4_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('Thrombus')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append('7')
                            Materiallist[-1].append(TissueElemIdPath + '/' + i)
                        if i.endswith('5_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('Lipid')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append('8')
                            Materiallist[-1].append(TissueElemIdPath + '/' + i)
                        if i.endswith('6_2dndarr.txt'):
                            Materiallist.append([])
                            Materiallist[-1].append('FibrousCap')
                            Materiallist[-1].append(solidcompid)
                            Materiallist[-1].append('9')
                            Materiallist[-1].append(TissueElemIdPath + '/' + i)
                try:
                    if info["Materialset(GenerateInput)"]:
                        MaterialDF = pdfunction.readexcel(info["Materialset(GenerateInput)"])
                        Materiallist = MaterialDF.values.tolist()
                except:
                    pass
                try:
                    if info["TimeStep(GenerateInput)"]:
                        GenerateInputTimeStep = info["TimeStep(GenerateInput)"]
                except:
                    pass
                try:
                    if info["AUIPath"]:
                        AUIPath = info["AUIPath"]
                except:
                    pass
                print('GenerateInput InputFloder=', InputFloder)
                print('GenerateInput OutputFloder=', OutputFloder)
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
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
                if GenerateInputTimeStep:
                    TimeStep = pdfunction.readexcel(GenerateInputTimeStep)
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
                if AUIPath:
                    self.ui.AUIPath_GI.setPlainText('{}'.format(AUIPath))
                # Touched function Solid
                self.ImportNasFile()
                self.GIAnalysisModule()
                self.SolidMaster()
                self.SlargeDeformation()
                self.GIApplyMaterial()
                self.SBoundaryCondition()
                self.SFSIBoundary()
                self.Timestep()
                self.SResultsOutput()
                self.Saveidbdatfil()
                self.SaveSInFil()
                self.GILoading_INFile()
