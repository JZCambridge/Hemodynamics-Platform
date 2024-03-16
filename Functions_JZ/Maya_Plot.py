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
os.chdir(os.getcwd())
sys.path.insert(0, 'E:\\OneDrive - University of Cambridge\\Uni\\PhD1\\Python\\Spyder\\Functions_07Dec20')

import Image_Process_Functions
import Save_Load_File
import Use_Plt
import VTK_Functions
import Post_Image_Process_Functions

# Load standard libs
import mayavi.mlab
import numpy

"""
##############################################################################
#Plot 3D view
##############################################################################
"""

from mayavi import mlab


def ThreeDTwoObj(matData,
                 fristContrVals=[1],
                 secondContrVals=[2],
                 firstOpa=0.3,
                 secondOpa=0.6,
                 slicPlan=True,
                 slicDirect='x_axes'):
    # create 3d scalar field
    src = mlab.pipeline.scalar_field(matData)
    mlab.pipeline.iso_surface(src,
                              contours=fristContrVals,
                              opacity=firstOpa)
    mlab.pipeline.iso_surface(src,
                              contours=secondContrVals,
                              opacity=secondOpa)
    mlab.pipeline.image_plane_widget(src,
                                     plane_orientation='x_axes',
                                     slice_index=10)


"""
##############################################################################
#Func: plot 1* 3D points with txt 
##############################################################################
"""


def One3DPoints(inMat,
                txt=''):
    # x, y, z
    x = inMat[:, 0]
    y = inMat[:, 1]
    z = inMat[:, 2]

    # Plot points
    mayavi.mlab.figure()
    mayavi.mlab.points3d(x, y, z,
                         colormap="Greens",
                         opacity=0.5)
    mayavi.mlab.text(x=0, y=0,
                     text=txt,
                     color=(1, 1, 1),
                     width=0.5)


"""
##############################################################################
#Func: plot 2* 3D points with txt 
##############################################################################
"""


def Two3DPoints(mat1,
                mat2,
                txt=''):
    # x, y, z
    x1 = mat1[:, 0]
    y1 = mat1[:, 1]
    z1 = mat1[:, 2]
    s1 = 2 * (numpy.ones(numpy.shape(x1)))

    x2 = mat2[:, 0]
    y2 = mat2[:, 1]
    z2 = mat2[:, 2]
    s2 = 2 * (numpy.ones(numpy.shape(x2)))

    # Plot points
    mayavi.mlab.figure()
    mayavi.mlab.points3d(x1, y1, z1, s1,
                         colormap="Greens",
                         mode='2dcross',
                         scale_factor=.6,
                         opacity=0.8)
    mayavi.mlab.points3d(x2, y2, z2, s2,
                         colormap="Reds",
                         mode='2dcircle',
                         scale_factor=1,
                         opacity=0.8)
    mayavi.mlab.text(x=0, y=0,
                     text=txt,
                     color=(1, 1, 1),
                     width=0.2)


"""
##############################################################################
#Func: plot CT values with slicing and txt 
##############################################################################
"""


def ValVolume(mat1,
              valRef,
              txt=''):
    """
    Display volume with max and min range
    Slicing
    Text
    :param mat1:
    :param valRef:
    :param txt:
    :return:
    """
    # figure
    mayavi.mlab.figure()
    # max and min
    max = numpy.max(valRef)
    min = numpy.min(valRef)
    # volume rendering
    src = mayavi.mlab.pipeline.scalar_field(mat1)
    mayavi.mlab.pipeline.volume(src,
                                vmin=min, vmax=max)
    # slicing
    mayavi.mlab.pipeline.image_plane_widget(src,
                                            plane_orientation='x_axes',
                                            slice_index=10)
    mayavi.mlab.pipeline.image_plane_widget(src,
                                            plane_orientation='y_axes',
                                            slice_index=10)
    # txt
    mayavi.mlab.text(x=0, y=0,
                     text=txt,
                     color=(1, 1, 1),
                     width=0.2)

    # colorbar, outline, axes
    mlab.colorbar(orientation='vertical')
    mlab.outline()
    mlab.axes()
