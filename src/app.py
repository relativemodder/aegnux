import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.mainwindow_with_plugins import MainWindow
from src.config import DESKTOP_FILE_NAME, AE_ICON_PATH, PLUGINS_DIR
from translations import load_strings


def main():
    load_strings()
    app = QApplication(sys.argv)
    app.setDesktopFileName(DESKTOP_FILE_NAME)
    app.setWindowIcon(QIcon(AE_ICON_PATH))

    # Создаем каталог для плагинов, если его нет
    import os
    if not os.path.exists(PLUGINS_DIR):
        os.makedirs(PLUGINS_DIR)

    mainWindow = MainWindow()
    mainWindow.show()

    return app.exec()
