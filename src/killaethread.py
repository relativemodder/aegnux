from src.processthread import ProcessThread

class KillAEThread(ProcessThread):
    def __init__(self):
        super().__init__()
    
    def run(self):
        self.run_command(
            ['wineserver', '-k'], 
            in_prefix=True
        )

        self.finished_signal.emit(True)