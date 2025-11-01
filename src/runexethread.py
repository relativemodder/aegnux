from src.processthread import ProcessThread
from src.utils import get_ae_install_dir

class RunExeThread(ProcessThread):
    def __init__(self, exe_args: list):
        super().__init__()
        self.exe_args = exe_args
    
    def run(self):
        self.run_command(
            ['wine'] + self.exe_args, 
            cwd=get_ae_install_dir(),
            in_prefix=True
        )

        self.finished_signal.emit(True)