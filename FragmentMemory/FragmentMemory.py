import sys
import time
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QSpacerItem, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal, QRect, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap

class Tag(QWidget):
    def __init__(self, tag, parent=None):
        super(Tag, self).__init__(parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        self.label = QLabel(f'{tag} hello world')
        self.label.setFont(QFont(self.parent.basicFont, 10))
        self.label3 = QLabel(f'{tag} I am constanc while world changes')
        self.label3.setFont(QFont(self.parent.basicFont, 10))
        self.label4 = QLabel(f'{tag} I love u, pidundun')
        self.label4.setFont(QFont(self.parent.basicFont, 10))
        self.label5 = QLabel(f'{tag} I miss u, a pi')
        self.label5.setFont(QFont(self.parent.basicFont, 10))
        self.label6 = QLabel(f'{tag} no matter where you are')
        self.label6.setFont(QFont(self.parent.basicFont, 10))
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
        pass

    def initUI(self):
        self.mainLayout()
        self.loadColor()
        self.loadWelcome()
        self.loadSearch()
        self.loadTag()
        self.basciOperation()
        self.bind()
    
    def initData(self):
        pass

    # 主界面
    def mainLayout(self):
        # 主界面基础设置
        self.basicFont = 'Microsoft YaHei'
        self.setGeometry(300, 300, 1200, 650)
        # self.setWindowTitle('Fragment Memory')
        self.setWindowTitle('记忆碎片')

    # 加载颜色主题
    def loadColor(self): # todo
        pass

    def loadWelcome(self):
        self.welcomeLabel = QLabel('夜深了，晚上好', self) # fix me! According the time

        # self.welcomeLabel = QLabel(self.welcome)
        self.welcome = ''
        self.welcomeLabel.setGeometry(QRect(105, 20, 400, 35)) # 使用绝对位置，保持左上角
        welcomeFont = QFont(self.basicFont, 14)
        welcomeFont.setBold(True)
        self.welcomeLabel.setFont(welcomeFont)

    # 加载搜索
    def loadSearch(self):
        self.searchBox = QLineEdit(self)

        self.searchBox.setPlaceholderText('输入搜索内容')
        self.searchBox.setFont(QFont(self.basicFont, 15))
        self.searchBox.setStyleSheet("QLineEdit:placeholder { color: gray; }")
        self.searchBox.setStyleSheet("QLineEdit { border: 2px solid gray; }")
        self.searchBox.setGeometry(QRect(80, 90, 650, 75))

    # 加载标签
    def loadTag(self):
        self.tagList = ['最近', '收藏', '项目'] # fix me! parse .xml
        self.tagButtonList = []
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setGeometry(QRect(70, 260, 650, 400))
        i = 0
        self.defButtonStyle = """
            QPushButton {
                background-color: transparent; /* 背景透明 */
                border: none; /* 移除所有边框 */
                padding: 5px; /* 内边距，根据需要调整 */
            }
            QPushButton:pressed {
                background-color: #d0d0d0; /* 点击时的背景色，可选 */
            }
        """
        self.pushButtonStyle = """
            QPushButton {
                background-color: transparent; /* 背景透明 */
                border: none; /* 移除所有边框 */
                border-bottom: 2px solid gray; /* 添加下边框 */
                padding: 5px; /* 内边距，根据需要调整 */
            }
        """
        for t in self.tagList: # 创建页面并绑定指定按钮
            self.stackedWidget.addWidget(Tag(t, self))
            button = QPushButton(t, self)
            button.setFont(QFont(self.basicFont, 12))
            button.clicked.connect(self.tagButtonCallback)
            button.setGeometry(QRect(80 + (100 * i), 210, 60, 40))
            button.setStyleSheet(self.defButtonStyle)
            self.tagButtonList.append(button)
            i += 1
        # 默认第一个被按下
        self.tagButtonList[0].setStyleSheet(self.pushButtonStyle)

    def tagButtonCallback(self):
        # 根据按下的不同按钮，确定切换到哪个页面
        clickedButton = self.sender()
        buttonName = clickedButton.text()
        print(f"按键 {buttonName} 被按下")
        index = self.tagList.index(buttonName)
        self.stackedWidget.setCurrentIndex(index)
        # 改变按钮颜色
        for b in self.tagButtonList:
            if b == clickedButton:
                b.setStyleSheet(self.pushButtonStyle)
            else:
                b.setStyleSheet(self.defButtonStyle)

    # 创建基本操作图标
    def basciOperation(self):
        urlFather = os.path.dirname(os.path.abspath(__file__))
        self.operationButtonStyle = """
            QPushButton {
                background-color: transparent; /* 背景透明 */
                border: none; /* 移除所有边框 */
                padding: 5px; /* 内边距，根据需要调整 */
            }
            QPushButton:pressed {
                background-color: #d0d0d0; /* 点击时的背景色，可选 */
            }
        """
        # 新建
        path = urlFather + (r'\icon\new.png')
        self.newButton = QPushButton(self)
        self.newButton.setStyleSheet(self.operationButtonStyle)
        self.newButton.setIcon(QIcon(path))
        self.newButton.setIconSize(QSize(150, 150))
        self.newButton.setGeometry(QRect(990, 40, 150, 150))
        # 浏览文件
        path = urlFather + (r'\icon\open.png')
        self.openButton = QPushButton(self)
        self.openButton.setStyleSheet(self.operationButtonStyle)
        self.openButton.setIcon(QIcon(path))
        self.openButton.setIconSize(QSize(125, 125))
        self.openButton.setGeometry(QRect(1000, 240, 125, 125))
        # 导入他人分享的文件
        path = urlFather + (r'\icon\import.png')
        self.importButton = QPushButton(self)
        self.importButton.setStyleSheet(self.operationButtonStyle)
        self.importButton.setIcon(QIcon(path))
        self.importButton.setIconSize(QSize(125, 125))
        self.importButton.setGeometry(QRect(1000, 440, 125, 125))

    # 绑定UI和操作
    def bind(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = App()
    main.show()
    sys.exit(app.exec_())