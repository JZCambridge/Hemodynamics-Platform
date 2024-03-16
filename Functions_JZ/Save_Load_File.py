# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 19:44:24 2020

@author: yingmohuanzhou
"""

"""
##############################################################################
#Open dialog return directory path
##############################################################################
"""
import tkinter
from tkinter import filedialog, messagebox


def DirectoryPath(dispMsg="",
                  fileObj=None,
                  tkObj=False):
    # Open dialog return directory path
    if not tkObj:
        fileObj = tkinter.Tk()

    while True:
        messagebox.showinfo(title="Select directory path", message=dispMsg)
        fileObj.directory = filedialog.askdirectory(title=dispMsg)
        if messagebox.askyesno(title=dispMsg, message="Check Path: \n" + fileObj.directory):
            if not tkObj:
                fileObj.destroy()
            break

    # No input tk obj need main loop
    if not tkObj:
        fileObj.mainloop()

    return fileObj.directory


"""
##############################################################################
#Tkinter Open dialog return file path
##############################################################################
"""
import tkinter
from tkinter import filedialog, messagebox


def OpenFilePath(dispMsg="",
                 fileTypes=(("all files", "*.*"), ("NIFTI files", "*.nii.gz"), ("STL files", "*.stl")),
                 fileObj=None,
                 tkObj=False):
    # Open dialog return file path
    # create tk object
    if not tkObj:
        fileObj = tkinter.Tk()

    # Lopping for input
    while True:
        messagebox.showinfo(title="Select file to load", message=dispMsg)
        fileObj.filename = filedialog.askopenfilename(title=dispMsg,
                                                      filetypes=fileTypes)
        if messagebox.askyesno(title="Path", message=dispMsg + "\nCheck File: \n" + fileObj.filename):
            if not tkObj:
                fileObj.destroy()
            break

    # No input tk obj need main loop
    if not tkObj:
        fileObj.mainloop()
    return fileObj.filename


"""
##############################################################################
#Func: Open dialog select save file
##############################################################################
"""
import tkinter
from tkinter import filedialog, messagebox


def SaveFilePath(dispMsg="",
                 fileObj=None,
                 fileTypes=(("all files", "*.*"), ("NIFTI files", "*.nii.gz"), ("NRRD files", "*.nrrd")),
                 tkObj=False):
    # Open dialog select save file
    if not tkObj:
        fileObj = tkinter.Tk()

    while True:
        messagebox.showinfo(title="Save file", message=dispMsg)
        fileObj.filename = filedialog.asksaveasfilename(title=dispMsg,
                                                        filetypes=fileTypes)
        if messagebox.askyesno(title="Path", message=dispMsg + "\nCheck File: \n" + fileObj.filename):
            if not tkObj:
                fileObj.destroy()
            break

    if not tkObj:
        fileObj.mainloop()
    return fileObj.filename


"""
##############################################################################
#Func: QT open dialog select save file
##############################################################################
"""
import PySide2


def SaveFilePathQT(dispMsg="",
                   fileObj=None,
                   fileTypes="All files (*.*);; "
                             "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                             "STL files (*.stl) ;; "
                             "Img files (*.png *.jpg) ;; "
                             "Graphic files (*.svg, *.eps, *.ps, *.pdf, *.tex) ",
                   qtObj=False):
    # Open dialog return file path
    filename = None
    # create tk object
    if not qtObj:
        # message box
        PySide2.QtWidgets.QMessageBox.information(
            None,
            "Save file",
            dispMsg,
            PySide2.QtWidgets.QMessageBox.Ok
        )
        # Lopping for input
        while True:
            # static method
            # PySide2.QtWidgets.QFileDialog.getSaveFileName([parent=None[,
            # caption=""[, dir=""[, filter=""[, selectedFilter=""[, options=QFileDialog.Options()]]]]]])¶
            filename, fileType = PySide2.QtWidgets.QFileDialog.getSaveFileName(
                None,
                dispMsg,
                "",  # current directory
                fileTypes
            )
            # ask results
            ret = PySide2.QtWidgets.QMessageBox.question(
                None,
                "Path",
                dispMsg + "\nCheck File: \n" + filename
            )

            if ret == PySide2.QtWidgets.QMessageBox.Yes:
                break

    if qtObj and fileObj is not None:
        # message box
        PySide2.QtWidgets.QMessageBox.information(
            None,
            "Save file",
            dispMsg,
            PySide2.QtWidgets.QMessageBox.Ok
        )
        # Lopping for input
        while True:
            # static method
            # PySide2.QtWidgets.QFileDialog.getSaveFileName([parent=None[,
            # caption=""[, dir=""[, filter=""[, selectedFilter=""[, options=QFileDialog.Options()]]]]]])¶
            filename, fileType = PySide2.QtWidgets.QFileDialog.getSaveFileName(
                None,
                dispMsg,
                "",  # current directory
                fileTypes
            )
            # ask results
            ret = PySide2.QtWidgets.QMessageBox.question(
                None,
                "Path",
                dispMsg + "\nCheck File: \n" + filename
            )

            if ret == PySide2.QtWidgets.QMessageBox.Yes:
                break

    return filename


"""
##############################################################################
#Func: QT Open dialog return file path
##############################################################################
"""
import PySide2
import os


def OpenFilePathQt(dispMsg="",
                   fileTypes="All files (*.*);; NIFTI/NRRD files(*.nii.gz *.nrrd) ;; STL files (*.stl)",
                   fileObj=None,
                   qtObj=False):
    # Open dialog return file path
    filename = None
    # create tk object
    if not qtObj:
        # message box
        PySide2.QtWidgets.QMessageBox.information(
            None,
            "Select file to load",
            dispMsg,
            PySide2.QtWidgets.QMessageBox.Ok
        )
        # Lopping for input
        while True:
            # static method
            # QString QFileDialog.getOpenFileName (QWidget parent = None, QString caption = QString(),
            # QString directory = QString(), QString filter = QString(), Options options = 0)
            filename, fileType = PySide2.QtWidgets.QFileDialog.getOpenFileNames(
                None,
                dispMsg,
                "",
                fileTypes
            )

            # string out
            if len(filename) == 0:
                filename = ""
            elif len(filename) == 1:
                filename = filename[0]
            else:
                out = ""
                for file in filename:
                    out += file + ",\n"
                filename = out

            # ask results
            ret = PySide2.QtWidgets.QMessageBox.question(
                None,
                "Path",
                dispMsg + "\nCheck File: \n" + filename
            )

            if ret == PySide2.QtWidgets.QMessageBox.Yes:
                break
    if qtObj and fileObj is not None:
        # message box
        # !! C++ code static cannot use reference input
        # PySide2.QtWidgets.QMessageBox.question(parent, title,
        # text[, buttons=QMessageBox.StandardButtons(Yes | No)[,defaultButton=NoButton]])
        retTemp = PySide2.QtWidgets.QMessageBox.information(
            fileObj,
            "Select file to load",
            dispMsg  # ,
            # QMessageBox.Ok | QMessageBox.Close,
            # QMessageBox.Close
        )

        # Lopping for input
        while True:
            # static method
            # QString QFileDialog.getOpenFileName (QWidget parent = None, QString caption = QString(),
            # QString directory = QString(), QString filter = QString(), Options options = 0)
            filename, fileType = PySide2.QtWidgets.QFileDialog.getOpenFileNames(
                fileObj,
                dispMsg,
                "",
                fileTypes
            )

            # string out
            if len(filename) == 0:
                filename = ""
            elif len(filename) == 1:
                filename = filename[0]
            else:
                out = ""
                for file in filename:
                    out += file + ",\n"
                filename = out

            # ask results
            ret = PySide2.QtWidgets.QMessageBox.question(
                fileObj,
                "Path",
                dispMsg + "\nCheck File: \n" + filename
            )

            if ret == PySide2.QtWidgets.QMessageBox.Yes:
                break

    return filename


"""
##############################################################################
#Func: QT Open dialog return directory path
##############################################################################
"""
import PySide2
import os


def OpenDirPathQt(dispMsg="",
                  fileObj=None,
                  qtObj=False):
    # Open dialog return file path
    dirname = None
    # create tk object
    if not qtObj:
        # message box
        PySide2.QtWidgets.QMessageBox.information(
            None,
            "Select directory",
            dispMsg,
            PySide2.QtWidgets.QMessageBox.Ok
        )
        # Lopping for input
        while True:
            # static method
            # static PySide.QtGui.QFileDialog.getExistingDirectory([parent=None[, caption=""[, dir=""[, options=QFileDialog.ShowDirsOnly]]]])
            dirname = PySide2.QtWidgets.QFileDialog.getExistingDirectory(
                None,
                dispMsg,
                "",
                PySide2.QtWidgets.QFileDialog.ShowDirsOnly
            )
            # ask results
            ret = PySide2.QtWidgets.QMessageBox.question(
                None,
                "Path",
                dispMsg + "\nCheck File: \n" + dirname
            )

            if ret == PySide2.QtWidgets.QMessageBox.Yes:
                break
    if qtObj and fileObj is not None:
        # message box
        # !! C++ code static cannot use reference input
        # PySide2.QtWidgets.QMessageBox.question(parent, title,
        # text[, buttons=QMessageBox.StandardButtons(Yes | No)[,defaultButton=NoButton]])
        retTemp = PySide2.QtWidgets.QMessageBox.information(
            fileObj,
            "Select file to load",
            dispMsg  # ,
            # QMessageBox.Ok | QMessageBox.Close,
            # QMessageBox.Close
        )

        # Lopping for input
        while True:
            # static method
            # QString QFileDialog.getOpenFileName (QWidget parent = None, QString caption = QString(),
            # QString directory = QString(), QString filter = QString(), Options options = 0)
            dirname = PySide2.QtWidgets.QFileDialog.getExistingDirectory(
                fileObj,
                dispMsg,
                "",
                PySide2.QtWidgets.QFileDialog.ShowDirsOnly
            )
            # ask results
            ret = PySide2.QtWidgets.QMessageBox.question(
                fileObj,
                "Path",
                dispMsg + "\nCheck File: \n" + dirname
            )

            if ret == PySide2.QtWidgets.QMessageBox.Yes:
                break

    return dirname


"""
##############################################################################
#Func: find the non "." filename
##############################################################################
"""
import ntpath
import string


def FilenameFromPath(fullPath):
    # get bas name
    fileExt = ntpath.basename(fullPath)

    # find first "."
    index = fileExt.find(".")

    # file name pnly
    if index == -1:  # not find "."
        filename = fileExt
    else:
        filename = fileExt[:index]

    return filename


"""
##############################################################################
#Func: find the "." extension
##############################################################################
"""
import ntpath
import string


def ExtensionFromPath(fullPath):
    # get bas name
    fileExt = ntpath.basename(fullPath)

    # find first "."
    index = fileExt.find(".")

    # file name pnly
    extension = None
    if index == -1:  # not find "."
        print('Cannot find extension!!')
    else:
        extension = fileExt[index:]

    return extension


"""
##############################################################################
#Func: file name with extension in full path
##############################################################################
"""
import ntpath


def PathLeaf(path):
    head, tail = ntpath.split(path)  # ntpath.split dealing with file ends with a slash
    return tail or ntpath.basename(head)  # ntpath.basename backslash or forward slash as path separator

"""
##############################################################################
#Func: find the indices of character
##############################################################################
"""
def FindIndicesStr(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

"""
##############################################################################
# Func: find the parent directory name and full path of parent directory
##############################################################################
"""
import os


def ParentDir(path=None):
    fullParentDir = os.path.dirname(path)
    ParentDir = os.path.basename(path)
    return fullParentDir, ParentDir


"""
##############################################################################
#Func: filename remove invalid characters
##############################################################################
"""
import string


def ValidFileName(filename):
    safechars = string.ascii_letters + string.digits + "~ -_."
    fileNameSafeFilter = list(filter(lambda c: c in safechars, filename))
    fileNameSafe = "".join(str(e) for e in fileNameSafeFilter)  # convert filter to string

    print(fileNameSafe)

    return fileNameSafe


"""
##############################################################################
#Func: check valid path
##############################################################################
"""

import errno, os

# Sadly, Python fails to provide the following magic number for us.
ERROR_INVALID_NAME = 123
'''
Windows-specific error code indicating an invalid pathname.

See Also
----------
https://docs.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-
    Official listing of all such codes.
'''


def is_pathname_valid(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    '''
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)  # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError as exc:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
    # If any other exception was raised, this is an unrelated fatal issue
    # (e.g., a bug). Permit this exception to unwind the call stack.
    #
    # Did we mention this should be shipped with Python already?


def is_path_creatable(pathname: str) -> bool:
    '''
    `True` if the current user has sufficient permissions to create the passed
    pathname; `False` otherwise.
    '''
    # Parent directory of the passed path. If empty, we substitute the current
    # working directory (CWD) instead.
    dirname = os.path.dirname(pathname) or os.getcwd()
    return os.access(dirname, os.W_OK)


def is_path_exists_or_creatable(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS _and_
    either currently exists or is hypothetically creatable; `False` otherwise.

    This function is guaranteed to _never_ raise exceptions.
    '''
    try:
        # To prevent "os" module calls from raising undesirable exceptions on
        # invalid pathnames, is_pathname_valid() is explicitly called first.
        return is_pathname_valid(pathname) and (
                os.path.exists(pathname) or is_path_creatable(pathname))
    # Report failure on non-fatal filesystem complaints (e.g., connection
    # timeouts, permissions issues) implying this path to be inaccessible. All
    # other exceptions are unrelated fatal issues and should not be caught here.
    except OSError:
        return False


"""
##############################################################################
#Func: check or create directory
##############################################################################
"""
import os
import ntpath


def checkCreateDir(path):
    # init
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ''
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ''
    rtrnInfo["directoryPath"] = {}
    print('type', type(path))

    # check is file or directory
    if is_path_exists_or_creatable(path):
        # check and create dir
        if not os.path.exists(path):
            os.makedirs(path)
            rtrnInfo["message"] += "Create directory: \n{}".format(path)
        else:
            rtrnInfo["message"] += "Existing directory: \n{}".format(path)
    elif os.path.isfile(path):
        # get dir
        path = ntpath.dirname(path)
        # create dir
        if not os.path.exists(path):
            os.makedirs(path)
            rtrnInfo["message"] += "Input file name & create directory: \n{}".format(path)
        else:
            rtrnInfo["message"] += "Input file name & existing directory: \n{}".format(path)
    else:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] += "Cannot create directory - special file (socket, FIFO, device file): " \
                                    + "\n{}".format(path)
        print("Cannot create directory - special file (socket, FIFO, device file): "
              "\n{}".format(path))

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Create Directory time: {} s------".format(
        rtrnInfo["processTime"])
    rtrnInfo["message"] += "\n{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Func: Combine name with date and time
##############################################################################
"""
from datetime import datetime
import ntpath
import string


