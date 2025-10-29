import os
import shutil
from src.config import (
    AE_DOWNLOAD_URL, AE_FILENAME, 
    WINE_RUNNER_TAR, WINETRICKS_BIN, 
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
            self.progress_signal.emit(10)

            if self.download_method == DownloadMethod.ONLINE:
                self.download_file_to(AE_DOWNLOAD_URL, AE_FILENAME)
                self.ae_filename = AE_FILENAME
            
            self.progress_signal.emit(15)

            self.log_signal.emit(f'[DEBUG] Unpacking AE from {self.ae_filename}...')
            self.unpack_zip(self.ae_filename, get_aegnux_installation_dir().as_posix())
            os.rename(get_aegnux_installation_dir().joinpath('Support Files'), get_ae_install_dir())
            
            self.progress_signal.emit(20)

            self.log_signal.emit(f'[DEBUG] Unpacking Wine Runner from {WINE_RUNNER_TAR}...')
            self.unpack_tar(WINE_RUNNER_TAR, get_wine_runner_dir().as_posix())
            
            self.progress_signal.emit(30)

            self.log_signal.emit(f'[DEBUG] Copying winetricks to {get_winetricks_bin()}...')
            shutil.copy(WINETRICKS_BIN, get_winetricks_bin())
            
            self.progress_signal.emit(35)

            self.log_signal.emit(f'[DEBUG] Copying cabextract to {get_cabextract_bin()}...')
            shutil.copy(CABEXTRACT_BIN, get_cabextract_bin())
            
            self.progress_signal.emit(40)

            self.log_signal.emit(f'[DEBUG] Initializing wineprefix in {get_wineprefix_dir()}...')
            self.run_command(['wineboot'], in_prefix=True)
            
            self.progress_signal.emit(50)

            self.log_signal.emit(f'[DEBUG] Tweaking visual settings in prefix')
            self.run_command(['wine', 'regedit', WINE_STYLE_REG], in_prefix=True)
            
            self.progress_signal.emit(55)

            self.log_signal.emit(f'[DEBUG] [WORKAROUND] Killing wineserver')
            self.run_command(['wineserver', '-k'], in_prefix=True)
            
            self.progress_signal.emit(60)

            tweaks = ['dxvk', 'corefonts', 'gdiplus', 'fontsmooth=rgb']
            for tweak in tweaks:
                self.log_signal.emit(f'[DEBUG] Installing {tweak} with winetricks')
                self.run_command(['winetricks', '-q', tweak], in_prefix=True)
                self.progress_signal.emit(60 + tweaks.index(tweak) * 2)
            
            self.progress_signal.emit(70)

            self.log_signal.emit(f'[DEBUG] Unpacking VCR to {get_vcr_dir_path()}...')
            self.unpack_zip(VCR_ZIP, get_vcr_dir_path().as_posix())
            
            self.progress_signal.emit(80)

            self.log_signal.emit(f'[DEBUG] Installing VCR')
            self.run_command(['wine', get_vcr_dir_path().joinpath('install_all.bat').as_posix()], in_prefix=True)
            
            self.progress_signal.emit(85)

            self.log_signal.emit(f'[DEBUG] Unpacking MSXML3 to {get_msxml_dir_path()}...')
            self.unpack_zip(MSXML_ZIP, get_msxml_dir_path().as_posix())
            
            self.progress_signal.emit(90)

            self.log_signal.emit(f'[DEBUG] Overriding MSXML3 DLL...')
            system32_dir = get_wineprefix_dir().joinpath('drive_c/windows/system32')
            shutil.copy(get_msxml_dir_path().joinpath('msxml3.dll'), system32_dir.joinpath('msxml3.dll'))
            shutil.copy(get_msxml_dir_path().joinpath('msxml3r.dll'), system32_dir.joinpath('msxml3r.dll'))

            self.run_command(
                ['wine', 'reg', 'add', 
                 'HKCU\\Software\\Wine\\DllOverrides', '/v', 
                 'msxml3', '/d', 'native,builtin', '/f'], 
                in_prefix=True
            )

            if is_nvidia_present():
                self.log_signal.emit("[INFO] Starting NVIDIA libs installation...")
                self.install_nvidia_libs()
            
            self.progress_signal.emit(99)

            self.cleanup()

            mark_aegnux_as_installed()
            
            self.progress_signal.emit(100)
            
            self.finished_signal.emit(True)
        except Exception as e:
            self.log_signal.emit(f'[ERROR] {e}')
            self.finished_signal.emit(False)

    def install_nvidia_libs(self):
        download_url = "https://github.com/SveSop/nvidia-libs/releases/download/v0.8.5/nvidia-libs-v0.8.5.tar.xz"
        nvidia_libs_dir = get_wineprefix_dir().joinpath("nvidia-libs")
        os.makedirs(nvidia_libs_dir, exist_ok=True)
        tar_file = nvidia_libs_dir.joinpath("nvidia-libs-v0.8.5.tar.xz")

        self.download_file_to(download_url, tar_file)
        self.log_signal.emit("[DEBUG] Download completed.")
        self.log_signal.emit("[DEBUG] Extracting NVIDIA libs...")

        extract_dir = nvidia_libs_dir.joinpath("nvidia-libs-v0.8.5")

        self.unpack_tar(tar_file, nvidia_libs_dir)

        self.log_signal.emit("[DEBUG] Extraction completed.")

        os.remove(tar_file)

        self.log_signal.emit("[DEBUG] Running setup script...")

        setup_script = extract_dir.joinpath("setup_nvlibs.sh")

        self.log_signal.emit(f"[DEBUG] Running: {setup_script} install")

        returncode = self.run_command([setup_script.as_posix(), 'install'], in_prefix=True)

        if returncode != 0:
            self.log_signal.emit(f"[ERROR] Setup script failed with return code {returncode}.")
            self.finished_signal.emit(False)
            return
        
        self.log_signal.emit("[INFO] NVIDIA libs installation completed!")
            