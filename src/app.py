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

    show_window = True
    quit_after_handling_args = False

    for arg in sys.argv:
        if 'misterhorsepm://' in arg or '.aep' in arg:
            show_window = False
            quit_after_handling_args = True
            break

    mainWindow = MainWindow(quit_after_handling_args)
    
    if show_window:
        mainWindow.show()

    return app.exec()