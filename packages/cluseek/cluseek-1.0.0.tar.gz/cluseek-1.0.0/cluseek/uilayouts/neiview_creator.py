# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'neiview_creator.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_NeiviewCreator(object):
    def setupUi(self, NeiviewCreator):
        if not NeiviewCreator.objectName():
            NeiviewCreator.setObjectName(u"NeiviewCreator")
        NeiviewCreator.setEnabled(True)
        NeiviewCreator.resize(621, 574)
        self.gridLayout = QGridLayout(NeiviewCreator)
        self.gridLayout.setObjectName(u"gridLayout")
        self.clus_local_evalue_input = QLineEdit(NeiviewCreator)
        self.clus_local_evalue_input.setObjectName(u"clus_local_evalue_input")

        self.gridLayout.addWidget(self.clus_local_evalue_input, 8, 4, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(22, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 16, 6, 2, 1)

        self.clus_local_evalue_label = QLabel(NeiviewCreator)
        self.clus_local_evalue_label.setObjectName(u"clus_local_evalue_label")
        self.clus_local_evalue_label.setWordWrap(True)

        self.gridLayout.addWidget(self.clus_local_evalue_label, 8, 0, 1, 4)

        self.line = QFrame(NeiviewCreator)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 15, 0, 1, 6)

        self.nneighborhoods_displaylabel = QLabel(NeiviewCreator)
        self.nneighborhoods_displaylabel.setObjectName(u"nneighborhoods_displaylabel")

        self.gridLayout.addWidget(self.nneighborhoods_displaylabel, 1, 4, 1, 1)

        self.nneighborhoods_label = QLabel(NeiviewCreator)
        self.nneighborhoods_label.setObjectName(u"nneighborhoods_label")

        self.gridLayout.addWidget(self.nneighborhoods_label, 1, 0, 1, 2)

        self.line_3 = QFrame(NeiviewCreator)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_3, 3, 0, 1, 6)

        self.clus_local_pidentity_label = QLabel(NeiviewCreator)
        self.clus_local_pidentity_label.setObjectName(u"clus_local_pidentity_label")
        self.clus_local_pidentity_label.setWordWrap(True)

        self.gridLayout.addWidget(self.clus_local_pidentity_label, 6, 0, 2, 4)

        self.spcr2 = QSpacerItem(91, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.spcr2, 17, 1, 1, 4)

        self.cancel_btn = QPushButton(NeiviewCreator)
        self.cancel_btn.setObjectName(u"cancel_btn")

        self.gridLayout.addWidget(self.cancel_btn, 16, 0, 2, 1)

        self.create_btn = QPushButton(NeiviewCreator)
        self.create_btn.setObjectName(u"create_btn")

        self.gridLayout.addWidget(self.create_btn, 16, 5, 2, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.border_label = QLabel(NeiviewCreator)
        self.border_label.setObjectName(u"border_label")
        self.border_label.setWordWrap(False)

        self.horizontalLayout_3.addWidget(self.border_label)

        self.border_spin = QSpinBox(NeiviewCreator)
        self.border_spin.setObjectName(u"border_spin")
        self.border_spin.setMaximum(999999999)
        self.border_spin.setValue(75000)

        self.horizontalLayout_3.addWidget(self.border_spin)

        self.label_4 = QLabel(NeiviewCreator)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_3.addWidget(self.label_4)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)


        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 6)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 9, 6, 1, 1)

        self.title_label = QLabel(NeiviewCreator)
        self.title_label.setObjectName(u"title_label")

        self.gridLayout.addWidget(self.title_label, 0, 0, 1, 3)

        self.horizontalSpacer_2 = QSpacerItem(115, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 7, 5, 1, 1)

        self.clus_local_pidentity_spin = QSpinBox(NeiviewCreator)
        self.clus_local_pidentity_spin.setObjectName(u"clus_local_pidentity_spin")
        self.clus_local_pidentity_spin.setMinimum(0)
        self.clus_local_pidentity_spin.setMaximum(100)
        self.clus_local_pidentity_spin.setValue(0)

        self.gridLayout.addWidget(self.clus_local_pidentity_spin, 6, 4, 2, 1)

        self.clus_global_identity_spin = QSpinBox(NeiviewCreator)
        self.clus_global_identity_spin.setObjectName(u"clus_global_identity_spin")
        self.clus_global_identity_spin.setMinimum(50)
        self.clus_global_identity_spin.setMaximum(100)

        self.gridLayout.addWidget(self.clus_global_identity_spin, 5, 4, 1, 1)

        self.line_4 = QFrame(NeiviewCreator)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_4, 10, 0, 1, 6)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 18, 5, 1, 1)

        self.clus_global_identity_label = QLabel(NeiviewCreator)
        self.clus_global_identity_label.setObjectName(u"clus_global_identity_label")
        self.clus_global_identity_label.setWordWrap(True)

        self.gridLayout.addWidget(self.clus_global_identity_label, 5, 0, 1, 4)

        self.chk_highlight_markers = QCheckBox(NeiviewCreator)
        self.chk_highlight_markers.setObjectName(u"chk_highlight_markers")
        self.chk_highlight_markers.setChecked(True)

        self.gridLayout.addWidget(self.chk_highlight_markers, 12, 0, 1, 6)

        self.label = QLabel(NeiviewCreator)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)

        self.label_2 = QLabel(NeiviewCreator)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 11, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.chk_gray_out_rare = QCheckBox(NeiviewCreator)
        self.chk_gray_out_rare.setObjectName(u"chk_gray_out_rare")
        self.chk_gray_out_rare.setChecked(True)

        self.horizontalLayout.addWidget(self.chk_gray_out_rare)

        self.spin_gray_out_rare_threshold = QSpinBox(NeiviewCreator)
        self.spin_gray_out_rare_threshold.setObjectName(u"spin_gray_out_rare_threshold")
        self.spin_gray_out_rare_threshold.setMaximumSize(QSize(50, 16777215))
        self.spin_gray_out_rare_threshold.setMaximum(99)
        self.spin_gray_out_rare_threshold.setValue(25)

        self.horizontalLayout.addWidget(self.spin_gray_out_rare_threshold)

        self.label_3 = QLabel(NeiviewCreator)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)


        self.gridLayout.addLayout(self.horizontalLayout, 14, 0, 1, 6)

        self.chk_black_out_singletons = QCheckBox(NeiviewCreator)
        self.chk_black_out_singletons.setObjectName(u"chk_black_out_singletons")
        self.chk_black_out_singletons.setChecked(True)

        self.gridLayout.addWidget(self.chk_black_out_singletons, 13, 0, 1, 6)


        self.retranslateUi(NeiviewCreator)

        QMetaObject.connectSlotsByName(NeiviewCreator)
    # setupUi

    def retranslateUi(self, NeiviewCreator):
        NeiviewCreator.setWindowTitle(QCoreApplication.translate("NeiviewCreator", u"Form", None))
        self.clus_local_evalue_input.setText(QCoreApplication.translate("NeiviewCreator", u"1.e-10", None))
        self.clus_local_evalue_label.setText(QCoreApplication.translate("NeiviewCreator", u"Local alignment E-value threshold", None))
        self.nneighborhoods_displaylabel.setText(QCoreApplication.translate("NeiviewCreator", u"Error", None))
        self.nneighborhoods_label.setText(QCoreApplication.translate("NeiviewCreator", u"Neighborhoods to display:", None))
        self.clus_local_pidentity_label.setText(QCoreApplication.translate("NeiviewCreator", u"Local alignment identity threshold", None))
        self.cancel_btn.setText(QCoreApplication.translate("NeiviewCreator", u"Cancel", None))
        self.create_btn.setText(QCoreApplication.translate("NeiviewCreator", u"Create", None))
        self.border_label.setText(QCoreApplication.translate("NeiviewCreator", u"View an additional", None))
        self.border_spin.setSuffix(QCoreApplication.translate("NeiviewCreator", u" bp", None))
        self.label_4.setText(QCoreApplication.translate("NeiviewCreator", u"on either side of each target region", None))
        self.title_label.setText(QCoreApplication.translate("NeiviewCreator", u"<html><head/><body><p><span style=\" font-weight:600;\">General</span></p></body></html>", None))
        self.clus_local_pidentity_spin.setSuffix(QCoreApplication.translate("NeiviewCreator", u"%", None))
        self.clus_global_identity_spin.setSuffix(QCoreApplication.translate("NeiviewCreator", u"%", None))
        self.clus_global_identity_label.setText(QCoreApplication.translate("NeiviewCreator", u"Global alignment identity threshold", None))
        self.chk_highlight_markers.setText(QCoreApplication.translate("NeiviewCreator", u"Highlight marker proteins", None))
        self.label.setText(QCoreApplication.translate("NeiviewCreator", u"<html><head/><body><p><span style=\" font-weight:600;\">Protein clustering criteria</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("NeiviewCreator", u"<html><head/><body><p><span style=\" font-weight:600;\">Automatic highlighting</span></p></body></html>", None))
        self.chk_gray_out_rare.setText(QCoreApplication.translate("NeiviewCreator", u"Color protein groups present in less than", None))
        self.spin_gray_out_rare_threshold.setSuffix(QCoreApplication.translate("NeiviewCreator", u"%", None))
        self.label_3.setText(QCoreApplication.translate("NeiviewCreator", u"of regions light gray", None))
        self.chk_black_out_singletons.setText(QCoreApplication.translate("NeiviewCreator", u"Color singleton protein groups dark gray", None))
    # retranslateUi

