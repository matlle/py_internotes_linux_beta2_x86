#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, academicyear, classe

class StatObject(QTreeView):
    def __init__(self, parent=None):
        super(StatObject, self).__init__(parent)


        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setAnimated(True)


        self.header().setDefaultAlignment(Qt.AlignCenter);


        #self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(QStringList(u"Année Academique, Classe, Salle de classe, Élève"))

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setDynamicSortFilter(True)

        self.setModel(self.proxy_model)


        self.updateStatObjectTree()

        
        #events


    def updateStatObjectTree(self):
        del self.model
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(
                QStringList(
                   u"Année Academique, Classe, Salle de classe, Élève"))
        self.proxy_model.setSourceModel(self.model)


        query = QSqlQuery("SELECT \
                              academic_year_id, \
                              academic_year_name \
                           FROM academic_year")
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
                    ayid = query.value(\
                            record.indexOf("academic_year_id")).toInt()[0]
                    ayname = query.value(
                            record.indexOf("academic_year_name")).toString()
                    ay_item = QStandardItem(ayname)
                    ay_item.setAccessibleText(QString.number(ayid))
                    ay_item.setAccessibleDescription(QString(u"ay"))
                    ay_item.setEditable(False)
                    ay_item.setIcon(QIcon(":/images/academicyear.jpg"))

                    if academicyear.AcademicYear.isAcademicYearHasClass(ayid) == True:
                        classes = academicyear.AcademicYear.getClassesById(ayid)
                        for c in range(0, len(classes)):
                           clid = classes[c]['class_id']
                           cl_item = QStandardItem(classes[c]['class_name'])
                           cl_item.setAccessibleText(QString.number(clid))
                           cl_item.setAccessibleDescription(QString(u"cl"))
                           cl_item.setEditable(False)
                           cl_item.setIcon(QIcon(u":/images/classe.png"))
                           ay_item.setChild(c, cl_item)

                           if classe.Class.isClassHasClassroom(clid) == True:
                               rooms = classe.Class.getClassroomsByClassId(clid)
                               for r in range(0, len(rooms)):
                                   crid = rooms[r]['classroom_id']
                                   cr_item = QStandardItem(rooms[r]['classroom_name'])
                                   cr_item.setAccessibleText(QString.number(crid))
                                   cr_item.setAccessibleDescription(QString(u"cr"))
                                   cr_item.setEditable(False)
                                   cr_item.setIcon(QIcon(u":/images/classroom-icon.png"))
                                   cl_item.setChild(r, cr_item)

                                   if classe.Class.isClassroomHasStudent(crid) == True:
                                       stds = classe.Class.getStudentsByClassroomId(crid)

                                       for s in range(0, len(stds)):
                                           stid = stds[s]['student_id']
                                           std_pic = stds[s]['student_photo_name']
                                           std_item = QStandardItem( 
                                                stds[s]['student_last_name'] + \
                                                    u" "+ stds[s]['student_first_name'])

                                           std_item.setAccessibleText(QString.number(stid))
                                           std_item.setAccessibleDescription(QString(u"std"))
                                           std_item.setEditable(False)
                                           if std_pic is not None and not std_pic.isEmpty() and not \
                                                   QImage(std_pic).isNull():
                                               std_item.setIcon(QIcon(std_pic))
                                           else:
                                               std_item.setIcon(QIcon(":/images/user-icon.png"))
                                           cr_item.setChild(s, std_item)




                    self.model.appendRow(ay_item)


    
