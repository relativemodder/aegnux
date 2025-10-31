"""
Управление плагинами Aegnux.

Этот модуль отвечает за всю работу с плагинами в системе:
- Поиск и загрузку плагинов
- Управление зависимостями
- Обмен событиями
- Контроль состояния

════════════════════════════════════════════════════════════════════════
Автор: Иван Петров
Создан: 15 августа 2023
Обновлён: 30 октября 2025
════════════════════════════════════════════════════════════════════════

Как использовать:
----------------
1. Создание менеджера:
   ```python
   менеджер = МенеджерПлагинов()
   ```

2. Поиск доступных плагинов:
   ```python
   менеджер.найти_плагины()  # Ищет в папке plugins/
   ```

3. Загрузка конкретного плагина:
   ```python
   менеджер.загрузить_плагин("мой_плагин")
   ```

4. Отправка события плагинам:
   ```python
   менеджер.отправить_событие(
       СобытиеПлагина.ПОСЛЕ_ЗАПУСКА_АЕ,
       данные={"время": datetime.now()}
   )
   ```

5. Управление плагинами:
   ```python
   # Включение/выключение
   менеджер.включить_плагин("мой_плагин")
   менеджер.выключить_плагин("другой_плагин")
   
   # Получение списка
   активные = менеджер.получить_все_плагины()
   ```
"""

import os
import sys
import json
import logging
import importlib
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Type, Any
from pathlib import Path

from src.utils import get_aegnux_installation_dir
from .base import ПлагинAegnux, СобытиеПлагина
from .exceptions import (
    ОшибкаПлагина,
    ОшибкаЗагрузкиПлагина,
    ПлагинНеНайден,
    ЗависимостиНеНайдены
)

# Настройка логирования
logger = logging.getLogger(__name__)


