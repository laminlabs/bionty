import os
import shutil
from pathlib import Path
from typing import Union

import requests  # type:ignore
import yaml  # type:ignore
from rich.progress import Progress

from bionty.base._settings import settings


def load_yaml(
    filename: Union[str, Path], convert_dates: bool = True
):  # pragma: no cover
    with open(filename) as f:
        return yaml.safe_load(f)


def write_yaml(
    data: dict,
    filename: Union[str, Path],
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
    url: str, localpath: Union[str, Path, None] = None, block_size: int = 1024, **kwargs
) -> Union[str, Path, None]:
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
    import botocore.session as session
    from botocore.config import Config

    if localpath is None:
        localpath = settings.datasetdir / filename
    elif localpath.is_dir():
        localpath = localpath / filename

    bucket = assets_base_url.replace("s3://", "")
    s3_client = session.get_session().create_client(
        "s3", config=Config(signature_version=session.UNSIGNED)
    )

    try:
        s3_object = s3_client.get_object(Bucket=bucket, Key=filename)
    except s3_client.exceptions.ClientError:
        return localpath

    cloud_mts = s3_object["LastModified"].timestamp()
    total_content_length = int(s3_object["ContentLength"])

    CHUNK_SIZE = 64 * 1024

    if not localpath.exists() or cloud_mts > localpath.stat().st_mtime:  # type: ignore
        localpath.parent.mkdir(parents=True, exist_ok=True)
        stream = s3_object["Body"]
        if total_content_length > 5000000:
            with Progress(refresh_per_second=10, transient=True) as progress:
                task = progress.add_task(
                    "[red]downloading...", total=total_content_length
                )
                try:
                    with localpath.open(mode="wb") as f:
                        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                            f.write(chunk)
                            progress.update(task, advance=CHUNK_SIZE)
                except Exception as e:
                    if localpath.exists():
                        localpath.unlink()
                    raise e
                # force the progress bar to 100% at the end
                progress.update(task, completed=total_content_length, refresh=True)
        else:
            try:
                with localpath.open(mode="wb") as f:
                    for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                        f.write(chunk)
            except Exception as e:
                if localpath.exists():
                    localpath.unlink()
                raise e
        os.utime(localpath, times=(cloud_mts, cloud_mts))

    return localpath
