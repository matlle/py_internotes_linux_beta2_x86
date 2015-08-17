#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class PhotoPreview(QDialog):
    def __init__(self, pixmap, parent=None):
        super(PhotoPreview, self).__init__(parent)

        label_help_text = QLabel(u"Cliquer sur 'Ok' pour enregistrer ou 'Annuler' pour annuler.")
        label_photo_preview = QLabel()


        label_photo_preview.setPixmap(pixmap)

        self.btn_ok = QPushButton(u"Ok")
        self.btn_ok.setIcon(QIcon(u":/images/button_apply.png"))

        self.btn_cancel = QPushButton(u"Annuler")
        self.btn_cancel.setIcon(QIcon(":/images/button_cancel.png"))

        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_ok)
        layout_btn.addWidget(self.btn_cancel)
        layout_btn.setAlignment(Qt.AlignRight)

        layout_main = QVBoxLayout()
        layout_main.addWidget(label_help_text)
        layout_main.addWidget(label_photo_preview)
        layout_main.addLayout(layout_btn)

        self.setLayout(layout_main)
        self.setWindowTitle(u"Fichier image - InterNotes")
        self.resize(pixmap.width(), self.height())


        self.connect(self.btn_ok, SIGNAL('clicked()'), self.accept)
        self.connect(self.btn_cancel, SIGNAL('clicked()'), self.reject)




