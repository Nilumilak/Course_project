from PyQt5 import QtCore, QtGui, QtWidgets
from VkDownloader import VkDownloader
from OkDownloader import OkDownloader


class UploadThread(QtCore.QThread):  # QThread to prevent freezing GUI
    def __init__(self, line_1, line_2, line_3, progress_bar, status_line, yandex_line, google_line):
        """
        Launches VkDownloader or OkDownloader
        :param line_1: profile id (or screen_name for vk)
        :param line_2: number of photos (default=5)
        :param line_3: album id
        :param progress_bar: progress bar in GUI
        :param status_line: bottom 'Status' bar in GUI
        :param yandex_line: 'Yandex drive token bar' in GUI
        :param google_line: 'Google drive token bar' in GUI
        """
        super().__init__()
        self.line_1 = line_1
        self.line_2 = line_2
        self.progress_bar = progress_bar
        self.line_3 = line_3
        self.status_line = status_line
        self.yandex_line = yandex_line
        self.google_line = google_line

    def run(self):
        if self.line_1.text() == '':
            self.status_line.setText('enter the profile id')

        elif self.yandex_line.text() == '' and self.google_line.text() == '':
            self.status_line.setText('enter yandex token or google token')

        elif (self.line_1.objectName() in ['lineEdit_6', 'lineEdit_8']   # checks Ok id's lines in GUI
              and self.line_1.text() and not self.line_1.text().isdigit()):
            self.status_line.setText('"Ok id" should be a number')

        elif self.line_2.text() and not self.line_2.text().isdigit():
            self.status_line.setText('"Number of photos" should be a number (1, 2, 3...)')

        elif self.line_3 and not self.line_3.text():  # checks album id's lines in GUI
            self.status_line.setText('enter the album id')

        elif self.line_3 and self.line_3.text() and not self.line_3.text().isdigit():  # checks album id's lines in GUI
            self.status_line.setText('album id should be a number')

        else:                                 # starts uploading if all input requirements are satisfied
            if self.line_3 is None:
                if self.line_1.objectName() in ['lineEdit_1', 'lineEdit_3']:
                    downloader = VkDownloader(self.line_1.text(), self.yandex_line.text(),
                                              self.google_line.text(), self.progress_bar)
                    downloader.upload_profile_photos_to_cloud_storage(int(self.line_2.text())
                                                                      if self.line_2.text() else 5)
                else:
                    downloader = OkDownloader(self.line_1.text(), self.yandex_line.text(),
                                              self.google_line.text(), self.progress_bar)
                    downloader.upload_profile_photos_to_cloud_storage(int(self.line_2.text())
                                                                      if self.line_2.text() else 5)
            else:
                if self.line_1.objectName() in ['lineEdit_1', 'lineEdit_3']:
                    downloader = VkDownloader(self.line_1.text(), self.yandex_line.text(),
                                              self.google_line.text(), self.progress_bar)
                    downloader.upload_album_photos_to_cloud_storage(int(self.line_3.text()),
                                                                    int(self.line_2.text())
                                                                    if self.line_2.text() else 5)
                else:
                    downloader = OkDownloader(self.line_1.text(), self.yandex_line.text(),
                                              self.google_line.text(), self.progress_bar)
                    downloader.upload_album_photos_to_cloud_storage(int(self.line_3.text()),
                                                                    int(self.line_2.text())
                                                                    if self.line_2.text() else 5)

            if downloader.respond is None or {'error', 'error_msg'} & downloader.respond.json().keys():
                self.status_line.setText('Invalid profile or album id')

            elif (str(downloader.ya_respond) and 'error' in downloader.ya_respond.json()
                  and 'DiskPathPointsToExistentDirectoryError' not in downloader.ya_respond.json().values()):
                self.status_line.setText('Invalid yandex token')

            elif str(downloader.google_respond) and 'error' in downloader.google_respond.json():
                self.status_line.setText('Invalid google token')

            else:
                self.status_line.setText('Success')


