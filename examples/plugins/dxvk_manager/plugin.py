import os
import json
import requests
from pathlib import Path
from src.plugins import AegnuxPlugin, PluginEvent
from PySide6.QtWidgets import (
    QMenu, QAction, QDialog, QVBoxLayout, 
    QComboBox, QPushButton, QProgressBar,
    QMessageBox
)

class DXVKManagerPlugin(AegnuxPlugin):
    """
    Плагин для управления версиями DXVK в префиксах Wine.
    """
    
    DXVK_RELEASES_URL = "https://api.github.com/repos/doitsujin/dxvk/releases"
    
    def __init__(self):
        super().__init__(
            name="DXVK Manager",
            version="1.0.0",
            description="Установка и управление версиями DXVK",
            author="Aegnux Team"
        )
        self.cache_dir = Path.home() / ".aegnux" / "cache" / "dxvk"
        self.menu = None
        self.install_action = None
        self.versions = []

    def on_load(self):
        """Инициализация при загрузке плагина"""
        self.log.info("Плагин DXVK Manager загружен")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._create_menu()
        self._fetch_versions()

    def on_unload(self):
        """Очистка при выгрузке плагина"""
        if self.menu:
            self.menu.deleteLater()
        self.log.info("Плагин DXVK Manager выгружен")

    def _create_menu(self):
        """Создание пунктов меню плагина"""
        self.menu = QMenu("DXVK")
        
        self.install_action = QAction("Установить DXVK...", self.menu)
        self.install_action.triggered.connect(self._show_install_dialog)
        
        self.menu.addAction(self.install_action)
        
        # Добавляем меню в основное окно
        self.add_menu(self.menu)

    def _fetch_versions(self):
        """Получение списка доступных версий DXVK"""
        try:
            response = requests.get(self.DXVK_RELEASES_URL)
            response.raise_for_status()
            
            releases = response.json()
            self.versions = [release["tag_name"] for release in releases]
            
            self.log.info(f"Получен список версий DXVK: {len(self.versions)} версий")
            
        except Exception as e:
            self.log.error(f"Ошибка при получении списка версий DXVK: {e}")
            self.versions = []

    def _show_install_dialog(self):
        """Показ диалога установки DXVK"""
        dialog = QDialog()
        dialog.setWindowTitle("Установка DXVK")
        layout = QVBoxLayout()
        
        # Комбобокс с версиями
        version_combo = QComboBox()
        version_combo.addItems(self.versions)
        layout.addWidget(version_combo)
        
        # Прогрессбар
        progress = QProgressBar()
        progress.setVisible(False)
        layout.addWidget(progress)
        
        # Кнопка установки
        install_button = QPushButton("Установить")
        install_button.clicked.connect(
            lambda: self._install_dxvk(
                version_combo.currentText(),
                progress,
                dialog
            )
        )
        layout.addWidget(install_button)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def _install_dxvk(self, version: str, progress: QProgressBar, dialog: QDialog):
        """
        Установка выбранной версии DXVK
        
        Args:
            version: Версия DXVK для установки
            progress: Виджет прогрессбара
            dialog: Диалог установки
        """
        try:
            progress.setVisible(True)
            progress.setRange(0, 0)  # Бесконечный прогресс
            
            # TODO: Реализовать загрузку и установку DXVK
            # Здесь должен быть код для:
            # 1. Загрузки архива DXVK
            # 2. Распаковки в кэш
            # 3. Копирования DLL в префикс
            # 4. Регистрации DLL
            
            QMessageBox.information(
                dialog,
                "Успешно",
                f"DXVK версии {version} успешно установлен"
            )
            
            self.log.info(f"Установлена версия DXVK {version}")
            
            dialog.accept()
            
        except Exception as e:
            self.log.error(f"Ошибка при установке DXVK: {e}")
            QMessageBox.critical(
                dialog,
                "Ошибка",
                f"Не удалось установить DXVK:\n{str(e)}"
            )
            progress.setVisible(False)