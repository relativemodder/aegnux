from src.processthread import ProcessThread

class KillAEThread(ProcessThread):
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            self.run_command(
                ['wineserver', '-k'],
                in_prefix=True
            )
        except Exception as e:
            self.log_signal.emit(f'[ERROR] {e}')

        self.finished_signal.emit(True)
