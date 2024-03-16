# -*- coding: utf-8 -*-
"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by
Jin ZHENG JZ410 (29Mar21)
"""

##############################################################################
# Import functions from JZ410
import sys
import os

# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
# Import functions
import Save_Load_File
import Image_Process_Functions
import Post_Image_Process_Functions
import Preprocess_Mask
import QT_GUI
import Pd_Funs
import Matrix_Math
##############################################################################

##############################################################################
# Standard library
from datetime import datetime
import time
import threading
import numpy
import pandas
from PySide2.QtUiTools import QUiLoader
##############################################################################

class AreaVolCalcs:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI

            self.ui.choose1stFileBtn_AVC.clicked.connect(lambda: self.ChooseFile(self.ui.load1stPathTxt_AVC))
            self.ui.choose2ndFileBtn_AVC.clicked.connect(lambda: self.ChooseFile(self.ui.load2ndPathTxt_AVC))
            self.ui.choose3rdFileBtn_AVC.clicked.connect(lambda: self.ChooseFile(self.ui.load3rdPathTxt_AVC))
            self.ui.loadCalcArea1stBtn_AVC.clicked.connect(lambda: self.CalcMeanArea1st())
            self.ui.loadCalcArea2ndBtn_AVC.clicked.connect(lambda: self.CalcMeanArea2nd())
            self.ui.loadCalcArea3rdBtn_AVC.clicked.connect(lambda: self.CalcMeanArea3rd())
            self.ui.murraysLawBtn_AVC.clicked.connect(lambda: self.MurrayLaw())
            self.ui.CABtn_AVC.clicked.connect(lambda: self.CACalcs())
            self.ui.chooseTXTBtn_AVC.clicked.connect(lambda: self.ChooseTXTFile())
            self.ui.saveTXTBtn_AVC.clicked.connect(lambda: self.SaveTXTFile())
            self.ui.chooseCSVBtn_AVC.clicked.connect(lambda: self.ChooseCSVFile())
            self.ui.saveCSVBtn_AVC.clicked.connect(lambda: self.ChooseTableFile())
            self.ui.csvMultiplyBtn_AVC.clicked.connect(lambda: self.OutputCSV())
            self.ui.chooseDir2Btn_AVC.clicked.connect(lambda: self.ChooseLoadDir2())
            self.ui.murraysLaw2Btn_AVC.clicked.connect(lambda: self.MurrayRedistribution())
            self.ui.chooseDir3Btn_AVC.clicked.connect(lambda: self.ChooseLoadDir3())
            self.ui.murraysLaw3Btn_AVC.clicked.connect(lambda: self.MurrayFlowConservation())
            self.ui.parameterTableFileBtn_AVC.clicked.connect(lambda: self.ChooseParameterTableFile())
            self.ui.branchMapTableBtn_AVC.clicked.connect(lambda: self.ChooseBranchMapTableFile())
            self.ui.autoType3Btn_AVC.clicked.connect(lambda: self.AutoType3())
            self.ui.autoBatchType3TableBtn_AVC.clicked.connect(lambda: self.ChooseBatchType3AutoTableFile())
            self.ui.autoBatchType3Btn_AVC.clicked.connect(lambda: self.BatchAutoType3())

        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
            

        # initial definition
        self.mask1st = None
        self.mask2nd = None
        self.mask3rd = None
        self.outMsgGeneralMurray = ''
        self.outMsgMurrayLaw1 = ''
        self.outMsgMurrayLaw2 = ''
        self.outMsgMurrayLaw3 = ''

    def ChooseFile(self, path):
        # set file name
        QT_GUI.ChooseFile(dispMsg="Choose the first segmentation file",
                          displayText=path,
                          updateMsgFunc=self.UpdateMsgLog)

    def LoadData1st(self):
        # load and set data
        self.mask1st = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.load1stPathTxt_AVC.toPlainText()
        )
        # update message
        self.UpdateMsgLog(msg="Load file:\n{}".format(self.ui.load1stPathTxt_AVC.toPlainText()))

    def LoadData2nd(self):
        # load and set data
        self.mask2nd = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.load2ndPathTxt_AVC.toPlainText()
        )
        # update message
        self.UpdateMsgLog(msg="Load file:\n{}".format(self.ui.load2ndPathTxt_AVC.toPlainText()))

    def LoadData3rd(self):
        # load and set data
        self.mask3rd = Save_Load_File.OpenLoadNIFTI(
            GUI=False,
            filePath=self.ui.load3rdPathTxt_AVC.toPlainText()
        )
        # update message
        self.UpdateMsgLog(msg="Load file:\n{}".format(self.ui.load3rdPathTxt_AVC.toPlainText()))

    def CalcMeanArea1st(self):
        # load
        self.LoadData1st()

        # get array of values
        self.lstOut = Preprocess_Mask.StrToLst(strIn=self.ui.filterVal1stTxt_AVC.toPlainText())

        # Filter value
        dataFilterVals, dataFilterOnes = Image_Process_Functions.FilterData(
            rangStarts=self.lstOut["floatOut"],
            dataMat=self.mask1st.OriData,
            funType="single value"
        )

        # Average area
        area1st = Post_Image_Process_Functions.AverageArea(
            inData=dataFilterOnes,
            thres=0
        )

        # area choice
        areaChoice = self.ui.areaChoiceFirstCBox_LC.currentText()
        area = 0
        if areaChoice == "Mean":
            area = area1st["averageArea"]
        elif areaChoice == "Median":
            area = area1st["medianArea"]
        elif areaChoice == "Max":
            area = area1st["maxArea"]
        elif areaChoice == "Min":
            area = area1st["minArea"]
        elif areaChoice == "Q1":
            area = area1st["Q1Area"]
        elif areaChoice == "Q3":
            area = area1st["Q3Area"]

        # update
        self.UpdateMsgLog(msg=area1st["Message"])
        # set values
        self.ui.areaNumeratorLineTxt_AVC.setText(str(area))
        self.ui.areaRCALineTxt_AVC.setText(str(area))
        self.ui.areaRCA2LineTxt_AVC.setText(str(area))
        self.ui.areaRCA3LineTxt_AVC.setText(str(area))
        self.ui.area1stLineTxt_AVC.setText(str(area))

    def CalcMeanArea2nd(self):
        # load
        self.LoadData2nd()

        # get array of values
        self.lstOut = Preprocess_Mask.StrToLst(strIn=self.ui.filterVal2ndTxt_AVC.toPlainText())

        # Filter value
        dataFilterVals, dataFilterOnes = Image_Process_Functions.FilterData(
            rangStarts=self.lstOut["floatOut"],
            dataMat=self.mask2nd.OriData,
            funType="single value"
        )

        # Average area
        area2nd = Post_Image_Process_Functions.AverageArea(
            inData=dataFilterOnes,
            thres=0
        )

        # area choice
        areaChoice = self.ui.areaChoiceSecondCBox_LC.currentText()
        area = 0
        if areaChoice == "Mean":
            area = area2nd["averageArea"]
        elif areaChoice == "Median":
            area = area2nd["medianArea"]
        elif areaChoice == "Max":
            area = area2nd["maxArea"]
        elif areaChoice == "Min":
            area = area2nd["minArea"]
        elif areaChoice == "Q1":
            area = area2nd["Q1Area"]
        elif areaChoice == "Q3":
            area = area2nd["Q3Area"]

        # update
        self.UpdateMsgLog(msg=area2nd["Message"])
        # set values
        self.ui.areaDenominatorLineTxt_AVC.setText(str(area))
        self.ui.areaLCALineTxt_AVC.setText(str(area))
        self.ui.areaLCA2LineTxt_AVC.setText(str(area))
        self.ui.areaLCA3LineTxt_AVC.setText(str(area))
        self.ui.area2ndLineTxt_AVC.setText(str(area))

    def CalcMeanArea3rd(self):
        # load
        self.LoadData3rd()

        # get array of values
        self.lstOut = Preprocess_Mask.StrToLst(strIn=self.ui.filterVal3rdTxt_AVC.toPlainText())

        # Filter value
        dataFilterVals, dataFilterOnes = Image_Process_Functions.FilterData(
            rangStarts=self.lstOut["floatOut"],
            dataMat=self.mask3rd.OriData,
            funType="single value"
        )

        # Average area
        area3rd = Post_Image_Process_Functions.AverageArea(
            inData=dataFilterOnes,
            thres=0
        )

        # area choice
        areaChoice = self.ui.areaChoiceThirdCBox_LC.currentText()
        area = 0
        if areaChoice == "Mean":
            area = area3rd["averageArea"]
        elif areaChoice == "Median":
            area = area3rd["medianArea"]
        elif areaChoice == "Max":
            area = area3rd["maxArea"]
        elif areaChoice == "Min":
            area = area3rd["minArea"]
        elif areaChoice == "Q1":
            area = area3rd["Q1Area"]
        elif areaChoice == "Q3":
            area = area3rd["Q3Area"]

        # update
        self.UpdateMsgLog(msg=area3rd["Message"])
        # set values
        self.ui.areaBranchLineTxt_AVC.setText(str(area))
        self.ui.area3rdLineTxt_AVC.setText(str(area))

    def MurrayLaw(self):
        # get info
        try:
            num = float(self.ui.areaNumeratorLineTxt_AVC.text())
            den = float(self.ui.areaDenominatorLineTxt_AVC.text())
            expo = float(self.ui.murrayExponentLineTxt_AVC.text())
        except:
            # update message
            self.UpdateMsgLog(
                msg="ERROR: Need input denominator, nominator and exponent values!"
            )
            return

        # calculation
        areaRatio = num / den
        murrayResult = areaRatio ** (expo / 2)

        # set values
        self.ui.areaRatioLineTxt_AVC.setText(str(areaRatio))
        self.ui.murrayLineTxt_AVC.setText(str(murrayResult))

        self.outMsgGeneralMurray = "\n################### Area Fraction & Murray's Law ###########################" \
                                   "\nArea ratio A/B: {}" \
                                   "\nA/B Murray's Law: {}" \
                                   "\n##########################################################################".format(
            self.ui.areaRatioLineTxt_AVC.text(),
            self.ui.murrayLineTxt_AVC.text())

        # update message
        self.UpdateMsgLog(
            msg=self.outMsgGeneralMurray
        )

    def CACalcs(self):
        # get info
        try:
            RCA = float(self.ui.areaRCALineTxt_AVC.text())
            LCA = float(self.ui.areaLCALineTxt_AVC.text())
            branch = float(self.ui.areaBranchLineTxt_AVC.text())
            expo = float(self.ui.exponentLineTxt_AVC.text())
            inflow = float(self.ui.inflowLineTxt_AVC.text())
            CABranch = self.ui.CABtnGrp_AVC.checkedButton().text()
        except:
            # update message
            self.UpdateMsgLog(
                msg="ERROR: Need input RCA, LCA, inflow and exponent values!"
            )
            return

        # RCA/LCA
        RL = RCA / LCA
        k = RL ** (expo / 2)

        # set values
        self.ui.RCALCARatioLineTxt_AVC.setText(str(RL))
        self.ui.murrayRCALCALineTxt_AVC.setText(str(k))

        # LCA, RCA branch calculation
        LCAFlow = inflow / (1 + k)
        RCAFlow = inflow * k / (1 + k)

        # set values
        self.ui.RCAOutflowLineTxt_AVC.setText(str(RCAFlow))
        self.ui.LCAOutflowLineTxt_AVC.setText(str(LCAFlow))

        # branch results
        mainArea = None
        mainflow = None
        if CABranch == "RCA":
            mainArea = RCA
            mainflow = RCAFlow
        elif CABranch == "LCA":
            mainArea = LCA
            mainflow = LCAFlow

        branMain = branch / mainArea
        branML = branMain ** (expo / 2)
        branFlow = branML * mainflow

        # set values
        self.ui.branMainLineTxt_AVC.setText(str(branMain))
        self.ui.branMLLineTxt_AVC.setText(str(branML))
        self.ui.branFlowLineTxt_AVC.setText(str(branFlow))
        self.ui.tableMultiplesTxt_LC.setPlainText(str(branFlow))

        self.outMsgMurrayLaw1 = "\n############# Coronary Artery Flow Distribution & Murray's Law #############" \
                                "\nRCA/LCA ratio: {}" \
                                "\nRCA/LCA Murray's law: {}" \
                                "\nRCA outflow: {}" \
                                "\nLCA outflow: {}" \
                                "\nBranch/Main ratio: {}" \
                                "\nBranch/Main Murray's law: {}" \
                                "\nBranch outflow: {}" \
                                "\n##########################################################################".format(
            self.ui.RCALCARatioLineTxt_AVC.text(),
            self.ui.murrayRCALCALineTxt_AVC.text(),
            self.ui.RCAOutflowLineTxt_AVC.text(),
            self.ui.LCAOutflowLineTxt_AVC.text(),
            self.ui.branMainLineTxt_AVC.text(),
            self.ui.branMLLineTxt_AVC.text(),
            self.ui.branFlowLineTxt_AVC.text())

        # update message
        self.UpdateMsgLog(
            msg=self.outMsgMurrayLaw1
        )

    """
    ##############################################################################
    # Murray's Law Redistribution
    ##############################################################################
    """

    def ChooseLoadDir2(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Load data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.areaBranchFolder2Txt_AVC.setPlainText(dirname)
        # update message
        self.UpdateMsgLog(
            msg='Choose: {}'.format(dirname)
        )

    def MurrayRedistribution(self):
        # get info
        print(float(self.ui.areaRCA2LineTxt_AVC.text()))
        print(float(self.ui.areaLCA2LineTxt_AVC.text()))
        print(self.ui.areaBranchFolder2Txt_AVC.toPlainText())
        print(self.ui.areaBranchFiles2Txt_AVC.toPlainText())
        print(self.ui.areaBranchLbls2Txt_AVC.toPlainText())
        print(self.ui.exponent2LineTxt_AVC.text())
        print(self.ui.inflow2LineTxt_AVC.text())
        print(self.ui.CABtnGrp2_AVC.checkedButton().text())
        try:
            RCA = float(self.ui.areaRCA2LineTxt_AVC.text())
            LCA = float(self.ui.areaLCA2LineTxt_AVC.text())
            branchFolder = self.ui.areaBranchFolder2Txt_AVC.toPlainText()
            branchFiles = Preprocess_Mask.StrToLst(self.ui.areaBranchFiles2Txt_AVC.toPlainText())["listOut"]
            branchLbls = Preprocess_Mask.StrToLst(self.ui.areaBranchLbls2Txt_AVC.toPlainText())["intOut"]
            expo = float(self.ui.exponent2LineTxt_AVC.text())
            inflow = float(self.ui.inflow2LineTxt_AVC.text())
            CABranch = self.ui.CABtnGrp2_AVC.checkedButton().text()
        except:
            # update message
            self.UpdateMsgLog(
                msg="ERROR: Need input RCA, LCA, inflow and exponent values!"
            )
            return

        # Combine folder and files
        print(branchFolder)
        print(branchFiles)
        branchFullFiles = Save_Load_File.AppendLists([branchFolder], branchFiles, sep="/")["combineList"]

        # compare list length
        compareLsts = Post_Image_Process_Functions.CompareListDimension(
            lsts=[branchFullFiles, branchLbls]
        )
        if compareLsts["error"]:
            print(branchFullFiles)
            print(branchLbls)
            self.UpdateMsgLog('Murray Redistribution: Not the Same list length!!!')
            return

        # Mean area calculation
        areaLst = Post_Image_Process_Functions.AreaList(
            files=branchFullFiles,
            lbls=branchLbls
        )

        # inflow
        # RCA/LCA
        RL = RCA / LCA
        k = RL ** (expo / 2)

        # set values
        self.ui.RCALCARatio2LineTxt_AVC.setText(str(RL))
        self.ui.murrayRCALCA2LineTxt_AVC.setText(str(k))

        # LCA, RCA branch calculation
        LCAFlow = inflow / (1 + k)
        RCAFlow = inflow * k / (1 + k)

        # set values
        self.ui.RCAOutflow2LineTxt_AVC.setText(str(RCAFlow))
        self.ui.LCAOutflow2LineTxt_AVC.setText(str(LCAFlow))

        # branch results
        mainArea = None
        mainflow = None
        if CABranch == "RCA":
            mainArea = RCA
            mainflow = RCAFlow
        elif CABranch == "LCA":
            mainArea = LCA
            mainflow = LCAFlow

        # Redistribution
        flowOut = Matrix_Math.RedistributionLst(
            lst=areaLst,
            exponent=expo / 2,
            totalValue=mainflow
        )

        # msg
        self.outMsgMurrayLaw2 = "############# Coronary Artery Flow Type 2 Redistribution #############" + \
                                "\nArtery Branch Calculation: " + CABranch + \
                                "\nTotal flow: {} & !{}! Branch Flow: {}".format(inflow, CABranch, mainflow) + \
                                "\nFlow redistribution: "

        for i in range(len(branchFiles)):
            self.outMsgMurrayLaw2 += '\nCase: {} [Label = {}] -- area: {} >> Flow: {}'.format(branchFiles[i],
                                                                                              branchLbls[i], areaLst[i],
                                                                                              flowOut[i])

        self.outMsgMurrayLaw2 += "\n##########################################################################"

        # Update message
        self.ui.murrayLaw2PathTxt_AVC.setPlainText(self.outMsgMurrayLaw2)
        self.ui.murrayLaw2OutTxt_AVC.setPlainText(self.outMsgMurrayLaw2)

        # update message
        self.UpdateMsgLog(
            msg=self.outMsgMurrayLaw2
        )

    """
    ##############################################################################
    # Murray's Law Flow Conservation
    ##############################################################################
    """

    def ChooseLoadDir3(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(dispMsg="Load data directory",
                                               fileObj=self.ui,
                                               qtObj=True)

        # set filename
        self.ui.areaBranchFolder3Txt_AVC.setPlainText(dirname)
        # update message
        self.UpdateMsgLog(
            msg='Choose: {}'.format(dirname)
        )

    def MurrayFlowConservation(self):
        # get info
        print(float(self.ui.areaRCA3LineTxt_AVC.text()))
        print(float(self.ui.areaLCA3LineTxt_AVC.text()))
        print(self.ui.areaBranchFolder3Txt_AVC.toPlainText())
        print(self.ui.areaBranchFiles3Txt_AVC.toPlainText())
        print(self.ui.areaBranchLbls3Txt_AVC.toPlainText())
        print(self.ui.exponent3LineTxt_AVC.text())
        print(self.ui.inflow3LineTxt_AVC.text())
        print(self.ui.CABtnGrp3_AVC.checkedButton().text())
        print(self.ui.targetRatioLineTxt_AVC.text())
        print(self.ui.stepSizeLineTxt_AVC.text())
        try:
            RCA = float(self.ui.areaRCA3LineTxt_AVC.text())
            LCA = float(self.ui.areaLCA3LineTxt_AVC.text())
            branchFolder = self.ui.areaBranchFolder3Txt_AVC.toPlainText()
            branchFiles = Preprocess_Mask.StrToLst(self.ui.areaBranchFiles3Txt_AVC.toPlainText())["listOut"]
            branchLbls = Preprocess_Mask.StrToLst(self.ui.areaBranchLbls3Txt_AVC.toPlainText())["intOut"]
            areachoices = Preprocess_Mask.StrToLst(self.ui.areaChoicesLbls3Txt_AVC.toPlainText())["listOut"]
            expo = float(self.ui.exponent3LineTxt_AVC.text())
            inflow = float(self.ui.inflow3LineTxt_AVC.text())
            targetRatio = float(self.ui.targetRatioLineTxt_AVC.text())
            stepSize = int(self.ui.stepSizeLineTxt_AVC.text())
            CABranch = self.ui.CABtnGrp3_AVC.checkedButton().text()
        except:
            # update message
            self.UpdateMsgLog(
                msg="ERROR: Need input RCA, LCA, inflow and exponent values!"
            )
            return

        # Combine folder and files
        branchFullFiles = Save_Load_File.AppendLists([branchFolder], branchFiles, sep="/")["combineList"]

        # compare list length
        compareLsts = Post_Image_Process_Functions.CompareListDimension(
            lsts=[branchFullFiles, branchLbls, areachoices]
        )
        if compareLsts["error"]:
            self.UpdateMsgLog('Murray Redistribution: Not the Same list length!!!')
            return

        # all area calculation
        arrLst = Image_Process_Functions.RemoveEmptySlices(
            files=branchFullFiles,
            lbls=branchLbls
        )

        # inflow
        # RCA/LCA
        RL = RCA / LCA
        k = RL ** (expo / 2)

        # set values
        self.ui.RCALCARatio3LineTxt_AVC.setText(str(RL))
        self.ui.murrayRCALCA3LineTxt_AVC.setText(str(k))

        # LCA, RCA branch calculation
        LCAFlow = inflow / (1 + k)
        RCAFlow = inflow * k / (1 + k)

        # set values
        self.ui.RCAOutflow3LineTxt_AVC.setText(str(RCAFlow))
        self.ui.LCAOutflow3LineTxt_AVC.setText(str(LCAFlow))

        # branch results
        mainArea = None
        mainflow = None
        if CABranch == "RCA":
            mainArea = RCA
            mainflow = RCAFlow
        elif CABranch == "LCA":
            mainArea = LCA
            mainflow = LCAFlow

        # Flow conservation
        areaLst, flowDivide, minRatio = Matrix_Math.ScanConservationLst(
            arrLst=arrLst,
            exponent=expo / 2,
            targetSum=mainArea,
            targetRatio=targetRatio,
            totalValue=mainflow,
            stepSize=stepSize,
            areaChoices=areachoices
        )

        # msg
        self.outMsgMurrayLaw3 = "############# Coronary Artery Flow Type 3 Flow Conservation #############" + \
                                "\nArtery Branch Calculation: " + CABranch + \
                                "\nTotal flow: {} & !{}! Branch Flow: {}".format(inflow, CABranch, mainflow)

        if minRatio <= targetRatio:
            self.outMsgMurrayLaw3 += "\nFind Slices Satisfy the Target Difference: {} " \
                                     "\nThe Minimum Difference is {} :):)".format(targetRatio, minRatio)
        else:
            self.outMsgMurrayLaw3 += "\nCANNOT Find Slices Satisfy the Target Difference: {} " \
                                     "\nThe Minimum Difference is {} :(:(".format(targetRatio, minRatio)
        for i in range(len(branchFiles)):
            self.outMsgMurrayLaw3 += '\nCase: {} [Label = {}] -- Area: {} >> Flow: {}'.format(branchFiles[i],
                                                                                              branchLbls[i], areaLst[i],
                                                                                              flowDivide[i])

        self.outMsgMurrayLaw3 += "\n##########################################################################"

        # Update message
        self.ui.murrayLaw3PathTxt_AVC.setPlainText(self.outMsgMurrayLaw3)
        self.ui.murrayLaw3OutTxt_AVC.setPlainText(self.outMsgMurrayLaw3)

        # update message
        self.UpdateMsgLog(
            msg=self.outMsgMurrayLaw3
        )

    """
    ##############################################################################
    # Output TXT
    ##############################################################################
    """

    def ChooseTXTFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="TXT file output path",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "TXT files (*.txt) ;; ",
                                                 qtObj=True)

        # set filename
        self.ui.saveTXTPathTxt_AVC.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose TXT file path:\n{}".format(
                self.ui.saveTXTPathTxt_AVC.toPlainText()
            )
        )

    def SaveTXTFile(self):
        # save txt
        msg = "\n" + datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        msg += self.outMsgGeneralMurray + '\n'
        msg += self.outMsgMurrayLaw1 + '\n'
        msg += self.outMsgMurrayLaw2 + '\n'
        msg += self.outMsgMurrayLaw3

        Save_Load_File.WriteTXT(
            path=self.ui.saveTXTPathTxt_AVC.toPlainText(),
            txt=msg,
            mode="append"
        )

        # update message
        self.UpdateMsgLog(
            msg="Save TXT file:\n{}".format(
                self.ui.saveTXTPathTxt_AVC.toPlainText()
            )
        )

    """
    ##############################################################################
    # Modify csv
    ##############################################################################
    """

    def ChooseCSVFile(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Input table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.openTableTxt_AVC.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose input Table file path:\n{}".format(
                self.ui.openTableTxt_AVC.toPlainText()
            )
        )

    def ChooseTableFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(
            dispMsg="output table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.saveTablePathTxt_AVC.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose output Table file path:\n{}".format(
                self.ui.saveTablePathTxt_AVC.toPlainText()
            )
        )

    def OutputCSV(self):
        # get all input
        inPath = self.ui.openTableTxt_AVC.toPlainText()
        outPath = self.ui.saveTablePathTxt_AVC.toPlainText()
        columns = Preprocess_Mask.StrToLst(
            strIn=self.ui.tableColumnsTxt_LC.toPlainText()
        )["floatOut"]
        multiples = Preprocess_Mask.StrToLst(
            strIn=self.ui.tableMultiplesTxt_LC.toPlainText()
        )["floatOut"]
        addMultiple = float(self.ui.tableAddMultiplesTxt_LC.toPlainText())

        # csv output
        rtrnInfo = Pd_Funs.MultiplyCSVColumns(
            inPath=inPath,
            multiples=numpy.multiply(multiples, addMultiple),
            columns=columns,
            outPath=outPath
        )

        # update message
        self.UpdateMsgLog(
            msg=rtrnInfo["message"]
        )

    """
    ##############################################################################
    # Automate Type 3 and Type 2 calculation
    ##############################################################################
    """
    def ChooseParameterTableFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(
            dispMsg="Parameter table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.parametersPathTxt_AVC.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose parameter Table file path:\n{}".format(
                self.ui.parametersPathTxt_AVC.toPlainText()
            )
        )

    def ChooseBranchMapTableFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(
            dispMsg="Branch map table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.branchMapPathTxt_AVC.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose branch map Table file path:\n{}".format(
                self.ui.branchMapPathTxt_AVC.toPlainText()
            )
        )

    def ChooseBatchType3AutoTableFile(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(
            dispMsg="Batch Type3 Automation table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.batchType3PathTxt_AVC.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose batch Table file path:\n{}".format(
                self.ui.batchType3PathTxt_AVC.toPlainText()
            )
        )

    def AutoType3(self, parametersPath=None, branchMapPath=None):
        # get input
        if parametersPath is None:
            parametersPath = self.ui.parametersPathTxt_AVC.toPlainText()
        if branchMapPath is None:
            branchMapPath = self.ui.branchMapPathTxt_AVC.toPlainText()

        # load DFs
        dfParameters = Pd_Funs.OpenDF(
            inPath=parametersPath,
            header=0,
            usecols=None
        )
        dfBranchMap = Pd_Funs.OpenDF(
            inPath=branchMapPath,
            header=0,
            usecols=None
        )

        # parameters
        inflow = float(dfParameters["Total Inflow"][0])
        threshold = float(dfParameters["Threshold"][0])
        step = int(dfParameters["Step"][0])
        outFolder = dfParameters["Output Folder"][0]
        expo = float(dfParameters["Exponential"][0])
        multipleStrs = dfParameters["Multiple"][0]

        nameRefs = dfBranchMap["Name Reference"].tolist()
        branchLbls = dfBranchMap["Branch Label"].tolist()
        filePaths = dfBranchMap["Mask Path"].tolist()
        sliceStarts = dfBranchMap["Start Slice"].tolist()
        sliceStops = dfBranchMap["Finish Slice"].tolist()
        maskLabels = dfBranchMap["Mask Label"].tolist()
        areaChoices = dfBranchMap["Area Choice"].tolist()
        refFiles = dfBranchMap["Reference File"].tolist()
        # averageArea, medianArea, Q1Area, Q3Area, minArea, maxArea

        # create branch label lists
        branchLblLsts = []
        maxLstLength = 0
        branchLblLstLengths = []
        print(branchLbls)
        for branchLst in branchLbls:
            # create list based on
            if isinstance(branchLst, int):
                lstTmp = [branchLst]
            elif isinstance(branchLst, str):
                lstTmp = Matrix_Math.ConvertListType(lst=branchLst.split(','), type=int)
            else:
                raise ValueError("Type error: {} with type: {}".format(branchLst, type(branchLst)))

            lengthTmp = len(lstTmp)

            # append
            branchLblLsts.append(lstTmp)
            branchLblLstLengths.append(lengthTmp)

            # max length
            if lengthTmp > maxLstLength:
                maxLstLength = lengthTmp

        # update
        self.UpdateMsgLog("Branch label to lists: \n{}".format(branchLblLsts))

        # fill list to check calculate flow or not
        findFlow = [False] * len(branchLbls)
        endBranches = [True] * len(branchLbls)
        areaConservative = [False] * len(branchLbls)
        parentBranches = [None] * len(branchLbls)
        distributeFlow = [0] * len(branchLbls)
        useArea = [0] * len(branchLbls)
        minRatios = [None] * len(branchLbls)

        # start with branch list length 1
        for branchlevel in range(1, maxLstLength + 1):
            # find branch level of the same length
            branchPosition = Matrix_Math.ListIndex(lst=branchLblLstLengths, matchElement=branchlevel)

            # get branches at the same level to new lists
            nameRefsUse = Matrix_Math.GetElementList(lst=nameRefs, indices=branchPosition)
            branchLblLstsUse = Matrix_Math.GetElementList(lst=branchLblLsts, indices=branchPosition)
            filePathsUse = Matrix_Math.GetElementList(lst=filePaths, indices=branchPosition)
            sliceStartsUse = Matrix_Math.GetElementList(lst=sliceStarts, indices=branchPosition)
            sliceStopsUse = Matrix_Math.GetElementList(lst=sliceStops, indices=branchPosition)
            maskLabelsUse = Matrix_Math.GetElementList(lst=maskLabels, indices=branchPosition)
            areaChoicesUse = Matrix_Math.GetElementList(lst=areaChoices, indices=branchPosition)

            # update
            msg = 'Level: {} \n'.format(branchlevel) + \
                  'nameRefsUse: {} \n'.format(nameRefsUse) + \
                  'branchLblLstsUse: {} \n'.format(branchLblLstsUse) + \
                  'filePathsUse: {} \n'.format(filePathsUse) + \
                  'sliceStartsUse: {} \n'.format(sliceStartsUse) + \
                  'maskLabelsUse: {} \n'.format(maskLabelsUse) + \
                  'areaChoicesUse: {} \n'.format(areaChoicesUse) + \
                  'sliceStopsUse: {}'.format(sliceStopsUse)

            self.UpdateMsgLog(msg)

            # flow distribbution
            # when it is the first level
            if branchlevel == 1:
                # direct flow distribution
                # flow distribution
                # Type 3 conservative flow distribution
                # all area calculation
                arrLst = Image_Process_Functions.RemoveEmptySlices(
                    files=filePathsUse,
                    lbls=maskLabelsUse,
                    sliceStarts=sliceStartsUse,
                    sliceStops=sliceStopsUse
                )
                # flow conservation
                areaLst, flowDivide, minRatio = Matrix_Math.ScanConservationLst(
                    arrLst=arrLst,
                    exponent=expo / 2,
                    targetSum=256,  # a fake number doesnt matter
                    targetRatio=threshold,
                    totalValue=inflow,
                    stepSize=10000,  # large step avoid initial distribution error
                    areaChoices=areaChoicesUse
                )

                # store information
                for child in range(len(branchPosition)):
                    # orginal position
                    oriPosition = branchPosition[child]

                    # store information
                    useArea[oriPosition] = areaLst[child]
                    # assume Type 2 area not conservative
                    areaConservative[oriPosition] = False
                    distributeFlow[oriPosition] = flowDivide[child]
                    findFlow[oriPosition] = True

            # all other levels
            else:
                for case in range(len(branchPosition)):
                    # actual list position
                    actualPosition = branchPosition[case]

                    # check the flow distribution
                    if findFlow[actualPosition]:
                        continue

                    else:
                        # find all branches from the same parent branch
                        childBranch = branchLblLsts[actualPosition]

                        # parent branch reference
                        parentBranch = childBranch[0:branchlevel - 1]

                        # find parent branch
                        parentBranchIndex = branchLblLsts.index(parentBranch)
                        # parent flow
                        parentFlow = distributeFlow[parentBranchIndex]
                        # parent branch is not end branch
                        endBranches[parentBranchIndex] = False
                        # parent area
                        parentArea = useArea[parentBranchIndex]

                        # update
                        msg = 'Children branch: {} \n'.format(nameRefs[actualPosition]) + \
                              'Label: {} \n'.format(childBranch) + \
                              'Parent branch: {} \n'.format(nameRefs[parentBranchIndex]) + \
                              'Label: {} \n'.format(parentBranch) + \
                              'Flow: {}'.format(parentFlow)

                        self.UpdateMsgLog(msg)

                        # find other branches
                        childrenBranches = [childBranch]
                        childrenBranchPosition = [actualPosition]
                        childrenFilePathsUse = [filePathsUse[case]]
                        childrenSliceStartsUse = [sliceStartsUse[case]]
                        childrenmaskLabelsUse = [maskLabelsUse[case]]
                        childrenSliceStopsUse = [sliceStopsUse[case]]
                        childrenAreaChoicesUse = [areaChoicesUse[case]]
                        for caseChild in range(case + 1, len(branchPosition)):
                            # find match children
                            if branchLblLstsUse[caseChild][0:branchlevel - 1] == parentBranch:
                                # append
                                childrenBranches.append(branchLblLstsUse[caseChild])
                                childrenBranchPosition.append(branchPosition[caseChild])
                                childrenFilePathsUse.append(filePathsUse[caseChild])
                                childrenSliceStartsUse.append(sliceStartsUse[caseChild])
                                childrenSliceStopsUse.append(sliceStopsUse[caseChild])
                                childrenmaskLabelsUse.append(maskLabelsUse[caseChild])
                                childrenAreaChoicesUse.append(areaChoicesUse[caseChild])

                        # update
                        msg = 'All children branch: {} \n'.format(childrenBranches) + \
                              'childrenBranchPosition: {} \n'.format(childrenBranchPosition) + \
                              'childrenFilePathsUse: {} \n'.format(childrenFilePathsUse) + \
                              'childrenSliceStartsUse: {} \n'.format(childrenSliceStartsUse) + \
                              'childrenSliceStopsUse: {} \n'.format(childrenSliceStopsUse) + \
                              'childrenAreaChoicesUse: {} \n'.format(childrenAreaChoicesUse) + \
                              'childrenmaskLabelsUse: {}'.format(childrenmaskLabelsUse)

                        self.UpdateMsgLog(msg)

                        # flow distribution
                        if len(childrenBranches) == 1:
                            # flow not conservative
                            distributeFlow[childrenBranchPosition[0]] = parentFlow
                            findFlow[childrenBranchPosition[0]] = True
                            ## store information
                            useArea[childrenBranchPosition[0]] = 0
                            # parent branch
                            parentBranches[childrenBranchPosition[0]] = nameRefs[parentBranchIndex]
                            # minimum ratio
                            minRatios[childrenBranchPosition[0]] = 0

                        else:
                            # flow distribution
                            # Type 3 conservative flow distribution
                            # all area calculation
                            arrLst = Image_Process_Functions.RemoveEmptySlices(
                                files=childrenFilePathsUse,
                                lbls=childrenmaskLabelsUse,
                                sliceStarts=childrenSliceStartsUse,
                                sliceStops=childrenSliceStopsUse
                            )
                            # flow conservation
                            areaLst, flowDivide, minRatio = Matrix_Math.ScanConservationLst(
                                arrLst=arrLst,
                                exponent=expo / 2,
                                targetSum=parentArea,
                                targetRatio=threshold,
                                totalValue=parentFlow,
                                stepSize=step,
                                areaChoices=childrenAreaChoicesUse
                            )

                            # store information
                            for child in range(len(childrenBranchPosition)):
                                # original position
                                oriPosition = childrenBranchPosition[child]

                                # store information
                                useArea[oriPosition] = areaLst[child]
                                # if satisfy
                                if minRatio <= threshold:
                                    areaConservative[oriPosition] = True
                                else: # type 2 distribution already
                                    areaConservative[oriPosition] = False
                                distributeFlow[oriPosition] = flowDivide[child]
                                findFlow[oriPosition] = True

                                # parent branch
                                parentBranches[oriPosition] = nameRefs[parentBranchIndex]

                                # minimum ratio
                                minRatios[oriPosition] = minRatio

        # output information table
        outDict = {
            "Name Reference": nameRefs,
            "Branch Label": branchLblLsts,
            "Find Flow": findFlow,
            "End Branches": endBranches,
            "Area Conservation": areaConservative,
            "Parent Branches": parentBranches,
            "Distributed Flow": distributeFlow,
            "Minimum Ratio": minRatios,
            "Use Area": useArea
        }
        # dataframe
        outDF = pandas.DataFrame(outDict)

        # output
        # save
        outFile = outFolder + "/" + "AutoFlowDistribute" + ".csv"
        Pd_Funs.SaveDF(
            outPath=outFile,
            pdIn=outDF,
            header=True,
            index=False
        )

        # update message
        self.UpdateMsgLog(
            msg="Output file:\n{}".format(
                outFile
            )
        )

        # output txt update
        # list of multiples
        if isinstance(multipleStrs, int) or isinstance(multipleStrs, numpy.int64):
            multipleLst = [multipleStrs]
        elif isinstance(multipleStrs, str):
            multipleLst = Matrix_Math.ConvertListType(lst=multipleStrs.split(','), type=float)
        else:
            raise ValueError("Type error: {} with type: {}".format(multipleStrs, type(multipleStrs)))

        # find all reference table
        tablePaths = [None] * len(branchLbls)
        # update
        self.UpdateMsgLog("Find parent branch")

        for parent in range(len(branchLbls)):
            # each branch parent
            parentRef = parentBranches[parent]

            # if already have files
            if refFiles[parent] != "N":
                tablePaths[parent] = refFiles[parent]
            else:
                # find ultimate branch
                findUltimateParent = False
                print('parentRef')
                print(parentRef)
                print("Branch: {} ".format(nameRefs[parent]))
                print(parentBranches)

                while not findUltimateParent:
                    # find parent position
                    parentBranchPosition = nameRefs.index(parentRef)

                    # find with file
                    if refFiles[parentBranchPosition] != "N":
                        tablePaths[parent] = refFiles[parentBranchPosition]
                        findUltimateParent = True
                        # update
                        msg = "Find output waveforms for: " + \
                              "Branch: {} ".format(nameRefs[parent]) + \
                              "Parent Branch: {} ".format(parentBranches[parent]) + \
                              "Ultimate Parent Branch: {} ".format(nameRefs[parentBranchPosition]) + \
                              "Table Path: {} ".format(refFiles[parentBranchPosition])
                        self.UpdateMsgLog(msg)
                    else:
                        # update parent
                        parentRef = parentBranches[parentBranchPosition]

        # check
        if any(tablePaths) is None:
            raise ValueError("Table are not all found {}".format(tablePaths))
        else:
            # update
            msg = "Find output waveforms: \n" + \
                "Branch: {}".format(nameRefs) + \
                "\nParent Branch: {}".format(parentBranches) + \
                "\nTablePaths: {}".format(tablePaths)
            self.UpdateMsgLog(msg)

        # output table
        for multiple in multipleLst:
            # create folder
            outFolderTable = outFolder + "/Flow_" + str(multiple).replace(".", "_")
            Save_Load_File.checkCreateDir(outFolderTable)

            for case in range(len(branchLbls)):
                # check is end branch
                if not endBranches[case]:
                    continue
                else:
                    # get flow
                    flow = distributeFlow[case]
                    # outpath
                    outFolderTablePath = outFolderTable + "/" + nameRefs[case] + ".txt"

                    # csv output
                    rtrnInfo = Pd_Funs.MultiplyCSVColumns(
                        inPath=tablePaths[case],
                        multiples=[numpy.multiply(multiple, flow)],
                        columns=[1],
                        outPath=outFolderTablePath
                    )

                    # update message
                    self.UpdateMsgLog(
                        msg=rtrnInfo["message"]
                    )

    def BatchAutoType3(self, tablePath=None):
        # load files
        if tablePath is None:
            batchTablePath = self.ui.batchType3PathTxt_AVC.toPlainText()
        else:
            batchTablePath = tablePath

        # load DFs
        dfBatchTable = Pd_Funs.OpenDF(
            inPath=batchTablePath,
            header=0,
            usecols=None
        )

        for parametersPath, branchMapPath in zip(
                dfBatchTable["Parameters Path"].tolist(),
                dfBatchTable["Branch Map Path"].tolist(),
        ):
            # update
            msg = 'parametersPath: {} \n'.format(parametersPath) + \
                  'branchMapPath: {}'.format(branchMapPath)
            self.UpdateMsgLog(msg)
            self.AutoType3(parametersPath=parametersPath, branchMapPath=branchMapPath)

    def UpdateMsgLog(self, msg=""):
        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + '{}'.format(msg) \
               + "\n############################\n"

        if self.modelui:
            # update log and display message
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
        print(disp)
