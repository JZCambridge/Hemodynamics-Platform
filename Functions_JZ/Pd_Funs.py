# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 19:44:24 2020

@author: yingmohuanzhou
"""

import Save_Load_File

"""
##############################################################################
# Func: open csv, txt to multiply columns
##############################################################################
"""
import pandas
import numpy
import time


def MultiplyCSVColumns(
        inPath,
        multiples,
        columns,
        outPath
):
    # initiation
    # time
    strtT = time.time()
    # return information
    rtrnInfo = {}
    rtrnInfo["error"] = False
    rtrnInfo["processTime"] = None
    rtrnInfo["processTimeMessage"] = None
    rtrnInfo["compareResults"] = []
    rtrnInfo["message"] = ""

    # input path to be txt, csv, xlsx
    extension = Save_Load_File.ExtensionFromPath(inPath)
    if extension is None:
        rtrnInfo["error"] = True
        rtrnInfo["message"] += "ERROR: No extension found!"
        return rtrnInfo

    # load
    if 'csv' in extension:
        pdIn = pandas.read_csv(inPath, sep=',', header=None)
    elif 'txt' in extension:
        pdIn = pandas.read_csv(inPath, sep='\t', header=None)
    elif 'xlsx' in extension:
        pdIn = pandas.read_excel(inPath, header=None)
    elif 'xls' in extension:
        pdIn = pandas.read_excel(inPath, header=None)
    elif 'xlsm' in extension:
        pdIn = pandas.read_excel(inPath, header=None)
    elif 'xlsb' in extension:
        pdIn = pandas.read_excel(inPath, header=None)
    elif 'odf' in extension:
        pdIn = pandas.read_excel(inPath, header=None)

    # multiplication
    multipleUpdate = True
    multiple = None
    if len(multiples) != len(columns):
        multiple = multiples[0]
        multipleUpdate = False

    for case in range(len(columns)):
        colm = int(columns[case])
        if multipleUpdate: multiple = multiples[case]

        # update cloumns
        pdIn[pdIn.columns[colm]] = pdIn[pdIn.columns[colm]] * multiple

    # output extension
    extensionOut = Save_Load_File.ExtensionFromPath(outPath)

    # output
    if 'csv' in extensionOut:
        pdIn.to_csv(outPath, sep=',', index=False, header=None)
    elif extensionOut is None:
        pdIn.to_csv(outPath + '.csv', sep=',', index=False, header=None)
    elif 'txt' in extensionOut:
        pdIn.to_csv(outPath, sep='\t', index=False, header=None)
    elif 'xlsx' in extensionOut:
        pdIn.to_excel(outPath, index=False, header=None)
    elif 'xls' in extensionOut:
        pdIn.to_excel(outPath, index=False, header=None)
    elif 'xlsm' in extensionOut:
        pdIn.to_excel(outPath, index=False, header=None)
    elif 'xlsb' in extensionOut:
        pdIn.to_excel(outPath, index=False, header=None)
    elif 'odf' in extensionOut:
        pdIn.to_excel(outPath, index=False, header=None)

    # return information
    stpT = time.time()
    rtrnInfo["processTime"] = stpT - strtT
    rtrnInfo["processTimeMessage"] = "------CSV/Table multiplication time: {} s------".format(rtrnInfo["processTime"])
    rtrnInfo["message"] += "Complete CSV/Table save to:\n{}\n{}".format(outPath, rtrnInfo["processTimeMessage"])
    print(rtrnInfo["message"])

    return rtrnInfo


"""
##############################################################################
# Func: open csv, txt return dataframe
##############################################################################
"""


def OpenDF(
        inPath,
        header=None,
        usecols=None,
        index_col=None
):
    # input path to be txt, csv, xlsx
    extension = Save_Load_File.ExtensionFromPath(inPath)
    if extension is None:
        raise ValueError("ERROR: No extension found!")

    # load
    if 'csv' in extension:
        pdIn = pandas.read_csv(inPath, sep=',', header=header, index_col=index_col)
    elif 'txt' in extension:
        pdIn = pandas.read_csv(inPath, sep='\t', header=header, index_col=index_col)
    elif 'xlsx' in extension:
        pdIn = pandas.read_excel(inPath, header=header, index_col=index_col)
    elif 'xls' in extension:
        pdIn = pandas.read_excel(inPath, header=header, index_col=index_col)
    elif 'xlsm' in extension:
        pdIn = pandas.read_excel(inPath, header=header, index_col=index_col)
    elif 'xlsb' in extension:
        pdIn = pandas.read_excel(inPath, header=header, index_col=index_col)
    elif 'odf' in extension:
        pdIn = pandas.read_excel(inPath, header=header, index_col=index_col)
    else:
        raise ValueError("Cannot open dataframe of: {}".format(inPath))

    # keep useful columes
    # check all names are in columns
    if usecols is not None:
        inColumns = []
        for element in usecols:
            if element in pdIn.columns:
                inColumns.append(element)

        DF = pdIn[inColumns]
    else:
        DF = pdIn

    return DF


"""
##############################################################################
# Func: save data frame
##############################################################################
"""


def SaveDF(
        outPath,
        pdIn,
        header=True,
        index=False
):
    # input path to be txt, csv, xlsx
    extension = Save_Load_File.ExtensionFromPath(outPath)
    if extension is None:
        raise ValueError("ERROR: No extension found!")

    # output
    if 'csv' in extension:
        pdIn.to_csv(outPath, sep=',', index=index, header=header)
    elif extension is None:
        pdIn.to_csv(outPath + '.csv', sep=',', index=index, header=header)
    elif 'txt' in extension:
        pdIn.to_csv(outPath, sep='\t', index=index, header=header)
    elif 'xlsx' in extension:
        pdIn.to_excel(outPath, index=index, header=header)
    elif 'xls' in extension:
        pdIn.to_excel(outPath, index=index, header=header)
    elif 'xlsm' in extension:
        pdIn.to_excel(outPath, index=index, header=header)
    elif 'xlsb' in extension:
        pdIn.to_excel(outPath, index=index, header=header)
    elif 'odf' in extension:
        pdIn.to_excel(outPath, index=index, header=header)
    else:
        raise ValueError("Cannot open dataframe of: {}".format(inPath))

    return
