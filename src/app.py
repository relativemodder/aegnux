import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.mainwindow import MainWindow
from src.config import DESKTOP_FILE_NAME, AE_ICON_PATH
from src.utils import check_aegnux_installed
from translations import load_strings

def main():
    load_strings()
    app = QApplication(sys.argv)
    app.setDesktopFileName(DESKTOP_FILE_NAME)
    app.setWindowIcon(QIcon(AE_ICON_PATH))

    show_window = True
    quit_after_handling_args = False

    # Headless launches (.aep files, misterhorsepm:// links) quit once the task they start
    # finishes. Without an installation nothing is started, so the process would idle forever
    # with no window; show the installer instead.
    if check_aegnux_installed():
        for arg in sys.argv:
            if 'misterhorsepm://' in arg or '.aep' in arg:
                show_window = False
                quit_after_handling_args = True
                break

    mainWindow = MainWindow(quit_after_handling_args)
    
    if show_window:
        mainWindow.show()

    exit_code = app.exec()
    mainWindow.wait_for_workers()
    return exit_code