import re
import numpy as np
import time
import math
import ast
from scipy.spatial import KDTree
import meshio

def readnas(InputnasPath):
    strT = time.time()
    if InputnasPath.endswith('.inp'):
        mesh = meshio.read(InputnasPath)
        InputnasPath = re.sub('.inp','.nas',InputnasPath)
        print('InputnasPath',InputnasPath)
        meshio.write(InputnasPath, mesh)
    nas_Fil = open(InputnasPath, 'r')
    nas_FilContxt = nas_Fil.read()
    nas_Fil.close()

    # nodelist = re.findall('GRID\*\s+(\d+)\s+([-\+\s\d\\.]{16})([-\+\s\d\\.]{16})\n\*\s+([-\+\s\d\\.]{16})\s*\n',nas_FilContxt)
    nodelist = re.findall('GRID\*\s+(\d+)\s+([-\+\sEe\d\\.]{16})([-\+\sEe\d\\.]{16})\n\*\s+([-\+\sEe\d\\.]{16})\s*\n',nas_FilContxt)
    CTRIA3elemlist = re.findall('CTRIA3\s+(\d+)\s+\d*\s+(\d+)\s+(\d+)\s+(\d+)\s*\n', nas_FilContxt)
    CQUAD4elemlist = re.findall('CQUAD4\s+(\d+)\s+\d*\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\n', nas_FilContxt)
    CTETRAelemlist = re.findall('CTETRA\s+(\d+)\s+\d*\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\n', nas_FilContxt)
    CPENTAelemlist = re.findall('CPENTA\s+(\d+)\s+\d*\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\n', nas_FilContxt)

    nodestradde1 = re.sub('(\d)\-', '\\1e-', str(nodelist))
    nodestradde2 = re.sub('(\d)\+', '\\1e+', nodestradde1)
    nodestradde3 = re.sub('(\.)\+', '\\1e+', nodestradde2)
    nodestradde4 = re.sub('(\.)\-', '\\1e-', nodestradde3)
    nodelistcheck = ast.literal_eval(nodestradde4)
    Nodearray = np.around(np.array(nodelistcheck, float), decimals=8)
    NodeDict={}
    for i in Nodearray:
        NodeDict[i[0]] = i[1:4]
    CTETRAelemarray = np.array(CTETRAelemlist, int)
    CPENTAelemarray = np.array(CPENTAelemlist, int)
    CTRIA3Elemarray = np.array(CTRIA3elemlist, int)
    CQUAD4lemarray = np.array(CQUAD4elemlist, int)
    if CTRIA3Elemarray.any() and CQUAD4lemarray.any():
        Elemarray = np.c_[CTRIA3Elemarray, np.zeros(len(CTRIA3Elemarray)) - np.ones(len(CTRIA3Elemarray))]
        Elemarray = np.r_[Elemarray, CQUAD4lemarray]
    elif not CTRIA3Elemarray.any() and CQUAD4lemarray.any():
        Elemarray = CQUAD4lemarray
    elif CTRIA3Elemarray.any() and not CQUAD4lemarray.any():
        Elemarray = np.c_[CTRIA3Elemarray, np.zeros(len(CTRIA3Elemarray)) - np.ones(len(CTRIA3Elemarray))]
    else:
        Elemarray = np.zeros(1)
    stpT = time.time()
    print('readnas', 'Time', stpT - strT)

    return Nodearray,NodeDict,CTETRAelemarray,CPENTAelemarray,Elemarray

def border(elemarray):
    faceelemsort = np.sort(elemarray, axis=1)
    fake, faceidtrue, faceid = np.unique(faceelemsort, axis=0, return_inverse=True, return_index=True)
    uniqueid, index = np.unique(faceid, return_index=True)
    inid = np.delete(faceid, index)
    outid = np.setdiff1d(uniqueid, inid)
    outelem = elemarray[faceidtrue[outid]]

    return outelem

