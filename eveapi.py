# Copyright 2015 Florian Tautz
# This program is licensed under the MIT License,
# see the contents of the LICENSE file in this directory for details.


from http.client import HTTPSConnection
from urllib.parse import urlencode
from datetime import datetime
from lxml import objectify
from util import CacheDb


class ApiError(Exception):
    pass


class ApiClient(object):
    API_HOST = 'api.eveonline.com'
    ENDPOINT_EXT = '.xml.aspx'
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, cache):
        self.cache = cache

    def query(self, endpoint, arguments=None):
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        if not endpoint.endswith(ApiClient.ENDPOINT_EXT):
            endpoint += ApiClient.ENDPOINT_EXT
        if arguments is None:
            arguments = {}

        query_string = '?'.join([endpoint, urlencode(arguments)])

        result = self.cache.get(query_string)

        if result is not None:
            return objectify.fromstring(result)

        connection = HTTPSConnection(ApiClient.API_HOST)
        connection.request('GET', query_string)
        response = connection.getresponse()
        if response.status != 200:
            raise ApiError('Error response: ' + str(response.status))
        result = response.read()
        result_object = objectify.fromstring(result)
        cached_until = datetime.strptime(result_object.cachedUntil.text,
                                         ApiClient.TIMESTAMP_FORMAT)
        self.cache.set(query_string, result, cached_until)
        return result_object

    def character_id(self, character_name):
        result = self.query('eve/CharacterID',
                            {'names': character_name})
        return int(result.result.rowset.row.attrib['characterID'])

    def character_name(self, character_id):
        result = self.query('eve/CharacterName',
                            {'ids': character_id})
        return result.result.rowset.row.attrib['name']

    def character_corphistory(self, character_id):
        result = self.query('eve/CharacterInfo',
                            {'characterID': character_id})
        corp_history = []
        for entry in result.result.rowset.row:
            corp_history.append((entry.attrib['corporationID'],
                                 entry.attrib['corporationName'],
                                 entry.attrib['startDate']))
        return corp_history


def get_client():
    cache = CacheDb('api_cache.db')
    return ApiClient(cache)


if __name__ == '__main__':
    cache = CacheDb('api_cache.db')
    api = ApiClient(cache)
    cid = 597471398
    result = api.query('eve/CharacterInfo', {'characterID': cid})
    for row in result.result.rowset.row:
        print(row.attrib['corporationName'])

    print(cid, '->', api.character_name(cid))
