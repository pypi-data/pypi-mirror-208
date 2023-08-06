"""
Download function for related files in the reality model library
"""
import logging
import re
from tqdm import tqdm
import requests
import os
import hashlib

from openxlab.model.clients.openapi_client import OpenapiClient
from openxlab.model.common.constants import endpoint, token, default_metafile_template_name, model_cache_path

logger = logging.getLogger("openxlab.model")


def download(model_repo, file, path=None, overwrite=False) -> None:
    """
    download model file|meta file|log filee|readme file
    usage: cli & sdk
    """
    try:
        # split params
        username, repository = _split_repo(model_repo)
        client = OpenapiClient(endpoint, token)
        url, file_name, _hash, weight_raw_size = client.get_download_url(repository, file)

    except ValueError as e:
        print(f"Error: {e}")
        return
    path_file = _download_to_local(url, file_name, path, _hash, weight_raw_size, overwrite)
    print("download model repo:{}, file_name:{}".format(model_repo, file_name))
    return path_file


def download_metafile_template(path=None) -> None:
    """
    download metafile template file
    """
    try:
        # split params
        client = OpenapiClient(endpoint, token)
        url = client.get_metafile_template_download_url()
    except ValueError as e:
        print(f"Error: {e}")
        return
    _download_to_local(url, file_name=default_metafile_template_name, path=path)


def _split_repo(model_repo) -> (str, str):
    """
    Split a full repository name into two separate strings: the username and the repository name.
    """
    # username/repository format check
    pattern = r'^[a-zA-Z0-9]+\/[a-zA-Z0-9\-_]+$'
    if not re.match(pattern, model_repo):
        raise ValueError("The input string must be in the format 'didi12/test-d-1'")

    values = model_repo.split('/')
    return values[0], values[1]


def _download_to_local(url, file_name, path=None, _hash=None, weight_raw_size=None, overwrite=False) -> str:
    """
    download file to local with progress_bar
    """
    path_file = file_name
    if path is not None:
        path_file = f"{path}/{file_name}"

    cache_path_file = f'{model_cache_path}/{file_name}'
    if not os.path.exists(model_cache_path):
        os.makedirs(model_cache_path)
    elif os.path.exists(cache_path_file) and overwrite is not True:
        if _hash is not None:
            local_hash = get_file_hash(cache_path_file)
            if local_hash == _hash:
                clear_and_link(cache_path_file, path_file)
                return path_file
        elif weight_raw_size is not None:
            local_size = os.path.getsize(cache_path_file)
            if local_size == weight_raw_size:
                clear_and_link(cache_path_file, path_file)
                return path_file

    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    with open(cache_path_file, 'wb') as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)
    progress_bar.close()
    clear_and_link(cache_path_file, path_file)
    return path_file


def get_file_hash(filename):
    hasher = hashlib.md5()
    with open(filename, 'rb') as file:
        file_size = file.seek(0, 2)
        if file_size <= 128:  # 如果文件小于等于128字节
            combined_block = file.read(file_size)  # 只读取一次，并将所有数据组合在一起
            hasher.update(combined_block)
        else:  # 否则，读取前64字节和后64字节
            file.seek(0)  # 将文件指针移动到文件开头
            first_block = file.read(64)
            hasher.update(first_block)
            file.seek(-64, 2)  # 将文件指针移动到文件末尾-64处
            last_block = file.read(64)
            hasher.update(last_block)
            combined_block = first_block + last_block
            hasher.update(combined_block)

    return hasher.hexdigest()


def clear_and_link(cache_path_file, path_file):
    if os.path.exists(path_file):
        os.remove(path_file)
    if os.path.islink(path_file):
        os.unlink(path_file)
    os.symlink(cache_path_file, path_file)