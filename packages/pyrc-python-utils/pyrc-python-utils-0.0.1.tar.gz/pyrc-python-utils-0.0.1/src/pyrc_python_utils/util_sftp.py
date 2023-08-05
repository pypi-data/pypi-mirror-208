# A SFTP convenience wrapper around python-o365 library - https://github.com/paramiko/paramiko
# Source reference - https://github.com/paramiko/paramiko/tree/main/paramiko
# See examples/sftp folder for usage scenarios
# TODO - Enhance error handling
# TODO - Comment code
import os
import re
import stat
from io import BytesIO

import paramiko

# This relative import statement allows scripts and package based calls to work
from . import util_file as util_file


def create_client(host: str, username: str, password: str) -> paramiko.SFTPClient:
    transport = paramiko.Transport((host, 22))
    transport.connect(None, username, password)

    return paramiko.SFTPClient.from_transport(transport)


def close_client(client: paramiko.SFTPClient):
    client.close()


def create_directory(client: paramiko.SFTPClient, remote_path: str):
    if not directory_exists(client, remote_path):
        client.mkdir(remote_path)


def remove_directory(client: paramiko.SFTPClient, remote_path: str):
    if directory_exists(client, remote_path):
        client.rmdir(remote_path)


def remove_file(client: paramiko.SFTPClient, remote_file: str):
    if is_file(client, remote_file):
        client.remove(remote_file)
    else:
        raise IOError(f'remote_file is not a file: {remote_file}')


def rebuild_directory(connection: paramiko.SFTPClient, remote_path: str):
    # Delete directory if it exists, and re-create
    remove_directory(connection, remote_path)
    create_directory(connection, remote_path)


def copy_file(client: paramiko.SFTPClient, source_remote_file: str, target_remote_path: str,
              target_remote_file: str = None, buffer_size=8192, overwrite_target_file: bool = True):
    with client.open(source_remote_file, 'rb') as source_file:

        if target_remote_file:
            full_path = target_remote_path + '/' + target_remote_file
        else:
            full_path = target_remote_path + '/' + os.path.basename(source_remote_file)

        if not overwrite_target_file:
            full_path = get_next_available_filename(full_path)

        with client.open(full_path, 'wb') as destination_file:
            while True:
                data = source_file.read(buffer_size)
                if not data:
                    break
                destination_file.write(data)


def copy_files(client: paramiko.SFTPClient, source_remote_path: str, target_remote_path: str, match_exp: str = None,
               buffer_size=8192):
    # For a remote directory, copy all files or those matching the regex - match_exp
    for remote_file in client.listdir(source_remote_path):
        full_path = source_remote_path + '/' + remote_file
        if is_file(client, full_path) and (match_exp is None or re.match(match_exp, remote_file)):
            copy_file(client, full_path, target_remote_path, buffer_size=buffer_size)


def copy_files_from_list(client: paramiko.SFTPClient, remote_file_list: list, target_remote_path: str,
                         buffer_size=8192):
    for remote_file in remote_file_list:
        copy_file(client, remote_file, target_remote_path, buffer_size=buffer_size)


def move_file(client: paramiko.SFTPClient, source_remote_file: str, target_remote_path: str,
              target_remote_file: str = None, buffer_size=8192, overwrite_target_file: bool = True):
    # Move not supported, so do a copy / remote
    copy_file(client, source_remote_file, target_remote_path, target_remote_file, buffer_size, overwrite_target_file)
    remove_file(client, source_remote_file)


def move_files(client: paramiko.SFTPClient, source_remote_path: str, target_remote_path: str, match_exp: str = None,
               buffer_size=8192):
    # For a remote directory, move all files or those matching the regex - match_exp
    for remote_file in client.listdir(source_remote_path):
        full_path = source_remote_path + '/' + remote_file
        if is_file(client, full_path) and (match_exp is None or re.match(match_exp, remote_file)):
            move_file(client, full_path, target_remote_path, buffer_size=buffer_size)


def move_files_from_list(client: paramiko.SFTPClient, remote_file_list: list, target_remote_path: str,
                         buffer_size=8192):
    for remote_file in remote_file_list:
        move_file(client, remote_file, target_remote_path, buffer_size=buffer_size)


