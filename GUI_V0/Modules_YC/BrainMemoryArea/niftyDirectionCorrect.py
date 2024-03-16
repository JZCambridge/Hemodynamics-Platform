# -*- coding: UTF-8 -*-
'''
@Project ：getpyfilepath.py
@File    ：niftyDirectionCorrect.py
@IDE     ：PyCharm
@Author  ：YangChen's Piggy
@Date    ：2022/3/24 13:32
'''
#-*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
import matplotlib.widgets
import copy
import requests
import os
##############################################################################
# Standard library
import numpy
import SimpleITK
import scipy
import scipy.ndimage
from matplotlib.transforms import Affine2D
from skimage import exposure
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
"""
##############################################################################
# Hippocampus Visualisation
##############################################################################
"""
def filToCos(secret_id = '',
             secret_key = '',
             region = '',
             bucket_create = False,
             fileSize5Gless = True,
             bucket_nam = '',
             localFilPth = None,
             ParentDir = "",
             SecLDir = "",
             ThirdLDir = "",
             FourthLDir = ""
):
    token = None               # 使用临时密钥需要传入 Token，默认为空,可不填
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)  # 获取配置对象
    #get client - side
    client = CosS3Client(config)
    # creat bucket
    if bucket_create :
        response = client.create_bucket(Bucket= bucket_nam)

    _,file_name = os.path.split(localFilPth)
    tmpobject_key = os.path.join(ParentDir, SecLDir, ThirdLDir, FourthLDir,file_name)
    object_key = tmpobject_key.replace("\\","/")

    if fileSize5Gless:
        with open(localFilPth, 'rb') as fp:
            response = client.put_object(
                Bucket=bucket_nam,  # Bucket 由 BucketName-APPID 组成
                Body=fp,
                Key=object_key,
                EnableMD5=True
            )
    else:
        response = client.upload_file(
            Bucket=bucket_nam,
            LocalFilePath= localFilPth,  # 本地文件的路径
            Key= object_key,  # 上传到桶之后的文件名
            PartSize=1,  # 上传分成几部分
            MAXThread=10,  # 支持最多的线程数
            EnableMD5=False  # 是否支持MD5
        )
    print(response['ETag'])
def LoadNifti(niiPath = None):
    # Load NIFTI as matrix
    # Output data
    if niiPath is None:
        print("please input niipath!")
    else:
        itkImag = SimpleITK.ReadImage(niiPath)

        # modify dicom image direction
        print("itkImag.GetDirection()", itkImag.GetDirection())
        #reorirentation
        itkImag = SimpleITK.DICOMOrient(itkImag, 'LPS')
        print("itkImag.DICOMOrient()", itkImag.GetDirection())
        #save nii.gz
        SimpleITK.WriteImage(itkImag, 'E:/test4.nii.gz')
        itkData = SimpleITK.GetArrayFromImage(itkImag)
# # simple itk reoriented method
#         # setup other image characteristics
#         image_out = SimpleITK.GetImageFromArray(itkData)
#         image_out.SetOrigin(itkImag.GetOrigin())
#         image_out.SetSpacing(itkImag.GetSpacing())
#         # set to RAI
#         image_out.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))
#         SimpleITK.WriteImage(image_out, 'E:/test4.nii.gz')
#         # itkImag.SetDirection((-1, 0, 0, 0, -1, 0, 0, 0, 1)) #???????????????????yang
#         itkData_out = SimpleITK.GetArrayFromImage(image_out)
#         print("Matrixsum",numpy.sum(itkData-itkData_out))
#         print("Reorientation", numpy.around(image_out.GetDirection()))
#
#         itkImag_2 = SimpleITK.ReadImage(r'E:/test1.nii.gz')
#         # modify dicom image direction
#         print("itkImag_2.GetDirection()", itkImag_2.GetDirection())
#         itkData_2 = SimpleITK.GetArrayFromImage(itkImag_2)
#
#


        # get voxel spacing (for 3-D image)
        print("Load: " + niiPath)
        try:
            spacing = itkImag.GetSpacing()
            spacing_x = spacing[0]
            spacing_y = spacing[1]
            spacing_z = spacing[2]
        except:
            pass
    # Return values
    # return  itkData, itkImag
    return  itkData, itkImag   #yang

