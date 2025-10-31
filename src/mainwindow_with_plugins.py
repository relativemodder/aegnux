"""Расширенная версия главного окна с поддержкой плагинов."""

from PySide6.QtWidgets import QMenu, QMenuBar, QToolBar
from PySide6.QtGui import QAction

from src.mainwindow import MainWindow as BaseMainWindow
from src.plugins import PluginManager
from src.dialogs.plugin_manager_dialog import PluginManagerDialog


class MainWindow(BaseMainWindow):
    """Расширенная версия главного окна с поддержкой плагинов."""

    def __init__(self):
        super().__init__()

        # Инициализация менеджера плагинов
        self.plugin_manager = PluginManager()
        self.plugin_manager.discover_plugins()

        # Создание меню
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Меню плагинов
        self.plugins_menu = QMenu("Плагины", self)
        self.menu_bar.addMenu(self.plugins_menu)

        # Действие для открытия менеджера плагинов
        manage_plugins_action = QAction("Управление плагинами", self)
        manage_plugins_action.triggered.connect(self.show_plugin_manager)
        self.plugins_menu.addAction(manage_plugins_action)
        self.plugins_menu.addSeparator()

        # Создание тулбара для плагинов
        self.plugins_toolbar = QToolBar("Плагины", self)
        self.addToolBar(self.plugins_toolbar)

        # Загрузка плагинов
        self._load_plugins()

    def _load_plugins(self):
        """Загружает все найденные плагины."""
        for plugin_class in self.plugin_manager._plugin_classes.values():
            try:
                plugin = plugin_class()
                self.plugin_manager._plugins[plugin.metadata.name] = plugin
                plugin.initialize()

                # Добавляем пункты меню от плагина
                for menu_text, menu_callback in plugin.get_menu_items():
                    action = QAction(menu_text, self)
                    action.triggered.connect(menu_callback)
                    self.plugins_menu.addAction(action)

                # Добавляем элементы тулбара от плагина
                for toolbar_text, toolbar_callback in plugin.get_toolbar_items():
                    action = QAction(toolbar_text, self)
                    action.triggered.connect(toolbar_callback)
                    self.plugins_toolbar.addAction(action)

            except Exception as e:
                print(f"Ошибка при загрузке плагина: {e}")

    def show_plugin_manager(self):
        """Показывает диалог управления плагинами."""
        dialog = PluginManagerDialog(self.plugin_manager, self)
        dialog.exec()
