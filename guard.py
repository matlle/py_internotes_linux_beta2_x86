# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, hashlib, uuid, random, mailer, workman, keydialog
import sys, datetime




class Guard(QDialog):
    def __init__(self, parent=None):
        super(Guard, self).__init__(parent)

        self.trial_days = 15
        self.k_prod = u"BBBBBBBBBBBBBBBBBBBBBBBBB"
        self.activated_prod = False
        
        self.init()


    def closeEvent(self, event):
        self.reject()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass

    def shutdown(self):
        self.reject()
        sys.exit(0)


    def checkActivationKey(self):
        raw_key = self.active_dialog.key_code.text()
        key = self.active_dialog.key_code.text().replace("-", "")
        if key == self.k_prod:
            q_settings = QSettings("MATLLE", "InterNotes")

            q_settings.beginGroup("as")
        
            q_settings.setValue(u"s", 1)
            q_settings.setValue(u"k", raw_key)

            q_settings.endGroup()

            self.activated_prod = True

            QMessageBox.information(self.active_dialog, "Licence activé - InterNotes", 
                              u"Clé valide.\n" 
                              u"Le logiciel est maintenant activé!")

            self.active_dialog.close()
            self.close()
        else:
            QMessageBox.critical(self.active_dialog, u"Erreur d'activation - InterNotes",
                    u"Cette clé n'est pas valide. Veuillez réessayer.")


    def activeOkBtnActivation(self):
        if self.key_code.text().length() < 29:
            self.btn_ok.setEnabled(False)
        else:
            self.btn_ok.setEnabled(True)


    def enterKeyDialog(self, alone=False):
        self.active_dialog = keydialog.KeyDialog()

       
        #events
        if not alone:
            self.connect(self.active_dialog.btn_cancel, SIGNAL("clicked()"), self.active_dialog.reject)
        else:
            self.connect(self.active_dialog.btn_cancel, SIGNAL("clicked()"), self.shutdown)
        self.connect(self.active_dialog.btn_ok, SIGNAL("clicked()"), self.checkActivationKey)

        #self.connect(self.active_dialog.key_code, SIGNAL("cursorPositionChanged(int, int)"), 
        #        self.activeOkBtnActivation)


        if not alone:
           self.active_dialog.show()
        else:
           return self.active_dialog.exec_()



    
    def showRemainingTimeDialog(self, days):
        self.label_infos_time = QLabel(
            u"Il vous reste <strong>" + str(days) + "</strong> "
            u"jours avant la fin de la periode d'essai.<br/>"
            u"Pensez à activer le logiciel avec une clé valide.<br/><br/>"
            u"Ou contactez (<strong>MATLLE</strong>) le fabricant du produit<br/>"
            u"pour obtenir une clé d'activation:<br/><br/>"
            u"Email:  <strong>paso.175@gmail.com</strong><br/>"
            u"Tel:  <strong>(+225) 07 08 68 98</strong> / "
            u"      <strong> 41 87 07 68</strong>"
            )

        self.label_infos_time.setStyleSheet("font-size: 14px;")


        btn_key = QPushButton(u"Entrez la clé d'activation")
        btn_key.setIcon(QIcon(":/images/button_apply.png"))

        btn_cancel = QPushButton(u"Annuler")
        btn_cancel.setIcon(QIcon(":/images/editdelete.png"))


        layout_form = QFormLayout()
        layout_form.addRow(u"", self.label_infos_time)


        layout_btn = QHBoxLayout()
        layout_btn.addWidget(btn_key)
        layout_btn.addWidget(btn_cancel)
        layout_btn.setAlignment(Qt.AlignRight)



        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_form)
        layout_main.addLayout(layout_btn)

        self.setLayout(layout_main)
        self.resize(500, 100)
        self.setWindowTitle(u"Periode d'essai - InterNotes")

       
        #events
        self.connect(btn_cancel, SIGNAL("clicked()"), self.reject)
        self.connect(btn_key, SIGNAL("clicked()"), self.enterKeyDialog)


        return self.exec_()


    def isAppActived(self):
        q_settings = QSettings("MATLLE", "InterNotes")

        q_settings.beginGroup("as")
        
        state = q_settings.value(u"s", 0).toInt()[0]

        q_settings.endGroup()

        if state == 0:
            return False
        elif state == 1:
            self.activated_prod = True
            return True


    def remainingTime(self):
        q_settings = QSettings("MATLLE", "InterNotes")

        q_settings.beginGroup("rt")

        first_time = q_settings.value(u"ft", u"").toDateTime()
        expired = q_settings.value(u"ended", 0).toInt()[0]
        
        q_settings.endGroup()

        if expired:
            return "expired"

        if not first_time:
            q_settings.setValue("ft", QDateTime.currentDateTime())
            return "first"
        else:
            first_time = first_time.toPyDateTime()
            if first_time > datetime.datetime.now():
                q_settings.setValue("ended", 1)
                return "expired"

            if first_time < datetime.datetime.now() - datetime.timedelta(
                           days=self.trial_days):

                q_settings.setValue("ended", 1)

                return "expired"
            else:
                elapsed = datetime.datetime.now() - first_time
                elapsed_days = elapsed.days
                remaining_days = self.trial_days - elapsed_days
                return remaining_days 
            
        





    def init(self):
        if self.isAppActived() == True:
            return
        re = self.remainingTime()
        if re == "expired":
            QMessageBox.critical(self, u"Licence d'évaluation expirée - InterNotes", 
                    u"Votre période d'essai InterNotes a expiré.\n"
                    u"Veuillez activé le logiciel avec une clé valide.\n\n"
                    u"Ou contactez le frabricant du logiciel (MATLLE) pour obtenir une clé d'activation:\n\n"
                    u"Email: paso.175@gmail.com\n"
                    u"Tel: (+225) 07 08 68 98 / 41 87 07 68"
                    )
            self.enterKeyDialog(alone=True)
        elif re == "first":
            return
        else:
            self.showRemainingTimeDialog(re)


