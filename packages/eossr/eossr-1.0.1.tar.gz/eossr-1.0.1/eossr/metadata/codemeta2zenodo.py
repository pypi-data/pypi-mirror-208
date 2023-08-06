#!/usr/bin/env python

import json
import re
import warnings
from datetime import date
from pathlib import Path

from ..utils import spdx_licenses
from .zenodo import (
    add_escape2020_community,
    add_escape2020_grant,
    validate_zenodo_metadata_deposit,
    write_zenodo_metadata,
)

codemeta_creators_fields = ['author', 'creator', 'maintainer', 'contributor']
codemeta_contributors_fields = ['editor', 'producer', 'publisher', 'provider', 'sponsor']
codemeta_allowed_person_fields = codemeta_creators_fields + codemeta_contributors_fields


def parse_person_schema_property(person_property, contributor_field):
    """
    Parse the Person Schema property correctly

    Parameters:
    --------
    person_property: dict
        dictionary codemeta key with the a list or a single Person property
        item.
    contributor_field : str
        contributor type {'editor', 'producer', 'sponsor'} or publisher,
        although the last one can only happen if `upload_type` is publication

    Returns:
    --------
    zenodo_person: dict
        dictionary with the correct zenodo syntax for all {author, contributor,
        maintainer}.
    """
    zenodo_person = {}

    name = person_property['familyName']
    if 'givenName' in person_property:
        name += f', {person_property["givenName"]}'
    zenodo_person['name'] = name

    # author ID in CodeMeta can be anything, not only ORCID
    # if format is 0000-0000-0000-0000, it is assumed to be an ORCID
    if "@id" in person_property and (
        "orcid.org/" in person_property["@id"] or re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$', person_property["@id"])
    ):
        # reformat "https://orcid.org/0000-0002-5686-2078" to "0000-0002-5686-2078"
        zenodo_person['orcid'] = person_property["@id"].split('orcid.org/')[-1]

    if "affiliation" in person_property:
        zenodo_person['affiliation'] = person_property['affiliation']['name']

    # Parse correctly the contributors
    if contributor_field in codemeta_contributors_fields:

        if contributor_field in ['provider', 'publisher']:
            zenodo_person['type'] = 'Other'
        else:
            # First letter of contributor type MUST be capitalized
            # (not for two words' contributor !)
            zenodo_person['type'] = contributor_field.title()

    return zenodo_person


def add_author_metadata(zenodo_file, codemt_person_entry, person_field):
    """
    Aux function to parse correctly all the authors, contributors and
    maintainers that can be found at the codemeta.json file

    zenodo_file: dict
        metadata dictionary with the zenodo syntax
    codemt_person_entry: list or dict
        metadata dictionary key field with the codemeta syntax
    person_field: str
        codemeta key field specifying creator {author, contributor, maintainer,
        creator}, or contributors {editor, sponsor, producer, project
        manager...}

    """
    full_contacts = {}

    # First create the full contact agenda by field
    if type(codemt_person_entry) is list:

        for person_property in codemt_person_entry:
            zenodo_person = parse_person_schema_property(person_property, person_field)
            # 'name' is the only key that MUST be contained in a
            # person_property at least
            full_contacts[zenodo_person['name']] = zenodo_person
    else:
        zenodo_person = parse_person_schema_property(codemt_person_entry, person_field)
        full_contacts[zenodo_person['name']] = zenodo_person

    # then save each person by field and avoid duplicates
    for person, value in full_contacts.items():

        if person_field in codemeta_creators_fields:

            # Contributors and maintainers in the same zenodo key
            if 'creators' not in zenodo_file:
                zenodo_file['creators'] = []

            if value not in zenodo_file['creators']:
                zenodo_file['creators'].append(full_contacts[person])
        elif person_field in codemeta_contributors_fields:

            if 'contributors' not in zenodo_file:
                zenodo_file['contributors'] = []

            if full_contacts[person] not in zenodo_file['contributors']:
                zenodo_file['contributors'].append(full_contacts[person])


