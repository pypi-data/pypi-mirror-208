# A SharePoint convenience wrapper around python-o365 library - https://github.com/O365/python-o365
# Source reference
#   https://github.com/O365/python-o365/blob/master/O365/sharepoint.py
# See examples/sharepoint folder for usage scenarios

import os
from pathlib import Path

from O365 import Account
from O365.drive import Drive, Folder
from O365.sharepoint import Sharepoint, Site


def get_sharepoint(client_id: str, client_secret: str, tenant_id: str) -> Sharepoint:
    credentials = (client_id, client_secret)

    account = Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
    account.authenticate()

    return account.sharepoint()


def get_site_from_sharepoint(sharepoint: Sharepoint, host: str, site_name: str) -> Site:
    # The get_site call expects the spaces to be stripped out of name for lookup purposes
    return sharepoint.get_site(host, 'sites/' + site_name.replace(" ", ""))


def get_document_library_from_site(site: Site, document_library_name: str) -> Drive or None:
    for doc_lib in site.list_document_libraries():
        if doc_lib.name == document_library_name:
            return doc_lib

    return None


def get_document_library(client_id: str, client_secret: str, tenant_id: str, host: str, site_name: str,
                         document_library_name: str) -> Drive or None:
    sharepoint = get_sharepoint(client_id, client_secret, tenant_id)
    site = get_site_from_sharepoint(sharepoint, host, site_name)

    return get_document_library_from_site(site, document_library_name)


def get_folder_items(folder: Folder or Drive) -> list:
    return folder.get_items()


def get_child_files(parent_folder: Folder or Drive) -> list:
    files = []

    for item in get_folder_items(parent_folder):
        if not item.is_folder:
            files.append(item)

    return files


def get_child_folders(parent_folder: Folder or Drive) -> list:
    folders = []

    for item in get_folder_items(parent_folder):
        if item.is_folder:
            folders.append(item)

    return folders


def get_folder(document_library: Drive, folder_path: str or Path) -> Folder or Drive:
    return document_library.get_item_by_path(folder_path)


def get_child_folder(parent_folder: Folder or Drive, name: str) -> Folder or None:
    for parent_folder in parent_folder.get_child_folders():
        if parent_folder.name == name:
            return parent_folder

    return None


def create_folder(document_library: Drive, parent_folder_path: str or Path, name: str) -> Folder:
    # Based on path from doc library, create a folder given a parent path and folder name
    folder = get_folder(document_library, parent_folder_path)
    return create_child_folder(folder, name)


def create_child_folder(parent_folder: Folder or Drive, name: str) -> Folder:
    child_folder = get_child_folder(parent_folder, name)

    # If the folder already exists, return it instead
    if child_folder is not None:
        return child_folder

    if isinstance(parent_folder, Drive):
        parent_folder = parent_folder.get_root_folder()

    # Otherwise create the child folder
    return parent_folder.create_child_folder(name)


def rebuild_child_folder(parent_folder: Folder or Drive, name: str) -> Folder:
    child_folder = get_child_folder(parent_folder, name)

    if child_folder:
        delete_folder(child_folder)

    return create_child_folder(parent_folder, name)


def delete_folder(folder: Folder):
    # Recursive deletion of containing files/folders, then proceed to folder
    folder_items = get_folder_items(folder)
    for item in folder_items:
        if item.is_folder:
            delete_folder(item)
        else:
            item.delete()

    folder.delete()


def upload_file(folder: Folder or Drive, source_file_path: str, target_file_name: str = None):
    if isinstance(folder, Drive):
        folder = folder.get_root_folder()

    folder.upload_file(source_file_path, target_file_name)


def upload_files(folder: Folder or Drive, source_folder_path: str):
    for root, dirs, files in os.walk(source_folder_path):
        for file in files:
            # Get the full path of the file
            source_file_path = os.path.join(root, file)
            upload_file(folder, source_file_path, file)
