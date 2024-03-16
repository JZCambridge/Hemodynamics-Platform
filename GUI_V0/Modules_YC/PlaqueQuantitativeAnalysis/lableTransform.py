# -*- coding: UTF-8 -*-
'''
@Project ：getpyfilepath.py 
@File    ：lableTransform.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2022/3/4 15:30 
'''
import numpy as np
import nibabel as nib
import json
import os

relinkfile=open("./relink.ini",'r')
relinkeset=json.loads(relinkfile.read())
relinkfile.close()
for root,dirs,files in os.walk("./output"):
    uidlist=[]
    for file in files:
        filename=os.path.join(root,file)
        if file[-7:]==".nii.gz":
            print(filename)
            niiimg1 = nib.load(filename)
            niidata = niiimg1.get_data()
            width, height, queue = niiimg1.dataobj.shape
            for z in range(0,queue):
                for y in range(0,height):
                    for x in range(0,width):
                        try:
                            daa=str(int(niidata[x,y,z]))
                            dab=relinkeset[daa]
                            niidata[x,y,z]=dab
                        except:
                            continue
            new_image = nib.Nifti1Image(niidata,niiimg1.affine)
            nib.save(new_image, os.path.join(root,"new_"+file))
pixelset=[]