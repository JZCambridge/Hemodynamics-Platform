# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：Data_Initialization.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/10/26 14:18 
'''

import os
import sys

# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_YC')
sys.path.insert(0, '../Functions_JZ')
# import Preprocess_Mask
from datetime import datetime
import  CFD_FEA_Post_Process
"""
##############################################################################
#  function: name
#  UnstrucutredGrid data generation: meshio_DataGenerate
##############################################################################
"""


"""
##############################################################################
# standard library
##############################################################################
"""
# standard library
import os
import numpy
# import meshio
# tripartite library
# selfdefined library


"""
##############################################################################
#  Matrix Module
#  convert an array to plain text
##############################################################################
"""
def arrayTostring(array, arryseparator = ' ', removedsymbol = ["[" , "]"]):
    """
        Dscription: convert an array to plain text

        Parameters
        ----------
        array: numpy.ndarray
            the array of each point coordinates
        arryseparator: str
            the separator between array's element
        removesymbol: the list of removed symbol
             eg:removedsymbol = [ '[', ']']

        Examples
        --------
        #>>> array= [[120.6669922 ,  83.47875214,  22.71462822],
                   [120.7276535 ,  82.77872467,  22.7862072 ],
                   [120.7466888 ,  83.1784668 ,  23.25130844],
                   [123.01153062, 131.91428047,  34.55538257],
                   [123.41004846, 131.95694526,  35.24022521],
                   [123.36766192, 132.43444777,  34.94282161]]
        #>>> Arry2String = arrayTostring(array, arryseparator = ' ', removedsymbol = ['[', ']'])
        #>>> print("Arry2String = ", Arry2String)
            Arry2String =
                    120.6669922   83.47875214  22.71462822
                    120.7276535   82.77872467  22.7862072
                    120.7466888   83.1784668   23.25130844
                    123.01153062 131.91428047  34.55538257
                    123.41004846 131.95694526  35.24022521
                    123.36766192 132.43444777  34.94282161
        """
    if array.shape:
        numpy.set_printoptions(threshold=numpy.inf)  # 将数组的元素全部打印出来。
        ndarraystrInit = numpy.array2string(array, separator = arryseparator)
        if removedsymbol:
            for each_symbol in removedsymbol:
                ndarraystrInit = ndarraystrInit.replace(each_symbol, '')
            ndarraystrInit.strip()
    else:
        raise IOError("This array is empty, please read a valid array! ")
    return ndarraystrInit
"""
##############################################################################
#  Matrix Module
#  updata the values in a matrix with new values
##############################################################################
"""
def arryValuesUpdata(OriArry, oldValue,
                     newValue = None
):
    """
        Dscription: convert an array to plain text

        Parameters
        ----------
        oldValue: numpy.ndarray
            1d array of the values in the initial array
        newValue: numpy.ndarray
            1d array of the new values
        OriArry: numpy.ndarray
             original array

        Returns
        -------
        updatedArry : numpy.ndarray
            updated array.

        Examples
        --------
        #>>> oldValue = [2 5 6 37687 37688 37689]
        #>>> newValue = [1 2 3 34592 34593 34594]
        #>>> OriArry =  [[2   5    6   37687 5 37689]
                        [ 2 37688 6   37687 37688 37689]
                        [ 2   5       37687 37688 6]]

          updatedArry = [[1   2    3      34592     2      34594]
                        [ 1 34593  3      34592    34593   34594]
                        [ 1   2   34592   34592    34593    3   ]]

        """
    if len(OriArry):
        if len(oldValue):
            if newValue == None:
                newValue = numpy.arange(1, len(oldValue)+1)
        else:
            print("Warning: the oldValue array is empty!")

        tmpArry = OriArry.copy()
        for cont in range(len(oldValue)):
            tmpArry[OriArry == oldValue[cont]] = newValue[cont]
        updatedArry = tmpArry
    else:
        print("The original array is empty!")
    return updatedArry




"""
##############################################################################
#  Vtk File module
#  XML Vtk file generation
##############################################################################
"""
def VTU_ParameterStr(ParameterName = "",
                     ParameterType = "scalar",
                     ParameterDataStr = "",
                     DataArrayType = "Float32",
                     Fileformat = "ascii"
                   ):
    if ParameterType == "scalar":
        NumberOfComponents = "1"
    elif ParameterType == "vector":
        NumberOfComponents = "3"
    elif ParameterType == "tensor":
        NumberOfComponents = "6"
    ParameterStr = ""
    Parameter_Head = "<DataArray type=\"" + DataArrayType + "\" Name=\"" + ParameterName + "\"" \
                   + " NumberOfComponents=\"" + NumberOfComponents +"\" " \
                   + "format=\"" + Fileformat + "\" >\n"
    Parameter_End = "</DataArray>\n"
    ParameterStr += Parameter_Head + ParameterDataStr + "\n" \
                 + Parameter_End
    return ParameterStr

def VTU_CellDataStr(ConnectivityDataStr: str,
                    OffsetsDataStr: str,
                    TypesDataStr: str,
                    DataArrayType = "Int64",
                    Fileformat = "ascii"
                   ):
    CellDataStr = ""
    CellDataStr += "<DataArray type=\""+ DataArrayType + "\" Name=\"connectivity\" format=\""+ Fileformat + "\" >\n" \
            + ConnectivityDataStr \
            + "</DataArray>\n" \
            + "<DataArray type=\""+ DataArrayType + "\" Name=\"offsets\" format=\""+ Fileformat + "\" >\n" \
            + OffsetsDataStr \
            + "</DataArray>\n" \
            + "<DataArray type=\""+ DataArrayType + "\" Name=\"types\" format=\""+ Fileformat + "\" >\n" \
            + TypesDataStr \
            + "</DataArray>\n"
    return CellDataStr

def XMLVtkFileGeneration(dataAbsPaths: list,
                      dataSavePath="",
                      vtkDescription="",
                      FFR = 0,
                      vtkFileFormat="ASCII",
                      vtkTitle="Description:\n",
                      DataSetFormat="UnstructuredGrid"):
    numpy.set_printoptions(threshold=1e6)
    # Vtk File initialization
    vtkDataSetInfo = ""
    PvdFile = ""
    # vtk head
    vtkVersion = ""
    DataSethead = ""

    Piecehead = ""
    Pieceend = ""

    # vtk points
    points = ""
    pointsNum = 0
    pointshead = ""
    pointsend = ""
    pointArry2Str = ""

    # vtk cells
    cells = ""
    cellsNums = 0

    cellsHead = ""
    cellsend = ""

    # vtk cells connectivity, offset and types
    cellOffsetArry = []
    cellOffsetArry2Str = ""
    cellConnectivitysArry2Str = ""
    cellTypesArry2Str = ""

    # vtk points data head
    pointData = ""
    pointDataHead = ""
    pointDataArry2Str = ""

    for dataAbsPath in dataAbsPaths:
        if dataAbsPath:
            # Npy_dict = CFD_FEA_Post_Process.LoadNPY(dataAbsPath)["data"]
            Npy_dict = numpy.load(dataAbsPath, allow_pickle=True).item()

            # points id in Cells
            if "Node_id" in Npy_dict.keys():
                if Npy_dict["Node_id"][-1] != len(Npy_dict["Node_id"]):
                    print(
                        "Warning: Node id is out-of-order， please reorder!")

            # coordinates array in Points
            if "Node_coo" in Npy_dict.keys():
                pointsArry = Npy_dict["Node_coo"]
                # print("pointsArry",pointsArry,type(pointsArry))
                pointsNum += len(pointsArry)
                pointArry2Str += "<DataArray type=\"Float32\" Name=\"Points\" NumberOfComponents=\"3\" format=\"ascii\" >\n"\
                                 +arrayTostring(pointsArry) + "\n" \
                                 + "</DataArray>\n"

            # points id in cells  celltypes
            if "Tetra_point_id" in Npy_dict.keys():
                Tetra_connectivityArry = Npy_dict["Tetra_point_id"]
                Tetra_connectivityArry -= 1
                Tetra_connectivityArryOfColumns = numpy.size(Tetra_connectivityArry, 1)
                Tetra_offset_Column = \
                    Tetra_connectivityArryOfColumns * numpy.ones(
                        len(Tetra_connectivityArry), int)

                # cells numbers and counts in cellsHead
                cellsNums += len(Tetra_connectivityArry)

                cellConnectivitysArry2Str += arrayTostring(Tetra_connectivityArry) + "\n"

                cellOffsetArry_Tetra = 10 * numpy.ones(len(Tetra_connectivityArry),
                                                     int)  # vtk_Tetra (=10)
                cellOffsetArry = numpy.append(cellOffsetArry, Tetra_offset_Column)

                cellTypesArry2Str += arrayTostring(cellOffsetArry_Tetra) + "\n"
                #print("cellOffsetArry",type(cellOffsetArry), cellOffsetArry)
            # points id in cells
            if "Hex_point_id" in Npy_dict.keys():
                Hex_connectivityArry = Npy_dict["Hex_point_id"]
                # print("Hex_connectivityArry", Hex_connectivityArry)
                Hex_connectivityArry = numpy.delete(Hex_connectivityArry, [3, 7], axis=1)
                Hex_connectivityArry -= 1
                Hex_connectivityArryOfColumns = numpy.size(Hex_connectivityArry, 1)

                Hex_offset_Column = \
                    Hex_connectivityArryOfColumns * numpy.ones(len(Hex_connectivityArry),
                                                        int)

                # cells numbers and counts in cellsHead
                cellsNums += len(Hex_connectivityArry)
                # print("Hex_connectivityArry", len(Hex_connectivityArry),
                #       len(Hex_connectivityArry) * (Hex_connectivityArryOfColumns + 1))

                cellConnectivitysArry2Str += arrayTostring(Hex_connectivityArry) + "\n"

                cellOffsetArry_Hex = 13 * numpy.ones(len(Hex_connectivityArry),
                                                   int)  # vtk_wedge (=13) vtk_voxel (=11)
                cellOffsetArry = numpy.append(cellOffsetArry,
                                              Hex_offset_Column).astype(int)
                # print("cellOffsetArry", type(cellOffsetArry),
                #       numpy.shape(cellOffsetArry), cellOffsetArry[0,])
                cellTypesArry2Str += arrayTostring(cellOffsetArry_Hex) + "\n"
                # print("cellTypesArry2Str",cellTypesArry2Str)

    # vtk head
    vtkVersion = "<?xml version=\"1.0\"?>\n"
    DataSethead = "<VTKFile type=\"" + DataSetFormat \
                + "\" version=\"1.0\" byte_order=\"LittleEndian\" " \
                  "header_type=\"UInt64\">\n"\
                + "<" + DataSetFormat + ">\n"
    Piecehead = "<Piece NumberOfPoints=\"" + str(pointsNum) \
              + "\" NumberOfCells=\"" + str(cellsNums) + "\">\n"

    vtkFileEnd = "\n" + "</PointData>\n" \
                 + "\n" + "</Piece>\n" \
                 + "\n" + "</UnstructuredGrid>" \
                 + "\n" + "</VTKFile>"

    # vtk points
    pointshead += "<Points>\n"
    pointsend += "</Points>\n"
    # vtk cells
    cellsHead += "<Cells>\n"
    cellsend += "</Cells>\n"
    #update cellOffsetArry
    for count in range(1,len(cellOffsetArry)):
        cellOffsetArry[count,] += cellOffsetArry[count-1,]
    # print("cellOffsetArry", cellOffsetArry)
    cellOffsetArry2Str += arrayTostring(cellOffsetArry) + "\n"

    points = pointshead + pointArry2Str + pointsend
    cells = cellsHead \
            +VTU_CellDataStr(cellConnectivitysArry2Str,
                             cellOffsetArry2Str,
                             cellTypesArry2Str)\
            + cellsend

    vtkDataSetInfo += vtkVersion + DataSethead

    vtkDataSetInfo += Piecehead + points + cells

    PvdFile += "<VTKFile type=\"Collection\" version=\"0.1\" byte_order=\"LittleEndian\">\n" \
               + "<Collection>\n"

    #Results File Initialization
    for dataAbsPath in dataAbsPaths:
        if dataAbsPath:
            # Npy_dict = CFD_FEA_Post_Process.LoadNPY(dataAbsPath)["data"]
            Npy_dict = numpy.load(dataAbsPath, allow_pickle=True).item()
            if "timeRange_TimesDict" in Npy_dict.keys():
                names = locals()
                count = 0
                for time in Npy_dict["timeRange_TimesDict"]:
                    # initialization
                    vtufilename = "file_" + str(count)
                    vtkFile = ""
                    vtkFileSavePth = ""
                    vtkDataSetAttributeInfo = ""

                    # velocity
                    vectors_velocityName = "Velocity"
                    vectors_velocityArry = None
                    vectors_velocityArry2Str = ""
                    velocity_Info = ""

                    # Nodal Pressure
                    scalars_NodalPressureName = "NODAL_PRESSURE"
                    scalars_NodalPressureArry = None
                    scalars_NodalPressureArry2Str = ""
                    nodalPressure_Info = ""

                    # Max Shear Stress
                    scalars_MaxShearStressName = "MAX_SHEAR_STRESS"
                    scalars_MaxShearStressArry = None
                    scalars_MaxShearStressArry2Str = ""
                    maxShearStress_Info = ""


                    # Oscillatory shear index
                    scalars_OSIName = "Oscillatory_Shear_Index"
                    scalars_OSIArry = None
                    scalars_OSIArry2Str = ""
                    OSI_Info = ""

                    # Relative residence time
                    scalars_RRTName = "Relative_Residence_Time"
                    scalars_RRTArry = None
                    scalars_RRTArry2Str = ""
                    RRT_Info = ""

                    # Time Average Pressure
                    scalars_TimeAveragePressureName = "Time_Average_Pressure"
                    scalars_TimeAveragePressureArry = None
                    scalars_TimeAveragePressureArry2Str = ""
                    TimeAveragePressure_Info = ""

                    # CT_FFR
                    scalars_CT_FFRName = "CT_FFR"
                    scalars_CT_FFRArry = None
                    scalars_CT_FFRArry2Str = ""
                    CT_FFR_Info = ""

                    # Time Average Wall Shear Stress
                    scalars_TAWSSName = "Time_Average_Wall_Shear_Stress"
                    scalars_TAWSSArry = None
                    scalars_TAWSSArry2Str = ""
                    TAWSS_Info = ""

                    # Wall Shear Stress_Vector Magnitude
                    scalars_WSS_VectorMagnitudeName = "WSSVectorMagnitude"
                    scalars_WSS_VectorMagnitudeArry = None
                    scalars_WSS_VectorMagnitudeArry2Str = ""
                    WSS_VectorMagnitude_Info = ""



                    # nodal WSS Magnitude
                    scalars_nodalWSSMagnitudeName = "WSSMagnitude"
                    scalars_nodalWSSMagnitudeArry = None
                    scalars_nodalWSSMagnitudeArry2Str = ""
                    nodalWSSMagnitude_Info = ""

                    # nodal WSS Time
                    scalars_nodalWSSTimeName = "WSS"
                    scalars_nodalWSSTimeArry = None
                    scalars_nodalWSSTimeArry2Str = ""
                    nodalWSSTime_Info = ""

                    # vtk file path
                    vtkDataSetAttributeInfo += \
                        "<PointData >\n"

                    for dataAbsPath in dataAbsPaths:
                        if dataAbsPath:
                            # Npy_dict = \
                            # CFD_FEA_Post_Process.LoadNPY(dataAbsPath)[
                            #     "data"]
                            Npy_dict = numpy.load(dataAbsPath,
                            allow_pickle=True).item()

                            if "parameter" in Npy_dict.keys():
                                if Npy_dict["parameter"] == ["X-VELOCITY",
                                                             "Y-VELOCITY",
                                                             "Z-VELOCITY",
                                                             "NODAL_PRESSURE",
                                                             "MAX_SHEAR_STRESS"]:
                                    # velocity
                                    vectors_velocityArry = Npy_dict[
                                        'lst_ParamsMat' + str(time)]
                                    vectors_velocityArry2Str = \
                                        arrayTostring(
                                        vectors_velocityArry[:,
                                        0:3])
                                    velocity_Info = VTU_ParameterStr(
                                        vectors_velocityName,
                                        "vector",
                                        vectors_velocityArry2Str)
                                    vtkDataSetAttributeInfo += velocity_Info

                                    # Nodal Pressure
                                    scalars_NodalPressureArry = Npy_dict[
                                        'lst_ParamsMat' + str(time)]
                                    scalars_NodalPressureArry2Str = \
                                        arrayTostring(
                                            scalars_NodalPressureArry[:, 3])
                                    nodalPressure_Info = VTU_ParameterStr(
                                        scalars_NodalPressureName,
                                        "scalar",
                                        scalars_NodalPressureArry2Str)
                                    vtkDataSetAttributeInfo += \
                                        nodalPressure_Info

                                    # Max Shear Stress
                                    scalars_MaxShearStressArry = Npy_dict[
                                        'lst_ParamsMat' + str(time)]
                                    scalars_MaxShearStressArry2Str = \
                                        arrayTostring(
                                            scalars_MaxShearStressArry[:,4])
                                    maxShearStress_Info = VTU_ParameterStr(
                                        scalars_MaxShearStressName,
                                        "scalar",
                                        scalars_MaxShearStressArry2Str)
                                    vtkDataSetAttributeInfo += \
                                        maxShearStress_Info

                            if "nodalOSI_UseNodes" in Npy_dict.keys():
                                # Oscillatory shear index
                                scalars_OSIArry = Npy_dict[
                                    'nodalOSI_UseNodes']
                                scalars_OSIArry2Str = \
                                    arrayTostring(
                                        scalars_OSIArry[:, 1])
                                OSI_Info = VTU_ParameterStr(
                                    scalars_OSIName,
                                    "scalar",
                                    scalars_OSIArry2Str)
                                vtkDataSetAttributeInfo += \
                                    OSI_Info

                            if "nodalRRT_UseNodes" in Npy_dict.keys():
                                # Relative residence time
                                scalars_RRTArry = Npy_dict[
                                    'nodalRRT_UseNodes']
                                scalars_RRTArry2Str = \
                                    arrayTostring(
                                        scalars_RRTArry[:, 1])
                                RRT_Info = VTU_ParameterStr(
                                    scalars_RRTName,
                                    "scalar",
                                    scalars_RRTArry2Str)
                                vtkDataSetAttributeInfo += \
                                    RRT_Info

                            if "nodeTimeAveragePressure_AllNodes_Coo" in Npy_dict.keys():
                                # Time Average Pressure
                                scalars_TimeAveragePressureArry = Npy_dict[
                                    'nodeTimeAveragePressure_AllNodes_Coo']
                                scalars_TimeAveragePressureArry2Str = \
                                    arrayTostring(
                                        scalars_TimeAveragePressureArry[:, 4])
                                TimeAveragePressure_Info = VTU_ParameterStr(
                                    scalars_TimeAveragePressureName,
                                    "scalar",
                                    scalars_TimeAveragePressureArry2Str)
                                vtkDataSetAttributeInfo += \
                                    TimeAveragePressure_Info

                                if FFR :
                                    # CT_FFR
                                    scalars_CT_FFRArry = Npy_dict[
                                        'nodeTimeAveragePressure_AllNodes_Coo']/ FFR
                                    scalars_CT_FFRArry2Str = \
                                        arrayTostring(
                                            scalars_CT_FFRArry[:,
                                            4])
                                    CT_FFR_Info = VTU_ParameterStr(
                                        scalars_CT_FFRName,
                                        "scalar",
                                        scalars_CT_FFRArry2Str)
                                    vtkDataSetAttributeInfo += \
                                        CT_FFR_Info

                            if "nodalTAWSS_UseNodes" in Npy_dict.keys():
                                # Time Average Wall Shear Stress
                                scalars_TAWSSArry = Npy_dict[
                                    'nodalTAWSS_UseNodes']
                                scalars_TAWSSArry2Str = \
                                    arrayTostring(
                                        scalars_TAWSSArry[:,1])
                                TAWSS_Info = VTU_ParameterStr(
                                    scalars_TAWSSName,
                                    "scalar",
                                    scalars_TAWSSArry2Str)
                                vtkDataSetAttributeInfo += \
                                    TAWSS_Info

                            if "nodalWSS_VectorMagnitude_UseNodes" in Npy_dict.keys():
                                # Wall Shear Stress_Vector Magnitude
                                scalars_WSS_VectorMagnitudeArry = Npy_dict[
                                    'nodalWSS_VectorMagnitude_UseNodes']
                                scalars_WSS_VectorMagnitudeArry2Str = \
                                    arrayTostring(
                                        scalars_WSS_VectorMagnitudeArry[:,1])
                                WSS_VectorMagnitude_Info = VTU_ParameterStr(
                                    scalars_WSS_VectorMagnitudeName,
                                    "scalar",
                                    scalars_WSS_VectorMagnitudeArry2Str)
                                vtkDataSetAttributeInfo += \
                                    WSS_VectorMagnitude_Info

                            if "nodalWSSMagnitude_UseNodes" in \
                                    Npy_dict.keys():
                                # nodal WSS Magnitude
                                scalars_nodalWSSMagnitudeArry = Npy_dict[
                                    'nodalWSSMagnitude_UseNodes']
                                scalars_nodalWSSMagnitudeArry2Str = \
                                    arrayTostring(
                                        scalars_nodalWSSMagnitudeArry[:,count])
                                nodalWSSMagnitude_Info = \
                                    VTU_ParameterStr(
                                    scalars_nodalWSSMagnitudeName,
                                    "scalar",
                                    scalars_nodalWSSMagnitudeArry2Str)
                                vtkDataSetAttributeInfo += \
                                    nodalWSSMagnitude_Info

                            if "nodalWSSTime_UseNodes" in \
                                    Npy_dict.keys():
                                # nodal WSS Time
                                scalars_nodalWSSTimeArry = Npy_dict[
                                    'nodalWSSTime_UseNodes']
                                scalars_nodalWSSTimeArry2Str = \
                                    arrayTostring(
                                        scalars_nodalWSSTimeArry[count,:,:])
                                nodalWSSTime_Info = \
                                    VTU_ParameterStr(
                                        scalars_nodalWSSTimeName,
                                        "vector",
                                        scalars_nodalWSSTimeArry2Str)
                                vtkDataSetAttributeInfo += \
                                    nodalWSSTime_Info

                    count += 1
                    # print("count",count)

                    # paraview pvd file
                    vtkFile = vtkDataSetInfo \
                              + vtkDataSetAttributeInfo \
                              + vtkFileEnd
                    vtkFileSavePth = dataSavePath + "/" + "CFD_file_" + str(
                        count) + ".vtu"
                    print("vtufile" + str(count))
                    with open(vtkFileSavePth, 'w') as f:
                        f.seek(0)
                        f.truncate()  # clean file
                        f.write(vtkFile)

                    # paraview pvd file
                    PvdFile += "<DataSet timestep=\"" +str(time) + "\"         file=\'" + vtkFileSavePth + "\'/>\n"
                PvdFile += "</Collection>\n" + "</VTKFile>\n"
                pvdFileSavePth = dataSavePath + "/" + "Paraview" + ".pvd"
                with open(pvdFileSavePth, 'w') as f:
                    f.seek(0)
                    f.truncate()  # clean file
                    f.write(PvdFile)

# fluid_PostResults_Dict_dict
def VTU_CellDataStr(ConnectivityDataStr: str,
                    OffsetsDataStr: str,
                    TypesDataStr: str,
                    DataArrayType = "Int64",
                    Fileformat = "ascii"
                   ):
    CellDataStr = ""
    CellDataStr += "<DataArray type=\""+ DataArrayType + "\" Name=\"connectivity\" format=\""+ Fileformat + "\" >\n" \
            + ConnectivityDataStr \
            + "</DataArray>\n" \
            + "<DataArray type=\""+ DataArrayType + "\" Name=\"offsets\" format=\""+ Fileformat + "\" >\n" \
            + OffsetsDataStr \
            + "</DataArray>\n" \
            + "<DataArray type=\""+ DataArrayType + "\" Name=\"types\" format=\""+ Fileformat + "\" >\n" \
            + TypesDataStr \
            + "</DataArray>\n"
    return CellDataStr

"""
##############################################################################
#  Meshio UnstrucutredGrid data generation
##############################################################################
"""
def meshio_DataGenerate(points,
                       cells,
                       point_data,
                       cell_data,
                       file_saving_Abspath
                       ):
    """
    Dscription: Generate unstrucutredGrid data by meshio,
       eg: "*.vtu, *.inp, *.vtk"

    Parameters
    ----------
    points: array
        the coordinates of each point
    cells: tuple of dict
        the point's relationship of each cells
    point_data: dict of array
        the correspondent filed data of each point
    cell_data: dict of array
        the correspondent filed data of each cell

    See Also
    --------
    meshio's documents

    Notes
    -----
    .vtu is a unstrucutredGrid file format
    # two triangles and one quad
    points =  [[0.0, 0.0],[1.0, 0.0],[0.0, 1.0],[1.0, 1.0],[2.0, 0.0],[2.0, 1.0],]

    cells = [("triangle", [[0, 1, 2], [1, 3, 2]]),
            ("quad", [[1, 4, 5, 3]]),]

    point_data = {"T": [0.3, -1.2, 0.5, 0.7, 0.0, -3.0]}

    cell_data = {"a": [[0.1, 0.2], [0.4]]}

    Examples
    --------
    # >>> import meshio
    # >>> meshio_DataGenerate(points,
    #                cells,
    #                point_data,
    #                cell_data,
    #                file_saving_Abspath
    #                )
    """
    mesh = meshio.Mesh(
        points,
        cells,
        # Optionally provide extra data on points, cells, etc.
        point_data,
        # Each item in cell data must match the cells array
        cell_data
    )
    mesh.write(
        file_saving_Abspath,  # str, os.PathLike, or buffer/open file
        # file_format="vtk",  # optional if first argument is a path;
        # inferred from extension
    )

"""
##############################################################################
#  Vtk File module
#  Legacy Vtk file generation
##############################################################################
"""
def LegacyVtkFileGeneration(dataAbsPaths:list,
                      dataSavePath = "",
                      vtkDescription = "",
                      vtkFileFormat = "ASCII",
                      vtkTitle = "Description:\n",
                      DataSetFormat = "UnstructuredGrid"):
    numpy.set_printoptions(threshold=1e6)
    # Vtk File initialization
    vtkDataSetInfo = ""
    vtkDataSetAttributeInfo = ""
    vtkFile = ""
    # vtk head
    vtkVersion = ""
    DataSethead = ""

    #vtk points
    points = ""
    pointsNum = 0

    pointshead = ""
    pointArry2Str = ""

    # vtk cells
    cells = ""
    cellsNums = 0
    cellsCounts = 0

    cellsHead = ""
    cellsArry2Str = ""

    # vtk points data head
    pointData = ""
    pointDataHead = ""
    pointDataArry2Str = ""

    # vtk cells types
    cellType = ""
    cellTypeHead = ""
    cellTypeArry2Str = ""

    # vtk scalars data
    scalarsName = ""
    scalarsHead = ""
    scalarsData = ""

    # vtk vectors data
    vectorsName = ""
    vectorsHead = ""
    vectorsData = ""

    # vtk tensors data
    tensorsName = ""
    tensorsHead = ""
    tensorsData = ""

    # vtk normals data
    normalsName = ""
    normalsHead = ""
    normalsData = ""

    for dataAbsPath in dataAbsPaths:
        if dataAbsPath:
            Npy_dict = CFD_FEA_Post_Process.LoadNPY(dataAbsPath)["data"]
            #Npy_dict = numpy.load(dataAbsPath, allow_pickle=True).item()
            if "Node_id" in Npy_dict.keys():
                if Npy_dict["Node_id"][-1] != len(Npy_dict["Node_id"]):
                    print("Warning: Node id is out-of-order， please reorder!")

            # coordinates array in Points
            if "Node_coo" in Npy_dict.keys():
                pointsArry = Npy_dict["Node_coo"]
                # print("pointsArry",pointsArry,type(pointsArry))
                pointsNum += len(pointsArry)
                pointArry2Str += arrayTostring(pointsArry) + "\n"

            # points id in cells  celltypes
            if "Tetra_point_id" in Npy_dict.keys():
                Tetra_cellsArry = Npy_dict["Tetra_point_id"]
                Tetra_cellsArry -= 1
                Tetra_cellsArryOfColumns = numpy.size(Tetra_cellsArry, 1)

                Tetra_cellsArry_firstColumn = \
                    Tetra_cellsArryOfColumns * numpy.ones(len(Tetra_cellsArry), int)

                Tetra_cellsArry = \
                    numpy.column_stack((Tetra_cellsArry_firstColumn.T, Tetra_cellsArry))

                # cells numbers and counts in cellsHead
                cellsNums += len(Tetra_cellsArry)
                cellsCounts += len(Tetra_cellsArry) * (Tetra_cellsArryOfColumns + 1)
                print("Tetra_cellsArry", len(Tetra_cellsArry),
                      len(Tetra_cellsArry) * (Tetra_cellsArryOfColumns + 1))

                cellsArry2Str += arrayTostring(Tetra_cellsArry) + "\n"

                cellTypeArry_Tetra = 10 * numpy.ones(len(Tetra_cellsArry), int) # vtk_Tetra (=10)
                cellTypeArry2Str += arrayTostring(cellTypeArry_Tetra.T) + "\n"

            # points id in cells
            if "Hex_point_id" in Npy_dict.keys():
                Hex_cellsArry = Npy_dict["Hex_point_id"]
                # print("Hex_cellsArry", Hex_cellsArry)
                Hex_cellsArry = numpy.delete(Hex_cellsArry, [3, 7], axis=1)
                Hex_cellsArry -= 1
                Hex_cellsArryOfColumns = numpy.size(Hex_cellsArry, 1)

                Hex_cellsArry_firstColumn = \
                    Hex_cellsArryOfColumns * numpy.ones(len(Hex_cellsArry), int)

                Hex_cellsArry = \
                    numpy.column_stack((Hex_cellsArry_firstColumn.T, Hex_cellsArry))
                # print("Hex_cellsArry",Hex_cellsArry)

                # cells numbers and counts in cellsHead
                cellsNums += len(Hex_cellsArry)
                print("Hex_cellsArry",len(Hex_cellsArry),len(Hex_cellsArry) * (Hex_cellsArryOfColumns + 1))
                cellsCounts += len(Hex_cellsArry) * (Hex_cellsArryOfColumns + 1)

                cellsArry2Str += arrayTostring(Hex_cellsArry) + "\n"

                cellTypeArry_Hex = 13 * numpy.ones(len(Hex_cellsArry),
                                                           int) # vtk_wedge (=13) vtk_voxel (=11)
                cellTypeArry2Str += arrayTostring(
                    cellTypeArry_Hex.T) + "\n"

    # vtk head
    vtkVersion = "# vtk DataFile Version 3.0\n"
    DataSethead = "DATASET " + DataSetFormat + "\n"

    # vtk points
    pointshead += "POINTS " + str(pointsNum) + " float\n"
    # vtk cells
    cellsHead += "CELLS " + str(cellsNums) + " " + str(cellsCounts) + "\n"

    # vtk points data head
    pointDataHead = "POINT_DATA " + str(pointsNum) + "\n"

    # vtk cells types
    cellTypeHead = "CELL_TYPES " + str(cellsNums) + "\n"

    points = pointshead + pointArry2Str
    cells = cellsHead + cellsArry2Str
    cellType = cellTypeHead + cellTypeArry2Str


    vtkDataSetInfo += vtkVersion + vtkDescription + "\n" + vtkFileFormat + "\n" + \
               DataSethead

    vtkDataSetInfo += points + cells + cellType + "POINT_DATA " + str(pointsNum) + "\n"

    for dataAbsPath in dataAbsPaths:
        if dataAbsPath:
            Npy_dict = CFD_FEA_Post_Process.LoadNPY(dataAbsPath)["data"]
            #Npy_dict = numpy.load(dataAbsPath, allow_pickle=True).item()

            # points id in Cells
            if "parameter" in Npy_dict.keys():
                if Npy_dict["parameter"] == ["X-VELOCITY", "Y-VELOCITY",
                                          "Z-VELOCITY", "NODAL_PRESSURE",
                                          "MAX_SHEAR_STRESS"]:
                    timeRange = Npy_dict["timeRange"]
                    count = 0
                    for eachTime in timeRange:
                        #initialization
                        vtkFile = ""
                        vtkDataSetAttributeInfo = ""
                        #velocity
                        vectors_velocityName = "Velocity_" + str(eachTime) + "s "
                        vectors_velocityArry = Npy_dict['lst_ParamsMat' + str(eachTime)]
                        vectors_velocityArry2Str = arrayTostring(vectors_velocityArry[:,0:3])

                        vector_velocitysHead = "VECTORS " + vectors_velocityName + " float\n"
                        vtkDataSetAttributeInfo += vector_velocitysHead + vectors_velocityArry2Str + "\n"

                        # Nodal Pressure
                        scalars_NodalPressureName = "NODAL_PRESSURE_" + str(eachTime) + "s "
                        scalars_NodalPressureArry = Npy_dict['lst_ParamsMat' + str(eachTime)]
                        scalars_NodalPressureArry2Str = arrayTostring(scalars_NodalPressureArry[:,3])

                        scalars_NodalPressureHead = "SCALARS " + scalars_NodalPressureName + " float\n" \
                                                    + "LOOKUP_TABLE default\n"
                        vtkDataSetAttributeInfo += scalars_NodalPressureHead + scalars_NodalPressureArry2Str + "\n"

                        # Max Shear Stress
                        scalars_MaxShearStressName = "MAX_SHEAR_STRESS_" + str(eachTime) + "s "
                        scalars_MaxShearStressArry = Npy_dict['lst_ParamsMat' + str(eachTime)]
                        scalars_MaxShearStressArry2Str = arrayTostring(scalars_MaxShearStressArry[:,4])

                        scalars_MaxShearStressHead = "SCALARS " + scalars_MaxShearStressName + " float\n" \
                                                    + "LOOKUP_TABLE default\n"
                        vtkDataSetAttributeInfo += scalars_MaxShearStressHead + scalars_MaxShearStressArry2Str + "\n"
                        vtkFile = vtkDataSetInfo + "\n" + vtkDataSetAttributeInfo

                        vtkFileSavePth = dataSavePath + "/" + "file_"+ str(count) + ".vtu"
                        with open(vtkFileSavePth, 'w') as f:
                            f.write(vtkFile)
                        count += 1
                        print("######",count)

# import re
# nas_Fil = open(r"E:\paraview\tst\1111.txt", 'r')
# nas_FilContxt = nas_Fil.read()
# CTETRAlist=re.findall(' 13', nas_FilContxt, re.M)
# CPENTAlist=re.findall(' 10', nas_FilContxt, re.M)
# print(len(CTETRAlist),len(CPENTAlist))