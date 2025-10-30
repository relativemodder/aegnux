"""Менеджер плагинов."""

import os
import sys
import importlib.util
import logging
from typing import Dict, List, Optional, Type

from src.utils import get_aegnux_installation_dir
from .base import AegnuxPlugin, PluginEvent
from .exceptions import PluginError, PluginLoadError, PluginNotFoundError


class PluginManager:
    """Управляет загрузкой и работой плагинов."""

    def __init__(self) -> None:
        """Инициализация менеджера плагинов."""
        self._plugins: Dict[str, AegnuxPlugin] = {}
        self._plugin_classes: Dict[str, Type[AegnuxPlugin]] = {}
        # Для обнаружения циклических зависимостей
        self._loading_stack: List[str] = []
        self.logger = logging.getLogger(__name__)
        self._plugins_dir = os.path.join(
            get_aegnux_installation_dir(), 'plugins')

    @property
    def plugins_dir(self) -> str:
        """Путь к директории с пользовательскими плагинами."""
        return self._plugins_dir

    @plugins_dir.setter
    def plugins_dir(self, path: str) -> None:
        """Установить путь к директории с плагинами."""
        self._plugins_dir = path

    def discover_plugins(self) -> None:
        """Находит все доступные плагины в директории плагинов."""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            return

        for entry in os.listdir(self.plugins_dir):
            plugin_dir = os.path.join(self.plugins_dir, entry)
            if not os.path.isdir(plugin_dir):
                continue

            plugin_file = os.path.join(plugin_dir, 'plugin.py')
            if not os.path.exists(plugin_file):
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
