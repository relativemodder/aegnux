import math
import os
import shutil
import subprocess
from src.types import DownloadMethod
from PySide6.QtWidgets import QMessageBox
from pathlib import Path

def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_name[i]}"

def is_nvidia_present():
    if shutil.which('nvidia-smi'):
        return True
    
    if os.path.exists('/proc/driver/nvidia'):
        return True
    
    try:
        process = subprocess.Popen(
            ['lspci'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=False
        )
        stdout, _ = process.communicate()
        if 'NVIDIA' in stdout.decode('utf-8', errors='ignore').upper():
            return True
    except:
        pass
    return False

def show_download_method_dialog(title: str, message: str) -> DownloadMethod:
    dialog = QMessageBox()
    dialog.setWindowTitle(title)
    dialog.setText(message)
    
    download_btn = dialog.addButton("Download", QMessageBox.ButtonRole.AcceptRole)
    choose_file_btn = dialog.addButton("Choose Local File", QMessageBox.ButtonRole.ActionRole)
    cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
    
    dialog.exec()
    
    clicked_button = dialog.clickedButton()

    if clicked_button == download_btn:
        return DownloadMethod.ONLINE
    
    if clicked_button == choose_file_btn:
        return DownloadMethod.OFFLINE
    
    return DownloadMethod.CANCEL

def get_aegnux_installation_dir():
    data_home = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    aegnux_dir = Path(data_home).joinpath('aegnux')

    if not os.path.exists(aegnux_dir):
        os.makedirs(aegnux_dir)

    return aegnux_dir

def get_ae_install_dir():
    aegnux_dir = get_aegnux_installation_dir()
    ae_dir = aegnux_dir.joinpath('AE')

    if not os.path.exists(ae_dir):
        os.makedirs(ae_dir)

    return ae_dir

def get_ae_plugins_dir():
    ae_dir = get_ae_install_dir()
    return ae_dir.joinpath('Plug-ins')

def get_wineprefix_dir():
    aegnux_dir = get_aegnux_installation_dir()
    wineprefix_dir = aegnux_dir.joinpath('wineprefix')

    if not os.path.exists(wineprefix_dir):
        os.makedirs(wineprefix_dir)

    return wineprefix_dir

def get_cep_dir():
    wineprefix_dir = get_wineprefix_dir()
    cep_dir = wineprefix_dir.joinpath('drive_c/Program Files (x86)/Common Files/Adobe/CEP')

    if not os.path.exists(cep_dir):
        os.makedirs(cep_dir)

    return cep_dir

def get_wine_runner_dir():
    aegnux_dir = get_aegnux_installation_dir()
    runner_dir = aegnux_dir.joinpath('runner')

    if not os.path.exists(runner_dir):
        os.makedirs(runner_dir)

    return runner_dir

def get_wine_bin():
    runner_dir = get_wine_runner_dir()
    return runner_dir.joinpath('bin/wine')

def get_wineserver_bin():
    runner_dir = get_wine_runner_dir()
    return runner_dir.joinpath('bin/wineserver')

def get_winetricks_bin():
    runner_dir = get_wine_runner_dir()
    return runner_dir.joinpath('bin/winetricks')

def get_cabextract_bin():
    runner_dir = get_wine_runner_dir()
    return runner_dir.joinpath('bin/cabextract')

def get_vcr_dir_path():
    runner_dir = get_wine_runner_dir()
    return runner_dir.joinpath('vcr')

def get_msxml_dir_path():
    runner_dir = get_wine_runner_dir()
    return runner_dir.joinpath('msxml')

def get_aegnux_installed_flag_path():
    hades = get_aegnux_installation_dir()
    return hades.joinpath('installed')

def check_aegnux_installed():
    return os.path.exists(get_aegnux_installed_flag_path())

def mark_aegnux_as_installed():
    with open(get_aegnux_installed_flag_path(), 'w') as f:
        f.write('have fun :)')

def get_wine_bin_path_env(old_path: str | None):
    old_path = old_path if old_path is not None else os.getenv('PATH')
    return f'{get_wine_runner_dir().as_posix()}/bin:{old_path}'

def get_mhtb_install_dir():
    wineprefix_dir = get_wineprefix_dir()
    mhtb_dir = wineprefix_dir.joinpath('drive_c/Program Files/Mister Horse Product Manager')
    
    if not os.path.exists(mhtb_dir):
        return None

    return mhtb_dir

def get_default_terminal() -> str:
    DEFAULT_ENVS = ["TERMINAL", "TERM_PROGRAM"]
    TERMINALS = [
        "konsole",
        "kitty",
        "alacritty",
        "gnome-terminal",
        "xfce4-terminal",
        "terminator",
        "lxterminal",
        "tilix",
        "st",
        "mate-terminal",
        "xterm",
        "urxvt",
        "deepin-terminal",
        "sakura",
        "tilda",
        "guake",
        "hyper",
        "eterm",
        "rxvt",
        "lxterm",
        "cosmic-terminal",
    ]

    candidates = (
        shutil.which(os.environ.get(var)) for var in DEFAULT_ENVS if os.environ.get(var)
    )

    # Debian/Ubuntu
    alt = "/etc/alternatives/x-terminal-emulator"
    if os.path.exists(alt):
        candidates = (shutil.which(os.readlink(alt)), *candidates)

    # Popular terminals
    candidates = (*candidates, *(shutil.which(term) for term in TERMINALS))

    terminal = next((t for t in candidates if t), None)
    if terminal:
        return terminal

    raise RuntimeError(
        "Your terminal was not found or is not supported.\n"
        "Install one of the following: " + ", ".join(TERMINALS)
    )

def get_aegnux_tip_marked_flag_path():
    hades = get_aegnux_installation_dir()
    return hades.joinpath('terminal_tip')

def check_aegnux_tip_marked():
    return os.path.exists(get_aegnux_tip_marked_flag_path())

def mark_aegnux_tip_as_shown():
    with open(get_aegnux_tip_marked_flag_path(), 'w') as f:
        f.write('Press ALT+T to open up a terminal')


def get_private_plugins_unpack_path():
    aegnux_dir = get_aegnux_installation_dir()
    ppu_dir = aegnux_dir.joinpath('private-plugins')

    if not os.path.exists(ppu_dir):
        os.makedirs(ppu_dir)

    return ppu_dir