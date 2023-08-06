from contextlib import closing, contextmanager
import copy
from dataclasses import dataclass
from functools import partial
from hashlib import sha256
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
import time
from typing import Optional, TypeVar, Union
import urllib
from urllib.parse import urljoin, urlparse

import requests

from chateval import config
from chateval.utils import logging
from chateval.utils.extract import ExtractManager
from chateval.utils.filelock import FileLock

logger = logging.get_logger(__name__)

T = TypeVar("T", str, Path)


def is_remote_url(url_or_filename: str) -> bool:
    parsed = urlparse(url_or_filename)
    return parsed.scheme in ("http", "https", "s3", "gs", "hdfs", "ftp")


def url_or_path_join(base_name: str, *pathnames: str) -> str:
    if is_remote_url(base_name):
        return posixpath.join(
            base_name,
            *(str(pathname).replace(os.sep, "/").lstrip("/") for pathname in pathnames),
        )
    else:
        return Path(base_name, *pathnames).as_posix()


def is_local_path(url_or_filename: str) -> bool:
    # On unix the scheme of a local path is empty (for both absolute and relative),
    # while on windows the scheme is the drive name (ex: "c") for absolute paths.
    # for details on the windows behavior, see https://bugs.python.org/issue42215
    return urlparse(url_or_filename).scheme == "" or os.path.ismount(
        urlparse(url_or_filename).scheme + ":/"
    )


def is_relative_path(url_or_filename: str) -> bool:
    return urlparse(url_or_filename).scheme == "" and not os.path.isabs(url_or_filename)


def relative_to_absolute_path(path: T) -> T:
    """Convert relative path to absolute path."""
    abs_path_str = os.path.abspath(os.path.expanduser(os.path.expandvars(str(path))))
    return Path(abs_path_str) if isinstance(path, Path) else abs_path_str


def ep_github_url(
    path: str, name: str, scenario=True, revision: Optional[str] = None
) -> str:

    revision = revision or os.getenv("EP_SCRIPTS_VERSION", config.SCRIPTS_VERSION)
    if scenario:
        return config.HUB_SCENARIO_URL.format(revision=revision, path=path, name=name)
    return False  # type: ignore


def cached_path(
    url_or_filename,
    download_config=None,
    **download_kwargs,
) -> str:
    """
    Given something that might be a URL (or might be a local path),
    determine which. If it's a URL, download the file and cache it, and
    return the path to the cached file. If it's already a local path,
    make sure the file exists and then return the path.
    Return:
        Local path (string)
    Raises:
        FileNotFoundError: in case of non-recoverable file
            (non-existent or no cache on disk)
        ConnectionError: in case of unreachable url
            and no cache on disk
        ValueError: if it couldn't parse the url or filename correctly
        requests.exceptions.ConnectionError: in case of internet connection issue
    """
    if download_config is None:
        download_config = DownloadConfig(**download_kwargs)

    cache_dir = download_config.cache_dir or config.DOWNLOADED_SCENARIO_PATH
    if isinstance(cache_dir, Path):
        cache_dir = str(cache_dir)
    if isinstance(url_or_filename, Path):
        url_or_filename = str(url_or_filename)

    if is_remote_url(url_or_filename):
        # URL, so get it from the cache (downloading if necessary)
        output_path = get_from_cache(
            url_or_filename,
            cache_dir=cache_dir,
            force_download=download_config.force_download,
            proxies=download_config.proxies,
            resume_download=download_config.resume_download,
            user_agent=download_config.user_agent,
            local_files_only=download_config.local_files_only,
            use_etag=download_config.use_etag,
            max_retries=download_config.max_retries,
            use_auth_token=download_config.use_auth_token,
            ignore_url_params=download_config.ignore_url_params,
            download_desc=download_config.download_desc,
        )
    elif os.path.exists(url_or_filename):
        # File, and it exists.
        output_path = url_or_filename
    elif is_local_path(url_or_filename):
        # File, but it doesn't exist.
        raise FileNotFoundError(f"Local file {url_or_filename} doesn't exist")
    else:
        # Something unknown
        raise ValueError(
            f"unable to parse {url_or_filename} as a URL or as a local path"
        )

    if output_path is None:
        return output_path

    if download_config.extract_compressed_file:
        output_path = ExtractManager(cache_dir=download_config.cache_dir).extract(
            output_path, force_extract=download_config.force_extract
        )

    return output_path


