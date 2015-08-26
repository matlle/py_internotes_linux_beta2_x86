# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from email.header import Header

import tools, threading, auth


f = 0

def send_email(to, subject, msg):
    import smtplib

    gmail_user = "matllesoftware@gmail.com"
    gmail_pwd = "matlle2015"
    FROM = 'matllesoftware@gmail.com'
    TO = [str(to)] 
    SUBJECT = subject
    TEXT = msg 
    
    global f

    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    if f:
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
            print e
            return False

    f = 1




def t_account_created(company, username):
    msg = "Bonjour Mr/Mme responsable " + company + ",\n\n\nVotre nouveau compte a été crée avec succèes.\n\n\nVous pouvez desormais vous connecter sur le logiciel InterNotes.\n\n\nVotre nom d\'utilisateur est: " + username + "\n\n\nVotre mot de passe est celui que vous avez entré lors de la création du compte.\n\n\nCordialement, \n\n\n\nL'équipe InterNotes \n\n(+225) 07 08 68 98\n(+225) 41 87 07 68\n(+225) 01 58 03 30 \nhttp://www.matlle.com"

         
    return msg

def t_account_restore_password(username, code):
    msg = "Bonjour Mr/Mme " + username + ",\n\n\n"\
          "Une personne a récemment demandé à réinitialiser "\
          "votre mot de passe InterNotes.\n\nSi vous êtes à "\
          "l\'origine de cette action, vous pouvez saisir le "\
          "code de réinitialisation ci-dessous\ndans le logiciel "\
          "pour réinitialiser votre mot de passe :\n\n\t\t "+ code +\
          "\n\nsinon, veuillez tout simplement ignorer ce message."\
          "\n\n\nCordialement, \n\n\n\nL'équipe InterNotes \n\n"\
          "(+225) 07 08 68 98\n(+225) 41 87 07 68\n(+225) 01 58 03 30"\
          "\nhttp://www.matlle.com"

         
    return msg


done = False

def run_send_email(email, company_name, username, sub):
    msg_body = t_account_created(company_name, username)
    if send_email(email, sub, msg_body):
        print "[+] Successfully sent email."
        global done
        done = True

    else:
        print "[-] Failed to send email. Try again..."
        #QMessageBox.warning(self, "InterNotes", u"Echec d'envoie du message de confirmation à votre email.")


        t = threading.Timer(1, run_send_email, [email, company_name, username, sub]).start()
        if done == True:
            t.cancel()



done = False
counter = 0

def run_send_email_for_reset_password(dialog):
    global done
    global counter
    if not dialog.isVisible():
        print "[-] Sending email canceled."
        done = True 
   
    elif not done and send_email("matllesoftware@gmail.com", "Restore password", 
           "Change your password"):
        print "[+] Successfully sent email."

        #dialog.setVisible(False)
        dialog.accept()

        done = True

    else:
        counter += 1
        print "[+] Sending email... Attempts " + str(counter)
        t = threading.Timer(1, run_send_email_for_reset_password, 
                  [dialog]).start()



        try:
            if counter >= 2 or done == True:
                t.cancel()
        except AttributeError:
            pass

