import re
from functools import lru_cache

import bioregistry
import requests


class OntologyURLError(Exception):
    """Base exception for ontology resolver errors."""

    pass


class OntologyNotFoundError(OntologyURLError):
    """Raised when an ontology cannot be found."""

    pass


class OntologyVersionNotFoundError(OntologyURLError):
    """Raised when a specific version of an ontology cannot be found."""

    pass


@lru_cache(maxsize=128)
def get_ontology_url(prefix: str, version: str | None = None) -> tuple[str, str]:
    """Get a versioned download URL for an ontology based on its CURIE prefix.

    Args:
        prefix: The CURIE prefix (e.g., 'GO', 'MONDO', 'HP')
        version: Optional version string (e.g., '2023-01-01')
                If None, the latest version will be determined.

    Returns:
        Tuple of (download_url, version_string)

    Raises:
        OntologyNotFoundError: If the ontology cannot be found
        OntologyVersionNotFoundError: If no versioned URL can be found
    """
    if not prefix:
        raise ValueError("please provide a prefix")

    # Normalize the prefix
    normalized = bioregistry.normalize_prefix(prefix) or prefix

    # Check if the prefix exists at all
    if not _prefix_exists(normalized):
        raise OntologyNotFoundError(f"ontology with prefix '{prefix}' not found")

    # If specific version requested, try to get it
    if version:
        # Try to get a verified URL for this specific version
        url, ver = _get_specific_version(normalized, version)

        # Only return if we found a valid URL
        if url:
            return url, ver
        else:
            raise OntologyVersionNotFoundError(
                f"version '{version}' of ontology '{prefix}' not found or URL not accessible"
            )

    # For latest version
    url, ver = _get_latest_version(normalized)
    if url:
        return url, ver

    # If we get here, no versioned URL was found
    raise OntologyVersionNotFoundError(
        f"no versioned URL found for ontology '{prefix}'"
    )


def _prefix_exists(prefix: str) -> bool:
    """Check if a prefix exists in any registry."""
    # Check Bioregistry
    if bioregistry.normalize_prefix(prefix):
        return True

    # Check OLS
    try:
        response = requests.head(
            f"https://www.ebi.ac.uk/ols/api/ontologies/{prefix.lower()}", timeout=5
        )
        if response.status_code < 400:
            return True
    except requests.RequestException:
        pass

    # Check OBO Foundry
    if bioregistry.get_obofoundry_prefix(prefix):
        return True

    return False


def _url_exists(url: str) -> bool:
    """Check if a URL exists and returns actual content."""
    # First try a HEAD request (faster)
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code >= 200 and response.status_code < 400:
            # To be extra sure, do a small GET request to verify content
            try:
                get_response = requests.get(url, timeout=10, stream=True)
                if get_response.status_code >= 200 and get_response.status_code < 400:
                    # Read a small chunk to verify we get actual content
                    chunk = next(get_response.iter_content(1024), None)
                    get_response.close()  # Close the connection
                    return chunk is not None
            except (requests.RequestException, StopIteration):
                return False
            return True
    except requests.RequestException:
        return False

    return False


def _get_specific_version(prefix: str, version: str) -> tuple[str | None, str | None]:
    """Get URL for a specific version of an ontology."""
    # Clean version string
    clean_version = version[1:] if version.startswith("v") else version
    obo_prefix = bioregistry.get_obofoundry_prefix(prefix) or prefix

    # First try standard OBO Foundry versioned patterns
    standard_patterns = [
        # Standard OBO versioned pattern with releases directory (most common)
        f"http://purl.obolibrary.org/obo/{obo_prefix.lower()}/releases/{clean_version}/{obo_prefix.lower()}.owl",
        # Alternative version pattern
        f"http://purl.obolibrary.org/obo/{obo_prefix.lower()}/{clean_version}/{obo_prefix.lower()}.owl",
        # Date-based versioning pattern
        f"http://purl.obolibrary.org/obo/{obo_prefix.lower()}/releases/{clean_version}/{obo_prefix.lower()}_{clean_version}.owl",
    ]

    for url in standard_patterns:
        if _url_exists(url):
            return url, clean_version

    # Try variants with different filenames
    file_variants = ["base.owl", "core.owl"]
    base_patterns = [
        f"http://purl.obolibrary.org/obo/{obo_prefix.lower()}/releases/{clean_version}/",
        f"http://purl.obolibrary.org/obo/{obo_prefix.lower()}/{clean_version}/",
    ]

    for base in base_patterns:
        for variant in file_variants:
            url = f"{base}{variant}"
            if _url_exists(url):
                return url, clean_version

    # Try OLS API
    try:
        response = requests.get(
            f"https://www.ebi.ac.uk/ols/api/ontologies/{prefix.lower()}/versions",
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            versions = data.get("_embedded", {}).get("ontologyVersions", [])
            for ver in versions:
                if ver.get("number") == clean_version:
                    config = ver.get("config", {})
                    if "fileLocation" in config:
                        file_location = config["fileLocation"]
                        if _url_exists(file_location):
                            return file_location, clean_version
    except requests.RequestException:
        pass

    return None, None


def _get_latest_version(prefix: str) -> tuple[str | None, str | None]:
    """Get the latest versioned URL for an ontology."""
    # First try OBO Foundry to get latest version
    obo_prefix = bioregistry.get_obofoundry_prefix(prefix) or prefix

    # Try OBO Foundry registry for version info
    version = _get_latest_version_from_obo_foundry(prefix, obo_prefix)
    if version:
        url, ver = _get_specific_version(prefix, version)
        if url:
            return url, ver

    # Try OLS API
    try:
        response = requests.get(
            f"https://www.ebi.ac.uk/ols/api/ontologies/{prefix.lower()}", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            config = data.get("config", {})
            version = config.get("version")
            file_location = config.get("fileLocation")

            # If we have both version and file location from OLS
            if version and file_location:
                # First check if a standard versioned URL exists
                url, ver = _get_specific_version(prefix, version)
                if url:
                    return url, ver

                # If not, use the file location from OLS, but verify it exists
                if _url_exists(file_location):
                    return file_location, version
    except requests.RequestException:
        pass

    return None, None


def _get_latest_version_from_obo_foundry(prefix: str, obo_prefix: str) -> str | None:
    """Extract the latest version from OBO Foundry registry."""
    try:
        response = requests.get(
            "http://obofoundry.org/registry/ontologies.jsonld", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            for ontology in data.get("ontologies", []):
                if (
                    ontology.get("id") == obo_prefix
                    or ontology.get("preferredPrefix") == prefix
                ):
                    # Try to get version from version IRI
                    version_iri = ontology.get("versionIri", "")
                    if version_iri:
                        match = re.search(r"/releases/([^/]+)/", version_iri)
                        if match:
                            return match.group(1)
    except requests.RequestException:
        pass
    return None
