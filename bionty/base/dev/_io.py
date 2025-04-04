import os
import shutil
from pathlib import Path
from typing import Union

import requests  # type:ignore
import yaml  # type:ignore
from lamindb_setup.core.upath import UPath
from rich.progress import Progress

from bionty.base._settings import settings


def load_yaml(filename: str | Path):  # pragma: no cover
    with open(filename) as f:
        return yaml.safe_load(f)


def write_yaml(
    data: dict,
    filename: str | Path,
    sort_keys: bool = False,
    default_flow_style: bool = False,
):  # pragma: no cover
    with open(filename, "w") as f:
        yaml.dump(
            data,
            f,
            sort_keys=sort_keys,
            default_flow_style=default_flow_style,
        )


def url_download(
    url: str, localpath: str | Path | None = None, block_size: int = 1024, **kwargs
) -> str | Path | None:
    """Downloads a file to a specified path.

    Args:
        url: The URL to download.
        localpath: The path to download the file to.
        block_size: Buffer size in bytes for sending a file-like message body.
        **kwargs: Keyword arguments are passed to 'requests'

    Returns:
        The localpath file is downloaded to

    Raises:
        HttpError: If the request response is not 200 and OK.
    """
    if url.startswith("file://"):
        url = url.split("file://")[-1]
        shutil.copy(url, localpath)
        return localpath
    try:
        response = requests.get(url, stream=True, allow_redirects=True, **kwargs)
        response.raise_for_status()

        total_content_length = int(response.headers.get("content-length", 0))
        if localpath is None:
            localpath = url.split("/")[-1]

        if total_content_length > 5000000:
            with Progress(refresh_per_second=10, transient=True) as progress:
                task = progress.add_task(
                    "[red]downloading...", total=total_content_length
                )

                with open(localpath, "wb") as file:
                    for data in response.iter_content(block_size):
                        file.write(data)
                        progress.update(task, advance=block_size)
                # force the progress bar to 100% at the end
                progress.update(task, completed=total_content_length, refresh=True)
        else:
            with open(localpath, "wb") as file:
                for data in response.iter_content(block_size):
                    file.write(data)

        return localpath

    except requests.exceptions.HTTPError as err:
        raise err


def s3_bionty_assets(
    filename: str, localpath: Path = None, assets_base_url: str = "s3://bionty-assets"
):
    """Synchronizes a S3 file path with local file storage.

    If the file does not exist locally it gets downloaded to datasetdir/filename or the passed localpath.
    If the file does not exist on S3, the file does not get synchronized, no erroring.

    Args:
        filename: The suffix of the assets_base_url.
        localpath: Local base path of the file to sync.
        assets_base_url: The S3 base URL. Prefix of the filename.

    Returns:
        A Path object of the synchronized path.
    """
    if localpath is None:
        localpath = settings.datasetdir / filename
    else:  # it errors on reticulate if we pass a directory
        if localpath.exists():
            assert localpath.is_file(), (
                f"localpath {localpath} has to be a file path, not a directory"
            )
    # this requires s3fs, but it is installed by lamindb
    # skip_instance_cache=True to avoid interference with cached filesystems
    # especially with their dircache
    remote_path = (
        UPath(
            assets_base_url,
            skip_instance_cache=True,
            use_listings_cache=True,
            anon=True,
        )
        / filename
    )
    # check that the remote path exists and is available
    try:
        remote_stat = remote_path.stat()
    except (FileNotFoundError, PermissionError):
        return localpath
    # this is needed unfortunately because s3://bionty-assets doesn't have ListObjectsV2
    # for anonymous users. And ListObjectsV2 is triggred inside .synchronize if no cache is present
    parent_path = remote_path.parent.path.rstrip("/")
    remote_path.fs.dircache[parent_path] = [remote_stat.as_info()]
    # synchronize the remote path
    remote_path.synchronize(localpath, error_no_origin=False, print_progress=True)
    # clean the artificial cache
    del remote_path.fs.dircache[parent_path]

    return localpath
