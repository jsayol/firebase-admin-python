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

"""Internal module for Firebase Rules."""

import requests

from firebase_admin import _http_client
from firebase_admin import __version__


class FirebaseRulesApiCallError(Exception):
    """An error encountered while interacting with the Firebase Rules Service."""

    def __init__(self, message, error):
        Exception.__init__(self, message)
        self.detail = error


class _FirebaseRulesService(object):
    """Provides methods for interacting with the Firebase Rules Service."""

    BASE_URL = 'https://firebaserules.googleapis.com'
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
            base_url=_FirebaseRulesService.BASE_URL,
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
        # TODO
        pass

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
            raise FirebaseRulesApiCallError(
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
