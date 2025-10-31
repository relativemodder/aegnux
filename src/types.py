"""
Типы данных, используемые в приложении Aegnux.

Этот модуль содержит определения перечислений и типов данных,
используемых в различных частях приложения для обеспечения
типобезопасности и улучшения читаемости кода.

Автор: Иван Петров
Дата создания: 15.08.2023
Последнее обновление: 30.10.2025
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Union, TypedDict

class DownloadMethod(Enum):
    """Способы загрузки After Effects."""
    ONLINE = auto()      # Загрузка через интернет
    OFFLINE = auto()     # Загрузка из локального файла
    CANCEL = auto()      # Отмена загрузки

class InstallationStatus(Enum):
    """Статусы установки программы."""
    NOT_INSTALLED = auto()   # Не установлено
    INSTALLING = auto()      # Идет установка
    INSTALLED = auto()       # Установлено
    ERROR = auto()          # Ошибка установки

class CodecsImportStats(TypedDict):
    """Статистика импорта кодеков."""
    found: int              # Найдено файлов
    copied: int             # Скопировано файлов
    skipped: int            # Пропущено файлов
    errors: int             # Количество ошибок

class PluginInfo(TypedDict):
    """Информация о плагине."""
    name: str              # Имя плагина
    version: str           # Версия плагина
    author: str           # Автор плагина
    description: str      # Описание плагина
    enabled: bool         # Включен/выключен

# Константы статусов
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
STATUS_WARNING = "warning"
STATUS_INFO = "info"

# Типы сообщений для пользователя
MessageLevel = Union[
    STATUS_SUCCESS,
    STATUS_ERROR, 
    STATUS_WARNING,
    STATUS_INFO
]

# Типы результатов операций
OperationResult = Dict[str, Union[bool, str, int, List[str]]]