class Window(object):  # Main GUI's window
    def upload(self, line_1, line_2, progress_bar, line_3=None):
        """
        Launches a thread
        :param line_1: profile id (or screen_name for vk)
        :param line_2: number of photos (default=5)
        :param progress_bar: progress bar in GUI
        :param line_3: album id
        """
        self.uploading = UploadThread(line_1, line_2, line_3, progress_bar, self.status_line,
                                      self.yandex_line, self.google_line)
        self.uploading.start()

    def setupUi(self, window):
        window.setObjectName("window")
        window.resize(830, 560)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(window.sizePolicy().hasHeightForWidth())
        window.setSizePolicy(sizePolicy)
        window.setMinimumSize(QtCore.QSize(160, 10))
        window.setMaximumSize(QtCore.QSize(830, 560))
        self.centralwidget = QtWidgets.QWidget(window)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton_1 = QtWidgets.QPushButton(self.centralwidget)           #Buttons
        self.pushButton_1.setGeometry(QtCore.QRect(286, 144, 75, 20))
        self.pushButton_1.setObjectName("pushButton_1")
        self.pushButton_1.clicked.connect(lambda: self.upload(self.lineEdit_1, self.lineEdit_2, self.progressBar_1))
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(285, 241, 75, 20))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(
            lambda: self.upload(self.lineEdit_3, self.lineEdit_5, self.progressBar_2, self.lineEdit_4))
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(285, 338, 75, 20))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(lambda: self.upload(self.lineEdit_6, self.lineEdit_7, self.progressBar_3))
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(285, 432, 75, 20))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(
            lambda: self.upload(self.lineEdit_8, self.lineEdit_10, self.progressBar_4, self.lineEdit_9))

        self.progressBar_1 = QtWidgets.QProgressBar(self.centralwidget)         # Progress bars
        self.progressBar_1.setGeometry(QtCore.QRect(376, 144, 250, 20))
        self.progressBar_1.setProperty("value", 0)
        self.progressBar_1.setObjectName("progressBar_1")
        self.progressBar_2 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_2.setGeometry(QtCore.QRect(375, 241, 250, 20))
        self.progressBar_2.setProperty("value", 0)
        self.progressBar_2.setObjectName("progressBar_2")
        self.progressBar_3 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_3.setGeometry(QtCore.QRect(375, 338, 250, 20))
        self.progressBar_3.setProperty("value", 0)
        self.progressBar_3.setObjectName("progressBar_3")
        self.progressBar_4 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_4.setGeometry(QtCore.QRect(375, 432, 250, 20))
        self.progressBar_4.setProperty("value", 0)
        self.progressBar_4.setObjectName("progressBar_4")

        self.status_line = QtWidgets.QLineEdit(self.centralwidget)              # Bottom 'Status' line
        self.status_line.setGeometry(QtCore.QRect(124, 510, 501, 21))
        self.status_line.setObjectName("status_line")

        self.google_line = QtWidgets.QLineEdit(self.centralwidget)              # Yandex and google token lines
        self.google_line.setGeometry(QtCore.QRect(125, 60, 511, 20))
        self.google_line.setObjectName("google_line")
        self.yandex_line = QtWidgets.QLineEdit(self.centralwidget)
        self.yandex_line.setGeometry(QtCore.QRect(125, 30, 511, 20))
        self.yandex_line.setObjectName("yandex_line")

        self.lineEdit_1 = QtWidgets.QLineEdit(self.centralwidget)               # Input lines
        self.lineEdit_1.setGeometry(QtCore.QRect(126, 125, 113, 20))
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(125, 159, 113, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(125, 213, 113, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_4.setGeometry(QtCore.QRect(125, 241, 113, 20))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_5 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_5.setGeometry(QtCore.QRect(125, 269, 113, 20))
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.lineEdit_6 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_6.setGeometry(QtCore.QRect(125, 323, 113, 20))
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_7 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_7.setGeometry(QtCore.QRect(125, 349, 113, 20))
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.lineEdit_8 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_8.setGeometry(QtCore.QRect(125, 403, 113, 20))
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.lineEdit_9 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_9.setGeometry(QtCore.QRect(125, 433, 113, 20))
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.lineEdit_10 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_10.setGeometry(QtCore.QRect(125, 464, 113, 20))
        self.lineEdit_10.setObjectName("lineEdit_10")

        self.label = QtWidgets.QLabel(self.centralwidget)               # Texts
        self.label.setGeometry(QtCore.QRect(82, 127, 29, 13))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 160, 111, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(82, 323, 30, 13))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 270, 111, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(15, 62, 110, 13))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(15, 32, 110, 13))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(20, 350, 111, 16))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(665, 50, 149, 13))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(82, 215, 29, 13))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(50, 243, 64, 13))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(50, 435, 65, 13))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(82, 405, 30, 13))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(20, 465, 111, 16))
        self.label_13.setObjectName("label_13")
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(650, 149, 134, 13))
        self.label_15.setObjectName("label_15")
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setGeometry(QtCore.QRect(650, 243, 132, 13))
        self.label_16.setObjectName("label_16")
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setGeometry(QtCore.QRect(650, 340, 135, 13))
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        self.label_18.setGeometry(QtCore.QRect(650, 434, 133, 13))
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(self.centralwidget)
        self.label_19.setGeometry(QtCore.QRect(85, 511, 51, 16))
        self.label_19.setObjectName("label_19")

        self.line = QtWidgets.QFrame(self.centralwidget)                        # Delimiter lines
        self.line.setGeometry(QtCore.QRect(-5, 90, 921, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(-5, 188, 961, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(-45, 298, 991, 20))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(-15, 378, 951, 20))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setGeometry(QtCore.QRect(-20, 490, 921, 16))
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")

        font = QtGui.QFont()
        font.setFamily("Javanese Text")
        font.setPointSize(22)
        font.setBold(False)
        font.setWeight(50)
        self.label_14 = QtWidgets.QLabel(self.centralwidget)                    # Text symbol '}'
        self.label_14.setGeometry(QtCore.QRect(640, 20, 15, 66))
        self.label_14.setFont(font)
        self.label_14.setIndent(-1)
        self.label_14.setObjectName("label_14")

        window.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(window)
        self.statusbar.setObjectName("statusbar")
        window.setStatusBar(self.statusbar)

        self.retranslateUi(window)
        QtCore.QMetaObject.connectSlotsByName(window)

    def retranslateUi(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("window", "Downloader"))
        self.pushButton_1.setText(_translate("window", "Upload"))
        self.label.setText(_translate("window", "Vk id:"))
        self.label_3.setText(_translate("window", "Ok id:"))
        self.label_5.setText(_translate("window", "Google drive token:"))
        self.label_6.setText(_translate("window", "Yandex drive token:"))
        self.label_8.setText(_translate("window", "At least one should be added"))
        self.label_9.setText(_translate("window", "Vk id:"))
        self.label_10.setText(_translate("window", "Vk album id:"))
        self.label_11.setText(_translate("window", "Ok album id:"))
        self.label_12.setText(_translate("window", "Ok id:"))
        self.pushButton_2.setText(_translate("window", "Upload"))
        self.pushButton_3.setText(_translate("window", "Upload"))
        self.pushButton_4.setText(_translate("window", "Upload"))
        self.label_15.setText(_translate("window", "Upload Vk profile pictures"))
        self.label_16.setText(_translate("window", "Upload Vk album pictures"))
        self.label_17.setText(_translate("window", "Upload Ok profile pictures"))
        self.label_18.setText(_translate("window", "Upload Ok album pictures"))
        self.label_14.setText(_translate("window", "}"))
        self.label_2.setText(_translate("window", "Number of photos:"))
        self.label_4.setText(_translate("window", "Number of photos:"))
        self.label_7.setText(_translate("window", "Number of photos:"))
        self.label_13.setText(_translate("window", "Number of photos:"))
        self.label_19.setText(_translate("window", "Status:"))
