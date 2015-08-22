#! -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import tools

class About(QDialog):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)

        self.init()
        
     
    def init(self):
        logo = QPixmap(":/images/banner.png")
        label_logo = QLabel()
        label_logo.setPixmap(logo)


        layout_head = QHBoxLayout()
        layout_head.addWidget(label_logo)


        logo_matlle = QPixmap(":/images/logomatllebanner.png")
        #logo_matlle.scaled(10, 10)
        label_logo_matlle = QLabel()
        label_logo_matlle.setPixmap(logo_matlle)
        

        page_about = QWidget()

        label_about = QLabel()
        label_about.setText(QString(
           u"<strong>InterNotes</strong>, logiciel conçu pour rendre simple et facile la gestion des bulletins de notes scolaires et universitaires<br/><br/> "
           u"<strong>Version 1.0.2 (Windows x86)</strong><br></br><br/><br/><br/>"
           u"Copyright © 2015 Matlle e.i. Tous droits reservés.<br/><br/><br/><br/><br/><br/><br/><br/>"
           u"<span style="">(+225) 07 08 68 98 / 41 87 07 68 / 01 58 03 30</span><br/>"
           u"matllesoftware@gmail.com<br/>"
           u"www.matlle.com"))

        label_about.setAlignment(Qt.AlignLeft)
        label_about.setWordWrap(True)

        layout_about = QHBoxLayout()
        layout_about.addWidget(label_about)
        page_about.setLayout(layout_about)


        page_licence = QWidget()

        label_licence = QLabel()
        label_licence.setText(QString(
            u"<h3>L'utilisation du present logiciel implique l'acceptation de ce contrat de licence<h3>"
            u"<h4>1. Licence<h4>"
            u"Le Propriétaire accorde au Bénéficiaire une licence non exclusive et non transférable "
            u"(1) pour utiliser le logiciel uniquement dans le cadre de ses activités à l'emplacement "
            u"et au sein de l'environnement prévu et (2) une copie du logiciel aux fins d'archivage ou de "
            u"sauvegarde pourvu que les mentions des titres, droits de marques et droits d'auteurs, "
            u"periode d'utilisation et autres droits personnels ou réservés figurent sur toutes les copies et "
            u"que toutes les copies soient sujettes au présent contrat. <br/>"
            u"<h4>2. Distribution</h4>"
            u"Sauf stipulation explicite contenue dans ce présent contrat, le Bénéficiaire "
            u"ne devra pas : (1) mettre à disposition d'autrui ni distribuer le logiciel ni aucun élément du "
            u"logiciel afférent à quelque partie que ce soit, ni accorder une sous-licence; (2) copier, concevoir "
            u"une version inverse, identique ou semblable, décomposer, dissocier, modifier en partie ou en totalité "
            u"le logiciel; (3) utiliser le logiciel dans le cadre d'échange de services, la sous-traitance, ou "
            u"autoriser une tierce partie à l'environnement prévu d'avoir accès au logiciel.<br/>"
            u"<h4>3. Installation et acceptation </h4>"
            u"Le Propriétaire prendra toute les dispositions nécessaires pour livrer les copies du logiciel "
            u"dont la licence est jointe au présent logiciel. Le Bénéficiaire disposera alors de 15 jours après la livraison "
            u"pour effectuer le test ou l'essai d'acceptation du logiciel. L'acceptation du logiciel par le Bénéficiaire sera "
            u"effective à partir de la date d'utilisation du logiciel ou à la date d'expiration de la période "
            u"de 15 jours à compter de la date d'installation sans que le Bénéficiaire n'ait besoin d'informer "
            u"le Propriétaire de quelque erreur ou amelioration. Si le Bénéficiaire notifie une erreur ou "
            u"une amelioration au Propriétaire et le Bénéficiaire "
            u"diagnostique la prétendue erreur ou amelioration, le logiciel sera accepté à la correction de cette erreur ou "
            u"à l'implementation de cette amelioration.<br/>"
            u"<h4>4. Prix</h4>"
            u"Le Bénéficiaire devra payer le prix du logiciel conformément aux modalités de paiement prévu "
            u"et facturé de façon raisonnable par le propriétaire du logiciel pour l'installation du logiciel. "
            u"Le paiement s'effectuera en intégralité sans quelque droit de compensation ou réduction et le Bénéficiaire paiera le prix et les eventuels frais au plus tard 30 jours aprés la période de test ou d'essai."
            ))

        label_licence.setAlignment(Qt.AlignLeft)
        label_licence.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidget(label_licence)

        layout_licence = QHBoxLayout()
        layout_licence.addWidget(scroll_area)
        page_licence.setLayout(layout_licence)
        

        onglets = QTabWidget()
        onglets.addTab(page_about, "À propos")
        onglets.addTab(page_licence, "Contrat de Licence")


        layout_body = QHBoxLayout()
        layout_body.addWidget(label_logo_matlle)
        layout_body.addWidget(onglets)


        self.btn_exit = QPushButton(u"Quitter")
        self.btn_exit.setIcon(QIcon(":/images/editdelete.png"))



        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.btn_exit)
        layout_btn.setAlignment(Qt.AlignRight)
        

        layout_main = QVBoxLayout()
        #layout_main.addWidget(group_year_and_class)
        layout_main.addLayout(layout_head)
        layout_main.addLayout(layout_body)
        #layout_main.addWidget(onglets)
        layout_main.addLayout(layout_btn)


        self.setLayout(layout_main)
        self.resize(600, 400)
        self.setWindowTitle(u"À propos d'InterNotes")
        

        self.connect(self.btn_exit, SIGNAL("clicked()"), 
                self.reject)


        return self.exec_()

     