def findface(CTETRAelemarray,CPENTAelemarray=None):
    strT = time.time()
    faceelem1 = CTETRAelemarray[:, (1, 4, 3)]
    faceelem2 = CTETRAelemarray[:, (1, 2, 4)]
    faceelem3 = CTETRAelemarray[:, (1, 3, 2)]
    faceelem4 = CTETRAelemarray[:, (2, 3, 4)]
    faceelem = np.r_[faceelem1, faceelem2, faceelem3, faceelem4]
    if CPENTAelemarray.any():
        faceelemCPENTA1 = CPENTAelemarray[:, (1, 2, 3)]
        faceelemCPENTA2 = CPENTAelemarray[:, (4, 5, 6)]
        faceelem = np.r_[faceelem, faceelemCPENTA1, faceelemCPENTA2]

    outelem = border(faceelem)
    outelem = np.c_[outelem, np.zeros(len(outelem)) - np.ones(len(outelem))]

    if CPENTAelemarray.any():
        faceelemquad1 = CPENTAelemarray[:, (1, 3, 6, 4)]
        faceelemquad2 = CPENTAelemarray[:, (3, 2, 5, 6)]
        faceelemquad3 = CPENTAelemarray[:, (1, 2, 5, 4)]
        faceelemquad = np.r_[faceelemquad1, faceelemquad2, faceelemquad3]

        outelemquad = border(faceelemquad)
        outelem = np.r_[outelem, outelemquad]

        solidelemcunt = len(CTETRAelemarray) + len(CPENTAelemarray)
    else:
        solidelemcunt = len(CTETRAelemarray)

    outelemid = np.arange(solidelemcunt + 1, solidelemcunt + len(outelem) + 1)
    Elemarray = np.c_[outelemid, outelem]
    stpT = time.time()
    print('findface', 'Time', stpT - strT)

    return Elemarray

def faceelemnormal(Elemarray,NodeDict):
    strT = time.time()
    NormalDict={}
    Quadnormaldict={}
    Quadnodedict={}
    for i in Elemarray:
        v1 = NodeDict[i[-4]] - NodeDict[i[-3]]
        v2 = NodeDict[i[-3]] - NodeDict[i[-2]]
        NormalDict[i[0]] = np.cross(v1, v2)
        if not i[-1] == -1:
            v3 = NodeDict[i[-1]] - NodeDict[i[-4]]
            v4 = NodeDict[i[-1]] - NodeDict[i[-2]]
            Quadnormaldict[i[0]] = np.cross(v3, v4)
            Quadnodedict[i[0]] = i[[-2, -1, -4]]
    stpT = time.time()
    print('elemnormal', 'Time', stpT - strT)

    return NormalDict,Quadnormaldict,Quadnodedict

def splitfaceelem(Elemarray,NormalDict,toleranceface=45):
    strT = time.time()
    tolerancefaceradians = math.radians(float(toleranceface))#角度转弧度
    costolerance = abs(math.cos(tolerancefaceradians))#计算余弦值
    elemarrayzero = Elemarray#初始化表面网格单元集E
    tmpComp_elemDict = {}#导出面存储位置
    Compskew = {}
    i = 0
    while elemarrayzero.size > 0:
        i = i + 1
        tmpComp_elemDict[i] = None #初始化共面网格单元集M
        tmpComp_elemDict[i] = elemarrayzero[0].reshape((1, -1))  # branch element to compent
        elemarrayzero = np.delete(elemarrayzero, 0, axis=0)
        Compskew[i] = 1
        list1 = [0]  # element lines
        for j in list1:
            branchelem = tmpComp_elemDict[i][j, :]#选取种子网格单元e
            normalbranchelem = NormalDict[Elemarray[np.where((Elemarray == branchelem).all(axis=1))[0][0]][0]]#选取种子网格法向量
            l_normalbranchelem = np.linalg.norm(normalbranchelem)  # 向量的模
            nearelemline = np.where(
                (elemarrayzero[:, 1:5] == branchelem[1]) | (elemarrayzero[:, 1:5] == branchelem[2]) | (
                        elemarrayzero[:, 1:5] == branchelem[3]))[0]#寻找邻近网格
            if not branchelem[4] == -1:
                nearelemline4 = np.where(elemarrayzero[:, 1:5] == branchelem[4])[0]
                nearelemline = np.r_[nearelemline, nearelemline4]
            if nearelemline.size > 0:
                nearelemline = np.unique(nearelemline)  # 去重，排序
                nearelem = None  # 初始化临时网格单元集合MT
                nearelem = elemarrayzero[nearelemline]#将邻近网格放入临时网格单元集合MT中
                if nearelem.ndim == 1:
                    nearelem = nearelem.reshape((1, -1))
                for n in range(0, nearelem.shape[0]):#从临时网格单元集合MT中选取网格单元
                    cont = nearelem.shape[0] - 1 - n  # 反向遍历,防止删错行
                    normalnearelem = NormalDict[Elemarray[np.where((Elemarray == nearelem[cont]).all(axis=1))[0][0]][0]]#选取法向量
                    l_normalnearelem = np.linalg.norm(normalnearelem)
                    dian = normalbranchelem.dot(normalnearelem)
                    cos_ = dian / (l_normalbranchelem * l_normalnearelem)#计算夹角余弦
                    if abs(cos_) > costolerance:
                        elemarrayzero = np.delete(elemarrayzero, nearelemline[cont], axis=0)
                        tmpComp_elemDict[i] = np.r_[tmpComp_elemDict[i], [nearelem[cont]]]
                        list1.append(len(list1))
                        if abs(cos_) < Compskew[i]:
                            Compskew[i] = abs(cos_)
    # self.Comp_elemDict=tmpComp_elemDict
    compskewsort = sorted(Compskew.items(), key=lambda d: d[1], reverse=True)
    cunt = 0
    compskewsortnew = []
    for i in range(len(compskewsort)):
        if compskewsort[i][1] == 1:
            cunt = cunt + 1
        else:
            compskewsortnew.append((i + 1 - cunt,) + compskewsort[i])
    if cunt > 0:
        for i in range(cunt):
            compskewsortnew.append((len(compskewsortnew) + 1,) + compskewsort[i])
    Comp_elemDict={}
    for i in compskewsortnew:
        Comp_elemDict[i[0]] = tmpComp_elemDict[i[1]]
    stpT = time.time()
    print('splitfaceelem', 'Time', stpT - strT)

    return Comp_elemDict

