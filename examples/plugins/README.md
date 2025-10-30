# Плагины для Aegnux

В этой директории находятся примеры плагинов для Aegnux. Вы можете использовать их как шаблоны для создания собственных плагинов.

## Структура плагина

Каждый плагин должен располагаться в отдельной директории и иметь как минимум следующие файлы:

```
my_plugin/
  └── plugin.py     # Основной файл плагина
```

## Создание плагина

1. Создайте новую директорию для вашего плагина в `~/.local/share/aegnux/plugins/`
2. Создайте файл `plugin.py`
3. Определите класс плагина, наследующий от `AegnuxPlugin`
4. Реализуйте необходимые методы

Пример простого плагина:

```python
from src.plugins import AegnuxPlugin, PluginMetadata, PluginEvent

class MyPlugin(AegnuxPlugin):
    def __init__(self):
        self.metadata = PluginMetadata(
            name="Мой плагин",
            version="1.0.0",
            author="Ваше имя",
            description="Описание плагина",
            # Если ваш плагин зависит от других:
            # dependencies=["other_plugin"]
        )
        super().__init__()

    def initialize(self):
        """Вызывается при загрузке плагина."""
        # Регистрация обработчиков событий
        self.register_event_handler(PluginEvent.BEFORE_AE_START, self.on_ae_start)
        
    def cleanup(self):
        """Вызывается при выгрузке плагина."""
        pass

    def get_menu_items(self):
        """Добавляет пункты в меню 'Плагины'."""
        return [
            ("Моё действие", self.my_action)
        ]

    def get_toolbar_items(self):
        """Добавляет кнопки на тулбар."""
        return [
            ("Быстрое действие", self.quick_action)
        ]

    # Обработчики событий
    def on_ae_start(self, event, *args, **kwargs):
        print("After Effects запускается!")

    # Действия плагина
    def my_action(self):
        """Вызывается при выборе пункта меню."""
        pass

    def quick_action(self):
        """Вызывается при нажатии кнопки на тулбаре."""
        pass
```

## События

Плагины могут реагировать на следующие события:

- `PluginEvent.BEFORE_AE_START` - перед запуском After Effects
- `PluginEvent.AFTER_AE_START` - после запуска After Effects
- `PluginEvent.BEFORE_AE_STOP` - перед остановкой After Effects
- `PluginEvent.AFTER_AE_STOP` - после остановки After Effects
- `PluginEvent.BEFORE_INSTALL` - перед установкой Aegnux
- `PluginEvent.AFTER_INSTALL` - после установки
- `PluginEvent.BEFORE_UNINSTALL` - перед удалением
- `PluginEvent.AFTER_UNINSTALL` - после удаления

Вы также можете создавать собственные события через `PluginEvent("my.event", payload={...})`.

## Рекомендации

1. Используйте русский язык для названий и описаний
2. Добавьте обработку ошибок в ваши обработчики событий
3. Проверяйте зависимости в `initialize()`
4. Освобождайте ресурсы в `cleanup()`
5. Не блокируйте UI длительными операциями