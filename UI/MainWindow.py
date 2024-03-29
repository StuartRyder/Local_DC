import time
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from UI.components.Heading import Heading
from UI.components.User import User
from UI.components.UserFile import UserFile
from UI.components.InsertFiles import InsertFiles
from UI.components.FileSearch import FileSearch
from UI.components.UserSearch import UserSearch
from UI.components.File import File
from UI.components.DownloadFile import DownloadFile
from UI.components.ReceiveFileThread import ReceiveFileThread
from .ChatWindow import ChatWindow


class BtnThread(QtCore.QThread):
    my_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(BtnThread, self).__init__()
        self.seachMode = False

    def run(self):
        while True:
            if self.seachMode == False:
                self.my_signal.emit()
            time.sleep(5)

    def setSearchMode(self, state: bool):
        self.seachMode = state


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent, clientIns):
        super(MainWindow, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.clientIns = clientIns
        self.searchMode = True
        self.fileLayoutLst = []
        self.userFiles = {}
        self.downloadFilesComponents = {}
        self.setObjectName("MainWindow")
        self.resize(1300, 846)
        self.setWindowIcon(QtGui.QIcon('images/logo.svg'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the Application?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.clientIns.closeApplication()
            # self.parent().show()
        else:
            event.ignore()

    def setupUi(self):
        #****** Defining layouts ***** #
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        ##***************** "Current Online Users" section**************##
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")

        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setSizeConstraint(
            QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.verticalLayout_10 = QtWidgets.QHBoxLayout()
        self.verticalLayout_10.setSizeConstraint(
            QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout_10.setObjectName("verticalLayout_10")

        self.userScroll = QtWidgets.QScrollArea()
        self.userWidget = QtWidgets.QWidget()
        self.allUsers = []

        self.heading1 = Heading("CURRENT ONLINE USERS", self.centralwidget)
        self.verticalLayout_10.addWidget(self.heading1)
        self.verticalLayout_5.addLayout(self.verticalLayout_10)

        self.usrSearchLayout = UserSearch(
            self.centralwidget, self.setSearchMode, self.searchUsers, self.createBtns)
        self.verticalLayout_5.addLayout(self.usrSearchLayout)

        # Btns in Thread
        self.StartButtonEvent()

        self.userWidget.setLayout(self.verticalLayout_9)
        # Scroll Area Properties
        self.userScroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.userScroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.userScroll.setWidgetResizable(True)
        self.userScroll.setWidget(self.userWidget)
        self.verticalLayout_5.addWidget(self.userScroll)
        self.verticalLayout_5.setStretch(0, 1)
        self.verticalLayout_5.setStretch(1, 10)
        self.verticalLayout_4.addLayout(self.verticalLayout_5)
        # divider
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_4.addWidget(self.line_3)
        ##*********************** END ************************##

        ##***************** "Your files" section **************##
        self.verticalLayout_18 = QtWidgets.QVBoxLayout()
        self.verticalLayout_18.setObjectName("verticalLayout_18")

        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")

        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")

        self.userFilesScroll = QtWidgets.QScrollArea()
        self.userFilesWidget = QtWidgets.QWidget()

        self.heading2 = Heading("YOUR FILES", self.centralwidget)
        self.horizontalLayout_10.addWidget(self.heading2)
        self.verticalLayout_6.addLayout(self.horizontalLayout_10)

        self.paintUserFiles()

        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_18.addItem(spacerItem1)
        self.userFilesWidget.setLayout(self.verticalLayout_18)
        # Scroll Area Properties
        self.userFilesScroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self.userFilesScroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self.userFilesScroll.setWidgetResizable(True)
        self.userFilesScroll.setWidget(self.userFilesWidget)
        self.verticalLayout_6.addWidget(self.userFilesScroll)
        # InsertFilesLayout
        self.InsertFilesLayout = InsertFiles(self.centralwidget)
        self.verticalLayout_6.addLayout(self.InsertFilesLayout)
        self.verticalLayout_6.setStretch(0, 1)
        self.verticalLayout_6.setStretch(1, 10)
        self.verticalLayout_4.addLayout(self.verticalLayout_6)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        ##*********************** END ************************##

        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)

        ##***************** "Search file btn" **************##
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.fileSearchLayout = FileSearch(
            self.centralwidget, self.searchForFiles)
        self.verticalLayout_7.addLayout(self.fileSearchLayout)

        self.line_8 = QtWidgets.QFrame(self.centralwidget)
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.verticalLayout_7.addWidget(self.line_8)
        ##*********************** END ************************##

        ##***************** "Display requested files" **************##
        self.fileSrchScroll = QtWidgets.QScrollArea()
        self.fileSearchWidget = QtWidgets.QWidget()

        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")

        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_18 = QtWidgets.QLabel(self.fileSearchWidget)
        self.label_18.setStyleSheet("font: 75 10pt \"Verdana\";")
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_5.addWidget(self.label_18)
        self.label_17 = QtWidgets.QLabel(self.fileSearchWidget)
        self.label_17.setStyleSheet("font: 75 10pt \"Verdana\";")
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_5.addWidget(self.label_17)
        self.label_16 = QtWidgets.QLabel(self.fileSearchWidget)
        self.label_16.setStyleSheet("font: 75 10pt \"Verdana\";")
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_5.addWidget(self.label_16)
        self.label_15 = QtWidgets.QLabel(self.fileSearchWidget)
        self.label_15.setStyleSheet("font: 75 10pt \"Verdana\";")
        self.label_15.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_5.addWidget(self.label_15)
        self.label_14 = QtWidgets.QLabel(self.fileSearchWidget)
        self.label_14.setText("")
        self.label_14.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_5.addWidget(self.label_14)
        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 2)
        self.horizontalLayout_5.setStretch(2, 7)
        self.horizontalLayout_5.setStretch(3, 2)
        self.horizontalLayout_5.setStretch(4, 1)
        self.verticalLayout_13.addLayout(self.horizontalLayout_5)
        self.line_9 = QtWidgets.QFrame(self.fileSearchWidget)
        self.line_9.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_9.setObjectName("line_9")
        self.verticalLayout_13.addWidget(self.line_9)
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_13.addItem(spacerItem2)

        self.fileSearchWidget.setLayout(self.verticalLayout_13)
        # Scroll Area Properties
        self.fileSrchScroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self.fileSrchScroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.fileSrchScroll.setWidgetResizable(True)
        self.fileSrchScroll.setWidget(self.fileSearchWidget)
        self.verticalLayout_7.addWidget(self.fileSrchScroll)
        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 10)
        self.verticalLayout.addLayout(self.verticalLayout_7)
        # divider
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        ##*********************** END ************************##

        ##***************** "Download section **************##
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")

        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")

        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")

        self.dlFileSrchScroll = QtWidgets.QScrollArea()
        self.dlFileSearchWidget = QtWidgets.QWidget()

        self.heading3 = Heading("Downloads", self.centralwidget)
        self.verticalLayout_16.addWidget(self.heading3)
        self.verticalLayout_8.addLayout(self.verticalLayout_16)

        spacerItem3 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_15.addItem(spacerItem3)
        self.dlFileSearchWidget.setLayout(self.verticalLayout_15)
        # Scroll Area Properties
        self.dlFileSrchScroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self.dlFileSrchScroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.dlFileSrchScroll.setWidgetResizable(True)
        self.dlFileSrchScroll.setWidget(self.dlFileSearchWidget)
        self.verticalLayout_8.addWidget(self.dlFileSrchScroll)
        
        # self.verticalLayout_8.addLayout(self.verticalLayout_15)

        self.verticalLayout_8.setStretch(0, 1)
        self.verticalLayout_8.setStretch(1, 7)
        self.verticalLayout.addLayout(self.verticalLayout_8)
        self.verticalLayout.setStretch(0, 2)
        self.verticalLayout.setStretch(2, 1)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(2, 2)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.paintDownloadsFiles()
        ##*********************** END ************************##

        # setting the central widget
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1181, 26))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        title = "Welcome " + \
            self.clientIns.clientCredentials["username"] + " to 🦈 INTRA-SHARE 🦈"
        self.setWindowTitle(_translate("MainWindow", title))
        self.heading1.setText(_translate("MainWindow", "CURRENT ONLINE USERS"))
        self.usrSearchLayout.lineEdit_2.setPlaceholderText(
            _translate("MainWindow", "Search Users"))
        self.usrSearchLayout.pushButton_2.setText(
            _translate("MainWindow", "Search"))

        self.heading2.setText(_translate("MainWindow", "SHARED FILES"))
        self.InsertFilesLayout.insertFilesBtn.clicked.connect(self.openFile)

        self.fileSearchLayout.lineEdit_2.setPlaceholderText(
            _translate("MainWindow", "Search Files"))
        self.fileSearchLayout.pushButton_2.setText(
            _translate("MainWindow", "Search"))

        self.label_18.setText(_translate("MainWindow", "Type"))
        self.label_17.setText(_translate("MainWindow", "FileName"))
        self.label_16.setText(_translate("MainWindow", "Owner"))
        self.label_15.setText(_translate("MainWindow", "Size     "))

        self.heading3.setText(_translate("MainWindow", "DOWNLOADS"))

    def StartButtonEvent(self):
        self.btnThrd = BtnThread()
        self.btnThrd.finished.connect(self.thread_finished)
        self.btnThrd.my_signal.connect(self.createBtns)
        self.btnThrd.start()

    def deleteUserProps(self):
        try:
            if len(self.allUsers) >= 1:
                for i in range(0, len(self.allUsers) - 1):
                    self.allUsers[i][0].removeWidget(
                        self.allUsers[i][0].username_label)
                    self.allUsers[i][0].removeWidget(
                        self.allUsers[i][0].msgPushButton)
                    self.allUsers[i][0].removeWidget(
                        self.allUsers[i][0].filePushButton)
                    self.verticalLayout_9.removeWidget(self.allUsers[i][1])
                    self.verticalLayout_9.removeItem(self.allUsers[i][0])
                self.verticalLayout_9.removeItem(self.allUsers[-1])
            self.allUsers.clear()
        except Exception as err:
            print("err: ", err)

    # Create buttons in thread

    def createBtns(self):
        try:
            self.deleteUserProps()

            for clientID, clientOBJ in self.clientIns.activeClients.items():
                if clientOBJ.online:
                    usr = User(clientOBJ, self.userWidget,
                               self.msgCurrentUser, self.getFileListOfClient)
                    # divider
                    usrline = QtWidgets.QFrame(self.userWidget)
                    usrline.setFrameShape(QtWidgets.QFrame.HLine)
                    usrline.setFrameShadow(QtWidgets.QFrame.Sunken)
                    usrline.setObjectName("usrline_" + str(clientID))
                    # adding to layout and widget
                    self.verticalLayout_9.addLayout(usr)
                    self.verticalLayout_9.addWidget(usrline)
                    self.allUsers.append((usr, usrline))
                # print(self.allUsers)

            spacerItem = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.verticalLayout_9.addItem(spacerItem)
            self.allUsers.append(spacerItem)
        except Exception as err:
            print("ERROR: ", err)

    def msgCurrentUser(self, clientOBJ):
        ID = clientOBJ.clientID
        if ID in self.clientIns.activeMessagingClient.keys():
            ret = QMessageBox.warning(self, 'Failed to open...',f"Chat window already open!", QMessageBox.Ok, QMessageBox.Cancel)
            return
        self.user = ChatWindow(clientOBJ, self.clientIns, self)
        self.user.show()

    def openFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filePathList, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Select Files", "", "All Files ();;Python Files (.py)", options=options)
        if filePathList:
            try:
                files = []
                for filepath in filePathList:
                    filename = filepath.split("/")[-1]
                    filesize = os.path.getsize(filepath)
                    files.append((filename, filepath, filesize))
                self.clientIns.insertFiles(files)
                self.paintUserFiles()
            except Exception as err:
                print("File Insertion Error: ", err)

    def thread_finished(self):
        print("finished\n")

    def searchUsers(self, search: str):
        try:
            lst = self.clientIns.searchUsers(search)
            self.setSearchMode(True)
            self.deleteUserProps()
            for clientOBJ in lst:
                clientID, username, online = clientOBJ
                if online:
                    usr = User(
                        self.clientIns.activeClients[clientID], self.userWidget, self.msgCurrentUser, self.getFileListOfClient)
                    # divider
                    usrline = QtWidgets.QFrame(self.userWidget)
                    usrline.setFrameShape(QtWidgets.QFrame.HLine)
                    usrline.setFrameShadow(QtWidgets.QFrame.Sunken)
                    usrline.setObjectName("usrline_" + str(clientID))
                    # adding to layout and widget
                    self.verticalLayout_9.addLayout(usr)
                    self.verticalLayout_9.addWidget(usrline)
                    self.allUsers.append((usr, usrline))
                # print(self.allUsers)

            spacerItem = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.verticalLayout_9.addItem(spacerItem)
            self.allUsers.append(spacerItem)
        except Exception as err:
            print("ERROR: ", err)

    def setSearchMode(self, state: bool):
        self.searchMode = state
        self.btnThrd.setSearchMode(state)

    def searchForFiles(self, filename: str):
        self.clientIns.searchFiles(filename)
        self.paintDisplayFiles()

    def getFileListOfClient(self, clientID: int):
        self.clientIns.getFileListOfClient(clientID)
        self.paintDisplayFiles()

    def paintDisplayFiles(self):
        # deleting fileLayout from fileLayoutLst
        for fileLayout in self.fileLayoutLst:
            fileLayout[0].removeWidget(fileLayout[0].fileType)
            fileLayout[0].removeWidget(fileLayout[0].fileName)
            fileLayout[0].removeWidget(fileLayout[0].ownerName)
            fileLayout[0].removeWidget(fileLayout[0].fileSize)
            fileLayout[0].removeWidget(fileLayout[0].dwnloadBtn)

            self.verticalLayout_13.removeWidget(fileLayout[1])
            self.verticalLayout_13.removeItem(fileLayout[0])

        self.fileLayoutLst.clear()

        # painting displayFiles
        for fileID, file in self.clientIns.displayFiles.items():
            fileLayout = File(
                fileID, file, self.fileSearchWidget, self.downloadsList, self.clientIns)
            # divider
            line_7 = QtWidgets.QFrame(self.fileSearchWidget)
            line_7.setFrameShape(QtWidgets.QFrame.HLine)
            line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
            line_7.setObjectName("line" + str(fileID))
            self.verticalLayout_13.insertLayout(
                len(self.verticalLayout_13)-1, fileLayout)
            self.verticalLayout_13.insertWidget(
                len(self.verticalLayout_13)-1, line_7)
            self.fileLayoutLst.append((fileLayout, line_7))

    def paintUserFiles(self):
        # deleting userFile layout from userFiles dict
        for fileID, fileLayout in self.userFiles.items():
            fileLayout[0].removeWidget(fileLayout[0].fileTypeBtn)
            fileLayout[0].removeWidget(fileLayout[0].fileName)
            fileLayout[0].removeWidget(fileLayout[0].fileSize)
            fileLayout[0].removeWidget(fileLayout[0].deleteBtn)

            self.verticalLayout_18.removeWidget(fileLayout[1])
            self.verticalLayout_18.removeItem(fileLayout[0])
        self.userFiles.clear()

        # painting userFiles
        for fileID, file in self.clientIns.hostedFiles.items():
            fileLayout = UserFile(
                file, fileID, self.userFilesWidget, self.removeUserFile)
            # divider
            line_7 = QtWidgets.QFrame(self.userFilesWidget)
            line_7.setFrameShape(QtWidgets.QFrame.HLine)
            line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
            line_7.setObjectName("divider" + str(fileID))
            self.verticalLayout_18.insertLayout(
                len(self.verticalLayout_18)-1, fileLayout)
            self.verticalLayout_18.insertWidget(
                len(self.verticalLayout_18)-1, line_7)
            self.userFiles[fileID] = (fileLayout, line_7)

    def removeUserFilePaint(self, fileID: int):
        fileLayout = self.userFiles[fileID]

        fileLayout[0].removeWidget(fileLayout[0].fileTypeBtn)
        fileLayout[0].removeWidget(fileLayout[0].fileName)
        fileLayout[0].removeWidget(fileLayout[0].fileSize)
        fileLayout[0].removeWidget(fileLayout[0].deleteBtn)

        self.verticalLayout_18.removeWidget(fileLayout[1])
        self.verticalLayout_18.removeItem(fileLayout[0])

        self.userFiles.pop(fileID)

    def removeUserFile(self, fileID: int):
        try:
            self.clientIns.deleteFile(fileID)
            self.removeUserFilePaint(fileID)
        except Exception as err:
            print("Failed to remove the file ", err)

    # show downloading files option
    def downloadsList(self, fileID:int, file:tuple):
        try:
            fileName, fileSize, userID, username, status = file
            if fileID in self.clientIns.activeClients[userID].fileTaking.keys():
                # start,completed_bytes,isPaused,pauseEvent,filepath = self.clientIns.activeClients[userID].fileTaking[fileID]
                # parameters = self.clientIns.downloadFile(userID, fileID, fileName, int(fileSize), filepath)
                QMessageBox.information(self, "File Download information", "Already present in downloads section.")
                return
            else:
                # Open dialog to select folder
                options = QtWidgets.QFileDialog.Options()
                options |= QtWidgets.QFileDialog.DontUseNativeDialog
                fileDir = str(QtWidgets.QFileDialog.getExistingDirectory(
                    self, "Select Directory"))
                if fileDir == None or len(fileDir) == 0:
                    return
                filepath = os.path.join(fileDir, fileName)
                parameters = self.clientIns.downloadFile(
                    userID, fileID, fileName, int(fileSize), filepath)
            if parameters == None:
                return
            self.dwnloadThread = ReceiveFileThread(parameters)
            self.dwnloadThread.finished.connect(
                lambda: print(f"dwnloadThread finished {fileID}"))
            self.dwnloadThread.finishedSig.connect(self.removeDownloadFile)
            self.dwnloadThread.progress.connect(self.downloadFileProgress)
            dlFileVbox = DownloadFile(file, fileID, self.dlFileSearchWidget, self.dwnloadThread, False, self.clientIns,self.removeDownloadFile, filepath, self.removeDownloadFile, self.downloadFileProgress)
            self.verticalLayout_15.insertLayout(len(self.verticalLayout_15)-1, dlFileVbox)

            # divider
            line_10 = QtWidgets.QFrame(self.dlFileSearchWidget)
            line_10.setFrameShape(QtWidgets.QFrame.HLine)
            line_10.setFrameShadow(QtWidgets.QFrame.Sunken)
            line_10.setObjectName("line_10")
            self.verticalLayout_15.insertWidget(
                len(self.verticalLayout_15)-1, line_10)
            self.downloadFilesComponents[fileID] = (dlFileVbox, line_10)

            self.dwnloadThread.start()
        except Exception as err:
            print("download err: ", err)

    @pyqtSlot(int, int)
    def downloadFileProgress(self, fileID: int, progress: int):
        try:
            Component = self.downloadFilesComponents[fileID]
            Component[0].dlProgressBar.setProperty("value", progress)
        except Exception as e:
            print("Error setting the progessbar: ", e)

    @pyqtSlot(int, int)
    def removeDownloadFile(self, userID: int, fileID: int):
        try:
            Component = self.downloadFilesComponents[fileID]
            Component[0].removeWidget(Component[0].dlFileInfo)
            Component[0].removeWidget(Component[0].pOr)
            Component[0].removeWidget(Component[0].clear)
            Component[0].removeWidget(Component[0].dlProgressBar)
            Component[0].removeItem(Component[0].dlFileProgressHbox)

            self.verticalLayout_18.removeWidget(Component[1])
            self.verticalLayout_18.removeItem(Component[0])

            print("REMOVING DOWNLOAD COMPONENT",fileID)
            del self.downloadFilesComponents[fileID]
            
            if fileID in self.clientIns.activeClients[userID].fileTaking.keys():
                self.clientIns.activeClients[userID].fileTaking.pop(fileID)
        except Exception as e:
            print("Error removeDownloadFile: ", e)

    def paintDownloadsFiles(self):
        for clientID,clientObj in self.clientIns.activeClients.items():
            deleteFiles = []
            for fileID,fileOBj in self.clientIns.activeClients[clientID].fileTaking.items():
                file = self.clientIns.getFileDetails(fileID)
                if len(file) == 0:
                    deleteFiles.append(fileID)
                    continue
                filepath = fileOBj[-1]
                dlFileVbox = DownloadFile(file, fileID, self.dlFileSearchWidget, None, False, self.clientIns,self.removeDownloadFile, filepath, self.removeDownloadFile, self.downloadFileProgress)
                self.verticalLayout_15.insertLayout(len(self.verticalLayout_15)-1, dlFileVbox)
                
                # divider
                line_10 = QtWidgets.QFrame(self.dlFileSearchWidget)
                line_10.setFrameShape(QtWidgets.QFrame.HLine)
                line_10.setFrameShadow(QtWidgets.QFrame.Sunken)
                line_10.setObjectName("line_10")
                self.verticalLayout_15.insertWidget(len(self.verticalLayout_15)-1, line_10)
                self.downloadFilesComponents[fileID] = (dlFileVbox, line_10)
            for fileID in deleteFiles:
                self.clientIns.activeClients[clientID].fileTaking.pop(fileID)