def compinitialize(Comp_elemDict):
    strT = time.time()
    CompIfo=[]
    for key in Comp_elemDict:
        CompIfo.append([str(key), str(key), str(key), 'True', 'PSHELL', 'Fluid_outlet', 'True'])
    CompIfo.append([str(len(CompIfo) + 1), '1', 'Fluid3D', 'False', 'PSOLID', '3DMesh', 'False'])
    stpT = time.time()
    print(CompIfo)
    print('getcomp', 'Time', stpT - strT)

    return CompIfo

def splitnode(Comp_elemDict):
    strT = time.time()
    Comp_nodeDict={}
    for key in Comp_elemDict:
        Comp_nodeDict[key] = np.unique(Comp_elemDict[key][:, 1:5])
        if Comp_nodeDict[key][0]==-1:
            Comp_nodeDict[key]=Comp_nodeDict[key][1:]
    stpT = time.time()
    print('splitnode','Time', stpT - strT)

    return Comp_nodeDict

def savestl(OutputPath,Comp_elemDict,NormalDict,Quadnormaldict,Quadnodedict,NodeDict):
    strT = time.time()
    for key in Comp_elemDict:
        f = open(OutputPath + '\\' + str(key) + '.stl', 'w')
        f.write("solid auto0\n")
        for i in Comp_elemDict[key]:
            normal = np.around(NormalDict[i[0]] / np.linalg.norm(NormalDict[i[0]]), 10)
            f.write('facet normal  {:<13} {:<13} {:<13}\n'.format(normal[0], normal[1], normal[2]))
            f.write('    outer loop\n')
            for j in i[1:4]:
                f.write('       vertex {:<13} {:<13} {:<13}\n'.format(NodeDict[j][0],NodeDict[j][1],NodeDict[j][2]))
            f.write('    endloop\n')
            f.write('endfacet\n')
            if i[0] in Quadnormaldict:
                normal = np.around(Quadnormaldict[i[0]] / np.linalg.norm(Quadnormaldict[i[0]]), 10)
                f.write('facet normal  {:<13} {:<13} {:<13}\n'.format(normal[0], normal[1], normal[2]))
                f.write('    outer loop\n')
                for j in Quadnodedict[i[0]]:
                    f.write('       vertex {:<13} {:<13} {:<13}\n'.format(NodeDict[j][0],NodeDict[j][1],NodeDict[j][2]))
                f.write('    endloop\n')
                f.write('endfacet\n')
        f.write('endsolid\n')
        f.close()
    stpT = time.time()
    print('savestl', 'Time', stpT - strT)

