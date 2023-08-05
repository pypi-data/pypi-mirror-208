import logging

from influxdb_influxql_client.client._base import _BaseClient
from influxdb_influxql_client.client.query_api import QueryApi

logger = logging.getLogger('influxdb_client.client.influxdb_client')


class InfluxQLClient(_BaseClient):
    def __init__(self, base_url, database):
        super().__init__(base_url, database)

    def query_api(self) -> QueryApi:
        return QueryApi(self)
