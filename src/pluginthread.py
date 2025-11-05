import os
import shutil
from src.processthread import ProcessThread
from src.utils import get_private_plugins_unpack_path, get_ae_plugins_dir, get_wineprefix_dir


class PluginThread(ProcessThread):
    def __init__(self):
        super().__init__()
    
    def set_plugin_zip_filename(self, filename: str):
        self.plugin_zip_filename = filename
    
    def run(self):
        self.log_signal.emit('[DEBUG] Unpacking plugins from the archive...')
        self.progress_signal.emit(5)
        self.remove_ppu_dir()

        ppu_dir = get_private_plugins_unpack_path()
        self.unpack_zip(self.plugin_zip_filename, ppu_dir.as_posix())
        self.progress_signal.emit(15)

        self.install_aex_plugins()
        self.install_cep_extensions()
        self.install_presets()
        self.run_installers()

        self.remove_ppu_dir()
        self.progress_signal.emit(95)
        self.log_signal.emit('[INFO] The plugins have been installed')

        self.finished_signal.emit(True)
        self.progress_signal.emit(100)
    
    def install_aex_plugins(self):
        self.log_signal.emit('[DEBUG] Installing aex plugins...')

        ppu_dir = get_private_plugins_unpack_path()
        aex_src = ppu_dir.joinpath('aex')

        for item in os.listdir(aex_src.as_posix()):
            if self._is_cancelled:
                self.cancelled.emit()
                return
            src_path = aex_src.joinpath(item)
            dst_path = get_ae_plugins_dir().joinpath(item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)

        self.log_signal.emit('[INFO] AEX plugins installed')
        self.progress_signal.emit(30)
    
    def install_presets(self):
        self.log_signal.emit('[DEBUG] Installing presets...')

        ppu_dir = get_private_plugins_unpack_path()
        preset_src = ppu_dir.joinpath('preset-backup')
        preset_dest = get_wineprefix_dir().joinpath('drive_c/users/relative/Documents/Adobe/After Effects 2024/User Presets')

        os.makedirs(preset_dest, exist_ok=True)
        for item in os.listdir(preset_src):
            if self._is_cancelled:
                self.cancelled.emit()
                return
            src_path = preset_src.joinpath(item)
            dst_path = preset_dest.joinpath(item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)

        self.log_signal.emit("[INFO] Presets installed")
        self.progress_signal.emit(55)
    
    def run_installers(self):
        self.log_signal.emit('[DEBUG] Running installers...')
        ppu_dir = get_private_plugins_unpack_path()
        install_src = ppu_dir.joinpath('installer')

        installers_counter = 0

        for exe in os.listdir(install_src.as_posix()):
            if exe.endswith('.exe') and exe not in ['E3D.exe', 'saber.exe']:
                self.progress_signal.emit(55 + installers_counter * 3)
                
                self.log_signal.emit(f"[INFO] Installing: {exe}")
                self.run_command(
                    ['wine', exe, '/verysilent', '/suppressmsgboxes'], 
                    install_src.as_posix(), True
                )
        
        self.progress_signal.emit(70)
        
        # Special handling for E3D and saber
        for exe in ['E3D.exe', 'saber.exe']:
            self.log_signal.emit(f"[INFO] Please manually install: {exe}")
            self.run_command(
                ['wine', exe], 
                install_src.as_posix(), True
            )
        
        self.progress_signal.emit(85)
        self.copy_element_files()
        
    def copy_element_files(self):
        self.log_signal.emit('[DEBUG] Copying Element files...')

        ppu_dir = get_private_plugins_unpack_path()
        install_src = ppu_dir.joinpath('installer')

        video_copilot_dir = get_ae_plugins_dir().joinpath("VideoCopilot")
        element_files = [
            ("Element.aex", "Element.aex"),
            ("Element.license", "Element.license")
        ]
        
        for src_name, dst_name in element_files:
            src_path = install_src.joinpath(src_name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, os.path.join(video_copilot_dir, dst_name))
                self.log_signal.emit(f"[INFO] {src_name} copied successfully")
        
        self.log_signal.emit("[INFO] Element installed")
        self.progress_signal.emit(90)
    
    def install_cep_extensions(self):
        self.log_signal.emit('[DEBUG] Installing CEP extensions...')

        ppu_dir = get_private_plugins_unpack_path()
        cep_dir = ppu_dir.joinpath('CEP')

        cep_reg_file = cep_dir.joinpath("AddKeys.reg")
        self.run_command(['wine', "regedit", cep_reg_file.as_posix()], in_prefix=True)

        self.install_flow()

        self.log_signal.emit("[INFO] CEP extensions installed")
        self.progress_signal.emit(45)
    
    def install_flow(self):
        ppu_dir = get_private_plugins_unpack_path()
        cep_dir = ppu_dir.joinpath('CEP')

        self.log_signal.emit('[DEBUG] Installing Flow...')
        
        flow_src = cep_dir.joinpath("flowv1.4.2")
        cep_dst = get_wineprefix_dir().joinpath("drive_c/Program Files (x86)/Common Files/Adobe/CEP/extensions")
        
        os.makedirs(cep_dst, exist_ok=True)
        shutil.copytree(flow_src, os.path.join(cep_dst, "flowv1.4.2"), dirs_exist_ok=True)
        self.log_signal.emit("[INFO] Flow installed")
    
    def remove_ppu_dir(self):
        ppu_dir = get_private_plugins_unpack_path()
        try:
            shutil.rmtree(ppu_dir.as_posix())
            self.log_signal.emit('[DEBUG] Temporary folder removed successfully.')
        except OSError as e:
            self.log_signal.emit(f'[WARNING] Failed to remove temporary folder {ppu_dir}: {e}')