def saveLumen(CompIfo,OutputPath):
    strT = time.time()
    f = open(OutputPath + '\\Lumen.stl', 'w')
    for i in CompIfo:
        if i[5] == 'Fluid_Lumen':
            stl = open(OutputPath + '\\' + i[0] +'.stl', 'r')
            data = stl.read()
            stl.close()
            f.write(data)
    f.close()
    stpT = time.time()
    print('saveLumen', 'Time', stpT - strT)

def savecompIfo(CompIfo,OutputPath):
    strT = time.time()
    f = open(OutputPath + '\\CompIfo.csv', 'w')
    f.write('ID,CompName,Localsystem,Property,Type,Lumen\n')
    CompIfosave = []
    for i in CompIfo:
        info = i[1:7]
        if info not in CompIfosave:
            CompIfosave.append(info)
    for i in CompIfosave:
        f.write('{},{},{},{},{},{}\n'.format(i[0], i[1], i[2], i[3], i[4], i[5]))
    f.close()
    stpT = time.time()
    print('savecompIfo', 'Time', stpT - strT)

def centerpoint(Comp_nodeDict,NodeDict):
    strT = time.time()
    CenterpointDict={}
    for key in Comp_nodeDict:
        CenterpointDict[key] = np.zeros((1, 3))
        for i in Comp_nodeDict[key]:
            CenterpointDict[key] = CenterpointDict[key] + NodeDict[i]
        CenterpointDict[key] = CenterpointDict[key] / len(Comp_nodeDict[key])
    stpT = time.time()
    print('centerpoint', 'Time', stpT - strT)

    return CenterpointDict

def localsystem(Comp_nodeDict,CompIfo,NormalDict,Comp_elemDict,Nodearray,CenterpointDict,NodeDict):
    strT = time.time()
    SysDict={}
    for key in Comp_nodeDict:
        if CompIfo[key - 1][3] == 'True':
            normal = NormalDict[Comp_elemDict[key][0][0]]
            # normal = np.zeros(3)
            # for i in Comp_elemDict[key]:
            #     dian1 = NormalDict[i[0]].dot(normal.reshape(3, 1))
            #     if dian1 < 0:
            #         normal=normal-NormalDict[i[0]]
            #     else:
            #         normal=normal+NormalDict[i[0]]

            indices = Comp_nodeDict[key] - np.ones((Comp_nodeDict[key]).shape, int)
            indices = indices.astype(int)
            nodearray = np.delete(Nodearray, indices, axis=0)
            tree = KDTree(nodearray[:, 1:4])
            point = NodeDict[nodearray[int(tree.query(CenterpointDict[key])[1][0])][0]]
            vector = point - CenterpointDict[key]
            l_v = np.linalg.norm(vector)
            l_n = np.linalg.norm(normal)
            dian = vector.dot(normal.reshape(3, 1))
            cos_ = dian / (l_v * l_n)
            changeNormalTypeList = ['Fluid_inlet']
            if (CompIfo[key - 1][5] in changeNormalTypeList) != (cos_ > 0):
                normal = -normal
                print('change', CompIfo[key - 1][2], 'Normal')
            normal=normal/l_n

            cid = int(CompIfo[key - 1][1])
            point1 = CenterpointDict[key]
            point2 = point1 + normal
            point3 = [NodeDict[Comp_elemDict[key][0][1]]] + normal
            # if (point2==point3).all!=0:
            #     point3=[NodeDict[Comp_elemDict[key][1][1]]] + normal
            sysIfo = np.c_[point1, point2, point3]
            syssave = []
            for j in range(0, 9):
                if sysIfo[0, j] <= -1:
                    sys = format(sysIfo[0, j], '.6g')
                elif sysIfo[0, j] <= -0.1:
                    sys = format(sysIfo[0, j], '.7g')
                    sys = sys.replace('0.', '.')
                elif sysIfo[0, j] < 0:
                    sys = format(sysIfo[0, j], '0.2e')
                    sys = sys.replace('e', '')
                elif sysIfo[0, j] >= 1:
                    sys = format(sysIfo[0, j], '.7g')
                elif sysIfo[0, j] >= 0.1:
                    sys = format(sysIfo[0, j], '.8g')
                    sys = sys.replace('0.', '.')
                elif sysIfo[0, j] > 0:
                    sys = format(sysIfo[0, j], '0.3e')
                    sys = sys.replace('e', '')
                else:
                    sys = 0.0
                syssave.append(sys)
            SysDict[
                key] = '$HMNAME SYSTCOL         {0:>8}"{1}"\nCORD2C  {2:>8}        {3:>8}{4:>8}{5:>8}{6:>8}{7:>8}{8:>8}+       \n+       {9:>8}{10:>8}{11:>8}\n'.format(
                cid, CompIfo[key - 1][2], cid, syssave[0], syssave[1], syssave[2], syssave[3], syssave[4],
                syssave[5], syssave[6], syssave[7], syssave[8])
    stpT = time.time()
    print('system', 'Time', stpT - strT)

    return SysDict

