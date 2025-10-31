"""Тесты для системы плагинов."""

import os
import shutil
from pathlib import Path
import pytest
from src.plugins import PluginManager, AegnuxPlugin, PluginMetadata, PluginEvent, PluginError


def create_plugin(path: Path, name: str, dependencies: list = None) -> None:
    """Создает тестовый плагин."""
    plugin_dir = path / name
    plugin_dir.mkdir(parents=True, exist_ok=True)

    deps_str = f"dependencies={dependencies}" if dependencies else ""

    with open(plugin_dir / 'plugin.py', 'w') as f:
        f.write(f"""
from src.plugins import AegnuxPlugin, PluginMetadata, PluginEvent

class {name}Plugin(AegnuxPlugin):
    def __init__(self):
        self.metadata = PluginMetadata(
            name="{name}",
            version="1.0.0",
            author="Test",
            description="Test plugin",
            {deps_str}
        )
        super().__init__()

    def initialize(self):
        self.event_received = False
        self.register_event_handler(PluginEvent.BEFORE_AE_START, self.on_event)

    def on_event(self, *args, **kwargs):
        self.event_received = True
""")


def test_plugin_manager_load_plugins(tmp_path):
    """Тест базовой загрузки плагинов."""
    # Создаем тестовый плагин во временной директории
    plugin_dir = tmp_path / 'plugins' / 'test_plugin'
    plugin_dir.mkdir(parents=True)

    with open(plugin_dir / 'plugin.py', 'w') as f:
        f.write("""
from src.plugins import AegnuxPlugin, PluginMetadata

class TestPlugin(AegnuxPlugin):
    def __init__(self):
        self.metadata = PluginMetadata(
            name="Test Plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
        super().__init__()
""")

    # Настраиваем менеджер плагинов на использование тестовой директории
    manager = PluginManager()
    manager.plugins_dir = str(tmp_path / 'plugins')

    # Проверяем обнаружение плагина
    manager.discover_plugins()
    assert len(manager._plugin_classes) == 1

    # Загружаем плагин
    plugin_name = next(iter(manager._plugin_classes.keys()))
    manager.load_plugin(plugin_name)

    # Проверяем что плагин загружен и активирован
    plugin = manager.get_plugin(plugin_name)
    assert plugin is not None
    assert plugin.is_enabled

    # Проверяем отключение плагина
    manager.disable_plugin(plugin_name)
    assert not plugin.is_enabled

    # Проверяем включение плагина
    manager.enable_plugin(plugin_name)
    assert plugin.is_enabled
