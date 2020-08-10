import threading
import psutil
import os
from modules.reg import fetch_reg
from modules.config import get_config

STEAM64_IDENTIFIER = 76561197960265728


class StoppableThread(threading.Thread):
    def __init__(self, target):
        super(StoppableThread, self).__init__(target=target)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


def check_steam_dir():
    if get_config('steam_path') == 'reg' and os.path.isfile(fetch_reg('SteamPath') + '\\Steam.exe'):
        return True
    elif os.path.isfile(get_config('steam_path') + '\\Steam.exe'):
        return True
    else:
        return False


def test():
    print('Listing current config...')
    print('locale:', get_config('locale'))
    print('autoexit:', get_config('autoexit'))
    print('mode:', get_config('mode'))
    print('try_soft_shutdown:', get_config('try_soft_shutdown'))
    print('show_avatar:', get_config('show_avatar'))
    print('steam_path:', get_config('steam_path'))

    print('Checking registry...')
    for key in ('AutoLoginUser', 'RememberPassword', 'SteamExe', 'SteamPath', 'pid', 'ActiveUser'):
        print(f'{key}:', fetch_reg(key))

    print('Checking Steam.exe location...')
    if check_steam_dir() and get_config('steam_path') == 'reg':
        print('Steam located at', fetch_reg('steampath'))
    elif check_steam_dir():
        print('Steam located at', get_config('steam_path'), '(Manually set)')
    else:
        print('Steam directory invalid')
        return False
    return True


def raise_exception():
    raise Exception


def check_running(process_name):
    '''Check if given process is running and return boolean value.
    :param process_name: Name of process to check
    '''
    for process in psutil.process_iter():
        try:
            if process_name.lower() in process.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied,
                psutil.ZombieProcess):
            pass
    return False


def steam_running():
    """Check if Steam is running"""
    steam_pid = fetch_reg('pid')

    if steam_pid == 0:
        return False

    try:
        process = psutil.Process(pid=steam_pid)
        name = process.name()

        if name.lower() == 'steam.exe':
            return True
        else:
            return False
    except psutil.NoSuchProcess:
        return False


def steam64_to_3(steamid64):
    steamid3 = f'[U:1:{int(steamid64) - STEAM64_IDENTIFIER}]'
    return steamid3


def steam64_to_32(steamid64):
    steamid32 = f'{int(steamid64) - STEAM64_IDENTIFIER}'
    return steamid32


def steam64_to_2(steamid64):
    steamid_n = int(steamid64) - STEAM64_IDENTIFIER

    if steamid_n % 2 == 0:
        steamid_modulo = '0'
    else:
        steamid_modulo = '1'

    steamid2 = f'STEAM_0:{steamid_modulo}:{steamid_n // 2}'

    return steamid2


def open_screenshot(steamid64, steam_path=get_config('steam_path')):
    if steam_path == 'reg':
        steam_path = fetch_reg('steampath')

    if '/' in steam_path:
        steam_path = steam_path.replace('/', '\\')

    os.startfile(f'{steam_path}\\userdata\\{steam64_to_32(steamid64)}\\760\\remote')
