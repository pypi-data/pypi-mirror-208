# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
NationBuilder Web API
"""

import requests


class NationBuilderWebAPI(object):
    """
    Simple web API for NationBuilder.

    https://nationbuilder.com/api_documentation
    """

    def __init__(self, config, base_url=None, access_token=None,
                 max_retries=None, **kwargs):
        self.config = config
        self.app = self.config.get_app()
        self.session = None

        self.base_url = base_url or self.config.require(
            'nationbuilder', 'api.base_url')
        self.base_url = self.base_url.rstrip('/')

        self.access_token = access_token or self.config.require(
            'nationbuilder', 'api.access_token')

        if max_retries is not None:
            self.max_retries = max_retries
        else:
            self.max_retries = self.config.getint('nationbuilder',
                                                  'api.max_retries')

        self.session = requests.Session()

        if self.max_retries is not None:
            adapter = requests.adapters.HTTPAdapter(max_retries=self.max_retries)
            self.session.mount(self.base_url, adapter)

    def _request(self, request_method, api_method, params=None):
        """
        Perform a request for the given API method, and return the response.
        """
        api_method = api_method.lstrip('/')

        params = params or {}
        params['access_token'] = self.access_token

        if request_method == 'GET':
            response = requests.get('{}/{}'.format(self.base_url, api_method),
                                    params=params)

        else:
            raise NotImplementedError("unknown request method: {}".format(
                request_method))

        response.raise_for_status()
        return response

    def get(self, api_method, params=None):
        """
        Perform a GET request for the given API method, and return the response.
        """
        return self._request('GET', api_method, params=params)

    def get_people(self, page_size=100, progress=None, **kwargs):
        """
        Retrieve all Person records.

        https://apiexplorer.nationbuilder.com/nationbuilder#People
        """
        response = self.get('/api/v1/people/count')
        count = response.json()['people_count']
        pages = count // page_size
        if count % page_size:
            pages += 1

        url = {'next': '/api/v1/people?limit={}'.format(page_size)}
        people = []

        def fetch(page, i):
            response = self.get(url['next'])
            data = response.json()
            people.extend(data['results'])
            url['next'] = data['next']

        self.app.progress_loop(fetch, range(pages), progress,
                               message="Fetching Person data from NationBuilder")
        return people

    def get_people_with_tag(self, tag, page_size=100, max_pages=None, **kwargs):
        """
        Retrieve all Person records with the given tag.

        https://apiexplorer.nationbuilder.com/nationbuilder#People
        """
        people = []

        # get first page
        api_method = '/api/v1/tags/{}/people'.format(tag)
        api_method = '{}?limit={}'.format(api_method, page_size)
        response = self.get(api_method)
        data = response.json()
        people.extend(data['results'])
        pages = 1

        # get more pages, until complete
        while data['next']:
            if max_pages and pages >= max_pages:
                break
            response = self.get(data['next'])
            data = response.json()
            people.extend(data['results'])
            pages += 1

        return people