def DateFileName(
        Dir="",
        fileName="",
        extension="",
        appendDate=True
):
    # return info
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = None
    rtrnInfo["CombineName"] = None

    # all input need to be string
    if not isinstance(Dir, str) \
            or not isinstance(fileName, str) \
            or not isinstance(extension, str):
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = "Not all input is string"
        return rtrnInfo

    # current date and time
    nowStr = datetime.now().strftime("%d%m%y_%H%M")  # dd/mm/yy /hh/mm # %S for ss

    # dealing with file name with '//' or '\'
    if "/" or "\\" in fileName:
        fileName = PathLeaf(fileName)

    # remove illegal characters
    ## Set here the valid chars
    fileNameSafe = ValidFileName(fileName)

    # create full name with date
    if appendDate:
        fileNameDate = fileNameSafe + nowStr
    else:
        fileNameDate = fileNameSafe

    # extension start with "."
    if extension != "" and extension[0] != ".":
        extension = "." + extension

    # Combine name
    if Dir == "":
        rtrnInfo["CombineName"] = Dir + fileNameDate + extension
    elif "/" in Dir and "\\" not in Dir:
        if Dir[-1] != "/":
            Dir = Dir + "/"
        rtrnInfo["CombineName"] = Dir + fileNameDate + extension
    elif "\\" in Dir and "/" not in Dir:
        if Dir[-1] != "\\":
            Dir = Dir + "\\"
        rtrnInfo["CombineName"] = Dir + fileNameDate + extension

    else:
        Dir = Dir + '\\'
        rtrnInfo['CombineName'] = Dir + fileNameDate + extension

    return rtrnInfo


