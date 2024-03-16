# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：Data_Initialization.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/10/26 14:18 
'''
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
def arrayTostring(array, arryseparator = ' ', removedsymbol = ['[', ']']):
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
        #>>> arrytostring = arrayTostring(array, arryseparator = ' ', removedsymbol = ['[', ']'])
        #>>> print("arrytostring = ", arrytostring)
            arrytostring =
                    120.6669922   83.47875214  22.71462822
                    120.7276535   82.77872467  22.7862072
                    120.7466888   83.1784668   23.25130844
                    123.01153062 131.91428047  34.55538257
                    123.41004846 131.95694526  35.24022521
                    123.36766192 132.43444777  34.94282161
        """
    if array.shape:
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
#  Vtk file generation
##############################################################################
"""
def VtkFileGeneration(dataAbsPaths,
                      vtkDescription = "",
                      vtkFileFormat = "ASCII",
                      vtkTitle = "Description:\n",
                      DataSetFormat = "UNSTRUCTURED_GRID"):
    # vtk head
    vtkVersion = "# vtk DataFile Version 3.0\n"
    DataSethead = "DATASET " + DataSetFormat + "\n"
    DataSet = ""
    vtkFile = vtkVersion + vtkDescription + "\n" + vtkFileFormat + "\n" + DataSethead

    #vtk points
    points = ""
    pointsNum = 0
    pointshead = "POINTS " + str(pointsNum) + " float\n"
    pointArry2Str = ""

    # vtk cells
    cells = ""
    cellsNums = 0
    cellsCounts = 0
    cellsHead = "CELLS " + str(cellsNums) + " " + str(cellsCounts) + "\n"
    cellsArry2Str = ""

    # vtk cells type
    cellType = ""
    cellTypeHead = "CELL_TYPES " + str(cellsNums)
    cellTypeArry2Str =""

    # vtk points data head
    pointData = ""
    pointDataHead = "POINT_DATA " + str(pointsNum)
    pointDataArry2Str = ""

    # vtk scalars data
    scalarsName = ""
    scalarsHead = "SCALARS " + scalarsName + " float\n" \
                  + "LOOKUP_TABLE default\n"
    scalarsData = ""

    # vtk vectors data
    vectorsName = ""
    vectorsHead = "VECTORS " + vectorsName + " float\n"
    vectorsData = ""

    # vtk tensors data
    tensorsName = ""
    tensorsHead = "TENSORS6 " + tensorsName + " float\n"
    tensorsData = ""

    # vtk normals data
    normalsName = ""
    normalsHead = "Normals " + normalsName + " float\n"
    normalsData = ""

    for dataAbsPath in dataAbsPaths:
        if dataAbsPath:
            Npy_dict = LoadNPY(dataAbsPath)["data"]
            if "Node_id" in Npy_dict:
                if Npy_dict["Node_id"][-1] != len(Npy_dict["Node_id"]):
                    print("Warning: Node id is out-of-order， please reorder!" )

            elif "Node_coo" in Npy_dict:
                pointsArry = Npy_dict["Node_coo"]
                pointsNum += len(pointsArry)
                pointArry2Str += arrayTostring(pointsArry) + "\n"


            elif "Tetra_point_id" in Npy_dict:
                Tetra_cellsArry = Npy_dict["Tetra_point_id"]

                Tetra_cellsArry_firstColumn = \
                    Tetra_cellsArry.ndim * numpy.ones(len(Tetra_cellsArry), int)

                Tetra_cellsArry = \
                    numpy.column_stack((Tetra_cellsArry_firstColumn.T, Tetra_cellsArry))

                cellsNums += len(Tetra_cellsArry)
                cellsCounts += len(Tetra_cellsArry) * (Tetra_cellsArry.ndim + 1)

                cellsArry2Str += arrayTostring(Tetra_cellsArry) + "\n"

                cellTypeArry_Tetra = 10 * numpy.ones(len(Tetra_cellsArry), int)
                cellTypeArry2Str += arrayTostring(cellTypeArry_Tetra.T) + "\n"

            elif "Hex_point_id" in Npy_dict:
                Hex_cellsArry = Npy_dict["Hex_point_id"]

                Hex_cellsArry_firstColumn = \
                    Hex_cellsArry.ndim * numpy.ones(len(Hex_cellsArry), int)

                Hex_cellsArry = \
                    numpy.column_stack((Hex_cellsArry_firstColumn.T, Hex_cellsArry))

                cellsNums += len(Hex_cellsArry)
                cellsCounts += len(Hex_cellsArry) * (Hex_cellsArry.ndim + 1)

                cellsArry2Str += arrayTostring(Hex_cellsArry) + "\n"

                cellTypeArry_Hex = 13 * numpy.ones(len(Hex_cellsArry),
                                                           int) # vtk_wedge (=13)
                cellTypeArry2Str += arrayTostring(
                    cellTypeArry_Hex.T) + "\n"

            elif "parameter" in Npy_dict:
                if Npy_dict["parameter"] == ["X-VELOCITY", "Y-VELOCITY",
                                          "Z-VELOCITY", "NODAL_PRESSURE",
                                          "MAX_SHEAR_STRESS"]:
                    timeRange = Npy_dict["timeRange"]
                    for eachTime in timeRange:
                        vectorName = "Velocity " + str(eachTime) + "s "
                        vectorArry = Npy_dict['lst_ParamsMat' + str(eachTime)]
                        vectorArry2Str = arrayTostring(vectorArry)

                        tensorName = "Tensor " + str(eachTime) + "s "
                        tensorArry = Npy_dict['lst_ParamsMat' + str(eachTime)]
                        tensorArry2Str = arrayTostring(tensorArry)

                        normalName = "Normal " + str(eachTime) + "s "
                        normalArry = Npy_dict['lst_ParamsMat' + str(eachTime)]
                        normalArry2Str = arrayTostring(normalArry)



            points = pointshead + pointArry2Str


            cells = cellsHead + cellsArry2Str

            cellType = cellTypeHead + cellTypeArry2Str







    #
    #         msg = "Load Node coordinates successfully."
    #     if "Element_id" in Npy_dict:
    #         meshio_cellsArry = Npy_dict["Element_id"]
    #         meshio_cells = arrayTostring(meshio_cellsArry)
    #         if meshio_cellsArry.ndim == 4:
    #

    #         meshio_points = arrayTostring(meshio_pointsArry)
    #         msg = "Load Node coordinates successfully."
    #
    # else:
    #     self.UpdateMsgLog(msg="***********\nWarning input filepath not exit!")

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



# tst = numpy.load(r"E:\paraview\tiantan\Wall_L\extractResults\Solid_Nodecoo_Dic.npy", allow_pickle=True)
# #print(tst)
# meshdata = tst.item()['Node_id']
#
# enoarryInit = numpy.load(r"E:\paraview\tiantan\Wall_L\extractResults\Solid_TetraElmnt_NdIfo_Dic.npy", allow_pickle=True)
# enoarry = enoarryInit.item()['point_id']
#
#
# lstarryInit = numpy.load(r"E:\paraview\tiantan\Wall_L\extractResults\Solid_lst_ParamsDic.npy", allow_pickle=True)
# lstarry = lstarryInit.item()
# print("lstarry",lstarry)


#updatedenoarry =  arryValuesUpdata(enoarry, meshdata )
# #meshdata.sort(axis=0)
#print(type(meshdata), len(meshdata),meshdata)
# print(type(enoarry), len(enoarry),enoarry)
# print(type(updatedenoarry), len(updatedenoarry),updatedenoarry)
# print("updatedenoarry unique", len(numpy.unique(updatedenoarry)),numpy.unique(updatedenoarry))




