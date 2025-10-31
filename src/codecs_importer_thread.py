from PySide6.QtCore import QThread, Signal
from src import codecs_importer


class CodecsImportThread(QThread):
    """Фоновый поток для импортa кодеков. Эмитирует лог-сообщения и результат.

    Signals:
        log_signal(str) - лог сообщений
        finished_signal(dict) - статистика импорта
    """
    log_signal = Signal(str)
    finished_signal = Signal(dict)
    # прогресс: количество обработанных, общее количество
    progress_signal = Signal(int, int)

    def __init__(self, src_dir: str, overwrite: bool = None):
        super().__init__()
        self.src_dir = src_dir
        self.overwrite = overwrite

    def run(self):
        try:
            stats = codecs_importer.import_codecs(
                self.src_dir,
                overwrite=self.overwrite,
                logger=self.log_signal.emit,
                progress=lambda processed,
                total: self.progress_signal.emit(
                    processed,
                    total),
                should_stop=lambda: self.isInterruptionRequested(),
            )
            self.finished_signal.emit(stats)
        except Exception as e:
            # Логируем и возвращаем ошибку в result
            self.log_signal.emit(f"Import failed: {e}")
            self.finished_signal.emit(
                {'found': 0, 'copied': 0, 'skipped': 0, 'errors': 1})
