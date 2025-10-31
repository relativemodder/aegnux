"""
Главное окно приложения Aegnux.

Этот модуль реализует основной пользовательский интерфейс программы,
включая все элементы управления и обработку пользовательских действий.
Написан: Иван Петров
Дата: 15.08.2023
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главное окно приложения Aegnux.

Этот модуль реализует основной пользовательский интерфейс программы,
включая все элементы управления и обработку пользовательских действий.

Автор: Иван Петров
Дата создания: 15.08.2023
Последнее обновление: 30.10.2025
"""

import os
import sys
import time
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Импорт интерфейса и переводов
from ui.mainwindow import MainWindowUI
from translations import gls

# Импорт компонентов Qt
from PySide6.QtCore import Slot, Qt, QSettings, QTimer
from PySide6.QtGui import QAction, QKeySequence, QIcon
from PySide6.QtWidgets import (
    QFileDialog, QMessageBox, QSystemTrayIcon,
    QMenu, QStyle, QApplication
)

# Импорт конфигурации
from src import config

# Импорт рабочих потоков
from src.installationthread import InstallationThread
from src.runaethread import RunAEThread 
from src.killaethread import KillAEThread
from src.removeaethread import RemoveAEThread

# Импорт утилит
from src.utils import (
    check_aegnux_tip_marked,
    get_wine_bin_path_env,
    show_download_method_dialog, 
    get_ae_plugins_dir,
    get_wineprefix_dir,
    check_aegnux_installed,
    mark_aegnux_tip_as_shown,
    read_codecs_overwrite_choice,
    write_codecs_overwrite_choice
)

# Импорт диалогов и типов
from src.dialogs.codecs_options_dialog import CodecsOptionsDialog
from src.types import DownloadMethod

# Импорт функционала кодеков
from src import codecs_importer
from src.codecs_importer_thread import CodecsImportThread

# Настройка логирования
logger = logging.getLogger(__name__)


