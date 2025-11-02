import os

LOG_THROTTLE_SECONDS=0.1
DESKTOP_FILE_NAME='com.relative.Aegnux'

BASE_DIR = os.getcwd()

AE_ICON_PATH = BASE_DIR + '/icons/aegnux.png'
STYLES_PATH = BASE_DIR + '/styles'

WINE_RUNNER_DIR = BASE_DIR + '/assets/wine'
WINETRICKS_BIN = BASE_DIR + '/bin/winetricks'
CABEXTRACT_BIN = BASE_DIR + '/bin/cabextract'
GDIPLUS_DLL = BASE_DIR + '/assets/gdiplus.dll'
FONTSMOOTH_REG = BASE_DIR + '/assets/fontsmooth.reg'
DXVK_TAR = BASE_DIR + '/assets/dxvk.tar.gz'
DXVK_REG = BASE_DIR + '/assets/dxvk.reg'

VCR_ZIP = BASE_DIR + '/assets/vcr.zip'
MSXML_ZIP = BASE_DIR + '/assets/msxml3.zip'

WINE_STYLE_REG = STYLES_PATH + '/wine_dark_theme.reg'

AE_DOWNLOAD_URL = 'i dont support piracy'
AE_PLUGINS_URL = 'i dont support piracy either'

AE_FILENAME = '/tmp/ae2024.zip'

DOWNLOAD_CHUNK_SIZE=1024