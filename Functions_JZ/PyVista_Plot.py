"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by jz410 (16Mar21)
"""

# Import self-written functions
import Save_Load_File

# import pyvista
# import numpy
# import os
# from datetime import datetime
#
#
# def PlotTwo3DPoints(inMat1,
#                     inMat2,
#                     text="",
#                     title=""):
#     # Plotter
#     plotter = pyvista.Plotter()
#
#     # polydata
#     point_cloud1 = pyvista.PolyData(inMat1)
#     point_cloud2 = pyvista.PolyData(inMat2)
#
#     # Add actor
#     plotter.add_mesh(mesh=point_cloud1,
#                      color='red',
#                      render_points_as_spheres=True)
#     plotter.add_mesh(mesh=point_cloud2,
#                      color='green',
#                      render_points_as_spheres=True)
#
#     # Set back ground
#     plotter.set_background(color="white")
#     # show axis
#     plotter.show_axes()
#     # show grid of black
#     plotter.show_grid(color='black')
#     # add text
#     plotter.add_text(text,
#                      position='lower_right',
#                      font_size=12,
#                      color="black")
#     plotter.add_text(title,
#                      position='upper_left',
#                      font_size=16,
#                      color="black")
#
#     # show plots
#     plotter.show()
#
#     # close and clean
#     plotter.close()
#     plotter.deep_clean()
#
#     return
#
#
# def Render3DVolume(inMat,
#                    limMax=None,
#                    limMin=None,
#                    txt="",
#                    title="",
#                    saveScreen=""):
#     # current date and time
#     now = datetime.now()
#     nowStr = now.strftime("%m%d%Y%H%M%S")  # dd/mm/yyyy /hh/mm/ss
#
#     # no max and min use 16%-86% range of non-zero
#     if limMax is None or limMin is None:
#         # non-zero
#         dataRange = inMat[numpy.where(inMat != 0)]
#         if limMin is None:
#             limMin = numpy.percentile(dataRange, 0.05)
#         if limMax is None:
#             limMax = numpy.percentile(dataRange, 99.95)
#     print("limMin: {}".format(limMin))
#     print("limMax: {}".format(limMax))
#
#     # Plotter
#     plotter = pyvista.Plotter(title=title)
#
#     # Add actor
#     plotter.add_volume(inMat,
#                        cmap="hsv",
#                        clim=[limMin, limMax],
#                        reset_camera=True,
#                      show_scalar_bar=False)
#
#     # Set back ground
#     plotter.set_background(color="white")
#     # show axis
#     plotter.show_axes()
#     # show grid of black
#     plotter.show_grid(color='black')
#     # add text
#     plotter.add_text(txt,
#                      position='lower_right',
#                      font_size=12,
#                      color="black")
#     plotter.add_text(title,
#                      position='upper_left',
#                      font_size=16,
#                      color="black")
#
#     #scalar bar
#     plotter.add_scalar_bar(color="black")
#     # set isometric view
#     plotter.view_isometric(negative=False)
#
#     # # save screenshot
#     # writableFile = False
#     # if not os.path.exists(saveScreen):
#     #     ""
#     # if saveScreen == "" or \
#     #     not os.access(os.path.dirname(saveScreen), os.W_OK): # not os.path.exists(saveScreen) or \# the file is there
#     #     # check the filepath is correct and writable
#     #     # the file does not exists but write privileges are given
#     #
#     #     # Save
#     #     saveScreen = "Backup_" + nowStr + ".png"
#     #
#     # print("Save to: " + saveScreen)
#     #
#     # show plots
#     plotter.show(screenshot=saveScreen)
#
#     return
