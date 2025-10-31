from src.plugins import AegnuxPlugin, PluginEvent

class ExamplePlugin(AegnuxPlugin):
    """
    Пример простого плагина для Aegnux.
    """
    
    def __init__(self):
        """
        Инициализация плагина
        """
        super().__init__(
            name="Example Plugin",
            version="1.0.0",
            description="Демонстрационный плагин для Aegnux",
            author="Your Name"
        )

    def on_load(self):
        """
        Вызывается при загрузке плагина
        """
        self.log.info("Плагин Example загружен!")
        
    def on_unload(self):
        """
        Вызывается при выгрузке плагина
        """
        self.log.info("Плагин Example выгружен!")

    def on_wine_start(self, event: PluginEvent):
        """
        Обработчик события запуска Wine
        """
        self.log.info(f"Wine запущен! Данные события: {event.data}")

    def on_wine_stop(self, event: PluginEvent):
        """
        Обработчик события остановки Wine
        """
        self.log.info(f"Wine остановлен! Данные события: {event.data}")

    def on_prefix_create(self, event: PluginEvent):
        """
        Обработчик события создания нового префикса Wine
        """
        prefix_path = event.data.get("prefix_path")
        self.log.info(f"Создан новый префикс Wine: {prefix_path}")