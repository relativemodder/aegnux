"""
Утилиты для работы с процессами.

Этот модуль содержит функции для запуска, отслеживания и управления
процессами в Linux и Wine окружении.

Автор: Иван Петров
Дата создания: 30.10.2025
"""

import os
import sys
import time
import signal
import psutil
import logging
import subprocess
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

def run_process(
    command: List[str],
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None
) -> Tuple[int, str, str]:
    """
    Запуск процесса с контролем выполнения.
    
    Args:
        command: Команда и аргументы
        cwd: Рабочая директория
        env: Переменные окружения
        timeout: Таймаут в секундах
        
    Returns:
        Tuple[int, str, str]: Код возврата, stdout, stderr
    """
    try:
        # Запускаем процесс
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Ждем завершения с таймаутом
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode, stdout, stderr
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Таймаут процесса: {' '.join(command)}")
            process.kill()
            stdout, stderr = process.communicate()
            return -1, stdout, stderr
            
    except Exception as e:
        logger.error(f"Ошибка запуска {' '.join(command)}: {e}")
        return -1, "", str(e)
        
def find_wine_processes() -> List[psutil.Process]:
    """
    Поиск процессов Wine в системе.
    
    Returns:
        List[psutil.Process]: Список процессов Wine
    """
    wine_processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Проверяем имя и командную строку
                if any(x in proc.name().lower() for x in ['wine']):
                    wine_processes.append(proc)
                elif proc.cmdline() and 'wine' in ' '.join(proc.cmdline()).lower():
                    wine_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    except Exception as e:
        logger.error(f"Ошибка поиска процессов Wine: {e}")
        
    return wine_processes
    
def kill_wine_processes(
    grace_period: int = 5,
    force: bool = False
) -> Tuple[int, int]:
    """
    Завершение всех процессов Wine.
    
    Args:
        grace_period: Время ожидания (сек)
        force: Принудительное завершение
        
    Returns:
        Tuple[int, int]: Количество (завершено, ошибок)
    """
    terminated = 0
    errors = 0
    
    try:
        # Получаем список процессов
        processes = find_wine_processes()
        
        if not processes:
            return 0, 0
            
        # Отправляем SIGTERM
        for proc in processes:
            try:
                proc.terminate()
            except Exception:
                continue
                
        # Ждем завершения
        time.sleep(grace_period)
        
        # Проверяем оставшиеся
        remaining = [p for p in processes if p.is_running()]
        
        if remaining and force:
            # Отправляем SIGKILL
            for proc in remaining:
                try:
                    proc.kill()
                    terminated += 1
                except Exception as e:
                    logger.error(f"Ошибка завершения {proc.pid}: {e}")
                    errors += 1
                    
    except Exception as e:
        logger.error(f"Ошибка завершения процессов Wine: {e}")
        errors += 1
        
    return terminated, errors
    
def get_process_info(pid: int) -> Optional[Dict[str, Union[str, int, float]]]:
    """
    Получение информации о процессе.
    
    Args:
        pid: ID процесса
        
    Returns:
        Optional[Dict]: Информация о процессе
    """
    try:
        proc = psutil.Process(pid)
        return {
            'pid': proc.pid,
            'name': proc.name(),
            'status': proc.status(),
            'created': proc.create_time(),
            'cpu_percent': proc.cpu_percent(),
            'memory_percent': proc.memory_percent(),
            'cmdline': ' '.join(proc.cmdline()),
            'username': proc.username()
        }
    except Exception as e:
        logger.error(f"Ошибка получения информации о процессе {pid}: {e}")
        return None