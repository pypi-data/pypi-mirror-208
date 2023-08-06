# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'neiviewer.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_NeiViewer(object):
    def setupUi(self, NeiViewer):
        if not NeiViewer.objectName():
            NeiViewer.setObjectName(u"NeiViewer")
        NeiViewer.resize(1068, 459)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NeiViewer.sizePolicy().hasHeightForWidth())
        NeiViewer.setSizePolicy(sizePolicy)
        NeiViewer.setMinimumSize(QSize(100, 100))
        self.gridLayout = QGridLayout(NeiViewer)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.vertiscroll_scrl = QScrollArea(NeiViewer)
        self.vertiscroll_scrl.setObjectName(u"vertiscroll_scrl")
        self.vertiscroll_scrl.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.vertiscroll_scrl.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.vertiscroll_scrl.setWidgetResizable(True)
        self.vertiscroll = QWidget()
        self.vertiscroll.setObjectName(u"vertiscroll")
        self.vertiscroll.setGeometry(QRect(0, 0, 1049, 450))
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.vertiscroll.sizePolicy().hasHeightForWidth())
        self.vertiscroll.setSizePolicy(sizePolicy1)
        self.lay_vertiscroll = QGridLayout(self.vertiscroll)
        self.lay_vertiscroll.setSpacing(0)
        self.lay_vertiscroll.setObjectName(u"lay_vertiscroll")
        self.lay_vertiscroll.setContentsMargins(0, 0, 0, 0)
        self.histocontainer = QWidget(self.vertiscroll)
        self.histocontainer.setObjectName(u"histocontainer")
        self.l = QVBoxLayout(self.histocontainer)
        self.l.setSpacing(0)
        self.l.setObjectName(u"l")
        self.l.setContentsMargins(0, 0, 0, 0)

        self.lay_vertiscroll.addWidget(self.histocontainer, 0, 2, 1, 1)

        self.clustercontainer_scrl = QScrollArea(self.vertiscroll)
        self.clustercontainer_scrl.setObjectName(u"clustercontainer_scrl")
        self.clustercontainer_scrl.setMinimumSize(QSize(600, 450))
        self.clustercontainer_scrl.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.clustercontainer_scrl.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.clustercontainer_scrl.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.clustercontainer_scrl.setWidgetResizable(True)
        self.clustercontainer = QWidget()
        self.clustercontainer.setObjectName(u"clustercontainer")
        self.clustercontainer.setGeometry(QRect(0, 0, 1027, 431))
        self.lay_clustercontainer = QVBoxLayout(self.clustercontainer)
        self.lay_clustercontainer.setSpacing(0)
        self.lay_clustercontainer.setObjectName(u"lay_clustercontainer")
        self.lay_clustercontainer.setContentsMargins(0, 0, 0, 0)
        self.spcr_magspring = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.lay_clustercontainer.addItem(self.spcr_magspring)

        self.clustercontainer_scrl.setWidget(self.clustercontainer)

        self.lay_vertiscroll.addWidget(self.clustercontainer_scrl, 0, 1, 1, 1)

        self.headercontainer = QWidget(self.vertiscroll)
        self.headercontainer.setObjectName(u"headercontainer")
        self.headercontainer.setMinimumSize(QSize(20, 0))
        self.lay_headercontainer = QVBoxLayout(self.headercontainer)
        self.lay_headercontainer.setSpacing(0)
        self.lay_headercontainer.setObjectName(u"lay_headercontainer")
        self.lay_headercontainer.setContentsMargins(0, 1, 0, 17)

        self.lay_vertiscroll.addWidget(self.headercontainer, 0, 0, 1, 1)

        self.vertiscroll_scrl.setWidget(self.vertiscroll)

        self.gridLayout.addWidget(self.vertiscroll_scrl, 0, 0, 1, 1)

        self.hscrollbarcontainer = QWidget(NeiViewer)
        self.hscrollbarcontainer.setObjectName(u"hscrollbarcontainer")
        self.hscrollbarcontainer.setMinimumSize(QSize(0, 10))
        self.lay_hscrollbarcontainer = QHBoxLayout(self.hscrollbarcontainer)
        self.lay_hscrollbarcontainer.setSpacing(0)
        self.lay_hscrollbarcontainer.setObjectName(u"lay_hscrollbarcontainer")
        self.lay_hscrollbarcontainer.setContentsMargins(0, 0, 0, 0)

        self.gridLayout.addWidget(self.hscrollbarcontainer, 1, 0, 1, 1)


        self.retranslateUi(NeiViewer)

        QMetaObject.connectSlotsByName(NeiViewer)
    # setupUi

    def retranslateUi(self, NeiViewer):
        NeiViewer.setWindowTitle(QCoreApplication.translate("NeiViewer", u"Form", None))
    # retranslateUi

