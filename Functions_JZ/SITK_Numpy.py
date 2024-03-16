"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by jz410 (28Feb21)
"""

# Add path for self functions
import sys
import os

# Set current folder as working directory
# Get the current working direcory: os.getcwd()
# Change the current working direcory: os.chdir()

import Image_Process_Functions
import Save_Load_File
import Use_Plt
import VTK_Functions
import Post_Image_Process_Functions

# Load standard libs
import numpy
import SimpleITK
import time

"""
##############################################################################
#Func: array positions for elements >, < , == value
##############################################################################
"""


def MaskCoorsVal(inMat,
                 value=[0],
                 valueEnd=[0],
                 compare="not equal"):
    maskCoorsRows = []

    # loop all values for position
    for i in range(len(value)):
        # compare
        if compare == "not equal":
            maskCoorsTupleAdd = numpy.where(inMat != value[i])
        elif compare == "equal":
            maskCoorsTupleAdd = numpy.where(inMat == value[i])
        elif compare == "greater":
            maskCoorsTupleAdd = numpy.where(inMat > value[i])
        elif compare == "greater equal" or compare == "greater_equal":
            maskCoorsTupleAdd = numpy.where(inMat >= value[i])
        elif compare == "smaller":
            maskCoorsTupleAdd = numpy.where(inMat < value[i])
        elif compare == "smaller equal" or compare == "smaller_equal":
            maskCoorsTupleAdd = numpy.where(inMat <= value[i])
        elif compare == "boundary":
            maskCoorsTupleAdd = numpy.where(((inMat > value[i]) & (inMat < valueEnd[i])))

        # add tuple
        maskCoorsTupleArr = numpy.asarray(maskCoorsTupleAdd)
        if not maskCoorsRows: #empty list
            maskCoorsRows = maskCoorsTupleArr
        else:
            maskCoorsRows = numpy.append(maskCoorsTupleArr, maskCoorsRows, axis=1)

    # transpose
    maskCTCoors_Arr = maskCoorsRows.T

    return maskCTCoors_Arr


"""
##############################################################################
#Class: match SimpleITK image and output Numpy 
##############################################################################
"""


class SITK_NP_Arr:
    """
    !!!
    #SimpleITK: image[x,y,z]
    #numpy: image_numpy_array[z,y,x]
    """

    def __init__(self):
        self.SITKImag = None
        self.startT = time.time()

    def InSITKImag(self,
                   SITKImag):
        """
        Import image and extract np.array
        """
        self.SITKImag = SITKImag
        # get numpy array
        self.SITKArr = SimpleITK.GetArrayFromImage(self.SITKImag)

    def InSITKArr(self,
                  SITKArr):
        """
        Import np.array
        """
        self.SITKArr = SITKArr

    def PositionMaskValues(self,
                           value=None,
                           valueEnd=None,
                           compare=None):
        """
        find the mask values coordinates in array [z, y, x]
        """
        # set default values
        if value is None:
            value = [0]
        if valueEnd is None:
            valueEnd = [0]
        if compare is None:
            compare = 'not equal'

        # output array
        self.SITKArrCoors_ZYX = MaskCoorsVal(inMat=self.SITKArr,
                                             value=value,
                                             valueEnd=valueEnd,
                                             compare=compare)

    def PositionXYZ(self,
                    inMatZYX=None):
        """
        Flip array from [z, y, x] to [x, y, z]
        """
        if inMatZYX is None:
            self.SITKArrCoors_XYZ = numpy.flip(self.SITKArrCoors_ZYX, axis=1)
        else:
            self.SITKArrCoors_XYZ = numpy.flip(inMatZYX, axis=1)

    def Actual3DCoors(self,
                      inPosition=None,
                      inSpace=None):
        """
        Convert pixel position to actual spacing
        """
        # set default
        if inPosition is None:
            self.inPosition = self.SITKArrCoors_XYZ
        else:
            self.inPosition = inPosition

        if inSpace is None:
            spacingXYZ = numpy.asarray(self.SITKImag.GetSpacing())
            self.inSpace = numpy.diag(spacingXYZ)
        else:
            self.inSpace = inSpace

        # mat multiply
        self.Actual3DCoors = numpy.matmul(self.inPosition, self.inSpace)

        # check shapes
        print("Position array shape: \n " + str(numpy.shape(self.inPosition)))
        print("Spacing array shape: \n " + str(numpy.shape(self.inSpace)))
        print("Actual3DCoors array shape: \n " + str(numpy.shape(self.Actual3DCoors)))

        # time
        self.multiT = time.time() - self.startT