def imgPlaneDirect(itkImag, AnatomicalDirect = 'Sagittal'):
    direction_ori = numpy.around(itkImag.GetDirection())  # [-0. -0. -1.  1.  0. -0.  0.  -1.  0.]
    direction_reshp = numpy.reshape(direction_ori, (3,3))
    direction = numpy.zeros_like(direction_reshp)
    direction[0] += direction_reshp[0]
    direction[1] += direction_reshp[1]
    direction[2] -= direction_reshp[2]
    direction_column = numpy.sum(direction, axis=1)

    # print("reshape",direction)
    # if sum(map(abs, direction_ori)) == 3: # if the direction list is a standard list with three '1' facts
    #     # Sagittal plane
    #     if AnatomicalDirect == 'Sagittal':
    #         if direction[0,0] != 0:
    #             imgDirect = "X"
    #         elif direction[0,1] != 0:
    #             imgDirect = "Y"
    #         elif direction[0,2] != 0:
    #             imgDirect = "Z"
    #         angle_refer = direction_column[1] + direction_column[2]
    #         if angle_refer >0:
    #             angle_rotate = 0
    #         elif angle_refer ==0:
    #             angle_rotate = 90
    #         elif angle_refer <0:
    #             angle_rotate = 180
    #
    #     # Coronal plane
    #     if AnatomicalDirect == 'Coronal':
    #         if direction[1,0] != 0:
    #             imgDirect = "X"
    #         elif direction[1,1] != 0:
    #             imgDirect = "Y"
    #         elif direction[1,2] != 0:
    #             imgDirect = "Z"
    #         angle_refer = direction_column[0] + direction_column[2]
    #         if angle_refer >0:
    #             angle_rotate = 0
    #         elif angle_refer ==0:
    #             angle_rotate = 90
    #         elif angle_refer <0:
    #             angle_rotate = 180
    #     # Transverse plane/Axial plane
    #     if AnatomicalDirect == 'Transverse':
    #         if direction[2,0] != 0:
    #             imgDirect = "X"
    #         elif direction[2,1] != 0:
    #             imgDirect = "Y"
    #         elif direction[2,2] != 0:
    #             imgDirect = "Z"
    #         angle_refer = direction_column[0] + direction_column[1]
    #         if angle_refer >0:
    #             angle_rotate = 0
    #         elif angle_refer ==0:
    #             angle_rotate = 90
    #         elif angle_refer <0:
    #             angle_rotate = 180
    # else:
    #     print("Please standardlize the direction matrix! ")
    imgDirect = "X"  #yang
    angle_rotate = 0
    return imgDirect , angle_rotate