class МенеджерПлагинов:
    """
    Центральный компонент системы плагинов.
    
    Отвечает за:
    1. Поиск плагинов в файловой системе
    2. Загрузку и выгрузку плагинов
    3. Проверку зависимостей
    4. Обмен событиями между плагинами
    5. Сохранение состояния плагинов
    """

    def __init__(self) -> None:
        """Инициализация менеджера плагинов."""
        # Хранилища плагинов
        self._плагины: Dict[str, ПлагинAegnux] = {}
        self._классы_плагинов: Dict[str, Type[ПлагинAegnux]] = {}
        
        # Отслеживание загрузки для защиты от циклических зависимостей
        self._стек_загрузки: List[str] = []
        
        # Настройка логирования
        self._настроить_логирование()
        
        # Путь к директории плагинов
        корень = get_aegnux_installation_dir()
        self._папка_плагинов = Path(корень) / 'plugins'
        
        # Создаем директорию если нет
        self._папка_плагинов.mkdir(parents=True, exist_ok=True)
        
    def _настроить_логирование(self):
        """Настройка системы логирования."""
        self.логгер = logging.getLogger(__name__)
        
        # Создаем папку для логов
        лог_папка = Path.home() / ".aegnux" / "logs" / "plugins"
        лог_папка.mkdir(parents=True, exist_ok=True)
        
        # Настраиваем файловый лог
        лог_файл = лог_папка / "manager.log"
        обработчик = logging.FileHandler(лог_файл, encoding='utf-8')
        обработчик.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s: %(message)s",
                datefmt="%d.%m.%Y %H:%M:%S"
            )
        )
        self.логгер.addHandler(обработчик)

    @property
    def папка_плагинов(self) -> Path:
        """
        Получение пути к папке плагинов.
        
        Returns:
            Path: Абсолютный путь к директории плагинов
        """
        return self._папка_плагинов

    @папка_плагинов.setter
    def папка_плагинов(self, путь: Path) -> None:
        """
        Установка новой папки плагинов.
        
        Args:
            путь: Новый путь к директории плагинов
        """
        self._папка_плагинов = Path(путь)
        self.логгер.info(f"Установлена новая папка плагинов: {путь}")

    def найти_плагины(self) -> None:
        """
        Поиск доступных плагинов в файловой системе.
        
        Сканирует папку плагинов в поисках:
        1. Поддиректорий с плагинами
        2. Файлов plugin.py в каждой директории
        3. Классов, унаследованных от ПлагинAegnux
        """
        try:
            # Проверяем и создаем директорию
            if not self.папка_плагинов.exists():
                self.папка_плагинов.mkdir(parents=True)
                self.логгер.info(f"Создана папка плагинов: {self.папка_плагинов}")
                return

            # Сканируем директории
            for элемент in self.папка_плагинов.iterdir():
                if not элемент.is_dir():
                    continue

                # Ищем основной файл плагина
                файл_плагина = элемент / 'plugin.py'
                if not файл_плагина.exists():
                    continue

            try:
                self._load_plugin_module(entry, plugin_file)
            except Exception as e:
                self.logger.error(f"Ошибка при загрузке плагина {entry}: {e}")

    def _load_plugin_module(self, plugin_name: str, plugin_file: str) -> None:
        """Загружает модуль плагина из файла."""
        try:
            spec = importlib.util.spec_from_file_location(
                plugin_name, plugin_file)
            if not spec or not spec.loader:
                raise PluginLoadError(
                    f"Не удалось создать спецификацию для {plugin_file}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            # Ищем класс плагина в модуле
            plugin_class = None
            for item in dir(module):
                if item.endswith('Plugin'):
                    cls = getattr(module, item)
                    if isinstance(
                            cls, type) and issubclass(
                            cls, AegnuxPlugin) and cls != AegnuxPlugin:
                        plugin_class = cls
                        break

            if not plugin_class:
                raise PluginLoadError(
                    f"Класс плагина не найден в {plugin_file}")

            self._plugin_classes[plugin_name] = plugin_class

        except Exception as e:
            raise PluginLoadError(f"Ошибка при загрузке {plugin_file}: {e}")

    def load_plugin(self, name: str) -> None:
        """Загружает и инициализирует плагин."""
        if name not in self._plugin_classes:
            raise PluginNotFoundError(f"Плагин {name} не найден")

        if name in self._plugins:
            return  # уже загружен

        # Проверяем на циклические зависимости
        if name in self._loading_stack:
            raise PluginLoadError(
                f"Обнаружена циклическая зависимость при загрузке {name}")

        self._loading_stack.append(name)

        try:
            # Создаем экземпляр плагина
            plugin = self._plugin_classes[name]()

            # Проверяем зависимости
            if plugin.metadata.dependencies:
                for dep in plugin.metadata.dependencies:
                    if dep not in self._plugin_classes:
                        raise PluginLoadError(
                            f"Зависимость {dep} для плагина {name} не найдена")
                    if dep not in self._plugins:
                        self.load_plugin(dep)

            plugin.initialize()
            self._plugins[name] = plugin

        except Exception as e:
            raise PluginLoadError(
                f"Ошибка при инициализации плагина {name}: {e}")
        finally:
            self._loading_stack.pop()

    def unload_plugin(self, name: str) -> None:
        """Выгружает плагин."""
        if name not in self._plugins:
            return

        try:
            plugin = self._plugins[name]
            plugin.cleanup()
            del self._plugins[name]
        except Exception as e:
            self.logger.error(f"Ошибка при выгрузке плагина {name}: {e}")

    def get_plugin(self, name: str) -> Optional[AegnuxPlugin]:
        """Возвращает загруженный плагин по имени."""
        # Поддерживаем поиск как по ключу (dirname/spec name), так и по
        # метаданному имени
        p = self._plugins.get(name)
        if p:
            return p
        for plugin in self._plugins.values():
            try:
                if plugin.metadata and getattr(
                        plugin.metadata, 'name', None) == name:
                    return plugin
            except Exception:
                continue
        return None

    def get_all_plugins(self) -> List[AegnuxPlugin]:
        """Возвращает список всех загруженных плагинов."""
        return list(self._plugins.values())

    def enable_plugin(self, name: str) -> None:
        """Включает плагин."""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.is_enabled = True

    def disable_plugin(self, name: str) -> None:
        """Отключает плагин."""
        plugin = self.get_plugin(name)
        if plugin:
            # Проверяем, не зависят ли от этого плагина другие активные плагины
            for other_name, other_plugin in self._plugins.items():
                if (other_plugin.is_enabled and
                    other_plugin.metadata.dependencies and
                        name in other_plugin.metadata.dependencies):
                    raise PluginError(
                        f"Нельзя отключить плагин {name}, от него зависит {other_name}")

            plugin.is_enabled = False

    def emit_event(
            self,
            event: PluginEvent | str | object,
            *args,
            **kwargs) -> None:
        """Отправляет событие всем плагинам.

        Принимаем как экземпляр `PluginEvent`, так и имя события (строку) или
        перечисление событий — везде нормализуем к `PluginEvent` с полем `name`.
        """
        evt = None
        # Normalize possible input types
        try:
            from .base import PluginEvent as PluginEventClass
        except Exception:
            PluginEventClass = None

        if isinstance(event, str):
            evt = PluginEvent(str(event), payload=kwargs.get('payload'))
        else:
            # could be enum or dataclass-like
            if PluginEventClass and isinstance(event, PluginEventClass):
                evt = event
            else:
                # assume enum with .name
                try:
                    evt = PluginEvent(
                        event.name, payload=getattr(
                            event, 'payload', None))
                except Exception:
                    evt = PluginEvent(str(event), payload=None)

        for plugin in self._plugins.values():
            if plugin.is_enabled:
                try:
                    plugin.handle_event(evt, *args, **kwargs)
                except Exception as e:
                    self.logger.error(
                        f"Ошибка при обработке события {
                            evt.name} в плагине {
                            plugin.metadata.name}: {e}")
