import os
from src.codecs_importer import import_codecs


def test_import_cancellation(tmp_path):
    # Создаем одну директорию с множеством файлов кодеков (чтобы сканирование
    # было одной итерацией)
    src = tmp_path / 'src'
    src.mkdir()
    total_files = 200
    for i in range(total_files):
        (src / f'f{i}.dll').write_text('x')

    # should_stop: игнорируем первый вызов (сканирование) но останавливаем
    # после ~50 вызовов обработки
    calls = {'n': 0}

    def should_stop():
        calls['n'] += 1
        # разрешаем первые ~60 вызовов, затем запрашиваем остановку
        return calls['n'] > 60

    stats = import_codecs(
        str(src),
        overwrite=True,
        logger=lambda m: None,
        should_stop=should_stop)

    # Если отмена произошла во время обработки, скопированных файлов должно
    # быть меньше чем найденных
    assert stats['found'] == total_files
    assert stats['copied'] < stats['found']
