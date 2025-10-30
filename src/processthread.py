#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для управления фоновыми процессами в Aegnux.

Этот модуль реализует базовый класс для всех фоновых операций,
включая загрузку файлов, распаковку архивов и выполнение команд.
Обеспечивает асинхронное выполнение длительных операций без блокировки GUI.

Автор: Иван Петров
Дата создания: 15.08.2023
Последнее обновление: 30.10.2025
"""

import os
import sys
import time
import select
import fcntl
import shutil
import logging
import requests
import zipfile
import tarfile
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple

# Импорт утилит
from src.utils import (
    format_size,
    get_wineprefix_dir,
    get_wine_bin_path_env,
    is_valid_archive
)

# Импорт конфигурации
from src.config import (
    DOWNLOAD_CHUNK_SIZE,
    LOG_THROTTLE_SECONDS,
    TEMP_DIR,
    LOG_DIR
)

# Импорт Qt компонентов
from PySide6.QtCore import QThread, Signal

# Настройка логирования
logger = logging.getLogger(__name__)


class ProcessThread(QThread):
    """
    Базовый класс для фоновых процессов.
    
    Предоставляет общий функционал для:
    - Загрузки файлов
    - Распаковки архивов
    - Выполнения команд
    - Отслеживания прогресса
    - Логирования
    
    Сигналы:
        log_signal: Отправка сообщений в лог
        progress_signal: Обновление прогресса (0-100)
        finished_signal: Завершение операции (успех/неудача)
        cancelled: Операция отменена пользователем
    """
    
    # Определение сигналов
    log_signal = Signal(str)          # Сообщения для лога
    progress_signal = Signal(int)     # Прогресс операции
    finished_signal = Signal(bool)    # Статус завершения
    cancelled = Signal()              # Сигнал отмены
    
    def __init__(self, parent=None):
        """Инициализация потока обработки."""
        super().__init__(parent)
        
        # Флаг отмены операции
        self._is_cancelled = False
        
        # Настройка логирования для потока
        self._setup_logging()
        
    def _setup_logging(self):
        """Настройка логирования для потока."""
        # Создаем обработчик для записи в файл
        log_file = LOG_DIR / f"{self.__class__.__name__}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s"
            )
        )
        logger.addHandler(file_handler)

    def cancel(self) -> None:
        """
        Отмена текущей операции.
        
        Устанавливает флаг отмены, который проверяется в критических точках
        выполнения операции для безопасного прерывания.
        """
        self._is_cancelled = True
        logger.info("Запрошена отмена операции")
        self.log_signal.emit("[ОТМЕНА] Запрошена отмена операции")
        
    def download_file_to(self, url: str, filename: str) -> bool:
        """
        Загрузка файла по URL с отображением прогресса.
        
        Args:
            url: URL файла для загрузки
            filename: Путь для сохранения файла
            
        Returns:
            bool: True при успешной загрузке, False при ошибке/отмене
        """
        try:
            # Создаем временную директорию если нужно
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Открываем соединение
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Получаем размер файла
            total_size = int(response.headers.get('content-length', 0))
            
            # Инициализация счетчиков
            bytes_downloaded = 0
            start_time = time.time()
            last_update = time.time()

        with open(filename, 'wb') as f:
            for data in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                if self._is_cancelled:
                    self.log_signal.emit(
                        f'[DOWNLOAD] Cancelled by user. Deleting partial file: {filename}')
                    r.close()
                    os.remove(filename)
                    self.cancelled.emit()
                    self.finished_signal.emit(False)
                    return

                f.write(data)
                downloaded += len(data)

                current_time = time.time()
                if current_time - last_update_time >= LOG_THROTTLE_SECONDS:
                    if total > 0:
                        percent = int((downloaded / total) * 100)
                    else:
                        percent = 0

                    elapsed_time = current_time - start_time
                    speed = (downloaded /
                             elapsed_time) if elapsed_time > 0 else 0

                    self.log_signal.emit(
                        f'[DOWNLOADING] {filename} ({percent}%/{format_size(total)}), {format_size(speed)}/s')
                    last_update_time = current_time

        if total > 0:
            final_percent = 100
        else:
            final_percent = 0

        self.log_signal.emit(
            f'[DOWNLOADED] {filename} (100%/{format_size(total)})')

    def unpack_zip(self, zip_file_path: str, extract_to_path: str) -> bool:
        """
        Распаковка ZIP архива с отслеживанием прогресса.
        
        Args:
            zip_file_path: Путь к ZIP архиву
            extract_to_path: Путь для распаковки
            
        Returns:
            bool: True при успешной распаковке, False при ошибке/отмене
        """
        try:
            # Проверяем существование архива
            if not os.path.exists(zip_file_path):
                raise FileNotFoundError(f"Архив не найден: {zip_file_path}")
            
            # Проверяем корректность архива
            if not is_valid_archive(zip_file_path):
                raise ValueError(f"Некорректный ZIP архив: {zip_file_path}")
                
            self.log_signal.emit(f"[РАСПАКОВКА] Начало распаковки: {zip_file_path}")
            
            # Открываем архив
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Получаем список файлов (без директорий)
                members = [m for m in zip_ref.infolist() if not m.is_dir()]
                total_files = len(members)
                
                if total_files == 0:
                    raise ValueError("Архив не содержит файлов")
                    
                # Создаем директорию для распаковки
                os.makedirs(extract_to_path, exist_ok=True)
                
                # Инициализируем счетчики
                extracted_files = 0
                last_update = time.time()
                start_time = time.time()

            # Распаковываем файлы
            for file_info in members:
                # Проверяем флаг отмены
                if self._is_cancelled:
                    msg = "Распаковка отменена пользователем"
                    logger.info(msg)
                    self.log_signal.emit(f"[ОТМЕНА] {msg}")
                    self.cancelled.emit()
                    self.finished_signal.emit(False)
                    return False
                
                try:
                    # Проверяем безопасность пути
                    if '..' in file_info.filename or file_info.filename.startswith('/'):
                        logger.warning(f"Пропуск небезопасного пути: {file_info.filename}")
                        continue
                        
                    # Распаковываем файл
                    zip_ref.extract(file_info, extract_to_path)
                    extracted_files += 1
                    
                    # Устанавливаем правильные права
                    extracted_path = os.path.join(extract_to_path, file_info.filename)
                    os.chmod(extracted_path, 0o644)  # rw-r--r--

                current_time = time.time()
                # Throttling logic
                if current_time - last_update_time >= LOG_THROTTLE_SECONDS or extracted_files == total_files:
                    if total_files > 0:
                        percent = int((extracted_files / total_files) * 100)
                    else:
                        percent = 0

                    self.log_signal.emit(
                        f'[EXTRACTING] {zip_file_path}: {extracted_files}/{total_files} files ({percent}%)')
                    last_update_time = current_time

        self.log_signal.emit(
            f'[EXTRACTED] ZIP finished extracting to {extract_to_path}')

    def unpack_tar(self, tar_file_path: str, extract_to_path: str):
        self.log_signal.emit(
            f'[EXTRACTING] Starting TAR extraction: {tar_file_path}')
        with tarfile.open(tar_file_path, 'r') as tar_ref:
            members = [m for m in tar_ref.getmembers() if m.isfile()]
            total_files = len(members)
            extracted_files = 0
            last_update_time = time.time()

            os.makedirs(extract_to_path, exist_ok=True)

            for member in members:
                if self._is_cancelled:
                    self.log_signal.emit(
                        '[EXTRACTING] TAR extraction cancelled by user.')
                    self.cancelled.emit()
                    self.finished_signal.emit(False)
                    return

                tar_ref.extract(member, extract_to_path)
                extracted_files += 1

                current_time = time.time()
                if total_files > 0 and (
                        current_time -
                        last_update_time >= LOG_THROTTLE_SECONDS or extracted_files == total_files):
                    percent = int((extracted_files / total_files) * 100)
                    self.log_signal.emit(
                        f'[EXTRACTING] {tar_file_path}: {extracted_files}/{total_files} files ({percent}%)')
                    last_update_time = current_time

        self.log_signal.emit(
            f'[EXTRACTED] TAR finished extracting to {extract_to_path}')

    def _set_non_blocking(self, file):
        if os.name == 'posix':
            fd = file.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def run_command(
            self,
            command: list,
            cwd: str = None,
            in_prefix: bool = False):
        self.log_signal.emit(f'[COMMAND] Running command: {" ".join(command)}')
        self._is_cancelled = False

        env = os.environ.copy()
        if in_prefix:
            env['WINEPREFIX'] = get_wineprefix_dir()
            env['PATH'] = get_wine_bin_path_env(env.get('PATH', os.defpath))

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=env
            )
        except FileNotFoundError:
            self.log_signal.emit(f'[ERROR] Command not found: {command[0]}')
            self.finished_signal.emit(False)
            return

        self._set_non_blocking(process.stdout)
        self._set_non_blocking(process.stderr)

        stdout_buffer = b''
        stderr_buffer = b''

        pipes = {
            process.stdout.fileno(): ('STDOUT', stdout_buffer),
            process.stderr.fileno(): ('STDERR', stderr_buffer)
        }

        last_log_time = time.time()

        while process.poll() is None or pipes:
            if self._is_cancelled:
                self.log_signal.emit(
                    '[COMMAND] Process cancelled by user. Terminating...')
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log_signal.emit(
                        '[COMMAND] Process did not terminate, killing...')
                    process.kill()
                self.cancelled.emit()
                self.finished_signal.emit(False)
                return

            if pipes:
                rlist, _, _ = select.select(pipes.keys(), [], [], 0.1)
            else:
                rlist = []

            current_time = time.time()
            if rlist or current_time - last_log_time >= LOG_THROTTLE_SECONDS:
                for fd in rlist:
                    stream_name, current_buffer_ref = pipes[fd]
                    pipe = process.stdout if stream_name == 'STDOUT' else process.stderr

                    try:
                        chunk = pipe.read(1024)
                    except BlockingIOError:
                        chunk = b''

                    if chunk:
                        current_buffer = current_buffer_ref + chunk

                        if stream_name == 'STDOUT':
                            stdout_buffer = current_buffer
                            pipes[fd] = (stream_name, stdout_buffer)
                        else:
                            stderr_buffer = current_buffer
                            pipes[fd] = (stream_name, stderr_buffer)

                    if not chunk and process.poll() is not None:
                        del pipes[fd]
                        break

                if current_time - last_log_time >= LOG_THROTTLE_SECONDS:
                    if process.stdout.fileno() in pipes:
                        stream_name, current_buffer = pipes[process.stdout.fileno(
                        )]
                        lines = current_buffer.split(b'\n')
                        stdout_buffer = lines.pop()
                        pipes[process.stdout.fileno()] = (
                            stream_name, stdout_buffer)

                        for line_bytes in lines:
                            line = line_bytes.decode(
                                'utf-8', errors='replace').strip()
                            if line:
                                self.log_signal.emit(f'[STDOUT] {line}')

                    if process.stderr.fileno() in pipes:
                        stream_name, current_buffer = pipes[process.stderr.fileno(
                        )]
                        lines = current_buffer.split(b'\n')
                        stderr_buffer = lines.pop()
                        pipes[process.stderr.fileno()] = (
                            stream_name, stderr_buffer)

                        for line_bytes in lines:
                            line = line_bytes.decode(
                                'utf-8', errors='replace').strip()
                            if line:
                                self.log_signal.emit(f'[STDERR] {line}')

                    last_log_time = current_time

            if process.poll() is not None and not pipes:
                break

        def flush_buffer(buffer, stream_name):
            if buffer.strip():
                try:
                    line = buffer.decode('utf-8', errors='replace').strip()
                    if line:
                        self.log_signal.emit(f'[{stream_name}] {line}')
                except UnicodeDecodeError:
                    pass

        flush_buffer(stdout_buffer, 'STDOUT')
        flush_buffer(stderr_buffer, 'STDERR')

        return_code = process.wait()

        if return_code == 0:
            self.log_signal.emit(
                f'[COMMAND] Command finished successfully. Return code: {return_code}')
        else:
            self.log_signal.emit(
                f'[COMMAND] Command failed. Return code: {return_code}')

        return return_code
