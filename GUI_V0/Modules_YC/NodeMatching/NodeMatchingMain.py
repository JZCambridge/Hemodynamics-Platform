# -*- coding: UTF-8 -*-
'''
@Project ：matching_for_test.py 
@File    ：meihongnodepressure.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/4/20 20:50 
'''
#!/usr/bin/python
#  -*- coding: UTF-8 -*
import pandas as pd
import numpy as np
import tkinter as tk
import os.path
import re
import os
import time
import sys
# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_YC')
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
from scipy.spatial import distance
from FileDisposing import *
from CFD_FEA_Post_Process import *
import pdfunction
import Save_Load_File
# Standard libs
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide2.QtUiTools import QUiLoader
from sklearn.cluster import KMeans
from sklearn.neighbors import KDTree


# define function load_data--to split coordinate data
def load_data(path):
    my_list = []
    with open(path, "r") as f:
        for line in f:
            sta = 0
            flag = 0
            list_line = list(line)
            for i in range(3):   #each line has 3 numbers x, y, z
                index = line.find('-0.', sta)  #Y find the starting point of data
                if index >= 0:
                    index += flag
                    list_line.insert(index, ' ')  #insert space between 3 numbers in each line
                    sta = index + 2
                    flag += 1
                else:
                    break
            line_new = ''.join(list_line)
            line_new = line_new.split()
            line_new = [float(coo) for coo in line_new]
            my_list.append(line_new)
    return pd.DataFrame(my_list)

# delete the head and tail of coo nos
def strip_head_tail(path, name, file_type):
    if file_type == 'nos':
        start, end = 8, -5
        name_in = name + '.nos'
        name_out = name + '_strip.nos'
    elif file_type == 'coo':
        start, end = 9, -4
        name_in = name + '.coo'
        name_out = name + '_strip.coo'
    with open(path + '/' + name_in, 'r') as f:
        lines = f.readlines()
    with open(path + '/' + name_out, 'w') as f:
        f.write(''.join(lines[start:end]))

# load pressure data to a dataframe
def load_pressure(path, name):
    with open(path + '/' + name + '.lst', 'r') as f:
        lines = f.readlines()
    lines_long = ''.join(lines)
    time_list = []
    start = 0
    pressure_f = []
    flag = 1
    node_num = []
    while True:
        time_start = lines_long.find('Time', start)  #find the start position of str'Time 0.00000E+00'
        time_end = lines_long.find('Node', time_start)#find the end position of str'Time 0.00000E+00'
        time_list.append(float(lines_long[time_start: time_end].split()[1])) #split the str'Time 0.00000E+00' and extract time '0.00000E+00'
        list_start = time_end
        start = time_start + 1   #cirlate all times
        list_end = lines_long.find('Time', start)
        temp = lines_long[list_start: list_end].strip().split('\n')
        pressure_temp = []
        if list_end == -1:
            temp = temp[:-1]
        for line in temp:
            if line:
                if flag == 1:
                    node_num.append(int(line.split()[1]))
                pressure_temp.append(float(line.split()[2]))
        flag += 1
        pressure_f.append(pressure_temp)
        if list_end == -1:
            break
    pressure_f = pd.DataFrame(pressure_f).T
    pressure_f['node_num'] = node_num
    print(pressure_f)
    print(time_list)
    return pressure_f, time_list

