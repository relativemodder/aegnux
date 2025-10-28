import os
import importlib
from translations.en_US import STRINGS as EN_STRINGS

STRINGS = {}

def get_current_locale() -> str:
    return os.getenv('LANG', 'en_US.UTF-8').split('.')[0]

def load_strings():
    global STRINGS

    locale = get_current_locale()
    
    try:
        mod = importlib.import_module(f'translations.{locale}')
        STRINGS = mod.STRINGS
    except:
        STRINGS = EN_STRINGS

def gls(key: str) -> str:
    return STRINGS.get(key, key)