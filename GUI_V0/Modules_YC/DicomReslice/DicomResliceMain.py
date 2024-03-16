# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：DicomResliceMain.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/9/27 14:53 
'''
# import pydicom
# import matplotlib.pyplot as plt
#
# ds = pydicom.dcmread(r"E:\DicomTest\2019.05.23\ser001img00001.dcm")
# plt.figure(figsize=(10, 10))
# plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
# plt.show()
#
# import numpy as np # linear algebra
# import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
# import dicom
# import os
# import scipy.ndimage
# import matplotlib.pyplot as plt
#
# from skimage import measure, morphology
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
#
# # 包含所有患者目录的根目录
# INPUT_FOLDER = '../input/sample_images/'
# patients = os.listdir(INPUT_FOLDER)
# patients.sort()
#
# def load_scan(path):
#     slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
#     slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
#     try:
#         slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
#     except:
#         slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
#
#     for s in slices:
#         s.SliceThickness = slice_thickness
#
#     return slices
#
# def get_pixels_hu(slices):
#     image = np.stack([s.pixel_array for s in slices])
#     # 转换为int16，int16是ok的，因为所有的数值都应该 <32k
#     image = image.astype(np.int16)
#
#     # 设置边界外的元素为0
#     image[image == -2000] = 0
#
#     # 转换为HU单位
#     for slice_number in range(len(slices)):
#
#         intercept = slices[slice_number].RescaleIntercept
#         slope = slices[slice_number].RescaleSlope
#
#         if slope != 1:
#             image[slice_number] = slope * image[slice_number].astype(np.float64)
#             image[slice_number] = image[slice_number].astype(np.int16)
#
#         image[slice_number] += np.int16(intercept)
#
#     return np.array(image, dtype=np.int16)
#
# first_patient = load_scan(INPUT_FOLDER + patients[0])
# first_patient_pixels = get_pixels_hu(first_patient)
# plt.hist(first_patient_pixels.flatten(), bins=80, color='c')
# plt.xlabel("Hounsfield Units (HU)")
# plt.ylabel("Frequency")
# plt.show()
#
# # 显示一个中间位置的切片
# plt.imshow(first_patient_pixels[80], cmap=plt.cm.gray)
# plt.show()
#
# def resample(image, scan, new_spacing=[1,1,1]):
#     # Determine current pixel spacing
#     spacing = np.array([scan[0].SliceThickness] + scan[0].PixelSpacing, dtype=np.float32)
#
#     resize_factor = spacing / new_spacing
#     new_real_shape = image.shape * resize_factor
#     new_shape = np.round(new_real_shape)
#     real_resize_factor = new_shape / image.shape
#     new_spacing = spacing / real_resize_factor
#
#     image = scipy.ndimage.interpolation.zoom(image, real_resize_factor, mode='nearest')
#
#     return image, new_spacing
#
# pix_resampled, spacing = resample(first_patient_pixels, first_patient, [1,1,1])
# print("Shape before resampling\t", first_patient_pixels.shape)
# print("Shape after resampling\t", pix_resampled.shape)
#
# def plot_3d(image, threshold=-300):
#
#     # Position the scan upright,
#     # so the head of the patient would be at the top facing the camera
#     p = image.transpose(2,1,0)
#
#     verts, faces = measure.marching_cubes(p, threshold)
#
#     fig = plt.figure(figsize=(10, 10))
#     ax = fig.add_subplot(111, projection='3d')
#
#     # Fancy indexing: `verts[faces]` to generate a collection of triangles
#     mesh = Poly3DCollection(verts[faces], alpha=0.70)
#     face_color = [0.45, 0.45, 0.75]
#     mesh.set_facecolor(face_color)
#     ax.add_collection3d(mesh)
#
#     ax.set_xlim(0, p.shape[0])
#     ax.set_ylim(0, p.shape[1])
#     ax.set_zlim(0, p.shape[2])
#
#     plt.show()
#
#     def largest_label_volume(im, bg=-1):
#         vals, counts = np.unique(im, return_counts=True)
#
#         counts = counts[vals != bg]
#         vals = vals[vals != bg]
#
#         if len(counts) > 0:
#             return vals[np.argmax(counts)]
#         else:
#             return None
#
#     def segment_lung_mask(image, fill_lung_structures=True):
#
#         # not actually binary, but 1 and 2.
#         # 0 is treated as background, which we do not want
#         binary_image = np.array(image > -320, dtype=np.int8) + 1
#         labels = measure.label(binary_image)
#
#         # Pick the pixel in the very corner to determine which label is air.
#         #   Improvement: Pick multiple background labels from around the patient
#         #   More resistant to "trays" on which the patient lays cutting the air
#         #   around the person in half
#         background_label = labels[0, 0, 0]
#
#         # Fill the air around the person
#         binary_image[background_label == labels] = 2
#
#         # Method of filling the lung structures (that is superior to something like
#         # morphological closing)
#         if fill_lung_structures:
#             # For every slice we determine the largest solid structure
#             for i, axial_slice in enumerate(binary_image):
#                 axial_slice = axial_slice - 1
#                 labeling = measure.label(axial_slice)
#                 l_max = largest_label_volume(labeling, bg=0)
#
#                 if l_max is not None:  # This slice contains some lung
#                     binary_image[i][labeling != l_max] = 1
#
#         binary_image -= 1  # Make the image actual binary
#         binary_image = 1 - binary_image  # Invert it, lungs are now 1
#
#         # Remove other air pockets insided body
#         labels = measure.label(binary_image, background=0)
#         l_max = largest_label_volume(labels, bg=0)
#         if l_max is not None:  # There are air pockets
#             binary_image[labels != l_max] = 0
#
#         return binary_image
#
#     segmented_lungs = segment_lung_mask(pix_resampled, False)
#     segmented_lungs_fill = segment_lung_mask(pix_resampled, True)
#
#     plot_3d(segmented_lungs, 0)

###############################################################################
import numpy as np
import pydicom
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import scipy.ndimage
import matplotlib.pyplot as plt

from skimage import measure, morphology
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 包含所有患者目录的根目录
INPUT_FOLDER = 'E:/DicomTest/'
patients = os.listdir(INPUT_FOLDER)
patients.sort()


def load_scan(path):
    slices = [pydicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

    for s in slices:
        s.SliceThickness = slice_thickness

    return slices


def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # 转换为int16，int16是ok的，因为所有的数值都应该 <32k
    image = image.astype(np.int16)

    # 设置边界外的元素为0
    image[image == -2000] = 0

    # 转换为HU单位
    for slice_number in range(len(slices)):

        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope

        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)

        image[slice_number] += np.int16(intercept)

    return np.array(image, dtype=np.int16)


first_patient = load_scan(INPUT_FOLDER + patients[0])
first_patient_pixels = get_pixels_hu(first_patient)
print("first_patient_pixels", first_patient_pixels)
# plt.hist(first_patient_pixels.flatten(), bins=80, color='c')
# plt.xlabel("Hounsfield Units (HU)")
# plt.ylabel("Frequency")
# plt.show()
#
# # 显示一个中间位置的切片
# plt.imshow(first_patient_pixels[80], cmap=plt.cm.gray)
# plt.show()
#

# pixel aspects, assuming all slices are the same
ps = first_patient.PixelSpacing
ss = first_patient.SliceThickness
ax_aspect = ps[1]/ps[0]
sag_aspect = ps[1]/ss
cor_aspect = ss/ps[0]

# plot 3 orthogonal slices
plt.figure(figsize=(10, 10))

a1 = plt.subplot(2, 2, 1)
plt.imshow(first_patient_pixels[len(first_patient)//2, :, ], cmap='gray')
a1.set_aspect(ax_aspect)

a2 = plt.subplot(2, 2, 2)
plt.imshow(imgs_ct [:, :, patient[0].pixel_array.shape[1]//2].T, cmap='gray')
a2.set_aspect(sag_aspect)

a3 = plt.subplot(2, 2, 3)
plt.imshow(imgs_ct [:, patient[0].pixel_array.shape[0]//2, :], cmap='gray')
a3.set_aspect(cor_aspect)

plt.tight_layout(rect=[0, 0.03, 1, 0.9])
plt.show()

# def resample(image, scan, new_spacing=[1,1,1]):
#     # Determine current pixel spacing
#     spacing = np.array([scan[0].SliceThickness] + scan[0].PixelSpacing, dtype=np.float32)
#
#     resize_factor = spacing / new_spacing
#     new_real_shape = image.shape * resize_factor
#     new_shape = np.round(new_real_shape)
#     real_resize_factor = new_shape / image.shape
#     new_spacing = spacing / real_resize_factor
#
#     image = scipy.ndimage.interpolation.zoom(image, real_resize_factor, mode='nearest')
#
#     return image, new_spacing
#
# pix_resampled, spacing = resample(first_patient_pixels, first_patient, [1,1,1])
# print("Shape before resampling\t", first_patient_pixels.shape)
# print("Shape after resampling\t", pix_resampled.shape)


def plot_3d(image, threshold=-300):

    # Position the scan upright,
    # so the head of the patient would be at the top facing the camera
    p = image.transpose(2,1,0)

    verts, faces = measure.marching_cubes(p, threshold)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces], alpha=0.70)
    face_color = [0.45, 0.45, 0.75]
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)

    ax.set_xlim(0, p.shape[0])
    ax.set_ylim(0, p.shape[1])
    ax.set_zlim(0, p.shape[2])

    plt.show()
plot_3d(first_patient, threshold=-300)





################################################################################
################################################################################
# import vtk
# from vtk.util import numpy_support
# import numpy
#
# PathDicom = "E:/DicomTest/CT/"
# reader = vtk.vtkDICOMImageReader()
# reader.SetDirectoryName(PathDicom)
# reader.Update()
#
# # Load dimensions using `GetDataExtent`
# _extent = reader.GetDataExtent()
# ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]
#
# # Load spacing values
# ConstPixelSpacing = reader.GetPixelSpacing()
#
# # Get the 'vtkImageData' object from the reader
# imageData = reader.GetOutput()
# # Get the 'vtkPointData' object from the 'vtkImageData' object
# pointData = imageData.GetPointData()
# # Ensure that only one array exists within the 'vtkPointData' object
# assert (pointData.GetNumberOfArrays()==1)
# # Get the `vtkArray` (or whatever derived type) which is needed for the `numpy_support.vtk_to_numpy` function
# arrayData = pointData.GetArray(0)
#
# # Convert the `vtkArray` to a NumPy array
# ArrayDicom = numpy_support.vtk_to_numpy(arrayData)
# # Reshape the NumPy array to 3D using 'ConstPixelDims' as a 'shape'
# ArrayDicom = ArrayDicom.reshape(ConstPixelDims, order='F')