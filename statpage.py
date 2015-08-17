# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import academicyear, classe, student, infos, statobject, statfeature, statoutput

class StatPage(QWidget):
    def __init__(self, parent=None):
        super(StatPage, self).__init__(parent)

        self.init()

        
        self.connect(self.stat_object_tree, SIGNAL("clicked(QModelIndex)"),
                    self.stat_feature_tree.setFeatureTree)

        self.connect(self.stat_object_tree, SIGNAL("clicked(QModelIndex)"),
                    self.clearOutput)



    def clearOutput(self):
        child = self.stat_output.layout.takeAt(0)
        if child:
            child.widget().deleteLater()


    def init(self):

        main_splitter = QSplitter(self)
        main_splitter.setChildrenCollapsible(False)
        
        self.stat_object_tree = statobject.StatObject()


        #output
        self.stat_output = statoutput.StatOutput(self.stat_object_tree)


        # feature
        self.stat_feature_tree = statfeature.StatFeature(
                self.stat_object_tree, self.stat_output)



        stats_splitter = QSplitter(0x2, self)
        stats_splitter.setChildrenCollapsible(False)


        stats_splitter.addWidget(self.stat_output)
        stats_splitter.addWidget(self.stat_feature_tree)

        stats_splitter.resize(900, stats_splitter.height())



        main_splitter.addWidget(self.stat_object_tree)
        main_splitter.addWidget(stats_splitter)



        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

 


