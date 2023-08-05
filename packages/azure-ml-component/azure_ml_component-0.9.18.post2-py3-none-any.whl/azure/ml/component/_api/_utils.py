# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import base64
import os
import re
import shutil
import requests
import zipfile
import posixpath
import ntpath
import hashlib

from io import SEEK_SET
from pathlib import Path
from requests.adapters import DEFAULT_POOLSIZE, HTTPAdapter
from typing import Union, List, Iterable, Any, Tuple, Optional
from pathlib import PosixPath, PureWindowsPath

from azureml._base_sdk_common.utils import get_retry_policy
from azureml.exceptions import UserErrorException
from azureml._project.ignore_file import IgnoreFile, get_project_ignore_file

_RE_GITHUB_URL = re.compile(r'^(https://github.com/[\w\-.]+/[\w\-.]+)')
_EMPTY_GUID = '00000000-0000-0000-0000-000000000000'
CHUNK_SIZE = 1024
hash_type = type(hashlib.md5())


def _get_content_md5(data):
    md5 = hashlib.md5()
    if isinstance(data, bytes):
        md5.update(data)
    elif hasattr(data, 'read'):
        pos = 0
        try:
            pos = data.tell()
        except Exception:
            pass
        for chunk in iter(lambda: data.read(4096), b""):
            md5.update(chunk)
        try:
            data.seek(pos, SEEK_SET)
        except (AttributeError, IOError):
            raise ValueError('data should be a seekable file-like/io.IOBase type stream object.')
    else:
        raise ValueError('data should be of type bytes or a readable file-like/io.IOBase stream object.')

    return base64.b64encode(md5.digest()).decode('utf-8')


def _looks_like_a_url(input_str):
    return input_str and (input_str.startswith('http://') or input_str.startswith('https://'))


def _normalize_file_name(target_dir=None, file_name=None, overwrite=False, logger=None):
    """Return a valid full file path to write."""
    if not target_dir:
        target_dir = os.getcwd()
        logger.debug("Target dir is not provided, use cwd: {}".format(target_dir))
    else:
        target_dir = os.path.abspath(target_dir)
        logger.debug("Normalized target dir: {}".format(target_dir))

    target_path = Path(target_dir)
    if not target_path.exists():
        raise UserErrorException("Target dir does not exist.")

    if target_path.is_file():
        raise UserErrorException("Target dir is not a directory.")

    if not file_name:
        raise UserErrorException("File name is required.")

    file_name = _replace_invalid_char_in_file_name(file_name)
    full_file_path = target_path / file_name

    logger.debug("Normalized file name: {}".format(full_file_path))
    if not overwrite and full_file_path.exists():
        raise UserErrorException("File already exists, use --overwrite if you attempt to overwrite.")

    return str(full_file_path)


def _download_file(url, file_name, logger):
    res = requests.get(url, allow_redirects=True, stream=True)

    logger.debug("Create file: {0}".format(file_name))
    with open(file_name, 'wb') as fp:
        # from document, chunk_size=None will read data as it arrives in whatever size the chunks are received.
        # UPDATED: chunk_size could not be None since it will return the whole content as one chunk only
        #          due to the implementation of urllib3, thus the progress bar could not displayed correctly.
        #          Changed to a chunk size of 1024.
        for buf in res.iter_content(chunk_size=1024):
            fp.write(buf)
    logger.debug("Download complete.")


def _download_file_to_local(url, target_dir=None, file_name=None, overwrite=False, logger=None):
    file_name = _normalize_file_name(target_dir=target_dir, file_name=file_name, overwrite=overwrite, logger=logger)

    # download file
    _download_file(url, file_name, logger)
    return file_name