def find_matching_metadata(codemeta_json):
    """
    Please note that the following fields are ASSUMED. If they are not
    correct, change them, or contact us otherwise.
        * "access_right": "open"
        * "language": "eng"

    param codemeta_json: dict
        already parsed dictionary containing the metadata of the codemeta.json
        file

    Returns:
    --------
    metadata_zenodo : dict
        dictionary cotaining the metadata information found at the
        codemeta.json file but written using the Zenodo syntax.
    """

    # All the 'person type' allowed in the CodeMeta schema are listed in the
    # 'codemeta_allowed_person_fields' list.  However, the Zenodo schema
    # does not accept certain codemeta 'person type' properties; like
    # publisher and provider, nor all the extended schema.org 'person type'
    # (actor, director, member, performer ...).
    # The crosswalk will be limited to the 'codemeta_allowed_person_fields'
    # list.
    if not codemeta_json['@context'] == 'https://doi.org/10.5063/schema/codemeta-2.0':
        raise ValueError(
            f"The converter has been developed for codemeta-2.0 "
            f"but the provided context is {codemeta_json['@context']}."
        )

    def append_related_identifiers(metadata_zenodo: dict, meta_dict: dict):
        if 'related_identifiers' in metadata_zenodo:
            if not isinstance(metadata_zenodo['related_identifiers'], list):
                raise TypeError(
                    f"metadata_zenodo['related_identifiers'] should be a list, "
                    f"but is {type(metadata_zenodo['related_identifiers'])}"
                )
            metadata_zenodo['related_identifiers'].append(meta_dict)
        else:
            metadata_zenodo['related_identifiers'] = [meta_dict]
        return metadata_zenodo

    metadata_zenodo = {'language': 'eng', 'access_right': 'open'}

    if "@type" not in codemeta_json or codemeta_json["@type"] == "SoftwareSourceCode":
        metadata_zenodo['upload_type'] = 'software'
    else:
        raise ValueError(
            f"CodeMeta schema has been developed for software, '@type' key must be 'SoftwareSourceCode' "
            f"but is {metadata_zenodo['upload_type']}"
        )

    if 'name' in codemeta_json:
        metadata_zenodo['title'] = codemeta_json['name']

    if 'description' in codemeta_json:
        metadata_zenodo['description'] = codemeta_json['description']

    if (
        'softwareVersion' in codemeta_json
        and 'version' in codemeta_json
        and codemeta_json['softwareVersion'] != codemeta_json['version']
    ):
        raise ValueError('`softwareVersion` and `version` have different values')
    if 'softwareVersion' in codemeta_json:
        metadata_zenodo['version'] = str(codemeta_json['softwareVersion'])
    elif 'version' in codemeta_json:
        metadata_zenodo['version'] = str(codemeta_json['version'])
    else:
        raise TypeError("A version must be provided in codemeta, either with `version` or `softwareVersion`")

    if 'keywords' in codemeta_json:
        if type(codemeta_json['keywords']) == list:
            metadata_zenodo['keywords'] = codemeta_json['keywords']
        else:
            metadata_zenodo['keywords'] = [codemeta_json['keywords']]

    if 'releaseNotes' in codemeta_json:
        metadata_zenodo['notes'] = "Release Notes: " + codemeta_json['releaseNotes']

    if 'citation' in codemeta_json:
        metadata_zenodo['references'] = codemeta_json['citation']

    if 'datePublished' in codemeta_json:
        metadata_zenodo['publication_date'] = codemeta_json['datePublished']
    else:
        metadata_zenodo['publication_date'] = str(date.today())

    for person_type in codemeta_allowed_person_fields:
        if person_type in codemeta_json:
            add_author_metadata(metadata_zenodo, codemeta_json[person_type], person_field=person_type)

    if 'codeRepository' in codemeta_json:
        meta_dict = {
            "scheme": "url",
            "identifier": codemeta_json['codeRepository'],
            "relation": "isDerivedFrom",
            "resource_type": metadata_zenodo['upload_type'],
        }
        metadata_zenodo = append_related_identifiers(metadata_zenodo, meta_dict)

    if 'readme' in codemeta_json:
        meta_dict = {
            "scheme": "url",
            "identifier": codemeta_json['readme'],
            "relation": "isDocumentedBy",
            "resource_type": "publication-softwaredocumentation",
        }
        metadata_zenodo = append_related_identifiers(metadata_zenodo, meta_dict)

    return metadata_zenodo