"""
##############################################################################
#Open dialog decide jump next section or exit
##############################################################################
"""
import tkinter
from tkinter import filedialog, messagebox


def JumpOrExit(dispMsg="",
               tkObj=False,
               root=None):
    # Open dialog select save file
    JumpFlg = True
    if not tkObj:
        root = tkinter.Tk()
    if messagebox.askyesno(title="Carry on NOT Jump or Exit?", message=dispMsg):
        if not tkObj:
            root.destroy()
        return JumpFlg
    else:
        if messagebox.askyesno(title="Jump next step? (Press 'No' Exit)", message="Jump next step? (Press 'No' Exit)"):
            if not tkObj:
                root.destroy()
            JumpFlg = False
            return JumpFlg
        else:
            if not tkObj:
                root.destroy()
                root.mainloop()
                print("User terminate program")
                sys.exit()
            if tkObj:  # GUI just return should be fine
                print("User wants to EXIT program")
                return None


"""
##############################################################################
#Show warning and exit
##############################################################################
"""
import tkinter
from tkinter import filedialog, messagebox


def WarnExit(dispMsg=""):
    root = tkinter.Tk()
    messagebox.showerror(title="Warning",
                         message=dispMsg)
    root.destroy()
    root.mainloop()
    sys.exit()


"""
##############################################################################
#Load NIFTI as matrix
##############################################################################
"""
import numpy
import SimpleITK
import tkinter
import sys
from tkinter import filedialog, messagebox
import os


