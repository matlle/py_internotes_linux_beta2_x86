#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools

class Class(QTreeWidget):
    list_items_room = []

    def __init__(self, in_student_tree, in_stat_page, parent=None):
        super(Class, self).__init__(parent)

        self.stat_page = in_stat_page

        self.setSortingEnabled(True)
        self.resize(self.width(), 600)
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        self.header().setDefaultAlignment(Qt.AlignCenter);

        
        self.student_tree = in_student_tree
        

        self.setHeaderLabel(QString(u"Classes (%i)" % self.topLevelItemCount()))
        
        self.connect(self, SIGNAL("itemChanged(QTreeWidgetItem*, int)"),
                     self.changeStateOfChildren)


    def clearStatPage(self):
        self.stat_page.stat_object_tree.updateStatObjectTree()
        self.stat_page.stat_feature_tree.clear()
        self.stat_page.stat_feature_tree.setHeaderLabel(u"")

        child = self.stat_page.stat_output.layout.takeAt(0)
        if child:
            child.widget().deleteLater()



    def selectClassesByAcademicYearId(self, item, col):
        self.clear()
        Class.list_items_room = []
        ayid = item.data(0, 11).toInt()[0]
        ayname = item.text(0)
        query = QSqlQuery()
        query.prepare("SELECT * FROM class WHERE academic_year_id = :ayid")
        query.bindValue(":ayid", ayid)
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
                    class_id = query.value(record.indexOf("class_id")).toInt()
                    class_name = query.value(record.indexOf("class_name")).toString()
                    ni = QTreeWidgetItem(self, QStringList(class_name))
                    ni.setData(0, 11, QVariant(class_id[0]))
                    ni.setIcon(0, QIcon(u":/images/classe.png"))
                    ni.setCheckState(0, Qt.Unchecked)
                    if self.isClassHasClassroom(class_id[0]) == True:
                        rooms = self.getClassroomsByClassId(class_id[0])
                        for r in rooms:
                            child_item = QTreeWidgetItem(ni, QStringList(r['classroom_name']))
                            child_item.setData(0, 11, QVariant(r['classroom_id']))
                            child_item.setCheckState(0, Qt.Unchecked)
                            child_item.setIcon(0, QIcon(u":/images/classroom-icon.png"))
                            ni.addChild(child_item)

                            Class.list_items_room.append(child_item)


                    self.insertTopLevelItem(0, ni)

            if query.size() == 0:
                self.student_tree.infos.showStudentInfos(0)
                del self.student_tree.model
                self.student_tree.model = QStandardItemModel(self)
                self.student_tree.model.setHorizontalHeaderLabels(
                        QStringList(u"Elèves - Nom et prenoms (0)"))
                self.student_tree.proxy_model.setSourceModel(
                        self.student_tree.model)
            self.setHeaderLabel(QString(u"Classes (%i) Année (%s)" % (self.topLevelItemCount(),
                                                                      ayname)))


    
    def appendNewClassItem(self, new_class_name, ay_id, ay_name):
        query = QSqlQuery()
        query.prepare("INSERT INTO class(class_name, class_created_at, academic_year_id) \
                       VALUES(:class_name, NOW(), :ayid)")
        query.bindValue(":class_name", new_class_name)
        query.bindValue(":ayid", ay_id)
        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                    u"Database Error: %s" % query.lastError().text())
        else:
            new_class_id = query.lastInsertId().toInt()[0]
            ni = QTreeWidgetItem(self, QStringList(new_class_name))
            ni.setData(0, 11, QVariant(new_class_id))
            ni.setIcon(0, QIcon(u":/images/classe.png"))
            self.insertTopLevelItem(0, ni)
            ni.setCheckState(0, Qt.Unchecked)
            self.setHeaderLabel(QString(u"Classes (%i) Année (%s)" % (self.topLevelItemCount(),
                                                                      ay_name)))

            self.clearStatPage()

     
    def appendNewClassroomItem(self, class_item, classroom_name):
        class_id = class_item.data(0, 11).toInt()[0]
        query = QSqlQuery()
        query.prepare("INSERT INTO classroom(classroom_name, classroom_created_at, class_id) \
                       VALUES(:classroom_name, NOW(), :clsid)")
        query.bindValue(":classroom_name", classroom_name)
        query.bindValue(":clsid", class_id)
        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                    u"Database Error: %s" % query.lastError().text())
        else:
            new_classroom_id = query.lastInsertId().toInt()[0]
            ni = QTreeWidgetItem(class_item, QStringList(classroom_name))
            ni.setData(0, 11, QVariant(new_classroom_id))
            ni.setIcon(0, QIcon(u":/images/classroom-icon.png"))
            ni.setCheckState(0, Qt.Unchecked)
            class_item.addChild(ni)

            Class.list_items_room.append(ni)

            self.clearStatPage()

            #self.insertTopLevelItem(0, ni)
            #self.setHeaderLabel(QString(u"Classes (%i) Année (%s)" % (self.topLevelItemCount(),



    def addClassroom(self):
        current_class_item = self.currentItem()
        if current_class_item.isSelected() == True:
            reply = QInputDialog.getText(self, u"Salle - InterNotes",
                                      u"Ajouter une salle (%s) " % current_class_item.text(0),
                                      QLineEdit.Normal, QString())

            classroom_name = reply[0] #.replace(" ", "")
            if reply[1] == True and not classroom_name.isEmpty():
                self.appendNewClassroomItem(current_class_item, classroom_name)
                self.clearStatPage()
            else:
                return

   

    @staticmethod
    def isClassHasClassroom(class_id):
        query = QSqlQuery("SELECT classroom_id \
                           FROM classroom \
                           WHERE class_id = " + str(class_id))
        if query.exec_():
            if query.size() >= 1:
                return True
            else:
                return False


    @staticmethod
    def isClassroomHasStudent(classroom_id):
        query = QSqlQuery("SELECT student_id \
                           FROM student \
                           WHERE classroom_id = " + str(classroom_id))
        if query.exec_():
            if query.size() >= 1:
                return True
            else:
                return False

    
    @staticmethod
    def getClassroomsByClassId(class_id):
        data = []
        query = QSqlQuery("SELECT classroom_id, \
                                  classroom_name \
                           FROM classroom \
                           WHERE class_id = " + str(class_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while query.next():
                    row = {}
                    row['classroom_id'] = query.value(record.indexOf("classroom_id")).toInt()[0]
                    row['classroom_name'] = query.value(record.indexOf("classroom_name")).toString()
                    data.append(row)


        return data


    @staticmethod
    def getStudentsByClassroomId(crid):
        data = []
        query = QSqlQuery("SELECT \
                               student_id, \
                               student_first_name, \
                               student_last_name, \
                               student_photo_name\
                           FROM student \
                           WHERE classroom_id = " + str(crid))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while query.next():
                    row = {}
                    row['student_id'] = query.value(
                            record.indexOf("student_id")).toInt()[0]

                    row['student_first_name'] = query.value(
                            record.indexOf("student_first_name")).toString()

                    row['student_last_name'] = query.value(
                            record.indexOf("student_last_name")).toString()

                    row['student_photo_name'] = query.value(
                            record.indexOf("student_photo_name")).toString()

                    data.append(row)


        return data


    
    def showNewClassBox(self, ay_id, ay_name):
        dialog = QDialog(self)
        combo_ay = QComboBox()
        combo_ay.addItem(ay_name, QVariant(ay_id))

        line_class = QLineEdit()

        layout_form = QFormLayout()
        layout_form.addRow(u"Année academique: ", combo_ay)
        layout_form.addRow(u"Nom de la classe: ", line_class)

        group_form = QGroupBox("Nouvelle classe")
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
        dialog.setWindowTitle(u"Classe - InterNotes")

        self.connect(btn_ok, SIGNAL("clicked()"), dialog.accept)
        self.connect(btn_cancel, SIGNAL("clicked()"), dialog.reject)

        return dialog.exec_(), line_class.text()

    


    def editClassItem(self):
        class_item = self.currentItem()
        if class_item.isSelected() == True:
            class_name = class_item.text(0)
            reply = QInputDialog.getText(self, u"Classe - InterNotes",
                    u"Modifier la classe", QLineEdit.Normal, class_name)
            nclsname = reply[0] #.replace(" ", "")
            if reply[1] == True and not nclsname.isEmpty():
                #update from db
                new_class_name = nclsname
                class_id = class_item.data(0, 11).toInt()[0]

                query = QSqlQuery()
                query.prepare("UPDATE class \
                               SET class_name = :clsname, \
                                   class_updated_at = NOW() \
                               WHERE class_id = :clsid")
                query.bindValue(":clsid", class_id)
                query.bindValue(":clsname", new_class_name)
                if not query.exec_():
                    QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query.lastError().text())
                else:
                    class_item.setText(0, new_class_name)
                    self.clearStatPage()
            else:
                return


    def editClassroomItem(self):
        classroom_item = self.currentItem()
        if classroom_item.isSelected() == True and classroom_item.parent() is not None:
            classroom_name = classroom_item.text(0)
            reply = QInputDialog.getText(self, u"Salle - InterNotes",
                    u"Modifier la salle", QLineEdit.Normal, classroom_name)
            nclassroom_name = reply[0] #.replace(" ", "")
            if reply[1] == True and not nclassroom_name.isEmpty():
                #update from db
                new_classroom_name = nclassroom_name
                classroom_id = classroom_item.data(0, 11).toInt()[0]

                query = QSqlQuery()
                query.prepare("UPDATE classroom \
                               SET classroom_name = :name, \
                                   classroom_updated_at = NOW() \
                               WHERE classroom_id = :id")
                query.bindValue(":id", classroom_id)
                query.bindValue(":name", new_classroom_name)
                if not query.exec_():
                    QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query.lastError().text())
                else:
                    classroom_item.setText(0, new_classroom_name)
                    self.clearStatPage()
            else:
                return



    def deleteClassItem(self):
        class_item = self.currentItem()
        if class_item.isSelected() == True:
            reply = QMessageBox.question(self, "Supprimer?", 
                    u"Êtes vous sûr de vouloir supprimer definitivement du logiciel la classe <b>%s</b> " \
                    u"selectionnée?" % class_item.text(0), QMessageBox.No | QMessageBox.Yes,
                                                           QMessageBox.No)
            if reply == QMessageBox.Yes:
                #delete from db
                class_id = class_item.data(0, 11).toInt()[0]
                class_index = self.indexOfTopLevelItem(class_item)
                ayname = QString(u'')

                  
                query_ay = QSqlQuery("SELECT ay.academic_year_name \
                                      FROM class cl \
                                      INNER JOIN academic_year ay ON ay.academic_year_id = cl.academic_year_id \
                                      WHERE cl.class_id = " + str(class_id))
                if query_ay.exec_():
                    record = query_ay.record()
                    if not record.isEmpty():
                        while query_ay.next():
                            ayname = query_ay.value(record.indexOf("academic_year_name")).toString()

                query_ay.finish()



               
                query_pre = QSqlQuery("SELECT student_id \
                                       FROM student \
                                       WHERE class_id = " + str(class_id))
                if query_pre.exec_():
                    record = query_pre.record()
                    if not record.isEmpty():
                        while query_pre.next():
                            student_id = query_pre.value(record.indexOf("student_id")).toInt()[0]

                            self.student_tree.removeOldPhoto(student_id)

                query_pre.finish()


                query = QSqlQuery()
                query.prepare("DELETE m.*, cr.*, \
                                      std.*, \
                                      cl.* \
                               FROM class cl \
                               LEFT JOIN student std ON std.class_id = cl.class_id \
                               LEFT JOIN mark m ON m.student_id = std.student_id \
                               LEFT JOIN classroom cr ON cr.class_id = cl.class_id \
                               WHERE cl.class_id = :clsid")
                query.bindValue(":clsid", class_id)
                if not query.exec_():
                    QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query.lastError().text())
                else:
                    if class_item.childCount() > 0:
                        for c in range(0, class_item.childCount()):
                            child = class_item.child(c)
                            Class.list_items_room.remove(child)
                    self.student_tree.selectStudentsByClassroomId(class_item)
                    o_item = self.takeTopLevelItem(class_index)
                    self.setHeaderLabel(QString(
                        u"Classes (%i) Année (%s)" % (self.topLevelItemCount(), ayname)))

                    self.clearStatPage()

            elif reply == 2:
                return


    def deleteClassroomItem(self):
        classroom_item = self.currentItem()
        if classroom_item.isSelected() == True and classroom_item.parent() is not None:
            reply = QMessageBox.question(self, "Supprimer?", 
                    u"Êtes vous sûr de vouloir supprimer definitivement du logiciel la salle <b>%s</b> " \
                    u"selectionnée?" % classroom_item.text(0), QMessageBox.Yes | QMessageBox.No,
                                                               QMessageBox.No)
            if reply == QMessageBox.Yes:
                #delete from db
                classroom_id = classroom_item.data(0, 11).toInt()[0]
                classroom_index = classroom_item.parent().indexOfChild(classroom_item)

                  
                query_pre = QSqlQuery("SELECT student_id \
                                       FROM student \
                                       WHERE classroom_id = " + str(classroom_id))
                if query_pre.exec_():
                    record = query_pre.record()
                    if not record.isEmpty():
                        while query_pre.next():
                            student_id = query_pre.value(record.indexOf("student_id")).toInt()[0]

                            self.student_tree.removeOldPhoto(student_id)

                query_pre.finish()


                query = QSqlQuery()
                query.prepare("DELETE m.*, std.*, \
                                      cr.* \
                               FROM classroom cr \
                               LEFT JOIN student std ON std.classroom_id = cr.classroom_id \
                               LEFT JOIN mark m ON m.classroom_id = cr.classroom_id \
                               WHERE cr.classroom_id = :id")
                query.bindValue(":id", classroom_id)
                if not query.exec_():
                    QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query.lastError().text())
                else:
                    Class.list_items_room.remove(classroom_item)
                    self.student_tree.selectStudentsByClassroomId(classroom_item)
                    o_item = classroom_item.parent().takeChild(classroom_index)
                    #self.setHeaderLabel(QString(u"Classes  (%i)" % self.topLevelItemCount()))
                    self.clearStatPage()

            elif reply == 2:
                return
    

    def checkAllChildren(self, parent_item):
       for c in range(0, parent_item.childCount()):
           child = parent_item.child(c)
           child.setCheckState(0, Qt.Checked)

    def uncheckAllChildren(self, parent_item):
       for c in range(0, parent_item.childCount()):
           child = parent_item.child(c)
           child.setCheckState(0, Qt.Unchecked)


    def changeStateOfChildren(self, current_item):
        if current_item.parent() is None and current_item.childCount() > 0:
            # because we want only parents here :)
            if current_item.checkState(0) == Qt.Checked:
                self.checkAllChildren(current_item)
            elif current_item.checkState(0) == Qt.Unchecked:
                self.uncheckAllChildren(current_item)

    
    def contextMenuEvent(self, event):
        menu = QMenu()

        action_edit = tools.createAction(self,
                u"&Modifer la classe",
                self.editClassItem,
                "",
                ":/images/edit.png",
                u"Modifier la classe", u"Modifier la classe selectionnée")

        action_delete = tools.createAction(self, u"&Supprimer la classe", self.deleteClassItem, 
                "Ctrl+D",
                ":/images/button_cancel.png",
                u"Supprimer la classe selectionneé. Attention, "
                u"ceci supprimera toutes les dépendances (salle(s), "
                u"élèves(s)) rattachées à cette classe!")
   
        action_add_classroom = tools.createAction(self, u"&Ajouter une salle", self.addClassroom,
                "Ctrl+A",
                u":/images/classroom-icon.png",
                u"Ajouter une salle à la classe selectionnée")



        # classroom actions
        action_edit_classroom = tools.createAction(self,
                u"&Modifer la salle",
                self.editClassroomItem,
                "",
                ":/images/edit.png",
                u"Modifier la salle", u"Modifier la salle selectionnée")
    
        action_delete_classroom = tools.createAction(self, u"&Supprimer la salle",
                self.deleteClassroomItem,
                "Ctrl+D",
                ":/images/button_cancel.png",
                u"Supprimer la salle selectionnée. Attention, "
                u"ceci supprimera tout eventuel élève enregistré dans cette salle!")

        
        if self.currentItem() is None or self.currentItem().isSelected() == False:
            action_edit.setEnabled(False)
            action_delete.setEnabled(False)
            action_add_classroom.setEnabled(False)
            action_edit_classroom.setEnabled(False)
            action_delete_classroom.setEnabled(False)
        else:
            action_edit.setEnabled(True)
            action_delete.setEnabled(True)
            action_add_classroom.setEnabled(True)
            action_edit_classroom.setEnabled(True)
            action_delete_classroom.setEnabled(True)



        if self.currentItem() is not None and self.currentItem().parent() is not None:
            menu.addAction(action_edit_classroom)
            menu.addAction(action_delete_classroom)
            menu.exec_(event.globalPos())

        else:
            menu.addAction(action_edit)
            menu.addAction(action_delete)
            menu.addAction(action_add_classroom)
            menu.exec_(event.globalPos())






    @staticmethod
    def getClassNameById(class_id):
        class_name = QString('')
        query = QSqlQuery("SELECT class_name FROM class \
                           WHERE class_id = " + str(class_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    class_name = query.value(record.indexOf("class_name")).toString()

        return class_name
     


    @staticmethod
    def getClassroomNameById(classroom_id):
        classroom_name = QString('')
        query = QSqlQuery("SELECT classroom_name FROM classroom \
                           WHERE classroom_id = " + str(classroom_id))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    classroom_name = query.value(record.indexOf("classroom_name")).toString()

        return classroom_name



    @staticmethod
    def getAllTopicsByClassroomId(classroom_id):
        topics = []
        query = QSqlQuery("SELECT topic_id, \
                                  topic_name, \
                                  topic_coef, \
                                  topic_type, \
                                  topic_prof \
                           FROM topic \
                           WHERE classroom_id = " + \
                           str(classroom_id) + \
                           " ORDER BY topic_type DESC")
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    t = []
                    tid = query.value(record.indexOf("topic_id")).toInt()[0]
                    tname = query.value(record.indexOf("topic_name")).toString()
                    tcoef = query.value(record.indexOf("topic_coef")).toInt()[0]
                    ttype = query.value(record.indexOf("topic_type")).toString()
                    tprof = query.value(record.indexOf("topic_prof")).toString()

                    t.append(tid)
                    t.append(tname)
                    t.append(tcoef)
                    t.append(ttype)
                    t.append(tprof)

                    topics.append(t)
        else:
            #print "Database Error: %s" % db.lastError().text()
            print "SQL Error!"

        return topics



    @staticmethod
    def getSlicesAverageByMarkGroup(crid, mg):
        slices = []

        sql = "SELECT \
                ROUND((SUM(my.mycoef) / SUM(my.total_coef)),2)\
                      bs_mg_my \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                    * IF(t.topic_coef = 0, 1, t.topic_coef) \
                   )\
                   mycoef, t.topic_coef total_coef, \
                   m.student_id stid FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.classroom_id = :crid \
                 AND m.mark_group = :mg \
                 GROUP BY t.topic_id, m.student_id) my \
                 GROUP BY my.stid HAVING bs_mg_my <= 0"



        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":mg", mg)

        if query.exec_():
          slices.append(query.size())
        else:
            print "SQL Error!"


        query.finish()


        sql = "SELECT \
                ROUND((SUM(my.mycoef) / SUM(my.total_coef)),2)\
                      bs_mg_my \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                    * IF(t.topic_coef = 0, 1, t.topic_coef) \
                    ) \
                   mycoef, t.topic_coef total_coef, \
                   m.student_id stid FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.classroom_id = :crid \
                 AND m.mark_group = :mg \
                 GROUP BY t.topic_id, m.student_id) my \
                 GROUP BY my.stid HAVING bs_mg_my <= 8.50"


        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":mg", mg)

        if query.exec_():
          slices.append(query.size())
        else:
            print "SQL Error!"


        query.finish()

        
        sql = "SELECT \
                ROUND((SUM(my.mycoef) / SUM(my.total_coef)),2)\
                      bs_mg_my \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                    * IF(t.topic_coef = 0, 1, t.topic_coef) \
                    ) \
                   mycoef, t.topic_coef total_coef, \
                   m.student_id stid FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.classroom_id = :crid \
                 AND m.mark_group = :mg \
                 GROUP BY t.topic_id, m.student_id) my \
                 GROUP BY my.stid HAVING bs_mg_my \
                 BETWEEN 8.50 AND 10.00"


        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":mg", mg)

        if query.exec_():
          slices.append(query.size())
        else:
            print "SQL Error!"


        query.finish()

        sql = "SELECT \
                ROUND((SUM(my.mycoef) / SUM(my.total_coef)),2)\
                      bs_mg_my \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                    * IF(t.topic_coef = 0, 1, t.topic_coef) \
                    ) \
                   mycoef, t.topic_coef total_coef, \
                   m.student_id stid FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.classroom_id = :crid \
                 AND m.mark_group = :mg \
                 GROUP BY t.topic_id, m.student_id) my \
                 GROUP BY my.stid HAVING bs_mg_my >= 10.00"              


        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":mg", mg)

        if query.exec_():
          slices.append(query.size())
        else:
            print "SQL Error!"


        return slices




    @staticmethod
    def getFirstStudentAverageAndLastStudentAverageByMarkGroup(crid, mg):
        first_last = []
        avgs = []


        sql = "SELECT \
                ROUND((SUM(my.mycoef) / SUM(my.total_coef)),2)\
                      bs_mg_my \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                    * IF(t.topic_coef = 0, 1, t.topic_coef) \
                    ) \
                   mycoef, t.topic_coef total_coef, \
                   m.student_id stid FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.classroom_id = :crid \
                 AND m.mark_group = :mg \
                 GROUP BY t.topic_id, m.student_id) my \
                 GROUP BY my.stid ORDER BY bs_mg_my DESC"              



        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  avgs.append(
                            query.value(
                             record.indexOf("bs_mg_my")).toDouble()[0]
                            )

        else:
            print "SQL Error!"



        first_last.append(avgs[0])
        first_last.append(avgs[len(avgs) - 1])


        return first_last



    @staticmethod
    def getFirstStudentAverageAndStudentIdAndStudentNameByMarkGroup(crid, mg):
        first = []
        avgs = []

        sql = "SELECT \
                ROUND((SUM(my.mycoef) / SUM(my.total_coef)),2)\
                      bs_mg_my, my.std_id, my.std_fname , my.std_lname \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                    * IF(t.topic_coef = 0, 1, t.topic_coef) \
                    ) \
                   mycoef, t.topic_coef total_coef, \
                   m.student_id stid, \
                   s.student_id std_id , \
                   s.student_first_name std_fname, \
                   s.student_last_name std_lname\
                    FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 INNER JOIN student s ON s.student_id = m.student_id \
                 WHERE m.classroom_id = :crid \
                 AND m.mark_group = :mg \
                 GROUP BY t.topic_id, m.student_id) my \
                 GROUP BY my.stid ORDER BY bs_mg_my DESC"              



        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    row = {}
                    row["bs_mg_my"] = query.value(
                              record.indexOf("bs_mg_my")).toDouble()[0]
                             
                    row["std_id"] = query.value(
                              record.indexOf("std_id")).toString()

                    row["std_fname"] = query.value(
                              record.indexOf("std_fname")).toString()

                    row["std_lname"] = query.value(
                              record.indexOf("std_lname")).toString()

                    avgs.append(row)
        else:
            print "SQL Error!"



        try:
            first.append(avgs[0])
        except IndexError:
            first = 0

        return first














    @staticmethod
    def getClassroomAverageByMarkGroup(crid, mg):
        cr_avg = 0.0 
        avgs = []

        sql = "SELECT \
                ROUND((SUM(my.mycoef) / SUM(my.total_coef)),2)\
                      bs_mg_my \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                      * IF(t.topic_coef = 0, 1, t.topic_coef) \
                     ) \
                   mycoef, t.topic_coef total_coef, \
                   m.student_id stid FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.classroom_id = :crid \
                 AND m.mark_group = :mg \
                 GROUP BY t.topic_id, m.student_id) my \
                 GROUP BY my.stid"              

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  avgs.append(
                            query.value(
                             record.indexOf("bs_mg_my")).toDouble()[0]
                            )

        else:
            print "SQL Error!"

        a = 0
        s = 0.0
        while a < len(avgs):
            s += avgs[a]
            a += 1
        
        try:
            cr_avg = s / len(avgs) 
        except ZeroDivisionError:
            pass


        return round(cr_avg, 2)



    @staticmethod
    def getNumberOfStudentInThisClassroomById(crid):
        std_nb = 0
        query = QSqlQuery("SELECT COUNT(student_id) nb \
                           FROM student \
                           WHERE classroom_id = " + str(crid))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    std_nb = query.value(
                   record.indexOf("nb")).toInt()[0]

        return std_nb



    @staticmethod
    def getClassroomsIdAndNameByClassId(clid):
        data = []
        query = QSqlQuery("SELECT cr.classroom_id, \
                                  cr.classroom_name \
                           FROM classroom cr \
                           INNER JOIN class cl ON cr.class_id = cl.class_id \
                           WHERE cl.class_id = " + str(clid))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    row = {}
                    row["classroom_id"] = query.value(
                            record.indexOf("classroom_id")).toInt()[0]
                   
                    row["classroom_name"] = query.value(
                            record.indexOf("classroom_name")).toString()

                    data.append(row)
        
        else:
            print "SQL ERROR!"

        return data





    @staticmethod
    def getAllStudentsIdAndNameByClassroomId(crid):
        data = []
        query = QSqlQuery("SELECT student_id, \
                                  student_first_name, \
                                  student_last_name \
                           FROM student \
                           WHERE classroom_id = " + str(crid) + 
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



