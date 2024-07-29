import re
import urllib.request
from http.client import BadStatusLine
from pathlib import Path
from urllib.error import HTTPError, URLError

import yaml  # type:ignore

VERSIONS_FILE_PATH = Path.cwd() / "bionty_base" / "sources.yaml"


def extract_urls_from_yaml(yaml_file):
    with open(yaml_file) as file:
        yaml_data = yaml.safe_load(file)
        urls = []

        def extract_urls(data):
            if isinstance(data, str):
                urls.extend(
                    re.findall(
                        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                        data,
                    )
                )
            elif isinstance(data, dict):
                for value in data.values():
                    extract_urls(value)
            elif isinstance(data, list):
                for item in data:
                    extract_urls(item)

        extract_urls(yaml_data)

        return urls


urls = extract_urls_from_yaml(VERSIONS_FILE_PATH)

failed_urls = []
for url in urls:
    try:
        assert urllib.request.urlopen(url, timeout=1000).getcode() == 200
    except (URLError, BadStatusLine):
        print(f"URL: {url} is currently not accessible.")
        pass
    except (AssertionError, ValueError, HTTPError) as e:
        failed_urls.append([url, e])

if len(failed_urls) != 0:
    for fail in failed_urls:
        print(fail)
    raise AssertionError(f"{len(failed_urls)} URLs failed.")
