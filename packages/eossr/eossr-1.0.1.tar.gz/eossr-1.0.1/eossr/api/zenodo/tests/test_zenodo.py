#!/usr/bin/env python
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pytest
import requests

from eossr import ROOT_DIR
from eossr.api import zenodo
from eossr.api.zenodo import Record, ZenodoAPI, get_record, get_zenodo_records
from eossr.api.zenodo.http_status import HTTPStatusError
from eossr.api.zenodo.zenodo import is_live, query_record

# test deactivated at the moment
# eossr_test_lib_id = 930570  # test library in sandbox (owner: T. Vuillaume)


def test_is_live():
    assert is_live()
    assert is_live(sandbox=True)


class TestZenodoApiSandbox(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestZenodoApiSandbox, self).__init__(*args, **kwargs)
        self.token = 'FakeToken'
        self.zenodo = ZenodoAPI(access_token=self.token, sandbox=True)

        # getting all records for tests purposes
        self.zenodo.parameters['size'] = 1000
        self.zenodo.parameters['all_versions'] = True

    def test_initialization_sandbox(self):
        assert isinstance(self.zenodo, ZenodoAPI)
        assert self.zenodo.api_url == 'https://sandbox.zenodo.org/api'
        assert self.zenodo.access_token == self.token
        assert self.zenodo.path_codemeta_file(ROOT_DIR) == ROOT_DIR.joinpath('codemeta.json')
        assert self.zenodo.path_zenodo_file(ROOT_DIR) == ROOT_DIR.joinpath('.zenodo.json')

    def test_query_community_entries(self):
        community_entries = self.zenodo.query_community_records('escape2020')
        assert isinstance(community_entries, requests.models.Response)


class TestZenodoAPINoToken(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestZenodoAPINoToken, self).__init__(*args, **kwargs)
        self.token = ''
        self.zenodo = ZenodoAPI(access_token=self.token, sandbox=False)

    def test_initialization(self):
        assert isinstance(self.zenodo, ZenodoAPI)
        assert self.zenodo.api_url == 'https://zenodo.org/api'
        assert self.zenodo.access_token == self.token

    @pytest.mark.xfail(raises=ValueError)
    def test_raise_token_status(self):
        # A value error should be raised as no valid token was provided
        self.zenodo._raise_token_status()


@pytest.mark.skipif(os.getenv('SANDBOX_ZENODO_TOKEN') is None, reason="SANDBOX_ZENODO_TOKEN not defined")
class TestZenodoAPITokenSandbox(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestZenodoAPITokenSandbox, self).__init__(*args, **kwargs)
        self.token = os.getenv('SANDBOX_ZENODO_TOKEN')
        self.zenodo = ZenodoAPI(access_token=self.token, sandbox=True)

    def test_init(self):
        assert self.zenodo.access_token == os.getenv('SANDBOX_ZENODO_TOKEN')

    def test_raise_token_status(self):
        self.zenodo._raise_token_status()

    def test_query_user_deposits(self):
        self.zenodo.query_user_deposits()

    def test_create_erase_new_deposit(self):
        create_new_deposit = self.zenodo.create_new_deposit()
        assert isinstance(create_new_deposit, requests.models.Response)
        record_id = create_new_deposit.json()['id']
        erase_deposit = self.zenodo.erase_deposit(record_id)
        assert isinstance(erase_deposit, requests.models.Response)

    def test_upload_package(self):
        # TODO: implement pytest unit test and fixture
        # prepare upload in a tmpdir
        with tempfile.TemporaryDirectory() as tmpdirname:
            print(f"tmpdir {tmpdirname}")
            shutil.copy(ROOT_DIR.joinpath('codemeta.json'), tmpdirname)
            _, filename = tempfile.mkstemp(dir=tmpdirname)
            Path(filename).write_text('Hello from eossr unit tests')

            # create new record
            new_record_id = self.zenodo.upload_dir_content(tmpdirname, publish=False)
            self.zenodo.erase_deposit(new_record_id)
            print(f"{new_record_id} created and deleted")

            # update existing record
            # Test deactivated on July 2022 as making new versions of records seems not possible anymore on sandbox,
            # and I am reluctant to do unit tests directly on Zenodo.
            # new_record_id = self.zenodo.upload_dir_content(tmpdirname, record_id=eossr_test_lib_id, publish=False)
            # self.zenodo.erase_entry(new_record_id)
            # print(f"{new_record_id} created and deleted")

    @pytest.mark.skipif(
        os.getenv('SANDBOX_ZENODO_TOKEN_GARCIA') is None, reason="SANDBOX_ZENODO_TOKEN_GARCIA not defined"
    )
    def test_pending_request(self):
        zk = ZenodoAPI(os.getenv('SANDBOX_ZENODO_TOKEN_GARCIA'), sandbox=True)
        record_id = 970583
        from eossr.api.ossr import escape_community

        # Add to escape2020 community and test request
        meta = {'communities': [{'identifier': escape_community}]}
        zk.update_record_metadata(record_id, meta)

        # Well.... we should test this but sandbox is sometimes too slow and make this test fail unpredictably
        # Give some time to zenodo to process the request and update its database
        # time.sleep(10)
        # records = self.zenodo.get_community_pending_requests('escape2020')
        # assert record_id in [rec.id for rec in records]

        # TODO: After accept_pending_request is implemented
        # self.zenodo.accept_pending_request(escape_community, record_id)
        # records = get_zenodo_records(community=escape_community, sandbox=True, size=4)
        # assert record_id in [rec.id for rec in records]

        # Remove from community
        meta = {'communities': []}
        zk.update_record_metadata(record_id, meta)
        records = get_zenodo_records(community=escape_community, sandbox=True, size=4)
        assert record_id not in [rec.id for rec in records]

    def test_get_community_pending_requests(self):
        z = self.zenodo
        records = z.get_community_pending_requests('escape2020')
        records_ids = [rec.id for rec in records]
        assert 532458 in records_ids  # pending request in escape2020 sandbox community - 2021-11-28


