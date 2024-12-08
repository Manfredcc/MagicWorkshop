import sys
import shutil
import json
from datetime import datetime
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QStackedWidget, QDialog, QLineEdit, QFileDialog, QMessageBox, QListWidget, QListWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, QRect, Qt, QSize, QProcess
from PyQt5.QtGui import QFont, QIcon, QPixmap
import FragOps
import threading
import time
import pyperclip

# todo 添加ruler筛选搜索结果

# 持续检测搜索框内容，搜索结果
class searchCheckWork(QThread):
    indexChange = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        oldText = ''
        while not self.parent.threadStopEvent.is_set():
            text = self.parent.searchBox.text()
            if text == oldText:
                time.sleep(0.3)
            elif text == '':
                oldText = text
                self.parent.page.widget(3).clear()
                self.indexChange.emit(0)
            else:
                oldText = text
                # fixme! 筛选模式和作者名
                rowValuesList = self.parent.ops.search(text)
                self.indexChange.emit(3)
                self.parent.page.widget(3).clear()
                for rowValue in rowValuesList:
                    if rowValue[0] != None: # key exists
                        item = QListWidgetItem(str(rowValue[0]) + ' : ' + str(rowValue[1]))
                    else:
                        item = QListWidgetItem(str(rowValue[1]))
                    item.setData(Qt.UserRole, rowValue)
                    self.parent.page.widget(3).addItem(item)

