import sys
from PySide6.QtWidgets import QApplication, QStackedWidget
from LoginPage import LoginPage
from MainWindow import MainWindow  


def main():
    app = QApplication(sys.argv)

    # Création du gestionnaire de fenêtres (StackedWidget)
    widget_manager = QStackedWidget()

    # Création des pages
    login_page = LoginPage(widget_manager)
    main_window = MainWindow(widget_manager)

    # Ajout des pages au gestionnaire
    widget_manager.addWidget(login_page)
    widget_manager.addWidget(main_window)

    # Afficher la page de connexion au démarrage
    widget_manager.setCurrentWidget(login_page)

    widget_manager.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
