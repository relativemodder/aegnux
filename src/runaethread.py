from src.processthread import ProcessThread
from src.utils import get_ae_install_dir

class RunAEThread(ProcessThread):
    def __init__(self):
        super().__init__()
    
    def run(self):
        self.run_command(
            ['wine', 'AfterFX.exe'], 
            cwd=get_ae_install_dir(),
            in_prefix=True
        )

        self.finished_signal.emit(True)