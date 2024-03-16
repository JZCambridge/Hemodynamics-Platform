# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 20:00:28 2020

@author: yingmohuanzhou
"""

import sys
import os

import Save_Load_File
import Image_Process_Functions
import Pd_Funs
import Matrix_Math
import SITK_Numpy

# import standard lib
import numpy
import json

def WriteDic(Outpath=None, branchLst=None):
    """
    # write dictionary
    """
    jsonOut = Outpath
    coronaryArtery = [
        # LCA
        {
            "branch_name": "LM",
            "label": [5],
            "branch_label": "2",
            "parent_branch": 'N',
            "exist": False,
            "use": False,
            "parent_exist": None,
            "original_csv": "LMExt.csv",  # Json to csv
            "3D_csv": "LM3D.csv",  # Xsecion 3D csv
            "original_branch": "LM_OriB_",  # Filter mask original branch
            "cross_section_image_NN": "LMCTANN.nii.gz",  # Xsection CTA NN
            "cross_section_mask_NN": "LMValNN.nii.gz",  # Xsection mask NN
            "cross_section_mask_fix": "LMValNNFixVal.nii.gz",  # Lumen correction fix mask
            "cross_section_mask_fix_extension": "LMValNNFE.nii.gz",  # Extension
            "original_volume_mask_fix": "LMValNNFEOV.nii.gz",  # Original volume
            "cross_section_image_LI": "LMCTALI.nii.gz",  # Xsection CTA LI
            "cross_section_mask_LI": "LMValLI.nii.gz"  # Xsection mask LI
        },
        {
            "branch_name": "IMB",
            "label": [50],
            "branch_label": "2,3",
            "parent_branch": "LM",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "IMB.csv",
            "3D_csv": "IMB3D.csv",
            "original_branch": "IMB_OriB_",
            "cross_section_image_NN": "IMBCTANN.nii.gz",
            "cross_section_mask_NN": "IMBValNN.nii.gz",
            "cross_section_mask_fix": "IMBValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "IMBValNNFE.nii.gz",
            "original_volume_mask_fix": "IMBValNNFEOV.nii.gz",
            "cross_section_image_LI": "IMBCTALI.nii.gz",
            "cross_section_mask_LI": "IMBValLI.nii.gz"
        },
        {
            "branch_name": "pLAD",
            "label": [6],
            "branch_label": "2,1",
            "parent_branch": "LM",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "pLADExt.csv",
            "3D_csv": "pLAD3D.csv",
            "original_branch": "pLAD_OriB_",
            "cross_section_image_NN": "pLADCTANN.nii.gz",
            "cross_section_mask_NN": "pLADValNN.nii.gz",
            "cross_section_mask_fix": "pLADValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "pLADValNNFE.nii.gz",
            "original_volume_mask_fix": "pLADValNNFEOV.nii.gz",
            "cross_section_image_LI": "pLADCTALI.nii.gz",
            "cross_section_mask_LI": "pLADValLI.nii.gz"
        },
        {
            "branch_name": "mLAD",
            "label": [7],
            "branch_label": "2,1,1",
            "parent_branch": "pLAD",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "mLADExt.csv",
            "3D_csv": "mLAD3D.csv",
            "original_branch": "mLAD_OriB_",
            "cross_section_image_NN": "mLADCTANN.nii.gz",
            "cross_section_mask_NN": "mLADValNN.nii.gz",
            "cross_section_mask_fix": "mLADValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "mLADValNNFE.nii.gz",
            "original_volume_mask_fix": "mLADValNNFEOV.nii.gz",
            "cross_section_image_LI": "mLADCTALI.nii.gz",
            "cross_section_mask_LI": "mLADValLI.nii.gz"
        },
        {
            "branch_name": "D1",
            "label": [9],
            "branch_label": "2,1,2",
            "parent_branch": "pLAD",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "D1.csv",
            "3D_csv": "D13D.csv",
            "original_branch": "D1_OriB_",
            "cross_section_image_NN": "D1CTANN.nii.gz",
            "cross_section_mask_NN": "D1ValNN.nii.gz",
            "cross_section_mask_fix": "D1ValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "D1ValNNFE.nii.gz",
            "original_volume_mask_fix": "D1ValNNFEOV.nii.gz",
            "cross_section_image_LI": "D1CTALI.nii.gz",
            "cross_section_mask_LI": "D1ValLI.nii.gz"
        },
        {
            "branch_name": "dLAD",
            "label": [8],
            "branch_label": "2,1,1,1",
            "parent_branch": "mLAD",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "dLADExt.csv",
            "3D_csv": "dLAD3D.csv",
            "original_branch": "dLAD_OriB_",
            "cross_section_image_NN": "dLADCTANN.nii.gz",
            "cross_section_mask_NN": "dLADValNN.nii.gz",
            "cross_section_mask_fix": "dLADValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "dLADValNNFE.nii.gz",
            "original_volume_mask_fix": "dLADValNNFEOV.nii.gz",
            "cross_section_image_LI": "dLADCTALI.nii.gz",
            "cross_section_mask_LI": "dLADValLI.nii.gz"
        },
        {
            "branch_name": "D2",
            "label": [10],
            "branch_label": "2,1,1,2",
            "parent_branch": "mLAD",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "D2.csv",
            "3D_csv": "D23D.csv",
            "original_branch": "D2_OriB_",
            "cross_section_image_NN": "D2CTANN.nii.gz",
            "cross_section_mask_NN": "D2ValNN.nii.gz",
            "cross_section_mask_fix": "D2ValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "D2ValNNFE.nii.gz",
            "original_volume_mask_fix": "D2ValNNFEOV.nii.gz",
            "cross_section_image_LI": "D2CTALI.nii.gz",
            "cross_section_mask_LI": "D2ValLI.nii.gz"
        },
        {
            "branch_name": "pCx",
            "label": [11],
            "branch_label": "2,2",
            "parent_branch": "LM",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "pCxExt.csv",
            "3D_csv": "pCx3D.csv",
            "original_branch": "pCx_OriB_",
            "cross_section_image_NN": "pCxCTANN.nii.gz",
            "cross_section_mask_NN": "pCxValNN.nii.gz",
            "cross_section_mask_fix": "pCxValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "pCxValNNFE.nii.gz",
            "original_volume_mask_fix": "pCxValNNFEOV.nii.gz",
            "cross_section_image_LI": "pCxCTALI.nii.gz",
            "cross_section_mask_LI": "pCxValLI.nii.gz"
        },
        {
            "branch_name": "LCx",
            "label": [13],
            "branch_label": "2,2,1",
            "parent_branch": "pCx",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "LCxExt.csv",
            "3D_csv": "LCx3D.csv",
            "original_branch": "LCx_OriB_",
            "cross_section_image_NN": "LCxCTANN.nii.gz",
            "cross_section_mask_NN": "LCxValNN.nii.gz",
            "cross_section_mask_fix": "LCxValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "LCxValNNFE.nii.gz",
            "original_volume_mask_fix": "LCxValNNFEOV.nii.gz",
            "cross_section_image_LI": "LCxCTALI.nii.gz",
            "cross_section_mask_LI": "LCxValLI.nii.gz"
        },
        {
            "branch_name": "OM1",
            "label": [12],
            "branch_label": "2,2,2",
            "parent_branch": "pCx",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "OM1.csv",
            "3D_csv": "OM13D.csv",
            "original_branch": "OM1_OriB_",
            "cross_section_image_NN": "OM1CTANN.nii.gz",
            "cross_section_mask_NN": "OM1ValNN.nii.gz",
            "cross_section_mask_fix": "OM1ValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "OM1ValNNFE.nii.gz",
            "original_volume_mask_fix": "OM1ValNNFEOV.nii.gz",
            "cross_section_image_LI": "OM1CTALI.nii.gz",
            "cross_section_mask_LI": "OM1ValLI.nii.gz"
        },
        {
            "branch_name": "L-PDA",
            "label": [15],
            "branch_label": "2,2,1,1",
            "parent_branch": "LCx",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "dLCXExt.csv",
            "3D_csv": "dLCX3D.csv",
            "original_branch": "dLCX_OriB_",
            "cross_section_image_NN": "dLCXCTANN.nii.gz",
            "cross_section_mask_NN": "dLCXValNN.nii.gz",
            "cross_section_mask_fix": "dLCXValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "dLCXValNNFE.nii.gz",
            "original_volume_mask_fix": "dLCXValNNFEOV.nii.gz",
            "cross_section_image_LI": "dLCXCTALI.nii.gz",
            "cross_section_mask_LI": "dLCXValLI.nii.gz"
        },
        {
            "branch_name": "OM2",
            "label": [14],
            "branch_label": "2,2,1,2",
            "parent_branch": "LCx",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "OM2.csv",
            "3D_csv": "OM23D.csv",
            "original_branch": "OM2_OriB_",
            "cross_section_image_NN": "OM2CTANN.nii.gz",
            "cross_section_mask_NN": "OM2ValNN.nii.gz",
            "cross_section_mask_fix": "OM2ValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "OM2ValNNFE.nii.gz",
            "original_volume_mask_fix": "OM2ValNNFEOV.nii.gz",
            "cross_section_image_LI": "OM2CTALI.nii.gz",
            "cross_section_mask_LI": "OM2ValLI.nii.gz"
        },

        # RCA
        {
            "branch_name": "pRCA",
            "label": [1],
            "branch_label": "1",
            "parent_branch": 'N',
            "exist": False,
            "use": False,
            "parent_exist": None,
            "original_csv": "pRCAExt.csv",
            "3D_csv": "pRCA3D.csv",
            "original_branch": "pRCA_OriB_",
            "cross_section_image_NN": "pRCACTANN.nii.gz",
            "cross_section_mask_NN": "pRCAValNN.nii.gz",
            "cross_section_mask_fix": "pRCAValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "pRCAValNNFE.nii.gz",
            "original_volume_mask_fix": "pRCAValNNFEOV.nii.gz",
            "cross_section_image_LI": "pRCACTALI.nii.gz",
            "cross_section_mask_LI": "pRCAValLI.nii.gz"
        },
        {
            "branch_name": "mRCA",
            "label": [2],
            "branch_label": "1,1",
            "parent_branch": "pRCA",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "mRCAExt.csv",
            "3D_csv": "mRCA3D.csv",
            "original_branch": "mRCA_OriB_",
            "cross_section_image_NN": "mRCACTANN.nii.gz",
            "cross_section_mask_NN": "mRCAValNN.nii.gz",
            "cross_section_mask_fix": "mRCAValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "mRCAValNNFE.nii.gz",
            "original_volume_mask_fix": "mRCAValNNFEOV.nii.gz",
            "cross_section_image_LI": "mRCACTALI.nii.gz",
            "cross_section_mask_LI": "mRCAValLI.nii.gz"
        },
        {
            "branch_name": "dRCA",
            "label": [3],
            "branch_label": "1,1,1",
            "parent_branch": "mRCA",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "dRCAExt.csv",
            "3D_csv": "dRCA3D.csv",
            "original_branch": "dRCA_OriB_",
            "cross_section_image_NN": "dRCACTANN.nii.gz",
            "cross_section_mask_NN": "dRCAValNN.nii.gz",
            "cross_section_mask_fix": "dRCAValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "dRCAValNNFE.nii.gz",
            "original_volume_mask_fix": "dRCAValNNFEOV.nii.gz",
            "cross_section_image_LI": "dRCACTALI.nii.gz",
            "cross_section_mask_LI": "dRCAValLI.nii.gz"
        },
        {
            "branch_name": "V",
            "label": [16],
            "branch_label": "1,2",
            "parent_branch": "pRCA",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "V.csv",
            "3D_csv": "V3D.csv",
            "original_branch": "V_OriB_",
            "cross_section_image_NN": "VCTANN.nii.gz",
            "cross_section_mask_NN": "VValNN.nii.gz",
            "cross_section_mask_fix": "VValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "VValNNFE.nii.gz",
            "original_volume_mask_fix": "VValNNFEOV.nii.gz",
            "cross_section_image_LI": "VCTALI.nii.gz",
            "cross_section_mask_LI": "VValLI.nii.gz"
        },
        {
            "branch_name": "AM",
            "label": [17],
            "branch_label": "1,3",
            "parent_branch": "pRCA",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "AM.csv",
            "3D_csv": "AM3D.csv",
            "original_branch": "AM_OriB_",
            "cross_section_image_NN": "AMCTANN.nii.gz",
            "cross_section_mask_NN": "AMValNN.nii.gz",
            "cross_section_mask_fix": "AMValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "AMValNNFE.nii.gz",
            "original_volume_mask_fix": "AMValNNFEOV.nii.gz",
            "cross_section_image_LI": "AMCTALI.nii.gz",
            "cross_section_mask_LI": "AMValLI.nii.gz"
        },
        {
            "branch_name": "CB",
            "label": [19],
            "branch_label": "1,4",
            "parent_branch": "pRCA",
            "exist": False,
            "use": False,
            "parent_exist": False,
            "original_csv": "CB.csv",
            "3D_csv": "CB3D.csv",
            "original_branch": "CB_OriB_",
            "cross_section_image_NN": "CBCTANN.nii.gz",
            "cross_section_mask_NN": "CBValNN.nii.gz",
            "cross_section_mask_fix": "CBValNNFixVal.nii.gz",
            "cross_section_mask_fix_extension": "CBValNNFE.nii.gz",
            "original_volume_mask_fix": "CBValNNFEOV.nii.gz",
            "cross_section_image_LI": "CBCTALI.nii.gz",
            "cross_section_mask_LI": "CBValLI.nii.gz"
        },
    ]

    # list of output dictionary list
    outputLst = []
    if branchLst is not None:
        for branchDict in coronaryArtery:
            # check in the list
            if branchDict["branch_name"] in branchLst:
                outputLst.append(branchDict)
            else:
                pass
    else:
        outputLst = coronaryArtery



    with open(jsonOut, 'w') as fp:
        json.dump(outputLst, fp)

    fp.close()
    print('dic created')


def ValidateUse(dicPath=None, jsonList=None, outputPath=None, ignoreCoordsLst=[],
                checkParent=True, checkSecondary=True):

    # load dictionary
    with open(dicPath, 'r') as f:
        coronaryDictionaries = json.load(f)
    f.close()

    # create list of interest branch
    barnchName = []
    barnchLbl = []
    for dict in coronaryDictionaries:
        barnchName.append(dict["branch_name"])
        barnchLbl.append(dict["branch_label"])

    print("List of segments in {}: \n".format(dicPath) + str(barnchName))

    # all json to input
    jsonInFiles = jsonList

    # check all segment existence
    for jsonInFile in jsonInFiles:
        # load
        with open(jsonInFile, 'r') as f:
            dictLst = json.load(f)
        f.close()

        # check segment existence
        for dict in dictLst:
            if dict["branch_name"] in barnchName:
                # get index
                index = barnchName.index(dict["branch_name"])
                # exist
                if (not dict["coordinates"]) and (dict["branch_name"] not in ignoreCoordsLst):  # empty coordinate list and not in ignore coordinate list
                    coronaryDictionaries[index]["exist"] = False
                else:
                    coronaryDictionaries[index]["exist"] = True
                    # use if it is initial branch
                    if len(coronaryDictionaries[index]["branch_label"]) == 1:
                        coronaryDictionaries[index]["use"] = True
            else:
                continue

    # check parent branch
    for dict in coronaryDictionaries:
        if checkParent:
            if dict["exist"] and (len(dict["branch_label"]) > 1):
                # get index
                index = barnchName.index(dict["parent_branch"])
                # parent exists
                dict["parent_exist"] = coronaryDictionaries[index]["exist"] == True
                # use is secondary branch
                if len(dict["branch_label"]) == 3 and dict["parent_exist"]:
                    dict["use"] = True
        else:
            dict["use"] = True # default to output


    # check use of segment after secondary branch
    for dict in coronaryDictionaries:
        if checkSecondary:
            i = 2
            if dict["parent_exist"] and (len(dict["branch_label"]) > 3):
                # jump loop
                while len(dict["branch_label"]) - i > 1:
                    dict["use"] = True

                    # check parent's parent
                    index = barnchLbl.index(dict["branch_label"][:len(dict["branch_label"]) - i])

                    if not coronaryDictionaries[index]["parent_exist"]:
                        dict["use"] = False
                        break

                    i += 2
        else:
            dict["use"] = True

    # output
    with open(outputPath, 'w') as fp:
        json.dump(coronaryDictionaries, fp)
    fp.close()
