from pathlib import Path
from tempfile import NamedTemporaryFile, gettempdir

from bionty_base.dev._handle_sources import parse_sources_yaml
from bionty_base.dev._io import s3_bionty_assets, url_download
from bionty_base.dev._md5 import calculate_md5
from rich import print

df = parse_sources_yaml()

for _index, row in df.iterrows():
    url = row["url"]
    md5 = row["md5"]
    if not md5:
        if not url.startswith("s3"):
            with NamedTemporaryFile() as temp_file:
                tmp_file_path = temp_file.name
                url_download(url, tmp_file_path)
                md5 = calculate_md5(tmp_file_path)
        elif url.startswith("s3"):
            file_name = url.removeprefix("s3://bionty-assets/")
            local_path = Path(f"{gettempdir()}/{file_name}")
            s3_bionty_assets(
                file_name, localpath=local_path, assets_base_url="s3://bionty-assets"
            )
            try:
                md5 = calculate_md5(local_path)
            except FileNotFoundError:
                print(f"[bold red]URL {url} could not be downloaded. Is it on S3?")
                continue
        else:
            raise ValueError(f"URL type for: {url} not recognized")

        print(f"[bold blue]URL: [green]{url} [blue]has md5: [green]{md5}")
