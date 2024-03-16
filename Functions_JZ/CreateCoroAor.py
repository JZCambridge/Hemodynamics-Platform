# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 20:15:57 2020

@author: yingmohuanzhou
"""
import sys
sys.path.insert(0, '.\Functions\Image_Process_Functions.py')
sys.path.insert(0, '.\Functions\Save_Load_File.py')
sys.path.insert(0, '.\Functions\VTK_Functions.py')


import Image_Process_Functions
import Save_Load_File
import Use_Plt
import VTK_Functions

#load CTA
CTAFile = Save_Load_File.OpenFilePath (dispMsg = "Load CTA NIFTI")
otherErMsg, aortaErMsg, aorMskValArrayTF, CTAOridata, CTAImg = Save_Load_File.LoadNifti(niiPath = CTAFile)

#load Aorta
AorFile = Save_Load_File.OpenFilePath (dispMsg = "Load Aorta NIFTI")
otherErMsg, aortaErMsg, aorMskValArrayTF, AorOridata, AorImg = Save_Load_File.LoadNifti(niiPath = AorFile)

#load Combo
ComboFile = Save_Load_File.OpenFilePath (dispMsg = "Load Combo NIFTI")
otherErMsg, aortaErMsg, aorMskValArrayTF, ComboOridata, ComboImg = Save_Load_File.LoadNifti(niiPath = ComboFile)

#coronary subtraction
CoronOridata = ComboOridata - AorOridata

#save data
dataMatMsked, dataMatMsks = Image_Process_Functions.FilterData (rangStarts = [0], rangStops = [0], dataMat = CoronOridata, funType = "single value")

Use_Plt.slider3Display (matData1 = CTAOridata, 
                    matData2 = dataMatMsks, 
                    matData3 = [0], 
                    fig3OverLap = True, 
                    ShareX = True, 
                    ShareY = True,
                    ask23MatData = True,
                    title = ["CTA", "Coronary mask", "Overlapping"],
                    plotRange = [True, False, False],
                    winMin = [0, 0, 0],
                    winMax = [1000, 100, 100])

#save data
niiFilePath = Save_Load_File.SaveFilePath (dispMsg = "Save Nifiti file")
Save_Load_File.MatNIFTISave (MatData = dataMatMsks, imgPath = niiFilePath, imgInfo = CTAImg)
    