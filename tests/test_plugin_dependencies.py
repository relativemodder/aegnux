from tests.test_plugins import create_plugin
import pytest
from src.plugins import PluginManager, PluginError


def test_plugin_dependencies(tmp_path):
    """Тест загрузки плагинов с зависимостями."""
    plugins_dir = tmp_path / 'plugins'

    # Создаем плагины с зависимостями
    create_plugin(plugins_dir, 'Base')
    create_plugin(plugins_dir, 'Dependent', dependencies=['Base'])

    # Настраиваем менеджер плагинов
    manager = PluginManager()
    manager.plugins_dir = str(plugins_dir)

    # Проверяем загрузку плагинов
    manager.discover_plugins()
    manager.load_plugin('Dependent')  # Должен автоматически загрузить Base

    assert 'Base' in manager._plugins
    assert 'Dependent' in manager._plugins

    # Проверяем что нельзя отключить Base пока активен Dependent
    with pytest.raises(PluginError):
        manager.disable_plugin('Base')

    # Но можно отключить после отключения Dependent
    manager.disable_plugin('Dependent')
    manager.disable_plugin('Base')
