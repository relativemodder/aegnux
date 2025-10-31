import os
import json
import shutil
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from src.plugins import AegnuxPlugin, PluginEvent
from PySide6.QtWidgets import (
    QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QComboBox, QProgressBar, QMessageBox, QLineEdit,
    QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal

class WineBuildsAPI:
    """API для работы с репозиторием сборок Wine"""
    
    WINE_GE_API = "https://api.github.com/repos/GloriousEggroll/wine-ge-custom/releases"
    
    @classmethod
    def get_available_versions(cls) -> List[Dict]:
        """
        Получение списка доступных версий Wine
        
        Returns:
            List[Dict]: Список версий с информацией
        """
        try:
            response = requests.get(cls.WINE_GE_API)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Ошибка получения списка версий: {e}")

    @classmethod
    def download_version(
        cls,
        url: str,
        target_path: Path,
        progress_callback: callable
    ):
        """
        Загрузка архива с Wine
        
        Args:
            url: URL для загрузки
            target_path: Путь для сохранения
            progress_callback: Функция для отображения прогресса
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total = int(response.headers.get('content-length', 0))
            block_size = 8192
            wrote = 0
            
            with open(target_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    wrote = wrote + len(data)
                    f.write(data)
                    if total:
                        progress = wrote / total * 100
                        progress_callback(progress)
                        
        except Exception as e:
            if target_path.exists():
                target_path.unlink()
            raise Exception(f"Ошибка загрузки: {e}")

class DownloadWorker(QThread):
    """Поток для загрузки версии Wine"""
    progress = Signal(float)
    finished = Signal(bool, str)
    
    def __init__(self, url: str, target_path: Path):
        super().__init__()
        self.url = url
        self.target_path = target_path
        
    def run(self):
        try:
            WineBuildsAPI.download_version(
                self.url,
                self.target_path,
                lambda p: self.progress.emit(p)
            )
            self.finished.emit(True, "Загрузка завершена")
        except Exception as e:
            self.finished.emit(False, str(e))

class WineManagerPlugin(AegnuxPlugin):
    """
    Плагин для управления версиями Wine
    """
    
    def __init__(self):
        super().__init__(
            name="Wine Manager",
            version="1.0.0",
            description="Управление версиями Wine",
            author="Aegnux Team"
        )
        self.menu = None
        self.versions_cache = Path.home() / ".aegnux" / "cache" / "wine-versions"
        self.builds_dir = Path.home() / ".aegnux" / "wine-builds"
        self.current_version: Optional[str] = None
        
    def on_load(self):
        """Инициализация при загрузке плагина"""
        self.log.info("Плагин Wine Manager загружен")
        self.versions_cache.mkdir(parents=True, exist_ok=True)
        self.builds_dir.mkdir(parents=True, exist_ok=True)
        self._create_menu()
        
    def on_unload(self):
        """Очистка при выгрузке плагина"""
        if self.menu:
            self.menu.deleteLater()
        self.log.info("Плагин Wine Manager выгружен")
        
    def _create_menu(self):
        """Создание пунктов меню"""
        self.menu = QMenu("Wine Manager")
        
        manage_action = QAction("Управление версиями...", self.menu)
        manage_action.triggered.connect(self._show_manager)
        
        self.menu.addAction(manage_action)
        
        self.add_menu(self.menu)
        
    def _get_installed_versions(self) -> List[str]:
        """
        Получение списка установленных версий
        
        Returns:
            List[str]: Список установленных версий
        """
        return [d.name for d in self.builds_dir.iterdir() if d.is_dir()]
        
    def _show_manager(self):
        """Показ диалога управления версиями"""
        dialog = QDialog()
        dialog.setWindowTitle("Управление версиями Wine")
        dialog.resize(800, 600)
        layout = QVBoxLayout()
        
        # Список установленных версий
        installed_group = QVBoxLayout()
        installed_group.addWidget(QLabel("Установленные версии:"))
        
        installed_list = QListWidget()
        installed_list.addItems(self._get_installed_versions())
        installed_group.addWidget(installed_list)
        
        # Кнопки управления версиями
        buttons_layout = QHBoxLayout()
        
        install_button = QPushButton("Установить новую версию...")
        install_button.clicked.connect(
            lambda: self._show_install_dialog(dialog, installed_list)
        )
        
        remove_button = QPushButton("Удалить")
        remove_button.clicked.connect(
            lambda: self._remove_version(installed_list)
        )
        
        buttons_layout.addWidget(install_button)
        buttons_layout.addWidget(remove_button)
        
        # Компоновка элементов
        layout.addLayout(installed_group)
        layout.addLayout(buttons_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def _show_install_dialog(self, parent: QDialog, installed_list: QListWidget):
        """
        Показ диалога установки новой версии
        
        Args:
            parent: Родительский диалог
            installed_list: Список установленных версий
        """
        dialog = QDialog(parent)
        dialog.setWindowTitle("Установка версии Wine")
        layout = QVBoxLayout()
        
        try:
            # Получаем список доступных версий
            releases = WineBuildsAPI.get_available_versions()
            
            # Комбобокс с версиями
            version_combo = QComboBox()
            for release in releases:
                version_combo.addItem(
                    release["name"],
                    userData=release
                )
            layout.addWidget(version_combo)
            
            # Прогрессбар
            progress = QProgressBar()
            progress.setVisible(False)
            layout.addWidget(progress)
            
            # Кнопки
            buttons = QHBoxLayout()
            
            install_button = QPushButton("Установить")
            install_button.clicked.connect(
                lambda: self._install_version(
                    version_combo.currentData(),
                    progress,
                    install_button,
                    dialog,
                    installed_list
                )
            )
            
            cancel_button = QPushButton("Отмена")
            cancel_button.clicked.connect(dialog.reject)
            
            buttons.addWidget(install_button)
            buttons.addWidget(cancel_button)
            layout.addLayout(buttons)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(
                dialog,
                "Ошибка",
                f"Не удалось получить список версий:\n{str(e)}"
            )
            dialog.reject()
            
    def _install_version(
        self,
        release: Dict,
        progress: QProgressBar,
        install_button: QPushButton,
        dialog: QDialog,
        installed_list: QListWidget
    ):
        """
        Установка выбранной версии
        
        Args:
            release: Информация о версии
            progress: Виджет прогрессбара
            install_button: Кнопка установки
            dialog: Диалог установки
            installed_list: Список установленных версий
        """
        try:
            # Находим подходящий asset
            asset = None
            for a in release["assets"]:
                if "linux-x86_64" in a["name"]:
                    asset = a
                    break
                    
            if not asset:
                raise Exception("Не найден архив для Linux x86_64")
                
            # Подготовка путей
            version_name = release["name"]
            target_dir = self.builds_dir / version_name
            
            if target_dir.exists():
                raise Exception(f"Версия {version_name} уже установлена")
                
            archive_path = self.versions_cache / asset["name"]
            
            # Запуск загрузки
            progress.setVisible(True)
            install_button.setEnabled(False)
            
            worker = DownloadWorker(asset["browser_download_url"], archive_path)
            
            def on_progress(percent):
                progress.setValue(int(percent))
                
            def on_finished(success, message):
                if success:
                    try:
                        # Распаковка архива
                        subprocess.run(
                            ["tar", "xf", str(archive_path), "-C", str(self.builds_dir)],
                            check=True
                        )
                        
                        # Обновление списка
                        installed_list.addItem(version_name)
                        
                        QMessageBox.information(
                            dialog,
                            "Успешно",
                            f"Версия {version_name} установлена"
                        )
                        dialog.accept()
                        
                    except Exception as e:
                        QMessageBox.critical(
                            dialog,
                            "Ошибка",
                            f"Ошибка распаковки архива:\n{str(e)}"
                        )
                        if target_dir.exists():
                            shutil.rmtree(target_dir)
                else:
                    QMessageBox.critical(
                        dialog,
                        "Ошибка",
                        f"Ошибка загрузки:\n{message}"
                    )
                    
                progress.setVisible(False)
                install_button.setEnabled(True)
                
            worker.progress.connect(on_progress)
            worker.finished.connect(on_finished)
            worker.start()
            
        except Exception as e:
            QMessageBox.critical(
                dialog,
                "Ошибка",
                str(e)
            )
            
    def _remove_version(self, installed_list: QListWidget):
        """
        Удаление выбранной версии
        
        Args:
            installed_list: Список установленных версий
        """
        selected = installed_list.currentItem()
        if not selected:
            QMessageBox.warning(
                None,
                "Предупреждение",
                "Выберите версию для удаления"
            )
            return
            
        version = selected.text()
        
        reply = QMessageBox.question(
            None,
            "Подтверждение",
            f"Удалить версию {version}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                shutil.rmtree(self.builds_dir / version)
                installed_list.takeItem(installed_list.row(selected))
                
            except Exception as e:
                QMessageBox.critical(
                    None,
                    "Ошибка",
                    f"Не удалось удалить версию:\n{str(e)}"
                )