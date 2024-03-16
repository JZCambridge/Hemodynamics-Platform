"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by jz410 (11Apr21)
"""

# Import standard libraries
import numpy
import time
import sys
import os

# Import self-written functions
import Post_Image_Process_Functions
import Save_Load_File
import Pd_Funs

"""
##############################################################################
#Func: load the NPY and export data
##############################################################################
"""


def LoadNPY(path):
    """
    :param path: full path of NPY
    :return: Dictionary
    "error" = Boolean > Overall error in the function
    "errorMessage" = str()
    "data" = numpy.ndarray() > data matrix
    Function loads a matrix/array form the NPY file of pure array or dictionary.
    Function determines the validity of the file path.
    "error" = True when any errors occur
    "errorMessage" = Provide cues of why
    """
    # return dictionary
    retDict = {}
    retDict["error"] = False
    retDict["errorMessage"] = ""
    retDict["Message"] = "LoadNPY:\n"
    retDict["data"] = None

    # Check file exist
    if not os.path.isfile(path):
        print("Warning input filepath not exit")
        retDict["error"] = True
        retDict["errorMessage"] = "Warning input filepath not exit"
        return retDict

    # check input is .npy
    if not path.endswith('.npy'):
        print("Warning input file is not NPY")
        retDict["error"] = True
        retDict["errorMessage"] = "Warning input file is not NPY"
        return retDict

    # load file
    fileData = numpy.load(path, allow_pickle=True)

    # fileData can be dictionary or array
    if numpy.shape(fileData) == ():  # dictionary
        retDict["data"] = fileData.item()  # by default
    else:
        retDict["data"] = fileData

    # return info
    retDict["Message"] += "Load:\n{}".format(fileData)

    return retDict


"""
##############################################################################
#Func: Match all element nodes and element and face in the same order
##############################################################################
"""


def MatchElemNd(inMat,
                inCompareBase,
                inCompareBaseSameOrder):
    """
    :param inMat: element matrix [element, nodes1 to n]
    :param inCompareBase: single array that element matrix is reordered based on
    :param inCompareBaseSameOrder: single array re-arranged based on 'inCompareBase'
    :return:
    """
    # start time
    matchTStrt = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["Message"] = "MatchElemNd:\n"

    # extract element and node refs from the ref group
    inMatNd = inMat[:, 0]
    rtrnInfo["Message"] = rtrnInfo["Message"] + "# of nodes from input element: {}\n".format(numpy.shape(inMatNd))

    ## create empty mat
    orderMat = numpy.zeros(numpy.shape(inMat))
    outCompareBase = numpy.zeros(numpy.shape(inCompareBase))
    outCompareBaseSameOrder = numpy.zeros(numpy.shape(inCompareBaseSameOrder))
    orderMatRow = 0

    # find index and fill
    for elem in range(len(inCompareBase)):
        # print(elem)
        # match or pass
        try:
            rowIndex = numpy.where(inMatNd == inCompareBase[elem])[0][0]  # row index of the in mat Nd ref
            # fill in data
            orderMat[orderMatRow] = inMat[rowIndex]
            # fill in face and element
            outCompareBase[orderMatRow] = inCompareBase[elem]
            outCompareBaseSameOrder[orderMatRow] = inCompareBaseSameOrder[elem]
            orderMatRow += 1
        except:
            # print(inCompareBase[elem])
            continue

    # remove no use rows
    if orderMatRow < 0 or orderMatRow == 0:
        orderMat = None
        outCompareBase = None
        outCompareBaseSameOrder = None
    else:  # need go to end row + 1 for mat range []
        orderMat = orderMat[0:(orderMatRow)]
        outCompareBase = outCompareBase[0:(orderMatRow), None]  # create one column to force column vector
        outCompareBaseSameOrder = outCompareBaseSameOrder[0:(orderMatRow), None]

    # timing
    matchTStp = time.time()
    matchT = matchTStp - matchTStrt

    # return info
    rtrnInfo["matchInMat"] = orderMat
    rtrnInfo["orderCompareBase"] = outCompareBase
    rtrnInfo["orderCompareBaseSecond"] = outCompareBaseSameOrder
    rtrnInfo["processTime"] = matchT
    rtrnInfo["processTimeMessage"] = "------Match time: {} s------".format(matchT)
    print(rtrnInfo["processTimeMessage"])
    rtrnInfo["Message"] += rtrnInfo["processTimeMessage"]

    ## compare fully matched
    if orderMatRow == len(inCompareBase):
        rtrnInfo["allMatch"] = True
    else:
        rtrnInfo["allMatch"] = False
    ## compare no match!
    if orderMatRow == 0:
        rtrnInfo["noMatch"] = True
    else:
        rtrnInfo["noMatch"] = False

    return rtrnInfo


"""
##############################################################################
#Func: Re-order the element nodes in orders that are used to calculate the area normals
##############################################################################
"""


def MatchFaceNdOrder(emptyCheck,
                     elemNodes,
                     numberNodes,
                     faceMat):
    """
    :param emptyCheck: True/False
    :param elemNodes:
    :param numberNodes:
    :param faceMat:
    :return:
    Re-order the element nodes in orders that are used to calculate the area normals
    """
    # timing
    ndOrderStrtT = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["numberNodes"] = numberNodes
    rtrnInfo["ElemFaceNodeOrder"] = None
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["Message"] = "MatchFaceNdOrder:\n"

    ## check empty dictionary
    if emptyCheck:
        print("Input array has empty element")
        rtrnInfo["Message"] += "Input array has empty element"
        return rtrnInfo

    ## Creat empty mat
    elementNodesShp = numpy.shape(elemNodes)
    elementNodesFilter = numpy.zeros(elementNodesShp)
    ## get relevant values

    # place nodes in order
    # [elem, nd1, nd2, nd3, nd4]
    ## for hexa case
    if numberNodes == 8:
        print("Hexa-element nodes re-order")
        rtrnInfo["Message"] += "Hexa-element nodes re-order\n"
        ## Creat empty mat
        faceNodes = numpy.zeros([elementNodesShp[0], 5])

        ## first column is the element ref
        faceNodes[:, 0] = elemNodes[:, 0]

        ### for the -3 case
        #### filtering -3 rows first column is "0" - element reference
        faceDirs = [-3, -2, -1, 1, 2, 3]
        columnOrders = numpy.array([
            [5, 8, 7, 6],
            [3, 7, 8, 4],
            [2, 6, 7, 3],
            [1, 4, 8, 5],
            [1, 5, 6, 2],
            [1, 2, 3, 4]
        ])
        for faceDir in range(len(faceDirs)):
            # 0, 1 col vector
            faceTF = faceMat == faceDirs[faceDir]
            # print("shape of TF vector: {}".format(numpy.shape(faceTF)))

            # filter
            elementNodesFilter = numpy.multiply(faceTF, elemNodes)

            # add to previous space
            refRow = columnOrders[faceDir]
            # print("refRow: ")
            # print(refRow)
            # print(numpy.shape(refRow))
            faceNodes[:, 1] = faceNodes[:, 1] + elementNodesFilter[:, refRow[0]]
            faceNodes[:, 2] = faceNodes[:, 2] + elementNodesFilter[:, refRow[1]]
            faceNodes[:, 3] = faceNodes[:, 3] + elementNodesFilter[:, refRow[2]]
            faceNodes[:, 4] = faceNodes[:, 4] + elementNodesFilter[:, refRow[3]]

            # if faceDirs[faceDir] == -3:
            #     print(faceTF)
            #     print(elementNodesFilter)
            #     print(faceNodes)

    ## for tetra case
    if numberNodes == 4:
        print("Tetra-element nodes re-order")
        rtrnInfo["Message"] += "Tetra-element nodes re-order\n"
        ## Creat empty mat
        faceNodes = numpy.zeros([elementNodesShp[0], 4])

        ## first column is the element ref
        faceNodes[:, 0] = elemNodes[:, 0]

        ### for the -3 case
        #### filtering -3 rows first column is "0" - element reference
        faceDirs = [1, 2, 3, 4]
        columnOrders = numpy.array([
            [4, 2, 3],
            [1, 4, 3],
            [1, 2, 4],
            [3, 2, 1]
        ])
        for faceDir in range(len(faceDirs)):
            # 0, 1 col vector
            faceTF = faceMat == faceDirs[faceDir]
            print("shape of TF vector: %d" % (numpy.shape(faceTF)))

            # filter
            elementNodesFilter = numpy.multiply(faceTF, elemNodes)

            # add to previous space
            refRow = columnOrders[faceDir]
            print("refRow: ")
            print(refRow)
            print(numpy.shape(refRow))
            faceNodes[:, 1] = faceNodes[:, 1] + elementNodesFilter[:, refRow[0]]
            faceNodes[:, 2] = faceNodes[:, 2] + elementNodesFilter[:, refRow[1]]
            faceNodes[:, 3] = faceNodes[:, 3] + elementNodesFilter[:, refRow[2]]

    # timing
    ndOrderStpT = time.time()
    ndOrderMatchT = ndOrderStpT - ndOrderStrtT

    # return
    rtrnInfo["numberNodes"] = numberNodes
    rtrnInfo["ElemFaceNodeOrder"] = faceNodes
    rtrnInfo["processTime"] = ndOrderMatchT
    rtrnInfo["processTimeMessage"] = "------Face node rearrange time: {} s------".format(ndOrderMatchT)
    rtrnInfo["Message"] += rtrnInfo["processTimeMessage"]
    print(rtrnInfo["processTimeMessage"])

    return rtrnInfo


"""
##############################################################################
#Func: Node and element face normal calculation
##############################################################################
"""


def NdNormalCalcs(ndMat,
                  ndCooMat,
                  elemUse,
                  ndUse,
                  emptyCheck):
    """
    :param ndMat: [node ref] size = no.nodes * 1
    :param ndCooMat: [node_x, node_y, node_z] size = no.nodes * 3
    :param elemUse: [element ref] - element for the ROI; size = no.element * 1
    :param ndUse: [element_node1, element_node2, element_node3[, element_node4]]
            size = no.element * 3
    :param emptyCheck: True or False
    :return:
    Node and element face normal calculation
    """
    # timing
    normCalcStrtT = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["nodeNormal"] = None
    rtrnInfo["nodeUseCalcs"] = None
    rtrnInfo["elemNormal"] = None
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["Message"] = "NdNormalCalcs:\n"

    ## check empty dictionary
    if emptyCheck:
        print("Input element array has empty elements")
        rtrnInfo["Message"] += "Input element array has empty elements\n"
        return rtrnInfo

    # Check can only work with 3 or 4 ordered nodes
    ndMatShp = numpy.shape(ndMat)
    ndUseShp = numpy.shape(ndUse)
    if ndUseShp[1] != 3 and ndUseShp[1] != 4:
        print("Wrong node input with shape {}".format(ndUseShp))
        rtrnInfo["Message"] += "Wrong node input with shape {}\n".format(ndUseShp)

    # create empty mat
    ## elem with norm [elem, normx, normy, notmz]
    ## node with norm [useNd, normx, normy, normz]
    ## useless nd [uselessNd, 0, 0, 0]
    elemNorms = numpy.zeros([ndUseShp[0], 4])
    elemNorms[:, 0] = elemUse.T
    ndNorms = numpy.zeros([ndMatShp[0], 4])
    ndNorms[:, 0] = ndMat.T
    ndUseCalcs = numpy.zeros(ndMatShp)

    # norm cals for different elements
    ## for nodes of hexa element
    if ndUseShp[1] == 4:
        for elem in range(len(elemUse)):
            # vector
            # match the element's node with it x, y, z
            ndIndecies1 = numpy.where(ndMat == ndUse[elem][0])
            ndIndex1 = ndIndecies1[0][0]
            rowVec1 = ndCooMat[ndIndex1]
            ndIndecies2 = numpy.where(ndMat == ndUse[elem][1])
            ndIndex2 = ndIndecies2[0][0]
            rowVec2 = ndCooMat[ndIndex2]
            ndIndecies3 = numpy.where(ndMat == ndUse[elem][2])
            ndIndex3 = ndIndecies3[0][0]
            rowVec3 = ndCooMat[ndIndex3]
            ndIndecies4 = numpy.where(ndMat == ndUse[elem][3])
            ndIndex4 = ndIndecies4[0][0]
            rowVec4 = ndCooMat[ndIndex4]

            # norm
            rowVec31 = rowVec1 - rowVec3
            rowVec42 = rowVec2 - rowVec4
            ndNorm = numpy.cross(rowVec31, rowVec42)
            ndNorm = ndNorm / (numpy.linalg.norm(ndNorm))
            # print(rowVec31)
            # print(rowVec42)
            # print(ndNorm)

            # fill in normals
            ## node normal is addition/magnitude
            ndNorms[ndIndex1][1:] += ndNorm
            ndNorms[ndIndex2][1:] += ndNorm
            ndNorms[ndIndex3][1:] += ndNorm
            ndNorms[ndIndex4][1:] += ndNorm
            ndUseCalcs[ndIndex1] = 1
            ndUseCalcs[ndIndex2] = 1
            ndUseCalcs[ndIndex3] = 1
            ndUseCalcs[ndIndex4] = 1
            elemNorms[elem][1:] = ndNorm

    ## for nodes of tetra element
    if ndUseShp[1] == 3:
        for elem in range(len(elemUse)):
            # vector
            ndIndecies1 = numpy.where(ndMat == ndUse[elem][0])
            ndIndex1 = ndIndecies1[0][0]
            rowVec1 = ndCooMat[ndIndex1]
            ndIndecies2 = numpy.where(ndMat == ndUse[elem][1])
            ndIndex2 = ndIndecies2[0][0]
            rowVec2 = ndCooMat[ndIndex2]
            ndIndecies3 = numpy.where(ndMat == ndUse[elem][2])
            ndIndex3 = ndIndecies3[0][0]
            rowVec3 = ndCooMat[ndIndex3]

            # norm
            rowVec23 = rowVec3 - rowVec2
            rowVec21 = rowVec1 - rowVec2
            ndNorm = numpy.cross(rowVec23, rowVec21)
            ndNorm = ndNorm / (numpy.linalg.norm(ndNorm))
            # print(rowVec23)
            # print(rowVec21)
            # print(ndNorm)

            # fill in norms
            ndNorms[ndIndex1][1:] += ndNorm
            ndNorms[ndIndex2][1:] += ndNorm
            ndNorms[ndIndex3][1:] += ndNorm
            ndNorms[ndIndex4][1:] += ndNorm
            ndUseCalcs[ndIndex1] = 1
            ndUseCalcs[ndIndex2] = 1
            ndUseCalcs[ndIndex3] = 1
            ndUseCalcs[ndIndex4] = 1
            elemNorms[elem][1:] = ndNorm

    # calculate each node row to unit vector
    ndNorms_NoRef = ndNorms[:, 1:]
    ndNorms_NoRef_Mag = [numpy.linalg.norm(ndNorms_NoRef, axis=1)]
    ndNorms[:, 1:] = ndNorms_NoRef / numpy.transpose(ndNorms_NoRef_Mag)
    # print(ndNorms)

    # time
    normCalcStpT = time.time()
    normCalcT = normCalcStpT - normCalcStrtT

    # return
    rtrnInfo["nodeNormal"] = ndNorms
    rtrnInfo["nodeUseCalcs"] = ndUseCalcs
    rtrnInfo["elemNormal"] = elemNorms
    rtrnInfo["processTime"] = normCalcT
    rtrnInfo["processTimeMessage"] = "------Node normals calculation time: {} s------".format(normCalcT)
    print(rtrnInfo["processTimeMessage"])
    rtrnInfo["Message"] += rtrnInfo["processTimeMessage"]

    return rtrnInfo


"""
##############################################################################
#Function: compare two results
##############################################################################
"""
import matplotlib.pyplot as plt


def CompareArrayDifference(Arr1,
                           Arr2,
                           Arr1_Name="Arr1",
                           Arr2_Name="Arr1",
                           unit="Unkonwn Unit",
                           pltRestuls=False,
                           suptitle="Comparing results",
                           xlabel="Node",
                           ylabel="",
                           hideOuterLabel=False):
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = ""
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["differenceMessage"] = None
    rtrnInfo["arr1Message"] = None
    rtrnInfo["arr2Message"] = None
    rtrnInfo["differencePercentageMessage"] = None
    rtrnInfo["Message"] = ""

    # Compare shape
    checkShp = Post_Image_Process_Functions.CompareArrShape(dataMat1=Arr1,
                                                            dataMat2=Arr2,
                                                            DialogWarn=False)
    if checkShp["error"]:
        # return information
        rtrnInfo["error"] = checkShp["error"]
        rtrnInfo["errorMessage"] = checkShp["errorMessage"]
        return rtrnInfo

    ## create empty
    arrShp = numpy.shape(Arr1)
    arrDiff = numpy.zeros(arrShp)

    ## Calculate diff
    arrDiff = Arr1 - Arr2
    arrDiffShp = numpy.shape(arrDiff)

    ## show key information
    ### max/min
    arrVals = [
        numpy.max(arrDiff),
        numpy.min(arrDiff),
        numpy.max(Arr1),
        numpy.min(Arr1),
        numpy.max(Arr2),
        numpy.min(Arr2)
    ]
    rtrnInfo["differenceMessage"] = ("{Arr1:<} v.s. {Arr2:<} max//min difference ({unit:<}): "
                                     "\n{max:+.3e} // {min:+.3e}\n".format(Arr1=Arr1_Name,
                                                                           Arr2=Arr2_Name,
                                                                           unit=unit,
                                                                           max=arrVals[0],
                                                                           min=arrVals[1]))
    rtrnInfo["arr1Message"] = ("{Arr1:<} max//min ({unit:<}): "
                               "\n{max:+.3e} // {min:+.3e}\n".format(Arr1=Arr1_Name,
                                                                     unit=unit,
                                                                     max=arrVals[2],
                                                                     min=arrVals[3]))
    rtrnInfo["arr2Message"] = ("{Arr2:<} max//min ({unit:<}):"
                               "\n{max:+.3e} // {min:+.3e}\n".format(Arr2=Arr2_Name,
                                                                     unit=unit,
                                                                     max=arrVals[4],
                                                                     min=arrVals[5]))
    print("##############################")
    print(rtrnInfo["differenceMessage"])
    print(rtrnInfo["arr1Message"])
    print(rtrnInfo["arr2Message"])

    ### max difference percentage
    arrDiff_wrt_Arr1 = numpy.divide(abs(arrDiff),
                                    abs(Arr1))
    rtrnInfo["differencePercentageMessage"] = ("Max//mean % difference wrt {Arr1:<} ({unit:<}): "
                                               "\n{max:.5%} // {mean:.5%}\n".format(Arr1=Arr1_Name,
                                                                                    unit=unit,
                                                                                    max=numpy.max(arrDiff_wrt_Arr1),
                                                                                    mean=numpy.mean(arrDiff_wrt_Arr1)))
    print(rtrnInfo["differencePercentageMessage"])
    print("##############################")

    rtrnInfo["Message"] = rtrnInfo["differenceMessage"] \
                          + rtrnInfo["arr1Message"] \
                          + rtrnInfo["arr2Message"] \
                          + rtrnInfo["differencePercentageMessage"]

    # visualise results
    if pltRestuls:
        if arrDiffShp[0] > 1000:
            print("Too large data to plot!")
        else:
            # create figure
            # plot
            fig, axs = plt.subplots(2, 2)
            # 1st plt
            axs[0, 0].plot(numpy.squeeze(Arr1))
            axs[0, 0].set_title(Arr1_Name)
            axs[0, 0].set(xlabel=xlabel, ylabel=ylabel)
            # 2nd plt
            axs[0, 1].plot(numpy.squeeze(Arr2), 'tab:orange')
            axs[0, 1].set_title(Arr2_Name)
            axs[0, 1].set(xlabel=xlabel, ylabel=ylabel)
            # 3rd matrix
            # ax2 = axs[2].matshow(numpy.diag(arrDiff))
            # axs[2].set_title('Difference')
            # fig.colorbar(ax2, ax=axs[2])
            # 3rd plot
            axs[1, 0].plot(numpy.squeeze(arrDiff), 'tab:green')
            axs[1, 0].set_title("Diff = {} - {}".format(Arr1_Name, Arr2_Name))
            axs[1, 0].set(xlabel=xlabel, ylabel=ylabel)
            # 4th plot
            axs[1, 1].plot(numpy.squeeze(arrDiff_wrt_Arr1 * 100), 'tab:red')
            axs[1, 1].set_title("Diff/({}) *100%".format(Arr1_Name))
            axs[1, 1].set(xlabel=xlabel, ylabel="%")
            # suptitle
            fig.suptitle(suptitle)

            # Hide x labels and tick labels for top plots and y ticks for right plots.
            if hideOuterLabel:
                for ax in axs.flat:
                    ax.label_outer()

            plt.show()

    return rtrnInfo


"""
##############################################################################
#Func: Save input array or dictionary
##############################################################################
"""
import ntpath
import json
import pandas
from datetime import datetime


def SaveDictOrArr(
        inMat,
        fileName,
        folderPath,
        addTime=False,
        outNotNpyFile=False
):
    # time
    strtT = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["filePathCSV"] = None
    rtrnInfo["filePathJSON"] = None
    rtrnInfo["filePathNPY"] = None
    rtrnInfo["dataType"] = None
    rtrnInfo["informationMessage"] = ""
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["Message"] = ""

    # current date and time
    now = datetime.now()
    nowStr = now.strftime("%d%m%Y%H%M%S")  # dd/mm/yyyy /hh/mm/ss

    # check input type
    if not isinstance(inMat, numpy.ndarray) and not isinstance(inMat, dict):
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = ("Input is not dictionary or numpy.ndarray! " +
                                    "\n Cannot convert and save results")
        print(rtrnInfo["errorMessage"])
        return rtrnInfo
    else:
        # split path and get fileName
        fileNameOnly = ntpath.basename(fileName)
        # split file name only get name
        name, extension = os.path.splitext(fileNameOnly)
        # check separator
        if "/" in folderPath \
                and "\\" not in folderPath:
            # path add name
            filePath = folderPath + "/" + name
        elif "\\" in folderPath \
                and "/" not in folderPath:
            # path add name
            filePath = folderPath + "\\" + name
        else:
            rtrnInfo["errorMessage"] = "Input directory path does not separator or mixed separators!!\n"
            # path to replace / to \\!
            folderPath = folderPath.replace("/", "\\")
            # path add name
            filePath = folderPath + "\\" + name

    # output for dictionary
    if isinstance(inMat, dict):
        # save json
        if outNotNpyFile:
            try:
                ## path
                if addTime:
                    filePathWhole = filePath + "_dict_" + nowStr + ".json"
                else:
                    filePathWhole = filePath + "_dict" + ".json"
                rtrnInfo["filePathJSON"] = filePathWhole
                ## convert everthing into list of ALL ARRAYS for json (LARGE)
                outMat = {}
                keys = outMat.keys()
                for key in keys:
                    # convert array to list This method change the orignal data!!!
                    outMat[key] = inMat[key].tolist() if isinstance(inMat[key], numpy.ndarray) else inMat[key]
                # print(inMat)

                ## write
                with open(filePathWhole, 'w') as fp:
                    json.dump(outMat, fp)
            except:
                pass

        # save npy
        ## path
        if addTime:
            filePathWhole = filePath + "_dict_" + nowStr + ".npy"
        else:
            filePathWhole = filePath + "_dict" + ".npy"
        rtrnInfo["filePathNPY"] = filePathWhole
        ## write
        numpy.save(file=filePathWhole, arr=inMat)

        # information
        rtrnInfo["informationMessage"] = "Dictionary save into (JSON and) NPY"
        rtrnInfo["dataType"] = "Dictionary"

    # output for ndarray
    if isinstance(inMat, numpy.ndarray):
        # save csv + npy
        ## for 3d data
        # https://stackoverflow.com/questions/46852741/python-storing-values-in-a-3d-array-to-csv
        # https://stackoverflow.com/quehttps://stackoverflow.com/questions/46134827/
        # how-to-recover-original-indices-for-a-flattened-numpy-array
        if numpy.shape(numpy.shape(inMat))[0] == 3:
            # output csv
            if outNotNpyFile:
                try:
                    # path
                    if addTime:
                        filePathWhole = filePath + "_3dndarr_" + nowStr + ".csv"
                    else:
                        filePathWhole = filePath + "_3dndarr" + ".csv"
                    rtrnInfo["filePathCSV"] = filePathWhole
                    # convert it to stacked format using Pandas
                    stacked = pandas.Panel(inMat.swapaxes(1, 2)).to_frame().stack().reset_index()
                    stacked.columns = ['x', 'y', 'z', 'value']
                    # save to disk no column index + no header
                    stacked.to_csv(filePathWhole, index=False, header=False)
                except:
                    pass

            # save npy
            if addTime:
                filePathWhole = filePath + "_3dndarr_" + nowStr + ".npy"
            else:
                filePathWhole = filePath + "_3dndarr" + ".npy"
            rtrnInfo["filePathNPY"] = filePathWhole
            numpy.save(file=filePathWhole, arr=inMat)

            # information
            rtrnInfo["informationMessage"] = "3D ndarray save into (CSV and) NPY"
            rtrnInfo["dataType"] = "3Dndarray"

        ## for 2D
        if numpy.shape(numpy.shape(inMat))[0] == 2:
            # output csv
            if outNotNpyFile:
                try:
                    # path
                    if addTime:
                        filePathWhole = filePath + "_2dndarr_" + nowStr + ".csv"
                    else:
                        filePathWhole = filePath + "_2dndarr" + ".csv"
                    rtrnInfo["filePathCSV"] = filePathWhole
                    # write
                    pandas.DataFrame(inMat).to_csv(filePathWhole, index=False, header=False)
                except:
                    pass

            # save npy
            if addTime:
                filePathWhole = filePath + "_2dndarr_" + nowStr + ".npy"
            else:
                filePathWhole = filePath + "_2dndarr" + ".npy"
            rtrnInfo["filePathNPY"] = filePathWhole
            numpy.save(file=filePathWhole, arr=inMat)

            # information
            rtrnInfo["informationMessage"] = "2D ndarray save into CSV and NPY"
            rtrnInfo["dataType"] = "2Dndarray"

    # message
    msg = "Save: {}".format(rtrnInfo["filePathNPY"])
    # print(msg)

    # timing
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------Saving time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["Message"] = msg + "\n" + rtrnInfo["processTimeMessage"]

    return rtrnInfo


"""
##############################################################################
#Func: Compare LST and STR time range
##############################################################################
"""


def ComapreLSTSTRTime(lstT, strsT):
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = "Time range in list and stress files are the same."

    ### check shape and the same value
    if numpy.shape(lstT) != numpy.shape(strsT):
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = ("Time array do not have the same shape " +
                                    "\n {} \n{}".format(numpy.shape(lstT),
                                                        numpy.shape(strsT)))
        print(rtrnInfo["errorMessage"])
    elif numpy.sum(lstT - strsT) > 0:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = ("Time arrays are not the same. \nDifference: {}".format(numpy.sum(lstT - strsT)))
        print(rtrnInfo["errorMessage"])

    return rtrnInfo


"""
##############################################################################
#Func: Set time, nodal pressure (and max shear stress max(sigma_13) useless)
##############################################################################
"""
import scipy.stats
import copy


def LSTNodalPressMaxShear(
        timeLst,
        ndLst,
        ndCoo,
        timeStep,
        ndUseCalcs,
        lstPrefx=None,
        pressIndex=None,
        maxShearIndex=None,
        ndTimeMinPressure_AllNdCoo_out=False,
        ndTimeMaxPressure_AllNdCoo_out=False,
        ndTimePTPPressure_AllNdCoo_out=False,
        ndTimeQ1Pressure_AllNdCoo_out=False,
        ndTimeQ3Pressure_AllNdCoo_out=False,
        ndTimeIQRPressure_AllNdCoo_out=False,
        ndTimeMedianPressure_AllNdCoo_out=False,
        ndTimeModePressure_AllNdCoo_out=False,
        ndTimeMeanPressure_AllNdCoo_out=False,
        ndTimeRMSPressure_AllNdCoo_out=False,
        ndTimeHMeanPressure_AllNdCoo_out=False,
        ndTimeGMeanPressure_AllNdCoo_out=False,
        ndTimeTriMeanPressure_AllNdCoo_out=False,
        ndTimeDecile1Pressure_AllNdCoo_out=False,
        ndTimeDecile2Pressure_AllNdCoo_out=False,
        ndTimeDecile3Pressure_AllNdCoo_out=False,
        ndTimeDecile4Pressure_AllNdCoo_out=False,
        ndTimeDecile6Pressure_AllNdCoo_out=False,
        ndTimeDecile7Pressure_AllNdCoo_out=False,
        ndTimeDecile8Pressure_AllNdCoo_out=False,
        ndTimeDecile9Pressure_AllNdCoo_out=False,
        ndTimeSTDPressure_AllNdCoo_out=False,
        ndTimeVarPressure_AllNdCoo_out=False,
        ndTimeKurtPressure_AllNdCoo_out=False,
        ndTimeSkewPressure_AllNdCoo_out=False,
        ndTimeSEPressure_AllNdCoo_out=False,
        ndTimeEnergyPressure_AllNdCoo_out=False,
        ndTimeEntropyPressure_AllNdCoo_out=False
):
    """
    :param timeLst: Ditionary of LST file results
    :param ndLst: array/list of node reference
    :param timeStep: array/list of actual time steps (seconds)
    :param ndUseCalcs: column vector-True when node is used for calcs
    :param lstPrefx: string prefix for the timeLst dictionary item rerference
    :param pressIndex: int (column number) of where NODAL_PRESSURE in timeLst time-step mat
    :param maxShearIndex: int (column number) of where MAX_SHEAR_STRESS in timeLst time-step mat
    :return: rtrnInfo = {}
                rtrnInfo["error"] = False
                rtrnInfo["errorMessage"] = None
                rtrnInfo["nodeTimeAveragePressure_AllNodes"] = None
                rtrnInfo["nodalPressure_AllNodes"] = None
                rtrnInfo["nodalPressure_UseNodes"] = None
                rtrnInfo["nodalMaxShear_UseNodes"] = None
                rtrnInfo["informationMessage"] = None
                rtrnInfo["processTime"] = None
                rtrnInfo["processTimeMessage"] = None
    Set time, nodal pressure (and max shear stress max(sigma_13) useless)
    """

    # time
    strtT = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["nodeTimeAveragePressure_AllNodes"] = None
    rtrnInfo["nodeTimeAveragePressure_AllNodes_Coo"] = None
    rtrnInfo["nodalPressure_AllNodes"] = None
    rtrnInfo["nodalPressure_UseNodes"] = None
    rtrnInfo["nodalMaxShear_UseNodes"] = None
    rtrnInfo["Message"] = ""
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None

    # find prefix if not given
    if lstPrefx == None:
        ## check key existing
        if "prefix" in timeLst:
            lstPrefx = timeLst["prefix"]
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide lstPrefx"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if pressIndex == None:
        ## check key existing
        if "parameter" in timeLst and 'NODAL_PRESSURE' in timeLst['parameter']:
            pressIndex = timeLst['parameter'].index('NODAL_PRESSURE')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide pressIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if maxShearIndex == None:
        ## check key existing
        if "parameter" in timeLst and 'MAX_SHEAR_STRESS' in timeLst['parameter']:
            maxShearIndex = timeLst['parameter'].index('MAX_SHEAR_STRESS')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide maxShearIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo

    ### create empty mat
    ndLstShp = numpy.shape(ndLst)
    timeStepShp = numpy.shape(timeStep)

    ndPressure = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndMaxShear = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndPressure_AllNd = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndTimeAvePressure_AllNd = numpy.zeros([ndLstShp[0], 2])

    ndTimeAvePressure_AllNd[:, 0] = ndLst

    ### for save results
    ndTimeAvePressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
    ndTimeAvePressure_AllNdCoo[:, 0] = ndLst
    ndTimeAvePressure_AllNdCoo[:, 1:4] = ndCoo

    # loop values
    for t in range(len(timeStep)):
        # calculate useful nd lst for time t
        matLst = numpy.multiply(ndUseCalcs, timeLst[lstPrefx + str(timeStep[t])])
        ndPressure[:, t] = matLst[:, pressIndex]
        ndMaxShear[:, t] = matLst[:, maxShearIndex]
        # get all node nodal pressure
        ndPressure_AllNd[:, t] = timeLst[lstPrefx + str(timeStep[t])][:, pressIndex]

    # calculate time-averaged nodal pressure
    ## For variaous time step
    ## create empty for delta_P
    ndPressureTimeDiff_AllNd = numpy.zeros([ndLstShp[0], timeStepShp[0] - 1])
    ## delta p
    ndPressureTimeDiff_AllNd = ndPressure_AllNd[:, 1:] + ndPressure_AllNd[:, :-1]
    # print("ndPressureTimeDiff_AllNd shape: {}".format(numpy.shape(ndPressureTimeDiff_AllNd)))
    ## delta_t
    deltaVecT = timeStep[1:] - timeStep[:-1]
    # print("delta_T shape: {}".format(numpy.shape(deltaVecT)))
    ## t range
    deltaT = timeStep[-1] - timeStep[0]
    ## time-average all node nodal pressure
    ndTimeAvePressure_AllNd[:, 1] = numpy.dot(ndPressureTimeDiff_AllNd, deltaVecT) * 0.5 / deltaT

    ## for save results
    ndTimeAvePressure_AllNdCoo[:, 4] = ndTimeAvePressure_AllNd[:, 1]

    # replace 0 in array for special 1/x calculation
    ndPressure_AllNd_0r1 = copy.deepcopy(ndPressure_AllNd)
    ndPressure_AllNd_0r1 = numpy.abs(ndPressure_AllNd_0r1)
    ndPressure_AllNd_0r1[ndPressure_AllNd_0r1 == 0] = 1

    # stats without time involve
    if ndTimeMinPressure_AllNdCoo_out:
        ndTimeMinPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeMinPressure_AllNdCoo[:, 0] = ndLst
        ndTimeMinPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeMinPressure_AllNdCoo[:, 4] = numpy.nanmin(ndPressure_AllNd, axis=1)
        rtrnInfo["nodeTimeMinPressure_AllNodes_Coo"] = ndTimeMinPressure_AllNdCoo

    if ndTimeMaxPressure_AllNdCoo_out:
        ndTimeMaxPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeMaxPressure_AllNdCoo[:, 0] = ndLst
        ndTimeMaxPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeMaxPressure_AllNdCoo[:, 4] = numpy.nanmax(ndPressure_AllNd, axis=1)
        rtrnInfo["nodeTimeMaxPressure_AllNodes_Coo"] = ndTimeMaxPressure_AllNdCoo

    if ndTimePTPPressure_AllNdCoo_out:
        ndTimeMinPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeMinPressure_AllNdCoo[:, 0] = ndLst
        ndTimeMinPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeMinPressure_AllNdCoo[:, 4] = numpy.nanmin(ndPressure_AllNd, axis=1)

        ndTimeMaxPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeMaxPressure_AllNdCoo[:, 0] = ndLst
        ndTimeMaxPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeMaxPressure_AllNdCoo[:, 4] = numpy.nanmax(ndPressure_AllNd, axis=1)

        ndTimePTPPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimePTPPressure_AllNdCoo[:, 0] = ndLst
        ndTimePTPPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimePTPPressure_AllNdCoo[:, 4] = ndTimeMaxPressure_AllNdCoo[:, 4] - ndTimeMinPressure_AllNdCoo[:, 4]
        rtrnInfo["nodeTimePTPPressure_AllNodes_Coo"] = ndTimePTPPressure_AllNdCoo

    if ndTimeQ1Pressure_AllNdCoo_out:
        ndTimeQ1Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeQ1Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeQ1Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeQ1Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 25, axis=1)
        rtrnInfo["nodeTimeQ1Pressure_AllNodes_Coo"] = ndTimeQ1Pressure_AllNdCoo

    if ndTimeQ3Pressure_AllNdCoo_out:
        ndTimeQ3Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeQ3Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeQ3Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeQ3Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 75, axis=1)
        rtrnInfo["nodeTimeQ3Pressure_AllNodes_Coo"] = ndTimeQ3Pressure_AllNdCoo

    if ndTimeIQRPressure_AllNdCoo_out:
        ndTimeQ1Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeQ1Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeQ1Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeQ1Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 25, axis=1)

        ndTimeQ3Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeQ3Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeQ3Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeQ3Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 75, axis=1)

        ndTimeIQRPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeIQRPressure_AllNdCoo[:, 0] = ndLst
        ndTimeIQRPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeIQRPressure_AllNdCoo[:, 4] = ndTimeQ3Pressure_AllNdCoo[:, 4] - ndTimeQ1Pressure_AllNdCoo[:, 4]
        rtrnInfo["nodeTimeIQRPressure_AllNodes_Coo"] = ndTimeIQRPressure_AllNdCoo

    if ndTimeMedianPressure_AllNdCoo_out:
        ndTimeMedianPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeMedianPressure_AllNdCoo[:, 0] = ndLst
        ndTimeMedianPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeMedianPressure_AllNdCoo[:, 4] = numpy.nanmedian(ndPressure_AllNd, axis=1)
        rtrnInfo["nodeTimeMedianPressure_AllNodes_Coo"] = ndTimeMedianPressure_AllNdCoo

    if ndTimeModePressure_AllNdCoo_out:
        ndTimeModePressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeModePressure_AllNdCoo[:, 0] = ndLst
        ndTimeModePressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeModePressure_AllNdCoo[:, 4] = scipy.stats.mode(ndPressure_AllNd, axis=1, nan_policy='omit')[0][0]
        rtrnInfo["nodeTimeModePressure_AllNodes_Coo"] = ndTimeModePressure_AllNdCoo

    if ndTimeMeanPressure_AllNdCoo_out:
        ndTimeMeanPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeMeanPressure_AllNdCoo[:, 0] = ndLst
        ndTimeMeanPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeMeanPressure_AllNdCoo[:, 4] = numpy.nanmean(ndPressure_AllNd, axis=1)
        rtrnInfo["nodeTimeMeanPressure_AllNodes_Coo"] = ndTimeMeanPressure_AllNdCoo

    if ndTimeRMSPressure_AllNdCoo_out:
        ndTimeRMSPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeRMSPressure_AllNdCoo[:, 0] = ndLst
        ndTimeRMSPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeRMSPressure_AllNdCoo[:, 4] = numpy.sqrt(numpy.nanmean(numpy.power(ndPressure_AllNd, 2), axis=1))
        rtrnInfo["nodeTimeRMSPressure_AllNodes_Coo"] = ndTimeRMSPressure_AllNdCoo

    if ndTimeHMeanPressure_AllNdCoo_out:
        ndTimeHMeanPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeHMeanPressure_AllNdCoo[:, 0] = ndLst
        ndTimeHMeanPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeHMeanPressure_AllNdCoo[:, 4] = scipy.stats.hmean(ndPressure_AllNd_0r1, axis=1)
        rtrnInfo["nodeTimeHMeanPressure_AllNodes_Coo"] = ndTimeHMeanPressure_AllNdCoo

    if ndTimeGMeanPressure_AllNdCoo_out:
        ndTimeGMeanPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeGMeanPressure_AllNdCoo[:, 0] = ndLst
        ndTimeGMeanPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeGMeanPressure_AllNdCoo[:, 4] = scipy.stats.gmean(ndPressure_AllNd_0r1, axis=1)
        rtrnInfo["nodeTimeGMeanPressure_AllNodes_Coo"] = ndTimeGMeanPressure_AllNdCoo

    if ndTimeTriMeanPressure_AllNdCoo_out:
        ndTimeTriMeanPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeTriMeanPressure_AllNdCoo[:, 0] = ndLst
        ndTimeTriMeanPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeTriMeanPressure_AllNdCoo[:, 4] = (numpy.nanpercentile(ndPressure_AllNd, 25, axis=1)
                                                    + 2 * numpy.nanpercentile(ndPressure_AllNd, 5, axis=1)
                                                    + numpy.nanpercentile(ndPressure_AllNd, 75, axis=1))/4
        rtrnInfo["nodeTimeTriMeanPressure_AllNodes_Coo"] = ndTimeTriMeanPressure_AllNdCoo

    if ndTimeDecile1Pressure_AllNdCoo_out:
        ndTimeDecile1Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeDecile1Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeDecile1Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeDecile1Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 10, axis=1)
        rtrnInfo["nodeTimeDecile1Pressure_AllNodes_Coo"] = ndTimeDecile1Pressure_AllNdCoo

    if ndTimeDecile2Pressure_AllNdCoo_out:
        ndTimeDecile2Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeDecile2Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeDecile2Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeDecile2Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 20, axis=1)
        rtrnInfo["nodeTimeDecile2Pressure_AllNodes_Coo"] = ndTimeDecile2Pressure_AllNdCoo

    if ndTimeDecile3Pressure_AllNdCoo_out:
        ndTimeDecile3Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeDecile3Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeDecile3Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeDecile3Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 30, axis=1)
        rtrnInfo["nodeTimeDecile3Pressure_AllNodes_Coo"] = ndTimeDecile3Pressure_AllNdCoo

    if ndTimeDecile4Pressure_AllNdCoo_out:
        ndTimeDecile4Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeDecile4Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeDecile4Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeDecile4Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 40, axis=1)
        rtrnInfo["nodeTimeDecile4Pressure_AllNodes_Coo"] = ndTimeDecile4Pressure_AllNdCoo

    if ndTimeDecile6Pressure_AllNdCoo_out:
        ndTimeDecile6Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeDecile6Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeDecile6Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeDecile6Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 60, axis=1)
        rtrnInfo["nodeTimeDecile6Pressure_AllNodes_Coo"] = ndTimeDecile6Pressure_AllNdCoo

    if ndTimeDecile7Pressure_AllNdCoo_out:
        ndTimeDecile7Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeDecile7Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeDecile7Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeDecile7Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 70, axis=1)
        rtrnInfo["nodeTimeDecile7Pressure_AllNodes_Coo"] = ndTimeDecile7Pressure_AllNdCoo

    if ndTimeDecile8Pressure_AllNdCoo_out:
        ndTimeDecile8Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeDecile8Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeDecile8Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeDecile8Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 80, axis=1)
        rtrnInfo["nodeTimeDecile8Pressure_AllNodes_Coo"] = ndTimeDecile8Pressure_AllNdCoo

    if ndTimeDecile9Pressure_AllNdCoo_out:
        ndTimeDecile9Pressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeDecile9Pressure_AllNdCoo[:, 0] = ndLst
        ndTimeDecile9Pressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeDecile9Pressure_AllNdCoo[:, 4] = numpy.nanpercentile(ndPressure_AllNd, 90, axis=1)
        rtrnInfo["nodeTimeDecile9Pressure_AllNodes_Coo"] = ndTimeDecile9Pressure_AllNdCoo

    if ndTimeSTDPressure_AllNdCoo_out:
        ndTimeSTDPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeSTDPressure_AllNdCoo[:, 0] = ndLst
        ndTimeSTDPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeSTDPressure_AllNdCoo[:, 4] = numpy.nanstd(ndPressure_AllNd, axis=1, ddof=1)
        rtrnInfo["nodeTimeSTDPressure_AllNodes_Coo"] = ndTimeSTDPressure_AllNdCoo

    if ndTimeVarPressure_AllNdCoo_out:
        ndTimeVarPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeVarPressure_AllNdCoo[:, 0] = ndLst
        ndTimeVarPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeVarPressure_AllNdCoo[:, 4] = numpy.nanvar(ndPressure_AllNd, axis=1, ddof=1)
        rtrnInfo["nodeTimeVarPressure_AllNodes_Coo"] = ndTimeVarPressure_AllNdCoo

    if ndTimeKurtPressure_AllNdCoo_out:
        ndTimeKurtPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeKurtPressure_AllNdCoo[:, 0] = ndLst
        ndTimeKurtPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeKurtPressure_AllNdCoo[:, 4] = scipy.stats.kurtosis(ndPressure_AllNd, nan_policy='omit', axis=1)
        rtrnInfo["nodeTimeKurtosisPressure_AllNodes_Coo"] = ndTimeKurtPressure_AllNdCoo

    if ndTimeSkewPressure_AllNdCoo_out:
        ndTimeSkewPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeSkewPressure_AllNdCoo[:, 0] = ndLst
        ndTimeSkewPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeSkewPressure_AllNdCoo[:, 4] = scipy.stats.skew(ndPressure_AllNd, nan_policy='omit', axis=1)
        rtrnInfo["nodeTimeSkewPressure_AllNodes_Coo"] = ndTimeSkewPressure_AllNdCoo

    if ndTimeSEPressure_AllNdCoo_out:
        ndTimeSEPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeSEPressure_AllNdCoo[:, 0] = ndLst
        ndTimeSEPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeSEPressure_AllNdCoo[:, 4] = scipy.stats.sem(ndPressure_AllNd, nan_policy='omit', axis=1)
        rtrnInfo["nodeTimeSEPressure_AllNodes_Coo"] = ndTimeSEPressure_AllNdCoo

    if ndTimeEnergyPressure_AllNdCoo_out:
        ndTimeEnergyPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeEnergyPressure_AllNdCoo[:, 0] = ndLst
        ndTimeEnergyPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeEnergyPressure_AllNdCoo[:, 4] = numpy.nansum(numpy.power(ndPressure_AllNd, 2), axis=1)
        rtrnInfo["nodeTimeEnergyPressure_AllNodes_Coo"] = ndTimeEnergyPressure_AllNdCoo

    if ndTimeEntropyPressure_AllNdCoo_out:
        ndTimeEntropyPressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
        ndTimeEntropyPressure_AllNdCoo[:, 0] = ndLst
        ndTimeEntropyPressure_AllNdCoo[:, 1:4] = ndCoo
        ndTimeEntropyPressure_AllNdCoo[:, 4] = scipy.stats.entropy(ndPressure_AllNd, axis=1)
        rtrnInfo["nodeTimeEntropyPressure_AllNodes_Coo"] = ndTimeEntropyPressure_AllNdCoo

    # time
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------LST processing time: {} s------".format(rtrnInfo["processTime"])

    # return
    rtrnInfo["nodeTimeAveragePressure_AllNodes"] = ndTimeAvePressure_AllNd
    rtrnInfo["nodeTimeAveragePressure_AllNodes_Coo"] = ndTimeAvePressure_AllNdCoo
    rtrnInfo["nodalPressure_AllNodes"] = ndPressure_AllNd
    rtrnInfo["nodalPressure_UseNodes"] = ndPressure
    rtrnInfo["nodalMaxShear_UseNodes"] = ndMaxShear
    rtrnInfo["Message"] = "Complete matching nodal pressure, max shear stress, " \
                          "time-average nodal pressure calculation\n" + \
                          rtrnInfo["processTimeMessage"]
    print(rtrnInfo["Message"])

    return rtrnInfo


"""
##############################################################################
#Func: Calculate all TAWSS, OSI, RRT
##############################################################################
"""
import scipy.stats


def WSSParameters(
        timeStep,
        ndLst,
        ndUseCalcs,
        ndWSSMag,
        ndWSSTime,
        ndCoo
):
    """
    :param timeStep:
    :param ndLst:
    :param ndUseCalcs:
    :param ndWSSMag:
    :param ndWSSTime:
    :param ndCoo:
    :return:
    rtrnInfo["nodalTAWSS_UseNodes_coordinates"] = np.array[ndLst, ndCoo (X, Y, Z), TAWSS] {node_numbers * 5}
    """

    # time
    strtT = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = None
    rtrnInfo["RRTOSIError"] = False
    rtrnInfo["RRTOSIErrorMessage"] = ""
    rtrnInfo["nodalTAWSS_UseNodes"] = None
    rtrnInfo["nodalWSS_VectorMagnitude_UseNodes"] = None
    rtrnInfo["nodalOSI_UseNodes"] = None
    rtrnInfo["nodalRRT_UseNodes"] = None
    rtrnInfo["nodalTAWSS_UseNodes_coordinates"] = None
    rtrnInfo["nodalWSS_VectorMagnitude_UseNodes_coordinates"] = None
    rtrnInfo["nodalOSI_UseNodes_coordinates"] = None
    rtrnInfo["nodalRRT_UseNodes_coordinates"] = None
    rtrnInfo["Message"] = None
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None

    # shape
    ndLstShp = numpy.shape(ndLst)
    timeStepShp = numpy.shape(timeStep)

    # delta_t
    deltaVecT = timeStep[1:] - timeStep[:-1]  # [K_t-1 * 3]
    # print("delta_T shape: {}".format(numpy.shape(deltaVecT)))
    ## t range
    deltaT = timeStep[-1] - timeStep[0]

    # TAWSS
    ## matrix of WSS magnitude difference
    ndTAWSS = numpy.zeros([ndLstShp[0], 2])
    ndWSSMagDiff = numpy.zeros([ndLstShp[0], timeStepShp[0] - 1])
    ndTAWSS[:, 0] = ndLst
    ## WSS magnitude difference
    ndWSSMagDiff = ndWSSMag[:, 1:] + ndWSSMag[:, :-1]
    # print("ndWSSMagDiff shape: {}".format(numpy.shape(ndWSSMagDiff)))

    ## TAWSS
    ndTAWSS[:, 1] = numpy.dot(ndWSSMagDiff, deltaVecT) * 0.5 / deltaT
    # print("ndTAWSS shape: {}".format(numpy.shape(ndTAWSS)))

    # TAWSS-Vector & RRT & OSI
    ## matrix for WSS vector difference for each node
    ndTAWSS_VectorMag = numpy.zeros([ndLstShp[0], 2])
    ndRRT = numpy.zeros([ndLstShp[0], 2])
    ndRRT_Check = numpy.zeros([ndLstShp[0], 2])
    ndOSI = numpy.zeros([ndLstShp[0], 2])

    ndTAWSS_VectorMag[:, 0] = ndLst
    ndRRT[:, 0] = ndLst
    ndRRT_Check[:, 0] = ndLst
    ndOSI[:, 0] = ndLst

    ## matrix out put with coordinates
    ndTAWSS_Coo = numpy.zeros([ndLstShp[0], 5])
    ndTAWSS_VectorMag_Coo = numpy.zeros([ndLstShp[0], 5])
    ndRRT_Coo = numpy.zeros([ndLstShp[0], 5])
    ndOSI_Coo = numpy.zeros([ndLstShp[0], 5])

    ## loop through each node
    for node in range(len(ndLst)):
        # jump not used nodes
        if not ndUseCalcs[node]:
            continue

        # ndWSS vector
        ndWSS = ndWSSTime[:, node, :]  # [(time) * (x, y, z)] [K_t * 3]
        # print("ndWSS shape: {}".format(numpy.shape(ndWSS)))
        ndWSSDiff = ndWSS[1:, :] + ndWSS[:-1, :]  # difference for time interval [K_t-1 * 3]
        # print("ndWSSDiff shape: {}".format(numpy.shape(ndWSSDiff)))

        # integration
        ndWSSIntegral = numpy.dot(deltaVecT.T, ndWSSDiff)  # [1 * 3]
        # print("ndWSSIntegral shape: {}".format(numpy.shape(ndWSSIntegral)))

        # magnitude TAWSS_VectorMagnitude
        ndTAWSS_VectorMag[node, 1] = numpy.linalg.norm(ndWSSIntegral) * 0.5 / deltaT

        # OSI calcs
        ## OSI dealing TAWSS = 0
        if ndTAWSS[node, 1] == 0:
            ndOSI[node, 1] = 0.5
            rtrnInfo["RRTOSIError"] = True
            rtrnInfo["RRTOSIErrorMessage"] += "Warning!! at node: {} " \
                                              "ZERO OSI denominator TAWSS = 0 " \
                                              "\nSET OSI = 1e5 \n".format(ndLst[node])
        else:
            ndOSI[node, 1] = 0.5 * (1 - (ndTAWSS_VectorMag[node, 1] / ndTAWSS[node, 1]))

        ## RRT calcs
        ### dealing with 0 divider
        if ndOSI[node, 1] == 0.5:
            ndRRT[node, 1] = 1e5
            ndRRT_Check[node, 1] = 1e5
            rtrnInfo["RRTOSIError"] = True
            rtrnInfo["RRTOSIErrorMessage"] += "Warning!! at node: {} " \
                                              "ZERO RRT denominator OSI = 0.5 " \
                                              "\nSET RRT = 1e5 \n".format(ndLst[node])
        elif ndTAWSS[node, 1] == 0:
            ndRRT[node, 1] = 1e5
            ndRRT_Check[node, 1] = 1e5
            rtrnInfo["RRTOSIError"] = True
            rtrnInfo["RRTOSIErrorMessage"] += "Warning!! at node: {} " \
                                              "ZERO RRT denominator TAWSS = 0 " \
                                              "\nSET RRT = 1e5 \n".format(ndLst[node])
        else:
            ndRRT[node, 1] = 1 / ndTAWSS_VectorMag[node, 1]
            ndRRT_Check[node, 1] = 1 / ((1 - 2 * ndOSI[node, 1]) * ndTAWSS[node, 1])

    # OSI/RRT division error
    if rtrnInfo["RRTOSIError"]:
        print(rtrnInfo["RRTOSIErrorMessage"])

    # Check calcs of RRT
    ndUseCalcs_Nonzero_indices = numpy.where(ndUseCalcs == 1)
    ndRRT_Diff_Compare = CompareArrayDifference(Arr1=ndRRT[ndUseCalcs_Nonzero_indices[0], 1],
                                                Arr2=ndRRT_Check[ndUseCalcs_Nonzero_indices[0], 1],
                                                Arr1_Name="RRT(TAIWSS)",
                                                Arr2_Name="RRT(OSI)",
                                                unit="Pa^(-1)")

    # Add Coordinate output
    ndTAWSS_Coo[:, 0] = ndLst
    ndTAWSS_VectorMag_Coo[:, 0] = ndLst
    ndRRT_Coo[:, 0] = ndLst
    ndOSI_Coo[:, 0] = ndLst

    ndTAWSS_Coo[:, 1:4] = ndCoo
    ndTAWSS_VectorMag_Coo[:, 1:4] = ndCoo
    ndRRT_Coo[:, 1:4] = ndCoo
    ndOSI_Coo[:, 1:4] = ndCoo

    ndTAWSS_Coo[:, 4] = ndTAWSS[:, 1]
    ndTAWSS_VectorMag_Coo[:, 4] = ndTAWSS_VectorMag[:, 1]
    ndRRT_Coo[:, 4] = ndRRT[:, 1]
    ndOSI_Coo[:, 4] = ndOSI[:, 1]
    print(ndTAWSS_Coo)

    # time
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------WSS parameter calculation time: {} s------".format(rtrnInfo["processTime"])

    # return
    rtrnInfo["nodalTAWSS_UseNodes"] = ndTAWSS
    rtrnInfo["nodalWSS_VectorMagnitude_UseNodes"] = ndTAWSS_VectorMag
    rtrnInfo["nodalOSI_UseNodes"] = ndOSI
    rtrnInfo["nodalRRT_UseNodes"] = ndRRT
    rtrnInfo["nodalTAWSS_UseNodes_coordinates"] = ndTAWSS_Coo
    rtrnInfo["nodalWSS_VectorMagnitude_UseNodes_coordinates"] = ndTAWSS_VectorMag_Coo
    rtrnInfo["nodalOSI_UseNodes_coordinates"] = ndOSI_Coo
    rtrnInfo["nodalRRT_UseNodes_coordinates"] = ndRRT_Coo
    rtrnInfo["Message"] = "Complete WSS parameters calculation.\n" + rtrnInfo["processTimeMessage"]
    print(rtrnInfo["Message"])

    return rtrnInfo


"""
##############################################################################
#Func: Calculation for shear stress vector
##############################################################################
"""
import scipy.stats


def StrsWSS(
        timeStrs,
        ndLst,
        ndCoo,
        timeStep,
        ndUseCalcs,
        ndNorms,
        strsPrefx=None,
        xxIndex=None,
        yyIndex=None,
        zzIndex=None,
        xyIndex=None,
        xzIndex=None,
        yzIndex=None,
        ndTimeMinWSS_AllNdCoo_out=False,
        ndTimeMaxWSS_AllNdCoo_out=False,
        ndTimePTPWSS_AllNdCoo_out=False,
        ndTimeQ1WSS_AllNdCoo_out=False,
        ndTimeQ3WSS_AllNdCoo_out=False,
        ndTimeIQRWSS_AllNdCoo_out=False,
        ndTimeMedianWSS_AllNdCoo_out=False,
        ndTimeModeWSS_AllNdCoo_out=False,
        ndTimeRMSWSS_AllNdCoo_out=False,
        ndTimeHMeanWSS_AllNdCoo_out=False,
        ndTimeGMeanWSS_AllNdCoo_out=False,
        ndTimeTriMeanWSS_AllNdCoo_out=False,
        ndTimeDecile1WSS_AllNdCoo_out=False,
        ndTimeDecile2WSS_AllNdCoo_out=False,
        ndTimeDecile3WSS_AllNdCoo_out=False,
        ndTimeDecile4WSS_AllNdCoo_out=False,
        ndTimeDecile6WSS_AllNdCoo_out=False,
        ndTimeDecile7WSS_AllNdCoo_out=False,
        ndTimeDecile8WSS_AllNdCoo_out=False,
        ndTimeDecile9WSS_AllNdCoo_out=False,
        ndTimeSTDWSS_AllNdCoo_out=False,
        ndTimeVarWSS_AllNdCoo_out=False,
        ndTimeKurtWSS_AllNdCoo_out=False,
        ndTimeSkewWSS_AllNdCoo_out=False,
        ndTimeSEWSS_AllNdCoo_out=False,
        ndTimeEnergyWSS_AllNdCoo_out=False,
        ndTimeEntropyWSS_AllNdCoo_out=False
):
    """
    :param timeStrs:
    :param ndLst:
    :param timeStep:
    :param ndUseCalcs:
    :param ndNorms:
    :param strsPrefx: strsPrefx = timeStrs["prefix"]
    :param xxIndex: xxIndex = timeStrs['parameter'].index('STRESS-XX')
    :param yyIndex: yyIndex = timeStrs['parameter'].index('STRESS-YY')
    :param zzIndex: zzIndex = timeStrs['parameter'].index('STRESS-ZZ')
    :param xyIndex: xyIndex = timeStrs['parameter'].index('STRESS-XY')
    :param xzIndex: xzIndex = timeStrs['parameter'].index('STRESS-XZ')
    :param yzIndex: yzIndex = timeStrs['parameter'].index('STRESS-YZ')
    :return:
    # Calculation for shear stress vector
    """
    # time
    strtT = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["nodalAveragePressure_UseNodes"] = None
    rtrnInfo["nodalWSSMagnitude_UseNodes"] = None
    rtrnInfo["nodalWSSTime_UseNodes"] = None
    rtrnInfo["Message"] = ""
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None

    # find prefix if not given
    if strsPrefx == None:
        ## check key existing
        if "prefix" in timeStrs:
            strsPrefx = timeStrs["prefix"]
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide strsPrefx"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if xxIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-XX' in timeStrs['parameter']:
            xxIndex = timeStrs['parameter'].index('STRESS-XX')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide xxIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if yyIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-YY' in timeStrs['parameter']:
            yyIndex = timeStrs['parameter'].index('STRESS-YY')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide yyIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if zzIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-ZZ' in timeStrs['parameter']:
            zzIndex = timeStrs['parameter'].index('STRESS-ZZ')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide zzIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if xyIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-XY' in timeStrs['parameter']:
            xyIndex = timeStrs['parameter'].index('STRESS-XY')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide xyIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if xzIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-XZ' in timeStrs['parameter']:
            xzIndex = timeStrs['parameter'].index('STRESS-XZ')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide xzIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if yzIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-YZ' in timeStrs['parameter']:
            yzIndex = timeStrs['parameter'].index('STRESS-YZ')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide yzIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo

    # shape & empty mat
    ndLstShp = numpy.shape(ndLst)
    timeStepShp = numpy.shape(timeStep)

    ndAvePressure = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndWSSMag = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndWSSTime = numpy.zeros([timeStepShp[0], ndLstShp[0], 3])

    # loop through time
    for t in range(len(timeStep)):
        # usefull mat at each timestep
        matLst = numpy.multiply(ndUseCalcs, timeStrs[strsPrefx + str(timeStep[t])])

        # create empty array
        ndShearVecT = numpy.zeros([ndLstShp[0], 3])
        ndShearVecMagT = numpy.zeros([ndLstShp[0], 1])
        ndPressureT = numpy.zeros([ndLstShp[0], 1])

        ## loop through each node
        for node in range(len(ndLst)):
            # jump not used nodes
            if not ndUseCalcs[node, :]:
                continue

            # stress sigma
            strsFlat = matLst[node]
            xx = strsFlat[xxIndex]
            yy = strsFlat[yyIndex]
            zz = strsFlat[zzIndex]
            xy = strsFlat[xyIndex]
            xz = strsFlat[xzIndex]
            yz = strsFlat[yzIndex]
            zx = xz
            zy = yz
            yx = xy
            # stress tensor
            strsSigma = numpy.array([[xx, xy, xz],
                                     [yx, yy, yz],
                                     [zx, zy, zz]])
            # hydrostatic pressure
            hydroStaPress = numpy.mean([xx, yy, zz])

            # if node < 100:
            #     print("uniform pressure(Pa): {}".format(hydroStaPress))

            # stress tensor remove hydrostatic pressure = shear stress only
            strsSigmaShear = strsSigma - numpy.identity(3) * hydroStaPress

            # normal direction
            ndNorm = ndNorms[node, 1:]
            # normalise again for saftey
            norm = numpy.linalg.norm(ndNorm)
            ndNorm = ndNorm / norm

            # matrix multiplication
            wallStress = numpy.dot(strsSigmaShear, ndNorm)  # this should be shear stress
            wallNormalStress = numpy.dot(ndNorm, wallStress) * ndNorm  # for security remove the normal component again

            # if numpy.sum(wallNormalStress) != 0 and node < 100:
            #     print("Normal stress after remove hydrostatic pressure is not ZERO!")
            #     print(wallNormalStress)

            wallShearStress = wallStress - wallNormalStress  # wall shear stress vector

            # updated
            ndShearVecT[node] = wallShearStress
            ndShearVecMagT[node] = numpy.linalg.norm(wallShearStress)
            ndPressureT[node] = hydroStaPress

        # updated value of each time
        """
        # Note in Fluid pressure is +ve when compression
        # Note in Solid tension is +ve 
        """
        ndAvePressure[:, t] = ndPressureT[:, 0]
        ndWSSMag[:, t] = ndShearVecMagT[:, 0]
        ndWSSTime[t, :, :] = ndShearVecT

    # use nodes label and coordinates
    print('ndLst : ', numpy.shape(ndLst))
    print('ndCoo : ', numpy.shape(ndCoo))
    print('ndWSSMag : ', numpy.shape(ndWSSMag))
    print('ndUseCalcs : ', numpy.shape(ndUseCalcs))
    print('numpy.where(ndUseCalcs == 1) : ', numpy.shape(numpy.where(ndUseCalcs == 1)))
    print('numpy.where(ndUseCalcs == 1)[0] : ', numpy.shape(numpy.where(ndUseCalcs == 1)[0]))
    print('numpy.where(ndUseCalcs == 1)[0] : ', numpy.shape(numpy.where(ndUseCalcs == 1)[1]))
    print('ndUseCalcs : ', ndUseCalcs)
    print('numpy.where(ndUseCalcs == 1) : ', numpy.where(ndUseCalcs == 1))
    print('numpy.where(ndUseCalcs == 1)[0] : ', numpy.where(ndUseCalcs == 1)[0])
    print('numpy.where(ndUseCalcs == 1)[1] : ', numpy.where(ndUseCalcs == 1)[1])
    ndLstUse = ndLst[numpy.where(ndUseCalcs == 1)[0]]
    ndCooUse = ndCoo[numpy.where(ndUseCalcs == 1)[0], :]
    ndWSSMagUse = ndWSSMag[numpy.where(ndUseCalcs == 1)[0], :]
    ndLstUseShp = numpy.shape(ndLstUse)

    print('ndLst : ', numpy.shape(ndLst))
    print('ndLstUse : ', numpy.shape(ndLstUse))
    print('ndCoo : ', numpy.shape(ndCoo))
    print('ndCooUse : ', numpy.shape(ndCooUse))

    # replace 0 to 1
    ndWSSMagUse_0r1 = copy.deepcopy(ndWSSMagUse)
    ndWSSMagUse_0r1 = numpy.abs(ndWSSMagUse_0r1)
    ndWSSMagUse_0r1[ndWSSMagUse_0r1 == 0] = 1

    # WSS time domain stats
    if ndTimeMinWSS_AllNdCoo_out:
        ndTimeMinWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeMinWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeMinWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeMinWSS_AllNdCoo[:, 4] = numpy.nanmin(ndWSSMagUse, axis=1)
        rtrnInfo["nodeTimeMinWSS_AllNodes_Coo"] = ndTimeMinWSS_AllNdCoo

    if ndTimeMaxWSS_AllNdCoo_out:
        ndTimeMaxWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeMaxWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeMaxWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeMaxWSS_AllNdCoo[:, 4] = numpy.nanmax(ndWSSMagUse, axis=1)
        rtrnInfo["nodeTimeMaxWSS_AllNodes_Coo"] = ndTimeMaxWSS_AllNdCoo

    if ndTimePTPWSS_AllNdCoo_out:
        ndTimeMinWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeMinWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeMinWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeMinWSS_AllNdCoo[:, 4] = numpy.nanmin(ndWSSMagUse, axis=1)

        ndTimeMaxWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeMaxWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeMaxWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeMaxWSS_AllNdCoo[:, 4] = numpy.nanmax(ndWSSMagUse, axis=1)

        ndTimePTPWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimePTPWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimePTPWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimePTPWSS_AllNdCoo[:, 4] = ndTimeMaxWSS_AllNdCoo[:, 4] - ndTimeMinWSS_AllNdCoo[:, 4]
        rtrnInfo["nodeTimePTPWSS_AllNodes_Coo"] = ndTimePTPWSS_AllNdCoo

    if ndTimeQ1WSS_AllNdCoo_out:
        ndTimeQ1WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeQ1WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeQ1WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeQ1WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 25, axis=1)
        rtrnInfo["nodeTimeQ1WSS_AllNodes_Coo"] = ndTimeQ1WSS_AllNdCoo

    if ndTimeQ3WSS_AllNdCoo_out:
        ndTimeQ3WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeQ3WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeQ3WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeQ3WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 75, axis=1)
        rtrnInfo["nodeTimeQ3WSS_AllNodes_Coo"] = ndTimeQ3WSS_AllNdCoo

    if ndTimeIQRWSS_AllNdCoo_out:
        ndTimeQ1WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeQ1WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeQ1WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeQ1WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 25, axis=1)

        ndTimeQ3WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeQ3WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeQ3WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeQ3WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 75, axis=1)

        ndTimeIQRWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeIQRWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeIQRWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeIQRWSS_AllNdCoo[:, 4] = ndTimeQ3WSS_AllNdCoo[:, 4] - ndTimeQ1WSS_AllNdCoo[:, 4]
        rtrnInfo["nodeTimeIQRWSS_AllNodes_Coo"] = ndTimeIQRWSS_AllNdCoo

    if ndTimeMedianWSS_AllNdCoo_out:
        ndTimeMedianWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeMedianWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeMedianWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeMedianWSS_AllNdCoo[:, 4] = numpy.nanmedian(ndWSSMagUse)
        rtrnInfo["nodeTimeMedianWSS_AllNodes_Coo"] = ndTimeMedianWSS_AllNdCoo

    if ndTimeModeWSS_AllNdCoo_out:
        ndTimeModeWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeModeWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeModeWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeModeWSS_AllNdCoo[:, 4] = scipy.stats.mode(ndWSSMagUse, axis=1, nan_policy='omit')[0][0]
        rtrnInfo["nodeTimeModeWSS_AllNodes_Coo"] = ndTimeModeWSS_AllNdCoo

        # ndTimeMeanWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        # ndTimeMeanWSS_AllNdCoo[:, 0] = ndLstUse
        # ndTimeMeanWSS_AllNdCoo[:, 1:4] = ndCooUse
        # ndTimeMeanWSS_AllNdCoo[:, 4] = numpy.nanmean(ndWSSMagUse, axis=1)
        # rtrnInfo["nodeTimeMeanWSS_AllNodes_Coo"] = ndTimeMeanWSS_AllNdCoo

    if ndTimeRMSWSS_AllNdCoo_out:
        ndTimeRMSWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeRMSWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeRMSWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeRMSWSS_AllNdCoo[:, 4] = numpy.sqrt(numpy.nanmean(numpy.power(ndWSSMagUse, 2), axis=1))
        rtrnInfo["nodeTimeRMSWSS_AllNodes_Coo"] = ndTimeRMSWSS_AllNdCoo

    if ndTimeHMeanWSS_AllNdCoo_out:
        ndTimeHMeanWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeHMeanWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeHMeanWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeHMeanWSS_AllNdCoo[:, 4] = scipy.stats.hmean(ndWSSMagUse_0r1, axis=1)
        rtrnInfo["nodeTimeHMeanWSS_AllNodes_Coo"] = ndTimeHMeanWSS_AllNdCoo

    if ndTimeGMeanWSS_AllNdCoo_out:
        ndTimeGMeanWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeGMeanWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeGMeanWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeGMeanWSS_AllNdCoo[:, 4] = scipy.stats.gmean(ndWSSMagUse_0r1, axis=1)
        rtrnInfo["nodeTimeGMeanWSS_AllNodes_Coo"] = ndTimeGMeanWSS_AllNdCoo

    if ndTimeTriMeanWSS_AllNdCoo_out:
        ndTimeTriMeanWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeTriMeanWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeTriMeanWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeTriMeanWSS_AllNdCoo[:, 4] = (numpy.nanpercentile(ndWSSMagUse, 25, axis=1)
                                                    + 2 * numpy.nanpercentile(ndWSSMagUse, 5, axis=1)
                                                    + numpy.nanpercentile(ndWSSMagUse, 75, axis=1))/4
        rtrnInfo["nodeTimeTriMeanWSS_AllNodes_Coo"] = ndTimeTriMeanWSS_AllNdCoo

    if ndTimeDecile1WSS_AllNdCoo_out:
        ndTimeDecile1WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeDecile1WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeDecile1WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeDecile1WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 10, axis=1)
        rtrnInfo["nodeTimeDecile1WSS_AllNodes_Coo"] = ndTimeDecile1WSS_AllNdCoo

    if ndTimeDecile2WSS_AllNdCoo_out:
        ndTimeDecile2WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeDecile2WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeDecile2WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeDecile2WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 20, axis=1)
        rtrnInfo["nodeTimeDecile2WSS_AllNodes_Coo"] = ndTimeDecile2WSS_AllNdCoo

    if ndTimeDecile3WSS_AllNdCoo_out:
        ndTimeDecile3WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeDecile3WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeDecile3WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeDecile3WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 30, axis=1)
        rtrnInfo["nodeTimeDecile3WSS_AllNodes_Coo"] = ndTimeDecile3WSS_AllNdCoo

    if ndTimeDecile4WSS_AllNdCoo_out:
        ndTimeDecile4WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeDecile4WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeDecile4WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeDecile4WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 40, axis=1)
        rtrnInfo["nodeTimeDecile4WSS_AllNodes_Coo"] = ndTimeDecile4WSS_AllNdCoo

    if ndTimeDecile6WSS_AllNdCoo_out:
        ndTimeDecile6WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeDecile6WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeDecile6WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeDecile6WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 60, axis=1)
        rtrnInfo["nodeTimeDecile6WSS_AllNodes_Coo"] = ndTimeDecile6WSS_AllNdCoo

    if ndTimeDecile7WSS_AllNdCoo_out:
        ndTimeDecile7WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeDecile7WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeDecile7WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeDecile7WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 70, axis=1)
        rtrnInfo["nodeTimeDecile7WSS_AllNodes_Coo"] = ndTimeDecile7WSS_AllNdCoo

    if ndTimeDecile8WSS_AllNdCoo_out:
        ndTimeDecile8WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeDecile8WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeDecile8WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeDecile8WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 80, axis=1)
        rtrnInfo["nodeTimeDecile8WSS_AllNodes_Coo"] = ndTimeDecile8WSS_AllNdCoo

    if ndTimeDecile9WSS_AllNdCoo_out:
        ndTimeDecile9WSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeDecile9WSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeDecile9WSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeDecile9WSS_AllNdCoo[:, 4] = numpy.nanpercentile(ndWSSMagUse, 90, axis=1)
        rtrnInfo["nodeTimeDecile9WSS_AllNodes_Coo"] = ndTimeDecile9WSS_AllNdCoo

    if ndTimeSTDWSS_AllNdCoo_out:
        ndTimeSTDWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeSTDWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeSTDWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeSTDWSS_AllNdCoo[:, 4] = numpy.nanstd(ndWSSMagUse, axis=1, ddof=1)
        rtrnInfo["nodeTimeSTDWSS_AllNodes_Coo"] = ndTimeSTDWSS_AllNdCoo

    if ndTimeVarWSS_AllNdCoo_out:
        ndTimeVarWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeVarWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeVarWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeVarWSS_AllNdCoo[:, 4] = numpy.nanvar(ndWSSMagUse, axis=1, ddof=1)
        rtrnInfo["nodeTimeVarWSS_AllNodes_Coo"] = ndTimeVarWSS_AllNdCoo

    if ndTimeKurtWSS_AllNdCoo_out:
        ndTimeKurtWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeKurtWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeKurtWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeKurtWSS_AllNdCoo[:, 4] = scipy.stats.kurtosis(ndWSSMagUse, nan_policy='omit', axis=1)
        rtrnInfo["nodeTimeKurtosisWSS_AllNodes_Coo"] = ndTimeKurtWSS_AllNdCoo

    if ndTimeSkewWSS_AllNdCoo_out:
        ndTimeSkewWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeSkewWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeSkewWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeSkewWSS_AllNdCoo[:, 4] = scipy.stats.skew(ndWSSMagUse, nan_policy='omit', axis=1)
        rtrnInfo["nodeTimeSkewWSS_AllNodes_Coo"] = ndTimeSkewWSS_AllNdCoo

    if ndTimeSEWSS_AllNdCoo_out:
        ndTimeSEWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeSEWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeSEWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeSEWSS_AllNdCoo[:, 4] = scipy.stats.sem(ndWSSMagUse, nan_policy='omit', axis=1)
        rtrnInfo["nodeTimeSEWSS_AllNodes_Coo"] = ndTimeSEWSS_AllNdCoo

    if ndTimeEnergyWSS_AllNdCoo_out:
        ndTimeEnergyWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeEnergyWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeEnergyWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeEnergyWSS_AllNdCoo[:, 4] = numpy.nansum(numpy.power(ndWSSMagUse, 2), axis=1)
        rtrnInfo["nodeTimeEnergyWSS_AllNodes_Coo"] = ndTimeEnergyWSS_AllNdCoo

    if ndTimeEntropyWSS_AllNdCoo_out:
        ndTimeEntropyWSS_AllNdCoo = numpy.zeros([ndLstUseShp[0], 5])
        ndTimeEntropyWSS_AllNdCoo[:, 0] = ndLstUse
        ndTimeEntropyWSS_AllNdCoo[:, 1:4] = ndCooUse
        ndTimeEntropyWSS_AllNdCoo[:, 4] = scipy.stats.entropy(ndWSSMagUse, axis=1)
        rtrnInfo["nodeTimeEntropyWSS_AllNodes_Coo"] = ndTimeEntropyWSS_AllNdCoo

    # time
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------WSS processing time: {} s------".format(rtrnInfo["processTime"])

    # return
    rtrnInfo["nodalAveragePressure_UseNodes"] = ndAvePressure
    rtrnInfo["nodalWSSMagnitude_UseNodes"] = ndWSSMag
    rtrnInfo["nodalWSSTime_UseNodes"] = ndWSSTime
    rtrnInfo["Message"] = "Complete WSS calculation. \n" + rtrnInfo["processTimeMessage"]
    print(rtrnInfo["Message"])

    return rtrnInfo

"""
##############################################################################
# Func: Load Npy Files
##############################################################################
"""
import CFD_FEA_Post_Process

def LoadNpyFile(timePath,hexaElemPath,tetraElemPath,ndCooPath,elfElemGrpPath,timeStrsPath,timeLstPath):
    # load NPY data
    timeData = CFD_FEA_Post_Process.LoadNPY(path=timePath)
    hexaElem = CFD_FEA_Post_Process.LoadNPY(path=hexaElemPath)
    tetraElem = CFD_FEA_Post_Process.LoadNPY(path=tetraElemPath)
    ndCoo = CFD_FEA_Post_Process.LoadNPY(path=ndCooPath)
    elfElemGrp = CFD_FEA_Post_Process.LoadNPY(path=elfElemGrpPath)
    timeStrs = CFD_FEA_Post_Process.LoadNPY(path=timeStrsPath)
    timeLst = CFD_FEA_Post_Process.LoadNPY(path=timeLstPath)

    return timeData["data"], hexaElem["data"], tetraElem["data"], ndCoo["data"], elfElemGrp["data"], \
           timeStrs["data"], timeLst["data"]

"""
##############################################################################
# Func: Calc and Save
##############################################################################
"""
import Matrix_Math
def CalcandSave(faceSetRef, saveDirPath, timeStart, timeStop, timeData, hexaElem, tetraElem, ndCoo, elfElemGrp,
                timeStrs, timeLst):
    # Time-independent element face set node reference matching
    ## elf face-element-group
    elfFace = elfElemGrp[faceSetRef][:, 0]
    elfElem = elfElemGrp[faceSetRef][:, 1]

    # extract element and node refs from the ref group
    # hexa element match first
    hexaElemFaceNode = CFD_FEA_Post_Process.MatchElemNd(
        inMat=hexaElem,
        inCompareBase=elfElem,
        inCompareBaseSameOrder=elfFace)

    hexaElemFaceNodeDict = {}
    hexaElemFaceNodeDict["element"] = hexaElemFaceNode["orderCompareBase"]
    hexaElemFaceNodeDict["elementNodes"] = hexaElemFaceNode["matchInMat"]
    hexaElemFaceNodeDict["face"] = hexaElemFaceNode["orderCompareBaseSecond"]
    hexaElemFaceNodeDict["empty"] = hexaElemFaceNode["noMatch"]
    hexaElemFaceNodeDict["numberNodes"] = 8

    ## tetra element conditions
    tetraElemFaceNodeDict = {}
    tetraElemFaceNodeDict["numberNodes"] = 4
    if not hexaElemFaceNode["allMatch"]:  # Not all elelments are hexa
        tetraElemFaceNode = CFD_FEA_Post_Process.MatchElemNd(
            inMat=tetraElem,
            inCompareBase=elfElem,
            inCompareBaseSameOrder=elfFace
        )
        tetraElemFaceNodeDict["element"] = tetraElemFaceNode["orderCompareBase"]
        tetraElemFaceNodeDict["elementNodes"] = tetraElemFaceNode["matchInMat"]
        tetraElemFaceNodeDict["face"] = tetraElemFaceNode["orderCompareBaseSecond"]
        tetraElemFaceNodeDict["empty"] = tetraElemFaceNode["noMatch"]
    elif hexaElemFaceNode["allMatch"]:
        tetraElemFaceNodeDict["element"] = None
        tetraElemFaceNodeDict["elementNodes"] = None
        tetraElemFaceNodeDict["face"] = None
        tetraElemFaceNodeDict["empty"] = True

    # match face node in orders
    hexaElemFaceNdOrderDict = CFD_FEA_Post_Process.MatchFaceNdOrder(
        emptyCheck=hexaElemFaceNodeDict["empty"],
        elemNodes=hexaElemFaceNodeDict["elementNodes"],
        numberNodes=hexaElemFaceNodeDict["numberNodes"],
        faceMat=hexaElemFaceNodeDict["face"]
    )

    # match face node in orders
    tetraElemFaceNdOrderDict = CFD_FEA_Post_Process.MatchFaceNdOrder(
        emptyCheck=tetraElemFaceNodeDict["empty"],
        elemNodes=tetraElemFaceNodeDict["elementNodes"],
        numberNodes=tetraElemFaceNodeDict["numberNodes"],
        faceMat=tetraElemFaceNodeDict["face"]
    )

    # Fill each useful node with normal
    ## create empty array for final nd normal calcs
    ndMatShp = numpy.shape(ndCoo["Node_id"])
    ndNorms = numpy.zeros([ndMatShp[0], 4])
    ndNorms[:, 0] = ndCoo["Node_id"].T
    ndUseCalcs = numpy.zeros(ndMatShp)

    ## nd normals of different element
    ### check none case
    hexaElemNdNormDict = {}
    tetraElemNdNormDict = {}
    if hexaElemFaceNodeDict["empty"]:
        hexaElemNdNormDict["elemNormal"] = None
        hexaElemNdNormDict["empty"] = True
    elif not hexaElemFaceNodeDict["empty"]:
        hexaElemNdNormDict = CFD_FEA_Post_Process.NdNormalCalcs(
            ndMat=ndCoo["Node_id"],
            ndCooMat=ndCoo["Node_coo"],
            elemUse=hexaElemFaceNdOrderDict["ElemFaceNodeOrder"][:, 0],
            ndUse=hexaElemFaceNdOrderDict["ElemFaceNodeOrder"][:, 1:],
            emptyCheck=hexaElemFaceNodeDict["empty"]
        )
        hexaElemNdNormDict["empty"] = False

    if tetraElemFaceNodeDict["empty"]:
        tetraElemNdNormDict["elemNormal"] = None
        tetraElemNdNormDict["empty"] = True
    elif not tetraElemFaceNodeDict["empty"]:
        tetraElemNdNormDict = CFD_FEA_Post_Process.NdNormalCalcs(
            ndMat=ndCoo["Node_id"],
            ndCooMat=ndCoo["Node_coo"],
            elemUse=tetraElemFaceNdOrderDict["ElemFaceNodeOrder"][:, 0],
            ndUse=tetraElemFaceNdOrderDict["ElemFaceNodeOrder"][:, 1:],
            emptyCheck=tetraElemFaceNodeDict["empty"]
        )
        tetraElemNdNormDict["empty"] = False

    ## final normals and output to save
    ### elem to save
    hexaElemInterestDict = {}
    hexaElemInterestDict["Element8Nodes"] = hexaElemFaceNodeDict["elementNodes"]
    hexaElemInterestDict["Element4Nodes"] = hexaElemFaceNdOrderDict["ElemFaceNodeOrder"]
    hexaElemInterestDict["ElementNormal"] = hexaElemNdNormDict["elemNormal"]
    hexaElemInterestDict["face"] = hexaElemFaceNodeDict['face']

    tetraElemInterestDict = {}
    tetraElemInterestDict["Element8Nodes"] = tetraElemFaceNodeDict["elementNodes"]
    tetraElemInterestDict["Element4Nodes"] = tetraElemFaceNdOrderDict["ElemFaceNodeOrder"]
    tetraElemInterestDict["ElementNormal"] = tetraElemNdNormDict["elemNormal"]
    tetraElemInterestDict["face"] = tetraElemFaceNodeDict['face']

    ## Save
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=tetraElemInterestDict,
        fileName="tetraElemInterestDict",
        folderPath=saveDirPath
    )

    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=hexaElemInterestDict,
        fileName="hexaElemInterestDict",
        folderPath=saveDirPath
    )

    ### noode average normals for node bewteen hexa and tetra element
    if hexaElemNdNormDict["empty"] and tetraElemNdNormDict["empty"]:
        pass
    elif hexaElemNdNormDict["empty"]:
        ndNorms[:, 1:] = tetraElemNdNormDict['nodeNormal'][:, 1:]  # copy normals
        ndUseCalcs = tetraElemNdNormDict['nodeUseCalcs']
    elif tetraElemNdNormDict["empty"]:
        ndNorms[:, 1:] = hexaElemNdNormDict['nodeNormal'][:, 1:]  # copy normals
        ndUseCalcs = hexaElemNdNormDict['nodeUseCalcs']
    elif not hexaElemNdNormDict["empty"] and not tetraElemNdNormDict["empty"]:
        # adding
        ndNorms[:, 1:] = hexaElemNdNormDict['nodeNormal'][:, 1:] + tetraElemNdNormDict['nodeNormal'][:, 1:]
        ndUseCalcs = hexaElemNdNormDict['nodeUseCalcs'] + tetraElemNdNormDict['nodeUseCalcs']
        # average
        ndNorms[:, 1:] = ndNorms[:, 1:] / ndUseCalcs
        # unifise ndUseCalcs
        ndUseCalcs = (ndUseCalcs > 0) * 1

    ### nodes to save
    ndInterestDict = {}
    ndInterestDict["NodeNormal"] = ndNorms
    ndInterestDict["NodeToCalcs"] = ndUseCalcs
    ndInterestDict["NodeID"] = ndCoo["Node_id"]
    ndInterestDict["NodeCoord"] = ndCoo["Node_coo"]

    ### coo array
    ndCooArr = numpy.zeros([numpy.shape(ndCoo["Node_id"])[0], 4])
    ndCooArr[:, 0] = ndCoo["Node_id"]
    ndCooArr[:, 1:] = ndCoo["Node_coo"]

    ### save
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndInterestDict,
        fileName="ndInterestDict",
        folderPath=saveDirPath
    )
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndCooArr,
        fileName="ndCooArr",
        folderPath=saveDirPath
    )

    # Get time vector, nodal pressure and max shear stress
    ## LST [velocity-x velocity-y velocity-z nodal-pressure maxshear]
    ## STR stress [xx xy xz yx yy yz zx zy zz]
    ## compare time
    lstT = numpy.array(timeLst["timeRange"])
    strsT = numpy.array(timeStrs["timeRange"])
    CFD_FEA_Post_Process.ComapreLSTSTRTime(lstT=lstT, strsT=strsT)

    ## time range of interest
    outTimeStart, outTimeStop = Matrix_Math.SliceNumberCorrect(
        sliceStart=timeStart,
        sliceStop=timeStop,
        boundaryStart=lstT[0],
        boundaryStop=lstT[-1],
    )
    timeStep = lstT[numpy.where(numpy.logical_and(lstT >= outTimeStart, lstT <= outTimeStop))]

    ## Set time, nodal pressure (and max shear stress max(sigma_13) useless)
    # ### !!! temp
    # timeLst["prefix"] = 'lst_ParamsMat'
    # #####
    lstPrefx = timeLst["prefix"]
    ndLst = ndCoo["Node_id"]
    ndUseCalcs = numpy.array([ndUseCalcs]).T  # convert to m * 1
    pressIndex = timeLst['parameter'].index('NODAL_PRESSURE')
    maxShearIndex = timeLst['parameter'].index('MAX_SHEAR_STRESS')

    ndPressMaxShear = CFD_FEA_Post_Process.LSTNodalPressMaxShear(
        timeLst=timeLst,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        lstPrefx=lstPrefx,
        pressIndex=pressIndex,
        maxShearIndex=maxShearIndex,
    )

    # # Save time-average nodal pressure
    # ndTimeAvePressure_AllNd_Save = CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=ndPressMaxShear["nodeTimeAveragePressure_AllNodes"],
    #     fileName="ndTimeAvePressure_AllNd",
    #     folderPath=saveDirPath
    # )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeAveragePressure_AllNodes_Coo"],
        fileName="ndTimeAvePressureCoo",
        folderPath=saveDirPath
    )

    ndPressMaxShear = CFD_FEA_Post_Process.LSTNodalPressMaxShear(
        timeLst=timeLst,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        lstPrefx=lstPrefx,
        pressIndex=pressIndex,
        maxShearIndex=maxShearIndex,
        ndTimeMinPressure_AllNdCoo_out=True,
        ndTimeMaxPressure_AllNdCoo_out=True,
        ndTimePTPPressure_AllNdCoo_out=True,
        ndTimeQ1Pressure_AllNdCoo_out=True,
        ndTimeQ3Pressure_AllNdCoo_out=True,
        ndTimeIQRPressure_AllNdCoo_out=True,
        ndTimeMedianPressure_AllNdCoo_out=True
    )
    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeMinPressure_AllNodes_Coo"],
        fileName="ndTimeMinPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeMaxPressure_AllNodes_Coo"],
        fileName="ndTimeMaxPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimePTPPressure_AllNodes_Coo"],
        fileName="ndTimePTPPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeQ1Pressure_AllNodes_Coo"],
        fileName="ndTimeQ1PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeQ3Pressure_AllNodes_Coo"],
        fileName="ndTimeQ3PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeIQRPressure_AllNodes_Coo"],
        fileName="ndTimeIQRPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeMedianPressure_AllNodes_Coo"],
        fileName="ndTimeMedianPressureCoo",
        folderPath=saveDirPath
    )

    # Save nodal pressure
    ndPressMaxShear = CFD_FEA_Post_Process.LSTNodalPressMaxShear(
        timeLst=timeLst,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        lstPrefx=lstPrefx,
        pressIndex=pressIndex,
        maxShearIndex=maxShearIndex,
        ndTimeModePressure_AllNdCoo_out=True,
        ndTimeRMSPressure_AllNdCoo_out=True,
        ndTimeHMeanPressure_AllNdCoo_out=True,
        ndTimeGMeanPressure_AllNdCoo_out=True,
        ndTimeTriMeanPressure_AllNdCoo_out=True,
        ndTimeDecile1Pressure_AllNdCoo_out=True
    )
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeModePressure_AllNodes_Coo"],
        fileName="ndTimeModePressureCoo",
        folderPath=saveDirPath
    )

    # Save nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeRMSPressure_AllNodes_Coo"],
        fileName="ndTimeRMSPressureCoo",
        folderPath=saveDirPath
    )

    # Save nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeHMeanPressure_AllNodes_Coo"],
        fileName="ndTimeHMeanPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeGMeanPressure_AllNodes_Coo"],
        fileName="ndTimeGMeanPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeTriMeanPressure_AllNodes_Coo"],
        fileName="ndTimeTriMeanPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeDecile1Pressure_AllNodes_Coo"],
        fileName="ndTimeDecile1PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    ndPressMaxShear = CFD_FEA_Post_Process.LSTNodalPressMaxShear(
        timeLst=timeLst,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        lstPrefx=lstPrefx,
        pressIndex=pressIndex,
        maxShearIndex=maxShearIndex,
        ndTimeDecile2Pressure_AllNdCoo_out=True,
        ndTimeDecile3Pressure_AllNdCoo_out=True,
        ndTimeDecile4Pressure_AllNdCoo_out=True,
        ndTimeDecile6Pressure_AllNdCoo_out=True,
        ndTimeDecile7Pressure_AllNdCoo_out=True,
        ndTimeDecile8Pressure_AllNdCoo_out=True,
        ndTimeDecile9Pressure_AllNdCoo_out=True,
    )
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeDecile2Pressure_AllNodes_Coo"],
        fileName="ndTimeDecile2PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeDecile3Pressure_AllNodes_Coo"],
        fileName="ndTimeDecile3PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeDecile4Pressure_AllNodes_Coo"],
        fileName="ndTimeDecile4PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeDecile6Pressure_AllNodes_Coo"],
        fileName="ndTimeDecile6PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeDecile7Pressure_AllNodes_Coo"],
        fileName="ndTimeDecile7PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeDecile8Pressure_AllNodes_Coo"],
        fileName="ndTimeDecile8PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeDecile9Pressure_AllNodes_Coo"],
        fileName="ndTimeDecile9PressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    ndPressMaxShear = CFD_FEA_Post_Process.LSTNodalPressMaxShear(
        timeLst=timeLst,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        lstPrefx=lstPrefx,
        pressIndex=pressIndex,
        maxShearIndex=maxShearIndex,
        ndTimeSTDPressure_AllNdCoo_out=True,
        ndTimeVarPressure_AllNdCoo_out=True,
        ndTimeKurtPressure_AllNdCoo_out=True,
        ndTimeSkewPressure_AllNdCoo_out=True,
        ndTimeSEPressure_AllNdCoo_out=True,
        ndTimeEnergyPressure_AllNdCoo_out=True,
        ndTimeEntropyPressure_AllNdCoo_out=True
    )
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeSTDPressure_AllNodes_Coo"],
        fileName="ndTimeSTDPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeVarPressure_AllNodes_Coo"],
        fileName="ndTimeVarPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeKurtosisPressure_AllNodes_Coo"],
        fileName="ndTimeKurtosisPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeSkewPressure_AllNodes_Coo"],
        fileName="ndTimeSkewPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeSEPressure_AllNodes_Coo"],
        fileName="ndTimeSEPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeEnergyPressure_AllNodes_Coo"],
        fileName="ndTimeEnergyPressureCoo",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear["nodeTimeEntropyPressure_AllNodes_Coo"],
        fileName="ndTimeEntropyPressureCoo",
        folderPath=saveDirPath
    )

    """
    # compare time-average nodal pressure with uniform average comparing
    ## create empty
    ndLstShp = numpy.shape(ndLst)
    ndMeanPressure_AllNd = numpy.zeros([ndLstShp[0], 1])
    ## Calculate uniform mean
    ndMeanPressure_AllNd = numpy.mean(ndPressMaxShear["nodalPressure_AllNodes"], axis=1)
    ## compare results
    ndMeanPressure_AllNd_compare = CFD_FEA_Post_Process.CompareArrayDifference(
        Arr1=ndPressMaxShear["nodeTimeAveragePressure_AllNodes"][:, 1],
        Arr2=ndMeanPressure_AllNd,
        Arr1_Name="Nodal pressure time mean",
        Arr2_Name="Nodal pressure uniform mean",
        unit="Pa")
    """

    # Calculation for shear stress vector
    # ### !!! temp
    # timeStrs["prefix"] = 'strss_ParamsMat'
    # #####
    # print(timeStrs["prefix"])
    WSSDict = CFD_FEA_Post_Process.StrsWSS(
        timeStrs=timeStrs,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        ndNorms=ndNorms,
        strsPrefx=None,
        xxIndex=None,
        yyIndex=None,
        zzIndex=None,
        xyIndex=None,
        xzIndex=None,
        yzIndex=None
    )

    # check the nodal pressure is approximately same = blood pressure
    ## only non-zero in ndUseCalcs elements
    ndUseCalcs_Nonzero_indices = numpy.where(ndUseCalcs == 1)
    CFD_FEA_Post_Process.CompareArrayDifference(
        Arr1=(-WSSDict["nodalAveragePressure_UseNodes"][ndUseCalcs_Nonzero_indices[0], :]),
        Arr2=ndPressMaxShear["nodalPressure_UseNodes"][ndUseCalcs_Nonzero_indices[0], :],
        Arr1_Name="Nodal pressure average",
        Arr2_Name="Nodal pressure Adina",
        unit="Pa"
    )

    # # Save WSS results THIS change the data type
    # ndTimeAvePressure_AllNd_Save = CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=WSSDict,
    #     fileName="WSSDict",
    #     folderPath=saveDirPath
    # )

    # Save time-min nodal pressure
    WSSDict = CFD_FEA_Post_Process.StrsWSS(
        timeStrs=timeStrs,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        ndNorms=ndNorms,
        strsPrefx=None,
        xxIndex=None,
        yyIndex=None,
        zzIndex=None,
        xyIndex=None,
        xzIndex=None,
        yzIndex=None,
        ndTimeMinWSS_AllNdCoo_out=True,
        ndTimeMaxWSS_AllNdCoo_out=True,
        ndTimePTPWSS_AllNdCoo_out=True,
        ndTimeQ1WSS_AllNdCoo_out=True,
        ndTimeQ3WSS_AllNdCoo_out=True,
        ndTimeIQRWSS_AllNdCoo_out=True,
        ndTimeMedianWSS_AllNdCoo_out=True
    )
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeMinWSS_AllNodes_Coo"],
        fileName="ndTimeMinWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-max nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeMaxWSS_AllNodes_Coo"],
        fileName="ndTimeMaxWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-ptp nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimePTPWSS_AllNodes_Coo"],
        fileName="ndTimePTPWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-q1 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeQ1WSS_AllNodes_Coo"],
        fileName="ndTimeQ1WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-q3 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeQ3WSS_AllNodes_Coo"],
        fileName="ndTimeQ3WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-iqr nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeIQRWSS_AllNodes_Coo"],
        fileName="ndTimeIQRWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-median nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeMedianWSS_AllNodes_Coo"],
        fileName="ndTimeMedianWSSCoo",
        folderPath=saveDirPath
    )

    # Save time nodal wss
    WSSDict = CFD_FEA_Post_Process.StrsWSS(
        timeStrs=timeStrs,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        ndNorms=ndNorms,
        strsPrefx=None,
        xxIndex=None,
        yyIndex=None,
        zzIndex=None,
        xyIndex=None,
        xzIndex=None,
        yzIndex=None,
        ndTimeModeWSS_AllNdCoo_out=True,
        ndTimeRMSWSS_AllNdCoo_out=True,
        ndTimeHMeanWSS_AllNdCoo_out=True,
        ndTimeGMeanWSS_AllNdCoo_out=True,
        ndTimeTriMeanWSS_AllNdCoo_out=True,
        ndTimeDecile1WSS_AllNdCoo_out=True
    )
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeModeWSS_AllNodes_Coo"],
        fileName="ndTimeModeWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-RMS nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeRMSWSS_AllNodes_Coo"],
        fileName="ndTimeRMSWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-HMean nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeHMeanWSS_AllNodes_Coo"],
        fileName="ndTimeHMeanWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-GMean nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeGMeanWSS_AllNodes_Coo"],
        fileName="ndTimeGMeanWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-TriMean nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeTriMeanWSS_AllNodes_Coo"],
        fileName="ndTimeTriMeanWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Decile1 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeDecile1WSS_AllNodes_Coo"],
        fileName="ndTimeDecile1WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Decile3 nodal pressure
    WSSDict = CFD_FEA_Post_Process.StrsWSS(
        timeStrs=timeStrs,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        ndNorms=ndNorms,
        strsPrefx=None,
        xxIndex=None,
        yyIndex=None,
        zzIndex=None,
        xyIndex=None,
        xzIndex=None,
        yzIndex=None,
        ndTimeDecile2WSS_AllNdCoo_out=True,
        ndTimeDecile3WSS_AllNdCoo_out=True,
        ndTimeDecile4WSS_AllNdCoo_out=True,
        ndTimeDecile6WSS_AllNdCoo_out=True,
        ndTimeDecile7WSS_AllNdCoo_out=True,
        ndTimeDecile8WSS_AllNdCoo_out=True,
        ndTimeDecile9WSS_AllNdCoo_out=True
    )
    # Save time-Decile2 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeDecile2WSS_AllNodes_Coo"],
        fileName="ndTimeDecile2WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Decile3 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeDecile3WSS_AllNodes_Coo"],
        fileName="ndTimeDecile3WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Decile4 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeDecile4WSS_AllNodes_Coo"],
        fileName="ndTimeDecile4WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Decile6 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeDecile6WSS_AllNodes_Coo"],
        fileName="ndTimeDecile6WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Decile7 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeDecile7WSS_AllNodes_Coo"],
        fileName="ndTimeDecile7WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Decile8 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeDecile8WSS_AllNodes_Coo"],
        fileName="ndTimeDecile8WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Decile9 nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeDecile9WSS_AllNodes_Coo"],
        fileName="ndTimeDecile9WSSCoo",
        folderPath=saveDirPath
    )

    # Save time-variance nodal pressure
    WSSDict = CFD_FEA_Post_Process.StrsWSS(
        timeStrs=timeStrs,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        ndNorms=ndNorms,
        strsPrefx=None,
        xxIndex=None,
        yyIndex=None,
        zzIndex=None,
        xyIndex=None,
        xzIndex=None,
        yzIndex=None,
        ndTimeSTDWSS_AllNdCoo_out=True,
        ndTimeVarWSS_AllNdCoo_out=True,
        ndTimeKurtWSS_AllNdCoo_out=True,
        ndTimeSkewWSS_AllNdCoo_out=True,
        ndTimeSEWSS_AllNdCoo_out=True,
        ndTimeEnergyWSS_AllNdCoo_out=True,
        ndTimeEntropyWSS_AllNdCoo_out=True
    )
    # Save time-std nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeSTDWSS_AllNodes_Coo"],
        fileName="ndTimeSTDWSSCoo",
        folderPath=saveDirPath
    )

    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeVarWSS_AllNodes_Coo"],
        fileName="ndTimeVarWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-kurtosis nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeKurtosisWSS_AllNodes_Coo"],
        fileName="ndTimeKurtosisWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-skew nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeSkewWSS_AllNodes_Coo"],
        fileName="ndTimeSkewWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-SE nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeSEWSS_AllNodes_Coo"],
        fileName="ndTimeSEWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Energy nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeEnergyWSS_AllNodes_Coo"],
        fileName="ndTimeEnergyWSSCoo",
        folderPath=saveDirPath
    )

    # Save time-Entropy nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict["nodeTimeEntropyWSS_AllNodes_Coo"],
        fileName="ndTimeEntropyWSSCoo",
        folderPath=saveDirPath
    )

    # Calculate OSI, RRT, TAWSS
    ndWSSMag = WSSDict["nodalWSSMagnitude_UseNodes"]
    ndWSSTime = WSSDict["nodalWSSTime_UseNodes"]
    WSSParamDict = CFD_FEA_Post_Process.WSSParameters(
        timeStep=timeStep,
        ndLst=ndLst,
        ndUseCalcs=ndUseCalcs,
        ndWSSMag=ndWSSMag,
        ndWSSTime=ndWSSTime,
        ndCoo=ndCoo["Node_coo"]
    )

    # # Save TAWSS
    # nodalTAWSS_UseNodes_save = CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=WSSParamDict["nodalTAWSS_UseNodes"],
    #     fileName="ndTAWSS",
    #     folderPath=saveDirPath
    # )
    # # Save ndTAWSS_VectorMag
    # nodalWSS_VectorMagnitude_UseNodes_save = CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=WSSParamDict["nodalWSS_VectorMagnitude_UseNodes"],
    #     fileName="ndTAWSS_VectorMag",
    #     folderPath=saveDirPath)
    # # Save ndOSI
    # nodalOSI_UseNodes_save = CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=WSSParamDict["nodalOSI_UseNodes"],
    #     fileName="ndOSI",
    #     folderPath=saveDirPath
    # )
    # # Save ndRRT
    # nodalRRT_UseNodes_save = CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=WSSParamDict["nodalRRT_UseNodes"],
    #     fileName="ndRRT",
    #     folderPath=saveDirPath
    # )

    # save for matching
    # Save TAWSS
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSParamDict["nodalTAWSS_UseNodes_coordinates"],
        fileName="ndCooTAWSS",
        folderPath=saveDirPath
    )
    # Save ndTAWSS_VectorMag
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSParamDict["nodalWSS_VectorMagnitude_UseNodes_coordinates"],
        fileName="ndCooTAWSS_VectorMag",
        folderPath=saveDirPath
    )
    # Save ndOSI
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSParamDict["nodalOSI_UseNodes_coordinates"],
        fileName="ndCooOSI",
        folderPath=saveDirPath
    )
    # Save ndRRT
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSParamDict["nodalRRT_UseNodes_coordinates"],
        fileName="ndCooRRT",
        folderPath=saveDirPath
    )

    ## start ######## added by yang
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=ndPressMaxShear,
        fileName="fluid_PostResults_Dict",
        folderPath=saveDirPath
    )

    # Save time-average nodal pressure
    # fluid_TimeAvePressureDict_Save = CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=ndPressMaxShear["nodeTimeAveragePressure_AllNodes_Coo"],
    #     fileName="fluid_TimeAvePressureDict",
    #     folderPath=saveDirPath
    # )

    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSDict,
        fileName="fluid_PostResults_WssDict",
        folderPath=saveDirPath
    )
    # Save time-average nodal pressure
    CFD_FEA_Post_Process.SaveDictOrArr(
        inMat=WSSParamDict,
        fileName="fluid_TimeAvePressureDict",
        folderPath=saveDirPath
    )
    ############## end ############## yang



# """
# ##############################################################################
# # Func: output each time nodal pressure
# ##############################################################################
# """
#
#
# def LSTNodalPressMaxShear(
#         timeLst,
#         ndLst,
#         ndCoo,
#         timeStep,
#         ndUseCalcs,
#         lstPrefx=None,
#         pressIndex=None,
#         maxShearIndex=None
# ):
#     """
#     :param timeLst: Ditionary of LST file results
#     :param ndLst: array/list of node reference
#     :param timeStep: array/list of actual time steps (seconds)
#     :param ndUseCalcs: column vector-True when node is used for calcs
#     :param lstPrefx: string prefix for the timeLst dictionary item rerference
#     :param pressIndex: int (column number) of where NODAL_PRESSURE in timeLst time-step mat
#     :param maxShearIndex: int (column number) of where MAX_SHEAR_STRESS in timeLst time-step mat
#     :return: rtrnInfo = {}
#                 rtrnInfo["error"] = False
#                 rtrnInfo["errorMessage"] = None
#                 rtrnInfo["nodeTimeAveragePressure_AllNodes"] = None
#                 rtrnInfo["nodalPressure_AllNodes"] = None
#                 rtrnInfo["nodalPressure_UseNodes"] = None
#                 rtrnInfo["nodalMaxShear_UseNodes"] = None
#                 rtrnInfo["informationMessage"] = None
#                 rtrnInfo["processTime"] = None
#                 rtrnInfo["processTimeMessage"] = None
#     Set time, nodal pressure (and max shear stress max(sigma_13) useless)
#     """
#
#     # time
#     strtT = time.time()
#
#     # return info
#     rtrnInfo = {}
#     rtrnInfo["error"] = False
#     rtrnInfo["errorMessage"] = ""
#     rtrnInfo["nodeTimeAveragePressure_AllNodes"] = None
#     rtrnInfo["nodeTimeAveragePressure_AllNodes_Coo"] = None
#     rtrnInfo["nodalPressure_AllNodes"] = None
#     rtrnInfo["nodalPressure_UseNodes"] = None
#     rtrnInfo["nodalMaxShear_UseNodes"] = None
#     rtrnInfo["Message"] = ""
#     rtrnInfo["processTime"] = None
#     rtrnInfo["processTimeMessage"] = None
#
#     # find prefix if not given
#     if lstPrefx == None:
#         ## check key existing
#         if "prefix" in timeLst:
#             lstPrefx = timeLst["prefix"]
#         else:
#             rtrnInfo["error"] = True
#             rtrnInfo["errorMessage"] = "NEED provide lstPrefx"
#             print(rtrnInfo["errorMessage"])
#             return rtrnInfo
#     if pressIndex == None:
#         ## check key existing
#         if "parameter" in timeLst and 'NODAL_PRESSURE' in timeLst['parameter']:
#             pressIndex = timeLst['parameter'].index('NODAL_PRESSURE')
#         else:
#             rtrnInfo["error"] = True
#             rtrnInfo["errorMessage"] = "NEED provide pressIndex"
#             print(rtrnInfo["errorMessage"])
#             return rtrnInfo
#     if maxShearIndex == None:
#         ## check key existing
#         if "parameter" in timeLst and 'MAX_SHEAR_STRESS' in timeLst['parameter']:
#             maxShearIndex = timeLst['parameter'].index('MAX_SHEAR_STRESS')
#         else:
#             rtrnInfo["error"] = True
#             rtrnInfo["errorMessage"] = "NEED provide maxShearIndex"
#             print(rtrnInfo["errorMessage"])
#             return rtrnInfo
#
#     ### create empty mat
#     ndLstShp = numpy.shape(ndLst)
#     timeStepShp = numpy.shape(timeStep)
#
#     ndPressure = numpy.zeros([ndLstShp[0], timeStepShp[0]])
#     ndMaxShear = numpy.zeros([ndLstShp[0], timeStepShp[0]])
#     ndPressure_AllNd = numpy.zeros([ndLstShp[0], timeStepShp[0]])
#     ndTimeAvePressure_AllNd = numpy.zeros([ndLstShp[0], 2])
#
#     ndTimeAvePressure_AllNd[:, 0] = ndLst
#
#     ### for save results
#     ndTimeAvePressure_AllNdCoo = numpy.zeros([ndLstShp[0], 5])
#     ndTimeAvePressure_AllNdCoo[:, 0] = ndLst
#     ndTimeAvePressure_AllNdCoo[:, 1:4] = ndCoo
#
#     # loop values
#     for t in range(len(timeStep)):
#         # calculate useful nd lst for time t
#         matLst = numpy.multiply(ndUseCalcs, timeLst[lstPrefx + str(timeStep[t])])
#         ndPressure[:, t] = matLst[:, pressIndex]
#         ndMaxShear[:, t] = matLst[:, maxShearIndex]
#         # get all node nodal pressure
#         ndPressure_AllNd[:, t] = timeLst[lstPrefx + str(timeStep[t])][:, pressIndex]
#
#     # calculate time-averaged nodal pressure
#     ## For variaous time step
#     ## create empty for delta_P
#     ndPressureTimeDiff_AllNd = numpy.zeros([ndLstShp[0], timeStepShp[0] - 1])
#     ## delta p
#     ndPressureTimeDiff_AllNd = ndPressure_AllNd[:, 1:] + ndPressure_AllNd[:, :-1]
#     print("ndPressureTimeDiff_AllNd shape: {}".format(numpy.shape(ndPressureTimeDiff_AllNd)))
#     ## delta_t
#     deltaVecT = timeStep[1:] - timeStep[:-1]
#     print("delta_T shape: {}".format(numpy.shape(deltaVecT)))
#     ## t range
#     deltaT = timeStep[-1] - timeStep[0]
#     ## time-average all node nodal pressure
#     ndTimeAvePressure_AllNd[:, 1] = numpy.dot(ndPressureTimeDiff_AllNd, deltaVecT) * 0.5 / deltaT
#
#     ## for save results
#     ndTimeAvePressure_AllNdCoo[:, 4] = ndTimeAvePressure_AllNd[:, 1]
#
#     # time
#     stpT = time.time()
#     rtrnInfo["processTime"] = stpT - strtT
#     rtrnInfo["processTimeMessage"] = "------LST processing time: {} s------".format(rtrnInfo["processTime"])
#
#     # return
#     rtrnInfo["nodeTimeAveragePressure_AllNodes"] = ndTimeAvePressure_AllNd
#     rtrnInfo["nodeTimeAveragePressure_AllNodes_Coo"] = ndTimeAvePressure_AllNdCoo
#     rtrnInfo["nodalPressure_AllNodes"] = ndPressure_AllNd
#     rtrnInfo["nodalPressure_UseNodes"] = ndPressure
#     rtrnInfo["nodalMaxShear_UseNodes"] = ndMaxShear
#     rtrnInfo["Message"] = "Complete matching nodal pressure, max shear stress, " \
#                           "time-average nodal pressure calculation\n" + \
#                           rtrnInfo["processTimeMessage"]
#     print(rtrnInfo["Message"])
#
#     return rtrnInfo

