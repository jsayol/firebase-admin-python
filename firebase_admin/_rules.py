# Copyright 2019 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Internal module for Firebase and Database Rules."""

import requests

from firebase_admin import _http_client
from firebase_admin import __version__
from firebase_admin.db import _DatabaseService


class RulesetFile(object):
    """A reference to a RulesetFile within a Ruleset.

    Please use the ``files`` property of the object returned by the module-level function
    ``get_ruleset(ruleset_id)`` to obtain instances of this class instead of instantiating it
    directly.
    """

    def __init__(self, name, content):
        self._name = name
        self._content = content

    @property
    def name(self):
        """Returns the name of this Ruleset file.

        Returns:
            string: The name of this Ruleset file.
        """
        return self._name

    @property
    def content(self):
        """Returns the content of this Ruleset file.

        Returns:
            string: The content of this Ruleset file.
        """
        return self._content


class Ruleset(object):
    """A reference to a Ruleset within a Firebase project.

    Please use the module-level functions ``get_ruleset(ruleset_id)`` or ``list_rulesets()``
    to obtain instances of this class instead of instantiating it directly.
    """

    def __init__(self, ruleset_id, create_time, files=None, service=None):
        self._ruleset_id = ruleset_id
        self._create_time = create_time
        self._service = service
        self._files = files

    @property
    def ruleset_id(self):
        """Returns the ID of this Ruleset.

        Returns:
            string: The ID of this Ruleset.
        """
        return self._ruleset_id

    @property
    def create_time(self):
        """Returns the creation time of this Ruleset.

        Returns:
            string: The creation time of this Ruleset.
        """
        return self._create_time

    @property
    def files(self):
        """Returns the files of this Ruleset.

        Returns:
            list: A list of ``RulesetFile`` instances for this Ruleset.
        """
        if self._files is None and self._service is not None:
            response = self._service.get_ruleset(self._ruleset_id)
            self._files = response['source']
        return self._files


class RulesApiCallError(Exception):
    """An error encountered while interacting with the Rules Service."""

    def __init__(self, message, error):
        Exception.__init__(self, message)
        self.detail = error


class _DatabaseRulesService(object):
    """Provides methods for interacting with the Database Rules Service."""

    DATABASE_RULES_PATH = '/.settings/rules.json'
    ERROR_CODES = {
        400: 'Invalid argument provided.',
        401: 'Request not authorized.',
        403: 'Client does not have sufficient privileges.',
        404: 'The specified entity could not be found.',
        409: 'The specified entity already exists.',
        423: 'The database has been manually locked by an owner.',
        500: 'Internal server error.',
        503: 'The server could not process the request in time.'
    }

    def __init__(self, app):
        db_url = app.options.get('databaseURL')
        if not db_url:
            raise ValueError(
                'Database URL is required to access the Database Rules Service. Make sure '
                'to set the databaseURL option.')
        self._db_url = _DatabaseService._validate_url(db_url)
        version_header = 'Python/Admin/{0}'.format(__version__)
        self._client = _http_client.TextHttpClient(
            credential=app.credential.get_credential(),
            base_url=db_url,
            headers={'X-Client-Version': version_header})
        self._timeout = app.options.get('httpTimeout')

    def get_rules(self):
        return self._make_request('get', 'Get')

    def set_rules(self, content):
        return self._make_request('put', 'Set', content)

    def _make_request(self, method, operation, data=None):
        try:
            return self._client.body(method=method,
                                     url=_DatabaseRulesService.DATABASE_RULES_PATH,
                                     data=data,
                                     timeout=self._timeout)
        except requests.exceptions.RequestException as error:
            raise RulesApiCallError(
                _DatabaseRulesService._extract_message(operation, error),
                error
            )

    @staticmethod
    def _extract_message(operation, error):
        if not isinstance(error, requests.exceptions.RequestException) or error.response is None:
            return '{0} Database rules: {1}'.format(operation, str(error))
        status = error.response.status_code
        message = _DatabaseRulesService.ERROR_CODES.get(status)
        if message:
            return '{0} Database rules: {1}'.format(operation, message)
        return '{0} Database rules: Error {2}.'.format(operation, status)


class _FirebaseRulesService(object):
    """Provides methods for interacting with the Firebase Rules Service."""

    BASE_URL = 'https://firebaserules.googleapis.com'
    API_VERSION = 'v1'
    ERROR_CODES = {
        400: 'Invalid argument provided.',
        401: 'Request not authorized.',
        403: 'Client does not have sufficient privileges.',
        404: 'The specified entity could not be found.',
        409: 'The specified entity already exists.',
        429: 'Quota exceeded for the requested resource.',
        500: 'Internal server error.',
        503: 'The server could not process the request in time.'
    }

    def __init__(self, app):
        project_id = app.project_id
        if not project_id:
            raise ValueError(
                'Project ID is required to access the Firebase Rules Service. Either '
                'set the projectId option, or use service account credentials. Alternatively, set '
                'the GOOGLE_CLOUD_PROJECT environment variable.')
        self._project_id = project_id
        version_header = 'Python/Admin/{0}'.format(__version__)
        self._client = _http_client.JsonHttpClient(
            credential=app.credential.get_credential(),
            base_url='{0}/{1}/projects/{2}/'.format(
                _FirebaseRulesService.BASE_URL,
                _FirebaseRulesService.API_VERSION,
                project_id
            ),
            headers={'X-Client-Version': version_header})
        self._timeout = app.options.get('httpTimeout')

    def get_rules(self, service):
        # TODO
        pass

    def set_rules(self, service, content):
        # TODO
        pass

    def list_rules_releases(self, filters, page_size, page_token):
        # TODO
        pass

    def get_rules_release(self, name):
        # TODO
        pass

    def create_rules_release(self, name, ruleset_id):
        # TODO
        pass

    def update_rules_release(self, name, ruleset_id):
        # TODO
        pass

    def delete_rules_release(self, name):
        # TODO
        pass

    def list_rulesets(self, page_size, page_token):
        # TODO
        pass

    def get_ruleset(self, ruleset_id):
        path = 'rulesets/{0}'.format(ruleset_id)
        response = self._make_request('get', path, ruleset_id, 'Ruleset ID')
        return Ruleset(
            ruleset_id,
            response["createTime"],
            files=map(_FirebaseRulesService._create_file_obj, response["source"]["files"]))

    def create_ruleset(self, files):
        # TODO
        pass

    def delete_ruleset(self, ruleset_id):
        # TODO
        pass

    def _make_request(self, method, url, resource_identifier, resource_identifier_label, json=None):
        try:
            return self._client.body(method=method, url=url, json=json, timeout=self._timeout)
        except requests.exceptions.RequestException as error:
            raise RulesApiCallError(
                _FirebaseRulesService._extract_message(
                    resource_identifier, resource_identifier_label, error),
                error)

    @staticmethod
    def _extract_message(identifier, identifier_label, error):
        if not isinstance(error, requests.exceptions.RequestException) or error.response is None:
            return '{0} "{1}": {2}'.format(identifier_label, identifier, str(error))
        status = error.response.status_code
        message = _FirebaseRulesService.ERROR_CODES.get(status)
        if message:
            return '{0} "{1}": {2}'.format(identifier_label, identifier, message)
        return '{0} "{1}": Error {2}.'.format(identifier_label, identifier, status)

    @staticmethod
    def _create_file_obj(file):
        return RulesetFile(name=file['name'], content=file['content'])
