# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'topclusters.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_TopClusters(object):
    def setupUi(self, TopClusters):
        if not TopClusters.objectName():
            TopClusters.setObjectName(u"TopClusters")
        TopClusters.resize(875, 587)
        self.gridLayout = QGridLayout(TopClusters)
        self.gridLayout.setObjectName(u"gridLayout")
        self.selection_scrollable = QScrollArea(TopClusters)
        self.selection_scrollable.setObjectName(u"selection_scrollable")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selection_scrollable.sizePolicy().hasHeightForWidth())
        self.selection_scrollable.setSizePolicy(sizePolicy)
        self.selection_scrollable.setMinimumSize(QSize(100, 0))
        self.selection_scrollable.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.selection_scrollable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selection_scrollable.setWidgetResizable(True)
        self.selection_scrollable_lay = QWidget()
        self.selection_scrollable_lay.setObjectName(u"selection_scrollable_lay")
        self.selection_scrollable_lay.setGeometry(QRect(0, 0, 98, 538))
        self.gridLayout_2 = QGridLayout(self.selection_scrollable_lay)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.selected_widget = QWidget(self.selection_scrollable_lay)
        self.selected_widget.setObjectName(u"selected_widget")
        self.selected_lay = QVBoxLayout(self.selected_widget)
        self.selected_lay.setObjectName(u"selected_lay")
        self.label = QLabel(self.selected_widget)
        self.label.setObjectName(u"label")

        self.selected_lay.addWidget(self.label)


        self.gridLayout_2.addWidget(self.selected_widget, 0, 0, 1, 1)

        self.selection_scrollable.setWidget(self.selection_scrollable_lay)

        self.gridLayout.addWidget(self.selection_scrollable, 0, 1, 1, 1)

        self.clear_btn = QPushButton(TopClusters)
        self.clear_btn.setObjectName(u"clear_btn")

        self.gridLayout.addWidget(self.clear_btn, 1, 1, 1, 1)

        self.cluster_table = QTableWidget(TopClusters)
        self.cluster_table.setObjectName(u"cluster_table")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cluster_table.sizePolicy().hasHeightForWidth())
        self.cluster_table.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.cluster_table, 0, 0, 2, 1)


        self.retranslateUi(TopClusters)

        QMetaObject.connectSlotsByName(TopClusters)
    # setupUi

    def retranslateUi(self, TopClusters):
        TopClusters.setWindowTitle(QCoreApplication.translate("TopClusters", u"Form", None))
        self.label.setText(QCoreApplication.translate("TopClusters", u"Selection:", None))
        self.clear_btn.setText(QCoreApplication.translate("TopClusters", u"Clear Selection", None))
    # retranslateUi

