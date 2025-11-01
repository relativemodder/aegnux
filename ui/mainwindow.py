from PySide6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout,
    QLabel, QMainWindow, QPushButton, QMessageBox,
    QSpacerItem, QSizePolicy, QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from translations import gls
from src.config import AE_ICON_PATH, STYLES_PATH
from src.utils import check_aegnux_installed

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

    def add_fixed_vertical_sizer(self, height: int):
        self.root_layout.addItem(
            QSpacerItem(1, height, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )

    def _construct_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
    
        self.root_layout = QVBoxLayout(central_widget)

        self.add_expanding_vertical_sizer()

        logo_label = QLabel()
        logo_pixmap = QPixmap(AE_ICON_PATH)

        scaled_pixmap = logo_pixmap.scaled(
            64,                                
            64,                                
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        logo_label.setPixmap(scaled_pixmap)
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

        self.add_fixed_vertical_sizer(30)

        action_row = QHBoxLayout()
        action_col = QVBoxLayout()

        self.install_button = QPushButton(gls('install'))
        self.install_button.setIcon(QIcon.fromTheme('install-symbolic'))
        self.install_button.setIconSize(QSize(25, 15))
        self.install_button.setObjectName('install_button')
        self.install_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        action_col.addWidget(self.install_button)


        self.run_button = QPushButton(gls('run_ae'))
        self.run_button.setIcon(QIcon.fromTheme('media-playback-start'))
        self.run_button.setIconSize(QSize(25, 15))
        self.run_button.setObjectName('run_ae')
        action_col.addWidget(self.run_button)
        self.run_button.hide()

        destruction_row = QHBoxLayout()

        self.remove_aegnux_button = QPushButton(gls('remove_aegnux'))
        self.remove_aegnux_button.setObjectName('remove_aegnux_button')
        destruction_row.addWidget(self.remove_aegnux_button)
        self.remove_aegnux_button.hide()

        action_col.addLayout(destruction_row)


        self.logs_edit = QTextEdit()
        self.logs_edit.setObjectName('logs_edit')
        self.logs_edit.setFixedHeight(140)
        self.logs_edit.setReadOnly(True)
        self.logs_edit.hide()
        action_col.addWidget(self.logs_edit)

        self.progress_bar = QProgressBar(minimum=0, maximum=100, value=0)
        self.progress_bar.hide()
        action_col.addWidget(self.progress_bar)

        action_row.addItem(QSpacerItem(50, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        action_row.addLayout(action_col)
        action_row.addItem(QSpacerItem(50, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

        self.root_layout.addLayout(action_row)

        self.add_expanding_vertical_sizer()

        
        footer_label = QLabel(gls('footer_text'))
        footer_label.setObjectName('footer_label')
        footer_label.setWordWrap(True)
        footer_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.root_layout.addWidget(footer_label)
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, gls('confirm_exit'),
            gls('confirm_exit_text'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()