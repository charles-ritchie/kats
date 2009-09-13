# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/charles/Coding/Python/KAS/gallerydlg.ui'
#
# Created: Sat Sep 12 06:42:06 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_GalleryDlg(object):
    def setupUi(self, GalleryDlg):
        GalleryDlg.setObjectName("GalleryDlg")
        GalleryDlg.resize(422, 609)
        self.verticalLayout = QtGui.QVBoxLayout(GalleryDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtGui.QScrollArea(GalleryDlg)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 383, 549))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.selectAllPushButton = QtGui.QPushButton(GalleryDlg)
        self.selectAllPushButton.setObjectName("selectAllPushButton")
        self.horizontalLayout.addWidget(self.selectAllPushButton)
        self.selectNonePushButton = QtGui.QPushButton(GalleryDlg)
        self.selectNonePushButton.setObjectName("selectNonePushButton")
        self.horizontalLayout.addWidget(self.selectNonePushButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(GalleryDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(GalleryDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), GalleryDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), GalleryDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(GalleryDlg)

    def retranslateUi(self, GalleryDlg):
        GalleryDlg.setWindowTitle(QtGui.QApplication.translate("GalleryDlg", "KATS - Thumbnail Gallery", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllPushButton.setText(QtGui.QApplication.translate("GalleryDlg", "Select All", None, QtGui.QApplication.UnicodeUTF8))
        self.selectNonePushButton.setText(QtGui.QApplication.translate("GalleryDlg", "Select None", None, QtGui.QApplication.UnicodeUTF8))

