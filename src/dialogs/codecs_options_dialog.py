from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QDialogButtonBox
from translations import gls


class CodecsOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(gls('confirm_overwrite'))
        self.resize(420, 120)

        layout = QVBoxLayout(self)

        label = QLabel(gls('overwrite_prompt'))
        layout.addWidget(label)

        self.cb_remember = QCheckBox(gls('remember_choice'))
        layout.addWidget(self.cb_remember)

        self.cb_install_prefix = QCheckBox(gls('install_to_prefix'))
        layout.addWidget(self.cb_install_prefix)

        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def exec_options(self):
        res = self.exec()
        overwrite = res == QDialog.Accepted
        remember = self.cb_remember.isChecked()
        install_prefix = self.cb_install_prefix.isChecked()
        return overwrite, remember, install_prefix