@dataclass
class DownloadConfig:
    """Configuration for our cached path manager.
    Attributes:
        cache_dir (:obj:`str` or :obj:`Path`, optional): Specify a cache directory
         to save the file to (overwrite the
            default cache dir).
        force_download (:obj:`bool`, default ``False``): If True, re-dowload the
         file even if it's already cached in
            the cache dir.
        resume_download (:obj:`bool`, default ``False``): If True, resume the download
         if incompletly recieved file is
            found.
        proxies (:obj:`dict`, optional):
        user_agent (:obj:`str`, optional): Optional string or dict that will be
         appended to the user-agent on remote
            requests.
        extract_compressed_file (:obj:`bool`, default ``False``): If True and the
         path point to a zip or tar file,
            extract the compressed file in a folder along the archive.
        force_extract (:obj:`bool`, default ``False``): If True when
         extract_compressed_file is True and the archive
            was already extracted, re-extract the archive and override the folder
             where it was extracted.
        delete_extracted (:obj:`bool`, default ``False``): Whether to delete
         (or keep) the extracted files.
        use_etag (:obj:`bool`, default ``True``): Whether to use the ETag HTTP
         response header to validate the cached files.
        num_proc (:obj:`int`, optional): The number of processes to launch to
         download the files in parallel.
        max_retries (:obj:`int`, default ``1``): The number of times to retry
        an HTTP request if it fails.
        use_auth_token (:obj:`str` or :obj:`bool`, optional): Optional string
        or boolean to use as Bearer token
            for remote files on the Datasets Hub. If True, will get token
             from ~/.huggingface.
        ignore_url_params (:obj:`bool`, default ``False``): Whether to strip all
         query parameters and #fragments from
            the download URL before using it for caching the file.
        download_desc (:obj:`str`, optional): A description to be displayed
         alongside with the progress bar while downloading the files.
    """

    cache_dir: Optional[Union[str, Path]] = None
    force_download: bool = False
    resume_download: bool = False
    local_files_only: bool = False
    proxies: Optional[dict] = None
    user_agent: Optional[str] = None
    extract_compressed_file: bool = False
    force_extract: bool = False
    delete_extracted: bool = False
    use_etag: bool = True
    num_proc: Optional[int] = None
    max_retries: int = 1
    use_auth_token: Optional[Union[str, bool]] = None
    ignore_url_params: bool = False
    download_desc: Optional[str] = None

    def copy(self) -> "DownloadConfig":
        return self.__class__(**{k: copy.deepcopy(v) for k, v in self.__dict__.items()})


def ep_hub_url(path: str, name: str, revision: Optional[str] = None) -> str:
    revision = revision or config.HUB_DEFAULT_VERSION
    return config.HUB_SCENARIO_URL.format(path=path, name=name, revision=revision)


def hash_url_to_filename(url, etag=None):
    """
    Convert `url` into a hashed filename in a repeatable way.
    If `etag` is specified, append its hash to the url's, delimited
    by a period.
    If the url ends with .h5 (Keras HDF5 weights) adds '.h5' to the name
    so that TF 2.0 can identify it as a HDF5 file
    (see https://github.com/tensorflow/tensorflow/blob/00fad90125b18b80fe054d
    e1055770cfb8fe4ba3/tensorflow/python/keras/engine/network.py#L1380)
    """
    url_bytes = url.encode("utf-8")
    url_hash = sha256(url_bytes)
    filename = url_hash.hexdigest()

    if etag:
        etag_bytes = etag.encode("utf-8")
        etag_hash = sha256(etag_bytes)
        filename += "." + etag_hash.hexdigest()

    if url.endswith(".py"):
        filename += ".py"

    return filename


class OfflineModeIsEnabled(ConnectionError):
    pass


def _raise_if_offline_mode_is_enabled(msg: Optional[str] = None):
    """Raise an OfflineModeIsEnabled error (subclass of ConnectionError)
    if EP_EVALUATE_OFFLINE is True."""
    if config.EP_SCENARIO_OFFLINE:
        raise OfflineModeIsEnabled(
            "Offline mode is enabled."
            if msg is None
            else "Offline mode is enabled. " + str(msg)
        )


def ftp_head(url, timeout=10.0):
    _raise_if_offline_mode_is_enabled(f"Tried to reach {url}")
    try:
        with closing(urllib.request.urlopen(url, timeout=timeout)) as r:
            r.read(1)
    except Exception:
        return False
    return True


def get_authentication_headers_for_url(
    url: str, use_auth_token: Optional[Union[str, bool]] = None
) -> dict:
    """Handle the HF authentication"""
    headers = {}  # type: ignore
    return headers


def http_get(
    url,
    temp_file,
    proxies=None,
    resume_size=0,
    headers=None,
    cookies=None,
    timeout=100.0,
    max_retries=0,
    desc=None,
):
    headers = copy.deepcopy(headers) or {}
    headers["user-agent"] = "user-agent"  # TODO check
    if resume_size > 0:
        headers["Range"] = f"bytes={resume_size:d}-"
    response = _request_with_retry(
        method="GET",
        url=url,
        stream=True,
        proxies=proxies,
        headers=headers,
        cookies=cookies,
        max_retries=max_retries,
        timeout=timeout,
    )
    if response.status_code == 416:  # Range not satisfiable
        return
    content_length = response.headers.get("Content-Length")
    total = resume_size + int(content_length) if content_length is not None else None
    with logging.tqdm(
        unit="B",
        unit_scale=True,
        total=total,
        initial=resume_size,
        desc=desc or "Downloading",
        disable=not logging.is_progress_bar_enabled(),
    ) as progress:
        for chunk in response.iter_content(chunk_size=1024):
            progress.update(len(chunk))
            temp_file.write(chunk)


