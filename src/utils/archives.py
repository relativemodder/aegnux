"""
Утилиты для работы с архивами.

Этот модуль содержит функции для проверки, распаковки и
обработки различных типов архивов (ZIP, TAR, etc.).

Автор: Иван Петров
Дата создания: 30.10.2025
"""

import os
import logging
import zipfile
import tarfile
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

def is_valid_archive(file_path: str) -> bool:
    """
    Проверяет корректность архива.
    
    Args:
        file_path: Путь к архиву
        
    Returns:
        bool: True если архив корректен, иначе False
    """
    try:
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zf:
                return zf.testzip() is None
                
        elif any(file_path.endswith(ext) for ext in ['.tar', '.gz', '.bz2', '.xz']):
            with tarfile.open(file_path, 'r:*') as tf:
                return tf.members is not None
                
        return False
        
    except Exception as e:
        logger.error(f"Ошибка проверки архива {file_path}: {e}")
        return False
        
def safe_extract(
    archive_path: str,
    extract_path: str,
    allowed_extensions: Optional[List[str]] = None
) -> Dict[str, int]:
    """
    Безопасная распаковка архива с проверками.
    
    Args:
        archive_path: Путь к архиву
        extract_path: Путь для распаковки
        allowed_extensions: Список разрешенных расширений
        
    Returns:
        Dict[str, int]: Статистика распаковки
    """
    stats = {
        'total': 0,
        'extracted': 0,
        'skipped': 0,
        'errors': 0
    }
    
    try:
        # Проверяем существование архива
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Архив не найден: {archive_path}")
            
        # Создаем директорию для распаковки
        os.makedirs(extract_path, exist_ok=True)
        
        # Распаковываем в зависимости от типа
        if archive_path.endswith('.zip'):
            stats.update(
                _extract_zip(archive_path, extract_path, allowed_extensions)
            )
        else:
            stats.update(
                _extract_tar(archive_path, extract_path, allowed_extensions)
            )
            
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка распаковки {archive_path}: {e}")
        stats['errors'] += 1
        return stats
        
def _extract_zip(
    zip_path: str,
    extract_path: str,
    allowed_extensions: Optional[List[str]] = None
) -> Dict[str, int]:
    """Извлечение файлов из ZIP архива."""
    stats = {'total': 0, 'extracted': 0, 'skipped': 0, 'errors': 0}
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Получаем список файлов
        members = [m for m in zf.infolist() if not m.is_dir()]
        stats['total'] = len(members)
        
        for member in members:
            try:
                # Проверяем расширение
                if allowed_extensions:
                    ext = os.path.splitext(member.filename)[1].lower()
                    if ext not in allowed_extensions:
                        stats['skipped'] += 1
                        continue
                        
                # Проверяем безопасность пути
                if '..' in member.filename or member.filename.startswith('/'):
                    logger.warning(f"Пропуск небезопасного пути: {member.filename}")
                    stats['skipped'] += 1
                    continue
                    
                # Извлекаем файл
                zf.extract(member, extract_path)
                stats['extracted'] += 1
                
                # Устанавливаем права
                extracted_path = os.path.join(extract_path, member.filename)
                os.chmod(extracted_path, 0o644)
                
            except Exception as e:
                logger.error(f"Ошибка извлечения {member.filename}: {e}")
                stats['errors'] += 1
                
    return stats
    
def _extract_tar(
    tar_path: str,
    extract_path: str,
    allowed_extensions: Optional[List[str]] = None
) -> Dict[str, int]:
    """Извлечение файлов из TAR архива."""
    stats = {'total': 0, 'extracted': 0, 'skipped': 0, 'errors': 0}
    
    with tarfile.open(tar_path, 'r:*') as tf:
        members = [m for m in tf.getmembers() if m.isfile()]
        stats['total'] = len(members)
        
        for member in members:
            try:
                # Проверяем расширение
                if allowed_extensions:
                    ext = os.path.splitext(member.name)[1].lower()
                    if ext not in allowed_extensions:
                        stats['skipped'] += 1
                        continue
                        
                # Проверяем безопасность пути
                if '..' in member.name or member.name.startswith('/'):
                    logger.warning(f"Пропуск небезопасного пути: {member.name}")
                    stats['skipped'] += 1
                    continue
                    
                # Извлекаем файл
                tf.extract(member, extract_path)
                stats['extracted'] += 1
                
                # Устанавливаем права
                extracted_path = os.path.join(extract_path, member.name)
                os.chmod(extracted_path, 0o644)
                
            except Exception as e:
                logger.error(f"Ошибка извлечения {member.name}: {e}")
                stats['errors'] += 1
                
    return stats