"""
##############################################################################
# Func: Calc point time series
##############################################################################
"""

def PointTimeSeriesExtract(faceSetRef,
                            saveTablePath,
                            fileReference,
                            timeStart,
                            timeStop,
                            timeData,
                            hexaElem,
                            tetraElem,
                            ndCoo,
                            elfElemGrp,
                            timeStrs,
                            timeLst,
                            X,
                            Y,
                            Z):
    # Time-independent element face set node reference matching
    ## elf face-element-group
    elfFace = elfElemGrp[faceSetRef][:, 0]
    elfElem = elfElemGrp[faceSetRef][:, 1]

    # extract element and node refs from the ref group
    # hexa element match first
    hexaElemFaceNode = CFD_FEA_Post_Process.MatchElemNd(
        inMat=hexaElem,
        inCompareBase=elfElem,
        inCompareBaseSameOrder=elfFace)

    hexaElemFaceNodeDict = {}
    hexaElemFaceNodeDict["element"] = hexaElemFaceNode["orderCompareBase"]
    hexaElemFaceNodeDict["elementNodes"] = hexaElemFaceNode["matchInMat"]
    hexaElemFaceNodeDict["face"] = hexaElemFaceNode["orderCompareBaseSecond"]
    hexaElemFaceNodeDict["empty"] = hexaElemFaceNode["noMatch"]
    hexaElemFaceNodeDict["numberNodes"] = 8

    ## tetra element conditions
    tetraElemFaceNodeDict = {}
    tetraElemFaceNodeDict["numberNodes"] = 4
    if not hexaElemFaceNode["allMatch"]:  # Not all elelments are hexa
        tetraElemFaceNode = CFD_FEA_Post_Process.MatchElemNd(
            inMat=tetraElem,
            inCompareBase=elfElem,
            inCompareBaseSameOrder=elfFace
        )
        tetraElemFaceNodeDict["element"] = tetraElemFaceNode["orderCompareBase"]
        tetraElemFaceNodeDict["elementNodes"] = tetraElemFaceNode["matchInMat"]
        tetraElemFaceNodeDict["face"] = tetraElemFaceNode["orderCompareBaseSecond"]
        tetraElemFaceNodeDict["empty"] = tetraElemFaceNode["noMatch"]
    elif hexaElemFaceNode["allMatch"]:
        tetraElemFaceNodeDict["element"] = None
        tetraElemFaceNodeDict["elementNodes"] = None
        tetraElemFaceNodeDict["face"] = None
        tetraElemFaceNodeDict["empty"] = True

    # match face node in orders
    hexaElemFaceNdOrderDict = CFD_FEA_Post_Process.MatchFaceNdOrder(
        emptyCheck=hexaElemFaceNodeDict["empty"],
        elemNodes=hexaElemFaceNodeDict["elementNodes"],
        numberNodes=hexaElemFaceNodeDict["numberNodes"],
        faceMat=hexaElemFaceNodeDict["face"]
    )

    # match face node in orders
    tetraElemFaceNdOrderDict = CFD_FEA_Post_Process.MatchFaceNdOrder(
        emptyCheck=tetraElemFaceNodeDict["empty"],
        elemNodes=tetraElemFaceNodeDict["elementNodes"],
        numberNodes=tetraElemFaceNodeDict["numberNodes"],
        faceMat=tetraElemFaceNodeDict["face"]
    )

    # Fill each useful node with normal
    ## create empty array for final nd normal calcs
    ndMatShp = numpy.shape(ndCoo["Node_id"])
    ndNorms = numpy.zeros([ndMatShp[0], 4])
    ndNorms[:, 0] = ndCoo["Node_id"].T
    ndUseCalcs = numpy.zeros(ndMatShp)

    ## nd normals of different element
    ### check none case
    hexaElemNdNormDict = {}
    tetraElemNdNormDict = {}
    if hexaElemFaceNodeDict["empty"]:
        hexaElemNdNormDict["elemNormal"] = None
        hexaElemNdNormDict["empty"] = True
    elif not hexaElemFaceNodeDict["empty"]:
        hexaElemNdNormDict = CFD_FEA_Post_Process.NdNormalCalcs(
            ndMat=ndCoo["Node_id"],
            ndCooMat=ndCoo["Node_coo"],
            elemUse=hexaElemFaceNdOrderDict["ElemFaceNodeOrder"][:, 0],
            ndUse=hexaElemFaceNdOrderDict["ElemFaceNodeOrder"][:, 1:],
            emptyCheck=hexaElemFaceNodeDict["empty"]
        )
        hexaElemNdNormDict["empty"] = False

    if tetraElemFaceNodeDict["empty"]:
        tetraElemNdNormDict["elemNormal"] = None
        tetraElemNdNormDict["empty"] = True
    elif not tetraElemFaceNodeDict["empty"]:
        tetraElemNdNormDict = CFD_FEA_Post_Process.NdNormalCalcs(
            ndMat=ndCoo["Node_id"],
            ndCooMat=ndCoo["Node_coo"],
            elemUse=tetraElemFaceNdOrderDict["ElemFaceNodeOrder"][:, 0],
            ndUse=tetraElemFaceNdOrderDict["ElemFaceNodeOrder"][:, 1:],
            emptyCheck=tetraElemFaceNodeDict["empty"]
        )
        tetraElemNdNormDict["empty"] = False

    ## final normals and output to save
    ### elem to save
    hexaElemInterestDict = {}
    hexaElemInterestDict["Element8Nodes"] = hexaElemFaceNodeDict["elementNodes"]
    hexaElemInterestDict["Element4Nodes"] = hexaElemFaceNdOrderDict["ElemFaceNodeOrder"]
    hexaElemInterestDict["ElementNormal"] = hexaElemNdNormDict["elemNormal"]
    hexaElemInterestDict["face"] = hexaElemFaceNodeDict['face']

    tetraElemInterestDict = {}
    tetraElemInterestDict["Element8Nodes"] = tetraElemFaceNodeDict["elementNodes"]
    tetraElemInterestDict["Element4Nodes"] = tetraElemFaceNdOrderDict["ElemFaceNodeOrder"]
    tetraElemInterestDict["ElementNormal"] = tetraElemNdNormDict["elemNormal"]
    tetraElemInterestDict["face"] = tetraElemFaceNodeDict['face']

    # ## Save
    # CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=tetraElemInterestDict,
    #     fileName="tetraElemInterestDict",
    #     folderPath=saveDirPath
    # )
    #
    # CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=hexaElemInterestDict,
    #     fileName="hexaElemInterestDict",
    #     folderPath=saveDirPath
    # )

    ### noode average normals for node bewteen hexa and tetra element
    if hexaElemNdNormDict["empty"] and tetraElemNdNormDict["empty"]:
        pass
    elif hexaElemNdNormDict["empty"]:
        ndNorms[:, 1:] = tetraElemNdNormDict['nodeNormal'][:, 1:]  # copy normals
        ndUseCalcs = tetraElemNdNormDict['nodeUseCalcs']
    elif tetraElemNdNormDict["empty"]:
        ndNorms[:, 1:] = hexaElemNdNormDict['nodeNormal'][:, 1:]  # copy normals
        ndUseCalcs = hexaElemNdNormDict['nodeUseCalcs']
    elif not hexaElemNdNormDict["empty"] and not tetraElemNdNormDict["empty"]:
        # adding
        ndNorms[:, 1:] = hexaElemNdNormDict['nodeNormal'][:, 1:] + tetraElemNdNormDict['nodeNormal'][:, 1:]
        ndUseCalcs = hexaElemNdNormDict['nodeUseCalcs'] + tetraElemNdNormDict['nodeUseCalcs']
        # average
        ndNorms[:, 1:] = ndNorms[:, 1:] / ndUseCalcs
        # unifise ndUseCalcs
        ndUseCalcs = (ndUseCalcs > 0) * 1

    ### nodes to save
    ndInterestDict = {}
    ndInterestDict["NodeNormal"] = ndNorms
    ndInterestDict["NodeToCalcs"] = ndUseCalcs
    ndInterestDict["NodeID"] = ndCoo["Node_id"]
    ndInterestDict["NodeCoord"] = ndCoo["Node_coo"]

    ### coo array
    ndCooArr = numpy.zeros([numpy.shape(ndCoo["Node_id"])[0], 4])
    ndCooArr[:, 0] = ndCoo["Node_id"]
    ndCooArr[:, 1:] = ndCoo["Node_coo"]

    # ### save
    # CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=ndInterestDict,
    #     fileName="ndInterestDict",
    #     folderPath=saveDirPath
    # )
    # CFD_FEA_Post_Process.SaveDictOrArr(
    #     inMat=ndCooArr,
    #     fileName="ndCooArr",
    #     folderPath=saveDirPath
    # )

    # Get time vector, nodal pressure and max shear stress
    ## LST [velocity-x velocity-y velocity-z nodal-pressure maxshear]
    ## STR stress [xx xy xz yx yy yz zx zy zz]
    ## compare time
    lstT = numpy.array(timeLst["timeRange"])
    strsT = numpy.array(timeStrs["timeRange"])
    CFD_FEA_Post_Process.ComapreLSTSTRTime(lstT=lstT, strsT=strsT)

    ## time range of interest
    outTimeStart, outTimeStop = Matrix_Math.SliceNumberCorrect(
        sliceStart=timeStart,
        sliceStop=timeStop,
        boundaryStart=lstT[0],
        boundaryStop=lstT[-1],
    )
    timeStep = lstT[numpy.where(numpy.logical_and(lstT >= outTimeStart, lstT <= outTimeStop))]

    ## Set time, nodal pressure (and max shear stress max(sigma_13) useless)
    # ### !!! temp
    # timeLst["prefix"] = 'lst_ParamsMat'
    # #####
    lstPrefx = timeLst["prefix"]
    ndLst = ndCoo["Node_id"]
    ndUseCalcs = numpy.array([ndUseCalcs]).T  # convert to m * 1
    pressIndex = timeLst['parameter'].index('NODAL_PRESSURE')
    maxShearIndex = timeLst['parameter'].index('MAX_SHEAR_STRESS')

    # check folder
    Save_Load_File.checkCreateDir(path=saveTablePath)

    # save points
    pointCSVPath = saveTablePath + '\\' + 'PointLabelXYZ.csv'

    outPointTable = {'Label': ndLst,
                     'X': ndCoo["Node_coo"][:, 0],
                     'Y': ndCoo["Node_coo"][:, 1],
                     'Z': ndCoo["Node_coo"][:, 2]}

    # output
    outPointTable_df = pandas.DataFrame.from_dict(outPointTable)
    Pd_Funs.SaveDF(outPath=pointCSVPath, pdIn=outPointTable_df, header=True)

    # output files
    pressureCSVPath = saveTablePath + '\\' + fileReference + '_P.csv'
    WSSCSVPath = saveTablePath + '\\' + fileReference + '_WSS.csv'

    CFD_FEA_Post_Process.PointPressureTimeSeries(
        timeLst=timeLst,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        lstPrefx=lstPrefx,
        pressIndex=pressIndex,
        maxShearIndex=maxShearIndex,
        SaveTablePath=pressureCSVPath,
        X=X,
        Y=Y,
        Z=Z
    )

    # Save time-variance nodal pressure
    CFD_FEA_Post_Process.PointWSSTimeSeries(
        timeStrs=timeStrs,
        ndLst=ndLst,
        ndCoo=ndCoo["Node_coo"],
        timeStep=timeStep,
        ndUseCalcs=ndUseCalcs,
        ndNorms=ndNorms,
        strsPrefx=None,
        xxIndex=None,
        yyIndex=None,
        zzIndex=None,
        xyIndex=None,
        xzIndex=None,
        yzIndex=None,
        SaveTablePath=WSSCSVPath,
        X=X,
        Y=Y,
        Z=Z
    )


