"""Тесты событийной системы плагинов."""

from src.plugins import PluginManager, PluginEvent, AegnuxPlugin, PluginMetadata


def test_plugin_event_handling(tmp_path):
    # Создаем простую структуру плагина
    plugin_dir = tmp_path / 'plugins' / 'evt_plugin'
    plugin_dir.mkdir(parents=True)
    (plugin_dir / 'plugin.py').write_text('''
from src.plugins import AegnuxPlugin, PluginMetadata, PluginEvent

class EvtPlugin(AegnuxPlugin):
    def __init__(self):
        self.metadata = PluginMetadata(
            name='EvtPlugin',
            version='0.1',
            author='Test',
            description='Event test plugin'
        )
        super().__init__()
        self.called = False

    def initialize(self):
        # регистрируем обработчик события 'test.event'
        def handler(event, *args, **kwargs):
            # сохраняем флаг в экземпляре плагина
            self.called = True
            self._last_payload = event.payload
        self.register_event_handler('test.event', handler)
''')

    manager = PluginManager()
    manager.plugins_dir = str(tmp_path / 'plugins')

    manager.discover_plugins()
    # загружаем плагин
    key = next(iter(manager._plugin_classes.keys()))
    manager.load_plugin(key)

    # отправляем событие
    evt = PluginEvent(name='test.event', payload={'x': 1})
    manager.emit_event(evt)

    # получаем плагин и проверяем флаг
    plugin = manager.get_plugin('EvtPlugin')
    assert plugin is not None
    assert getattr(plugin, 'called', False) is True
    assert getattr(plugin, '_last_payload', None) == {'x': 1}
