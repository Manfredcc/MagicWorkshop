import sys
import time
import json
from datetime import datetime
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QStackedWidget, QDialog, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal, QRect, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
import FragOps

class NewFragMemWork(QThread):
    signal = pyqtSignal()

    def __init__(self, ops, key, content, tagList):
        super().__init__()
        self.key = key
        self.content = content
        self.tagList = tagList
        self.ops = ops

    def run(self):
        self.FragMem = FragOps.FragMem(self.key, self.content, self.tagList)
        self.ops.newFrag(self.FragMem)
        self.signal.emit()


# 创建记忆碎片的交互界面，等待用户输入信息（关键词、内容、标签）
# todo: 可选标签，或新建自定义标签
# todo: 用户可以回车直接确认，可以不经过按钮点击
class NewFragMemDialog(QDialog):
    def __init__(self, parent=None):
        super(NewFragMemDialog, self).__init__(parent)
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


class Tag(QWidget):
    def __init__(self, tag, parent=None):
        super(Tag, self).__init__(parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        self.label = QLabel(f'{tag} hello world')
        self.label.setFont(QFont("Microsoft YaHei", 10))
        self.label3 = QLabel(f'{tag} I am constanc while world changes')
        self.label3.setFont(QFont("Microsoft YaHei", 10))
        self.label4 = QLabel(f'{tag} I love u, pidundun')
        self.label4.setFont(QFont("Microsoft YaHei", 10))
        self.label5 = QLabel(f'{tag} I miss u, a pi')
        self.label5.setFont(QFont("Microsoft YaHei", 10))
        self.label6 = QLabel(f'{tag} no matter where you are')
        self.label6.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self.label)
        layout.addWidget(self.label3)
        layout.addWidget(self.label4)
        layout.addWidget(self.label5)
        layout.addWidget(self.label6)

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
        self.confFile = r'\conf\defCOnf.json'
        with open(self.curPath + self.confFile, 'r', encoding='utf-8') as file:
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
        # 基本标签页面
        self.page = QStackedWidget(self)
        self.layoutConfigure(self.page, self.confData['page']['layout'])
        # 标签按钮
        self.tagButtonList = [] # 保存所有的标签按钮实例
        self.tagNameList = list(self.confData['tagButton']['name'].values())
        i = 0
        for t in self.tagNameList: # 为每个按钮创建页面内容，并添加到page中统一管理
            self.page.addWidget(Tag(t, self))
            button = QPushButton(t, self)
            self.layoutConfigure(button, self.confData['tagButton']['layout'], i)
            button.clicked.connect(self.tagButtonCallback)
            self.tagButtonList.append(button)
            i += 1
        self.tagButtonList[0].setStyleSheet(self.confData['tagButton']['layout']['selectedStyle']) # 默认选中第一个页面，更改按钮样式
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

    def getWelcome(self):
        hour = datetime.now().hour
        if 0 <= hour < 5:       return self.confData['welcome']['greeting']['midnight']
        elif 5 <= hour < 11:    return self.confData['welcome']['greeting']['morning']
        elif 1 <= hour < 13:    return self.confData['welcome']['greeting']['noon']
        elif 13 <= hour < 18:   return self.confData['welcome']['greeting']['afternoon']
        elif 18 <= hour < 22:   return self.confData['welcome']['greeting']['evening']
        else:                   return self.confData['welcome']['greeting']['night']

    def tagButtonCallback(self): # 根据按下的不同按钮，切换到指定页面
        clickedButton = self.sender()
        index = self.tagNameList.index(clickedButton.text())
        self.page.setCurrentIndex(index)
        for b in self.tagButtonList: # 颜色标记选中的页面对应的按钮
            if b == clickedButton:
                b.setStyleSheet(self.confData['tagButton']['layout']['selectedStyle'])
            else:
                b.setStyleSheet(self.confData['tagButton']['layout']['style'])

    # 绑定UI和操作
    def bind(self):
        pass

    def initData(self):
        self.ops = FragOps.FragOps('mem.xlsx', 'Manfred')

    def __newClick(self):
        dialog = NewFragMemDialog(self)
        dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = App()
    main.show()
    sys.exit(app.exec_())