def http_head(
    url,
    proxies=None,
    headers=None,
    cookies=None,
    allow_redirects=True,
    timeout=10.0,
    max_retries=0,
) -> requests.Response:
    headers = copy.deepcopy(headers) or {}
    headers["user-agent"] = "user-agent"  # TODO: change
    response = _request_with_retry(
        method="HEAD",
        url=url,
        proxies=proxies,
        headers=headers,
        cookies=cookies,
        allow_redirects=allow_redirects,
        timeout=timeout,
        max_retries=max_retries,
    )
    return response


def _request_with_retry(
    method: str,
    url: str,
    max_retries: int = 0,
    base_wait_time: float = 0.5,
    max_wait_time: float = 2,
    timeout: float = 10.0,
    **params,
) -> requests.Response:
    """Wrapper around requests to retry in case it fails with a ConnectTimeout,
     with exponential backoff.
    Note that if the environment variable EP_EVALUATE_OFFLINE is set to 1,
     then a OfflineModeIsEnabled error is raised.
    Args:
        method (str): HTTP method, such as 'GET' or 'HEAD'.
        url (str): The URL of the resource to fetch.
        max_retries (int): Maximum number of retries, defaults to 0 (no retries).
        base_wait_time (float): Duration (in seconds) to wait before retrying the
         first time. Wait time between
            retries then grows exponentially, capped by max_wait_time.
        max_wait_time (float): Maximum amount of time between two retries, in seconds.
        **params: Params to pass to :obj:`requests.request`.
    """
    _raise_if_offline_mode_is_enabled(f"Tried to reach {url}")
    tries, success = 0, False
    while not success:
        tries += 1
        try:
            response = requests.request(
                method=method.upper(), url=url, timeout=timeout, **params
            )
            success = True
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
        ) as err:
            if tries > max_retries:
                raise err
            else:
                logger.info(
                    f"{method} request to {url} timed out,"
                    f" retrying... [{tries/max_retries}]"
                )
                sleep_time = min(
                    max_wait_time, base_wait_time * 2 ** (tries - 1)
                )  # Exponential backoff
                time.sleep(sleep_time)
    return response


def ftp_get(url, temp_file, timeout=10.0):
    _raise_if_offline_mode_is_enabled(f"Tried to reach {url}")
    try:
        logger.info(f"Getting through FTP {url} into {temp_file.name}")
        with closing(urllib.request.urlopen(url, timeout=timeout)) as r:
            shutil.copyfileobj(r, temp_file)
    except urllib.error.URLError as e:
        raise ConnectionError(e) from None


