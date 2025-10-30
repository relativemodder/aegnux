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
    
    def init_installation(self):
        if check_aegnux_installed():
            self.install_button.hide()
            self.run_button.show()
            self.kill_button.show()
            self.remove_aegnux_button.show()

            self.plugins_button.show()
            self.wineprefix_button.show()
        else:
            self.install_button.show()
            self.run_button.hide()
            self.kill_button.hide()
            self.remove_aegnux_button.hide()

            self.plugins_button.hide()
            self.wineprefix_button.hide()

    def _construct_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
    
        self.root_layout = QVBoxLayout(central_widget)

        self.add_expanding_vertical_sizer()

        logo_label = QLabel()
        logo_pixmap = QPixmap(AE_ICON_PATH)

        scaled_pixmap = logo_pixmap.scaled(
            64,                                     # Ширина
            64,                                     # Высота
            Qt.AspectRatioMode.KeepAspectRatio,     # Сохранять соотношение сторон
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

        folders_row = QHBoxLayout()
        self.plugins_button = QPushButton(gls('plugins'))
        self.plugins_button.setIcon(QIcon.fromTheme('document-open-folder'))
        self.plugins_button.setIconSize(QSize(25, 15))
        self.plugins_button.setObjectName('plugins_button')

        self.import_codecs_button = QPushButton(gls('import_codecs') if hasattr(gls, '__call__') else 'Import Codecs')
        self.import_codecs_button.setIcon(QIcon.fromTheme('folder-download'))
        self.import_codecs_button.setIconSize(QSize(25, 15))
        self.import_codecs_button.setObjectName('import_codecs_button')

        # cancel import button (hidden until an import is running)
        self.cancel_import_button = QPushButton(gls('cancel_import') if hasattr(gls, '__call__') else 'Cancel Import')
        self.cancel_import_button.setIcon(QIcon.fromTheme('process-stop'))
        self.cancel_import_button.setIconSize(QSize(25, 15))
        self.cancel_import_button.setObjectName('cancel_import_button')
        self.cancel_import_button.hide()

        self.wineprefix_button = QPushButton(gls('wineprefix'))
        self.wineprefix_button.setIcon(QIcon.fromTheme('document-open-folder'))
        self.wineprefix_button.setIconSize(QSize(25, 15))
        self.wineprefix_button.setObjectName('wineprefix_button')

        self.toggle_logs_button = QPushButton(gls('toggle_logs'))
        self.toggle_logs_button.setIcon(QIcon.fromTheme('view-list-text'))
        self.toggle_logs_button.setIconSize(QSize(25, 15))
        self.toggle_logs_button.setObjectName('toggle_logs_button')
        self.toggle_logs_button.setVisible(False)
        action_col.addWidget(self.toggle_logs_button)

        folders_row.addWidget(self.plugins_button)
        folders_row.addWidget(self.import_codecs_button)
        folders_row.addWidget(self.cancel_import_button)
        folders_row.addWidget(self.wineprefix_button)

        action_col.addLayout(folders_row)

        destruction_row = QHBoxLayout()

        self.kill_button = QPushButton(gls('kill_ae'))
        self.kill_button.setObjectName('kill_ae')
        destruction_row.addWidget(self.kill_button)
        self.kill_button.hide()


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