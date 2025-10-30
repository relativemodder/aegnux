import os
import tempfile
import shutil
from src.codecs_importer import import_codecs


def create_sample_tree(root):
    os.makedirs(root, exist_ok=True)
    # создаем файлы кодеков и другие файлы
    files = [
        'a.dll',
        'b.AX',
        'subdir/c.acm',
        'subdir/d.txt'
    ]
    for f in files:
        p = os.path.join(root, f)
        d = os.path.dirname(p)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        with open(p, 'w') as fh:
            fh.write('data')


def test_import_basic(tmp_path):
    src = tmp_path / 'src'
    dst = tmp_path / 'dst'
    create_sample_tree(str(src))

    # переопределяем config.CODECS_DIR через трюк с окружением (monkeypatch
    # недоступен)
    import src.config as cfg
    cfg.CODECS_DIR = str(dst)

    stats = import_codecs(str(src), overwrite=True, logger=lambda m: None)

    assert stats['found'] == 3
    assert stats['copied'] == 3
    assert stats['errors'] == 0


def test_import_skip_existing(tmp_path):
    src = tmp_path / 'src2'
    dst = tmp_path / 'dst2'
    create_sample_tree(str(src))

    import src.config as cfg
    cfg.CODECS_DIR = str(dst)

    # первый импорт
    stats1 = import_codecs(str(src), overwrite=True, logger=lambda m: None)
    # второй импорт с overwrite=False должен пропускать файлы
    stats2 = import_codecs(str(src), overwrite=False, logger=lambda m: None)

    assert stats1['copied'] == 3
    assert stats2['skipped'] == 3
