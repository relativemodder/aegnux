"""
Главный модуль приложения Aegnux.

Этот модуль инициализирует основное приложение, настраивает GUI
и запускает главное окно программы.
"""

import sys
import os
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from src.mainwindow_with_plugins import MainWindow
from src.config import (
    DESKTOP_FILE_NAME,
    AE_ICON_PATH,
    PLUGINS_DIR,
    LOG_FILE
)
from translations import load_strings


def setup_logging():
    """Настройка системы логирования."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )


def init_directories():
    """Инициализация необходимых директорий."""
    dirs = [
        PLUGINS_DIR,  # Директория плагинов
        Path.home() / '.aegnux' / 'cache',  # Кэш
        Path.home() / '.aegnux' / 'temp',  # Временные файлы
        Path.home() / '.aegnux' / 'config',  # Конфигурация
    ]
    
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)


def main():
    """Точка входа в приложение."""
    # Инициализация
    setup_logging()
    init_directories()
    load_strings()
    
    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("Aegnux")
    app.setApplicationVersion("0.1.0-alpha")
    app.setDesktopFileName(DESKTOP_FILE_NAME)
    app.setWindowIcon(QIcon(AE_ICON_PATH))
    
    # Запуск главного окна
    main_window = MainWindow()
    main_window.show()
    
    # Запуск цикла обработки событий
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
