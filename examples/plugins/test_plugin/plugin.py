"""Пример простого плагина для Aegnux."""

from src.plugins import AegnuxPlugin, PluginMetadata


class TestPlugin(AegnuxPlugin):
    """Тестовый плагин, демонстрирующий базовый функционал."""

    def __init__(self):
        self.metadata = PluginMetadata(
            name="Тестовый плагин",
            version="1.0.0",
            author="Aegnux Team",
            description="Демонстрационный плагин для примера"
        )
        super().__init__()

    def initialize(self) -> None:
        """Инициализация плагина."""
        print("Тестовый плагин инициализирован")

    def cleanup(self) -> None:
        """Очистка ресурсов плагина."""
        print("Тестовый плагин выгружен")

    def get_menu_items(self):
        """Добавляет пункт в меню."""
        return [
            ("Тестовое действие", self.test_action)
        ]

    def test_action(self):
        """Тестовое действие плагина."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(None, "Тестовый плагин", "Тестовое действие выполнено!")