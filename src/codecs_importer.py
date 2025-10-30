"""Простой импортёр кодеков из директории Windows в проект.

Функциональность:
- Рекурсивно ищет файлы с расширениями, указанными в config.CODECS_EXTENSIONS
- Копирует их в config.CODECS_DIR, сохраняя относительную директорию от источника
- Возвращает статистику (скопировано/пропущено/ошибки)

Этот модуль не выполняет никаких бинарных преобразований — только копирование файлов.
"""
import os
import shutil
from typing import Callable, Dict, Optional
from src import config


def _is_codec_file(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in config.CODECS_EXTENSIONS


def import_codecs(
    src_dir: str,
    overwrite: bool = None,
    logger: Optional[Callable[[str], None]] = None,
    progress: Optional[Callable[[int, int], None]] = None,
    should_stop: Optional[Callable[[], bool]] = None,
) -> Dict[str, int]:
    """Импортирует кодеки из `src_dir` в `config.CODECS_DIR`.

    Args:
        src_dir: путь к корню Windows (или любой директории с кодеками)
        overwrite: если True — перезаписывать существующие файлы; если False — пропускать;
                   если None — использовать значение config.CODECS_OVERWRITE_BY_DEFAULT
        logger: функция для логирования (принимает строку); если None — лог не выводится

    Returns:
        dict: статистика: {'found': N, 'copied': N, 'skipped': N, 'errors': N}
    """
    if overwrite is None:
        overwrite = config.CODECS_OVERWRITE_BY_DEFAULT

    stats = {'found': 0, 'copied': 0, 'skipped': 0, 'errors': 0}

    src_dir = os.path.abspath(src_dir)
    target_base = os.path.abspath(config.CODECS_DIR)

    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"Source directory does not exist: {src_dir}")

    # Соберём список файлов-кодеков сначала, чтобы иметь возможность
    # отобразить прогресс
    candidates = []
    for root, _, files in os.walk(src_dir):
        if should_stop and should_stop():
            # interrupted during scan
            if logger:
                logger("Import cancelled during scan")
            return stats
        for f in files:
            full = os.path.join(root, f)
            if _is_codec_file(full):
                candidates.append(full)

    total = len(candidates)
    stats['found'] = total

    if progress:
        # Report initial state
        try:
            progress(0, total)
        except Exception:
            pass

    os.makedirs(target_base, exist_ok=True)

    for idx, full in enumerate(candidates):
        if should_stop and should_stop():
            if logger:
                logger("Import cancelled by user")
            # report current progress via progress callback
            if progress:
                try:
                    progress(idx, total)
                except Exception:
                    pass
            return stats
        rel = os.path.relpath(full, src_dir)
        target_path = os.path.join(target_base, rel)
        target_dir = os.path.dirname(target_path)
        try:
            os.makedirs(target_dir, exist_ok=True)
            if os.path.exists(target_path) and not overwrite:
                stats['skipped'] += 1
                if logger:
                    logger(f"Skipped existing: {target_path}")
            else:
                shutil.copy2(full, target_path)
                stats['copied'] += 1
                if logger:
                    logger(f"Copied: {full} -> {target_path}")
        except Exception as e:
            stats['errors'] += 1
            if logger:
                logger(f"Error copying {full}: {e}")

        if progress:
            try:
                progress(idx + 1, total)
            except Exception:
                pass

    return stats
