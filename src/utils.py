import math
import os
import shutil
import subprocess
from typing import Callable
from src.types import DownloadMethod
# Ленивый импорт QMessageBox чтобы избежать зависимости от GUI во время тестов
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
    except BaseException:
        pass
    return False


def show_download_method_dialog(title: str, message: str) -> DownloadMethod:
    from PySide6.QtWidgets import QMessageBox

    dialog = QMessageBox()
    dialog.setWindowTitle(title)
    dialog.setText(message)

    download_btn = dialog.addButton(
        "Download", QMessageBox.ButtonRole.AcceptRole)
    choose_file_btn = dialog.addButton(
        "Choose Local File",
        QMessageBox.ButtonRole.ActionRole)
    cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

    dialog.exec()

    clicked_button = dialog.clickedButton()

    if clicked_button == download_btn:
        return DownloadMethod.ONLINE

    if clicked_button == choose_file_btn:
        return DownloadMethod.OFFLINE

    return DownloadMethod.CANCEL


def get_aegnux_installation_dir():
    data_home = os.getenv(
        'XDG_DATA_HOME',
        os.path.expanduser('~/.local/share'))
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


def get_aegnux_tip_marked_flag_path():
    hades = get_aegnux_installation_dir()
    return hades.joinpath('terminal_tip')


def check_aegnux_tip_marked():
    return os.path.exists(get_aegnux_tip_marked_flag_path())


def mark_aegnux_tip_as_shown():
    with open(get_aegnux_tip_marked_flag_path(), 'w') as f:
        f.write('Press ALT+T to open up a terminal')


def get_codecs_overwrite_flag_path():
    hades = get_aegnux_installation_dir()
    return hades.joinpath('codecs_overwrite')


def read_codecs_overwrite_choice() -> bool | None:
    """Возвращает True/False если пользователь ранее сохранил выбор, иначе None."""
    p = get_codecs_overwrite_flag_path()
    if not os.path.exists(p):
        return None
    try:
        with open(p, 'r') as f:
            v = f.read().strip()
        if v == '1':
            return True
        if v == '0':
            return False
    except Exception:
        pass
    return None


def write_codecs_overwrite_choice(choice: bool):
    p = get_codecs_overwrite_flag_path()
    try:
        with open(p, 'w') as f:
            f.write('1' if choice else '0')
    except Exception:
        # best effort only
        pass


def install_codecs_into_wineprefix(
        codecs_dir: str, logger: Callable[[str], None] | None = None) -> dict:
    """Копирует все файлы из `codecs_dir` в стандартные места Windows внутри WINEPREFIX.

    Копируются файлы с сохранением относительной структуры в:
      <WINEPREFIX>/drive_c/windows/system32
      <WINEPREFIX>/drive_c/windows/syswow64

    Возвращает статистику похожую на import_codecs.
    """
    from shutil import copy2
    from pathlib import Path

    stats = {'found': 0, 'copied': 0, 'skipped': 0, 'errors': 0}

    p = Path(codecs_dir)
    if not p.exists():
        raise FileNotFoundError(f"Codecs dir not found: {codecs_dir}")

    wineprefix = get_wineprefix_dir()
    # целевые каталоги внутри wineprefix
    targets = [
        wineprefix.joinpath('drive_c/Windows/System32'),
        wineprefix.joinpath('drive_c/Windows/SysWOW64')
    ]

    for target in targets:
        target.mkdir(parents=True, exist_ok=True)

    for root, _, files in os.walk(str(p)):
        for f in files:
            full = os.path.join(root, f)
            stats['found'] += 1
            # сохраняем относительный путь от каталога кодеков
            rel = os.path.relpath(full, str(p))
            for target in targets:
                dest = target.joinpath(rel)
                dest_dir = dest.parent
                try:
                    os.makedirs(dest_dir, exist_ok=True)
                    if os.path.exists(dest):
                        stats['skipped'] += 1
                        if logger:
                            logger(f"Skipped (exists): {dest}")
                    else:
                        copy2(full, str(dest))
                        stats['copied'] += 1
                        if logger:
                            logger(f"Installed codec: {dest}")
                except Exception as e:
                    stats['errors'] += 1
                    if logger:
                        logger(f"Error installing {full} -> {dest}: {e}")

    return stats
