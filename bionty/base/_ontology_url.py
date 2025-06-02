from functools import lru_cache

import requests


def import_bioregistry():
    """Import bioregistry module if available."""
    try:
        import bioregistry

        return bioregistry
    except ImportError:
        raise ImportError(
            "Please install bioregistry with `pip install bioregistry`."
        ) from None


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
    bioregistry = import_bioregistry()

    if not prefix:
        raise ValueError("please provide a prefix")

    # Normalize the prefix
    normalized = bioregistry.normalize_prefix(prefix) or prefix

    # Check if the prefix exists at all
    if not _prefix_exists(normalized):
        raise OntologyNotFoundError(f"ontology with prefix '{prefix}' not found")

    # If specific version requested, try to get it
    if version:
        # try standard versioned URL patterns
        url, ver = _get_specific_version(normalized, version)
        if url:
            return url, ver

        raise OntologyVersionNotFoundError(
            f"version '{version}' of ontology '{prefix}' not found"
        )

    # For latest version
    url, ver = _get_latest_from_ols4(normalized)
    if url:
        return url, ver

    # If we get here, no versioned URL was found
    raise OntologyVersionNotFoundError(
        f"no versioned URL found for ontology '{prefix}'"
    )


def _prefix_exists(prefix: str) -> bool:
    """Check if a prefix exists in any registry."""
    bioregistry = import_bioregistry()

    if bioregistry.normalize_prefix(prefix):
        return True

    # Check OLS4
    try:
        response = requests.head(
            f"https://www.ebi.ac.uk/ols4/api/ontologies/{prefix.lower()}", timeout=5
        )
        if response.status_code < 400:
            return True
    except requests.RequestException:
        pass

    return False


def _url_exists(url: str) -> bool:
    """Check if a URL exists and returns a valid response."""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code >= 200 and response.status_code < 400
    except requests.RequestException:
        return False


def _extract_version_from_iri(version_iri: str | None):
    """Extract version from an IRI string by taking the second-to-last path component."""
    if isinstance(version_iri, str):
        # If we have at least two parts, return the second-to-last
        parts = version_iri.split("/")
        if len(parts) >= 2:
            return parts[-2].removeprefix("v")


def _get_specific_version(prefix: str, version: str) -> tuple[str | None, str | None]:
    """Get URL for a specific version of an ontology using standard patterns."""
    bioregistry = import_bioregistry()

    # Clean version string
    clean_version = version[1:] if version.startswith("v") else version
    obo_prefix = bioregistry.get_obofoundry_prefix(prefix) or prefix

    # Try standard OBO Foundry versioned patterns
    standard_patterns = [
        # Direct version path
        f"http://purl.obolibrary.org/obo/{obo_prefix.lower()}/{clean_version}/{obo_prefix.lower()}.owl",
        # Releases directory
        f"http://purl.obolibrary.org/obo/{obo_prefix.lower()}/releases/{clean_version}/{obo_prefix.lower()}.owl",
        # Semantic version with v prefix
        f"http://purl.obolibrary.org/obo/{obo_prefix.lower()}/v{clean_version}/{obo_prefix.lower()}.owl",
    ]

    for url in standard_patterns:
        if _url_exists(url):
            return url, clean_version

    return None, None


def _get_latest_from_ols4(prefix: str) -> tuple[str | None, str | None]:
    """Get the latest version information from OLS4."""
    try:
        response = requests.get(
            f"https://www.ebi.ac.uk/ols4/api/ontologies/{prefix.lower()}", timeout=30
        )
        if response.status_code != 200:
            return None, None

        data = response.json()
        config = data.get("config", {})

        # Get version information
        version = config.get("version")

        # Check versionIri first (preferred source)
        version_iri = config.get("versionIri")
        if version_iri and _url_exists(version_iri):
            # If we have a versionIri and it exists, use it
            # Extract version from IRI if not already provided
            if not version:
                version = _extract_version_from_iri(version_iri)
            return version_iri, version

        # Fall back to fileLocation if available
        file_location = config.get("fileLocation")
        if file_location and _url_exists(file_location):
            if not version and version_iri:
                # even when version_iri is not accessible, we can still extract the version, for example: pw
                version = _extract_version_from_iri(version_iri)
            return file_location, version

        # No valid URLs found
        return None, None

    except requests.RequestException:
        return None, None
