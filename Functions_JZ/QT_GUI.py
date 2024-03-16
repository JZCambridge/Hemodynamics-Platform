"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by jz410 (28Feb21)
"""

# Import self-written functions
import Save_Load_File
import Image_Process_Functions
import Post_Image_Process_Functions
import Use_Plt

# import standard libs
import time
import datetime
import sys
import os

"""
##############################################################################
#Func: Choose and display file path
##############################################################################
"""


def ChooseFile(dispMsg="Choose file to load",
               fileTypes="All files (*.*)",
               displayText=None,
               updateMsgFunc=None):
    # choose
    filename = Save_Load_File.OpenFilePathQt(
        dispMsg=dispMsg,
        fileTypes=fileTypes,
        fileObj=None,
        qtObj=False
    )

    # set filename
    if displayText is not None:
        displayText.setPlainText('{}'.format(filename))

    # update message
    if updateMsgFunc is not None:
        updateMsgFunc(
            msg="Choose file:\n{}".format(
                filename
            )
        )


"""
##############################################################################
#Func: Load image data and set data
##############################################################################
"""


def LoadData(displayText,
             setDataFunc,
             updateMsgFunc=None):
    # load two data
    data = Save_Load_File.OpenLoadNIFTI(
        GUI=False,
        filePath=displayText.toPlainText()
    )

    # set data
    setDataFunc(data)

    # update message
    if updateMsgFunc is not None:
        updateMsgFunc(
            msg="Choose file:\n{}".format(displayText.toPlainText())
        )


"""
##############################################################################
# Class: create QT DockWidget
##############################################################################
"""
# from PySide2.QtWidgets import QDockWidget, QVBoxLayout, QFrame
# from PySide2 import QtCore, QtGui
import PySide2.QtCore
import PySide2.QtWidgets


class CreateDockWidget(PySide2.QtWidgets.QDockWidget):

    def __init__(self,
                 parent,
                 name="Default",
                 position='Right'):

        # create DockWidget
        super().__init__(parent)

        # dock position
        qtDockPosition = PySide2.QtCore.Qt.RightDockWidgetArea
        if position == 'Right':
            qtDockPosition = PySide2.QtCore.Qt.RightDockWidgetArea
        if position == 'Left':
            qtDockPosition = PySide2.QtCore.Qt.LeftDockWidgetArea
        if position == 'Top':
            qtDockPosition = PySide2.QtCore.Qt.TopDockWidgetArea
        if position == 'Bottom':
            qtDockPosition = PySide2.QtCore.Qt.BottomDockWidgetArea

        # add dock widget
        parent.addDockWidget(qtDockPosition, self)

        # set title
        self.setWindowTitle(name)

        # get all dock children in the main window
        child = parent.findChildren(PySide2.QtWidgets.QDockWidget)

        # # print all dock widget titles
        # msg = "Title ["
        # for i in range(len(child)):
        #     msg += '{}, '.format(child[i].windowTitle())
        # msg += "]"
        # print(msg)

        # Stack Dock widgets with same position
        childTab = []
        if len(child) > 1:
            # remove the dockwidget not at the same side
            for i in range(len(child)):
                # dock position
                area = parent.dockWidgetArea(child[i])
                if area == qtDockPosition:
                    childTab.append(child[i])
                else:
                    continue

        if len(childTab) > 1:
            # only tab for the same position
            parent.tabifyDockWidget(childTab[0], self)

            # # Print all dock widget titles
            # print("childTab[0]: {} & childTab[-1]: {}".format(childTab[0].windowTitle(), childTab[-1].windowTitle()))
            # print("Current Dock title: {}".format(self.windowTitle()))

            # set the new dock widget to appear first
            self.show()
            self.raise_()

        # create frame and layout
        self.frame = PySide2.QtWidgets.QFrame()
        self.vl = PySide2.QtWidgets.QVBoxLayout()

        # add frame in qDock widget
        self.setWidget(self.frame)

    def GetFrame(self):
        return self.frame

    def GetLayout(self):
        return self.vl
