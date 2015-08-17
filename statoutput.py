# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools, student, topic, classe, academicyear

import Tkinter
import FileDialog
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator, MultipleLocator

import numpy as np

from operator import itemgetter

import random, datetime as dt



class StatOutput(QScrollArea):
    def __init__(self, in_stat_object_tree, parent=None):
        super(StatOutput, self).__init__(parent)

        self.stat_object_tree = in_stat_object_tree # "in" means instance

        self.figure = plt.figure(facecolor='#979797')

        #self.canvas = FigureCanvas(self.figure)

        self.init()
  

    def clearLayout(self):
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    
    def plotCurve(self, stid, period, tid, tname):

        plt.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

        date = []
        mark = []
        marks = topic.Topic.getAllMarksByIdStudentIdAndMarkGroup(tid, stid, period)

        ran = []

        for m in range(0, len(marks)):
            mark.append(marks[m][1])
            d = marks[m][4]
            d = unicode(d)
            d = d.encode('utf-8')
            ran.append(int(d[0:2]))
            date.append(d)


        date = [dt.datetime.strptime(d,'%d/%m/%Y').date() for d in date]

        
        #plt.gca().xaxis.set_minor_locator(mdates.DayLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))

        plt.gca().yaxis.set_ticks(mark) 


        plt.gca().xaxis.grid(True, which="minor")
        

        plt.plot(date, mark, label='Evolution des notes', marker='o')
        plt.gcf().autofmt_xdate()
        plt.xlabel('Dates')
        plt.ylabel('Notes')

        plt.title(period + " - " + tname)

        plt.legend()
        plt.grid()

        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()

        child = self.layout.takeAt(0)
        if child:
            child.widget().deleteLater()

        self.layout.addWidget(self.canvas)

    
    def plotPie(self, stid, period, topics):
        labels = [] 
        sizes = []
        for i in range(0, len(topics)):
            tid = topics[i]["topic_id"]
            mg = student.Student.getStudentAverageByTopicAndMarkGroup(tid, stid, period)
            sizes.append(mg)

            labels.append(topics[i]["topic_name"] + " (" + str(mg) + "/20)")

        labels = tuple(labels)


        explode = []
        for i in sizes:
            if i == max(sizes):
                explode.append(0.1)
            else:
                explode.append(0)


        colors = plt.cm.Set1(np.linspace(0,1,9))

        patches = plt.pie(sizes, explode=explode, labels=labels, colors=colors, 
                        autopct='%1.2f%%', shadow=True, startangle=90)

        plt.title(period, loc="left", bbox=dict(facecolor='0.8',), fontsize=30)
        
        #"lower left", bbox_to_anchor=(-0.15, 0)
        plt.legend(labels, loc="lower left", bbox_to_anchor=(-0.15, 0),
                          fancybox=True, framealpha=0.3, shadow=True)


        plt.axis('equal')

        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()

        child = self.layout.takeAt(0)
        if child:
            child.widget().deleteLater()

        self.layout.addWidget(self.canvas)


    def showPlot(self, item):
        self.figure.clear()

        current_proxy_index = self.stat_object_tree.currentIndex()
        model_index = self.stat_object_tree.proxy_model.mapToSource(current_proxy_index)
        std_item = self.stat_object_tree.model.itemFromIndex(model_index)
        stid = std_item.accessibleText().toInt()[0]


        if item.parent():
            # It's a topic
            period = item.parent().text(0)
            tid = item.data(0, 11).toInt()[0]
            tname = item.text(0)

            self.plotCurve(stid, period, tid, tname)
        else:
            topics = []
            # It's a period
            period = item.text(0)
            for c in range(0, item.childCount()):
                data = {}
                child_item = item.child(c)
                child_id = child_item.data(0, 11).toInt()[0]
                child_name = child_item.text(0)

                data["topic_id"] = child_id
                data["topic_name"] = child_name
                
                topics.append(data)

            #topics = tuple(topics)

            self.plotPie(stid, period, topics)


    def showHist(self, item):
        if not item.parent():
            return
        self.figure.clear()

        current_proxy_index = self.stat_object_tree.currentIndex()
        model_index = self.stat_object_tree.proxy_model.mapToSource(current_proxy_index)
        cr_item = self.stat_object_tree.model.itemFromIndex(model_index)
        crid = cr_item.accessibleText().toInt()[0]
        cr_name = cr_item.text()

        ayid = item.data(0, 11).toInt()[0]
        period_name = item.text(0)

        students = classe.Class.getAllStudentsIdAndNameByClassroomId(crid)
        stds = []
        stds_name = []
        stds_my = []

        for s in range(0, len(students)):
            if student.Student.isStudentHasAnyMarksInThisMarkGroup(
                    students[s]["student_id"], period_name):
                
                row = {}
                n = students[s]["student_last_name"] + " " + \
                             students[s]["student_first_name"]

                row["student_name"] = n.toLower()

                my = student.Student.getStudentAverageByMarkGroup(
                        students[s]["student_id"], period_name)
                
                row["student_my"] = my

                stds.append(row)


        stds = sorted(stds, key=itemgetter('student_my'))
        stds_my = [stds[x]["student_my"] for x in range(0, len(stds))]
        stds_name = [stds[x]["student_name"] for x in range(0, len(stds))]

        pos = np.arange(len(stds))+.5    # the bar centers on the y axis


        plt.barh(pos, stds_my, height=0.5, color='#3d8ec9', alpha=1, align='center')

        plt.yticks(pos, stds_name)
        

        plt.xlabel('Moyenne (/20)')
        plt.title(cr_name + ' - ' + period_name)

        plt.xticks(stds_my)
        plt.gcf().autofmt_xdate()

        plt.grid(True)

        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()

        child = self.layout.takeAt(0)
        if child:
            child.widget().deleteLater()

        self.layout.addWidget(self.canvas)



    def showClassSlicesPie(self, clid, period):
        labels = [] 
        avgs = []
        cl_name = classe.Class.getClassNameById(clid)
        classrooms = classe.Class.getClassroomsIdAndNameByClassId(clid)

        for i in range(0, len(classrooms)):
            crid = classrooms[i]["classroom_id"]
            my = classe.Class.getClassroomAverageByMarkGroup(
                    crid, period)

            if my == 0.0:
                continue
            avgs.append(my)


            labels.append(
                    classrooms[i]["classroom_name"] + \
                            " (" + str(my) + "/20)")


        labels = tuple(labels)


        explode = []
        for i in avgs:
            if i == max(avgs):
                explode.append(0.1)
            else:
                explode.append(0)


        colors = plt.cm.Set1(np.linspace(0,1,9))

        patches = plt.pie(avgs, explode=explode, 
                        labels=labels, colors=colors, 
                        autopct='%1.2f%%', shadow=True, startangle=90)

        plt.title(period, 
                loc="left", bbox=dict(facecolor='0.8',),
                fontsize=30)
        
        plt.legend(labels, loc="lower left", 
                          bbox_to_anchor=(-0.15, 0),
                          fancybox=True, framealpha=0.3,
                          shadow=True)


        plt.axis('equal')

        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()

        child = self.layout.takeAt(0)
        if child:
            child.widget().deleteLater()

        self.layout.addWidget(self.canvas)

    
    def showClassSlicesHist(self, clid, period):
        self.figure.clear()

        cl_name = classe.Class.getClassNameById(clid)
        classrooms = classe.Class.getClassroomsByClassId(clid)

        stds = []
        stds_name = []
        stds_my = []

        for s in range(0, len(classrooms)):
            room_id = classrooms[s]["classroom_id"]
            room_name = classe.Class.getClassroomNameById(room_id) 
            first = classe.Class.getFirstStudentAverageAndStudentIdAndStudentNameByMarkGroup(
                    room_id, period)
            if first:
                row = {}
                row["student_my"] = first[0]["bs_mg_my"]

                n = first[0]["std_lname"] + " " + \
                             first[0]["std_fname"].toLower()

                n += " (" + room_name + ")"

                row["student_name"] = n


                stds.append(row)


        stds = sorted(stds, key=itemgetter('student_my'), reverse=True)
        stds_my = [stds[x]["student_my"] for x in range(0, len(stds))]
        stds_name = [stds[x]["student_name"] for x in range(0, len(stds))]

        pos = np.arange(len(stds))+.5    # the bar centers on the y axis

        x = np.arange(len(stds_my))

        plt.bar(x, stds_my, color='#3d8ec9',
                alpha=0.8)

        plt.xticks(pos, stds_name)
        plt.gcf().autofmt_xdate()
        plt.title(cl_name + " - " + period)
        plt.ylabel('Moyenne (/20)')
        plt.yticks(stds_my)

        plt.grid(True)
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()

        child = self.layout.takeAt(0)
        if child:
            child.widget().deleteLater()

        self.layout.addWidget(self.canvas)





    def showClassSlicesPlot(self, item):
        if not item.parent():
            return

        self.figure.clear()
        
        clid = item.data(0, 11).toInt()[0]
        period = item.text(0)

        parent_data = item.parent().data(0, 11).toString()

        if parent_data == "classes_my":
            self.showClassSlicesPie(clid, period)
        elif parent_data == "firsts_my":
            self.showClassSlicesHist(clid, period)

    
    def showAcademicYearStudentsYearlyAverageHist(self, item):
        current_proxy_index = self.stat_object_tree.currentIndex()
        model_index = self.stat_object_tree.proxy_model.mapToSource(current_proxy_index)
        ay_item = self.stat_object_tree.model.itemFromIndex(model_index)
        ayid = ay_item.accessibleText().toInt()[0]
        ay_name = ay_item.text()

        students_ym = []

        period = academicyear.AcademicYear.getPeriodById(ayid)
        students_from_ayid = academicyear.AcademicYear.getAllStudentsIdAndNameById(ayid)
        
        for i in range(0, len(students_from_ayid)):
            sid = students_from_ayid[i]["student_id"]

            if period == "quarter":
                if not student.Student.isStudentHasAnyMarksInThisMarkGroup(
                        sid, u"1er Trimestre") or \
                   not student.Student.isStudentHasAnyMarksInThisMarkGroup(
                        sid, u"2ème Trimestre") or \
                   not student.Student.isStudentHasAnyMarksInThisMarkGroup(
                           sid, u"3ème Trimestre"):
                       continue
                else:
                    students_ym.append(students_from_ayid[i])

            else:
                if not student.Student.isStudentHasAnyMarksInThisMarkGroup(
                        sid, u"1er Semestre") or \
                   not student.Student.isStudentHasAnyMarksInThisMarkGroup(
                        sid, u"2ème Semestre"):
                       continue
                else:
                    students_ym.append(students_from_ayid[i])


        for i in range(0, len(students_ym)):
            sid = students_ym[i]["student_id"]
            students_ym[i]["ym"] = student.Student.getStudentYearlyAverage(sid)
            students_ym[i]["cr_name"] = student.Student.getClassroomNameById(sid)


        
        students_ym = sorted(students_ym, key=itemgetter('ym'), reverse=True)

        students_ym_ten_firsts = students_ym[:10]

        stds_ym = [students_ym_ten_firsts[x]["ym"] for x in range(0, len(students_ym_ten_firsts))]
        stds_name = [students_ym_ten_firsts[x]["student_last_name"] \
                + " " + students_ym_ten_firsts[x]["student_first_name"] \
                + " (" + students_ym_ten_firsts[x]["cr_name"] + ")" for x in range(0, len(
            students_ym_ten_firsts))]

        pos = np.arange(len(students_ym_ten_firsts))+.5    # the bar centers on the y axis

        x = np.arange(len(students_ym_ten_firsts))

        plt.bar(x, stds_ym, color='#3d8ec9',
                alpha=0.8)

        plt.xticks(pos, stds_name)
        plt.gcf().autofmt_xdate()

        plt.title(ay_name + u" - Moyenne annuelle")
        plt.ylabel('Moyenne annuelle (/20)')
        plt.yticks(stds_ym)

        plt.grid(True)

        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()
        
        child = self.layout.takeAt(0)
        if child:
            child.widget().deleteLater()

        self.layout.addWidget(self.canvas)


    def showAcademicClassesYearlyAveragePie(self, item):
        pass


    def showAcademicYearPlot(self, item):
        self.figure.clear()

        item_name = item.data(0, 11).toString()

        if item_name == "stds_ym":
            self.showAcademicYearStudentsYearlyAverageHist(item)
        elif item_name == "classes_ym":
            self.showAcademicYearClassesYearlyAveragePie(item)


    def onPrintGraph(self):
        pass
    
    def onExportGraph(self):
        pass


    def init(self):
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)

        self.resize(self.width(), 900)



    """
    def contextMenuEvent(self, event):
        menu = QMenu()

        action_print_graph = tools.createAction(self, u"&Imprimer ce graphique", 
                self.onPrintGraph, "Ctrl+Alt+G",
                u"Imprimer ce graphique", u"Imprimer ce graphique")
   
        action_export_graph = tools.createAction(self, u"&Exporter ce graphique (PDF)", 
                self.onExportGraph, "Ctrl+Alt+E",
                u"Exporter ce graphique", u"Exporter ce graphique au format PDF")
        
        #if self.currentIndex() is None or self.currentIndex().isValid() == False:
        #    action_edit.setEnabled(False)
        #    action_delete.setEnabled(False)
        #else:
        #    action_edit.setEnabled(True)
        #    action_delete.setEnabled(True)


        menu.addAction(action_print_graph)
        menu.addAction(action_export_graph)
        menu.exec_(event.globalPos())
    """
