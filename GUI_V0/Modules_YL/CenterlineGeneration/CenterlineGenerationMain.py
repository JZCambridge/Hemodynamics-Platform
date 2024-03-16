import sys
import os

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
import Save_Load_File
import Pd_Funs

# 　input of this class is filepath of Tenoke_ccta_dl_segment_label.exe and location of where CTA.nii.gz
# output of this class is to extract centerline file based on cta file
# now this program support up to 2 threads, otherwise, there will be too much load on cpu
import threading
import time
from PySide2.QtUiTools import QUiLoader

class CenterlineEx:
    def __init__(self, UI=None, Hedys=None, exePath='', folderPath=None, TablePath=None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.chooseExeBtn_CG_1.clicked.connect(lambda: self.ChooseExeFile())
        # used for tab 2 choose exe file
        self.ui.ChooseExeBtn_CG_3.clicked.connect(lambda: self.ChooseExeFile(flag=1))
        self.ui.chooseSaveBtn_CG_1.clicked.connect(lambda: self.ChooseCTADir())
        self.ui.ChooseExcelPathBtn_CG_3.clicked.connect(lambda: self.ChooseTablePath())
        self.ui.GenerateBtn_CG_1.clicked.connect(lambda: self.iterate())
        self.ui.BatchProcessBtn_CG_3.clicked.connect(lambda: self.BatchViaExcel())

        self.InitCenterlineEx(exePath=exePath, folderPath=folderPath, TablePath=TablePath)

    def InitCenterlineEx(self, exePath='', folderPath=None, TablePath=None):
        self.destination = folderPath
        self.root_address = ''
        self.part1_address = exePath
        self.part105_address = ''
        self.part2_address = ''
        self.part3_address = ''
        self.part4_address = ''
        self.pathCollection = []
        self.count = 0
        self.thread1Collection = []
        self.thread2Collection = []
        self.DataFrame = None
        self.ManualFlag = False
        self.CSVPath = TablePath

    # to choose the path of part1 exe file
    def ChooseExeFile(self, flag=0):
        ExePath = Save_Load_File.OpenFilePathQt(
            dispMsg="Load Exe Path",
            fileTypes='All files (*.*);; exe files(*.exe)',
            fileObj=self.ui,
            qtObj=True
        )
        if flag == 0:
            self.ui.LoadExePathTxt_CG_1.setPlainText(ExePath)
        else:
            self.ui.LoadExePathTxt_CG_3.setPlainText(ExePath)

    def ChooseTablePath(self):
        TablePath = Save_Load_File.OpenFilePathQt(
            dispMsg='Choose Excel File Path',
            fileTypes='All files (*.*);; excel files(*.csv *.xlsx)',
            fileObj=self.ui,
            qtObj=True
        )

        self.ui.TablePathTxt_CG_3.setPlainText(TablePath)

    # used to choose the directory path
    def ChooseCTADir(self):
        DirName = Save_Load_File.OpenDirPathQt(
            dispMsg="Save directory",
            fileObj=self.ui,
            qtObj=True
        )

        self.ui.LoadCTAPathTxt_CG_1.setPlainText(DirName)

    # use the file path of part1 exe file to set the path of other exe files
    def rearrange(self):
        print(self.part1_address)

        if r'/' in self.part1_address:
            self.root_address = '/'.join(self.part1_address.split('/')[:-2])
        else:
            self.root_address = '/'.join(self.part1_address.split('\\')[:-2])
        self.root_address += '/'
        # print('root', self.root_address)

        self.part105_address = self.root_address + r'Tenoke_ccta_Part2Alt\Tenoke_ccta_Part2Alt.exe'
        self.part2_address = self.root_address + r'Tenoke_ccta_Part2AltB\Tenoke_ccta_Part2AltB.exe'
        self.part3_address = self.root_address + r'Tenoke_ccta_Part3\Tenoke_ccta_Part3.exe'
        self.part4_address = self.root_address + r'Tenoke_ccta_Part4\Tenoke_ccta_Part4.exe'
    # iterate the chosen directory to get the absolute path of CTA file
    def iterate(self):
        # 　use \\ to replace / in the path
        for (root, dirs, files) in os.walk(self.ui.LoadCTAPathTxt_CG_1.toPlainText().replace(r'/', '\\')):
            if 'CTA.nii.gz' in files:
                self.pathCollection.append(root)
            else:
                pass

        self.part1_address = self.ui.LoadExePathTxt_CG_1.toPlainText()
        self.rearrange()

        # to check if the multi-thread method is chosen
        if not self.ui.MultiThreadCBox_CG_1.isChecked():
            for path in self.pathCollection:
                self.destination = path
                # self.DetectManual()
                self.run()

        # if multi-thread method is chosen, rearrange the
        else:
            # split the list of path contain cta file into two lists
            split_list = self.split_list_average_n(self.pathCollection, 2)
            self.thread1Collection = next(split_list)
            self.thread2Collection = next(split_list)

            print('thread1', self.thread1Collection)
            print('thread2', self.thread2Collection)

            thread1 = myThread(threadID=1, name='thread-1', folderPath=self.thread1Collection,
                               exePath=self.part1_address)
            thread2 = myThread(threadID=2, name='thread-2', folderPath=self.thread2Collection,
                               exePath=self.part1_address)
            thread1.start()
            thread2.start()

        # clear the path in storage
        self.initialize()

    # divide list into n equal lists
    def split_list_average_n(self, origin_list, n):
        if len(origin_list) % n == 0:
            cnt = len(origin_list) // n
        else:
            cnt = len(origin_list) // n + 1

        for i in range(0, n):
            yield origin_list[i * cnt:(i + 1) * cnt]

    # read the chosen excel file and convert it to dataframe
    def ReadExcelInfo(self):
        if self.CSVPath:
            self.DataFrame = Pd_Funs.OpenDF(self.CSVPath, header=0)
        else:
            # breakpoint()
            self.DataFrame = Pd_Funs.OpenDF(self.ui.TablePathTxt_CG_3.toPlainText(), header=0)
        # print(self.DataFrame['FolderPath'])

    # used to detect if manual tracing file exists
    def DetectManual(self):
        manualFile = 'Combo_Vals_Man.nii.gz'
        maunalPath = os.path.join(self.destination, manualFile)
        if os.path.exists(maunalPath):
            self.ManualFlag = True
        else:
            self.ManualFlag = False

    def BatchViaExcel(self):
        if not self.part1_address:
            self.part1_address = self.ui.LoadExePathTxt_CG_3.toPlainText()
        self.ReadExcelInfo()

        for i in range(len(self.DataFrame)):
            self.destination = self.DataFrame['FolderPath'][i]
            self.DetectManual()
            self.run()

    # this method used to empty all the storage
    def initialize(self):
        self.thread1Collection = []
        self.thread2Collection = []
        self.pathCollection = []

    # generate the windows command to generate the center line
    def run(self):
        self.DetectManual()  # detect if manual tracing file exists
        self.rearrange()  # rearrange command info
        step1 = self.part1_address + ' ' + self.destination
        step105 = self.part105_address + ' ' + self.destination
        step2 = self.part2_address + ' ' + self.destination
        step3 = self.part3_address + ' ' + self.destination
        step4 = self.part4_address + ' ' + self.destination + ' 45'

        # print(step1)
        # print('\n')
        #
        # if self.ManualFlag:
        #     print(step105)
        #     print('\n')
        # else:
        #     pass

        # print(step2)
        # print('\n')
        # print(step3)
        # print('\n')
        # print(step4)
        print(step1)
        os.system(step1)
        print('step 1 done')

        # print('Manual file {}'.format(self.ManualFlag))

        if self.ManualFlag:
            os.system(step105)
            print('manual tracing done')
        else:
            pass

        print(step2)
        os.system(step2)
        print('step 2 done')
        print(step3)
        os.system(step3)
        print('step 3 done')
        print(step4)
        os.system(step4)
        print('all steps done')
        # time.sleep(5)


# create multi thread to allow process multiple cases at the same time, usually two threads are maximum
class myThread(threading.Thread):
    def __init__(self, threadID=0, name='', folderPath='', exePath='', jumpFlag=False):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.folderPath = folderPath
        self.exePath = exePath
        self.jumpFlag = jumpFlag

    def run(self):
        count = 0
        print('starting' + self.name)
        for i in range(len(self.folderPath)):
            a = CenterlineEx(exePath=self.exePath, folderPath=self.folderPath[i], jumpFlag=self.jumpFlag)
            a.run()
            print(str(self.threadID) + self.folderPath[i])
            # time.sleep(15)
        print('Exiting' + self.name)
