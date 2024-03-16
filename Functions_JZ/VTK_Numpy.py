"""
##############################################################################
#Convert numpy array yo VTK vtkImageData
##############################################################################
"""
import vtk


class vtkImageImportFromArray:
    def __init__(self):
        self.__import = vtk.vtkImageImport()
        self.__ConvertIntToUnsignedShort = False
        self.__Array = None

    # type dictionary: note that python doesn't support
    # unsigned integers properly!
    __typeDict = {'b': vtk.VTK_SIGNED_CHAR,  # int8
                  'B': vtk.VTK_UNSIGNED_CHAR,  # uint8
                  'h': vtk.VTK_SHORT,  # int16
                  'H': vtk.VTK_UNSIGNED_SHORT,  # uint16
                  'i': vtk.VTK_INT,  # int32
                  'I': vtk.VTK_UNSIGNED_INT,  # uint32
                  'f': vtk.VTK_FLOAT,  # float32
                  'd': vtk.VTK_DOUBLE,  # float64
                  'F': vtk.VTK_FLOAT,  # float32
                  'D': vtk.VTK_DOUBLE,  # float64
                  }

    __sizeDict = {vtk.VTK_SIGNED_CHAR: 1,
                  vtk.VTK_UNSIGNED_CHAR: 1,
                  vtk.VTK_SHORT: 2,
                  vtk.VTK_UNSIGNED_SHORT: 2,
                  vtk.VTK_INT: 4,
                  vtk.VTK_UNSIGNED_INT: 4,
                  vtk.VTK_FLOAT: 4,
                  vtk.VTK_DOUBLE: 8}

    # convert 'Int32' to 'unsigned short'
    def SetConvertIntToUnsignedShort(self, yesno):
        self.__ConvertIntToUnsignedShort = yesno

    def GetConvertIntToUnsignedShort(self):
        return self.__ConvertIntToUnsignedShort

    def ConvertIntToUnsignedShortOn(self):
        self.__ConvertIntToUnsignedShort = True

    def ConvertIntToUnsignedShortOff(self):
        self.__ConvertIntToUnsignedShort = False

    def Update(self):
        self.__import.Update()

    # get the output
    def GetOutputPort(self):
        return self.__import.GetOutputPort()

    # get the output
    def GetOutput(self):
        return self.__import.GetOutput()

    # import an array
    def SetArray(self, imArray):
        self.__Array = imArray
        numComponents = 1
        dim = imArray.shape
        if len(dim) == 0:
            dim = (1, 1, 1)
        elif len(dim) == 1:
            dim = (1, 1, dim[0])
        elif len(dim) == 2:
            dim = (1, dim[0], dim[1])
        elif len(dim) == 4:
            numComponents = dim[3]
            dim = (dim[0], dim[1], dim[2])

        typecode = imArray.dtype.char

        ar_type = self.__typeDict[typecode]

        complexComponents = 1
        if (typecode == 'F' or typecode == 'D'):
            numComponents = numComponents * 2
            complexComponents = 2

        if (self.__ConvertIntToUnsignedShort and typecode == 'i'):
            imArray = imArray.astype('h')
            ar_type = vtk.VTK_UNSIGNED_SHORT

        size = len(imArray.flat) * self.__sizeDict[ar_type] * complexComponents
        self.__import.CopyImportVoidPointer(imArray, size)
        self.__import.SetDataScalarType(ar_type)
        self.__import.SetNumberOfScalarComponents(numComponents)
        extent = self.__import.GetDataExtent()
        self.__import.SetDataExtent(extent[0], extent[0] + dim[2] - 1,
                                    extent[2], extent[2] + dim[1] - 1,
                                    extent[4], extent[4] + dim[0] - 1)
        self.__import.SetWholeExtent(extent[0], extent[0] + dim[2] - 1,
                                     extent[2], extent[2] + dim[1] - 1,
                                     extent[4], extent[4] + dim[0] - 1)

    def GetArray(self):
        return self.__Array

    # a whole bunch of methods copied from vtkImageImport

    def SetDataExtent(self, extent):
        self.__import.SetDataExtent(extent)

    def GetDataExtent(self):
        return self.__import.GetDataExtent()

    def SetDataSpacing(self, spacing):
        self.__import.SetDataSpacing(spacing)

    def GetDataSpacing(self):
        return self.__import.GetDataSpacing()

    def SetDataOrigin(self, origin):
        self.__import.SetDataOrigin(origin)

    def GetDataOrigin(self):
        return self.__import.GetDataOrigin()


