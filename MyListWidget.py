from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from copy import *

class ListItem:
    def __init__(self, argIndex, argTitleMember, argSelectMember, argText):
        self.Index = argIndex
        self.titleMember = argTitleMember
        self.selectMember = argSelectMember
        self.text = argText
        self.addButton = None
        self.deleteButton = None
        self.editButton = None
        self.plId = ""
        self.youtubeData = None

    def setButtons(self, add, edit, delete):
        self.addButton = add
        self.deleteButton = delete
        self.editButton = edit

    def setYtData(self, argId, argName, argYID):
        self.youtubeData = (argId, argName, argYID)

    def getYtData(self):
        return self.youtubeData

class MyList(list):
    def __init__(self, parent, startTop, argIsCheckBoxEnable=False):
        self.parentWindow = parent
        self.listItems = []
        self.__startTop = startTop
        self.lastTop = startTop
        self.thisSelectedItem = None
        self.onClick = None
        self.onDoubleClick = None
        self.onAddButtonClick = None
        self.onEditButtonClick = None
        self.onDeleteButtonClick = None
        self.isCheckBoxEnable = argIsCheckBoxEnable
        self.IS_ADD = False
        self.IS_DELETE = False
        self.IS_EDIT = False 
        self.beforeItem = None
        self.backupDeleteCss = None
        
    def setIsADDButton(self, argOption):
        self.IS_ADD = argOption

    def setIsDeleteButton(self, argOption):
        self.IS_DELETE = argOption

    def setIsEditButton(self, argOption):
        self.IS_EDIT = argOption

    def __initOptionButon(self, itemObj, listItem):
        addButtonLabel, editButtonLabel, deleteButtonLabel = None, None, None

        if self.IS_ADD:
            addButtonLabel = QLabel(parent=self.parentWindow)
            addButtonLabel.setStyleSheet("border: none;"
                        "background-image: url(:/image/icons/add.png);"
                        "background-repeat: non-repeat;"
                        "background-color: transparent")
            addButtonLabel.setGeometry(itemObj.width() - 110, int(itemObj.height() / 2) - 12 + itemObj.y(), 
                                        24, 24)
            addButtonLabel.mousePressEvent = lambda e: self.onAddButtonClick(listItem) if e.buttons() & Qt.LeftButton and not self.onAddButtonClick == None else None
            addButtonLabel.setVisible(True)
            addButtonLabel.raise_()
            
        if self.IS_EDIT:
            editButtonLabel = QLabel(parent=self.parentWindow)
            editButtonLabel.setStyleSheet("border: none;"
                        "background-image: url(:/image/icons/edit.png);"
                        "background-repeat: non-repeat;"
                        "background-color: transparent")
            editButtonLabel.setGeometry(itemObj.width() - 81, int(itemObj.height() / 2) - 12 + itemObj.y(), 
                                        24, 24)
            editButtonLabel.mousePressEvent = lambda e: self.onEditButtonClick(listItem) if e.buttons() & Qt.LeftButton and not self.onEditButtonClick == None else None
            editButtonLabel.setVisible(True)
            editButtonLabel.raise_()

        if self.IS_DELETE:
            deleteButtonLabel = QLabel(parent=self.parentWindow)
            deleteButtonLabel.setStyleSheet("border: none;"
                        "background-image: url(:/image/icons/delete.png);"
                        "background-repeat: non-repeat;"
                        "background-color: transparent")
            deleteButtonLabel.setGeometry(itemObj.width() - 52, int(itemObj.height() / 2) - 12 + itemObj.y(), 
                                        24, 24)
            deleteButtonLabel.mousePressEvent = lambda e: self.__deleteMousePress(deleteButtonLabel, listItem) if e.buttons() & Qt.LeftButton else None
            deleteButtonLabel.mouseReleaseEvent = lambda e: deleteButtonLabel.setStyleSheet(self.backupDeleteCss) if e.buttons() & Qt.LeftButton else None
            deleteButtonLabel.setVisible(True)
            deleteButtonLabel.raise_()

        return addButtonLabel, editButtonLabel, deleteButtonLabel

    def __deleteMousePress(self, button, listItem):
        self.backupDeleteCss = button.styleSheet()
        button.setStyleSheet("border: none;"
            "background-image: url(:/image/icons/delete_red.png);"
            "background-repeat: non-repeat;"
            "background-color: transparent")
        
        if not self.onDeleteButtonClick == None:
            self.onDeleteButtonClick(listItem)

    def append(self, value):
        self.lastTop += 42
        # init Selction Labele

        newSelLabel = QLabel(parent=self.parentWindow)
        newSelLabel.setGeometry(3, self.lastTop, self.parentWindow.width(), 42)
        newSelLabel.setStyleSheet("background-color: transparent;\nborder:none\n")
        newSelLabel.setVisible(True)
        
        # init item Label
        newTitleLabel = QLabel(text=value, parent=self.parentWindow) if not self.isCheckBoxEnable else QCheckBox(text=value, parent=self.parentWindow)
        newTitleLabel.setFixedWidth(self.parentWindow.width())
        newTitleLabel.move(15, self.lastTop + 13)
        newTitleLabel.setFont(QFont("나눔고딕", 12))
        newTitleLabel.setStyleSheet("background-color: transparent;\nborder: none;\ncolor: black\n\n")
        newTitleLabel.setVisible(True)

        # 체크박스인경우 디폴트는 체크상태
        if self.isCheckBoxEnable:
            newTitleLabel.setChecked(True)

        myItem = ListItem(self.size(), newTitleLabel, newSelLabel, value)
        
        add, edit, delete = self.__initOptionButon(newSelLabel, myItem)

        myItem.setButtons(add, edit, delete)

        newSelLabel.mousePressEvent = lambda e: self.__itemSelection(myItem) if e.buttons() & Qt.LeftButton else None
        newTitleLabel.mousePressEvent = lambda e: self.__itemSelection(myItem) if e.buttons() & Qt.LeftButton else None
        newSelLabel.mouseDoubleClickEvent = lambda e: self.onDoubleClick(myItem) if e.buttons() & Qt.LeftButton and self.onDoubleClick != None else None
        newTitleLabel.mouseDoubleClickEvent = lambda e: self.onDoubleClick(myItem) if e.buttons() & Qt.LeftButton and self.onDoubleClick != None else None
        
        self.listItems.append(myItem)
        super().append(myItem)
        return myItem

    def Select(self, index):
        self.__itemSelection(self[index])

    def removeToIndex(self, Index):
        thisItem = self[Index]
        thisItem.titleMember.deleteLater()
        thisItem.selectMember.deleteLater()
        if self.IS_ADD and self.IS_EDIT and self.IS_DELETE:
            thisItem.addButton.deleteLater()
            thisItem.editButton.deleteLater()
            thisItem.deleteButton.deleteLater()
        self.remove(thisItem)
        self.listItems.remove(thisItem)
        thisItem = None
        self.beforeItem = None
        

    def Refresh(self):
        copySelf = []
        for i in range(self.size()):
            copySelf.append(self[i])

        self.clear()
        for item in copySelf:
            self.append(item.text)
            self.listItems[self.size() - 1].plId = item.plId
            self.listItems[self.size() - 1].youtubeData = item.youtubeData
            self[self.size() - 1].plId = item.plId
            self[self.size() - 1].youtubeData = item.youtubeData

    def __clearSelectLabel(self):
        for item in self.listItems:
            item.selectMember.setStyleSheet("background-color: transparent;\nborder: none;")
            item.titleMember.setStyleSheet("background-color: transparent;\nborder: none;\ncolor: black\n\n")

    def changeButtons(self, option, item):
        if option == 1:
            item.addButton.setStyleSheet("background-image: url(:/image/icons/add_white.png);"
                            "background-repeat: non-repeat;"
                            "background-color: transparent")
            item.editButton.setStyleSheet("background-image: url(:/image/icons/edit_white.png);"
                            "background-repeat: non-repeat;"
                            "background-color: transparent")
            item.deleteButton.setStyleSheet("background-image: url(:/image/icons/delete_white.png);"
                            "background-repeat: non-repeat;"
                            "background-color: transparent")
        elif option == 2:
            item.addButton.setStyleSheet("background-image: url(:/image/icons/add.png);"
                            "background-repeat: non-repeat;"
                            "background-color: transparent")
            item.editButton.setStyleSheet("background-image: url(:/image/icons/edit.png);"
                            "background-repeat: non-repeat;"
                            "background-color: transparent")
            item.deleteButton.setStyleSheet("background-image: url(:/image/icons/delete.png);"
                            "background-repeat: non-repeat;"
                            "background-color: transparent")

    def IsVisibleButtons(self):
        return self.IS_ADD and self.IS_EDIT and self.IS_DELETE

    def clear(self):
        while self.size() > 0:
            self.removeToIndex(self.size() - 1)
        self.lastTop = self.__startTop

    # thisItem : ListItem 객체
    def __itemSelection(self, thisItem):
        self.thisSelectedItem = thisItem.selectMember
        self.__clearSelectLabel() # 선택상태들을 전부 해제

        thisItem.selectMember.setStyleSheet("background-color: #175A38;\nborder:none\n ")
        thisItem.titleMember.setStyleSheet("background-color: transparent;\nborder: none;\ncolor: white\n\n")

        if self.IsVisibleButtons() and not self.beforeItem == None:
            self.changeButtons(2, self.beforeItem)
            self.changeButtons(1, thisItem)
        elif self.IsVisibleButtons():
            self.changeButtons(1, thisItem)

        # checkBox
        if self.isCheckBoxEnable and thisItem.titleMember.isChecked():
            thisItem.titleMember.setChecked(False)
            
        elif self.isCheckBoxEnable and not thisItem.titleMember.isChecked():
            thisItem.titleMember.setChecked(True)

        if self.onClick != None:
            self.onClick(thisItem)
        
        self.beforeItem = thisItem

    def SelectedItem(self):
        return self.thisSelectedItem

    def size(self):
        return len(self)