def _make_zipfile(zip_file_path, folder_or_file_to_zip, exclude_function=None):
    """Create an archive with exclusive files or directories. Adapted from shutil._make_zipfile.

    :param zip_file_path: Path of zip file to create.
    :param folder_or_file_to_zip: Directory or file that will be zipped.
    :param exclude_function: Function of exclude files or directories
    """
    with zipfile.ZipFile(zip_file_path, "w") as zf:
        if os.path.isfile(folder_or_file_to_zip):
            zf.write(folder_or_file_to_zip, os.path.basename(folder_or_file_to_zip))
        else:
            for dirpath, dirnames, filenames in os.walk(folder_or_file_to_zip):
                relative_dirpath = os.path.relpath(dirpath, folder_or_file_to_zip)
                for name in sorted(dirnames):
                    full_path = os.path.normpath(os.path.join(dirpath, name))
                    relative_path = os.path.normpath(os.path.join(relative_dirpath, name))
                    if exclude_function and exclude_function(full_path):
                        continue
                    zf.write(full_path, relative_path)
                for name in filenames:
                    full_path = os.path.normpath(os.path.join(dirpath, name))
                    relative_path = os.path.normpath(os.path.join(relative_dirpath, name))
                    if exclude_function and exclude_function(full_path):
                        continue
                    if os.path.isfile(full_path):
                        zf.write(full_path, relative_path)


def _replace_invalid_char_in_file_name(file_name, rep='_'):
    """Replace all invalid characters (<>:"/\\|?*) in file name."""
    invalid_file_name_chars = r'<>:"/\|?*'
    return "".join(rep if c in invalid_file_name_chars else c for c in file_name)


def _write_file_to_local(content, target_dir=None, file_name=None, overwrite=False, logger=None):
    file_name = _normalize_file_name(target_dir=target_dir, file_name=file_name, overwrite=overwrite, logger=logger)

    # save file
    with open(file_name, 'w') as fp:
        # we suppose that content only use '\n' as EOL.
        fp.write(content)
    return file_name


def get_value_by_key_path(dct, key_path, default_value=None):
    """Given a dict, get value from key path.

    >>> dct = {
    ...     'Employee': {
    ...         'Profile': {
    ...             'Name': 'Alice',
    ...             'Age': 25,
    ...         }
    ...     }
    ... }
    >>> get_value_by_key_path(dct, 'Employee/Profile/Name')
    'Alice'
    >>> get_value_by_key_path(dct, 'Employee/Profile/Age')
    25
    >>> get_value_by_key_path(dct, 'Employee/Profile')
    {'Name': 'Alice', 'Age': 25}
    """
    if not key_path:
        raise ValueError("key_path must not be empty")

    segments = key_path.split('/')
    final_flag = object()
    segments.append(final_flag)

    walked = []

    cur_obj = dct
    for seg in segments:
        # If current segment is final_flag,
        # the cur_obj is the object that the given key path points to.
        # Simply return it as result.
        if seg is final_flag:
            # return default_value if cur_obj is None
            return default_value if cur_obj is None else cur_obj

        # If still in the middle of key path, when cur_obj is not a dict,
        # will fail to locate the values
        if not isinstance(cur_obj, dict):
            # TODO: maybe add options to raise exceptions here in the future
            return default_value

        # Move to next segment
        cur_obj = cur_obj.get(seg)
        walked.append(seg)

    raise RuntimeError("Should never go here")


def try_to_get_value_from_multiple_key_paths(dct, key_path_list, default_value=None):
    """Same as get_value_by_key_path, but try to get from multiple key paths,
       try the given key paths one by one."""
    for key_path in key_path_list:
        value = get_value_by_key_path(dct, key_path=key_path)
        if value is not None:
            return value
    return default_value


def is_absolute(file_path):
    # Here we don't use Path(file).is_absolute because it can only handle the case in current OS,
    # but in our scenario, we may run this code in Windows, but need to check whether the path is posix absolute.
    return posixpath.isabs(file_path) or ntpath.isabs(file_path)


def get_file_path_hash(file_path):
    """Get hash value of a file path."""
    import hashlib
    h = hashlib.sha256()
    h.update(Path(file_path).resolve().absolute().as_posix().encode('utf-8'))
    return h.hexdigest()


