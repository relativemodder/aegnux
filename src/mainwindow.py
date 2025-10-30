import os
import subprocess
from ui.mainwindow import MainWindowUI
from translations import gls
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMessageBox
from src.installationthread import InstallationThread
from src.runaethread import RunAEThread
from src.killaethread import KillAEThread
from src.removeaethread import RemoveAEThread
from src.utils import (
    check_aegnux_tip_marked, get_wine_bin_path_env,
    show_download_method_dialog, get_ae_plugins_dir, get_wineprefix_dir,
    check_aegnux_installed, mark_aegnux_tip_as_shown
)
from src.utils import read_codecs_overwrite_choice, write_codecs_overwrite_choice
from src.dialogs.codecs_options_dialog import CodecsOptionsDialog
from src.types import DownloadMethod
from src import codecs_importer
from src.codecs_importer_thread import CodecsImportThread


class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(gls('welcome_win_title'))
        self.install_button.clicked.connect(self.install_button_clicked)
        self.run_button.clicked.connect(self.run_ae_button_clicked)
        self.kill_button.clicked.connect(self.kill_ae_button_clicked)
        self.remove_aegnux_button.clicked.connect(
            self.remove_aegnux_button_clicked)
        self.toggle_logs_button.clicked.connect(self.toggle_logs)
        self.plugins_button.clicked.connect(self.plugins_folder_clicked)
        # кнопка импорта кодеков (добавлена в UI)
        try:
            self.import_codecs_button.clicked.connect(
                self.import_codecs_clicked)
        except Exception:
            # Если в UI нет кнопки (старые версии), игнорируем
            pass
        try:
            self.cancel_import_button.clicked.connect(
                self.cancel_import_clicked)
        except Exception:
            pass
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

        self.alt_t_action = QAction(self)
        self.alt_t_action.setShortcut(QKeySequence("Alt+T"))
        self.alt_t_action.triggered.connect(self.run_command_alt_t)
        self.addAction(self.alt_t_action)

        self.ctrl_q_action = QAction(self)
        self.ctrl_q_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.ctrl_q_action.triggered.connect(self.run_command_ctrl_q)
        self.addAction(self.ctrl_q_action)

        self.init_installation()

    def lock_ui(self, lock: bool = True):
        self.install_button.setEnabled(not lock)
        self.run_button.setEnabled(not lock)
        self.remove_aegnux_button.setEnabled(not lock)

        if not self.logs_edit.isVisible():
            self.toggle_logs_button.setVisible(lock)

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

        if check_aegnux_installed() and not check_aegnux_tip_marked():
            QMessageBox.information(self, '', gls('tip_alt_t'))
            mark_aegnux_tip_as_shown()

    @Slot(str)
    def _log(self, message: str):
        self.logs_edit.append(message + '\n')

    @Slot()
    def install_button_clicked(self):
        method = show_download_method_dialog(
            gls('installation_method_title'),
            gls('installation_method_text'))

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

    @Slot()
    def run_command_alt_t(self):
        env = os.environ.copy()
        env['WINEPREFIX'] = get_wineprefix_dir()
        env['PATH'] = get_wine_bin_path_env('/usr/bin')

        process = subprocess.Popen(
            ['./bin/kitty/bin/kitty', 'bash'],
            env=env
        )

    @Slot()
    def run_command_ctrl_q(self):
        exit()

    @Slot()
    def import_codecs_clicked(self):
        # выбор исходной папки (установка Windows или резервная копия)
        src = QFileDialog.getExistingDirectory(
            self, gls('select_windows_folder') if hasattr(
                gls, '__call__') else 'Select Windows folder')
        if not src:
            return

        # проверяем сохраненный выбор
        stored = read_codecs_overwrite_choice()
        overwrite = None
        remember_choice = False
        install_to_prefix = False

        if stored is None:
            dlg = CodecsOptionsDialog(self)
            overwrite, remember_choice, install_to_prefix = dlg.exec_options()
        else:
            overwrite = bool(stored)

        # Start background thread
        self.lock_ui()
        # show indeterminate progress
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()

        self._log(
            f"Starting codecs import from: {src} (overwrite={overwrite})")

        self._codecs_thread = CodecsImportThread(src, overwrite=overwrite)
        self._codecs_thread.log_signal.connect(self._log)
        self._codecs_thread.progress_signal.connect(self._on_codecs_progress)
        self._codecs_thread.finished_signal.connect(
            self._on_codecs_import_finished)
        self._codecs_thread.start()
        # показываем кнопку отмены во время выполнения
        try:
            self.cancel_import_button.show()
            self.import_codecs_button.setEnabled(False)
        except Exception:
            pass
        # если пользователь запросил установку в wineprefix, запоминаем для
        # пост-обработки
        self._install_to_prefix_pending = install_to_prefix
        # если пользователь попросил запомнить выбор, сохраняем его
        if remember_choice:
            write_codecs_overwrite_choice(overwrite)

    def _on_codecs_progress(self, processed: int, total: int):
        try:
            # switch to determinate if it was indeterminate
            if self.progress_bar.maximum() == 0:
                self.progress_bar.setRange(0, total if total > 0 else 1)
            self.progress_bar.setValue(processed)
        except Exception:
            pass

    def _on_codecs_import_finished(self, stats: dict):
        # restore progress bar to determinate state
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.lock_ui(False)

        try:
            self.cancel_import_button.hide()
            self.import_codecs_button.setEnabled(True)
        except Exception:
            pass

        msg = f"Found: {
            stats.get(
                'found',
                0)}, Copied: {
            stats.get(
                'copied',
                0)}, Skipped: {
                    stats.get(
                        'skipped',
                        0)}, Errors: {
                            stats.get(
                                'errors',
                                0)}"
        QMessageBox.information(
            self, gls('import_codecs_result') if hasattr(
                gls, '__call__') else 'Import finished', msg)

        # если пользователь запросил, устанавливаем кодеки в wineprefix
        try:
            if hasattr(
                    self,
                    '_install_to_prefix_pending') and self._install_to_prefix_pending:
                from src.utils import install_codecs_into_wineprefix
                self._log('Installing codecs into Wine prefix...')
                install_stats = install_codecs_into_wineprefix(
                    config.CODECS_DIR, logger=self._log)
                imsg = f"Installed into prefix - Found: {
                    install_stats.get(
                        'found', 0)}, Copied: {
                    install_stats.get(
                        'copied', 0)}, Skipped: {
                    install_stats.get(
                        'skipped', 0)}, Errors: {
                            install_stats.get(
                                'errors', 0)}"
                QMessageBox.information(
                    self, gls('install_to_prefix_result') if hasattr(
                        gls, '__call__') else 'Installed to prefix', imsg)
        except Exception as e:
            self._log(f'Error installing into prefix: {e}')

    @Slot()
    def cancel_import_clicked(self):
        try:
            if hasattr(
                    self,
                    '_codecs_thread') and self._codecs_thread.isRunning():
                self._log('Cancel requested...')
                self._codecs_thread.requestInterruption()
                # allow thread to wrap up
                self._codecs_thread.wait(2000)
                self._log('Cancel signal sent')
        except Exception as e:
            self._log(f'Error cancelling import: {e}')
