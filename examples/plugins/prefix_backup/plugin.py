import os
import shutil
from datetime import datetime
from pathlib import Path
from src.plugins import AegnuxPlugin, PluginEvent
from PySide6.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox

class PrefixBackupPlugin(AegnuxPlugin):
    """
    Плагин для создания и восстановления резервных копий префиксов Wine.
    """
    
    def __init__(self):
        super().__init__(
            name="Prefix Backup",
            version="1.0.0",
            description="Создание и восстановление резервных копий префиксов Wine",
            author="Aegnux Team"
        )
        self.backup_dir = Path.home() / ".aegnux" / "backups"
        self.menu = None
        self.backup_action = None
        self.restore_action = None

    def on_load(self):
        """Инициализация при загрузке плагина"""
        self.log.info("Плагин Prefix Backup загружен")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._create_menu()

    def on_unload(self):
        """Очистка при выгрузке плагина"""
        if self.menu:
            self.menu.deleteLater()
        self.log.info("Плагин Prefix Backup выгружен")

    def _create_menu(self):
        """Создание пунктов меню плагина"""
        self.menu = QMenu("Резервные копии")
        
        self.backup_action = QAction("Создать резервную копию...", self.menu)
        self.backup_action.triggered.connect(self._backup_prefix)
        
        self.restore_action = QAction("Восстановить из копии...", self.menu)
        self.restore_action.triggered.connect(self._restore_prefix)
        
        self.menu.addAction(self.backup_action)
        self.menu.addAction(self.restore_action)
        
        # Добавляем меню в основное окно
        self.add_menu(self.menu)

    def _backup_prefix(self):
        """Создание резервной копии префикса"""
        prefix_dir = QFileDialog.getExistingDirectory(
            None,
            "Выберите префикс для резервного копирования",
            str(Path.home())
        )
        
        if not prefix_dir:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix_name = os.path.basename(prefix_dir)
            backup_path = self.backup_dir / f"{prefix_name}_{timestamp}"
            
            shutil.copytree(prefix_dir, backup_path)
            
            QMessageBox.information(
                None,
                "Успешно",
                f"Резервная копия создана в:\n{backup_path}"
            )
            
            self.log.info(f"Создана резервная копия префикса {prefix_dir}")
            
        except Exception as e:
            self.log.error(f"Ошибка при создании резервной копии: {e}")
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Не удалось создать резервную копию:\n{str(e)}"
            )

    def _restore_prefix(self):
        """Восстановление префикса из резервной копии"""
        backup_path = QFileDialog.getExistingDirectory(
            None,
            "Выберите резервную копию для восстановления",
            str(self.backup_dir)
        )
        
        if not backup_path:
            return
            
        target_dir = QFileDialog.getExistingDirectory(
            None,
            "Выберите место для восстановления",
            str(Path.home())
        )
        
        if not target_dir:
            return
            
        try:
            shutil.copytree(backup_path, target_dir, dirs_exist_ok=True)
            
            QMessageBox.information(
                None,
                "Успешно",
                f"Префикс восстановлен в:\n{target_dir}"
            )
            
            self.log.info(f"Префикс восстановлен из {backup_path} в {target_dir}")
            
        except Exception as e:
            self.log.error(f"Ошибка при восстановлении префикса: {e}")
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Не удалось восстановить префикс:\n{str(e)}"
            )