def create_or_cleanup_folder(folder_path):
    """If folder doesn't exist, create one; else, clean it up.

    :param folder_path: The folder to create or clean up
    :raises: Exception
    """
    if os.path.isfile(folder_path) or os.path.islink(folder_path):
        os.unlink(folder_path)
    elif os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)


def check_spec_file(spec_file) -> Path:
    """Check if spec file is legal, raise error if illegal."""
    try:
        path = Path(spec_file).resolve()
    except BaseException as e:
        raise UserErrorException('File {} failed to resolve with exception: {}'.format(spec_file, e))

    if not path.exists():
        raise UserErrorException('File {0} not found.'.format(spec_file))

    if path.is_dir():
        raise UserErrorException('spec file could not be a folder.')

    if path.suffix != '.yaml' and path.suffix != '.yml':
        raise UserErrorException('Invalid file {0}. Only accepts *.yaml or *.yml files.'.format(spec_file))
    return path


def default_content_hash_calculator(path):
    """This func is derived from src/azureml-pipeline-core/azureml/pipeline/core/_datasource_builder.py"""
    relative_path_list = []
    if os.path.isfile(path):
        relative_path_list.extend(os.path.basename(path))
        path = os.path.dirname(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path, topdown=True):
            relative_path_list.extend([os.path.relpath(os.path.join(root, name), path) for name in files])
    else:
        raise ValueError("path not found %s" % path)

    if len(relative_path_list) == 0:
        hash = "00000000000000000000000000000000"
    else:
        hasher = hashlib.md5()
        for f in relative_path_list:
            hasher.update(str(f).encode('utf-8'))
            with open(str(os.path.join(path, f)), 'rb') as afile:
                buf = afile.read()
                hasher.update(buf)
        hash = hasher.hexdigest()
    return hash


def create_session_with_retry(retry=3, pool_maxsize=None):
    """
    Create requests.session with retry.
    This function is copied from azureml._base_sdk_common.utils.create_session_with_retry.
    Added parameter pool_size to allow creating session with max pool size.

    :param retry: retry time
    :param pool_maxsize: max pool size
    rtype: Response
    """
    retry_policy = get_retry_policy(num_retry=retry)
    pool_maxsize = DEFAULT_POOLSIZE if pool_maxsize is None else pool_maxsize

    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retry_policy, pool_maxsize=pool_maxsize))
    session.mount('http://', HTTPAdapter(max_retries=retry_policy, pool_maxsize=pool_maxsize))
    return session


def get_component_registration_max_workers():
    # Before Python 3.8, the default max_worker is the number of processors multiplied by 5.
    # It may sends a large number of the uploading snapshot requests that will occur remote refuses requests.
    # In order to avoid retrying the upload requests, max_worker will use the default value in Python 3.8,
    # min(32, os.cpu_count + 4).
    max_workers_env_var = 'AML_COMPONENT_REGISTRATION_MAX_WORKER'
    default_max_workers = min(32, (os.cpu_count() or 1) + 4)
    try:
        max_workers = int(os.environ.get(max_workers_env_var, default_max_workers))
    except ValueError:
        print(
            "Environment variable {} with value {} set but failed to parse. "
            "Use the default max_worker {} as registration thread pool max_worker."
            "Please reset the value to an integer.".format(
                max_workers_env_var, os.environ.get(max_workers_env_var), default_max_workers))
        max_workers = default_max_workers
    return max_workers


def get_directory_hash(path, include_function=None, exclude_function=None):
    """
    Get the hash of files in the directory.

    :type path: str
    :type include_function: Callable
    :type exclude_function: Callable

    :rtype: list
    """
    hash_list = []
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            full_path = os.path.normpath(os.path.join(dirpath, name))

            if ((not exclude_function and not include_function)
                    or (exclude_function and not exclude_function(full_path))
                    or (include_function and include_function(full_path))):
                with open(full_path, "rb") as f:
                    hash_list.append(_get_content_md5(f))
    return hash_list