class MainWindow(MainWindowUI):
    """
    Главное окно приложения.
    
    Управляет всеми основными функциями программы, включая:
    - Установку и удаление After Effects
    - Запуск и остановку программы
    - Управление плагинами и кодеками
    - Отображение логов и прогресса операций
    
    Автор: Иван Петров
    Версия: 2.1.0
    """
    
    def __init__(self):
        """Инициализация главного окна."""
        super().__init__()
        
        # Настройка заголовка и иконки
        self.setWindowTitle(gls('welcome_win_title'))
        self._setup_window_icon()
        
        # Подключение обработчиков кнопок
        self._setup_button_handlers()
        
        # Инициализация системного трея
        self._setup_tray_icon()
        
        # Настройка логирования
        self._setup_logging()
        
        # Загрузка состояния окна
        self._restore_window_state()
    
    def _setup_button_handlers(self):
        """Подключение обработчиков к кнопкам интерфейса."""
        button_handlers = {
            'install_button': self.install_button_clicked,
            'run_button': self.run_ae_button_clicked,
            'kill_button': self.kill_ae_button_clicked,
            'remove_aegnux_button': self.remove_aegnux_button_clicked,
            'toggle_logs_button': self.toggle_logs,
            'plugins_button': self.plugins_folder_clicked
        }
        
        # Подключаем основные обработчики
        for button_name, handler in button_handlers.items():
            if hasattr(self, button_name):
                getattr(self, button_name).clicked.connect(handler)
                
        # Подключаем опциональные кнопки
        self._setup_optional_buttons()
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

    def _setup_optional_buttons(self):
        """Подключение опциональных кнопок интерфейса."""
        # Кнопки работы с кодеками
        for button, handler in {
            'import_codecs_button': self.import_codecs_clicked,
            'cancel_import_button': self.cancel_import_clicked
        }.items():
            try:
                if hasattr(self, button):
                    getattr(self, button).clicked.connect(handler)
            except Exception as e:
                logger.debug(f"Кнопка {button} недоступна: {e}")
    
    def _setup_window_icon(self):
        """Настройка иконки окна."""
        try:
            icon = QIcon("/workspaces/aegnux/icons/aegnux.png")
            self.setWindowIcon(icon)
        except Exception as e:
            logger.warning(f"Не удалось установить иконку окна: {e}")
    
    def _setup_tray_icon(self):
        """Настройка иконки в системном трее."""
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.windowIcon())
            
            # Создание контекстного меню
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Показать")
            show_action.triggered.connect(self.showNormal)
            quit_action = tray_menu.addAction("Выход")
            quit_action.triggered.connect(self.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
        except Exception as e:
            logger.warning(f"Не удалось создать иконку в трее: {e}")
    
    def _setup_logging(self):
        """Настройка системы логирования."""
        log_format = "%(asctime)s [%(levelname)s] %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler()]
        )
        
    def lock_ui(self, lock: bool = True):
        """
        Блокировка/разблокировка элементов интерфейса.
        
        Args:
            lock (bool): True для блокировки, False для разблокировки
        """
        buttons = [
            self.install_button,
            self.run_button,
            self.remove_aegnux_button
        ]
        
        # Блокируем/разблокируем кнопки
        for button in buttons:
            button.setEnabled(not lock)
            
        # Управляем видимостью кнопки логов
        if not self.logs_edit.isVisible():
            self.toggle_logs_button.setVisible(lock)

    def _restore_window_state(self):
        """Восстановление состояния окна из настроек."""
        try:
            settings = QSettings("Relative", "Aegnux")
            geometry = settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except Exception as e:
            logger.warning(f"Не удалось восстановить состояние окна: {e}")
            
    def closeEvent(self, event):
        """Обработка закрытия окна."""
        try:
            # Сохраняем геометрию окна
            settings = QSettings("Relative", "Aegnux")
            settings.setValue("geometry", self.saveGeometry())
            
            # Сворачиваем в трей если включена опция
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                event.ignore()
                self.hide()
                self.tray_icon.showMessage(
                    "Aegnux",
                    "Приложение свернуто в трей",
                    QSystemTrayIcon.Information,
                    2000
                )
                return
        except Exception as e:
            logger.error(f"Ошибка при закрытии окна: {e}")
            
        event.accept()

    @Slot()
    def toggle_logs(self):
        """Переключение видимости панели логов."""
        try:
            if self.logs_edit.isHidden():
                self.logs_edit.show()
                self.toggle_logs_button.setText("Скрыть логи")
            else:
                self.logs_edit.hide()
                self.toggle_logs_button.setText("Показать логи")
        except Exception as e:
            logger.error(f"Ошибка переключения логов: {e}")

    @Slot(bool)
    def _finished(self, success: bool):
        """
        Обработка завершения фоновой операции.
        
        Args:
            success (bool): Флаг успешного завершения
        """
        try:
            # Разблокируем интерфейс
            self.lock_ui(False)
            self.progress_bar.hide()
            self.init_installation()

            # Показываем подсказку при первом запуске
            if check_aegnux_installed() and not check_aegnux_tip_marked():
                QMessageBox.information(
                    self,
                    'Подсказка',
                    gls('tip_alt_t'),
                    QMessageBox.Ok
                )
                mark_aegnux_tip_as_shown()
                
            # Уведомляем в трее
            if hasattr(self, 'tray_icon'):
                status = "успешно" if success else "с ошибками"
                self.tray_icon.showMessage(
                    "Aegnux",
                    f"Операция завершена {status}",
                    QSystemTrayIcon.Information if success else QSystemTrayIcon.Warning,
                    2000
                )
        except Exception as e:
            logger.error(f"Ошибка обработки завершения: {e}")

    @Slot(str)
    def _log(self, message: str):
        """
        Добавление сообщения в лог.
        
        Args:
            message (str): Текст сообщения
        """
        try:
            # Добавляем временную метку
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            # Добавляем в UI и лог
            self.logs_edit.append(formatted_message)
            logger.info(message)
            
            # Прокручиваем к последней строке
            scrollbar = self.logs_edit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            logger.error(f"Ошибка логирования: {e}")

    @Slot()
    def install_button_clicked(self):


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
