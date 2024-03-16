# -*- coding: UTF-8 -*-
'''
@Project ：Hemod_Platform 
@File    ：FileDisposing.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/4/18 15:37 
'''
import numpy as np
import os.path
import re

# Standard libs
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox,QWidget, QTableWidget, QHBoxLayout, QApplication, QTableWidgetItem, QAbstractItemView,QTabWidget,QDialog,QComboBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile

"""
##############################################################################
#Split FilePath and return head FileName,FileFormat
##############################################################################
"""
def Split_AbsFilePath(AbsFilpth:str):
    '''Dscription: Split FilePath and return FileHead FileName,FileFormat

        Args:
            AbsFilpth: The file's absolute path 
  
        Returns:
            head(end with "/"), FilNam, FilFormat(start with ".")
    '''
    if AbsFilpth:
        head, tail = os.path.split(AbsFilpth)
        FilNam, FilFormat = os.path.splitext(tail)
        if head.endswith("/") :
            head = head
        else:
            head +=  "/"
        return head, FilNam, FilFormat
    else:
        print("IOError:No such file or directory")


"""
##############################################################################
#Open File and return File Absolute Path
##############################################################################
"""
def Opening_File(MainWindow, Fil_Formt:str):
    FilDialog = QFileDialog(MainWindow)
    FilDirectory = FilDialog.getOpenFileName(MainWindow, "Open File", "", Fil_Formt)  #"Por (*.por)"
    FilAbsPth = FilDirectory[0]
    if FilAbsPth:
        return  FilAbsPth
    else:
        print("IOError:No such file or directory")

"""
##############################################################################
#Opening_Files
##############################################################################
"""
#################################################Opening_Files###########################################################
def Opening_Files(MainWindow, Fil_Formt, EndingSymbolAdded ):
    filePaths, _ = QFileDialog.getOpenFileNames(MainWindow, "Open Files", "", Fil_Formt)  #"Por (*.por)"
    #FilAbsPth = FilDirectorys[0]
    # if FilAbsPth:
    #     return  FilAbsPth
    # else:
    #     print("IOError:No such file or directory")

    if EndingSymbolAdded:
        tmpfilePaths = []
        for eachFil in filePaths:
            eachFil += ","
            tmpfilePaths.append(eachFil)
        filePaths = tmpfilePaths

    return filePaths

"""
##############################################################################
#Open FileDialog and return File Directory
##############################################################################
"""
###############################################Opening_FileDialog#######################################################
def Opening_FileDialog(MainWindow):
    FilDialog = QFileDialog(MainWindow)
    FilDirectory = FilDialog.getExistingDirectory(MainWindow, "Open FileDirectory") + "/"
    return  FilDirectory