def get_path_hash(file_or_folder_path, exclude_function=None):
    """
    Calculate the hash of the file or folder
    :param file_or_folder_path:
    :type file_or_folder_path: str

    :rtype: list
    """
    if os.path.isfile(file_or_folder_path):
        with open(file_or_folder_path, "rb") as f:
            hash_list = [_get_content_md5(f)]
    else:
        hash_list = get_directory_hash(file_or_folder_path, exclude_function=exclude_function)
    return hash_list


def dict_update(raw, new):
    for key, value in new.items():
        if isinstance(raw.get(key, None), dict) and isinstance(new[key], dict):
            dict_update(raw[key], new[key])
        else:
            raw[key] = new[key]


def get_ignore_file(directory_path: Union[Path, str]) -> Optional[IgnoreFile]:
    return get_project_ignore_file(Path(directory_path).resolve().absolute())


def get_snapshot_content_hash_version():
    return 202208


def convert_windows_path_to_unix(path: Union[str, os.PathLike]) -> PosixPath:
    return PureWindowsPath(path).as_posix()


def traverse_directory(
    root: str,
    files: List[str],
    source: str,
    prefix: str,
    ignore_file: IgnoreFile,
) -> Iterable[Tuple[str, Union[str, Any]]]:
    """Enumerate all files in the given directory and compose paths for them to
    be uploaded to in the remote storage. e.g.
    [/mnt/c/Users/dipeck/upload_files/my_file1.txt,
    /mnt/c/Users/dipeck/upload_files/my_file2.txt] -->

        [(/mnt/c/Users/dipeck/upload_files/my_file1.txt, LocalUpload/<guid>/upload_files/my_file1.txt),
        (/mnt/c/Users/dipeck/upload_files/my_file2.txt, LocalUpload/<guid>/upload_files/my_file2.txt))]

    :param root: Root directory path
    :type root: str
    :param files: List of all file paths in the directory
    :type files: List[str]
    :param source: Local path to project directory
    :type source: str
    :param prefix: Remote upload path for project directory (e.g. LocalUpload/<guid>/project_dir)
    :type prefix: str
    :param ignore_file: The .amlignore or .gitignore file in the project directory
    :type ignore_file: azureml._project.ignore_file.IgnoreFile
    :return: Zipped list of tuples representing the local path and remote destination path for each file
    :rtype: Iterable[Tuple[str, Union[str, Any]]]
    """
    # Normalize Windows paths
    root = convert_windows_path_to_unix(root)
    source = convert_windows_path_to_unix(source)
    working_dir = convert_windows_path_to_unix(os.getcwd())
    project_dir = root[len(str(working_dir)) :] + "/"
    file_paths = [
        convert_windows_path_to_unix(os.path.join(root, name))
        for name in files
        if not ignore_file.is_file_excluded(os.path.join(root, name))
    ]  # get all files not excluded by the ignore file
    file_paths_including_links = {fp: None for fp in file_paths}

    for path in file_paths:
        target_prefix = ""
        symlink_prefix = ""

        # check for symlinks to get their true paths
        if os.path.islink(path):
            target_absolute_path = os.path.join(working_dir, os.readlink(path))
            target_prefix = "/".join([root, str(os.readlink(path))]).replace(project_dir, "/")

            # follow and add child links if the directory is a symlink
            if os.path.isdir(target_absolute_path):
                symlink_prefix = path.replace(root + "/", "")

                for r, _, f in os.walk(target_absolute_path, followlinks=True):
                    target_file_paths = {
                        os.path.join(r, name): symlink_prefix + os.path.join(r, name).replace(target_prefix, "")
                        for name in f
                    }  # for each symlink, store its target_path as key and symlink path as value
                    file_paths_including_links.update(target_file_paths)  # Add discovered symlinks to file paths list
            else:
                file_path_info = {
                    target_absolute_path: path.replace(root + "/", "")
                }  # for each symlink, store its target_path as key and symlink path as value
                file_paths_including_links.update(file_path_info)  # Add discovered symlinks to file paths list
            # Remove original symlink entry now that detailed entry has been added
            del file_paths_including_links[path]

    file_paths = sorted(
        file_paths_including_links
    )  # sort files to keep consistent order in case of repeat upload comparisons
    dir_parts = [convert_windows_path_to_unix(os.path.relpath(root, source)) for _ in file_paths]
    dir_parts = ["" if dir_part == "." else dir_part + "/" for dir_part in dir_parts]
    blob_paths = []

    for (dir_part, name) in zip(dir_parts, file_paths):
        if file_paths_including_links.get(
            name
        ):  # for symlinks, use symlink name and structure in directory to create remote upload path
            blob_path = prefix + dir_part + file_paths_including_links.get(name)
        else:
            blob_path = prefix + dir_part + name.replace(root + "/", "")
        blob_paths.append(blob_path)

    return zip(file_paths, blob_paths)


