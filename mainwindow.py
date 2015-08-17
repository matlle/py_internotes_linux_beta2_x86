# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from studentpage import StudentPage
from statpage import StatPage
import tools, topic, printing, export, auth, dbconfig, about

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #db = database.getDbConnection()

        self.guard = None

        #Qt.WindowStaysOnTopHint
        splash = QSplashScreen(QPixmap(":/images/splash.png"))

        splash.show()
        splash.showMessage(u"Connexion à la base de donnée, patienter svp...", Qt.AlignBottom | Qt.AlignLeft)

        self.dbconf = dbconfig.DbConfig()
        
        if not self.dbconf.opened:
            raise ValueError('Database not connected')

        else:
            splash.showMessage(u"Connecté à la base de donnée!", Qt.AlignBottom | Qt.AlignLeft)

            a = auth.Auth(self)

            self.init()

        splash.finish(self)



    def writePositionSettings(self):
        q_settings = QSettings("MATLLE", "InterNotes")
        q_settings.beginGroup("mainwindow")

        q_settings.setValue("geometry", self.saveGeometry())
        q_settings.setValue("savestate", self.saveState())
        q_settings.setValue("maximized", self.isMaximized())
        if not self.isMaximized(): 
            q_settings.setValue("pos", self.pos())
            q_settings.setValue("size", self.size())

        q_settings.endGroup()


    def readPositionSettings(self):
        q_settings = QSettings("MATLLE", "InterNotes")

        q_settings.beginGroup("mainwindow")

        self.restoreGeometry(q_settings.value("geometry", self.saveGeometry()).toByteArray())
        self.restoreState(q_settings.value("savestate", self.saveState()).toByteArray())
        self.move(q_settings.value("pos", self.pos()).toPoint())
        self.resize(q_settings.value("size", self.size()).toSize())
        if q_settings.value("maximized", self.isMaximized()).toBool():
            self.showMaximized()

        q_settings.endGroup();


    def moveEvent(self, M_event):
        self.writePositionSettings()

    def resizeEvent(self, R_event):
        self.writePositionSettings()

    def closeEvent(self, C_event):
        reply = QMessageBox.question(self, u"Quitter?",
                u"Êtes vous sure de vouloir fermer InterNotes?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.writePositionSettings()
            qApp.quit()
        else:
            C_event.ignore()


    def init(self, cancel=False):
        #query = QSqlQuery()
        if cancel == True:
            return

        self.setWindowTitle("InterNotes")

        self.setupFileMenu()
        self.setupSettingsMenu()
        self.setupHelpMenu()

        self.setupToolBar()
        self.setupShortcuts()

        main_container = QWidget()

        self.contents_widget = QListWidget()
        self.contents_widget.setViewMode(1)
        self.contents_widget.setIconSize(QSize(96, 84))
        self.contents_widget.setMovement(0)
        self.contents_widget.setMaximumWidth(105)
        self.contents_widget.setMinimumWidth(105)
        self.contents_widget.setSpacing(6)
        #self.contents_widget.setStyleSheet("background-color: #ccc;")


        self.pages_widget = QStackedWidget()

        self.stat_page = StatPage()
        self.student_page = StudentPage(self.stat_page)

        self.pages_widget.addWidget(self.student_page)
        self.pages_widget.addWidget(self.stat_page)
       
        self.createIcon()
        self.contents_widget.setCurrentRow(0)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.contents_widget)
        horizontal_layout.addWidget(self.pages_widget, 1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(horizontal_layout)
        main_layout.addSpacing(12)

        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)
        self.statusBar().showMessage("Ready...", 5000)
        #self.showMaximized()

        self.setupSignalSlotEvents()

    
    def createIcon(self):
        student_item = QListWidgetItem(self.contents_widget)
        student_item.setIcon(QIcon(":/images/students.png"))
        student_item.setText(QString("Eleves"))

        statistic_item = QListWidgetItem(self.contents_widget)
        statistic_item.setIcon(QIcon(":/images/kchart.png"))
        statistic_item.setText(QString("Graphiques"))
        

    def changePage(self, current, previous):
        if not current:
            current = previous
        self.pages_widget.setCurrentIndex(
                self.contents_widget.row(current))

        if self.contents_widget.currentRow() == 1:
            self.action_new_academicyear.setEnabled(False)
            self.action_new_student.setEnabled(False)
            self.action_new_class.setEnabled(False)
            self.action_topic.setEnabled(False)
            self.search_student_field.setEnabled(False)

        elif self.contents_widget.currentRow() == 0:
            self.action_new_academicyear.setEnabled(True)
            self.action_new_student.setEnabled(True)
            self.action_new_class.setEnabled(True)
            self.action_topic.setEnabled(True)
            self.search_student_field.setEnabled(True)

   
    def setupFileMenu(self):
        file_menu = self.menuBar().addMenu(self.tr("&Action"))

        self.menu_new = file_menu.addMenu(QIcon(":/images/newaction.png"),
                self.tr(u"Nouveau"))

        self.action_new_student = self.menu_new.addAction(QIcon(":/images/add_user.png"), u"Élève")
        self.action_new_student.setStatusTip(u"Nouveau élève")

        self.action_new_class = self.menu_new.addAction(QIcon(":/images/classe.png"),
                u"Classe")
        self.action_new_class.setStatusTip(u"Nouvelle classe")

        #self.action_new_classroom = self.menu_new.addAction(u"Salle")
        self.action_new_academicyear = self.menu_new.addAction(QIcon(":/images/academicyear.jpg"),
                u"Année Academique")
        self.action_new_academicyear.setStatusTip(u"Nouvelle année academique")

        self.action_topic = self.menu_new.addAction(QIcon(":/images/topic.png"),
                u"Matière")
        self.action_topic.setStatusTip(u"Matière")

        file_menu.addSeparator() 

        self.action_export_pdf = file_menu.addAction(QIcon(u":/images/exportpdf.png"),
                self.tr("Exporter PDF"))

        file_menu.addSeparator() 


        file_menu.addSeparator() 

        self.action_disconnect = file_menu.addAction(QIcon(":/images/disconnect.png"), 
                self.tr("&Déconnection"))
        self.action_disconnect.setStatusTip(u"Déconnection")

        self.action_reboot = file_menu.addAction(QIcon(":/images/app_reboot.png"), self.tr("&Redémarrer"))
        self.action_exit = file_menu.addAction(QIcon(":/images/app_exit.png"), self.tr("&Quitter"))
        self.action_exit.setStatusTip(u"Fermer InterNotes")


    


    def setupHelpMenu(self):
        self.help_menu = self.menuBar().addMenu(self.tr(u"&Aide"))
        self.action_key_activation = self.help_menu.addAction(QIcon(":/images/keys.png"),
                self.tr("Licence activation"))

        self.action_about = self.help_menu.addAction(QIcon(":/images/logo.png"), 
                self.tr("À propos"))

    
    def setupSettingsMenu(self):
        settings_menu = self.menuBar().addMenu(self.tr(u"&Paramètres"))

        self.config = settings_menu.addMenu(QIcon(":/images/configure.png"),
                self.tr(u"Configurations"))

        self.action_config_database = self.config.addAction(QIcon(":/images/database.png"), 
                u"Base de donnée")
        #self.action_new_class = self.menu_new.addAction(u"Classe")


    def setupToolBar(self):
        self.toolbar = self.addToolBar("primary_toolbar")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setObjectName("primary_toolbar")
        self.toolbar.addAction(self.action_new_academicyear)
        self.toolbar.addAction(self.action_new_class)
        self.toolbar.addAction(self.action_new_student)
        self.toolbar.addAction(self.action_topic)
        self.toolbar.addAction(self.action_disconnect)
        self.toolbar.addAction(self.action_exit)
        
        self.toolbar.addSeparator()

        self.search_student_field = QLineEdit(self)
        self.search_student_field.setPlaceholderText(u"Rechercher élève")
        self.toolbar.addWidget(self.search_student_field)


    def setupShortcuts(self):
        self.action_new_academicyear.setShortcut(QKeySequence("Ctrl+I"))
        self.action_new_class.setShortcut(QKeySequence("Ctrl+L"))
        self.action_new_student.setShortcut(QKeySequence("Ctrl+N"))
        self.action_topic.setShortcut(QKeySequence("Ctrl+M"))
        self.action_exit.setShortcut(QKeySequence("Ctrl+Q"))
        self.action_about.setShortcut(QKeySequence("Ctrl+H"))
        self.action_export_pdf.setShortcut(QKeySequence("Ctrl+E"))
    




     
    """ ACTIONS """
    def onShowAboutBox(self):
        a = about.About(self)

        """
        QMessageBox.information(self, self.tr("Apropos de InterNotes"), 
               u"Logiciel de gestion des notes et bulletin de notes des eleves.\n" \
                       u"Développé par MATLLE")
        """
    
    def onShowEnterKeyDialog(self):
        if self.guard:
            if self.guard.activated_prod:
                q_settings = QSettings("MATLLE", "InterNotes")
                q_settings.beginGroup("as")

                key = q_settings.value("k", "").toString()

                q_settings.endGroup()

                QMessageBox.information(self.guard, u"Licence activé - InterNotes",
                        u"Le logiciel est activé avec la clé de licence:\n\n"
                        u"%s" % key
                        )

            else:
                self.guard.enterKeyDialog()



    def onNewAcademicYear(self):
        reply = self.student_page.academic_year_tree.showNewAcademicYearBox() 
        if reply[0] == 1:
            ayname = reply[1]

            period = ''
            if reply[2] == True:
                period = 'quarter'
            else:
                period = 'semester'
            

            self.student_page.academic_year_tree.appendNewAcademicYearItem(ayname, period)
        else:
           return


    def onNewClass(self):
        ay_current_item = self.student_page.academic_year_tree.currentItem()
        if ay_current_item is None:
            QMessageBox.critical(self, u"Error - InterNotes",
                    u"Veuillez d'abord selectioner une année academique")
            return
        ay_id = ay_current_item.data(0, 11).toInt()[0]
        ay_name = ay_current_item.text(0)
        reply = self.student_page.class_tree.showNewClassBox(ay_id, ay_name)
        nclname = reply[1] #.replace(" ", "")
        if reply[0] == 1 and not nclname.isEmpty():
            self.student_page.class_tree.appendNewClassItem(nclname, ay_id, ay_name)
        else:
            return


    def onShowTopicDialog(self):
       t = topic.Topic(self.student_page, self)



    def onNewStudent(self):
        reply = self.student_page.student_name_tree.showNewStudentDialog()

        student_infos = {}
        student_infos['student_first_name'] = reply[1]
        student_infos['student_last_name'] = reply[2]
        student_infos['student_birth_date'] = reply[3]
        student_infos['student_birth_place'] = reply[4]
        student_infos['student_genre'] = reply[5]
        student_infos['student_height'] = reply[6]
        student_infos['student_matricule'] = reply[7]
        student_infos['student_previous_school'] = reply[8]
        student_infos['student_redoubler'] = reply[9]
        student_infos['student_email'] = reply[10]
        student_infos['student_phone1'] = reply[11]
        student_infos['student_phone2'] = reply[12]
        student_infos['student_phone3'] = reply[13]

        student_infos['ay_id'] = reply[14]
        student_infos['class_id'] = reply[15]
        student_infos['classroom_id'] = reply[16]
        student_infos['new_photo_file_name'] = reply[17]

        student_infos['student_matricule_ministeriel'] = reply[18]
        student_infos['marks'] = reply[19]
        student_infos['student_statut'] = reply[20]
        student_infos['student_previous_classroom'] = reply[21]


        if reply[0] == 1:
            self.student_page.student_name_tree.appendNewStudentItem(student_infos)
        elif reply[0] == 0:
            if student_infos['new_photo_file_name']:
                new_photo_file_name = student_infos['new_photo_file_name']
                if new_photo_file_name is not None and not new_photo_file_name.isEmpty():
                    tmp_photo_file = QFile(new_photo_file_name, self)
                    if not tmp_photo_file.remove():
                        QMessageBox.critical(self, u"Error", u"Erreur de suppression de la photo temporaire\n" + new_photo_file_name)
                    student_infos['new_photo_file_name'] = ''


    def onShowExportDialog(self):
        p = export.Export(self.student_page, self)


    def onShowPrintingDialog(self):
        p = printing.Printing(self.student_page, self)

    def onShowSigninDialog(self):
        a = auth.Auth(self)

    def onShowDatabaseConfigDialog(self):
        if self.dbconf:
            self.dbconf.dbConfigDialog(parent=self, q=True)
        else:
            dbcon = dbconfig.DbConfig(self)

    

    def onReboot(self):
        reply = QMessageBox.question(self, u"Quitter?",
                u"Êtes vous sure de vouloir redémarrer InterNotes?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QApplication.exit(tools.EXIT_CODE_REBOOT)

    def quit(self):
        self.close()
        

    """
    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction(self.action_new_academicyear)
        menu.addAction(self.action_new_class)
        menu.exec_(event.globalPos())
    """


    """ SIGNAL/SLOT EVENTS """
    def setupSignalSlotEvents(self):
        self.connect(self.action_exit, SIGNAL("triggered()"), self.quit)
        self.connect(self.action_about, SIGNAL("triggered()"), self.onShowAboutBox)
        self.connect(self.action_key_activation, SIGNAL("triggered()"), self.onShowEnterKeyDialog)
        self.connect(self.action_new_academicyear, SIGNAL("triggered()"), self.onNewAcademicYear)
        self.connect(self.action_new_class, SIGNAL("triggered()"), self.onNewClass)
        self.connect(self.action_new_student, SIGNAL("triggered()"), self.onNewStudent)



        self.connect(self.search_student_field, SIGNAL("textEdited(QString)"), 
                self.student_page.student_name_tree.proxy_model, SLOT("setFilterFixedString(QString)"))

        self.connect(self.search_student_field, SIGNAL("textEdited(QString)"), 
                self.student_page.student_name_tree.currentStudentNameSearched)



        self.connect(self.action_topic, SIGNAL("triggered()"), 
                self.onShowTopicDialog)

        self.connect(self.action_export_pdf, SIGNAL("triggered()"), 
                self.onShowExportDialog)


        self.connect(self.action_disconnect, SIGNAL("triggered()"), 
                self.onShowSigninDialog)

        self.connect(self.action_config_database, SIGNAL("triggered()"), 
                self.onShowDatabaseConfigDialog)

        self.connect(self.action_reboot, SIGNAL("triggered()"), 
                self.onReboot)

        self.connect(self.contents_widget, 
                   SIGNAL("currentItemChanged(QListWidgetItem*, QListWidgetItem*)"),
                   self.changePage)

