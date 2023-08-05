import os

APP_DIR = os.path.join(os.path.expanduser('~'), '.lecture_automator')

def get_app_dir() -> str:
    if not os.path.exists(APP_DIR):
        os.makedirs(APP_DIR)
    return APP_DIR


def get_cache_dir() -> str:
    cache_path = os.path.join(get_app_dir(), 'cache')
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    return cache_path
