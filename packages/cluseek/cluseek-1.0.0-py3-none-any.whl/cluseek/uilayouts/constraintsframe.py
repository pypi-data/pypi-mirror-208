# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'constraintsframe.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ConstraintsFrame(object):
    def setupUi(self, ConstraintsFrame):
        if not ConstraintsFrame.objectName():
            ConstraintsFrame.setObjectName(u"ConstraintsFrame")
        ConstraintsFrame.resize(1000, 700)
        ConstraintsFrame.setMinimumSize(QSize(1000, 700))
        self.gridLayout_3 = QGridLayout(ConstraintsFrame)
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(3, -1, 3, 5)
        self.accset_container = QWidget(ConstraintsFrame)
        self.accset_container.setObjectName(u"accset_container")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accset_container.sizePolicy().hasHeightForWidth())
        self.accset_container.setSizePolicy(sizePolicy)
        self.accset_container.setMinimumSize(QSize(290, 0))
        self.accset_container.setMaximumSize(QSize(340, 16777215))
        self.gridLayout = QGridLayout(self.accset_container)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(3, 2, 2, 2)
        self.chk_only_longest_per_taxon = QCheckBox(self.accset_container)
        self.chk_only_longest_per_taxon.setObjectName(u"chk_only_longest_per_taxon")

        self.gridLayout.addWidget(self.chk_only_longest_per_taxon, 2, 0, 1, 1)

        self.scrl_accsets = QScrollArea(self.accset_container)
        self.scrl_accsets.setObjectName(u"scrl_accsets")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrl_accsets.sizePolicy().hasHeightForWidth())
        self.scrl_accsets.setSizePolicy(sizePolicy1)
        self.scrl_accsets.setMinimumSize(QSize(260, 0))
        self.scrl_accsets.setMaximumSize(QSize(16777215, 16777215))
        self.scrl_accsets.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrl_accsets.setWidgetResizable(True)
        self.accsets = QWidget()
        self.accsets.setObjectName(u"accsets")
        self.accsets.setGeometry(QRect(0, 0, 333, 521))
        self.lay_accsets = QFormLayout(self.accsets)
        self.lay_accsets.setObjectName(u"lay_accsets")
        self.lay_accsets.setHorizontalSpacing(1)
        self.lay_accsets.setVerticalSpacing(1)
        self.lay_accsets.setContentsMargins(3, 3, 3, 3)
        self.scrl_accsets.setWidget(self.accsets)

        self.gridLayout.addWidget(self.scrl_accsets, 1, 0, 1, 3)

        self.chk_only_one_wgs_run = QCheckBox(self.accset_container)
        self.chk_only_one_wgs_run.setObjectName(u"chk_only_one_wgs_run")
        self.chk_only_one_wgs_run.setChecked(True)

        self.gridLayout.addWidget(self.chk_only_one_wgs_run, 3, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(58, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 3, 1, 1, 1)

        self.btn_applyrules = QPushButton(self.accset_container)
        self.btn_applyrules.setObjectName(u"btn_applyrules")
        self.btn_applyrules.setMaximumSize(QSize(80, 30))

        self.gridLayout.addWidget(self.btn_applyrules, 3, 2, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.txt_maxspacing = QLabel(self.accset_container)
        self.txt_maxspacing.setObjectName(u"txt_maxspacing")

        self.gridLayout_2.addWidget(self.txt_maxspacing, 1, 0, 1, 1)

        self.minscore_spin = QSpinBox(self.accset_container)
        self.minscore_spin.setObjectName(u"minscore_spin")

        self.gridLayout_2.addWidget(self.minscore_spin, 4, 1, 1, 1)

        self.spin_maxdist = QSpinBox(self.accset_container)
        self.spin_maxdist.setObjectName(u"spin_maxdist")
        self.spin_maxdist.setMaximum(999999999)
        self.spin_maxdist.setSingleStep(1000)

        self.gridLayout_2.addWidget(self.spin_maxdist, 1, 1, 1, 1)

        self.minscore_infolabel = QLabel(self.accset_container)
        self.minscore_infolabel.setObjectName(u"minscore_infolabel")

        self.gridLayout_2.addWidget(self.minscore_infolabel, 4, 0, 1, 1)

        self.line = QFrame(self.accset_container)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 2, 0, 1, 2)

        self.easyscore_chk = QCheckBox(self.accset_container)
        self.easyscore_chk.setObjectName(u"easyscore_chk")
        self.easyscore_chk.setChecked(True)

        self.gridLayout_2.addWidget(self.easyscore_chk, 3, 0, 1, 2)


        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 3)

        self.line_3 = QFrame(self.accset_container)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_3, 4, 0, 1, 3)

        self.out_infolabel = QLabel(self.accset_container)
        self.out_infolabel.setObjectName(u"out_infolabel")
        self.out_infolabel.setWordWrap(True)

        self.gridLayout.addWidget(self.out_infolabel, 5, 0, 1, 2)

        self.btn_viewresults = QPushButton(self.accset_container)
        self.btn_viewresults.setObjectName(u"btn_viewresults")
        self.btn_viewresults.setEnabled(False)

        self.gridLayout.addWidget(self.btn_viewresults, 5, 2, 1, 1)


        self.gridLayout_3.addWidget(self.accset_container, 0, 0, 2, 1)

        self.contextdisplay = QWidget(ConstraintsFrame)
        self.contextdisplay.setObjectName(u"contextdisplay")
        self.contextdisplay.setMinimumSize(QSize(560, 480))
        self.lay_contextdisplay = QVBoxLayout(self.contextdisplay)
        self.lay_contextdisplay.setSpacing(0)
        self.lay_contextdisplay.setObjectName(u"lay_contextdisplay")
        self.lay_contextdisplay.setContentsMargins(0, 0, 0, 0)

        self.gridLayout_3.addWidget(self.contextdisplay, 0, 2, 1, 2)

        self.blastresults = QWidget(ConstraintsFrame)
        self.blastresults.setObjectName(u"blastresults")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.blastresults.sizePolicy().hasHeightForWidth())
        self.blastresults.setSizePolicy(sizePolicy2)
        self.blastresults.setMinimumSize(QSize(0, 0))
        self.lay_blastresults = QVBoxLayout(self.blastresults)
        self.lay_blastresults.setSpacing(0)
        self.lay_blastresults.setObjectName(u"lay_blastresults")
        self.lay_blastresults.setContentsMargins(0, 0, 0, 0)

        self.gridLayout_3.addWidget(self.blastresults, 0, 4, 1, 1)

        self.horizontalSpacer = QSpacerItem(388, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 1, 2, 1, 1)

        self.btn_showneighbors = QPushButton(ConstraintsFrame)
        self.btn_showneighbors.setObjectName(u"btn_showneighbors")
        self.btn_showneighbors.setMinimumSize(QSize(180, 30))
        self.btn_showneighbors.setMaximumSize(QSize(80, 30))

        self.gridLayout_3.addWidget(self.btn_showneighbors, 1, 3, 1, 1)

        self.line_2 = QFrame(ConstraintsFrame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.line_2.setLineWidth(2)
        self.line_2.setMidLineWidth(0)
        self.line_2.setFrameShape(QFrame.VLine)

        self.gridLayout_3.addWidget(self.line_2, 0, 1, 2, 1)


        self.retranslateUi(ConstraintsFrame)

        QMetaObject.connectSlotsByName(ConstraintsFrame)
    # setupUi

    def retranslateUi(self, ConstraintsFrame):
        ConstraintsFrame.setWindowTitle(QCoreApplication.translate("ConstraintsFrame", u"Form", None))
#if QT_CONFIG(tooltip)
        self.chk_only_longest_per_taxon.setToolTip(QCoreApplication.translate("ConstraintsFrame", u"<html><head/><body><p>This option will cause the co-localization algorithm to only accept one region from each NCBI taxon. This is useful for limiting the volume of data.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chk_only_longest_per_taxon.setText(QCoreApplication.translate("ConstraintsFrame", u"Yield 1 region per taxon", None))
#if QT_CONFIG(tooltip)
        self.chk_only_one_wgs_run.setToolTip(QCoreApplication.translate("ConstraintsFrame", u"<html><head/><body><p>Select this if you are expecting multiple regions in each taxon, but still want to ensure that each found region is unique. EG, if a taxon has two gene clusters in its genome, the software should yield 2 regions from that taxon, even if each has been sequenced multiple times.</p><p><br/></p><p>The software will attempt to group found nucleotide sequences by the Whole Genome Sequencing (WGS) run they belong to, and will return only the run with the most found regions. If several runs have the same number of regions among their nucleotide sequences, it will only return the run with the longest (bp-wise) regions.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chk_only_one_wgs_run.setText(QCoreApplication.translate("ConstraintsFrame", u"Yield 1 WGS run per taxon", None))
        self.btn_applyrules.setText(QCoreApplication.translate("ConstraintsFrame", u"Search!", None))
        self.txt_maxspacing.setText(QCoreApplication.translate("ConstraintsFrame", u"Max target region size (bp):", None))
#if QT_CONFIG(tooltip)
        self.minscore_spin.setToolTip(QCoreApplication.translate("ConstraintsFrame", u"<html><head/><body><p>Only regions whose total score is at least equal to this value will be included in the results.</p><p>Each marker protein is only counted once, meaning that the maximum attainable score is the sum of all the positive scores of all the marker proteins.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.spin_maxdist.setToolTip(QCoreApplication.translate("ConstraintsFrame", u"<html><head/><body><p>The maximum distance between individual queries required to find a genetic cluster.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.minscore_infolabel.setText(QCoreApplication.translate("ConstraintsFrame", u"Minimum Score:", None))
        self.easyscore_chk.setText(QCoreApplication.translate("ConstraintsFrame", u"Simple Scoring (Search regions with ALL selected)", None))
        self.out_infolabel.setText(QCoreApplication.translate("ConstraintsFrame", u"No results yet! Select your marker proteins and press \"Search!\"", None))
        self.btn_viewresults.setText(QCoreApplication.translate("ConstraintsFrame", u"View", None))
        self.btn_showneighbors.setText(QCoreApplication.translate("ConstraintsFrame", u"Display Full Genetic Neighbourhood", None))
    # retranslateUi

