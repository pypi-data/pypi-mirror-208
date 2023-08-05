from influxdb_influxql_client.client.util.request_helper import RequestHelper


class _BaseClient(object):
    def __init__(self, base_url, database):
        self.url = base_url
        self.database = database
        self.sh = RequestHelper(base_url)