"""
##############################################################################
#Func: Set time, nodal pressure (and max shear stress max(sigma_13) useless)
##############################################################################
"""
import scipy.stats
import copy


def PointPressureTimeSeries(
        timeLst,
        ndLst,
        ndCoo,
        timeStep,
        ndUseCalcs,
        lstPrefx=None,
        pressIndex=None,
        maxShearIndex=None,
        SaveTablePath='',
        X=0,
        Y=0,
        Z=0
):

    # time
    strtT = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None

    # find prefix if not given
    if lstPrefx == None:
        ## check key existing
        if "prefix" in timeLst:
            lstPrefx = timeLst["prefix"]
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide lstPrefx"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if pressIndex == None:
        ## check key existing
        if "parameter" in timeLst and 'NODAL_PRESSURE' in timeLst['parameter']:
            pressIndex = timeLst['parameter'].index('NODAL_PRESSURE')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide pressIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if maxShearIndex == None:
        ## check key existing
        if "parameter" in timeLst and 'MAX_SHEAR_STRESS' in timeLst['parameter']:
            maxShearIndex = timeLst['parameter'].index('MAX_SHEAR_STRESS')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide maxShearIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo

    ### create empty mat
    ndLstShp = numpy.shape(ndLst)
    timeStepShp = numpy.shape(timeStep)

    ndPressure = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndMaxShear = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndPressure_AllNd = numpy.zeros([ndLstShp[0], timeStepShp[0]])

    # loop values
    for t in range(len(timeStep)):
        # calculate useful nd lst for time t
        matLst = numpy.multiply(ndUseCalcs, timeLst[lstPrefx + str(timeStep[t])])
        ndPressure[:, t] = matLst[:, pressIndex]
        ndMaxShear[:, t] = matLst[:, maxShearIndex]
        # get all node nodal pressure
        ndPressure_AllNd[:, t] = timeLst[lstPrefx + str(timeStep[t])][:, pressIndex]

    # point position
    pointXYZ = [float(X), float(Y), float(Z)]
    print(pointXYZ)

    # # save intermediate
    # AllNdCoo = numpy.zeros([ndLstShp[0], 5])
    # AllNdCoo[:, 0] = ndLst
    # AllNdCoo[:, 1:4] = ndCoo
    #
    # a = numpy.asarray(AllNdCoo)
    # numpy.savetxt("E:/PythonTest/Npy/foo.csv", a, delimiter=",")

    # find position
    #print(ndCoo == pointXYZ)
    print(pointXYZ)
    print(ndCoo[8974])
    print(ndCoo[8974]==pointXYZ)
    rowIndex = numpy.where(numpy.all(ndCoo == pointXYZ, axis=1))
    print(rowIndex)

    # # Output
    # row = rowIndex[0][0]
    # pressureOut = ndPressure_AllNd[row]
    # outTable = [timeStep, pressureOut]
    #
    # # Output table
    # a = numpy.transpose(numpy.asarray(outTable))
    # numpy.savetxt(SaveTablePath, a, delimiter=",")

    # Output
    try:
        row = rowIndex[0][0]
        pressureOut = ndPressure_AllNd[row]
        outTable = {'Time': timeStep, 'P': pressureOut}

        # output
        outTable_df = pandas.DataFrame.from_dict(outTable)
        Pd_Funs.SaveDF(outPath=SaveTablePath, pdIn=outTable_df, header=True)
    except:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = 'NO point match!!!'
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    # time
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------LST processing time: {} s------".format(rtrnInfo["processTime"])
    print(rtrnInfo["processTimeMessage"])

    return rtrnInfo

