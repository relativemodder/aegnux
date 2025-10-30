from tests.test_plugins import create_plugin
from src.plugins import PluginManager, PluginEvent


def test_plugin_events(tmp_path):
    """Тест системы событий плагинов."""
    plugins_dir = tmp_path / 'plugins'

    # Создаем два плагина
    create_plugin(plugins_dir, 'First')
    create_plugin(plugins_dir, 'Second')

    # Настраиваем менеджер плагинов
    manager = PluginManager()
    manager.plugins_dir = str(plugins_dir)

    # Загружаем плагины
    manager.discover_plugins()
    manager.load_plugin('First')
    manager.load_plugin('Second')

    # Проверяем что обработчики событий еще не вызывались
    first_plugin = manager.get_plugin('First')
    second_plugin = manager.get_plugin('Second')
    assert not first_plugin.event_received
    assert not second_plugin.event_received

    # Отправляем событие
    manager.emit_event(PluginEvent.BEFORE_AE_START)

    # Проверяем что обработчики были вызваны
    assert first_plugin.event_received
    assert second_plugin.event_received

    # Проверяем что отключенный плагин не получает события
    first_plugin.event_received = False
    second_plugin.event_received = False
    manager.disable_plugin('Second')

    manager.emit_event(PluginEvent.BEFORE_AE_START)
    assert first_plugin.event_received  # активный плагин получил событие
    assert not second_plugin.event_received  # отключенный плагин не получил
