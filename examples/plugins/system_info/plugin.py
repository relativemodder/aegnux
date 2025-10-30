import os
import sys
import platform
import psutil
from pathlib import Path
from src.plugins import AegnuxPlugin, PluginEvent
from PySide6.QtWidgets import (
    QMenu, QAction, QDialog, QVBoxLayout, 
    QLabel, QTextEdit, QPushButton
)

class SystemInfoPlugin(AegnuxPlugin):
    """
    Плагин для отображения системной информации и диагностики.
    """
    
    def __init__(self):
        super().__init__(
            name="System Info",
            version="1.0.0",
            description="Отображение системной информации и диагностика",
            author="Aegnux Team"
        )
        self.menu = None
        self.info_action = None

    def on_load(self):
        """Инициализация при загрузке плагина"""
        self.log.info("Плагин System Info загружен")
        self._create_menu()

    def on_unload(self):
        """Очистка при выгрузке плагина"""
        if self.menu:
            self.menu.deleteLater()
        self.log.info("Плагин System Info выгружен")

    def _create_menu(self):
        """Создание пунктов меню плагина"""
        self.menu = QMenu("Система")
        
        self.info_action = QAction("Информация о системе...", self.menu)
        self.info_action.triggered.connect(self._show_system_info)
        
        self.menu.addAction(self.info_action)
        
        # Добавляем меню в основное окно
        self.add_menu(self.menu)

    def _get_system_info(self) -> str:
        """
        Сбор системной информации
        
        Returns:
            str: Отформатированная системная информация
        """
        info = []
        
        # Информация об ОС
        info.append("=== Операционная система ===")
        info.append(f"ОС: {platform.system()} {platform.release()}")
        info.append(f"Версия: {platform.version()}")
        info.append(f"Архитектура: {platform.machine()}")
        info.append("")
        
        # Информация о CPU
        info.append("=== Процессор ===")
        info.append(f"Модель: {platform.processor()}")
        info.append(f"Ядра: {psutil.cpu_count()} (физические: {psutil.cpu_count(logical=False)})")
        info.append(f"Загрузка: {psutil.cpu_percent()}%")
        info.append("")
        
        # Информация о памяти
        mem = psutil.virtual_memory()
        info.append("=== Память ===")
        info.append(f"Всего: {self._format_bytes(mem.total)}")
        info.append(f"Доступно: {self._format_bytes(mem.available)}")
        info.append(f"Использовано: {self._format_bytes(mem.used)} ({mem.percent}%)")
        info.append("")
        
        # Информация о дисках
        info.append("=== Диски ===")
        for disk in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(disk.mountpoint)
                info.append(f"Точка монтирования: {disk.mountpoint}")
                info.append(f"  Всего: {self._format_bytes(usage.total)}")
                info.append(f"  Использовано: {self._format_bytes(usage.used)} ({usage.percent}%)")
                info.append(f"  Тип: {disk.fstype}")
                info.append("")
            except Exception:
                continue
        
        # Информация о Python
        info.append("=== Python ===")
        info.append(f"Версия: {sys.version}")
        info.append(f"Путь: {sys.executable}")
        info.append("")
        
        return "\n".join(info)

    def _format_bytes(self, bytes: int) -> str:
        """
        Форматирование размера в байтах в человекочитаемый вид
        
        Args:
            bytes: Размер в байтах
            
        Returns:
            str: Отформатированный размер
        """
        for unit in ["Б", "КБ", "МБ", "ГБ", "ТБ"]:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} ПБ"

    def _show_system_info(self):
        """Показ диалога с системной информацией"""
        dialog = QDialog()
        dialog.setWindowTitle("Информация о системе")
        dialog.resize(600, 400)
        layout = QVBoxLayout()
        
        # Текстовое поле с информацией
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText(self._get_system_info())
        layout.addWidget(info_text)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec_()