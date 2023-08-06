import warnings
from datetime import date

import jsonschema
import requests
from jsonref import replace_refs

from ..utils import write_json
from . import valid_semver

_zenodo_valid_licenses = None
_zenodo_deposit_schema = None


def _load_zenodo_deposit_schema():
    def update_dict_recursively(dict1, dict2):
        for key, value in dict2.items():
            if key in dict1 and isinstance(value, dict):
                update_dict_recursively(dict1[key], value)
            else:
                dict1[key] = value

    global _zenodo_deposit_schema
    zenodo_base_schema_url = "https://zenodo.org/schemas/records/base-v1.0.0.json"
    zenodo_deposit_schema_url = "https://zenodo.org/schemas/deposits/records/legacyrecord.json"
    zenodo_base_schema = replace_refs(requests.get(zenodo_base_schema_url).json())
    zenodo_deposit_schema = replace_refs(requests.get(zenodo_deposit_schema_url).json())
    _zenodo_deposit_schema = zenodo_base_schema
    update_dict_recursively(_zenodo_deposit_schema, zenodo_deposit_schema)
    _zenodo_deposit_schema['required'] = ['title', 'upload_type', 'creators', 'description']


class ZenodoMetadataValidationError(Exception):
    pass


def validate_zenodo_metadata_deposit(metadata):
    """
    Validate the zenodo metadata following the description from https://developers.zenodo.org/#representation before
    doing a deposit (upload). Note that once deposited, the metadata schema is different for a record.
    Raise a ValueError if the metadata is not valid.
    Raise warnings for some important metadata.

    Parameters:
    ----------
    metadata: dict
    """
    if "version" in metadata and not valid_semver(metadata["version"]):
        warnings.warn(f"Version {metadata['version']} does not follow the recommended format from semver.org.")

    if _zenodo_deposit_schema is None:
        _load_zenodo_deposit_schema()
    try:
        jsonschema.validate(metadata, _zenodo_deposit_schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ZenodoMetadataValidationError(f"Zenodo metadata is not valid: {e.message}") from e

    # extra checks not in Zenodo schema
    if "publication_date" not in metadata:
        warnings.warn("Missing publication_date in the metadata.")
    else:
        try:
            date.fromisoformat(metadata["publication_date"])
        except ValueError as exc:
            raise ZenodoMetadataValidationError(
                f"Invalid publication_date {metadata['publication_date']}, not isoformat"
            ) from exc

    if "access_right" not in metadata:
        warnings.warn("Missing access_right in the metadata, defaults to open.")
    elif metadata["access_right"] in ["open", "embargoed"]:
        if "license" not in metadata:
            raise ZenodoMetadataValidationError("Missing license")
        elif not (valid_license(metadata["license"])):
            raise ZenodoMetadataValidationError(f"Invalid license {metadata['license']}")
    elif metadata["access_right"] == "restricted":
        if "embargo_date" not in metadata:
            raise ZenodoMetadataValidationError("Missing embargo_date")
        else:
            try:
                date.fromisoformat(metadata["embargo_date"])
            except ValueError as exc:
                raise ZenodoMetadataValidationError("Invalid embargo_date, not isoformat") from exc
    elif metadata["access_right"] == "restricted":
        if "access_conditions" not in metadata:
            raise ZenodoMetadataValidationError("Missing access_conditions")

    return None


def write_zenodo_metadata(zenodo_metadata, filename='.zenodo.json', overwrite=False, validate=True):
    """
    Write the zenodo metadata to a file.

    Parameters:
    ----------
    zenodo_metadata: dict
    filename: str
    """
    if validate:
        validate_zenodo_metadata_deposit(zenodo_metadata)
    write_json(zenodo_metadata, filename, overwrite=overwrite)


def add_escape2020_community(zenodo_metadata):
    """
    Add compulsory information to the Zenodo metadata:
     * zenodo community : ESCAPE2020

    :param zenodo_metadata: Zenodo metadata dictionary
    """
    if 'communities' not in zenodo_metadata:
        zenodo_metadata['communities'] = [{"identifier": "escape2020"}]
    elif all(community['identifier'] != 'escape2020' for community in zenodo_metadata['communities']):
        zenodo_metadata['communities'].append({"identifier": "escape2020"})


def add_escape2020_grant(zenodo_metadata):
    """
    Add compulsory information to the Zenodo metadata:
     * ESCAPE grant ID (zenodo syntax)

    :param zenodo_metadata: Zenodo metadata dictionary
    """
    if 'grants' not in zenodo_metadata:
        zenodo_metadata['grants'] = [{"id": "10.13039/501100000780::824064"}]
    elif all(grant['id'] != '10.13039/501100000780::824064' for grant in zenodo_metadata['grants']):
        zenodo_metadata['grants'].append({"id": "10.13039/501100000780::824064"})


def _load_valid_licenses():
    """
    Load the list of valid licenses from zenodo.org into global variable _zenodo_valid_licenses
    Note: this should use `eossr.api.zenodo.get_licenses` but importing here would lead to a circular import.
    A refactoring of the library is needed to avoid this.
    """
    global _zenodo_valid_licenses
    req = requests.get("https://zenodo.org/api/licenses", {'size': 1000})
    try:
        req.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise requests.exceptions.HTTPError(f"Unable to get the list of licenses from Zenodo: {req.text}") from exc
    _zenodo_valid_licenses = [license["id"] for license in req.json()["hits"]["hits"]]


def valid_license(license_name):
    """
    Validate the license name.

    :param license_name: license name
    :return: True if the license is valid, False otherwise
    """
    global _zenodo_valid_licenses
    if _zenodo_valid_licenses is None:
        _load_valid_licenses()
    return license_name in _zenodo_valid_licenses
