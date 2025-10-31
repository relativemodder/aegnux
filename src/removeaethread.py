from src.processthread import ProcessThread
from src.utils import get_aegnux_installation_dir
import shutil


class RemoveAEThread(ProcessThread):
    def __init__(self):
        super().__init__()

    def run(self):
        shutil.rmtree(get_aegnux_installation_dir(), True)
        self.finished_signal.emit(True)