def elemArea(NormalDict,Quadnormaldict):
    strT = time.time()
    ElemAreaDict={}
    for key in NormalDict:
        if key in Quadnormaldict:
            ElemAreaDict[key] = np.linalg.norm(NormalDict[key]) * 0.5 + np.linalg.norm(Quadnormaldict[key]) * 0.5
        else:
            ElemAreaDict[key] = np.linalg.norm(NormalDict[key]) * 0.5
    stpT = time.time()
    print('elemArea', 'Time', stpT - strT)

    return ElemAreaDict

def compArea(CompIfo,Comp_elemDict,ElemAreaDict):
    strT = time.time()
    getAreaTypeList = ['Fluid_outlet']
    CompAreaDict={}
    for i in range(len(CompIfo)):
        if CompIfo[i][3] == 'True':
            if CompIfo[i][5] in getAreaTypeList:
                CompAreaDict[i + 1] = 0
                for j in Comp_elemDict[i + 1]:
                    CompAreaDict[i + 1] = CompAreaDict[i + 1] + ElemAreaDict[j[0]]
            else:
                CompAreaDict[i + 1] = 1
    stpT = time.time()
    print('compArea', 'Time', stpT - strT)

    return CompAreaDict

def saveareaCSV(OutputPath,csvname,CompIfo,CompAreaDict):
    strT = time.time()
    f = open(OutputPath + '\\' + csvname + '.csv', 'w')
    f.write('name,propID/set,area\n')
    tmplist = []
    for key in CompAreaDict:
        if CompIfo[key-1][2] not in tmplist:
            tmplist.append(CompIfo[key-1][2])
            f.write('{},{},{}\n'.format(CompIfo[key-1][2], CompIfo[key-1][1], CompAreaDict[key]))
    f.close()
    stpT = time.time()
    print('saveareaCSV', 'Time', stpT - strT)

