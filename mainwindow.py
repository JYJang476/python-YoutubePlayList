import sys
import os
import PyQt5.QtWebEngineWidgets
import win32api
from win32con import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5 import uic
from MyListWidget import *

# 리소스 임포트
import rc

main_form = uic.loadUiType("main.ui")[0]
add_form = uic.loadUiType("add.ui")[0]
edit_form = uic.loadUiType("edit.ui")[0]

class MyWindow(QMainWindow, main_form):
    def __init__(self):
        super().__init__()
        self.__initLayout()
        # init shadow object
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(6)
        self.shadow.setXOffset(5)
        self.shadow.setXOffset(7)
        self.shadow.setColor(QColor.fromRgb(0xDEDEDE))
        
        # init ui
        self.setupUi(self)

        self.m_list.setGraphicsEffect(self.shadow)
        self.m_onplaylist.setVisible(False)
        self.m_msgBox.setVisible(False)

        self.m_btback_add.clicked.connect(self.showMainFrame)
        self.m_btback_edit.clicked.connect(self.showMainFrame)

        self.m_msgClose.clicked.connect(self.__m_msgClose_click)
        self.m_addPlayList.clicked.connect(lambda: self.showAddFrame())

        self.m_leftMenu.setVisible(False)
        self.m_closepl.clicked.connect(self.m_closepl_click)

        self.showBlind(visible=False)
        self.m_blind.mousePressEvent = self.m_closepl_click

        self.m_leftMenu.setGeometry(0, 0, 280, 900)
        self.m_blind.setGeometry(280, 0, 271, 900)
        # Mouse Event Timer
        self.mouseEventTimer = QTimer()
        self.mouseEventTimer.setInterval(500)
        self.mouseEventTimer.timeout.connect(self.mainframe_mouseMove)
        self.mouseEventTimer.start()

        # Left Label Click 
        self.m_onplaylist.mousePressEvent = self.m_onplaylist_click       
        
        self.PlayList = MyList(parent=self.m_scroll, startTop=-42)
        self.leftPlayList = MyList(parent=self.m_leftScroll, startTop=0)
        self.m_list_add = MyList(parent=self.m_addScroll, startTop=-42, argIsCheckBoxEnable=True)
        self.m_list_edit = MyList(parent=self.m_editScroll, startTop=-42, argIsCheckBoxEnable=True)

        self.m_doneButton_add.clicked.connect(self.m_doneButton_add_click)
        
        # 테스트용 나중에 삭제할 것      
        for i in range(15):
            self.PlayList.append("kkk" + str(i))
            self.PlayList.onDoubleClick = lambda thisItem: print(thisItem.text)
        
        self.leftPlayList.setIsADDButton(True)
        self.leftPlayList.setIsEditButton(True)
        self.leftPlayList.setIsDeleteButton(True)
        self.leftPlayList.onAddButtonClick = self.showAddFrame

        for i in range(15):
            self.leftPlayList.append("kkk" + str(i))
            self.m_list_add.append("kkk" + str(i))
            self.m_list_edit.append("kkk" + str(i))
        # 테스트 데이터 끝

        self.m_scrollbar.valueChanged.connect(lambda value: self.m_leftScroll.setGeometry(0, 0 - value, 461, 42 * self.leftPlayList.size()))
        self.m_scrollbar.setPageStep(self.m_leftScrollbar.height())
        self.m_scrollbar.setMaximum(130)

        self.m_scrollbar.valueChanged.connect(lambda value: self.m_scroll.setGeometry(0, 0 - value, 461, 42 * self.PlayList.size()))
        self.m_scrollbar.setPageStep(self.m_scrollbar.height())
        self.m_scrollbar.setMaximum(130)

    def __initLayout(self):
        pass
    
    def __m_msgClose_click(self):
        self.m_msgBox.setVisible(False)
        self.showBlind(visible=False)

    def showBlind(self, visible, parent=None):
        if visible:
            self.m_blind.setParent(parent)
        self.m_blind.setVisible(visible)
    
    # add 화면 확인 버튼
    def m_doneButton_add_click(self):
        self.m_blind.mousePressEvent = lambda e: self.__m_msgClose_click()
        self.showBlind(True, self.m_addframe)
        self.m_blind.setGeometry(0, 0, 550, 900)
        self.m_msgBox.setVisible(True)
        self.m_msgBox.setGeometry(110, 310, 317, 174)
        self.m_msgBox.raise_()

    # 플레이리스트 닫기 버튼
    def m_closepl_click(self, e):
        self.m_leftMenu.setVisible(False)
        self.showBlind(visible=False)

    # 플레이리스트 버튼
    def m_onplaylist_click(self, e):
        self.m_blind.mousePressEvent = self.m_closepl_click
        self.m_leftMenu.setVisible(True)
        self.showBlind(True, self)

    def mainframe_mouseMove(self):
        x, y = win32api.GetCursorPos()
        if self.m_onplaylist.isVisible and x - self.windowHandle().position().x() < 31:
            self.m_onplaylist.setVisible(True)
        elif x - self.windowHandle().position().x() > 31:
            self.m_onplaylist.setVisible(False)
    
    def showMainFrame(self):
        self.m_mainframe.setVisible(True)
        self.m_blind.setGeometry(280, 0, 271, 900)
        self.showBlind(True, self)
        self.m_editframe.setVisible(False)
        self.m_addframe.setVisible(False)    

    def showAddFrame(self):
        self.showBlind(visible=False)
        self.m_mainframe.setVisible(False)
        self.m_editframe.setVisible(False)
        self.m_addframe.setVisible(True)

    def showEditFrame(self):
        self.m_mainframe.setVisible(False)
        self.m_addframe.setVisible(False)
        self.m_editframe.setVisible(True)
        
class AddForm(QMainWindow, add_form):
    def __init__(self):
        super().__init__()
        # init ui
        self.setupUi(self)


class EditForm(QMainWindow, edit_form):
    def __init__(self):
        super().__init__()
        # init ui
        self.setupUi(self)


# 가상환경 전용
# qt_dir = "C:\\Users\\주영'\\Documents\\opencv\\qtguitest\\Lib\\site-packages\\PyQt5\\Qt\\"
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_dir + "plugins\\platforms"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindow = MyWindow()
    myWindow.show()
    
    app.exec_()