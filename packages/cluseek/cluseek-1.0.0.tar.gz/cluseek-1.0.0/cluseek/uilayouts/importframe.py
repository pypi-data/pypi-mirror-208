# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'importframe.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ImportFrame(object):
    def setupUi(self, ImportFrame):
        if not ImportFrame.objectName():
            ImportFrame.setObjectName(u"ImportFrame")
        ImportFrame.resize(360, 262)
        self.gridLayout = QGridLayout(ImportFrame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.importFileStack_scrl = QScrollArea(ImportFrame)
        self.importFileStack_scrl.setObjectName(u"importFileStack_scrl")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.importFileStack_scrl.sizePolicy().hasHeightForWidth())
        self.importFileStack_scrl.setSizePolicy(sizePolicy)
        self.importFileStack_scrl.setMinimumSize(QSize(300, 180))
        self.importFileStack_scrl.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.importFileStack_scrl.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.importFileStack_scrl.setWidgetResizable(True)
        self.importFileStack = QWidget()
        self.importFileStack.setObjectName(u"importFileStack")
        self.importFileStack.setGeometry(QRect(0, 0, 340, 178))
        self.importFileStack.setMinimumSize(QSize(0, 0))
        self.lay_importFileStack = QVBoxLayout(self.importFileStack)
        self.lay_importFileStack.setSpacing(0)
        self.lay_importFileStack.setObjectName(u"lay_importFileStack")
        self.importFileStack_scrl.setWidget(self.importFileStack)

        self.gridLayout.addWidget(self.importFileStack_scrl, 0, 0, 1, 5)

        self.hspacer1_2 = QSpacerItem(42, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.hspacer1_2, 1, 0, 1, 1)

        self.btn_addFile = QPushButton(ImportFrame)
        self.btn_addFile.setObjectName(u"btn_addFile")

        self.gridLayout.addWidget(self.btn_addFile, 1, 1, 1, 1)

        self.hspacer1_1 = QSpacerItem(48, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.hspacer1_1, 1, 2, 1, 1)

        self.btn_loadFiles = QPushButton(ImportFrame)
        self.btn_loadFiles.setObjectName(u"btn_loadFiles")

        self.gridLayout.addWidget(self.btn_loadFiles, 1, 3, 1, 1)

        self.hspacer1_3 = QSpacerItem(41, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.hspacer1_3, 1, 4, 1, 1)

        self.frame_afterLoaded = QWidget(ImportFrame)
        self.frame_afterLoaded.setObjectName(u"frame_afterLoaded")
        self.lay_afterLoaded = QFormLayout(self.frame_afterLoaded)
        self.lay_afterLoaded.setObjectName(u"lay_afterLoaded")
        self.lay_afterLoaded.setHorizontalSpacing(6)
        self.lay_afterLoaded.setVerticalSpacing(6)
        self.lay_afterLoaded.setContentsMargins(0, 0, 0, 0)

        self.gridLayout.addWidget(self.frame_afterLoaded, 3, 0, 1, 1)

        self.blastconfig_btn = QPushButton(ImportFrame)
        self.blastconfig_btn.setObjectName(u"blastconfig_btn")

        self.gridLayout.addWidget(self.blastconfig_btn, 2, 2, 1, 1)


        self.retranslateUi(ImportFrame)

        QMetaObject.connectSlotsByName(ImportFrame)
    # setupUi

    def retranslateUi(self, ImportFrame):
        ImportFrame.setWindowTitle(QCoreApplication.translate("ImportFrame", u"Form", None))
        self.btn_addFile.setText(QCoreApplication.translate("ImportFrame", u"Add Input", None))
        self.btn_loadFiles.setText(QCoreApplication.translate("ImportFrame", u"Load Files", None))
        self.blastconfig_btn.setText(QCoreApplication.translate("ImportFrame", u"Remote BLAST Configuration", None))
    # retranslateUi