"""
##############################################################################
#Func: Calculation for shear stress vector
##############################################################################
"""
import scipy.stats


def PointWSSTimeSeries(
        timeStrs,
        ndLst,
        ndCoo,
        timeStep,
        ndUseCalcs,
        ndNorms,
        strsPrefx=None,
        xxIndex=None,
        yyIndex=None,
        zzIndex=None,
        xyIndex=None,
        xzIndex=None,
        yzIndex=None,
        SaveTablePath='',
        X=0,
        Y=0,
        Z=0
):

    # time
    strtT = time.time()

    # return info
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["errorMessage"] = ""

    # find prefix if not given
    if strsPrefx == None:
        ## check key existing
        if "prefix" in timeStrs:
            strsPrefx = timeStrs["prefix"]
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide strsPrefx"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if xxIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-XX' in timeStrs['parameter']:
            xxIndex = timeStrs['parameter'].index('STRESS-XX')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide xxIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if yyIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-YY' in timeStrs['parameter']:
            yyIndex = timeStrs['parameter'].index('STRESS-YY')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide yyIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if zzIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-ZZ' in timeStrs['parameter']:
            zzIndex = timeStrs['parameter'].index('STRESS-ZZ')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide zzIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if xyIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-XY' in timeStrs['parameter']:
            xyIndex = timeStrs['parameter'].index('STRESS-XY')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide xyIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if xzIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-XZ' in timeStrs['parameter']:
            xzIndex = timeStrs['parameter'].index('STRESS-XZ')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide xzIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo
    if yzIndex == None:
        ## check key existing
        if "parameter" in timeStrs and 'STRESS-YZ' in timeStrs['parameter']:
            yzIndex = timeStrs['parameter'].index('STRESS-YZ')
        else:
            rtrnInfo["error"] = True
            rtrnInfo["errorMessage"] = "NEED provide yzIndex"
            print(rtrnInfo["errorMessage"])
            return rtrnInfo

    # shape & empty mat
    ndLstShp = numpy.shape(ndLst)
    timeStepShp = numpy.shape(timeStep)

    ndAvePressure = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndWSSMag = numpy.zeros([ndLstShp[0], timeStepShp[0]])
    ndWSSTime = numpy.zeros([timeStepShp[0], ndLstShp[0], 3])

    # loop through time
    for t in range(len(timeStep)):
        # usefull mat at each timestep
        matLst = numpy.multiply(ndUseCalcs, timeStrs[strsPrefx + str(timeStep[t])])

        # create empty array
        ndShearVecT = numpy.zeros([ndLstShp[0], 3])
        ndShearVecMagT = numpy.zeros([ndLstShp[0], 1])
        ndPressureT = numpy.zeros([ndLstShp[0], 1])

        ## loop through each node
        for node in range(len(ndLst)):
            # jump not used nodes
            if not ndUseCalcs[node, :]:
                continue

            # stress sigma
            strsFlat = matLst[node]
            xx = strsFlat[xxIndex]
            yy = strsFlat[yyIndex]
            zz = strsFlat[zzIndex]
            xy = strsFlat[xyIndex]
            xz = strsFlat[xzIndex]
            yz = strsFlat[yzIndex]
            zx = xz
            zy = yz
            yx = xy
            # stress tensor
            strsSigma = numpy.array([[xx, xy, xz],
                                     [yx, yy, yz],
                                     [zx, zy, zz]])
            # hydrostatic pressure
            hydroStaPress = numpy.mean([xx, yy, zz])

            # if node < 100:
            #     print("uniform pressure(Pa): {}".format(hydroStaPress))

            # stress tensor remove hydrostatic pressure = shear stress only
            strsSigmaShear = strsSigma - numpy.identity(3) * hydroStaPress

            # normal direction
            ndNorm = ndNorms[node, 1:]
            # normalise again for saftey
            norm = numpy.linalg.norm(ndNorm)
            ndNorm = ndNorm / norm

            # matrix multiplication
            wallStress = numpy.dot(strsSigmaShear, ndNorm)  # this should be shear stress
            wallNormalStress = numpy.dot(ndNorm, wallStress) * ndNorm  # for security remove the normal component again

            # if numpy.sum(wallNormalStress) != 0 and node < 100:
            #     print("Normal stress after remove hydrostatic pressure is not ZERO!")
            #     print(wallNormalStress)

            wallShearStress = wallStress - wallNormalStress  # wall shear stress vector

            # updated
            ndShearVecT[node] = wallShearStress
            ndShearVecMagT[node] = numpy.linalg.norm(wallShearStress)
            ndPressureT[node] = hydroStaPress

        # updated value of each time
        """
        # Note in Fluid pressure is +ve when compression
        # Note in Solid tension is +ve 
        """
        ndAvePressure[:, t] = ndPressureT[:, 0]
        ndWSSMag[:, t] = ndShearVecMagT[:, 0]
        ndWSSTime[t, :, :] = ndShearVecT

    # use nodes label and coordinates
    ndLstUse = ndLst[numpy.where(ndUseCalcs == 1)[0]]
    ndCooUse = ndCoo[numpy.where(ndUseCalcs == 1)[0], :]
    ndWSSMagUse = ndWSSMag[numpy.where(ndUseCalcs == 1)[0], :]
    ndLstUseShp = numpy.shape(ndLstUse)

    # replace 0 to 1
    ndWSSMagUse_0r1 = copy.deepcopy(ndWSSMagUse)
    ndWSSMagUse_0r1 = numpy.abs(ndWSSMagUse_0r1)
    ndWSSMagUse_0r1[ndWSSMagUse_0r1 == 0] = 1

    # point position
    pointXYZ = [float(X), float(Y), float(Z)]

    # # save intermediate
    # AllNdCoo = numpy.zeros([ndLstShp[0], 5])
    # AllNdCoo[:, 0] = ndLst
    # AllNdCoo[:, 1:4] = ndCoo
    #
    # a = numpy.asarray(AllNdCoo)
    # numpy.savetxt("E:/PythonTest/Npy/foo.csv", a, delimiter=",")

    # find position
    print(pointXYZ)
    print(ndCoo[8974])
    print(ndCoo[8974] == pointXYZ)
    rowIndex = numpy.where(numpy.all(ndCoo == pointXYZ, axis=1))

    # Output
    try:
        row = rowIndex[0][0]
        WSSOut = ndWSSMagUse[row]
        outTable = {'Time': timeStep, 'WSS': WSSOut}

        # output
        outTable_df = pandas.DataFrame.from_dict(outTable)
        Pd_Funs.SaveDF(outPath=SaveTablePath, pdIn=outTable_df, header=True)
    except:
        rtrnInfo["error"] = True
        rtrnInfo["errorMessage"] = 'NO point match!!!'
        print(rtrnInfo["errorMessage"])
        return rtrnInfo

    # time
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------WSS processing time: {} s------".format(rtrnInfo["processTime"])
    print(rtrnInfo["processTimeMessage"])

    return rtrnInfo