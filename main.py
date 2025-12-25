import sys
import qtawesome as qta
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QStackedWidget, QFrame, QLineEdit)

# ==========================================
# 1. BASE DE DONNÉES DE SIMULATION (MOCK DATA)
# ==========================================
ALL_DATA = {
    "categories": [
        {"ID": "CAT01", "Nom": "Céréales", "Description": "Riz, Maïs, Mil"},
        {"ID": "CAT02", "Nom": "Huiles", "Description": "Huile végétale, Beurre"},
        {"ID": "CAT03", "Nom": "Boissons", "Description": "Sodas, Eau minérale"}
    ],
    "articles": [
        {"Code": "RIZ001", "Nom": "Sac de Riz 50kg", "Prix": "25 000", "Stock": "120", "Cat": "Céréales"},
        {"Code": "HUI002", "Nom": "Huile 5L", "Prix": "6 500", "Stock": "45", "Cat": "Huiles"},
        {"Code": "EAU005", "Nom": "Pack Eau 1.5L", "Prix": "3 000", "Stock": "200", "Cat": "Boissons"}
    ],
    "ventes": [
        {"Facture": "FAC-2024-001", "Client": "Moussa DIARRA", "Montant": "50 000", "Date": "2024-05-20"},
        {"Facture": "FAC-2024-002", "Client": "Boutique Danaya", "Montant": "125 000", "Date": "2024-05-21"}
    ],
    "achats": [
        {"BC": "ACH-99", "Fournisseur": "SODIMA SA", "Total": "1 200 000", "Statut": "Livré"},
        {"BC": "ACH-100", "Fournisseur": "Mali Distribution", "Total": "450 000", "Statut": "En attente"}
    ],
    "clients": [
        {"Nom": "Moussa DIARRA", "Tel": "76 00 11 22", "Type": "Détaillant", "Solde": "15 000"},
        {"Nom": "Boutique Danaya", "Tel": "65 44 33 22", "Type": "Grossiste", "Solde": "0"}
    ],
    "fournisseurs": [
        {"Nom": "SODIMA SA", "Contact": "Sidi KONE", "Ville": "Bamako", "Dette": "250 000"},
        {"Nom": "Mali Distribution", "Contact": "Awa TRAORE", "Ville": "Ségou", "Dette": "0"}
    ],
    "magasins": [
        {"Nom": "Dépôt Principal", "Lieu": "ACI 2000", "Responsable": "Amadou"},
        {"Nom": "Annexe Marché", "Lieu": "Grand Marché", "Responsable": "Fatima"}
    ],
    "ajustements": [
        {"Date": "2024-12-20", "Article": "Sac de Riz 50kg", "Qte": "-5", "Type": "Casse", "Note": "Sac percé"},
        {"Date": "2024-12-22", "Article": "Huile 5L", "Qte": "+10", "Type": "Entrée", "Note": "Inventaire"}
    ]
}

# ==========================================
# 2. COMPOSANTS DE L'INTERFACE
# ==========================================