"""
vtkImageExportToArray - a NumPy front-end to vtkImageExport

This class converts a VTK image to a numpy array.  The output
array will always have 3 dimensions (or 4, if the image had
multiple scalar components).

To use this class, you must have numpy installed (http://numpy.scipy.org)

Methods

  SetInputConnection(vtkAlgorithmOutput) -- connect to VTK image pipeline
  SetInputData(vtkImageData) -- set an vtkImageData to export
  GetArray() -- execute pipeline and return a numpy array

Methods from vtkImageExport

  GetDataExtent()
  GetDataSpacing()
  GetDataOrigin()
"""

import numpy
import numpy.core.umath as umath

from vtk import vtkImageExport
from vtk import vtkStreamingDemandDrivenPipeline
from vtk import VTK_SIGNED_CHAR
from vtk import VTK_UNSIGNED_CHAR
from vtk import VTK_SHORT
from vtk import VTK_UNSIGNED_SHORT
from vtk import VTK_INT
from vtk import VTK_UNSIGNED_INT
from vtk import VTK_LONG
from vtk import VTK_UNSIGNED_LONG
from vtk import VTK_FLOAT
from vtk import VTK_DOUBLE


class vtkImageExportToArray:
    def __init__(self):
        self.__export = vtkImageExport()
        self.__ConvertUnsignedShortToInt = False

    # type dictionary

    __typeDict = {VTK_SIGNED_CHAR: 'b',
                  VTK_UNSIGNED_CHAR: 'B',
                  VTK_SHORT: 'h',
                  VTK_UNSIGNED_SHORT: 'H',
                  VTK_INT: 'i',
                  VTK_UNSIGNED_INT: 'I',
                  VTK_FLOAT: 'f',
                  VTK_DOUBLE: 'd'}

    __sizeDict = {VTK_SIGNED_CHAR: 1,
                  VTK_UNSIGNED_CHAR: 1,
                  VTK_SHORT: 2,
                  VTK_UNSIGNED_SHORT: 2,
                  VTK_INT: 4,
                  VTK_UNSIGNED_INT: 4,
                  VTK_FLOAT: 4,
                  VTK_DOUBLE: 8}

    # convert unsigned shorts to ints, to avoid sign problems
    def SetConvertUnsignedShortToInt(self, yesno):
        self.__ConvertUnsignedShortToInt = yesno

    def GetConvertUnsignedShortToInt(self):
        return self.__ConvertUnsignedShortToInt

    def ConvertUnsignedShortToIntOn(self):
        self.__ConvertUnsignedShortToInt = True

    def ConvertUnsignedShortToIntOff(self):
        self.__ConvertUnsignedShortToInt = False

    # set the input
    def SetInputConnection(self, input):
        return self.__export.SetInputConnection(input)

    def SetInputData(self, input):
        return self.__export.SetInputData(input)

    def GetInput(self):
        return self.__export.GetInput()

    def GetArray(self):
        self.__export.Update()
        input = self.__export.GetInput()
        extent = input.GetExtent()
        type = input.GetScalarType()
        numComponents = input.GetNumberOfScalarComponents()
        dim = (extent[5] - extent[4] + 1,
               extent[3] - extent[2] + 1,
               extent[1] - extent[0] + 1)
        if (numComponents > 1):
            dim = dim + (numComponents,)

        imArray = numpy.zeros(dim, self.__typeDict[type])
        self.__export.Export(imArray)

        # convert unsigned short to int to avoid sign issues
        if (type == VTK_UNSIGNED_SHORT and self.__ConvertUnsignedShortToInt):
            imArray = umath.bitwise_and(imArray.astype('i'), 0xffff)

        return imArray

    def GetDataExtent(self):
        return self.__export.GetDataExtent()

    def GetDataSpacing(self):
        return self.__export.GetDataSpacing()

    def GetDataOrigin(self):
        return self.__export.GetDataOrigin()
