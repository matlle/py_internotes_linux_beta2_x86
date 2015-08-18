#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools

class KeyDialog(QDialog):
    def __init__(self, parent=None):
        super(KeyDialog, self).__init__(parent)

        self.init()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass


    def activeOkBtnActivation(self):
        if self.key_code.text().length() < 29:
            self.btn_ok.setEnabled(False)
        else:
            self.btn_ok.setEnabled(True)





    def init(self):
        #self.setWindowFlags(Qt.CustomizeWindowHint)

        self.setWindowModality(Qt.WindowModal)

        self.key_code = QLineEdit()
        self.key_code.setInputMask(">NNNNN-NNNNN-NNNNN-NNNNN-NNNNN;#")

       
        self.btn_ok = QPushButton(u"Ok")
        self.btn_ok.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_ok.setEnabled(False)

        self.btn_cancel = QPushButton(u"Cancel")
        self.btn_cancel.setIcon(QIcon(":/images/editdelete.png"))

        layout_form = QFormLayout()
        layout_form.addRow(u"Clé d'activation: ", self.key_code)

        group_form = QGroupBox(u"Entrez une clé d'activation")
        group_form.setLayout(layout_form)


        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_ok)
        layout_btn.addWidget(self.btn_cancel)
        layout_btn.setAlignment(Qt.AlignRight)


        layout_main = QVBoxLayout()
        layout_main.addWidget(group_form)
        layout_main.addLayout(layout_btn)

        self.setLayout(layout_main)
        self.resize(450, 100)

        self.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, 
            self.size(), qApp.desktop().availableGeometry()))

        self.setWindowTitle(u"Licence Activation - InterNotes")


        #events
        self.connect(self.key_code, SIGNAL("cursorPositionChanged(int, int)"),
                self.activeOkBtnActivation)