def savenas(OutputPath,nasname,SysDict,NodeDict,Comp_nodeDict,CompIfo,CTETRAelemarray,CPENTAelemarray,Comp_elemDict):
    strT = time.time()
    f = open(OutputPath + '\\' + nasname + '.nas', 'w')
    f.write('BEGIN BULK\n')
    for key in SysDict:
        f.write(SysDict[key] + '\n')
    nodestrdict = {}
    for key in NodeDict:
        nodestr = []
        for i in range(3):
            nodestr.append(str(NodeDict[key][i]))
        nodestrdict[key] = nodestr
    for key in Comp_nodeDict:
        if CompIfo[key - 1][3] == 'True':
            for i in Comp_nodeDict[key]:
                nodestrdict[i].append(str(CompIfo[key - 1][1]))
    for key in nodestrdict:
        f.write('GRID*   {:<32}{:>16}{:>16}\n'.format(int(key), nodestrdict[key][0], nodestrdict[key][1]))
        if len(nodestrdict[key]) == 3:
            f.write('{:<8}{:>16}\n'.format('*', nodestrdict[key][2]))
        else:
            f.write('{:<8}{:>16}{:>16}\n'.format('*', nodestrdict[key][2], nodestrdict[key][3]))
    save3Dmesh(OutputPath, nodestrdict, CTETRAelemarray, CPENTAelemarray)
    elemid = 0
    for i in CTETRAelemarray:
        elemid = elemid + 1
        elemidout=elemid
        # elemidout=i[0]
        f.write('CTETRA  {:>8}{:>8}{:>8}{:>8}{:>8}{:>8}\n'.format(elemidout, CompIfo[-1][1], i[1], i[2], i[3],i[4]))
    for i in CPENTAelemarray:
        elemid = elemid + 1
        elemidout = elemid
        # elemidout=i[0]
        f.write('CPENTA  {:>8}{:>8}{:>8}{:>8}{:>8}{:>8}{:>8}{:>8}\n'.format(elemidout, CompIfo[-1][1], i[1],
                                                                            i[2], i[3], i[4], i[5], i[6]))
    for key in Comp_elemDict:
        for i in Comp_elemDict[key]:
            if i[4] == -1:
                elemid = elemid + 1
                elemidout = elemid
                # elemidout=i[0]
                f.write('CTRIA3  {:>8}{:>8}{:>8}{:>8}{:>8}\n'.format(elemidout, CompIfo[key - 1][1], int(i[1]),
                                                                     int(i[2]), int(i[3])))
            else:
                elemid = elemid + 1
                elemidout = elemid
                # elemidout=i[0]
                f.write(
                    'CQUAD4  {:>8}{:>8}{:>8}{:>8}{:>8}{:>8}\n'.format(elemidout, CompIfo[key - 1][1], int(i[1]),
                                                                      int(i[2]), int(i[3]), int(i[4])))
    list2 = []
    for i in CompIfo:
        list1 = []
        for j in (1, 2, 4):
            list1.append(i[j])
        tuple1 = tuple(list1)
        list2.append(tuple1)
    comp = []
    for i in set(list2):
        comp.append(list(i))
    f.write('$$    HyperMesh name and color information for generic components               $\n')
    for i in range(len(comp)):
        if comp[i][2] == 'PSHELL':
            f.write('$HMNAME COMP{0:>12}{1:>8}"{2}"{1:>8} "{2}" 4\n'.format('', comp[i][0], comp[i][1]))
        elif comp[i][2] == 'PSOLID':
            f.write('$HMNAME COMP{0:>12}{1:>8}"{2}"{1:>8} "{2}" 5\n'.format('', comp[i][0], comp[i][1]))
        else:
            print('prop wrong: PSHELL or PSOLID')
    f.write('$$    Property Definition for Surface and Volume Elements                       $\n')
    for i in range(len(comp)):
        if comp[i][2] == 'PSHELL':
            f.write(
                '$HMNAME PROP{0:>12}{1:>8}"{2}"4\nPSHELL  {1:>8}{3:>8}{3:>16}{3:>16}\n'.format('', comp[i][0],
                                                                                               comp[i][1], 1))
        elif comp[i][2] == 'PSOLID':
            f.write(
                '$HMNAME PROP{0:>12}{1:>8}"{2}"5\nPSOLID  {1:>8}{3:>8}\n'.format('', comp[i][0], comp[i][1], 1))
        else:
            print('prop wrong: PSHELL or PSOLID')
    f.write('$HMNAME MAT{:>21}"Fake" "MAT1"\nMAT1           11000.0  1000.0  0.3\n'.format(1))
    f.write('ENDDATA')
    f.close()
    stpT = time.time()
    print('savenas', 'Time', stpT - strT)

def save3Dmesh(OutputPath, nodestrdict, CTETRAelemarray, CPENTAelemarray):
    f = open(OutputPath + '\\' + '3Dmesh.nas', 'w')
    f.write('BEGIN BULK\n')
    for key in nodestrdict:
        f.write('GRID*   {:<32}{:>16}{:>16}\n'.format(int(key), nodestrdict[key][0], nodestrdict[key][1]))
        f.write('{:<8}{:>16}\n'.format('*', nodestrdict[key][2]))
    elemid = 0
    for i in CTETRAelemarray:
        elemid = elemid + 1
        elemidout=elemid
        # elemidout=i[0]
        f.write('CTETRA  {:>8}{:>8}{:>8}{:>8}{:>8}{:>8}\n'.format(elemidout,'',i[1],i[2],i[3],i[4]))
    for i in CPENTAelemarray:
        elemid = elemid + 1
        elemidout = elemid
        # elemidout=i[0]
        f.write('CPENTA  {:>8}{:>8}{:>8}{:>8}{:>8}{:>8}{:>8}{:>8}\n'.format(elemidout,'',i[1],i[2],i[3],i[4],i[5],i[6]))
    f.write('ENDDATA')
    f.close()