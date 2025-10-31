import os
from pathlib import Path
from src.plugins import AegnuxPlugin, PluginEvent
from PySide6.QtWidgets import (
    QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QTabWidget
)
from PySide6.QtCore import Qt

class LicenseInfoPlugin(AegnuxPlugin):
    """
    Плагин для отображения информации о лицензиях и легальном использовании.
    """
    
    def __init__(self):
        super().__init__(
            name="License Info",
            version="1.0.0",
            description="Информация о лицензиях и правовые уведомления",
            author="Aegnux Team"
        )
        self.menu = None
        
    def on_load(self):
        """Инициализация при загрузке плагина"""
        self.log.info("Плагин License Info загружен")
        self._create_menu()
        
    def on_unload(self):
        """Очистка при выгрузке плагина"""
        if self.menu:
            self.menu.deleteLater()
        self.log.info("Плагин License Info выгружен")
        
    def _create_menu(self):
        """Создание пунктов меню"""
        self.menu = QMenu("Лицензии")
        
        info_action = QAction("Правовая информация...", self.menu)
        info_action.triggered.connect(self._show_info_dialog)
        
        license_action = QAction("Управление лицензиями...", self.menu)
        license_action.triggered.connect(self._show_license_dialog)
        
        self.menu.addAction(info_action)
        self.menu.addAction(license_action)
        
        self.add_menu(self.menu)
        
    def _show_info_dialog(self):
        """Показ диалога с правовой информацией"""
        dialog = QDialog()
        dialog.setWindowTitle("Правовая информация")
        dialog.resize(800, 600)
        layout = QVBoxLayout()
        
        # Вкладки с информацией
        tabs = QTabWidget()
        
        # Вкладка с общей информацией
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        general_text = QTextEdit()
        general_text.setReadOnly(True)
        general_text.setHtml("""
            <h2>Важное уведомление о легальном использовании</h2>
            
            <p>Aegnux является инструментом для тестирования и разработки программного обеспечения. 
            Программа предназначена исключительно для:</p>
            
            <ul>
                <li>Тестирования совместимости программного обеспечения</li>
                <li>Разработки и отладки приложений</li>
                <li>Образовательных целей</li>
                <li>Проверки работоспособности программ</li>
            </ul>
            
            <p><b>Важно понимать:</b></p>
            
            <ul>
                <li>Aegnux не предназначен для обхода технических средств защиты авторских прав</li>
                <li>При использовании программного обеспечения необходимо соблюдать условия его лицензирования</li>
                <li>Для коммерческого использования программ требуются соответствующие лицензии</li>
            </ul>
            
            <p>Разработчики Aegnux призывают:</p>
            
            <ul>
                <li>Уважать права правообладателей программного обеспечения</li>
                <li>Приобретать лицензионное программное обеспечение</li>
                <li>Использовать программы в соответствии с их лицензионными соглашениями</li>
            </ul>
            
            <p>Aegnux распространяется по лицензии MIT и включает компоненты, распространяемые 
            под различными свободными лицензиями.</p>
        """)
        
        general_layout.addWidget(general_text)
        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "Общая информация")
        
        # Вкладка с лицензиями компонентов
        components_tab = QWidget()
        components_layout = QVBoxLayout()
        
        components_text = QTextEdit()
        components_text.setReadOnly(True)
        components_text.setHtml("""
            <h2>Лицензии используемых компонентов</h2>
            
            <h3>Wine</h3>
            <p>Wine распространяется под лицензией LGPL. Подробнее: 
            <a href='https://www.winehq.org/license'>https://www.winehq.org/license</a></p>
            
            <h3>Winetricks</h3>
            <p>Winetricks распространяется под лицензией LGPL. Подробнее: 
            <a href='https://wiki.winehq.org/Winetricks'>https://wiki.winehq.org/Winetricks</a></p>
            
            <h3>DXVK</h3>
            <p>DXVK распространяется под лицензией zlib/libpng. Подробнее: 
            <a href='https://github.com/doitsujin/dxvk/blob/master/LICENSE'>GitHub - DXVK License</a></p>
            
            <h3>VKD3D</h3>
            <p>VKD3D распространяется под лицензией LGPL. Подробнее: 
            <a href='https://source.winehq.org/git/vkd3d.git/'>Source - VKD3D</a></p>
        """)
        
        components_layout.addWidget(components_text)
        components_tab.setLayout(components_layout)
        tabs.addTab(components_tab, "Компоненты")
        
        layout.addWidget(tabs)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def _show_license_dialog(self):
        """Показ диалога управления лицензиями"""
        dialog = QDialog()
        dialog.setWindowTitle("Управление лицензиями")
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Здесь вы можете указать лицензионные ключи для программ, "
            "которые вы тестируете. Это поможет соблюдать лицензионные соглашения."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Добавление лицензионного ключа
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Программа:"))
        key_layout.addWidget(QLineEdit())
        key_layout.addWidget(QLabel("Ключ:"))
        key_layout.addWidget(QLineEdit())
        key_layout.addWidget(QPushButton("Добавить"))
        layout.addLayout(key_layout)
        
        # Список сохраненных лицензий
        layout.addWidget(QLabel("Сохраненные лицензии:"))
        licenses_list = QListWidget()
        layout.addWidget(licenses_list)
        
        # Кнопки
        buttons = QHBoxLayout()
        buttons.addWidget(QPushButton("Экспорт"))
        buttons.addWidget(QPushButton("Импорт"))
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()