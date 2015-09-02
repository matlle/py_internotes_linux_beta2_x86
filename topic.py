#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, photopreview, academicyear, classe, studentpage

class Topic(QDialog):
    def __init__(self, in_std_page, parent=None):
        super(Topic, self).__init__(parent)
        
        self.std_page = in_std_page # instance

        self.list_removables_topics = []
        self.init()

        



    
      

    
    def clearStatPage(self):
        self.std_page.stat_page.stat_object_tree.updateStatObjectTree()
        self.std_page.stat_page.stat_feature_tree.clear()
        self.std_page.stat_page.stat_feature_tree.setHeaderLabel(u"")

        child = self.std_page.stat_page.stat_output.layout.takeAt(0)
        if child:
            child.widget().deleteLater()


    def update_student_marks_widget(self):
        #if self.std_page.student_infos.currentIndex() == 1:
        if self.std_page.student_infos.student_id and \
                self.std_page.student_infos.std_name and \
                self.std_page.student_infos.std_genre:
            self.std_page.student_infos.showMarksOnTabChange(
                    index=1, updated=True)

            self.clearStatPage()

        self.reject()


    def closeEvent(self, event):
        self.update_student_marks_widget()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass

    
    def getClassesByAcademicYearId(self, ay_id):
        data = []
        query = QSqlQuery("SELECT class_id, class_name FROM class WHERE academic_year_id = " + str(ay_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while query.next():
                    row = {}
                    row['class_id'] = query.value(record.indexOf("class_id")).toInt()[0]
                    row['class_name'] = query.value(record.indexOf("class_name")).toString()
                    data.append(row)


        return data




    def getClassroomsByClassId(self, class_id):
        data = []
        query = QSqlQuery("SELECT classroom_id, \
                                  classroom_name \
                           FROM classroom WHERE class_id = " + str(class_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while query.next():
                    row = {}
                    row['classroom_id'] = query.value(record.indexOf("classroom_id")).toInt()[0]
                    row['classroom_name'] = query.value(record.indexOf("classroom_name")).toString()
                    data.append(row)

        return data




    def getTopicsByClassroomId(self, classroom_id):
        data = []
        query = QSqlQuery("SELECT * \
                           FROM topic WHERE classroom_id = " + str(classroom_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while query.next():
                    row = {}
                    row['topic_id'] = query.value(record.indexOf("topic_id")).toInt()[0]
                    row['topic_name'] = query.value(record.indexOf("topic_name")).toString()
                    row['topic_coef'] = query.value(record.indexOf("topic_coef")).toInt()[0]
                    row['topic_type'] = query.value(record.indexOf("topic_type")).toString()
                    row['classroom_id'] = query.value(record.indexOf("classroom_id")).toString()
                    data.append(row)

        return data





    def setClassComboBoxByAcademicYearId(self, ay_index):
        ay_id = self.combo_ay.itemData(ay_index).toInt()[0]
        classes = self.getClassesByAcademicYearId(ay_id)
        self.combo_class.clear()
        for c in classes:
            self.combo_class.addItem(c['class_name'], QVariant(c['class_id']))


    def setClassroomComboBoxByClassId(self, class_index):
        class_id = self.combo_class.itemData(class_index).toInt()[0]
        rooms = self.getClassroomsByClassId(class_id)
        self.combo_classroom.clear()
        for r in rooms:
            self.combo_classroom.addItem(r['classroom_name'], QVariant(r['classroom_id']))






    def updateAcademicYearComboBox(self):
        query = QSqlQuery("SELECT academic_year_id, \
                                  academic_year_name \
                           FROM academic_year \
                           ORDER BY academic_year_name DESC")
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while query.next():
                    ay_id = query.value(record.indexOf("academic_year_id")).toInt()[0]
                    ay_name = query.value(record.indexOf("academic_year_name")).toString()
                    self.combo_ay.addItem(ay_name, QVariant(ay_id))

        self.combo_ay.setCurrentIndex(-1)

    

    def addNewRow(self):
        nb_row = self.table_view.rowCount()

        nb = nb_row + 1
        self.table_view.insertRow(nb_row)
        self.table_view.setRowHeight(nb_row, 20)

        spin_coef = QSpinBox()
        spin_coef.setMinimum(1)

        combo_type = QComboBox()


        to_types = self.getAllTopicTypes()
                    
        for tt in range(0, len(to_types)):
            combo_type.addItem(to_types[tt])

        combo_type.addItem(u'Autre')
        combo_type.addItem(u'Littéraire')
        combo_type.addItem(u'Scientifique')
        combo_type.addItem(u'Technique')

        combo_type.setDuplicatesEnabled(False)
        combo_type.setEditable(True)
        combo_type.setInsertPolicy(QComboBox.InsertAtTop)


        self.table_view.setItem(nb_row, 0, QTableWidgetItem())
        self.table_view.setCellWidget(nb_row, 1, spin_coef)
        self.table_view.setItem(nb_row, 2, QTableWidgetItem())
        self.table_view.setCellWidget(nb_row, 3, combo_type)

        self.connect(spin_coef, SIGNAL("valueChanged(int)"), 
                                     self.activeSaveBtn)

        self.connect(combo_type, SIGNAL("currentIndexChanged(int)"), 
                                     self.activeSaveBtn)



    def updateOldTopic(self, tid, tname, tcoef, tprof, ttype, crid):
        query = QSqlQuery()
        query.prepare("UPDATE topic \
                       SET topic_name = :name, \
                           topic_coef = :coef, \
                           topic_prof = :prof, \
                           topic_type = :type, \
                           classroom_id = :crid, \
                           topic_updated_at = NOW() \
                       WHERE topic_id = :tid")

        query.bindValue(":name", tname)
        query.bindValue(":coef", tcoef)
        query.bindValue(":prof", tprof)
        query.bindValue(":type", ttype)
        query.bindValue(":crid", crid)
        query.bindValue(":tid", tid)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes", 
                    u"Database Error: %s" % query.lastError().text())



    def insertNewTopic(self, tname, tcoef, tprof, ttype, crid):
        query = QSqlQuery()
        query.prepare("INSERT INTO topic \
                           (topic_name, \
                           topic_coef, \
                           topic_prof, \
                           topic_type, \
                           classroom_id, \
                           topic_created_at) \
                           VALUES(:name, \
                                  :coef, \
                                  :prof, \
                                  :type, \
                                  :crid, \
                                  NOW()  \
                                 ) \
                       ")

        query.bindValue(":name", tname)
        query.bindValue(":coef", tcoef)
        query.bindValue(":prof", tprof)
        query.bindValue(":type", ttype)
        query.bindValue(":crid", crid)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes", 
                    u"Database Error: %s" % query.lastError().text())
        else:
            return query.lastInsertId().toInt()[0]



    def deleteAllTopicsByClassroomId(self, crid):
        query = QSqlQuery("DELETE FROM topic WHERE classroom_id = " + str(crid))
        if not query.exec_():
            QMessageBox.information(self, "Error - InterNotes",
                    u"Database Error: %s " % query.lastError().text())

    def deleteRemovablesTopics(self):
        list_id = self.list_removables_topics
        s = ''
        if list_id:
            if len(list_id) == 1:
                s = '= ' + str(list_id[0])
            else:
                for t in range(0, len(list_id)):
                    if t + 1 == len(list_id):
                        s += '= ' + str(list_id[t])
                    else:
                        s += '= ' + str(list_id[t]) + " OR t.topic_id "
                
            sql = "DELETE m.*, \
                          t.*  \
                   FROM topic t \
                   LEFT JOIN mark m ON m.topic_id = t.topic_id \
                   WHERE t.topic_id " + s
            query = QSqlQuery(sql)
        
            if not query.exec_():
                QMessageBox.critical(self, "Error - InterNotes", 
                     u"Database Error: %s " % query.lastError().text())
            else:
                self.list_removables_topics = []




    def saveTopics(self):
        if self.combo_classroom.currentIndex() != -1:
            cr_index = self.combo_classroom.currentIndex()
            crid = self.combo_classroom.itemData(cr_index).toInt()[0]

            self.deleteRemovablesTopics()

            if self.table_view.rowCount() > 0:
                nb_row = self.table_view.rowCount()
                for r in range(0, nb_row):
                    topic_name = self.table_view.item(r, 0).text()
                    if topic_name.isEmpty():
                        QMessageBox.critical(self, u"Error - InterNotes", u"Pour chaque matière vous devez " + 
                                            u"renseigner au moins le nom")
                        return
                    else:
                        topic_id = self.table_view.item(r, 0).data(Qt.AccessibleTextRole).toInt()[0]
                        topic_coef = self.table_view.cellWidget(r, 1).value()
                        topic_prof = self.table_view.item(r, 2).text()
                        topic_type = self.table_view.cellWidget(r, 3).currentText()

                        if topic_id:
                           self.updateOldTopic(topic_id, topic_name, 
                                              topic_coef, topic_prof, topic_type, crid) 



                           self.btn_save.setEnabled(False)
                        else:
                           tid = self.insertNewTopic(topic_name, topic_coef, 
                                               topic_prof, topic_type, crid)

                           # put the id here
                           self.table_view.item(r, 0).setData(Qt.AccessibleTextRole, 
                                   QVariant(tid))

                           self.btn_save.setEnabled(False)

            else:
                self.deleteAllTopicsByClassroomId(crid)

                    

    def cancelAll(self):
        if self.combo_classroom.currentIndex() != -1:
            cr_index = self.combo_classroom.currentIndex()
            self.setTableTopicsByClassroomId(cr_index)



    def deleteRow(self):
        row = self.table_view.currentRow()

        id = self.table_view.item(row, 0).data(Qt.AccessibleTextRole).toInt()[0]
        if id:
            self.list_removables_topics.append(id)

        self.table_view.removeRow(row)
        self.activeDeleteBtn()
        self.activeSaveBtn()


    def activeSaveBtn(self):
        self.btn_save.setEnabled(True)
   

    def activeDeleteBtn(self):
        if self.combo_classroom.currentIndex() != -1:
            if self.table_view.currentRow() >= 0:
                self.btn_delete_row.setEnabled(True)
            else:
                self.btn_delete_row.setEnabled(False)

        else:
            self.btn_delete_row.setEnabled(False)

    
    def setTableTopicsByClassroomId(self, classroom_index):
        crid = self.combo_classroom.itemData(classroom_index).toInt()[0]
        query = QSqlQuery("SELECT * \
                           FROM topic WHERE classroom_id = " + str(crid))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                self.table_view.setRowCount(query.size())
                nb_row = query.size()
                items = []
                for r in range(0, nb_row):
                    self.table_view.setRowHeight(r, 20)
                while query.next():
                    row = {}
                    topic_id = query.value(record.indexOf("topic_id")).toInt()[0]
                    topic_name = query.value(record.indexOf("topic_name")).toString()
                    topic_coef = query.value(record.indexOf("topic_coef")).toInt()[0]
                    topic_type = query.value(record.indexOf("topic_type")).toString()
                    topic_prof = query.value(record.indexOf("topic_prof")).toString()
                    classroom_id = query.value(record.indexOf("classroom_id")).toInt()[0]

                    item_name = QTableWidgetItem(topic_name)
                    item_name.setData(Qt.AccessibleTextRole, QVariant(topic_id))

                    row['item_name'] = item_name 

                    row['item_coef'] = topic_coef
                    row['item_type'] = topic_type
                    row['item_prof'] = QTableWidgetItem(topic_prof)
                    items.append(row)
             
                for i in range(0, len(items)):
                    self.table_view.setItem(i, 0, items[i]['item_name'])

                    spin_coef = QSpinBox()
                    spin_coef.setMinimum(1)

                    spin_coef.setValue(items[i]['item_coef'])
                    self.table_view.setCellWidget(i, 1, spin_coef)

                    self.table_view.setItem(i, 2, items[i]['item_prof'])

                    combo_type_topic = QComboBox()


                    to_types = self.getAllTopicTypes()
                    
                    for tt in range(0, len(to_types)):
                        combo_type_topic.addItem(to_types[tt])

                    combo_type_topic.addItem(u'Autre')
                    combo_type_topic.addItem(u'Littéraire')
                    combo_type_topic.addItem(u'Scientifique')
                    combo_type_topic.addItem(u'Technique')

                    combo_type_topic.setDuplicatesEnabled(False)
                    combo_type_topic.setEditable(True)
                    combo_type_topic.setInsertPolicy(QComboBox.InsertAtBottom)

                    index_type = combo_type_topic.findText(items[i]['item_type'])
                    combo_type_topic.setCurrentIndex(index_type)
                    self.table_view.setCellWidget(i, 3, combo_type_topic)


                    self.connect(spin_coef, SIGNAL("valueChanged(int)"), 
                                     self.activeSaveBtn)

                    self.connect(combo_type_topic, SIGNAL("currentIndexChanged(int)"), 
                                     self.activeSaveBtn)

                self.table_view.sortItems(0)
                if self.combo_classroom.currentIndex() != -1:
                    self.btn_new_row.setEnabled(True)
                    self.btn_save.setEnabled(True)
                    self.btn_cancel.setEnabled(True)
                else:
                    self.btn_new_row.setEnabled(False)
                    self.btn_save.setEnabled(False)
                    self.btn_cancel.setEnabled(False)

                self.activeDeleteBtn()

  

     
    def init(self):
        self.combo_ay = QComboBox()
        self.combo_ay.setMinimumWidth(200)
        self.updateAcademicYearComboBox()
        self.combo_ay.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        self.combo_class = QComboBox()
        self.combo_class.setMinimumWidth(200)
        self.combo_class.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        self.combo_classroom = QComboBox()
        self.combo_classroom.setMinimumWidth(200)
        self.combo_classroom.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        label_ay = QLabel(u"Année academique:")
        label_class = QLabel(u"Classe: ")
        label_classroom = QLabel(u"Salle: ")


        layout_ay_cl = QHBoxLayout()

        ay_form_layout = QFormLayout()
        ay_form_layout.addRow(u"", label_ay)
        ay_form_layout.addRow(u"", self.combo_ay)

        cl_form_layout = QFormLayout()
        cl_form_layout.addRow(u"", label_class)
        cl_form_layout.addRow(u"", self.combo_class)

        cr_form_layout = QFormLayout()
        cr_form_layout.addRow(u"", label_classroom)
        cr_form_layout.addRow(u"", self.combo_classroom)


        layout_ay_cl.addLayout(ay_form_layout)
        layout_ay_cl.addLayout(cl_form_layout)
        layout_ay_cl.addLayout(cr_form_layout)

        group_year_and_class = QGroupBox(u"Année academique et classe")
        group_year_and_class.setLayout(layout_ay_cl)




        self.table_view = QTableWidget()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.table_view.setGridStyle(Qt.NoPen)
        self.table_view.setShowGrid(False)
        self.table_view.setTabKeyNavigation(True) 
        self.table_view.setColumnCount(4)
        headers = []
        headers.append(u"Nom")
        headers.append(u"Coefficient")
        headers.append(u"Professeur")
        headers.append(u"Type")
        self.table_view.setHorizontalHeaderLabels(headers)
        self.table_view.setColumnWidth(0, 150)
        self.table_view.setColumnWidth(1, 100)
        self.table_view.setColumnWidth(2, 150)
        self.table_view.setColumnWidth(3, 150)



        self.btn_new_row = QPushButton(u"Nouvelle matière")
        self.btn_delete_row = QPushButton(u"Supprimer")
        self.btn_save = QPushButton(u"Enregistrer tout")
        self.btn_cancel = QPushButton(u"Annuler")
        self.btn_exit = QPushButton(u"Quitter")

        self.btn_save.setEnabled(False)
        self.btn_new_row.setEnabled(False)
        self.btn_delete_row.setEnabled(False)
        self.btn_cancel.setEnabled(False)

        self.btn_new_row.setIcon(QIcon(":/images/button_new_row.png"))
        self.btn_delete_row.setIcon(QIcon(":/images/button_remove.png"))
        self.btn_save.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_cancel.setIcon(QIcon(":/images/button_cancel.png"))
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))

        btn_box = QDialogButtonBox(Qt.Vertical)

        btn_box.addButton(self.btn_new_row, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_delete_row, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_save, QDialogButtonBox.AcceptRole)
        btn_box.addButton(self.btn_cancel, QDialogButtonBox.AcceptRole)
        btn_box.addButton(self.btn_exit, QDialogButtonBox.RejectRole)

        layout_table_topic = QHBoxLayout()
        layout_table_topic.addWidget(self.table_view)
        layout_table_topic.addWidget(btn_box)
        
        group_topic = QGroupBox(u"Matière")
        group_topic.setLayout(layout_table_topic)


        layout_main = QVBoxLayout()
        layout_main.addWidget(group_year_and_class)
        layout_main.addWidget(group_topic)

        self.setLayout(layout_main)
        self.resize(800, 500)
        self.setWindowTitle(u"Matière - InterNotes")

        
        self.connect(self.combo_ay, SIGNAL("currentIndexChanged(int)"), 
                self.setClassComboBoxByAcademicYearId)

        self.connect(self.combo_class, SIGNAL("currentIndexChanged(int)"), 
                self.setClassroomComboBoxByClassId)

        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.setTableTopicsByClassroomId)

        self.connect(self.table_view, SIGNAL("cellChanged(int, int)"), 
                self.activeSaveBtn)

        self.connect(self.table_view, SIGNAL("itemClicked(QTableWidgetItem *)"), 
                self.activeDeleteBtn)

        self.connect(self.table_view, SIGNAL("currentItemChanged(QTableWidgetItem *, \
                                                     QTableWidgetItem *)"), 
                self.activeDeleteBtn)


        self.connect(self.btn_save, SIGNAL("clicked()"), 
                self.saveTopics)

        self.connect(self.btn_new_row, SIGNAL("clicked()"), 
                self.addNewRow)

        self.connect(self.btn_delete_row, SIGNAL("clicked()"), 
                self.deleteRow)

        self.connect(self.btn_cancel, SIGNAL("clicked()"), 
                self.cancelAll)

        self.connect(self.btn_exit, SIGNAL("clicked()"), 
                self.update_student_marks_widget)

        return self.exec_()

     


    @staticmethod
    def getAllTopicsByClassroomId(crid):
        data = []
        query = QSqlQuery("SELECT topic_id, \
                                  topic_name \
                           FROM topic \
                           WHERE classroom_id = " + str(crid))
        if not query.exec_():
            print "SQL Error!"
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    row = {}
                    row['topic_id'] = query.value(
                            record.indexOf("topic_id")).toInt()[0]

                    row['topic_name'] = query.value(
                            record.indexOf("topic_name")).toString()

                    data.append(row)

        return data



    @staticmethod
    def getNameById(topic_id):
        topic_name = ''
        query = QSqlQuery("SELECT topic_name \
                           FROM topic \
                           WHERE topic_id = " + str(topic_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    topic_name = query.value(
                            record.indexOf("topic_name")).toString()

        return topic_name

    @staticmethod
    def getProfById(topic_id):
        prof = ''
        query = QSqlQuery("SELECT topic_prof \
                           FROM topic \
                           WHERE topic_id = " + str(topic_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    prof = query.value(
                            record.indexOf("topic_prof")).toString()

        return prof

    @staticmethod
    def isStudentHasAnyMarksInThisTopicAndMarkGroup(tid, stid, group):
        sql = "SELECT mark_id \
               FROM mark \
               WHERE topic_id = " + str(tid) + \
               " AND student_id = " + str(stid) + \
               " AND mark_group = '" + group + "'"

        query = QSqlQuery(sql)
        if query.exec_():
            if query.size() >= 1:
                return True
            else:
                return False
        else:
            print "SQL Error!"


    @staticmethod
    def getAllMarksByIdStudentIdAndMarkGroup(topic_id, stid, group):
        marks = []
        sql = "SELECT  * \
               FROM mark \
               WHERE topic_id = " + str(topic_id) + \
               " AND student_id = " + str(stid) +   \
               " AND mark_group = '" + group + "'" + \
               " ORDER BY mark_created_at DESC"


        query = QSqlQuery(sql)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    m = []
                    mark_id = query.value(
                            record.indexOf("mark_id")).toInt()[0]
                    mark_mark = query.value(
                            record.indexOf("mark_mark")).toDouble()[0]
                    mark_level = query.value(
                            record.indexOf("mark_level")).toInt()[0]
                    mark_observation = query.value(
                         record.indexOf("mark_observation")).toString()
                    mark_date = query.value(
                            record.indexOf("mark_date")).toString()
                    
                    m.append(mark_id)
                    m.append(mark_mark)
                    m.append(mark_level)
                    m.append(mark_observation)
                    m.append(mark_date)

                    marks.append(m)
        
        else:
            print "Database Error: %s" % db.lastError().text()

        return marks




    @staticmethod
    def getAllTopicTypes():
        data = []
        query = QSqlQuery("SELECT topic_type \
                           FROM topic \
                          ")
        if not query.exec_():
            print "SQL Error!"
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    topic_type = query.value(
                            record.indexOf("topic_type")).toString()

                    data.append(topic_type)

        return data
