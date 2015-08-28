# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, student


class AcademicYear(QTreeWidget):
    def __init__(self, in_classtree, in_student_tree, in_stat_page, parent=None):
        super(AcademicYear, self).__init__(parent)

        self.stat_page = in_stat_page 

        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.header().setDefaultAlignment(Qt.AlignCenter);

        self.updateAcademicYearTree()
        self.setHeaderLabel(QString(u"Années academique (%i)" % self.topLevelItemCount()))

        self.class_tree = in_classtree # 'in' means 'instance of'
        self.student_tree = in_student_tree 
        


    
    def clearStatPage(self):
        self.stat_page.stat_object_tree.updateStatObjectTree()
        self.stat_page.stat_feature_tree.clear()
        self.stat_page.stat_feature_tree.setHeaderLabel(u"")

        child = self.stat_page.stat_output.layout.takeAt(0)
        if child:
            child.widget().deleteLater()


    def updateAcademicYearTree(self):
        query = QSqlQuery("SELECT * FROM academic_year")
        if not query.exec_():
            try:
                QMessageBox.critical(self, "Error", 
                    QString("Database Error: %1").arg(db.lastError().text()))
            except:
                return
        else:
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    ay_id = query.value(record.indexOf("academic_year_id")).toInt()
                    ay_name = query.value(record.indexOf("academic_year_name")).toString()
                    ni = QTreeWidgetItem(self, QStringList(ay_name))
                    ni.setData(0, 11, QVariant(ay_id[0]))
                    ni.setIcon(0, QIcon(":/images/academicyear.jpg"))
                    self.insertTopLevelItem(0, ni)




    
    def appendNewAcademicYearItem(self, new_ay_name, period):
        query = QSqlQuery()
        query.prepare("INSERT INTO academic_year(  \
                                   academic_year_name, \
                                   academic_year_divided_in, \
                                   academic_year_created_at) \
                       VALUES(:ay_name, :period, NOW())")

        query.bindValue(":ay_name", new_ay_name)
        query.bindValue(":period", period)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                    u"Database Error: %s" % query.lastError().text())
        else:
            new_ay_id = query.lastInsertId().toInt()[0]
            ni = QTreeWidgetItem(self, QStringList(new_ay_name))
            ni.setData(0, 11, QVariant(new_ay_id))
            ni.setIcon(0, QIcon(":/images/academicyear.jpg"))
            self.insertTopLevelItem(0, ni)
            self.setHeaderLabel(QString(u"Années academique (%i)" % self.topLevelItemCount()))

            self.clearStatPage()



    def editAcademicYearItem(self):
        ay_item = self.currentItem()
        if ay_item.isSelected() == True:
            ay_name = ay_item.text(0)
            ayid = ay_item.data(0, 11).toInt()[0]
            period = self.getPeriodById(ayid)

            reply = self.showNewAcademicYearBox(ay_name, period)
            if reply[0] == 0:
                return
            if period == 'quarter' and reply[2] == False:
                #period's been changed
                self.deleteAllMarksByAcademicYearId(ayid)
                QMessageBox.information(self, "Infos - InterNotes",
                        u"La subdivision de cette année a étté changé. " + 
                        u"Par conséquent, toutes les notes inscrites " + 
                        u"dans cette année ont été supprimé!");
            elif period == 'semester' and reply[2] == True:
                #period's been changed here also
                self.deleteAllMarksByAcademicYearId(ayid)
                QMessageBox.information(self, "Infos - InterNotes",
                        u"La subdivision de cette année a étté changé. " + 
                        u"Par conséquent, toutes les notes inscrites " + 
                        u"dans cette année ont été supprimé!");

            new_period = ''
            if reply[2] == True:
                new_period = 'quarter'
            else:
                new_period = 'semester'

            if reply[0] == 1:
                #update from db
                ayname = reply[1]

                query = QSqlQuery()
                query.prepare("UPDATE academic_year \
                               SET academic_year_name = :ayname, \
                                   academic_year_divided_in = :period, \
                                   academic_year_updated_at = NOW() \
                               WHERE academic_year_id = :ayid")
                query.bindValue(":ayid", ayid)
                query.bindValue(":ayname", ayname)
                query.bindValue(":period", new_period)
                if not query.exec_():
                    QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query.lastError().text())
                else:
                    ay_item.setText(0, ayname)
                    self.class_tree.selectClassesByAcademicYearId(ay_item, 0)

                    self.clearStatPage()

            else:
                return



    def deleteAcademicYearItem(self):
        ay_item = self.currentItem()
        if ay_item.isSelected() == True:
            reply = QMessageBox.question(self, "Supprimer?", 
                    u"Êtes vous sûr de vouloir supprimer definitivement du logiciel l'année academique <b>%s</b> " \
                    u"selectionnée et toutes les composantes ratachées à cette année?" % ay_item.text(0), QMessageBox.Yes | QMessageBox.No,
                                                        QMessageBox.No)
            if reply == QMessageBox.Yes:
                #delete from db
                ayid = ay_item.data(0, 11).toInt()[0]
                ay_index = self.indexOfTopLevelItem(ay_item)

                query_pre = QSqlQuery("SELECT student_id FROM student WHERE academic_year_id = " + str(ayid))
                if query_pre.exec_():
                    record = query_pre.record()
                    if not record.isEmpty():
                        while query_pre.next():
                            student_id = query_pre.value(record.indexOf("student_id")).toInt()[0]

                            self.student_tree.removeOldPhoto(student_id)

                query_pre.finish()



                query_away = QSqlQuery()
                query_away.prepare("DELETE aw.* \
                                      FROM student std \
                                      LEFT JOIN away aw ON aw.student_id = std.student_id \
                                      WHERE std.academic_year_id = :ayid \
                                    ")

                query_away.bindValue(":ayid", ayid)
                if not query_away.exec_():
                    QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query_away.lastError().text())
                    return

                query_away.finish()




                query_first = QSqlQuery()
                query_first.prepare("DELETE m.*,\
                                            t.*,\
                                            std.*,\
                                            cr.* \
                                     FROM classroom  cr \
                                     LEFT JOIN mark m ON m.classroom_id = cr.classroom_id \
                                     LEFT JOIN topic t ON t.classroom_id = cr.classroom_id \
                                     LEFT JOIN student std ON std.classroom_id = cr.classroom_id \
                                     INNER JOIN class cl ON cl.class_id = cr.class_id \
                                     WHERE cl.academic_year_id = :ayid \
                                   ")

                query_first.bindValue(":ayid", ayid)
                if not query_first.exec_():
                    QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query_first.lastError().text())
                    return

                query_first.finish()




                query_second = QSqlQuery()
                query_second.prepare("DELETE cl.*, \
                                             ay.* \
                                      FROM academic_year ay \
                                      LEFT JOIN class cl ON cl.academic_year_id = ay.academic_year_id \
                                      WHERE ay.academic_year_id = :ayid \
                                    ")

                query_second.bindValue(":ayid", ayid)
                if not query_second.exec_():
                    QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query_second.lastError().text())
                    return
                else:
                    o_item = self.takeTopLevelItem(ay_index)
                    self.setHeaderLabel(QString(u"Années academique (%i)" % self.topLevelItemCount()))
                    self.class_tree.setHeaderLabel(u"Classes (0)")
                    self.class_tree.clear()


                    self.class_tree.student_tree.infos.showStudentInfos(0)

                    del self.class_tree.student_tree.model
                    self.class_tree.student_tree.model = QStandardItemModel(self.class_tree.student_tree)
                    self.class_tree.student_tree.model.setHorizontalHeaderLabels(QStringList(
                        u"Elèves - Nom et prenoms (0)"
                        ))
            
                    self.class_tree.student_tree.proxy_model.setSourceModel(
                            self.class_tree.student_tree.model)

                    self.class_tree.student_tree.infos.showStudentInfos(0)




                    next_item = self.currentItem()
                    self.class_tree.selectClassesByAcademicYearId(next_item, 0)

                    self.clearStatPage()

            elif reply == QMessageBox.No:
                return



     
    def newClass(self):
        current_item = self.currentItem()
        if current_item is None:
            QMessageBox.critical(self, u"Error - InterNotes",
                    u"Veuillez d'abord selectioner une année academique")
            return
        ay_id = current_item.data(0, 11).toInt()[0]
        ay_name = current_item.text(0)
        reply = self.class_tree.showNewClassBox(ay_id, ay_name)
        nclname = reply[1] #.replace(" ", "")
        if reply[0] == 1 and not nclname.isEmpty():
            self.class_tree.appendNewClassItem(nclname, ay_id, ay_name)

            self.clearStatPage()

        else:
            return



    def showNewAcademicYearBox(self, ayname=None, period=None):
        dialog = QDialog(self)

        line_academic_year = QLineEdit()
        if ayname:
            line_academic_year.setText(ayname)
        radio_quarter = QRadioButton(u"Trimestre", dialog)
        radio_semester = QRadioButton(u"Semestre", dialog)
        if period:
            if period == 'quarter':
                radio_quarter.setChecked(True)
            else:
                radio_semester.setChecked(True)
        else:
            radio_quarter.setChecked(True)

        layout_form = QFormLayout()
        layout_form.addRow(u"Année academique: ", line_academic_year)
        layout_form.addRow(u"Année divisée en: ", radio_quarter)
        layout_form.addRow(u"", radio_semester)

        group_form = QGroupBox(u"Année Academique")
        group_form.setLayout(layout_form)

        btn_ok = QPushButton("Ok")
        btn_ok.setIcon(QIcon(":/images/button_apply.png"))
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setIcon(QIcon(":/images/button_cancel.png"))

        layout_btn = QHBoxLayout()
        layout_btn.addWidget(btn_ok)
        layout_btn.addWidget(btn_cancel)
        layout_btn.setAlignment(Qt.AlignRight)
       

        layout_main = QVBoxLayout()
        layout_main.addWidget(group_form)
        layout_main.addLayout(layout_btn)

        dialog.setLayout(layout_main)
        dialog.resize(400, 100)
        dialog.setWindowTitle(u"Année academique - InterNotes")

        self.connect(btn_ok, SIGNAL("clicked()"), dialog.accept)
        self.connect(btn_cancel, SIGNAL("clicked()"), dialog.reject)

        return dialog.exec_(), line_academic_year.text(), radio_quarter.isChecked()
                                                          
               










    def contextMenuEvent(self, event):
         menu = QMenu()

         action_edit = tools.createAction(self, u"&Modifier l'année", 
                             self.editAcademicYearItem, 
                             "",
                             ":/images/edit.png",
                             u"Modifier l'année", 
                             u"Modifier l'année academique selectionnée")

         action_delete = tools.createAction(self, u"&Supprimer l'année", 
                             self.deleteAcademicYearItem, 
                             "Ctrl+D",
                             ":/images/button_cancel.png",
                             u"Supprimer l'année academique selectionnée. Attention ceci supprimera toutes les composantes (classe(s), salle(s), élève(s)) rattachées à cette année academique!"
                             )

         action_new_class = tools.createAction(self, u"&Classe", self.newClass, 
                                   "Ctrl+C",
                                   u":/images/classe.png",
                                   u"Créer une classe dans cette année academique")


          
         if self.currentItem() is None or self.currentItem().isSelected() == False:
             action_edit.setEnabled(False)
             action_delete.setEnabled(False)
             action_new_class.setEnabled(False)
         else:
             action_edit.setEnabled(True)
             action_delete.setEnabled(True)
             action_new_class.setEnabled(True)



         menu.addAction(action_edit)
         menu.addAction(action_delete)
         menu.addAction(action_new_class)
         menu.exec_(event.globalPos())




    @staticmethod
    def getNameById(ay_id):
        ay_name = QString('')
        query = QSqlQuery("SELECT academic_year_name FROM academic_year \
                           WHERE academic_year_id = " + str(ay_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    ay_name = query.value(record.indexOf("academic_year_name")).toString()

        return ay_name


    @staticmethod
    def isAcademicYearHasClass(ayid):
        query = QSqlQuery("SELECT class_id \
                           FROM class \
                           WHERE academic_year_id = " + str(ayid))
        if query.exec_():
            if query.size() >= 1:
                return True
            else:
                return False


    @staticmethod
    def getClassesById(ay_id):
        data = []
        query = QSqlQuery("SELECT \
                           class_id, \
                           class_name \
                           FROM class \
                           WHERE academic_year_id = " + str(ay_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    row = {}
                    row['class_id'] = query.value(
                            record.indexOf("class_id")).toInt()[0]

                    row['class_name'] = query.value(
                            record.indexOf("class_name")).toString()

                    data.append(row)

        return data



    @staticmethod
    def getPeriodById(ay_id):
        period = QString(u'')
        query = QSqlQuery("SELECT academic_year_divided_in FROM academic_year \
                           WHERE academic_year_id = " + str(ay_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    period = query.value(record.indexOf("academic_year_divided_in")).toString()

        return period


    def deleteAllMarksByAcademicYearId(self, ay_id):
        query = QSqlQuery("DELETE FROM mark  \
                           WHERE academic_year_id = " + str(ay_id))
        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                    u"Database Error: %s" % query.lastError().text())




    @staticmethod
    def getAllStudentsIdAndNameById(ayid):
        data = []
        query = QSqlQuery("SELECT student_id, \
                                  student_first_name, \
                                  student_last_name \
                           FROM student \
                           WHERE academic_year_id = " + str(ayid) + 
                           " ORDER BY student_last_name ASC")
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    row = {}
                    row["student_id"] = query.value(
                                record.indexOf("student_id")).toInt()[0]

                    row["student_first_name"] = query.value(
                                record.indexOf("student_first_name")).toString()

                    row["student_last_name"] = query.value(
                                record.indexOf("student_last_name")).toString()
                    
                    data.append(row)
                            

        return data




