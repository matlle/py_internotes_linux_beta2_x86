# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, student, academicyear, classe, topic


class StatFeature(QTreeWidget):
    def __init__(self, in_stat_object_tree, in_stat_output, parent=None):
        super(StatFeature, self).__init__(parent)

        self.setSortingEnabled(True)
        self.sortItems(0, Qt.AscendingOrder)
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        self.header().setDefaultAlignment(Qt.AlignCenter);

        self.setHeaderLabel(QString(u""))

        self.stat_object_tree = in_stat_object_tree 

        self.stat_output = in_stat_output # 'in' means 'instance of'

        self.object_descr = ''




        self.connect(self, SIGNAL("itemClicked(QTreeWidgetItem*, int)"), self.output)

        



    def output(self, item, col):
        if self.object_descr == 'std':
            self.stat_output.showPlot(item)
        elif self.object_descr == 'cr':
            self.stat_output.showHist(item)
        elif self.object_descr == 'cl':
            self.stat_output.showClassSlicesPlot(item)
        elif self.object_descr == 'ay':
            self.stat_output.showAcademicYearPlot(item)
        


    def setStudentFeatures(self, stid, crid):
        ayid = student.Student.getAcademicYearIdById(stid)
        ay_period = academicyear.AcademicYear.getPeriodById(ayid)
        if ay_period == "quarter":
            periods = [u"1er Trimestre", u"2ème Trimestre", 
                      u"3ème Trimestre"]
        else:
            periods = [u"1er Semestre", u"2ème Semestre"]

        for p in periods:
            if student.Student.isStudentHasAnyMarksInThisMarkGroup(
                    stid, p) == True:
                cr_item = QTreeWidgetItem(self, QStringList(p))
                cr_item.setData(0, 11, QVariant(ayid))

                topics = classe.Class.getAllTopicsByClassroomId(crid)
                for t in range(0, len(topics)):
                    tid = topics[t][0]
                    t_name = topics[t][1]
                    if topic.Topic.isStudentHasAnyMarksInThisTopicAndMarkGroup(
                            tid, stid, p) == True:

                        t_item = QTreeWidgetItem(cr_item, QStringList(t_name))
                        t_item.setData(0, 11, QVariant(tid))
                        cr_item.addChild(t_item) 

                self.insertTopLevelItem(0, cr_item)



    def setClassroomFeatures(self, ayid, crid):
        feature_item = QTreeWidgetItem(self, 
                QStringList(u"Moyennes trimestrielles"))
                        
        feature_item.setData(0, 11, QVariant(u"my_period"))

        period = academicyear.AcademicYear.getPeriodById(ayid)
        
        if period == 'quarter':
            mg = u'1er Trimestre'
            mg_item = QTreeWidgetItem(feature_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(ayid))
            feature_item.addChild(mg_item) 

            mg = u'2ème Trimestre'
            mg_item = QTreeWidgetItem(feature_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(ayid))
            feature_item.addChild(mg_item) 

            mg = u'3ème Trimestre'
            mg_item = QTreeWidgetItem(feature_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(ayid))
            feature_item.addChild(mg_item) 

        else:
            mg = u'1er Semestre'
            mg_item = QTreeWidgetItem(feature_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(ayid))
            feature_item.addChild(mg_item) 

            mg = u'2ème Semestre'
            mg_item = QTreeWidgetItem(feature_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(ayid))
            feature_item.addChild(mg_item) 


        self.insertTopLevelItem(0, feature_item)



    def setClassFeatures(self, ayid, clid):
        classes_my_item = QTreeWidgetItem(self, 
                QStringList(u"Répartition des moyennes de chaque salle de classe"))
                        
        classes_my_item.setData(0, 11, QVariant(u"classes_my"))


        firsts_my_item = QTreeWidgetItem(self, 
                QStringList(u"Répartition des moyennes de premiers de chaque salle de classe "))
                        
        firsts_my_item.setData(0, 11, QVariant(u"firsts_my"))

        period = academicyear.AcademicYear.getPeriodById(ayid)


        if period == 'quarter':
            # classes_my
            mg = u'1er Trimestre'
            mg_item = QTreeWidgetItem(classes_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            classes_my_item.addChild(mg_item) 

            mg = u'2ème Trimestre'
            mg_item = QTreeWidgetItem(classes_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            classes_my_item.addChild(mg_item) 

            mg = u'3ème Trimestre'
            mg_item = QTreeWidgetItem(classes_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            classes_my_item.addChild(mg_item) 



            # firsts_my 
            mg = u'1er Trimestre'
            mg_item = QTreeWidgetItem(firsts_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            firsts_my_item.addChild(mg_item) 

            mg = u'2ème Trimestre'
            mg_item = QTreeWidgetItem(firsts_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            firsts_my_item.addChild(mg_item) 

            mg = u'3ème Trimestre'
            mg_item = QTreeWidgetItem(firsts_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            firsts_my_item.addChild(mg_item) 



        else:
            # classes_my
            mg = u'1er Semestre'
            mg_item = QTreeWidgetItem(classes_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            classes_my_item.addChild(mg_item) 

            mg = u'2ème Semestre'
            mg_item = QTreeWidgetItem(classes_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            classes_my_item.addChild(mg_item) 

            
            # firsts_my
            mg = u'1er Semestre'
            mg_item = QTreeWidgetItem(firsts_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            firsts_my_item.addChild(mg_item) 

            mg = u'2ème Semestre'
            mg_item = QTreeWidgetItem(firsts_my_item, QStringList(mg))
            mg_item.setData(0, 11, QVariant(clid))
            firsts_my_item.addChild(mg_item) 



        self.insertTopLevelItem(0, classes_my_item)
        self.insertTopLevelItem(0, firsts_my_item)
        


    def setAcademicYearFeatures(self, ayid):
        #classes_my_item = QTreeWidgetItem(self, 
        #        QStringList(u"Répartition des moyennes des classes par année"))

        #classes_my_item.setData(0, 11, QVariant(u"classes_ym"))

        std_my_item = QTreeWidgetItem(self, 
                QStringList(u"Répartition des moyennes des 10 premiers de cette année academique"))

        std_my_item.setData(0, 11, QVariant("stds_ym"))

        self.insertTopLevelItem(0, std_my_item)
        #self.insertTopLevelItem(0, classes_my_item)



    def setFeatureTree(self, current_proxy_index):
        self.clear()

        model_index = self.stat_object_tree.proxy_model.mapToSource(current_proxy_index)
        object_item = self.stat_object_tree.model.itemFromIndex(model_index)
        object_id = object_item.accessibleText().toInt()[0]
        self.object_descr = object_item.accessibleDescription()
        object_item_name = object_item.text()

        self.setHeaderLabel(object_item_name)

        if self.object_descr == "std":
            if object_item.parent():
                cr_item = object_item.parent()
                cr_name = cr_item.text()
                crid = cr_item.accessibleText().toInt()[0] 

                if cr_item.parent():
                    cl_item = cr_item.parent()
                    cl_name = cl_item.text()

                    if cl_item.parent():
                        ay_item = cl_item.parent()
                        ay_name = ay_item.text()

                        self.setHeaderLabel(ay_name + " > "+ cl_name + \
                                " > " + cr_name + " > " + object_item_name)


            self.setStudentFeatures(object_id, crid)

        elif self.object_descr == 'cr':
            if object_item.parent():
                cl_item = object_item.parent()
                cl_name = cl_item.text()

                if cl_item.parent():
                    ay_item = cl_item.parent()
                    ay_name = ay_item.text()
                    ayid = ay_item.accessibleText().toInt()[0] 

                    self.setHeaderLabel(ay_name + " > " + cl_name + \
                           " > " + object_item_name)
            

            self.setClassroomFeatures(ayid, object_id)


        elif self.object_descr == 'cl':
            if object_item.parent():
                ay_item = object_item.parent()
                ayid = ay_item.accessibleText().toInt()[0] 
                ay_name = ay_item.text()

                self.setHeaderLabel(ay_name + \
                           " > " + object_item_name)
            

            self.setClassFeatures(ayid, object_id)
                

        elif self.object_descr == 'ay':
            if not object_item.parent():

                self.setHeaderLabel(object_item_name)
            

            self.setAcademicYearFeatures(object_id)