def FilterData(
        rangStarts=[0],
        rangStops=[0],
        dataMat=[0],
        funType="single value"):
    # initial value
    dataMatMsked = None
    dataMatMsks = None
    DataType = dataMat.dtype.type
    # equal to single vlaues
    if funType == "single value":
        print("single value")
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))

        for rangStart in rangStarts:
            print("mask value")
            print(rangStart)
            dataMatTFMsk = dataMat == rangStart
            dataMatMsks += 1 * dataMatTFMsk

        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)

        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input is filtered with: " + str(rangStarts))

    # equal to single vlaues
    if funType == "not single value":
        print("not single value")
        dataMatMsks = numpy.ones(numpy.shape(dataMat))

        for rangStart in rangStarts:
            print("mask value")
            print(rangStart)

            dataMatTFMsk = dataMat != rangStart
            dataMatMsks = dataMatMsks * dataMatTFMsk

        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)

        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input keep without: " + str(rangStarts))

    # greater than a single vlaue
    if funType == "single value greater":
        print("single value greater")
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))

        for rangStart in rangStarts:
            print("mask value")
            print(rangStart)
            dataMatTFMsk = dataMat > rangStart
            dataMatMsks += 1 * dataMatTFMsk

        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input is filtered with: " + str(rangStarts))

    # less than a single vlaue
    if funType == "single value less":
        print("single value less")
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))

        for rangStart in rangStarts:
            print("mask value")
            print(rangStart)
            dataMatTFMsk = dataMat < rangStart
            dataMatMsks += 1 * dataMatTFMsk

        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input is filtered with: " + str(rangStarts))

    # in boundaries
    if funType == "boundary":
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))
        for rangStart, rangStop in zip(rangStarts, rangStops):  # loop simultaneously
            # Given wrong order of boundary
            if rangStart > rangStop:
                print(
                    "Boundary order wrong! Range lowest value is: " + str(rangStart) + "Range highest value is: " + str(
                        rangStop))
                print("Automatic switch boundary")
                dataMatTFMskStrt = dataMat >= rangStop  # included boundary
                dataMatTFMskStop = dataMat <= rangStart
                dataMatTFMsk = numpy.multiply(dataMatTFMskStrt, dataMatTFMskStop)
                # stack mask data
                dataMatMsks += 1 * dataMatTFMsk
            else:
                dataMatTFMskStrt = dataMat >= rangStart  # included boundary
                dataMatTFMskStop = dataMat <= rangStop
                dataMatTFMsk = numpy.multiply(dataMatTFMskStrt, dataMatTFMskStop)
                # stack mask data
                dataMatMsks += 1 * dataMatTFMsk
        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        # mask ori Mat Data
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input boundary is filtered with: " + str(rangStarts) + " " + str(rangStops))

    # in boundaries
    if funType == "outside boundary":
        dataMatMsks = numpy.zeros(numpy.shape(dataMat))
        for rangStart, rangStop in zip(rangStarts, rangStops):  # loop simultaneously
            # Given wrong order of boundary
            if rangStart > rangStop:
                print(
                    "Boundary order wrong! Range lowest value is: " + str(rangStart) + "Range highest value is: " + str(
                        rangStop))
                print("Automatic switch boundary")
                dataMatTFMskStrt = dataMat <= rangStop  # included boundary
                dataMatTFMskStop = dataMat >= rangStart
                dataMatTFMsk = numpy.multiply(dataMatTFMskStrt, dataMatTFMskStop)
                # stack mask data
                dataMatMsks += 1 * dataMatTFMsk
            else:
                dataMatTFMskStrt = dataMat <= rangStart  # included boundary
                dataMatTFMskStop = dataMat >= rangStop
                dataMatTFMsk = numpy.multiply(dataMatTFMskStrt, dataMatTFMskStop)
                # stack mask data
                dataMatMsks += 1 * dataMatTFMsk
        # mask dataMatTFMsks with 0, 1 only
        dataMatTFMsks = dataMatMsks > 0
        dataMatMsks = dataMatTFMsks.astype(DataType)
        # mask ori Mat Data
        dataMatMsked = numpy.multiply(dataMatMsks, dataMat)
        dataMatMsked = dataMatMsked.astype(DataType)
        print("Input outside boundary is filtered with: " + str(rangStarts) + " " + str(rangStops))

    mskVals = dataMatMsked
    mskOnes = dataMatMsks

    return mskVals, mskOnes

