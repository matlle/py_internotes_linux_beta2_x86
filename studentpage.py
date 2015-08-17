# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import academicyear, classe, student, infos

class StudentPage(QWidget):
    def __init__(self, in_stat_page, parent=None):
        super(StudentPage, self).__init__(parent)

        #db = database.getDbConnection()

        self.stat_page = in_stat_page

        self.init()

        self.connect(self.academic_year_tree, SIGNAL("itemClicked(QTreeWidgetItem*, int)"), 
                     self.class_tree.selectClassesByAcademicYearId)

        self.connect(self.class_tree, SIGNAL("itemChanged(QTreeWidgetItem*, int)"),
                    self.student_name_tree.selectStudentsByClassroomId)


        self.connect(self.student_name_tree, SIGNAL("clicked(QModelIndex)"),
                    self.student_infos.showStudentInfos)



    def init(self):

        main_splitter = QSplitter(self)
        main_splitter.setChildrenCollapsible(False)
        
        year_splitter = QSplitter(0x2, self)
        year_splitter.setChildrenCollapsible(False)

        # student tree names
        self.student_name_tree = student.Student(self.stat_page)

        # class tree
        self.class_tree = classe.Class(
                    self.student_name_tree,
                    self.stat_page)

        # academic year tree
        self.academic_year_tree = academicyear.AcademicYear(
                self.class_tree,
                self.student_name_tree,
                self.stat_page)
        
        # student infos
        self.student_infos = infos.Infos(self.student_name_tree)

        self.student_name_tree.infos = self.student_infos

        year_splitter.addWidget(self.academic_year_tree)
        year_splitter.addWidget(self.class_tree)

        main_splitter.addWidget(year_splitter)
        main_splitter.addWidget(self.student_name_tree)
        main_splitter.addWidget(self.student_infos)

        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

 



    def setupStudentInfosWidget(self):
        self.student_infos = QWidget(self)
        self.student_infos.resize(1100, self.student_infos.height())
        #self.student_infos.setStyleSheet("background-color: white;")




