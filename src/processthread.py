import os
import time
import requests
import zipfile
import tarfile
import subprocess
import select
import fcntl
from src.utils import format_size, get_wineprefix_dir, get_wine_bin_path_env
from src.config import DOWNLOAD_CHUNK_SIZE, LOG_THROTTLE_SECONDS
from PySide6.QtCore import QThread, Signal


class ProcessThread(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finished_signal = Signal(bool)
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def download_file_to(self, url: str, filename: str):
        r = requests.get(url, stream=True)
        total = int(r.headers.get('content-length', 0))

        downloaded = 0
        start_time = time.time()
        last_update_time = time.time()  # throttling timer

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

    def unpack_zip(self, zip_file_path: str, extract_to_path: str):
        self.log_signal.emit(
            f'[EXTRACTING] Starting ZIP extraction: {zip_file_path}')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            members = [m for m in zip_ref.infolist() if not m.is_dir()]
            total_files = len(members)
            extracted_files = 0
            last_update_time = time.time()

            os.makedirs(extract_to_path, exist_ok=True)

            for file_info in members:
                if self._is_cancelled:
                    self.log_signal.emit(
                        '[EXTRACTING] ZIP extraction cancelled by user.')
                    self.cancelled.emit()
                    self.finished_signal.emit(False)
                    return

                zip_ref.extract(file_info, extract_to_path)
                extracted_files += 1

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