def LoadNifti(headNiiPath="",
              subPaths=[0],
              niiPath="none",
              fileObj=None,
              tkObj=False,
              convertOrient=False,
              Orient="LPS"):
    # Load nifti and convert
    itkImag = SimpleITK.ReadImage(niiPath)
    print("Load: " + niiPath)

    # convert orientation
    if convertOrient:
        itkImag = SimpleITK.DICOMOrient(itkImag, Orient)
        print("Convert orientation: {}".format(Orient))

    # extract mat
    itkData = SimpleITK.GetArrayFromImage(itkImag)

    # get voxel spacing (for 3-D image)
    spacing = itkImag.GetSpacing()
    # spacing_x = spacing[0]
    # spacing_y = spacing[1]
    # spacing_z = spacing[2]
    # print("spacing_x: ")
    # print(spacing_x)
    # print("spacing_y: ")
    # print(spacing_y)
    # print("spacing_z: ")
    # print(spacing_z)

    # Load NIFTI as matrix
    # Check direct path is correct
    # if not (headNiiPath == "") and not os.path.isdir(headNiiPath):
    #     if not tkObj:
    #         fileObj = tkinter.Tk()
    #
    #     messagebox.showerror(title="Not correct directory path",
    #                          message="Not correct directory path: STOP!")
    #     if not tkObj:
    #         fileObj.destroy()
    #         fileObj.mainloop()
    #
    #     # sys.exit()
    #     return

    # # Create aorta mask
    # shape = numpy.shape(subPaths)
    # aorMskValArrayTF = numpy.zeros(shape)
    #
    # # flags
    # coroFlg = False
    # CTAFlg = False
    # aorFlg = False
    # otherFlg = False
    # checkCoro = False
    # checkCTA = False
    # checkAor = False
    #
    # # msgs
    # otherErMsg = False
    # aortaErMsg = False
    #
    # # empty matrix
    # itkData = numpy.zeros([200, 512, 512])
    #
    # for i in range(shape[0]):
    #     if niiPath == "none":
    #         subPath = subPaths[i]
    #         # Check files
    #         niiPath = headNiiPath + "/" + subPath
    #     else:
    #         # split filename and path
    #         headNiiPath, subPath = os.path.split(niiPath)
    #
    #     # Check is file
    #     checkFile = os.path.isfile(niiPath)
    #     # print ("Check file: " + niiPath)
    #     # print (checkFile)
    #
    #     if 'coronary' in subPath:  # Need to updata with different folder name
    #         checkCoro = True
    #         if checkFile == 0:  # False
    #             continue
    #         else:
    #             coroFlg = True
    #             break
    #     # Check CTA
    #     elif 'CTA' in subPath:  # Need to updata with different folder name
    #         checkCTA = True
    #         if checkFile == 0:  # False
    #             continue
    #         else:
    #             CTAFlg = True
    #             break
    #     # Check aorta/label map
    #     elif ('aorta' in subPath) or ('labelmap' in subPath):
    #         checkAor = True
    #         if checkFile == 0:  # False
    #             continue
    #         else:
    #             aorFlg = True
    #             break
    #     # Other file
    #     if checkFile == 0:  # False
    #         continue
    #     else:
    #         otherFlg = True
    #         break
    #
    # # Output data
    # if coroFlg == True or CTAFlg == True or aorFlg == True or otherFlg == True:
    #     # print("check coroFlg: " + str(coroFlg) +
    #     #       "\ncheck CTAFlg: " + str(CTAFlg) +
    #     #       "\ncheck aorFlg: " + str(aorFlg) +
    #     #       "\ncheck otherFlg: " + str(otherFlg))
    #     # Load nifti and convert
    #     itkImag = SimpleITK.ReadImage(niiPath)
    #     itkData = SimpleITK.GetArrayFromImage(itkImag)
    #     print("Load: " + niiPath)
    #     # get voxel spacing (for 3-D image)
    #     try:
    #         spacing = itkImag.GetSpacing()
    #         spacing_x = spacing[0]
    #         spacing_y = spacing[1]
    #         spacing_z = spacing[2]
    #         print("spacing_x: ")
    #         print(spacing_x)
    #         print("spacing_y: ")
    #         print(spacing_y)
    #         print("spacing_z: ")
    #         print(spacing_z)
    #     except:
    #         pass
    #
    # else:
    #     # Dealing flgs
    #     if coroFlg == False and checkCoro == True:
    #         # For destory 2nd dialogs
    #         if not tkObj:
    #             root = tkinter.Tk()
    #         messagebox.showerror(title="No coronary segmentation", message="No coronary segmentation: STOP!")
    #         if not tkObj:
    #             root.destroy()
    #             root.mainloop()
    #         sys.exit()
    #
    #     if CTAFlg == False and checkCTA == True:
    #         # For destory 2nd dialogs
    #         if not tkObj:
    #             root = tkinter.Tk()
    #         messagebox.showerror(title="No CTA", message="No CTA: STOP!")
    #         if not tkObj:
    #             root.destroy()
    #             root.mainloop()
    #         sys.exit()
    #
    #     if aorFlg == False and checkAor == True:
    #         print("Cannot load AORTA, empty mask created")
    #         aortaErMsg = True
    #     elif not otherFlg:
    #         otherErMsg = True
    #         print("Cannot load: " + subPath + "\n empty mask created")

    # Return values
    return "otherErMsg", "aortaErMsg", "aorMskValArrayTF", itkData, itkImag


