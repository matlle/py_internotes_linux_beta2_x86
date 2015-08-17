# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtSql import *

import tools, photopreview, academicyear, classe, student, topic

class Infos(QTabWidget):
    def __init__(self, in_student_tree, parent=None):
        super(Infos, self).__init__(parent)
        
        self.student_tree = in_student_tree # instance

        self.init()

        self.student_id = 0
        self.std_name = ''
        self.std_genre = ''

        self.previous_stid = 0

        # events
        self.connect(self, SIGNAL("currentChanged(int)"), 
            self.showMarksOnTabChange)
        


     
    def init(self):
        self.page_infos = QWidget()
        #self.page_infos.setStyleSheet("background-color: white;")

        self.widget_page_marks = QWidget()
        self.page_marks = QScrollArea()
        #self.page_marks.setBackgroundRole(QPalette.Shadow)
        #self.page_marks.setBackgroundRole(QPalette.Highlight)
        self.page_marks.setBackgroundRole(QPalette.HighlightedText)




        self.addTab(self.page_infos, u"Informations")
        self.addTab(self.page_marks, u"Notes/Moyennes")

        self.resize(1100, self.height())


    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    @staticmethod
    def rankMe(rank, genre):
        r = ''
        if rank[0] == 0:
            if genre == 'Femme':
                r = u'Non classée'
            else:
                r = u'Non classé'
        else:
            if rank[0] == 1:
                if genre == 'Femme':
                    r = u'1ère%s' % ' ' + rank[1] if rank else ''
                else:
                    r = u'1er%s' % ' ' + rank[1] if rank else ''

            else:
                r = u'%dème%s' % (rank[0], ' ' + rank[1] if rank else '')
        
        return r
         

    def showMarksOnTabChange(self, index, updated=False):
        if index == 1:
            #self.showStudentMarks(clean=True)
            if updated == True:
                self.showStudentMarks(stid=self.student_id,
                                       hinfo=self.std_name,
                                       stdgenre=self.std_genre)
                return
            if self.previous_stid:
                if self.previous_stid == self.student_id:
                    return
            if self.student_id and self.std_name and self.std_genre:
                self.showStudentMarks(stid=self.student_id,
                                       hinfo=self.std_name,
                                       stdgenre=self.std_genre)

                self.previous_stid = self.student_id



    def showStudentMarks(self, stid=0, hinfo=None, stdgenre='Homme', clean=False):
        if clean == True:
            if self.widget_page_marks.layout() is not None:
                self.clearLayout(self.widget_page_marks.layout())
                return
            else:
                return

        self.widget_page_marks = QWidget()

        title = QString(u"<center><h1>Notes et Moyennes</h2>\
                <h3>%s</h2></center>" % hinfo)
        label_title = QLabel(title)
        label_title.setStyleSheet("border: 1px solid black;")
        
        ayid = student.Student.getAcademicYearIdById(stid)
        crid = student.Student.getClassroomIdById(stid)
        period = academicyear.AcademicYear.getPeriodById(ayid)
    
        group_period = []
        c = 0
        if period == 'quarter':
           if student.Student.isStudentHasAnyMarksInThisMarkGroup(stid, 
                   u"1er Trimestre") == True:
               group_period.append(u'1er Trimestre')
           if student.Student.isStudentHasAnyMarksInThisMarkGroup(stid,
                   u"2ème Trimestre") == True:
               group_period.append(u'2ème Trimestre')
           if student.Student.isStudentHasAnyMarksInThisMarkGroup(stid,
                   u"3ème Trimestre") == True:
               group_period.append(u'3ème Trimestre')

        elif period == 'semester':
           if student.Student.isStudentHasAnyMarksInThisMarkGroup(stid, 
                   u"1er Semestre") == True:
               group_period.append(u'1er Semestre')
           if student.Student.isStudentHasAnyMarksInThisMarkGroup(stid, 
                   u"2ème Semestre") == True:
               group_period.append(u'2ème Semestre')
       
        

        label_table = QLabel()
        label_table.setAlignment(Qt.AlignCenter)
        label_table.setStyleSheet("font-size: 14px; color: white;")
        table = QString(u"")
        if group_period:
            topics = classe.Class.getAllTopicsByClassroomId(crid)




        for c in range(0, len(group_period)):
            mg = unicode(group_period[c])

            table += u"<br/><center><h2>%s</h2></center>" % group_period[c]
            table += u"<table border='0.6' width='900'>"
            table += u"<thead><tr bgcolor='#585d5f'><th>MATIÈRE</th><th>NOTE</th>\
                       <th>MOYENNE</th><th>COEF</th><th>MOYENNE X COEF</th><th>RANG</th>\
                       <th>PROFESSEUR</th>\
                       </tr></thead>"

            total_coef = 0 
            total_mycoef = 0.0
            total_level_mycoef = 0
            bs_coef = 0
            bs_mycoef = 0.0
            level_mycoef = 0
            bs_level_mycoef = 0

            bs_my_level = 0


            for i in range(0, len(topics)):
                tid = topics[i][0]
                marks = topic.Topic.getAllMarksByIdStudentIdAndMarkGroup(tid, stid, mg)
                prof = topic.Topic.getProfById(tid)
                my = student.Student.getStudentAverageByTopicAndMarkGroup(tid, stid, mg)

                coef = 0 
                if len(marks):
                    coef = topics[i][2]
                    bs_coef += coef
                    if coef:
                        level_mycoef = coef * 20
                    else:
                        level_mycoef = 20

                    bs_level_mycoef += level_mycoef

                    rank = student.Student.getStudentAverageRankByTopicAndMarkGroup(
                                crid, tid, my, mg)

                    rank = self.rankMe(rank, stdgenre)
                else:
                    if stdgenre == 'Femme':
                        rank = u'Non classée'
                    else:
                        rank = u'Non classé'

                table += u"<tr><td>"+ topics[i][1] + u" ("+str(len(marks))+")</td>\
                               <td><table border='0.3' width='100%'>" \
                    

                if coef:
                    mycoef = my * coef
                else:
                    mycoef = my

                bs_mycoef += mycoef

                for m in range(0, len(marks)):
                    table += u"<tr><td style='font-weight: bold'>%.2f/%d</td>\
                               <td style='font-weight: bold; color: green;'>%s</td></tr>" \
                                   % (marks[m][1], marks[m][2], marks[m][4]) 
                    
                table += u"<table></td>"
                if len(marks):
                    bs_my_level = 20
                    table += u"<td style='font-weight: bold; color: #e30e39'>%.2f/20</td>" % \
                             my 
                else:
                    table += u"<td style='font-weight: bold; color: #e30e39'>%s</td>" % \
                                     ' ' 
                if coef or mycoef:
                    table += u"<td>%s</td><td>%.2f/%d</td>" \
                                        % (coef if coef else '', mycoef, level_mycoef)
                    #bs_level_mycoef += level_mycoef

                else:
                    table += u"<td>%s</td><td>%s</td>" \
                                        % (' ', ' ')
                    #elif my == 0.0:
                    #    table += u"<td>%d</td><td>%s</td>" \
                    #                    % (coef, ' ')

                table += u"<td>%s</td><td>%s</td>" % (rank, prof if prof else ' ')
                table += u"</tr>" 

                topic_type = topics[i][3]
                bs = student.Student.getBalanceSheetByTopicsTypeAndMarkGroup(
                            topic_type, stid, mg)

                bs_my = student.Student.getStudentAverageByTopicTypeAndMarkGroup(
                            stid, mg, topic_type)
                    #if my:
                    #    bs_my_level = 20

                bs_rank = student.Student.getStudentAverageRankByTopicTypeAndMarkGroup(
                            crid, topic_type, mg, bs_my)

                bs_rank = self.rankMe(bs_rank, stdgenre)


                try:
                    if topics[i][3] != topics[i+1][3]:
                        total_coef += bs_coef
                        total_mycoef += bs_mycoef 
                        total_level_mycoef += bs_level_mycoef
                        table += u"<tr bgcolor='#767c7f'><td style='font-weight: bold;\
                                            font-style:italic'>Bilan %s</td>\
                                            <td style='font-weight: bold; font-style: italic'>\
                                            %.2f/%d</td><td style='font-weight: bold;\
                                            font-style: italic'>%.2f/%d</td>\
                                            <td style='font-weight: bold;\
                                            font-style: italic'>%d</td>\
                                            <td style='font-weight: bold;\
                                            font-style: italic'>%.2f/%d</td>\
                                            <td style='font-weight: bold;\
                                     font-style: italic'>%s</td><td colspan='1'> \
                                    </tr>" % (topic_type, bs["sm"], bs["sl"],
                                             bs_my, bs_my_level, bs_coef, 
                                             bs_mycoef, bs_level_mycoef, bs_rank)
                        bs_coef = 0
                        bs_mycoef = 0.0
                        bs_level_mycoef = 0 
                        bs_my_level = 0
                except IndexError:
                    total_coef += bs_coef
                    total_mycoef += bs_mycoef 
                    total_level_mycoef += bs_level_mycoef
                    table += u"<tr bgcolor='#767c7f'><td style='font-weight: bold;\
                                       font-style:italic'>Bilan %s</td>\
                                       <td style='font-weight: bold;\
                                font-style: italic'>%.2f/%d</td><td style='font-weight: bold;\
                                 font-style: italic'>%.2f/%d</td>\
                                 <td style='font-weight: bold;\
                                 font-style: italic'>%d</td>\
                                 <td style='font-weight: bold; font-style: italic'>%.2f/%d</td>\
                                 <td style='font-weight: bold;\
                                 font-style: italic'>%s</td>\
                                 <td colspan='1'></td> \
                                 </tr>" % (topic_type, bs["sm"], bs["sl"],
                                         bs_my, bs_my_level, bs_coef, 
                                         bs_mycoef, bs_level_mycoef, bs_rank) 
                    bs_coef = 0
                    bs_mycoef = 0.0
                    bs_level_mycoef = 0 
                    bs_my_level = 0

                #bs_mg = student.Student.getBalanceSheetByMarkGroup(stid, mg)


            table += u"<tr><td>Total points:</td> \
                          <td style='font-weight: bold;'>%.2f/%d</td>" % \
                          (total_mycoef, total_level_mycoef)
                          #(bs_mg["sm"], bs_mg["sl"])

            table += u"<td>Total coefficient:</td> \
                          <td style='font-weight: bold;'>%d</td>" % \
                            total_coef
                            #student.Student.getTotalSumCoef(crid)
            table += u"<td colspan='3'></td> \
                         </tr>" 

            table += u"</table>"

            # bs_mg_my must be: total_mycoef / total_coef
            # bs_mg_my = total_mycoef / total_coef
            bs_mg_my = student.Student.getStudentAverageByMarkGroup(stid, mg)

            bs_mg_rank = student.Student.getStudentAverageRankByMarkGroup(crid, mg, bs_mg_my)
            bs_mg_rank = self.rankMe(bs_mg_rank, stdgenre)

            table += u"<center><table border='0.4' style='margin-top: 10px;'> \
                        <tr><td>"

            if c != 0:
                table += u"<table border='0.3'>\
                                   <tr><th>Rappel</th><th>Moyenne</th><th>Rang</th></tr>" 
                if period == 'quarter':
                    if c == 1:
                        g = u'1er Trimestre'
                        r_mg_my = student.Student.getStudentAverageByMarkGroup(stid, g)
                        r_mg_rank = student.Student.getStudentAverageRankByMarkGroup(
                                    crid, g, r_mg_my)

                        r_mg_rank = self.rankMe(r_mg_rank, stdgenre)

                        table += u"<tr><td>1er Trimestre</td>" 
                        table += u"<td>%.2f/20</td>" % r_mg_my
                        table += u"<td>%s</td></tr>" % r_mg_rank

                    elif c == 2:
                        g = u'1er Trimestre'
                        r_mg_my = student.Student.getStudentAverageByMarkGroup(stid, g)
                        r_mg_rank = student.Student.getStudentAverageRankByMarkGroup(
                                    crid, g, r_mg_my)

                        r_mg_rank = self.rankMe(r_mg_rank, stdgenre)
                        table += u"<tr><td>1er Trimestre</td>"
                        table += u"<td>%.2f/20</td>" % r_mg_my 
                        table += u"<td>%s</td></tr>" % r_mg_rank 
                    


                        g = u'2ème Trimestre'
                        r_mg_my = student.Student.getStudentAverageByMarkGroup(stid, g)
                        r_mg_rank = student.Student.getStudentAverageRankByMarkGroup(
                                    crid, g, r_mg_my)

                        r_mg_rank = self.rankMe(r_mg_rank, stdgenre)
                        table += u"<tr><td>2ème Trimestre</td>"
                        table += u"<td>%.2f/20</td>" % r_mg_my
                        table += u"<td>%s</td></tr>" % r_mg_rank 

                else:
                    g = u'1er Semestre'
                    r_mg_my = student.Student.getStudentAverageByMarkGroup(stid, g)
                    r_mg_rank = student.Student.getStudentAverageRankByMarkGroup(
                                    crid, g, r_mg_my)

                    r_mg_rank = self.rankMe(r_mg_rank, stdgenre)
                    table += u"<tr><td>1er Semestre</td>" 
                    table += u"<td>%.2f/20</td>" % r_mg_my
                    table += u"<td>%s</td></tr>" % r_mg_rank


                table += u"</table>"

            table += u"Moyenne du %s:<center><h3>%.2f/20</h3></center></td>" % \
                        (mg, bs_mg_my) 

            avg_slices = classe.Class.getSlicesAverageByMarkGroup(crid, mg)

            """table += u"<td rowspan='2'> \
                           <table border='0.4'> \
                               <tr><td><em>TH + FELICITATION</em></td>\
                                   <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
                                   </td></tr> \
                               <tr><td><em>TH + ENCOURAGEMENT</em></td><td></td></tr> \
                               <tr><td><em>TABLEAU D'HONNEUR</em></td><td></td></tr> \
                               <tr><td><em>AVERTISSEMENT</em></td><td></td></tr> \
                               <tr><td><em>BLAME</em></td><td></td></tr> \
                               <tr><td><em>ABSENCES JUSTIFIÉES</em></td><td></td></tr> \
                               <tr><td><em>ABSENCES NON JUSTIFIÉES</em></td><td></td></tr> \
                           </table> \
                       </td>
                    """

            table += u"<td rowspan='2'><center>Repartition des moyennes par tranche</center> \
                             <table border='0.3' width='100%'>" 

            table += u"<tr><td style='font-weight: bold;'><center>] - ; 0]</center></td>\
                            <td style='font-weight: bold;'><center>] - ; 8.50]</center></td>\
                            <td style='font-weight: bold;'><center>[8.50 ; 10.00]</center></td>\
                            <td style='font-weight: bold;'><center>[10.00 ; - [</center></td>\
                                 </tr> \
                            <tr style='font-weight: bold;'>\
                            <td style='font-weight: bold;'><center>%d</center></td>\
                            <td style='font-weight: bold;'><center>%d</center></td>\
                            <td style='font-weight: bold;'><center>%d</center></td>\
                            <td style='font-weight: bold;'><center>%d</center></td></tr>" % \
                                (avg_slices[0], avg_slices[1], avg_slices[2], avg_slices[3])

            first_last = classe.Class.getFirstStudentAverageAndLastStudentAverageByMarkGroup(\
                        crid, mg)

            table += u"<tr><td>Moyenne du 1er: </td>\
                           <td style='font-weight: bold'>%.2f/20</td>" % \
                        first_last[0] 
            table += u"<td>Moyenne du dernier: </td>\
                           <td style='font-weight: bold;'>%.2f/20</td>\
                            </tr>" % first_last[1] 

            cr_avg = classe.Class.getClassroomAverageByMarkGroup(crid, mg)

            table += u"<tr><td>Moyenne de la classe: </td>\
                             <td colspan='3' style='font-weight: bold;'> \
                             <center>%.2f/20</center></td></tr>" % cr_avg 
            end = False 
            if period == 'quarter':
                if c == 2:
                    end = True 
            else:
                if c == 1:
                    end = True 

            if end:
                yearly_my = student.Student.getStudentYearlyAverage(stid)

                yearly_rank = student.Student.getStudentYearlyRank(
                                    crid, yearly_my)
                yearly_rank = self.rankMe(yearly_rank, stdgenre)
                table += u"<tr><td colspan='4' rowspan='2'><br/>\
                            <center>Moyenne annuelle: \
                            <span style='font-weight: bold;'>%.2f/20</span></center>\
                            <center>Rang annuelle:\
                            <span style='font-weight: bold;'>%s</span></center>\
                               </td></tr>" % (yearly_my, yearly_rank)


            table += u"<table> \
                        </td></tr>" 
                        

            table += u"<tr><td> \
                        Rang: <center><h3>%s</h3></center></td>" % bs_mg_rank \

            table += u"</tr>"

            """table += u"<tr><td><center>PROFESSEUR PRINCIPAL</center><br/><br/><br/></td>\
                           <td><center>DIRECTEUR DES ÉTUDES</center></td>\
                           <td><center>Decision du conseil de classe</center></td></tr>"
            """
            
            table += u"</table><center>"


            #c += 1

        label_table.setText(table)
        
        layout_main = QVBoxLayout()
        if group_period:
            layout_main.addWidget(label_title)
        layout_main.addWidget(label_table)

        

        if self.widget_page_marks.layout() is not None:
            self.clearLayout(self.widget_page_marks.layout())
            layout = self.widget_page_marks.layout() 
            if group_period:
                layout.addWidget(label_title)
            layout.addWidget(label_table)
        else:
            self.widget_page_marks.setLayout(layout_main)
            
        self.page_marks.setWidget(self.widget_page_marks)

        

        


    def showStudentInfos(self, current_proxy_index=0, updated=False):
        if current_proxy_index == 0:
            if self.page_infos.layout() is not None:
                self.clearLayout(self.page_infos.layout())
                self.student_id = 0
                self.showStudentMarks(clean=True)
                return
            else:
                return
        else:
            model_index = self.student_tree.proxy_model.mapToSource(current_proxy_index)
            student_item = self.student_tree.model.itemFromIndex(model_index)
            if not student_item:
                if self.page_infos.layout() is not None:
                    self.clearLayout(self.page_infos.layout())
                    self.student_id = 0
                    self.showStudentMarks(clean=True)
                    return


        #model_index = self.student_tree.proxy_model.mapToSource(current_proxy_index)
        #student_item = self.student_tree.model.itemFromIndex(model_index)
        student_id = student_item.accessibleText().toInt()[0]

        if self.student_id and updated == False:
            if student_id == self.student_id:
                return

        infos = self.student_tree.getStudentInfosById(student_id)

        academic_name = academicyear.AcademicYear.getNameById(infos["academic_year_id"])

        stdname = academic_name + ": " +infos['student_last_name'] + " " + infos['student_first_name'] + \
                  ": " + infos['classroom_name']
        kind = infos['student_genre']

        self.student_id = student_id
        self.std_name = stdname
        self.std_genre = kind

        if self.currentIndex() == 1:
            self.showStudentMarks(stid=student_id, hinfo=stdname, stdgenre=kind)
            self.previous_stid = student_id 
        else:
            self.previous_stid = 0


        layout_form_infos = QFormLayout()
        student_last_name = QLineEdit(infos['student_last_name'])
        student_last_name.setReadOnly(True)
        student_last_name.setStyleSheet("font-size: 14px; font-weight: bold;")

        student_first_name = QLineEdit(infos['student_first_name'])
        student_first_name.setReadOnly(True)
        student_first_name.setStyleSheet("font-size: 14px; font-weight: bold;")

        student_birth_date = QLineEdit(infos['student_birth_date'])
        student_birth_date.setReadOnly(True)
        student_birth_date.setStyleSheet("font-size: 14px; font-weight: bold;")

        student_birth_place = QLineEdit(infos['student_birth_place'])
        student_birth_place.setReadOnly(True)
        student_birth_place.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_genre = QLineEdit(infos['student_genre'])
        student_genre.setReadOnly(True)
        student_genre.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_height = QLineEdit(QString.number(infos['student_height']))
        student_height.setReadOnly(True)
        student_height.setStyleSheet("font-size: 16px; font-weight: bold;")


        student_academic_year_name = QLabel(QString(u"Année: <span style='font-size: 18px; font-weight: bold;'>" +
                                          academic_name + 
                                          "</span>"))

        student_classroom_name = QLabel(QString(u"Classe: <span style='font-size: 18px; font-weight: bold;'>" +
                                          infos['classroom_name'] + 
                                          "</span>"))

        student_matricule = QLabel(QString(u"Matricule: <span style='font-size: 18px; font-weight: bold;'>" + 
                                          infos['student_matricule'] + 
                                          "</span>"))

        student_matricule_ministeriel = QLabel(
                                     QString(u"Matricule ministeriel: <span style='font-size: 18px; font-weight: bold;'>" 
                                     + infos['student_matricule_ministeriel'] + 
                                     "</span>"))

        student_previous_school = QLineEdit(infos['student_previous_school'])
        student_previous_school.setReadOnly(True)
        student_previous_school.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_previous_classroom = QLineEdit(infos['student_previous_classroom'])
        student_previous_classroom.setReadOnly(True)
        student_previous_classroom.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_statut = QLineEdit(infos['student_statut'])
        student_statut.setReadOnly(True)
        student_statut.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_redoubler = QLineEdit(infos['student_redoubler'])
        student_redoubler.setReadOnly(True)
        student_redoubler.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_email = QLineEdit(infos['student_email'])
        student_email.setReadOnly(True)
        student_email.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_phone1 = QLineEdit(infos['student_phone1'])
        student_phone1.setReadOnly(True)
        student_phone1.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_phone2 = QLineEdit(infos['student_phone2'])
        student_phone2.setReadOnly(True)
        student_phone2.setStyleSheet("font-size: 16px; font-weight: bold;")

        student_phone3 = QLineEdit(infos['student_phone3'])
        student_phone3.setReadOnly(True)
        student_phone3.setStyleSheet("font-size: 16px; font-weight: bold;")
       
        layout_form_infos.addRow(u"Nom: ", student_last_name)
        layout_form_infos.addRow(u"Prénom ", student_first_name)
        layout_form_infos.addRow(u"Date de naissance: ", student_birth_date)
        layout_form_infos.addRow(u"Lieu de naissance: ", student_birth_place)
        layout_form_infos.addRow(u"Genre: ", student_genre)
        layout_form_infos.addRow(u"Taille (cm): ", student_height)
        layout_form_infos.addRow(u"Statut: ", student_statut)
        layout_form_infos.addRow(u"Ecole précedante: ", student_previous_school)
        layout_form_infos.addRow(u"Classe précedante: ", student_previous_classroom)
        layout_form_infos.addRow(u"Redoublant: ", student_redoubler)
        layout_form_infos.addRow(u"Email: ", student_email)
        layout_form_infos.addRow(u"Téléphone 1: ", student_phone1)
        layout_form_infos.addRow(u"Téléphone 2: ", student_phone2)
        layout_form_infos.addRow(u"Téléphone 3: ", student_phone3)


        btn_photo = QPushButton()
        if infos['student_photo_name'] is not None and \
                not infos['student_photo_name'].isEmpty() and not \
                QImage(infos['student_photo_name']).isNull():
            btn_photo.setIcon(QIcon(infos['student_photo_name']))
        else:
            btn_photo.setIcon(QIcon(":/images/user-icon.png"))
        btn_photo.setIconSize(QSize(200, 200))


        layout_photo = QVBoxLayout()
        layout_photo.addWidget(btn_photo)
        layout_photo.addWidget(student_academic_year_name)
        layout_photo.addWidget(student_classroom_name)
        layout_photo.addWidget(student_matricule)
        layout_photo.addWidget(student_matricule_ministeriel)
        layout_photo.setAlignment(Qt.AlignTop)

        group_photo = QGroupBox()
        group_photo.setLayout(layout_photo)

        group_infos = QGroupBox(u"Informations personnelles")
        group_infos.setLayout(layout_form_infos)
        group_infos.setAlignment(Qt.AlignHCenter)
       
        layout_main = QHBoxLayout() 
        layout_main.addWidget(group_infos)
        layout_main.addWidget(group_photo)


        if self.page_infos.layout() is not None:
            self.clearLayout(self.page_infos.layout())
            layout = self.page_infos.layout() 
            layout.addWidget(group_infos)
            layout.addWidget(group_photo)

        else:
            self.page_infos.setLayout(layout_main)



