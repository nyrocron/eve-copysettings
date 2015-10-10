import re
from glob import glob
from os import path, mkdir
from datetime import datetime
from shutil import copyfile, move

from eveapi import get_client

api = get_client()


def list_characters(settings_dir):
    characters = []
    filename_regex = re.compile(r'core_char_(?P<charid>\d+)\.dat')
    for entry in glob(path.join(settings_dir, 'core_char_*.dat')):
        filename = path.basename(entry)
        match = filename_regex.match(filename)
        if not match:
            continue
        character_id = int(match.group('charid'))
        character_name = api.character_name(character_id)
        characters.append((character_name, entry))
    return characters


def copy_character_settings(settings_dir):
    character_configs = list_characters(config.settings_dir)
    character_configs.sort(key=lambda c: c[0])
    copy_settings(character_configs)


def list_accounts(settings_dir):
    accounts = []
    filename_regex = re.compile(r'core_user_(?P<userid>\d+).dat')
    for entry in glob(path.join(settings_dir, 'core_user_*.dat')):
        filename = path.basename(entry)
        match = filename_regex.match(filename)
        if not match:
            continue
        #user_id = int(match.group('userid'))
        user_mtime = datetime.fromtimestamp(path.getmtime(entry)).strftime('%Y-%m-%d %H:%M:%S')
        accounts.append((user_mtime, entry))
    return accounts


def copy_account_settings(settings_dir):
    account_configs = list_accounts(settings_dir)
    account_configs.sort(key=lambda a: a[0], reverse=True)
    copy_settings(account_configs)


def copy_settings(fileinfo_list):
    for i, fileinfo in enumerate(fileinfo_list):
        print(str(i).rjust(2), fileinfo[0])

    try:
        source_id = int(input('Source index: '))
    except ValueError:
        return

    backup_dir = path.join('backup', datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    mkdir(backup_dir)

    source_info = fileinfo_list.pop(source_id)
    src_path = source_info[-1]
    for dst_info in fileinfo_list:
        dst_path = dst_info[-1]
        dst_filename = path.basename(dst_path)
        move(dst_path, path.join(backup_dir, dst_filename))
        copyfile(src_path, dst_path)


if __name__ == '__main__':
    import config
    copy_character_settings(config.settings_dir)
    copy_account_settings(config.settings_dir)
