from PySide6.QtWidgets import (
    QVBoxLayout, QWidget,
    QLabel, QMainWindow, QPushButton,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from translations import gls
from src.config import AE_ICON_PATH, STYLES_PATH

class MainWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self._construct_ui()
        self._set_styles()
        self.setMinimumSize(480, 600)
    
    def _set_styles(self):
        with open(f'{STYLES_PATH}/mainwindow.css') as fp:
            self.setStyleSheet(fp.read())
    
    def add_expanding_vertical_sizer(self):
        self.root_layout.addItem(
            QSpacerItem(1, 2, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        )

    def _construct_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
    
        self.root_layout = QVBoxLayout(central_widget)

        self.add_expanding_vertical_sizer()

        logo_label = QLabel()
        logo_pixmap = QPixmap(AE_ICON_PATH)

        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.root_layout.addWidget(logo_label)

        title_label = QLabel(gls('welcome_to_aegnux'))
        title_label.setObjectName('title_label')
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.root_layout.addWidget(title_label)

        
        subtitle_label = QLabel(gls('subtitle_text'))
        subtitle_label.setObjectName('subtitle_label')
        subtitle_label.setWordWrap(True)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.root_layout.addWidget(subtitle_label)


        self.install_button = QPushButton(gls('install'))
        self.install_button.setIcon(QIcon.fromTheme('install-symbolic'))
        self.install_button.setIconSize(QSize(35, 20))
        self.install_button.setObjectName('install_button')
        self.root_layout.addWidget(self.install_button)


        self.add_expanding_vertical_sizer()

        
        footer_label = QLabel(gls('footer_text'))
        footer_label.setObjectName('footer_label')
        footer_label.setWordWrap(True)
        footer_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.root_layout.addWidget(footer_label)