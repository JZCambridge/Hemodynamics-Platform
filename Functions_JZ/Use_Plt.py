# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 19:52:47 2020

@author: yingmohuanzhou
"""
# overall library
import Image_Process_Functions
import matplotlib
matplotlib.use('tkagg')

"""
##############################################################################
# class cursor show axes values
##############################################################################
"""


class Cursor:
    """
    A cross hair cursor.
    """

    def __init__(self, ax):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='r', lw=0.8, ls='-')
        self.vertical_line = ax.axvline(color='r', lw=0.8, ls='-')
        # text location in axes coordinates
        self.text = ax.text(0.1, 0.95, '', color="r", transform=ax.transAxes)

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def on_mouse_move(self, event):
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            # update the line positions
            self.horizontal_line.set_ydata(y)
            self.vertical_line.set_xdata(x)
            self.text.set_text('x=%1.2f, y=%1.2f' % (x, y))
            self.ax.figure.canvas.draw()


"""
##############################################################################
#Display three image with matplotlib with slider
##############################################################################
"""
import matplotlib.pyplot as plt
import matplotlib.widgets
import numpy
import tkinter
import sys
import Save_Load_File
from tkinter import filedialog, messagebox
import cv2
import copy


# matplotlib.use('TkAgg')

def slider3Display(matData1=[0],
                   matData2=[0],
                   matData3=[0],
                   fig3OverLap=True,
                   ShareX=True,
                   ShareY=True,
                   ask23MatData=False,
                   OneOverTwo=False,
                   ContourOver=False,
                   tkObj=False,
                   wait=True,
                   root="",
                   slicDiect='X',
                   title=["CTA", "Coronary mask", "Overlapping"],
                   plotRange=[False, False, False],
                   winMin=[0, 0, 0],
                   winMax=[100, 100, 100],
                   cmapChoice='gray',
                   cursorChoice=False):
    # Can show 3 different plots
    # Can share X and/or Y axes
    # Can overlap the 3 plots

    # return msg
    dirErrMsg = ""
    infoMsg = "Slicing along: "

    # front size
    fs = 12

    # Set slicDiect to default 'X' if no matching
    directionList = ['X', 'Y', 'Z']
    noDirectMatch = True
    for val in directionList:
        if val == slicDiect:
            noDirectMatch = False
            infoMsg += str(slicDiect)
            break
    if noDirectMatch:
        dirErrMsg = "Plotting: no direction match: " + str(slicDiect) + " Use default 'X'"
        print("Plotting: no direction match: " + str(slicDiect) + " Use default 'X'")
        slicDiect = 'X'

    # Must have one set of data
    if numpy.shape(numpy.shape(matData1)) == (1,):
        # load mat
        mat1File = Save_Load_File.OpenFilePath(dispMsg="Load 1st NIFTI data to display")
        otherErMsg, aortaErMsg, aorMskValArrayTF, matData1 = Save_Load_File.LoadNifti(niiPath=mat1File)

    # marData1 shape
    matData1Shape = numpy.shape(matData1)

    # second data
    if ask23MatData:
        if numpy.shape(numpy.shape(matData2)) == (1,):  # nromal data is 3 tuples
            # load mat
            mat2File = Save_Load_File.OpenFilePath(dispMsg="Load 2nd NIFTI data to display")
            otherErMsg, aortaErMsg, aorMskValArrayTF, matData2 = Save_Load_File.LoadNifti(niiPath=mat2File)
    elif not ask23MatData:
        if numpy.shape(numpy.shape(matData2)) == (1,):
            # create empty one if no data and not ask to load
            matData2 = numpy.zeros(matData1Shape)

    # third data
    if not fig3OverLap:
        # 3 rd pic is a single pic
        if ask23MatData:
            if numpy.shape(numpy.shape(matData3)) == (1,):
                # load mat
                mat3File = Save_Load_File.OpenFilePath(dispMsg="Load 3rd NIFTI data to display")
                otherErMsg, aortaErMsg, aorMskValArrayTF, matData3 = Save_Load_File.LoadNifti(niiPath=mat3File)
        elif not ask23MatData:
            if numpy.shape(numpy.shape(matData3)) == (1,):
                # create empty one if no data and not ask to load
                matData3 = numpy.zeros(matData1Shape)

        # Check all mats are same shape
        if matData1Shape != numpy.shape(matData2) or matData1Shape != numpy.shape(matData3):
            if tkObj:
                root = tkinter.Tk()
            errMsg = "Mat 1 shape: \n" + str(matData1Shape) + "\nMat 2 shape: \n" + str(
                numpy.shape(matData2)) + "\nMat 3 shape: \n" + str(numpy.shape(matData3))
            print(errMsg)
            messagebox.showerror(title="Shapes not match!!",
                                 message=errMsg)
            if tkObj:
                root.destroy()
                root.mainloop()
            # sys. exit()

        # Create and plot
        # slicing direction
        if slicDiect == 'X':
            figMat1 = matData1[0]
            figMat2 = matData2[0]
            figMat3 = matData3[0]
        if slicDiect == 'Y':
            figMat1 = matData1[:, 0, :]
            figMat2 = matData2[:, 0, :]
            figMat3 = matData3[:, 0, :]
        if slicDiect == 'Z':
            figMat1 = matData1[:, :, 0]
            figMat2 = matData2[:, :, 0]
            figMat3 = matData3[:, :, 0]

        fig, axes0 = plt.subplots(nrows=1, ncols=3, figsize=(9, 3), sharex=ShareX, sharey=ShareY)
        ax0 = axes0.ravel()

        # plot range
        if plotRange[0]:
            ax00 = ax0[0].imshow(figMat1, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
        else:
            ax00 = ax0[0].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), cmap=cmapChoice)
        ax0[0].set_title(title[0], fontsize=fs)
        fig.colorbar(ax00, ax=ax0[0])

        # plot range
        if plotRange[1]:
            ax01 = ax0[1].imshow(figMat2, vmin=winMin[1], vmax=winMax[1], cmap=cmapChoice)
        else:
            ax01 = ax0[1].imshow(figMat2, vmin=numpy.min(matData2), vmax=numpy.max(matData2), cmap=cmapChoice)
        ax0[1].set_title(title[1], fontsize=fs)
        fig.colorbar(ax01, ax=ax0[1])

        # plot range
        if plotRange[2]:
            ax02 = ax0[2].imshow(figMat3, vmin=winMin[2], vmax=winMax[2], cmap=cmapChoice)
        else:
            ax02 = ax0[2].imshow(figMat3, vmin=numpy.min(matData3), vmax=numpy.max(matData3), cmap=cmapChoice)
        ax0[2].set_title(title[2], fontsize=fs)
        fig.colorbar(ax02, ax=ax0[2])

        # Set windows dialogue title
        fig.canvas.set_window_title('Do NOT close window. Press "ENTER" to continue!')
        plt.tight_layout(pad=0.5)
        # plt.savefig('img/output.jpg')

        # Setting slider
        axcolor = 'lightgoldenrodyellow'
        axSlice = plt.axes([0.1, 0.15, 0.6, 0.03], facecolor=axcolor)  # [left, bottom, width, height]
        # slicing direction
        if slicDiect == 'X':
            shpMax = matData1Shape[0]
        if slicDiect == 'Y':
            shpMax = matData1Shape[1]
        if slicDiect == 'Z':
            shpMax = matData1Shape[2]
        sSlice = matplotlib.widgets.Slider(ax=axSlice,
                                           label='Slice',
                                           valmin=0,
                                           valmax=(shpMax - 1),
                                           valinit=10,
                                           valstep=1)

        def updateNoOverLp(val):
            # slice value
            imgSlice = sSlice.val

            # update value
            # Directions
            # slicing direction
            if slicDiect == 'X':
                figMat1 = matData1[imgSlice]
                figMat2 = matData2[imgSlice]
                figMat3 = matData3[imgSlice]
            if slicDiect == 'Y':
                figMat1 = matData1[:, imgSlice, :]
                figMat2 = matData2[:, imgSlice, :]
                figMat3 = matData3[:, imgSlice, :]
            if slicDiect == 'Z':
                figMat1 = matData1[:, :, imgSlice]
                figMat2 = matData2[:, :, imgSlice]
                figMat3 = matData3[:, :, imgSlice]

            # update img
            ax00.set_data(figMat1)
            ax01.set_data(figMat2)
            ax02.set_data(figMat3)

            # update and draw
            fig.canvas.draw_idle()

        # active slider update
        sSlice.on_changed(updateNoOverLp)

        # plot
        plt.show(block=True)
        # # plt.pause((24*60*60))
        # while not tkObj:
        #     if plt.waitforbuttonpress():
        #         break

    # third data
    if fig3OverLap and ContourOver:
        print("Plot overlap and contour")
        title.append("Overlapping mask")
        # Check all mats are same shape
        if matData1Shape != numpy.shape(matData2):
            if tkObj:
                root = tkinter.Tk()
            errMsg = "Mat 1 shape: \n" + str(matData1Shape) + "\nMat 2 shape: \n" + str(numpy.shape(matData2))
            print(errMsg)
            messagebox.showerror(title="Shapes not match: STOP!",
                                 message=errMsg)
            if tkObj:
                root.destroy()
                root.mainloop()
            sys.exit()

        # Create and plot
        # slicing direction
        if slicDiect == 'X':
            figMat1 = matData1[0]
            figMat2 = matData2[0]
        if slicDiect == 'Y':
            figMat1 = matData1[:, 0, :]
            figMat2 = matData2[:, 0, :]
        if slicDiect == 'Z':
            figMat1 = matData1[:, :, 0]
            figMat2 = matData2[:, :, 0]

        fig, axes0 = plt.subplots(nrows=1, ncols=4, figsize=(12, 6), sharex=ShareX, sharey=ShareY,
                                  constrained_layout=False)  # width, height in inches
        fig.subplots_adjust(bottom=0.25)  # set plot distance
        ax0 = axes0.ravel()

        # plot range
        if plotRange[0]:
            ax00 = ax0[0].imshow(figMat1, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
        else:
            ax00 = ax0[0].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), cmap=cmapChoice)
        ax0[0].set_title(title[0], fontsize=fs)
        fig.colorbar(ax00, ax=ax0[0], fraction=0.046, pad=0.04)

        # plot range
        if plotRange[1]:
            ax01 = ax0[1].imshow(figMat2, vmin=winMin[1], vmax=winMax[1], cmap=cmapChoice)
        else:
            ax01 = ax0[1].imshow(figMat2, vmin=numpy.min(matData2), vmax=numpy.max(matData2), cmap=cmapChoice)
        ax0[1].set_title(title[1], fontsize=fs)
        fig.colorbar(ax01, ax=ax0[1], fraction=0.046, pad=0.04)

        # plot Contour
        if not OneOverTwo:  # !!!! intially wrong definition of on over two should be TWO over ONE
            # CV2 contour
            # Need to convert to CV_8UC1 == numpy.uint8
            contourBase = copy.deepcopy(figMat2)
            contourBase = contourBase.astype(numpy.uint8)
            contours, hierarchy = cv2.findContours(contourBase,
                                                   cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE,
                                                   offset=(0, 0))
            if plotRange[2]:
                ax021 = ax0[2].imshow(figMat1, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
            else:
                ax021 = ax0[2].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), cmap=cmapChoice)
            # plot all contour
            for cntr in contours:
                ax022 = ax0[2].fill(cntr[:, :, 0], cntr[:, :, 1], facecolor='none', edgecolor='red', linewidth=2)

            ax0[2].set_title(title[2], fontsize=fs)
        elif OneOverTwo:
            # CV2 contour
            # Need to convert to CV_8UC1 == numpy.uint8
            contourBase = copy.deepcopy(figMat1)
            contourBase = contourBase.astype(numpy.uint8)
            contours, hierarchy = cv2.findContours(contourBase,
                                                   cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE,
                                                   offset=(0, 0))

            if plotRange[2]:
                ax021 = ax0[2].imshow(figMat2, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
            else:
                ax021 = ax0[2].imshow(figMat2, vmin=numpy.min(matData1), vmax=numpy.max(matData1), cmap=cmapChoice)
            # plot all contour
            for cntr in contours:
                ax022 = ax0[2].fill(cntr[:, :, 0], cntr[:, :, 1], facecolor='none', edgecolor='red', linewidth=2)

            ax0[2].set_title(title[2], fontsize=fs)
        fig.colorbar(ax021, ax=ax0[2], fraction=0.046, pad=0.04)

        # plot Overlap
        if not OneOverTwo:  # !!!! intially wrong definition of on over two should be TWO over ONE
            if plotRange[2]:
                ax031 = ax0[3].imshow(figMat1, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
            else:
                ax031 = ax0[3].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), cmap=cmapChoice)
            ax032 = ax0[3].imshow(figMat2, vmin=numpy.min(matData2), vmax=numpy.max(matData2), alpha=0.5,
                                  cmap="Reds")
            ax0[3].set_title(title[3], fontsize=fs)
        elif OneOverTwo:
            if plotRange[2]:
                ax031 = ax0[3].imshow(figMat2, vmin=winMin[1], vmax=winMax[1], cmap=cmapChoice)
            else:
                ax031 = ax0[3].imshow(figMat2, vmin=numpy.min(matData2), vmax=numpy.max(matData2), cmap=cmapChoice)
            ax032 = ax0[3].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), alpha=0.5,
                                  cmap="Reds")
            ax0[3].set_title(title[3], fontsize=fs)
        fig.colorbar(ax031, ax=ax0[3], fraction=0.046, pad=0.04)

        # Set windows dialogue title
        fig.canvas.set_window_title('Do NOT close window. Press "ENTER" to continue!')

        # plt.tight_layout(pad=0.5)
        # plt.savefig('img/output.jpg')

        # Setting slider
        axcolor = 'lightgoldenrodyellow'
        axSlice = plt.axes([0.1, 0.06, 0.6, 0.03], facecolor=axcolor)  # [left, bottom, width, height]
        # slicing direction
        if slicDiect == 'X':
            shpMax = matData1Shape[0]
        if slicDiect == 'Y':
            shpMax = matData1Shape[1]
        if slicDiect == 'Z':
            shpMax = matData1Shape[2]

        print(slicDiect)
        print(matData1Shape)
        print(shpMax)
        sSlice = matplotlib.widgets.Slider(ax=axSlice,
                                           label='Slice',
                                           valmin=0,
                                           valmax=(shpMax - 1),
                                           valinit=10,
                                           valstep=1)

        def updateOverLP(val):
            # slice value
            imgSlice = sSlice.val

            # update value
            # Directions
            # slicing direction
            if slicDiect == 'X':
                figMat1 = matData1[imgSlice]
                figMat2 = matData2[imgSlice]
            if slicDiect == 'Y':
                figMat1 = matData1[:, imgSlice, :]
                figMat2 = matData2[:, imgSlice, :]
            if slicDiect == 'Z':
                figMat1 = matData1[:, :, imgSlice]
                figMat2 = matData2[:, :, imgSlice]

            # Contour
            if not OneOverTwo:  # !!!! intially wrong definition of on over two should be TWO over ONE
                # CV2 contour
                # Need to convert to CV_8UC1 == numpy.uint8
                contourBase = copy.deepcopy(figMat2)
                contourBase = contourBase.astype(numpy.uint8)
                contours, hierarchy = cv2.findContours(contourBase,
                                                       cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE,
                                                       offset=(0, 0))
                # update
                # overlapping
                ax031.set_data(figMat1)
                ax032.set_data(figMat2)
                # Clear contour and replot
                ax0[2].clear()
                ax0[2].imshow(figMat1, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
                for cntr in contours:
                    ax0[2].fill(cntr[:, :, 0], cntr[:, :, 1], facecolor='none', edgecolor='red', linewidth=2)

            elif OneOverTwo:
                # CV2 contour
                # Need to convert to CV_8UC1 == numpy.uint8
                contourBase = copy.deepcopy(figMat1)
                contourBase = contourBase.astype(numpy.uint8)
                contours, hierarchy = cv2.findContours(contourBase,
                                                       cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE,
                                                       offset=(0, 0))
                # update
                # overlapping
                ax031.set_data(figMat2)
                ax032.set_data(figMat1)
                # Clear contour and replot
                ax0[2].clear()
                ax0[2].imshow(figMat2, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
                for cntr in contours:
                    ax0[2].fill(cntr[:, :, 0], cntr[:, :, 1], facecolor='none', edgecolor='red', linewidth=2)

            # update img
            ax00.set_data(figMat1)
            ax01.set_data(figMat2)

            # update and draw
            fig.canvas.draw_idle()

        # active slider update
        sSlice.on_changed(updateOverLP)

        # Setting slider
        axcolor = 'lightgoldenrodyellow'
        axOpacity = plt.axes([0.1, 0.02, 0.6, 0.03], facecolor=axcolor)

        sOpacity = matplotlib.widgets.Slider(ax=axOpacity,
                                             label='Opacity',
                                             valmin=0,
                                             valmax=1,
                                             valinit=0.5,
                                             valstep=0.05)

        def updateOpacity(val):
            # slice value
            aOpacity = sOpacity.val

            # update img
            ax032.set_alpha(aOpacity)

            # update and draw
            fig.canvas.draw_idle()

        # active slider update
        sOpacity.on_changed(updateOpacity)

        # plot
        plt.show(block=True)
        # while not tkObj and wait:
        #     if plt.waitforbuttonpress():
        #         break

    # third data
    if fig3OverLap and not ContourOver:
        print("Plot overlap no contour")

        # Check all mats are same shape
        if matData1Shape != numpy.shape(matData2) and ask23MatData:
            errMsg = "Mat 1 shape: \n" + str(matData1Shape) + "\nMat 2 shape: \n" + str(numpy.shape(matData2))
            print(errMsg)

        if matData1Shape != numpy.shape(matData2) and not ask23MatData:
            errMsg = "Mat 1 shape: \n" + str(matData1Shape) + "\nMat 2 shape: \n" + str(numpy.shape(matData2))
            print(errMsg)
            matData2 = numpy.zeros(matData1Shape)

        # Create and plot
        # slicing direction
        if slicDiect == 'X':
            figMat1 = matData1[0]
            figMat2 = matData2[0]
        if slicDiect == 'Y':
            figMat1 = matData1[:, 0, :]
            figMat2 = matData2[:, 0, :]
        if slicDiect == 'Z':
            figMat1 = matData1[:, :, 0]
            figMat2 = matData2[:, :, 0]
        # create subplots
        fig, axes0 = plt.subplots(
            nrows=1,
            ncols=3,
            figsize=(9, 3),
            sharex=ShareX,
            sharey=ShareY
        )
        # resize figure for functions
        fig.subplots_adjust(left=0.1, bottom=0.25)  # set plot distance
        ax0 = axes0.ravel()

        # plot range
        if plotRange[0]:
            ax00 = ax0[0].imshow(
                figMat1,
                vmin=winMin[0],
                vmax=winMax[0],
                cmap=cmapChoice
            )
        else:
            ax00 = ax0[0].imshow(
                figMat1,
                vmin=numpy.min(matData1),
                vmax=numpy.max(matData1),
                cmap=cmapChoice
            )
        ax0[0].set_title(title[0], fontsize=fs)
        fig.colorbar(ax00, ax=ax0[0])

        # plot range
        if plotRange[1]:
            ax01 = ax0[1].imshow(
                figMat2,
                vmin=winMin[1],
                vmax=winMax[1],
                cmap=cmapChoice
            )
        else:
            ax01 = ax0[1].imshow(
                figMat2,
                vmin=numpy.min(matData2),
                vmax=numpy.max(matData2),
                cmap=cmapChoice
            )
        ax0[1].set_title(title[1], fontsize=fs)
        fig.colorbar(ax01, ax=ax0[1])

        # plot range
        if not OneOverTwo:  # !!!! intially wrong definition of on over two should be TWO over ONE
            if plotRange[2]:
                ax021 = ax0[2].imshow(
                    figMat1,
                    vmin=winMin[0],
                    vmax=winMax[0],
                    cmap=cmapChoice
                )
            else:
                ax021 = ax0[2].imshow(
                    figMat1,
                    vmin=numpy.min(matData1),
                    vmax=numpy.max(matData1),
                    cmap=cmapChoice
                )
            # mask creation for on the non-zero region
            maskOver = numpy.ma.masked_where(figMat2 == 0, figMat2)
            ax022 = ax0[2].imshow(
                maskOver,
                vmin=numpy.min(matData2),
                vmax=numpy.max(matData2),
                alpha=0.5,
                cmap="Reds"
            )
            ax0[2].set_title(title[2], fontsize=fs)

        elif OneOverTwo:
            if plotRange[2]:
                ax021 = ax0[2].imshow(
                    figMat2,
                    vmin=winMin[1],
                    vmax=winMax[1],
                    cmap=cmapChoice
                )
            else:
                ax021 = ax0[2].imshow(
                    figMat2,
                    vmin=numpy.min(matData2),
                    vmax=numpy.max(matData2),
                    cmap=cmapChoice
                )
            # transparent '0's
            maskOver = numpy.ma.masked_where(figMat1 == 0, figMat1)
            ax022 = ax0[2].imshow(
                maskOver,
                vmin=numpy.min(matData1),
                vmax=numpy.max(matData1),
                alpha=0.5,
                cmap="Reds"
            )
            ax0[2].set_title(title[2], fontsize=fs)
        fig.colorbar(ax021, ax=ax0[2])

        # Set windows dialogue title
        fig.canvas.manager.set_window_title('Do NOT close window. Press "ENTER" to continue!')

        # plt.tight_layout(pad=0.5)
        # plt.savefig('img/output.jpg')

        # change slides
        def updateOverLP(val):
            # slice value
            imgSlice = sSlice.val

            # update value
            # slicing direction
            if slicDiect == 'X':
                figMat1 = matData1[imgSlice]
                figMat2 = matData2[imgSlice]
            if slicDiect == 'Y':
                figMat1 = matData1[:, imgSlice, :]
                figMat2 = matData2[:, imgSlice, :]
            if slicDiect == 'Z':
                figMat1 = matData1[:, :, imgSlice]
                figMat2 = matData2[:, :, imgSlice]

            # update img
            ax00.set_data(figMat1)
            ax01.set_data(figMat2)
            if not OneOverTwo:
                ax021.set_data(figMat1)
                # transparent "0"
                maskOver = numpy.ma.masked_where(figMat2 == 0, figMat2)
                ax022.set_data(maskOver)
            if OneOverTwo:
                ax021.set_data(figMat2)
                # transparent "0"
                maskOver = numpy.ma.masked_where(figMat1 == 0, figMat1)
                ax022.set_data(maskOver)

            # update and draw
            fig.canvas.draw_idle()

        ## Setting slider box
        axcolor = 'lightgoldenrodyellow'
        axSlice = fig.add_axes(
            [0.05, 0.1, 0.8, 0.03],
            facecolor=axcolor
        )  # [left, bottom, width, height]
        ## slicing direction
        if slicDiect == 'X':
            shpMax = matData1Shape[0]
        if slicDiect == 'Y':
            shpMax = matData1Shape[1]
        if slicDiect == 'Z':
            shpMax = matData1Shape[2]
        sSlice = matplotlib.widgets.Slider(
            ax=axSlice,
            label='Slice',
            valmin=0,
            valmax=(shpMax - 1),
            valinit=10,
            valstep=1
        )

        ## active slider update
        sSlice.on_changed(updateOverLP)

        # change opacity
        def updateOpacity(val):
            # slice value
            aOpacity = sOpacity.val

            # update img
            ax022.set_alpha(aOpacity)

            # update and draw
            fig.canvas.draw_idle()

        ## Setting slider
        axcolor = 'lightgoldenrodyellow'
        axOpacity = plt.axes(
            [0.05, 0.25, 0.01, 0.66],
            facecolor=axcolor
        )  # [left, bottom, width, height]
        ## create slider
        sOpacity = matplotlib.widgets.Slider(
            ax=axOpacity,
            label='Opacity',
            valmin=0,
            valmax=1,
            valinit=0.5,
            valstep=0.05,
            orientation="vertical"
        )

        # active slider update
        sOpacity.on_changed(updateOpacity)

        # set up crusor
        if cursorChoice:
            cursor = Cursor(ax0[2])
            fig.canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)
            fig.canvas.draw_idle()

        def wakeupCursor(val):
            print("push")
            cursor = Cursor(ax0[2])
            fig.canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)
            fig.canvas.draw_idle()

        # button to wake up cursor
        axBut = fig.add_axes(
            [0.66, 0.06, 0.2, 0.03],
            facecolor=axcolor
        )  # [left, bottom, width, height]
        but = matplotlib.widgets.Button(axBut, 'Cursor')
        but.on_clicked(wakeupCursor)


        # set text to change slice
        def submit(expression):
            # slice value
            imgSlice = int(expression)
            # upadte slider
            sSlice.set_val(imgSlice)
            # update value
            # slicing direction
            if slicDiect == 'X':
                figMat1 = matData1[imgSlice]
                figMat2 = matData2[imgSlice]
            if slicDiect == 'Y':
                figMat1 = matData1[:, imgSlice, :]
                figMat2 = matData2[:, imgSlice, :]
            if slicDiect == 'Z':
                figMat1 = matData1[:, :, imgSlice]
                figMat2 = matData2[:, :, imgSlice]

            # update img
            ax00.set_data(figMat1)
            ax01.set_data(figMat2)
            if not OneOverTwo:
                ax021.set_data(figMat1)
                # transparent "0"
                maskOver = numpy.ma.masked_where(figMat2 == 0, figMat2)
                ax022.set_data(maskOver)
            if OneOverTwo:
                ax021.set_data(figMat2)
                # transparent "0"
                maskOver = numpy.ma.masked_where(figMat1 == 0, figMat1)
                ax022.set_data(maskOver)

            # update and draw
            fig.canvas.draw_idle()

        ## Setting slider box
        axText = fig.add_axes(
            [0.2, 0.06, 0.4, 0.03],
            facecolor=axcolor
        )  # [left, bottom, width, height]
        text_box = matplotlib.widgets.TextBox(
            axText,
            "Slice to show:"
        )
        text_box.on_submit(submit)
        text_box.set_val("10")  # Trigger `submit` with the initial string.

        # plot
        plt.show(block=True)
        # while not tkObj and wait:
        #     if plt.waitforbuttonpress():
        #         break


"""
##############################################################################
#Display six images with matplotlib
##############################################################################
"""
import matplotlib.pyplot as plt
import matplotlib.widgets
import numpy
import tkinter
import sys
import Save_Load_File


def PlotSixFigs(matData1=[0],
                matData2=[0],
                matData3=[0],
                matData4=[0],
                matData5=[0],
                matData6=[0],
                fig3OverLap=True,
                fig6OverLap=False,
                OneOverTwo=True,
                FourOverFive=True,
                ShareX=True,
                ShareY=True,
                ask2to5MatData=True,
                title=["CTA", "Coronary mask", "Overlapping", "Coronary mask", "Overlapping"],
                plotRange=[True, False, False, False, False, False],
                winMin=[0, 0, 0, 0, 0, 0],
                winMax=[100, 100, 100, 100, 100, 100],
                cmapChoice='gray'):
    # Can show 6 different plots
    # Can share X and/or Y axes
    # Can overlap the 3 and 6 plots

    # front size
    fs = 12

    # Must have one set of data
    if numpy.shape(numpy.shape(matData1)) == (1,):
        # load mat
        mat1File = Save_Load_File.OpenFilePath(dispMsg="Load 1st NIFTI data to display")
        otherErMsg, aortaErMsg, aorMskValArrayTF, matData1 = Save_Load_File.LoadNifti(niiPath=mat1File)

    # marData1 shape
    matData1Shape = numpy.shape(matData1)

    # second data
    if ask2to5MatData:
        if numpy.shape(numpy.shape(matData4)) == (1,):  # nromal data is 3 tuples
            # load mat
            mat4File = Save_Load_File.OpenFilePath(dispMsg="Load 4th NIFTI data to display")
            otherErMsg, aortaErMsg, aorMskValArrayTF, matData4 = Save_Load_File.LoadNifti(niiPath=mat4File)
    elif not ask2to5MatData:
        if numpy.shape(numpy.shape(matData4)) == (1,):
            # create empty one if no data and not ask to load
            matData2 = numpy.zeros(matData1Shape)

    # forth data
    if ask2to5MatData:
        if numpy.shape(numpy.shape(matData4)) == (1,):  # nromal data is 3 tuples
            # load mat
            mat4File = Save_Load_File.OpenFilePath(dispMsg="Load 2nd NIFTI data to display")
            otherErMsg, aortaErMsg, aorMskValArrayTF, matData4 = Save_Load_File.LoadNifti(niiPath=mat4File)
    elif not ask2to5MatData:
        if numpy.shape(numpy.shape(matData4)) == (1,):
            # create empty one if no data and not ask to load
            matData4 = numpy.zeros(matData1Shape)

    # fifth data
    if ask2to5MatData:
        if numpy.shape(numpy.shape(matData5)) == (1,):  # nromal data is 3 tuples
            # load mat
            mat5File = Save_Load_File.OpenFilePath(dispMsg="Load 5th NIFTI data to display")
            otherErMsg, aortaErMsg, aorMskValArrayTF, matData5 = Save_Load_File.LoadNifti(niiPath=mat5File)
    elif not ask2to5MatData:
        if numpy.shape(numpy.shape(matData5)) == (1,):
            # create empty one if no data and not ask to load
            matData5 = numpy.zeros(matData1Shape)

    # sixth data
    if ask2to5MatData:
        if numpy.shape(numpy.shape(matData6)) == (1,):  # nromal data is 3 tuples
            # load mat
            mat6File = Save_Load_File.OpenFilePath(dispMsg="Load 6th NIFTI data to display")
            otherErMsg, aortaErMsg, aorMskValArrayTF, matData6 = Save_Load_File.LoadNifti(niiPath=mat6File)
    elif not ask2to5MatData:
        if numpy.shape(numpy.shape(matData6)) == (1,):
            # create empty one if no data and not ask to load
            matData6 = numpy.zeros(matData1Shape)

    # third data
    if not fig3OverLap:
        # 3 rd pic is a single pic
        if ask2to5MatData:
            if numpy.shape(numpy.shape(matData3)) == (1,):
                # load mat
                mat3File = Save_Load_File.OpenFilePath(dispMsg="Load 3rd NIFTI data to display")
                otherErMsg, aortaErMsg, aorMskValArrayTF, matData3 = Save_Load_File.LoadNifti(niiPath=mat3File)
        elif not ask2to5MatData:
            if numpy.shape(numpy.shape(matData3)) == (1,):
                # create empty one if no data and not ask to load
                matData3 = numpy.zeros(matData1Shape)

        # Create and plot
        figMat1 = matData1
        figMat2 = matData2
        figMat3 = matData3
        figMat4 = matData4
        figMat5 = matData5
        figMat6 = matData6

        fig, axes0 = plt.subplots(nrows=2, ncols=3, figsize=(9, 3), sharex=ShareX, sharey=ShareY)
        ax0 = axes0.ravel()

        # plot range
        if plotRange[0]:
            ax00 = ax0[0].imshow(figMat1, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
        else:
            ax00 = ax0[0].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), cmap=cmapChoice)
        ax0[0].set_title(title[0], fontsize=fs)
        fig.colorbar(ax00, ax=ax0[0])

        # plot range
        if plotRange[1]:
            ax01 = ax0[1].imshow(figMat2, vmin=winMin[1], vmax=winMax[1])
        else:
            ax01 = ax0[1].imshow(figMat2, vmin=numpy.min(matData2), vmax=numpy.max(matData2), cmap=cmapChoice)
        ax0[1].set_title(title[1], fontsize=fs)
        fig.colorbar(ax01, ax=ax0[1])

        # plot range
        if plotRange[2]:
            ax02 = ax0[2].imshow(figMat3, vmin=winMin[2], vmax=winMax[2], cmap=cmapChoice)
        else:
            ax02 = ax0[2].imshow(figMat3, vmin=numpy.min(matData3), vmax=numpy.max(matData3), cmap=cmapChoice)
        ax0[2].set_title(title[2], fontsize=fs)
        fig.colorbar(ax02, ax=ax0[2])

        # plot range
        if plotRange[3]:
            ax03 = ax0[3].imshow(figMat4, vmin=winMin[3], vmax=winMax[3], cmap=cmapChoice)
        else:
            ax03 = ax0[3].imshow(figMat4, vmin=numpy.min(matData4), vmax=numpy.max(matData4), cmap=cmapChoice)
        ax0[3].set_title(title[3], fontsize=fs)
        fig.colorbar(ax03, ax=ax0[3])

        # plot range
        if plotRange[4]:
            ax04 = ax0[4].imshow(figMat5, vmin=winMin[4], vmax=winMax[4], cmap=cmapChoice)
        else:
            ax04 = ax0[4].imshow(figMat5, vmin=numpy.min(matData5), vmax=numpy.max(matData5), cmap=cmapChoice)
        ax0[4].set_title(title[4], fontsize=fs)
        fig.colorbar(ax04, ax=ax0[4])

        # plot range
        if plotRange[5]:
            ax05 = ax0[5].imshow(figMat6, vmin=winMin[5], vmax=winMax[5], cmap=cmapChoice)
        else:
            ax05 = ax0[5].imshow(figMat6, vmin=numpy.min(matData6), vmax=numpy.max(matData6), cmap=cmapChoice)
        ax0[5].set_title(title[5], fontsize=fs)
        fig.colorbar(ax05, ax=ax0[5])

        # Set windows dialogue title
        fig.canvas.set_window_title('Do NOT close window. Press "ENTER" to continue!')

        plt.tight_layout(pad=0.5)
        # plt.savefig('img/output.jpg')

        # plot
        plt.show(block=True)
        while True:
            if plt.waitforbuttonpress():
                break

    # third data
    if fig3OverLap:

        # Check all mats are same shape
        if matData1Shape != numpy.shape(matData2):
            root = tkinter.Tk()
            errMsg = "Mat 1 shape: \n" + str(matData1Shape) + "\nMat 2 shape: \n" + str(numpy.shape(matData2))
            print(errMsg)
            messagebox.showerror(title="Shapes not match: STOP!",
                                 message=errMsg)
            root.destroy()
            root.mainloop()
            sys.exit()

        # Create and plot
        # Create and plot
        figMat1 = matData1
        figMat2 = matData2
        # figMat3 = matData3
        figMat4 = matData4
        figMat5 = matData5
        figMat6 = matData6

        fig, axes0 = plt.subplots(nrows=2, ncols=3, figsize=(9, 3), sharex=ShareX, sharey=ShareY)
        ax0 = axes0.ravel()

        # plot range
        if plotRange[0]:
            ax00 = ax0[0].imshow(figMat1, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
        else:
            ax00 = ax0[0].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), cmap=cmapChoice)
        ax0[0].set_title(title[0], fontsize=fs)
        fig.colorbar(ax00, ax=ax0[0])

        # plot range
        if plotRange[1]:
            ax01 = ax0[1].imshow(figMat2, vmin=winMin[1], vmax=winMax[1], cmap=cmapChoice)
        else:
            ax01 = ax0[1].imshow(figMat2, vmin=numpy.min(matData2), vmax=numpy.max(matData2), cmap=cmapChoice)
        ax0[1].set_title(title[1], fontsize=fs)
        fig.colorbar(ax01, ax=ax0[1])

        # plot range
        if OneOverTwo:
            if plotRange[2]:
                ax021 = ax0[2].imshow(figMat1, vmin=winMin[0], vmax=winMax[0], cmap=cmapChoice)
            else:
                ax021 = ax0[2].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), cmap=cmapChoice)
            ax022 = ax0[2].imshow(figMat2, vmin=numpy.min(matData2), vmax=numpy.max(matData2), alpha=0.5, cmap="Reds")
            ax0[2].set_title(title[2], fontsize=fs)
        elif not OneOverTwo:
            if plotRange[2]:
                ax021 = ax0[2].imshow(figMat2, vmin=winMin[1], vmax=winMax[1], cmap=cmapChoice)
            else:
                ax021 = ax0[2].imshow(figMat2, vmin=numpy.min(matData2), vmax=numpy.max(matData2), cmap=cmapChoice)
            ax022 = ax0[2].imshow(figMat1, vmin=numpy.min(matData1), vmax=numpy.max(matData1), alpha=0.5, cmap="Reds")
            ax0[2].set_title(title[2], fontsize=fs)
        fig.colorbar(ax021, ax=ax0[2])

        # plot range
        if plotRange[3]:
            ax03 = ax0[3].imshow(figMat4, vmin=winMin[3], vmax=winMax[3], cmap=cmapChoice)
        else:
            ax03 = ax0[3].imshow(figMat4, vmin=numpy.min(matData4), vmax=numpy.max(matData4), cmap=cmapChoice)
        ax0[3].set_title(title[3], fontsize=fs)
        fig.colorbar(ax03, ax=ax0[3])

        # plot range
        if plotRange[4]:
            ax04 = ax0[4].imshow(figMat5, vmin=winMin[4], vmax=winMax[4], cmap=cmapChoice)
        else:
            ax04 = ax0[4].imshow(figMat5, vmin=numpy.min(matData5), vmax=numpy.max(matData5), cmap=cmapChoice)
        ax0[4].set_title(title[4], fontsize=fs)
        fig.colorbar(ax04, ax=ax0[4])

        # plot range
        if plotRange[5]:
            ax05 = ax0[5].imshow(figMat6, vmin=winMin[5], vmax=winMax[5], cmap=cmapChoice)
        else:
            ax05 = ax0[5].imshow(figMat6, vmin=numpy.min(matData6), vmax=numpy.max(matData6), cmap=cmapChoice)
        ax0[5].set_title(title[5], fontsize=fs)
        fig.colorbar(ax05, ax=ax0[5])

        # Set windows dialogue title
        fig.canvas.set_window_title('Do NOT close window. Press "ENTER" to continue!')

        plt.tight_layout(pad=0.5)
        # plt.savefig('img/output.jpg')

        # Setting slider
        axcolor = 'lightgoldenrodyellow'
        axOpacity = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)

        sOpacity = matplotlib.widgets.Slider(
            ax=axOpacity,
            label='Opacity',
            valmin=0,
            valmax=1,
            valinit=0.5,
            valstep=0.05
        )

        def updateOpacity(val):
            # slice value
            aOpacity = sOpacity.val

            # update img
            ax022.set_alpha(aOpacity)

            # update and draw
            fig.canvas.draw_idle()

        # active slider update
        sOpacity.on_changed(updateOpacity)

        # plot
        plt.show(block=True)
        while True:
            if plt.waitforbuttonpress():
                break


"""
##############################################################################
# Func: radial display 
##############################################################################
"""


def RadialDisplay(
        Img,
        colorMap,
        minVal,
        maxVal,
        plotTitle,
        fontSize,
        colorBar,
        showAxes,
        XLbl,
        YLbl,
        saveImg,
        imgOutPath,
        colorBarTitle,
        nTicks=5
):
    # plot
    fig, ax = plt.subplots(nrows=1, ncols=1, constrained_layout=False)
    axPlt = ax.imshow(
        Img,
        cmap=colorMap,
        vmin=minVal,
        vmax=maxVal,
    )
    ax.set_title(
        plotTitle,
        fontsize=fontSize
    )
    ## colorbar
    if colorBar:
        # ticks
        tickList = [None] * nTicks
        # values
        tickList[0] = minVal
        tickList[nTicks - 1] = maxVal
        interval = (maxVal - minVal) / (nTicks - 1)
        # y labels
        yLbls = [None] * nTicks
        yLbls[0] = "{0:.3g}".format(minVal)
        yLbls[nTicks - 1] = "{0:.3g}".format(maxVal)
        for i in range(1, nTicks - 1):
            tickList[i] = i * interval + minVal
            yLbls[i] = "{0:.3g}".format(tickList[i])
        # Add colorbar, make sure to specify tick locations to match desired ticklabels
        cbar = fig.colorbar(axPlt, extend='both', ticks=tickList)
        cbar.ax.set_yticklabels(yLbls)  # vertically oriented colorbar
        cbar.set_label(colorBarTitle, rotation=270, fontsize=fontSize, labelpad=15)
    if showAxes:
        ax.set_xlabel(XLbl, fontsize=fontSize)
        ax.set_ylabel(YLbl, fontsize=fontSize)
    else:
        ax.axis('off')
    ## save
    if saveImg:
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(imgOutPath, dpi=150)


"""
##############################################################################
# Func: display masks and contours
##############################################################################
"""
import matplotlib.pyplot as plt
import scipy.ndimage
import numpy
import matplotlib.colors
import matplotlib.patches
import skimage.measure
import time


def PlotMasksContours(
        backImg,
        backColorMap,
        backMinVal,
        backMaxVal,
        colorBarTitle,
        plotTitle,
        resampleFac,
        inMasks,
        maskLengeds,
        maskStarts,
        maskStops,
        maskSigma,
        cmapChoices,
        maskTransparency,
        contourMasks,
        contourStarts,
        contourStops,
        contourSigma,
        contourLevel,
        contourColors,
        contourLineWidths,
        contourRefs,
        fontSize,
        legend,
        colorBar,
        showAxes,
        XLbl,
        YLbl,
        saveImg,
        imgOutPath,
        maskLegendX,
        maskLegendY,
        maskLegendLoc,
        contourLegendX,
        contourLegendY,
        contourLegendLoc,
        resizeX,
        xSliceStart,
        xSliceFinish,
        resizeY,
        ySliceStart,
        ySliceFinish,
        splineOrder,
        showMask,
        showContour
):
    # time
    strtT = time.time()

    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["message"] = ""

    # plot background image
    ## resampling
    backImgRes = scipy.ndimage.zoom(
        input=backImg,
        zoom=resampleFac,
        output=None,
        order=splineOrder,
        mode='constant',
        cval=0.0,
        prefilter=True
    )
    ## plot
    fig, ax = plt.subplots(nrows=1, ncols=1, constrained_layout=False)
    backPlt = ax.imshow(
        backImgRes,
        cmap=backColorMap,
        vmin=backMinVal,
        vmax=backMaxVal
    )

    # plot masks
    if showMask:
        ## legend patches
        patches = []
        ## no.masks
        inMaskShp = numpy.shape(inMasks)  # assume x dirction stacking
        inMaskNo = inMaskShp[0]
        ## looping masks
        for slice in range(inMaskNo):
            # mask
            inMask = inMasks[slice]

            # resampling
            inMask = scipy.ndimage.zoom(
                input=inMask,
                zoom=resampleFac,
                output=None,
                order=0,
                mode='constant',
                cval=0.0,
                prefilter=True
            )

            # filter thresholds
            rangStart = maskStarts[slice]
            rangStop = maskStops[slice]

            # filter
            _, resultMskOnes = Image_Process_Functions.FilterData(
                rangStarts=[rangStart],
                rangStops=[rangStop],
                dataMat=inMask,
                funType="boundary",
                ConvertVTKType=False,
                InDataType=numpy.float64
            )

            # Guassian smoothing
            resultMskOnesGaussian = scipy.ndimage.gaussian_filter(resultMskOnes, sigma=maskSigma, order=0)

            # mask
            maskOver = numpy.ma.masked_where(resultMskOnesGaussian == 0, resultMskOnesGaussian)

            # cmap
            cmapChoice = matplotlib.colors.ListedColormap([cmapChoices[slice]])

            # mask
            im = ax.imshow(
                maskOver,
                cmap=cmapChoice,
                alpha=maskTransparency
            )
            color = im.cmap(im.norm(rangStop))
            # patches
            patches.append(matplotlib.patches.Patch(color=color, label=maskLengeds[slice]))

    # plot contours
    if showContour:
        ## contour legend patches
        contourLegend = []
        legendLines = []
        ## no.masks
        contourMaskShp = numpy.shape(contourMasks)  # assume x direction stacking
        contourMaskNo = contourMaskShp[0]
        ## looping masks
        for slice in range(contourMaskNo):
            # mask
            inContour = contourMasks[slice]

            # resampling
            inContour = scipy.ndimage.zoom(
                input=inContour,
                zoom=resampleFac,
                output=None,
                order=0,
                mode='constant',
                cval=0.0,
                prefilter=True
            )

            # filter thresholds
            rangStart = contourStarts[slice]
            rangStop = contourStops[slice]

            # filter
            _, resultMskOnes = Image_Process_Functions.FilterData(
                rangStarts=[rangStart],
                rangStops=[rangStop],
                dataMat=inContour,
                funType="boundary",
                ConvertVTKType=False,
                InDataType=numpy.float64
            )

            # Guassian smoothing
            resultMskOnesGaussian = scipy.ndimage.gaussian_filter(resultMskOnes, sigma=contourSigma, order=0)

            # contours
            contours = skimage.measure.find_contours(resultMskOnesGaussian, fully_connected='high', level=contourLevel)

            # plot contour
            legendFlg = True
            for contour in contours:
                l, = ax.plot(
                    contour[:, 1],
                    contour[:, 0],
                    linewidth=contourLineWidths[slice],
                    color=contourColors[slice]
                )  # The comma is Python syntax that denotes either a single-element tuple
                if legendFlg:
                    legendLines.append(l)
                    contourLegend.append(contourRefs[slice])
                    legendFlg = False

    # set title
    ax.set_title(
        plotTitle,
        fontsize=fontSize
    )

    # legnend
    if legend:
        print(legendLines)
        print(contourLegend)
        legend1 = ax.legend(
            legendLines,
            contourLegend,
            bbox_to_anchor=(contourLegendX, contourLegendY),
            loc=contourLegendLoc,
            borderaxespad=0,
            fontsize=fontSize
        )
        ax.legend(
            handles=patches,
            bbox_to_anchor=(maskLegendX, maskLegendY),
            loc=maskLegendLoc,
            borderaxespad=0,
            fontsize=fontSize
        )
        '''
        Location String Location Code
        'best'
        0
        'upper right'
        1
        'upper left'
        2
        'lower left'
        3
        'lower right'
        4
        'right'
        5
        'center left'
        6
        'center right'
        7
        'lower center'
        8
        'upper center'
        9
        'center'
        10
        '''

        ax.add_artist(legend1)

    # colorbar
    if colorBar:
        cbar = fig.colorbar(backPlt, extend='both')
        cbar.set_label(colorBarTitle, rotation=270, fontsize=fontSize, labelpad=15)

    if showAxes:
        ax.set_xlabel(XLbl, fontsize=fontSize)
        ax.set_ylabel(YLbl, fontsize=fontSize)
    else:
        ax.axis('off')

    # resize
    if resizeX:
        ax.set_xlim([xSliceStart, xSliceFinish])
    if resizeY:
        ax.set_ylim([ySliceStart, ySliceFinish])

    ## save
    if saveImg:
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(imgOutPath, dpi=150)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Plot overlapping image time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "{}".format(rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo
