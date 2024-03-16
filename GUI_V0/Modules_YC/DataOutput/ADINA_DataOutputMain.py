#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：1
@File    ：GUIDATO_test.py
@IDE     ：PyCharm
@Author  ：yang's piggy
@Date    ：2021/4/4 21:18
'''
# -*- coding: UTF-8 -*-
# import os
# envpath = r'D:\Anaconda3\envs\Vista_Side2\lib\site-packages\PySide2\plugins\platforms'
# os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = envpath

import numpy as np
import os
import os.path
import re
import time
import sys

# Standard libs
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide2.QtUiTools import QUiLoader
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_YC')
sys.path.insert(0, '../Functions_AZ')
sys.path.insert(0, '../Functions_JZ')
from FileDisposing import *
import pdfunction
import Save_Load_File
########################################################################################################################
#################################################Opening_File###########################################################
def Opening_File(MainWindow,Fil_Formt):
    FilDialog = QFileDialog(MainWindow)
    FilDirectory = FilDialog.getOpenFileName(MainWindow, "Open File", "", Fil_Formt)  #"Por (*.por)"
    FilAbsPth = FilDirectory[0]
    if FilAbsPth:
        return  FilAbsPth
    else:
        print("IOError:No such file or directory")

########################################################################################################################
#################################################Opening_Files###########################################################
def Opening_Files(MainWindow,Fil_Formt):
    FilDirectorys,_  = QFileDialog.getOpenFileNames(MainWindow, "Open File", "", Fil_Formt)  #"Por (*.por)"
    #FilAbsPth = FilDirectorys[0]
    # if FilAbsPth:
    #     return  FilAbsPth
    # else:
    #     print("IOError:No such file or directory")
    return FilDirectorys

########################################################################################################################
###############################################Opening_FileDialog#######################################################
def Opening_FileDialog(MainWindow):
    FilDialog = QFileDialog(MainWindow)
    FilDirectory = FilDialog.getExistingDirectory(MainWindow, "Open FileDirectory") + "/"
    return  FilDirectory

########################################################################################################################
###################################input time match the nearest one in the array########################################
def find_nearest(array, value):
    '''
        Description:
        Matching the 'value' to the nearest one in the 'array', and return a dict saving array index
        and value
    '''
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()

    # return dict
    rtnInfo = {}
    rtnInfo["index"] = idx
    rtnInfo["value"] = array[idx]

    return rtnInfo

########################################################################################################################
############################################Define Class:ADINA_DataOutput###############################################
class ADINA_DataOutput:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        # ***************************choose analysis type***********************
        self.ui.BtnGrp_DtO.buttonClicked.connect(lambda: self.Choose_AnalysisType())
        ########################Choose .Idb file and .Por File##################
        self.ui.chooseIdbPorBtn.clicked.connect(lambda: self.ChooseIdbPorFile())
        self.ui.chooseIdbPorBtn.clicked.connect(lambda: self.LoadIdbPorFile())
        # ##########################set time range##############################
        # self.ui.setTiemRange_DatO.clicked.connect(lambda:
        # adina_DataOutput.TimeRange(self))###delete
        #########################Choose .plo file directory ####################
        self.ui.PloDirBtn.clicked.connect(lambda: self.ChoosePloFileDir())
        #############################Generate Plo file##########################
        self.ui.GnertPloBtn.clicked.connect(lambda: self.LoadIdbPorFile())  #
        self.ui.GnertPloBtn.clicked.connect(lambda: self.TimeRange())  # set time range
        self.ui.GnertPloBtn.clicked.connect(lambda: self.GenertPloFile())
        #############################Choose AUI.exe#############################
        self.ui.ChooseAUIBtn.clicked.connect(lambda: self.ChooseAUIDir())
        ##############################Extract Resluts###########################
        self.ui.ExtrctRsltsBtn.clicked.connect(lambda: self.Loading_PloFile())
        ###########################choose ADINA Resluts#########################
        self.ui.chooseRsltsFlBtn.clicked.connect(lambda: self.ChooseADINAResults())
        #######################convert ADINA Resluts to Matrix##################
        self.ui.CnvrtMtrxsBtn.clicked.connect(lambda: self.TimeRange())
        self.ui.CnvrtMtrxsBtn.clicked.connect(lambda: self.GetResultParamsMAT())
        # ######################################################################
        self.ui.pushButton_BatchTable_DatO.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_DatO.clicked.connect(lambda: self.batchrun())
        # ######################################################################

        self.InitDataOutput()

    def InitDataOutput(self):
        # initial definition
        self.AnalysisType = None
        self.Por_FilAbsPth = None
        self.Por_FilHead = None
        self.Por_FilNam = None
        self.Por_FilFormat = None
        self.Idb_FilAbsPth = None
        self.TimeStepStart = None
        self.TimeStepEnd = None
        self.TimeStepStartStr = None
        self.TimeStepEndStr = None
        self.TimeRangeBool = None
        self.Plo_FilDirectory = None
        self.Plo_FilAbsPth = None
        self.eno_FilNam = None
        self.coo_FilNam = None
        self.nos_FilNam = None
        self.lst_FilNam = None
        self.strss_FilNam = None
        self.elf_FilNam = None
        self.NodesetNum1 = None
        self.NodesetNum2 = None
        self.ADINA_AUI_FilDirectory = None
        self.Choose_AnalysisType()

    ############################################Choose analysis type####################################################
    def Choose_AnalysisType(self):
        if self.ui.FluidRdBtn.isChecked():
            self.AnalysisType = "Fluid"
        elif self.ui.SolidRdBtn.isChecked():
            self.AnalysisType = "Solid"
        return self.AnalysisType

    ########################################Select .Idb file and .Por File##############################################
    def ChooseIdbPorFile(self):
        tmpPor_FilAbsPth = Opening_File(self.ui,"Por (*.por)")
        self.ui.plainTextEdit_DatO.setPlainText(tmpPor_FilAbsPth)

        tmpIdb_FilAbsPth = Opening_File(self.ui, "Idb (*.idb)")
        self.ui.plainTextEdit_DatO.appendPlainText(tmpIdb_FilAbsPth)
    def LoadIdbPorFile(self):
        tmpFilePaths = self.ui.plainTextEdit_DatO.toPlainText()
        tmpFilePathslst = re.split('\n', tmpFilePaths)
        # print("tmpFilePathslst", tmpFilePathslst,type(tmpFilePathslst))
        for FilPath in tmpFilePathslst:
            if FilPath.endswith(".por"):
                self.Por_FilAbsPth = FilPath
            elif FilPath.endswith(".idb"):
                self.Idb_FilAbsPth = FilPath
            # else:
            #     QMessageBox.critical(self.ui,
            #                             'Note',
            #                             'Please select idb or por file!')
        print("self.Por_FilAbsPth",self.Por_FilAbsPth,"self.Idb_FilAbsPth",self.Idb_FilAbsPth)
        if self.Por_FilAbsPth:
            self.Por_FilHead, self.Por_FilNam, self.Por_FilFormat = Split_AbsFilePath(self.Por_FilAbsPth)
        # ***********************************if you onlu choose choose the idb file and don't choose the por file ,the purpose is to get the nodeid information  of the selected faceset *************************************************
        elif self.Idb_FilAbsPth and self.Por_FilAbsPth == None :
            if self.AnalysisType == 'Fluid':
                self.Por_FilAbsPth = ''
                self.Por_FilHead = ''
                self.Por_FilFormat =  ''
                self.Por_FilNam = 'LumenNodeset'
                infoBox = QMessageBox()  ##Message Box that doesn't run
                infoBox.setIcon(QMessageBox.Information)
                infoBox.setText('We only select idb file in nodematching step, so you are extrating the  surface nodeset data.'
                                    'es: Lumen nodeset ')
                infoBox.setWindowTitle("Information")
                infoBox.setStandardButtons(QMessageBox.Ok)
                infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)  # 3秒自动关闭
                infoBox.exec_()
            else:
                self.Por_FilAbsPth = ''
                self.Por_FilNam =  'WallInNodeset'
                infoBox = QMessageBox()  ##Message Box that doesn't run
                infoBox.setIcon(QMessageBox.Information)
                infoBox.setText('We only select idb file in nodematching step, so you are extrating the  surface nodeset data. '
                                    'es: WallIn nodeset')
                infoBox.setWindowTitle("Information")
                infoBox.setStandardButtons(QMessageBox.Ok)
                infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)  # 3秒自动关闭
                infoBox.exec_()

        #print(self.Por_FilNam, type(self.Por_FilNam))
        return self.Por_FilAbsPth, self.Por_FilNam, self.Idb_FilAbsPth

    ######################################input time start and end in seconds###########################################
    def TimeRange(self):
        self.TimeStepStartStr = self.ui.lineEdit_TimeStartDatO.text()
        self.TimeStepEndStr = self.ui.lineEdit_TimeEndDatO.text()
        if self.TimeStepStartStr and self.TimeStepEndStr:
            self.TimeRangeBool = True
            self.TimeStepStart = float(self.TimeStepStartStr)
            self.TimeStepEnd = float(self.TimeStepEndStr)
            if (self.TimeStepStart + 0.000001) and self.TimeStepEnd:
                return self.TimeStepStart, self.TimeStepEnd
        else:
            self.TimeRangeBool = False
            self.TimeStepStart = 0
            self.TimeStepEnd = 200
            # infoBox = QMessageBox()  ##Message Box that doesn't run
            # infoBox.setIcon(QMessageBox.Information)
            # infoBox.setText('please input correct time range')
            # infoBox.setWindowTitle("Information")
            # infoBox.setStandardButtons(QMessageBox.Ok)
            # infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)  # 3秒自动关闭
            # infoBox.exec_()

    ##################################################Choose .plo file directory #################################################
    def ChoosePloFileDir(self):
        tmpPlo_FilDirectory = Opening_FileDialog(self.ui)  #####选择文件存储位置  并提示qmessagebox
        if tmpPlo_FilDirectory :
            self.ui.plainTextEdit_DatO3.setPlainText(tmpPlo_FilDirectory)
        else:
            infoBox = QMessageBox()  ##Message Box that doesn't run
            infoBox.setIcon(QMessageBox.Information)
            infoBox.setText('Please select Plo file')
            infoBox.setWindowTitle("Information")
            infoBox.setStandardButtons(QMessageBox.Ok)
            infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)  # 3秒自动关闭
            infoBox.exec_()

    #################################################Generate Plo file##################################################
    def GenertPloFile(self):
        self.Plo_FilDirectory = self.ui.plainTextEdit_DatO3.toPlainText()
        if len(self.ui.LumenOrWallInset_DatO.text()) :
            self.NodesetNum1 = self.ui.LumenOrWallInset_DatO.text()
            self.NodesetNum2 = self.ui.LumenOrWallInset_DatO.text()
        else:
            self.NodesetNum1 = 'FIRST'
            self.NodesetNum2 = 'LAST'
        ################################Writing .Plo .eno .coo .elf .lst .str file absolute Path########################
        self.Plo_FilAbsPth = self.Plo_FilDirectory + self.Por_FilNam + ".plo"
        eno_FilAbsPth = self.Plo_FilDirectory + self.Por_FilNam + ".eno"  # obtain .eno file's absolute path
        coo_FilAbsPth = self.Plo_FilDirectory + self.Por_FilNam + ".coo"
        nos_FilAbsPth = self.Plo_FilDirectory + self.Por_FilNam + ".nos"
        elf_FilAbsPth = self.Plo_FilDirectory + self.Por_FilNam + ".elf"
        lst_FilAbsPth = self.Plo_FilDirectory + self.Por_FilNam + ".lst"
        str_FilAbsPth = self.Plo_FilDirectory + self.Por_FilNam + ".str"

        ################################################################################################################
        #############################################Writing PLo context################################################
        # *****************************************open .idb file or .in file*******************************************
        # *****************************************extract eno coo nos elf file ******************************************
        PloStr = ''   # eno coo nos elf file can be extracted by idb or por file
        # if self.Idb_FilAbsPth:
            # PloStr += 'DATABASE OPEN FILE=\'' + self.Idb_FilAbsPth + '\' SAVE=NO\n\n'
        # if self.Por_FilAbsPth:
        #     PloStr += 'DATABASE OPEN FILE=\'' + self.Por_FilAbsPth + '\' SAVE=NO\n\n'
        if self.Idb_FilAbsPth:
            PloStr += 'DATABASE OPEN FILE=\'' + self.Idb_FilAbsPth + '\' SAVE=NO\n\n'
        else:
            print("Please select idb file to extract eno coo nos elf file!")

        # ***************************export element-node of  all groups and write to a .eno file************************
        PloStr += 'FILELIST OPTION=FILE  FILE=\'' + eno_FilAbsPth + '\' LINPAG=0 EJECT=NO\n'
        for i in range(0, 50):
            PloStr += 'LIST ENODES GROUP=%d\n' % (i + 1)

        # ***************************export coordinates of  all nodes and write to a .coo file**************************
        PloStr += 'FILELIST OPTION=FILE  FILE=\'' + coo_FilAbsPth + '\' LINPAG=0 EJECT=NO\n'
        PloStr += 'LIST COORDINATES NODE FIRST=FIRST LAST=LAST SYSTEM=0 GLOBAL=YES\n'

        # # ***************************export all nodes on the lumen and write to a .nos file**************************
        PloStr += 'FILELIST OPTION=FILE  FILE=\'' + nos_FilAbsPth + '\' LINPAG=0 EJECT=NO\n'
        PloStr += 'LIST NODESET FIRST=%s LAST=%s \n'%(self.NodesetNum1,
                                                      self.NodesetNum2)

        # ********************export  element nodes of  all element face set and write to a .elf file*******************
        PloStr += 'FILELIST OPTION=FILE  FILE=\'' + elf_FilAbsPth + '\' LINPAG=0 EJECT=NO\n'
        PloStr += 'LIST ELFACESET FIRST=FIRST LAST=LAST\n'

            # ***************************************** extract lst str file ******************************************
        if self.Por_FilAbsPth:
            # *******************************loading .por file and select the time range************************************
            if self.TimeRangeBool:
                PloStr += 'DATABASE NEW\nLOADPORTHOLE OPERATIO=CREATE FILE=\'' + self.Por_FilAbsPth + '\' RANGE=TIME TIMESTART=%f' % self.TimeStepStart + ' TIMEEND=%f\n' % self.TimeStepEnd
            else:
                PloStr += 'DATABASE NEW\nLOADPORTHOLE OPERATIO=CREATE FILE=\'' + self.Por_FilAbsPth + '\'\n '
            PloStr += 'ZONE NAME=Sout  NODEATTACH=YES  GEOMATTACH=YES\n WHOLE_MODEL\n'  ####is not 'whole_model'
            PloStr += 'RESULTGRID NAME=MyGrid TYPE=PORTHOLE NGRIDR=1  NGRIDS=1  NGRIDT=1\n'
            # *******************************************select the time step***********************************************
            PloStr += 'RESPRANGE LOAD-STEP NAME=SRange TSTART=EARLIEST TEND=LATEST INCREMEN=AVAILABLE INTERPOL=NO NSKIP=0\nSMOOTHING NAME=StruSmooType TYPE=AVERAGED\n'

            # ********************export or solid result parameters of  all times and write to a .lst file******************
            PloStr += 'FILELIST OPTION=FILE  FILE=\'' + lst_FilAbsPth + '\' LINPAG=0 EJECT=NO\n'
            if self.AnalysisType == "Fluid":
                # ********************export  fluid result parameters of  all times and write to a .lst file****************
                PloStr += 'ZONELIST ZONENAME=Sout RESULTGRID=MyGrid SMOOTHING=StruSmooType RESULTCO=DEFAULT RESPOPTI=RESPRANGE RESPONSE=DEFAULT RESPRANG=SRange VARIABLE= X-VELOCITY Y-VELOCITY Z-VELOCITY NODAL_PRESSURE MAX_SHEAR_STRESS \n'

            elif self.AnalysisType == "Solid":
                # ********************export  solid result parameters of  all times and write to a .lst file****************
                PloStr += 'ZONELIST ZONENAME=Sout RESULTGRID=MyGrid SMOOTHING=StruSmooType RESULTCO=DEFAULT RESPOPTI=RESPRANGE RESPONSE=DEFAULT RESPRANG=SRange VARIABLE= SIGMA-P1 EFFECTIVE_STRESS MAX_SHEAR_STRESS SIGMA-NORM2 \n'
            else:
                print("Analysis Type must be selected")

        # ********************export  result parameters of  all times and write to a .str file**************************
            PloStr += 'FILELIST OPTION=FILE  FILE=\'' + str_FilAbsPth + '\' LINPAG=0 EJECT=NO\n'
            PloStr += 'ZONELIST ZONENAME=Sout RESULTGRID=MyGrid SMOOTHING=StruSmooType RESULTCO=DEFAULT RESPOPTI=RESPRANGE RESPONSE=DEFAULT RESPRANG=SRange VARIABLE= STRESS-XX STRESS-YY STRESS-ZZ STRESS-XY STRESS-XZ STRESS-YZ\n'
        else:
            print("Please select por file to extract results file!")
        ######################################  Writing Plo context to a new file  #####################################
        with open(self.Plo_FilAbsPth, 'w') as f:
            f.write(PloStr)
        infoBox = QMessageBox()  ##Message Box that doesn't run
        infoBox.setIcon(QMessageBox.Information)
        infoBox.setText("Done！")
        infoBox.setWindowTitle("Information")
        infoBox.setStandardButtons(QMessageBox.Ok)
        infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)  # 3秒自动关闭
        infoBox.exec_()
        return self.Plo_FilAbsPth, self.Plo_FilDirectory

    def ChooseAUIDir(self):
        # *******************************************Obtain ADINA AUI.exe FilDirectory *********************************
        tmpADINA_AUI_FilDirectory = Opening_File(self.ui,"*(AUI.exe)")
        self.ui.plainTextEdit_DatO2.setPlainText(tmpADINA_AUI_FilDirectory)

    def Loading_PloFile(self):
        """ Description: Loading PloFile and output .eno .elf .coo .lst .str file in self.Plo_FilDirectory"""
        self.ADINA_AUI_FilDirectory = self.ui.plainTextEdit_DatO2.toPlainText()
        self.Plo_FilDirectory = self.ui.plainTextEdit_DatO3.toPlainText()
        start =time.time()
        ####################################################################################################################
        ###################################### Loading  .plo file in ADINA_AUI  ############################################
        # **************************** Writing a .bat(command file by windows)  to load .plo  *******************************
        ADINA_AUI_Batch = self.ADINA_AUI_FilDirectory + ' -b -m 16gb -t 8 ' + self.Plo_FilAbsPth
        #print(ADINA_AUI_Batch)
        ADINA_AUI_Batch_FilAbsPth = self.Plo_FilDirectory + "ADINA_AUI_Batch.bat"
        with open(ADINA_AUI_Batch_FilAbsPth, 'w') as f:
            f.write(ADINA_AUI_Batch)
        # *******************************************  run .bat to load .plo  ***********************************************
        os.system(ADINA_AUI_Batch_FilAbsPth)
        print("------Running time: {} s------".format(time.time() - start))
        # QMessageBox.information(self.ui,
        #                         'Note',
        #                         'Done！\n Time Consuming: {} '.format(int(time.time() - start)))

        infoBox = QMessageBox()  ##Message Box that doesn't run
        infoBox.setIcon(QMessageBox.Information)
        infoBox.setText(str('Done！\n Time Consuming: {} '.format(int(time.time() - start))))
        infoBox.setWindowTitle("Information")
        infoBox.setStandardButtons(QMessageBox.Ok)
        infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)  # 3秒自动关闭
        infoBox.exec_()

    #################################################ChooseADINAResults##################################################
    def ChooseADINAResults(self):
        # *********************************  choose  .eno .coo .lst .str .elf file  ************************************
        tmpeno_FilNam = Opening_File(self.ui, "eno (*.eno)")
        self.ui.plainTextEdit_DatO4.setPlainText(tmpeno_FilNam)
        tmpcoo_FilNam = Opening_File(self.ui,"coo (*.coo)")
        self.ui.plainTextEdit_DatO4.appendPlainText(tmpcoo_FilNam)
        tmpnos_FilNam = Opening_File(self.ui, "nos (*.nos)")
        self.ui.plainTextEdit_DatO4.appendPlainText(tmpnos_FilNam)
        tmplst_FilNam = Opening_File(self.ui,"lst (*.lst)")
        self.ui.plainTextEdit_DatO4.appendPlainText(tmplst_FilNam)
        tmpstrss_FilNam = Opening_File(self.ui,"str (*.str)")
        self.ui.plainTextEdit_DatO4.appendPlainText(tmpstrss_FilNam)
        tmpelf_FilNam = Opening_File(self.ui,"elf (*.elf)")
        self.ui.plainTextEdit_DatO4.appendPlainText(tmpelf_FilNam)

    def GetResultParamsMAT(self):
        """
            Dscription: convert extracted results to *.npy file

            Notes
            -----
            pre-converted results are plain text,eg: *.coo, *.eno, *.str
            converted results are dict of array,eg: *.npy, *.eno, *.str

            Examples
            --------
            a *.coo file:

            Node               X                   Y                   Z
            2 0.1206669922000E+03 0.8347875214000E+02 0.2271462822000E+02
            5 0.1207276535000E+03 0.8277872467000E+02 0.2278620720000E+02
            6 0.1207466888000E+03 0.8317846680000E+02 0.2325130844000E+02

            *.coo file's correspondent *.npy file:

            {'Node_id': array([    2,     5,     6, ..., 37687, 37688, 37689]),
             'Node_coo': array([[120.6669922 ,  83.47875214,  22.71462822],
                       [120.7276535 ,  82.77872467,  22.7862072 ],
                       [120.7466888 ,  83.1784668 ,  23.25130844],
                       ...,
                       [123.01153062, 131.91428047,  34.55538257],
                       [123.41004846, 131.95694526,  35.24022521],
                       [123.36766192, 132.43444777,  34.94282161]])}
        """
        tmpFileAbsPaths = self.ui.plainTextEdit_DatO4.toPlainText()
        tmpFileAbsPathslst = re.split('\n', tmpFileAbsPaths)
        # print("tmpFilePathslst", tmpFilePathslst,type(tmpFilePathslst))
        for FilAbsPath in tmpFileAbsPathslst:
            if FilAbsPath.endswith(".eno"):
                self.eno_FilNam = FilAbsPath
            elif FilAbsPath.endswith(".coo"):
                self.coo_FilNam = FilAbsPath
            elif FilAbsPath.endswith(".nos"):
                self.nos_FilNam = FilAbsPath
            elif FilAbsPath.endswith(".lst"):
                self.lst_FilNam = FilAbsPath
            elif FilAbsPath.endswith(".str"):
                self.strss_FilNam = FilAbsPath
            elif FilAbsPath.endswith(".elf"):
                self.elf_FilNam = FilAbsPath
        start = time.time()
        ####################################################################################################################
        if self.eno_FilNam:
            ########################## Reading .eno file and  output  matrix "element num    node num "#########################
            # *******************************************  Reading .eno file  ***************************************************
            # os.chdir(Split_AbsFilePath(self.eno_FilNam)[0])
            eno_Fil = open(self.eno_FilNam, "r")
            eno_FilContxt = eno_Fil.read()  # type(eno_FilContxt)=str

            # *********************************  Element group numbers included in .eno file  **********************************
            # ElmntGroupInfo = re.findall('Element Group\s+(\d+)', eno_FilContxt, re.M)
            # ElmntGroupNum = len(ElmntGroupInfo)

            # ********************************* split .eno file context by 'End of list'  **************************************
            eno_FilContt_NoEndOL = re.split('End of list',
                                            eno_FilContxt)  # the output result type by function 're.split' is a list

            # ************** find and save tetra element and Hex element information from  updated .eno file context ***********
            TetraElmnt_NdIfo = re.findall('(?:(?:^|\n) (?: +\d+){5}\n)', eno_FilContxt,
                                          re.M)  ##type(TetraElmnt_NdIfo)=list 匹配行头格式 (?:^|\n)行头内容.*
            # print("TetraElmnt_NdIfo",TetraElmnt_NdIfo,type(TetraElmnt_NdIfo))
            HexElmnt_NdIfo = re.findall('(?:(?: +\d+){6}\n(?:.+\d+){3}\n)', eno_FilContxt, re.M)

            # *************************** delete '\n'  from  updated str and put all str in one line ***************************
            TetraElmnt_NdIfo_Dltn = [w.replace('\n', '') for w in TetraElmnt_NdIfo]
            # print("TetraElmnt_NdIfo_Dltn", TetraElmnt_NdIfo_Dltn, type(TetraElmnt_NdIfo_Dltn))
            HexElmnt_NdIfo_Dltn = [w.replace('\n', '') for w in HexElmnt_NdIfo]

            # ************************************ replace multiple space by ',' ***********************************************
            TetraElmnt_NdIfo_Dltn_Nospac = [re.sub(' +', ',', w) for w in TetraElmnt_NdIfo_Dltn]
            HexElmnt_NdIfo_Dltn_Nospac = [re.sub(' +', ',', w) for w in HexElmnt_NdIfo_Dltn]

            # **************************************** delete the first ',' **************************************************
            TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac = [w[1:] for w in TetraElmnt_NdIfo_Dltn_Nospac]
            # print("TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac=\n",TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac)
            HexElmnt_NdIfo_Dltn_Nospac_NoFirstSpac = [w[1:] for w in HexElmnt_NdIfo_Dltn_Nospac]

            # ************************** split TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac by ',' *********************************
            TetraElmnt_NdIfoUpdtd_Split = [w.split(",") for w in TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac]
            # print("TetraElmnt_NdIfoUpdtd_Split=\n", TetraElmnt_NdIfoUpdtd_Split)
            HexElmnt_NdIfoUpdtd_Split = [w.split(",") for w in HexElmnt_NdIfo_Dltn_Nospac_NoFirstSpac]


            TetraElmnt_NdIfo_Mat = np.asarray(TetraElmnt_NdIfoUpdtd_Split, dtype=int)
            if len(TetraElmnt_NdIfo_Mat):
                TetraElmnt_NdIfo_Mat_elementId = TetraElmnt_NdIfo_Mat[:, 0].astype(
                    np.int)
                TetraElmnt_NdIfo_Mat_pointId = TetraElmnt_NdIfo_Mat[:, 1:].astype(
                    np.int)

                TetraElmntNdIfoDict = {}
                TetraElmntNdIfoDict["Tetra_Element_id"] = TetraElmnt_NdIfo_Mat_elementId
                TetraElmntNdIfoDict["Tetra_point_id"] = TetraElmnt_NdIfo_Mat_pointId
                np.save(Split_AbsFilePath(self.eno_FilNam)[0]+'/'+'%s_TetraElmnt_NdIfo_Dic' % self.AnalysisType,
                        TetraElmntNdIfoDict)
            else:
                print("This model don't have tetralelment.")

            HexElmnt_NdIfo_Mat = np.asarray(HexElmnt_NdIfoUpdtd_Split, dtype=int)
            if len(HexElmnt_NdIfo_Mat):

                HexElmnt_NdIfo_Mat_elementId = HexElmnt_NdIfo_Mat[:, 0].astype(np.int)
                HexElmnt_NdIfo_Mat_pointId = HexElmnt_NdIfo_Mat[:, 1:].astype(np.int)

                HexElmntNdIfoDict ={}
                HexElmntNdIfoDict["Hex_Element_id"] = HexElmnt_NdIfo_Mat_elementId
                HexElmntNdIfoDict["Hex_point_id"] = HexElmnt_NdIfo_Mat_pointId
                np.save(Split_AbsFilePath(self.eno_FilNam)[0]+'/'+'%s_HexElmnt_NdIfo_Dic' % self.AnalysisType,
                        HexElmntNdIfoDict)
            else:
                print("This model don't have hexelment.")

            # print("TetraElmnt_NdIfo_Mat\n",TetraElmnt_NdIfo_Mat)
            # print("HexElmnt_NdIfo_Mat\n",HexElmnt_NdIfo_Mat)
            np.save(Split_AbsFilePath(self.eno_FilNam)[0]+'/'+'%s_TetraElmnt_NdIfo_Mat' % self.AnalysisType,TetraElmnt_NdIfo_Mat)
            np.save(Split_AbsFilePath(self.eno_FilNam)[0]+'/'+'%s_HexElmnt_NdIfo_Mat' % self.AnalysisType, HexElmnt_NdIfo_Mat)
            eno_Fil.close()
        else:
            print("you do not choose eno fil.")

        ####################################################################################################################
        if self.coo_FilNam:
            ########################## Reading .coo file and  output  matrix "element num    node coordinate "##################
            # *******************************************  Reading .coo file  ***************************************************
            # os.chdir(Split_AbsFilePath(self.coo_FilNam)[0])
            coo_Fil = open(self.coo_FilNam, "r")
            coo_FilContxt = coo_Fil.read()  # type(cooo_FilContxt)=str

            # ****************** find all element nums and corresponded coordinates in .coo file context   *********************
            Nd_coordInfo = re.findall('( +\d+(?:\D\d.\d+E\D\d{2}){3})', coo_FilContxt, re.M)  #####  |D  取代负号
            # ************************************ replace multiple space by ',' ***********************************************
            Nd_coordInfoNoSpac = [re.sub(' +', ',', w) for w in Nd_coordInfo]
            # ************************************ replace “-” by ',-' ***********************************************
            Nd_coordInfoNoNegative = [re.sub('-', ',-', w) for w in Nd_coordInfoNoSpac]
            Nd_coordInfoNoNegativeE = [re.sub('E,', 'E', w) for w in Nd_coordInfoNoNegative]
            # print("No Negative", Nd_coordInfoNoNegative)
            # **************************************** delete the first space **************************************************
            Nd_coordInfoNoFirstSpac = [w[1:] for w in Nd_coordInfoNoNegativeE]
            # ************************** split TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac by ',' *********************************
            Nd_coordInfoSplit = [w.split(",") for w in Nd_coordInfoNoFirstSpac]

            Nd_CoordMat = np.array(Nd_coordInfoSplit)
            # print("Nd_CoordMat",Nd_CoordMat)
            Nd_CoordMat_coord = Nd_CoordMat[:, 1:].astype(np.float)
            Nd_CoordMat_node = Nd_CoordMat[:, 0].astype(np.int)
            # print("Node", Nd_CoordMat_node)
            # print("Coord", Nd_CoordMat_coord)
            # np.savetxt('Node_id.mat',Nd_CoordMat_node)
            # np.savetxt('Node_x_y_z.mat', Nd_CoordMat_coord)
            NdcoorMat = {}
            NdcoorMat["Node_id"] = Nd_CoordMat_node
            NdcoorMat["Node_coo"] = Nd_CoordMat_coord
            # print("NdcoorMat",NdcoorMat)
            np.save(Split_AbsFilePath(self.coo_FilNam)[0]+'/'+'%s_Nodecoo_Dic'%self.AnalysisType, NdcoorMat)
            coo_Fil.close()
        else:
            print("you do not choose coo file")

        if self.nos_FilNam:
            # *******************************************  Reading .nos file  ***************************************************
            # os.chdir(Split_AbsFilePath(self.nos_FilNam)[0])
            nos_Fil = open(self.nos_FilNam, "r")
            nos_FilContxt = nos_Fil.read()  # type(noso_FilContxt)=str

            # ****************** find all element nums and corresponded setinates in .nos file context   *********************
            Nd_setInfo = re.findall('( +\d+(?: +\d+ +\d+))', nos_FilContxt, re.M)  #####  |D  取代负号
            #print(Nd_setInfo)
            # ************************************ replace multiple space by ',' ***********************************************
            Nd_setInfoNoSpac = [re.sub(' +', ',', w) for w in Nd_setInfo]
            # **************************************** delete the first space **************************************************
            Nd_setInfoNoFirstSpac = [w[1:] for w in Nd_setInfoNoSpac]
            # ************************** split TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac by ',' *********************************
            Nd_setInfoSplit = [w.split(",") for w in Nd_setInfoNoFirstSpac]

            Nd_setMat = np.array(Nd_setInfoSplit)
            # print("Nd_setMat",Nd_setMat)
            if  np.shape(Nd_setMat)[0] == 0:
                Nd_setMat_node = []
            else:
                Nd_setMat_node = Nd_setMat[:, 0].astype(np.int)

            # print("Node", Nd_setMat_node)
            # print("set", Nd_setMat_set)
            # np.savetxt('Node_id.mat',Nd_setMat_node)
            # np.savetxt('Node_x_y_z.mat', Nd_setMat_set)
            NdsetMat = {}
            NdsetMat["Node_id"] = Nd_setMat_node
            # print("NdnosrMat",NdnosrMat)
            np.save(Split_AbsFilePath(self.nos_FilNam)[0]+'/'+'%s_Nodeset_Dic'%self.AnalysisType, NdsetMat)
            nos_Fil.close()
        else:
            print("you do not choose nos file")

        ####################################################################################################################
        if self.lst_FilNam and self.strss_FilNam :
            ###################### Reading .lst file and  output  matrix "node num,  vx, vy, vz, p, max ss"#####################
            # *******************************************  Reading .lst file  **************************************************
            # os.chdir(Split_AbsFilePath(self.lst_FilNam)[0])
            lst_Fil = open(self.lst_FilNam, "r")
            lst_FilContxt = lst_Fil.read()  # type(lst_FilContxt)=str

            # ********************************* split .lst file context by 'End of list'  **************************************
            lst_FilContxt_NoEndOL = re.split('(?:\n+\s+(\*){3}\s+End of list\.\n+)', lst_FilContxt, re.M)
            # *************************************  reckon up the Timestep num  ***********************************************
            lst_FilContxt_TimStpNms = re.findall('( +Time.+\n)', lst_FilContxt_NoEndOL[0])
            # *************************************  remove the 'time' '\n'  ***************************************************
            lst_FilContxt_TWithotTim = [re.sub('\n|Time', '', w) for w in lst_FilContxt_TimStpNms]
            # ************************************** remove the space **********************************************************
            lst_FilContxt_TWithotTim_NSpac = [re.sub(' +', '', w) for w in lst_FilContxt_TWithotTim]
            # ************************************** remove the space **********************************************************
            lst_FilContxt_TWithotTim_NSpac_AddE = [re.sub('(\d)\-', '\\1E-', w) for w in lst_FilContxt_TWithotTim_NSpac]
            lst_FilContxt_TWithotTim_NSpac_AddE = [re.sub('(\d)\+', '\\1E+', w) for w in lst_FilContxt_TWithotTim_NSpac_AddE]
            # ***************************************** save TimeMat ***********************************************************
            lst_TimeMat = np.array(lst_FilContxt_TWithotTim_NSpac_AddE, dtype=float)
            np.save(Split_AbsFilePath(self.lst_FilNam)[0]+'/'+'%s_Times'%self.AnalysisType, lst_TimeMat)
            # print("Times=",lst_TimeMat)
            # print("Timeslist=",list(lst_TimeMat))
            if len(lst_TimeMat):
                TimesDict = {}
                if self.TimeStepStartStr:
                    if self.TimeStepStart > list(lst_TimeMat)[0]:
                        TimesDict["timeRange_TimesDict"] = lst_TimeMat[1:]
                else:
                    TimesDict["timeRange_TimesDict"] = lst_TimeMat
                np.save(Split_AbsFilePath(self.lst_FilNam)[0]+'/'+'%s_Times_Dic' % self.AnalysisType,
                        TimesDict)
            else:
                print("This model don't have times.", sys._getframe().f_lineno)

            # ***************************************** save TimeMat ***********************************************************
            lst_FilContxt_NoEndOL_Splt = re.split('(?: +Time.+\n)', lst_FilContxt_NoEndOL[0])
            # ***************************************** delete the heading *****************************************************
            lst_FilContxt_NoEndOL_Splt.remove(lst_FilContxt_NoEndOL_Splt[0])
            # ********************************************* remove \n **********************************************************
            lst_FilContxt_NS_Remvn = [re.sub('\n', '', w) for w in lst_FilContxt_NoEndOL_Splt]
            # ********************************************* remove 'Node' ******************************************************
            lst_FilContxt_NSR_RemvNd = [re.sub('Node', '', w) for w in lst_FilContxt_NS_Remvn]
            # ***************************************** resub multiple spaces to one space *************************************
            lst_FilContxt_NSRR_RemvMultiSPac = [re.sub(' +', ' ', w) for w in lst_FilContxt_NSR_RemvNd]
            lst_FilContxt_NSRRR_RemvFirstSPac = [w[1:] for w in lst_FilContxt_NSRR_RemvMultiSPac]  # remove the  first space
            lst_FilContxt_NSRRR_RemvFirstSPac_AddE = [re.sub('(\d)\-', '\\1E-', w) for w in lst_FilContxt_NSRRR_RemvFirstSPac]
            lst_FilContxt_NSRRR_RemvFirstSPac_AddE = [re.sub('(\d)\+', '\\1E+', w) for w in
                                                   lst_FilContxt_NSRRR_RemvFirstSPac_AddE]

            # ************************************************ split ***********************************************************
            lst_ParamsMat = [w.split(" ") for w in lst_FilContxt_NSRRR_RemvFirstSPac_AddE]
            # print("lst_ParamsMat\n",lst_ParamsMat)

            ####################################################################################################################
            ## Reading .str file and output  matrix "node num stress-xx, stress-yy,stress-zz, stress-xy, stress-xz, stress-yz"##

            # *******************************************  Reading .str file  **************************************************

            # os.chdir(Split_AbsFilePath(self.strss_FilNam)[0])
            strss_Fil = open(self.strss_FilNam, "r")
            strss_FilContxt = strss_Fil.read()  # type(strss_FilContxt)=str

            # ********************************* split .eno file context by 'End of list'  **************************************
            strss_FilContt_NoEndOL = re.split('(?:\n+\s+(\*){3}\s+End of list\.\n+)', strss_FilContxt, re.M)
            # ******************************************** split by Time line  *************************************************
            strss_FilContt_N_Split = re.split('(?: +Time.+\n)', strss_FilContt_NoEndOL[0])
            # ******************************************** remove the heading  *************************************************
            strss_FilContt_N_Split.remove(strss_FilContt_N_Split[0])
            # ******************************************** remove the \n  ******************************************************
            strss_FilContt_NS_Rmvn = [re.sub('\n', '', w) for w in strss_FilContt_N_Split]
            # ******************************************** remove the Node *****************************************************
            strss_FilContt_NSR_RmvNd = [re.sub('Node', '', w) for w in strss_FilContt_NS_Rmvn]
            # ******************************************** resub  multiple spaces to one ***************************************
            strss_FilContt_NSRR_OneSpac = [re.sub(' +', ' ', w) for w in strss_FilContt_NSR_RmvNd]
            strss_FilContt_NSRR_OneSpac_AddE = [re.sub('(\d)\-', '\\1E-', w) for w in
                                                      strss_FilContt_NSRR_OneSpac]
            strss_FilContt_NSRR_OneSpac_AddE = [re.sub('(\d)\+', '\\1E+', w) for w in
                                                      strss_FilContt_NSRR_OneSpac_AddE]
            # ******************************************** resub  the first space **********************************************
            strss_FilContt_NSRRO_NoFirstSpac = [w[1:] for w in strss_FilContt_NSRR_OneSpac_AddE]
            # ***************************************************** split ******************************************************
            strss_ParamsMat = [w.split(" ") for w in strss_FilContt_NSRRO_NoFirstSpac]
            # print("strss_ParamsMat\n",strss_ParamsMat)

            ####################################################################################################################
            ############################################ output lst str parameters##############################################

            names = locals()
            # # find nearest time step
            self.TimeStepStartDict = find_nearest(array=lst_TimeMat, value=self.TimeStepStart)
            self.TimeStepEndDict = find_nearest(array=lst_TimeMat, value=self.TimeStepEnd)
            # print("Find nearest start time for {} \n is {} in lst_TimeMat \n at time step {}".format(self.TimeStepStart,self.TimeStepStartDict["value"],self.TimeStepStartDict["index"]))
            # print("Find nearest end time for {} \n is {} in lst_TimeMat \n at time step {}".format(self.TimeStepEnd,self.TimeStepEndDict["value"],self.TimeStepEndDict["index"]))

            # ************** ADINA BUG:ADINA writes  timestep=0 in *.lst and *.str file be writen by default *******************
            if self.TimeStepStart > list(lst_TimeMat)[0]:
                lst_TimeMat_StartID = 1
            else:
                lst_TimeMat_StartID = 0
            # print("lst_TimeMat_StartID=",lst_TimeMat_StartID)

            # ******************************************* output lst str parameters ********************************************
            lst_ParamsDic = {}
            lst_ParamsDic["prefix"] = "lst_ParamsMat"
            lst_ParamsDic["range"] = list(range(self.TimeStepStartDict["index"], self.TimeStepEndDict["index"] + 1))
            lst_ParamsDic["timeRange"] = list(lst_TimeMat[lst_TimeMat_StartID:])  ##!!!!! timestep1 = 0.000

            if self.AnalysisType == "Fluid":
                lstColumn = 6
                lst_ParamsDic["parameter"] = ["X-VELOCITY", "Y-VELOCITY",
                                              "Z-VELOCITY", "NODAL_PRESSURE",
                                              "MAX_SHEAR_STRESS"]
            elif self.AnalysisType == "Solid":
                lstColumn = 5
                lst_ParamsDic["parameter"] = ["SIGMA-P1", "EFFECTIVE-STRESS",
                                              "MAX-SHEAR-STRESS", "SIGMA-NORM2"]
            strss_ParamsDic = {}
            strss_ParamsDic["prefix"] = "strss_ParamsMat"
            strss_ParamsDic["range"] = list(range(self.TimeStepStartDict["index"], self.TimeStepEndDict["index"] + 1))
            strss_ParamsDic["timeRange"] = list(lst_TimeMat[lst_TimeMat_StartID:])  # list[]   ##!!!!! timestep1 = 0.000
            strss_ParamsDic["parameter"] = ["STRESS-XX", "STRESS-YY", "STRESS-ZZ", "STRESS-XY", "STRESS-XZ",
                                            "STRESS-YZ"]  # list[]

            for timestep in range(lst_TimeMat_StartID, len(lst_TimeMat)):  ###!!!!! timestep1 = 0.000
                # exec('lst_ParamsMatTimestp{} = {}'.format(timestep, np.array(lsttmpStr[timestep]).reshape(-1,6)))
                names['lst_ParamsMat' + str(lst_TimeMat[timestep])] = np.array(lst_ParamsMat[timestep]).reshape(-1,
                                                                                                                lstColumn)  # extract the matrix of eachstep
                names['lst_ParamsMat' + str(lst_TimeMat[timestep])] = names['lst_ParamsMat' + str(lst_TimeMat[timestep])][:,
                                                                      1:].astype(np.float)
                lst_ParamsDic['lst_ParamsMat' + str(lst_TimeMat[timestep])] = names[
                    'lst_ParamsMat' + str(lst_TimeMat[timestep])]


                names['strss_ParamsMat' + str(lst_TimeMat[timestep])] = np.array(strss_ParamsMat[timestep]).reshape(-1,
                                                                                                                    7)  # extract the matrix of eachstep
                names['strss_ParamsMat' + str(lst_TimeMat[timestep])] = names[
                                                                            'strss_ParamsMat' + str(lst_TimeMat[timestep])][
                                                                        :, 1:].astype(np.float)
                strss_ParamsDic['strss_ParamsMat' + str(lst_TimeMat[timestep])] = names[
                    'strss_ParamsMat' + str(lst_TimeMat[timestep])]
            # print("lst_ParamsDic\n",lst_ParamsDic)
            # print("strss_ParamsDic\n", strss_ParamsDic)
            np.save(Split_AbsFilePath(self.strss_FilNam)[0]+'/'+'%s_lst_ParamsDic'%self.AnalysisType, lst_ParamsDic)
            # lst_ParamsMat= np.load('lst_ParamsMat.npy')
            np.save(Split_AbsFilePath(self.strss_FilNam)[0]+'/'+'%s_strss_ParamsDic'%self.AnalysisType, strss_ParamsDic)
            # strss_ParamsMat= np.load('strss_ParamsMat.npy')
            lst_Fil.close()
            strss_Fil.close()
        else:
            print("you do not choose lst and strss file")
        ####################################################################################################################
        if self.elf_FilNam:
        ############################################ output lst str parameters##############################################
        # *******************************************  Reading .elf file  **************************************************

            # os.chdir(Split_AbsFilePath(self.elf_FilNam)[0])
            elf_Fil = open(self.elf_FilNam, "r")
            elf_FilContxt = elf_Fil.read()  # type(elf_FilContxt)=str

            # *******************************  reckon up the element faceset number  *******************************************
            elf_FacSetNm = re.findall(' Listing of Elfaceset +(\d+)\n', elf_FilContxt)
            elf_FacSetNmMat = np.array(elf_FacSetNm, dtype=int)
            # *************************** obtain matrix   face, element num,  element group  ***********************************
            elf_FacSetInfo = re.findall(' +Face       El     Group\n((?:.+\n)+)\sDESCRIPTION.+\n', elf_FilContxt)
            # *************************** delete '\n'  from  updated str and put all str in one line ***************************
            elf_FacSetInfo_Remvn = [re.sub('\n', '', w) for w in elf_FacSetInfo]
            # ******************************************** resub  multiple spaces to one ***************************************
            elf_FacSetInfo_R_OneSpac = [re.sub(' +', ' ', w) for w in elf_FacSetInfo_Remvn]
            # ******************************************** remove the space of head and tail ***********************************
            elf_FacSetInfo_RO_RemvSpacHT = [w.strip(' ') for w in elf_FacSetInfo_R_OneSpac]
            # ************************************************** split by ' ' **************************************************
            elf_FacSetInfo_ROR_Split = [w.split(" ") for w in elf_FacSetInfo_RO_RemvSpacHT]
            # print("elf_FacSetInfo_ROR_Split\n",elf_FacSetInfo_ROR_Split)
            elf_face_elem_grp_mat = {}
            elf_face_elem_grp_mat["prefix"] = 'elfFaceSet'
            elf_face_elem_grp_mat["range"] = elf_FacSetNmMat
            names = locals()
            for facesetIndex in range(0, len(elf_FacSetNmMat)):
                names['elfFaceSet' + str(elf_FacSetNmMat[facesetIndex])] = np.array(elf_FacSetInfo_ROR_Split[facesetIndex],
                                                                                    dtype=int).reshape(-1, 3)
                elf_face_elem_grp_mat['elfFaceSet' + str(elf_FacSetNmMat[facesetIndex])] = names[
                    'elfFaceSet' + str(elf_FacSetNmMat[facesetIndex])]
                # print("elfFaceSet%d="%elf_FacSetNmMat[facesetIndex],names['elfFaceSet' + str(elf_FacSetNmMat[facesetIndex])])
            # np.savetxt('elf.mat', elf_face_elem_grp_mat)
            # print("elf_face_elem_grp_mat\n",elf_face_elem_grp_mat)
            np.save(Split_AbsFilePath(self.elf_FilNam)[0]+'/'+'%s_elf_face_elem_grp_mat'%self.AnalysisType, elf_face_elem_grp_mat)
            elf_Fil.close()
        else:
            print("you do not choose elf file")
        print("------Running time: {} s------".format(time.time() - start))
        # QMessageBox.information(self.ui,
        # 'Note',
        # 'Done！\n Time Consuming: {} '.format(int(time.time() - start)))
        infoBox = QMessageBox()  ##Message Box that doesn't run
        infoBox.setIcon(QMessageBox.Information)
        infoBox.setText(
            str('Done！\n Time Consuming: {} '.format(int(time.time() - start))))
        infoBox.setWindowTitle("Information")
        infoBox.setStandardButtons(QMessageBox.Ok)
        infoBox.button(QMessageBox.Ok).animateClick(2 * 1000)  # 3秒自动关闭
        infoBox.exec_()

 # c:\adinaNN\x64\adina.exe -b -s -mm 100mw -t 2 prob02.dat
    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_DatO.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_DatO.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            DataOutput = False
            try:
                if info["DataOutput"]:
                    DataOutput = info["DataOutput"]
            except:
                pass
            if DataOutput:
                DataOutputoutputfloder = ''
                DataOutputPORFloder = ''
                DataOutputIDBFloder = ''
                DataOutputFluid = True
                TimeStart = ''
                TimeStop = ''
                AUIFloder = ''
                try:
                    if info["OutputFolder"]:
                        DataOutputoutputfloder = info["OutputFolder"] + '/Npy'
                except:
                    pass
                try:
                    if info["OutputFolder(DataOutput)"]:
                        DataOutputoutputfloder = info["OutputFolder(DataOutput)"]
                except:
                    pass
                try:
                    if info["Idb Path(DataOutput)"]:
                        DataOutputIDBFloder = info["Idb Path(DataOutput)"]
                except:
                    pass
                try:
                    if info["Por Path(DataOutput)"]:
                        DataOutputPORFloder = info["Por Path(DataOutput)"]
                except:
                    pass
                try:
                    if info["TimeStart(DataOutput)"]:
                        TimeStart = info["TimeStart(DataOutput)"]
                except:
                    pass
                try:
                    if info["TimeStop(DataOutput)"]:
                        TimeStop = info["TimeStop(DataOutput)"]
                except:
                    pass
                try:
                    if info["AUI Path(DataOutput)"]:
                        AUIFloder = info["AUI Path(DataOutput)"]
                except:
                    pass
                try:
                    if isinstance(info["Fluid(DataOutput)"], np.bool_):
                        DataOutputFluid = info["Fluid(DataOutput)"]
                except:
                    pass
                print('DataOutput OutputFloder=', DataOutputoutputfloder)
                if not os.path.exists(DataOutputoutputfloder):
                    os.mkdir(DataOutputoutputfloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                if DataOutputIDBFloder:
                    if DataOutputPORFloder:
                        self.ui.plainTextEdit_DatO.setPlainText('{}\n{}'.format(DataOutputPORFloder, DataOutputIDBFloder))
                    else:
                        self.ui.plainTextEdit_DatO.setPlainText('{}'.format(DataOutputIDBFloder))
                    name = re.findall('.+/(.+)\.idb', self.ui.plainTextEdit_DatO.toPlainText())
                    self.ui.plainTextEdit_DatO4.setPlainText('{0}/{1}.eno\n{0}/{1}.coo\n{0}/{1}.nos\n{0}/{1}.lst'
                        '\n{0}/{1}.str\n{0}/{1}.elf'.format(DataOutputoutputfloder, name[-1]))
                self.ui.SolidRdBtn.setChecked(True)
                if DataOutputFluid:
                    self.ui.FluidRdBtn.setChecked(True)
                if TimeStart:
                    self.ui.lineEdit_TimeStartDatO.setText('{}'.format(TimeStart))
                if TimeStop:
                    self.ui.lineEdit_TimeEndDatO.setText('{}'.format(TimeStop))
                if DataOutputoutputfloder:
                    self.ui.plainTextEdit_DatO3.setPlainText('{}/'.format(DataOutputoutputfloder))
                if AUIFloder:
                    self.ui.plainTextEdit_DatO2.setPlainText('{}'.format(AUIFloder))

                # Touched function
                self.Choose_AnalysisType()
                self.LoadIdbPorFile()
                self.TimeRange()
                self.GenertPloFile()
                self.Loading_PloFile()
                self.GetResultParamsMAT()
                self.InitDataOutput()

                nodePath = '/'.join([DataOutputoutputfloder.replace('\\', '/'), 'Fluid_Nodecoo_Dic.npy'])
                ParamsPath = '/'.join([DataOutputoutputfloder.replace('\\', '/'), 'Fluid_lst_ParamsDic.npy'])
                savePath = '/'.join([DataOutputoutputfloder.replace('\\', '/'), '1'])
                if not os.path.exists(savePath):
                    os.mkdir(savePath)

                Params = np.load(ParamsPath, allow_pickle=True).item()
                node = np.load(nodePath, allow_pickle=True).item()

                for number in Params['range']:
                    timestep = str(Params['timeRange'][number - 1])
                    key_str = 'lst_ParamsMat' + timestep
                    c = np.c_[node['Node_id'], node['Node_coo'], Params[key_str]]
                    path = savePath + '/step' + str(number) + '.csv'
                    np.savetxt(path, c, header='Node ID, Node Coordinate X, Node Coordinate Y, Node Coordinate Z, Velocity X, Velocity Y, Velocity Z, Nodal pressure, Max shear stress', delimiter=",")