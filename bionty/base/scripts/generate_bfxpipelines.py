import base64
import hashlib
import json
import os
import secrets
import string
from pathlib import Path
from typing import Dict, Optional, Union

from github import Github
from rich.progress import track

BASE_BFX_PIPELINES_PATH = "./scripts/bfxpipelines_info"


def base62(n_char: int) -> str:
    """Like nanoid without hyphen and underscore."""
    alphabet = string.digits + string.ascii_letters.swapcase()
    id = "".join(secrets.choice(alphabet) for i in range(n_char))
    return id


def to_b64_str(bstr: bytes) -> str:
    b64 = base64.urlsafe_b64encode(bstr).decode().strip("=")
    return b64


def hash_str(s: str) -> str:
    bstr = s.encode("utf-8")
    # as we're truncating at a short length, we choose md5 over sha512
    return to_b64_str(hashlib.md5(bstr).digest())


def hash_id(input_id: Optional[str] = None, *, n_char: int) -> str:
    if input_id is None:
        return base62(n_char=n_char)
    else:
        return hash_str(input_id)[:n_char].replace("_", "0").replace("-", "0")


def generate_nf_core_pipelines_info() -> None:
    """Generates a json file that contains all required pipelines information by querying the nf-core Github org."""
    gh_login = Github(os.getenv("GITHUB_TOKEN"))
    nf_core_org = gh_login.get_organization("nf-core")
    blacklist = ["cookiecutter", "tools"]
    nf_core_pipelines = {}

    for repo in track(
        nf_core_org.get_repos(),
        description="Fetching information from nf-core repositories...",
    ):
        if "pipeline" in list(repo.get_topics()):
            if repo.name in blacklist:
                continue

            for version in repo.get_releases():
                actual_version = (
                    version.tag_name if len(version.tag_name) >= 1 else "pre-release"
                )
                pipeline_name = f"{repo.name} v{actual_version}"
                underscore_pipeline_name = (
                    pipeline_name.replace(" ", "_").replace(".", "_").replace("-", "_")
                )

                nf_core_pipelines[underscore_pipeline_name] = {
                    "id": hash_id(pipeline_name, n_char=12),
                    "name": f"nf-core {pipeline_name}",
                    "versions": actual_version,
                    "reference": repo.url,
                }

    with open(f"{BASE_BFX_PIPELINES_PATH}/nf_core_pipelines.json", "w") as f:
        json_data = json.dumps(nf_core_pipelines, indent=4)
        f.write(json_data)


def merge_json_files(pipelines_folder_path: Union[str, Path], output_path: str) -> None:
    """Merge all JSON files in a folder and write the merged data to a new JSON file.

    Args:
        pipelines_folder_path: Path to the folder containing the JSON files.
        output_path: Path to the output JSON file.
    """
    pipelines_folder_path = Path(pipelines_folder_path)
    file_paths = list(pipelines_folder_path.glob("*.json"))

    pipeline_json: Dict = {}

    for file_path in file_paths:
        with open(file_path) as f:
            if not str(file_path).endswith("bfxpipelines.json"):
                pipelines_info = json.load(f)
                pipeline_json = {**pipeline_json, **pipelines_info}

    with open(output_path, "w") as f:
        json.dump(pipeline_json, f, indent=4)


generate_nf_core_pipelines_info()
merge_json_files(
    pipelines_folder_path=BASE_BFX_PIPELINES_PATH,
    output_path=f"{BASE_BFX_PIPELINES_PATH}/bfxpipelines.json",
)
