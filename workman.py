#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, mailer, auth

import smtplib
from email.header import Header

class Workman(QObject):
    def __init__(self, parent=None):
        super(Workman, self).__init__(parent)
        
        self.counter = 0
        self.er_email = False 

    finished = pyqtSignal()
    succeed = pyqtSignal()
    canceled = pyqtSignal()
    email_error = pyqtSignal()
    
    @pyqtSlot()
    def finish(self):
        self.finished.emit()
    
    @pyqtSlot()
    def cancel(self):
        self.canceled.emit()

    @pyqtSlot() 
    def process(self):
        while True:
            self.counter += 1
            if self.counter == 2:
                self.er_email = True
                break

            
            print "[+] Sending email... Attempts " + str(self.counter)

            code_number = auth.Auth.generateCodeNumber()
            msg = mailer.t_account_restore_password(
                    auth.Auth.getAccountCompanyName(), code_number)


            if self.send_email(auth.Auth.getAccountEmail(), "InterNotes - Changer votre mot de passe", 
                msg):

                print "[+] Successfully sent email."
                self.success_sent = True
                break

        if self.er_email == True:
            self.canceled.emit()
            self.email_error.emit()
            return
        elif self.success_sent == True:
            self.succeed.emit()
        self.finished.emit()



    def send_email(self, to, subject, msg):

        gmail_user = "matllesoftware@gmail.com"
        gmail_pwd = "matllesoftware"
        FROM = 'matllesoftware@gmail.com'
        TO = [str(to)] 
        SUBJECT = subject
        TEXT = msg 
    

        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

        try:
            #server = smtplib.SMTP(SERVER) 
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            #server.quit()
            server.close()
            return True
        except Exception as e:
            print 
            return False