@pytest.mark.skipif(os.getenv('ZENODO_TOKEN') is None, reason="ZENODO_TOKEN not defined")
class TestZenodoAPIToken(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestZenodoAPIToken, self).__init__(*args, **kwargs)
        self.token = os.getenv('ZENODO_TOKEN')
        self.zenodo = ZenodoAPI(access_token=self.token, sandbox=False)

    def test_get_user_records(self):
        records = self.zenodo.get_user_records()
        assert isinstance(records[0], Record)

    def test_find_similar_records_sandbox(self):
        self.zenodo.parameters.update({'size': 100})
        existing_record = Record.from_id(939075, sandbox=True)  # One of the copies of eossr
        assert len(self.zenodo.find_similar_records(existing_record)) > 0
        not_existing_record = Record.from_id(767507, sandbox=True)  # Sandbox E.GARCIA ZenodoCI_vTest Records
        assert self.zenodo.find_similar_records(not_existing_record) == []


def test_get_zenodo_records():
    zenodo_records = get_zenodo_records('ESCAPE template project', all_versions=True)
    assert len(zenodo_records) > 1
    all_dois = [r.data['doi'] for r in zenodo_records]
    assert '10.5281/zenodo.4923992' in all_dois


@pytest.mark.xfail(raises=HTTPStatusError)
def test_get_record_42():
    get_record(42)


def test_query_record_941144():
    # unsubmitted record in T. Vuillaume's sandbox - for test purposes
    answer = query_record(941144, sandbox=True)
    assert answer.status_code == 404


@pytest.mark.xfail(raises=HTTPStatusError)
def test_get_record_941144():
    get_record(941144, sandbox=True)


@pytest.fixture
def record_4923992():
    return get_record(4923992)


def test_record(record_4923992):
    assert record_4923992.data['conceptdoi'] == '10.5281/zenodo.3572654'
    record_4923992.print_info()
    codemeta = record_4923992.get_codemeta()
    assert isinstance(codemeta, dict)
    assert codemeta['name'] == 'ESCAPE template project'
    record_4923992.get_mybinder_url()


def test_get_record_sandbox():
    record = get_record(520735, sandbox=True)
    assert record.data['doi'] == '10.5072/zenodo.520735'


def test_write_record_zenodo(record_4923992, tmpdir):
    record_4923992._write_zenodo_deposit(filename=tmpdir / '.zenodo.json', validate=False)
    with open(tmpdir / '.zenodo.json') as file:
        json_dict = json.load(file)
    assert json_dict['title'] == 'ESCAPE template project'
    assert json_dict['version'] == 'v2.2'


def test_search_records():
    records = zenodo.search_records('conceptrecid:5524912')
    assert records[0]['metadata']['title'] == 'eossr'


def test_search_funders():
    funders = zenodo.search_funders('name:European+Commission')
    assert len(funders) > 1


def test_search_grants():
    grants = zenodo.search_grants('code:824064')
    assert len(grants) == 1
    assert grants[0]['metadata']['acronym'] == 'ESCAPE'


def test_search_license():
    licenses = zenodo.search_licenses('id:MIT')
    assert licenses[0]['metadata']['title'] == 'MIT License'


def test_search_communities():
    communities = zenodo.search_communities('escape2020')
    assert communities[0]['title'] == 'ESCAPE OSSR'


def test_get_associated_versions():
    record = Record.from_id(4786641)  # ZenodoCI deprecated lib. A single version
    versions = record.get_associated_versions()
    assert len(versions) == 1
    assert list(versions)[0] == record.id  # itself
    eossr_record = Record.from_id(6352039)
    eossr_record_versions = eossr_record.get_associated_versions()
    assert len(eossr_record_versions) >= 7  # Seven versions, to date 21/03/2022
    for recid, version in eossr_record_versions.items():
        assert eossr_record.data['conceptrecid'] == Record.from_id(recid).data['conceptrecid']
    assert eossr_record_versions[5524913] == 'v0.2'  # ID of eOSSR version v0.2


@pytest.mark.xfail(raises=FileNotFoundError)
def test_get_codemeta_fail():
    record = Record.from_id(3734091)
    record.get_codemeta()


def test_get_supported_licenses():
    zenodo_licenses = zenodo.get_supported_licenses()
    assert isinstance(zenodo_licenses, list)
    assert 'MIT' in zenodo_licenses
    assert 'Apache-2.0' in zenodo_licenses
    assert "Apache License x." not in zenodo_licenses


def test_download_record():
    with tempfile.TemporaryDirectory() as tmpdir:
        record = Record.from_id(3743490)
        record.download(tmpdir)
        assert os.path.exists(f'{tmpdir}/template_project_escape-v1.1.zip')