class CodeMeta2ZenodoController(object):
    """Control the conversion of a codemeta file to a zenodo file"""

    def __init__(self, codemeta_dict):
        assert isinstance(codemeta_dict, dict)
        self.codemeta_data = codemeta_dict
        self.zenodo_data = {}

    @classmethod
    def from_file(cls, codemeta_filename):
        """Load `codemeta_filename` into the converter"""
        with open(codemeta_filename) as infile:
            controller = cls(json.load(infile))
        return controller

    def convert_license(self):
        def strip_spdx_url(license_url):
            return license_url.replace("https://spdx.org/licenses/", "")

        if 'license' not in self.codemeta_data:
            raise KeyError("Missing license in codemeta file")
        record_license = self.codemeta_data.get('license')
        if isinstance(record_license, list):
            spdx = spdx_licenses()
            licenses_ids = [strip_spdx_url(license_url) for license_url in record_license]
            if all([license_id in spdx for license_id in licenses_ids]):
                self.zenodo_data['license'] = 'other-open'
            else:
                warnings.warn(
                    "A list of licenses has been provided but some of them are not SPDX licenses." "Using 'other-open'."
                )
                self.zenodo_data['license'] = 'other-closed'
        else:
            self.zenodo_data['license'] = strip_spdx_url(record_license)

    def convert(self, validate=True):
        """Convert data over to zenodo format"""
        self.zenodo_data = find_matching_metadata(self.codemeta_data)
        self.convert_license()
        if validate:
            self.validate()

    def validate(self):
        """
        Validate the zenodo data.
        """
        validate_zenodo_metadata_deposit(self.zenodo_data)

    def add_escape2020_community(self):
        """
        Add compulsory information to the .zenodo.json file:
         * zenodo community : ESCAPE2020
        """
        add_escape2020_community(self.zenodo_data)

    def add_escape2020_grant(self):
        """
        Add compulsory information to the .zenodo.json file:
         * ESCAPE grant ID (zenodo syntax)
        """
        add_escape2020_grant(self.zenodo_data)

    def write_zenodo(self, zenodo_filename='.zenodo.json', overwrite=False, validate=True):
        """Write `zenodo_filename` after conversion"""
        write_zenodo_metadata(self.zenodo_data, zenodo_filename, overwrite=overwrite, validate=validate)


def converter(codemeta_dict, add_escape2020=True):
    """
    Convert codemeta metadata into zenodo metadata

    :param codemeta_dict: dict
    :param add_escape2020: bool
        if True, add escape2020 community and grant
    :return: dict
        zenodo metadata
    """
    meta_converter = CodeMeta2ZenodoController(codemeta_dict)
    meta_converter.convert()
    if add_escape2020:
        meta_converter.add_escape2020_community()
        meta_converter.add_escape2020_grant()
    return meta_converter.zenodo_data


def parse_codemeta_and_write_zenodo_metadata_file(codemeta_filename, outdir, add_escape2020=True, overwrite=True):
    """
    Reads the codemeta.json file and creates a new `.zenodo.json` file in outdir.
    This file contains the same information that in the codemeta.json file but following the zenodo metadata schema.

    codemeta_filename: str or Path
        path to the codemeta.json file
    outdir: str or Path
        path to the outdir where the file `.zenodo.json` will be created
    add_escape2020: bool
        adds escape2020 metadata in zenodo metadata file
    overwrite: bool
        overwrite existing `.zendoo.json` file in `outdir`
    """
    meta_converter = CodeMeta2ZenodoController.from_file(codemeta_filename)
    meta_converter.convert()
    if add_escape2020:
        meta_converter.add_escape2020_community()
        meta_converter.add_escape2020_grant()
    outfile = Path(outdir).joinpath('.zenodo.json')
    meta_converter.write_zenodo(outfile.name, overwrite=overwrite)
