#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtSql import *

import tools, photopreview, academicyear, classe, student, topic, infos, auth

import uuid

class Export(QDialog):
    def __init__(self, in_student_tree, parent):
        super(Export, self).__init__(parent)
        
        self.student_tree = in_student_tree.student_name_tree    # in_ instance

        self.new_header_image_file_name = ''

        self.init()

        

    @staticmethod
    def isAccountHasLogo():
        header_image = ''
        sql = "SELECT \
                account_print_header_image_name header_image\
               FROM account "

        query = QSqlQuery(sql)
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while (query.next()):
                    header_image = query.value(
                            record.indexOf("header_image")).toString()
            
            if header_image.isNull() or header_image.isEmpty():
                return False 
            else:
                return True

        else:
            print "SQL Error!"

      

    def selectHeaderImage(self):
        photo_file_name = QFileDialog.getOpenFileName(self, u"Sélectioner un logo", QDir.homePath(), 
                                                          "Images (*.png *.jpg *.jpeg)")
        if not photo_file_name.isNull():
            pic = QImage(photo_file_name)
            if pic.isNull():
                QMessageBox.critical(self, u"Sélectioner un logo", 
                          u"Impossible d'ouvrir le fichier '" + photo_file_name + " '")
                return
            
            if pic.width() > 9003.0:
                pic_scaled = pic.scaled(9003, 100)
            else:
                pic_scaled = pic.scaledToHeight(100)

            pic_pixmap = QPixmap.fromImage(pic_scaled)
            dialog_photo_preview = photopreview.PhotoPreview(pic_pixmap, self)
            reply = dialog_photo_preview.exec_()

            self.new_header_image_file_name = QString(
                    QDir.currentPath() + u"/images/upload/header/" + \
                    uuid.uuid1().hex + ".png")

            if reply == 1:
                writer = QImageWriter(self.new_header_image_file_name, "png")
                writer.setQuality(100)
                if not writer.write(pic_scaled):
                    QMessageBox.critical(self, u"Sélectioner un logo",
                                           writer.errorString())

                self.label_image_preview.setPixmap(QPixmap(self.new_header_image_file_name))
                self.btn_header_ok.setEnabled(True)
            else:
                self.new_header_image_file_name = u""



    def showHeaderSetupDialog(self):
        dialog = QDialog(self)

        self.label_image_preview = QLabel()

        btn_select_header_image = QPushButton(u"Cliquer ici pour sélectioner un nouveau logo")

        header_infos = self.getHeaderInfos()

        line_company_name = QLineEdit(auth.Auth.getAccountCompanyName())
        line_localisation = QLineEdit(header_infos["account_school_localization"])
        #line_localisation.setMaxLength(30)
        line_postal = QLineEdit(header_infos["account_postal_address"])
        line_phone_1 = QLineEdit(header_infos["account_phone1"])
        line_phone_1.setInputMask("99-99-99-99")
        line_phone_2 = QLineEdit(header_infos["account_phone2"])
        line_phone_2.setInputMask("99-99-99-99")
 
        radio_minister_national = QRadioButton(u"Ministère de l'éducation nationale", dialog)
        radio_minister_national.setChecked(True)


        radio_minister_technic = QRadioButton(u"Ministère de l'enseignement technique", dialog)

        radio_minister_national_technic = QRadioButton(u"Ministère de l'éducation nationale\n"
                                                 u"et de l'enseignement technique", dialog)

        radio_minister_superior = QRadioButton(u"Ministère de l'enseignement supérieur\n"
                                      u"et de la recherche scientifique", dialog)

        minister = header_infos["header_minister"]
        if minister:
            if minister == u"Ministère de l'éducation nationale":
                radio_minister_national.setChecked(True)
            elif minister == u"Ministère de l'enseignement technique":
                radio_minister_technic.setChecked(True)
            elif minister == u"Ministère de l'éducation nationale et de l'enseignement technique":
                radio_minister_national_technic.setChecked(True)
            elif minister == u"Ministère de l'enseignement supérieur et de la recherche scientifique":
                radio_minister_superior.setChecked(True)

        
        layout_form = QFormLayout()
        layout_form.addRow(u"", self.label_image_preview)
        layout_form.addRow(u"", btn_select_header_image)

        layout_form.addRow(u"Nom de l'établissement: ", line_company_name)
        layout_form.addRow(u"Localisation: ", line_localisation)
        layout_form.addRow(u"Adresse Postale: ", line_postal)
        layout_form.addRow(u"Téléphone 1: ", line_phone_1)
        layout_form.addRow(u"Téléphone 2: ", line_phone_2)

        layout_form_minister = QFormLayout()

        layout_form_minister.addRow(u"Ministère: ", radio_minister_national)
        layout_form_minister.addRow(u"", radio_minister_technic)
        layout_form_minister.addRow(u"", radio_minister_national_technic)
        layout_form_minister.addRow(u"", radio_minister_superior)

        group_minister = QGroupBox(u"À quel ministère votre établissement est-il affilié?")
        group_minister.setLayout(layout_form_minister)

        self.btn_header_ok = QPushButton("Ok")
        self.btn_header_ok.setEnabled(False)
        self.btn_header_ok.setIcon(QIcon(":/images/button_apply.png"))
        btn_header_cancel = QPushButton("Annuler")
        btn_header_cancel.setIcon(QIcon(":/images/button_cancel.png"))

        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_header_ok)
        layout_btn.addWidget(btn_header_cancel)
        layout_btn.setAlignment(Qt.AlignRight)
       

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_form)
        layout_main.addWidget(group_minister)
        layout_main.addLayout(layout_btn)

        dialog.setLayout(layout_main)
        dialog.resize(700, 200)
        dialog.setWindowTitle(u"Entête de document - InterNotes")


        self.connect(btn_select_header_image, SIGNAL("clicked()"),
                self.selectHeaderImage)

        self.connect(self.btn_header_ok, SIGNAL("clicked()"), dialog.accept)
        self.connect(btn_header_cancel, SIGNAL("clicked()"), dialog.reject)



        return (dialog.exec_(), 
                               line_localisation.text(),
                               line_postal.text(),
                               line_phone_1.text(),
                               line_phone_2.text(),
                               radio_minister_national.isChecked(),
                               radio_minister_technic.isChecked(),
                               radio_minister_national_technic.isChecked(),
                               radio_minister_superior.isChecked(),
                               line_company_name.text()
                               )
        


    
    def showEditHeaderSetupDialog(self, logo, localisation, postal, phone1, phone2, minister):
        dialog = QDialog(self)

        self.label_image_preview = QLabel()
        self.new_header_image_file_name = logo
        self.label_image_preview.setPixmap(QPixmap(logo))

        btn_select_header_image = QPushButton(u"Cliquer ici pour sélectioner un nouveau logo")


        line_company_name = QLineEdit(auth.Auth.getAccountCompanyName())
        line_localisation = QLineEdit(localisation)
        #line_localisation.setMaxLength(30)
        line_postal = QLineEdit(postal)
        line_phone_1 = QLineEdit(phone1)
        line_phone_1.setInputMask("99-99-99-99")
        line_phone_2 = QLineEdit(phone2)
        line_phone_2.setInputMask("99-99-99-99")
 
        radio_minister_national = QRadioButton(u"Ministère de l'éducation nationale", dialog)


        radio_minister_technic = QRadioButton(u"Ministère de l'enseignement technique", dialog)

        radio_minister_national_technic = QRadioButton(u"Ministère de l'éducation nationale\n"
                                                 u"et de l'enseignement technique", dialog)

        radio_minister_superior = QRadioButton(u"Ministère de l'enseignement supérieur\n"
                                      u"et de la recherche scientifique", dialog)

        if minister == u"Ministère de l'éducation nationale":
            radio_minister_national.setChecked(True)
        elif minister == u"Ministère de l'enseignement technique":
            radio_minister_technic.setChecked(True)
        elif minister == u"Ministère de l'éducation nationale et de l'enseignement technique":
            radio_minister_national_technic.setChecked(True)
        elif minister == u"Ministère de l'enseignement supérieur et de la recherche scientifique":
            radio_minister_superior.setChecked(True)
        

        layout_form = QFormLayout()
        layout_form.addRow(u"", self.label_image_preview)
        layout_form.addRow(u"", btn_select_header_image)

        layout_form.addRow(u"Nom de l'établissement: ", line_company_name)
        layout_form.addRow(u"Localisation: ", line_localisation)
        layout_form.addRow(u"Adresse Postale: ", line_postal)
        layout_form.addRow(u"Téléphone 1: ", line_phone_1)
        layout_form.addRow(u"Téléphone 2: ", line_phone_2)

        layout_form_minister = QFormLayout()

        layout_form_minister.addRow(u"Ministère: ", radio_minister_national)
        layout_form_minister.addRow(u"", radio_minister_technic)
        layout_form_minister.addRow(u"", radio_minister_national_technic)
        layout_form_minister.addRow(u"", radio_minister_superior)

        group_minister = QGroupBox(u"À quel ministère votre établissement est-il affilié?")
        group_minister.setLayout(layout_form_minister)


        self.btn_header_ok = QPushButton("Ok")
        self.btn_header_ok.setIcon(QIcon(":/images/button_apply.png"))
        btn_header_cancel = QPushButton("Annuler")
        btn_header_cancel.setIcon(QIcon(":/images/button_cancel.png"))

        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_header_ok)
        layout_btn.addWidget(btn_header_cancel)
        layout_btn.setAlignment(Qt.AlignRight)
       

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_form)
        layout_main.addWidget(group_minister)
        layout_main.addLayout(layout_btn)

        dialog.setLayout(layout_main)
        dialog.resize(700, 200)
        dialog.setWindowTitle(u"Entête de document - InterNotes")


        self.connect(btn_select_header_image, SIGNAL("clicked()"),
                self.selectHeaderImage)

        self.connect(self.btn_header_ok, SIGNAL("clicked()"), dialog.accept)
        self.connect(btn_header_cancel, SIGNAL("clicked()"), dialog.reject)



        return (dialog.exec_(), 
                               line_localisation.text(),
                               line_postal.text(),
                               line_phone_1.text(),
                               line_phone_2.text(),
                               radio_minister_national.isChecked(),
                               radio_minister_technic.isChecked(),
                               radio_minister_national_technic.isChecked(),
                               radio_minister_superior.isChecked(),
                               line_company_name.text()
                               )





    def updateHeader(self, logo, company_name, localisation, postal, phone1, phone2, minister):
        query = QSqlQuery()
        query.prepare("UPDATE account \
                       SET    account_company_name = :company, \
                              account_school_localization = :localization, \
                              account_postal_address = :postal, \
                              account_phone1 = :phone1, \
                              account_phone2 = :phone2, \
                              account_print_header_image_name = :logo, \
                              account_print_header_minister = :minister, \
                              account_updated_at = NOW() \
                       ")

        query.bindValue(":company", company_name)
        query.bindValue(":localization", localisation)
        query.bindValue(":postal", postal)
        query.bindValue(":phone1", phone1)
        query.bindValue(":phone2", phone2)
        query.bindValue(":logo", logo)
        query.bindValue(":minister", minister)
        if not query.exec_():
            QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query.lastError().text())
        #else:
        #    self.btn_header.setText(QString(u"Modifier l'entête"))


    
    def getHeaderInfos(self):
        data = {}
        query = QSqlQuery("SELECT account_school_localization, \
                                  account_postal_address, \
                                  account_phone1, \
                                  account_phone2, \
                                  account_print_header_image_name AS header_image, \
                                  account_print_header_minister AS header_minister \
                           FROM account \
                         ")
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while query.next():
                    data['account_school_localization'] = query.value(
                                record.indexOf("account_school_localization")).toString()
                    data['account_postal_address'] = query.value(
                                record.indexOf("account_postal_address")).toString()
                    data['account_phone1'] = query.value(
                                record.indexOf("account_phone1")).toString()
                    data['account_phone2'] = query.value(
                                record.indexOf("account_phone2")).toString()
                    data['header_image'] = query.value(
                                record.indexOf("header_image")).toString()
                    data['header_minister'] = query.value(
                                record.indexOf("header_minister")).toString()
        
        else:
            QMessageBox.critical(self, "Error - InterNotes",
                            u"Database Error: %s" % query.lastError().text())

        return data




    def setHeader(self):
        header_image = u""
        if Export.isAccountHasLogo() == False: 
            reply = self.showHeaderSetupDialog()
        else:
            data = self.getHeaderInfos()
            header_image = data["header_image"]
            reply = self.showEditHeaderSetupDialog(
                               header_image,
                               data["account_school_localization"],
                               data["account_postal_address"],
                               data["account_phone1"],
                               data["account_phone2"],
                               data["header_minister"]
                               )

        if reply[0] == 0:
            if not header_image and self.new_header_image_file_name:
                tmp_file = QFile(self.new_header_image_file_name)
                if not tmp_file.remove():
                    QMessageBox.critical(self, u"Error - InterNotes",
                            u"Erreur de suppression de l'image temporaire\n" + \
                                    self.new_header_image_file_name)
                self.new_header_image_file_name = ''

        else:
            if header_image and header_image != self.new_header_image_file_name:
                old_logo = header_image
                old_logo_file = QFile(old_logo)
                if not old_logo_file.remove():
                    QMessageBox.warning(self, u"Error - InterNotes",
                            u"Erreur de suppression de l'ancien logo\n" + \
                                    old_logo)

            logo = self.new_header_image_file_name
            localisation = reply[1]
            postal = reply[2]
            phone1 = reply[3]
            phone2 = reply[4]
            company_name = reply[9]

            minister = u''
            if reply[5] == True:
                minister = u"Ministère de l'éducation nationale"
            elif reply[6] == True:
                minister = u"Ministère de l'enseignement technique"
            elif reply[7] == True:
                minister = u"Ministère de l'éducation nationale et de l'enseignement technique"
            elif reply[8] == True:
                minister = u"Ministère de l'enseignement supérieur et de la recherche scientifique"

            self.updateHeader(logo, company_name, localisation, postal, phone1, phone2, minister)




    def activeExportBtn(self):
        if self.combo_period.currentIndex() != -1:
            self.btn_export.setEnabled(True)
        else:
            self.btn_export.setEnabled(False)
    
    def hideYcrGroup(self, bol):
        self.group_ycr.setVisible(False)
        self.setPeriodComboBox()
        self.activeExportBtn()


    def showYcrGroup(self, bol):
        #if bol == True:
        self.group_ycr.setVisible(True)
        self.setPeriodComboBox()
        self.activeExportBtn()




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



    def getAcademicYearPeriodByStudentId(self, stid):
        period = [] 
        query = QSqlQuery("SELECT DISTINCT mark_group \
                           FROM mark \
                           WHERE student_id = " + str(stid) + 
                           " ORDER BY mark_group")
        if query.exec_():
            record = query.record()
            if not record.isEmpty():
                while(query.next()):
                    period.append(
                        query.value(record.indexOf("mark_group")).toString()
                        )

        return period


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

    def getSelectedStudentId(self):
            current_proxy_index = self.student_tree.currentIndex()
            model_index = self.student_tree.proxy_model.mapToSource(current_proxy_index)
            student_item = self.student_tree.model.itemFromIndex(model_index)
            stid = student_item.accessibleText().toInt()[0]
            return stid

    def setPeriodComboBox(self):
        self.combo_period.clear()
        if self.btn_radio_selected_student.isChecked():
            student_id = self.getSelectedStudentId()
            period = self.getAcademicYearPeriodByStudentId(student_id)
            for p in range(0, len(period)): 
                self.combo_period.addItem(period[p])

        else:
            if self.combo_classroom.currentIndex() != -1:
                ay_current_index = self.combo_ay.currentIndex()
                ayid = self.combo_ay.itemData(ay_current_index).toInt()[0]
                period = academicyear.AcademicYear.getPeriodById(ayid)
                if period == 'quarter':
                    self.combo_period.addItem(u'1er Trimestre')
                    self.combo_period.addItem(u'2ème Trimestre')
                    self.combo_period.addItem(u'3ème Trimestre')
                elif period == 'semester':
                    self.combo_period.addItem(u'1er Semestre')
                    self.combo_period.addItem(u'2ème Semestre')

    
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


    def footer(self):
        self.painter.save()
        #x = 700
        x = 72
        pageRect = self.printer.pageRect()
        y = pageRect.height() - 10
            
        self.painter.setPen(Qt.gray)
        self.painter.drawLine(x, y, pageRect.width() - 72, y)
        y += 2
        font = QFont("Helvetica", 5)
        font.setItalic(True)
        self.painter.setFont(font)
        option = QTextOption(Qt.AlignCenter)
        option.setWrapMode(QTextOption.WordWrap)
        self.painter.setPen(Qt.black)
        output_date = QDateTime.currentDateTime().toLocalTime().toString(
                            u"dddd dd MMMM yyyy \'à\' hh\'h\':mm\'m\':ss\'s\'")
        self.painter.drawText(
            QRectF(x, y,
            pageRect.width() - 0.5 * 700, 150), 
             QString(u"Fait le %1 par InterNotes Version 1.0.2 © 2014 - 2015, Matlle e.i. www.matlle.com")
                              .arg(output_date)
                              , option)
        self.painter.restore()



    def exportPDF(self):
        self.printer = QPrinter(QPrinter.HighResolution)
        self.printer.setPaperSize(QPrinter.A4)
        self.printer.setOrientation(QPrinter.Portrait)

        self.printer.setOutputFormat(QPrinter.PdfFormat)
        
        """
        doc_name = QFileDialog.getSaveFileName(self, u"Exporter pdf", 
                QDir.homePath() + u"/bulletin.pdf", 
                                                          "PDF (*.pdf)")
        if doc_name.isEmpty() or doc_name is None:
            return
        self.printer.setOutputFileName(doc_name)
        """

        #self.printer.setOutputFileName("bulletin.pdf")

        #dialog = QPrintDialog(self.printer, self)
        #dialog.setOption(QAbstractPrintDialog.PrintToFile)
        #dialog.setWindowTitle(u"Exporter PDF - InterNotes")

        #if dialog.exec_():

        advice_pdf_name = u'/bulletin-' # advice... how say 'proposer' in English?

        if 1:
            topics = []
            group_period = ''
            current_std_id = 0
            current_std_cr_name = u''
            stds_id = []
            infos_std = {}
            group_period = self.combo_period.currentText()

            advice_pdf_name += group_period + u"-"

            if self.btn_radio_selected_student.isChecked():
                std_id = self.getSelectedStudentId()
                stds_id.append(std_id)

                student_name = student.Student.getNameById(std_id)

                advice_pdf_name += student_name
                
            else:
                cr_index = self.combo_classroom.currentIndex()
                current_std_crid = self.combo_classroom.itemData(cr_index).toInt()[0]
                cr_list_stds_id = student.Student.getAllStudentsIdByClassroomId(
                        current_std_crid)

                advice_pdf_name += self.combo_classroom.currentText()


                for i in range(0, len(cr_list_stds_id)):
                    stdid = cr_list_stds_id[i]
                    if student.Student.isStudentHasAnyMarksInThisMarkGroup(stdid, group_period):
                        stds_id.append(stdid)

            advice_pdf_name += u".pdf"

            doc_name = QFileDialog.getSaveFileName(self, u"Exporter pdf", 
                QDir.homePath() + advice_pdf_name, 
                                                          "PDF (*.pdf)")
            if doc_name.isEmpty() or doc_name is None:
                return
            self.printer.setOutputFileName(doc_name)





            s = 0

            self.printer.newPage()
            self.painter = QPainter(self.printer)

            while s < len(stds_id):
                current_std_id = stds_id[s]
                """
                current_std_periods = self.getAcademicYearPeriodByStudentId(current_std_id)
                if not group_period in current_std_periods:
                    s += 1
                    continue
                """

                current_std_crid = student.Student.getClassroomIdById(current_std_id)
                current_std_cr_name = classe.Class.getClassroomNameById(current_std_crid)
                topics = classe.Class.getAllTopicsByClassroomId(current_std_crid)
                infos_std = self.student_tree.getStudentInfosById(current_std_id)

                pageRect = self.printer.pageRect()

                self.footer()

                self.painter.save()


                #self.painter.drawText(0, 0, "Text on initial minimum border")

           
                sans_font = QFont("Helvetica", 6)
                sans_line_height = QFontMetrics(sans_font).height()

                serif_font = QFont("Times", 11)
                serif_font.setBold(False)
                fm = QFontMetrics(serif_font)
                fm_height = int(fm.height() * 8.5)

                left_margin = 75
                x = left_margin
                include_header = False
                if self.btn_check_header.isChecked():
                    initial_y   = 0
                    include_header = True
                else:
                    initial_y   = 1500

                y = initial_y




                option = QTextOption(Qt.AlignCenter)
                width_title_topic = fm.width(u" MATIÈRE ") * 29.5
                width_title_avg = fm.width(u" MOY. ") * 11.5
                width_title_coef = fm.width(u"COEF") * 11.5
                width_title_avgcoef = fm.width(u"MOY.XCOEF.") * 11.5
                width_title_rank = fm.width(u" RANG ") * 16.5
                width_title_prof = fm.width(u" PROFESSEUR ") * 13
                width_title_remark = fm.width(u" APPRECIATION ") * 11.5
                width_title_sign = fm.width(u" EMARGEMENT ") * 11.5


                whole_width = width_title_topic + width_title_avg + width_title_coef + \
                              width_title_avgcoef + width_title_rank + width_title_prof + \
                              width_title_remark + width_title_sign

                if include_header == True:
                    #header_infos = auth.Auth.getAccountHeaderInfos()
                    header_infos = self.getHeaderInfos()

                    # header_logo
                    w_logo = whole_width

                    account_logo = header_infos["header_image"] #auth.Auth.getAccountLogo()

                    if not account_logo.isEmpty() \
                            and not account_logo == '' \
                            and not account_logo == None:
                        rect_logo = QRect(x, y, w_logo, fm_height + 650)

                        self.painter.setPen(Qt.NoPen)

                        self.painter.drawRect(rect_logo)

                        self.painter.setPen(Qt.black)

                        pic = QPixmap(account_logo)

                        pic_scaled = pic.scaledToHeight(fm_height + 650)
                        self.painter.drawPixmap(x, y, pic_scaled)

                        y += rect_logo.height() 




                    # header_company_name
                    w_header_company_name = whole_width


                    rect_header_company_name = QRect(x, y + 25, w_header_company_name, fm_height + 5) 
                    self.painter.drawRect(rect_header_company_name)

                    self.painter.drawText(
                        QRectF(x, y + 30, w_header_company_name, fm_height), 
                            QString("%1")
                              .arg(auth.Auth.getAccountCompanyName()).toUpper()
                              , option)

                    y += rect_header_company_name.height() 


                    # header postal address - phone number - minister 
                    w_header_postal_phone = width_title_topic + width_title_avg + width_title_coef + \
                                        width_title_avgcoef

                    rect_header_postal_phone = QRect(x, y, w_header_postal_phone, fm_height + 200)

                    self.painter.setPen(Qt.NoPen)

                    self.painter.drawRect(rect_header_postal_phone)

                    self.painter.setPen(Qt.black)

                    font = QFont("Helvetica", 6, -1, False)
                    self.painter.setFont(font)
                
               
                    option = QTextOption(Qt.AlignLeft)
                    self.painter.drawText(
                         QRectF(x, y + 35, w_header_postal_phone, fm_height + 200), 
                         QString("Localisation:"+ " " +"%1\nAdresse Postale:" + "  " +"%2\nTéléphone: %3")
                              .arg(header_infos["account_school_localization"]).toUpper()
                              .arg(header_infos["account_postal_address"]).toUpper()
                              .arg(header_infos["account_phone1"] + " / " + \
                                      header_infos["account_phone2"])
                              , option)


                    header_x = x

                    header_x += rect_header_postal_phone.width()

                    w_header_minister = width_title_rank + width_title_prof + width_title_remark + \
                                        width_title_sign

                    rect_header_minister = QRect(header_x, y, w_header_minister, fm_height + 200)

                    self.painter.setPen(Qt.NoPen)

                    self.painter.drawRect(rect_header_minister)

                    self.painter.setPen(Qt.black)

                    option = QTextOption(Qt.AlignCenter)
                    self.painter.drawText(
                         QRectF(header_x, y + 35, w_header_minister, fm_height + 80), 
                         QString("RÉPUBLIQUE DE CÔTE D'IVOIRE\n%1")
                              .arg(header_infos["header_minister"]).toUpper()
                              , option)






                    y += rect_header_postal_phone.height() + 100 




                    font = QFont("Helvetica", 8, -1, False)
                    self.painter.setFont(QFont())


                    option = QTextOption(Qt.AlignCenter)

                    # end header



                self.painter.setPen(Qt.NoPen)

                p_x = x
                w_mg = width_title_topic + width_title_avg + width_title_coef

                rect_mg = QRect(p_x, y, w_mg, fm_height + 100)
                self.painter.drawRect(rect_mg)

                self.painter.setPen(Qt.black)

                self.painter.drawText(
                         QRectF(p_x + 3, y + 50, w_mg - 6, fm_height - 6), 
                            QString("BULLETIN DE NOTES: %1")
                              .arg(group_period).toUpper()
                              , option)

                p_x += rect_mg.width()
                w_cr = width_title_avgcoef + width_title_rank + width_title_prof

                self.painter.setPen(Qt.NoPen)

                rect_classroom = QRect(p_x, y, w_cr, fm_height + 100)
                self.painter.drawRect(rect_classroom)

                self.painter.setPen(Qt.black)

                self.painter.drawText(
                       QRectF(p_x + 3, y + 50, w_cr - 6, fm_height - 6), 
                          QString("CLASSE: %1")
                              .arg(current_std_cr_name).toUpper()
                          , option)

                self.painter.setPen(Qt.black)

                p_x += rect_classroom.width() + width_title_remark
            
                w_photo = width_title_sign

                rect_photo = QRect(p_x, y, w_photo, fm_height + 1300)
                #self.painter.drawRect(rect_photo)

                std_photo_name = infos_std['student_photo_name']

                if std_photo_name.isEmpty() or \
                        std_photo_name == '' or \
                        std_photo_name == None or \
                        QPixmap(std_photo_name).isNull():

                    self.painter.drawRect(rect_photo)
                    if Export.isAccountHasLogo() == True: 
                        self.painter.drawText(
                          QRectF(p_x + 3, (fm_height + 3200) / 1.6, w_photo - 6, fm_height - 6), 
                            u"PHOTO", option)
                    else:
                        self.painter.drawText(
                          QRectF(p_x + 3, (fm_height + 3200) / 2.6, w_photo - 6, fm_height - 6), 
                            u"PHOTO", option)
                else:
                    self.painter.setPen(Qt.NoPen)
                    self.painter.drawRect(rect_photo)
                    self.painter.setPen(Qt.black)

                    photo = QPixmap(std_photo_name)
                    photo = photo.scaled(w_photo - 1, fm_height + 1300)
                    self.painter.drawPixmap(p_x, y, photo)


                y += rect_classroom.height()

                w_infos = width_title_topic + width_title_avg + width_title_coef + width_title_avgcoef
                w_infos += width_title_rank + width_title_prof


                rect_infos = QRect(x, y, w_infos, fm_height + 1030)
                self.painter.drawRect(rect_infos)

                font = QFont("Helvetica", 7, -1, False)
                self.painter.setFont(font)

                option = QTextOption(Qt.AlignLeft)


                p_r_y = y
                p_r_x = x
                w_p_r = width_title_coef + width_title_avgcoef
            
                rect_pro_matricule = QRect(p_r_x + 20, p_r_y + 20, w_p_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_p_r - 6, fm_height - 6), 
                        u"MATRICULE:", option)

                p_r_x += rect_pro_matricule.width()


                w_d_r = width_title_topic

                rect_pro_matricule_one = QRect(p_r_x + 20, p_r_y + 20, w_d_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                       QRectF(p_r_x + 50, p_r_y + 20, w_d_r - 6, fm_height - 6), 
                          QString("%1")
                        .   arg(infos_std['student_matricule'])
                    , option)

                p_r_x += rect_pro_matricule_one.width()

                w_dd_r = width_title_remark

                rect_pro_ay = QRect(p_r_x + 20, p_r_y + 20, w_dd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                       QRectF(p_r_x + 50, p_r_y + 20, w_dd_r - 6, fm_height - 6), 
                         u"ANNÉE ACADEMIQUE:", option)


                p_r_x += rect_pro_ay.width()

                w_ddd_r = width_title_prof - 23

                ay_name = student.Student.getAcademicYearNameById(current_std_id)

                rect_pro_ay_one = QRect(p_r_x + 20, p_r_y + 20, w_ddd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                      QRectF(p_r_x + 50, p_r_y + 20, w_ddd_r - 6, fm_height - 6), 
                         QString("%1")
                          .arg(ay_name)
                    , option)



                p_r_x = x
                p_r_y += rect_pro_ay_one.height() + 70


                rect_pro_matricule = QRect(p_r_x + 20, p_r_y + 20, w_p_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                      QRectF(p_r_x + 50, p_r_y + 20, w_p_r - 6, fm_height - 6), 
                      u"MATRICULE MINISTERIEL:", option)

                p_r_x += rect_pro_matricule.width()


                w_d_r = width_title_topic

                rect_pro_matricule_one = QRect(p_r_x + 20, p_r_y + 20, w_d_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                    QRectF(p_r_x + 50, p_r_y + 20, w_d_r - 6, fm_height - 6), 
                    QString("%1")
                        .arg(infos_std["student_matricule_ministeriel"])
                    , option)

                p_r_x += rect_pro_matricule_one.width()

                w_dd_r = width_title_remark

                rect_pro_ay = QRect(p_r_x + 20, p_r_y + 20, w_dd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                       QRectF(p_r_x + 50, p_r_y + 20, w_dd_r - 6, fm_height - 6), 
                        u"STATUT:", option)


                p_r_x += rect_pro_ay.width()

                w_ddd_r = width_title_prof - 23

                rect_pro_ay_one = QRect(p_r_x + 20, p_r_y + 20, w_ddd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                       QRectF(p_r_x + 50, p_r_y + 20, w_ddd_r - 6, fm_height - 6), 
                         QString("%1")
                        .   arg(infos_std["student_statut"].toUpper())
                       , option)


                p_r_x = x
                p_r_y += rect_pro_ay_one.height() + 70


                rect_pro_matricule = QRect(p_r_x + 20, p_r_y + 20, w_p_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_p_r - 6, fm_height - 6), 
                           u"NOM ET PRENOMS:", option)

                p_r_x += rect_pro_matricule.width()


                w_d_r = width_title_topic

                rect_pro_matricule_one = QRect(p_r_x + 20, p_r_y + 20, w_d_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_d_r - 6, fm_height - 6), 
                          QString("%1")
                           .arg(infos_std["student_last_name"] + " " + infos_std["student_first_name"])
                           .toUpper()
                        , option)

                p_r_x += rect_pro_matricule_one.width()

                w_dd_r = width_title_remark

                rect_pro_ay = QRect(p_r_x + 20, p_r_y + 20, w_dd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_dd_r - 6, fm_height - 6), 
                          u"EFFECTIF DE CLASSE:", option)


                p_r_x += rect_pro_ay.width()

                w_ddd_r = width_title_prof - 23

                std_nb = classe.Class.getNumberOfStudentInThisClassroomById(
                    current_std_crid)
            
                rect_pro_ay_one = QRect(p_r_x + 20, p_r_y + 20, w_ddd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_ddd_r - 6, fm_height - 6), 
                           QString("%1")
                        .arg(std_nb)
                    , option)



                p_r_x = x
                p_r_y += rect_pro_ay_one.height() + 70


                rect_pro_matricule = QRect(p_r_x + 20, p_r_y + 20, w_p_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_p_r - 6, fm_height - 6), 
                          u"DATE DE NAISSANCE:", option)

                p_r_x += rect_pro_matricule.width()


                w_d_r = width_title_topic

                rect_pro_matricule_one = QRect(p_r_x + 20, p_r_y + 20, w_d_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                       QRectF(p_r_x + 50, p_r_y + 20, w_d_r - 6, fm_height - 6), 
                           QString("%1     GENRE:   %2")
                              .arg(infos_std['student_birth_date'])
                              .arg(infos_std['student_genre'])
                       , option)

                p_r_x += rect_pro_matricule_one.width()

                w_dd_r = width_title_remark

                rect_pro_ay = QRect(p_r_x + 20, p_r_y + 20, w_dd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_dd_r - 6, fm_height - 6), 
                            u"REDOUBLANT(E):", option)


                p_r_x += rect_pro_ay.width()

                w_ddd_r = width_title_prof - 23

                rect_pro_ay_one = QRect(p_r_x + 20, p_r_y + 20, w_ddd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_ddd_r - 6, fm_height - 6), 
                            QString("%1")
                                .arg(infos_std['student_redoubler'])
                        , option)


                p_r_x = x
                p_r_y += rect_pro_ay_one.height() + 70


                rect_pro_matricule = QRect(p_r_x + 20, p_r_y + 20, w_p_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_p_r - 6, fm_height - 6), 
                            u"ÉCOLE PRÉCEDENTE:", option)

                p_r_x += rect_pro_matricule.width()


                w_d_r = width_title_topic

                rect_pro_matricule_one = QRect(p_r_x + 20, p_r_y + 20, w_d_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_matricule_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_d_r - 6, fm_height - 6), 
                            QString("%1")
                                .arg(infos_std['student_previous_school'])
                                .toUpper()
                        , option)

                p_r_x += rect_pro_matricule_one.width()

                w_dd_r = width_title_remark + 200

                rect_pro_ay = QRect(p_r_x + 20, p_r_y + 20, w_dd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_dd_r - 6, fm_height - 6), 
                           u"CLASSE PRÉCEDENTE:", option)


                p_r_x += rect_pro_ay.width()

                w_ddd_r = width_title_prof - 23

                rect_pro_ay_one = QRect(p_r_x + 20, p_r_y + 20, w_ddd_r, fm_height)
                self.painter.setPen(Qt.NoPen)
                self.painter.drawRect(rect_pro_ay_one)
                self.painter.setPen(Qt.black)
                self.painter.drawText(
                        QRectF(p_r_x + 50, p_r_y + 20, w_ddd_r - 6, fm_height - 6), 
                            QString("%1")
                            .arg(infos_std["student_previous_classroom"].toUpper())
                        , option)





            #==============> TABLE HEAD <==================

                option = QTextOption(Qt.AlignCenter)
                font = QFont()
                self.painter.setFont(font)
                self.painter.setPen(Qt.black)

                y += rect_infos.height() + 100

                rect_topic = QRect(x, y, width_title_topic, fm_height)
                self.painter.fillRect(rect_topic, QColor("#cccccc"))
                self.painter.drawRect(rect_topic)
                self.painter.drawText(
                    QRectF(x + 3, y + 3, width_title_topic - 6, fm_height - 6), 
                    u"MARTIÈRE", option)

                x += width_title_topic


                rect_avg = QRect(x, y, width_title_avg, fm_height)
                self.painter.fillRect(rect_avg, QColor("#cccccc"))
                self.painter.drawRect(rect_avg)
                self.painter.drawText(
                        QRectF(x + 3, y + 3, width_title_avg - 6, fm_height - 6), 
                        u"MOY.", option)

                x += width_title_avg


                rect_coef = QRect(x, y, width_title_coef, fm_height)
                self.painter.fillRect(rect_coef, QColor("#cccccc"))
                self.painter.drawRect(rect_coef)
                self.painter.drawText(
                    QRectF(x + 3, y + 3, width_title_coef - 6, fm_height - 6), 
                    u"COEF.", option)

                x += width_title_coef



                rect_avgcoef = QRect(x, y, width_title_avgcoef, fm_height) 
                self.painter.fillRect(rect_avgcoef, QColor("#cccccc"))
                self.painter.drawRect(rect_avgcoef)
                self.painter.drawText(
                    QRectF(x + 3, y + 3, width_title_avgcoef - 6, fm_height - 6), 
                    u"MOY. X COEF.", option)

                x += width_title_avgcoef


                rect_rank = QRect(x, y, width_title_rank, fm_height)
                self.painter.fillRect(rect_rank, QColor("#cccccc"))
                self.painter.drawRect(rect_rank)
                self.painter.drawText(
                        QRectF(x + 3, y + 3, width_title_rank - 6, fm_height - 6), 
                        u"RANG", option)

                x += width_title_rank



                rect_prof = QRect(x, y, width_title_prof, fm_height)
                self.painter.fillRect(rect_prof, QColor("#cccccc"))
                self.painter.drawRect(rect_prof)
                self.painter.drawText(
                        QRectF(x + 3, y + 3, width_title_prof - 6, fm_height - 6), 
                           u"PROFESSEUR", option)

                x += width_title_prof
            



                rect_remark = QRect(x, y, width_title_remark, fm_height)
                self.painter.fillRect(rect_remark, QColor("#cccccc"))
                rect_remark = self.painter.drawRect(rect_remark)
                self.painter.drawText(
                    QRectF(x + 3, y + 3, width_title_remark - 6, fm_height - 6), 
                    u"APPRECIATION", option)

                x += width_title_remark



                rect_sign = QRect(x, y, width_title_sign, fm_height)
                self.painter.fillRect(rect_sign, QColor("#cccccc"))
                self.painter.drawRect(rect_sign)
                self.painter.drawText(
                        QRectF(x + 3, y + 3, width_title_sign - 6, fm_height - 6), 
                         u"EMARGEMENT", option)




            #===============> BEGIN TABLE CONTENT <====================

                option = QTextOption(Qt.AlignLeft)
                #option.setWrapMode(QTextOption.WordWrap)


                x = left_margin
                y += rect_topic.height()
                previous_y = 0
                bs_level_my = 0
                level_mycoef = 0
                bs_coef = 0
                bs_mycoef = 0.0
                bs_mycoef_level = 0

                total_coef = 0
                total_mycoef = 0.0
                total_mycoef_level = 0


                fm_height = int(fm.height() * 11)


                for t in range(0, len(topics)):
                
                    tid = topics[t][0]
                    topic_type = topics[t][3]
                    prof = topic.Topic.getProfById(tid)

                    font = QFont("Helvetica", 8, -1, True)
                    self.painter.setFont(font)

                    rect_one_topic = QRect(x, y, width_title_topic, fm_height)
                    self.painter.drawRect(rect_one_topic)
                    self.painter.drawText(
                        QRectF(x + 3, y + 25, width_title_topic - 6, fm_height - 20), 
                        topics[t][1].toUpper(), option)

                    x += width_title_topic

                    font = QFont("Helvetica", 7, -1, False)
                    self.painter.setFont(font)

                    my = student.Student.getStudentAverageByTopicAndMarkGroup(
                          tid, current_std_id, group_period)
                
                    rect_one_avg = QRect(x, y, width_title_avg, fm_height)
                    self.painter.drawRect(rect_one_avg)

                    marks = topic.Topic.isStudentHasAnyMarksInThisTopicAndMarkGroup(
                            tid, current_std_id, group_period)

                    coef = ''
                    if marks:
                        coef = topics[t][2]
                        bs_coef += coef
                        bs_level_my = 20
                        self.painter.drawText(
                            QRectF(x + 3, y + 25, width_title_avg - 6, fm_height - 6), 
                            QString("%L1/20").arg(my, 0, "f", 2), option)
                    else:
                        self.painter.drawText(
                            QRectF(x + 3, y + 25, width_title_avg - 6, fm_height - 6), 
                             u"", option)

                    x += width_title_avg


                    rect_one_coef = QRect(x, y, width_title_coef, fm_height)
                    self.painter.drawRect(rect_one_coef)
                    if coef:
                        self.painter.drawText(
                            QRectF(x + 30, y + 25, width_title_coef - 6, fm_height - 6), 
                               QString("%1").arg(coef), option)
                    else:
                        self.painter.drawText(
                              QRectF(x + 30, y + 25, width_title_coef - 6, fm_height - 6), 
                                 QString("%1").arg(""), option)

                    x += width_title_coef


                    rect_one_avgcoef = QRect(x, y, width_title_avgcoef, fm_height)
                    self.painter.drawRect(rect_one_avgcoef)
                    if marks:
                        if coef:
                            mycoef = my * coef
                            level_mycoef = coef * 20
                        else:
                            mycoef = my
                            level_mycoef = 20

                        bs_mycoef += mycoef
                        bs_mycoef_level += level_mycoef

                        self.painter.drawText(
                            QRectF(x + 3, y + 25, width_title_avgcoef - 6, fm_height - 6), 
                              QString("%L1/%2")
                                 .arg(mycoef, 0, "f", 2)
                                 .arg(level_mycoef)
                              , option)


                    else:
                        self.painter.drawText(
                            QRectF(x + 3, y + 25, width_title_avgcoef - 6, fm_height - 6), 
                            u"", option)


                    x += width_title_avgcoef

                    rank = student.Student.getStudentAverageRankByTopicAndMarkGroup(
                            current_std_crid, tid, my, group_period)
                
                    std_genre = infos_std['student_genre']
                    rank = infos.Infos.rankMe(rank, std_genre)

                    rect_one_rank = QRect(x, y, width_title_rank, fm_height)
                    self.painter.drawRect(rect_one_rank)
                    self.painter.drawText(
                        QRectF(x + 3, y + 25, width_title_rank - 6, fm_height - 6), 
                        rank, option)

                    x += width_title_rank


                    font = QFont("Helvetica", 5, -1, True)
                    self.painter.setFont(font)

                    rect_one_prof = QRect(x, y, width_title_prof, fm_height)
                    self.painter.drawRect(rect_one_prof)
                    self.painter.drawText(
                        QRectF(x + 3, y + 3, width_title_prof - 6, fm_height - 20), 
                        prof.toUpper(), option)

                    font = QFont("Helvetica", 7, -1, False)
                    self.painter.setFont(font)

                    x += width_title_prof


                    rect_one_remark = QRect(x, y, width_title_remark, fm_height)
                    self.painter.drawRect(rect_one_remark)
                    self.painter.drawText(
                           QRectF(x + 3, y + 25, width_title_remark - 6, fm_height - 6), 
                        u"", option)

                    x += width_title_remark


                    rect_one_sign = QRect(x, y, width_title_sign, fm_height)
                    self.painter.drawRect(rect_one_sign)
                    self.painter.drawText(
                        QRectF(x + 3, y + 25, width_title_sign - 6, fm_height - 6), 
                        u"", option)



                    try:
                        if topic_type != topics[t+1][3]:
                            total_coef += bs_coef
                            total_mycoef += bs_mycoef
                            total_mycoef_level += bs_mycoef_level

                            x = left_margin
                            y += rect_one_topic.height()

                            font = QFont("Helvetica", 8, -1, True)
                            self.painter.setFont(font)

                            rect_bs_topics_type = QRect(x, y, width_title_topic, fm_height)
                            self.painter.fillRect(rect_bs_topics_type, QColor("#dfdfdf"))
                            self.painter.drawRect(rect_bs_topics_type)
                            self.painter.drawText(
                                QRectF(x + 3, y + 25, width_title_topic - 6, fm_height - 6), 
                                u"BILAN " + topic_type.toUpper(), option)

                            x += width_title_topic

                            font = QFont("Helvetica", 7, -1, False)
                            self.painter.setFont(font)

                            bs_my = student.Student.getStudentAverageByTopicTypeAndMarkGroup(
                                        current_std_id, group_period, topic_type)

                            bs_rank = student.Student.getStudentAverageRankByTopicTypeAndMarkGroup(
                                    current_std_crid, topic_type, group_period, bs_my)

                            bs_rank = infos.Infos.rankMe(bs_rank, std_genre)

                            rect_bs_my = QRect(x, y, width_title_avg, fm_height)
                            self.painter.fillRect(rect_bs_my, QColor("#dfdfdf"))
                            self.painter.drawRect(rect_bs_my)
                            self.painter.drawText(
                                     QRectF(x + 3, y + 25, width_title_topic - 6, fm_height - 6), 
                                     QString("%L1/%2")
                                             .arg(bs_my, 0, "f", 2)
                                             .arg(bs_level_my)
                                        , option)


                            x += width_title_avg

                            rect_bs_coef = QRect(x, y, width_title_coef, fm_height)
                            self.painter.fillRect(rect_bs_coef, QColor("#dfdfdf"))
                            self.painter.drawRect(rect_bs_coef)
                            self.painter.drawText(
                                       QRectF(x + 30, y + 25, width_title_coef - 6, fm_height - 6), 
                                       QString("%1").arg(bs_coef)
                                            , option)

                            x += width_title_coef

                            rect_bs_mycoef = QRect(x, y, width_title_avgcoef, fm_height)
                            self.painter.fillRect(rect_bs_mycoef, QColor("#dfdfdf"))
                            self.painter.drawRect(rect_bs_mycoef)
                            self.painter.drawText(
                                       QRectF(x + 3, y + 25, width_title_avgcoef - 6, fm_height - 6), 
                                       QString("%L1/%2")
                                            .arg(bs_mycoef, 0, "f", 2)
                                            .arg(bs_mycoef_level)
                                       , option)


                            x += width_title_avgcoef

                            rect_bs_rank = QRect(x, y, width_title_rank, fm_height)
                            self.painter.fillRect(rect_bs_rank, QColor("#dfdfdf"))
                            self.painter.drawRect(rect_bs_rank)
                            self.painter.drawText(
                                   QRectF(x + 3, y + 25, width_title_rank - 6, fm_height - 6), 
                                       QString("%1").arg(bs_rank)
                                       , option)

                            x += width_title_rank

                            rect_bs_prof = QRect(x, y, 
                                width_title_prof + width_title_remark + width_title_sign,
                                fm_height)
                            self.painter.fillRect(rect_bs_prof, QColor("#dfdfdf"))
                            self.painter.drawRect(rect_bs_prof)
                            self.painter.drawText(
                                QRectF(x + 3, y + 25, 
                       (width_title_prof + width_title_remark + width_title_sign) - 6, fm_height - 6), 
                                     u"", option)



                            bs_level_my = 0
                            bs_coef = 0
                            bs_mycoef = 0.0
                            bs_mycoef_level = 0

                    except IndexError:

                        total_coef += bs_coef
                        total_mycoef += bs_mycoef
                        total_mycoef_level += bs_mycoef_level

                        x = left_margin
                        y += rect_one_topic.height()

                        font = QFont("Helvetica", 8, -1, True)
                        self.painter.setFont(font)

                        rect_bs_topics = QRect(x, y, width_title_topic, fm_height)
                        self.painter.fillRect(rect_bs_topics, QColor("#dfdfdf"))
                        self.painter.drawRect(rect_bs_topics)
                        self.painter.drawText(
                        QRectF(x + 3, y + 25, width_title_topic - 6, fm_height - 6), 
                        u"BILAN " + topic_type.toUpper(), option)

                        x += width_title_topic

                        font = QFont("Helvetica", 7, -1, False)
                        self.painter.setFont(font)


                        bs_my = student.Student.getStudentAverageByTopicTypeAndMarkGroup(
                                current_std_id, group_period, topic_type)

                        bs_rank = student.Student.getStudentAverageRankByTopicTypeAndMarkGroup(
                                current_std_crid, topic_type, group_period, bs_my)

                        bs_rank = infos.Infos.rankMe(bs_rank, std_genre)


                        rect_bs_my = QRect(x, y, width_title_avg, fm_height)
                        self.painter.fillRect(rect_bs_my, QColor("#dfdfdf"))
                        self.painter.drawRect(rect_bs_my)
                        self.painter.drawText(
                                   QRectF(x + 3, y + 25, width_title_avg - 6, fm_height - 6), 
                                   QString("%L1/%2")
                                             .arg(bs_my, 0, "f", 2)
                                             .arg(bs_level_my)
                                            , option)

                        x += width_title_avg

                        rect_bs_coef = QRect(x, y, width_title_coef, fm_height)
                        self.painter.fillRect(rect_bs_coef, QColor("#dfdfdf"))
                        self.painter.drawRect(rect_bs_coef)
                        self.painter.drawText(
                                   QRectF(x + 30, y + 25, width_title_coef - 6, fm_height - 6), 
                                   QString("%1").arg(bs_coef)
                                            , option)

                        x += width_title_coef

                        rect_bs_mycoef = QRect(x, y, width_title_avgcoef, fm_height)
                        self.painter.fillRect(rect_bs_mycoef, QColor("#dfdfdf"))
                        self.painter.drawRect(rect_bs_mycoef)
                        self.painter.drawText(
                                   QRectF(x + 3, y + 25, width_title_avgcoef - 6, fm_height - 6), 
                                   QString("%L1/%2")
                                           .arg(bs_mycoef, 0, "f", 2)
                                           .arg(bs_mycoef_level)
                                        , option)



                        x += width_title_avgcoef

                        rect_bs_rank = QRect(x, y, width_title_rank, fm_height)
                        self.painter.fillRect(rect_bs_rank, QColor("#dfdfdf"))
                        self.painter.drawRect(rect_bs_rank)
                        self.painter.drawText(
                                   QRectF(x + 3, y + 25, width_title_rank - 6, fm_height - 6), 
                                   QString("%1").arg(bs_rank)
                                            , option)


                        x += width_title_rank

                        rect_bs_prof = QRect(x, y, 
                              width_title_prof + width_title_remark + width_title_sign,
                              fm_height)
                        self.painter.fillRect(rect_bs_prof, QColor("#dfdfdf"))
                        self.painter.drawRect(rect_bs_prof)
                        self.painter.drawText(
                          QRectF(x + 3, y + 25, 
                      (width_title_prof + width_title_remark + width_title_sign) - 6, fm_height - 6), 
                                     u"", option)

                        bs_level_my = 0
                        bs_coef = 0
                        bs_mycoef = 0.0
                        bs_mycoef_level = 0


                    if y + 1035 >= pageRect.height():
                        self.printer.newPage()
                        pageRect = self.printer.pageRect()
                        y = initial_y
                        self.footer()


                    x = left_margin
                    y += rect_one_topic.height()

            

                x = left_margin
                y += rect_one_topic.height() - 100

                if y + 1035 >= pageRect.height():
                    self.printer.newPage()
                    pageRect = self.printer.pageRect()
                    y = initial_y
                    self.footer()

                # total points
                option = QTextOption(Qt.AlignCenter)
            
                w = width_title_topic + width_title_avg + width_title_coef + width_title_avgcoef
                w += width_title_rank + width_title_prof + width_title_remark + width_title_sign


                font = QFont("Helvetica", 8, -1, False)
                self.painter.setFont(font)

                rect_total_p = QRect(x, y, w, fm_height)
                self.painter.drawRect(rect_total_p)
                self.painter.drawText(
                    QRectF(x + 3, y + 3, w - 6, fm_height - 6), 
                        QString("Total points:  %L1/%2      Total coefficient:   %3")
                        .arg(total_mycoef, 0, "f", 2)
                        .arg(total_mycoef_level)
                        .arg(total_coef)
                    , option)

                font = QFont("Helvetica", 7, -1, False)
                self.painter.setFont(font)

                if y + 2000 >= pageRect.height():
                    self.printer.newPage()
                    pageRect = self.printer.pageRect()
                    y = initial_y
                    self.footer()


                # mg_avg_rank
                x = left_margin
                y += rect_total_p.height()
                old_y = y
            
                rect_height = 1150
                if group_period == u'2ème Trimestre' or group_period == u'3ème Trimestre' or group_period == u'2ème Semestre':
                    rect_height = 1200

                rect_mg_avg_rank = QRect(x, y, width_title_topic, fm_height + rect_height)
                self.painter.drawRect(rect_mg_avg_rank)
                self.painter.drawText(
                      QRectF(x + 3, y + 3, width_title_topic - 6, fm_height - 6), 
                      u""
                      , option)


                if rect_height == 1200:
                    t_x = x
                    t_y = y
                    w_recall = width_title_topic - 1200


                    rect_recall = QRect(t_x, y, w_recall, fm_height + 10)
                    self.painter.drawRect(rect_recall)
                    self.painter.drawText(
                             QRectF(t_x + 1, y, w_recall - 6, fm_height - 10), 
                             u"Rappel", option)

                    t_x += rect_recall.width()
                    w_moy = w_recall - 400

                    rect_moy = QRect(t_x, y, w_moy, fm_height + 10)
                    self.painter.drawRect(rect_moy)
                    self.painter.drawText(
                        QRectF(t_x + 1, y, w_moy - 6, fm_height - 10), 
                         u"Moyenne", option)

                    t_x += rect_moy.width()
                    w_rank = width_title_topic - (w_recall + w_moy)

                    rect_rank = QRect(t_x, y, w_rank, fm_height + 10)
                    self.painter.drawRect(rect_rank)
                    self.painter.drawText(
                         QRectF(t_x + 1, y, w_rank - 6, fm_height - 10), 
                         u"Rang", option)

                    if group_period == u'2ème Trimestre':
                        t_x = x
                        t_y += rect_rank.height()

                        font = QFont("Helvetica", 7, -1, True)
                        self.painter.setFont(font)
                        option = QTextOption(Qt.AlignLeft)

                        rect_recall_one = QRect(t_x, t_y, w_recall, fm_height)
                        self.painter.drawRect(rect_recall_one)
                        self.painter.drawText(
                             QRectF(t_x + 1, t_y, w_recall - 6, fm_height - 6), 
                             u"1er Trimestre", option)

                        t_x += rect_recall_one.width()

                        font = QFont("Helvetica", 7, -1, False)
                        self.painter.setFont(font)
                        option = QTextOption(Qt.AlignCenter)

                        mg = u'1er Trimestre'
                        r_mg_my = student.Student.getStudentAverageByMarkGroup(
                               current_std_id, mg) 

                        r_mg_rank = student.Student.getStudentAverageRankByMarkGroup(
                               current_std_crid, mg, r_mg_my)

                        r_mg_rank = infos.Infos.rankMe(r_mg_rank, std_genre)
        

                        rect_moy_one = QRect(t_x, t_y, w_moy, fm_height)
                        self.painter.drawRect(rect_moy_one)
                        self.painter.drawText(
                                 QRectF(t_x + 1, t_y, w_moy - 6, fm_height - 6), 
                                 QString("%L1/20")
                                     .arg(r_mg_my, 0, "f", 2)
                                 , option)

                        t_x += rect_moy_one.width()

                        rect_rank_one = QRect(t_x, t_y, w_rank, fm_height)
                        self.painter.drawRect(rect_rank_one)
                        self.painter.drawText(
                            QRectF(t_x + 1, t_y, w_rank - 6, fm_height - 6), 
                                QString("%1")
                                   .arg(r_mg_rank)
                                , option)

                    if group_period == u'3ème Trimestre':
                        # 1st
                        t_x = x
                        t_y += rect_rank.height()

                        font = QFont("Helvetica", 7, -1, True)
                        self.painter.setFont(font)
                        option = QTextOption(Qt.AlignLeft)

                        rect_recall_one = QRect(t_x, t_y, w_recall, fm_height)
                        self.painter.drawRect(rect_recall_one)
                        self.painter.drawText(
                              QRectF(t_x + 1, t_y, w_recall - 6, fm_height - 6), 
                              u"1er Trimestre", option)

                        t_x += rect_recall_one.width()

                        font = QFont("Helvetica", 7, -1, False)
                        self.painter.setFont(font)
                        option = QTextOption(Qt.AlignCenter)


                        mg = u'1er Trimestre'
                        r_mg_my = student.Student.getStudentAverageByMarkGroup(
                             current_std_id, mg) 

                        r_mg_rank = student.Student.getStudentAverageRankByMarkGroup(
                                current_std_crid, mg, r_mg_my)

                        r_mg_rank = infos.Infos.rankMe(r_mg_rank, std_genre)


                        rect_moy_one = QRect(t_x, t_y, w_moy, fm_height)
                        self.painter.drawRect(rect_moy_one)
                        self.painter.drawText(
                            QRectF(t_x + 1, t_y, w_moy - 6, fm_height - 6), 
                             QString("%L1/20")
                                 .arg(r_mg_my, 0, "f", 2)
                             , option)

                        t_x += rect_moy_one.width()

                        rect_rank_one = QRect(t_x, t_y, w_rank, fm_height)
                        self.painter.drawRect(rect_rank_one)
                        self.painter.drawText(
                             QRectF(t_x + 1, t_y, w_rank - 6, fm_height - 6), 
                             QString("%1")
                                 .arg(r_mg_rank)
                             , option)

                        #2nd
                        t_x = x
                        t_y += rect_rank_one.height()

                        font = QFont("Helvetica", 7, -1, True)
                        self.painter.setFont(font)
                        option = QTextOption(Qt.AlignLeft)

                        rect_recall_one = QRect(t_x, t_y, w_recall, fm_height)
                        self.painter.drawRect(rect_recall_one)
                        self.painter.drawText(
                                 QRectF(t_x + 1, t_y, w_recall - 6, fm_height - 6), 
                                 u"2ème Trimestre", option)

                        t_x += rect_recall_one.width()

                        font = QFont("Helvetica", 7, -1, False)
                        self.painter.setFont(font)
                        option = QTextOption(Qt.AlignCenter)


                        mg = u'2ème Trimestre'
                        r_mg_my = student.Student.getStudentAverageByMarkGroup(
                            current_std_id, mg) 

                        r_mg_rank = student.Student.getStudentAverageRankByMarkGroup(
                            current_std_crid, mg, r_mg_my)

                        r_mg_rank = infos.Infos.rankMe(r_mg_rank, std_genre)



                        rect_moy_one = QRect(t_x, t_y, w_moy, fm_height)
                        self.painter.drawRect(rect_moy_one)
                        self.painter.drawText(
                                 QRectF(t_x + 1, t_y, w_moy - 6, fm_height - 6), 
                                 QString("%L1/20")
                                     .arg(r_mg_my, 0, "f", 2)
                                 , option)

                        t_x += rect_moy_one.width()

                        rect_rank_one = QRect(t_x, t_y, w_rank, fm_height)
                        self.painter.drawRect(rect_rank_one)
                        self.painter.drawText(
                                 QRectF(t_x + 1, t_y, w_rank - 6, fm_height - 6), 
                                 QString("%1")
                                     .arg(r_mg_rank)
                                 , option)


                    if group_period == u'2ème Semestre':
                        t_x = x
                        t_y += rect_rank.height()

                        font = QFont("Helvetica", 7, -1, True)
                        self.painter.setFont(font)
                        option = QTextOption(Qt.AlignLeft)

                        rect_recall_one = QRect(t_x, t_y, w_recall, fm_height)
                        self.painter.drawRect(rect_recall_one)
                        self.painter.drawText(
                                 QRectF(t_x + 1, t_y, w_recall - 6, fm_height - 6), 
                                 u"1er Semestre", option)

                        t_x += rect_recall_one.width()

                        font = QFont("Helvetica", 7, -1, False)
                        self.painter.setFont(font)
                        option = QTextOption(Qt.AlignCenter)

                        mg = u'1er Semestre'
                        r_mg_my = student.Student.getStudentAverageByMarkGroup(
                            current_std_id, mg) 

                        r_mg_rank = student.Student.getStudentAverageRankByMarkGroup(
                            current_std_crid, mg, r_mg_my)

                        r_mg_rank = infos.Infos.rankMe(r_mg_rank, std_genre)
        

                        rect_moy_one = QRect(t_x, t_y, w_moy, fm_height)
                        self.painter.drawRect(rect_moy_one)
                        self.painter.drawText(
                                 QRectF(t_x + 1, t_y, w_moy - 6, fm_height - 6), 
                                 QString("%L1/20")
                                    .arg(r_mg_my, 0, "f", 2)
                                 , option)

                        t_x += rect_moy_one.width()

                        rect_rank_one = QRect(t_x, t_y, w_rank, fm_height)
                        self.painter.drawRect(rect_rank_one)
                        self.painter.drawText(
                                QRectF(t_x + 1, t_y, w_rank - 6, fm_height - 6), 
                                QString("%1")
                                    .arg(r_mg_rank)
                                , option)



                cut = 350
                moy_text_y = 100
                rank_text_y = 700
                if rect_height == 1200:
                    cut = 700
                    moy_text_y = 700
                    rank_text_y = 1000

                avg_group_period = student.Student.getStudentAverageByMarkGroup(
                    current_std_id, group_period)

                rank_group_period = student.Student.getStudentAverageRankByMarkGroup(
                    current_std_crid, group_period, avg_group_period)

                rank_group_period = infos.Infos.rankMe(rank_group_period, std_genre)

                font = QFont("Helvetica", 7.8, -1, False)
                self.painter.setFont(font)

                rect_mg_avg = QRect(x, y, width_title_topic, fm_height + cut)
                self.painter.drawRect(rect_mg_avg)
                self.painter.drawText(
                    QRectF(x + 3, y + moy_text_y, width_title_topic - 6, fm_height - 10), 
                    QString("Moyenne du %1: %L2/20")
                              .arg(group_period)
                              .arg(avg_group_period, 0, "f", 2)
                    , option)


                font = QFont("Helvetica", 8, -1, False)
                self.painter.setFont(font)

                self.painter.drawText(
                    QRectF(x + 3, y + rank_text_y, width_title_topic - 6, fm_height - 10), 
                    QString("Rang:  %1")
                              .arg(rank_group_period)
                    , option)


                font = QFont("Helvetica", 7, -1, False)
                self.painter.setFont(font)

                x += width_title_topic

            
                # price
                w_price = width_title_avg + width_title_coef + width_title_avgcoef

                option = QTextOption(Qt.AlignLeft)

                rect_mg_price = QRect(x, y, w_price, fm_height + rect_height)
                self.painter.drawRect(rect_mg_price)


                self.painter.drawText(
                    QRectF(x + 3, y + 3, w_price - 6, fm_height - 10), 
                    QString(u"TH + FELICITATION ")
                    , option)

                rect_little = w_price - (width_title_avgcoef + width_title_avg)
                rect_little -= 160
                rect_th_cong = QRect(x + 1700, y + 10, rect_little, fm_height - 25)
                self.painter.drawRect(rect_th_cong)

                y += rect_th_cong.height() 

                self.painter.drawText(
                    QRectF(x + 3, y + 40, w_price - 6, fm_height - 10), 
                    QString(u"TH + ENCOURAGEMENT ")
                    , option)

                rect_little_two = w_price - (width_title_avgcoef + width_title_avg)
                rect_little_two -= 160
                rect_th_encou = QRect(x + 1700, y + 10, rect_little_two, fm_height - 25)
                self.painter.drawRect(rect_th_encou)

                y += rect_th_encou.height()

                self.painter.drawText(
                        QRectF(x + 3, y + 40, w_price - 6, fm_height - 10), 
                        QString(u"TABLEAU D'HONNEUR ")
                      , option)

                rect_little_three = w_price - (width_title_avgcoef + width_title_avg)
                rect_little_three -= 160
                rect_th = QRect(x + 1700, y + 10, rect_little_three, fm_height - 25)
                self.painter.drawRect(rect_th)

                y += rect_th.height()


                self.painter.drawText(
                        QRectF(x + 3, y + 40, w_price - 6, fm_height - 10), 
                           QString(u"AVERTISSEMEMENT")
                        , option)

                rect_little_four = w_price - (width_title_avgcoef + width_title_avg)
                rect_little_four -= 160
                rect_warning = QRect(x + 1700, y + 10, rect_little_four, fm_height - 25)
                self.painter.drawRect(rect_warning)


                y += rect_warning.height()

                self.painter.drawText(
                    QRectF(x + 3, y + 40, w_price - 6, fm_height - 10), 
                    QString(u"BLÂME")
                    , option)

                rect_little_five = w_price - (width_title_avgcoef + width_title_avg)
                rect_little_five -= 160
                rect_blame = QRect(x + 1700, y + 10, rect_little_five, fm_height - 25)
                self.painter.drawRect(rect_blame)

                y += rect_blame.height()

                self.painter.drawText(
                    QRectF(x + 3, y + 40, w_price - 6, fm_height - 10), 
                    QString(u"ABSENCES JUSTIFIÉES")
                    , option)

                rect_little_six = w_price - (width_title_avgcoef + width_title_avg)
                rect_little_six -= 160
                rect_away_verified = QRect(x + 1700, y + 10, rect_little_six, fm_height - 25)
                self.painter.drawRect(rect_away_verified)


                font = QFont("Helvetica", 6, -1, False)
                self.painter.setFont(font)

                nb_away_verified = student.Student.getVerifiedAways(current_std_id)

                self.painter.drawText(
                    QRectF(x + 1708, y + 30, rect_little_six, fm_height - 10), 
                    QString(str(nb_away_verified) + u"h")
                    , option)


                font = QFont("Helvetica", 7, -1, False)
                self.painter.setFont(font)


                y += rect_away_verified.height()

            
                self.painter.drawText(
                    QRectF(x + 3, y + 40, w_price - 6, fm_height - 10), 
                    QString(u"ABSENCES NON JUSTIFIÉES")
                    , option)

                rect_little_seven = w_price - (width_title_avgcoef + width_title_avg)
                rect_little_seven -= 160
                rect_away_unverified = QRect(x + 1700, y + 10, rect_little_seven, fm_height - 25)
                self.painter.drawRect(rect_away_unverified)


                nb_away_unverified = student.Student.getUnVerifiedAways(current_std_id)

                font = QFont("Helvetica", 6, -1, False)
                self.painter.setFont(font)

                self.painter.drawText(
                    QRectF(x + 1708, y + 30, rect_little_seven, fm_height - 10), 
                    QString(str(nb_away_unverified) + u"h")
                    , option)


                font = QFont("Helvetica", 7, -1, False)
                self.painter.setFont(font)


                x += rect_mg_price.width()
                y = old_y 

                # slices
                w_slices = width_title_rank + width_title_prof + width_title_remark + width_title_sign

                rect_mg_avg_slices = QRect(x, y, w_slices, fm_height + rect_height)
                self.painter.drawRect(rect_mg_avg_slices)

                option = QTextOption(Qt.AlignCenter)

                font = QFont("Helvetica", 8, -1, False)
                self.painter.setFont(font)

                self.painter.drawText(
                    QRectF(x + 3, y - 30, w_slices - 6, fm_height - 10), 
                    u"Repartition des moyennes par tranche", option)

                font = QFont("Helvetica", 7, -1, False)
                self.painter.setFont(font)

                old_x = x 
                rect_w_slices = w_slices - (width_title_prof + width_title_remark + width_title_sign)
                rect_less_zero = QRect(x + 600, y + 150, rect_w_slices, fm_height - 25)
                self.painter.drawRect(rect_less_zero)

                self.painter.drawText(
                    QRectF(x + 600, y + 140, rect_w_slices - 6, fm_height - 10), 
                    u"] - ; 0 ]", option)

                x += rect_less_zero.width()

                rect_less_eq_8 = QRect(x + 600, y + 150, rect_w_slices, fm_height - 25)
                self.painter.drawRect(rect_less_eq_8)

                self.painter.drawText(
                    QRectF(x + 600, y + 140, rect_w_slices - 6, fm_height - 10), 
                    u"] - ; 8.50 ]", option)


                x += rect_less_eq_8.width()

                rect_range_8_10 = QRect(x + 600, y + 150, rect_w_slices, fm_height - 25)
                self.painter.drawRect(rect_range_8_10)

                self.painter.drawText(
                    QRectF(x + 600, y + 140, rect_w_slices - 6, fm_height - 10), 
                    u"[ 8.50 ; 10.00 ]", option)

                x += rect_range_8_10.width()

                rect_plus_10 = QRect(x + 600, y + 150, rect_w_slices, fm_height - 25)
                self.painter.drawRect(rect_plus_10)

                self.painter.drawText(
                    QRectF(x + 600, y + 140, rect_w_slices - 6, fm_height - 10), 
                    u"[ 10.00 ; - [", option)


                y += rect_plus_10.height()
                x = old_x

                avg_slices = classe.Class.getSlicesAverageByMarkGroup(
                    current_std_crid, group_period)

                rect_less_zero_one = QRect(x + 600, y + 150, rect_w_slices, fm_height - 25)
                self.painter.drawRect(rect_less_zero_one)

                self.painter.drawText(
                    QRectF(x + 600, y + 140, rect_w_slices - 6, fm_height - 10), 
                    QString("%1")
                        .arg(avg_slices[0])
                    , option)

                x += rect_less_zero_one.width()

                rect_less_eq_8_one = QRect(x + 600, y + 150, rect_w_slices, fm_height - 25)
                self.painter.drawRect(rect_less_eq_8_one)

                self.painter.drawText(
                    QRectF(x + 600, y + 140, rect_w_slices - 6, fm_height - 10), 
                    QString("%1")
                        .arg(avg_slices[1])
                    , option)

                x += rect_less_eq_8_one.width()

                rect_range_8_10_one = QRect(x + 600, y + 150, rect_w_slices, fm_height - 25)
                self.painter.drawRect(rect_range_8_10_one)

                self.painter.drawText(
                    QRectF(x + 600, y + 140, rect_w_slices - 6, fm_height - 10), 
                    QString("%1")
                        .arg(avg_slices[2])
                    , option)


                x += rect_range_8_10.width()

                rect_plus_10_one = QRect(x + 600, y + 150, rect_w_slices, fm_height - 25)
                self.painter.drawRect(rect_plus_10_one)

                self.painter.drawText(
                    QRectF(x + 600, y + 140, rect_w_slices - 6, fm_height - 10), 
                    QString("%1")
                        .arg(avg_slices[3])
                    , option)

                y += rect_plus_10_one.height()
                x = old_x

                font = QFont("Helvetica", 8, -1, False)
                self.painter.setFont(font)

                first_last = classe.Class.getFirstStudentAverageAndLastStudentAverageByMarkGroup(
                    current_std_crid, group_period)

                self.painter.drawText(
                    QRectF(x + 3, y + 160, w_slices - 6, fm_height - 10), 
                    QString("Moyenne du 1er:   %L1/20     Moyenne du dernier:   %L2/20")
                         .arg(first_last[0], 0, "f", 2)
                         .arg(first_last[1], 0, "f", 2)
                    , option)

                current_std_cr_avg = classe.Class.getClassroomAverageByMarkGroup(
                    current_std_crid, group_period)

                self.painter.drawText(
                    QRectF(x + 3, y + 300, w_slices - 6, fm_height - 10), 
                    QString("Moyenne de la classe:     %L1/20")
                       .arg(current_std_cr_avg, 0, "f", 2)
                    , option)


                if group_period == u'3ème Trimestre' or group_period == u'2ème Semestre':
                    avg_yearly_current_std_id = student.Student.getStudentYearlyAverage(
                        current_std_id)

                    rank_yearly_current_std_id = student.Student.getStudentYearlyRank(
                        current_std_crid, avg_yearly_current_std_id)

                    rank_yearly_current_std_id = infos.Infos.rankMe(
                        rank_yearly_current_std_id, std_genre)

                    self.painter.drawText(
                        QRectF(x + 3, y + 700, w_slices - 6, fm_height - 10), 
                        QString("Moyenne annuelle:  %L1/20")
                        .arg(avg_yearly_current_std_id, 0, "f", 2)
                    , option)

                    self.painter.drawText(
                        QRectF(x + 3, y + 850, w_slices - 6, fm_height - 10), 
                        QString("Rang annuelle:  %1")
                        .arg(rank_yearly_current_std_id)
                     , option)


                font = QFont("Helvetica", 7, -1, False)
                self.painter.setFont(font)
            
                y = old_y
                y += rect_mg_avg_slices.height()
                x = left_margin

                if y + 1035 >= pageRect.height():
                    self.printer.newPage()
                    pageRect = self.printer.pageRect()
                    y = initial_y
                    self.footer()

                font = QFont("Helvetica", 8, -1, False)
                self.painter.setFont(font)

                rect_dir = QRect(x, y, width_title_topic, fm_height + rect_height - 300)
                self.painter.drawRect(rect_dir)
                self.painter.drawText(
                    QRectF(x + 3, y + 3, width_title_topic - 6, fm_height - 6), 
                    u"DIRECTEUR:", option)

                x += width_title_topic

                rect_main_prof = QRect(x, y, w_price, fm_height + rect_height - 300)
                self.painter.drawRect(rect_main_prof)
                self.painter.drawText(
                    QRectF(x + 3, y + 3, w_price - 6, fm_height - 6), 
                    u"Professeur principal:", option)


                x += rect_main_prof.width()

                rect_main_prof = QRect(x, y, w_slices, fm_height + rect_height - 300)
                self.painter.drawRect(rect_main_prof)
                self.painter.drawText(
                    QRectF(x + 3, y + 3, w_slices - 6, fm_height - 6), 
                    u"Décision du conseil de classe:", option)

                font = QFont("Helvetica", 7, -1, False)
                self.painter.setFont(font)

                if not s + 1 == len(stds_id):
                    self.printer.newPage()
                
                self.painter.restore()

            #===============> END TABLE CONTENT <====================



                s += 1

            self.painter.end()
    


        
        
    
    def init(self):
        self.setWindowModality(Qt.WindowModal)

        """
        self.btn_radio_bul = QRadioButton(u"Bulletin de notes")
        self.btn_radio_bul.setChecked(True)
        self.btn_radio_graph = QRadioButton(u"Graphique")
        self.btn_radio_graph.setEnabled(False)
        """
        self.btn_check_header = QCheckBox(u"Inclus entête de document?")
        self.btn_check_header.setChecked(True)
        
        #if Export.isAccountHasLogo() == False: 
        self.btn_header = QPushButton(u"Entête")
        #self.btn_header = QPushButton(u"Modifier l'entête")
        

        self.btn_export = QPushButton(u"Exporter PDF")
        self.btn_export.setEnabled(False)
        self.btn_exit = QPushButton(u"Quitter")
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))
        self.btn_export.setIcon(QIcon(":/images/exportpdf.png"))
        self.btn_header.setIcon(QIcon(":/images/printheader.jpg"))


        self.btn_radio_selected_student = QRadioButton(u"L'élève selectioné(e)")
        self.btn_radio_all_students = QRadioButton(u"Tous les élèves d'une salle de classe")



        layout_bul = QFormLayout()
        layout_bul.addRow(self.btn_radio_selected_student)
        layout_bul.addRow(self.btn_radio_all_students)

        group_bul = QGroupBox(u"Bulletin de notes")
        group_bul.setLayout(layout_bul)


        self.combo_ay = QComboBox()
        self.updateAcademicYearComboBox()
        self.combo_class = QComboBox()
        self.combo_classroom = QComboBox()

        self.combo_ay.setSizeAdjustPolicy(QComboBox.AdjustToContents) 
        self.combo_class.setSizeAdjustPolicy(QComboBox.AdjustToContents) 
        self.combo_classroom.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        layout_ycr = QFormLayout()
        layout_ycr.addRow(u"Année: ", self.combo_ay)
        layout_ycr.addRow(u"Classe: ", self.combo_class)
        layout_ycr.addRow(u"Salle: ", self.combo_classroom)

        self.group_ycr = QGroupBox(u"Sélectioner la salle de classe")
        self.group_ycr.setLayout(layout_ycr)


        self.combo_period = QComboBox()
        self.combo_period.setSizeAdjustPolicy(QComboBox.AdjustToContents) 

        layout_period = QFormLayout()
        layout_period.addRow("Periode: ", self.combo_period)

        group_period = QGroupBox(u"Sélectioner la periode")
        group_period.setLayout(layout_period)

        
        layout_group = QVBoxLayout()
        layout_group.addWidget(group_bul)
        layout_group.addWidget(self.group_ycr)
        layout_group.addWidget(group_period)



        btn_box = QDialogButtonBox(Qt.Vertical)
        #btn_box.addButton(self.btn_radio_bul, QDialogButtonBox.ActionRole)
        #btn_box.addButton(self.btn_radio_graph, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_check_header, QDialogButtonBox.ActionRole)
        btn_box.addButton(self.btn_header, QDialogButtonBox.YesRole)
        btn_box.addButton(self.btn_export, QDialogButtonBox.YesRole)
        btn_box.addButton(self.btn_exit, QDialogButtonBox.RejectRole)


        layout_content = QHBoxLayout()
        layout_content.addLayout(layout_group)
        layout_content.addWidget(btn_box)


        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_content)

        self.setLayout(layout_main)


        if self.student_tree.currentIndex().isValid():
            self.btn_radio_selected_student.setChecked(True)
            self.hideYcrGroup(False)
        else:
            self.btn_radio_selected_student.setDisabled(True)
            self.btn_radio_all_students.setChecked(True)


        self.setWindowTitle(u"Exporter - InterNotes")
        
        self.resize(500, 300)


        # Events
        self.connect(self.btn_radio_selected_student, SIGNAL("clicked(bool)"), self.hideYcrGroup)
        self.connect(self.btn_radio_all_students, SIGNAL("clicked(bool)"), self.showYcrGroup)
        self.connect(self.btn_header, SIGNAL("clicked(bool)"), self.setHeader)
        self.connect(self.btn_export, SIGNAL("clicked()"), self.exportPDF)
        self.connect(self.btn_exit, SIGNAL("clicked()"), self.reject)

        self.connect(self.btn_check_header, SIGNAL("stateChanged(int)"), 
                self.btn_header.setEnabled)

        self.connect(self.combo_ay, SIGNAL("currentIndexChanged(int)"), 
                self.setClassComboBoxByAcademicYearId)

        self.connect(self.combo_class, SIGNAL("currentIndexChanged(int)"), 
                self.setClassroomComboBoxByClassId)

        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.setPeriodComboBox)


        self.connect(self.combo_classroom, SIGNAL("currentIndexChanged(int)"), 
                self.activeExportBtn)


        self.connect(self.combo_classroom, SIGNAL("activated(int)"), 
                self.activeExportBtn)



        self.show()

        if Export.isAccountHasLogo() == False: 
            QMessageBox.information(self, "Entête de document - InterNotes",
                    u"Il semble que vous n'ayez defini aucun logo d'entête de document. " 
                    u"Si aucun logo n'est défini, InterNotes générera les bulletins sans logo d'entête. "
                    u"Nous vous recommandons donc d'y ajouter un logo en cliquant sur "
                    u"le boutton \"Entête\" de la fenêtre précedente.")



        #return self.exec_()