def get_from_cache(
    url,
    cache_dir=None,
    force_download=False,
    proxies=None,
    etag_timeout=100,
    resume_download=False,
    user_agent=None,
    local_files_only=False,
    use_etag=True,
    max_retries=0,
    use_auth_token=None,
    ignore_url_params=False,
    download_desc=None,
) -> str:
    """
    Given a URL, look for the corresponding file in the local cache.
    If it's not there, download it. Then return the path to the cached file.
    Return:
        Local path (string)
    Raises:
        FileNotFoundError: in case of non-recoverable file
            (non-existent or no cache on disk)
        ConnectionError: in case of unreachable url
            and no cache on disk
    """
    if cache_dir is None:
        cache_dir = config.EP_SCENARIO_CACHE
    if isinstance(cache_dir, Path):
        cache_dir = str(cache_dir)

    os.makedirs(cache_dir, exist_ok=True)

    if ignore_url_params:
        # strip all query parameters and #fragments from the URL
        cached_url = urljoin(url, urlparse(url).path)
    else:
        cached_url = url  # additional parameters may be added to the given URL

    connected = False
    response = None
    cookies = None
    etag = None
    head_error = None

    # Try a first time to file the file on the local file system without eTag (None)
    # if we don't ask for 'force_download' then we spare a request
    filename = hash_url_to_filename(cached_url, etag=None)
    cache_path = os.path.join(cache_dir, filename)

    if os.path.exists(cache_path) and not force_download and not use_etag:
        return cache_path

    # Prepare headers for authentication
    headers = get_authentication_headers_for_url(url, use_auth_token=use_auth_token)
    if user_agent is not None:
        headers["user-agent"] = user_agent

    # We don't have the file locally or we need an eTag
    if not local_files_only:
        if url.startswith("ftp://"):
            connected = ftp_head(url)
        try:
            response = http_head(
                url,
                allow_redirects=True,
                proxies=proxies,
                timeout=etag_timeout,
                max_retries=max_retries,
                headers=headers,
            )
            if response.status_code == 200:  # ok
                etag = response.headers.get("ETag") if use_etag else None
                for k, v in response.cookies.items():
                    # In some edge cases, we need to get a confirmation token
                    if k.startswith("download_warning") and "drive.google.com" in url:
                        url += "&confirm=" + v
                        cookies = response.cookies
                connected = True
                # Fix Google Drive URL to avoid Virus scan warning
                if "drive.google.com" in url and "confirm=" not in url:
                    url += "&confirm=t"
            # In some edge cases, head request returns 400 but the
            # connection is actually ok
            elif (
                (
                    response.status_code == 400
                    and "firebasestorage.googleapis.com" in url
                )
                or (response.status_code == 405 and "drive.google.com" in url)
                or (
                    response.status_code == 403
                    and (
                        re.match(
                            r"^https?://github.com/.*?/.*?/releases/download/.*?/.*?$",
                            url,
                        )
                        or re.match(
                            r"^https://.*?s3.*?amazonaws.com/.*?$", response.url
                        )
                    )
                )
                or (response.status_code == 403 and "ndownloader.figstatic.com" in url)
            ):
                connected = True
                logger.info(f"Couldn't get ETag version for url {url}")
            elif (
                response.status_code == 401
                and config.EP_ENDPOINT in url
                and use_auth_token is None
            ):
                raise ConnectionError(
                    f"Unauthorized for URL {url}. Please use the parameter"
                    f" ``use_auth_token=True`` after logging in with"
                    f" ``huggingface-cli login``"
                )
        except (OSError, requests.exceptions.Timeout) as e:
            # not connected
            head_error = e
            pass

    # connected == False = we don't have a connection, or url doesn't exist,
    # or is otherwise inaccessible.
    # try to get the last downloaded one
    if not connected:
        if os.path.exists(cache_path) and not force_download:
            return cache_path
        if local_files_only:
            raise FileNotFoundError(
                f"Cannot find the requested files in the cached path at {cache_path}"
                f" and outgoing traffic has been"
                " disabled. To enable file online look-ups, set 'local_files_only'"
                " to False."
            )
        elif response is not None and response.status_code == 404:
            raise FileNotFoundError(f"Couldn't find file at {url}")
        _raise_if_offline_mode_is_enabled(f"Tried to reach {url}")
        if head_error is not None:
            raise ConnectionError(f"Couldn't reach {url} ({repr(head_error)})")
        elif response is not None:
            raise ConnectionError(
                f"Couldn't reach {url} (error {response.status_code})"
            )
        else:
            raise ConnectionError(f"Couldn't reach {url}")

    # Try a second time
    filename = hash_url_to_filename(cached_url, etag)
    cache_path = os.path.join(cache_dir, filename)

    if os.path.exists(cache_path) and not force_download:
        return cache_path

    # From now on, connected is True.
    # Prevent parallel downloads of the same file with a lock.
    lock_path = cache_path + ".lock"
    with FileLock(lock_path):  # type: ignore

        if resume_download:
            incomplete_path = cache_path + ".incomplete"

            @contextmanager
            def _resumable_file_manager():
                with open(incomplete_path, "a+b") as f:
                    yield f

            temp_file_manager = _resumable_file_manager
            if os.path.exists(incomplete_path):
                resume_size = os.stat(incomplete_path).st_size
            else:
                resume_size = 0
        else:
            temp_file_manager = partial(
                tempfile.NamedTemporaryFile, dir=cache_dir, delete=False  # type: ignore
            )
            resume_size = 0

        # Download to temporary file, then copy to cache dir once finished.
        # Otherwise you get corrupt cache entries if the download gets interrupted.
        with temp_file_manager() as temp_file:
            logger.info(
                f"{url} not found in cache or force_download set to True,"
                f" downloading to {temp_file.name}"
            )

            # GET file object
            if url.startswith("ftp://"):
                ftp_get(url, temp_file)
            else:
                http_get(
                    url,
                    temp_file,
                    proxies=proxies,
                    resume_size=resume_size,
                    headers=headers,
                    cookies=cookies,
                    max_retries=max_retries,
                    desc=download_desc,
                )

        logger.info(f"storing {url} in cache at {cache_path}")
        shutil.move(temp_file.name, cache_path)

        logger.info(f"creating metadata file for {cache_path}")
        meta = {"url": url, "etag": etag}
        meta_path = cache_path + ".json"
        with open(meta_path, "w", encoding="utf-8") as meta_file:
            json.dump(meta, meta_file)

    return cache_path
