import sys
import os
import bcrypt
import qtawesome as qta
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QMessageBox, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QStackedWidget, QFrame)

# ==========================================
# 1. DONNÉES DE SIMULATION (MOCK DB)
# ==========================================
# Ces données permettent à l'app de fonctionner sans MySQL
MOCK_DATA = {
    "articles": [
        {"Code": "RIZ001", "Nom": "Sac de Riz 50kg", "Prix": "25 000", "Stock": "120"},
        {"Code": "HUI002", "Nom": "Huile 5L", "Prix": "6 500", "Stock": "45"}
    ],
    "clients": [
        {"Nom": "Moussa DIARRA", "Tel": "76 00 11 22", "Type": "Détaillant", "Solde": "150 000"},
        {"Nom": "Boutique Danaya", "Tel": "65 44 33 22", "Type": "Grossiste", "Solde": "0"}
    ],
    "fournisseurs": [
        {"Entreprise": "Mali Distribution", "Contact": "Sidi KONE", "Ville": "Bamako"},
        {"Entreprise": "Sodima SA", "Contact": "Fatoumata TRAORE", "Ville": "Ségou"}
    ],
    "achats": [
        {"Date": "2024-05-20", "Fournisseur": "Sodima SA", "Total": "1 250 000", "Statut": "Reçu"},
        {"Date": "2024-05-21", "Fournisseur": "Mali Distribution", "Total": "450 000", "Statut": "En commande"}
    ]
}

# ==========================================
# 2. COMPOSANT : PAGE GÉNÉRIQUE
# ==========================================
class DataPage(QWidget):
    """Classe de base pour créer des pages avec tableau et boutons d'action."""
    def __init__(self, title, data_list, columns, icon_name):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # En-tête de page
        header = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon_name, color="#2c3e50").pixmap(32, 32))
        header.addWidget(icon_label)
        header.addWidget(QLabel(f"<h1>{title}</h1>"))
        header.addStretch()
        
        btn_add = QPushButton(" Ajouter Nouveau")
        btn_add.setIcon(qta.icon('fa5s.plus-circle', color="white"))
        btn_add.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 15px; font-weight: bold;")
        btn_add.clicked.connect(lambda: QMessageBox.information(self, "Démo", f"Fenêtre d'ajout {title} (Simulation)"))
        header.addWidget(btn_add)
        layout.addLayout(header)

        # Tableau
        self.table = QTableWidget(len(data_list), len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { background-color: white; border: 1px solid #ddd; }")
        
        # Remplissage
        for row, item in enumerate(data_list):
            for col, key in enumerate(columns):
                self.table.setItem(row, col, QTableWidgetItem(str(item.get(key, ""))))
        
        layout.addWidget(self.table)

# ==========================================
# 3. FENÊTRE PRINCIPALE (DASHBOARD)
# ==========================================
class DashboardWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.setWindowTitle("DANAYA ERP - Système de Gestion Intégré")
        self.resize(1200, 800)

        # Widget Central et Layout Horizontal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- BARRE LATÉRALE (SIDEBAR) ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #2c3e50; border: none;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        
        # Logo & Titre
        logo_label = QLabel("DANAYA ERP")
        logo_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin: 20px 0;")
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        self.sidebar_layout.addWidget(logo_label)

        # Boutons de Navigation
        self.nav_buttons = {}
        menu_items = [
            (" Ventes", "fa5s.shopping-cart", 0),
            (" Achats", "fa5s.truck", 1),
            (" Articles", "fa5s.cubes", 2),
            (" Clients", "fa5s.users", 3),
            (" Fournisseurs", "fa5s.address-book", 4)
        ]

        for text, icon, index in menu_items:
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon, color="white"))
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setStyleSheet("""
                QPushButton { color: white; border: none; padding: 15px; text-align: left; font-size: 14px; }
                QPushButton:hover { background-color: #34495e; }
                QPushButton:checked { background-color: #3498db; font-weight: bold; }
            """)
            btn.clicked.connect(lambda checked, idx=index: self.container.setCurrentIndex(idx))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons[index] = btn

        self.sidebar_layout.addStretch()
        
        # Bouton Déconnexion
        btn_logout = QPushButton(" Déconnexion")
        btn_logout.setIcon(qta.icon('fa5s.power-off', color="white"))
        btn_logout.setStyleSheet("color: #e74c3c; border: none; padding: 15px; text-align: left;")
        btn_logout.clicked.connect(self.close)
        self.sidebar_layout.addWidget(btn_logout)

        self.main_layout.addWidget(self.sidebar)

        # --- ZONE DE CONTENU (STACKED WIDGET) ---
        self.container = QStackedWidget()
        self.main_layout.addWidget(self.container)

        # Création des pages
        self.container.addWidget(DataPage("Gestion des Ventes", [], ["Facture", "Client", "Montant", "Date"], "fa5s.shopping-cart"))
        self.container.addWidget(DataPage("Gestion des Achats", MOCK_DATA["achats"], ["Date", "Fournisseur", "Total", "Statut"], "fa5s.truck"))
        self.container.addWidget(DataPage("Catalogue Articles", MOCK_DATA["articles"], ["Code", "Nom", "Prix", "Stock"], "fa5s.cubes"))
        self.container.addWidget(DataPage("Répertoire Clients", MOCK_DATA["clients"], ["Nom", "Tel", "Type", "Solde"], "fa5s.users"))
        self.container.addWidget(DataPage("Registre Fournisseurs", MOCK_DATA["fournisseurs"], ["Entreprise", "Contact", "Ville"], "fa5s.address-book"))

        # Sélectionner la première page par défaut
        self.nav_buttons[0].setChecked(True)
        self.container.setCurrentIndex(0)

# ==========================================
# 4. FENÊTRE DE CONNEXION (LOGIN)
# ==========================================
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion DANAYA")
        self.setFixedSize(400, 500)
        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Style pour le login
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        title = QLabel("<h2>DANAYA</h2><p>Gestion Commerciale</p>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        self.user_input = QtWidgets.QLineEdit(placeholderText="Identifiant")
        self.pass_input = QtWidgets.QLineEdit(placeholderText="Mot de passe")
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        
        style_input = "padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px;"
        self.user_input.setStyleSheet(style_input)
        self.pass_input.setStyleSheet(style_input)
        
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)

        btn_login = QPushButton(" SE CONNECTER")
        btn_login.setIcon(qta.icon('fa5s.sign-in-alt', color="white"))
        btn_login.setStyleSheet("background-color: #3498db; color: white; padding: 12px; font-weight: bold; border-radius: 5px;")
        btn_login.clicked.connect(self.auth)
        layout.addWidget(btn_login)
        
        layout.addWidget(QLabel("<center> admin / admin </center>"))
        self.setCentralWidget(widget)

    def auth(self):
        if self.user_input.text() == "admin" and self.pass_input.text() == "admin":
            self.dashboard = DashboardWindow({"full_name": "Youssouf BOIRE", "role": "admin"})
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects.")

# ==========================================
# 5. DÉMARRAGE
# ==========================================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Palette de couleurs "Dark/Modern"
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#f5f6fa"))
    app.setPalette(palette)

    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
