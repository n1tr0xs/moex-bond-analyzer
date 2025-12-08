# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QSizePolicy, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(255, 203)
        self.layoutWidget = QWidget(Widget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(1, 1, 252, 200))
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label)

        self.minBondYieldSpinBox = QDoubleSpinBox(self.layoutWidget)
        self.minBondYieldSpinBox.setObjectName(u"minBondYieldSpinBox")
        self.minBondYieldSpinBox.setMaximum(999999999.000000000000000)

        self.horizontalLayout_2.addWidget(self.minBondYieldSpinBox)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_1 = QLabel(self.layoutWidget)
        self.label_1.setObjectName(u"label_1")
        self.label_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_1.setWordWrap(False)

        self.verticalLayout_3.addWidget(self.label_1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.minDaysToMaturitySpinBox = QSpinBox(self.layoutWidget)
        self.minDaysToMaturitySpinBox.setObjectName(u"minDaysToMaturitySpinBox")
        self.minDaysToMaturitySpinBox.setMaximum(999999999)

        self.verticalLayout_2.addWidget(self.minDaysToMaturitySpinBox)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_3)

        self.maxDaysToMaturitySpinBox = QSpinBox(self.layoutWidget)
        self.maxDaysToMaturitySpinBox.setObjectName(u"maxDaysToMaturitySpinBox")
        self.maxDaysToMaturitySpinBox.setMaximum(999999999)

        self.verticalLayout.addWidget(self.maxDaysToMaturitySpinBox)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.buttonStart = QPushButton(self.layoutWidget)
        self.buttonStart.setObjectName(u"buttonStart")

        self.verticalLayout_4.addWidget(self.buttonStart)

        self.buttonShowFile = QPushButton(self.layoutWidget)
        self.buttonShowFile.setObjectName(u"buttonShowFile")
        self.buttonShowFile.setEnabled(False)

        self.verticalLayout_4.addWidget(self.buttonShowFile)

        self.progressBar = QProgressBar(self.layoutWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout_4.addWidget(self.progressBar)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"MOEX Bond Analyzer by n1tr0xs", None))
        self.label.setText(QCoreApplication.translate("Widget", u"\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0434\u043e\u0445\u043e\u0434\u043d\u043e\u0441\u0442\u044c", None))
        self.label_1.setText(QCoreApplication.translate("Widget", u"\u0414\u043d\u0435\u0439 \u0434\u043e \u043f\u043e\u0433\u0430\u0448\u0435\u043d\u0438\u044f", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"\u041c\u0438\u043d\u0438\u043c\u0443\u043c", None))
        self.label_3.setText(QCoreApplication.translate("Widget", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0443\u043c", None))
        self.buttonStart.setText(QCoreApplication.translate("Widget", u"\u0421\u0442\u0430\u0440\u0442", None))
        self.buttonShowFile.setText(QCoreApplication.translate("Widget", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0444\u0430\u0439\u043b", None))
    # retranslateUi

