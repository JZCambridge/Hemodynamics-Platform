# -*- coding: UTF-8 -*-
'''
@Author  ：YangChen's Piggy
@Date    ：2021/4/19 14:36
'''
#!/usr/bin/python
#  -*- coding: UTF-8 -*

import pandas as pd
import numpy as np
import numpy
import tkinter as tk
import os.path
import re
import os
import time
import os
import sys
# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_YC')
sys.path.insert(0, '../Functions_JZ')
import Preprocess_Mask


from multiprocessing import Pool
#from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import Process
from sklearn.cluster import KMeans
from tkinter import filedialog, dialog
from scipy.spatial import KDTree
from scipy.spatial import distance
from FileDisposing import *
from CFD_FEA_Post_Process import *
# Standard libs
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox,QWidget, QTableWidget, QHBoxLayout, QVBoxLayout, QApplication, QTableWidgetItem, QAbstractItemView,QTabWidget,\
    QDialog,QComboBox, QProgressBar,  QLabel, QStatusBar,QLineEdit, QHeaderView
from PySide2.QtUiTools import QUiLoader
# app = QApplication([])
# MainWindow = QMainWindow()
coo_FilNam = None
lst_FilNam = None
########################################################################################################################
#####################################################Multiprocessor#####################################################

########################################################################################################################
####################### matching the Tissue coord with the noo file and get the matched nodeID##########################
def KNNMatching(InitMat, ObjctMat, IniStartColumnNum, IniEndColumnNum, ObjStartColumnNum, ObjEndColumnNum,IniReturnColumnNum):
    ############################################find the nearest node###################################################
    # ********************************* the nearst node index  ********************************************************#
    MatchedRows_num = []
    # **************************** ***** the nearst distance  **********************************************************#
    min_distance = []
    # ********************************* the  Matched Rows datas in ObjctMat ******************************************#
    MatchedRows = []
    # ********************************* one culumn of  Matched Rows datas in ObjctMat  *******************************#
    MatchedRows_1stColumn = []
    # ******************* the initial datas including all information like pressure coordinates elementid  ************#
    tree = KDTree(InitMat[:,IniStartColumnNum : IniEndColumnNum+1])  #ObjctMat[:,0]is the NodeID of wall elements
    #print(ObjctMat)
    for i in range(len(ObjctMat)):
        dist, InitMatRowsQueryed = tree.query(ObjctMat[i,ObjStartColumnNum : ObjEndColumnNum+1], k=1)
        MatchedRows_num.append(InitMatRowsQueryed)
        MatchedRows.append(InitMat[InitMatRowsQueryed,:])
        MatchedRows_1stColumn.append(InitMat[InitMatRowsQueryed, IniReturnColumnNum]) #return nodeid
        min_distance.append(dist)
    # np.savetxt('min_num.txt', min_num, delimiter=',')
    # np.savetxt('min_dist.txt', min_dist, delimiter=',')
    # np.savetxt('ObjctMat.txt', ObjctMat, delimiter=',')
    # print('min_num',min_num)
    # print('min_dist', min_dist)
    return MatchedRows_num, min_distance, MatchedRows, MatchedRows_1stColumn

def OneIndexMultiple(inMat, inCompareBase, inCompareBaseSameOrder):
    '''Dscription

        Args:
            inMat: initial matrix that includes matched nodesID between Tissue coors and noo file
            inCompareBase: eno file mat
            inCompareBaseSameOrder: single array re-arranged based on 'inCompareBase'

        Returns:
            None:
        '''

    #**************************************************start time******************************************************#
    matchTStrt = time.time()

    #************************************************return info*******************************************************#
    rtrnInfo = {}
    rtrnInfo["Message"] = "Extract matched elments with each Tissue :\n"
    rtrnInfo["Message"] = rtrnInfo["Message"] + "# coordinates from input Tissue: {}\n".format(numpy.shape(inMat))

    #**********************************************create empty mat****************************************************#
    orderMat = numpy.zeros(numpy.shape(inMat))
    outCompareBase = numpy.zeros(numpy.shape(inCompareBase))
    outCompareBaseSameOrder = numpy.zeros(numpy.shape(inCompareBaseSameOrder))
    orderMatRow = 0

    # find index and fill
    rowIndex = []
    # data storage
    MatchedRowSignal = []
    MatchedRowInfoArry = []

    for RecurNum in range(len(inMat)):
        try:
            #*****************find all row num that include the one node in inMat in eno file**************************#
            RowNumReturnTuple = numpy.where(inMat[RecurNum] == inCompareBase)  #the return result of np.where() is a tuple contain list cells
            #*****************************extract all the elmentID for each matched node ******************************#
            for RowNum in range(len(RowNumReturnTuple[0])):
                #MatchedRowInfoArry = np.append(MatchedRowInfo, np.array(inCompareBase[RowNumReturnTuple[0][RowNum]]), axis=0)
                MatchedRowSignal.append(inCompareBase[RowNumReturnTuple[0][RowNum]][0])
        except:
            continue

    #****************************************** delete the repeated nodes  ********************************************#
    MatchedRowSignal_unique = np.unique(MatchedRowSignal)
    matchTStp = time.time()
    matchT = matchTStp - matchTStrt

    # **********************************************return info********************************************************#
    rtrnInfo["MatchedInfo"] = MatchedRowSignal_unique
    rtrnInfo["MatchedRowInfoArry"] = MatchedRowInfoArry
    rtrnInfo["processTime"] = matchT
    rtrnInfo["processTimeMessage"] = "------Match time: {} s------".format(matchT)
    #print(rtrnInfo["processTimeMessage"])
    rtrnInfo["Message"] += rtrnInfo["processTimeMessage"]

    print(rtrnInfo["processTime"])

    # ## compare fully matched
    # if orderMatRow == len(inCompareBase):
    #     rtrnInfo["allMatch"] = True
    # else:
    #     rtrnInfo["allMatch"] = False
    # ## compare no match!
    # if orderMatRow == 0:
    #     rtrnInfo["noMatch"] = True
    # else:
    #     rtrnInfo["noMatch"] = False

    return MatchedRowSignal_unique, MatchedRowInfoArry
