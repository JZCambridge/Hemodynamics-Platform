"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by jz410 (28Feb21)
"""

# Import self-written functions
import sys
import os

# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, 'E:\\OneDrive - University of Cambridge\\Uni\\PhD1\\Python\\Spyder\\Functions_07Dec20')

import Save_Load_File
import Image_Process_Functions
import Post_Image_Process_Functions
import Use_Plt

# import standard libs
import tkinter
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk
import time
import datetime

"""
##############################################################################
#Class: create top level
##############################################################################
"""


class TopLevelCreate:
    """
    Create top level
    """

    def __init__(self,
                 titleTL="",
                 geoTL='1000x800'):
        # Create a top level as a separate window
        self.topLvl = tkinter.Toplevel()
        self.topLvl.title(titleTL)
        self.topLvl.geometry(geoTL)

        # create frames with scrollable canvas for lbls
        ## create a top frame for scrollable area
        self.frame_Others = tkinter.Frame(self.topLvl,
                                          width=800, height=500)
        self.frame_Others.pack(side=tkinter.TOP,
                               fill=tkinter.BOTH)

        ## create canvas, build scrollbar inside the frame
        self.topCanvas = tkinter.Canvas(self.frame_Others,
                                        width=800, height=500)

        ## scrollbars need assign to the based frame
        ### vertical
        vbar = tkinter.Scrollbar(master=self.frame_Others,
                                 orient=tkinter.VERTICAL)
        vbar.pack(side="right",
                  fill=tkinter.Y)
        vbar.config(command=self.topCanvas.yview)
        ### horizontal
        hbar = tkinter.Scrollbar(master=self.frame_Others,
                                 orient=tkinter.HORIZONTAL)
        hbar.pack(side="bottom",
                  fill=tkinter.X)
        hbar.config(command=self.topCanvas.xview)

        ## create scrolled frame
        self.scrollable_frame = ttk.Frame(self.topCanvas)
        ### Func to update frame region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.topCanvas.configure(
                scrollregion=self.topCanvas.bbox("all")
            )
        )
        ### Canvas draw scrollale_frame
        self.topCanvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        ## add to canvas
        self.topCanvas.config(xscrollcommand=hbar.set,
                              yscrollcommand=vbar.set)  # ,
        # scrollregion=(0, 0, 1000, 1000))
        self.topCanvas.pack(side=tkinter.TOP,
                            fill=tkinter.BOTH)

        # create scroll text for update
        ## create frame for scroll txt
        self.frame_scTxt = tkinter.Frame(self.topLvl,
                                         width=800,
                                         height=200)
        self.frame_scTxt.pack(side=tkinter.TOP,
                              fill=tkinter.BOTH,
                              pady=5,
                              padx=5)
        ## Save log
        tkinter.Button(master=self.frame_scTxt,
                       text='Save Log',
                       width=20,
                       height=1,
                       command=self.SaveLog,
                       bg='yellow',
                       fg='black'
                       ).pack(side=tkinter.TOP)
        ## create scroll text
        self.scTxt = scrolledtext.ScrolledText(master=self.frame_scTxt,
                                               width=200,
                                               height=160)
        self.scTxt.pack(side=tkinter.TOP,
                        fill=tkinter.BOTH)
        ## disable input
        self.scTxt.configure(state='disabled')

    def __del__(self):
        print("Top level is closed and class is destroyed")

    def UpdateSCTxt(self,
                    msg):
        """
        Update scroll text with msg
        """
        # Msg construction:
        msgStart = "============================================== \n"
        msgEnd = "\n##############################################\n"
        ## date
        currentDate = datetime.date.today()
        msgDate = currentDate.strftime("%d/%m/%Y")
        ## time
        now = datetime.datetime.now()
        msgTime = now.strftime("%H:%M:%S")
        msgShow = msgStart + msgDate + " - " + msgTime + \
                  ": \n" + msg + msgEnd

        # Show msg
        self.scTxt.configure(state='normal')
        self.scTxt.insert(tkinter.END, msgShow)
        self.scTxt.configure(state='disabled')

    def SaveLog(self):
        """
        Choose directory and save log
        :return:
        """
        # Choose directory
        dirPath = Save_Load_File.DirectoryPath(dispMsg="Choose directory to save LOG file",
                                               fileObj=self.topLvl,
                                               tkObj=True)
        # date
        now = datetime.datetime.now()
        dt_string = now.strftime("%d%m%Y_%H%M%S")
        #Txt file
        txtPath = dirPath + "/MapRslts" + dt_string + ".log"

        # Update txt
        self.UpdateSCTxt(msg="Save log:\n" + txtPath)

        # Save text
        Save_Load_File.WriteTXT(path=txtPath,
                                txt=self.scTxt.get("1.0", tkinter.END))




"""
##############################################################################
#Func: open file and fill entry/text
##############################################################################
"""


def OpenFillEntryTxt(inEntry,
                     inFileObj):
    """
    Choose file path and input to provided tk.Entry or tk.txt
    """
    # choose file
    filePath = Save_Load_File.OpenFilePath(dispMsg="Choose file to load",
                                           fileTypes=[("All files", "*.*"), ("Txt files", "*.coo *.txt")],
                                           fileObj=inFileObj,
                                           tkObj=True)

    # fill entry delete and insert
    inEntry.delete(0, 'end')
    inEntry.insert('end', filePath)


"""
##############################################################################
#Func: Save file and fill entry/text
##############################################################################
"""


def SaveFillEntryTxt(inEntry,
                     inFileObj):
    """
    Choose/create save file path and input to provided tk.Entry or tk.txt
    """
    # Choose/create save file
    filePath = Save_Load_File.SaveFilePath(dispMsg="Choose/create file to save",
                                           fileObj=inFileObj,
                                           tkObj=True)

    # fill entry delete and insert
    inEntry.delete(0, 'end')
    inEntry.insert('end', filePath)
