from ui.mainwindow import MainWindowUI
from translations import gls
from PySide6.QtCore import Slot


class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(gls('welcome_win_title'))
        self.install_button.clicked.connect(self.install_button_clicked)
    
    @Slot()
    def install_button_clicked(self):
        pass