def tst():
    print ("hello")


class TissueMaterialAssignment():
    def __init__(self,UI = None,Hedys = None):
        if UI:
            self.ui = UI
        else:
            self.ui = QUiLoader().load(r"E:\GUI\Hedys_test0620\GUI_V0\ui\VtuDataExtraction.ui")
        if Hedys:
            self.modelui = Hedys.ui
        else:
            self.modelui = None

        # ******************************************read the Tissue coors*************************************************
        self.ui.TissueCoorbutton_GI.clicked.connect(lambda: self.ChooseTissueCoors())
        self.ui.TissueCoorbutton_GI.clicked.connect(lambda: self.loadTissueCoorsAbsPathList())
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.TissueMaterialAssignment.ReadTissueCoors())
        # ******************************************read the noo Info*************************************************
        self.ui.WallNodesCoorpushButton_GI.clicked.connect(lambda: self.ChooseSNdCooResults())
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.TissueMaterialAssignment.ReadSNdCooResults())
        # ******************************************read the Hex adn tetral eno Info*************************************************
        self.ui.WallElementNodepushButton_GI.clicked.connect(lambda: self.ChooseSTetraEnoResults())
        self.ui.WallElementNodepushButton_GI.clicked.connect(lambda: self.ReadTetraEnoResults())
        self.ui.WallHexElementNodepushButton_GI.clicked.connect(lambda: self.ChooseSHexEnoResults())
        self.ui.WallHexElementNodepushButton_GI.clicked.connect(lambda: self.ReadSHexEnoResults())
        # ************************************** tissue file's saving directory *************************************************
        self.ui.SaveTissueElementInfopushButton_GI.clicked.connect(lambda: self.DefineExtrctTissueElmentIDSaveDir())
        self.ui.SaveTissueElementInfopushButton_GI.clicked.connect(lambda: self.ExtrctTissueElmentIDSaveDir())
        # ******************************************extract *************************************************
        self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.loadTissueCoorsAbsPathList())
        self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.TissueMatcingMultiprocessor())
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.multiProcess())
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.multiProcess())
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.TotalProcedure('E:/A_Projects/A_Hemodynamics_Platform/materialassign/data/LAR_2dndarr_.npy'))
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.ExtrctTissue_ElmentID())
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.ExtrctTissue_ElmentID())
        # Tissuemultprocessing =  TissueMaterialAssignmentMain.Tissuemultprocessing(TissueMaterialAssignment)
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.TissueMatcingMultiprocessor())
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.run())
        # testClass1 =  TissueMaterialAssignmentMain.testClass(self)
        # self.ui.ExtratpushButton_GI.clicked.connect(lambda: self.testClass1.multiProcess())

        self.InitTissue()

    def InitTissue(self):
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.statusLabel = QLabel()
        self.TissueCoo = None
        self.cooArry = None
        self.HexElmntNodesMat = None
        self.TetraElmntNodesMat = None
        self.HexElmntNodesMat_SameEmpArry = None
        self.TetraElmntNodesMat_SameEmpArry = None
        self.MatchedScooArryNodesID = None
        self.MatchedScooArryNodesID_SameEmpArry = None
        self.MatchedTissue_ElmentID_unique = None
        self.MatchedTissue_ElmentRowInfoArry = None
        self.ExtrctTissue_ElmentIDSaveDir = None
        self.TissueCoorsAbsPathList = None
        self.TissueCoorsFilNam = None
        self.OneTissueCoorsAbsPath = None


    ####################################################################################################################
    ######################################## read the Tissue coors ###############################################
    def ChooseTissueCoors(self):
        # ***************************** Extract the coordinates of each components ************************************#
        TissueCooFil = Opening_Files(self.ui, "Tissue Coordinate (*.npy)")
        self.ui.TissueCoortxt_GI.clear()
        for listele in TissueCooFil:
            listele += ','
            self.ui.TissueCoortxt_GI.appendPlainText(listele)
        #print("self.ui.TissueCoortxt_GI.setPlainText(TissueCooFil)",self.ui.TissueCoortxt_GI.toPlainText(),type(self.ui.TissueCoortxt_GI.toPlainText()))

    def loadTissueCoorsAbsPathList(self):
        self.TissueCoorsAbsPathList = Preprocess_Mask.StrToLst(strIn=self.ui.TissueCoortxt_GI.toPlainText())["listOut"]
        # for eachitem in self.TissueCoorsAbsPathList:
        #     _, self.TissueCoorsFilNam, _ = Split_AbsFilePath(eachitem)
        #     self.TissueCoorsFilNameList.append(self.TissueCoorsFilNam)
        #return self.TissueCoorsAbsPathList, self.TissueCoorsFilNameList
        return self.TissueCoorsAbsPathList

    def ReadTissueCoors(self,):
        if self.OneTissueCoorsAbsPath:
            self.TissueCoo = LoadNPY(self.OneTissueCoorsAbsPath)["data"]
        else:
            self.TissueCoo = []
            QMessageBox.warning(
                self.ui,
                'Warning',
                "Don't open tissue coordinates file successfully"
            )
        return self.TissueCoo
        # print("TissueCoo shape",TissueCoo,  type(TissueCoo), TissueCoo.shape)
        # TissueCoo["LypidPool"] = np.array([[6.230706e+01, 6.590672e+01]])
        # TissueCoo["Thrombus"] = np.array([[6.70706e+01, 6.490672e+01]])

    ####################################################################################################################
    ############################################### read the noo Info ##################################################
    def ChooseSNdCooResults(self):
        # ******************************************** load .npy  *****************************************************#
        Ndcoo = Opening_File(self.ui, "NodeCoordinates (*.npy)")
        self.ui.WallNodesCoortxt_GI.setPlainText(Ndcoo)
        # ****************************************** node cooridnates *************************************************#
    def ReadSNdCooResults(self):
        if  self.ui.WallNodesCoortxt_GI.toPlainText():
            Nodesid = LoadNPY(self.ui.WallNodesCoortxt_GI.toPlainText())["data"]["Node_id"]
            Nodecoo = LoadNPY(self.ui.WallNodesCoortxt_GI.toPlainText())["data"]["Node_coo"]
            self.ScooArry = np.zeros((np.size(Nodesid, 0), 4))
            self.ScooArry[:, 0] = Nodesid
            self.ScooArry[:, 1:4] = Nodecoo[:, 0:3]
        else:
            self.ScooArry = []
            QMessageBox.warning(
                self.ui,
                'Warning',
                "Open Solid Node_coordinates file unsuccessfully")
        return  self.ScooArry