"""
##############################################################################
#Dealing with aorta mask
##############################################################################
"""


def AortaMsk_Val(aortaErMsg, aorMskValArrayTF, aorMskValArray, itkData, coroOridata):
    # Dealing with aorta mask
    aortaMsk = numpy.zeros(numpy.shape(coroOridata))
    noAorMak = False
    if not aortaErMsg:
        aortaMsk = itkData
        aorMskVal = numpy.sum(numpy.multiply(aorMskValArray, aorMskValArrayTF))
    else:
        aorMskVal = 1
        noAorMak = True

    return noAorMak, aorMskVal, aortaMsk


"""
##############################################################################
#Save NIFTI data as .nii.gz
##############################################################################
"""
# self written
import Post_Image_Process_Functions
import time
from datetime import datetime
import SimpleITK


def MatNIFTISave(MatData,
                 SubF="",
                 imgPath="",
                 imgInfo="",
                 ConvertDType=False,
                 refDataMat=None,
                 out2D=False):
    # Save NIFTI data as .nii.gz

    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = None
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["SavePath"] = None
    rtrnInfo["message"] = ""

    # No input create path
    if imgPath == "":
        # folder
        headPath = DirectoryPath()
        # Time
        todays_date = datetime.now()
        # Create path
        imgPath = headPath + "/" + SubF + "_" + str(todays_date.year) + str(todays_date.month) + str(
            todays_date.day) + "_" + str(todays_date.hour) + str(todays_date.minute) + ".nii.gz"
        # msg
        rtrnInfo["message"] += "No saving path given. Use: \n{}\n".format(imgPath)

    # check extension
    if ".nii.gz" not in imgPath:
        imgPath = imgPath + ".nii.gz"
        # msg
        rtrnInfo["message"] += "Saving path is not NIFTI format. Add extension: \n{}\n".format(imgPath)

    # convert data type
    if ConvertDType \
            and refDataMat is not None:
        convertData = Post_Image_Process_Functions.ConvertDType(refDataMat=refDataMat,
                                                                tConDataMat=MatData,
                                                                inObj="Array")
        MatData = convertData.ConvertData
        # msg
        rtrnInfo["message"] += "Converted data type:\n{}\n".format(convertData.rtrnInfo["message"])

    # Create img


    img = SimpleITK.GetImageFromArray(MatData)
    if imgInfo == "":
        pass
    # image data information setting
    elif not out2D:
        if isinstance(imgInfo, SimpleITK.Image):
            print("Save NIFTI: input is SimpleITK.Image")
            img.CopyInformation(imgInfo)
            # set direction seperately
            img.SetDirection(imgInfo.GetDirection())
            # msg
            rtrnInfo["message"] += "Save NIFTI: input is SimpleITK.Image\n"
        else:
            print("Save NIFTI: input is")
            print(type(imgInfo))
            img.CopyInformation(imgInfo)
            # msg
            rtrnInfo["message"] += "Save NIFTI: input is {}\n".format(type(imgInfo))
    # 2D image
    else:
        # set separately
        # print("######################################")
        # for key in imgInfo.GetMetaDataKeys():
        #     print("\"{0}\":\"{1}\"".format(key, imgInfo.GetMetaData(key)))
        #
        # print("######################################")
        # print(imgInfo.GetOrigin())
        # print("######################################")
        # print(imgInfo.GetSpacing())
        # print("######################################")
        # print(imgInfo.GetDirection())

        # set
        img.SetOrigin(list(imgInfo.GetOrigin())[:2])
        img.SetSpacing(list(imgInfo.GetSpacing())[:2])
        # img.SetDirection(imgInfo.GetDirection())
        # img.SetMetaData(imgInfo.GetMetaData())
        # print("######################################")
        # print("size")
        # print(img.GetSize())




    # create directory
    createDir = checkCreateDir(path=ntpath.dirname(imgPath))
    rtrnInfo["message"] += "Create Direcotry: {}\n".format(createDir["message"])

    # oputput
    SimpleITK.WriteImage(img, imgPath)

    # msg
    rtrnInfo["message"] += "Save: {}\n".format(imgPath)

    # return information
    rtrnInfo["SavePath"] = str(imgPath)

    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Saving file time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}\n".format(
        rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