def put_file(client: paramiko.SFTPClient, local_file: str or bytes, remote_path: str, remote_file: str = None,
             overwrite_remote_file: bool = True):
    create_directory(client, remote_path)

    # Remote file name was not provided, so use the local file name
    if not remote_file:
        remote_file = os.path.basename(local_file)

    # If we're asked NOT to overwrite, get next available file name
    if not overwrite_remote_file:
        remote_file = get_next_available_filename(client, remote_path, remote_file)

    # Do the put based on the local file being a path or byte array
    if type(local_file) is str:
        client.put(local_file, remote_path + '/' + remote_file)
    else:
        with BytesIO(local_file) as local_file_obj:
            client.putfo(local_file_obj, remote_path + '/' + remote_file)


def put_files(client: paramiko.SFTPClient, local_path: str, remote_path: str):
    for root, dirs, files in os.walk(local_path):
        for file in files:
            # Get the full path of the file
            local_file = os.path.join(root, file)
            put_file(client, local_file, remote_path, file)


def get_file(client: paramiko.SFTPClient, remote_file: str, local_path: str = None, local_file: str = None,
             as_bytes: bool = False, overwrite_local_file: bool = True) -> list:
    if not is_file(client, remote_file):
        raise IOError(f"remote_file is not a file: {remote_file}")

    # Do we return the get as a byte array?
    if as_bytes:
        with BytesIO() as remote_file_obj:
            client.getfo(remote_file, remote_file_obj)
            remote_file_obj.seek(0)
            return remote_file_obj.read()

    if not local_path:
        raise IOError("local_path needs to be specified if not streaming Get to byte array")

    # Build local file path
    if local_file:
        full_path = os.path.join(local_path, local_file)
    else:
        # Local file name was not provided, so use the remote file name
        full_path = os.path.join(local_path, os.path.basename(remote_file))

    # If we're asked NOT to overwrite, get next available file name
    if not overwrite_local_file:
        full_path = util_file.get_next_available_filename(full_path)

    client.get(remote_file, full_path)


def get_files(client: paramiko.SFTPClient, remote_path: str, local_path: str, match_exp: str = None):
    # For a remote directory, get all files or those matching the regex - match_exp
    for remote_file in client.listdir(remote_path):
        full_path = remote_path + '/' + remote_file
        if is_file(client, full_path) and (match_exp is None or re.match(match_exp, remote_file)):
            get_file(client, full_path, local_path)


def get_files_from_list(client: paramiko.SFTPClient, remote_file_list: list, local_path: str):
    # For the supplied list of remote file paths, copy each one to the local path
    for remote_file in remote_file_list:
        get_file(client, remote_file, os.path.join(local_path, os.path.basename(remote_file)))


def get_file_list(client: paramiko.SFTPClient, remote_path: str, file_match_exp: str = None, dir_match_exp: str = None,
                  recursive: bool = False,
                  max_depth: int = None) -> list:
    # Returns a listing of files (full path) based on a remote directory - supports recursive search, regex filtering
    # and max_depth traversal
    result = []

    def _traverse_directory(current_path, current_depth):
        nonlocal result
        if max_depth is not None and current_depth > max_depth:
            return

        for item in client.listdir(current_path):
            full_path = current_path + '/' + item

            # if this is a file, and it matches the regex (if supplied_), add to the list
            if is_file(client, full_path) and (file_match_exp is None or re.match(file_match_exp, item)):
                result.append(full_path)
            elif is_directory(client, full_path) and recursive and (
                    dir_match_exp is None or re.match(dir_match_exp, item)):
                _traverse_directory(full_path, current_depth + 1)

    _traverse_directory(remote_path, 0)
    return result


def is_directory(client: paramiko.SFTPClient, remote_path: str) -> bool:
    item = client.stat(remote_path)
    if stat.S_ISDIR(item.st_mode):
        return True

    return False


def is_file(client: paramiko.SFTPClient, remote_file: str) -> bool:
    item = client.stat(remote_file)
    if stat.S_ISREG(item.st_mode):
        return True

    return False


def directory_exists(client: paramiko.SFTPClient, remote_path: str) -> bool:
    try:
        client.stat(remote_path)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        raise


def get_next_available_filename(client: paramiko.SFTPClient, remote_path: str, remote_file: str) -> str:
    base, ext = os.path.splitext(remote_file)

    counter = 1
    while True:
        file = f"{base}_{counter}{ext}" if counter > 1 else remote_file
        full_path = os.path.join(remote_path, file)
        if not file_exists(client, full_path):
            break
        counter += 1

    return file


def file_exists(client: paramiko.SFTPClient, remote_file: str) -> bool:
    try:
        client.stat(remote_file)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        raise