########################################################################################################################
########################################### read the Hex adn tetral eno Info############################################
    def ChooseSTetraEnoResults(self):
        # ********************************* load .npy  ********************************************************************#
        # ElmntNodesInfo = Opening_Files(self.ui, "HexElmnt (*.npy)")
        # print("ElmntNodesInfo",ElmntNodesInfo,type(ElmntNodesInfo))
        TetraElmntNodes = Opening_File(self.ui, "TetraElmnt (*.npy)")
        self.ui.WallElementNodetst_GI.setPlainText(TetraElmntNodes)
    def ReadTetraEnoResults(self):
        # ****************************************** node cooridnates *****************************************************#
        if self.ui.WallElementNodetst_GI.toPlainText():
            self.TetraElmntNodesMat = LoadNPY(self.ui.WallElementNodetst_GI.toPlainText())["data"]
        else:
            self.TetraElmntNodesMat = []
            print("not use tetralelements and nodes datas")
        # ****************************************** creat empty array ****************************************************#
        self.TetraElmntNodesMat_SameEmpArry  = numpy.zeros(numpy.shape(self.TetraElmntNodesMat))
        return self.TetraElmntNodesMat,self.TetraElmntNodesMat_SameEmpArry

    def ChooseSHexEnoResults(self):
        # ********************************* load .npy  ********************************************************************#
        # ElmntNodesInfo = Opening_Files(self.ui, "HexElmnt (*.npy)")
        # print("ElmntNodesInfo",ElmntNodesInfo,type(ElmntNodesInfo))
        HexElmntNodes = Opening_File(self.ui, "HexElmnt (*.npy)")
        self.ui.WallHexElementNodetst_GI.setPlainText(HexElmntNodes)

    def ReadSHexEnoResults(self):
        #****************************************** Nodeset id ***********************************************************#
        if self.ui.WallHexElementNodetst_GI.toPlainText():
            self.HexElmntNodesMat = LoadNPY(self.ui.WallHexElementNodetst_GI.toPlainText())["data"]
        else:
            self.HexElmntNodesMat = []
            print("not use hexelements and nodes datas")#########################################
        #print("nosArry shape", nosArry.shape)
        # ****************************************** creat empty array ****************************************************#
        self.HexElmntNodesMat_SameEmpArry = numpy.zeros(numpy.shape(self.HexElmntNodesMat))
        return self.HexElmntNodesMat, self.HexElmntNodesMat_SameEmpArry

    def DefineExtrctTissueElmentIDSaveDir(self):
        self.ExtrctTissue_ElmentIDSaveDir = Opening_FileDialog(self.ui)
        self.ui.SaveTissueElementInfoText_GI.setPlainText(self.ExtrctTissue_ElmentIDSaveDir)
        return self.ExtrctTissue_ElmentIDSaveDir

    def ExtrctTissueElmentIDSaveDir(self):
        self.ui.SaveTissueElementInfoText_GI.toPlainText()
