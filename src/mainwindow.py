import os
from ui.mainwindow import MainWindowUI
from translations import gls
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog
from src.installationthread import InstallationThread
from src.runaethread import RunAEThread
from src.killaethread import KillAEThread
from src.removeaethread import RemoveAEThread
from src.utils import show_download_method_dialog, get_ae_plugins_dir, get_wineprefix_dir
from src.types import DownloadMethod


class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(gls('welcome_win_title'))
        self.install_button.clicked.connect(self.install_button_clicked)
        self.run_button.clicked.connect(self.run_ae_button_clicked)
        self.kill_button.clicked.connect(self.kill_ae_button_clicked)
        self.remove_aegnux_button.clicked.connect(self.remove_aegnux_button_clicked)
        self.toggle_logs_button.clicked.connect(self.toggle_logs)
        self.plugins_button.clicked.connect(self.plugins_folder_clicked)
        self.wineprefix_button.clicked.connect(self.wineprefix_folder_clicked)

        self.install_thread = InstallationThread()
        self.install_thread.log_signal.connect(self._log)
        self.install_thread.progress_signal.connect(self.progress_bar.setValue)
        self.install_thread.finished_signal.connect(self._finished)

        self.run_ae_thread = RunAEThread()
        self.run_ae_thread.log_signal.connect(self._log)
        self.run_ae_thread.finished_signal.connect(self._finished)

        self.kill_ae_thread = KillAEThread()
        self.remove_ae_thread = RemoveAEThread()
        self.remove_ae_thread.finished_signal.connect(self._finished)

        self.init_installation()

    def lock_ui(self, lock: bool = True):
        self.install_button.setEnabled(not lock)
        self.run_button.setEnabled(not lock)
        self.remove_aegnux_button.setEnabled(not lock)
    
    @Slot()
    def toggle_logs(self):
        if self.logs_edit.isHidden():
            self.logs_edit.show()
            return
        self.logs_edit.hide()
    
    @Slot(bool)
    def _finished(self, success: bool):
        self.lock_ui(False)
        self.progress_bar.hide()
        self.init_installation()

    @Slot(str)
    def _log(self, message: str):
        self.logs_edit.append(message + '\n')
    
    @Slot()
    def install_button_clicked(self):
        method = show_download_method_dialog(gls('installation_method_title'), gls('installation_method_text'))

        if method == DownloadMethod.CANCEL:
            return
        
        self.install_thread.set_download_method(method)

        if method == DownloadMethod.OFFLINE:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                gls('offline_ae_zip_title'),
                "",
                "Zip Files (*.zip);;All Files (*)"
            )
            if filename == '':
                return
            
            self.install_thread.set_offline_filename(filename)
        
        self.lock_ui()
        self.progress_bar.show()
        self.install_thread.start()
    
    @Slot()
    def run_ae_button_clicked(self):
        self.lock_ui()
        self.run_ae_thread.start()
    
    @Slot()
    def kill_ae_button_clicked(self):
        self.kill_ae_thread.start()
    
    @Slot()
    def remove_aegnux_button_clicked(self):
        self.lock_ui()
        self.remove_ae_thread.start()
    
    @Slot()
    def plugins_folder_clicked(self):
        os.system(f'xdg-open "{get_ae_plugins_dir()}"')
    
    @Slot()
    def wineprefix_folder_clicked(self):
        os.system(f'xdg-open "{get_wineprefix_dir()}"')