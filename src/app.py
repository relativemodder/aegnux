import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.mainwindow import MainWindow
from src.config import DESKTOP_FILE_NAME, AE_ICON_PATH
from translations import load_strings

def main():
    load_strings()
    app = QApplication(sys.argv)
    app.setDesktopFileName(DESKTOP_FILE_NAME)
    app.setWindowIcon(QIcon(AE_ICON_PATH))

    mainWindow = MainWindow()
    mainWindow.show()

    return app.exec()