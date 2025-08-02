# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'audio_visualizervdHahY.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTabWidget, QTextBrowser,
    QWidget)

from pyqtgraph import PlotWidget

class Ui_Wizualizator_audio(object):
    def setupUi(self, Wizualizator_audio):
        if not Wizualizator_audio.objectName():
            Wizualizator_audio.setObjectName(u"Wizualizator_audio")
        Wizualizator_audio.resize(1081, 711)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Wizualizator_audio.sizePolicy().hasHeightForWidth())
        Wizualizator_audio.setSizePolicy(sizePolicy)
        Wizualizator_audio.setAutoFillBackground(False)
        Wizualizator_audio.setTabShape(QTabWidget.TabShape.Rounded)
        self.Graph1 = QWidget(Wizualizator_audio)
        self.Graph1.setObjectName(u"Graph1")
        self.openFileBTN = QPushButton(self.Graph1)
        self.openFileBTN.setObjectName(u"openFileBTN")
        self.openFileBTN.setGeometry(QRect(0, 10, 181, 31))
        self.textBrowser = QTextBrowser(self.Graph1)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(190, 10, 221, 31))
        self.StartBTN = QPushButton(self.Graph1)
        self.StartBTN.setObjectName(u"StartBTN")
        self.StartBTN.setGeometry(QRect(640, 0, 75, 24))
        self.PRBTN = QPushButton(self.Graph1)
        self.PRBTN.setObjectName(u"PRBTN")
        self.PRBTN.setGeometry(QRect(720, 0, 75, 24))
        self.CancelBTN = QPushButton(self.Graph1)
        self.CancelBTN.setObjectName(u"CancelBTN")
        self.CancelBTN.setGeometry(QRect(800, 0, 75, 24))
        self.plotWidget = PlotWidget(self.Graph1)
        self.plotWidget.setObjectName(u"plotWidget")
        self.plotWidget.setGeometry(QRect(40, 150, 481, 471))
        Wizualizator_audio.setCentralWidget(self.Graph1)
        self.menubar = QMenuBar(Wizualizator_audio)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1081, 33))
        Wizualizator_audio.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Wizualizator_audio)
        self.statusbar.setObjectName(u"statusbar")
        Wizualizator_audio.setStatusBar(self.statusbar)

        self.retranslateUi(Wizualizator_audio)

        QMetaObject.connectSlotsByName(Wizualizator_audio)
    # setupUi

    def retranslateUi(self, Wizualizator_audio):
        Wizualizator_audio.setWindowTitle(QCoreApplication.translate("Wizualizator_audio", u"Wizualizator audio", None))
#if QT_CONFIG(tooltip)
        #Wizualizator_audio.setToolTip(QCoreApplication.translate("Wizualizator_audio", u"otwiera dialog pozwalaj\u0105cy na wybranie pliku audio", None))
#endif // QT_CONFIG(tooltip)
        self.openFileBTN.setText(QCoreApplication.translate("Wizualizator_audio", u"otw\u00f3rz plik audio", None))
        self.textBrowser.setHtml(QCoreApplication.translate("Wizualizator_audio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Otwarty plik: brak</p></body></html>", None))
        self.StartBTN.setText(QCoreApplication.translate("Wizualizator_audio", u"Start", None))
        self.PRBTN.setText(QCoreApplication.translate("Wizualizator_audio", u"Pauza", None))
        self.CancelBTN.setText(QCoreApplication.translate("Wizualizator_audio", u"Stop", None))
    # retranslateUi