#Load dictionary
##############################################################################
"""
import ast


def LoadDictionary(headPath="", CenterSubFs="", CenterPath='none'):
    # Load dictionary
    if CenterPath == 'none':
        CenterPath = headPath + "/" + CenterSubFs[0]

    # load dictionary data
    file = open(CenterPath, "r")
    contents = file.read()
    dictionary = ast.literal_eval(contents)
    file.close()
    # print(dictionary)
    print("Load dictionary: " + str(CenterPath))

    return dictionary


"""
##############################################################################
#In dictionary find branch name, coronary mask val, center points
##############################################################################
"""
import numpy


def LoadCoronaryVals(dictionary, dictItem):
    # In dictionary find branch name, coronary mask val, center points
    lblItem = 0
    branchName = dictionary[dictItem]['branch_name']
    branchMskVal = dictionary[dictItem]['label'][lblItem]  # first number in a array

    # stacking coordinate
    noCenLinRow = numpy.shape(dictionary[dictItem]['coordinates'])
    # create empty matrix
    cenLineRows = noCenLinRow[0]
    cenLine_xtail = numpy.zeros([cenLineRows, 3])  # 3 columns x, y, z

    # stack colms = x, rows = y, depth = z
    for i in range(noCenLinRow[0]):
        cenLine_xtail[i, 0] = dictionary[dictItem]['coordinates'][i]["X"]
        cenLine_xtail[i, 1] = dictionary[dictItem]['coordinates'][i]["Y"]
        cenLine_xtail[i, 2] = dictionary[dictItem]['coordinates'][i]["Z"]

    # Convert centerline depth = z to the first column as in ITK
    cenLine = numpy.roll(cenLine_xtail, 1, 1)

    print("Load branch: " + branchName)

    return branchName, branchMskVal, cenLine, cenLineRows


"""
##############################################################################
#Determine file path and correct
##############################################################################
"""


def CheckConvertPath(inPath):
    # path is string
    if not isinstance(inPath, str):
        print("Warning! Input path is not string for \n def CheckConvertPath")
        return

    # Check path seperator
    singleBackSlash = inPath.find('\\')
    singleForwardSlash = inPath.find('/')
    doubleBackSlash = inPath.find('\\\\')
    print("singleBackSlash")
    print(singleBackSlash)
    print("singleForwardSlash")
    print(singleForwardSlash)
    print("doubleBackSlash")
    print(doubleBackSlash)

    # convert all slash to double back for no "//"
    if doubleBackSlash == -1:
        convPath = inPath.replace('\\', '\\\\')
        convPath = convPath.replace('/', '\\\\')
        return convPath
    else:
        print("No conversion: // in the path!!")
        return


"""
##############################################################################
#Func: append two list
##############################################################################
"""
import time


def AppendLists(lst1,
                lst2,
                sep="\\"):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = None
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["combineList"] = []

    # Need two lists:
    if not isinstance(lst1, list) \
            or not isinstance(lst2, list):
        # return information
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = "Need lists input!"
        print("Need lists input!")

        # return
        return rtrnInfo

    # combine lists
    for lst1i in lst1:
        for lst2i in lst2:
            combo = lst1i + sep + lst2i
            rtrnInfo["combineList"].append(combo)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Saving time: {} s------".format(rtrnInfo["processTime"])
    print("create:")
    print(rtrnInfo["combineList"])

    return rtrnInfo


"""
##############################################################################
#Class load NIFTI data
##############################################################################
"""
import SimpleITK


class OpenLoadNIFTI:
    def __init__(self,
                 dispMsg="Load Nifiti",
                 fileObj=None,
                 tkObj=False,
                 GUI=True,
                 filePath=None,
                 convertOrient=False,
                 Orient="LPS"):
        # Set values
        self.fileObj = fileObj
        self.tkObj = tkObj
        self.dispMsg = dispMsg
        self.convertOrient = convertOrient
        self.Orient = Orient

        # GUI load file
        if GUI:
            print("GUI Load data")
            self.InteractOpen()
        elif not GUI and filePath != None:
            print("NO GUI Load data")
            self.filePath = filePath
            self.NoInteractOpen()

    def InteractOpen(self):
        # GUI file path
        self.filePath = OpenFilePath(dispMsg=self.dispMsg,
                                     fileObj=self.fileObj,
                                     tkObj=self.tkObj)
        # Load data
        self.otherErMsg, self.aortaErMsg, self.aorMskValArrayTF, self.OriData, self.OriImag = LoadNifti(
            niiPath=self.filePath,
            fileObj=self.fileObj,
            tkObj=self.tkObj,
            convertOrient=self.convertOrient,
            Orient=self.Orient
        )

    def NoInteractOpen(self):
        # Load data
        self.otherErMsg, self.aortaErMsg, self.aorMskValArrayTF, self.OriData, self.OriImag = LoadNifti(
            niiPath=self.filePath,
            fileObj=self.fileObj,
            tkObj=self.tkObj,
            convertOrient=self.convertOrient,
            Orient=self.Orient
        )


"""
##############################################################################
#Class save NIFTI data
##############################################################################
"""


class SaveNIFTI:
    def __init__(self,
                 MatData,
                 imgInfo=None,
                 Lbl=None,
                 tkObj=False,
                 dispMsg="Choose Nifit saving path",
                 GUI=True,
                 filePath=None):
        self.dispMsg = dispMsg
        self.MatData = MatData
        self.imgInfo = imgInfo
        self.tkObj = tkObj
        self.Lbl = Lbl
        self.err = False

        # GUI
        if GUI:
            print("GUI Save data")
            self.InteractSave()
        if not GUI and filePath != None:
            print("No GUI Save data")
            self.filePath = filePath
            self.NoInteractSave()

    def InteractSave(self):
        saveResults = JumpOrExit(dispMsg="Carry on: saving results?",
                                 tkObj=self.tkObj,
                                 root=self.Lbl)

        if saveResults == True:
            self.filePath = SaveFilePath(dispMsg=self.dispMsg,
                                         fileObj=self.Lbl,
                                         tkObj=self.tkObj)
            self.fullFilePath = MatNIFTISave(MatData=self.MatData,
                                             imgPath=self.filePath,
                                             imgInfo=self.imgInfo)

        if saveResults == None:  # GUI stop
            self.err = True

    def NoInteractSave(self):
        # save
        self.fullFilePath = MatNIFTISave(MatData=self.MatData,
                                         imgPath=self.filePath,
                                         imgInfo=self.imgInfo)


"""
##############################################################################
#Class load dictionary TXT (jason) data
##############################################################################
"""


class CenterlineDict:
    def __init__(self,
                 dispMsg="Load dictionary of centerline TXT",
                 filePath="",
                 itemVal=0):
        self.filePath = filePath  # For later predefined case
        self.itemVal = itemVal
        self.dispMsg = dispMsg

        # load dictionsry
        self.filePath = OpenFilePath(dispMsg=self.dispMsg)
        self.dictionary = LoadDictionary(CenterPath=self.filePath)

    def DictInfoExtract(self, itemVal=0):
        self.itemVal = itemVal

        # function return values
        self.branchName, self.branchMskVal, self.cenLine, self.cenLineRows = LoadCoronaryVals(self.dictionary,
                                                                                              self.itemVal)


"""
##############################################################################
#Load DICOM and save other type
##############################################################################
"""
import os
import SimpleITK


class ReadWriteDCM:
    def __init__(self,
                 fileDirect=None, outfilePath=None):
        # set variables
        self.fileDirect = fileDirect
        self.message = ""
        self.error = False
        self.filePath = outfilePath
        self.DCMReader = None
        self.DCMImg = None

    def ReadDCMSeries(self,
                      fileDirect=None):
        # update file directory
        if fileDirect != None:
            self.fileDirect = fileDirect

        # check directory exist
        if not os.path.isdir(self.fileDirect):
            self.error = True
            self.message += "\nDirectory: \n" + str(self.fileDirect) + "\n does not exist!"
            return

        # Load DCM
        self.DCMReader = SimpleITK.ImageSeriesReader()

        # Check there is multiple series (IDs) in a directory
        IDs = self.DCMReader.GetGDCMSeriesIDs(self.fileDirect)
        if len(IDs) > 1:
            print('Multiple series in {}'.format(self.fileDirect))
            print(IDs)
            print('Default uses ID[0]: {}'.format(IDs[0]))
            dicom_names = self.DCMReader.GetGDCMSeriesFileNames(self.fileDirect, seriesID =IDs[0], useSeriesDetails=True)

        dicom_names = self.DCMReader.GetGDCMSeriesFileNames(self.fileDirect, useSeriesDetails=True)

        # Dealing with very long names
        if len(dicom_names) > 512:
            print('Long DCM files!!')
            tagDictLstInit = None
            dicom_names_use = []
            excludeTags = [
                '0008|0018', # Uniquely identifies the SOP Instance
                '0008|0033', # The time the image pixel data creation started.
                '0020|0013', # A number that identifies this image.
                '0020|0032', # A number that identifies this image.
                '0020|1041', # Relative position of the image plane expressed in mm.
                '0020|9056', # The ordinal number of a frame in a group of frames, with the same Stack ID (0020,9056).
                '0020|9057', # The ordinal number of a frame in a group of frames, with the same Stack ID (0020,9056).
                '7005|1067', # TOSHIBA
                '7005|1069', # TOSHIBA
                '7005|106c', # TOSHIBA
            ]

            for file in dicom_names:
                # get file info
                reader = SimpleITK.ImageFileReader()
                reader.SetFileName(file)
                reader.LoadPrivateTagsOn()
                reader.ReadImageInformation()

                # get meta data
                tagDict = {}
                for k in reader.GetMetaDataKeys():
                    if k not in excludeTags:
                        tagDict[k] = reader.GetMetaData(k)

                        if file != dicom_names[0]:
                            if reader.GetMetaData(k) != tagDictLstInit[k]:
                                print('difference tag: {}'.format(k))
                                print(reader.GetMetaData(k))
                                print(tagDictLstInit[k])

                print('########################################################')

                # first one dict
                if file == dicom_names[0]:
                    tagDictLstInit = tagDict
                    dicom_names_use.append(file)

                else:
                    # keep file names the same as the first one
                    if tagDict == tagDictLstInit: dicom_names_use.append(file)
                    else: continue

            print('Sorted files {} out of {}'.format(len(dicom_names_use), len(dicom_names)))

        else:
            dicom_names_use = dicom_names

        # read image
        self.DCMReader.SetFileNames(dicom_names_use)
        self.DCMImg = self.DCMReader.Execute()
        print(dicom_names_use)

    def ConvertOrientation(self, orientation="LPS"):

        print(self.DCMImg.GetDimension())
        print(self.DCMImg.GetSize())

        try:
            self.DCMImg = SimpleITK.DICOMOrient(self.DCMImg, orientation)
        except:
            # # convert dimension when there is 4 dimensions
            # if self.DCMImg.GetDimension() == 4 and self.DCMImg.GetSize()[3] == 1:
            if self.DCMImg.GetDimension() == 4:
                self.DCMImg = self.DCMImg[:, :, :, 0] # convert dimension

            self.DCMImg = SimpleITK.DICOMOrient(self.DCMImg, orientation)

    def SaveDCMSeries(self, outfilePath=None):
        # File Path
        if outfilePath != None:
            self.filePath = outfilePath

        # save
        SimpleITK.WriteImage(self.DCMImg, self.filePath)
        self.message += "\nSave: \n" + str(self.filePath)


"""
##############################################################################
#Func: write TXT
##############################################################################
"""


def WriteTXT(path, txt, mode="append"):
    """
    Write TXT
    :param path:
    :return:
    """
    # write
    if mode == "write":
        save_text = open(path, 'w+')
        save_text.write(txt)
        save_text.close()
    elif mode == "append":
        save_text = open(path, 'a+')
        save_text.write(txt)
        save_text.close()

    return


"""
##############################################################################
#Func: List all first child directories in a directory
##############################################################################
"""
import os


def FirstSubDirectories(
        directoryPath
):
    # check directory existing
    if not os.path.isdir(directoryPath):
        raise ValueError("Not a directory: {}!!".format(directoryPath))
    if not os.path.exists(directoryPath):
        raise ValueError("Directory not exist: {}!!".format(directoryPath))

    # list all subdirectories
    rtrnInfo = {}
    rtrnInfo['directoryNames'] = []
    rtrnInfo['directoryFullPaths'] = []
    for f in os.scandir(directoryPath):
        if f.is_dir():
            rtrnInfo['directoryNames'].append(f.name)
            rtrnInfo['directoryFullPaths'].append(f.path)

    return rtrnInfo


"""
##############################################################################
#Func: convert parameter to True
##############################################################################
"""


def CheckTrue(parameter):
    isTrue = False

    if isinstance(parameter, int) or isinstance(parameter, float):
        isTrue = parameter == 1
    elif isinstance(parameter, str):
        trueStrs = ["Yes", "Y", "True", "correct"]
        isTrue = parameter.lower() in (string.lower() for string in trueStrs)
    elif isinstance(parameter, bool):
        isTrue = parameter

    return isTrue

"""
##############################################################################
#Func: List all files & names with a specific extension in a dir
##############################################################################
"""

def FindFilesExtension(dirPath, ext, traverse=False):
    import os

    # init
    outDict = {}
    outDict["FileNames"] = []
    outDict["FileFullPaths"] = []

    # extension add .
    if "." not in ext: ext = "." + ext

    # traverse
    if traverse:
        for root, dirs, files in os.walk(dirPath):
            for file in files:
                if ext in file: # may not be ending
                    # append name
                    outDict["FileNames"].append(FilenameFromPath(file))
                    # append path
                    outDict["FileFullPaths"].append(os.path.join(root, file))
    else:
        for file in os.listdir(dirPath):
            if ext in file: # may not be ending
                # append name
                outDict["FileNames"].append(FilenameFromPath(file))
                # append path
                outDict["FileFullPaths"].append(os.path.join(dirPath, file))
    
    return outDict

"""
##############################################################################
#Func: find file absolute path under a directory
##############################################################################
"""

def ReturnFilesFullPath(dirPath, fileRef, folderSearch=None, traverse=False):
    import os

    # init
    filePathLst = []

    # traverse
    if traverse:
        for root, dirs, files in os.walk(dirPath):
            # have search folder
            if (folderSearch is not None) and (folderSearch in dirs):
                for file in files:
                    if fileRef in file:  # may not be ending
                        # append path
                        filePathLst.append(os.path.join(root, file))
                    else: continue
            else: # search all files
                for file in files:
                    print(file)
                    if fileRef in file:  # may not be ending
                        # append path
                        filePathLst.append(os.path.join(root, file))
                    else: continue

    else: # only current folder
        print(traverse)
        for file in os.listdir(dirPath):
            print(file)
            if fileRef in file:  # may not be ending
                # append path
                filePathLst.append(os.path.join(dirPath, file))

    return filePathLst

"""
##############################################################################
#Func: find folder absolute path under a directory
##############################################################################
"""

def ReturnFoldersFullPath(dirPath, folderSearch=None, traverse=False):
    import os

    # init
    dirlist = []

    # traverse
    if traverse:
        for root, dirs, files in os.walk(dirPath):
            # have search folder
            if folderSearch in dirs:  # may not be ending
                # append path
                print(root)
                print(os.path.join(root, folderSearch))
                dirlist.append(os.path.join(root, folderSearch))
            else: continue

    else: # only current folder
        print("No traverse")
        dirlist = [os.path.join(dirPath, item) for item in os.listdir(dirPath) if os.path.isdir(os.path.join(dirPath, item))]

    return dirlist

"""
##############################################################################
#Func: standardise the folder seperation \\
##############################################################################
"""

def standardFolderSeperation(inStr):

    filetemp = inStr.replace("/", "\\")
    file = filetemp.replace("\\\\", "\\")

    return file

"""
##############################################################################
#Func: batch copy files from one folder to another with folder structure
##############################################################################
"""
import shutil

def BatchCopyFiles(fromFolder, toFolder, fileRefs, numberLimit=None):
    # standardise
    fromFolder = standardFolderSeperation(fromFolder)
    toFolder = standardFolderSeperation(toFolder)

    # loop through all files
    numberCount = 0
    for root, dirs, files in os.walk(fromFolder):
        for file in files:
            # absolute path
            file = os.path.join(root, file)

            # check files are in the files
            for fileRef in fileRefs:
                fileRef = standardFolderSeperation(fileRef)

                if fileRef in file:
                    print("Find {} in \n{}".format(fileRef, file))

                    # create destiation file path
                    destinationFile = file.replace(fromFolder, toFolder)

                    # copy
                    os.makedirs(os.path.dirname(destinationFile), exist_ok=True)
                    shutil.copy(file, destinationFile)
                    print("Copy from: \n{} \nto \n{}".format(file, destinationFile))

                    # check number limit
                    numberCount += 1
                    if numberCount >= numberLimit:
                        print("Reach limit: {}".format(numberLimit))
                        return
