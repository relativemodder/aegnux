"""Базовый класс и типы для системы плагинов."""

from typing import List, Tuple, Callable, Optional, Dict, Union
from dataclasses import dataclass, field
from enum import Enum, auto


@dataclass
class PluginMetadata:
    """Метаданные плагина."""
    name: str
    version: str
    author: str
    description: str
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)


class PluginEvent:
    """Класс события, который служит и контейнером-константой и фабрикой.

    У этого класса есть класс-атрибуты для распространённых событий
    (например, `PluginEvent.BEFORE_AE_START`) — они содержат объект с
    полем `name`. Одновременно сам класс может быть вызван как конструктор
    для создания экземпляра события: `PluginEvent(name, payload=...)`.
    Это обеспечивает обратную совместимость с существующими тестами и
    плагинами.
    """

    class _Const:
        def __init__(self, name: str):
            self.name = name

        def __repr__(self):
            return f"<PluginEventConst {self.name}>"

    # Стандартные имена событий (часто используемые)
    BEFORE_AE_START = _Const('BEFORE_AE_START')
    AFTER_AE_START = _Const('AFTER_AE_START')
    BEFORE_AE_STOP = _Const('BEFORE_AE_STOP')
    AFTER_AE_STOP = _Const('AFTER_AE_STOP')
    BEFORE_INSTALL = _Const('BEFORE_INSTALL')
    AFTER_INSTALL = _Const('AFTER_INSTALL')
    BEFORE_UNINSTALL = _Const('BEFORE_UNINSTALL')
    AFTER_UNINSTALL = _Const('AFTER_UNINSTALL')

    def __init__(self, name: str, payload: Optional[dict] = None):
        self.name = name
        self.payload = payload

    def __repr__(self):
        return f"<PluginEvent name={self.name} payload={self.payload!r}>"


class AegnuxPlugin:
    """Базовый класс для всех плагинов Aegnux.

    Плагин может регистрировать внутренние обработчики событий через
    метод `register_event_handler` и реализовать `handle_event` для
    кастомной обработки событий, либо полагаться на встроенную систему
    обработчиков.
    """

    metadata: PluginMetadata

    def __init__(self) -> None:
        if not hasattr(self, 'metadata'):
            raise ValueError("Плагин должен определить metadata")
        # internal event handlers: event_name -> list(callable)
        self._event_handlers: Dict[str, List[Callable]] = {}

    def initialize(self) -> None:
        """Вызывается при загрузке плагина."""
        pass

    def cleanup(self) -> None:
        """Вызывается при выгрузке плагина."""
        pass

    def get_menu_items(self) -> List[Tuple[str, Callable]]:
        """Возвращает список пунктов меню плагина.

        Returns:
            List[Tuple[str, Callable]]: Список кортежей (название_пункта, функция)
        """
        return []

    def get_toolbar_items(self) -> List[Tuple[str, Callable]]:
        """Возвращает список элементов тулбара.

        Returns:
            List[Tuple[str, Callable]]: Список кортежей (название_кнопки, функция)
        """
        return []

    @property
    def is_enabled(self) -> bool:
        """Включен ли плагин."""
        return self.metadata.enabled

    @is_enabled.setter
    def is_enabled(self, value: bool) -> None:
        """Установить состояние плагина."""
        self.metadata.enabled = value

    # --- event helpers ---
    def register_event_handler(
            self, event_name: Union[str, object], handler: Callable) -> None:
        """Регистрирует обработчик события локально в плагине.

        Обычно менеджер просто вызывает `plugin.handle_event` и плагин
        сам распределяет вызов среди зарегистрированных обработчиков.
        """
        key = event_name.name if not isinstance(
            event_name, str) else event_name
        if key not in self._event_handlers:
            self._event_handlers[key] = []
        self._event_handlers[key].append(handler)

    def unregister_event_handler(
            self, event_name: Union[str, object], handler: Callable) -> None:
        """Удаляет ранее зарегистрированный обработчик."""
        key = event_name.name if not isinstance(
            event_name, str) else event_name
        if key in self._event_handlers:
            try:
                self._event_handlers[key].remove(handler)
            except ValueError:
                pass

    def handle_event(self,
                     event: Union[PluginEvent,
                                  object,
                                  str],
                     *args,
                     **kwargs) -> None:
        """Вызывает обработчики для входящего события.

        По умолчанию ищем зарегистрированные обработчики по имени события.
        Плагин может переопределить этот метод для собственной логики.
        """
        if not self.is_enabled:
            return
        key = None
        if isinstance(event, PluginEvent):
            key = event.name
        elif isinstance(event, str):
            key = event
        else:
            # enum
            key = event.name
        handlers = self._event_handlers.get(key, [])
        for h in handlers:
            try:
                h(event, *args, **kwargs)
            except Exception as e:
                # Здесь просто печатаем, менеджер тоже логирует ошибки
                print(
                    f"Ошибка в обработчике события {
                        event.name} плагина {
                        self.metadata.name}: {e}")