class DataTablePage(QWidget):
    """Classe de base pour les pages avec tableau et recherche."""
    def __init__(self, title, data, columns, color):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel(f"<h1 style='color:{color}'>{title}</h1>"))
        header.addStretch()
        btn_add = QPushButton(" + Nouveau")
        btn_add.setStyleSheet(f"background-color: {color}; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        header.addWidget(btn_add)
        layout.addLayout(header)

        # Search Bar
        self.search = QLineEdit(placeholderText=f"🔍 Rechercher dans {title.lower()}...")
        self.search.setStyleSheet("padding: 12px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;")
        self.search.textChanged.connect(self.filter_table)
        layout.addWidget(self.search)

        # Table
        self.table = QTableWidget(len(data), len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        
        self.populate_table(data)
        layout.addWidget(self.table)

    def populate_table(self, data):
        for row, item in enumerate(data):
            for col, key in enumerate(item.keys()):
                self.table.setItem(row, col, QTableWidgetItem(str(item[key])))

    def filter_table(self):
        search_text = self.search.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

class StockPage(DataTablePage):
    """Page Stock avec alertes visuelles."""
    def __init__(self):
        super().__init__("État des Stocks", ALL_DATA["articles"], 
                         ["Code", "Nom", "Prix", "Stock", "Catégorie"], "#2980b9")
        self.apply_alerts()

    def apply_alerts(self):
        for row in range(self.table.rowCount()):
            stock_item = self.table.item(row, 3)
            if stock_item and int(stock_item.text()) < 50:
                stock_item.setForeground(QtGui.QColor("#e74c3c"))
                stock_item.setText(f"⚠️ {stock_item.text()} (Bas)")

class DashboardPage(QWidget):
    """Page d'accueil avec cartes de statistiques."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h1>DANAYA APP - Vue d'ensemble</h1>"))
        
        grid = QHBoxLayout()
        stats = [
            ("Ventes Total", "2 450 000 F", "#9b59b6", "fa5s.chart-line"),
            ("Stock Valeur", "12 800 000 F", "#2ecc71", "fa5s.boxes"),
            ("Commandes", "145", "#3498db", "fa5s.shopping-cart"),
            ("Alertes Stock", "4", "#e74c3c", "fa5s.exclamation-triangle")
        ]
        
        for label, val, color, icon_name in stats:
            card = QFrame()
            card.setStyleSheet(f"background-color: {color}; border-radius: 12px; min-width: 220px; padding: 20px;")
            l = QVBoxLayout(card)
            
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon(icon_name, color="white").pixmap(45, 45))
            icon_label.setAlignment(QtCore.Qt.AlignCenter)
            l.addWidget(icon_label)
            
            l.addWidget(QLabel(f"<center><font color='white' size='4'>{label}</font></center>"))
            l.addWidget(QLabel(f"<center><font color='white' size='6'><b>{val}</b></font></center>"))
            grid.addWidget(card)
        
        layout.addLayout(grid)
        layout.addStretch()
        layout.addWidget(QLabel("<center><b>Utilisez le menu à gauche pour naviguer dans les outils de gestion.</b></center>"))

# ==========================================
# 3. FENÊTRE PRINCIPALE
# ==========================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DANAYA ERP v1.0")
        self.resize(1280, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("background-color: white; border-right: 1px solid #ddd;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        logo = QLabel("DANAYA APP")
        logo.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50; padding: 25px 0;")
        logo.setAlignment(QtCore.Qt.AlignCenter)
        self.sidebar_layout.addWidget(logo)

        self.container = QStackedWidget()
        
        # Menu Configuration (Texte, Icone, Couleur, Widget)
        self.menu_items = [
            (" Accueil", "fa5s.home", "#7f8c8d", DashboardPage()),
            (" Catégories", "fa5s.th-list", "#27ae60", DataTablePage("Catégories", ALL_DATA["categories"], ["ID", "Nom", "Description"], "#27ae60")),
            (" Articles", "fa5s.cubes", "#2ecc71", DataTablePage("Catalogue Articles", ALL_DATA["articles"], ["Code", "Nom", "Prix", "Stock", "Famille"], "#2ecc71")),
            (" Stock", "fa5s.box", "#2980b9", StockPage()),
            (" Ajustement", "fa5s.tools", "#3498db", DataTablePage("Historique Ajustements", ALL_DATA["ajustements"], ["Date", "Article", "Qte", "Type", "Note"], "#3498db")),
            (" Ventes", "fa5s.shopping-cart", "#9b59b6", DataTablePage("Journal des Ventes", ALL_DATA["ventes"], ["Facture", "Client", "Montant", "Date"], "#9b59b6")),
            (" Achats", "fa5s.truck", "#e67e22", DataTablePage("Achats Fournisseurs", ALL_DATA["achats"], ["BC", "Fournisseur", "Total", "Statut"], "#e67e22")),
            (" Fournisseurs", "fa5s.address-book", "#d35400", DataTablePage("Répertoire Fournisseurs", ALL_DATA["fournisseurs"], ["Nom", "Contact", "Ville", "Solde"], "#d35400")),
            (" Clients", "fa5s.users", "#8e44ad", DataTablePage("Fichier Clients", ALL_DATA["clients"], ["Nom", "Tel", "Type", "Solde"], "#8e44ad")),
            (" Magasins", "fa5s.warehouse", "#95a5a6", DataTablePage("Gestion Dépôts", ALL_DATA["magasins"], ["Nom", "Lieu", "Responsable"], "#95a5a6")),
        ]

        for i, (text, icon, color, page_widget) in enumerate(self.menu_items):
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon, color="white"))
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: {color}; color: white; border: none; padding: 13px; 
                             text-align: left; font-weight: bold; margin: 3px 15px; border-radius: 6px; font-size: 13px; }}
                QPushButton:hover {{ background-color: #34495e; }}
                QPushButton:checked {{ border: 2px solid #333; background-color: #2c3e50; }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.container.setCurrentIndex(idx))
            self.sidebar_layout.addWidget(btn)
            self.container.addWidget(page_widget)

        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(QLabel("<center>© 2025 Danaya Boutique</center>"))

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.container)

# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Palette Modernisée
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#ffffff"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
