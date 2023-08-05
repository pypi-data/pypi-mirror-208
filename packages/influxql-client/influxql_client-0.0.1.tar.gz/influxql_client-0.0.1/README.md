# InfluxDB InfluxQL Client

Temporarily filling in the gap to query influxdb using InfluxQL rather than Flux

Package was created for a specific use case, but will be maintained. PRs welcomed + feature requests welcomed.

## Usage


```python
from influxdb_influxql_client import InfluxQLClient

ic = InfluxQLClient('http://mocked.local:8086', 'database')

# Given this uses requests library, it is possible to update the session to handle basic auth/proxies etc
# For example, disabling SSL verification
ic.sh.verify = False

results = ic.query_api().query("select 1")

for result in results.results:
    for series in result.series:
        print(series.values)

```
