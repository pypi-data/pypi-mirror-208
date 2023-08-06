#!/usr/bin/env python

import concurrent.futures
import json
import os
import pprint
import re
import sys
import textwrap
import warnings
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, urlretrieve

import requests

from ...metadata.codemeta2zenodo import converter, parse_codemeta_and_write_zenodo_metadata_file
from ...metadata.zenodo import write_zenodo_metadata
from ...utils import get_codemeta_from_zipurl, write_json
from . import http_status

__all__ = [
    'zenodo_api_url',
    'zenodo_sandbox_api_url',
    'ZenodoAPI',
    'SimilarRecordError',  # noqa
    'Record',
    'query_zenodo_records',
    'get_zenodo_records',
    'query_record',
    'get_record',
    'get_supported_licenses',
    'search_records',
    'search_funders',
    'search_grants',
    'search_communities',
    'search_licenses',
    'is_live',
]

zenodo_api_url = "https://zenodo.org/api"
zenodo_sandbox_api_url = "https://sandbox.zenodo.org/api"

_default_size_query = 50


class ZenodoAPI:
    def __init__(self, access_token=None, sandbox=False):
        """
        Manages the communication with the (sandbox.)zenodo REST API through the Python request library.
        The client would allow to perform the following tasks within the (sandbox.)zenodo api environment:

          - Fetches a user's published entries,
          - Creates a new deposit,
          - Fetches any published record,
          - Creates a new version of an existing deposit,
          - Uploads files to a specific Zenodo deposit,
          - Erases a non-published deposit / new version draft,
          - Erases (old version) files from an deposit (when creating a new_version deposit and uploading
            new_version files),
          - Uploads information to the deposit (Zenodo compulsory deposit information),
          - Publishes an deposit
          - Finds all the published community entries
            * per title
            * per deposit_id
          - Finds all the records of a user (defined by the zenodo token)
          - Searches for similar records within all records associated to a user.

          Please note that every request.json() answer has been limited to 50 elements. You can set this value
          as follows (once ZenodoAPI has been initialised, for example):
          z = ZenodoApi(token)
          z.parameters.update({'size': INTEGER_NUMBER)

        :param access_token: str
            Personal access token to (sandbox.)zenodo.org/api
        :param sandbox: bool
            Communicates with either zenodo or sandbox.zenodo api
        """

        self.sandbox = sandbox
        self.api_url = zenodo_sandbox_api_url if sandbox else zenodo_api_url
        if access_token is None:
            warnings.warn("No access token provided, limited functionalities")
        self.access_token = access_token
        self.parameters = {'access_token': self.access_token}
        self.parameters.setdefault('size', _default_size_query)

    def _raise_token_status(self):
        """
        private method to check if a valid token has been provided, called in methods requiring a token
        :return:
        """
        if self.access_token is None or self.access_token == '':
            raise ValueError("No access token was provided. This method requires one.")

    def query_user_deposits(self):
        """
        Fetch the published entries of a user. Works to test connection to Zenodo too.

        GET method to {api_url}/deposit/depositions

        :return: request.get method
        """
        self._raise_token_status()
        url = f"{self.api_url}/deposit/depositions"
        answer = requests.get(url, params=self.parameters)
        http_status.ZenodoHTTPStatus(answer.status_code, answer.json())
        return answer

    def query_deposit(self, deposit_id):
        """
        Fetches (recovers all the existing information, as well as links) of an existing Zenodo deposit.
        Parameters
        ----------
        deposit_id: str or int

        Returns
        -------

        """
        self._raise_token_status()
        url = f"{self.api_url}/deposit/depositions/{deposit_id}"
        answer = requests.get(url, params=self.parameters)
        http_status.ZenodoHTTPStatus(answer.status_code, answer.json())
        return answer

    def create_new_deposit(self):
        """
        Create a new deposit in (sandbox.)zenodo

        POST method to {api_url}/deposit/depositions

        :return: request.put method
        """
        self._raise_token_status()
        url = f"{self.api_url}/deposit/depositions"
        headers = {"Content-Type": "application/json"}
        req = requests.post(url, json={}, headers=headers, params=self.parameters)
        http_status.ZenodoHTTPStatus(req.status_code, req.json())
        return req

    def query_record(self, record_id):
        """
        Query (recovers all the existing information, as well as links) of a Zenodo record.

        GET method to {api_url}/deposit/depositions/{deposit_id}

        :param record_id: str
            deposit_id of the entry to fetch

        :return: request.get method
        """
        return query_record(record_id, sandbox=self.sandbox)

    def upload_file_deposit(self, deposit_id, name_file, path_file):
        """
        Upload a file to a Zenodo deposit. If first retrieve the deposit by a GET method to the
            {api_url}/deposit/depositions/{record_id}.

        PUT method to {bucket_url}/{filename}. The full api url is recovered when the deposit is firstly retrieved.

        :param deposit_id: str
            deposition_id of the Zenodo deposit
        :param name_file: str
            File name of the file when uploaded
        :param path_file: str
            Path to the file to be uploaded

        :return: request.put method
        """
        self._raise_token_status()
        # 1 - Retrieve and recover information of a record that is in process of being published
        fetch = requests.get(f"{self.api_url}/deposit/depositions/{deposit_id}", params=self.parameters)
        http_status.ZenodoHTTPStatus(fetch.status_code, fetch.json())

        # 2 - Upload the files
        bucket_url = fetch.json()['links']['bucket']  # full url is recovered from previous GET method
        url = f"{bucket_url}/{name_file}"

        with open(path_file, 'rb') as upload_file:
            upload = requests.put(url, data=upload_file, params=self.parameters)

        http_status.ZenodoHTTPStatus(upload.status_code, upload.json())
        return upload

    def set_deposit_metadata(self, deposit_id, json_metadata):
        """
        Set a deposit metadata. The metadata passed must be exhaustive, i.e. all the compulsory fields must be provided.

        PUT method to {api_url}/deposit/depositions/{deposit_id}. `data` MUST be included as json.dump(data)

        :param deposit_id: str
            deposition_id of the Zenodo deposit
        :param json_metadata: object
            json object containing the metadata (compulsory fields) that are enclosed when a new deposit is created.

        :return: request.put method
        """
        self._raise_token_status()
        url = f"{self.api_url}/deposit/depositions/{deposit_id}"
        headers = {"Content-Type": "application/json"}

        # The metadata field is already created, just need to be updated.
        # Thus, the root 'metadata' key need to be kept, to indicate the field to be updated.
        data = {"metadata": json_metadata}
        req = requests.put(url, data=json.dumps(data), headers=headers, params=self.parameters)
        http_status.ZenodoHTTPStatus(req.status_code, req.json())
        return req

    def update_deposit_metadata(self, deposit_it, metadata):
        """
        Update the deposit metadata with only the one provided.

        Parameters
        ----------
        deposit_it: str or int
        metadata: dict
            The metadata to be updated.
        """
        # TODO: implement this method
        req = self.query_deposit(deposit_it)
        data = req.json()
        data['metadata'].update(metadata)
        req = self.set_deposit_metadata(deposit_it, data['metadata'])
        return req

    def erase_deposit(self, deposit_id):
        """
        Erase a deposit (that has not been published yet).
        Any new upload/version will be first saved as 'draft' and not published until confirmation (i.e, requests.post)

        DELETE method to {api_url}/deposit/depositions/{deposit_id}.

        :param deposit_id: str or int
            deposition_id of the Zenodo deposit to be erased

        :return: request.delete method
        """
        self._raise_token_status()
        url = f"{self.api_url}/deposit/depositions/{deposit_id}"
        req = requests.delete(url, params=self.parameters)
        if req.status_code == 204:
            print("The deposit has been deleted")
            return req
        elif req.status_code == 410:  # Not raising an error in this case is OK
            warnings.warn("The deposit already was deleted")
        else:
            http_status.ZenodoHTTPStatus(req.status_code, req.json())
            return req

    def erase_file_deposit(self, deposit_id, file_id):
        """
        Erase a file from a deposit (that has not been published yet).
        This method is intended to be used for substitution of files (deletion) within a deposit by their correspondent
        new versions.

        DELETE method to {api_url}/deposit/depositions/{deposit_id}/files/{file_id}

        :param deposit_id: str
            deposition_id of the Zenodo deposit
        :param file_id: str
            ID of the files stored in Zenodo

        :return: requests.delete method
        """
        self._raise_token_status()
        url = f"{self.api_url}/deposit/depositions/{deposit_id}/files/{file_id}"
        req = requests.delete(url, params=self.parameters)
        http_status.ZenodoHTTPStatus(req.status_code)
        return req

    def publish_deposit(self, deposit_id):
        """
        Publishes a deposit in (sandbox.)zenodo

        POST method to {api_url}/deposit/depositions/{deposit_id}/actions/publish

        :param deposit_id: str
            deposition_id of the Zenodo entry

        :return: requests.put method
        """
        self._raise_token_status()
        url = f"{self.api_url}/deposit/depositions/{deposit_id}/actions/publish"
        req = requests.post(url, params=self.parameters)
        http_status.ZenodoHTTPStatus(req.status_code, req.json())
        return req

    def new_version_deposit(self, record_id):
        """
        Creates a new version of an existing record.

        POST method to {api_url}/deposit/depositions/{deposit_id}/actions/newversion

        :param record_id: str or int
        :return: requests.post method
        """
        self._raise_token_status()
        url = f"{self.api_url}/deposit/depositions/{record_id}/actions/newversion"
        parameters = {'access_token': self.access_token}
        req = requests.post(url, params=parameters)
        http_status.ZenodoHTTPStatus(req.status_code, req.json())
        return req

    def query_community_records(self, community_name='escape2020', **kwargs):
        """
        Query the records within a community.

        GET method, previous modification of the query arguments, to {api_url}/records

        :param community_name: str
            Community name.
        :param kwargs: dict
            Parameters for `query_zenodo_records`

        :return: `requests.models.Response`
        """
        # https://developers.zenodo.org/#list36
        parameters = deepcopy(self.parameters)
        parameters.update(kwargs)
        parameters['communities'] = str(community_name)
        return query_zenodo_records('', sandbox=self.sandbox, **parameters)

    @staticmethod
    def path_codemeta_file(root_dir):
        return Path(root_dir).joinpath('codemeta.json')

    @staticmethod
    def path_zenodo_file(root_dir):
        return Path(root_dir).joinpath('.zenodo.json')

    def upload_dir_content(self, directory, record_id=None, metadata=None, erase_previous_files=True, publish=True):
        """
        Package the project root directory as a zip archive and upload it to Zenodo.
        If a `record_id` is passed, a new version of that record is created. Otherwise, a new record is created.

        :param directory: Path or str
            path to the directory to upload
        :param record_id: str, int of None
            If a record_id is provided, a new version of the record will be created.
        :param metadata: dict or None
            dictionary of zenodo metadata
            if None, the metadata will be read from a `.zenodo.json` file or a `codemeta.json` file in `self.root_dir`
        :param erase_previous_files: bool
            In case of making a new version of an existing record (`record_id` not None), erase files from the previous
            version
        :param publish: bool
            If true, publish the record. Otherwise, the record is prepared but publication must be done manually. This
            is useful to check or discard the record before publication.
        """
        self._raise_token_status()
        # prepare new record version
        if record_id is not None:

            record = Record.from_id(record_id, sandbox=self.sandbox)
            record_id = record.last_version_id
            new_deposit = self.new_version_deposit(record_id)
            new_deposit_id = new_deposit.json()['links']['latest_draft'].rsplit('/')[-1]
            print(f" * Preparing a new version of record {record_id}")
            # TODO: log
            if erase_previous_files:
                old_files_ids = [file['id'] for file in new_deposit.json()['files']]
                for file_id in old_files_ids:
                    self.erase_file_deposit(new_deposit_id, file_id)
                    print(f"   - file {file_id} erased")
        else:

            new_deposit = self.create_new_deposit()
            new_deposit_id = new_deposit.json()['id']
            print(' * Preparing a new record')

        print(f" * New record id: {new_deposit_id}")

        # get metadata
        path_codemeta_file = self.path_codemeta_file(directory)
        path_zenodo_file = self.path_zenodo_file(directory)
        if metadata is not None:
            print(f" * Record metadata based on provided metadata: {metadata}")
        elif path_zenodo_file.exists():
            print(f"   - Record metadata based on zenodo file {path_zenodo_file}")
            with open(path_zenodo_file) as file:
                metadata = json.load(file)
        elif path_codemeta_file.exists():
            print(f"   - Record metadata based on codemeta file {path_codemeta_file}")
            with open(path_codemeta_file) as file:
                codemeta = json.load(file)
            metadata = converter(codemeta)
        else:
            raise FileNotFoundError(" ! No metadata file provided")

        # upload files
        dir_to_upload = Path(directory)
        for file in dir_to_upload.iterdir():
            self.upload_file_deposit(deposit_id=new_deposit_id, name_file=file.name, path_file=file)
            print(f" * {file.name} uploaded")

        # and update metadata
        self.set_deposit_metadata(new_deposit_id, json_metadata=metadata)
        print(" * Metadata updated successfully")

        # publish new record
        if publish:
            self.publish_deposit(new_deposit_id)
            if record_id:
                print(f" * New version of {record_id} published at {new_deposit_id} !")
            else:
                print(f" * Record {new_deposit_id} published")
            print(f" * The new doi should be 10.5281/{new_deposit_id}")

        print(f" * Check the upload at {self.api_url[:-4]}/deposit/{new_deposit_id} *")

        return new_deposit_id

    def check_upload_to_zenodo(self, directory):
        """
        `Tests` the different stages of the GitLab-Zenodo connection and that the status_code returned by every
        stage is the correct one.

        Checks:
         - The existence of a `.zenodo.json` file in the ROOT dir of the project
            - If not, it checks if it exists a `codemeta.json` file
               - If it exists it performs the codemeta2zenodo conversion
               - If not, it exits the program

         - The communication with Zenodo through its API to verify that:
            - You can fetch a user entries
            - You can create a new entry
            - The provided zenodo metadata can be digested, and not errors appear
            - Finally erases the test entry - because IT HAS NOT BEEN PUBLISHED !
        """
        self._raise_token_status()
        path_zenodo_file = self.path_zenodo_file(directory)
        path_codemeta_file = self.path_codemeta_file(directory)
        if not path_zenodo_file.exists():
            if not path_codemeta_file.exists():
                raise FileNotFoundError(f"No codemeta {path_codemeta_file} nor zenodo {path_zenodo_file} files.")

            print("\n * Creating a .zenodo.json file from your codemeta.json file...")

            parse_codemeta_and_write_zenodo_metadata_file(path_codemeta_file, path_zenodo_file)
        print(f"\n * Using {path_zenodo_file} file to simulate a new upload to Zenodo... \n")

        # 1 - Test connection
        print("1 --> Testing communication with Zenodo...")

        test_connection = self.query_user_deposits()

        http_status.ZenodoHTTPStatus(test_connection.status_code, test_connection.json())
        print("  * Test connection status OK !")

        # 2 - Test new entry
        print("2 --> Testing the creation of a dummy entry to (sandbox)Zenodo...")

        new_deposit = self.create_new_deposit()

        http_status.ZenodoHTTPStatus(new_deposit.status_code, new_deposit.json())
        print("  * Test new deposit status OK !")

        # 3 - Test upload metadata
        print("3 --> Testing the ingestion of the Zenodo metadata...")

        test_deposit_id = new_deposit.json()['id']
        with open(path_zenodo_file) as file:
            metadata_entry = json.load(file)
        updated_metadata = self.set_deposit_metadata(test_deposit_id, json_metadata=metadata_entry)

        try:
            http_status.ZenodoHTTPStatus(updated_metadata.status_code)
            print("  * Metadata deposit status OK !")
            pprint.pprint(metadata_entry)
        except http_status.HTTPStatusError:
            print("  ! ERROR while testing update of metadata\n", updated_metadata.json())
            print("  ! The deposit will be deleted")

        # 4 - Test delete entry
        print("4 --> Deleting the dummy entry...")
        delete_test_entry = self.erase_deposit(test_deposit_id)
        try:
            http_status.ZenodoHTTPStatus(delete_test_entry.status_code)
        except http_status.HTTPStatusError:
            print(f" !! ERROR erasing dummy test entry: {delete_test_entry.json()}")
            print(f"Please erase it manually at {self.api_url[:-4]}/deposit")
            sys.exit(-1)

        print("  * Delete test entry status OK !")

        print(
            "\n\tYAY ! Successful testing of the connection to Zenodo ! \n\n"
            "You should not face any trouble when uploading a project to Zenodo"
        )

    def get_user_records(self):
        """Finds all the records associated with a user (defined by the zenodo token)"""
        request = self.query_user_deposits()

        return [Record(hit) for hit in request.json() if hit['state'] == 'done']

    def find_similar_records(self, record):
        """
        Find similar records in the owner records.
        This check is not exhaustive and is based only on a limited number of parameters.

        :param record: `eossr.api.zenodo.Record`
        :return: list[Record]
            list of similar records
        """
        similar_records = []
        user_records = self.get_user_records()
        for user_rec in user_records:
            if user_rec.title == record.title:
                similar_records.append(user_rec)

            if 'related_identifiers' in user_rec.data['metadata'] and 'related_identifiers' in record.data['metadata']:

                relid1 = [r['identifier'] for r in user_rec.data['metadata']['related_identifiers']]
                relid2 = [r['identifier'] for r in record.data['metadata']['related_identifiers']]

                if set(relid1).intersection(relid2):
                    similar_records.append(user_rec)

        return similar_records

    def get_community_pending_requests(self, community, **params):
        """
        Get a list of records that have been requested to be added to a community.

        :param community: str
            Name of the community.
        :param params: dict
            Parameters for the request. Override the class parameters.
        :return: [Record]
        """
        self._raise_token_status()
        url = self.api_url + f'/records/?q=provisional_communities:{community.lower()}'
        parameters = deepcopy(self.parameters)
        parameters.update(params)
        req = requests.get(url, params=parameters)
        http_status.ZenodoHTTPStatus(req.status_code, json=req.json())
        req_json = req.json()
        records = [Record(rec) for rec in req_json['hits']['hits']]
        return records

    def accept_pending_request(self, community, record_id):
        """
        Accept a pending request into a community.
        The community must be owned by the token owner.

        :param community: str
            community name. The community must be owned by the token owner.
        :param record_id:
            str or int
        """
        self._raise_token_status()
        raise NotImplementedError("Sorry, we are working on it")
        # TODO: this should work based on https://github.com/zenodo/zenodo/issues/1436
        # run(['curl', '-i', '-X', 'POST', '-H',
        #      'Content-Type:application/json', '--data',
        #      f'{"action":"accept", "recid:{record_id}"}',
        #      f'"https://zenodo.org/communities/{community}/curate/"',
        #      ])

    def update_record_metadata(self, record_id, metadata):
        """
        Update a published record metadata

        :param record_id: int
        :param metadata: dict
        :return: `requests.response`
        """
        self._raise_token_status()
        req = requests.post(
            f"{self.api_url}/deposit/depositions/{record_id}/actions/edit?access_token={self.access_token}"
        )
        if req.status_code == 403:
            # In this case it is fine to continue editing the record metadata
            warnings.warn("The record was already open for edition")
        else:
            http_status.ZenodoHTTPStatus(req.status_code, req.json())

        record = get_record(record_id, sandbox=self.sandbox)
        record_metadata = record.data['metadata']
        record_metadata['upload_type'] = record_metadata['resource_type']['type']
        record_metadata.pop('access_right_category')
        record_metadata.pop('relations')
        record_metadata.pop('related_identifiers')
        record_metadata.pop('resource_type')
        record_metadata.update(metadata)
        self.set_deposit_metadata(record_id, json_metadata=record_metadata)
        req = self.publish_deposit(record_id)
        return req