def slider3Display(matData1=[0],
                   matData2=[0],
                   matData3=[0],
                   fig3OverLap=True,
                   ask23MatData=False,
                   OneOverTwo=False,
                   ContourOver=False,
                   slicDiect='X',
                   initSlice = 37/130,
                   plotRange=[False, False, False],
                   winMin=[0, 0, 0],
                   winMax=[100, 100, 100],
                   angle_rotation=0,
                   cmapChoice='gray',
                   imagSavPth=''):
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
        dirErrMsg = "Plotting: no direction match: " + str(
            slicDiect) + " Use default 'X'"
        print("Plotting: no direction match: " + str(
            slicDiect) + " Use default 'X'")
        slicDiect = 'X'

    # marData1 shape
    matData1Shape = numpy.shape(matData1)

    # second data
    if ask23MatData:
        print("ask23MatData error!")
    elif not ask23MatData:
        if numpy.shape(numpy.shape(matData2)) == (1,):
            # create empty one if no data and not ask to load
            matData2 = numpy.zeros(matData1Shape)

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
        figsize = numpy.shape(matData1)
        if slicDiect == 'Z': #the direction is fliped in simple itk
            figMat1 = matData1[int(initSlice*figsize[0])]
            figMat2 = matData2[int(initSlice*figsize[0])]
        if slicDiect == 'Y':
            figMat1 = matData1[:, int(initSlice*figsize[1]), :]
            figMat2 = matData2[:, int(initSlice*figsize[1]), :]
        if slicDiect == 'X':
            figMat1 = matData1[:, :, int(initSlice*figsize[2])]
            figMat2 = matData2[:, :, int(initSlice*figsize[2])]
        # figMat1 = numpy.rot90(figMat1, int(angle_rotation/90))#???????????????????????????????????????????????????yang
        figMat1 = numpy.flip(figMat1, 0)#???????????????????????????????????????????????????yang
        figMat1 = Contrast_enhancement(figMat1)
        # figMat2 = numpy.rot90(figMat2, int(angle_rotation/90))#??????????????????????yang
        figMat2 = numpy.flip(figMat2, 0)
        fig1, ax1 = plt.subplots(nrows=1, ncols=1)  # create figure & 1 axis

        # plot range
        if not OneOverTwo:  # !!!! intially wrong definition of on over two
            # should be TWO over ONE
            if plotRange[2]:
                ax121 = ax1.imshow(
                    figMat1,
                    vmin=winMin[0],
                    vmax=winMax[0],
                    cmap=cmapChoice
                )
            else:
                ax121 = ax1.imshow(
                    figMat1,
                    vmin=numpy.min(figMat1),
                    vmax=numpy.max(figMat1),
                    cmap=cmapChoice
                )
            # mask creation for on the non-zero region
            maskOver = numpy.ma.masked_where(figMat2 == 0, figMat2)
            ax122 = ax1.imshow(
                maskOver,
                vmin=numpy.min(figMat2),
                vmax=numpy.max(figMat2),
                alpha=0.5,
                cmap="viridis" # plasma   cividis inferno
            )
            # ax1.set_title(title, fontsize=fs)
            ax1.axis('off')

        elif OneOverTwo:
            if plotRange[2]:
                ax121 = ax1.imshow(
                    figMat2,
                    vmin=winMin[1],
                    vmax=winMax[1],
                    cmap=cmapChoice
                )
            else:
                ax121 = ax1.imshow(
                    figMat2,
                    vmin=numpy.min(figMat2),
                    vmax=numpy.max(figMat2),
                    cmap=cmapChoice
                )
            # transparent '0's
            maskOver = numpy.ma.masked_where(figMat1 == 0, figMat1)
            ax122 = ax1.imshow(
                maskOver,
                vmin=numpy.min(figMat1),
                vmax=numpy.max(figMat1),
                alpha=0.5,
                cmap="viridis"
            )
            ax1.axis('off')

        plt.show(block=True)
        fig1.savefig(imagSavPth, bbox_inches='tight',pad_inches = 0)  # save the figure to file
        # plt.savefig('E:/to.png')
        plt.close(fig1)  # close the figure window

def Contrast_enhancement(img):
    newimg = numpy.array(copy.deepcopy(img)) #this makes a real copy of img, if you dont, any change to img will change newimg too
    temp_img=numpy.array(copy.deepcopy(img))*3/2+50/255
    newimg = numpy.where(newimg<=100,temp_img,newimg)
    return newimg



def GetNifity_url(urlPath,output_path):
    response = requests.get(urlPath)
    # output_path = os.path.join('n4_bias', category, name)
    if not os.path.exists(output_path):
        with open(output_path, 'wb') as f:
            f.write(response.content)
            f.flush()

