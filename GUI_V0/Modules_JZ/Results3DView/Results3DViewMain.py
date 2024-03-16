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
import Preprocess_Mask
import VTK_Functions
import QT_GUI
import Pd_Funs
##############################################################################

##############################################################################
# Standard libs
import numpy
from datetime import datetime


##############################################################################

class Results3DView:
    def __init__(self, UI=None, Hedys=None):
        # input
        if UI:
            self.ui = UI
        else:
            self.ui = None

        if Hedys:
            self.modelui = Hedys.ui
        else:
            self.modelui = None

        # images buttons
        self.ui.chooseScreenShotBtn_R3V.clicked.connect(lambda: self.ChooseSaveFileScreenShot())
        self.ui.saveScreenShotBtn_R3V.clicked.connect(lambda: self.ScreenShot())
        self.ui.showBtn_R3V.clicked.connect(lambda: self.View3D())

        # volume rendering buttons
        self.ui.VRChooseFilesBtn_R3V.clicked.connect(lambda: self.ChooseOpenFilesVR())
        self.ui.VRSaveFilesBtn_R3V.clicked.connect(lambda: self.ChooseSaveFileVR())

        # points rendering buttons
        self.ui.PTChooseFilesBtn_R3V.clicked.connect(lambda: self.ChooseOpenFilesPT())

        # points rendering buttons
        self.ui.CLChooseFilesBtn_R3V.clicked.connect(lambda: self.ChooseOpenFilesCL())
        self.ui.CLFactorChooseFilesBtn_R3V.clicked.connect(lambda: self.ChooseFactorFileCL())

        # results rendering buttons
        self.ui.RRChooseFilesBtn_R3V.clicked.connect(lambda: self.ChooseOpenVolumeFilesRR())
        self.ui.RRChooseResultsFilesBtn_R3V.clicked.connect(lambda: self.ChooseOpenResultsFilesRR())
        self.ui.RRSaveFilesBtn_R3V.clicked.connect(lambda: self.ChooseSaveFileRR())
        self.ui.RRSaveSTLFilesBtn_R3V.clicked.connect(lambda: self.ChooseSaveSTLFileRR())
        self.ui.RRSaveCutFilesBtn_R3V.clicked.connect(lambda: self.ChooseSaveCutFileRR())

        # image slicing buttons
        self.ui.ISChooseFilesBtn_R3V.clicked.connect(lambda: self.ChooseOpenFilesIS())
        self.ui.ISSaveCutFilesBtn_R3V.clicked.connect(lambda: self.ChooseSaveFileIS())

        # general setting buttons
        self.ui.ChooseOutlineFilesBtn_R3V.clicked.connect(lambda: self.ChooseOpenOultlineFiles())
        self.ui.getCameraBtn_R3V.clicked.connect(lambda: self.GetCamera())

        # batch processing buttons
        self.ui.batchBtn_R3V.clicked.connect(lambda: self.BatchRender())
        self.ui.batchFileChooseBtn_R3V.clicked.connect(lambda: self.ChooseTableFile())

        # initial definition
        self.i = 0
        self.render = None

    def View3D(self):
        # separate rendering
        if self.ui.seperateRenderCheckBox_R3V.isChecked():
            self.initNoWdiget()
        else:
            self.initWdiget()

        # volume rendering
        if self.ui.volumeRenderCheckBox_R3V.isChecked():
            self.VolumeRendering()

        # point 3D
        if self.ui.point3DCheckBox_R3V.isChecked():
            self.Points3D()

        # line 3D
        if self.ui.line3DCheckBox_R3V.isChecked():
            self.Lines3D()

        # results rendering
        if self.ui.resultsRenderCheckBox_R3V.isChecked():
            self.ResultsRendering()

        # image slices
        if self.ui.sliceImageCheckBox_R3V.isChecked():
            self.SliceImage()

        # text
        if self.ui.textCheckBox_R3V.isChecked():
            self.Text()

        # backgoround
        self.render.Background(str(self.ui.bckColorLineTxt_LC.text()))

        # outline
        if self.ui.outlineCheckBox_R3V.isChecked():
            self.render.Outline(str(self.ui.outlineFileTxt_R3V.toPlainText()))

        # scale
        self.ScaleAxes()

        # camera
        self.SetCamera()

        # loop
        self.render.Initiate()
        self.UpdateMsgLog("Start Image")

    def initNoWdiget(self):
        # init width height
        height = int(self.ui.windowHeightLineTxt_LC.text())
        width = int(self.ui.windowWidthLineTxt_LC.text())

        # vtk init
        self.render = VTK_Functions.VTK3DView(
            qt=False,
            qtFrame=None,
            qtLayout=None,
            height=height,
            width=width
        )

    def initWdiget(self):
        if self.modelui:
            ui = self.modelui
        else:
            ui = self.ui
        # layout frame
        # add dock
        dock = QT_GUI.CreateDockWidget(
            parent=ui,
            name="3DView_" + str(self.i),
            position='Right'
        )
        frame = dock.GetFrame()
        layout = dock.GetLayout()
        self.i += 1

        # vtk init
        self.render = VTK_Functions.VTK3DView(
            qt=True,
            qtFrame=frame,
            qtLayout=layout
        )

    """
    ##############################################################################
    Batch rendering
    ##############################################################################
    """

    def ChooseTableFile(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="output table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.filePathBRTxt_R3V.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose output Table file path:\n{}".format(
                self.ui.filePathBRTxt_R3V.toPlainText()
            )
        )

    def BatchRender(self):
        # input
        batchFilePath = self.ui.filePathBRTxt_R3V.toPlainText()

        # batch files
        dataFrameBatch = Pd_Funs.OpenDF(
            inPath=batchFilePath,
            header=0
        )

        # Looping
        for filePath in dataFrameBatch['Cases'].tolist():

            # load data frame
            dataFrame = Pd_Funs.OpenDF(
                inPath=filePath,
                header=0
            )

            # init
            self.initNoWdiget()

            # file number
            fileNum = None

            # screen shot
            if self.ui.seperateRenderCheckBox_R3V.isChecked():
                if 'ScreenShotPaths' in dataFrame.columns:
                    ScreenShotPaths = dataFrame['ScreenShotPaths'].tolist()
                else:
                    self.UpdateMsgLog("Warning!! No screen shot file paths!")
                    return

            # results rendering
            if self.ui.resultsRenderCheckBox_R3V.isChecked():
                print(dataFrame)
                # get all files
                if 'volumeFilesVRR' in dataFrame.columns:
                    volumeFilesVRR = dataFrame['volumeFilesVRR'].tolist()
                    fileNum = len(volumeFilesVRR)
                else:
                    self.UpdateMsgLog("Warning!! No input volume file paths!")
                    return

                if 'referenceFilesVRR' in dataFrame.columns:
                    referenceFilesVRR = dataFrame['referenceFilesVRR'].tolist()
                else:
                    self.UpdateMsgLog("Warning!! No input result file paths!")
                    return

                if 'vtkPathsVRR' in dataFrame.columns:
                    vtkPathsVRR = dataFrame['vtkPathsVRR'].tolist()
                else:
                    vtkPathsVRR = [None] * len(volumeFilesVRR)

                if 'out2DMeshPathsVRR' in dataFrame.columns:
                    out2DMeshPathsVRR = dataFrame['out2DMeshPathsVRR'].tolist()
                else:
                    out2DMeshPathsVRR = [None] * len(volumeFilesVRR)

                if 'outVolumeCutPathsVRR' in dataFrame.columns:
                    outVolumeCutPathsVRR = dataFrame['outVolumeCutPathsVRR'].tolist()
                else:
                    outVolumeCutPathsVRR = [None] * len(volumeFilesVRR)

                if 'displayRangeVRR' in dataFrame.columns:
                    displayRangeVRR = dataFrame['displayRangeVRR'].tolist()
                else:
                    displayRangeVRR = [None] * len(volumeFilesVRR)

                if 'rangeStartsVRR' in dataFrame.columns:
                    rangeStartsVRR = dataFrame['rangeStartsVRR'].tolist()
                else:
                    rangeStartsVRR = [None] * len(volumeFilesVRR)

                if 'rangeStopsVRR' in dataFrame.columns:
                    rangeStopsVRR = dataFrame['rangeStopsVRR'].tolist()
                else:
                    rangeStopsVRR = [None] * len(volumeFilesVRR)

            # STL rendering
            if self.ui.volumeRenderCheckBox_R3V.isChecked():
                print(dataFrame)
                # input
                filesVR = dataFrame['filesVR'].tolist()
                transparenciesVR = dataFrame['transparenciesVR'].tolist()
                colorsVR = dataFrame['colorsVR'].tolist()
                smoothChoicesVR = dataFrame['smoothChoicesVR'].tolist()
                iterationsVR = dataFrame['iterationsVR'].tolist()
                passBandsVR = dataFrame['passBandsVR'].tolist()
                output2DMeshesVR = dataFrame['output2DMeshesVR'].tolist()
                out2DMeshPathsVR = dataFrame['out2DMeshPathsVR'].tolist()
                showEdgesVR = dataFrame['showEdgesVR'].tolist()
                bottomsVR = dataFrame['bottomsVR'].tolist()
                topsVR = dataFrame['topsVR'].tolist()

                fileNum = len(filesVR)

            # get camera setting
            if 'autoSetCam' in dataFrame.columns:
                autoSetCam = dataFrame['autoSetCam'].tolist()
            else:
                autoSetCam = [None] * fileNum

            if 'parallelProjectionCam' in dataFrame.columns:
                parallelProjectionCam = dataFrame['parallelProjectionCam'].tolist()
            else:
                parallelProjectionCam = [None] * fileNum

            if 'viewUpStrCam' in dataFrame.columns:
                viewUpStrCam = dataFrame['viewUpStrCam'].tolist()
            else:
                viewUpStrCam = [None] * fileNum

            if 'viewAngleCam' in dataFrame.columns:
                viewAngleCam = dataFrame['viewAngleCam'].tolist()
            else:
                viewAngleCam = [None] * fileNum

            if 'positionStrCam' in dataFrame.columns:
                positionStrCam = dataFrame['positionStrCam'].tolist()
            else:
                positionStrCam = [None] * fileNum

            if 'focalPointStrCam' in dataFrame.columns:
                focalPointStrCam = dataFrame['focalPointStrCam'].tolist()
            else:
                focalPointStrCam = [None] * fileNum

            # loop
            for case in range(fileNum):
                if self.ui.resultsRenderCheckBox_R3V.isChecked():
                    self.ResultsRendering(
                        volumeFiles=[volumeFilesVRR[case]],
                        referenceFiles=[referenceFilesVRR[case]],
                        vtkPaths=[vtkPathsVRR[case]],
                        out2DMeshPaths=[out2DMeshPathsVRR[case]],
                        outPaths=[outVolumeCutPathsVRR[case]],
                        displayRange=bool(displayRangeVRR[case]),
                        rangeStarts=[rangeStartsVRR[case]],
                        rangeStops=[rangeStopsVRR[case]]
                    )

                if self.ui.volumeRenderCheckBox_R3V.isChecked():
                    self.VolumeRendering(
                        [filesVR[case]],
                        [transparenciesVR[case]],
                        [colorsVR[case]],
                        [smoothChoicesVR[case]],
                        [iterationsVR[case]],
                        [passBandsVR[case]],
                        [output2DMeshesVR[case]],
                        [out2DMeshPathsVR[case]],
                        [showEdgesVR[case]],
                        [bottomsVR[case]],
                        [topsVR[case]]
                    )

                # text
                if self.ui.textCheckBox_R3V.isChecked():
                    self.Text()

                # backgoround
                self.render.Background(str(self.ui.bckColorLineTxt_LC.text()))

                # outline
                if self.ui.outlineCheckBox_R3V.isChecked():
                    self.render.Outline(str(self.ui.outlineFileTxt_R3V.toPlainText()))

                # scale
                self.ScaleAxes()

                # set camera
                if autoSetCam[case] is None:
                    autoSet = None
                else:
                    autoSet = bool(autoSetCam[case])

                if parallelProjectionCam[case] is None:
                    parallelProjection = None
                else:
                    parallelProjection = bool(parallelProjectionCam[case])

                if viewUpStrCam[case] is None:
                    viewUpStr = None
                else:
                    viewUpStr = viewUpStrCam[case]

                if viewAngleCam[case] is None:
                    viewAngle = None
                else:
                    viewAngle = float(viewAngleCam[case])

                if positionStrCam[case] is None:
                    positionStr = None
                else:
                    positionStr = positionStrCam[case]

                if focalPointStrCam[case] is None:
                    focalPointStr = None
                else:
                    focalPointStr = focalPointStrCam[case]

                self.SetCamera(
                    autoSet=autoSet,
                    parallelProjection=parallelProjection,
                    viewUpStr=viewUpStr,
                    viewAngle=viewAngle,
                    positionStr=positionStr,
                    focalPointStr=focalPointStr
                )

                # render
                self.render.OffScreenRnder()

                # screenshot
                if self.ui.seperateRenderCheckBox_R3V.isChecked():
                    self.ScreenShot(path=ScreenShotPaths[case])

                # finish rendering
                self.render.ClearRenderer()

    """
    ##############################################################################
    Volume rendering
    ##############################################################################
    """

    def ChooseOpenFilesVR(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Load medical image or mask",
                                                 fileTypes="All files (*.*);; NIFTI/NRRD files(*.nii.gz *.nrrd) ;; STL files (*.stl)",
                                                 fileObj=self.ui,
                                                 qtObj=True)

        # set filename
        self.ui.filesVRTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseSaveFileVR(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Path to save screenshot",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                                                           "STL files (*.stl *.obj) ;; "
                                                           "Img files (*.png *.jpg) ;; "
                                                           "VTK files (*.vtk, *.vtp, *.vtu) ",
                                                 qtObj=True)

        # set filename
        self.ui.out2DMeshPathsVRTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving file:\n{}".format(filename))

    def VolumeRendering(
            self,
            files=None,
            transparencies=None,
            colors=None,
            smoothChoices=None,
            iterations=None,
            passBands=None,
            output2DMeshes=None,
            out2DMeshPaths=None,
            showEdges=None,
            bottoms=None,
            tops=None
    ):
        # input
        if files is None:
            files = Preprocess_Mask.StrToLst(strIn=self.ui.filesVRTxt_R3V.toPlainText())["listOut"]
        if transparencies is None: transparencies = \
            Preprocess_Mask.StrToLst(strIn=self.ui.transparenciesVRTxt_R3V.toPlainText())["floatOut"]
        if colors is None:
            colors = Preprocess_Mask.StrToLst(strIn=self.ui.colorsVRTxt_R3V.toPlainText())["listOut"]
        if smoothChoices is None:
            smoothChoices = Preprocess_Mask.StrToLst(strIn=self.ui.smoothChoicesVRTxt_R3V.toPlainText())["booleanOut"]
        if iterations is None:
            iterations = Preprocess_Mask.StrToLst(strIn=self.ui.iterationsVRTxt_R3V.toPlainText())[
                "intOut"]
        if passBands is None: passBands = Preprocess_Mask.StrToLst(strIn=self.ui.passBandsVRTxt_R3V.toPlainText())[
            "floatOut"]
        if output2DMeshes is None: output2DMeshes = \
            Preprocess_Mask.StrToLst(strIn=self.ui.output2DMeshesVRTxt_R3V.toPlainText())["booleanOut"]
        if out2DMeshPaths is None: out2DMeshPaths = \
            Preprocess_Mask.StrToLst(strIn=self.ui.out2DMeshPathsVRTxt_R3V.toPlainText())["listOut"]
        if showEdges is None: showEdges = Preprocess_Mask.StrToLst(strIn=self.ui.showEdgesVRTxt_R3V.toPlainText())[
            "booleanOut"]
        if bottoms is None: bottoms = Preprocess_Mask.StrToLst(strIn=self.ui.bottomsVRTxt_R3V.toPlainText())["floatOut"]
        if tops is None: tops = Preprocess_Mask.StrToLst(strIn=self.ui.topsVRTxt_R3V.toPlainText())["floatOut"]

        msg = 'files: \n{}'.format(files) + \
              '\ntransparencies: \n{}'.format(transparencies) + \
              '\ncolors: \n{}'.format(colors) + \
              '\nsmoothChoices: \n{}'.format(smoothChoices) + \
              '\niterations: \n{}'.format(iterations) + \
              '\npassBands: \n{}'.format(passBands) + \
              '\noutput2DMeshes: \n{}'.format(output2DMeshes) + \
              '\nout2DMeshPaths: \n{}'.format(out2DMeshPaths) + \
              '\nshowEdges: \n{}'.format(showEdges) + \
              '\nbottoms: \n{}'.format(bottoms) + \
              '\ntops: \n{}'.format(tops)

        self.UpdateMsgLog(msg)

        self.render.VolumeRendering(
            files,
            transparencies,
            colors,
            smoothChoices,
            iterations,
            passBands,
            output2DMeshes,
            out2DMeshPaths,
            showEdges,
            bottoms,
            tops
        )

        # update
        self.UpdateMsgLog(self.render.message)

    """
    ##############################################################################
    Points rendering
    ##############################################################################
    """

    def ChooseOpenFilesPT(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Load medical image or mask",
                                                 fileTypes="All files (*.*);; NIFTI/NRRD files(*.nii.gz *.nrrd) ;; STL files (*.stl)",
                                                 fileObj=self.ui,
                                                 qtObj=True)

        # set filename
        self.ui.filesPTTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def Points3D(self):
        # input
        files = Preprocess_Mask.StrToLst(strIn=self.ui.filesPTTxt_R3V.toPlainText())["listOut"]
        filters = Preprocess_Mask.StrToLst(strIn=self.ui.filtersPTTxt_R3V.toPlainText())["listOut"]
        threStarts = Preprocess_Mask.StrToLst(strIn=self.ui.threStartsPTTxt_R3V.toPlainText())["floatOut"]
        threStops = Preprocess_Mask.StrToLst(strIn=self.ui.threStopsPTTxt_R3V.toPlainText())["floatOut"]
        pointSizes = Preprocess_Mask.StrToLst(strIn=self.ui.pointSizesPTTxt_R3V.toPlainText())["floatOut"]
        colors = Preprocess_Mask.StrToLst(strIn=self.ui.colorsPTTxt_R3V.toPlainText())["listOut"]

        self.render.Points3D(
            files,
            filters,
            threStarts,
            threStops,
            pointSizes,
            colors
        )

        # update
        self.UpdateMsgLog(self.render.message)

    """
    ##############################################################################
    Points rendering
    ##############################################################################
    """

    def ChooseOpenFilesCL(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Load medical image or mask",
                                                 fileTypes="All files (*.*);; NIFTI/NRRD files(*.nii.gz *.nrrd) ;; STL files (*.stl)",
                                                 fileObj=self.ui,
                                                 qtObj=True)

        # set filename
        self.ui.filesCLTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseFactorFileCL(self):
        # Save data
        filename = Save_Load_File.OpenFilePathQt(
            dispMsg="output table path",
            fileObj=self.ui,
            fileTypes="Table (*.txt, *.csv, *.xlsx, *.xls, *.xlsm, *.xlsb) ;; "
                      "All files (*.*);; ",
            qtObj=True
        )

        # set filename
        self.ui.filePathFactorCLTxt_R3V.setPlainText(filename)

        # update message
        self.UpdateMsgLog(
            msg="Choose factor Table file path:\n{}".format(
                self.ui.filePathFactorCLTxt_R3V.toPlainText()
            )
        )

    def Lines3D(self):
        # input
        files = Preprocess_Mask.StrToLst(strIn=self.ui.filesCLTxt_R3V.toPlainText())["listOut"]
        factorFile = self.ui.filePathFactorCLTxt_R3V.toPlainText()
        widths = Preprocess_Mask.StrToLst(strIn=self.ui.widthsCLTxt_R3V.toPlainText())["floatOut"]
        colors = Preprocess_Mask.StrToLst(strIn=self.ui.colorsCLTxt_R3V.toPlainText())["listOut"]

        smoothChoices = Preprocess_Mask.StrToLst(strIn=self.ui.smoothChoicesCLTxt_R3V.toPlainText())["booleanOut"]
        smoothResamples = Preprocess_Mask.StrToLst(strIn=self.ui.resamplingCLTxt_R3V.toPlainText())["intOut"]

        filters = Preprocess_Mask.StrToLst(strIn=self.ui.filtersCLTxt_R3V.toPlainText())["listOut"]
        threStarts = Preprocess_Mask.StrToLst(strIn=self.ui.threStartsCLTxt_R3V.toPlainText())["floatOut"]
        threStops = Preprocess_Mask.StrToLst(strIn=self.ui.threStopsCLTxt_R3V.toPlainText())["floatOut"]

        print(files)
        print(factorFile)
        print(widths)
        print(colors)
        print(filters)
        print(threStarts)
        print(threStops)

        self.render.Lines3D(
            files=files,
            factorFile=factorFile,
            filters=filters,
            threStarts=threStarts,
            threStops=threStops,
            widths=widths,
            colors=colors,
            smoothChoices=smoothChoices,
            smoothResamples=smoothResamples
        )

        # update
        self.UpdateMsgLog(self.render.message)

    """
    ##############################################################################
    Results rendering
    ##############################################################################
    """

    def ChooseOpenVolumeFilesRR(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Load medical image or mask",
                                                 fileTypes="All files (*.*);; NIFTI/NRRD files(*.nii.gz *.nrrd) ;; STL files (*.stl)",
                                                 fileObj=self.ui,
                                                 qtObj=True)

        # set filename
        self.ui.volumeFilesTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseOpenResultsFilesRR(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Load medical image or mask",
                                                 fileTypes="All files (*.*);; NIFTI/NRRD files(*.nii.gz *.nrrd) ;; STL files (*.stl)",
                                                 fileObj=self.ui,
                                                 qtObj=True)

        # set filename
        self.ui.referenceFilesTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseSaveFileRR(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Path to save screenshot",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                                                           "STL files (*.stl *.obj) ;; "
                                                           "Img files (*.png *.jpg) ;; "
                                                           "VTK files (*.vtk, *.vtp, *.vtu) ",
                                                 qtObj=True)

        # set filename
        self.ui.vtkPathsTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving file:\n{}".format(filename))

    def ChooseSaveSTLFileRR(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Path to save smooth mesh",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                                                           "STL files (*.stl *.obj) ;; "
                                                           "Img files (*.png *.jpg) ;; "
                                                           "VTK files (*.vtk, *.vtp, *.vtu) ",
                                                 qtObj=True)

        # set filename
        self.ui.out2DMeshPathsTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving file:\n{}".format(filename))

    def ChooseSaveCutFileRR(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Path to save cut VOI",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                                                           "STL files (*.stl *.obj) ;; "
                                                           "Img files (*.png *.jpg) ;; "
                                                           "VTK files (*.vtk, *.vtp, *.vtu) ",
                                                 qtObj=True)

        # set filename
        self.ui.outPathsTxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving file:\n{}".format(filename))

    def ResultsRendering(
            self,
            volumeFiles=None,
            referenceFiles=None,
            vtkPaths=None,
            out2DMeshPaths=None,
            outPaths=None,
            displayRange=None,
            rangeStarts=None,
            rangeStops=None
    ):
        # input
        if volumeFiles is None:
            volumeFiles = Preprocess_Mask.StrToLst(strIn=self.ui.volumeFilesTxt_R3V.toPlainText())["listOut"]
        if referenceFiles is None:
            referenceFiles = Preprocess_Mask.StrToLst(strIn=self.ui.referenceFilesTxt_R3V.toPlainText())["listOut"]
        ballRadii = Preprocess_Mask.StrToLst(strIn=self.ui.ballRadiiTxt_R3V.toPlainText())["floatOut"]

        saveChoices = Preprocess_Mask.StrToLst(strIn=self.ui.saveChoicesTxt_R3V.toPlainText())["booleanOut"]
        if vtkPaths is None:
            vtkPaths = Preprocess_Mask.StrToLst(strIn=self.ui.vtkPathsTxt_R3V.toPlainText())["listOut"]

        smoothChoices = Preprocess_Mask.StrToLst(strIn=self.ui.smoothChoicesTxt_R3V.toPlainText())["booleanOut"]
        iterations = Preprocess_Mask.StrToLst(strIn=self.ui.iterationsTxt_R3V.toPlainText())["intOut"]
        passBands = Preprocess_Mask.StrToLst(strIn=self.ui.passBandsTxt_R3V.toPlainText())["floatOut"]
        output2DMeshes = Preprocess_Mask.StrToLst(strIn=self.ui.output2DMeshesTxt_R3V.toPlainText())["booleanOut"]
        if out2DMeshPaths is None:
            out2DMeshPaths = Preprocess_Mask.StrToLst(strIn=self.ui.out2DMeshPathsTxt_R3V.toPlainText())["listOut"]

        volumeCut = self.ui.volumeCutRRCheckBox_R3V.isChecked()
        interp = self.ui.resampleRRCBox_LC.currentText()
        xStarts = Preprocess_Mask.StrToLst(strIn=self.ui.xStartsTxt_R3V.toPlainText())["floatOut"]
        xStops = Preprocess_Mask.StrToLst(strIn=self.ui.xStopsTxt_R3V.toPlainText())["floatOut"]
        yStarts = Preprocess_Mask.StrToLst(strIn=self.ui.yStartsTxt_R3V.toPlainText())["floatOut"]
        yStops = Preprocess_Mask.StrToLst(strIn=self.ui.yStopsTxt_R3V.toPlainText())["floatOut"]
        zStarts = Preprocess_Mask.StrToLst(strIn=self.ui.zStartsTxt_R3V.toPlainText())["floatOut"]
        zStops = Preprocess_Mask.StrToLst(strIn=self.ui.zStopsTxt_R3V.toPlainText())["floatOut"]
        xResamplings = Preprocess_Mask.StrToLst(strIn=self.ui.xResamplingsTxt_R3V.toPlainText())["floatOut"]
        yResamplings = Preprocess_Mask.StrToLst(strIn=self.ui.yResamplingsTxt_R3V.toPlainText())["floatOut"]
        zResamplings = Preprocess_Mask.StrToLst(strIn=self.ui.zResamplingsTxt_R3V.toPlainText())["floatOut"]
        outputNIFTIs = Preprocess_Mask.StrToLst(strIn=self.ui.outputNIFTIsTxt_R3V.toPlainText())["booleanOut"]
        if outPaths is None:
            outPaths = Preprocess_Mask.StrToLst(strIn=self.ui.outPathsTxt_R3V.toPlainText())["listOut"]

        if displayRange is None:
            displayRange = self.ui.displayRangeRRCheckBox_R3V.isChecked()
        if rangeStarts is None:
            rangeStarts = Preprocess_Mask.StrToLst(strIn=self.ui.rangeStartsTxt_R3V.toPlainText())["floatOut"]
        if rangeStops is None:
            rangeStops = Preprocess_Mask.StrToLst(strIn=self.ui.rangeStopsTxt_R3V.toPlainText())["floatOut"]

        colorMap = self.ui.colorMapRRCheckBox_R3V.isChecked()
        colorNumbers = Preprocess_Mask.StrToLst(strIn=self.ui.colorNumbersTxt_R3V.toPlainText())["intOut"]
        colorHueStarts = Preprocess_Mask.StrToLst(strIn=self.ui.colorHueStartsTxt_R3V.toPlainText())["floatOut"]
        colorHueStops = Preprocess_Mask.StrToLst(strIn=self.ui.colorHueStopsTxt_R3V.toPlainText())["floatOut"]
        colorSaturationStarts = Preprocess_Mask.StrToLst(strIn=self.ui.colorSaturationStartsTxt_R3V.toPlainText())[
            "floatOut"]
        colorSaturationStops = Preprocess_Mask.StrToLst(strIn=self.ui.colorSaturationStopsTxt_R3V.toPlainText())[
            "floatOut"]
        colorValueStarts = Preprocess_Mask.StrToLst(strIn=self.ui.colorValueStartsTxt_R3V.toPlainText())["floatOut"]
        colorValueStops = Preprocess_Mask.StrToLst(strIn=self.ui.colorValueStopsTxt_R3V.toPlainText())["floatOut"]
        colorAboves = Preprocess_Mask.StrToLst(strIn=self.ui.colorAbovesTxt_R3V.toPlainText())["listOut"]
        colorBelows = Preprocess_Mask.StrToLst(strIn=self.ui.colorBelowsTxt_R3V.toPlainText())["listOut"]
        colorNans = Preprocess_Mask.StrToLst(strIn=self.ui.colorNansTxt_R3V.toPlainText())["listOut"]

        scalarBar = self.ui.scalarBarRRCheckBox_R3V.isChecked()
        scalarWidths = Preprocess_Mask.StrToLst(strIn=self.ui.scalarWidthsTxt_R3V.toPlainText())["floatOut"]
        scalarTitles = Preprocess_Mask.StrToLst(strIn=self.ui.scalarTitlesTxt_R3V.toPlainText())["listOut"]
        scalarVeticalTitleSpaces = \
            Preprocess_Mask.StrToLst(strIn=self.ui.scalarVeticalTitleSpacesTxt_R3V.toPlainText())["floatOut"]
        scalarMaxNumColors = Preprocess_Mask.StrToLst(strIn=self.ui.scalarMaxNumColorsTxt_R3V.toPlainText())["intOut"]
        scalarNumLbls = Preprocess_Mask.StrToLst(strIn=self.ui.scalarNumLblsTxt_R3V.toPlainText())["intOut"]

        text = self.ui.textRRCheckBox_R3V.isChecked()
        textSize = int(self.ui.textSizeRRLineTxt_LC.text())
        textColor = str(self.ui.textColorRRLineTxt_LC.text())
        textOpacity = float(self.ui.textOpacityRRLineTxt_LC.text())
        textBold = self.ui.textBoldRRCheckBox_R3V.isChecked()
        textItalic = self.ui.textItalicRRCheckBox_R3V.isChecked()
        textShadow = self.ui.textShadowRRCheckBox_R3V.isChecked()

        bottoms = Preprocess_Mask.StrToLst(strIn=self.ui.bottomsRRTxt_R3V.toPlainText())["floatOut"]
        tops = Preprocess_Mask.StrToLst(strIn=self.ui.topsRRTxt_R3V.toPlainText())["floatOut"]

        # update message
        msg = 'rangeStarts: {} \n'.format(rangeStarts) + \
              'rangeStops: {}'.format(rangeStops)
        self.UpdateMsgLog(msg)

        self.render.ResultsRendering(
            volumeFiles,
            referenceFiles,
            ballRadii,
            saveChoices,
            vtkPaths,
            smoothChoices,
            iterations,
            passBands,
            output2DMeshes,
            out2DMeshPaths,
            volumeCut,
            interp,
            xStarts,
            xStops,
            yStarts,
            yStops,
            zStarts,
            zStops,
            xResamplings,
            yResamplings,
            zResamplings,
            outputNIFTIs,
            outPaths,
            displayRange,
            rangeStarts,
            rangeStops,
            colorMap,
            colorNumbers,
            colorHueStarts,
            colorHueStops,
            colorSaturationStarts,
            colorSaturationStops,
            colorValueStarts,
            colorValueStops,
            colorAboves,
            colorBelows,
            colorNans,
            scalarBar,
            scalarWidths,
            scalarTitles,
            scalarVeticalTitleSpaces,
            scalarMaxNumColors,
            scalarNumLbls,
            text,
            textSize,
            textColor,
            textOpacity,
            textBold,
            textItalic,
            textShadow,
            bottoms,
            tops
        )

        # update
        self.UpdateMsgLog(self.render.message)

    """
    ##############################################################################
    Image slices
    ##############################################################################
    """

    def ChooseOpenFilesIS(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Load medical image or mask",
                                                 fileTypes="All files (*.*);; NIFTI/NRRD files(*.nii.gz *.nrrd) ;; STL files (*.stl)",
                                                 fileObj=self.ui,
                                                 qtObj=True)

        # set filename
        self.ui.imageFilesSITxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ChooseSaveFileIS(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Path to save screenshot",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "NIFTI/NRRD files(*.nii.gz *.nrrd) ;; "
                                                           "STL files (*.stl *.obj) ;; "
                                                           "Img files (*.png *.jpg) ;; "
                                                           "VTK files (*.vtk, *.vtp, *.vtu) ",
                                                 qtObj=True)

        # set filename
        self.ui.outPathsSITxt_R3V.appendPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving file:\n{}".format(filename))

    def SliceImage(self):
        # input
        imageFiles = Preprocess_Mask.StrToLst(strIn=self.ui.imageFilesSITxt_R3V.toPlainText())["listOut"]

        volumeCut = self.ui.volumeCutSICheckBox_R3V.isChecked()
        interp = self.ui.resampleSICBox_LC.currentText()
        xStarts = Preprocess_Mask.StrToLst(strIn=self.ui.xStartsSITxt_R3V.toPlainText())["floatOut"]
        xStops = Preprocess_Mask.StrToLst(strIn=self.ui.xStopsSITxt_R3V.toPlainText())["floatOut"]
        yStarts = Preprocess_Mask.StrToLst(strIn=self.ui.yStartsSITxt_R3V.toPlainText())["floatOut"]
        yStops = Preprocess_Mask.StrToLst(strIn=self.ui.yStopsSITxt_R3V.toPlainText())["floatOut"]
        zStarts = Preprocess_Mask.StrToLst(strIn=self.ui.zStartsSITxt_R3V.toPlainText())["floatOut"]
        zStops = Preprocess_Mask.StrToLst(strIn=self.ui.zStopsSITxt_R3V.toPlainText())["floatOut"]
        xResamplings = Preprocess_Mask.StrToLst(strIn=self.ui.xResamplingsSITxt_R3V.toPlainText())["floatOut"]
        yResamplings = Preprocess_Mask.StrToLst(strIn=self.ui.yResamplingsSITxt_R3V.toPlainText())["floatOut"]
        zResamplings = Preprocess_Mask.StrToLst(strIn=self.ui.zResamplingsSITxt_R3V.toPlainText())["floatOut"]
        outputNIFTIs = Preprocess_Mask.StrToLst(strIn=self.ui.outputNIFTIsSITxt_R3V.toPlainText())["booleanOut"]
        outPaths = Preprocess_Mask.StrToLst(strIn=self.ui.outPathsSITxt_R3V.toPlainText())["listOut"]

        displayRange = self.ui.displayRangeSICheckBox_R3V.isChecked()
        rangeStarts = Preprocess_Mask.StrToLst(strIn=self.ui.rangeStartsSITxt_R3V.toPlainText())["floatOut"]
        rangeStops = Preprocess_Mask.StrToLst(strIn=self.ui.rangeStopsSITxt_R3V.toPlainText())["floatOut"]

        colorMap = self.ui.colorMapSICheckBox_R3V.isChecked()
        colorNumbers = Preprocess_Mask.StrToLst(strIn=self.ui.colorNumbersSITxt_R3V.toPlainText())["intOut"]
        colorHueStarts = Preprocess_Mask.StrToLst(strIn=self.ui.colorHueStartsSITxt_R3V.toPlainText())["floatOut"]
        colorHueStops = Preprocess_Mask.StrToLst(strIn=self.ui.colorHueStopsSITxt_R3V.toPlainText())["floatOut"]
        colorSaturationStarts = Preprocess_Mask.StrToLst(strIn=self.ui.colorSaturationStartsSITxt_R3V.toPlainText())[
            "floatOut"]
        colorSaturationStops = Preprocess_Mask.StrToLst(strIn=self.ui.colorSaturationStopsSITxt_R3V.toPlainText())[
            "floatOut"]
        colorValueStarts = Preprocess_Mask.StrToLst(strIn=self.ui.colorValueStartsSITxt_R3V.toPlainText())["floatOut"]
        colorValueStops = Preprocess_Mask.StrToLst(strIn=self.ui.colorValueStopsSITxt_R3V.toPlainText())["floatOut"]
        colorAboves = Preprocess_Mask.StrToLst(strIn=self.ui.colorAbovesSITxt_R3V.toPlainText())["listOut"]
        colorBelows = Preprocess_Mask.StrToLst(strIn=self.ui.colorBelowsSITxt_R3V.toPlainText())["listOut"]
        colorNans = Preprocess_Mask.StrToLst(strIn=self.ui.colorNansSITxt_R3V.toPlainText())["listOut"]

        slide3D = self.ui.slide3DSICheckBox_R3V.isChecked()
        fixedSlice = self.ui.fixedSliceSICheckBox_R3V.isChecked()
        uniformSlice = self.ui.uniformSliceSICheckBox_R3V.isChecked()
        directX = self.ui.directXSICheckBox_R3V.isChecked()
        directY = self.ui.directYSICheckBox_R3V.isChecked()
        directZ = self.ui.directZSICheckBox_R3V.isChecked()
        xStartSlices = Preprocess_Mask.StrToLst(strIn=self.ui.xStartSlicesSITxt_R3V.toPlainText())["intOut"]
        xStopSlices = Preprocess_Mask.StrToLst(strIn=self.ui.xStopSlicesSITxt_R3V.toPlainText())["intOut"]
        yStartSlices = Preprocess_Mask.StrToLst(strIn=self.ui.yStartSlicesSITxt_R3V.toPlainText())["intOut"]
        yStopSlices = Preprocess_Mask.StrToLst(strIn=self.ui.yStopSlicesSITxt_R3V.toPlainText())["intOut"]
        zStartSlices = Preprocess_Mask.StrToLst(strIn=self.ui.zStartSlicesSITxt_R3V.toPlainText())["intOut"]
        zStopSlices = Preprocess_Mask.StrToLst(strIn=self.ui.zStopSlicesSITxt_R3V.toPlainText())["intOut"]

        text = self.ui.textSICheckBox_R3V.isChecked()
        textSize = int(self.ui.textSizeSILineTxt_LC.text())
        textColor = str(self.ui.textColorSILineTxt_LC.text())
        textOpacity = float(self.ui.textOpacitySILineTxt_LC.text())
        textBold = self.ui.textBoldSICheckBox_R3V.isChecked()
        textItalic = self.ui.textItalicSICheckBox_R3V.isChecked()
        textShadow = self.ui.textShadowSICheckBox_R3V.isChecked()

        self.render.SlicingImage(
            imageFiles,
            volumeCut,
            interp,
            xStarts,
            xStops,
            yStarts,
            yStops,
            zStarts,
            zStops,
            xResamplings,
            yResamplings,
            zResamplings,
            outputNIFTIs,
            outPaths,
            displayRange,
            rangeStarts,
            rangeStops,
            colorMap,
            colorNumbers,
            colorHueStarts,
            colorHueStops,
            colorSaturationStarts,
            colorSaturationStops,
            colorValueStarts,
            colorValueStops,
            colorAboves,
            colorBelows,
            colorNans,
            slide3D,
            fixedSlice,
            uniformSlice,
            directX,
            directY,
            directZ,
            xStartSlices,
            xStopSlices,
            yStartSlices,
            yStopSlices,
            zStartSlices,
            zStopSlices,
            text,
            textSize,
            textColor,
            textOpacity,
            textBold,
            textItalic,
            textShadow
        )

        # update
        self.UpdateMsgLog(self.render.message)

    """
    ##############################################################################
    General setting
    ##############################################################################
    """

    def Text(self):
        # input
        msg = self.ui.textTTTxt_R3V.toPlainText()
        textSize = int(self.ui.textSizeTTLineTxt_LC.text())
        textColor = str(self.ui.textColorTTLineTxt_LC.text())
        textOpacity = float(self.ui.textOpacityTTLineTxt_LC.text())
        textBold = self.ui.textBoldTTCheckBox_R3V.isChecked()
        textItalic = self.ui.textItalicTTCheckBox_R3V.isChecked()
        textShadow = self.ui.textShadowTTCheckBox_R3V.isChecked()

        self.render.DisplayText(
            msg,
            textSize,
            textColor,
            textOpacity,
            textBold,
            textItalic,
            textShadow
        )

        # update
        self.UpdateMsgLog("Change Text to: {}".format(msg))

    def ChooseOpenOultlineFiles(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Load medical image or mask",
                                                 fileTypes="All files (*.*);; NIFTI/NRRD files(*.nii.gz *.nrrd) ;; STL files (*.stl)",
                                                 fileObj=self.ui,
                                                 qtObj=True)

        # set filename
        self.ui.outlineFileTxt_R3V.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose file:\n{}".format(filename))

    def ScaleAxes(self):
        scale = self.ui.scaleCheckBox_R3V.isChecked()
        axes = self.ui.axesCheckBox_R3V.isChecked()

        top = self.ui.topSCLCheckBox_R3V.isChecked()
        bottom = self.ui.bottomSCLCheckBox_R3V.isChecked()
        left = self.ui.leftSCLCheckBox_R3V.isChecked()
        right = self.ui.rightSCLCheckBox_R3V.isChecked()

        textSize = int(self.ui.textSizeSCLLineTxt_LC.text())
        textColor = str(self.ui.textColorSCLLineTxt_LC.text())
        textOpacity = float(self.ui.textOpacitySCLLineTxt_LC.text())
        textBold = self.ui.textBoldSCLCheckBox_R3V.isChecked()
        textItalic = self.ui.textItalicSCLCheckBox_R3V.isChecked()
        textShadow = self.ui.textShadowSCLCheckBox_R3V.isChecked()

        if scale:
            self.render.ScaleBar(
                top,
                bottom,
                left,
                right,
                textSize,
                textColor,
                textOpacity,
                textBold,
                textItalic,
                textShadow
            )

            # update message
            self.UpdateMsgLog(msg="Add scale")

        if axes:
            self.render.Axes(
                textSize,
                textColor,
                textOpacity,
                textBold,
                textItalic,
                textShadow
            )

            # update message
            self.UpdateMsgLog(msg="Add axes")

    def SetCamera(
            self,
            autoSet=None,
            parallelProjection=None,
            viewUpStr=None,
            viewAngle=None,
            positionStr=None,
            focalPointStr=None
    ):
        # set input
        if autoSet is None:
            autoSet = self.ui.autoSetCheckBox_R3V.isChecked()
        if parallelProjection is None:
            parallelProjection = self.ui.parallelProjectionCheckBox_R3V.isChecked()
        if viewUpStr is None:
            viewUp = Preprocess_Mask.StrToLst(strIn=self.ui.viewUpTxt_R3V.text())["floatOut"]
        else:
            viewUp = Preprocess_Mask.StrToLst(strIn=viewUpStr)["floatOut"]
        if viewAngle is None:
            viewAngle = float(self.ui.viewAngleTxt_R3V.text())
        if positionStr is None:
            position = Preprocess_Mask.StrToLst(strIn=self.ui.positionTxt_R3V.text())["floatOut"]
        else:
            position = Preprocess_Mask.StrToLst(strIn=positionStr)["floatOut"]
        if focalPointStr is None:
            focalPoint = Preprocess_Mask.StrToLst(strIn=self.ui.focalPointTxt_R3V.text())["floatOut"]
        else:
            focalPoint = Preprocess_Mask.StrToLst(strIn=focalPointStr)["floatOut"]

        if autoSet:
            msg = 'Auto set camera'
        else:
            msg = "viewUp: {} \n".format(viewUp) + \
                  "viewAngle: {} \n".format(viewAngle) + \
                  "position: {} \n".format(position) + \
                  "focalPoint: {} \n".format(focalPoint)

        # update message
        self.UpdateMsgLog(msg="Camera setting:\n" + msg)

        self.render.SetCamera(
            autoSet,
            parallelProjection,
            position,
            focalPoint,
            viewUp,
            viewAngle
        )

        # update message
        self.UpdateMsgLog(msg="Set Camera!")

    def GetCamera(self):
        self.render.GetCamera()

        # set
        self.ui.viewUpTxt_R3V.setText(str(self.render.cameraInfo['viewUp']))
        self.ui.viewAngleTxt_R3V.setText(str(self.render.cameraInfo['viewAngle']))
        self.ui.positionTxt_R3V.setText(str(self.render.cameraInfo['position']))
        self.ui.focalPointTxt_R3V.setText(str(self.render.cameraInfo['focalPoint']))

        # msg
        msg = "Position: {}\n" \
              "Focal Position: {}\n" \
              "View up: {}\n" \
              "View Angle: {}".format(
            self.render.cameraInfo['position'],
            self.render.cameraInfo['focalPoint'],
            self.render.cameraInfo['viewUp'],
            self.render.cameraInfo['viewAngle']
        )

        self.ui.cameraInfoTxt_LC.setPlainText(msg)

        # update message
        self.UpdateMsgLog(msg)

    def ScreenShot(self, path=None):
        if path is None:
            path = self.ui.screenShotPathTxt_R3V.toPlainText()

        self.render.ScreenShot(path)

        # update message
        self.UpdateMsgLog(msg="Save screenshot: {}".format(path))

    def ChooseSaveFileScreenShot(self):
        # Save data
        filename = Save_Load_File.SaveFilePathQT(dispMsg="Path to save screenshot",
                                                 fileObj=self.ui,
                                                 fileTypes="All files (*.*);; "
                                                           "Img files (*.png *.jpg) ;; ",
                                                 qtObj=True)

        # set filename
        self.ui.screenShotPathTxt_R3V.setPlainText(filename)

        # update message
        self.UpdateMsgLog(msg="Choose saving file:\n{}".format(filename))

    """
    ##############################################################################
    Message
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
        # self.outLog += disp
        print(msg)
