from src.processthread import ProcessThread
from src.utils import get_ae_install_dir
from src.runexethread import RunExeThread

class RunAEThread(RunExeThread):
    def __init__(self):
        super().__init__(['AfterFX.exe'])
    
    def run(self):
        super().run()