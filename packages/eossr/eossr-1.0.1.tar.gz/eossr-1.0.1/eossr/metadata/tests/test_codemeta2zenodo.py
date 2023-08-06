import json
from os.path import dirname, join, realpath

import pytest

from eossr.metadata import codemeta2zenodo

SAMPLES_DIR = join(dirname(realpath(__file__)), "samples")
ROOT_DIR = dirname(realpath("codemeta.json"))


codemeta_entries = [
    "@context",
    "@type",
    "name",
    "description",
    "license",
    "softwareVersion",
    "developmentStatus",
    "codeRepository",
    "dateCreated",
    "isAccessibleForFree",
    "isPartOf",
    "contIntegration",
    "issueTracker",
    "readme",
    "buildInstructions",
    "operatingSystem",
    "author",
    "contributor",
    "maintainer",
    "funder",
    "funding",
    "programmingLanguage",
    "softwareRequirements",
    "keywords",
    "downloadUrl",
    "dateModified",
    "datePublished",
    "runtimePlatform",
    "releaseNotes",
    "readme",
]

zenodo_entries = [
    "upload_type",
    "title",
    "description",
    "language",
    "access_right",
    "version",
    "keywords",
    "notes",
    "license",
    "publication_date",
    "creators",
    # #"communities",
    # #"grants",
    # #"contributors",
    # #"references",
]


@pytest.fixture()
def tmp_dir(tmp_path):
    test_dir = tmp_path
    test_dir.mkdir(exist_ok=True)
    return test_dir


def test_Codemeta2ZenodoController():
    codemeta_file = join(ROOT_DIR, "codemeta.json")
    converter = codemeta2zenodo.CodeMeta2ZenodoController.from_file(codemeta_file)
    assert converter.codemeta_data != {}
    assert all(key in converter.codemeta_data.keys() for key in codemeta_entries)

    converter.convert()
    assert converter.zenodo_data != {}
    assert converter.zenodo_data["language"] == "eng"
    assert converter.zenodo_data["access_right"] == "open"
    assert all(key in converter.zenodo_data.keys() for key in zenodo_entries)

    converter.add_escape2020_community()
    assert converter.zenodo_data["communities"] == [{"identifier": "escape2020"}]
    converter.add_escape2020_grant()
    assert converter.zenodo_data["grants"] == [{"id": "10.13039/501100000780::824064"}]


@pytest.mark.xfail
def test_codemeta_license_fails():
    codemeta_file = join(ROOT_DIR, "codemeta.json")
    converter = codemeta2zenodo.CodeMeta2ZenodoController.from_file(codemeta_file)
    converter.codemeta_data['license'] = "https://creativecommons.org/licenses/by/4.0/"
    converter.convert()


def test_add_author_metadata():

    with open(join(SAMPLES_DIR, "codemeta_contributors_sample.json")) as f:
        codemeta_metadata = json.load(f)
    zenodo_metadata = {}

    assert all(person in codemeta_metadata.keys() for person in codemeta2zenodo.codemeta_allowed_person_fields)

    for person in codemeta2zenodo.codemeta_allowed_person_fields:
        codemeta2zenodo.add_author_metadata(zenodo_metadata, codemeta_metadata[person], person)

    assert 'creators' in zenodo_metadata
    # 4 'creators' one repeated, should not be duplicated.
    # Maintainer and Contributor. Author and Creator are the same person
    assert len(zenodo_metadata['creators']) == 3

    assert 'orcid' not in zenodo_metadata['creators'][0]
    assert zenodo_metadata['creators'][1]['name'] == 'Maintainer-surname, Maintainer-name'
    assert zenodo_metadata['creators'][1]['orcid'] == '0000-0000-0000-0000'

    assert 'contributors' in zenodo_metadata
    # Editor, Producer, Publisher, Provider and Sponsor
    assert len(zenodo_metadata['contributors']) == 5


def test_parse_person_schema_property():

    with open(join(SAMPLES_DIR, "codemeta_contributors_sample.json")) as f:
        codemeta_metadata = json.load(f)

    for person in codemeta2zenodo.codemeta_contributors_fields:
        zenodo_metadata = codemeta2zenodo.parse_person_schema_property(codemeta_metadata[person], person)
        if person == 'editor':
            assert zenodo_metadata['type'] == 'Editor'
        elif person == 'producer':
            assert zenodo_metadata['type'] == 'Producer'
        elif person == 'sponsor':
            assert zenodo_metadata['type'] == 'Sponsor'
        else:
            assert zenodo_metadata['type'] == 'Other'


# class TestConverting(unittest.TestCase):


def test_converter():
    with open(join(SAMPLES_DIR, "codemeta_sample1.json")) as file:
        codemeta = json.load(file)
    zenodo = codemeta2zenodo.converter(codemeta)
    assert zenodo['communities'][0]['identifier'] == 'escape2020'


def test_sample_file_conversion(tmp_dir):
    codemeta2zenodo.parse_codemeta_and_write_zenodo_metadata_file(join(SAMPLES_DIR, "codemeta_sample1.json"), tmp_dir)
    with open(tmp_dir.joinpath('.zenodo.json').name, 'r') as f:
        zen_meta = json.load(f)
    assert 'related_identifiers' in zen_meta
    assert "https://readme.com" in [ri['identifier'] for ri in zen_meta['related_identifiers']]


def test_root_codemeta_conversion(tmp_dir):
    codemeta2zenodo.parse_codemeta_and_write_zenodo_metadata_file(join(ROOT_DIR, "codemeta.json"), tmp_dir)
    with open(tmp_dir.joinpath('.zenodo.json').name, 'r') as f:
        json.load(f)


@pytest.mark.xfail(raises=KeyError)
def test_no_license_in_codemeta():
    converter = codemeta2zenodo.CodeMeta2ZenodoController({})
    converter.convert_license()


def test_convert_license():
    converter = codemeta2zenodo.CodeMeta2ZenodoController({})
    converter.codemeta_data['license'] = "https://spdx.org/licenses/MIT"
    converter.convert_license()
    assert converter.zenodo_data["license"] == "MIT"

    converter.codemeta_data["license"] = "Apache-2.0"
    converter.convert_license()
    assert converter.zenodo_data["license"] == "Apache-2.0"

    converter.codemeta_data["license"] = ["MIT", "https://spdx.org/licenses/BSD-3-Clause", "Apache-2.0"]
    converter.convert_license()
    assert converter.zenodo_data["license"] == "other-open"