def _get_file_hash(filename: Union[str, Path], _hash: hash_type) -> hash_type:
    with open(str(filename), "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            _hash.update(chunk)
    return _hash


def _get_upload_files_from_folder(path: Union[str, Path], ignore_file: IgnoreFile) -> List[str]:
    upload_paths = []
    for root, _, files in os.walk(path, followlinks=True):
        upload_paths += list(traverse_directory(root, files, Path(path).resolve(), "", ignore_file=ignore_file))
    return upload_paths


def _get_file_list_content_hash(file_list) -> str:
    # file_list is a list of tuples, (absolute_path, relative_path)

    _hash = hashlib.sha256()
    # Add file count to the hash and add '#' around file name then add each file's size to avoid collision like:
    # Case 1:
    # 'a.txt' with contents 'a'
    # 'b.txt' with contents 'b'
    #
    # Case 2:
    # cspell:disable-next-line
    # 'a.txt' with contents 'ab.txtb'
    _hash.update(str(len(file_list)).encode())
    # Sort by "destination" path, since in this function destination prefix is empty and keep the link name in path.
    for file_path, file_name in sorted(file_list, key=lambda x: str(x[1]).lower()):
        _hash.update(("#" + file_name + "#").encode())
        _hash.update(str(os.path.getsize(file_path)).encode())
    for file_path, file_name in sorted(file_list, key=lambda x: str(x[1]).lower()):
        _hash = _get_file_hash(file_path, _hash)
    return str(_hash.hexdigest())


def get_snapshot_content_hash(path: Union[str, Path], ignore_file: IgnoreFile) -> str:
    """Generating sha256 hash for file/folder, e.g. Code snapshot fingerprints to prevent tampering.
    The process of hashing is:
    1. If it's a link, get the actual path of the link.
    2. If it's a file, append file content.
    3. If it's a folder:
        1. list all files under the folder
        2. convert file count to str and append to hash
        3. sort the files by lower case of relative path
        4. for each file append '#'+relative path+'#' and file size to hash
        5. do another iteration on file list to append each files content to hash.
        The example of absolute path to relative path mapping is:
        [
            ('/mnt/c/codehash/code/file1.txt', 'file1.txt'),
            ('/mnt/c/codehash/code/folder1/file1.txt', 'folder1/file1.txt'),
            ('/mnt/c/codehash/code/Folder2/file1.txt', 'Folder2/file1.txt'),
            ('/mnt/c/codehash/code/Folder2/folder1/file1.txt', 'Folder2/folder1/file1.txt')
        ]
    4. Hash the content and convert to hex digest string.
    """
    # DO NOT change this function unless you change the verification logic together
    actual_path = path
    if os.path.islink(path):
        link_path = os.readlink(path)
        actual_path = link_path if os.path.isabs(link_path) else os.path.join(os.path.dirname(path), link_path)
    if os.path.isdir(actual_path):
        return _get_file_list_content_hash(_get_upload_files_from_folder(actual_path, ignore_file=ignore_file))
    if os.path.isfile(actual_path):
        return _get_file_list_content_hash([(actual_path, Path(actual_path).name)])
    return None