########################################################################################################################
################################################# In file generation####################################################
class NodeMatching:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
        
        self.ui.pushButton_NM3.clicked.connect(lambda: self.open_file_fluididb())
        self.ui.pushButton_NM5.clicked.connect(lambda: self.open_file_fluidpor())
        self.ui.pushButton_SaveFluidPloFile_NM.clicked.connect(lambda: self.FPloSavePath())
        self.ui.pushButton_SaveSolidPloFile_NM.clicked.connect(lambda: self.SPloSavePath())
        self.ui.pushButton_NM5_2.clicked.connect(lambda: self.export_fluid_data())
        self.ui.pushButton_NM2.clicked.connect(lambda: self.open_file_solididb())
        self.ui.pushButton_NM7.clicked.connect(lambda: self.export_solid_data())
        self.ui.pushButton_NM1.clicked.connect(lambda: self.open_file_ADINA())
        self.ui.pushButton_NM3_2.clicked.connect(lambda: self.submit_fd_to_adina())
        self.ui.pushButton_NM.clicked.connect(lambda: self.submit_sd_to_adina())
        self.ui.pushButton_NM2_2.clicked.connect(lambda: self.strip_data())
        self.ui.Run_NM.clicked.connect(lambda: self.run())
        self.ui.pushButton_BatchTable_NM.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_NM.clicked.connect(lambda: self.batchrun())

        self.InitNodeMatching()

    def InitNodeMatching(self):
        ## 0.1 variables0
        self.fluid_lumen_number = ''
        self.solid_lumen_number = ''
        self.let_number = ''
        self.fluid_in_path = ''
        self.fluid_por_path = ''
        self.solid_in_path = ''
        self.fluid_in_name = ''
        self.fluid_por_name = ''
        self.solid_in_name = ''
        self.adina_path = ''
        self.offset = 0.0
        self.interval_num = 0
        self.NodeSetPrefix = None
        self.PressureID = None
        self.EleFaceSetPrefix = None
        self.TimeFunctionPrefix = None
        self.LoadPrefix = None

    ## 0.2 functions
    def open_file_fluididb(self):
        file_path = QFileDialog.getOpenFileName(self.ui, "Open File")[0]  # desktop
        self.ui.fluidfile_NM2.setPlainText(file_path)

    def load_file_fluididb(self):
        tmpfile_path = self.ui.fluidfile_NM2.toPlainText()
        self.fluid_in_path, self.fluid_in_name = os.path.split(tmpfile_path)
        self.fluid_in_name = os.path.splitext(self.fluid_in_name)[0]

    def open_file_fluidpor(self):
        file_path = QFileDialog.getOpenFileName(self.ui, "Open File")[0]  # desktop
        self.ui.plainTextEdit_NM3.setPlainText(file_path)

    def load_file_fluidpor(self):
        tmpfile_path = self.ui.plainTextEdit_NM3.toPlainText()
        self.fluid_por_path, self.fluid_por_name, self.fluid_por_format = \
                                                        Split_AbsFilePath(tmpfile_path)

    def FPloSavePath(self):
        FploDir = Opening_FileDialog(self.ui)
        self.ui.plainTextEdit_SaveFluidPloFile_NM.setPlainText(FploDir)

    def open_file_solididb(self):
        file_path = QFileDialog.getOpenFileName(self.ui, "Open File")[0] # desktop
        self.ui.plainTextEditNM5.setPlainText(file_path)

    def load_file_solididb(self):
        tmpfile_path = self.ui.plainTextEditNM5.toPlainText()
        self.solid_in_path, self.solid_in_name = os.path.split(tmpfile_path)
        self.solid_in_name = os.path.splitext(self.solid_in_name)[0]

    def SPloSavePath(self):
        SploDir = Opening_FileDialog(self.ui)
        self.ui.plainTextEdit_SaveSolidPloFile_NM.setPlainText(SploDir)

    def export_fluid_data(self):
        self.load_file_fluididb()
        self.load_file_fluidpor()
        FPloSavePath = self.ui.plainTextEdit_SaveFluidPloFile_NM.toPlainText()
        self.fluid_lumen_number = int(float(self.ui.fluidset_NM1.text()))  # get the index of lumen set
        # 1.create lumen_nodeset
        ## 1.1 substract lumen node labels
        ### 1.1.1 fluid
        with open(FPloSavePath + "/" + self.fluid_in_name + ".plo", 'a+') as f_plo:
            # extract nodeset&coordinates from input file
            fluid_database_path =  self.ui.fluidfile_NM2.toPlainText()
            f_plo.writelines("DATABASE OPEN FILE='" + fluid_database_path + "' SAVE=NO\n")
            f_plo.writelines("FILELIST OPTION=FILE  FILE ='" + self.fluid_in_name + ".nos' LINPAG=0 EJECT=NO\
            \nLIST NODESET FIRST=" + str(self.fluid_lumen_number) + " LAST=" + str(self.fluid_lumen_number) + "\n")  # get the index of lumen set
            f_plo.writelines("FILELIST OPTION=FILE  FILE ='" + self.fluid_in_name + ".coo' LINPAG=0 EJECT=NO\
            \nLIST COORDINATES NODE FIRST=FIRST LAST=LAST SYSTEM=0 GLOBAL=YES\n")
            # extract pressure data from por file
            fluid_porthole_path = self.fluid_por_path + "/" + self.fluid_por_name + ".por"
            #fluid_porthole_path = "/" + self.fluid_por_name + ".por"
            f_plo.writelines("DATABASE NEW\n")
            f_plo.writelines("LOADPORTHOLE OPERATIO=CREATE FILE='" + fluid_porthole_path + "'\n")
            f_plo.writelines("ZONE NAME=Sout  NODEATTACH=YES  GEOMATTACH=YES\nWHOLE_MODEL\n")
            f_plo.writelines("RESULTGRID NAME=MyGrid TYPE=PORTHOLE NGRIDR=1  NGRIDS=1  NGRIDT=1\n\
            RESPRANGE LOAD-STEP NAME=SRange TSTART=EARLIEST TEND=LATEST INCREMEN=AVAILABLE INTERPOL=NO NSKIP=0\n\
            SMOOTHING NAME=StruSmooType TYPE=AVERAGED\n")
            f_plo.writelines("FILELIST OPTION=FILE  FILE='" + self.fluid_in_name + ".lst' LINPAG=0 EJECT=NO\n\
        ZONELIST ZONENAME=Sout RESULTGRID=MyGrid SMOOTHING=StruSmooType RESULTCO=DEFAULT RESPOPTI=RESPRANGE,\n\
            RESPONSE=DEFAULT RESPRANG= SRange VARIABLE = NODAL_PRESSURE ")

    def export_solid_data(self):
        self.load_file_solididb()
        self.solid_lumen_number = int(float(self.ui.lumenset_NM.text()))
        SPloSavePath = self.ui.plainTextEdit_SaveSolidPloFile_NM.toPlainText()
        # 1.create lumen_nodeset
        ## 1.1 substract lumen node labels
        ### 1.1.2 solid
        with open(SPloSavePath + "/" + self.solid_in_name + ".plo", 'a+') as f_plo:
            # extract nodeset&coordinates from input file
            solid_database_path = self.ui.plainTextEditNM5.toPlainText()
            f_plo.writelines("DATABASE OPEN FILE='" + solid_database_path + "' SAVE=No\n")
            f_plo.writelines("FILELIST OPTION=FILE  FILE ='" + self.solid_in_name + ".nos' LINPAG=0 EJECT=NO\
            \nLIST NODESET FIRST=" + str(self.solid_lumen_number) + " LAST=" + str(self.solid_lumen_number) + "\n")
            f_plo.writelines("FILELIST OPTION=FILE  FILE ='" + self.solid_in_name + ".coo' LINPAG=0 EJECT=NO\
            \nLIST COORDINATES NODE FIRST=FIRST LAST=LAST SYSTEM=0 GLOBAL=YES\n")

    def open_file_ADINA(self):
        adina_path = QFileDialog.getOpenFileName(self.ui, "Open File")[0]  # desktop\
        self.ui.plainTextEdit_NM1.setPlainText(adina_path)

    def submit_fd_to_adina(self):
        self.load_file_fluididb()
        fluid_in_file = self.ui.fluidfile_NM2.toPlainText()
        FPloSavePath = self.ui.plainTextEdit_SaveFluidPloFile_NM.toPlainText()
        adina_path = self.ui.plainTextEdit_NM1.toPlainText()
        # chcp 437\n
        print('cd /d ' + FPloSavePath + ' && ' + adina_path + ' -b -s -m 8gb ' + FPloSavePath + self.fluid_in_name + '.plo')
        os.system(
            'cd /d ' + FPloSavePath + ' && ' + adina_path + ' -b -s -m 8gb ' + FPloSavePath + self.fluid_in_name + '.plo')

    def submit_sd_to_adina(self):
        solid_in_file = self.ui.plainTextEditNM5.toPlainText()
        SPloSavePath = self.ui.plainTextEdit_SaveSolidPloFile_NM.toPlainText()
        adina_path = self.ui.plainTextEdit_NM1.toPlainText()
        # chcp 437\n
        print('cd /d ' + SPloSavePath + ' && ' + adina_path + ' -b -s -m 8gb ' + SPloSavePath + self.solid_in_name + '.plo')
        os.system(
            'cd /d ' + SPloSavePath + ' && ' + adina_path + ' -b -s -m 8gb ' + SPloSavePath + self.solid_in_name + '.plo')

    def strip_data(self):
        self.load_file_fluididb()
        self.load_file_solididb()
        FPloSavePath = self.ui.plainTextEdit_SaveFluidPloFile_NM.toPlainText()
        SPloSavePath = self.ui.plainTextEdit_SaveSolidPloFile_NM.toPlainText()
        strip_head_tail(FPloSavePath, self.fluid_in_name, 'nos')
        strip_head_tail(SPloSavePath, self.solid_in_name, 'nos')
        strip_head_tail(FPloSavePath, self.fluid_in_name, 'coo')
        strip_head_tail(SPloSavePath, self.solid_in_name, 'coo')

    def run(self):
        self.load_file_fluididb()
        self.load_file_solididb()
        FPloSavePath = self.ui.plainTextEdit_SaveFluidPloFile_NM.toPlainText()
        SPloSavePath = self.ui.plainTextEdit_SaveSolidPloFile_NM.toPlainText()
        self.let_number = self.ui.lineEditNM.text()
        self.offset = float(self.ui.lineEdit_NM2.text())
        self.interval_num = int(float(self.ui.lineEdit_NM3.text()))

        self.NodeSetPrefix = int(float(self.ui.lineEdit_TimeFunctionPrefix_NM.text()))
        self.PressureID = int(float(self.ui.lineEdit_PressureID_NM.text()))
        self.EleFaceSetPrefix = int(float(self.ui.lineEdit_EleFaceSetPrefix_NM.text()))
        self.TimeFunctionPrefix = int(float(self.ui.lineEdit_TimeFunctionPrefix_NM.text()))
        self.LoadPrefix = int(float(self.ui.lineEdit_LoadPrefix_NM.text()))

        with open(SPloSavePath + self.solid_in_name + '.log', "a+") as f:
            f.writelines("Start Time: " + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()) + '\n')
        # 2.find the match
        # 2.1 import fluid/solid lumen_nodeset data
        lumen_nodeset_f = pd.read_csv(FPloSavePath + self.fluid_in_name + '_strip.nos', sep='\s+',
                                      index_col=None, \
                                      names=['node_num', '0', '1'])
        lumen_nodeset_f = lumen_nodeset_f['node_num']
        lumen_nodeset_s = pd.read_csv(SPloSavePath + self.solid_in_name + '_strip.nos', sep='\s+',
                                      index_col=None, \
                                      names=['node_num', '0', '1'])
        lumen_nodeset_s = lumen_nodeset_s['node_num']
        # 2.2 import fluid/solid coordinate data
        coord_f = load_data(FPloSavePath + self.fluid_in_name + '_strip.coo')
        coord_f.columns = ['node_num', 'x', 'y', 'z']
        coord_f = coord_f[coord_f['node_num'].isin(lumen_nodeset_f)]  # filter fluid boundary data
        coord_f.reset_index(drop=True, inplace=True)
        coord_s = load_data(SPloSavePath + self.solid_in_name + '_strip.coo')
        coord_s.columns = ['node_num', 'x', 'y', 'z']
        coord_s = coord_s[coord_s['node_num'].isin(lumen_nodeset_s)]  # filter fluid boundary data
        coord_s.reset_index(drop=True, inplace=True)
        # 3.find the nearest node
        min_num = []
        min_dist = []
        tree = KDTree(coord_s[['x', 'y', 'z']])
        for i in range(len(coord_f)):
            dist, ind = tree.query(coord_f[['x', 'y', 'z']][i:i + 1], k=1)
            #print("coord_s['node_num'][i:i + 1]", coord_s['node_num'][i:i + 1])
            min_num.append(int(coord_s['node_num'][ind[0]]))    ###return nodeid of coord_s
            min_dist.append(dist)
        # print(min_num)
        # print(min_dist)
        # for i in range(len(coord_f)):
        #     neighbor = (coord_f.at[i, 'x'] - self.offset < coord_s['x']) & (coord_s['x'] < coord_f.at[i, 'x'] + self.offset) & \
        #                (coord_f.at[i, 'y'] - self.offset < coord_s['y']) & (coord_s['y'] < coord_f.at[i, 'y'] + self.offset) & \
        #                (coord_f.at[i, 'z'] - self.offset < coord_s['z']) & (coord_s['z'] < coord_f.at[i, 'z'] + self.offset)
        #     temp = coord_s['node_num'][neighbor]  #################################
        #     temp.reset_index(drop=True, inplace=True)
        #     min_index = np.argmin(distance.cdist(coord_f[['x', 'y', 'z']][i: i + 1], coord_s[['x', 'y', 'z']][neighbor]), axis=1)[0]  ###########如果出现连个点都满足条件，取最小的点
        #     min_num.append(int(temp[min_index]))

        # 3.group pressure
        # 3.1 obtain pressure_s&pressure_f
        pressure_f, time_list = load_pressure(FPloSavePath, self.fluid_in_name)
        pressure_f = pressure_f[pressure_f['node_num'].isin(lumen_nodeset_f)]  # filter fluid pressure data
        pressure_f.reset_index(drop=True, inplace=True)  # delete the index first
        pressure_f = pressure_f.drop(labels='node_num', axis=1)
        pressure_s = pd.concat([pd.Series(min_num), pressure_f], axis=1, ignore_index=True)
        pressure_s.rename(columns={0: 'node_num'}, inplace=True)
        pressure_s = pressure_s.groupby('node_num').mean()
        # 3.2 group by magnitudes
        km = KMeans(n_clusters=self.interval_num)
        label = km.fit_predict(pressure_s)
        node_label = pd.concat([pressure_s.reset_index()['node_num'], pd.DataFrame(label)], axis=1, ignore_index=True)
        # 4.write input file
        # 4.1 nodeset
        for i in range(self.interval_num):
            with open(SPloSavePath + '/AddGroup.plo', "a+") as f:
                f.writelines("*\nNODESET NAME=" + str(self.NodeSetPrefix) + str(
                    i) + " ALL-EXT=NO DESCRIPT='NONE' OPTION=NODE GROUP=0 ZONE='',\n")
                f.writelines("     ELSET=0 TARGET=0 ANGLE=0.00000000000000,\n")
                f.writelines("     DISTANCE=0.00000000000000 APPEND=NO\n@CLEAR\n")
            temp = node_label[node_label[1] == i]
            temp.reset_index(drop=True, inplace=True)
            group = pd.concat([temp[0], pd.DataFrame(np.ones([len(temp), 1])). \
                              dot(pd.DataFrame([0, 1]).T).astype(int)], axis=1, ignore_index=True)
            group.to_csv(SPloSavePath + '/AddGroup.plo', mode='a', index=False, header=None, sep=' ')
        # 4.2 pressure
        with open(SPloSavePath + '/AddGroup.plo', "a+") as f:
            f.writelines("*\nLOAD PRESSURE NAME=" + str(
                self.PressureID) +" MAGNITUD=1 BETA=0.00000000000000,\n     LINE=0 SYSTEM=0\n")
            # 4.3 elfaceset
            let_num = self.let_number.split(',')
            defined = []
            for i in range(self.interval_num):
                f.writelines("*\nELFACESET NAME=" + str(self.TimeFunctionPrefix) + str(
                    i) + " ALL-EXT=NO DESCRIPT='NONE' OPTION=NODESET GROUP=0,\n     ZONE='' ANGLE=20.0000000000000 "
                         "TARGET=0 APPEND=NO EXTERNAL=MODEL\n@CLEAR\n")
                f.writelines(str(self.TimeFunctionPrefix) + str(i) + " 0 1\n@\n")
                f.writelines("*\nELFACESET NAME=" + str(self.EleFaceSetPrefix) + str(
                    i) + " ALL-EXT=NO DESCRIPT='NONE' OPTION=SUBTRACT GROUP=0,\n     ZONE='' ANGLE=20.0000000000000 "
                         "TARGET=" + str(self.TimeFunctionPrefix) + str(i) + " APPEND=NO EXTERNAL=MODEL\n@CLEAR\n")
                f.writelines('\n'.join(let_num) + '\n' + '\n'.join(defined) + "\n@\n")
                defined.append(str(self.TimeFunctionPrefix) + str(i))
        # time function
        for i in range(self.interval_num):
            with open(SPloSavePath + '/AddGroup.plo', "a+") as f:
                f.writelines("*\nTIMEFUNCTION NAME=" + str(self.TimeFunctionPrefix) + str(i) + "\n@CLEAR\n")
            time_function = pd.concat([pd.DataFrame(time_list), pd.DataFrame(km.cluster_centers_[i])], axis=1,
                                      ignore_index=True)
            time_function.to_csv(SPloSavePath + '/AddGroup.plo', mode='a', index=False, header=None, sep=' ')
        # apply load
        with open(SPloSavePath + '/AddGroup.plo', "a+") as f:
            f.writelines("*\nAPPLY-LOAD BODY=0\n")
            for i in range(self.interval_num):
                f.writelines(str(self.LoadPrefix) + str(i + 1) + "  'PRESSURE' " + str(
                    self.PressureID) + " 'ELEMENT-FACE' " + str(self.EleFaceSetPrefix) + str(i) + " 0 " + str(
                    self.TimeFunctionPrefix) + str(i) + '\n')
        with open(SPloSavePath + self.solid_in_name + '.log', "a+") as f:
            f.writelines("Complete Time: " + time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()) + '\n')

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_NM.setPlainText('{}'.format(filename))

    def batchrun(self,CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_NM.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')
            NodeMatching = False
            try:
                if info["NodeMatching"]:
                    NodeMatching = info["NodeMatching"]
            except:
                pass
            if NodeMatching:
                InputFolder = ''
                OutputFolder = ''
                NodeMatchingInletAndOutletSet = ''
                NodeMatchingOffesetvalue = ''
                NodeMatchingGroupNum = ''
                NodeMatchingfluidlumenset = ''
                NodeMatchingsolidlumenset = ''
                NodeMatchingPressureID = ''
                NodeMatchingEleFaceSetPrefix = ''
                NodeMatchingTimeFunctionPrefix = ''
                NodeMatchingLoadPrefix = ''
                NodeMatchingAUI = ''
                NodeMatchingIdb = ''
                NodeMatchingPor = ''
                NodeMatchingin = ''
                # change inputFolder and outputFolder
                try:
                    if info['solidin(NodeMatching)']:
                        NodeMatchingin = info['solidin(NodeMatching)']
                except:
                    pass
                try:
                    if info['SolidIdb(NodeMatching)']:
                        InputFolder = info['SolidIdb(NodeMatching)']
                except:
                    pass
                try:
                    if info['SolidCompIfo(NodeMatching)']:
                        SolidCompIfo = pdfunction.readexcel(info['SolidCompIfo(NodeMatching)'])
                        InletorOutletlist = ['Solid_outlet', 'Solid_inlet']
                        solidLumenlist = ['Solid_inlumen']
                        InletorOutletID = []
                        solidLumenID = []
                        for j in range(len(SolidCompIfo)):
                            InletorOutletinfo = SolidCompIfo.iloc[j]
                            if InletorOutletinfo['Type'] in InletorOutletlist:
                                InletorOutletID.append(str(InletorOutletinfo['ID']))
                            if InletorOutletinfo['Type'] in solidLumenlist:
                                solidLumenID.append(str(InletorOutletinfo['ID']))
                        NodeMatchingInletAndOutletSet = ','.join(InletorOutletID)
                        NodeMatchingsolidlumenset = ','.join(solidLumenID)
                except:
                    pass
                try:
                    if info['InletAndOutletSet(NodeMatching)']:
                        NodeMatchingInletAndOutletSet = info['InletAndOutletSet(NodeMatching)']
                except:
                    pass
                try:
                    if info['Offesetvalue(NodeMatching)']:
                        NodeMatchingOffesetvalue = info['Offesetvalue(NodeMatching)']
                except:
                    pass
                try:
                    if info['GroupNum(NodeMatching)']:
                        NodeMatchingGroupNum = info['GroupNum(NodeMatching)']
                except:
                    pass
                try:
                    if info['fluidlumenset(NodeMatching)']:
                        NodeMatchingfluidlumenset = info['fluidlumenset(NodeMatching)']
                except:
                    pass
                try:
                    if info['solidlumenset(NodeMatching)']:
                        NodeMatchingsolidlumenset = info['solidlumenset(NodeMatching)']
                except:
                    pass
                try:
                    if info['PressureID(NodeMatching)']:
                        NodeMatchingPressureID = info['PressureID(NodeMatching)']
                except:
                    pass
                try:
                    if info['EleFaceSetPrefix(NodeMatching)']:
                        NodeMatchingEleFaceSetPrefix = info['EleFaceSetPrefix(NodeMatching)']
                except:
                    pass
                try:
                    if info['TimeFunctionPrefix(NodeMatching)']:
                        NodeMatchingTimeFunctionPrefix = info['TimeFunctionPrefix(NodeMatching)']
                except:
                    pass
                try:
                    if info['LoadPrefix(NodeMatching)']:
                        NodeMatchingLoadPrefix = info['LoadPrefix(NodeMatching)']
                except:
                    pass
                try:
                    if info['AUIPath']:
                        NodeMatchingAUI = info['AUIPath']
                except:
                    pass
                try:
                    if info['fluidIdb(NodeMatching)']:
                        NodeMatchingIdb = info['fluidIdb(NodeMatching)']
                except:
                    pass
                try:
                    if info['fluidPor(NodeMatching)']:
                        NodeMatchingPor = info['fluidPor(NodeMatching)']
                except:
                    pass
                try:
                    if info['OutputFolder']:
                        OutputFolder = info['OutputFolder'] + '/NodeMatching'
                except:
                    pass
                try:
                    if info['OutputFolder(NodeMatching)']:
                        OutputFolder = info['OutputFolder(NodeMatching)']
                except:
                    pass
                print('NodeMatching InputFolder=', InputFolder)
                print('NodeMatching OutputFolder=', OutputFolder)
                # make dir
                if not os.path.exists(OutputFolder):
                    os.mkdir(OutputFolder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                self.ui.plainTextEditNM5.setPlainText('{}'.format(InputFolder))
                self.ui.plainTextEdit_SaveFluidPloFile_NM.setPlainText('{}/'.format(OutputFolder))
                self.ui.plainTextEdit_SaveSolidPloFile_NM.setPlainText('{}/'.format(OutputFolder))
                if NodeMatchingIdb:
                    self.ui.fluidfile_NM2.setPlainText('{}'.format(NodeMatchingIdb))
                if NodeMatchingPor:
                    self.ui.plainTextEdit_NM3.setPlainText('{}'.format(NodeMatchingPor))
                if NodeMatchingAUI:
                    self.ui.plainTextEdit_NM1.setPlainText('{}'.format(NodeMatchingAUI))
                if NodeMatchingfluidlumenset:
                    self.ui.fluidset_NM1.setText('{}'.format(NodeMatchingfluidlumenset))
                if NodeMatchingsolidlumenset:
                    self.ui.lumenset_NM.setText('{}'.format(NodeMatchingsolidlumenset))
                if NodeMatchingInletAndOutletSet:
                    self.ui.lineEditNM.setText('{}'.format(NodeMatchingInletAndOutletSet))
                if NodeMatchingOffesetvalue:
                    self.ui.lineEdit_NM2.setText('{}'.format(NodeMatchingOffesetvalue))
                if NodeMatchingGroupNum:
                    self.ui.lineEdit_NM3.setText('{}'.format(NodeMatchingGroupNum))
                if NodeMatchingPressureID:
                    self.ui.lineEdit_PressureID_NM.setText('{}'.format(NodeMatchingPressureID))
                if NodeMatchingEleFaceSetPrefix:
                    self.ui.lineEdit_EleFaceSetPrefix_NM.setText('{}'.format(NodeMatchingEleFaceSetPrefix))
                if NodeMatchingTimeFunctionPrefix:
                    self.ui.lineEdit_TimeFunctionPrefix_NM.setText('{}'.format(NodeMatchingTimeFunctionPrefix))
                if NodeMatchingLoadPrefix:
                    self.ui.lineEdit_LoadPrefix_NM.setText('{}'.format(NodeMatchingLoadPrefix))
                # Touched function
                self.export_fluid_data()
                self.export_solid_data()
                self.submit_fd_to_adina()
                self.submit_sd_to_adina()
                self.strip_data()
                self.run()
                # stack in
                if NodeMatchingin:
                    infile = open(NodeMatchingin, 'r')
                    intxt = infile.read()
                    infile.close()
                    AddGroup = open(OutputFolder + '/AddGroup.plo', 'r')
                    AddGrouptxt = AddGroup.read()
                    AddGroup.close()
                    f = open(OutputFolder + '/WallWithPressure.in', 'w')
                    f.write(intxt + '/n' + AddGrouptxt)
                    f.close()

if __name__ == "__main__":
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\NodeMatching.ui")
    stats = NodeMatching(UI=ui)
    stats.ui.show()
    app.exec_()
