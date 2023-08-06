# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'graphframe.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_GraphFrame(object):
    def setupUi(self, GraphFrame):
        if not GraphFrame.objectName():
            GraphFrame.setObjectName(u"GraphFrame")
        GraphFrame.resize(715, 554)
        self.gridLayout = QGridLayout(GraphFrame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btn_loglin = QPushButton(GraphFrame)
        self.btn_loglin.setObjectName(u"btn_loglin")

        self.gridLayout.addWidget(self.btn_loglin, 1, 5, 1, 1)

        self.le_min = QLineEdit(GraphFrame)
        self.le_min.setObjectName(u"le_min")

        self.gridLayout.addWidget(self.le_min, 3, 2, 1, 1)

        self.spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.spacer2, 3, 0, 1, 1)

        self.lbl_variable = QLabel(GraphFrame)
        self.lbl_variable.setObjectName(u"lbl_variable")

        self.gridLayout.addWidget(self.lbl_variable, 1, 1, 1, 1)

        self.le_max = QLineEdit(GraphFrame)
        self.le_max.setObjectName(u"le_max")

        self.gridLayout.addWidget(self.le_max, 3, 5, 1, 1)

        self.lbl_scale = QLabel(GraphFrame)
        self.lbl_scale.setObjectName(u"lbl_scale")

        self.gridLayout.addWidget(self.lbl_scale, 1, 3, 1, 1)

        self.spacer3 = QSpacerItem(20, 13, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.spacer3, 2, 2, 1, 1)

        self.btn_wiperule = QPushButton(GraphFrame)
        self.btn_wiperule.setObjectName(u"btn_wiperule")

        self.gridLayout.addWidget(self.btn_wiperule, 3, 7, 1, 1)

        self.lbl_min = QLabel(GraphFrame)
        self.lbl_min.setObjectName(u"lbl_min")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_min.sizePolicy().hasHeightForWidth())
        self.lbl_min.setSizePolicy(sizePolicy)
        self.lbl_min.setMinimumSize(QSize(31, 21))
        self.lbl_min.setMaximumSize(QSize(31, 21))

        self.gridLayout.addWidget(self.lbl_min, 3, 1, 1, 1)

        self.btn_variable = QPushButton(GraphFrame)
        self.btn_variable.setObjectName(u"btn_variable")

        self.gridLayout.addWidget(self.btn_variable, 1, 2, 1, 1)

        self.btn_addrule = QPushButton(GraphFrame)
        self.btn_addrule.setObjectName(u"btn_addrule")

        self.gridLayout.addWidget(self.btn_addrule, 3, 6, 1, 1)

        self.lbl_max = QLabel(GraphFrame)
        self.lbl_max.setObjectName(u"lbl_max")
        sizePolicy.setHeightForWidth(self.lbl_max.sizePolicy().hasHeightForWidth())
        self.lbl_max.setSizePolicy(sizePolicy)
        self.lbl_max.setMinimumSize(QSize(31, 21))
        self.lbl_max.setMaximumSize(QSize(31, 21))

        self.gridLayout.addWidget(self.lbl_max, 3, 3, 1, 1)

        self.spacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.spacer1, 3, 8, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 9, 1, 1)

        self.graphcontainer = QWidget(GraphFrame)
        self.graphcontainer.setObjectName(u"graphcontainer")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.graphcontainer.sizePolicy().hasHeightForWidth())
        self.graphcontainer.setSizePolicy(sizePolicy1)
        self.lay_graphcontainer = QVBoxLayout(self.graphcontainer)
        self.lay_graphcontainer.setSpacing(0)
        self.lay_graphcontainer.setObjectName(u"lay_graphcontainer")
        self.lay_graphcontainer.setContentsMargins(0, 0, 0, -1)

        self.gridLayout.addWidget(self.graphcontainer, 0, 0, 1, 10)

        self.save_graph_btn = QPushButton(GraphFrame)
        self.save_graph_btn.setObjectName(u"save_graph_btn")

        self.gridLayout.addWidget(self.save_graph_btn, 1, 7, 1, 1)


        self.retranslateUi(GraphFrame)

        QMetaObject.connectSlotsByName(GraphFrame)
    # setupUi

    def retranslateUi(self, GraphFrame):
        GraphFrame.setWindowTitle(QCoreApplication.translate("GraphFrame", u"Form", None))
        self.btn_loglin.setText(QCoreApplication.translate("GraphFrame", u"Log/Lin", None))
        self.lbl_variable.setText(QCoreApplication.translate("GraphFrame", u"Variable:", None))
        self.lbl_scale.setText(QCoreApplication.translate("GraphFrame", u"Y Scale:", None))
        self.btn_wiperule.setText(QCoreApplication.translate("GraphFrame", u"Forget", None))
        self.lbl_min.setText(QCoreApplication.translate("GraphFrame", u"Min:", None))
        self.btn_variable.setText(QCoreApplication.translate("GraphFrame", u"Variable", None))
        self.btn_addrule.setText(QCoreApplication.translate("GraphFrame", u"Save", None))
        self.lbl_max.setText(QCoreApplication.translate("GraphFrame", u"Max:", None))
        self.save_graph_btn.setText(QCoreApplication.translate("GraphFrame", u"Save Graph", None))
    # retranslateUi

