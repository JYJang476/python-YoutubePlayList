import sys
import os
import threading
import time
from copy import copy, deepcopy
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5 import uic
from MyListWidget import *

# 컨트롤러 임포트
from controller.Controller import Controller
from controller.PlayListController import PlayListController
from controller.MusicListController import MusicListController
from controller.CrawlerController import CrawlerController

# 리소스 임포트
import rc

main_form = uic.loadUiType("main.ui")[0]

class MyWindow(QMainWindow, main_form):
    def __init__(self):
        super().__init__()
        self.__initLayout()
        # init shadow object
        self.PlayerState = 0   
        # init ui
        self.setupUi(self)

        self.showMainFrame()

        self.crawData = None
        self.thisUrl = "https://www.youtube.com/embed/"
        self.nextVideo = None
        self.isClosed = False
        self.m_msgBox.setVisible(False)
        self.m_msgBox_main.setVisible(False)
        self.edit_musics = []
        self.main_musics = []

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

        self.m_schButton.clicked.connect(self.clickCrawButton)
        self.m_nameEdit.clicked.connect(self.showNameEditor)
        
        # Left Label Click 
        self.m_onplaylist.mousePressEvent = self.m_onplaylist_click   
        
        self.PlayList = MyList(parent=self.m_scroll, startTop=-42)
        self.leftPlayList = MyList(parent=self.m_leftScroll, startTop=0)
        self.m_list_edit = MyList(parent=self.m_editScroll, startTop=-42, argIsCheckBoxEnable=True)
        self.m_list_add = MyList(parent=self.m_addScroll, startTop=-42, argIsCheckBoxEnable=True)
        
        self.m_webengine.page().runJavaScript('''
            function initBlack() {
                let player = document.getElementsByTagName("body")[0];
                player.style = 'background-color: black';
            }
            initBlack();
        ''')
        self.m_blind.mousePressEvent = self.m_closepl_click
        self.m_leftMenu.setVisible(True)
        self.showBlind(True, self)
        self.m_leftMenu.raise_()

        # add 페이지 리스트 세팅
        self.leftPlayList.setIsADDButton(True)
        self.leftPlayList.setIsEditButton(True)
        self.leftPlayList.setIsDeleteButton(True)
        
        # 선택 플레이리스트에 음악 추가
        def addMusic(listItem):
            def validation(id, title, artist):
                if (id == "" or title == "" or artist == ""):
                    return False
                return True
            def doneMsg():
                if not validation(self.m_plName_main.text(), self.m_addtitle_main.text(), self.m_addartst_main.text()):
                    QMessageBox.critical(self, "error", "빈 공간이 있는지 확인해주세요")
                else:
                    newMusic = {'link': True, 'title': self.m_addtitle_main.text(), 
                    'musician': self.m_addartst_main.text(), 'url': self.m_plName_main.text()}
                    MusicListController().add_music_list(listItem.plId, [newMusic])
                self.__m_msgClose_click("main")
            self.showMsgBox("main")
            self.m_doneButton_main.clicked.connect(doneMsg)
        
        def delPlayList(listItem):
            PlayListController().destroy_playlist(listItem.plId)
            self.leftPlayList.removeToIndex(listItem.Index)
            self.leftPlayList.Refresh()

        self.leftPlayList.onAddButtonClick = addMusic
        self.leftPlayList.onEditButtonClick = self.initEditFrame
        self.leftPlayList.onDeleteButtonClick = delPlayList

        self.m_doneButton_add.mousePressEvent = lambda e: self.m_doneButton_add.setStyleSheet("border: none; background-color: green; color: white") if e.buttons() & Qt.LeftButton else None
        self.m_doneButton_add.mouseReleaseEvent = self.m_doneButton_add_click

        self.m_doneButton_final.mousePressEvent = lambda e: self.m_doneButton_final.setStyleSheet("border: none; background-color: green; color: white") if e.buttons() & Qt.LeftButton else None
        self.m_doneButton_final.mouseReleaseEvent = self.clickAddDoneButton
        
        self.m_scrollbar.valueChanged.connect(lambda value: self.m_leftScroll.setGeometry(0, 0 - value, 461, 42 * self.leftPlayList.size()))
        self.m_scrollbar.setPageStep(self.m_leftScroll.height() - self.m_leftScrollParent.height())
        self.m_scrollbar.setMaximum(100)

        self.m_scrollbar.valueChanged.connect(lambda value: self.m_scroll.setGeometry(0, 0 - value, 461, 42 * self.PlayList.size()))
        self.m_scrollbar.setPageStep(self.m_scrollbar.height())
        self.m_scrollbar.setMaximum(self.m_scroll.height() - self.m_scrollParent.height())
        
    
        # 플레이리스트 추가
        Controller().init_database()
        for pl_id, pl_name, pl_date in PlayListController().index_playlist():
            listItem = self.leftPlayList.append(pl_name)
            listItem.plId = pl_id
            self.leftPlayList.onDoubleClick = lambda selthisItem: self.printMusicList(selthisItem.plId)
        
        # 플레이어 상태를 계속 체크
        def urlchange():
            self.checkThread = threading.Thread(target=self.checkPlayerState)
            self.checkThread.start()

        self.m_webengine.urlChanged.connect(urlchange)

    def showNameEditor(self):
        self.m_ytbID_edit.setVisible(True)
        self.m_schButton_edit.setVisible(True)
        self.m_ytbID_edit.setText(self.m_listTitle_edit.text())


    # 윈도우 종료시 스레드 처리
    def closeEvent(self, e):
        self.isClosed = True
        e.accept()

    def checkPlayerState(self):
        def goNext(a):
            # -1 : 로딩중 or 에러
            # 0  : 영상 끝
            # 1  : 재생중
            # 5  : 준비중
            # 3  : 일시정지
            if a == 0 or a == -1:
                if self.nextVideo == self.PlayList.size():
                    self.nextVideo = 0
                if self.PlayerState == 0:
                    self.m_webengine.setUrl(QUrl(self.thisUrl + self.PlayList[self.nextVideo].getYtData()[2] + "?autoplay=1"))
                    self.PlayList.Select(self.nextVideo)
                    self.nextVideo += 1        
                    self.PlayerState = 1
            elif a == 3:
                self.PlayerState = 0


        while(not self.isClosed):
            self.m_webengine.page().runJavaScript('''
                function getState() {
                    let player = document.getElementById("movie_player");
                    if(player != null)
                        return player.getPlayerState();
                }
                getState();
            ''', goNext)
            time.sleep(1)

    # 해당 플레이리스트 음악목록 출력 (main)
    def printMusicList(self, argId):
        self.PlayList.clear()
        
        playList = MusicListController().index_music_list(argId)

        for m_id, m_name, m_artist, m_yId, _, m_date in playList:       
            def pl_DbClick(listItem):
                self.m_webengine.setUrl(QUrl("https://www.youtube.com/embed/" + listItem.getYtData()[2]))
                self.nextVideo = listItem.Index + 1    
                
            item = self.PlayList.append(m_name)
            item.setYtData(m_id, m_name, m_yId)
            self.m_webengine.setUrl(QUrl("https://www.youtube.com/embed/" + item.getYtData()[2]))
            self.PlayList.onDoubleClick = pl_DbClick


    # 해당 플레이리스트 음악목록 출력 (main)
    def printMusicListEdit(self, argId):
        self.m_list_edit.clear()
        playList = MusicListController().index_music_list(argId)

        for m_id, m_name, m_artist, m_yId, _, m_date in playList:
            item = self.m_list_edit.append(m_name)
            item.plId = m_id

    # 크롤링 버튼 클릭 시 (add)
    def clickCrawButton(self):
        urldata = "https://www.youtube.com/watch?v=" + self.m_ytbID.text()
        self.crawData = CrawlerController().get_music_list(urldata)
        # # 받아온 데이터를 통해 목록을 작성
        if not str(type(self.crawData)) == "<class 'str'>":
            for data in self.crawData:
                listItem = self.m_list_add.append(data["title"])
                if not data["link"]:
                    listItem.titleMember.setChecked(False)
        elif str(type(self.crawData)) == "<class 'str'>":
            QMessageBox.critical(self, "error", self.crawData,  QMessageBox.Yes)

    def clickAddDoneButton(self, e):
        self.m_doneButton_final.setStyleSheet("background-color: #2F3C8F; color:white")
        newPlayList = []
        
        for data, listItem in zip(self.crawData, self.m_list_add):
            # 체크 상태인 아이템만 저장
            if listItem.titleMember.isChecked():
                # 튜플 데이터들 저장
                newPlayList.append(data)
        # DB에 플레이리스트 추가
        PlayListController().create_playlist(self.m_plName.text(), newPlayList)
        # 정리 후 메인 화면 이동
            # 텍스트박스 지우기(id, 이름)
            # 리스트 박스 초기화
        self.m_ytbID.setText("")
        self.leftPlayList.clear()
        self.m_list_add.clear()
        self.__m_msgClose_click("add")        
        # 리스트 박스 갱신
        # 메인화면 이동
        for pl_id, pl_name, pl_date in PlayListController().index_playlist():
            listItem = self.leftPlayList.append(pl_name)
            listItem.plId = pl_id
            self.leftPlayList.onDoubleClick = lambda selthisItem: self.printMusicList(selthisItem.plId)
            
        self.showMainFrame()

    # 메세지 창을 띄우는 메서드
    def showMsgBox(self, parentName):
        if parentName == "edit":
            def closeEditMsg():
                self.showBlind(False)
                self.m_msgBox_edit.setVisible(False)
                self.m_plName_edit.setText("")
                self.m_addtitle_edit.setText("")
                self.m_addartist_edit.setText("")
                self.edit_musics.clear()
            self.m_msgClose_2.clicked.connect(closeEditMsg)
            self.showBlind(True, parent=self.m_editframe)
            self.m_blind.setGeometry(0, 0, 550, 900)
            self.m_blind.mousePressEvent = lambda e: self.__m_msgClose_click("edit") if e.buttons() & Qt.LeftButton else None
            self.m_msgBox_edit.setGeometry(110, 310, 317, 261)
            self.m_msgBox_edit.setParent(self.m_editframe)
            self.m_msgBox_edit.setVisible(True)
            self.m_msgBox_edit.raise_()

        elif parentName == "main":
            self.showBlind(True, parent=self.m_mainframe)
            self.m_blind.setGeometry(0, 0, 550, 900)            
            self.m_blind.mousePressEvent = lambda e: self.__m_msgClose_click("main") if e.buttons() & Qt.LeftButton else None
            def closeMainMsg():
                self.showBlind(False)
                self.m_msgBox_main.setVisible(False)
                self.m_plName_main.setText("")
                self.m_addtitle_main.setText("")
                self.m_addartst_main.setText("")
            
            self.m_msgClose_main.clicked.connect(closeMainMsg)

            self.m_msgBox_main.setGeometry(110, 310, 317, 261)
            self.m_msgBox_main.setParent(self.m_mainframe)
            self.m_msgBox_main.setVisible(True)
            self.m_msgBox_main.raise_()

    def __initLayout(self):
        pass
    
    def __m_msgClose_click(self, type):
        self.showBlind(visible=False)
        if type == "edit":
            self.m_msgBox_edit.setVisible(False)
        elif type == "add":
            self.m_msgBox.setVisible(False)
        elif type == "main":
            self.m_msgBox_main.setVisible(False)
            if self.m_leftMenu.isVisible():
                self.showBlind(True, parent=self.m_mainframe)
                self.m_blind.mousePressEvent = self.m_closepl_click
                self.m_blind.setGeometry(280, 0, 271, 900)
        

    def showBlind(self, visible, parent=None):
        if visible:
            self.m_blind.setParent(parent)
        self.m_blind.setVisible(visible)
    
    # add 화면 확인 버튼
    def m_doneButton_add_click(self, e):
        self.m_doneButton_add.setStyleSheet("border: none; background-color: #2F3C8F; color: white")
        self.m_blind.mousePressEvent = lambda e: self.__m_msgClose_click("add") if e.buttons() & Qt.LeftButton else None
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
        if e.buttons() & Qt.LeftButton:
            self.m_blind.mousePressEvent = self.m_closepl_click
            self.m_leftMenu.setVisible(True)
            self.showBlind(True, self)
            self.m_leftMenu.raise_()

    def showMainFrame(self):
        self.m_mainframe.setVisible(True)
        self.m_blind.setGeometry(280, 0, 271, 900)
        self.m_blind.mousePressEvent = self.m_closepl_click
        self.showBlind(True, self)
        self.m_editframe.setVisible(False)
        self.m_addframe.setVisible(False)    

    def showAddFrame(self):
        self.showBlind(visible=False)        
        self.m_mainframe.setVisible(False)
        self.m_editframe.setVisible(False)
        self.m_addframe.setVisible(True)

    def showEditFrame(self):       
        self.showBlind(False)
        self.m_mainframe.setVisible(False)
        self.m_addframe.setVisible(False)
        self.m_editframe.setVisible(True)

    # edit 페이지 초기화 (edit)
    def initEditFrame(self, ListItem):
        # 텍스트박스 숨기기
        self.m_ytbID_edit.setVisible(False)
        self.m_schButton_edit.setVisible(False)
        # 리스트 비우기
        if self.m_list_edit.size() > 0:
            self.m_list_edit.clear()
        # 플레이리스트 정보 가져오기
        # 음악 목록 로드
            # 목록 가져와서 출력
        self.printMusicListEdit(ListItem.plId)
        # 이름 로드
        self.m_listTitle_edit.setText(ListItem.titleMember.text())
        # 이름 바꾸기 버튼 클릭 이벤트
        self.m_schButton_edit.clicked.connect(lambda: print(self.m_ytbID_edit.text()) )
        # 확인 버튼 클릭 이벤트 m_musicAddButton
        self.m_musicAddButton.clicked.connect(lambda: self.showMsgBox("edit"))
        self.m_doneButton_final_edit.clicked.connect(lambda: self.clickMusicAddDone(ListItem.plId))
        self.m_doneButton_edit.clicked.connect(lambda: self.clickEditDoneButton(ListItem.plId))
        self.m_msgBox_edit.setVisible(False)
        
        def doneChangeName():
            PlayListController().modify_playlist_name(ListItem.plId, self.m_ytbID_edit.text())
            self.m_ytbID_edit.setVisible(False)
            self.m_schButton_edit.setVisible(False)
            self.m_listTitle_edit.setText(self.m_ytbID_edit.text())
            ListItem.titleMember.setText(self.m_ytbID_edit.text())
            self.m_ytbID_edit.setText("")
            

        self.m_schButton_edit.clicked.connect(doneChangeName)

        self.showEditFrame()

    def clickMusicAddDone(self, argPlId):
        def validation(id, title, artist):
            if (id == "" or title == "" or artist == ""):
                return False
            return True
        if(not validation(self.m_plName_edit.text(), self.m_addtitle_edit.text(), self.m_addartist_edit.text())):
            QMessageBox.critical(self, "error", "빈 공간이 있는지 확인해주세요")
        else:
            newMusic = {'link': True, 'title': self.m_addtitle_edit.text(), 
            'musician': self.m_addartist_edit.text(), 'url': self.m_plName_edit.text()}
            self.edit_musics.append(newMusic)
            self.m_list_edit.append(self.m_addtitle_edit.text())

        self.showBlind(False)
        self.m_msgBox_edit.setVisible(False)
        self.m_plName_edit.setText("")
        self.m_addtitle_edit.setText("")
        self.m_addartist_edit.setText("")
        self.edit_musics.clear()
       
        self.m_blind.mousePressEvent = self.m_closepl_click

        
    def clickEditDoneButton(self, argPlId):
        if(self.m_ytbID_edit.isVisible() or self.m_schButton_edit.isVisible()):
            QMessageBox.critical(self, "error", "이름변경이 진행중입니다.")
            return

        newPlayList = []
        musicList = MusicListController().index_music_list(argPlId)  
        for music, listItem in zip(musicList, self.m_list_edit):
            # 체크 상태가 아닌 음악 삭제
            if not listItem.titleMember.isChecked():
                # 삭제할 음악 index 추가
                newPlayList.append(listItem.plId)
        
        if(len(newPlayList) > 0):
            MusicListController().delete_music_list(newPlayList)

        if(len(self.edit_musics) > 0):
            MusicListController().add_music_list(argPlId, self.edit_musics)
        # 정리 후 메인 화면 이동
            # 텍스트박스 지우기(id, 이름)
            # 리스트 박스 초기화
        self.showMainFrame()


# 가상환경 전용
# qt_dir = "C:\\Users\\주영'\\Documents\\opencv\\qtguitest\\Lib\\site-packages\\PyQt5\\Qt\\"
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_dir + "plugins\\platforms"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindow = MyWindow()
    myWindow.show()
    
    app.exec_()