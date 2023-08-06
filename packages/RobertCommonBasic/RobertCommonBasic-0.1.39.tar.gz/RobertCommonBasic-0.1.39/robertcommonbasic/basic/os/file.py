import os
import shutil

from chardet import detect as chardet_detect
from typing import Union, Optional
from datetime import datetime
from glob import glob
from hashlib import sha1

from .path import create_dir_if_not_exist


def check_file_exist(file_path: str):
    return os.path.exists(file_path)


def check_is_file(file_path: str):
    return os.path.isfile(file_path)


def get_file_size(file_path: str):
    return os.path.getsize(file_path)


def get_file_name(file_path: str):
    return os.path.basename(file_path)


def get_file_folder(file_path: str):
    return os.path.dirname(file_path)


def get_file_create_time(file_path: str):
    return datetime.fromtimestamp(os.path.getctime(file_path))


def get_file_modify_time(file_path: str):
    return datetime.fromtimestamp(os.path.getmtime(file_path))


def get_file_access_time(file_path: str):
    return datetime.fromtimestamp(os.path.getatime(file_path))


def del_file(file_path: str):
    return os.remove(file_path)


def del_folder(file_folder: str):
    shutil.rmtree(file_folder)


def copy_file(src_file_path: str, dst_file_path: str):
    if check_file_exist(src_file_path) is True:
        create_dir_if_not_exist(get_file_folder(dst_file_path))
        return shutil.copyfile(src_file_path, dst_file_path)


def copy_folder(src_folder_path: str, dst_folder_path: str):
    if check_file_exist(src_folder_path) is True:
        create_dir_if_not_exist(dst_folder_path)
        return shutil.copytree(src_folder_path, dst_folder_path)


def move_file(src_file_path: str, dst_file_path: str):
    if check_file_exist(src_file_path) is True:
        dst_folder = get_file_folder(dst_file_path)
        create_dir_if_not_exist(dst_folder)
        return shutil.move(src_file_path, dst_file_path)


def scan_files(glob_path: str, recursive: bool = False):
    return sorted(glob(glob_path, recursive=recursive))


def file_hash(file_path: str):
    if os.path.isfile(file_path):
        hash_sha1 = sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha1.update(chunk)
        return hash_sha1.hexdigest()


# 比较文件
def compare_file(src_path: str, dst_path: str):
    return file_hash(src_path) == file_hash(dst_path)


# 重命名文件
def rename_file(old_path: str, new_path: str):
    if check_file_exist(old_path) is True:
        if check_file_exist(new_path) is True:
            del_file(new_path)
        os.rename(old_path, new_path)


def get_file_encoding(file_path: str):
    with open(file_path, 'rb') as f:
        return chardet_detect(f.read(1024))['encoding']


# 写文件
def save_file(file_path: str, file_content: Union[str, bytes], file_encoding: Optional[str] = None, file_mode: Optional[str] = None):
    create_dir_if_not_exist(get_file_folder(file_path))
    if isinstance(file_content, str):
        with open(file_path, 'w' if file_mode is None else file_mode, encoding=file_encoding) as f:
            f.write(file_content)
    elif isinstance(file_content, bytes):
        with open(file_path, 'wb' if file_mode is None else file_mode) as f:
            f.write(file_content)


def read_file(file_path: str, file_mode: str = 'rb'):
    if check_file_exist(file_path) is True:
        return open(file_path, file_mode).read()
    return None
