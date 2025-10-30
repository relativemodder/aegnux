import os

LOG_THROTTLE_SECONDS = 0.1
DESKTOP_FILE_NAME = 'com.relative.Aegnux'

BASE_DIR = os.getcwd()

AE_ICON_PATH = BASE_DIR + '/icons/aegnux.png'
STYLES_PATH = BASE_DIR + '/styles'

WINE_RUNNER_DIR = BASE_DIR + '/assets/wine'
WINETRICKS_BIN = BASE_DIR + '/bin/winetricks'
CABEXTRACT_BIN = BASE_DIR + '/bin/cabextract'

VCR_ZIP = BASE_DIR + '/assets/vcr.zip'
MSXML_ZIP = BASE_DIR + '/assets/msxml3.zip'

WINE_STYLE_REG = STYLES_PATH + '/wine_dark_theme.reg'

AE_DOWNLOAD_URL = 'https://huggingface.co/cutefishae/AeNux-model/resolve/main/2024.zip'
AE_PLUGINS_URL = 'https://huggingface.co/cutefishae/AeNux-model/resolve/main/aenux-require-plugin.zip'

AE_FILENAME = '/tmp/ae2024.zip'

DOWNLOAD_CHUNK_SIZE = 1024

# Directory where imported Windows codecs will be copied
CODECS_DIR = BASE_DIR + '/assets/wine/win_codecs'

# Каталог для хранения пользовательских плагинов
PLUGINS_DIR = BASE_DIR + '/plugins'

# Расширения файлов, считающиеся кодеками при импорте из установки Windows
CODECS_EXTENSIONS = ['.dll', '.ax', '.acm', '.axf', '.axv']

# По умолчанию не перезаписывать существующие файлы при импорте
CODECS_OVERWRITE_BY_DEFAULT = False