class BrainMemoryAreaScreenshotMain:
    def __init__(self,
                 cta_url,
                 mask_url,
                 pngSaveNam,
                 secret_id='',
                 secret_key='',
                 region='',
                 bucket_create=False,
                 bucket_nam='',
                 ParentDir="knowledgebase",
                 SecLDir="test",
                 ThirdLDir="brain",
                 FourthLDir=""
                 ):
        self.secret_id =secret_id
        self.secret_key =secret_key
        self.region =region
        self.bucket_create =bucket_create
        self.bucket_nam =bucket_nam
        self.localFilPth =None
        self.ParentDir =ParentDir
        self.SecLDir =SecLDir
        self.ThirdLDir =ThirdLDir
        self.FourthLDir =FourthLDir
        self.cta_url = cta_url
        self.mask_url = mask_url
        self.pngSaveNam = pngSaveNam
        self.InitProcess()

    def InitProcess(self):
        # # initial definition
        # # self.CTAPath = os.path.join(os.getcwd(), "brain_preproc_img.nii.gz")
        # self.CTAPath = "brain_preproc_img.nii.gz"
        # # self.Maskpath = os.path.join(os.getcwd(), "cleanup_labelmap96_src.nii.gz")
        # self.Maskpath = "cleanup_labelmap96_src.nii.gz"
        # GetNifity_url(self.cta_url,self.CTAPath)
        # GetNifity_url(self.mask_url,self.Maskpath)


        # self.CTAPath = r"E:\B_BrainVolumn\brtst\1.3.6.1.4.1.41390.1.1.1412051.20220228.78221\brain_preproc_img.nii.gz"  #yang
        # self.Maskpath = r"E:\B_BrainVolumn\brtst\1.3.6.1.4.1.41390.1.1.1412051.20220228.78221\cleanup_labelmap96_src.nii.gz"

        # self.CTAPath = r"E:\B_BrainVolumn\brtst\1.3.6.1.4.1.41390.1.1.0363010001.20220219.392566633\brain_preproc_img.nii.gz"  #yang
        # self.Maskpath = r"E:\B_BrainVolumn\brtst\1.3.6.1.4.1.41390.1.1.0363010001.20220219.392566633\cleanup_labelmap96_src.nii.gz"

        # self.CTAPath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  Philips_T1W_3D_TFE_ref_20211017170838_901\brain_preproc_img.nii.gz"  #yang
        # self.Maskpath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  Philips_T1W_3D_TFE_ref_20211017170838_901\cleanup_labelmap96_src.nii.gz"

        # self.CTAPath = r"E:\B_BrainVolumn\0214\outputTOZHOU\brain_preproc_img.nii.gz"  #yang
        # self.Maskpath = r"E:\B_BrainVolumn\0214\outputTOZHOU\cleanup_labelmap96_src.nii.gz"

        # self.CTAPath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  GE_Sag_3D-MPRAGE_20211017181005_3\brain_preproc_img.nii.gz"  # yang
        # self.Maskpath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  GE_Sag_3D-MPRAGE_20211017181005_3\cleanup_labelmap96_src.nii.gz"

        # self.CTAPath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  Philips_T1W_3D_TFE_ref_20211017170838_901\brain_preproc_img.nii.gz"  # yang
        # self.Maskpath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  Philips_T1W_3D_TFE_ref_20211017170838_901\cleanup_labelmap96_src.nii.gz"

        # self.CTAPath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  Siemens_t1_mprage_tra_p2_iso_20211017164000_14\brain_preproc_img.nii.gz"  # yang
        # self.Maskpath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  Siemens_t1_mprage_tra_p2_iso_20211017164000_14\cleanup_labelmap96_src.nii.gz"

        # self.CTAPath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  UIH_t1_gre_fsp_3d_sag_20211015145901_501\brain_preproc_img.nii.gz"  # yang
        # self.Maskpath = r"E:\B_BrainVolumn\0214\AladdinBrain2_Bo Meifeng  UIH_t1_gre_fsp_3d_sag_20211015145901_501\cleanup_labelmap96_src.nii.gz"

        self.imgSavePth = os.path.join(os.getcwd(), self.pngSaveNam)
        self.sliceDiect = None
        self.initSlice = 37 / 130
        self.labelLst = [13, 26]
        self.newVal = '1'
        self.angle_rotation = None
        self.outputData = None
        self.outputDataOnes = None
        self.CTA = None
        self.inMsk = None

    def LoadCTAData(self):
        # load two data
        if self.CTAPath is None:
            print("error,please input the nifity file path ")
        else:
            self.CTAOriData, self.CTAImag = LoadNifti(niiPath=self.CTAPath,)
            self.sliceDiect, self.angle_rotation = imgPlaneDirect(self.CTAImag, AnatomicalDirect='Sagittal')

    def CTAData_Ehancement(self):
        # Equalization
        img_eq = exposure.equalize_hist(self.CTAOriData)

        # Adaptive Equalization
        # 参数2：Clipping limit, normalized between 0 and 1 (higher values give
        # more contrast).
        self.CTAOriData_adapteq = exposure.equalize_adapthist(img_eq, clip_limit=0.005)



    def LoadImage(self):
        # load data
        if self.Maskpath is None:
            print("error,please input the Mask file path ")
        else:
            self.ImgDatOriData,self.MskImag = LoadNifti(niiPath=self.Maskpath,)

    def FilterValues(self):
        # get array of values
        if not self.labelLst:
            self.lstOut = []
        else:
            self.lstOut = self.labelLst
        # Filter value
        self.dataFilterVals, dataFilterOnes = FilterData(
            rangStarts=self.lstOut,
            dataMat=self.ImgDatOriData,
            funType="single value"
        )

        # set new values
        if self.newVal == "":
            self.dataFilterNewVals = dataFilterOnes
        else:
            # get new mask value
            try:
                factor = float(self.newVal)
            except:
                print("Cannot get new mask value")
                factor = 1
            # set new mask value
            self.dataFilterNewVals = dataFilterOnes * factor

        self.outputData = copy.deepcopy(self.dataFilterNewVals)
        try:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=self.ImgDatOriData.dtype.type
            )
        except:
            self.outputDataOnes = numpy.array(
                (self.outputData != 0) * 1,
                dtype=numpy.int16)

    def PlotOVerlap(self):
        # get inputs
        # Use_Plt.slider3Display(
        slider3Display(
            matData1=self.CTAOriData_adapteq,
            matData2=self.outputData,
            matData3=[0],
            fig3OverLap=True,
            ask23MatData=False,
            slicDiect=self.sliceDiect,
            initSlice = self.initSlice,
            plotRange=[False, False, False],
            winMin=[300.7, 0, 300.7],
            winMax=[601.4, 255, 601.4],
            angle_rotation=self.angle_rotation,
            imagSavPth= self.imgSavePth
        )

    def remve_cta_maskfil(self):
        pass
        # os.remove( self.CTAPath )
        # os.remove( self.Maskpath)

