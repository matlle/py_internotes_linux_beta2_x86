# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, hashlib, uuid, random, mailer, workman
import sys, datetime




class DbConfig(QDialog):
    def __init__(self, parent=None):
        super(DbConfig, self).__init__(parent)

        self.db_type = "QMYSQL" 
        self.db_host = u''
        self.db_name = u''
        self.db_username = u''
        self.db_password = u''
        self.db = None
        self.opened = False
        
        self.opened = self.init()



    
    def closeEvent(self, event):
       event.ignore() 

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass
    
    def stop(self):
        sys.exit(0)

    def setDbConnection(self):
        q_settings = QSettings("Matlle", "InterNotes")
        q_settings.beginGroup("db_config")

        q_settings.setValue("db_host", self.line_edit_db_host.text())
        q_settings.setValue("db_name", self.line_edit_db_name.text())
        q_settings.setValue("db_username", self.line_edit_db_username.text())
        q_settings.setValue("db_password", self.line_edit_db_password.text())

        q_settings.endGroup()
        

        QMessageBox.information(self.dialog, u"Redémarrage... - InterNotes", 
            u"InterNotes va maintenant être redémarré "
            u"pour prendre en compte les nouveaux "
            u"paramètres de connexion à la base de donnée.")


        self.dialog.close()
        QApplication.exit(tools.EXIT_CODE_REBOOT)


    

    def getDbConnection(self):
        if self.db is not None:
            return self.db
        else:
            self.db = QSqlDatabase.addDatabase(self.db_type)
            self.db.setHostName(self.db_host)
            self.db.setDatabaseName(self.db_name)
            self.db.setUserName(self.db_username)
            self.db.setPassword(self.db_password)

            return self.db




    def activeOkBtn(self):
        if self.line_edit_db_host.text().isEmpty() or \
           self.line_edit_db_name.text().isEmpty() or \
           self.line_edit_db_username.text().isEmpty():
            self.btn_ok.setEnabled(False)
        else:
            self.btn_ok.setEnabled(True)

    
    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            wid = child.widget()
            del wid
            #child.widget().deleteLater()

    
    def dbConfigDialog(self, parent=None, q=False):
        self.dialog = QDialog(parent)

        self.line_edit_db_host = QLineEdit(self.db_host) if self.db_host else QLineEdit()
        #self.line_edit_db_host.setInputMask("000.000.000.000;_")

        self.line_edit_db_name = QLineEdit(self.db_name) if self.db_name else QLineEdit()

        self.line_edit_db_username = QLineEdit(self.db_username) if self.db_username else QLineEdit()

        self.line_edit_db_password = QLineEdit(self.db_password) if self.db_password else QLineEdit()

        self.line_edit_db_password.setEchoMode(QLineEdit.PasswordEchoOnEdit)

       
        self.btn_ok = QPushButton(u"Ok")
        self.btn_ok.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_ok.setEnabled(False)

        if self.line_edit_db_host.text().isEmpty() and self.line_edit_db_name.text().isEmpty() \
                and self.line_edit_db_username.text().isEmpty() \
                and self.line_edit_db_password.text().isEmpty():

            self.btn_ok.setEnabled(False)

        self.btn_exit = QPushButton(u"Quitter")
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))

        layout_form = QFormLayout()
        layout_form.addRow(u"Addresse du serveur: ", self.line_edit_db_host)
        layout_form.addRow(u"Nom de la base de donnée: ", self.line_edit_db_name)
        layout_form.addRow(u"Nom d'utilisateur: ", self.line_edit_db_username)
        layout_form.addRow(u"Mot de passe: ", self.line_edit_db_password)

        group_form = QGroupBox(u"Configurez la base de donnée MySQL")
        group_form.setLayout(layout_form)


        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_ok)
        #if q == True:
        layout_btn.addWidget(self.btn_exit)
        layout_btn.setAlignment(Qt.AlignRight)




        if self.dialog.layout() is not None:
            self.clearLayout(self.dialog.layout())

            layout = self.layout()
            layout.addWidget(group_form)
            layout.addLayout(layout_btn)
        else:
            layout_main = QVBoxLayout()
            layout_main.addWidget(group_form)
            layout_main.addLayout(layout_btn)

            self.dialog.setLayout(layout_main)

        self.dialog.resize(600, 300)
        self.dialog.setWindowTitle(u"Configuration de la base de donnée - InterNotes")

       
        #events
        if q == True:
            self.connect(self.btn_exit, SIGNAL("clicked()"), self.dialog.reject)
        else:
            self.connect(self.btn_exit, SIGNAL("clicked()"), self.stop)

        self.connect(self.btn_ok, SIGNAL("clicked()"), self.setDbConnection)

        self.connect(self.line_edit_db_host, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtn)

        self.connect(self.line_edit_db_name, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtn)

        self.connect(self.line_edit_db_username, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtn)

        self.connect(self.line_edit_db_password, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtn)


        self.dialog.show()




    def init(self):
        #self.findDbSettings()

        q_settings = QSettings("Matlle", "InterNotes")

        q_settings.beginGroup("db_config")

        self.db_host = q_settings.value("db_host", u"127.0.0.1").toString()
        self.db_name = q_settings.value("db_name", u"internotes").toString()
        self.db_username = q_settings.value("db_username", u"root").toString()
        self.db_password = q_settings.value("db_password", u"").toString()

        q_settings.endGroup()

        self.db = self.getDbConnection()
        if not self.db.open():
            self.opened = False
            QMessageBox.critical(self, "Error - InterNotes",
                    u"InterNotes n'arrive pas à se connecter "
                    u"au serveur de basse de donnée MySQL. "
                    u"Assurez vous que les paramètres de "
                    u"connection à la base de donnée sont correctes "
                    u"et que le serveur a bien demarré.\n\n"
                    u"Cause de l'Erreur:\n"
                    u"%s" % self.db.lastError().text()
                    )

            self.dbConfigDialog()
            return self.opened

        else:
            self.opened = True
            return self.opened


