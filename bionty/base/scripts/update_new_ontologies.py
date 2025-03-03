import bioregistry
from bionty.base.dev._handle_sources import parse_sources_yaml
from rich import print

sources = parse_sources_yaml()
latest_versions = (
    sources.groupby("source")["version"]
    .apply(
        lambda version: version.iloc[
            version.astype(str).str.replace(".", "").str.isdigit().argmax()
        ]
    )
    .reset_index()
)
latest_versions_dict = latest_versions.set_index("source")["version"].to_dict()

new_latest_versions: dict[str, str] = {}
for source, current_latest_version in latest_versions_dict.items():
    bioregistry_version = bioregistry.get_version(source)
    if bioregistry_version:
        if bioregistry_version > current_latest_version:
            new_latest_versions[source] = bioregistry_version

if len(new_latest_versions) != 0:
    for source, version in new_latest_versions.items():
        print(
            f"[bold blue]Source: [green]{source}[blue] has a more recent version:"
            f" [green]{version}"
        )
    raise AssertionError(
        f"{len(new_latest_versions.keys())} databases have more recent versions."
    )