class SimilarRecordError(Exception):
    pass


class Record:
    """
    Basic class object to handle Zenodo records
    """

    def __init__(self, data: dict):
        for k in ['id', 'metadata']:
            if k not in data.keys():
                raise ValueError(f"key {k} not present in data")
        # list of keys mandatory to create a Zenodo entry.
        # Other keys are either optional, or can be hidden in case of Closed Access entries.
        for meta_key in ['title', 'doi']:
            if meta_key not in data['metadata'].keys():
                raise ValueError(f"Mandatory key {meta_key} not in data['metadata']")
        self.data = data

    def __str__(self):
        return f"Record #{self.id} : {self.title}"

    def __repr__(self):
        return f"Record({self.id})"

    def _write_zenodo_deposit(self, filename='.zenodo.json', overwrite=False, validate=True):
        """
        Write the zenodo metadata to a `.zenodo.json` file, so it can be used to create a new deposit.
        The created is not guaranteed to be valid, but it is a good starting point.

        :param filename: str
            path to the file to write
        :param overwrite: bool
            True to overwrite existing file
        :param validate: bool
            True to validate the metadata before writing the file
        """
        # Transform metadata from record to deposit first
        metadata = deepcopy(self.data['metadata'])
        metadata['upload_type'] = metadata['resource_type']['type']
        metadata.pop('resource_type')
        metadata.pop('access_right_category')
        if 'relations' in metadata:
            metadata.pop('relations')
        if 'communities' in metadata:
            metadata['communities'] = [{'identifier': c['id']} for c in metadata['communities']]
        metadata['related_identifiers'] = [
            rid
            for rid in metadata['related_identifiers']
            if not (rid['relation'] == 'isVersionOf' and 'zenodo' in rid['identifier'])
        ]
        if 'zenodo' in metadata['doi']:
            metadata.pop('doi')
        metadata['license'] = metadata['license']['id']

        write_zenodo_metadata(metadata, filename=filename, overwrite=overwrite, validate=validate)

    def write_metadata(self, filename, overwrite=False):
        """
        Write the metadata to a json file.

        Parameters
        ----------
        filename: str
        overwrite: bool
            True to overwrite existing file
        """
        write_json(self.data['metadata'], filename=filename, overwrite=overwrite)

    @property
    def id(self):
        return self.data['id']

    @property
    def title(self):
        return self.data['metadata']['title']

    @property
    def metadata(self):
        return self.data['metadata']

    @property
    def filelist(self):
        """
        Return the list of files in the record

        :return: [str]
        """
        return [f['links']['self'] for f in self.data['files']]

    @property
    def last_version_id(self):
        """
        Return the ID of the last version of this record.
        If there is no other version, returns self.id

        :return: int
        """
        if 'relations' not in self.data['metadata']:
            return self.id
        else:
            return self.data['metadata']['relations']['version'][0]['last_child']['pid_value']

    def get_last_version(self):
        """
        Return the last version of the record.
        If there is only one version, or if this is already the last version, return itself.

        :return: `eossr.api.zenodo.Record`
        """
        if 'relations' not in self.data['metadata'] or self.data['metadata']['relations']['version'][0]['is_last']:
            return self
        record_id = self.last_version_id
        url = Path(self.data['links']['self']).parent.joinpath(str(record_id)).as_posix()
        return Record(requests.get(url).json())

    @property
    def from_sandbox(self):
        """
        Is the record from sandbox?
        :return: bool
        """
        if 'sandbox' in self.data['links']['self']:
            return True
        else:
            return False

    def get_associated_versions(self, size=_default_size_query, **kwargs):
        """
        Returns a dictionary of all the versions of the current record

        :param size: int
            Number of results to return. Default = 50 (`_default_size_query`)
        :param kwargs: Zenodo query arguments.
            For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36

        :return: dict
            dictionary of `{record_id: record_version}`
        """
        conceptrecid = self.data['conceptrecid']
        params = {'all_versions': True, **kwargs}
        params.setdefault('size', size)

        versions = {}
        for record in get_zenodo_records(f'conceptrecid:{conceptrecid}', sandbox=self.from_sandbox, **params):
            if 'version' in record.metadata:
                versions[record.id] = record.metadata['version']
            else:
                versions[record.id] = None
        return versions

    def _summary(self, linebreak='\n'):
        """
        Generate a summary of the record information.
        The information includes the record id, title, version, DOI, URL and description.
        If certain information is unavailable, it defaults to 'Unknown'.
        HTML tags in the description are stripped before being included in the summary.

        :param linebreak: string
            line break character. default: '\n'

        :return: string
            The summary string.
        """
        lines = [f"=== Record #{self.id} ===", f"Title: {self.title}"]
        version = self.metadata.get('version', 'Unknown')
        lines.append(f"Version: {version}")
        lines.append(f"DOI: {self.data.get('doi', 'Unknown')}")

        links = self.data.get('links', {})
        if 'html' in links:
            lines.append(f"URL: {links['html']}")

        description = self.metadata.get('description', '')
        # Replace paragraph tags with newlines
        description = re.sub('<p>', linebreak, re.sub('</p>', linebreak, description))
        # Then strip the remaining HTML tags
        stripped_description = re.sub('<[^<]+?>', '', description)

        # Wrap description text to 70 characters wide
        wrapped_description = textwrap.fill(stripped_description, width=70)
        lines.append(wrapped_description)

        descrp = linebreak.join(lines)
        return descrp

    def print_info(self, linebreak='\n', file=sys.stdout):
        """
        Print the summary of the record information to a stream, or to sys.stdout by default.

        :param linebreak: string
            line break character. default: '\n'
        :param file: a file-like object (stream); defaults to the current sys.stdout.

        :return: None
        """
        print(self._summary(linebreak=linebreak), file=file)

    @classmethod
    def from_id(cls, record_id, sandbox=False):
        """
        Retrieve a record from its record id.

        :param record_id: int
        :param sandbox: bool
            True to use Zenodo's sandbox

        :return: `eossr.api.zenodo.Record`
        """
        record = get_record(record_id=record_id, sandbox=sandbox)
        return record

    def get_codemeta(self, **zipurl_kwargs):
        """
        Get codemeta metadata from the record (can also be in a zip archive).
        Raises an error if no `codemeta.json` file is found.

        :param zipurl_kwargs: dict
            kwargs for `eossr.utils.ZipUrl`

        :return: dict
            codemeta metadata
        """
        if 'files' not in self.data:
            raise FileNotFoundError(f'The record {self.id} does not contain any file')

        codemeta_paths = [s for s in self.filelist if Path(s).name == 'codemeta.json']
        ziparchives = [s for s in self.filelist if s.endswith('.zip')]
        if len(codemeta_paths) >= 1:
            # if there are more than one codemeta file in the repository, we consider the one in the root directory,
            # hence the one with the shortest path
            chosen_codemeta = min(codemeta_paths, key=len)
            return json.loads(urlopen(chosen_codemeta).read())
        elif len(ziparchives) > 0:
            for zipurl in ziparchives:
                try:
                    return get_codemeta_from_zipurl(zipurl, **zipurl_kwargs)
                except FileNotFoundError:
                    pass
            raise FileNotFoundError(f"No `codemeta.json` file found in record {self.id}")
        else:
            raise FileNotFoundError(f"No `codemeta.json` file found in record {self.id}")

    @property
    def doi(self):
        if 'doi' not in self.data:
            raise KeyError(f"Record {self.id} does not have a doi")
        return self.data['doi']

    def get_mybinder_url(self):
        """
        Returns a URL to a mybinder instance of that record

        :return: str
        """
        binder_zenodo_url = 'https://mybinder.org/v2/zenodo/'
        doi = self.doi
        return binder_zenodo_url + doi

    def download(self, directory='.', max_workers=None):
        """
        Download the record to a directory.

        Parameters
        ----------
        directory: str or Path
            Directory where to download the record content
        max_workers: int or None
            Number of workers to use for the download. If None, use all available workers.
        """
        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {
                executor.submit(urlretrieve, url, f'{directory}/{os.path.basename(url)}'): url for url in self.filelist
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    future.result()
                    print(f'{url} : Download complete')
                except Exception as exc:
                    print(f'{url} generated an exception: {exc}')


def query_zenodo_records(search='', sandbox=False, **kwargs):
    """
    Query Zenodo for records whose names or descriptions include the provided string `search`.
    Function rewritten from pyzenodo3 (https://github.com/space-physics/pyzenodo3)

    :param search: string
        A string to refine the search in Zenodo. The default will search for all records.
    :param sandbox: bool
        Indicates the use of sandbox zenodo or not.
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 50
            - all_versions: int
                Show (1) or hide (0) all versions of records
            - type: string or list[string]
                Records of the specified type (Publication, Poster, Presentation, Software, ...)
                A logical OR is applied in case of a list
            - keywords: string or list[string]
                Records with the specified keywords
                 A logical OR is applied in case of a list
            - communities: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list
            - file_type: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list

    :return:
    `requests.models.Response`
    """
    search = search.replace("/", " ")  # zenodo can't handle '/' in search query

    params = {'q': search, **kwargs}

    params.setdefault('size', str(_default_size_query))

    def lowercase(param):
        if isinstance(param, str):
            param = param.lower()
        if isinstance(param, list):
            param = [char.lower() for char in param]
        return param

    for param_name in ['communities', 'type', 'file_type']:
        if param_name in kwargs:
            params[param_name] = lowercase(kwargs[param_name])

    api_url = zenodo_sandbox_api_url if sandbox else zenodo_api_url
    url = api_url + "/records?" + urlencode(params, doseq=True)
    req = requests.get(url)
    http_status.HTTPStatusError(req.status_code, req.json())
    return req


def get_zenodo_records(search='', sandbox=False, **kwargs):
    """
    Search Zenodo for records whose names or descriptions include the provided string `search`.
    Function rewritten from pyzenodo3 (https://github.com/space-physics/pyzenodo3)

    :param search: string
        A string to refine the search in Zenodo. The default will search for all records.
    :param sandbox: bool
        Indicates the use of sandbox zenodo or not.
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 100
            - all_versions: int
                Show (1) or hide (0) all versions of records
            - type: string or list[string]
                Records of the specified type (Publication, Poster, Presentation, Software, ...)
                A logical OR is applied in case of a list
            - keywords: string or list[string]
                Records with the specified keywords
                 A logical OR is applied in case of a list
            - communities: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list
            - file_type: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list

    :return: [Record]
        list of records
    """
    answer = query_zenodo_records(search=search, sandbox=sandbox, **kwargs)
    hits = answer.json()["hits"]["hits"]
    if not hits:
        raise LookupError(f"No records found for search {search}")
    else:
        return [Record(hit) for hit in hits]


def query_record(record_id, sandbox=False):
    """
    Send a request for a record to Zenodo (or its sandbox if `sandbox=True`).

    :param record_id: int
        record ID
    :param sandbox: boolean
        whether to request in the sandbox or not
    :return:
    `requests.models.Response`
    """
    api_url = zenodo_sandbox_api_url if sandbox else zenodo_api_url
    url = f"{api_url}/records/{record_id}"
    return requests.get(url)


def get_record(record_id, sandbox=False):
    """
    Get a record from its id

    :param record_id: int or str
        Zenodo record id number.
    :param sandbox: bool
        Indicates the use of sandbox zenodo or not.

    :return: Record
    """
    answer = query_record(record_id, sandbox=sandbox)
    answer_json = answer.json()
    http_status.ZenodoHTTPStatus(answer.status_code, answer_json)
    return Record(answer_json)


def get_supported_licenses(size=1000):
    """
    Recovers the list of Zenodo supported license IDs and names.
    Makes a request.get() call to Zenodo.

    :return: list
        license id plus license name Zenodo supported licenses list
    """
    licenses = search_licenses(size=size)
    return [license['metadata']['id'] for license in licenses]


def _query(field, search='', sandbox=False, **kwargs):
    """
    https://help.zenodo.org/guides/search/

    :param field: str
        where to search: 'records', 'funders', 'grants', 'communities', 'licenses'
    :param search: str
    :param sandbox: boolean
        True to search in the sandbox
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 100
            - all_versions: int
                Show (1) or hide (0) all versions of records
            - type: string or list[string]
                Records of the specified type (Publication, Poster, Presentation, Software, ...)
                A logical OR is applied in case of a list
            - keywords: string or list[string]
                Records with the specified keywords
                 A logical OR is applied in case of a list
            - communities: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list
            - file_type: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list
    :return: `requests.response`
    """

    def lowercase(param):
        if isinstance(param, str):
            param = param.lower()
        if isinstance(param, list):
            param = [char.lower() for char in param]
        return param

    search = search.replace("/", " ")  # zenodo can't handle '/' in search query

    params = {'q': search, **kwargs}

    params.setdefault('size', 100)

    for param_name in ['communities', 'type', 'file_type']:
        if param_name in kwargs:
            params[param_name] = lowercase(kwargs[param_name])

    api_url = zenodo_api_url if not sandbox else zenodo_sandbox_api_url
    url = api_url + f"/{field}?" + urlencode(params, doseq=True)

    response = requests.get(url)
    return response


def _search(field, search='', sandbox=False, **kwargs):
    """
    https://help.zenodo.org/guides/search/

    :param field: str
        where to search: 'records', 'funders', 'grants', 'communities', 'licenses'
    :param search: str
    :param sandbox: boolean
        True to search in the sandbox
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 100
            - all_versions: int
                Show (1) or hide (0) all versions of records
            - type: string or list[string]
                Records of the specified type (Publication, Poster, Presentation, Software, ...)
                A logical OR is applied in case of a list
            - keywords: string or list[string]
                Records with the specified keywords
                 A logical OR is applied in case of a list
            - communities: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list
            - file_type: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list
    :return: [dict]
    """

    query = _query(field, search=search, sandbox=sandbox, **kwargs)
    http_status.ZenodoHTTPStatus(query.status_code, query.json())

    hits = [hit for hit in query.json()["hits"]["hits"]]
    return hits


def search_records(search='', sandbox=False, **kwargs):
    """
    https://help.zenodo.org/guides/search/

    :param search: str
    :param sandbox: boolean
        True to search in the sandbox
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 100
            - all_versions: int
                Show (1) or hide (0) all versions of records
            - type: string or list[string]
                Records of the specified type (Publication, Poster, Presentation, Software, ...)
                A logical OR is applied in case of a list
            - keywords: string or list[string]
                Records with the specified keywords
                 A logical OR is applied in case of a list
            - communities: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list
            - file_type: string or list[string]
                Records from the specified keywords
                A logical OR is applied in case of a list
    :return: [dict]
    """
    hits = _search('records', search=search, sandbox=sandbox, **kwargs)
    return hits


def search_funders(search='', sandbox=False, **kwargs):
    """
    https://help.zenodo.org/guides/search/

    :param search: str
    :param sandbox: boolean
        True to search in the sandbox
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 5
    :return: [dict]
    """
    kwargs.setdefault('size', 5)
    hits = _search('funders', search=search, sandbox=sandbox, **kwargs)
    return hits


def search_grants(search='', sandbox=False, **kwargs):
    """
    https://help.zenodo.org/guides/search/

    :param search: str
    :param sandbox: boolean
        True to search in the sandbox
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 5
    :return: [dict]
    """
    kwargs.setdefault('size', 5)
    hits = _search('grants', search=search, sandbox=sandbox, **kwargs)
    return hits


def search_communities(search='', sandbox=False, **kwargs):
    """
    https://help.zenodo.org/guides/search/

    :param search: str
    :param sandbox: boolean
        True to search in the sandbox
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 5
    :return: [dict]
    """
    kwargs.setdefault('size', 5)
    hits = _search('communities', search=search, sandbox=sandbox, **kwargs)
    return hits


def search_licenses(search='', sandbox=False, **kwargs):
    """
    https://help.zenodo.org/guides/search/

    :param search: str
    :param sandbox: boolean
        True to search in the sandbox
    :param kwargs: Zenodo query arguments.
        For an exhaustive list, see the query arguments at https://developers.zenodo.org/#list36
        Common arguments are:
            - size: int
                Number of results to return
                Default = 5
    :return: [dict]
    """
    kwargs.setdefault('size', 5)
    hits = _search('licenses', search=search, sandbox=sandbox, **kwargs)
    return hits


def is_live(sandbox=False):
    """
    Check if Zenodo website is live
    :param sandbox: bool
        True to test sandbox instead
    :return: bool
        True if live
    """
    url = zenodo_sandbox_api_url if sandbox else zenodo_api_url
    req = requests.get(url)
    return req.status_code == 200


def query_deposit(deposit_id, access_token, sandbox=False):
    """
    Query a deposit

    Parameters
    ----------
    deposit_id: str or int

    Returns
    -------

    """
    url = zenodo_api_url + 'deposit/depositions/{}'.format(deposit_id)
    response = requests.get(url, params={'access_token': access_token})
    return response
