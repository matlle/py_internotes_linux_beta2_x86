#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pyqt_style_rc, images_rc
import tools, dbconfig, guard

from mainwindow import MainWindow




def main():
    reboot = True

    while reboot:
        app = QApplication(sys.argv)
        app.setOrganizationName("Matlle")
        app.setOrganizationDomain("matlle.com")
        app.setApplicationName("InterNotes")
        app.setWindowIcon(QIcon(':/images/logo.png'))

        translatorFileName = QLatin1String("qt_");
        translatorFileName += QLocale.system().name()
        translator = QTranslator(app)
        if (translator.load(translatorFileName,
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))):
            app.installTranslator(translator)



        #app.setStyle("plastique")

        css = QFile(':/qdarkstyle/style.qss')
        css.open(QIODevice.ReadOnly)
        if css.isOpen():
            app.setStyleSheet(QVariant(css.readAll()).toString())
        css.close()

    

        QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF-8"))
        QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"))
        
        """
        locale = QLocale.system().name().section('_', 0, 0)
        translator = QTranslator(app)
        translator.load(QString("qt_") + locale,
            QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        app.installTranslator(translator)
        """


        g = guard.Guard() 

        mainwindow = None 

        try:
            mainwindow = MainWindow()
            mainwindow.readPositionSettings()
            mainwindow.guard = g
            mainwindow.show()
        except ValueError:
            pass


        ret_code = app.exec_()
        if ret_code == tools.EXIT_CODE_REBOOT:
            del g
            if mainwindow:
                del mainwindow
            del app
            reboot = True
        else:
            reboot = False



if __name__== '__main__':
    main()
