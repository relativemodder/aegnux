import os
import tempfile
import shutil
from src.utils import install_codecs_into_wineprefix
from src.codecs_importer import import_codecs
import src.config as cfg


def create_sample_tree(root, count=5):
    os.makedirs(root, exist_ok=True)
    files = [f'a{i}.dll' for i in range(count)]
    files += [f'subdir/b{i}.ax' for i in range(count)]
    for f in files:
        p = os.path.join(root, f)
        d = os.path.dirname(p)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        with open(p, 'w') as fh:
            fh.write('data')


def test_install_into_wineprefix(tmp_path, monkeypatch):
    # create source codecs dir
    src = tmp_path / 'codecs'
    create_sample_tree(str(src), count=3)

    # ensure a clean wineprefix under XDG_DATA_HOME
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path))

    # call installer
    stats = install_codecs_into_wineprefix(str(src), logger=lambda m: None)

    # check results in wineprefix
    wineprefix = tmp_path / 'aegnux' / 'wineprefix'
    sys32 = wineprefix / 'drive_c' / 'Windows' / 'System32'
    syswow = wineprefix / 'drive_c' / 'Windows' / 'SysWOW64'

    assert sys32.exists()
    assert syswow.exists()

    # count copied files (should be >0)
    copied_sys32 = sum(1 for _ in (sys32.rglob('*')) if _.is_file())
    copied_syswow = sum(1 for _ in (syswow.rglob('*')) if _.is_file())
    assert copied_sys32 > 0
    assert copied_syswow > 0


def test_cancel_import(tmp_path):
    # create many codec files
    src = tmp_path / 'big'
    create_sample_tree(str(src), count=50)

    # a should_stop that triggers after N calls
    class Stopper:
        def __init__(self, limit):
            self.count = 0
            self.limit = limit

        def __call__(self):
            self.count += 1
            return self.count > self.limit

    stopper = Stopper(limit=10)

    # run import with should_stop; it should finish early
    stats = import_codecs(
        str(src),
        overwrite=True,
        logger=lambda m: None,
        progress=lambda p,
        t: None,
        should_stop=stopper)

    # When cancelled, processed copied should be less than total found
    assert stats['copied'] < stats['found'] or stats['errors'] > 0
