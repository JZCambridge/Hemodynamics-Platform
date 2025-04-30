# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 20:04:55 2020

@author: yingmohuanzhou
"""
import VTK_Numpy
import Post_Image_Process_Functions
import Image_Process_Functions
import Save_Load_File
import SITK_Numpy
import Pd_Funs

"""
##############################################################################
#VTK Create actor with NIFTI file input
##############################################################################
"""
import vtk
import numpy
from vtk.util import numpy_support  # numpy_to_vtk and vtk_to_numpy
import sys


def CreateActor(fileName_Data, tissueB, tissueT):
    # Check input is file or numpy data
    strFlg = False
    arrayFlg = False
    if isinstance(fileName_Data, str):
        # print("VTK input is file string")
        strFlg = True
    elif isinstance(fileName_Data.GetArray(), numpy.ndarray):
        # print("VTK input is numpy array")
        # print("Input array dtype: ")
        # print(fileName_Data.GetArray().dtype)
        arrayFlg = True
    else:
        raise TypeError("Input data style is not array or string. Not support!!")
        return

    # VTK Create actor with NIFTI file input
    if strFlg:
        # print("Read NIFTI file")
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(fileName_Data)
        reader.Update()
    # Convert numpy
    elif arrayFlg:
        # print("Processing Array")
        reader = fileName_Data

    selectTissue = vtk.vtkImageThreshold()
    selectTissue.ThresholdBetween(tissueB, tissueT)
    selectTissue.SetInValue(255)
    selectTissue.SetOutValue(0)

    if strFlg:
        print("Thresholding Nifiti file")
        selectTissue.SetInputConnection(reader.GetOutputPort())
    if arrayFlg:
        # Convert vtk arrray in to polydata
        selectTissue.SetInputConnection(reader.GetOutputPort())

    smoothing_filter = vtk.vtkImageGaussianSmooth()
    smoothing_filter.SetDimensionality(3)
    smoothing_filter.SetInputConnection(selectTissue.GetOutputPort())
    smoothing_filter.SetStandardDeviations(10.0, 10.0, 10.0)
    smoothing_filter.SetRadiusFactors(10.0, 10.0, 10.0)

    isoValue = 255
    mcubes = vtk.vtkMarchingCubes()
    mcubes.SetInputConnection(selectTissue.GetOutputPort())
    # mcubes.SetInputConnection(selectTissue.GetOutputPort())
    mcubes.ComputeScalarsOff()
    mcubes.ComputeGradientsOff()
    mcubes.ComputeNormalsOn()
    mcubes.SetValue(0, isoValue)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(mcubes.GetOutputPort())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stripper.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return strFlg, arrayFlg, actor, reader, mapper


"""
##############################################################################
#VTK Create actor with NIFTI file input
##############################################################################
"""
import vtk
import numpy
from vtk.util import numpy_support  # numpy_to_vtk and vtk_to_numpy
import sys


def CreateNiftiActor(
        fileName,
        tissueB,
        tissueT,
        smooth=False,
        iteration=16,
        passBand=0.001,
        color='red'
):
    # Check input is file or numpy data
    if not isinstance(fileName, str):
        raise TypeError("Input file is not string!!")

    # print("Read NIFTI file")
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(fileName)
    reader.Update()

    selectTissue = vtk.vtkImageThreshold()
    selectTissue.ThresholdBetween(tissueB, tissueT)
    selectTissue.SetInValue(255)
    selectTissue.SetOutValue(0)
    selectTissue.SetInputConnection(reader.GetOutputPort())

    isoValue = 255
    mcubes = vtk.vtkMarchingCubes()
    mcubes.SetInputConnection(selectTissue.GetOutputPort())
    mcubes.ComputeScalarsOff()
    mcubes.ComputeGradientsOff()
    mcubes.ComputeNormalsOn()
    mcubes.SetValue(0, isoValue)

    if smooth:
        # window sinc fucntion
        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetInputConnection(mcubes.GetOutputPort())
        smoother.SetNumberOfIterations(iteration)
        smoother.BoundarySmoothingOff()
        smoother.FeatureEdgeSmoothingOff()
        smoother.SetFeatureAngle(120.0)
        smoother.SetPassBand(passBand)
        smoother.NonManifoldSmoothingOn()
        smoother.NormalizeCoordinatesOn()
        smoother.Update()
        # stripper
        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(smoother.GetOutputPort())
    else:
        # stripper for triangles
        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(mcubes.GetOutputPort())

    # update and polydata
    stripper.Update()
    polydata = stripper.GetOutput()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stripper.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    # Set color
    actor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d(color))

    return actor, polydata

"""
##############################################################################
#Func: Create actor from any supported VTK mesh format
##############################################################################
"""
def CreateSTLActor(
        fileName,
        smooth=False,
        iteration=16,
        passBand=0.001,
        color='red'
):
    # Check input is file or numpy data
    if not isinstance(fileName, str):
        raise TypeError("Input file is not string!!")
        
    # Get file extension
    extension = os.path.splitext(fileName)[1].lower()
    
    # Choose appropriate reader based on extension
    if extension == '.vtk':
        reader = vtk.vtkPolyDataReader()
    elif extension == '.stl':
        reader = vtk.vtkSTLReader()
    elif extension == '.ply':
        reader = vtk.vtkPLYReader()
    elif extension == '.obj':
        reader = vtk.vtkOBJReader()
    elif extension == '.vtp':
        reader = vtk.vtkXMLPolyDataReader()
    elif extension == '.vtu':
        reader = vtk.vtkXMLUnstructuredGridReader()
    else:
        raise ValueError(f"Unsupported file format: {extension}")
        
    reader.SetFileName(fileName)
    reader.Update()
    
    # Extract polydata if needed (for formats that don't directly produce polydata)
    if extension == '.vtu':
        # Convert unstructured grid to polydata
        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputConnection(reader.GetOutputPort())
        geometryFilter.Update()
        inputForPipeline = geometryFilter.GetOutputPort()
    else:
        inputForPipeline = reader.GetOutputPort()
    
    # Apply smoothing if requested
    if smooth:
        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetInputConnection(inputForPipeline)
        smoother.SetNumberOfIterations(iteration)
        smoother.BoundarySmoothingOff()
        smoother.FeatureEdgeSmoothingOff()
        smoother.SetFeatureAngle(120.0)
        smoother.SetPassBand(passBand)
        smoother.NonManifoldSmoothingOn()
        smoother.NormalizeCoordinatesOn()
        smoother.Update()
        
        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(smoother.GetOutputPort())
        stripper.Update()
        polydata = stripper.GetOutput()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(inputForPipeline)
    else:
        # Get the polydata directly 
        if extension == '.vtu':
            polydata = geometryFilter.GetOutput()
        else:
            polydata = reader.GetOutput()
            
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(inputForPipeline)
        # 2. disable scalar colouring so actor colours take over
        mapper.ScalarVisibilityOff() 
    
    # Create the actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    # Set color
    actor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d(color))
    
    return actor, polydata


"""
##############################################################################
#Func: VTK output 2d surface mesh
##############################################################################
"""
import os.path


def writeMeshFile(
        trianglesData,
        filename,
        binary=True,
        verbose=False
):
    """Write mesh file.
    The output format is determined by file name extension. Files can be written
    in binary (default) and ASCII format."""

    outformat = os.path.splitext(filename)[1].strip('.')
    # set writer based on filename extension
    if outformat == 'stl' or outformat == 'STL':
        write = vtk.vtkSTLWriter()
    elif outformat == 'vtk' or outformat == 'VTK':
        write = vtk.vtkPolyDataWriter()
    elif outformat == 'obj' or outformat == 'OBJ':
        write = vtk.vtkMNIObjectWriter()
    elif outformat == 'tag' or outformat == 'TAG':
        write = vtk.vtkMNITagPointWriter()
    else:
        raise ValueError('cannot write output format: ' + outformat)
    write.SetInputData(trianglesData)

    if outformat != 'tag':
        if binary:
            if verbose: print('setting ouptut to binary')
            write.SetFileTypeToBinary()
        else:
            if verbose: print('setting ouptut to ascii')
            write.SetFileTypeToASCII()

    write.SetFileName(filename)
    err = write.Write()
    if err != 1:
        raise IOError('failed to write')

    if verbose:
        print("wrote", filename)
    pass


"""
##############################################################################
#VTK Create actor with Array input
##############################################################################
"""
import vtk
import numpy


def CreateArrayActor(
        array,
        refernceImage,
        tissueB,
        tissueT,
        smooth=False
):
    # Check input is file or numpy data
    if not isinstance(array, numpy.ndarray):
        raise TypeError("Input file is not numpy.ndarray!!")

    # array to VTK image data
    reader = VTK_Numpy.vtkImageImportFromArray()
    reader.SetArray(imArray=array)
    reader.SetDataSpacing(refernceImage.GetSpacing())
    reader.SetDataOrigin(refernceImage.GetOrigin())
    reader.Update()

    # Thresholding
    selectTissue = vtk.vtkImageThreshold()
    selectTissue.ThresholdBetween(tissueB, tissueT)
    selectTissue.SetInValue(255)
    selectTissue.SetOutValue(0)
    selectTissue.SetInputConnection(reader.GetOutputPort())

    # Gaussian smooth
    smoothing_filter = vtk.vtkImageGaussianSmooth()
    smoothing_filter.SetDimensionality(3)
    smoothing_filter.SetInputConnection(selectTissue.GetOutputPort())
    smoothing_filter.SetStandardDeviations(10.0, 10.0, 10.0)
    smoothing_filter.SetRadiusFactors(10.0, 10.0, 10.0)

    isoValue = 255
    mcubes = vtk.vtkMarchingCubes()
    if smooth:
        mcubes.SetInputConnection(selectTissue.GetOutputPort())
    else:
        mcubes.SetInputConnection(smoothing_filter.GetOutputPort())
    mcubes.ComputeScalarsOff()
    mcubes.ComputeGradientsOff()
    mcubes.ComputeNormalsOn()
    mcubes.SetValue(0, isoValue)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(mcubes.GetOutputPort())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stripper.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


"""
##############################################################################
#VTK Create actor outline with reader input
##############################################################################
"""
import vtk
import numpy


def CreateOutLine(reader):
    # An outline provides context around the data.
    if isinstance(reader, str):
        fileName = reader
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(fileName)
        reader.Update()

    # Set color
    colors = vtk.vtkNamedColors()

    outlineData = vtk.vtkOutlineFilter()
    outlineData.SetInputConnection(reader.GetOutputPort())

    mapOutline = vtk.vtkPolyDataMapper()
    mapOutline.SetInputConnection(outlineData.GetOutputPort())

    outline = vtk.vtkActor()
    outline.SetMapper(mapOutline)
    outline.GetProperty().SetColor(colors.GetColor3d("Black"))

    return outline


"""
##############################################################################
#Func: VTK Create actor scale
##############################################################################
"""
import vtk
import numpy


def CreateAxes(
        iren,
        textProperty=None
):
    # Set color
    colors = vtk.vtkNamedColors()

    # set axes
    axes = vtk.vtkAxesActor()
    widget = vtk.vtkOrientationMarkerWidget()
    widget.SetOrientationMarker(axes)

    ## color shaft
    rgba = [0] * 4
    colors.GetColor('Carrot', rgba)
    widget.SetOutlineColor(rgba[0], rgba[1], rgba[2])
    widget.SetInteractor(iren)
    widget.SetViewport(0.0, 0.0, 0.4, 0.4)
    widget.SetEnabled(1)
    widget.InteractiveOn()

    # set property
    if textProperty is not None:
        axes.GetXAxisCaptionActor2D().SetCaptionTextProperty(textProperty)
        axes.GetYAxisCaptionActor2D().SetCaptionTextProperty(textProperty)
        axes.GetZAxisCaptionActor2D().SetCaptionTextProperty(textProperty)
    else:
        # color text
        textProperty = vtk.vtkTextProperty()
        textProperty.SetFontFamilyToArial()
        textProperty.SetColor(1.0, 0.0, 0.0)
        textProperty.SetFontSize(12)

        axes.GetXAxisCaptionActor2D().SetCaptionTextProperty(textProperty)
        axes.GetYAxisCaptionActor2D().SetCaptionTextProperty(textProperty)
        axes.GetZAxisCaptionActor2D().SetCaptionTextProperty(textProperty)

    return widget


"""
##############################################################################
#VTK Create actor outline with reader input
##############################################################################
"""
import vtk
import numpy


def CreateScale(
        top,
        bottom,
        left,
        right,
        textProperty=None
):
    # create actor
    legendScaleActor = vtk.vtkLegendScaleActor()

    if not bottom:
        legendScaleActor.SetBottomAxisVisibility(0)
    if not top:
        legendScaleActor.SetTopAxisVisibility(0)
    if not right:
        legendScaleActor.SetRightAxisVisibility(0)
    if not left:
        legendScaleActor.SetLeftAxisVisibility(0)

    # text
    if textProperty is not None:
        legendScaleActor.GetLegendLabelProperty().ShallowCopy(textProperty)
        legendScaleActor.GetLegendTitleProperty().ShallowCopy(textProperty)
    else:
        legendScaleActor.GetLegendLabelProperty().SetFontSize(
            legendScaleActor.GetLegendLabelProperty().GetFontSize() * 2)
        legendScaleActor.GetLegendTitleProperty().SetFontSize(
            legendScaleActor.GetLegendTitleProperty().GetFontSize() * 2)

    # offset
    legendScaleActor.GetLegendTitleProperty().SetLineOffset(
        legendScaleActor.GetLegendTitleProperty().GetFontSize() * -1.2 - 10)
    legendScaleActor.GetLegendLabelProperty().SetLineOffset(
        legendScaleActor.GetLegendLabelProperty().GetFontSize() * -1 - 10)

    return legendScaleActor


"""
##############################################################################
#VTK Create message actor with message input
##############################################################################
"""
import vtk
import numpy


def TextActor(Msg, txtProprty=None):
    # VTK Create message actor with message input
    # Set color
    colors = vtk.vtkNamedColors()
    # create a text actor
    txt = vtk.vtkTextActor()
    txt.SetInput(Msg)
    if txtProprty is None:
        txtprop = txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.SetFontSize(18)
        txtprop.SetColor(colors.GetColor3d("Red"))
        # txt.SetDisplayPosition(20,30)
    else:
        txt.SetTextProperty(txtProprty)

    return txt


"""
##############################################################################
#Func: VTK set camera
##############################################################################
"""
import vtk
import numpy


def SetCamera(
        position,
        focalPoint,
        viewUp,
        viewAngle,
        parallelProjection=False
):
    # Create a new camera object
    camera = vtk.vtkCamera()
    # position
    camera.SetPosition(position)
    # FocalPoint
    camera.SetFocalPoint(focalPoint)
    # SetViewUp
    camera.SetViewUp(viewUp)
    # SetViewAngle
    camera.SetViewAngle(viewAngle)
    # parallel
    camera.SetParallelProjection(parallelProjection)

    return camera


"""
##############################################################################
#Func: VTK screen shot
##############################################################################
"""
import vtk
import numpy


def ScreenShot(
        renWin,
        path
):
    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.SetInputBufferTypeToRGB()
    w2if.ReadFrontBufferOff()
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(path)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()

    return


"""
##############################################################################
#VTK Display actors
##############################################################################
"""
import vtk
import numpy
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


def DisplayOverlayNifti(ActFile_Data,
                        ThresUp,
                        ThresBot,
                        opacityChoice,
                        colorChoice,
                        ThresDType=numpy.float64,
                        CaseRef=["No txt"],
                        qt=False,
                        qtFrame=None,
                        qtLayout=None):
    # VTK Display two splited views sharing camera
    # Color
    colors = vtk.vtkNamedColors()  # https://vtk.org/Wiki/VTK/Examples/Cxx/Visualization/NamedColorPatches

    # convert float64 as double
    ThresUp = numpy.array(ThresUp, dtype=ThresDType)
    ThresBot = numpy.array(ThresBot, dtype=ThresDType)

    # create renderer
    aRenderer = vtk.vtkRenderer()

    # Add each actor
    ActFile_Data_Shape = numpy.shape(ActFile_Data)

    for i in range(ActFile_Data_Shape[0]):
        # Actor
        ActThresB = ThresBot[i]

        # Act1ThresB.astype(numpy.float64) #change to double for vtk value
        ActThresT = ThresUp[i]
        # Act1ThresT.astype(numpy.float64) #change to double for vtk value
        strFlg, arrayFlg, ActActor, ActReader, mapper = CreateActor(ActFile_Data[i], ActThresB, ActThresT)
        # set opacity
        ActActor.GetProperty().SetOpacity(opacityChoice[i])
        ActActor.GetProperty().SetColor(colors.GetColor3d(colorChoice[i]))

        # add actor in renderer
        aRenderer.AddActor(ActActor)

        # outline
        if i == 0:
            outlineActor = CreateOutLine(ActReader)
            # add actor in renderer
            aRenderer.AddActor(outlineActor)

    # Txt actor
    # txt
    txtActor = TextActor(CaseRef[0])
    # add actor in renderer
    aRenderer.AddActor(txtActor)

    # Set bkg color
    aRenderer.SetBackground(colors.GetColor3d('Gray'))

    # set rendering window
    if not qt:
        print("qt is False")
    else:
        print(qt)
    if qtFrame is None:
        print("qtFrame is None")
    else:
        print(qtFrame)
    # if qtLayout is None: print("qtLayout is None")
    # else: print(qtLayout)
    if qt and \
            qtFrame is not None and \
            qtLayout is not None:
        # QT VTK Widget
        ## vtk widget
        vtkWidget = QVTKRenderWindowInteractor(qtFrame)
        ## add layout
        qtLayout.addWidget(vtkWidget)
        ## set layout
        qtFrame.setLayout(qtLayout)

        # pipeline
        # add renderer
        vtkWidget.GetRenderWindow().AddRenderer(aRenderer)

        # interactor
        interactor = vtkWidget.GetRenderWindow().GetInteractor()

        # interactor style
        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        # Initialize the event loop and then start it.
        interactor.Initialize()
        interactor.Start()
    else:
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(aRenderer)

        # interacter vtkInteractorStyleTrackballCamera
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        interactor.SetRenderWindow(renWin)

        # Initialize the event loop and then start it.
        interactor.Initialize()
        interactor.Start()


"""
##############################################################################
#VTK Display two splited views sharing camera 
##############################################################################
"""
import vtk
import numpy


def DisplayTwoSeperateNifti(ActFile1_Data1,
                            ActFile2_Data2,
                            ThresUp,
                            ThresBot,
                            ThresDType=numpy.float64,
                            opacityChoice=[1, 1],
                            colorChoice=["Red", "Blue"],
                            CaseRef=["No txt", "No txt"]):
    # VTK Display two splited views sharing camera
    # Color
    colors = vtk.vtkNamedColors()

    # convert float64 as double
    ThresUp = numpy.array(ThresUp, dtype=ThresDType)
    ThresBot = numpy.array(ThresBot, dtype=ThresDType)

    # First
    Act1ThresB = ThresBot[0]
    # Act1ThresB.astype(numpy.float64) #change to double for vtk value
    Act1ThresT = ThresUp[0]
    # Act1ThresT.astype(numpy.float64) #change to double for vtk value
    strFlg1, arrayFlg1, Act1Actor, Act1Reader, mapper1 = CreateActor(ActFile1_Data1, Act1ThresB, Act1ThresT)
    # set opacity
    Act1Actor.GetProperty().SetOpacity(opacityChoice[0])
    Act1Actor.GetProperty().SetColor(colors.GetColor3d(colorChoice[0]))

    # Second
    Act2ThresB = ThresBot[1]
    # Act2ThresB.astype(numpy.float64) #change to double for vtk value
    Act2ThresT = ThresUp[1]
    # Act2ThresT.astype(numpy.float64) #change to double for vtk value
    strFlg2, arrayFlg2, Act2Actor, Act2Reader, mapper2 = CreateActor(ActFile2_Data2, Act2ThresB, Act2ThresT)
    # set opacity
    Act2Actor.GetProperty().SetOpacity(opacityChoice[1])
    Act2Actor.GetProperty().SetColor(colors.GetColor3d(colorChoice[1]))

    # outline
    outlineActor1 = CreateOutLine(Act1Reader, strFlg1, arrayFlg1)
    outlineActor2 = CreateOutLine(Act2Reader, strFlg2, arrayFlg2)

    # Txt actor
    # txt
    txtActor1 = TextActor(CaseRef[0])
    txtActor2 = TextActor(CaseRef[1])

    # Set camera position
    camera = vtk.vtkCamera()
    camera.SetViewUp(0, 0, -1)
    camera.SetPosition(0, 1, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.ComputeViewPlaneNormal()
    camera.Dolly(1.5)

    # Left renderer
    # Create the renderer, the render window, and the interactor. The renderer
    # draws into the render window, the interactor enables mouse- and
    # keyboard-based interaction with the data within the render window.

    # Add actor
    leftRenderer = vtk.vtkRenderer()
    leftRenderer.AddActor(outlineActor1)
    leftRenderer.AddActor(Act1Actor)
    leftRenderer.AddActor(txtActor1)

    # view port
    leftRenderer.SetViewport(0.0, 0.0, 0.5, 1.0)  # xmins[i],ymins[i],xmaxs[i],ymaxs[i]

    # Set bkg color
    leftRenderer.SetBackground(colors.GetColor3d('Gray'))

    # Set same camera to view together
    leftRenderer.SetActiveCamera(camera)

    # Right renderer
    # Create the renderer, the render window, and the interactor. The renderer
    # draws into the render window, the interactor enables mouse- and
    # keyboard-based interaction with the data within the render window.

    # Add actor
    rightRenderer = vtk.vtkRenderer()
    rightRenderer.AddActor(outlineActor2)
    rightRenderer.AddActor(Act2Actor)
    rightRenderer.AddActor(txtActor2)

    # view port
    rightRenderer.SetViewport(0.5, 0.0, 1.0, 1.0)  # xmins[i],ymins[i],xmaxs[i],ymaxs[i]

    # Set bkg color
    rightRenderer.SetBackground(colors.GetColor3d('Gray'))

    # Set same camera to view together
    rightRenderer.SetActiveCamera(camera)

    # create windows to stage renders
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(leftRenderer)
    renWin.AddRenderer(rightRenderer)

    # interacter vtkInteractorStyleTrackballCamera
    interactor = vtk.vtkRenderWindowInteractor()
    # Create an object for the interacter style
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renWin)

    # Initialize the event loop and then start it.
    interactor.Initialize()
    interactor.Start()


"""
##############################################################################
#VTK Interactor Style change threhold
##############################################################################
"""
import vtk


class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None):
        self.AddObserver("MiddleButtonPressEvent", self.middleButtonPressEvent)
        self.AddObserver("MiddleButtonReleaseEvent", self.middleButtonReleaseEvent)

        # Add threshold value
        self.threshold = 0

    def middleButtonPressEvent(self, obj, event):
        print("Middle Button pressed")
        self.threshold = self.threshold + 10
        print(self.threshold)
        self.OnMiddleButtonDown()
        return

    def middleButtonReleaseEvent(self, obj, event):
        print("Middle Button released")
        self.OnMiddleButtonUp()
        return


"""
##############################################################################
#VTK Display actors
##############################################################################
"""
import vtk
import numpy


class DisplayThresNifti:
    def __init__(self, ActFile_Data):
        self.ActFile_Data = ActFile_Data
        # Color
        self.colors = vtk.vtkNamedColors()  # https://vtk.org/Wiki/VTK/Examples/Cxx/Visualization/NamedColorPatches

        # create renderer
        self.aRenderer = vtk.vtkRenderer()

        # create interactor
        self.ActThresB = 400

        # Actor
        # Act1ThresB.astype(numpy.float64) #change to double for vtk value
        self.ActThresT = 800
        # Act1ThresT.astype(numpy.float64) #change to double for vtk value
        strFlg, arrayFlg, self.ActActor, ActReader, self.mapper = CreateActor(self.ActFile_Data, self.ActThresB,
                                                                              self.ActThresT)
        # set opacity
        self.ActActor.GetProperty().SetOpacity(1)
        self.ActActor.GetProperty().SetColor(self.colors.GetColor3d("Red"))

        # add actor in renderer
        self.aRenderer.AddActor(self.ActActor)

        outlineActor = CreateOutLine(ActReader, strFlg, arrayFlg)
        # add actor in renderer
        self.aRenderer.AddActor(outlineActor)

        # Txt actor
        # txt
        self.txtActor = TextActor(str(self.ActThresB) + " Hu to " + str(self.ActThresT) + " Hu")
        # add actor in renderer
        self.aRenderer.AddActor(self.txtActor)

        # Set bkg color
        self.aRenderer.SetBackground(self.colors.GetColor3d('Gray'))

        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.aRenderer)

        # interacter vtkInteractorStyleTrackballCamera
        self.interactor = vtk.vtkRenderWindowInteractor()
        # Create interactor
        self.MyInteractorStyle()
        self.interactor.SetInteractorStyle(self.interactorStyle)
        self.interactor.AddObserver("KeyPressEvent", self.Keypress)
        self.interactor.SetRenderWindow(self.renWin)

        # Initialize the event loop and then start it.
        self.interactor.Initialize()
        self.interactor.Start()

    def MyInteractorStyle(self):
        self.interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        # self.interactorStyle.AddObserver("KeyPressEvent", self.Keypress)

    def Keypress(self, obj, event):
        key = obj.GetKeySym()

        if key == "Up":
            print("Step +20")
            self.ActThresB = self.ActThresB + 50
            print(self.ActThresB)
        elif key == "Down":
            print("Step -20")
            self.ActThresB = self.ActThresB - 50
            print(self.ActThresB)
        elif key == "Right":
            print("Step +100")
            self.ActThresB = self.ActThresB + 100
            print(self.ActThresB)
        elif key == "Left":
            print("Step -100")
            self.ActThresB = self.ActThresB - 100
            print(self.ActThresB)
        if key == "w":
            print("Step +5")
            self.ActThresB = self.ActThresB + 10
            print(self.ActThresB)
        elif key == "s":
            print("Step -20")
            self.ActThresB = self.ActThresB - 10
            print(self.ActThresB)
        elif key == "d":
            print("Step +250")
            self.ActThresB = self.ActThresB + 250
            print(self.ActThresB)
        elif key == "a":
            print("Step -250")
            self.ActThresB = self.ActThresB - 250
            print(self.ActThresB)
        elif key == "i":
            self.ActThresB = float(input("Set Threshold start: "))
            self.ActThresT = float(input("Set Threshold stop: "))

            # update actor
        strFlg, arrayFlg, ActActor, ActReader, self.mapper = CreateActor(self.ActFile_Data, self.ActThresB,
                                                                         self.ActThresT)
        self.ActActor.SetMapper(self.mapper)

        self.txtActor.SetInput(str(self.ActThresB) + " Hu to " + str(self.ActThresT) + " Hu")

        self.interactor.GetRenderWindow().Render()
        return


"""
##############################################################################
#Func: position to points
##############################################################################
"""


def points2actor(xyz, apoint_size, color):
    # initialistion
    points = vtk.vtkPoints()
    # Create the topology of the point (a vertex)
    vertices = vtk.vtkCellArray()
    # Color
    colors = vtk.vtkNamedColors()

    # Add points
    for i in range(0, numpy.shape(xyz)[0]):
        p = xyz[i]
        point_id = points.InsertNextPoint(p)
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(point_id)
    # Create a poly data object
    polydata = vtk.vtkPolyData()
    # Set the points and vertices we created as the geometry and topology of the polydata
    polydata.SetPoints(points)
    polydata.SetVerts(vertices)
    polydata.Modified()
    # Mapper for points
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    # ACTOR for points
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(apoint_size)
    actor.GetProperty().SetColor(colors.GetColor3d(color))

    return actor, polydata

"""
##############################################################################
#Func: polyline actor
##############################################################################
"""

def polyline_actor(xyz, width, color, use_x_color=True):
    """
    Creates a VTK actor representing a polyline with optional x-coordinate coloring.
    
    Args:
        xyz (list): List of 3D points [[x1,y1,z1], [x2,y2,z2], ...]
        width (int): Line width
        color (str): Color name from VTK named colors (used when not using x-coloring)
        use_x_color (bool): When True, colors the line based on x-coordinate values
    
    Returns:
        actor: VTK actor for rendering
        polyData: VTK polydata object
    """
    # Initialization
    colors = vtk.vtkNamedColors()
    points = vtk.vtkPoints()
    polyLine = vtk.vtkPolyLine()
    cells = vtk.vtkCellArray()
    polyData = vtk.vtkPolyData()
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()

    # Create scalar array for x-coordinate values if using x-coloring
    if use_x_color:
        x_scalars = vtk.vtkFloatArray()
        x_scalars.SetName("XCoordinates")
        
    # Add points and collect x values if needed
    for point in xyz:
        # Adding points to the polyline
        points.InsertNextPoint(point)
        
        # Store the x-coordinate as a scalar value for coloring
        if use_x_color:
            x_scalars.InsertNextValue(point[0])  # point[0] is the x-coordinate

    # Set up polyline topology
    polyLine.GetPointIds().SetNumberOfIds(len(xyz))
    for i in range(len(xyz)):
        polyLine.GetPointIds().SetId(i, i)

    # Create a cell array to store the lines and add the polyline
    cells.InsertNextCell(polyLine)

    # Add the points to the dataset
    polyData.SetPoints(points)

    # If using x-coordinate coloring, add the scalars to the polydata
    if use_x_color:
        polyData.GetPointData().SetScalars(x_scalars)

    # Add the lines to the dataset
    polyData.SetLines(cells)

    # Setup the mapper with our polydata
    mapper.SetInputData(polyData)
    
    # Configure color mapping based on the selected mode
    if use_x_color:
        # Find the range of x-coordinates for the color scale
        x_values = [point[0] for point in xyz]
        mapper.SetScalarRange(min(x_values), max(x_values))
        
        # Create a color lookup table to map from x values to colors
        lut = vtk.vtkLookupTable()
        lut.SetHueRange(0.667, 0.0)  # Blue to red color spectrum
        lut.Build()
        
        # Connect the lookup table to the mapper
        mapper.SetLookupTable(lut)
        mapper.SetScalarModeToUsePointData()
        mapper.ScalarVisibilityOn()
    else:
        # Use the specified solid color when not using x-coloring
        actor.GetProperty().SetColor(colors.GetColor3d(color))

    # Set up the actor with our mapper
    actor.SetMapper(mapper)
    actor.GetProperty().SetLineWidth(int(width))

    return actor, polyData

"""
##############################################################################
#Func: image cut volume and resample
##############################################################################
"""


def NIFTIVOIResample(
        file,
        xStart,
        xStop,
        yStart,
        yStop,
        zStart,
        zStop,
        xResampling,
        yResampling,
        zResampling,
        outputNIFTI,
        outPath
):
    # data file
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(file)
    reader.Update()
    vtk_image = reader.GetOutput()
    vtk_image_dim = vtk_image.GetDimensions()

    # spacing correction
    if xStart < 0:
        xStart = 0
    if yStart < 0:
        yStart = 0
    if zStart < 0:
        zStart = 0
    if xStop > vtk_image_dim[0] - 1:
        xStop = vtk_image_dim[0] - 1
    if yStop > vtk_image_dim[1] - 1:
        yStop = vtk_image_dim[1] - 1
    if zStop > vtk_image_dim[2] - 1:
        zStop = vtk_image_dim[2] - 1

    print(
        "Resampling: \n"
        "x: {}-{} y: {}-{} z: {}-{}".format(
            xStart,
            xStop,
            yStart,
            yStop,
            zStart,
            zStop
        )
    )

    # Extract the region of interest.
    voi = vtk.vtkExtractVOI()
    voi.SetInputConnection(reader.GetOutputPort())
    voi.SetVOI(
        int(xStart),
        int(xStop),
        int(yStart),
        int(yStop),
        int(zStart),
        int(zStop)
    )
    # if the SampleRate=(2,2,2), every other point will be selected, resulting in a volume 1/8th the original size.
    print(
        int(xResampling),
        int(yResampling),
        int(zResampling),
    )
    voi.SetSampleRate(
        int(xResampling),
        int(yResampling),
        int(zResampling),
    )
    voi.Update()
    imagedata = voi.GetOutput()

    # save nifti
    if outputNIFTI:
        writer = vtk.vtkNIFTIImageWriter()
        writer.SetInputConnection(voi.GetOutputPort())
        writer.SetFileName(outPath)
        # copy most information directory from the header
        writer.SetNIFTIHeader(reader.GetNIFTIHeader())
        # this information will override the reader's header
        writer.SetQFac(reader.GetQFac())
        writer.SetTimeDimension(reader.GetTimeDimension())
        writer.SetQFormMatrix(reader.GetQFormMatrix())
        writer.SetSFormMatrix(reader.GetSFormMatrix())
        writer.Write()

    return voi, imagedata


"""
##############################################################################
#Func: image cut volume and resample
##############################################################################
"""


def NIFTIVOIReslice(
        file,
        xStart,
        xStop,
        yStart,
        yStop,
        zStart,
        zStop,
        xResampling,
        yResampling,
        zResampling,
        outputNIFTI,
        outPath,
        interp="Nearest"
):
    # data file
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(file)
    reader.Update()
    vtk_image = reader.GetOutput()
    vtk_image_dim = vtk_image.GetDimensions()
    vtk_image_space = vtk_image.GetSpacing()
    vtk_image_origin = vtk_image.GetOrigin()

    # spacing correction
    if xStart < 0:
        xStart = 0
    if yStart < 0:
        yStart = 0
    if zStart < 0:
        zStart = 0
    if xStop > vtk_image_dim[0] - 1:
        xStop = vtk_image_dim[0] - 1
    if yStop > vtk_image_dim[1] - 1:
        yStop = vtk_image_dim[1] - 1
    if zStop > vtk_image_dim[2] - 1:
        zStop = vtk_image_dim[2] - 1

    print(
        "Resampling: \n"
        "x: {}-{} y: {}-{} z: {}-{}".format(
            xStart,
            xStop,
            yStart,
            yStop,
            zStart,
            zStop
        )
    )

    # transformation no change of origin and direction
    axialElement = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]
    resliceAxes = vtk.vtkMatrix4x4()
    resliceAxes.DeepCopy(axialElement)

    # Extract the region of interest.
    voi = vtk.vtkImageReslice()
    voi.SetInputConnection(reader.GetOutputPort())
    voi.SetResliceAxes(resliceAxes)
    voi.Update()

    voi.SetOutputExtent(
        int(xStart * xResampling),
        int(xStop * xResampling),
        int(yStart * yResampling),
        int(yStop * yResampling),
        int(zStart * zResampling),
        int(zStop * zResampling)
    )
    # resampling.
    voi.SetOutputSpacing(
        float(vtk_image_space[0] / xResampling),
        float(vtk_image_space[1] / yResampling),
        float(vtk_image_space[2] / zResampling),
    )
    # origin
    xOri = vtk_image_origin[0] + (xStart) * vtk_image_space[0]
    yOri = vtk_image_origin[1] + (yStart) * vtk_image_space[1]
    zOri = vtk_image_origin[2] + (zStart) * vtk_image_space[2]
    newOri = [-xOri, -yOri, -zOri]
    voi.SetOutputOrigin(vtk_image_origin)

    # set interpolation

    if interp == "Nearest":
        resample = vtk.vtkImageInterpolator()
        resample.SetInterpolationModeToNearest()
        print('Choose interpolation: {}'.format(interp))
    elif interp == "Linear":
        resample = vtk.vtkImageInterpolator()
        resample.SetInterpolationModeToLinear()
        print('Choose interpolation: {}'.format(interp))
    elif interp == "Cubic":
        resample = vtk.vtkImageInterpolator()
        resample.SetInterpolationModeToCubic()
        print('Choose interpolation: {}'.format(interp))
    elif interp == "BSpline":
        resample = vtk.vtkImageBSplineInterpolator()
        print('Choose interpolation: {}'.format(interp))
    elif interp == "Sinc":
        resample = vtk.vtkImageSincInterpolator()
        print('Choose interpolation: {}'.format(interp))
    else:
        print("Resampling cannot find {}. Use Spline!!".format(interp))
        resample = vtk.vtkImageBSplineInterpolator()

    print(resample)
    voi.SetInterpolator(resample)
    voi.SetAutoCropOutput(True)

    # update
    voi.Update()
    imagedata = voi.GetOutput()

    # save nifti
    if outputNIFTI:
        writer = vtk.vtkNIFTIImageWriter()
        writer.SetInputConnection(voi.GetOutputPort())
        writer.SetFileName(outPath)
        # copy most information directory from the header
        writer.SetNIFTIHeader(reader.GetNIFTIHeader())
        # this information will override the reader's header
        writer.SetQFac(reader.GetQFac())
        writer.SetTimeDimension(reader.GetTimeDimension())
        writer.SetQFormMatrix(reader.GetQFormMatrix())
        writer.SetSFormMatrix(reader.GetSFormMatrix())
        writer.Write()

    return voi, imagedata


"""
##############################################################################
#Func: match imagedata and polydata
##############################################################################
"""
import vtk
import numpy
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy
import sklearn.neighbors


def ImagedataMapToPolydata(
        vtk_image,
        ballRadius,
        polydata,
        displayRange,
        rangeStart,
        rangeStop,
        lookUpTable
):
    # sclar data
    scalar_data = vtk_image.GetPointData().GetScalars()

    # get all non-zero points in the image
    imageAllPntVals = numpy.zeros(vtk_image.GetNumberOfPoints())
    imageAllPntCoords = numpy.zeros([vtk_image.GetNumberOfPoints(), 3])
    for point in range(vtk_image.GetNumberOfPoints()):
        if scalar_data.GetValue(point) != 0:
            # set all coordinates
            imageAllPntCoords[point] = vtk_image.GetPoint(point)
            # print('imageAllPntCoords[{}/{}]: {} '.format(point, vtk_image.GetNumberOfPoints(), imageAllPntCoords[point]))

            # set all point values NOT all coordinate have values
            imageAllPntVals[point] = scalar_data.GetValue(point)
            # print('imageAllPntCoords[{}/{}]: {} - {}'.format(
            #     point,
            #     vtk_image.GetNumberOfPoints(),
            #     imageAllPntCoords[point],
            #     imageAllPntVals[point]
            # )
            # )

    # remove zeros
    imagePntValsNonZero = imageAllPntVals[numpy.where(imageAllPntVals != 0)]
    imagePntCoordsNonZero = imageAllPntCoords[numpy.where(imageAllPntVals != 0)]
    # print(
    #     "imagePntValsNonZero shape:{} \nimagePntCoordsNonZero:{}".format(
    #         numpy.shape(imagePntValsNonZero),
    #         numpy.shape(imagePntCoordsNonZero)
    #     )
    # )

    # ball tree find nearest non-zero
    # create ball nearest neighbour
    tree = sklearn.neighbors.BallTree(
        imagePntCoordsNonZero,
        leaf_size=min(222, int(vtk_image.GetNumberOfPoints() / 5))
    )

    # get all points
    points = polydata.GetPoints()
    np_pts = numpy.array([points.GetPoint(i) for i in range(polydata.GetNumberOfPoints())])
    print(
        "np_pts shape:{}".format(
            numpy.shape(np_pts)
        )
    )

    # ball tree match
    (ind, dist) = tree.query_radius(
        np_pts,
        r=ballRadius,
        return_distance=True,
        sort_results=True
    )

    # match points
    # Getting the number of points
    n_pnts_shp = polydata.GetNumberOfPoints()
    # Initializing an array with the right shape
    pnt_data = numpy.zeros(n_pnts_shp)
    for pnt in range(n_pnts_shp):
        # closest indices
        if ind[pnt].size != 0:  # NOT empty array
            pnt_data[pnt] = imagePntValsNonZero[ind[pnt][0]]

    polydata.GetPointData().SetScalars(numpy_to_vtk(pnt_data))

    # Calculate cell normals.
    triangle_cell_normals = vtk.vtkPolyDataNormals()
    triangle_cell_normals.SetInputData(polydata)
    triangle_cell_normals.ComputeCellNormalsOn()
    triangle_cell_normals.ComputePointNormalsOff()
    triangle_cell_normals.ConsistencyOn()
    triangle_cell_normals.AutoOrientNormalsOn()
    triangle_cell_normals.Update()  # Creates vtkPolyData.

    # mapper
    # range
    if displayRange:
        minVal = rangeStart
        maxVal = rangeStop
    else:
        # range
        dataRange = polydata.GetPointData().GetScalars().GetRange()
        minVal = dataRange[0]
        maxVal = dataRange[1]

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(triangle_cell_normals.GetOutputPort())  # this is better for vis-)
    mapper.ScalarVisibilityOn()  # Show colour.
    mapper.SetScalarRange(minVal, maxVal)
    mapper.SetScalarModeToUsePointData()
    mapper.SetLookupTable(lookUpTable)

    # Take the isosurface data and create geometry.
    actor = vtk.vtkLODActor()
    actor.SetNumberOfCloudPoints(100000)
    actor.SetMapper(mapper)

    return actor, polydata


"""
##############################################################################
#Func: save polydata
##############################################################################
"""


def save_polydata(
        polydata,
        file_name,
        binary=False,
        color_array_name=None
):
    # get file extension (type)
    file_extension = file_name.split(".")[-1].lower()

    # todo better generic load
    writer = vtk.vtkPolyDataWriter()
    # todo test all
    if file_extension == "vtk":
        writer = vtk.vtkPolyDataWriter()
    elif file_extension == "vtp":
        writer = vtk.vtkPolyDataWriter()
    elif file_extension == "fib":
        writer = vtk.vtkPolyDataWriter()
    elif file_extension == "ply":
        writer = vtk.vtkPLYWriter()
    elif file_extension == "stl":
        writer = vtk.vtkSTLWriter()
    elif file_extension == "xml":
        writer = vtk.vtkXMLPolyDataWriter()
    elif file_extension == "obj":
        writer = vtk.vtkOBJWriter()

    writer.SetFileName(file_name)
    writer.SetInputData(polydata)
    if color_array_name is not None:
        writer.SetArrayName(color_array_name);

    if binary:
        writer.SetFileTypeToBinary()

    writer.Update()
    writer.Write()


"""
##############################################################################
#Func: look up table
##############################################################################
"""


def LookUpTable(
        rangeStart,
        rangeStop,
        colorNumber=None,
        colorHueStart=None,
        colorHueStop=None,
        colorSaturationStart=None,
        colorSaturationStop=None,
        colorValueStart=None,
        colorValueStop=None,
        colorBelow=None,
        colorAbove=None,
        colorNan=None
):
    # scalar map look up table
    lookUpTable = vtk.vtkLookupTable()
    # colors
    colors = vtk.vtkNamedColors()

    # build table
    lookUpTable.SetTableRange(rangeStart, rangeStop)

    if colorNumber is not None:
        lookUpTable.SetNumberOfColors(colorNumber)
    if colorHueStart is not None and colorHueStop is not None:
        lookUpTable.SetHueRange(colorHueStart, colorHueStop)
    if colorSaturationStart is not None and colorSaturationStop is not None:
        lookUpTable.SetSaturationRange(colorSaturationStart, colorSaturationStop)
    if colorValueStart is not None and colorValueStop is not None:
        lookUpTable.SetValueRange(colorValueStart, colorValueStop)
    if colorBelow is not None:
        lookUpTable.SetBelowRangeColor(colors.GetColor4d(colorBelow))
    if colorAbove is not None:
        lookUpTable.SetAboveRangeColor(colors.GetColor4d(colorAbove))
    if colorNan is not None:
        lookUpTable.SetNanColor(colors.GetColor4d(colorNan))

    lookUpTable.Build()

    return lookUpTable


"""
##############################################################################
#Func: text property
##############################################################################
"""


def TextProperty(
        textColor='black',
        textSize=20,
        textOpacity=None,
        textBold=None,
        textItalic=None,
        textShadow=None
):
    # text property setting
    textProperty = vtk.vtkTextProperty()
    # colors
    colors = vtk.vtkNamedColors()

    # build table
    textProperty.SetColor(colors.GetColor3d(textColor))
    textProperty.SetFontSize(int(textSize))

    if textOpacity is not None:
        textProperty.SetOpacity(float(textOpacity))
    if textBold is not None:
        textProperty.SetBold(bool(textBold))
    if textItalic is not None:
        textProperty.SetItalic(bool(textItalic))
    if textShadow is not None:
        textProperty.SetShadow(bool(textShadow))

    return textProperty


"""
##############################################################################
#Func: delete all actors
##############################################################################
"""


def DeleteALLActors(
        render
):
    # get all render
    actorCollector = render.GetActors()

    # delete all
    for actor in actorCollector:
        render.RemoveActor(actor)
        print('Remove actor: {}'.format(actor))

    return render


"""
##############################################################################
#Class: 3D viewer
##############################################################################
"""
import scipy

class VTK3DView(object):
    def __init__(
            self,
            qt=False,
            qtFrame=None,
            qtLayout=None,
            height=None,
            width=None
    ):
        # color https://vtk.org/doc/nightly/html/classvtkNamedColors.html#details https://www.w3.org/TR/css-color-3/
        # 'Red': ['IndianRed', 'LightCoral', 'Salmon', 'DarkSalmon',
        #         'LightSalmon', 'Red', 'Crimson', 'FireBrick', 'DarkRed'],
        # 'Pink': ['Pink', 'LightPink', 'HotPink', 'DeepPink',
        #          'MediumVioletRed', 'PaleVioletRed'],
        # 'Orange': ['LightSalmon', 'Coral', 'Tomato', 'OrangeRed',
        #            'DarkOrange', 'Orange'],
        # 'Yellow': ['Gold', 'Yellow', 'LightYellow', 'LemonChiffon',
        #            'LightGoldenrodYellow', 'PapayaWhip', 'Moccasin',
        #            'PeachPuff', 'PaleGoldenrod', 'Khaki', 'DarkKhaki'],
        # 'Purple': ['Lavender', 'Thistle', 'Plum', 'Violet', 'Orchid',
        #            'Fuchsia', 'Magenta', 'MediumOrchid', 'MediumPurple',
        #            'BlueViolet', 'DarkViolet', 'DarkOrchid', 'DarkMagenta',
        #            'Purple', 'Indigo', 'DarkSlateBlue', 'SlateBlue',
        #            'MediumSlateBlue'],
        # 'Green': ['GreenYellow', 'Chartreuse', 'LawnGreen', 'Lime',
        #           'LimeGreen', 'PaleGreen', 'LightGreen',
        #           'MediumSpringGreen', 'SpringGreen', 'MediumSeaGreen',
        #           'SeaGreen', 'ForestGreen', 'Green', 'DarkGreen',
        #           'YellowGreen', 'OliveDrab', 'Olive', 'DarkOliveGreen',
        #           'MediumAquamarine', 'DarkSeaGreen', 'LightSeaGreen',
        #           'DarkCyan', 'Teal'],
        # 'Blue/Cyan': ['Aqua', 'Cyan', 'LightCyan', 'PaleTurquoise',
        #               'Aquamarine', 'Turquoise', 'MediumTurquoise',
        #               'DarkTurquoise', 'CadetBlue', 'SteelBlue',
        #               'LightSteelBlue', 'PowderBlue', 'LightBlue',
        #               'SkyBlue', 'LightSkyBlue', 'DeepSkyBlue',
        #               'DodgerBlue', 'CornflowerBlue', 'RoyalBlue', 'Blue',
        #               'MediumBlue', 'DarkBlue', 'Navy', 'MidnightBlue'],
        # 'Brown': ['Cornsilk', 'BlanchedAlmond', 'Bisque', 'NavajoWhite',
        #           'Wheat', 'BurlyWood', 'Tan', 'RosyBrown', 'SandyBrown',
        #           'Goldenrod', 'DarkGoldenrod', 'Peru', 'Chocolate',
        #           'SaddleBrown', 'Sienna', 'Brown', 'Maroon'],
        # 'White': ['White', 'Snow', 'Honeydew', 'MintCream', 'Azure',
        #           'AliceBlue', 'GhostWhite', 'WhiteSmoke', 'Seashell',
        #           'Beige', 'OldLace', 'FloralWhite', 'Ivory',
        #           'AntiqueWhite', 'Linen',
        #           'LavenderBlush', 'MistyRose'],
        # 'Gray': ['Gainsboro', 'LightGrey', 'Silver', 'DarkGray', 'Gray',
        #          'DimGray', 'LightSlateGray', 'SlateGray', 'DarkSlateGray',
        #          'Black']
        # 'Whites': ['antique_white', 'azure', 'bisque', 'blanched_almond',
        #            'cornsilk', 'eggshell', 'floral_white', 'gainsboro',
        #            'ghost_white', 'honeydew', 'ivory', 'lavender',
        #            'lavender_blush', 'lemon_chiffon', 'linen', 'mint_cream',
        #            'misty_rose', 'moccasin', 'navajo_white', 'old_lace',
        #            'papaya_whip', 'peach_puff', 'seashell', 'snow',
        #            'thistle', 'titanium_white', 'wheat', 'white',
        #            'white_smoke', 'zinc_white'],
        # 'Greys': ['cold_grey', 'dim_grey', 'grey', 'light_grey',
        #           'slate_grey', 'slate_grey_dark', 'slate_grey_light',
        #           'warm_grey'],
        # 'Blacks': ['black', 'ivory_black', 'lamp_black'],
        # 'Reds': ['alizarin_crimson', 'brick', 'cadmium_red_deep', 'coral',
        #          'coral_light', 'deep_pink', 'english_red', 'firebrick',
        #          'geranium_lake', 'hot_pink', 'indian_red', 'light_salmon',
        #          'madder_lake_deep', 'maroon', 'pink', 'pink_light',
        #          'raspberry', 'red', 'rose_madder', 'salmon', 'tomato',
        #          'venetian_red'],
        # 'Browns': ['beige', 'brown', 'brown_madder', 'brown_ochre',
        #            'burlywood', 'burnt_sienna', 'burnt_umber', 'chocolate',
        #            'deep_ochre', 'flesh', 'flesh_ochre', 'gold_ochre',
        #            'greenish_umber', 'khaki', 'khaki_dark', 'light_beige',
        #            'peru', 'rosy_brown', 'raw_sienna', 'raw_umber', 'sepia',
        #            'sienna', 'saddle_brown', 'sandy_brown', 'tan',
        #            'van_dyke_brown'],
        # 'Oranges': ['cadmium_orange', 'cadmium_red_light', 'carrot',
        #             'dark_orange', 'mars_orange', 'mars_yellow', 'orange',
        #             'orange_red', 'yellow_ochre'],
        # 'Yellows': ['aureoline_yellow', 'banana', 'cadmium_lemon',
        #             'cadmium_yellow', 'cadmium_yellow_light', 'gold',
        #             'goldenrod', 'goldenrod_dark', 'goldenrod_light',
        #             'goldenrod_pale', 'light_goldenrod', 'melon',
        #             'naples_yellow_deep', 'yellow', 'yellow_light'],
        # 'Greens': ['chartreuse', 'chrome_oxide_green', 'cinnabar_green',
        #            'cobalt_green', 'emerald_green', 'forest_green', 'green',
        #            'green_dark', 'green_pale', 'green_yellow', 'lawn_green',
        #            'lime_green', 'mint', 'olive', 'olive_drab',
        #            'olive_green_dark', 'permanent_green', 'sap_green',
        #            'sea_green', 'sea_green_dark', 'sea_green_medium',
        #            'sea_green_light', 'spring_green', 'spring_green_medium',
        #            'terre_verte', 'viridian_light', 'yellow_green'],
        # 'Cyans': ['aquamarine', 'aquamarine_medium', 'cyan', 'cyan_white',
        #           'turquoise', 'turquoise_dark', 'turquoise_medium',
        #           'turquoise_pale'],
        # 'Blues': ['alice_blue', 'blue', 'blue_light', 'blue_medium',
        #           'cadet', 'cobalt', 'cornflower', 'cerulean', 'dodger_blue',
        #           'indigo', 'manganese_blue', 'midnight_blue', 'navy',
        #           'peacock', 'powder_blue', 'royal_blue', 'slate_blue',
        #           'slate_blue_dark', 'slate_blue_light',
        #           'slate_blue_medium', 'sky_blue', 'sky_blue_deep',
        #           'sky_blue_light', 'steel_blue', 'steel_blue_light',
        #           'turquoise_blue', 'ultramarine'],
        # 'Magentas': ['blue_violet', 'cobalt_violet_deep', 'magenta',
        #              'orchid', 'orchid_dark', 'orchid_medium',
        #              'permanent_red_violet', 'plum', 'purple',
        #              'purple_medium', 'ultramarine_violet', 'violet',
        #              'violet_dark', 'violet_red', 'violet_red_medium',
        #              'violet_red_pale']
        self.colors = vtk.vtkNamedColors()

        # Renderer
        self.renderer = vtk.vtkRenderer()

        # Render Window
        if qt and \
                qtFrame is not None and \
                qtLayout is not None:
            # QT VTK Widget
            ## vtk widget
            vtkWidget = QVTKRenderWindowInteractor(qtFrame)
            ## add layout
            qtLayout.addWidget(vtkWidget)
            ## set layout
            qtFrame.setLayout(qtLayout)

            # Render Window
            self.renderWindow = vtkWidget.GetRenderWindow()
            # interactor style setting
            self.interactor = vtkWidget.GetRenderWindow().GetInteractor()
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        else:
            self.renderWindow = vtk.vtkRenderWindow()
            self.renderWindow.SetSize(height, width)

            # interactor style setting
            self.interactor = vtk.vtkRenderWindowInteractor()
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
            self.interactor.SetRenderWindow(self.renderWindow)

        # message
        self.message = ""

        # camera info
        self.cameraInfo = {}

        # widget to use
        self.scalar_bar_widget = None
        self.axes_widget = None
        self.planeWidgetX = None
        self.planeWidgetY = None
        self.planeWidgetZ = None

    def Initiate(self):
        # add renderer
        self.renderWindow.AddRenderer(self.renderer)

        # need to update the add-on widget
        if self.scalar_bar_widget is not None:
            self.scalar_bar_widget.On()
        if self.axes_widget is not None:
            self.axes_widget.On()
        if self.planeWidgetX is not None:
            self.planeWidgetX.On()
        if self.planeWidgetY is not None:
            self.planeWidgetY.On()
        if self.planeWidgetZ is not None:
            self.planeWidgetZ.On()

        # Initialize the event loop and then start it.
        self.interactor.Initialize()
        self.interactor.Start()

    def OffScreenRnder(self):
        # add renderer
        self.renderWindow.AddRenderer(self.renderer)

        # off screen rendering
        self.renderWindow.OffScreenRenderingOn()
        self.renderWindow.Render()

    def VolumeRendering(
            self,
            files,
            transparencies,
            colors,
            smoothChoices,
            iterations,
            passBands,
            output2DMeshes,
            out2DMeshPaths,
            showEdges,
            bottoms=[],
            tops=[]
    ):
        # message
        self.message = 'Working in Volume Rendering: \n'
        # check same length
        checkList = Post_Image_Process_Functions.CompareListDimension(
            lsts=[
                files,
                transparencies,
                colors,
                smoothChoices,
                iterations,
                passBands,
                output2DMeshes,
                showEdges
            ]
        )
        if checkList["error"]:
            # message
            self.message += checkList["errorMessage"] + "\n"
            print(self.message)
            return

        # loop
        for item in range(len(files)):
            # each item
            file = files[item]
            transparency = transparencies[item]
            color = colors[item]
            showEdge = showEdges[item]
            smoothChoice = smoothChoices[item]
            iteration = iterations[item]
            passBand = passBands[item]
            output2DMesh = output2DMeshes[item]
            if len(out2DMeshPaths) == 1:
                out2DMeshPath = out2DMeshPaths[0]
            else:
                out2DMeshPath = out2DMeshPaths[item]

            # file type
            extension = Save_Load_File.ExtensionFromPath(
                fullPath=file
            )

            # nifti reader
            actor = None
            if extension == ".nii.gz":
                actor, polydata = CreateNiftiActor(
                    fileName=file,
                    tissueB=bottoms[item],
                    tissueT=tops[item],
                    smooth=smoothChoice,
                    iteration=iteration,
                    passBand=passBand,
                    color=color,
                )
            elif extension in [".vtk", ".vtp", ".fib", ".ply", ".stl", ".xml", ".obj"]:
                actor, polydata = CreateSTLActor(
                    fileName=file,
                    smooth=smoothChoice,
                    iteration=iteration,
                    passBand=passBand,
                    color=color,
                )
            else:
                # message
                self.message += 'Unsupport extension: {}'.format(extension) + "\n"
                print(self.message)
                return

            if output2DMesh:
                writeMeshFile(
                    trianglesData=polydata,
                    filename=out2DMeshPath,
                    binary=True,
                    verbose=True
                )

            # set property
            print(f'find color: {color}, vtk color: {self.colors.GetColor3d(color)}')
            actorProperty = vtk.vtkProperty()
            actorProperty.SetOpacity(float(transparency))
            actorProperty.SetColor(self.colors.GetColor3d(color))
            actorProperty.SetEdgeVisibility(bool(showEdge))
            actor.SetProperty(actorProperty)

            # add renderer actor
            self.renderer.AddActor(actor)

            # message
            self.message += 'Pure volume rendering: {}'.format(file) + "\n"

    def Points3D(
            self,
            files,
            filters,
            threStarts,
            threStops,
            pointSizes,
            colors
    ):
        # message
        self.message = 'Working in 3D Points:'
        # check same length
        checkList = Post_Image_Process_Functions.CompareListDimension(
            lsts=[
                files,
                filters,
                threStarts,
                threStops,
                pointSizes,
                colors
            ]
        )
        if checkList["error"]:
            # message
            self.message += checkList["errorMessage"] + "\n"
            return

        # loop
        for item in range(len(files)):
            # each item
            file = files[item]
            filterChoice = filters[item]
            threStart = threStarts[item]
            threStop = threStops[item]
            pointSize = pointSizes[item]
            color = colors[item]

            # load file
            mask = Save_Load_File.OpenLoadNIFTI(
                GUI=False,
                filePath=file
            )

            # spacing
            spacing = numpy.diag(numpy.asarray(mask.OriImag.GetSpacing()))

            # mask filter
            maskXYZ = SITK_Numpy.SITK_NP_Arr()
            maskXYZ.InSITKArr(SITKArr=mask.OriData)
            maskXYZ.PositionMaskValues(
                value=[threStart],
                valueEnd=[threStop],
                compare=filterChoice
            )
            maskXYZ.PositionXYZ()
            maskXYZ.Actual3DCoors(inSpace=spacing)

            # add actor
            actor, polydata = points2actor(
                xyz=maskXYZ.Actual3DCoors,
                apoint_size=pointSize,
                color=color
            )

            # add renderer
            self.renderer.AddActor(actor)

            # message
            self.message += '3D point rendering: {}'.format(file) + "\n"

    def Lines3D(
            self,
            files,
            factorFile,
            filters,
            threStarts,
            threStops,
            widths,
            colors,
            smoothChoices,
            smoothResamples
    ):
        # message
        self.message = 'Working in 3D lines:'

        # check same length
        checkList = Post_Image_Process_Functions.CompareListDimension(
            lsts=[
                files,
                filters,
                threStarts,
                threStops,
                widths,
                colors,
                smoothChoices,
                smoothResamples
            ]
        )
        if checkList["error"]:
            # message
            self.message += checkList["errorMessage"] + "\n"
            return

        # loop
        for item in range(len(files)):
            # each item
            file = files[item]
            filterChoice = filters[item]
            threStart = threStarts[item]
            threStop = threStops[item]
            width = widths[item]
            color = colors[item]
            smoothChoice = smoothChoices[item]
            smoothResample = smoothResamples[item]

            # table or nifti
            if '.nii.gz' in file:
                # load file
                mask = Save_Load_File.OpenLoadNIFTI(
                    GUI=False,
                    filePath=file
                )

                # spacing
                spacing = numpy.diag(numpy.asarray(mask.OriImag.GetSpacing()))

                # mask filter
                maskXYZ = SITK_Numpy.SITK_NP_Arr()
                maskXYZ.InSITKArr(SITKArr=mask.OriData)
                maskXYZ.PositionMaskValues(
                    value=[threStart],
                    valueEnd=[threStop],
                    compare=filterChoice
                )
                maskXYZ.PositionXYZ()
                maskXYZ.Actual3DCoors(inSpace=spacing)

                # single line connection
                orderCoors = Image_Process_Functions.ConnectSingleLine(
                    coordinates=maskXYZ.Actual3DCoors
                )

                # smoothing
                if smoothChoice:
                    # remove repeated points
                    # using list comprehension
                    # to remove duplicated
                    # from list
                    res = []
                    # [res.append(x) for x in Coors_XYZ if x not in res]
                    [res.append(list(x)) for x in orderCoors if list(x) not in res]

                    # make to xx, yy, zz
                    coorLen = len(res)
                    xx = numpy.zeros(coorLen)
                    yy = numpy.zeros(coorLen)
                    zz = numpy.zeros(coorLen)

                    for i in range(coorLen):
                        xx[i] = res[i][0]
                        yy[i] = res[i][1]
                        zz[i] = res[i][2]

                    # spline 3D
                    tck, u = scipy.interpolate.splprep([xx, yy, zz], s=3, t=5)
                    x_knots, y_knots, z_knots = scipy.interpolate.splev(tck[0], tck)
                    u_fine = numpy.linspace(0, 1, smoothResample)
                    x_fine, y_fine, z_fine = scipy.interpolate.splev(u_fine, tck)

                    # xx, yy, zz to list [[x, y, z], ..]
                    smoothLen = len(x_fine)
                    smoothCoors = [None] * smoothLen
                    for i in range(smoothLen):
                        smoothCoors[i] = [x_fine[i], y_fine[i], z_fine[i]]

                    # actual 3d coords
                    use3DCoors = smoothCoors
                else:
                    use3DCoors = orderCoors

                # add actor
                actor, polydata = polyline_actor(
                    xyz=use3DCoors,
                    width=width,
                    color=color
                )

            else:
                # load DFs
                factorDF = Pd_Funs.OpenDF(
                            inPath=factorFile,
                            header=0
                        )

                coordDF = Pd_Funs.OpenDF(
                    inPath=file,
                    header=0
                )

                # Get coordinates and convert to numpy array
                Coors_XYZ = coordDF.values

                # Get factors with the same number of rows as coordinates
                # If factors has fewer rows, repeat the last row to match
                factorArray = factorDF.values
                if len(factorArray) < len(Coors_XYZ):
                    # Pad with repeats of the last row
                    padding = numpy.repeat(factorArray[-1:], len(Coors_XYZ) - len(factorArray), axis=0)
                    factorArray = numpy.vstack([factorArray, padding])
                elif len(factorArray) > len(Coors_XYZ):
                    # Truncate to match coordinate length
                    factorArray = factorArray[:len(Coors_XYZ)]

                # Apply element-wise multiplication directly
                # This multiplies each x,y,z with its corresponding factor
                Actual3DCoors_temp = Coors_XYZ * factorArray

                # Convert back to list format if needed for downstream operations
                Actual3DCoors = Actual3DCoors_temp.tolist()

                print(Actual3DCoors)

                # # single line connection
                # orderCoors = Image_Process_Functions.ConnectSingleLine(
                #     coordinates=Actual3DCoors
                # )
                # print(orderCoors)

                # smoothing
                if smoothChoice:
                    # remove repeated points
                    # using list comprehension
                    # to remove duplicated
                    # from list
                    res = []
                    # [res.append(x) for x in Coors_XYZ if x not in res]
                    [res.append(list(x)) for x in Actual3DCoors if list(x) not in res]

                    # make to xx, yy, zz
                    coorLen = len(res)
                    xx = numpy.zeros(coorLen)
                    yy = numpy.zeros(coorLen)
                    zz = numpy.zeros(coorLen)

                    for i in range(coorLen):
                        xx[i] = res[i][0]
                        yy[i] = res[i][1]
                        zz[i] = res[i][2]

                    # spline 3D
                    tck, u = scipy.interpolate.splprep([xx, yy, zz], s=3, t=5)
                    x_knots, y_knots, z_knots = scipy.interpolate.splev(tck[0], tck)
                    u_fine = numpy.linspace(0, 1, smoothResample)
                    x_fine, y_fine, z_fine = scipy.interpolate.splev(u_fine, tck)

                    # xx, yy, zz to list [[x, y, z], ..]
                    smoothLen = len(x_fine)
                    smoothCoors = [None] * smoothLen
                    for i in range(smoothLen):
                        smoothCoors[i] = [x_fine[i], y_fine[i], z_fine[i]]

                    # actual 3d coords
                    use3DCoors = smoothCoors

                else:
                    use3DCoors = Actual3DCoors

                print(use3DCoors)

                # add actor
                actor, polydata = polyline_actor(
                    xyz=use3DCoors,
                    width=width,
                    color=color
                )

            # add renderer
            self.renderer.AddActor(actor)

            # message
            self.message += '3D line rendering: {}'.format(file) + "\n"

    def ResultsRendering(
            self,
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
    ):
        # message
        self.message = 'Working in results rendering: \n'
        # check same length
        checkList = Post_Image_Process_Functions.CompareListDimension(
            lsts=[
                volumeFiles,
                referenceFiles
            ]
        )
        if checkList["error"]:
            # message
            self.message += checkList["errorMessage"] + "\n"
            return

        # loop
        for item in range(len(volumeFiles)):
            # each item
            volumeFile = volumeFiles[item]
            referenceFile = referenceFiles[item]
            ballRadius = ballRadii[item]
            saveChoice = saveChoices[item]
            vtkPath = vtkPaths[item]
            smoothChoice = smoothChoices[item]
            iteration = iterations[item]
            passBand = passBands[item]
            output2DMesh = output2DMeshes[item]
            out2DMeshPath = out2DMeshPaths[item]

            # volume cut of the reference data
            if volumeCut:
                _, imagedata = NIFTIVOIReslice(
                    file=referenceFile,
                    xStart=xStarts[item],
                    xStop=xStops[item],
                    yStart=yStarts[item],
                    yStop=yStops[item],
                    zStart=zStarts[item],
                    zStop=zStops[item],
                    xResampling=xResamplings[item],
                    yResampling=yResamplings[item],
                    zResampling=zResamplings[item],
                    outputNIFTI=outputNIFTIs[item],
                    outPath=outPaths[item],
                    interp=interp
                )
            else:
                # nifti reader
                reader = vtk.vtkNIFTIImageReader()
                reader.SetFileName(referenceFile)
                reader.Update()
                imagedata = reader.GetOutput()

            # file type
            extension = Save_Load_File.ExtensionFromPath(
                fullPath=volumeFile
            )

            # load surface mesh
            polydata = None
            if extension == ".nii.gz":
                _, polydata = CreateNiftiActor(
                    fileName=volumeFile,
                    tissueB=bottoms[item],
                    tissueT=tops[item],
                    smooth=smoothChoice,
                    iteration=iteration,
                    passBand=passBand,
                )
            elif extension in [".stl", ".obj", ".ply", ".vtk", ".vtp", "vtu"]:
                _, polydata = CreateSTLActor(
                    fileName=volumeFile,
                    smooth=smoothChoice,
                    iteration=iteration,
                    passBand=passBand
                )
            else:
                # message
                self.message += 'Unsupport extension: {}'.format(extension) + "\n"
                print(self.message)
                return

            # output 2D mesh
            if output2DMesh:
                writeMeshFile(
                    trianglesData=polydata,
                    filename=out2DMeshPath,
                    binary=True,
                    verbose=True
                )

            # scalar map look up table
            if colorMap:
                lookUpTable = LookUpTable(
                    rangeStart=rangeStarts[item],
                    rangeStop=rangeStops[item],
                    colorNumber=colorNumbers[item],
                    colorHueStart=colorHueStarts[item],
                    colorHueStop=colorHueStops[item],
                    colorSaturationStart=colorSaturationStarts[item],
                    colorSaturationStop=colorSaturationStops[item],
                    colorValueStart=colorValueStarts[item],
                    colorValueStop=colorValueStops[item],
                    colorBelow=colorBelows[item],
                    colorAbove=colorAboves[item],
                    colorNan=colorNans[item]
                )
            else:
                # scalar range
                dataRange = imagedata.GetPointData().GetScalars().GetRange()
                minVal = dataRange[0]
                maxVal = dataRange[1]

                lookUpTable = LookUpTable(
                    rangeStart=minVal,
                    rangeStop=maxVal,
                    colorNumber=36,
                    colorHueStart=0.667,
                    colorHueStop=0.0,
                    colorSaturationStart=None,
                    colorSaturationStop=None,
                    colorValueStart=None,
                    colorValueStop=None,
                    colorBelow='Purple',
                    colorAbove='Magenta',
                    colorNan='grey'
                )

            # map image results to polydata
            actor, mapPolydata = ImagedataMapToPolydata(
                vtk_image=imagedata,
                ballRadius=ballRadius,
                polydata=polydata,
                displayRange=displayRange,
                rangeStart=rangeStarts[item],
                rangeStop=rangeStops[item],
                lookUpTable=lookUpTable
            )

            # save and output
            if saveChoice:
                save_polydata(
                    polydata=mapPolydata,
                    file_name=vtkPath,
                    binary=False,
                    color_array_name=None
                )

            # add renderer actor
            self.renderer.AddActor(actor)

            # text property setting
            if text:
                textProperty = TextProperty(
                    textColor=textColor,
                    textSize=textSize,
                    textOpacity=textOpacity,
                    textBold=textBold,
                    textItalic=textItalic,
                    textShadow=textShadow
                )
            else:
                textProperty = TextProperty(
                    textColor='black',
                    textSize=30,
                    textOpacity=1,
                    textBold=False,
                    textItalic=False,
                    textShadow=False
                )

            # scalar bar
            scalar_bar = vtk.vtkScalarBarActor()
            scalar_bar.SetOrientationToVertical()
            scalar_bar.SetLookupTable(lookUpTable)
            scalar_bar.DrawTickLabelsOn()
            scalar_bar.SetTextPad(5)
            scalar_bar.SetUnconstrainedFontSize(True)
            scalar_bar.SetLabelFormat("%.2f")
            scalar_bar.SetLabelTextProperty(textProperty)
            scalar_bar.SetTitleTextProperty(textProperty)
            scalar_bar.SetFixedAnnotationLeaderLineColor(50)
            scalar_bar.FixedAnnotationLeaderLineColorOn()
            scalar_bar.DrawAnnotationsOn()

            if scalarBar:
                scalar_bar.SetMaximumWidthInPixels(int(scalarWidths[item]))
                scalar_bar.SetMaximumNumberOfColors(scalarMaxNumColors[item])
                scalar_bar.SetNumberOfLabels(scalarNumLbls[item])
                scalar_bar.SetTitle(scalarTitles[item])
                scalar_bar.SetVerticalTitleSeparation(int(scalarVeticalTitleSpaces[item]))
            else:
                scalar_bar.SetMaximumWidthInPixels(80)
                scalar_bar.SetMaximumNumberOfColors(11)
                scalar_bar.SetNumberOfLabels(12)
                scalar_bar.SetTitle("")
                scalar_bar.SetVerticalTitleSeparation(5)

            # create the scalar_bar_widget
            if scalarBar:
                self.scalar_bar_widget = vtk.vtkScalarBarWidget()
                self.scalar_bar_widget.SetInteractor(self.interactor)
                self.scalar_bar_widget.SetScalarBarActor(scalar_bar)
                # self.scalar_bar_widget.On()

            # message
            self.message += 'Map results rendering: {}'.format(referenceFile) + "\n"

    def SlicingImage(
            self,
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
    ):
        # message
        self.message = 'Working in 3D slicing: \n'

        # loop
        for item in range(len(imageFiles)):
            # each item
            imageFile = imageFiles[item]

            # volume cut of the reference data
            if volumeCut:
                reader, imagedata = NIFTIVOIReslice(
                    file=imageFile,
                    xStart=xStarts[item],
                    xStop=xStops[item],
                    yStart=yStarts[item],
                    yStop=yStops[item],
                    zStart=zStarts[item],
                    zStop=zStops[item],
                    xResampling=xResamplings[item],
                    yResampling=yResamplings[item],
                    zResampling=zResamplings[item],
                    outputNIFTI=outputNIFTIs[item],
                    outPath=outPaths[item],
                    interp=interp,
                )
            else:
                # nifti reader
                reader = vtk.vtkNIFTIImageReader()
                reader.SetFileName(imageFile)
                reader.Update()

            # range
            if displayRange:
                minVal = rangeStarts[item]
                maxVal = rangeStops[item]
            else:
                # scalar range
                dataRange = reader.GetOutput().GetPointData().GetScalars().GetRange()
                minVal = dataRange[0]
                maxVal = dataRange[1]

            # look up table
            # print(minVal, maxVal)
            if colorMap:
                lookUpTable = LookUpTable(
                    rangeStart=minVal,
                    rangeStop=maxVal,
                    colorNumber=colorNumbers[item],
                    colorHueStart=colorHueStarts[item],
                    colorHueStop=colorHueStops[item],
                    colorSaturationStart=colorSaturationStarts[item],
                    colorSaturationStop=colorSaturationStops[item],
                    colorValueStart=colorValueStarts[item],
                    colorValueStop=colorValueStops[item],
                    colorBelow=colorBelows[item],
                    colorAbove=colorAboves[item],
                    colorNan=colorNans[item]
                )
                print(colorAboves[item])
            else:
                lookUpTable = LookUpTable(
                    rangeStart=minVal,
                    rangeStop=maxVal,
                    colorNumber=None,
                    colorHueStart=0,
                    colorHueStop=0,
                    colorSaturationStart=0,
                    colorSaturationStop=0,
                    colorValueStart=0,
                    colorValueStop=1,
                    colorBelow=None,
                    colorAbove=None,
                    colorNan=None
                )

            # image setting
            sagittal_colors = vtk.vtkImageMapToColors()
            sagittal_colors.SetInputConnection(reader.GetOutputPort())
            sagittal_colors.SetLookupTable(lookUpTable)
            sagittal_colors.Update()

            # fixed slices position
            if fixedSlice:
                for xStartSlice, \
                    xStopSlice, \
                    yStartSlice, \
                    yStopSlice, \
                    zStartSlice, \
                    zStopSlice \
                        in zip(
                    xStartSlices,
                    xStopSlices,
                    yStartSlices,
                    yStopSlices,
                    zStartSlices,
                    zStopSlices
                ):
                    # image actor
                    medicalImageActor = vtk.vtkImageActor()
                    medicalImageActor.GetMapper().SetInputConnection(sagittal_colors.GetOutputPort())
                    medicalImageActor.SetDisplayExtent(
                        xStartSlice,
                        xStopSlice,
                        yStartSlice,
                        yStopSlice,
                        zStartSlice,
                        zStopSlice
                    )
                    medicalImageActor.ForceOpaqueOn()

                    # renderer add actor
                    self.renderer.AddActor(medicalImageActor)

            # uniform
            if uniformSlice:
                # extent
                xExt = reader.GetOutput().GetDimensions()[0]
                yExt = reader.GetOutput().GetDimensions()[1]
                zExt = reader.GetOutput().GetDimensions()[2]
                if directX:
                    for xstep in range(0, xExt, xStartSlices[0]):
                        # image actor
                        medicalImageActor = vtk.vtkImageActor()
                        medicalImageActor.GetMapper().SetInputConnection(sagittal_colors.GetOutputPort())
                        print(xstep,
                              xstep,
                              0,
                              yExt,
                              0,
                              zExt)
                        medicalImageActor.SetDisplayExtent(
                            xstep,
                            xstep,
                            0,
                            yExt,
                            0,
                            zExt
                        )
                        medicalImageActor.ForceOpaqueOn()
                        # renderer add actor
                        self.renderer.AddActor(medicalImageActor)

                if directY:
                    for ystep in range(0, yExt, yStartSlices[0]):
                        # image actor
                        medicalImageActor = vtk.vtkImageActor()
                        medicalImageActor.GetMapper().SetInputConnection(sagittal_colors.GetOutputPort())
                        medicalImageActor.SetDisplayExtent(
                            0,
                            xExt,
                            ystep,
                            ystep,
                            0,
                            zExt
                        )
                        medicalImageActor.ForceOpaqueOn()
                        # renderer add actor
                        self.renderer.AddActor(medicalImageActor)

                if directZ:
                    for zstep in range(0, zExt, zStartSlices[0]):
                        # image actor
                        medicalImageActor = vtk.vtkImageActor()
                        medicalImageActor.GetMapper().SetInputConnection(sagittal_colors.GetOutputPort())
                        medicalImageActor.SetDisplayExtent(
                            0,
                            xExt,
                            0,
                            yExt,
                            zstep,
                            zstep
                        )
                        medicalImageActor.ForceOpaqueOn()
                        # renderer add actor
                        self.renderer.AddActor(medicalImageActor)

            if slide3D:
                # text property setting
                if text:
                    textProperty = TextProperty(
                        textColor=textColor,
                        textSize=textSize,
                        textOpacity=textOpacity,
                        textBold=textBold,
                        textItalic=textItalic,
                        textShadow=textShadow
                    )
                else:
                    textProperty = TextProperty(
                        textColor='black',
                        textSize=30,
                        textOpacity=1,
                        textBold=False,
                        textItalic=False,
                        textShadow=False
                    )

                if directX:
                    # relicing plane
                    self.planeWidgetX = vtk.vtkImagePlaneWidget()
                    self.planeWidgetX.DisplayTextOn()
                    self.planeWidgetX.SetResliceInterpolateToCubic()
                    self.planeWidgetX.SetInteractor(self.interactor)
                    self.planeWidgetX.SetInputConnection(sagittal_colors.GetOutputPort())
                    self.planeWidgetX.SetPlaneOrientationToXAxes()
                    self.planeWidgetX.SetTextProperty(textProperty)
                    # self.planeWidgetX.On()

                if directY:
                    # relicing plane
                    self.planeWidgetY = vtk.vtkImagePlaneWidget()
                    self.planeWidgetY.DisplayTextOn()
                    self.planeWidgetY.SetResliceInterpolateToCubic()
                    self.planeWidgetY.SetInteractor(self.interactor)
                    self.planeWidgetY.SetInputConnection(sagittal_colors.GetOutputPort())
                    self.planeWidgetY.SetPlaneOrientationToYAxes()
                    self.planeWidgetY.SetTextProperty(textProperty)
                    # self.planeWidgetY.On()

                if directZ:
                    # relicing plane
                    self.planeWidgetZ = vtk.vtkImagePlaneWidget()
                    self.planeWidgetZ.DisplayTextOn()
                    self.planeWidgetZ.SetResliceInterpolateToCubic()
                    self.planeWidgetZ.SetInteractor(self.interactor)
                    self.planeWidgetZ.SetInputConnection(sagittal_colors.GetOutputPort())
                    self.planeWidgetZ.SetPlaneOrientationToZAxes()
                    self.planeWidgetZ.SetTextProperty(textProperty)
                    # self.planeWidgetZ.On()

    def DisplayText(
            self,
            msg,
            textSize,
            textColor,
            textOpacity,
            textBold,
            textItalic,
            textShadow
    ):
        # property
        textProperty = TextProperty(
            textColor=textColor,
            textSize=textSize,
            textOpacity=textOpacity,
            textBold=textBold,
            textItalic=textItalic,
            textShadow=textShadow
        )

        # actor
        actor = TextActor(msg, txtProprty=textProperty)

        self.renderer.AddActor(actor)

    def Background(self, color):
        # set color
        self.renderer.SetBackground(self.colors.GetColor3d(color))

    def Outline(self, file):
        # outline
        outline = CreateOutLine(file)
        self.renderer.AddActor(outline)

    def ScaleBar(
            self,
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
    ):

        # text property
        # property
        textProperty = TextProperty(
            textColor=textColor,
            textSize=textSize,
            textOpacity=textOpacity,
            textBold=textBold,
            textItalic=textItalic,
            textShadow=textShadow
        )

        # actor
        actor = CreateScale(
            top,
            bottom,
            left,
            right,
            textProperty=textProperty
        )

        self.renderer.AddActor(actor)

    def Axes(
            self,
            textSize,
            textColor,
            textOpacity,
            textBold,
            textItalic,
            textShadow
    ):

        # text property
        # property
        textProperty = TextProperty(
            textColor=textColor,
            textSize=textSize,
            textOpacity=textOpacity,
            textBold=textBold,
            textItalic=textItalic,
            textShadow=textShadow
        )

        # actor
        self.axes_widget = CreateAxes(
            iren=self.interactor,
            textProperty=textProperty
        )

    def SetCamera(
            self,
            autoSet,
            parallelProjection,
            position,
            focalPoint,
            viewUp,
            viewAngle
    ):
        if autoSet:
            self.renderer.ResetCamera()
            self.renderer.ResetCameraClippingRange()

        else:
            # set camera
            camera = SetCamera(
                position,
                focalPoint,
                viewUp,
                viewAngle,
                parallelProjection
            )

            # set renderer
            self.renderer.SetActiveCamera(camera)
            self.renderer.ResetCameraClippingRange()

    def GetCamera(self):
        # camera
        camera = self.renderer.GetActiveCamera()

        # dict
        self.cameraInfo['position'] = camera.GetPosition()
        self.cameraInfo['focalPoint'] = camera.GetFocalPoint()
        self.cameraInfo['viewUp'] = camera.GetViewUp()
        self.cameraInfo['viewAngle'] = camera.GetViewAngle()

    def ScreenShot(
            self,
            path
    ):

        ScreenShot(
            renWin=self.renderWindow,
            path=path
        )

    def ClearRenderer(self):
        # close rendering
        self.renderWindow.OffScreenRenderingOff()

        DeleteALLActors(self.renderer)