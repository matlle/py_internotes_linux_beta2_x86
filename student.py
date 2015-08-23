#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, photopreview, academicyear, classe, infos, topic

import uuid

class Student(QTreeView):
    def __init__(self, in_stat_page, parent=None):
        super(Student, self).__init__(parent)

        self.stat_page = in_stat_page

        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setAlternatingRowColors(True)
        self.setIndentation(0)
        self.header().setDefaultAlignment(Qt.AlignCenter);

        #self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(QStringList(u"Elèves - Nom et prenoms (0)"))

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setDynamicSortFilter(True)

        self.setModel(self.proxy_model)

        self.infos = None
        self.list_room_id = []
        self.list_removables_marks = []
        self.list_removables_aways = []


        #self.updateStudentTree()

        #self.setHeaderLabel(QString(u"Elèves - Nom et prenoms (%i)" % self.topLevelItemCount()))

         
         

        # events
        self.connect(self, SIGNAL("doubleClicked(QModelIndex)"), 
            self.onEditStudent)
        


    def selectStudentsByClassroomId(self, current_item):
        #self.clear()
            if not self.currentIndex().isValid():
                self.infos.showStudentInfos(0)

            self.list_room_id = []
            for i in range(0, len(classe.Class.list_items_room)):
                critem = classe.Class.list_items_room[i]
                if critem.checkState(0) == Qt.Checked:
                    cr_id = critem.data(0, 11).toInt()[0]
                    self.list_room_id.append(cr_id)

            sql = QString('')
            if len(self.list_room_id) == 1:
                sql += "= " + QString.number(self.list_room_id[0])
            elif len(self.list_room_id) > 1:
                sql = QString('')
                for i in range(0, len(self.list_room_id)):
                    if i + 1 == len(self.list_room_id):
                        sql += "= " + QString.number(self.list_room_id[i])
                    else:
                        sql += "= " + QString.number(self.list_room_id[i]) + " OR classroom_id "


            if sql.isEmpty():
                del self.model
                self.model = QStandardItemModel(self)
                self.model.setHorizontalHeaderLabels(
                    QStringList(u"Elèves - Nom et prenoms (0)")) 
                self.proxy_model.setSourceModel(self.model)
                self.infos.showStudentInfos(0)
            else:
                qs = QString("SELECT student_id, \
                                     student_first_name, \
                                     student_last_name, \
                                     student_photo_name \
                              FROM student WHERE classroom_id " + sql)
                query = QSqlQuery(qs)
                if not query.exec_():
                    try:
                        QMessageBox.critical(self, "Error", 
                            QString("Database Error: %1").arg(db.lastError().text()))
                    except:
                        return
                else:
                    record = query.record()
                    del self.model
                    self.model = QStandardItemModel(self)
                    self.model.setHorizontalHeaderLabels(
                        QStringList(u"Elèves - Nom et prenoms (0)"))
                    self.proxy_model.setSourceModel(self.model)
                    if not record.isEmpty():
                        while(query.next()):
                            student_id = query.value(record.indexOf("student_id")).toInt()[0]
                            student_first_name = query.value(record.indexOf("student_first_name")).toString()
                            student_last_name = query.value(record.indexOf("student_last_name")).toString()
                            student_photo_name = query.value(record.indexOf("student_photo_name")).toString()

                            ni = QStandardItem(student_last_name + " " + student_first_name)
                            ni.setAccessibleText(QString.number(student_id))
                            ni.setEditable(False)
                            if student_photo_name is not None \
                                    and not student_photo_name.isEmpty() and not \
                                    QImage(student_photo_name).isNull():
                                ni.setIcon(QIcon(student_photo_name))
                            else:
                                ni.setIcon(QIcon(":/images/user-icon.png"));
                            self.model.appendRow(ni)
                            self.model.setHorizontalHeaderLabels(
                                QStringList(u"Elèves - Nom et prenoms (%i)" % 
                                    query.size()))
                    self.proxy_model.setSourceModel(self.model)





    def activeSaveBtn(self):
        if self.btn_save:
           self.btn_save.setEnabled(True)
   
    def activeSaveAwayBtn(self):
        if self.btn_save_away:
           self.btn_save_away.setEnabled(True)

    def activeNewAndCancelBtn(self):
        if self.combo_classroom.currentIndex() != -1:
            cr_index = self.combo_classroom.currentIndex()
            crid = self.combo_classroom.itemData(cr_index).toInt()[0]
            topics = topic.Topic.getAllTopicsByClassroomId(crid)
            if len(topics) > 0:
                self.btn_new_row.setEnabled(True)
                self.btn_cancel_notes.setEnabled(True)
                if self.btn_save:
                    self.btn_save.setEnabled(True)

            else:
                self.btn_new_row.setEnabled(False)
                self.btn_cancel_notes.setEnabled(False)
                if self.btn_save:
                    self.btn_save.setEnabled(True)
        else:
            self.btn_new_row.setEnabled(False)
            self.btn_cancel_notes.setEnabled(False)
            if self.btn_save:
                self.btn_save.setEnabled(False)

        self.table_view.setRowCount(0)
        self.activeDeleteBtn()



    def activeNewAndCancelAwayBtn(self):
        if self.combo_classroom.currentIndex() != -1:
            self.btn_new_row_away.setEnabled(True)
            self.btn_cancel_away.setEnabled(True)
            if self.btn_save_away:
                self.btn_save_away.setEnabled(True)
        else:
            self.btn_new_row_away.setEnabled(False)
            self.btn_cancel_away.setEnabled(False)
            if self.btn_save_away:
                self.btn_save_away.setEnabled(False)

        self.table_view_away.setRowCount(0)
        self.activeDeleteAwayBtn()


    def activeDeleteAwayBtn(self):
        if self.combo_classroom.currentIndex() != -1:
            if self.table_view_away.currentRow() >= 0:
                self.btn_delete_row_away.setEnabled(True)
            else:
                self.btn_delete_row_away.setEnabled(False)

        else:
            self.btn_delete_row_away.setEnabled(False)


    def activeDeleteBtn(self):
        if self.combo_classroom.currentIndex() != -1:
            if self.table_view.currentRow() >= 0:
                self.btn_delete_row.setEnabled(True)
            else:
                self.btn_delete_row.setEnabled(False)

        else:
            self.btn_delete_row.setEnabled(False)


    def activeOkBtn(self):
        if self.combo_classroom.currentIndex() != -1:
            self.btn_ok.setEnabled(True)
        else:
            self.btn_ok.setEnabled(False)


    def cancelAll(self):
        #self.table_view.setRowCount(0)
        self.setTableMarksByStudentIdAndByMarkGroup(0)
        self.list_removables_marks = []

    def cancelAllAway(self):
        #self.table_view.setRowCount(0)
        self.setTableAwayByStudentIdAndByMarkGroup(0)
        self.list_removables_aways = []


    def deleteRow(self):
        row = self.table_view.currentRow()

        id = self.table_view.item(row, 3).data(Qt.AccessibleTextRole).toInt()[0]
        if id:
            self.list_removables_marks.append(id)

        self.table_view.removeRow(row)
        self.activeDeleteBtn()
        self.activeSaveBtn()

        self.stat_page.stat_object_tree.updateStatObjectTree()
        self.stat_page.stat_feature_tree.clear()
        self.stat_page.stat_feature_tree.setHeaderLabel(u"")

        child = self.stat_page.stat_output.layout.takeAt(0)
        if child:
            child.widget().deleteLater()
        

    def deleteAwayRow(self):
        row = self.table_view_away.currentRow()

        id = self.table_view_away.item(row, 4).data(Qt.AccessibleTextRole).toInt()[0]
        if id:
            self.list_removables_aways.append(id)

        self.table_view_away.removeRow(row)
        self.activeDeleteAwayBtn()
        self.activeSaveAwayBtn()



    def addNewMarkRow(self):
        nb_row = self.table_view.rowCount()

        nb = nb_row + 1
        self.table_view.insertRow(nb_row)
        self.table_view.setRowHeight(nb_row, 20)

        spin_mark = QDoubleSpinBox()
        #spin_mark.setMinimum(1)

        spin_on = QSpinBox()
        spin_on.setMinimum(1)

        combo_topic = QComboBox()
        if self.combo_classroom.currentIndex() != -1:
            cr_index = self.combo_classroom.currentIndex()
            crid = self.combo_classroom.itemData(cr_index).toInt()[0]
            topics = topic.Topic.getAllTopicsByClassroomId(crid)
            for t in topics:
                combo_topic.addItem(t['topic_name'], QVariant(t['topic_id']))


        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat(u"dd/MM/yyyy")

        self.table_view.setCellWidget(nb_row, 0, combo_topic)
        self.table_view.setCellWidget(nb_row, 1, spin_mark)
        self.table_view.setCellWidget(nb_row, 2, spin_on)
        self.table_view.setItem(nb_row, 3, QTableWidgetItem())
        self.table_view.setCellWidget(nb_row, 4, date_edit)


        self.connect(combo_topic, SIGNAL("currentIndexChanged(int)"), 
                                     self.activeSaveBtn)

        self.connect(spin_mark, SIGNAL("valueChanged(double)"), 
                                     self.activeSaveBtn)

        self.connect(spin_on, SIGNAL("valueChanged(int)"), 
                                     self.activeSaveBtn)

        self.connect(date_edit, SIGNAL("dateChanged(QDate)"), 
                                     self.activeSaveBtn)

        self.stat_page.stat_object_tree.updateStatObjectTree()
        self.stat_page.stat_feature_tree.clear()
        self.stat_page.stat_feature_tree.setHeaderLabel(u"")

        child = self.stat_page.stat_output.layout.takeAt(0)
        if child:
            child.widget().deleteLater()





    def addNewAwayRow(self):
        nb_row = self.table_view_away.rowCount()

        nb = nb_row + 1
        self.table_view_away.insertRow(nb_row)
        self.table_view_away.setRowHeight(nb_row, 20)

        combo_justify = QComboBox()
        combo_justify.addItem(u"Non Justifiée")
        combo_justify.addItem(u"Justifiée")


        date_edit = QDateTimeEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat(u"dd/MM/yyyy")

        time_from_edit = QTimeEdit()
        time_from_edit.setDisplayFormat(u"hh:mm")

        time_to_edit = QTimeEdit()
        time_to_edit.setDisplayFormat(u"hh:mm")

        self.table_view_away.setCellWidget(nb_row, 0, date_edit)
        self.table_view_away.setCellWidget(nb_row, 1, time_from_edit)
        self.table_view_away.setCellWidget(nb_row, 2, time_to_edit)
        self.table_view_away.setCellWidget(nb_row, 3, combo_justify)
        self.table_view_away.setItem(nb_row, 4, QTableWidgetItem())


        self.connect(combo_justify, SIGNAL("currentIndexChanged(int)"), 
                                     self.activeSaveAwayBtn)

        self.connect(date_edit, SIGNAL("dateChanged(QDate)"), 
                                     self.activeSaveAwayBtn)


        self.connect(time_from_edit, SIGNAL("timeChanged(QTime)"), 
                                     self.activeSaveAwayBtn)

        self.connect(time_to_edit, SIGNAL("timeChanged(QTime)"), 
                                     self.activeSaveAwayBtn)




    def updateOldMark(self, mark_id, mark_mark, mark_level,
                            mark_observation, mark_date, mark_group, stid, tid, crid, ayid):
        query = QSqlQuery()
        query.prepare("UPDATE mark \
                       SET mark_mark = :mark, \
                           mark_level = :level, \
                           mark_observation = :observation, \
                           mark_date = :date, \
                           mark_group = :group, \
                           topic_id = :tid, \
                           student_id = :stid, \
                           classroom_id = :crid, \
                           academic_year_id = :ayid, \
                           mark_updated_at = NOW() \
                       WHERE mark_id = :mid")

        query.bindValue(":mid", mark_id)
        query.bindValue(":mark", mark_mark)
        query.bindValue(":level", mark_level)
        query.bindValue(":observation", mark_observation)
        query.bindValue(":date", mark_date)
        query.bindValue(":group", mark_group)
        query.bindValue(":stid", stid)
        query.bindValue(":tid", tid)
        query.bindValue(":crid", crid)
        query.bindValue(":ayid", ayid)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes", 
                    u"Database Error: %s" % query.lastError().text())

        else:
            self.stat_page.stat_object_tree.updateStatObjectTree()
            self.stat_page.stat_feature_tree.clear()
            self.stat_page.stat_feature_tree.setHeaderLabel(u"")

            child = self.stat_page.stat_output.layout.takeAt(0)
            if child:
                child.widget().deleteLater()


    def insertNewMark(self, mark_mark, mark_level,
                             mark_observation, mark_date, mark_group, stid, tid, crid, ayid):
        query = QSqlQuery()
        query.prepare("INSERT INTO mark \
                           (mark_mark, \
                            mark_level, \
                            mark_observation, \
                            mark_date, \
                            mark_group, \
                            student_id, \
                            topic_id, \
                            classroom_id, \
                            academic_year_id, \
                            mark_created_at) \
                           VALUES(:mark, \
                                  :level, \
                                  :observation, \
                                  :date, \
                                  :group, \
                                  :stid, \
                                  :tid, \
                                  :crid, \
                                  :ayid, \
                                  NOW() \
                                 ) \
                       ")

        query.bindValue(":mark", mark_mark)
        query.bindValue(":level", mark_level)
        query.bindValue(":observation", mark_observation)
        query.bindValue(":date", mark_date)
        query.bindValue(":group", mark_group)
        query.bindValue(":stid", stid)
        query.bindValue(":tid", tid)
        query.bindValue(":crid", crid)
        query.bindValue(":ayid", ayid)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes", 
                    u"Database Error: %s" % query.lastError().text())
        else:
            return query.lastInsertId().toInt()[0]
            self.stat_page.stat_object_tree.updateStatObjectTree()
            self.stat_page.stat_feature_tree.clear()
            self.stat_page.stat_feature_tree.setHeaderLabel(u"")

            child = self.stat_page.stat_output.layout.takeAt(0)
            if child:
                child.widget().deleteLater()





    def updateOldAway(self, away_id, away_date, away_time_from,
                            away_time_to, away_justify, away_motif,
                            away_period, stid):
        query = QSqlQuery()
        query.prepare("UPDATE away \
                       SET away_date = :date, \
                           away_time_from = :time_from, \
                           away_time_to = :time_to, \
                           away_justify = :justify, \
                           away_motif = :motif, \
                           away_period = :period, \
                           student_id = :stid, \
                           away_updated_at = NOW() \
                       WHERE away_id = :aid")

        query.bindValue(":aid", away_id)
        query.bindValue(":date", away_date)
        query.bindValue(":time_from", away_time_from)
        query.bindValue(":time_to", away_time_to)
        query.bindValue(":justify", away_justify)
        query.bindValue(":motif", away_motif)
        query.bindValue(":period", away_period)
        query.bindValue(":stid", stid)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes", 
                    u"Database Error: %s" % query.lastError().text())




    def insertNewAway(self, away_date, away_time_from,
                            away_time_to, away_justify, away_motif,
                            away_period, stid):
        query = QSqlQuery()
        query.prepare("INSERT INTO away \
                           (away_date, \
                            away_time_from, \
                            away_time_to, \
                            away_justify, \
                            away_motif, \
                            away_period, \
                            student_id, \
                            away_created_at) \
                           VALUES(:date, \
                                  :time_from, \
                                  :time_to, \
                                  :justify, \
                                  :motif, \
                                  :period, \
                                  :stid, \
                                  NOW() \
                                 ) \
                       ")

        query.bindValue(":date", away_date)
        query.bindValue(":time_from", away_time_from)
        query.bindValue(":time_to", away_time_to)
        query.bindValue(":justify", away_justify)
        query.bindValue(":motif", away_motif)
        query.bindValue(":period", away_period)
        query.bindValue(":stid", stid)

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes", 
                    u"Database Error: %s" % query.lastError().text())
        else:
            return query.lastInsertId().toInt()[0]








    def deleteRemovablesMarks(self):
        list_id = self.list_removables_marks
        s = ''
        if list_id:
            if len(list_id) == 1:
                s = '= ' + str(list_id[0])
            else:
                for m in range(0, len(list_id)):
                    if m + 1 == len(list_id):
                        s += '= ' + str(list_id[m])
                    else:
                        s += '= ' + str(list_id[m]) + " OR mark_id "
            
            sql = "DELETE FROM mark WHERE mark_id " + s
            
            query = QSqlQuery(sql)

            if not query.exec_():
                QMessageBox.critical(self, "Error - InterNotes",
                        u"Date Error: %s " % query.lastError().text())

            else:
                self.list_removables_marks = []
                self.stat_page.stat_object_tree.updateStatObjectTree()
                self.stat_page.stat_feature_tree.clear()
                self.stat_page.stat_feature_tree.setHeaderLabel(u"")

                child = self.stat_page.stat_output.layout.takeAt(0)
                if child:
                    child.widget().deleteLater()




    def deleteRemovablesAways(self):
        list_id = self.list_removables_marks
        s = ''
        if list_id:
            if len(list_id) == 1:
                s = '= ' + str(list_id[0])
            else:
                for m in range(0, len(list_id)):
                    if m + 1 == len(list_id):
                        s += '= ' + str(list_id[m])
                    else:
                        s += '= ' + str(list_id[m]) + " OR away_id "
            
            sql = "DELETE FROM away WHERE away_id " + s
            
            query = QSqlQuery(sql)

            if not query.exec_():
                QMessageBox.critical(self, "Error - InterNotes",
                        u"Date Error: %s " % query.lastError().text())



    def saveMarks(self, mark_data, stid, crid, ayid, flag=False):
        if len(mark_data) > 0:
            for m in range(0, len(mark_data)):
                if mark_data[m]['mark_level'] <= 1:
                    QMessageBox.critical(self, u"Error - InterNotes", u"Veuillez renseigner " + 
                                                u"le total de point pour chaque note")
                    return
                if 'mark_id' in mark_data[m]:
                    self.updateOldMark(mark_data[m]['mark_id'], mark_data[m]['mark_mark'], 
                               mark_data[m]['mark_level'], mark_data[m]['mark_observation'], 
                               mark_data[m]['mark_date'],
                               mark_data[m]['mark_group'], stid, mark_data[m]['topic_id'], crid, ayid) 

                else:
                    mid = self.insertNewMark(mark_data[m]['mark_mark'], mark_data[m]['mark_level'],
                                mark_data[m]['mark_observation'], 
                                mark_data[m]['mark_date'], mark_data[m]['mark_group'], stid,
                                mark_data[m]['topic_id'], crid, ayid)

                    self.stat_page.stat_object_tree.updateStatObjectTree()
                    self.stat_page.stat_feature_tree.clear()
                    self.stat_page.stat_feature_tree.setHeaderLabel(u"")

                    child = self.stat_page.stat_output.layout.takeAt(0)
                    if child:
                        child.widget().deleteLater()

                    # put the new mark_id here
                    if flag == True:
                        item_observation = mark_data[m]['item_observation']
                        item_observation.setData(Qt.AccessibleTextRole, 
                                   QVariant(mid))




    def saveAways(self, away_data, stid, flag=False):
        if len(away_data) > 0:
            for a in range(0, len(away_data)):
                """
                if away_data[a]['away_date'] <= 1:
                    QMessageBox.critical(self, u"Error - InterNotes",
                                         u"Veuillez renseigner " + 
                                         u"la date et les heures pour chaque absence")
                    return
                """
                if 'away_id' in away_data[a]:
                    self.updateOldAway(away_data[a]['away_id'], away_data[a]['away_date'], 
                               away_data[a]['away_time_from'], away_data[a]['away_time_to'], 
                               away_data[a]['away_justify'],
                               away_data[a]['away_motif'], away_data[a]['away_period'], stid) 

                else:
                    aid = self.insertNewAway(away_data[a]['away_date'], away_data[a]['away_time_from'],
                                away_data[a]['away_time_to'], 
                                away_data[a]['away_justify'], away_data[a]['away_motif'],
                                away_data[a]['away_period'], stid)

                    # put the new away_id here
                    if flag == True:
                        item_motif = away_data[a]['item_motif']
                        item_motif.setData(Qt.AccessibleTextRole, 
                                   QVariant(aid))






    def onClickedSaveBtn(self):
        data = self.getAllNewMarksFromTableView()     
        if not data:
            return
        self.saveMarks(data, self.stid, data[0]['classroom_id'], data[0]['academic_year_id'], True)
        if self.btn_save:
            self.btn_save.setEnabled(False)
        self.deleteRemovablesMarks()
   


    def onClickedSaveAwayBtn(self):
        data = self.getAllNewAwaysFromTableView() 
        if not data:
            return
        self.saveAways(data, self.stid, True)
        if self.btn_save_away:
            self.btn_save_away.setEnabled(False)
        self.deleteRemovablesAways()




    def getAllNewMarksFromTableView(self):
        marks = []
        if self.combo_classroom.currentIndex() != -1:
            ay_index = self.combo_ay.currentIndex()
            cr_index = self.combo_classroom.currentIndex()

            crid = self.combo_classroom.itemData(cr_index).toInt()[0]
            ayid = self.combo_ay.itemData(ay_index).toInt()[0]

            mark_group = self.combo_mark_group.currentText()

            if self.table_view.rowCount() > 0:
                nb_row = self.table_view.rowCount()
                for r in range(0, nb_row):
                    mark = {}
                    combo_topic = self.table_view.cellWidget(r, 0)
                    topic_index = combo_topic.currentIndex()
                    mark['topic_id'] = combo_topic.itemData(topic_index).toInt()[0]

                    mark_id = self.table_view.item(r, 3).data(Qt.AccessibleTextRole).toInt()[0]
                    if mark_id:
                        mark['mark_id'] = mark_id 
                    mark['mark_mark'] = self.table_view.cellWidget(r, 1).value()
                    mark['mark_level'] = self.table_view.cellWidget(r, 2).value()

                    mark['item_observation'] = self.table_view.item(r, 3)
                    mark['mark_observation'] = self.table_view.item(r, 3).text()

                    #self.student_birth_date.date().toString("dd/MM/yyyy"),

                    date_edit = self.table_view.cellWidget(r, 4)
                    mark['mark_date'] = date_edit.date().toString("dd/MM/yyyy")

                    mark['mark_group'] = mark_group
                    mark['classroom_id'] = crid
                    mark['academic_year_id'] = ayid

                    marks.append(mark)
        
        return marks





    def getAllNewAwaysFromTableView(self):
        aways = []
        if self.combo_classroom.currentIndex() != -1:

            mark_group = self.combo_mark_group_away.currentText()

            if self.table_view_away.rowCount() > 0:
                nb_row = self.table_view_away.rowCount()
                for r in range(0, nb_row):
                    away = {}
                    date_edit = self.table_view_away.cellWidget(r, 0)
                    away['away_date'] = date_edit.date().toString("dd/MM/yyyy")

                    time_from_edit = self.table_view_away.cellWidget(r, 1)
                    away['away_time_from'] = time_from_edit.time().toString("hh:mm")

                    time_to_edit = self.table_view_away.cellWidget(r, 2)
                    away['away_time_to'] = time_to_edit.time().toString("hh:mm")


                    combo_justify = self.table_view_away.cellWidget(r, 3)
                    away['away_justify'] = combo_justify.currentText() 

                    away_id = self.table_view_away.item(r, 4).data(Qt.AccessibleTextRole).toInt()[0]
                    if away_id:
                        away['away_id'] = away_id 

                    away['item_motif'] = self.table_view_away.item(r, 4)
                    away['away_motif'] = self.table_view_away.item(r, 4).text()

                    #self.student_birth_date.date().toString("dd/MM/yyyy"),

                    away['away_period'] = mark_group 

                    aways.append(away)
        
        return aways





    def isStudentHasMarksInThisClassroomId(self, crid):
        query = QSqlQuery("SELECT * FROM mark WHERE classroom_id = " + str(crid))
        if query.exec_():
            if query.size() >= 1:
                return True
            else:
                return False


    def setTableMarksByClassroomIndexChanged(self):
        mark_group_index = self.combo_mark_group.currentIndex()
        self.combo_mark_group.setCurrentIndex(-1)
        self.combo_mark_group.setCurrentIndex(0)
        self.setTableMarksByStudentIdAndByMarkGroup(0)
        


    def setTableMarksByStudentIdAndByMarkGroup(self, group_index):
        if self.combo_classroom.currentIndex() == -1 or self.stid == None:
            return
        else: 
            ay_index = self.combo_ay.currentIndex()
            cr_index = self.combo_classroom.currentIndex()
            crid = self.combo_classroom.itemData(cr_index).toInt()[0]
            if self.isStudentHasMarksInThisClassroomId(crid) == False:
                return

        mark_group = self.combo_mark_group.currentText()

        query = QSqlQuery()
        query.prepare("SELECT * \
                       FROM mark m \
                       INNER JOIN topic t USING(topic_id) \
                       WHERE student_id = :stid AND \
                             mark_group = :group \
                       ORDER BY t.topic_name, mark_date DESC")
        query.bindValue(":stid", self.stid)
        query.bindValue(":group", mark_group)

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
                    mark_id = query.value(record.indexOf("mark_id")).toInt()[0]
                    mark_mark = query.value(record.indexOf("mark_mark")).toDouble()[0]
                    mark_level = query.value(record.indexOf("mark_level")).toInt()[0]
                    mark_observation = query.value(record.indexOf("mark_observation")).toString()

                    mark_date_string = query.value(record.indexOf("mark_date")).toString()
                    l_date = mark_date_string.split("/")
                    y = l_date[2].toInt()[0]
                    m = l_date[1].toInt()[0]
                    d = l_date[0].toInt()[0]
                    new_date = QDate(y, m, d)
                    mark_date_edit = QDateEdit(new_date)
                    mark_date_edit.setCalendarPopup(True)
                    mark_date_edit.setDisplayFormat(u"dd/MM/yyyy")

                    topic_id = query.value(record.indexOf("topic_id")).toInt()[0]

                    #item_name = QTableWidgetItem(topic_name)
                    #item_name.setData(Qt.AccessibleTextRole, QVariant(topic_id))

                    row['mark_id'] = mark_id
                    row['mark_mark'] = mark_mark 
                    row['mark_level'] = mark_level
                    row['mark_observation'] = mark_observation
                    row['mark_date'] = mark_date_edit 
                    row['topic_id'] = topic_id 
                    items.append(row)
             

                for i in range(0, len(items)):

                    combo_topic = QComboBox()
                    if self.combo_classroom.currentIndex() != -1:
                        cr_index = self.combo_classroom.currentIndex()
                        crid = self.combo_classroom.itemData(cr_index).toInt()[0]
                        topics = topic.Topic.getAllTopicsByClassroomId(crid)
                        for t in topics:
                            combo_topic.addItem(t['topic_name'], QVariant(t['topic_id']))
                        mark_topic_name = topic.Topic.getNameById(items[i]['topic_id']) 
                        index = combo_topic.findText(mark_topic_name)
                        combo_topic.setCurrentIndex(index)

                    self.table_view.setCellWidget(i, 0, combo_topic)



                    spin_mark = QDoubleSpinBox()
                    #spin_mark.setMinimum(1)
                    spin_mark.setValue(items[i]['mark_mark'])
                    self.table_view.setCellWidget(i, 1, spin_mark)

                    spin_level = QSpinBox()
                    spin_level.setMinimum(1)
                    spin_level.setValue(items[i]['mark_level'])
                    self.table_view.setCellWidget(i, 2, spin_level)
                    
                    item_observation = QTableWidgetItem(items[i]['mark_observation'])
                    item_observation.setData(Qt.AccessibleTextRole, QVariant(items[i]['mark_id']))
                    self.table_view.setItem(i, 3, item_observation)


                    self.table_view.setCellWidget(i, 4, items[i]['mark_date'])



                    self.connect(combo_topic, SIGNAL("currentIndexChanged(int)"), 
                                     self.activeSaveBtn)

                    self.connect(spin_mark, SIGNAL("valueChanged(double)"), 
                                     self.activeSaveBtn)

                    self.connect(spin_level, SIGNAL("valueChanged(int)"), 
                                     self.activeSaveBtn)

                    self.connect(items[i]['mark_date'], SIGNAL("dateChanged(QDate)"), 
                                     self.activeSaveBtn)


        self.table_view.sortItems(4)




    def setTableAwayByStudentIdAndByMarkGroup(self, group_index):
        if self.combo_classroom.currentIndex() == -1 or self.stid == None:
            return
        else: 
            ay_index = self.combo_ay.currentIndex()
            cr_index = self.combo_classroom.currentIndex()
            crid = self.combo_classroom.itemData(cr_index).toInt()[0]
            if self.isStudentHasMarksInThisClassroomId(crid) == False:
                return

        mark_group = self.combo_mark_group_away.currentText()

        query = QSqlQuery()
        query.prepare("SELECT * \
                       FROM away a \
                       WHERE student_id = :stid AND \
                             away_period = :period \
                       ORDER BY a.away_date DESC")
        query.bindValue(":stid", self.stid)
        query.bindValue(":period", mark_group)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                self.table_view_away.setRowCount(query.size())
                nb_row = query.size()
                items = []
                for r in range(0, nb_row):
                    self.table_view_away.setRowHeight(r, 20)
                while query.next():
                    row = {}
                    away_id = query.value(record.indexOf("away_id")).toInt()[0]
                    away_justify = query.value(record.indexOf("away_justify")).toString()
                    away_motif = query.value(record.indexOf("away_motif")).toString()

                    away_date_string = query.value(record.indexOf("away_date")).toString()
                    l_date = away_date_string.split("/")
                    y = l_date[2].toInt()[0]
                    m = l_date[1].toInt()[0]
                    d = l_date[0].toInt()[0]
                    new_date = QDate(y, m, d)
                    away_date_edit = QDateEdit(new_date)
                    away_date_edit.setCalendarPopup(True)
                    away_date_edit.setDisplayFormat(u"dd/MM/yyyy")


                    away_time_from_string = query.value(record.indexOf("away_time_from")).toString()
                    l_time = away_time_from_string.split(":") 
                    h = l_time[0].toInt()[0]
                    m = l_time[1].toInt()[0]
                    new_time = QTime(h, m)
                    away_time_from_edit = QTimeEdit()
                    away_time_from_edit.setDisplayFormat(u"hh:mm")
                    away_time_from_edit.setTime(new_time)


                    away_time_to_string = query.value(record.indexOf("away_time_to")).toString()
                    l_time = away_time_to_string.split(":") 
                    h = l_time[0].toInt()[0]
                    m = l_time[1].toInt()[0]
                    new_time = QTime(h, m)
                    away_time_to_edit = QTimeEdit()
                    away_time_to_edit.setDisplayFormat(u"hh:mm")
                    away_time_to_edit.setTime(new_time)

                    row['away_id'] = away_id
                    row['away_date'] = away_date_edit
                    row['away_time_from'] = away_time_from_edit
                    row['away_time_to'] = away_time_to_edit
                    row['away_justify'] = away_justify
                    row['away_motif'] = away_motif
                    items.append(row)
             

                for i in range(0, len(items)):
                    self.table_view_away.setCellWidget(i, 0, items[i]['away_date'])

                    self.table_view_away.setCellWidget(i, 1, items[i]['away_time_from'])
                    self.table_view_away.setCellWidget(i, 2, items[i]['away_time_to'])

                    combo_justify = QComboBox()
                    combo_justify.addItem(u"Non Justifiée")
                    combo_justify.addItem(u"Justifiée")
                    index = combo_justify.findText(items[i]["away_justify"])
                    combo_justify.setCurrentIndex(index)

                    self.table_view_away.setCellWidget(i, 3, combo_justify)

                    
                    item_motif = QTableWidgetItem(items[i]['away_motif'])
                    item_motif.setData(Qt.AccessibleTextRole, QVariant(items[i]['away_id']))
                    self.table_view_away.setItem(i, 4, item_motif)


                    self.connect(items[i]['away_time_from'], SIGNAL("timeChanged(QTime)"), 
                                     self.activeSaveAwayBtn)

                    self.connect(items[i]['away_time_to'], SIGNAL("timeChanged(QTime)"), 
                                     self.activeSaveAwayBtn)


                    self.connect(items[i]['away_date'], SIGNAL("dateChanged(QDate)"), 
                                     self.activeSaveBtn)

                    self.connect(combo_justify, SIGNAL("currentIndexChanged(int)"), 
                                     self.activeSaveBtn)



        self.table_view_away.sortItems(0)





                    
    def saveNewMarks(self, marks, student_id, classroom_id):
        for m in range(0, len(marks)):
            if marks[m]['mark_level'] <= 1:
                QMessageBox.critical(self, u"Error - InterNotes", u"Impossible d'enregistrer " +
                                       u"le(s) note(s). Veuillez renseigner " + 
                                       u"le total de point pour chaque note")
                return
            query = QSqlQuery()
            query.prepare("INSERT INTO mark( \
                                       mark_mark, \
                                       mark_level, \
                                       mark_observation, \
                                       mark_date, \
                                       mark_group, \
                                       student_id, \
                                       topic_id, \
                                       classroom_id, \
                                       academic_year_id, \
                                       mark_created_at) \
                                   VALUES( \
                                        :mark, \
                                        :level, \
                                        :observation, \
                                        :date, \
                                        :group, \
                                        :stid, \
                                        :tid, \
                                        :crid, \
                                        :ayid, \
                                        NOW())")

            query.bindValue(":mark", marks[m]['mark_mark'])
            query.bindValue(":level", marks[m]['mark_level'])
            query.bindValue(":observation", marks[m]['mark_observation'])
            query.bindValue(":date", marks[m]['mark_date'])
            query.bindValue(":group", marks[m]['mark_group'])
            query.bindValue(":stid", student_id)
            query.bindValue(":tid", marks[m]['topic_id'])
            query.bindValue(":crid", classroom_id)
            query.bindValue(":ayid", marks[m]['academic_year_id'])

            if not query.exec_():
                QMessageBox.critical(self, "Error - InterNotes",
                    u"Database Error: %s" % query.lastError().text())
                return
            else:
                self.stat_page.stat_object_tree.updateStatObjectTree()
                self.stat_page.stat_feature_tree.clear()
                self.stat_page.stat_feature_tree.setHeaderLabel(u"")

                child = self.stat_page.stat_output.layout.takeAt(0)
                if child:
                    child.widget().deleteLater()



    def appendNewStudentItem(self, infos):
        ayid = infos['ay_id']
        clid = infos['class_id']
        crid = infos['classroom_id']
        
        marks = infos['marks']

        query = QSqlQuery()
        query.prepare("INSERT INTO student(\
                           student_first_name, \
                           student_last_name, \
                           student_birth_date, \
                           student_birth_place, \
                           student_genre, \
                           student_height, \
                           student_matricule, \
                           student_matricule_ministeriel, \
                           student_statut, \
                           student_previous_school, \
                           student_previous_classroom, \
                           student_redoubler, \
                           student_email, \
                           student_phone1, \
                           student_phone2, \
                           student_phone3, \
                           student_photo_name, \
                           student_created_at, \
                           academic_year_id, \
                           class_id, \
                           classroom_id) \
                       VALUES( \
                           :first_name, \
                           :last_name, \
                           :birth_date, \
                           :birth_place, \
                           :genre, \
                           :height, \
                           :matricule, \
                           :matricule_ministeriel, \
                           :statut, \
                           :previous_school, \
                           :previous_classroom, \
                           :redoubler, \
                           :email, \
                           :phone1, \
                           :phone2, \
                           :phone3, \
                           :photo_name, \
                           NOW(), \
                           :ay_id, \
                           :clid, \
                           :crid)")

        query.bindValue(":first_name", infos['student_first_name'])
        query.bindValue(":last_name", infos['student_last_name'])
        query.bindValue(":birth_date", infos['student_birth_date'])
        query.bindValue(":birth_place", infos['student_birth_place'])
        query.bindValue(":genre", infos['student_genre'])
        query.bindValue(":height", infos['student_height'])
        query.bindValue(":matricule", infos['student_matricule'])
        query.bindValue(":matricule_ministeriel", infos['student_matricule_ministeriel'])
        query.bindValue(":statut", infos['student_statut'])
        query.bindValue(":previous_school", infos['student_previous_school'])
        query.bindValue(":previous_classroom", infos['student_previous_classroom'])
        query.bindValue(":redoubler", infos['student_redoubler'])
        query.bindValue(":email", infos['student_email'])
        query.bindValue(":phone1", infos['student_phone1'])
        query.bindValue(":phone2", infos['student_phone2'])
        query.bindValue(":phone3", infos['student_phone3'])
        query.bindValue(":photo_name", infos['new_photo_file_name'])
        query.bindValue(":ayid", ayid)
        query.bindValue(":clid", clid)
        query.bindValue(":crid", crid)
        if not query.exec_():
            QMessageBox.critical(self, u"Error - InterNotes",
                    u"Database Error: %s" % query.lastError().text())
        else:
            new_student_id = query.lastInsertId().toInt()[0]
            if marks:
                self.saveNewMarks(marks, new_student_id, crid)
            ni = QStandardItem(infos['student_last_name'] + " " + 
                                                   infos['student_first_name'])
            #ni.setData(0, 11, QVariant(new_student_id))
            ni.setAccessibleText(QString.number(new_student_id))
            ni.setEditable(False)
            if infos['new_photo_file_name'] is not None and not \
                    infos['new_photo_file_name'].isEmpty() and not \
                    QImage(infos['new_photo_file_name']).isNull():
                ni.setIcon(QIcon(infos['new_photo_file_name']))
            else:
                ni.setIcon(QIcon(":/images/user-icon.png"))

            query.finish()
            
            std_nb = 0
            if len(self.list_room_id):
                if crid in self.list_room_id:
                    self.model.appendRow(ni)

                    for id in range(0, len(self.list_room_id)):
                        std_nb += classe.Class.getNumberOfStudentInThisClassroomById(
                                self.list_room_id[id])

                    self.model.setHorizontalHeaderLabels(
                             QStringList(u"Elèves - Nom et prenoms (%i)" % std_nb))

             
            self.stat_page.stat_object_tree.updateStatObjectTree()
            self.stat_page.stat_feature_tree.clear()
            self.stat_page.stat_feature_tree.setHeaderLabel(u"")

            child = self.stat_page.stat_output.layout.takeAt(0)
            if child:
                child.widget().deleteLater()


            
            
    
    
    
    
    def editStudentItem(self, infos):
        ayid = infos['ay_id']
        clid = infos['class_id']
        crid = infos['classroom_id']
        stid = infos['student_id']

        mark_data = infos['mark_data']

        current_item = infos['item']

        query = QSqlQuery()
        query.prepare("UPDATE student \
                       SET student_first_name = :first_name, \
                           student_last_name = :last_name, \
                           student_birth_date = :birth_date, \
                           student_birth_place = :birth_place, \
                           student_genre = :genre, \
                           student_height = :height, \
                           student_matricule = :matricule, \
                           student_matricule_ministeriel = :matricule_ministeriel, \
                           student_statut = :statut, \
                           student_previous_school = :previous_school, \
                           student_previous_classroom = :previous_classroom, \
                           student_redoubler = :redoubler, \
                           student_email = :email, \
                           student_phone1 = :phone1, \
                           student_phone2 = :phone2, \
                           student_phone3 = :phone3, \
                           student_photo_name = :photo_name, \
                           student_updated_at = NOW(), \
                           academic_year_id = :ayid, \
                           class_id = :clid, \
                           classroom_id = :crid \
                       WHERE student_id = :stid")

        query.bindValue(":stid", stid)
        query.bindValue(":first_name", infos['student_first_name'])
        query.bindValue(":last_name", infos['student_last_name'])
        query.bindValue(":birth_date", infos['student_birth_date'])
        query.bindValue(":birth_place", infos['student_birth_place'])
        query.bindValue(":genre", infos['student_genre'])
        query.bindValue(":height", infos['student_height'])
        query.bindValue(":matricule", infos['student_matricule'])
        query.bindValue(":matricule_ministeriel", infos['student_matricule_ministeriel'])
        query.bindValue(":statut", infos['student_statut'])
        query.bindValue(":previous_school", infos['student_previous_school'])
        query.bindValue(":previous_classroom", infos['student_previous_classroom'])
        query.bindValue(":redoubler", infos['student_redoubler'])
        query.bindValue(":email", infos['student_email'])
        query.bindValue(":phone1", infos['student_phone1'])
        query.bindValue(":phone2", infos['student_phone2'])
        query.bindValue(":phone3", infos['student_phone3'])
        
        if infos['new_photo_file_name'] is not None and not infos['new_photo_file_name'].isEmpty():
            query.bindValue(":photo_name", infos['new_photo_file_name'])
            self.removeOldPhoto(stid)
        else:
            query.bindValue(":photo_name", infos['student_photo_file_name'])

        query.bindValue(":ayid", ayid)
        query.bindValue(":clid", clid)
        query.bindValue(":crid", crid)
       

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                    u"Database Error: %s" % query.lastError().text())
        else:
            query.finish()
            self.saveMarks(mark_data, stid, crid, ayid)
            query = QSqlQuery("SELECT student_first_name, \
                                      student_last_name, \
                                      student_photo_name \
                               FROM student \
                               WHERE student_id = " + str(stid))
            if not query.exec_():
                QMessageBox.critical(self, "Error - InterNotes",
                        u"Database Error: %s " % query.lastError().text())
            else:
                record = query.record()
                if not record.isEmpty():
                    while query.next():
                        new_first_name = query.value(record.indexOf("student_first_name")).toString()
                        new_last_name = query.value(record.indexOf("student_last_name")).toString()
                        new_photo_name  = query.value(record.indexOf("student_photo_name")).toString()

                        #ni = QTreeWidgetItem(self, QStringList(infos['student_last_name'] + " " + 
                        #                                       infos['student_first_name']))
                        current_item.setText(new_last_name + " " + new_first_name)
                        if new_photo_name is not None and not \
                                new_photo_name.isEmpty() and not \
                                QImage(new_photo_name).isNull():
                            current_item.setIcon(QIcon(new_photo_name))
                        else:
                            current_item.setIcon(QIcon(":/images/user-icon.png"))
                        
                        #self.insertTopLevelItem(0, current_item)
    
    
                        self.stat_page.stat_object_tree.updateStatObjectTree()
                        self.stat_page.stat_feature_tree.clear()
                        self.stat_page.stat_feature_tree.setHeaderLabel(u"")

                        child = self.stat_page.stat_output.layout.takeAt(0)
                        if child:
                            child.widget().deleteLater()
    
    




    def getStudentInfosById(self, student_id):
       row = {}
       query = QSqlQuery("SELECT std.*, \
                                 cr.classroom_name \
                          FROM student std \
                          INNER JOIN classroom cr ON cr.classroom_id = std.classroom_id \
                          WHERE std.student_id = " + str(student_id))

       if not query.exec_():
           QMessageBox.critical(self, "Error - InterNotes",
                   u"Database Error: %s " % query.lastError().text())
       else:
           record = query.record()
           if not record.isEmpty():
               while query.next():
                   row['student_id'] = query.value(record.indexOf("student_id")).toInt()[0]
                   row['academic_year_id'] = query.value(record.indexOf("academic_year_id")).toInt()[0]
                   row['class_id'] = query.value(record.indexOf("class_id")).toInt()[0]
                   row['classroom_id'] = query.value(record.indexOf("classroom_id")).toInt()[0]
                   row['classroom_name'] = query.value(record.indexOf("classroom_name")).toString()
                   row['student_first_name'] = query.value(record.indexOf("student_first_name")).toString()
                   row['student_last_name'] = query.value(record.indexOf("student_last_name")).toString()
                   row['student_birth_date'] = query.value(record.indexOf("student_birth_date")).toString()
                   row['student_birth_place'] = query.value(record.indexOf("student_birth_place")).toString()
                   row['student_genre'] = query.value(record.indexOf("student_genre")).toString()
                   row['student_height'] = query.value(record.indexOf("student_height")).toInt()[0]
                   row['student_matricule'] = query.value(record.indexOf("student_matricule")).toString()
                   row['student_matricule_ministeriel'] = query.value(record.indexOf("student_matricule_ministeriel")).toString()
                   row['student_previous_school'] = query.value(record.indexOf("student_previous_school")).toString()
                   row['student_previous_classroom'] = query.value(record.indexOf("student_previous_classroom")).toString()
                   row['student_statut'] = query.value(record.indexOf("student_statut")).toString()
                   row['student_redoubler'] = query.value(record.indexOf("student_redoubler")).toString()
                   row['student_email'] = query.value(record.indexOf("student_email")).toString()
                   row['student_phone1'] = query.value(record.indexOf("student_phone1")).toString()
                   row['student_phone2'] = query.value(record.indexOf("student_phone2")).toString()
                   row['student_phone3'] = query.value(record.indexOf("student_phone3")).toString()
                   row['student_photo_name'] = query.value(record.indexOf("student_photo_name")).toString()

       return row


    def getStudentMarksById(self, student_id):
       row = {}
       query = QSqlQuery("SELECT std.*, \
                                 cr.classroom_name \
                          FROM student std \
                          INNER JOIN classroom cr ON cr.classroom_id = std.classroom_id \
                          WHERE std.student_id = " + str(student_id))

       if not query.exec_():
           QMessageBox.critical(self, "Error - InterNotes",
                   u"Database Error: %s " % query.lastError().text())
       else:
           record = query.record()
           if not record.isEmpty():
               while query.next():
                   row['student_id'] = query.value(record.indexOf("student_id")).toInt()[0]
                   row['academic_year_id'] = query.value(record.indexOf("academic_year_id")).toInt()[0]
                   row['class_id'] = query.value(record.indexOf("class_id")).toInt()[0]
                   row['classroom_id'] = query.value(record.indexOf("classroom_id")).toInt()[0]
                   row['classroom_name'] = query.value(record.indexOf("classroom_name")).toString()
                   row['student_first_name'] = query.value(record.indexOf("student_first_name")).toString()
                   row['student_last_name'] = query.value(record.indexOf("student_last_name")).toString()
                   row['student_birth_date'] = query.value(record.indexOf("student_birth_date")).toString()
                   row['student_birth_place'] = query.value(record.indexOf("student_birth_place")).toString()
                   row['student_genre'] = query.value(record.indexOf("student_genre")).toString()
                   row['student_height'] = query.value(record.indexOf("student_height")).toInt()[0]
                   row['student_matricule'] = query.value(record.indexOf("student_matricule")).toString()
                   row['student_matricule_ministeriel'] = query.value(record.indexOf("student_matricule_ministeriel")).toString()
                   row['student_previous_school'] = query.value(record.indexOf("student_previous_school")).toString()
                   row['student_redoubler'] = query.value(record.indexOf("student_redoubler")).toString()
                   row['student_email'] = query.value(record.indexOf("student_email")).toString()
                   row['student_phone1'] = query.value(record.indexOf("student_phone1")).toString()
                   row['student_phone2'] = query.value(record.indexOf("student_phone2")).toString()
                   row['student_phone3'] = query.value(record.indexOf("student_phone3")).toString()
                   row['student_photo_name'] = query.value(record.indexOf("student_photo_name")).toString()

       return row





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

    
    def setClassComboBoxByAcademicYearId(self, ay_index):
        ay_id = self.combo_ay.itemData(ay_index).toInt()[0]
        classes = self.getClassesByAcademicYearId(ay_id)
        self.combo_class.clear()
        for c in classes:
            self.combo_class.addItem(c['class_name'], QVariant(c['class_id']))
   


    def setMarkGroupComboBoxByAcademicYearId(self, ay_index):
        if self.combo_classroom.currentIndex() != -1:
            #cr_index = self.combo_classroom.currentIndex()
            #crid = self.combo_classroom.itemData(cr_index).toInt()[0]
            #if self.isStudentHasMarksInThisClassroomId(crid) == True:
            ay_id = self.combo_ay.itemData(ay_index).toInt()[0]
            #classes = self.getClassesByAcademicYearId(ay_id)
            period = academicyear.AcademicYear.getPeriodById(ay_id)
            self.combo_mark_group.clear()
            try:
                self.combo_mark_group_away.clear()
            except:
                pass
            if period == 'quarter':
                self.combo_mark_group.addItem(u"1er Trimestre")
                self.combo_mark_group.addItem(u"2ème Trimestre")
                self.combo_mark_group.addItem(u"3ème Trimestre")

                try:
                    self.combo_mark_group_away.addItem(u"1er Trimestre")
                    self.combo_mark_group_away.addItem(u"2ème Trimestre")
                    self.combo_mark_group_away.addItem(u"3ème Trimestre")
                except:
                    pass

            elif period == 'semester':
                try:
                    self.combo_mark_group.addItem(u"1er Semestre")
                    self.combo_mark_group.addItem(u"2ème Semestre")
                except:
                    pass


                self.combo_mark_group_away.addItem(u"1er Semestre")
                self.combo_mark_group_away.addItem(u"2ème Semestre")

        else:
            self.combo_mark_group.clear()
            try:
                self.combo_mark_group_away.clear()
            except:
                pass



    def setClassroomComboBoxByClassId(self, class_index):
        class_id = self.combo_class.itemData(class_index).toInt()[0]
        rooms = self.getClassroomsByClassId(class_id)
        self.combo_classroom.clear()
        for r in rooms:
            self.combo_classroom.addItem(r['classroom_name'], QVariant(r['classroom_id']))

    
    def showNewStudentDialog(self):
        dialog = QDialog(self)
        self.new_photo_file_name = QString('')
        self.stid = None

        self.combo_ay = QComboBox()
        self.combo_ay.setMinimumWidth(200)
        self.combo_ay.setSizeAdjustPolicy(QComboBox.AdjustToContents) 
        self.updateAcademicYearComboBox()

        self.combo_class = QComboBox()
        self.combo_class.setMinimumWidth(200)
        self.combo_class.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        self.combo_classroom = QComboBox()
        self.combo_classroom.setMinimumWidth(200)
        self.combo_classroom.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        label_ay = QLabel(u"Année academique: ")
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

        
        #page info
        page_info = QWidget()

        self.btn_photo = QPushButton()
        self.btn_photo.setIcon(QIcon(":/images/user-icon.png"))
        self.btn_photo.setIconSize(QSize(200, 200))
        layout_photo = QGridLayout()
        layout_photo.addWidget(self.btn_photo, 0, 0)
        layout_photo.setAlignment(Qt.AlignTop)
        group_photo = QGroupBox(u"Photo")
        group_photo.setLayout(layout_photo)

        
        self.student_first_name = QLineEdit()
        self.student_last_name = QLineEdit()
        self.student_birth_date = QDateEdit()
        self.student_birth_date.setCalendarPopup(True)
        self.student_birth_date.setDisplayFormat(u"dd/MM/yyyy")
        self.student_birth_place = QLineEdit()
        self.student_genre = QComboBox()
        self.student_genre.addItem(u"Homme")
        self.student_genre.addItem(u"Femme")
        self.student_height = QSpinBox()
        self.student_height.setRange(1, 300)
        self.student_height.setMaximum(300)
        self.student_matricule = QLineEdit()
        self.student_matricule_misteriel = QLineEdit()
        self.student_previous_school = QLineEdit()
        self.student_previous_classroom = QLineEdit()
        self.student_statut = QComboBox()
        self.student_statut.addItem(u"Non affecté(e)")
        self.student_statut.addItem(u"Affecté(e)")
        self.student_redoubler = QComboBox()
        self.student_redoubler.addItem(u"Non")
        self.student_redoubler.addItem(u"Oui")
        self.student_email = QLineEdit()
        self.student_phone1 = QLineEdit()
        self.student_phone1.setInputMask("99-99-99-99")
        self.student_phone2 = QLineEdit()
        self.student_phone2.setInputMask("99-99-99-99")
        self.student_phone3 = QLineEdit()
        self.student_phone3.setInputMask("99-99-99-99")


        layout_form_info = QFormLayout()
        layout_form_info.addRow(u"Nom: ", self.student_last_name)
        layout_form_info.addRow(u"Prénom: ", self.student_first_name)
        layout_form_info.addRow(u"Date de naissance: ", self.student_birth_date)
        layout_form_info.addRow(u"Lieu de naissance: ", self.student_birth_place)
        layout_form_info.addRow(u"Genre: ", self.student_genre)
        layout_form_info.addRow(u"Taille (cm): ", self.student_height)
        layout_form_info.addRow(u"Matricule: ", self.student_matricule)
        layout_form_info.addRow(u"Matricule ministeriel: ", self.student_matricule_misteriel)
        layout_form_info.addRow(u"Statut: ", self.student_statut)
        layout_form_info.addRow(u"Ecole précedente: ", self.student_previous_school)
        layout_form_info.addRow(u"Classe précedente: ", self.student_previous_classroom)
        layout_form_info.addRow(u"Redoublant: ", self.student_redoubler)
        layout_form_info.addRow(u"Email: ", self.student_email)
        layout_form_info.addRow(u"Téléphone 1: ", self.student_phone1)
        layout_form_info.addRow(u"Téléphone 2: ", self.student_phone2)
        layout_form_info.addRow(u"Téléphone 3: ", self.student_phone3)

        

        group_info = QGroupBox("Informations personnelles")
        group_info.setLayout(layout_form_info)
        

        layout_main_page_info = QHBoxLayout()
        layout_main_page_info.addWidget(group_info)
        layout_main_page_info.addWidget(group_photo)
     

        page_info.setLayout(layout_main_page_info)


        # page marks 
        page_mark = QWidget()
        

        self.table_view = QTableWidget()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.table_view.setStyleSheet("alternate-background-color: gray;")

        self.table_view.setShowGrid(False)
        self.table_view.setTabKeyNavigation(True)
        self.table_view.setColumnCount(5)


        headers = []
        headers.append(u"Martière")
        headers.append(u"Note")
        headers.append(u"Sur total point")
        headers.append(u"Observation")
        headers.append(u"Date")
        self.table_view.setHorizontalHeaderLabels(headers)
        self.table_view.setColumnWidth(0, 150)
        self.table_view.setColumnWidth(1, 80)
        self.table_view.setColumnWidth(2, 110)
        self.table_view.setColumnWidth(3, 150)
        self.table_view.setColumnWidth(4, 150)






        self.btn_save = QPushButton(u"Enregistrer tout")
        self.btn_new_row = QPushButton(u"Nouvelle note")
        self.btn_delete_row = QPushButton(u"Supprimer")
        self.btn_cancel_notes = QPushButton(u"Annuler")

        self.btn_new_row.setEnabled(False)
        self.btn_delete_row.setEnabled(False)
        self.btn_cancel_notes.setEnabled(False)

        self.btn_new_row.setIcon(QIcon(":/images/button_new_row.png"))
        self.btn_delete_row.setIcon(QIcon(":/images/button_remove.png"))
        self.btn_cancel_notes.setIcon(QIcon(":/images/button_cancel.png"))



        self.combo_mark_group = QComboBox()
        self.combo_mark_group.setMinimumWidth(200)
        self.combo_mark_group.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        layout_mark_group = QFormLayout()
        layout_mark_group.addRow(u"Période: ", self.combo_mark_group)


        btn_box = QDialogButtonBox(Qt.Vertical)
        btn_box.addButton(self.btn_new_row, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_delete_row, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_cancel_notes, QDialogButtonBox.ActionRole)


        layout_main_page_mark = QHBoxLayout()
        layout_main_page_mark.addWidget(self.table_view)
        layout_main_page_mark.addWidget(btn_box)

        layout_boss = QVBoxLayout()
        layout_boss.addLayout(layout_mark_group)
        layout_boss.addLayout(layout_main_page_mark)

        page_mark.setLayout(layout_boss)

        
        # setup onglets
        onglets = QTabWidget()
        onglets.addTab(page_info, "Information personnelles")
        onglets.addTab(page_mark, "Notes")




        self.btn_ok = QPushButton("Ok")
        self.btn_ok.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_ok.setEnabled(False)
        self.btn_exit = QPushButton("Quitter")
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))

        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_ok)
        layout_btn.addWidget(self.btn_exit)
        layout_btn.setAlignment(Qt.AlignRight)
       

        layout_main = QVBoxLayout()
        layout_main.addWidget(group_year_and_class)
        layout_main.addWidget(onglets)
        layout_main.addLayout(layout_btn)

        dialog.setLayout(layout_main)
        dialog.resize(900, 500)
        dialog.setWindowTitle(u"Nouveau élève - InterNotes")


        #events
        self.connect(self.combo_ay, SIGNAL("currentIndexChanged(int)"), 
                self.setClassComboBoxByAcademicYearId)

        self.connect(self.combo_ay, SIGNAL("currentIndexChanged(int)"), 
                self.setMarkGroupComboBoxByAcademicYearId)

        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.setTableMarksByClassroomIndexChanged)

        self.connect(self.combo_classroom, SIGNAL("activated(int)"), 
                self.setTableMarksByClassroomIndexChanged)

        self.connect(self.combo_class, SIGNAL("currentIndexChanged(int)"), 
                self.setClassroomComboBoxByClassId)

        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.activeOkBtn)

        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.activeNewAndCancelBtn)

        self.connect(self.table_view, SIGNAL("itemClicked(QTableWidgetItem *)"), 
                self.activeDeleteBtn)

        self.connect(self.table_view, SIGNAL("currentItemChanged(QTableWidgetItem *, \
                                                                 QTableWidgetItem *)"), 
                self.activeDeleteBtn)


        self.connect(self.btn_new_row, SIGNAL("clicked()"), 
                self.addNewMarkRow)

        self.connect(self.btn_delete_row, SIGNAL("clicked()"), 
                self.deleteRow)

        self.connect(self.btn_cancel_notes, SIGNAL("clicked()"), 
                self.cancelAll)


        self.connect(self.btn_photo, SIGNAL("clicked()"), self.selectPhoto)
        self.connect(self.btn_ok, SIGNAL("clicked()"), dialog.accept)
        self.connect(self.btn_exit, SIGNAL("clicked()"), dialog.reject)


        return (dialog.exec_(), self.student_first_name.text(),
                               self.student_last_name.text(),
                               self.student_birth_date.date().toString("dd/MM/yyyy"),
                               self.student_birth_place.text(),
                               self.student_genre.currentText(),
                               self.student_height.value(),
                               self.student_matricule.text(),
                               self.student_previous_school.text(),
                               self.student_redoubler.currentText(),
                               self.student_email.text(),
                               self.student_phone1.text(),
                               self.student_phone2.text(),
                               self.student_phone3.text(),
                               self.combo_ay.itemData(self.combo_ay.currentIndex()).toInt()[0],
                               self.combo_class.itemData(self.combo_class.currentIndex()).toInt()[0],
                               self.combo_classroom.itemData(self.combo_classroom.currentIndex()).toInt()[0],
                               self.new_photo_file_name,
                               self.student_matricule_misteriel.text(),
                               self.getAllNewMarksFromTableView(),
                               self.student_statut.currentText(),
                               self.student_previous_classroom.text()
                               )
    


    def showEditStudentDialog(self, selected_index):
        #stid = selected_item.data(0, Qt.AccessibleTextRole).toInt()[0]
        model_index = self.proxy_model.mapToSource(selected_index)
        item = self.model.itemFromIndex(model_index)
        self.stid = item.accessibleText().toInt()[0]
        infos = self.getStudentInfosById(self.stid)

        dialog = QDialog(self)
        self.new_photo_file_name = QString('')
        self.student_photo_file_name = QString('')

        self.combo_ay = QComboBox()
        self.combo_ay.setMinimumWidth(200)
        self.combo_ay.setSizeAdjustPolicy(QComboBox.AdjustToContents) 
        self.updateAcademicYearComboBox()



        self.combo_class = QComboBox()
        self.combo_class.setMinimumWidth(200)
        self.combo_class.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        self.combo_classroom = QComboBox()
        self.combo_classroom.setMinimumWidth(200)
        self.combo_classroom.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        label_ay = QLabel(u"Année academique: ")
        label_class = QLabel(u"Classe: ")
        label_classroom = QLabel(u"Salle: ")


        old_ay_id = infos['academic_year_id']
        if old_ay_id is not None and not old_ay_id == 0:
            ay_name = academicyear.AcademicYear.getNameById(old_ay_id)
            ay_index = self.combo_ay.findText(ay_name)
            self.combo_ay.setCurrentIndex(ay_index)
            self.setClassComboBoxByAcademicYearId(ay_index)


        old_class_id = infos['class_id']
        if old_class_id is not None and not old_class_id == 0:
            class_name = classe.Class.getClassNameById(old_class_id)
            class_index = self.combo_class.findText(class_name)
            self.combo_class.setCurrentIndex(class_index)
            self.setClassroomComboBoxByClassId(class_index)

         

        old_classroom_id = infos['classroom_id']
        if old_classroom_id is not None and not old_classroom_id == 0:
            classroom_name = classe.Class.getClassroomNameById(old_classroom_id)
            classroom_index = self.combo_classroom.findText(classroom_name)
            self.combo_classroom.setCurrentIndex(classroom_index)
  


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



        
        #page info
        page_info = QWidget()

        self.btn_photo = QPushButton()
        if infos['student_photo_name'] is not None and not \
                infos['student_photo_name'].isEmpty() and not \
                QImage(infos['student_photo_name']).isNull():
            self.btn_photo.setIcon(QIcon(infos['student_photo_name']))
            self.student_photo_file_name = QString(infos['student_photo_name'])
        else:
            self.btn_photo.setIcon(QIcon(":/images/user-icon.png"))
        self.btn_photo.setIconSize(QSize(200, 200))
        layout_photo = QGridLayout()
        layout_photo.addWidget(self.btn_photo, 0, 0)
        layout_photo.setAlignment(Qt.AlignTop)
        group_photo = QGroupBox(u"Photo")
        group_photo.setLayout(layout_photo)

        self.student_first_name = QLineEdit(infos['student_first_name'])
        self.student_last_name = QLineEdit(infos['student_last_name'])

        l_date = infos['student_birth_date'].split("/")
        y = l_date[2].toInt()[0]
        m = l_date[1].toInt()[0]
        d = l_date[0].toInt()[0]
        new_date = QDate(y, m, d)
        self.student_birth_date = QDateEdit(new_date)
        self.student_birth_date.setCalendarPopup(True)
        self.student_birth_date.setDisplayFormat(u"dd/MM/yyyy")
        self.student_birth_place = QLineEdit(infos['student_birth_place'])
        self.student_genre = QComboBox()
        self.student_genre.addItem(u"Homme")
        self.student_genre.addItem(u"Femme")
        if infos['student_genre'] == 'Homme':
            self.student_genre.setCurrentIndex(0)
        elif infos['student_genre'] == 'Femme':
            self.student_genre.setCurrentIndex(1)


        
        self.student_statut = QComboBox()
        self.student_statut.addItem(u"Non affecté(e)")
        self.student_statut.addItem(u"Affecté(e)")

        if infos['student_statut'] == u'Non affecté(e)':
            self.student_genre.setCurrentIndex(0)
        elif infos['student_statut'] == u'Affecté(e)':
            self.student_genre.setCurrentIndex(1)


        self.student_height = QSpinBox()
        self.student_height.setRange(1, 300)
        self.student_height.setMaximum(300)
        self.student_height.setValue(infos['student_height'])

        self.student_matricule = QLineEdit(infos['student_matricule'])
        self.student_matricule_ministeriel = QLineEdit(infos['student_matricule_ministeriel'])
        self.student_previous_school = QLineEdit(infos['student_previous_school'])
        self.student_previous_classroom = QLineEdit(infos['student_previous_classroom'])
        self.student_redoubler = QComboBox()
        self.student_redoubler.addItem(u"Non")
        self.student_redoubler.addItem(u"Oui")
        if infos['student_redoubler'] == 'Non':
            self.student_redoubler.setCurrentIndex(0)
        elif infos['student_redoubler'] == 'Oui':
            self.student_redoubler.setCurrentIndex(1)
        self.student_email = QLineEdit(infos['student_email'])
        self.student_phone1 = QLineEdit(infos['student_phone1'])
        self.student_phone1.setInputMask("99-99-99-99")
        self.student_phone2 = QLineEdit(infos['student_phone2'])
        self.student_phone2.setInputMask("99-99-99-99")
        self.student_phone3 = QLineEdit(infos['student_phone3'])
        self.student_phone3.setInputMask("99-99-99-99")


        layout_form_info = QFormLayout()
        layout_form_info.addRow(u"Nom: ", self.student_last_name)
        layout_form_info.addRow(u"Prénom: ", self.student_first_name)
        layout_form_info.addRow(u"Date de naissance: ", self.student_birth_date)
        layout_form_info.addRow(u"Lieu de naissance: ", self.student_birth_place)
        layout_form_info.addRow(u"Genre: ", self.student_genre)
        layout_form_info.addRow(u"Taille (cm): ", self.student_height)
        layout_form_info.addRow(u"Matricule: ", self.student_matricule)
        layout_form_info.addRow(u"Matricule ministeriel: ", self.student_matricule_ministeriel)
        layout_form_info.addRow(u"Statut: ", self.student_statut)
        layout_form_info.addRow(u"Ecole précedente: ", self.student_previous_school)
        layout_form_info.addRow(u"Classe précedente: ", self.student_previous_classroom)
        layout_form_info.addRow(u"Redoublant: ", self.student_redoubler)
        layout_form_info.addRow(u"Email: ", self.student_email)
        layout_form_info.addRow(u"Téléphone 1: ", self.student_phone1)
        layout_form_info.addRow(u"Téléphone 2: ", self.student_phone2)
        layout_form_info.addRow(u"Téléphone 3: ", self.student_phone3)

        group_info = QGroupBox("Informations personnelles")
        group_info.setLayout(layout_form_info)
        

        layout_main_page_info = QHBoxLayout()
        layout_main_page_info.addWidget(group_info)
        layout_main_page_info.addWidget(group_photo)

        page_info.setLayout(layout_main_page_info)

        

        # page marks 
        page_mark = QWidget()
        

        self.table_view = QTableWidget()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)

        self.table_view.setShowGrid(False)
        self.table_view.setTabKeyNavigation(True)
        self.table_view.setColumnCount(5)

        headers = []
        headers.append(u"Martière")
        headers.append(u"Note")
        headers.append(u"Sur total point")
        headers.append(u"Observation")
        headers.append(u"Date")
        self.table_view.setHorizontalHeaderLabels(headers)
        self.table_view.setColumnWidth(0, 150)
        self.table_view.setColumnWidth(1, 70)
        self.table_view.setColumnWidth(2, 110)
        self.table_view.setColumnWidth(3, 150)
        self.table_view.setColumnWidth(4, 150)


        
        self.btn_save = QPushButton(u"Enregistrer tout")
        self.btn_new_row = QPushButton(u"Nouvelle note")
        self.btn_delete_row = QPushButton(u"Supprimer")
        self.btn_cancel_notes = QPushButton(u"Annuler")

        self.btn_save.setEnabled(False)
        self.btn_new_row.setEnabled(False)
        self.btn_delete_row.setEnabled(False)
        self.btn_cancel_notes.setEnabled(False)


        self.btn_save.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_new_row.setIcon(QIcon(":/images/button_new_row.png"))
        self.btn_delete_row.setIcon(QIcon(":/images/button_remove.png"))
        self.btn_cancel_notes.setIcon(QIcon(":/images/button_cancel.png"))

        self.activeNewAndCancelBtn()


        self.combo_mark_group = QComboBox()
        self.combo_mark_group.setMinimumWidth(200)
        self.combo_mark_group.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        #self.setMarkGroupComboBoxByAcademicYearId(ay_index)

        layout_mark_group = QFormLayout()
        layout_mark_group.addRow(u"Période: ", self.combo_mark_group)

        #self.setTableMarksByStudentIdAndByMarkGroup(0)



        btn_box = QDialogButtonBox(Qt.Vertical)
        btn_box.addButton(self.btn_save, QDialogButtonBox.AcceptRole)
        btn_box.addButton(self.btn_new_row, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_delete_row, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_cancel_notes, QDialogButtonBox.ActionRole)

        layout_main_page_mark = QHBoxLayout()
        layout_main_page_mark.addWidget(self.table_view)
        layout_main_page_mark.addWidget(btn_box)

        layout_main_page_mark = QHBoxLayout()
        layout_main_page_mark.addWidget(self.table_view)
        layout_main_page_mark.addWidget(btn_box)

        layout_boss = QVBoxLayout()
        layout_boss.addLayout(layout_mark_group)
        layout_boss.addLayout(layout_main_page_mark)

        page_mark.setLayout(layout_boss)
         


       
        #page away
        page_away = QWidget()

        self.table_view_away = QTableWidget()
        self.table_view_away.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view_away.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view_away.setAlternatingRowColors(True)

        self.table_view_away.setShowGrid(False)
        self.table_view_away.setTabKeyNavigation(True)
        self.table_view_away.setColumnCount(5)

        headers = []
        headers.append(u"Date")
        headers.append(u"De (Heure)")
        headers.append(u"À (Heure)")
        headers.append(u"Justification")
        headers.append(u"Motif si justifiée")
        self.table_view_away.setHorizontalHeaderLabels(headers)
        self.table_view_away.setColumnWidth(0, 100)
        self.table_view_away.setColumnWidth(1, 100)
        self.table_view_away.setColumnWidth(2, 100)
        self.table_view_away.setColumnWidth(3, 100)
        self.table_view_away.setColumnWidth(4, 250)


        
        self.btn_save_away = QPushButton(u"Enregistrer tout")
        self.btn_new_row_away = QPushButton(u"Nouvelle absence")
        self.btn_delete_row_away = QPushButton(u"Supprimer")
        self.btn_cancel_away = QPushButton(u"Annuler")

        self.btn_save_away.setEnabled(False)
        self.btn_new_row_away.setEnabled(False)
        self.btn_delete_row_away.setEnabled(False)
        self.btn_cancel_away.setEnabled(False)


        self.btn_save_away.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_new_row_away.setIcon(QIcon(":/images/button_new_row.png"))
        self.btn_delete_row_away.setIcon(QIcon(":/images/button_remove.png"))
        self.btn_cancel_away.setIcon(QIcon(":/images/button_cancel.png"))

        self.activeNewAndCancelAwayBtn()


        self.combo_mark_group_away = QComboBox()
        self.combo_mark_group_away.setMinimumWidth(200)
        self.combo_mark_group_away.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        self.setMarkGroupComboBoxByAcademicYearId(ay_index)

        layout_mark_group = QFormLayout()
        layout_mark_group.addRow(u"Période: ", self.combo_mark_group_away)



        self.setTableMarksByStudentIdAndByMarkGroup(0)
        self.setTableAwayByStudentIdAndByMarkGroup(0)




        btn_box = QDialogButtonBox(Qt.Vertical)
        btn_box.addButton(self.btn_save_away, QDialogButtonBox.AcceptRole)
        btn_box.addButton(self.btn_new_row_away, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_delete_row_away, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_cancel_away, QDialogButtonBox.ActionRole)

        layout_main_page_mark = QHBoxLayout()
        layout_main_page_mark.addWidget(self.table_view_away)
        layout_main_page_mark.addWidget(btn_box)

        layout_main_page_mark = QHBoxLayout()
        layout_main_page_mark.addWidget(self.table_view_away)
        layout_main_page_mark.addWidget(btn_box)

        layout_boss = QVBoxLayout()
        layout_boss.addLayout(layout_mark_group)
        layout_boss.addLayout(layout_main_page_mark)

        page_away.setLayout(layout_boss)
         




        
        # add the pages to the onglet
        onglets = QTabWidget()
        onglets.addTab(page_info, "Information personnelles")
        onglets.addTab(page_mark, "Notes")
        onglets.addTab(page_away, "Absence")




        self.btn_ok = QPushButton("Ok")
        self.btn_ok.setIcon(QIcon(":/images/button_apply.png"))
        self.btn_exit = QPushButton("Quitter")
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))

        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_ok)
        layout_btn.addWidget(self.btn_exit)
        layout_btn.setAlignment(Qt.AlignRight)
       

        layout_main = QVBoxLayout()
        layout_main.addWidget(group_year_and_class)
        layout_main.addWidget(onglets)
        layout_main.addLayout(layout_btn)

        dialog.setLayout(layout_main)
        dialog.resize(900, 500)
        dialog.setWindowTitle(u"Modifier élève - InterNotes")

        self.connect(self.combo_ay, SIGNAL("currentIndexChanged(int)"), 
                self.setClassComboBoxByAcademicYearId)

        self.connect(self.combo_class, SIGNAL("currentIndexChanged(int)"),
                self.setClassroomComboBoxByClassId)

        self.connect(self.combo_ay, SIGNAL("currentIndexChanged(int)"), 
                self.setMarkGroupComboBoxByAcademicYearId)

        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.setTableMarksByClassroomIndexChanged)

        self.connect(self.combo_classroom, SIGNAL("activated(int)"), 
                self.setTableMarksByClassroomIndexChanged)

        self.connect(self.combo_mark_group, SIGNAL("currentIndexChanged(int)"), 
                self.setTableMarksByStudentIdAndByMarkGroup)

        self.connect(self.combo_mark_group, SIGNAL("activated(int)"), 
                self.setTableMarksByStudentIdAndByMarkGroup)


        

        self.connect(self.combo_mark_group_away, SIGNAL("currentIndexChanged(int)"), 
                self.setTableAwayByStudentIdAndByMarkGroup)

        self.connect(self.combo_mark_group_away, SIGNAL("activated(int)"), 
                self.setTableAwayByStudentIdAndByMarkGroup)




        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.activeOkBtn)


        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.activeNewAndCancelBtn)

        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.activeNewAndCancelAwayBtn)

        self.connect(self.table_view, SIGNAL("itemClicked(QTableWidgetItem *)"), 
                self.activeDeleteBtn)

        self.connect(self.table_view_away, SIGNAL("itemClicked(QTableWidgetItem *)"), 
                self.activeDeleteAwayBtn)

        self.connect(self.table_view, SIGNAL("currentItemChanged(QTableWidgetItem *, \
                                                                 QTableWidgetItem *)"), 
                self.activeDeleteBtn)

        self.connect(self.table_view_away, SIGNAL("currentItemChanged(QTableWidgetItem *, \
                                                                 QTableWidgetItem *)"), 
                self.activeDeleteAwayBtn)

        self.connect(self.table_view, SIGNAL("cellChanged(int, int)"), 
                self.activeSaveBtn)

        self.connect(self.table_view_away, SIGNAL("cellChanged(int, int)"), 
                self.activeSaveAwayBtn)





        self.connect(self.btn_save, SIGNAL("clicked()"), 
                self.onClickedSaveBtn)

        self.connect(self.btn_save_away, SIGNAL("clicked()"), 
                self.onClickedSaveAwayBtn)

        self.connect(self.btn_new_row, SIGNAL("clicked()"), 
                self.addNewMarkRow)

        self.connect(self.btn_new_row_away, SIGNAL("clicked()"), 
                self.addNewAwayRow)

        self.connect(self.btn_delete_row, SIGNAL("clicked()"), 
                self.deleteRow)

        self.connect(self.btn_delete_row_away, SIGNAL("clicked()"), 
                self.deleteAwayRow)

        self.connect(self.btn_cancel_notes, SIGNAL("clicked()"), 
                self.cancelAll)

        self.connect(self.btn_cancel_away, SIGNAL("clicked()"), 
                self.cancelAllAway)

        self.connect(self.btn_photo, SIGNAL("clicked()"), self.selectPhoto)
        self.connect(self.btn_ok, SIGNAL("clicked()"), dialog.accept)
        self.connect(self.btn_exit, SIGNAL("clicked()"), dialog.reject)


        return (dialog.exec_(), self.student_first_name.text(),
                               self.student_last_name.text(),
                               self.student_birth_date.date().toString("dd/MM/yyyy"),
                               self.student_birth_place.text(),
                               self.student_genre.currentText(),
                               self.student_height.value(),
                               self.student_matricule.text(),
                               self.student_previous_school.text(),
                               self.student_redoubler.currentText(),
                               self.student_email.text(),
                               self.student_phone1.text(),
                               self.student_phone2.text(),
                               self.student_phone3.text(),
                               self.combo_ay.itemData(self.combo_ay.currentIndex()).toInt()[0],
                               self.combo_class.itemData(self.combo_class.currentIndex()).toInt()[0],
                               self.combo_classroom.itemData(self.combo_classroom.currentIndex()).toInt()[0],
                               self.new_photo_file_name,
                               self.student_matricule_ministeriel.text(),
                               self.student_photo_file_name,
                               self.stid,
                               item,
                               self.getAllNewMarksFromTableView(),
                               self.student_statut.currentText(),
                               self.student_previous_classroom.text()
                               )
        
        
        
        
        
        
        
        

    def selectPhoto(self):
        photo_file_name = QFileDialog.getOpenFileName(self, u"Sélectioner une photo", QDir.homePath(), 
                                                          "Images (*.png *.jpg *.jpeg)")
        if not photo_file_name.isNull():
            pic = QImage(photo_file_name)
            if pic.isNull():
                QMessageBox.critical(self, u"Sélectioner une photo", 
                          u"Impossible d'ouvrir le fichier '" + photo_file_name + " '")
                return

            pic_scaled = pic.scaledToHeight(250)

            pic_pixmap = QPixmap.fromImage(pic_scaled)
            dialog_photo_preview = photopreview.PhotoPreview(pic_pixmap, self)
            reply = dialog_photo_preview.exec_()

            self.new_photo_file_name = QString(
                    QDir.currentPath() + u"/images/upload/userphoto/" + \
                            uuid.uuid1().hex + ".png")

            if reply == 1:
                writer = QImageWriter(self.new_photo_file_name, "png")
                writer.setQuality(100)
                if not writer.write(pic_scaled):
                    QMessageBox.critical(self, u"Sélectioner une photo",
                                           writer.errorString())

                self.btn_photo.setIcon(QIcon(self.new_photo_file_name))
            else:
                self.new_photo_file_name = u""


    
    def removeOldPhoto(self, student_id):
        query = QSqlQuery("SELECT student_photo_name FROM student \
                           WHERE student_id = " + str(student_id))
        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                                 query.lastError().text())
            return
          
        record = query.record()
        if not record.isEmpty():
            while query.next():
                student_photo_name = query.value(record.indexOf("student_photo_name")).toString()
                if student_photo_name is not None and not student_photo_name.isEmpty():
                    photo_file = QFile(student_photo_name)
                    if not photo_file.remove():
                        QMessageBox.warning(self, "Error - InterNotes", 
                               "Erreur de suppression de l'ancienne photo de l'élève")


    def onEditStudentItem(self):
        #student_item = self.currentItem()
        proxy_index = self.currentIndex()
        model_index = self.proxy_model.mapToSource(proxy_index)
        item = self.model.itemFromIndex(model_index)
        #if student_item.isSelected() == True:
        self.onEditStudent(proxy_index)




    def onDeleteStudentItem(self):
        #student_item = self.currentItem()
        proxy_index = self.currentIndex()
        model_index = self.proxy_model.mapToSource(proxy_index)
        item = self.model.itemFromIndex(model_index)
        item_row = item.row()
        student_id = item.accessibleText().toInt()[0]
        student_name = item.text()

        #if student_item.isSelected() == True:
        reply = QMessageBox.question(self, "Supprimer?", 
            u"Êtes vous sûr de vouloir supprimer definitivement du logiciel l'élève <b>%s</b> " \
            u"selectionné?" % student_name, QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.No)
        if reply == QMessageBox.Yes:
            #delete from db
            #student_id = student_item.data(0, 11).toInt()[0]
            #student_index = self.indexOfTopLevelItem(student_item)

            self.removeOldPhoto(student_id)

            query = QSqlQuery()
            query.prepare("DELETE m.*, std.* \
                           FROM student std \
                           LEFT JOIN mark m ON m.student_id = std.student_id \
                           WHERE std.student_id = :stdid")
            query.bindValue(":stdid", student_id)
            if not query.exec_():
                QMessageBox.critical(self, "Error - InterNotes",
                          u"Database Error: %s" % query.lastError().text())
            else:
                self.model.removeRow(item_row)

                std_nb = 0
                if len(self.list_room_id):

                    for id in range(0, len(self.list_room_id)):
                        std_nb += classe.Class.getNumberOfStudentInThisClassroomById(
                                self.list_room_id[id])

                    self.model.setHorizontalHeaderLabels(
                             QStringList(u"Elèves - Nom et prenoms (%i)" % std_nb))


                if self.model.rowCount() == 0:
                    self.infos.showStudentInfos(0)
                else:
                    self.infos.showStudentInfos(self.currentIndex())
                    self.stat_page.stat_object_tree.updateStatObjectTree()
                    self.stat_page.stat_feature_tree.clear()
                    self.stat_page.stat_feature_tree.setHeaderLabel(u"")

                    child = self.stat_page.stat_output.layout.takeAt(0)
                    if child:
                        child.widget().deleteLater()

        elif reply == 2:
            return


    


    def onEditStudent(self, index):
        reply = self.showEditStudentDialog(index)
        std_crid = Student.getClassroomIdById(reply[20]); 

        # If the student has changed of classroom, delete "ALL" his/her previous marks
        if reply[0] == 1:
            if std_crid != reply[16]:
                self.deleteAllMarksById(reply[20])
                QMessageBox.information(self, "Info - InterNotes",
                    u"Vous avez affecté cet élève à une autre salle de classe. Par conséquent, toutes ses " + 
                    u"précedentes notes ont été supprimé!");

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
        student_infos['student_photo_file_name'] = reply[19]
        student_infos['student_id'] = reply[20]
        student_infos['item'] = reply[21]

        student_infos['mark_data'] = reply[22]
        student_infos['student_statut'] = reply[23]
        student_infos['student_previous_classroom'] = reply[24]

        #self.deleteRemovablesMarks()

        #student_infos['student_last_name'] = student_infos['student_last_name'].replace(" ", "")
        if reply[0] == 1:
            self.deleteRemovablesMarks()
            self.editStudentItem(student_infos)
            if self.infos is not None:
                self.infos.showStudentInfos(index, updated=True)
        elif reply[0] == 0:
            if student_infos['new_photo_file_name']:
                new_photo_file_name = student_infos['new_photo_file_name']
                if new_photo_file_name is not None and not new_photo_file_name.isEmpty():
                    tmp_photo_file = QFile(new_photo_file_name, self)
                    if not tmp_photo_file.remove():
                        QMessageBox.critical(self, "Error - InterNotes", "Erreur de suppression de la photo temporaire\n" + new_photo_file_name)
                    student_infos['new_photo_file_name'] = ''
        if self.infos is not None:
            self.infos.showStudentInfos(index)


    def keyPressEvent(self, event):
        cpi = self.currentIndex()
        mi = self.proxy_model.mapToSource(cpi)
        item = self.model.itemFromIndex(mi)
        if event.key() == Qt.Key_Down:
            if not self.indexBelow(self.currentIndex()).isValid():
                return

            self.setCurrentIndex(self.indexBelow(self.currentIndex()))

            self.infos.showStudentInfos(self.currentIndex())

        elif event.key() == Qt.Key_Up:
            if not self.indexAbove(self.currentIndex()).isValid():
                return

            self.setCurrentIndex(self.indexAbove(self.currentIndex()))

            self.infos.showStudentInfos(self.currentIndex())

        else:
            QTreeView.keyPressEvent(self, event)




    def currentStudentNameSearched(self):
        self.setCurrentIndex(self.proxy_model.index(0, 0))
        proxy_index = self.currentIndex()
        model_index = self.proxy_model.mapToSource(proxy_index)
        if model_index.isValid():
            self.infos.showStudentInfos(proxy_index)
        else:
            self.infos.showStudentInfos(0)
        

    
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        action_edit = tools.createAction(self, u"&Modifer l'élève",
                self.onEditStudentItem,
                "",
                ":/images/edit.png",
                u"Modifier l'élève", u"Modifier l'élève selectionné")

        action_delete = tools.createAction(self,
                u"&Supprimer l'élève",
                self.onDeleteStudentItem,
                "Ctrl+D",
                ":/images/button_cancel.png",
                u"Supprimer l'élève selectionné.")
   
        
        if self.currentIndex() is None or self.currentIndex().isValid() == False:
            action_edit.setEnabled(False)
            action_delete.setEnabled(False)
        else:
            action_edit.setEnabled(True)
            action_delete.setEnabled(True)



        menu.addAction(action_edit)
        menu.addAction(action_delete)
        menu.exec_(event.globalPos())







    def deleteAllMarksById(self, stid):
        query = QSqlQuery("DELETE FROM mark \
                          WHERE student_id = " + str(stid))

        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                   u"Database Error: %s " % query.lastError().text())
        else:
            self.stat_page.stat_object_tree.updateStatObjectTree()
            self.stat_page.stat_feature_tree.clear()
            self.stat_page.stat_feature_tree.setHeaderLabel(u"")

            child = self.stat_page.stat_output.layout.takeAt(0)
            if child:
                child.widget().deleteLater()


   
      
    @staticmethod
    def getClassroomIdById(stid):
        crid = 0
        query = QSqlQuery("SELECT cr.classroom_id \
                           FROM student std \
                           INNER JOIN classroom cr ON cr.classroom_id = std.classroom_id \
                           WHERE std.student_id = " + str(stid))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    crid = query.value(record.indexOf("classroom_id")).toInt()[0]
        else:
            print "SQL Error!"

        return crid


    @staticmethod
    def getClassroomNameById(stid):
        cr_name = QString(u"")

        query = QSqlQuery("SELECT cr.classroom_name \
                           FROM student std \
                           INNER JOIN classroom cr ON cr.classroom_id = std.classroom_id \
                           WHERE std.student_id = " + str(stid))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    cr_name = query.value(
                            record.indexOf("classroom_name")).toString()
        else:
            print "SQL Error!"

        return cr_name


    @staticmethod
    def getAcademicYearIdById(stid):
        ayid = 0
        query = QSqlQuery("SELECT academic_year_id \
                           FROM student \
                           WHERE student_id = " + str(stid))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    ayid = query.value(record.indexOf("academic_year_id")).toInt()[0]
        else:
            print "SQL Error!"

        return ayid
    

    @staticmethod
    def isStudentHasAnyMarksInThisMarkGroup(stid, group):
        sql = "SELECT mark_id \
               FROM mark \
               WHERE student_id = " + str(stid) + \
               " AND mark_group = " + "'" + group + "'"
        query = QSqlQuery(sql)
        if query.exec_():
            if query.size() >= 1:
                return True
            else:
                return False
        else:
            print "SQL Error!"



    @staticmethod
    def isStudentHasAnyMarksInThisTopic(stid, tid):
        sql = "SELECT mark_id \
               FROM mark \
               INNER JOIN topic t USING(topic_id) \
               WHERE student_id = " + str(stid) + \
               " AND t.topic_id = " + tid

        query = QSqlQuery(sql)
        if query.exec_():
            if query.size() >= 1:
                return True
            else:
                return False
        else:
            print "SQL Error!"


    @staticmethod
    def getStudentAverageByTopicAndMarkGroup(tid, stid, mg):
        my = None
        sql = "SELECT \
                ROUND(SUM(mark_mark) / (SUM(mark_level) / 20), 2) \
                AS my \
               FROM mark m \
               WHERE student_id = :stid \
                AND topic_id = :tid \
                AND mark_group = :mg"

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":stid", stid)
        query.bindValue(":tid", tid)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while (query.next()):
                    my = query.value(
                        record.indexOf("my")).toDouble()[0]

        else:
            print "SQL Error!"


        return my



    @staticmethod
    def getStudentAverageRankByTopicAndMarkGroup(crid, tid, my, mg):
        rank = {}
        avgs = {}
        r = 1
        sql = "SELECT \
                ROUND(SUM(mark_mark) / (SUM(mark_level) / 20), 2) \
                AS my \
               FROM mark \
               WHERE classroom_id = :crid \
                AND topic_id = :tid \
                AND mark_group = :mg \
               GROUP BY student_id \
               ORDER BY my DESC"

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":tid", tid)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  avgs[r] = (
                            query.value(
                             record.indexOf("my")).toDouble()[0]
                            )
                  r += 1

        else:
            print "SQL Error!"


        rank[0] = 0
        try:
            rank[0] = list(avgs.keys())[list(avgs.values()).index(my)]
        except ValueError:
            pass

        rank[1] = ''
        nb = 0
        for k, v in avgs.items():
            if v == my:
                nb += 1
        if nb >= 2:
            rank[1] = 'execo'

        return rank 





    @staticmethod
    def getStudentAverageByTopicTypeAndMarkGroup(stid, mg, ttype):
        bs_my = 0.0
        sql = "SELECT \
                ROUND(AVG(my.avg), 2) as bs_my \
               FROM \
                (SELECT m.student_id as stid, \
                        SUM(mark_mark) / (SUM(mark_level) / 20) as avg \
                 FROM mark as m \
                 INNER JOIN topic as t ON t.topic_id = m.topic_id \
                 WHERE m.student_id = :stid \
                 AND m.mark_group = :mg \
                 AND t.topic_type = :ttype \
                 GROUP BY t.topic_id, m.student_id) as my \
               GROUP BY my.stid"

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":stid", stid)
        query.bindValue(":mg", mg)
        query.bindValue(":ttype", ttype)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  bs_my = (
                            query.value(
                             record.indexOf("bs_my")).toDouble()[0]
                            )

        else:
            print "SQL Error!"

        return bs_my



    @staticmethod
    def getStudentAverageByMarkGroup(stid, mg):
        bs_mg_my = 0.0
        sql = "SELECT \
                ROUND((SUM(my.mycoef) / SUM(my.total_coef)),2)\
                      bs_mg_my \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                    *  IF(t.topic_coef = 0, 1, t.topic_coef) \
                    )\
                   mycoef, \
                 t.topic_coef total_coef FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.student_id = :stid \
                 AND m.mark_group = :mg GROUP BY t.topic_id) my"

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":stid", stid)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  bs_mg_my = (
                            query.value(
                             record.indexOf("bs_mg_my")).toDouble()[0]
                            )

        else:
            print "SQL Error!"

        return bs_mg_my



    @staticmethod
    def getStudentYearlyAverage(stid):
        yearly_my = 0.0

        sql = "SELECT \
                CASE WHEN general.mg IN ('1er Semestre', '2ème Semestre') \
                  THEN ROUND(SUM(general.yearly_my) / 4, 2) \
                  ELSE ROUND(SUM(general.yearly_my) / 5, 2) \
                  END \
                AS ym \
                FROM ( \
                    SELECT \
                    ROUND( \
                       IF ( my.mg = '1er Trimestre', SUM(my.mycoef) / SUM(my.total_coef), (SUM(my.mycoef) / SUM(my.total_coef)) * 2 ) \
                     ,2)\
                    AS yearly_my, my.mg \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                  * IF(t.topic_coef = 0, 1, t.topic_coef) \
                    ) \
                   mycoef, t.topic_coef total_coef, \
                   m.mark_group mg FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.student_id = :stid \
                 GROUP BY t.topic_id, m.mark_group) my \
                 GROUP BY my.mg) general"              

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":stid", stid)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  yearly_my = (
                            query.value(
                             record.indexOf("ym")).toDouble()[0]
                            )

        else:
            print "SQL Error!"


        return yearly_my





    @staticmethod
    def getStudentYearlyRank(crid, yearly_my):
        rank = {}
        avgs = {}
        r = 1

        sql = "SELECT \
                CASE WHEN general.mg IN ('1er Semestre', '2ème Semestre') \
                  THEN ROUND(SUM(general.yearly_my) / 4, 2) \
                  ELSE ROUND(SUM(general.yearly_my) / 5, 2) \
                  END \
                AS ym \
                FROM ( \
                    SELECT \
                    ROUND( \
                       IF ( my.mg = '1er Trimestre', SUM(my.mycoef) / SUM(my.total_coef), (SUM(my.mycoef) / SUM(my.total_coef)) * 2 ) \
                     ,2)\
                    AS yearly_my, my.mg, my.stid \
               FROM \
                (SELECT (ROUND(SUM(mark_mark) / \
                 (SUM(mark_level) / 20), 2) \
                     * IF(t.topic_coef = 0, 1, t.topic_coef) \
                     ) \
                   mycoef, t.topic_coef total_coef, \
                   m.mark_group mg, m.student_id stid FROM mark m \
                 INNER JOIN topic t ON t.topic_id = m.topic_id \
                 WHERE m.classroom_id = :crid \
                 GROUP BY t.topic_id, m.mark_group, m.student_id) my \
                 GROUP BY my.mg, my.stid) general \
                 GROUP BY general.stid ORDER BY ym DESC"              




        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  avgs[r] = (
                            query.value(
                             record.indexOf("ym")).toDouble()[0]
                            )
                  r += 1

        else:
            print "SQL Error!"

        rank[0] = 0
        try:
            rank[0] = list(\
                avgs.keys())[list(avgs.values()).index(yearly_my)]

        except ValueError:
            pass

        rank[1] = ''
        nb = 0
        for k, v in avgs.items():
            if v == yearly_my:
                nb += 1
        if nb >= 2:
            rank[1] = 'execo'

        return rank








    @staticmethod
    def getStudentAverageRankByTopicTypeAndMarkGroup(crid, ttype, mg, bs_my):
        rank = {}
        avgs = {}
        r = 1
        sql = "SELECT \
                ROUND(AVG(my.avg), 2) as r \
               FROM \
                (SELECT m.student_id as stid, \
                        SUM(mark_mark) / (SUM(mark_level) / 20) as avg \
                 FROM mark as m \
                 INNER JOIN topic as t ON t.topic_id = m.topic_id \
                 WHERE m.classroom_id = :crid \
                 AND m.mark_group = :mg \
                 AND t.topic_type = :ttype \
                 GROUP BY t.topic_id, m.student_id) as my \
               GROUP BY my.stid \
               ORDER BY r DESC"

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)
        query.bindValue(":ttype", ttype)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  avgs[r] = (
                            query.value(
                             record.indexOf("r")).toDouble()[0]
                            )
                  r += 1

        else:
            print "SQL Error!"


        rank[0] = 0
        try:
            rank[0] = list(avgs.keys())[list(avgs.values()).index(bs_my)]
        except ValueError:
            pass

        rank[1] = ''
        nb = 0
        for k, v in avgs.items():
            if v == bs_my:
                nb += 1
        if nb >= 2:
            rank[1] = 'execo'

        return rank 



    @staticmethod
    def getStudentAverageRankByMarkGroup(crid, mg, bs_mg_my):
        rank = {}
        avgs = {}
        r = 1

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
                  avgs[r] = (
                            query.value(
                             record.indexOf("bs_mg_my")).toDouble()[0]
                            )
                  r += 1

        else:
            print "SQL Error!"


        rank[0] = 0
        try:
            rank[0] = list(avgs.keys())[list(avgs.values()).index(bs_mg_my)]
        except ValueError:
            pass

        rank[1] = ''
        nb = 0
        for k, v in avgs.items():
            if v == bs_mg_my:
                nb += 1
        if nb >= 2:
            rank[1] = 'execo'

        return rank 








    @staticmethod
    def getBalanceSheetByTopicsTypeAndMarkGroup(ttype, stid, mg):
        bs = {} # Balance Sheet
        sql = "SELECT \
                SUM(mark_mark) sm, SUM(mark_level) sl \
               FROM mark m \
               INNER JOIN topic t ON t.topic_id = m.topic_id \
               WHERE student_id = :stid \
                AND t.topic_type = :ttype \
                AND m.mark_group = :mg"

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":stid", stid)
        query.bindValue(":ttype", ttype)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  bs["sm"] = (
                            query.value(
                             record.indexOf("sm")).toDouble()[0])

                  bs["sl"] = (
                            query.value(
                             record.indexOf("sl")).toInt()[0])

        else:
            print "SQL Error!"

        
        return bs




    @staticmethod
    def getBalanceSheetByMarkGroup(stid, mg):
        bs_mg = {} # Balance Sheet
        sql = "SELECT \
                SUM(mark_mark) AS sm, SUM(mark_level) AS sl \
               FROM mark m \
               INNER JOIN topic t ON t.topic_id = m.topic_id \
               WHERE student_id = :stid \
                AND m.mark_group = :mg"

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":stid", stid)
        query.bindValue(":mg", mg)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  bs_mg["sm"] = (
                            query.value(
                             record.indexOf("sm")).toDouble()[0])

                  bs_mg["sl"] = (
                            query.value(
                             record.indexOf("sl")).toInt()[0])

        else:
            print "SQL Error!"

        
        return bs_mg



    @staticmethod
    def getTotalSumCoef(crid):
        scoef = {} 
        sql = "SELECT \
                SUM(topic_coef) scoef \
               FROM topic \
               WHERE classroom_id = :crid" 

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":crid", crid)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  scoef = (
                            query.value(
                             record.indexOf("scoef")).toInt()[0])

        else:
            print "SQL Error!"

        
        return scoef



    @staticmethod
    def getAcademicYearNameById(stid):
        ay_name = QString(u'')
        query = QSqlQuery("SELECT ay.academic_year_name \
                           FROM student std \
                           INNER JOIN academic_year ay USING(academic_year_id) \
                           WHERE std.student_id = " + str(stid))
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    ay_name = query.value(record.indexOf("academic_year_name")).toString()

        return ay_name


    @staticmethod
    def getAllStudentsIdByClassroomId(crid):
        stds_id = []
        query = QSqlQuery("SELECT student_id \
                           FROM student \
                           WHERE classroom_id = " + str(crid) + 
                           " ORDER BY student_last_name ASC")
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    stds_id.append(
                              query.value(record.indexOf("student_id")).toInt()[0]
                            )

        return stds_id



    @staticmethod
    def getNameById(std_id):
        student_name = u'' 
        sql = "SELECT \
                student_last_name last_name, \
                student_first_name first_name \
               FROM student \
               WHERE student_id = :id" 

        query = QSqlQuery()
        query.prepare(sql)
        query.bindValue(":id", std_id)

        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                  last_name = (
                            query.value(
                             record.indexOf("last_name")).toString())

                  first_name = (
                            query.value(
                             record.indexOf("first_name")).toString())
                  
                  student_name = last_name + " " + first_name


        else:
            print "SQL Error!"

        
        return student_name
