"""Диалог управления плагинами."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton,
    QLabel, QWidget, QCheckBox
)
from PySide6.QtCore import Qt

from src.plugins import PluginManager, AegnuxPlugin


class PluginListItem(QListWidgetItem):
    """Элемент списка плагинов."""

    def __init__(self, plugin: AegnuxPlugin):
        super().__init__()
        self.plugin = plugin
        self.setText(plugin.metadata.name)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(
            Qt.CheckState.Checked if plugin.is_enabled
            else Qt.CheckState.Unchecked
        )


class PluginManagerDialog(QDialog):
    """Диалог для управления плагинами."""

    def __init__(self, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setup_ui()
        self.load_plugins()

    def setup_ui(self):
        """Настройка интерфейса."""
        self.setWindowTitle("Управление плагинами")
        self.resize(500, 400)

        layout = QVBoxLayout()

        # Список плагинов
        self.plugin_list = QListWidget()
        self.plugin_list.itemChanged.connect(self._on_plugin_state_changed)
        self.plugin_list.currentItemChanged.connect(self._on_plugin_selected)
        layout.addWidget(self.plugin_list)

        # Информация о плагине
        info_widget = QWidget()
        info_layout = QVBoxLayout()

        self.name_label = QLabel()
        info_layout.addWidget(self.name_label)

        self.version_label = QLabel()
        info_layout.addWidget(self.version_label)

        self.author_label = QLabel()
        info_layout.addWidget(self.author_label)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        info_layout.addWidget(self.description_label)

        info_widget.setLayout(info_layout)
        layout.addWidget(info_widget)

        # Кнопки
        button_layout = QHBoxLayout()

        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_plugins(self):
        """Загружает список плагинов."""
        self.plugin_list.clear()
        for plugin in self.plugin_manager.get_all_plugins():
            self.plugin_list.addItem(PluginListItem(plugin))

    def _on_plugin_state_changed(self, item: PluginListItem):
        """Обработка изменения состояния плагина."""
        plugin = item.plugin
        enabled = item.checkState() == Qt.CheckState.Checked

        if enabled:
            self.plugin_manager.enable_plugin(plugin.metadata.name)
        else:
            self.plugin_manager.disable_plugin(plugin.metadata.name)

    def _on_plugin_selected(
            self,
            current: PluginListItem,
            previous: PluginListItem):
        """Обработка выбора плагина в списке."""
        if not current:
            self._clear_plugin_info()
            return

        plugin = current.plugin
        meta = plugin.metadata

        self.name_label.setText(f"Название: {meta.name}")
        self.version_label.setText(f"Версия: {meta.version}")
        self.author_label.setText(f"Автор: {meta.author}")
        self.description_label.setText(f"Описание: {meta.description}")

    def _clear_plugin_info(self):
        """Очищает информацию о плагине."""
        self.name_label.setText("")
        self.version_label.setText("")
        self.author_label.setText("")
        self.description_label.setText("")
