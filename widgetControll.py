from MyListWidget import *

class VideoControll:
    def __init__(self, argTargetWebView):
        self.videoWidget = argTargetWebView
        self.__BaseYoutubeUrl = "https://www.youtube.com/embed/"
    
    def setUrl(self, argVideoId):
        self.videoWidget.setUrl(QUrl("%s%s".(self.__BaseYoutubeUrl, argVideoId)))

    def getUrl(self):
        return QUrl("%s%s".(self.__BaseYoutubeUrl, argVideoId))


class AddControll:
    def __init__(self):
        self.__mainList = MyList(parent=self.m_addScroll, startTop=-42, argIsCheckBoxEnable=True)
        self.__mainList.setIsADDButton(True)
        self.__mainList.setIsEditButton(True)
        self.__mainList.setIsDeleteButton(True)
        self.__mainList.onAddButtonClick = self.showAddFrame