########################################################################################################################
###################matching ndcoo Info with Tissuecoors,and reture the matched nodcoo row nums####################
    def ExtrctTissueElmentID (self):
        #*********************matching the Tissue coord with the noo file and get the matched nodeID*************#
        MatchedScooArryRows_num, ScooArrymin_distance, MatchedScooArryRows, self.MatchedScooArryNodesID \
            = KNNMatching(self.ScooArry, self.TissueCoo, 1,3,0,2,0)
        MatchedScooArryNodesID_SameEmpArry = numpy.zeros(numpy.shape(self.MatchedScooArryNodesID))
        #***************extract the row number of eno file matched with pre Tissue_coord_matched nodes***********#
        self.MatchedTissue_ElmentID_unique, self.MatchedTissue_ElmentRowInfoArry = \
            OneIndexMultiple(self.MatchedScooArryNodesID, self.TetraElmntNodesMat, MatchedScooArryNodesID_SameEmpArry)
        ###################PS:don't consider the hexmesh matching
        #######
        ########
        #print("MatchedTissue_ElmentID_unique",self.MatchedTissue_ElmentID_unique,"MatchedTissue_ElmentRowInfoArry",self.MatchedTissue_ElmentRowInfoArry)
        np.savetxt(self.ui.SaveTissueElementInfoText_GI.toPlainText() + self.TissueCoorsFilNam + ".csv", self.MatchedTissue_ElmentID_unique,
                   delimiter=",")
        # np.savetxt("./"+ self.TissueCoorsFilNam + ".txt",
        #            self.MatchedTissue_ElmentID_unique,
        #            delimiter=",")
        print('done')
        return  self.MatchedTissue_ElmentID_unique,  self.MatchedTissue_ElmentRowInfoArry

    def TotalProcedure(self):
        #print("0")
        self.ReadTissueCoors()
        #print("1")
        self.ReadSNdCooResults()
        #print("2")
        self.ReadTetraEnoResults()
        #print("3")
        self.ReadSHexEnoResults()
        #print("4")
        self.ExtrctTissueElmentIDSaveDir()
        #print("5")
        self.ExtrctTissueElmentID()
        #print("6")
        time.sleep(1)
    def TissueMatcingMultiprocessor(self):
        multipool = Pool(10)
        i = 1
        for OneTissueCoorsAbsPath in self.TissueCoorsAbsPathList:
            print("processing", i)
            self.OneTissueCoorsAbsPath = OneTissueCoorsAbsPath
            _, self.TissueCoorsFilNam, _ = Split_AbsFilePath(OneTissueCoorsAbsPath)
            multipool.apply_async(self(self), args=(OneTissueCoorsAbsPath,))
            i+=1

            #multipool.map(self(self), self.TissueCoorsAbsPathList)
        multipool.close()
        multipool.join()

    def __call__(self, *args, **kwds):  #
        return self.TotalProcedure()
        #return self.TotalProcedure('E:/A_Projects/A_Hemodynamics_Platform/materialassign/data/LAR_2dndarr_.npy')


# if __name__ == "__main__":
#  # run()
#     MainWindow.show()
#     app.exec_()