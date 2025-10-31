import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict
from src.plugins import AegnuxPlugin, PluginEvent
from PySide6.QtWidgets import (
    QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QTextEdit, QMessageBox, QCheckBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal

class WinetricksWorker(QThread):
    """Поток для выполнения команд winetricks"""
    progress = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, prefix_path: str, packages: List[str]):
        super().__init__()
        self.prefix_path = prefix_path
        self.packages = packages
        
    def run(self):
        try:
            env = os.environ.copy()
            env["WINEPREFIX"] = self.prefix_path
            
            process = subprocess.Popen(
                ["winetricks", "--unattended"] + self.packages,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                self.progress.emit(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.finished.emit(True, "Установка завершена успешно")
            else:
                self.finished.emit(False, f"Ошибка установки (код {process.returncode})")
                
        except Exception as e:
            self.finished.emit(False, str(e))

class WinetricksGUIPlugin(AegnuxPlugin):
    """
    Плагин для графического интерфейса Winetricks
    """
    
    def __init__(self):
        super().__init__(
            name="Winetricks GUI",
            version="1.0.0",
            description="Графический интерфейс для Winetricks",
            author="Aegnux Team"
        )
        self.menu = None
        self.cache_dir = Path.home() / ".aegnux" / "cache" / "winetricks"
        self.packages_cache = self.cache_dir / "packages.json"
        self.packages: Dict = {}
        
    def on_load(self):
        """Инициализация при загрузке плагина"""
        self.log.info("Плагин Winetricks GUI загружен")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._create_menu()
        self._load_packages()
        
    def on_unload(self):
        """Очистка при выгрузке плагина"""
        if self.menu:
            self.menu.deleteLater()
        self.log.info("Плагин Winetricks GUI выгружен")
        
    def _create_menu(self):
        """Создание пунктов меню"""
        self.menu = QMenu("Winetricks")
        
        install_action = QAction("Установить компоненты...", self.menu)
        install_action.triggered.connect(self._show_installer)
        
        refresh_action = QAction("Обновить список компонентов", self.menu)
        refresh_action.triggered.connect(self._update_packages)
        
        self.menu.addAction(install_action)
        self.menu.addAction(refresh_action)
        
        self.add_menu(self.menu)
        
    def _load_packages(self):
        """Загрузка списка пакетов из кэша"""
        try:
            if self.packages_cache.exists():
                with open(self.packages_cache, 'r', encoding='utf-8') as f:
                    self.packages = json.load(f)
            else:
                self._update_packages()
        except Exception as e:
            self.log.error(f"Ошибка загрузки списка пакетов: {e}")
            self.packages = {}
            
    def _update_packages(self):
        """Обновление списка доступных пакетов"""
        try:
            result = subprocess.run(
                ["winetricks", "--list"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                packages = {}
                current_category = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.endswith(':'):
                        current_category = line[:-1]
                        packages[current_category] = []
                    elif current_category and not line.startswith('-'):
                        name = line.split()[0]
                        packages[current_category].append(name)
                
                self.packages = packages
                
                with open(self.packages_cache, 'w', encoding='utf-8') as f:
                    json.dump(packages, f, indent=2)
                    
                self.log.info("Список пакетов успешно обновлен")
                
            else:
                raise Exception(f"winetricks вернул код {result.returncode}")
                
        except Exception as e:
            self.log.error(f"Ошибка обновления списка пакетов: {e}")
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Не удалось обновить список пакетов:\n{str(e)}"
            )
    
    def _show_installer(self):
        """Показ диалога установки компонентов"""
        dialog = QDialog()
        dialog.setWindowTitle("Установка компонентов Winetricks")
        dialog.resize(800, 600)
        layout = QVBoxLayout()
        
        # Список категорий и пакетов
        packages_layout = QHBoxLayout()
        
        # Список пакетов
        packages_list = QListWidget()
        packages_list.setSelectionMode(QListWidget.MultiSelection)
        
        for category, items in self.packages.items():
            packages_list.addItem(QListWidgetItem(f"=== {category} ==="))
            for item in sorted(items):
                list_item = QListWidgetItem(item)
                list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Unchecked)
                packages_list.addItem(list_item)
                
        packages_layout.addWidget(packages_list)
        
        # Лог установки
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        packages_layout.addWidget(log_text)
        
        layout.addLayout(packages_layout)
        
        # Прогресс установки
        progress = QProgressBar()
        progress.setVisible(False)
        layout.addWidget(progress)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        install_button = QPushButton("Установить")
        install_button.clicked.connect(
            lambda: self._install_packages(
                packages_list,
                log_text,
                progress,
                install_button
            )
        )
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(install_button)
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def _install_packages(
        self,
        packages_list: QListWidget,
        log_text: QTextEdit,
        progress: QProgressBar,
        install_button: QPushButton
    ):
        """
        Установка выбранных пакетов
        
        Args:
            packages_list: Список пакетов
            log_text: Виджет для вывода лога
            progress: Индикатор прогресса
            install_button: Кнопка установки
        """
        selected_packages = []
        
        for i in range(packages_list.count()):
            item = packages_list.item(i)
            if (item.flags() & Qt.ItemIsUserCheckable and 
                item.checkState() == Qt.Checked):
                selected_packages.append(item.text())
                
        if not selected_packages:
            QMessageBox.warning(
                None,
                "Предупреждение",
                "Выберите компоненты для установки"
            )
            return
            
        # Получаем текущий префикс
        prefix_path = os.environ.get("WINEPREFIX")
        if not prefix_path:
            QMessageBox.critical(
                None,
                "Ошибка",
                "Не задан путь к префиксу Wine (WINEPREFIX)"
            )
            return
            
        # Запускаем установку в отдельном потоке
        progress.setVisible(True)
        progress.setRange(0, 0)
        install_button.setEnabled(False)
        log_text.clear()
        
        self.worker = WinetricksWorker(prefix_path, selected_packages)
        
        def on_progress(message):
            log_text.append(message)
            log_text.verticalScrollBar().setValue(
                log_text.verticalScrollBar().maximum()
            )
            
        def on_finished(success, message):
            progress.setVisible(False)
            install_button.setEnabled(True)
            
            if success:
                log_text.append("\n" + message)
                QMessageBox.information(None, "Успешно", message)
            else:
                log_text.append("\nОшибка: " + message)
                QMessageBox.critical(None, "Ошибка", message)
        
        self.worker.progress.connect(on_progress)
        self.worker.finished.connect(on_finished)
        self.worker.start()