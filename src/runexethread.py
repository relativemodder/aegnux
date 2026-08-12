from src.processthread import ProcessThread
from src.utils import get_ae_install_dir

class RunExeThread(ProcessThread):
    def __init__(self, exe_args: list, use_portal: bool = False):
        super().__init__()
        self.exe_args = exe_args
        self.use_portal = use_portal
    
    def run(self):
        self.run_command(
            ['wine'] + self.exe_args, 
            cwd=get_ae_install_dir(),
            in_prefix=True,
            use_portal=self.use_portal
        )

        self.finished_signal.emit(True)
