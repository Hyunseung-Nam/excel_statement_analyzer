# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowwmpxno.ui'
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
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(420, 400)
        MainWindow.setStyleSheet(u"background-color:white")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(12, 12, 12, 12)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 48))
        font = QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setStyleSheet(u"color: black;\n"
"border: 2px solid black;\n"
"border-radius: 10px;\n"
"padding: 5px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.btn_load_excel = QPushButton(self.centralwidget)
        self.btn_load_excel.setObjectName(u"btn_load_excel")
        self.btn_load_excel.setMinimumSize(QSize(0, 40))
        self.btn_load_excel.setStyleSheet(u"QPushButton{\n"
"    color: black;\n"
"    border: 2px solid black;\n"
"    padding: 5px;\n"
"}\n"
"QPushButton:hover{\n"
"    background-color: gray;\n"
"}")

        self.verticalLayout.addWidget(self.btn_load_excel)

        self.input_keyword = QLineEdit(self.centralwidget)
        self.input_keyword.setObjectName(u"input_keyword")
        self.input_keyword.setMinimumSize(QSize(0, 32))
        self.input_keyword.setStyleSheet(u"color: black;")

        self.verticalLayout.addWidget(self.input_keyword)

        self.btn_keyword_noraebang = QPushButton(self.centralwidget)
        self.btn_keyword_noraebang.setObjectName(u"btn_keyword_noraebang")
        self.btn_keyword_noraebang.setMinimumSize(QSize(0, 32))
        self.btn_keyword_noraebang.setStyleSheet(u"QPushButton{\n"
"    color: black;\n"
"    border: 1px solid black;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton:hover{\n"
"    background-color: lightgray;\n"
"}")

        self.verticalLayout.addWidget(self.btn_keyword_noraebang)

        self.btn_calculate = QPushButton(self.centralwidget)
        self.btn_calculate.setObjectName(u"btn_calculate")
        self.btn_calculate.setMinimumSize(QSize(0, 40))
        self.btn_calculate.setStyleSheet(u"QPushButton{\n"
"    color: black;\n"
"    border: 2px solid black;\n"
"    padding: 5px;\n"
"}\n"
"QPushButton:hover{\n"
"    background-color: gray;\n"
"}")

        self.verticalLayout.addWidget(self.btn_calculate)

        self.lbl_sum_result = QLabel(self.centralwidget)
        self.lbl_sum_result.setObjectName(u"lbl_sum_result")
        self.lbl_sum_result.setMinimumSize(QSize(0, 48))
        font1 = QFont()
        font1.setPointSize(12)
        self.lbl_sum_result.setFont(font1)
        self.lbl_sum_result.setStyleSheet(u"color: black;")
        self.lbl_sum_result.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.lbl_sum_result)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 420, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\uc5d1\uc140 \uba85\uc138\uc11c \uae08\uc561 \ud569\uc0b0\uae30", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\uc5d1\uc140 \uba85\uc138\uc11c \uae08\uc561 \ud569\uc0b0\uae30", None))
        self.btn_load_excel.setText(QCoreApplication.translate("MainWindow", u"\uc5d1\uc140 \ud30c\uc77c \ubd88\ub7ec\uc624\uae30", None))
        self.input_keyword.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\uac80\uc0c9\ud560 \uac00\ub9f9\uc810 \ud0a4\uc6cc\ub4dc\ub97c \uc785\ub825\ud558\uc138\uc694", None))
        self.btn_keyword_noraebang.setText(QCoreApplication.translate("MainWindow", u"\ub178\ub798\ubc29", None))
        self.btn_calculate.setText(QCoreApplication.translate("MainWindow", u"\ud569\uc0b0\ud558\uae30", None))
        self.lbl_sum_result.setText("")
    # retranslateUi