# 创建记忆碎片的交互界面，等待用户输入信息（关键词、内容、标签）
# todo: 可选标签，或新建自定义标签
# todo: 用户可以回车直接确认，可以不经过按钮点击
class NewFragMemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle('新建记忆碎片')

        self.layout = QVBoxLayout(self)
        self.keyBox = QLineEdit(self)
        self.keyBox.setPlaceholderText('关键词（可选）')
        self.contentBox = QLineEdit(self)
        self.contentBox.setPlaceholderText('内容（默认拷贝剪切板）')

        self.buttonBox = QHBoxLayout()
        self.okButton = QPushButton('确认')
        self.okButton.clicked.connect(self.__ok_button_click)
        self.cancelButton = QPushButton('取消')
        self.cancelButton.clicked.connect(self.__cancel_button_click)
        self.buttonBox.addWidget(self.okButton)
        self.buttonBox.addWidget(self.cancelButton)

        self.layout.addWidget(self.keyBox)
        self.layout.addWidget(self.contentBox)
        self.layout.addLayout(self.buttonBox)
        self.setFixedSize(800, 400)
    
    def __ok_button_click(self):
        key = self.keyBox.text()
        content = self.contentBox.text()
        tagList = ['医护门口机']
        fragMem = FragOps.FragMem(key, content, tagList)
        self.parent.ops.newFrag(fragMem)
        self.close()
    
    def __cancel_button_click(self):
        self.close()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initData()

    def initUI(self):
        self.loadConf() # Keep this first
        self.initLayout()
        # self.bind()

    def loadConf(self):
        self.curPath = os.path.dirname(os.path.abspath(__file__))
        self.confFile = self.curPath + r'\conf\defCOnf.json'
        with open(self.confFile, 'r', encoding='utf-8') as file:
            self.confData = json.load(file)

    def layoutConfigure(self, obj, layout, index=-1):
        # 检查并设置位置大小
        if set({'x', 'y', 'w', 'h'}).issubset(layout.keys()):
            if -1 == index:
                obj.setGeometry(QRect(layout['x'], layout['y'], layout['w'], layout['h']))
            elif 'xOffset' in layout:
                obj.setGeometry(QRect(layout['x'] + index * layout['xOffset'], layout['y'], layout['w'], layout['h']))
            elif 'yOffset' in layout:
                obj.setGeometry(QRect(layout['x'], layout['y'] + index * layout['yOffset'], layout['w'], layout['h']))
            else:
                print('invalid parameter')
                
        # 检查并设置字体
        if set({'font', 'fontsize'}).issubset(layout.keys()):
            qfont = QFont(layout['font'], layout['fontsize'])
            if 'bold' in layout and layout['bold'] == True:
                qfont.setBold(True)
            obj.setFont(qfont)
        # 检查并设置基本样式
        if 'style' in layout:
            obj.setStyleSheet(layout['style'])

    def initLayout(self):
        # 主界面
        jdata = self.confData['main']
        self.setWindowTitle(jdata['title'])
        self.layoutConfigure(self, jdata['layout'])
        # 欢迎词
        self.welcomeLabel = QLabel(self.getWelcome(), self)
        self.layoutConfigure(self.welcomeLabel, self.confData['welcome']['layout'])
        # 搜索框
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText(self.confData['search']['title'])
        self.layoutConfigure(self.searchBox, self.confData['search']['layout'])
        # 页面
        self.pageButtonList = [] # 保存所有的标签按钮实例
        self.pageNameList = list(self.confData['pageButton']['name'].values())
        # 基本标签页面
        self.page = QStackedWidget(self)
        self.layoutConfigure(self.page, self.confData['page']['layout'])
        self.createScroll()
        # 页面按钮
        i = 0
        for t in self.pageNameList: # 为每个页面创建一个按钮
            button = QPushButton(t, self)
            self.layoutConfigure(button, self.confData['pageButton']['layout'], i)
            button.clicked.connect(self.pageButtonClick)
            self.pageButtonList.append(button)
            i += 1
        self.pageButtonList[0].setStyleSheet(self.confData['pageButton']['layout']['selectedStyle']) # 默认选中第一个页面，更改按钮样式
        self.lastPageButtonIndex = 0
        # 基本操作图标
        self.opsButtonList = []
        i = 0
        for path in list(self.confData['opsButton']['path'].values()):
            button = QPushButton(self)
            button.setIcon(QIcon(self.curPath + path))
            button.setIconSize(QSize(self.confData['opsButton']['iconSize'], self.confData['opsButton']['iconSize']))
            self.layoutConfigure(button, self.confData['opsButton']['layout'], i)
            self.opsButtonList.append(button)
            i += 1
        # bind new click
        self.opsButtonList[0].clicked.connect(self.__newClick)
        self.opsButtonList[1].clicked.connect(self.__setClick)
        self.opsButtonList[2].clicked.connect(self.__importClick)
        # 详情列表
        self.detail = QLabel(self)
        self.layoutConfigure(self.detail, self.confData['detail']['layout'])

    def getWelcome(self):
        self.user = self.confData['user']['name']
        hour = datetime.now().hour
        if 0 <= hour < 5:       return self.confData['welcome']['greeting']['midnight'] + ', ' + self.user
        elif 5 <= hour < 11:    return self.confData['welcome']['greeting']['morning'] + ', ' + self.user
        elif 1 <= hour < 13:    return self.confData['welcome']['greeting']['noon'] + ', ' + self.user
        elif 13 <= hour < 18:   return self.confData['welcome']['greeting']['afternoon'] + ', ' + self.user
        elif 18 <= hour < 22:   return self.confData['welcome']['greeting']['evening'] + ', ' + self.user
        else:                   return self.confData['welcome']['greeting']['night']

    def pageButtonClick(self): # 根据按下的不同按钮，切换到指定页面
        clickedButton = self.sender()
        index = self.pageNameList.index(clickedButton.text())
        self.pushPageButton(index)
        
    def pushPageButton(self, index):
        if self.lastPageButtonIndex == index:
            return
        else:
            self.lastPageButtonIndex = index
            self.page.setCurrentIndex(index)

        for b in self.pageButtonList: # 清空按钮颜色
            b.setStyleSheet(self.confData['pageButton']['layout']['style'])
        # 将点击的按钮下划线标记
        self.pageButtonList[index].setStyleSheet(self.confData['pageButton']['layout']['selectedStyle'])
    
    def showDetail(self, author, time, tagList):
        pass

    def scrollItemClick(self, item):
        data = item.data(Qt.UserRole)
        time = data[4] if len(data) > 4 else "Unknown Time"
        author = data[3] if len(data) > 3 else "Unknown Author"
        tagList = data[2] if len(data) > 2 else []
        detail = f"Time : {time}  |  Author : {author}  |  Tags : {str(tagList)}"
        self.detail.setText(detail)
        pyperclip.copy(item.text())

    def createScroll(self):
        for t in self.pageNameList:
            listWidget = QListWidget()
            listWidget.itemClicked.connect(self.scrollItemClick)
            self.layoutConfigure(listWidget, self.confData['scroll']['layout'])
            self.page.addWidget(listWidget)

    # 绑定UI和操作
    def bind(self):
        pass

    def initData(self):
        self.memPath = self.curPath + self.confData['memory']['path']
        self.memFile = self.memPath + self.confData['memory']['name']
        self.ops = FragOps.FragOps(self.memFile, self.user)
        self.threadStopEvent = threading.Event()
        self.searchCheckThread = searchCheckWork(self)
        self.searchCheckThread.indexChange.connect(self.pushPageButton)
        self.searchCheckThread.start()

    def __newClick(self):
        dialog = NewFragMemDialog(self)
        dialog.exec_()

    # todo 将浏览UI改为设置，配置各个参数
    # todo 检查配置状态，动态更新部分设置，不能更新的就提醒用户重启应用才能生效，可以选择是否现在重启
    # todo 切换记忆
    def __setClick(self):
        self.process = QProcess(self)
        self.process.start(self.confData['user']['edit'], [self.confFile])
    
    # todo 导入逻辑：复制一个excel文件，并选择操作：
    # 1.更换记忆
    # 2.将记忆并入（颗粒度可以精确到天、月、年）
    def __importClick(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls);;All Files (*)", options=options)
 
        if file_name:
            if file_name.lower().endswith(('.xlsx', '.xls')):
                try:
                    shutil.copy(file_name, os.path.join(self.memPath, os.path.basename(file_name)))
                    QMessageBox.information(self, 'Success', f'File {file_name} copied to {self.memPath}')
                except Exception as e:
                    QMessageBox.warning(self, 'Error', f'Failed to copy file: {e}')
            else:
                QMessageBox.warning(self, 'Invalid File', 'Please select a valid Excel file (.xlsx or .xls).')

    def closeEvent(self, event):
        self.threadStopEvent.set()
        print("Exit FragmentMemory Program...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = App()
    main.show()
    sys.exit(app.exec_())