cta_url = "https://cdn.tenoke.com/knowledgebase/test/brain/1.2" \
               ".156.112605.189250946343691.20220218223940.2.8032.1" \
               "/brain_preproc_img.nii.gz"
mask_url = "https://cdn.tenoke.com/knowledgebase/test/brain/1.2" \
                ".156.112605.189250946343691.20220218223940.2.8032.1" \
                "/cleanup_labelmap96_src.nii.gz"
BMA = BrainMemoryAreaScreenshotMain(cta_url,
                                    mask_url,
                                     pngSaveNam= "hippocampus.png",
                                     secret_id='',
                                     secret_key='',
                                     region='ap-shanghai',
                                     bucket_create=False,
                                     bucket_nam='open-1259166643',
                                     ParentDir="knowledgebase",
                                     SecLDir="test",
                                     ThirdLDir="brain",
                                     FourthLDir=""
                                    )
BMA.LoadCTAData()
BMA.CTAData_Ehancement()
BMA.LoadImage()
BMA.FilterValues()
BMA.PlotOVerlap()
BMA.remve_cta_maskfil()
print("done")



# import numpy
# alpha = numpy.pi/2
# beta = 0
# gamma = -numpy.pi/2
# A = numpy.array([[numpy.cos(gamma), -numpy.sin(gamma), 0],
#                 [numpy.sin(gamma), numpy.cos(gamma), 0],
#                 [0, 0, 1]])
# B = numpy.array([[numpy.cos(beta), 0, numpy.sin(beta)],
#                 [0, 1, 0],
#                 [-numpy.sin(beta), 0, numpy.cos(beta)]
#                 ])
# C = numpy.array([[1, 0, 0],
#                  [0, numpy.cos(alpha), -numpy.sin(alpha)],
#                 [0, numpy.sin(alpha), numpy.cos(alpha)],
#                 ])
# inMat = numpy.array([0,0,-1,1,0,0,0,1,0]).reshape(3,3)
# print("inMat", inMat)
# outMat = numpy.matmul(numpy.matmul(numpy.matmul(inMat, numpy.linalg.inv(C)), numpy.linalg.inv(B)), numpy.linalg.inv(A)).astype(int)
# print("outMat", outMat)
#
# import numpy as np
#
# # rotate_matrix = [[-0.0174524064372832, -0.999847695156391, 0.0],
# #                  [0.308969929589947, -0.00539309018185907, -0.951056516295153],
# #                  [0.950911665781176, -0.0165982248672099, 0.309016994374948]]
# # tmpRM = numpy.array([0,0,-1,1,0,0,0,1,0]).reshape(3,3)
# # tmpRM = numpy.array([1,0,0,0,1,0,0,0,1]).reshape(3,3)
# # tmpRM = numpy.array([0.866,0.433,0.25,0,0.5,-0.866,-0.5,0.75,0.433]).reshape(3,3)
# #inverse  tmpRM
# # RM = numpy.linalg.inv(tmpRM)
# # RM = numpy.array([0.866,0.433,0.25,0,0.5,-0.866,-0.5,0.75,0.433]).reshape(3,3)
# RM = numpy.array([0,0,-1,0,-1,0,-1,0,0]).reshape(3,3)
# # uni_Matrix = tmpRM.dot(RM)
# print("iverse matrix", RM)
# # print("unit matrix", uni_Matrix)
# # RM = np.array(rotate_matrix)
# #  tait_bryan angles
# def rotateMatrixToEulerAngles(R):
#     theta_z = np.arctan2(RM[1, 0], RM[0, 0])
#     # theta_y = np.arctan2(-1 * RM[2, 0], np.sqrt(RM[2, 1] * RM[2, 1] + RM[2, 2] * RM[2, 2]))
#     theta_y = np.arctan2(-1 * RM[2, 0], np.sqrt(1 - RM[2, 0] * RM[2, 0]))
#     theta_x = np.arctan2(RM[2, 1], RM[2, 2])
#     print(f"Euler angles:\ntheta_z: {theta_z}\ntheta_y: {theta_y}\ntheta_x: {theta_x}")
#     return theta_z, theta_y, theta_x
#
#
#
# #
# def rotateMatrixToEulerAngles2(R):
#     theta_z = np.arctan2(RM[1, 0], RM[0, 0]) / np.pi * 180
#     # theta_y = np.arctan2(-1 * RM[2, 0], np.sqrt(RM[2, 1] * RM[2, 1] + RM[2, 2] * RM[2, 2])) / np.pi * 180
#     theta_y = np.arctan2(-1 * RM[2, 0], np.sqrt(1 - RM[2, 0] * RM[2, 0])) / np.pi * 180
#     theta_x = np.arctan2(RM[2, 1], RM[2, 2]) / np.pi * 180
#     print(f"Euler angles:\ntheta_z: {theta_z}\ntheta_y: {theta_y}\ntheta_x: {theta_x}")
#     return theta_z, theta_y, theta_x
#
# def rotateMatrixToEulerAngles3(R):
#     theta_y = np.arctan2(-1 * RM[2, 0], np.sqrt(RM[0, 0] * RM[0, 0] + RM[1, 0] * RM[1, 0])) / np.pi * 180
#     theta_z = np.arctan2(RM[1, 0]/np.cos(theta_y), RM[0, 0]/np.cos(theta_y))/ np.pi * 180
#     theta_x = np.arctan2(RM[2,1]/np.cos(theta_y), RM[2, 2]/np.cos(theta_y))/ np.pi * 180
#     print(f"333Euler angles:\ntheta_z: {theta_z}\ntheta_y: {theta_y}\ntheta_x: {theta_x}")
#     return theta_z, theta_y, theta_x
#
#
#
# if __name__ == '__main__':
#     # rotateMatrixToEulerAngles(RM)
#     rotateMatrixToEulerAngles2(RM)
#     rotateMatrixToEulerAngles3(RM)
#
# import numpy
# from numpy.linalg import  *
# from scipy.spatial.transform import Rotation as R
# # tmpRM = numpy.array([0,0,-1,1,0,0,0,1,0]).reshape(3,3)
# tmpRM = numpy.array([0,1,0,0,0,-1,-1,0,0]).reshape(3,3)
# print("det", det(tmpRM))
# # tmpRM = numpy.array([1,0,0,0,1,0,0,0,1]).reshape(3,3)
# # tmpRM = numpy.array([0.866,0.433,0.25,0,0.5,-0.866,-0.5,0.75,0.433]).reshape(3,3)
# # #inverse  tmpRM
# RM = numpy.linalg.inv(tmpRM)
# print("iverse matrix", RM)
#
# # # RM = np.array(rotate_matrix)
# r = R.from_matrix(RM)
# rota_angle = r.as_euler('zyx', degrees=True)
# print(rota_angle)