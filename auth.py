# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, hashlib, uuid, random, mailer, workman
import sys, datetime




class Auth(QDialog):
    def __init__(self, parent=None):
        super(Auth, self).__init__(parent)

        self.SALT = 'T14AmartaBATTLETanK200621512:13'
        self.connected_return_key = False
        self.bad_counter = 3
        self.init()


    def closeEvent(self, event):
        sys.exit(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass

    def shutdown(self):
        self.reject()
        sys.exit(0)

    def isAnyAccountExist(self):
        sql = "SELECT account_id FROM account"

        query = QSqlQuery(sql)
        if query.exec_():
            if query.size() >= 1:
                return True
            else:
                return False
        else:
            print "SQL Error!"

    def isEmailAddressValid(self, email):
        s = QString("\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}\\b")
        re = QRegExp(s, Qt.CaseInsensitive)
        return re.exactMatch(email)


    def createAccount(self):
        company_name = self.company_name.text()
        username = self.username.text()
        password1 = str(self.password.text())
        password2 = str(self.password2.text())
        email = self.email.text().replace(" ", "")


        if password1 != password2:
            QMessageBox.critical(self, "Error - InterNotes", "Les mots de passe doivent être identiques.\nVeuillez réessayer.")
            self.password.clear()
            self.password2.clear()
            return
        if not self.isEmailAddressValid(email):
            QMessageBox.critical(self, "Error - InterNotes", "Cette addresse email n'est pas valide.\nVeuillez réessayer.")
            return


        query = QSqlQuery()
        query.prepare("INSERT INTO account(\
                              account_company_name, \
                              account_username, \
                              account_password, \
                              account_email, \
                              account_created_at) \
                       VALUES( \
                              :company, \
                              :username, \
                              :password, \
                              :email, \
                              NOW() \
                              ) \
                     ")
        
        hashed_password = hashlib.sha512(password1 + self.SALT).hexdigest()

        query.bindValue(":company", company_name)
        query.bindValue(":username", username)
        query.bindValue(":password", hashed_password)
        query.bindValue(":email", email)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                    "Database Error: %s" % query.lastError().text())
        else:
            self.done(1)
            subject = "InterNotes - Votre compte a été activé"
            company = unicode(company_name)
            email = unicode(email)
            username = unicode(username)

            company = company.encode('utf-8')
            email = email.encode('utf-8')
            username = username.encode('utf-8')
            mailer.run_send_email(email, company, username, subject)


    def signin(self):
        login = self.login.text()
        account_email = ''
        account_username = ''
        account_password = ''

        query = QSqlQuery()

        query.prepare("SELECT account_password \
                       FROM account \
                       WHERE account_email = :email \
                       OR account_username = :username") 

        
        query.bindValue(":email", login)
        query.bindValue(":username", login)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                    "Database Error: %s" % query.lastError().text())
        else:
            record = query.record()
            if not record.isEmpty():
                while (query.next()):
                    account_password = query.value(
                            record.indexOf("account_password")).toString()


            password = self.password.text()
            password = unicode(password)
            password = password.encode('utf-8')

            hashed_password = hashlib.sha512(password + self.SALT).hexdigest()
            if hashed_password == account_password:
                self.bad_counter = 3
                self.done(1)
            else:
                self.bad_counter -= 1
                QMessageBox.critical(self, "Infos", "Email/Nom d'utilisateur et/ou mot de passe incorrect.\nEssai restant (%d)" % self.bad_counter)
                if self.bad_counter == 0:
                    self.password.clear()
                    sys.exit(0)
                else:
                    self.password.clear()

            #self.done(1)
    


    @staticmethod
    def getAccountEmail():
        account_email = ''

        sql = "SELECT account_email \
               FROM account"
        
        query = QSqlQuery(sql)

        if not query.exec_():
            #QMessageBox.critical(self, "Error - InterNotes",
            #        "Database Error: %s" % query.lastError().text())
            print "SQL Error!"
        else:
            record = query.record()
            if not record.isEmpty():
                while (query.next()):
                    account_email = query.value(
                            record.indexOf("account_email")).toString()

        account_email = unicode(account_email)
        account_email = account_email.encode('utf-8')
        return account_email



    @staticmethod
    def getAccountCompanyName():
        account_company_name = ''

        sql = "SELECT account_company_name \
               FROM account"
        
        query = QSqlQuery(sql)

        if not query.exec_():
            print "SQL Error!"
        else:
            record = query.record()
            if not record.isEmpty():
                while (query.next()):
                    account_company_name = query.value(
                            record.indexOf("account_company_name")).toString()

        account_company_name = unicode(account_company_name)
        account_company_name = account_company_name.encode('utf-8')
        return account_company_name
    



    @staticmethod
    def getAccountCodeNumber():
        account_code_number = 0 

        sql = "SELECT account_code_number, \
                      account_code_number_date \
               FROM account"
        
        query = QSqlQuery(sql)

        if not query.exec_():
            #QMessageBox.critical(self, "Error - InterNotes",
            #        "Database Error: %s" % query.lastError().text())
            print "SQL Error get!"
        else:
            record = query.record()
            if not record.isEmpty():
                while (query.next()):
                    account_code_number = query.value(
                            record.indexOf("account_code_number")).toString()

                    account_code_number_date = query.value(
                            record.indexOf("account_code_number_date")).toDateTime()

        account_code_number = unicode(account_code_number)
        account_code_number = account_code_number.encode('utf-8')

        if account_code_number and account_code_number_date:
            mins_5 = 300
            two_hours = 2 * (60 * 60)
            if account_code_number_date < datetime.datetime.now() - datetime.timedelta(
                                seconds=two_hours):
                return 0 
            else:
                return account_code_number
        else:
            return 0 



    @staticmethod
    def setAccountCodeNumber(email, code_number):

        query = QSqlQuery()
        query.prepare("UPDATE account \
                       SET account_code_number = :code, \
                           account_code_number_date = NOW(), \
                           account_updated_at = NOW() \
                       WHERE account_email = :email")
        
        query.bindValue(":code", code_number)
        query.bindValue(":email", email)

        if not query.exec_():
            #QMessageBox.critical(self, "Error - InterNotes",
            #        "Database Error: %s" % query.lastError().text())
            print "SQL Error set!"

    

    @staticmethod
    def generateCodeNumber():
        account_code_number = Auth.getAccountCodeNumber()
        if account_code_number == 0:
            list_numbers = random.sample(xrange(0, 9), 7)
            string_numbers = ''.join(str(e) for e in list_numbers)
            email = Auth.getAccountEmail()
            Auth.setAccountCodeNumber(email, string_numbers)
            return string_numbers
        else:
            return account_code_number


    def activeOkBtnRestorePassword(self):
        if self.line_edit_code.text().length() < 13: 
            self.btn_ok_rp.setEnabled(False)
        else:
            self.btn_ok_rp.setEnabled(True)


    def activeOkBtnNewPassword(self):
        if self.line_edit_new_password1.text().length() < 4 or \
           self.line_edit_new_password2.text().length() < 4: 
            self.btn_ok_np.setEnabled(False)
        else:
            self.btn_ok_np.setEnabled(True)


    def saveNewPassword(self):
        password1 = str(self.line_edit_new_password1.text())
        password2 = str(self.line_edit_new_password2.text())

        if password1 != password2:
            QMessageBox.critical(self, "Error - InterNotes", "Les mots de passe doivent être identiques.\nVeuillez réessayer.")
            self.line_edit_new_password1.clear()
            self.line_edit_new_password2.clear()
            return


        query = QSqlQuery()
        query.prepare("UPDATE account \
                       SET account_password = :password,\
                           account_updated_at = NOW() \
                       WHERE account_email = :email")
        
        hashed_password = hashlib.sha512(password1 + self.SALT).hexdigest()

        query.bindValue(":password", hashed_password)
        query.bindValue(":email", Auth.getAccountEmail())

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                    "Database Error: %s" % query.lastError().text())
        else:
            self.np_dialog.done(1)
            QMessageBox.information(self, "Mot de passe changé - InterNotes", 
                    u"Votre mot de passe a été réinitialisé avec succès!")




    def changePassword(self):
        self.np_dialog = QDialog(self) 

        label_info = QLabel(QString(u"<center>Choisissez un nouveau mot de passe.\n" \
                                     u"Il doit contenir au moins (4) quatres caractères."
                                     u"</center>"))

        self.line_edit_new_password1 = QLineEdit()
        self.line_edit_new_password2 = QLineEdit()

        self.line_edit_new_password1.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.line_edit_new_password2.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        layout_form = QFormLayout()
        layout_form.addRow("Nouveau mot de passe: ", self.line_edit_new_password1)
        layout_form.addRow("Confirmer le mot de passe: ", self.line_edit_new_password2)

        self.btn_ok_np = QPushButton(u"Ok")
        self.btn_ok_np.setEnabled(False)
        btn_cancel = QPushButton(u"Annuler")

        self.btn_ok_np.setIcon(QIcon(":/images/button_apply.png"))
        btn_cancel.setIcon(QIcon(":/images/editdelete.png"))

        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_ok_np)
        layout_btn.addWidget(btn_cancel)
        layout_btn.setAlignment(Qt.AlignRight)

        layout_main = QVBoxLayout()
        layout_main.addWidget(label_info)
        #layout_main.addSpacing(10)
        #layout_main.addWidget(self.line_edit_code)
        layout_main.addLayout(layout_form)
        layout_main.addSpacing(15)
        layout_main.addLayout(layout_btn)


        self.np_dialog.setWindowTitle(u"Choisissez un nouveau mot de passe - InterNotes")
        self.np_dialog.resize(60, 200)
        self.np_dialog.setLayout(layout_main)

        self.connect(self.btn_ok_np, SIGNAL("clicked()"), self.saveNewPassword)
        self.connect(btn_cancel, SIGNAL("clicked()"), self.np_dialog.reject)

        self.connect(self.line_edit_new_password1, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnNewPassword)

        self.connect(self.line_edit_new_password2, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnNewPassword)

        self.np_dialog.exec_()


    def checkCodeNumber(self):
        account_code_number = Auth.getAccountCodeNumber()
        user_given_code_number = self.line_edit_code.text()
        user_given_code_number = unicode(user_given_code_number)
        user_given_code_number = user_given_code_number.encode('utf-8')

        user_given_code_number = user_given_code_number.replace("-", "")

        if user_given_code_number != account_code_number:
            self.line_edit_code.clear()
            QMessageBox.critical(self, "Error - InterNotes", 
                    "Code incorrect. Veuillez réessayer.")
        else:
            #QMessageBox.information(self, "Infos - InterNotes", "Good code number!")
            self.line_edit_code.clear()
            self.rp_dialog.done(1)
            self.changePassword()




    def restore_password(self):
        self.rp_dialog = QDialog(self)
        self.rp_dialog.setWindowModality(Qt.WindowModal)
                            
        label_info = QLabel(u"Consultez votre courrier électronique.\n" \
                     u"Nous vous avons envoyé un message avec un code\n" \
                     u"de confirmation à sept (7) chiffres. Saisissez-le " \
                     u"ci-dessous\npour continuer la réinitialisation de " \
                     u"votre mot de passe.\n(NB: ce code n'est valide que" \
                     u" quelques heures seulement.)\n\n" \
                     u"Nous avons envoyé votre code " \
                     u"à :\n%s" % self.getAccountEmail())

        self.line_edit_code = QLineEdit()
        self.line_edit_code.setInputMask("9-9-9-9-9-9-9")


        self.btn_ok_rp = QPushButton(u"Ok")
        self.btn_ok_rp.setEnabled(False)
        btn_cancel = QPushButton(u"Annuler")

        self.btn_ok_rp.setIcon(QIcon(":/images/button_apply.png"))
        btn_cancel.setIcon(QIcon(":/images/editdelete.png"))

        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_ok_rp)
        layout_btn.addWidget(btn_cancel)
        layout_btn.setAlignment(Qt.AlignRight)

        layout_main = QVBoxLayout()
        layout_main.addWidget(label_info)
        layout_main.addSpacing(10)
        layout_main.addWidget(self.line_edit_code)
        layout_main.addSpacing(15)
        layout_main.addLayout(layout_btn)


        self.rp_dialog.setWindowTitle(u"Consulter votre courrier électronique - InterNotes")
        self.rp_dialog.resize(60, 200)
        self.rp_dialog.setLayout(layout_main)

        self.connect(self.btn_ok_rp, SIGNAL("clicked()"), self.checkCodeNumber)
        self.connect(btn_cancel, SIGNAL("clicked()"), self.rp_dialog.reject)

        self.connect(self.line_edit_code, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnRestorePassword)

        self.rp_dialog.exec_()


    def errorSendEmail(self):                        
        QMessageBox.critical(self, "Error - InterNotes", 
                "Echec d'envoie de l'email.\nVeuillez réssayer plus tard.")


    def restorePassword(self):
        reply_question = QMessageBox.question(self, 
                u"Mot de passe oublié - InterNotes",
                u"Avez vous une connexion internet active?\nPouvez vous envoyer et recevoir des données?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply_question == QMessageBox.No:
            return
        else:
            reply_email = QInputDialog.getText(
                    self, u"Mot de passe oublié - InterNotes",
                    u"L'addresse email du compte", QLineEdit.Normal)
            if reply_email[1] == False:
                return
            elif reply_email[1] == True:
                email_account = reply_email[0].replace(" ", "")
                if not email_account.isEmpty(): 
                    if self.isEmailAddressValid(email_account):
                        if email_account == self.getAccountEmail():

                            """progress_dialog = QProgressDialog(
                                self)


                            progress_dialog.setAutoReset(False)
                            progress_dialog.setWindowModality(Qt.WindowModal)
                            progress_dialog.setWindowTitle(u"Envoie d'email - InterNotes")
                            progress_dialog.resize(600, 100)
                            progress_dialog.show()"""

                            dialog = QDialog(self)
                            dialog.setWindowModality(Qt.WindowModal)
                            
                            label_info = QLabel(QString(u"<center>Veuillez patienter...</center>"), dialog)
                            mv = QMovie(u":/images/loading.gif")
                            mv.start()
                            label_loading = QLabel() 
                            label_loading.setAttribute(Qt.WA_NoSystemBackground)
                            label_loading.setMovie(mv)

                            btn_cancel = QPushButton(u"Annuler")
                            layout_btn = QHBoxLayout()
                            layout_btn.addWidget(btn_cancel)
                            layout_btn.setAlignment(Qt.AlignRight)

                            layout_main = QVBoxLayout()
                            layout_main.addWidget(label_info)
                            layout_main.addSpacing(10)
                            layout_main.addWidget(label_loading)
                            layout_main.addSpacing(10)
                            layout_main.addLayout(layout_btn)

                            layout_main.setSizeConstraint(QLayout.SetFixedSize)

                            dialog.setWindowTitle(u"Envoie d'email - InterNotes")
                            #dialog.resize(600, 100)
                            dialog.setLayout(layout_main)
                            

                            self.my_thread = QThread()
                            self.my_workman = workman.Workman()
                            self.my_workman.moveToThread(self.my_thread)

                            #self.connect(my_workman, SIGNAL(error(QString)), 
                            #         this, SLOT(errorString(QString)));

                            self.connect(self.my_thread, SIGNAL("started()"), self.my_workman, 
                                      SLOT("process()"))

                            self.connect(self.my_workman, SIGNAL("finished()"), self.my_thread, 
                                    SLOT("quit()"))

                            self.connect(self.my_workman, SIGNAL("canceled()"), self.my_thread, 
                                    SLOT("quit()"))

                            self.connect(btn_cancel, SIGNAL("clicked()"), 
                                    self.my_workman, SLOT("cancel()"))

                            self.connect(btn_cancel, SIGNAL("clicked()"), 
                                    dialog.reject)

                            self.connect(self.my_workman, SIGNAL("email_error()"), 
                                    self.errorSendEmail)

                            self.connect(self.my_workman, SIGNAL("canceled()"), 
                                    dialog.reject)

                            self.connect(self.my_workman, SIGNAL("succeed()"), 
                                    dialog.accept)

                            self.connect(self.my_workman, SIGNAL("finished()"), 
                                    self.restore_password)

                            self.connect(self.my_workman, SIGNAL("finished()"), self.my_workman, 
                                    SLOT("deleteLater()"))

                            self.connect(self.my_thread, SIGNAL("finished()"), self.my_thread, 
                                    SLOT("deleteLater()"))

                            self.my_thread.start()




                            #self.connect(dialog, SIGNAL("accepted()"), self.restore_password)





                            dialog.show()




                            #mailer.run_send_email_for_reset_password(dialog)

                        else:
                            QMessageBox.critical(
                              self, u"Mot de passe oublé - InterNotes",
                              u"Cette addresse email ne correspond pas à celle enregistrée\nlors de la création du compte.")
                    else:
                        QMessageBox.critical(self, u"Mot de passe oublié - InterNotes",
                                "Addresse email non valide.")
                else:
                    return



    def activeOkBtnSignup(self):
        if self.company_name.text().length() < 2 or \
           self.username.text().length() < 2 or \
           self.password.text().length() < 4 or \
           self.password2.text().length() < 4 or \
           self.email.text().isEmpty():
            self.btn_ok.setEnabled(False)
        else:
            self.btn_ok.setEnabled(True)

    def activeOkBtnSignin(self):
        if self.login.text().length() < 2 or \
                self.password.text().length() < 4:
            self.btn_ok.setEnabled(False)
            if self.connected_return_key:
                self.disconnect(self.login, SIGNAL("returnPressed()"), self.signin)
                self.disconnect(self.password, SIGNAL("returnPressed()"), self.signin)
                self.connected_return_key = False
        else:
            self.btn_ok.setEnabled(True)
            if not self.connected_return_key:
                self.connect(self.login, SIGNAL("returnPressed()"), self.signin)
                self.connect(self.password, SIGNAL("returnPressed()"), self.signin)
                self.connected_return_key = True


    def signupDialog(self):
        self.company_name = QLineEdit()
        self.email = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.password2 = QLineEdit()
        self.password2.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.email_tip = QLabel(u"* Veuillez entrer une addresse email valide.\nVous pourrez vous reconnecter avec cette addresse\net elle sera utilisée pour reinitialiser votre\nmot de passe en cas d'oubli.")
        self.email_tip.setStyleSheet("font-size: 14px;")
       
        self.btn_ok = QPushButton(u"Ok")
        self.btn_ok.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_ok.setEnabled(False)

        self.btn_exit = QPushButton(u"Quitter")
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))

        layout_form = QFormLayout()
        layout_form.addRow(u"Nom de l'établissement: ", self.company_name)
        layout_form.addRow(u"Nom d'utilisateur: ", self.username)
        layout_form.addRow(u"Mot de passe: ", self.password)
        layout_form.addRow(u"Confirmer le mot de passe: ", self.password2)
        layout_form.addRow(u"Email:* ", self.email)
        layout_form.addRow(u"   ", self.email_tip)

        group_form = QGroupBox(u"Créer un compte")
        group_form.setLayout(layout_form)


        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_ok)
        layout_btn.addWidget(self.btn_exit)
        layout_btn.setAlignment(Qt.AlignRight)



        layout_main = QVBoxLayout()
        layout_main.addWidget(group_form)
        layout_main.addLayout(layout_btn)

        self.setLayout(layout_main)
        self.resize(600, 300)
        self.setWindowTitle(u"Créer un compte - InterNotes")

       
        #events
        self.connect(self.btn_exit, SIGNAL("clicked()"), self.shutdown)
        self.connect(self.btn_ok, SIGNAL("clicked()"), self.createAccount)

        self.connect(self.company_name, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnSignup)

        self.connect(self.username, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnSignup)

        self.connect(self.password, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnSignup)

        self.connect(self.password2, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnSignup)

        self.connect(self.email, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnSignup)
        


        return self.exec_()



    
    def signinDialog(self):
        self.login = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        self.label_warning = QLabel(
            u"Après trois (3) essais incorrects,\nle logiciel s'arrêtra.")

        self.label_warning.setStyleSheet("font-size: 14px;")

        self.btn_password_forgot = QPushButton(u"Mot de passe oublié?")
        self.btn_password_forgot.setFlat(True)

        self.btn_ok = QPushButton(u"Ok")
        self.btn_ok.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_ok.setEnabled(False)

        self.btn_exit = QPushButton(u"Quitter")
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))


        layout_form = QFormLayout()
        layout_form.addRow(u"Email ou Nom d'utilisateur: ", self.login)
        layout_form.addRow(u"Mot de passe: ", self.password)
        layout_form.addRow(u"  ", self.label_warning)

        group_form = QGroupBox(u"Connexion")
        group_form.setLayout(layout_form)


        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_password_forgot)
        layout_btn.addWidget(self.btn_ok)
        layout_btn.addWidget(self.btn_exit)
        layout_btn.setAlignment(Qt.AlignRight)



        layout_main = QVBoxLayout()
        layout_main.addWidget(group_form)
        layout_main.addLayout(layout_btn)

        self.setLayout(layout_main)
        self.resize(500, 200)
        self.setWindowTitle(u"Connexion - InterNotes")

       
        #events
        self.connect(self.btn_exit, SIGNAL("clicked()"), self.shutdown)
        self.connect(self.btn_ok, SIGNAL("clicked()"), self.signin)
        self.connect(self.btn_password_forgot, SIGNAL("clicked()"), 
                self.restorePassword)

        self.connect(self.login, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnSignin)

        self.connect(self.password, SIGNAL("cursorPositionChanged(int, int)"), 
                self.activeOkBtnSignin)
        


        return self.exec_()




    def init(self):
        if self.isAnyAccountExist() == True:
            self.signinDialog()
        else:
            self.signupDialog()


