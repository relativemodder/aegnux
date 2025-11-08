from src.processthread import ProcessThread
from src.utils import get_ae_install_dir
from src.runexethread import RunExeThread

class RunAEThread(RunExeThread):
    def __init__(self):
        super().__init__(['AfterFX.exe'])
    
    def add_aep_file_arg(self, aep_file: str):
        self.exe_args.append('Z:' + aep_file)
    
    def clear_aep_file_arg(self):
        for arg in self.exe_args:
            if '.aep' in arg:
                self.exe_args.remove(arg)
    
    def run(self):
        super().run()