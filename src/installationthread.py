import os
from pathlib import Path
import shutil
import tarfile
import traceback
from src.config import (
    AE_DOWNLOAD_URL, AE_FILENAME, DXVK_REG, FONTSMOOTH_REG, 
    WINE_RUNNER_DIR, WINETRICKS_BIN, 
    CABEXTRACT_BIN, WINE_STYLE_REG,
    VCR_ZIP, MSXML_ZIP, GDIPLUS_DLL, DXVK_TAR
)
from src.processthread import ProcessThread
from src.utils import (
    DownloadMethod, get_aegnux_installation_dir, 
    get_ae_install_dir, get_wine_runner_dir, is_nvidia_present,
    get_winetricks_bin, get_wineprefix_dir, get_cabextract_bin,
    get_vcr_dir_path, get_msxml_dir_path, mark_aegnux_as_installed,
    get_cep_dir
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

            self.unpack_ae()
            
            self.progress_signal.emit(20)

            self.log_signal.emit(f'[DEBUG] Copying Wine Runner from {WINE_RUNNER_DIR}...')
            shutil.copytree(WINE_RUNNER_DIR, get_wine_runner_dir(), dirs_exist_ok=True)
            
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

            tweaks = ['corefonts']
            for tweak in tweaks:
                self.log_signal.emit(f'[DEBUG] Installing {tweak} with winetricks')
                self.run_command(['winetricks', '-q', tweak], in_prefix=True)
                self.progress_signal.emit(60 + tweaks.index(tweak) * 2)
            
            self.install_dxvk()
            
            self.progress_signal.emit(70)

            self.install_vcr()
            
            self.progress_signal.emit(85)

            self.install_msxml3()

            self.install_gdiplus()

            self.log_signal.emit(f'[DEBUG] Applying fontsmooth settings')
            self.run_command(
                ['wine', 'regedit', FONTSMOOTH_REG], 
                in_prefix=True
            )

            if is_nvidia_present():
                self.log_signal.emit("[INFO] Starting NVIDIA libs installation...")
                self.install_nvidia_libs()
            
            try:
                self.log_signal.emit(f"[INFO] Created CEP directory in {get_cep_dir()}")
            except:
                pass
            
            self.progress_signal.emit(99)

            self.cleanup()

            mark_aegnux_as_installed()
            
            self.progress_signal.emit(100)
            
            self.finished_signal.emit(True)
        except Exception as e:
            traceback.print_exc()
            self.log_signal.emit(f'[ERROR] {e}')
            self.finished_signal.emit(False)
    
    def install_vcr(self):
        self.log_signal.emit(f'[DEBUG] Unpacking VCR to {get_vcr_dir_path()}...')
        self.unpack_zip(VCR_ZIP, get_vcr_dir_path().as_posix())
        
        self.progress_signal.emit(80)

        self.log_signal.emit(f'[DEBUG] Installing VCR')
        self.run_command(['wine', get_vcr_dir_path().joinpath('install_all.bat').as_posix()], in_prefix=True)
    
    def install_msxml3(self):
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
    
    def install_gdiplus(self):
        system32_dir = get_wineprefix_dir().joinpath('drive_c/windows/system32')
        self.log_signal.emit(f'[DEBUG] Overriding gdiplus DLL...')
        shutil.copy(GDIPLUS_DLL, system32_dir.joinpath('gdiplus.dll'))

        self.run_command(
            ['wine', 'reg', 'add', 
             'HKCU\\Software\\Wine\\DllOverrides', '/v', 
             'gdiplus', '/d', 'native,builtin', '/f'], 
            in_prefix=True
        )
    
    def get_tar_root_dir_name(self, tar_path) -> str | None:
        with tarfile.open(tar_path, 'r') as tar:
            member_names = tar.getnames()
            if not member_names:
                return None
            
            first_member = member_names[0]
            root_name = first_member.split(os.path.sep)[0]

            return root_name

    def install_dxvk(self):
        system32_dir = get_wineprefix_dir().joinpath('drive_c/windows/system32')
        syswow64_dir = get_wineprefix_dir().joinpath('drive_c/windows/syswow64')
        self.unpack_tar(DXVK_TAR, get_wineprefix_dir())

        dxvk_name = self.get_tar_root_dir_name(DXVK_TAR)
        dxvk_root_dir = get_wineprefix_dir().joinpath(dxvk_name)

        self.log_signal.emit(f'[DEBUG] DXVK root dir is {dxvk_root_dir}')

        source_x64 = dxvk_root_dir.joinpath('x64')
        source_x32 = dxvk_root_dir.joinpath('x32')

        for source in [source_x64, source_x32]:
            for item in source.iterdir():
                system_dir = system32_dir if 'x64' in source.as_posix() else syswow64_dir

                if item.is_file():
                    shutil.copy2(item, system_dir.joinpath(item.name))
                elif item.is_dir():
                    dest = system_dir.joinpath(item.name)
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)

        self.log_signal.emit(f'[DEBUG] Overriding DXVK dlls')
        self.run_command(
            ['wine', 'regedit', DXVK_REG], 
            in_prefix=True
        )
    
    def unpack_ae(self):
        self.log_signal.emit(f'[DEBUG] Unpacking AE from {self.ae_filename}...')
        aegnux_install_dir = get_aegnux_installation_dir()
        self.unpack_zip(self.ae_filename, aegnux_install_dir.as_posix())

        root_path = Path(aegnux_install_dir)
        target_dir = Path(get_ae_install_dir())
        source_folder_to_delete = None

        self.log_signal.emit('[DEBUG] Searching for AfterFX.exe...')

        for exe_path in root_path.rglob('AfterFX.exe'):
            source_dir_to_move = exe_path.parent
            self.log_signal.emit(f'[DEBUG] Found installation folder: {source_dir_to_move}')
            for item in source_dir_to_move.iterdir():
                shutil.move(item.as_posix(), target_dir.joinpath(item.name).as_posix())
            self.log_signal.emit(f'[DEBUG] All contents moved to {target_dir}')
            source_folder_to_delete = source_dir_to_move.parent
            break

        if source_folder_to_delete and source_folder_to_delete != root_path:
            self.log_signal.emit(f'[DEBUG] Removing temporary folder: {source_folder_to_delete}')
            try:
                shutil.rmtree(source_folder_to_delete.as_posix())
                self.log_signal.emit('[DEBUG] Temporary folder removed successfully.')
            except OSError as e:
                self.log_signal.emit(f'[ERROR] Failed to remove temporary folder {source_folder_to_delete}: {e}')
        else:
            self.log_signal.emit('[WARNING] Installation folder not found or matched root path. No folder was deleted.')

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
            