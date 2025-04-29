# -*- coding: UTF-8 -*-
'''
@Project ：MainGUI.py 
@File    ：getpyfilepath.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/5/17 22:32 
'''

import os
import re
def getFileName2(path, suffix):
    i = 0
    input_template_All = []
    input_template_All_Path = []
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            #print(os.path.join(root, name))
            #i += 1
            #print(i)
            #print(name)
            if (os.path.splitext(name)[1] == suffix) and (name != '__init__.py'):
                input_template_All.append(name)
                input_template_All_Path.append(os.path.join(root, name))
    return input_template_All, input_template_All_Path

def gethiddenimports(fileabspath):
    modulesc = open(fileabspath,'r')
    modulescontext = modulesc.read()
    print(modulescontext)
    hiddenimportsDleFrom = [w.replace('from','') for w in modulescontext]
    hiddenimports = [re.sub('import','.', w) for w in hiddenimportsDleFrom]
    # moduleline = None
    # for line in modulescontext:
    #     print(line)
    #     re.sub(' +from +'),'',line)
    #     re.sub(' +import +','.',line)
    #     hiddenimports.append(line)
    print('hiddenimports = ',hiddenimportsDleFrom)



path = r'E:\pyinstaller_test\GUI26May21'


#input_template_All1 = getFileName1(path, '.py')
input_template_All2, input_template_All_Path2 = getFileName2(path, '.py')
print(input_template_All_Path2 )
os.path.abspath('.')
pyscriptfile = open (r'E:\pyinstaller_test\GUI26May21\pyscripts.txt', 'w')
for listcontext in  input_template_All_Path2:
    listcontext = listcontext.replace('\\', '/')
    pyscriptfile.write('\''+str(listcontext)+'\','+'\n')
pyscriptfile.close()
modulefilePth = r'E:\pyinstaller_test\GUI26May21\modules.txt'



#
# import os
# train_dir = r'E:\pyinstaller_test\GUI'
# datanames = os.listdir(train_dir)
# for dataname in datanames:
#     i=0
#     print(i)
#     if os.path.splitext(dataname)[1] == '.py':
#         print(dataname)