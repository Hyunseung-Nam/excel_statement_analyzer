# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowtVXHRl.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(384, 456)
        MainWindow.setStyleSheet(u"background-color:white")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 351, 51))
        font = QFont()
        font.setPointSize(15)
        font.setBold(False)
        self.label.setFont(font)
        self.label.setStyleSheet(u"color: black;              \n"
"border: 2px solid black;  \n"
"border-radius: 10px;      \n"
"padding: 5px;\n"
"")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_load_excel = QPushButton(self.centralwidget)
        self.btn_load_excel.setObjectName(u"btn_load_excel")
        self.btn_load_excel.setGeometry(QRect(50, 80, 281, 41))
        self.btn_load_excel.setStyleSheet(u"QPushButton{\n"
"	color: black;              \n"
"	border: 2px solid black;       \n"
"	padding: 5px;\n"
"}\n"
"QPushButton:hover{\n"
"	background-color:gray;\n"
"}")
        self.input_keyword = QLineEdit(self.centralwidget)
        self.input_keyword.setObjectName(u"input_keyword")
        self.input_keyword.setGeometry(QRect(50, 130, 281, 31))
        self.input_keyword.setStyleSheet(u"color: black;")
        self.btn_calculate = QPushButton(self.centralwidget)
        self.btn_calculate.setObjectName(u"btn_calculate")
        self.btn_calculate.setGeometry(QRect(70, 180, 241, 41))
        self.btn_calculate.setStyleSheet(u"QPushButton{\n"
"	color: black;              \n"
"	border: 2px solid black;  \n"
"	padding: 5px;   \n"
"}\n"
"QPushButton:hover{\n"
"	background-color:gray;\n"
"}")
        self.lbl_sum_result = QLabel(self.centralwidget)
        self.lbl_sum_result.setObjectName(u"lbl_sum_result")
        self.lbl_sum_result.setGeometry(QRect(70, 230, 241, 61))
        font1 = QFont()
        font1.setPointSize(12)
        self.lbl_sum_result.setFont(font1)
        self.lbl_sum_result.setStyleSheet(u"color:black;\n"
"")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 384, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\uc5d1\uc140 \uba85\uc138\uc11c \uae08\uc561 \ud569\uc0b0\uae30", None))
        self.btn_load_excel.setText(QCoreApplication.translate("MainWindow", u"\uc5d1\uc140 \ud30c\uc77c \ubd88\ub7ec\uc624\uae30", None))
        self.input_keyword.setText("")
        self.input_keyword.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\uac80\uc0c9\ud560 \uac00\ub9f9\uc810 \ud0a4\uc6cc\ub4dc\ub97c \uc785\ub825\ud558\uc138\uc694", None))
        self.btn_calculate.setText(QCoreApplication.translate("MainWindow", u"\ud569\uc0b0\ud558\uae30", None))
        self.lbl_sum_result.setText("")
    # retranslateUi

