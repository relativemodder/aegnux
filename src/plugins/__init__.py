"""Инициализация системы плагинов."""

from .base import AegnuxPlugin, PluginMetadata, PluginEvent
from .manager import PluginManager
from .exceptions import PluginError, PluginLoadError, PluginNotFoundError

__all__ = [
    'AegnuxPlugin',
    'PluginMetadata',
    'PluginManager',
    'PluginError',
    'PluginLoadError',
    'PluginNotFoundError',
    'PluginEvent'
]
