# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：SpacingModifing.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/11/30 16:07 
'''
## using simpleITK to load and save data.
import SimpleITK
def niftiSpacingSetting(work_dir,
                        output_dir,
                        spacingX,
                        spacingY,
                        spacingZ):
    itk_img = SimpleITK.ReadImage(work_dir)
    img = SimpleITK.GetArrayFromImage(itk_img)
    print("original spacing:", itk_img.GetSpacing())
    out = SimpleITK.GetImageFromArray(img)
    out.SetSpacing([spacingX, spacingY, spacingZ])
    SimpleITK.WriteImage(out, output_dir)
    print("new spacing:", itk_img.GetSpacing())

niftiSpacingSetting("E:\B_PlaqueQuantitativeAnalysis\Carotid\luyu\cal4_1.2.840.31314.141432 34.20151214081352.1631851_left.nii.gz",
                    "E:\B_PlaqueQuantitativeAnalysis\Carotid\luyu\cal4_1.2.840.31314.141432 34.20151214081352.1631851_left_resetSpacing.nii.gz",
                    0.5,
                    0.5,
                    3)



