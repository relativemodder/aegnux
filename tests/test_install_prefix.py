import os
import shutil
from pathlib import Path

from src.utils import install_codecs_into_wineprefix


def test_install_into_wineprefix(tmp_path, monkeypatch):
    # Готовим фиктивный XDG_DATA_HOME чтобы wineprefix создавался во временной
    # папке
    fake_home = tmp_path / 'xdg'
    monkeypatch.setenv('XDG_DATA_HOME', str(fake_home))

    codecs_dir = tmp_path / 'codecs'
    codecs_dir.mkdir()

    # Создаем тестовые файлы кодеков
    (codecs_dir / 'a.dll').write_text('a')
    (codecs_dir / 'b.ax').write_text('b')

    # Вызываем установщик
    stats = install_codecs_into_wineprefix(
        str(codecs_dir), logger=lambda m: None)

    # Проверяем что файлы были найдены и скопированы в System32 и SysWOW64
    assert stats['found'] == 2
    assert stats['copied'] >= 2

    wineprefix = Path(fake_home).joinpath('aegnux').joinpath('wineprefix')
    s32 = wineprefix.joinpath('drive_c/Windows/System32')
    sw64 = wineprefix.joinpath('drive_c/Windows/SysWOW64')

    # Файлы должны существовать хотя бы в одной из целевых папок (копируются
    # для каждой цели)
    assert (s32 / 'a.dll').exists() or (sw64 / 'a.dll').exists()
    assert (s32 / 'b.ax').exists() or (sw64 / 'b.ax').exists()
