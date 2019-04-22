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

"""Internal module for Database Rules."""

import requests

from firebase_admin import _http_client
from firebase_admin import __version__
from firebase_admin.db import _DatabaseService


class DatabaseRulesApiCallError(Exception):
    """An error encountered while interacting with the Database Rules Service."""

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
        self._client = _http_client.JsonHttpClient(
            credential=app.credential.get_credential(),
            base_url=db_url.rstrip('/') + _DatabaseRulesService.DATABASE_RULES_PATH,
            headers={'X-Client-Version': version_header})
        self._timeout = app.options.get('httpTimeout')


    def get_rules(self):
        # TODO
        pass


    def set_rules(self, content):
        # TODO
        pass

    def _make_request(self, method, url, resource_identifier, resource_identifier_label, json=None):
        try:
            return self._client.body(method=method, url=url, json=json, timeout=self._timeout)
        except requests.exceptions.RequestException as error:
            raise DatabaseRulesApiCallError(
                _DatabaseRulesService._extract_message(
                    resource_identifier, resource_identifier_label, error),
                error)

    @staticmethod
    def _extract_message(identifier, identifier_label, error):
        if not isinstance(error, requests.exceptions.RequestException) or error.response is None:
            return '{0} "{1}": {2}'.format(identifier_label, identifier, str(error))
        status = error.response.status_code
        message = _DatabaseRulesService.ERROR_CODES.get(status)
        if message:
            return '{0} "{1}": {2}'.format(identifier_label, identifier, message)
        return '{0} "{1}": Error {2}.'.format(identifier_label, identifier, status)
