import json
import unittest
from unittest import mock

from influxdb_influxql_client import InfluxQLClient


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if str(args[0]).startswith('select 1'):
        with open('./mocked_responses/happy_cpu_metrics.json') as f:
            d = json.load(f)
        return MockResponse(d, 200)

    return MockResponse(None, 404)


class BasicTest(unittest.TestCase):

    @mock.patch('influxdb_influxql_client.client.query_api.QueryApi._query', side_effect=mocked_requests_get)
    def test_fetch(self, mock_get):
        ic = InfluxQLClient('http://mocked.local:8086', 'database')
        results = ic.query_api().query("select 1")

        assert len(results.results) == 1
        assert len(results.results[0].series) == 1
        assert 'time' in results.results[0].series[0].columns
        assert 'mean' in results.results[0].series[0].columns
        assert results.results[0].series[0].name == "cpu"
        assert len(results.results[0].series[0].values) == 1801


if __name__ == '__main__':
    unittest.main()
