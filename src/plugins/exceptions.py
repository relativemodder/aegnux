"""Исключения для системы плагинов."""


class PluginError(Exception):
    """Базовое исключение для ошибок плагинов."""
    pass


class PluginLoadError(PluginError):
    """Ошибка при загрузке плагина."""
    pass


class PluginNotFoundError(PluginError):
    """Плагин не найден."""
    pass


class PluginInitError(PluginError):
    """Ошибка при инициализации плагина."""
    pass
