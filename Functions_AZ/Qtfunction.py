from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
import numpy as np
import pdfunction

############################  Table Widget  ####################################
def chooselineinfo(ui):
    InputcsvPath = ui.toPlainText()
    table=pdfunction.readexcel(InputcsvPath)
    items = table.CompName
    item, ok = QInputDialog.getItem(QMainWindow(), "select input comp name", 'comp name', items, 0, False)
    if ok and item:
        line = table[(table.CompName == item)].index.tolist()
        lineinfo = table.loc[line[0]]
        print(lineinfo)
        return lineinfo
    else:
        return np.zeros(1)

def writetable(table,listinput):
    for i in range(table.rowCount()):
        for j in range(table.columnCount()):
            item = QTableWidgetItem('{0}'.format(listinput[i][j]))
            if j == 0:
                item.setFlags(Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignHCenter)
            table.setItem(i, j, item)

def updatetableitem(ui, string):
    item = QTableWidgetItem(string)
    item.setTextAlignment(Qt.AlignHCenter)
    currentrow = ui.currentRow()
    currentColumn = ui.currentColumn()
    ui.setItem(currentrow, currentColumn, item)

def updatetableline(ui, cunt, string, lineinfo):
    if lineinfo.any() == 0:
        pass
    else:
        for i in range(ui.rowCount()):
            try:
                tabletext =ui.item(i, cunt).text()
            except:
                tabletext = ''
            if tabletext == string:
                lineinmagelist = ['ReorderID', 'CompName', 'Localsystem', 'Property', 'Type', 'Lumen']
                lineundefinelist = ['154', 'unknown', 'True', 'PSHELL', 'Fluid_outlet', 'False']
                for j in range(1, ui.columnCount()):
                    try:
                        item = QTableWidgetItem('{0}'.format(lineinfo[lineinmagelist[j - 1]]))
                    except:
                        item = QTableWidgetItem('{0}'.format(lineundefinelist[j - 1]))
                        print('table {},{} notdefine'.format(i, j))
                    item.setTextAlignment(Qt.AlignHCenter)
                    ui.setItem(i, j, item)

def readtable(table):
    tableIfo=[]
    for i in range(table.rowCount()):
        tableIfo.append([])
        for j in range(table.columnCount()):
            tableIfo[i].append(table.item(i, j).text())
    print(tableIfo)

    return tableIfo
