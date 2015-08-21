#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools

class About(QDialog):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)

        self.init()
        
     
    def init(self):
        logo = QPixmap(":/images/banner.png")
        label_logo = QLabel()
        label_logo.setPixmap(logo)


        layout_head = QHBoxLayout()
        layout_head.addWidget(label_logo)


        logo_matlle = QPixmap(":/images/logomatllebanner.png")
        #logo_matlle.scaled(10, 10)
        label_logo_matlle = QLabel()
        label_logo_matlle.setPixmap(logo_matlle)
        

        page_about = QWidget()

        label_about = QLabel()
        label_about.setText(QString(
           u"<strong>InterNotes</strong>, logiciel conçu pour rendre simple et facile la gestion des bulletins de notes scolaires et universitaires<br/><br/> "
           u"<strong>Version 1.0.2 (Windows x86)</strong><br></br><br/><br/><br/>"
           u"Copyright © 2015 Matlle e.i. Tous droits reservés.<br/><br/><br/><br/><br/><br/><br/><br/>"
           u"<span style="">(+225) 07 08 68 98 / 41 87 07 68 / 01 58 03 30</span><br/>"
           u"matllesoftware@gmail.com"
           u"www.matlle.com"))

        label_about.setAlignment(Qt.AlignLeft)
        label_about.setWordWrap(True)

        layout_about = QHBoxLayout()
        layout_about.addWidget(label_about)
        page_about.setLayout(layout_about)


        page_licence = QWidget()

        label_licence = QLabel()
        label_licence.setText(QString(
            u"Licence d'utilisation"
            u""))
        label_licence.setAlignment(Qt.AlignLeft)
        label_licence.setWordWrap(True)

        layout_licence = QHBoxLayout()
        layout_licence.addWidget(label_licence)
        page_licence.setLayout(layout_licence)
        

        onglets = QTabWidget()
        onglets.addTab(page_about, "À propos")
        onglets.addTab(page_licence, "Licence")


        layout_body = QHBoxLayout()
        layout_body.addWidget(label_logo_matlle)
        layout_body.addWidget(onglets)


        self.btn_exit = QPushButton(u"Quitter")
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))



        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_exit)
        layout_btn.setAlignment(Qt.AlignRight)
        

        layout_main = QVBoxLayout()
        #layout_main.addWidget(group_year_and_class)
        layout_main.addLayout(layout_head)
        layout_main.addLayout(layout_body)
        #layout_main.addWidget(onglets)
        layout_main.addLayout(layout_btn)


        self.setLayout(layout_main)
        self.resize(600, 400)
        self.setWindowTitle(u"À propos d'InterNotes")
        


        self.connect(self.btn_exit, SIGNAL("clicked()"), 
                self.reject)

        return self.exec_()

     
