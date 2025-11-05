import os
import subprocess
from ui.mainwindow import MainWindowUI
from translations import gls
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMessageBox
from src.installationthread import InstallationThread
from src.runaethread import RunAEThread
from src.runexethread import RunExeThread
from src.killaethread import KillAEThread
from src.pluginthread import PluginThread
from src.removeaethread import RemoveAEThread
from src.utils import (
    check_aegnux_tip_marked, get_default_terminal, get_wine_bin_path_env, 
    get_cep_dir, get_ae_plugins_dir, get_wineprefix_dir, 
    check_aegnux_installed, mark_aegnux_tip_as_shown, get_ae_install_dir, get_aegnux_installation_dir
)
from src.types import DownloadMethod


class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(gls('welcome_win_title'))
        self.install_button.clicked.connect(self.install_button_clicked)
        self.run_button.clicked.connect(self.run_ae_button_clicked)
        self.remove_aegnux_button.clicked.connect(self.remove_aegnux_button_clicked)

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

        self.plugin_thread = PluginThread()
        self.plugin_thread.log_signal.connect(self._log)
        self.plugin_thread.progress_signal.connect(self.progress_bar.setValue)
        self.plugin_thread.finished_signal.connect(self._finished)

        self.alt_t_action = QAction(self)
        self.alt_t_action.setShortcut(QKeySequence("Alt+T"))
        self.alt_t_action.triggered.connect(self.run_command_alt_t)
        self.addAction(self.alt_t_action)

        self.ctrl_q_action = QAction(self)
        self.ctrl_q_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.ctrl_q_action.triggered.connect(self.run_command_ctrl_q)
        self.addAction(self.ctrl_q_action)

        self._construct_menubar()
        self.init_installation()

        self.ae_action.triggered.connect(self.run_ae_button_clicked)
        self.exe_action.triggered.connect(self.run_exe_button_clicked)
        self.reg_action.triggered.connect(self.reg_button_clicked)
        self.plugininst_action.triggered.connect(self.install_plugins_button_clicked)
        self.kill_action.triggered.connect(self.kill_ae_button_clicked)
        self.log_action.triggered.connect(self.toggle_logs)
        self.term_action.triggered.connect(self.run_command_alt_t)
        self.wpd_action.triggered.connect(self.wineprefix_folder_clicked)
        self.plugind_action.triggered.connect(self.plugins_folder_clicked)
        self.aed_action.triggered.connect(self.ae_folder_clicked)
        self.aeg_action.triggered.connect(self.aegnux_folder_clicked)
        self.cep_action.triggered.connect(self.cep_folder_clicked)

    def init_installation(self):
        if check_aegnux_installed():
            self.install_button.hide()
            self.run_button.show()
            self.remove_aegnux_button.show()

            self.runMenu.setEnabled(True)
            self.browseMenu.setEnabled(True)
            self.kill_action.setEnabled(True)
            self.plugininst_action.setEnabled(True)
            self.term_action.setEnabled(True)

        else:
            self.install_button.show()
            self.run_button.hide()
            self.remove_aegnux_button.hide()

            self.runMenu.setEnabled(False)
            self.browseMenu.setEnabled(False)
            self.kill_action.setEnabled(False)
            self.term_action.setEnabled(False)
            self.plugininst_action.setEnabled(False)
    
    def _construct_menubar(self):
        self.runMenu = self.menuBar().addMenu(gls('run_menu'))
        self.ae_action = self.runMenu.addAction(gls('ae_action'))
        self.exe_action = self.runMenu.addAction(gls('exe_action'))
        self.plugininst_action = self.runMenu.addAction(gls('plugininst_action'))
        self.reg_action = self.runMenu.addAction(gls('reg_action'))

        self.browseMenu = self.menuBar().addMenu(gls('browse_menu'))
        self.wpd_action = self.browseMenu.addAction(gls('wpd_action'))
        self.plugind_action = self.browseMenu.addAction(gls('plugind_action'))
        self.aed_action = self.browseMenu.addAction(gls('aed_action'))
        self.aeg_action = self.browseMenu.addAction(gls('aeg_action'))
        self.cep_action = self.browseMenu.addAction(gls('cep_action'))

        self.debugMenu = self.menuBar().addMenu(gls('debug_menu'))
        self.kill_action = self.debugMenu.addAction(gls('kill_action'))
        self.log_action = self.debugMenu.addAction(gls('log_action'))
        self.term_action = self.debugMenu.addAction(gls('term_action'))

    def lock_ui(self, lock: bool = True):
        self.install_button.setEnabled(not lock)
        self.run_button.setEnabled(not lock)
        self.remove_aegnux_button.setEnabled(not lock)

        self.runMenu.setEnabled(not lock)
    
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

        if not success:
            QMessageBox.critical(
                self,
                gls('error'),
                self.logs_edit.toPlainText().split('\n')[-2]
            )
            return

        if check_aegnux_installed() and not check_aegnux_tip_marked():
            QMessageBox.information(self, '', gls('tip_alt_t'))
            mark_aegnux_tip_as_shown()


    @Slot(str)
    def _log(self, message: str):
        self.logs_edit.append(message + '\n')
    
    @Slot()
    def install_button_clicked(self):
        # method = show_download_method_dialog(gls('installation_method_title'), gls('installation_method_text'))

        method = DownloadMethod.OFFLINE

        if method == DownloadMethod.CANCEL:
            return
        
        self.install_thread.set_download_method(method)

        if method == DownloadMethod.OFFLINE:
            QMessageBox.warning(
                self,
                gls('offline_note'),
                gls('offline_note_text')
            )

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
    def install_plugins_button_clicked(self):
        QMessageBox.information(
            self,
            gls('plugin_note'),
            gls('plugin_note_text')
        )

        filename, _ = QFileDialog.getOpenFileName(
            self,
            gls('offline_ae_zip_title'),
            "",
            "Zip Files (*.zip);;All Files (*)"
        )
        if filename == '':
            return
        
        self.plugin_thread.set_plugin_zip_filename(filename)
        
        self.lock_ui()
        self.progress_bar.show()
        self.plugin_thread.start()
    
    @Slot()
    def run_ae_button_clicked(self):
        self.lock_ui()
        self.run_ae_thread.start()
    
    @Slot()
    def run_exe_button_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            gls('Open .exe'),
            "",
            "Exe Files (*.exe);;All Files (*)"
        )
        if filename == '':
            return

        self.run_exe_thread = RunExeThread([filename])
        self.run_exe_thread.log_signal.connect(self._log)
        self.run_exe_thread.finished_signal.connect(self._finished)

        self.lock_ui()
        self.run_exe_thread.start()
    
    @Slot()
    def reg_button_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            gls('Open .reg'),
            "",
            "Reg Files (*.reg);;All Files (*)"
        )
        if filename == '':
            return

        self.reg_thread = RunExeThread(['regedit', filename])
        self.reg_thread.log_signal.connect(self._log)
        self.reg_thread.finished_signal.connect(self._finished)

        self.lock_ui()
        self.reg_thread.start()
    
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
    
    @Slot()
    def ae_folder_clicked(self):
        os.system(f'xdg-open "{get_ae_install_dir()}"')
    
    @Slot()
    def aegnux_folder_clicked(self):
        os.system(f'xdg-open "{get_aegnux_installation_dir()}"')
    
    @Slot()
    def cep_folder_clicked(self):
        os.system(f'xdg-open "{get_cep_dir()}"')
    
    @Slot()
    def run_command_alt_t(self):
        env = os.environ.copy()
        env['WINEPREFIX'] = get_wineprefix_dir()
        env['PATH'] = get_wine_bin_path_env('/usr/bin')

        try:
            terminal = get_default_terminal()
            subprocess.Popen([terminal, "bash"], env=env)
        except RuntimeError as e:
            print("[CRITICAL ERROR]:", e)
    
    @Slot()
    def run_command_ctrl_q(self):
        exit()