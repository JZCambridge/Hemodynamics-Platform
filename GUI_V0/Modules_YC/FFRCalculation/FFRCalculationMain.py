# -*- coding: UTF-8 -*-
'''
@Project ：getpyfilepath.py 
@File    ：FFRCalculationMain.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2022/3/12 13:37 
'''
import numpy
import os
import vtk
import re
# dataRangeIQRAve = 123
# numpy.save("E:/dataRangeIQRAve.npy", dataRangeIQRAve)
data_read = numpy.load(r"E:\Test\666028\34percent\FFR\postNpy\ndTimeAvePressureCoo_2dndarr.npy")
# data_read = numpy.load(r"E:\Test\666028\34percent\FFR\postNpy\ndCooOSI_2dndarr.npy")
print("data_read", data_read)
# print(os.path.split("E:/gh345/ga/tst.nii.gz"))

vtufilepath = r"E:\Test\boudarylayerdelete\CFD_file_46.vtu"
class FFRExtractin:
    def __init__(self):
        # self.vtufilepath =  r"E:\Test\CFD_file_13.vtu"
        self.vtufilepath =  r"E:\Test\CFD_file_13ori.vtu"
        self.vtuDict = {}
        self.tetralElementExtraction()

    def tetralElementExtraction(self):
        if self.vtufilepath:
            # ************ Reading .vtu file  ***************
            # os.chdir(Split_AbsFilePath(self.coo_FilNam)[0])
            vtu_Fil = open(self.vtufilepath, "r")
            vtu_FilContxt = vtu_Fil.read()
            # ************** find all tetral elements matrix *******************
            tmp_vtu_matrixInfo = re.split(".*</DataArray>\n", vtu_FilContxt)
            tmp_vtu_matrixInfo = tmp_vtu_matrixInfo[0:-1]
            vtu_matrixInfo = [re.split("(.*<DataArray type.+\n)",w) for w in tmp_vtu_matrixInfo]
            for w in vtu_matrixInfo:
                matrixType = re.findall('type=\"(.+)\".+Name',w[1])[0]
                tmpDimension = re.findall('NumberOfComponents=\"(.+)\".+format',w[1])
                vtuDict_key = re.findall('Name=\"(\w+)\".+format',w[1])[0]
                if  tmpDimension:
                    matrixDimension_column = int(tmpDimension[0])
                else:
                    matrixDimension_column = 1
                tmparray = w[2].split()
                if matrixType == "Float32":
                    self.vtuDict[vtuDict_key] = numpy.asarray(tmparray,dtype= float).reshape(-1,matrixDimension_column )
                elif matrixType == "Int64":
                    self.vtuDict[vtuDict_key] = numpy.asarray(tmparray,dtype=int).reshape(-1,matrixDimension_column)
            # self.vtuDict
            print(self.vtuDict)
            matrixDimension_column = re.findall("Number of compnents:\"\d+\"", vtu_matrixInfo)

                # ************************** split
                # TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac by ',
                # ' *********************************
                # Nd_coordInfoSplit = [w.split(",") for w in
                #                      Nd_coordInfoNoFirstSpac]
                #
                # Nd_CoordMat = np.array(Nd_coordInfoSplit)
        #     # ************************************ replace multiple space by ',
        #     # ' ***********************************************
        #     Nd_coordInfoNoSpac = [re.sub(' +', ',', w) for w in Nd_coordInfo]
        #     # ************************************ replace “-” by ',
        #     # -' ***********************************************
        #     Nd_coordInfoNoNegative = [re.sub('-', ',-', w) for w in Nd_coordInfoNoSpac]
        #     Nd_coordInfoNoNegativeE = [re.sub('E,', 'E', w) for w in
        #                                Nd_coordInfoNoNegative]
        #     # print("No Negative", Nd_coordInfoNoNegative)
        #     # **************************************** delete the first space
        #     # **************************************************
        #     Nd_coordInfoNoFirstSpac = [w[1:] for w in Nd_coordInfoNoNegativeE]
        #     # ************************** split
        #     # TetraElmnt_NdIfo_Dltn_Nospac_NoFirstSpac by ',
        #     # ' *********************************
        #     Nd_coordInfoSplit = [w.split(",") for w in Nd_coordInfoNoFirstSpac]
        #
        #     Nd_CoordMat = numpy.array(Nd_coordInfoSplit)
        #     # print("Nd_CoordMat",Nd_CoordMat)
        #     Nd_CoordMat_coord = Nd_CoordMat[:, 1:].astype(numpy.float)
        #     Nd_CoordMat_node = Nd_CoordMat[:, 0].astype(numpy.int)
        #     # print("Node", Nd_CoordMat_node)
        #     # print("Coord", Nd_CoordMat_coord)
        #     # numpy.savetxt('Node_id.mat',Nd_CoordMat_node)
        #     # numpy.savetxt('Node_x_y_z.mat', Nd_CoordMat_coord)
        #     NdcoorMat = {}
        #     NdcoorMat["Node_id"] = Nd_CoordMat_node
        #     NdcoorMat["Node_coo"] = Nd_CoordMat_coord
        #     # print("NdcoorMat",NdcoorMat)
        #     numpy.save(Split_AbsFilePath(self.coo_FilNam)[
        #                 0] + '/' + '%s_Nodecoo_Dic' % self.AnalysisType, NdcoorMat)
        #     coo_Fil.close()
        # else:
        #     print("you do not choose coo file")
#
# class FFR_Calculation:
#     def __init__(self,UI):


# FFRExtractin()
