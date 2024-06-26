# Copyright 2015-2024 Florian Tautz
# This program is licensed under the MIT License,
# see the contents of the LICENSE file in this directory for details.


import re
from glob import glob
from os import path, makedirs
from datetime import datetime
from shutil import copyfile, move

from esi_utils import character_name


def list_characters(settings_dir):
    characters = []
    filename_regex = re.compile(r'core_char_(?P<charid>\d+)\.dat')
    for entry in glob(path.join(settings_dir, 'core_char_*.dat')):
        filename = path.basename(entry)
        match = filename_regex.match(filename)
        if not match:
            continue
        character_id = int(match.group('charid'))
        characters.append((character_name(character_id), entry))
    return characters


def copy_character_settings(settings_dir):
    character_configs = list_characters(config.settings_dir)
    character_configs.sort(key=lambda c: c[0])
    print("Copy Character Settings")
    copy_settings_dialogue(character_configs)


def list_accounts(settings_dir):
    accounts = []
    filename_regex = re.compile(r'core_user_\d+\.dat')
    for entry in glob(path.join(settings_dir, 'core_user_*.dat')):
        filename = path.basename(entry)
        match = filename_regex.match(filename)
        if not match:
            continue
        user_mtime = datetime.fromtimestamp(path.getmtime(entry)).strftime('%Y-%m-%d %H:%M:%S')
        accounts.append((user_mtime, entry))
    return accounts


def copy_account_settings(settings_dir):
    account_configs = list_accounts(settings_dir)
    account_configs.sort(key=lambda a: a[0], reverse=True)
    print("Copy Account Settings")
    copy_settings_dialogue(account_configs)


def copy_settings_dialogue(fileinfo_list):
    if len(fileinfo_list) == 0:
        raise Exception("no settings files provided")

    for i, fileinfo in enumerate(fileinfo_list):
        print(str(i).rjust(2), fileinfo[0])

    try:
        source_id = int(input('Source index: '))
    except ValueError:
        return

    backup_dir = path.join('backup', datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    makedirs(backup_dir)

    source_info = fileinfo_list.pop(source_id)
    src_path = source_info[-1]

    print(' 0 ALL')
    for i, fileinfo in enumerate(fileinfo_list, start=1):
        print(str(i).rjust(2), fileinfo[0])

    try:
        destination_id = int(input('Destination index: '))
    except ValueError:
        return

    if destination_id > 0:
        fileinfo_list = [fileinfo_list[destination_id - 1]]

    for dst_info in fileinfo_list:
        dst_path = dst_info[-1]
        dst_filename = path.basename(dst_path)
        move(dst_path, path.join(backup_dir, dst_filename))
        copyfile(src_path, dst_path)


if __name__ == '__main__':
    import config
    copy_character_settings(config.settings_dir)
    copy_account_settings(config.settings_dir)
