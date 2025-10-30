"""
Конфигурационный модуль Aegnux.

Содержит все основные настройки приложения, включая пути к файлам,
параметры системы и константы. Разделен на логические секции для
удобства поддержки и модификации.
"""

import os
from pathlib import Path


# Основные параметры приложения
APP_NAME = "Aegnux"
APP_VERSION = "0.1.0-alpha"
DESKTOP_FILE_NAME = "com.relative.Aegnux"
LOG_THROTTLE_SECONDS = 0.1

# Базовые директории
BASE_DIR = Path(os.getcwd())
CONFIG_DIR = Path.home() / ".aegnux" / "config"
CACHE_DIR = Path.home() / ".aegnux" / "cache"
TEMP_DIR = Path.home() / ".aegnux" / "temp"
LOG_DIR = Path.home() / ".aegnux" / "logs"

# Файлы логов
LOG_FILE = LOG_DIR / "aegnux.log"
ERROR_LOG = LOG_DIR / "errors.log"
DEBUG_LOG = LOG_DIR / "debug.log"

# Пути к ресурсам
ICONS_DIR = BASE_DIR / "icons"
STYLES_DIR = BASE_DIR / "styles"
ASSETS_DIR = BASE_DIR / "assets"

AE_ICON_PATH = ICONS_DIR / "aegnux.png"
WINE_STYLE_REG = STYLES_DIR / "wine_dark_theme.reg"

# Настройки Wine
WINE_RUNNER_DIR = ASSETS_DIR / "wine"
WINETRICKS_BIN = BASE_DIR / "bin" / "winetricks"
CABEXTRACT_BIN = BASE_DIR / "bin" / "cabextract"

# Компоненты и зависимости
VCR_ZIP = ASSETS_DIR / "vcr.zip"
MSXML_ZIP = ASSETS_DIR / "msxml3.zip"

# URL для загрузки
AE_DOWNLOAD_URL = "https://huggingface.co/cutefishae/AeNux-model/resolve/main/2024.zip"
AE_PLUGINS_URL = "https://huggingface.co/cutefishae/AeNux-model/resolve/main/aenux-require-plugin.zip"

# Настройки загрузки
AE_FILENAME = Path("/tmp/ae2024.zip")
DOWNLOAD_CHUNK_SIZE = 1024 * 8  # 8KB

# Настройки кодеков
CODECS_DIR = WINE_RUNNER_DIR / "win_codecs"
CODECS_EXTENSIONS = [".dll", ".ax", ".acm", ".axf", ".axv"]
CODECS_OVERWRITE_BY_DEFAULT = False

# Настройки плагинов
PLUGINS_DIR = BASE_DIR / "plugins"
PLUGIN_CONFIG_DIR = CONFIG_DIR / "plugins"
PLUGIN_DATA_DIR = Path.home() / ".aegnux" / "plugin_data"

# Создание необходимых директорий при импорте
for directory in [
    CONFIG_DIR,
    CACHE_DIR,
    TEMP_DIR,
    LOG_DIR,
    PLUGIN_CONFIG_DIR,
    PLUGIN_DATA_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)
