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
import Pd_Funs
##############################################################################

##############################################################################
# Standard library
import csv
import json
import skimage.measure
import numpy
import scipy.stats
import skimage.segmentation
import skimage.morphology
from multiprocessing import Pool
from datetime import datetime
import time
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *

##############################################################################

class CenterlineJSONUpdate:
    def __init__(self, UI=None, Hedys=None):
        self.ui = None
        if UI:
            self.ui = UI

            self.ui.ChooseOpenJSNFileBtn_CJU.clicked.connect(lambda: self.ChooseOpenJSNFileCJU())
            self.ui.ChooseCSVDirBtn_CJU.clicked.connect(lambda: self.ChooseCSVDirCJU())
            self.ui.ChooseBatchTableFileBtn_CJU.clicked.connect(lambda: self.ChooseBatchTableFile())
            self.ui.updateBtn_CJU.clicked.connect(lambda: self.UpdateCenterlineJson())
            self.ui.batchUpdateBtn_CJU.clicked.connect(lambda: self.BatchUpdateJson())
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

    """
    ##############################################################################
    # Init dictionary template
    ##############################################################################
    """

    def DictionTemplate(self):
        self.R_Dict = [
            {"branch_name": "R-aorta", "label": [22], "coordinates": [], "parenthood": 0},
            {"branch_name": "pRCA", "label": [1], "coordinates": [], "parenthood": 0},
            {"branch_name": "mRCA", "label": [2], "coordinates": [], "parenthood": 1},
            {"branch_name": "dRCA", "label": [3], "coordinates": [], "parenthood": 2},
            {"branch_name": "R-PDA", "label": [4], "coordinates": [], "parenthood": 3},
            {"branch_name": "V", "label": [16], "coordinates": [], "parenthood": 1},
            {"branch_name": "AM", "label": [17], "coordinates": [], "parenthood": 2},
            {"branch_name": "R-PLB", "label": [18], "coordinates": [], "parenthood": 3},
            {"branch_name": "CB", "label": [19], "coordinates": [], "parenthood": 1},
            {"branch_name": "unknown", "label": [20], "coordinates": [], "parenthood": 0},
            {"branch_name": "RCA", "label": [1, 2, 3], "coordinates": [], "parenthood": 0}
        ]

        self.L_Dict = [
            {"branch_name": "L-aorta", "label": [21], "coordinates": [], "parenthood": 0},
            {"branch_name": "LM", "label": [5], "coordinates": [], "parenthood": 0},
            {"branch_name": "IMB", "label": [50], "coordinates": [], "parenthood": 5},
            {"branch_name": "pLAD", "label": [6], "coordinates": [], "parenthood": 5},
            {"branch_name": "mLAD", "label": [7], "coordinates": [], "parenthood": 6},
            {"branch_name": "dLAD", "label": [8], "coordinates": [], "parenthood": 7},
            {"branch_name": "D1", "label": [9], "coordinates": [], "parenthood": 6},
            {"branch_name": "D2", "label": [10], "coordinates": [], "parenthood": 7},
            {"branch_name": "pCx", "label": [11], "coordinates": [], "parenthood": 5},
            {"branch_name": "OM1", "label": [12], "coordinates": [], "parenthood": 11},
            {"branch_name": "LCx", "label": [13], "coordinates": [], "parenthood": 11},
            {"branch_name": "OM2", "label": [14], "coordinates": [], "parenthood": 13},
            {"branch_name": "L-PDA", "label": [15], "coordinates": [], "parenthood": 13},
            {"branch_name": "unknown", "label": [20], "coordinates": [], "parenthood": 0},
            {"branch_name": "LAD", "label": [6, 7, 8], "coordinates": [], "parenthood": 5},
            {"branch_name": "LCX", "label": [11, 13, 15], "coordinates": [], "parenthood": 5}
        ]

        # branch name lists
        self.RBarnchNameLst = [dict["branch_name"] for dict in self.R_Dict]
        self.LBarnchNameLst = [dict["branch_name"] for dict in self.L_Dict]

    """
    ##############################################################################
    # Update Centerline Dictionary
    ##############################################################################
    """

    def ChooseOpenJSNFileCJU(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Load image segmentation",
            fileTypes="All files (*.*);; JSON files (*.json)",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.jsonFilePathTxt_CJU.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose json file:\n{}".format(filename))

    def ChooseCSVDirCJU(self):
        # Save data
        dirname = Save_Load_File.OpenDirPathQt(
            dispMsg="Choose CSV directory",
            fileObj=self.ui,
            qtObj=True
        )

        # set filename
        self.ui.CSVDirPathTxt_CJU.setPlainText(dirname)

        # update message
        self.UpdateMsgLog(msg="Choose CSV directory:\n{}".format(dirname))

    def UpdateCenterlineJson(self, jsonFile=None, CSVDir=None, updateType=None):

        # update input
        if jsonFile is None: jsonFile = self.ui.jsonFilePathTxt_CJU.toPlainText()
        if CSVDir is None: CSVDir = self.ui.CSVDirPathTxt_CJU.toPlainText()
        if updateType is None: updateType = self.ui.updateTypeCBox_CJU.currentText()

        # init
        self.DictionTemplate()

        # load old JSON
        with open(jsonFile, 'r') as f:
            oldDictLst = json.load(f)
        f.close()

        # check L or R
        if "L_coronary_centerline_network.json" in jsonFile:  # left update
            outDictLst = self.L_Dict
            barnchNameLst = self.LBarnchNameLst
        elif "R_coronary_centerline_network.json" in jsonFile:
            outDictLst = self.R_Dict
            barnchNameLst = self.RBarnchNameLst
        else:
            self.UpdateMsgLog(msg="!!!Warning input JSON does not have 'L_coronary_centerline_network' or "
                                  "'R_coronary_centerline_network':\n{}".format(jsonFile))
            return

        # check directory
        if not os.path.isdir(CSVDir):
            if os.path.isfile(CSVDir):
                CSVDir, _ = Save_Load_File.ParentDir(CSVDir)
                self.UpdateMsgLog(msg="!!!Warning input CSVDir is file use parent path: :\n{}".format(CSVDir))
            else:
                self.UpdateMsgLog(msg="!!!Error wrong path:\n{}".format(CSVDir))
                return

        # update
        if updateType == "Add CSV":
            # get all CSV file name
            csvFiles = Save_Load_File.FindFilesExtension(dirPath=CSVDir, ext=".csv", traverse=True)

            # update out Dict first
            for oldDict in oldDictLst:
                # empty coordinate
                if not oldDict["coordinates"]:
                    pass
                else:  # not empty
                    # find corresponding position in new dict
                    index = barnchNameLst.index(oldDict["branch_name"])
                    # add coordinate
                    outDictLst[index]['coordinates'] = oldDict["coordinates"]

            # add csv
            for outDict in outDictLst:
                # check empty coordiante
                if (not outDict["coordinates"]) and (outDict["branch_name"] in csvFiles["FileNames"]):
                    # find corresponding position in new dict
                    index = csvFiles["FileNames"].index(outDict["branch_name"])

                    # more than one position!!!
                    if type(index) == list:
                        self.UpdateMsgLog(msg="!!!Warning more than one CSV in name:"
                                              "\n{} \n{}".format(outDict["branch_name"],
                                                                 csvFiles["FileFullPaths"][index]))
                        index = index[0]

                    # load DF and covert to list
                    # Open file
                    with open(csvFiles["FileFullPaths"][index]) as file_obj:
                        # Create reader object by passing the file
                        # object to reader method
                        reader_obj = csv.reader(file_obj)

                        # Iterate over each row in the csv file
                        # using reader object
                        for row in reader_obj:
                            outDict["coordinates"].append(
                                {
                                    "X": int(row[0]),
                                    "Y": int(row[1]),
                                    "Z": int(row[2])
                                }
                            )

        elif updateType == "Replace with CSV":
            # get all CSV file name
            csvFiles = Save_Load_File.FindFilesExtension(dirPath=CSVDir, ext=".csv", traverse=True)

            # update out Dict first
            for oldDict in oldDictLst:
                # empty coordinate
                if not oldDict["coordinates"]:
                    pass
                else:  # not empty
                    # find corresponding position in new dict
                    index = barnchNameLst.index(oldDict["branch_name"])
                    # add coordinate
                    outDictLst[index]['coordinates'] = oldDict["coordinates"]

            # add csv
            for outDict in outDictLst:
                # check empty coordiante
                if (outDict["branch_name"] in csvFiles["FileNames"]):
                    # find corresponding position in new dict
                    index = csvFiles["FileNames"].index(outDict["branch_name"])

                    # more than one position!!!
                    if type(index) == list:
                        self.UpdateMsgLog(msg="!!!Warning more than one CSV in name:"
                                              "\n{} \n{}".format(outDict["branch_name"],
                                                                 csvFiles["FileFullPaths"][index]))
                        index = index[0]

                    # empty coordinates
                    outDict["coordinates"] = []

                    # load DF and covert to list
                    # Open file
                    with open(csvFiles["FileFullPaths"][index]) as file_obj:
                        # Create reader object by passing the file
                        # object to reader method
                        reader_obj = csv.reader(file_obj)

                        # Iterate over each row in the csv file
                        # using reader object
                        for row in reader_obj:
                            if row:
                                outDict["coordinates"].append(
                                    {
                                        "X": int(row[0]),
                                        "Y": int(row[1]),
                                        "Z": int(row[2])
                                    }
                                )

        elif updateType == "Only CSV":
            # get all CSV file name
            csvFiles = Save_Load_File.FindFilesExtension(dirPath=CSVDir, ext=".csv", traverse=True)

            # add csv
            for outDict in outDictLst:
                # check empty coordiante
                if (outDict["branch_name"] in csvFiles["FileNames"]):
                    # find corresponding position in new dict
                    index = csvFiles["FileNames"].index(outDict["branch_name"])

                    # more than one position!!!
                    if type(index) == list:
                        self.UpdateMsgLog(msg="!!!Warning more than one CSV in name:"
                                              "\n{} \n{}".format(outDict["branch_name"],
                                                                 csvFiles["FileFullPaths"][index]))
                        index = index[0]

                    # empty coordinates
                    outDict["coordinates"] = []

                    # load DF and covert to list
                    # Open file
                    with open(csvFiles["FileFullPaths"][index]) as file_obj:
                        # Create reader object by passing the file
                        # object to reader method
                        reader_obj = csv.reader(file_obj)

                        # Iterate over each row in the csv file
                        # using reader object
                        for row in reader_obj:
                            if row:
                                outDict["coordinates"].append(
                                    {
                                        "X": int(row[0]),
                                        "Y": int(row[1]),
                                        "Z": int(row[2])
                                    }
                                )

        else:
            self.UpdateMsgLog(msg="!!!ERROR update type:\n{}".format(updateType))
            return

        # save
        with open(jsonFile, 'w') as fp:
            json.dump(outDictLst, fp)
        fp.close()

        self.UpdateMsgLog(msg="Update:\n{}".format(jsonFile))

    """
    ##############################################################################
    # Batch Update
    ##############################################################################
    """

    def ChooseBatchTableFile(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="Batch table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt *.csv *.xlsx *.xls *.xlsm *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.batchPathTxt_CJU.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose batch update table file path:\n{}".format(
                self.ui.batchPathTxt_CJU.toPlainText()
            )
        )

    def BatchUpdateJson(self, tablePath=None):
        # input
        if tablePath is None: tablePath = self.ui.batchPathTxt_CJU.toPlainText()

        # batch files
        batchDF = Pd_Funs.OpenDF(
            inPath=tablePath,
            header=0
        )

        for CSVDir, \
            jsonFile, \
            updateType \
                in zip(
            batchDF["CSVDirectory"].tolist(),
            batchDF["JsonFile"].tolist(),
            batchDF["UpdateType"].tolist()
        ):
            # update
            self.UpdateCenterlineJson(jsonFile=jsonFile, CSVDir=CSVDir, updateType=updateType)

        # update
        self.UpdateMsgLog("Complete batch update!")

    """
    ##############################################################################
    # Message
    ##############################################################################
    """

    def UpdateMsgLog(self, msg=""):
        # Date and time
        nowStr = datetime.now().strftime("%d/%b/%y - %H:%M:%S")
        disp = "##############" \
               + nowStr \
               + "############## \n" \
               + msg \
               + "\n############################\n"

        if self.modelui:
            # update log and display message
            self.modelui.plainTextEdit_Message.setPlainText(disp)
            self.modelui.plainTextEdit_Log.appendPlainText(disp)
        print(disp)

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\UpdateCenterlineJson.ui")
    stats = CenterlineJSONUpdate(UI=ui)
    stats.ui.show()
    app.exec_()