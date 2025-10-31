import os
from pathlib import Path
import shutil
from src.config import (
    AE_DOWNLOAD_URL, AE_FILENAME,
    WINE_RUNNER_DIR, WINETRICKS_BIN,
    CABEXTRACT_BIN, WINE_STYLE_REG,
    VCR_ZIP, MSXML_ZIP
)
from src.processthread import ProcessThread
from src.utils import (
    DownloadMethod, get_aegnux_installation_dir,
    get_ae_install_dir, get_wine_runner_dir, is_nvidia_present,
    get_winetricks_bin, get_wineprefix_dir, get_cabextract_bin,
    get_vcr_dir_path, get_msxml_dir_path, mark_aegnux_as_installed
)


class InstallationThread(ProcessThread):
    def __init__(self):
        super().__init__()

    def set_download_method(self, method: DownloadMethod):
        self.download_method = method

    def set_offline_filename(self, filename: str):
        self.ae_filename = filename

    def cleanup(self):
        self.log_signal.emit(f'[CLEANUP] Removing temporary AE .zip file')
        if self.download_method == DownloadMethod.ONLINE:
            os.remove(AE_FILENAME)

    def run(self):
        try:
            try:
                shutil.rmtree(get_aegnux_installation_dir(), True)
            except:
                self.log_signal.emit(f'[WARNING] Can\'t remove existing installation.')

            self.progress_signal.emit(10)

            if self.download_method == DownloadMethod.ONLINE:
                self.download_file_to(AE_DOWNLOAD_URL, AE_FILENAME)
                self.ae_filename = AE_FILENAME

            self.progress_signal.emit(15)


