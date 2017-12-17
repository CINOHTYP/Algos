API Reference
=============
## TsDataSet
class **TsDataSet**(*tsdata_list*)
> Return a new TsDataSet object initialized from a list of OpenTSDB query results.

| Operation  | Description       |  
| ---------- | ----------------- | 
| tsdata_list| Return TsData object list. | 
| metrics    | Return the metrics. |  
| tags       | Return the tags. |
| dps        | Return the pandas.DataFrame data. |
| info       | Show the data information and return a tuple of that. |
| [key]      | Return the pandas.Dataframe with columns included the key. |

**TsDataSet** examples:
```python
>>> from tsdata import TsDataSet
>>> TsDataSet_response = \
...     [
...         {
...             "metric": "test_rps",
...             "tags": {
...                 "host": "host1"
...             },
...             "aggregateTags": [],
...             "dps": {
...                 "1507510800": 54.58156394958496,
...                 "1507510860": 65.78498077392578,
...                 "1507510920": 70.2049331665039
...             }
...         },
...         {
...             "metric": "test_rps",
...             "tags": {
...                 "host": "host2"
...             },
...             "aggregateTags": [],
...             "dps": {
...                 "1507510800": 109.16312789916992,
...                 "1507510860": 131.56996154785156,
...                 "1507510920": 140.4098663330078
...             }
...         }
...     ]
>>> TsDataSet(TsDataSet_response)
                     test_rps{host=host1}  test_rps{host=host2}
Time
2017-10-09 09:00:00             54.581564            109.163128
2017-10-09 09:01:00             65.784981            131.569962
2017-10-09 09:02:00             70.204933            140.409866
>>> TsDataSet(TsDataSet_response).tsdata_list
[{
    'metric': 'test_rps',
    'tags': {
         '{host=host1}'
    },
    'aggregateTags': [],
    'dps':
                     test_rps{host=host1}
Time
2017-10-09 09:00:00             54.581564
2017-10-09 09:01:00             65.784981
2017-10-09 09:02:00             70.204933
}, {
    'metric': 'test_rps',
    'tags': {
         '{host=host2}'
    },
    'aggregateTags': [],
    'dps':
                     test_rps{host=host2}
Time
2017-10-09 09:00:00            109.163128
2017-10-09 09:01:00            131.569962
2017-10-09 09:02:00            140.409866
}]
>>> TsDataSet(TsDataSet_response).metrics
set(['test_rps'])
>>> TsDataSet(TsDataSet_response).tags
set(['{host: host2}', '{host: host1}'])
>>> TsDataSet(TsDataSet_response).dps
                     test_rps{host=host1}  test_rps{host=host2}
Time
2017-10-09 09:00:00             54.581564            109.163128
2017-10-09 09:01:00             65.784981            131.569962
2017-10-09 09:02:00             70.204933            140.409866
>>> TsDataSet(TsDataSet_response).info
<class 'tsdata.TsDataSet'>
From:   '2017-10-09 09:00:00'
To:     '2017-10-09 09:02:00'
Days:   1
Shape:  (3, 2)
NaN:    0(0.0%)
PPD:    3.0
('2017-10-09 09:00:00', '2017-10-09 09:02:00', 1, (3, 2), 0, 0.0, 3.0)
>>> TsDataSet(TsDataSet_response)['host1']
                     test_rps{host=host1}
Time
2017-10-09 09:00:00             54.581564
2017-10-09 09:01:00             65.784981
2017-10-09 09:02:00             70.204933
>>> TsDataSet(TsDataSet_response)['host3']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "tsdata.py", line 96, in __getitem__
    raise KeyError(key)
KeyError: 'host3'
```
## Connection
class **Connection**(server='localhost', port=4242)
> Build a connection with an OpenTSDB and return a new connection object.

| Operation  | Description       |  Input |
| ---------- | ----------------- | ------- |
| read_ts    | Return a TsDataSet object by querying the OpenTSDB with a json BodyContent. | **(dict) |
| read_df    | Return a pandas.DataFrame object by querying the OpenTSDB with a json BodyContent. | **(dict) |
| write_ts   | Return the summary results of writing. | list, TsDataSet, or pandas.DataFrame |

**Connection** examples:
```python
>>> from client import Connection
>>> # Bad connection
... connection = Connection('192.168.1.91', 4242)
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
  File "client.py", line 51, in __init__
    ping(server, port)
  File "client.py", line 40, in ping
    raise Exception('Can\'t connect to OpenTSDB Server')
Exception: Can't connect to OpenTSDB Server
>>> # Good connection
... connection = Connection('192.168.1.91', 4243)
Ping 192.168.1.91:4243 ... OpenTSDB connection status: OK
>>> BodyContent = {
...         "start": 1507510800000,
...         "end": 1507510980000,
...         "queries": [{
...             "metric": "test_rps",
...             "aggregator": "avg",
...             "downsample": "1m-avg-nan",
...             "filters": [{
...                     "tagk": "host",
...                     "type": "wildcard",
...                     "filter": "*",
...                     "group_by": True
...                     }
...             ]
...         }, {
...             "metric": "test_cpu",
...             "aggregator": "avg",
...             "downsample": "1m-avg-nan",
...             "filters": [{
...                 "tagk": "host",
...                 "type": "wildcard",
...                 "filter": "*",
...                 "group_by": True
...             }
...             ]
...         }
...         ]
...     }
>>> connection.read_ts(**BodyContent)
                     test_rps{host=host1}  test_rps{host=host2}  \
Time
2017-10-09 09:00:00             54.581566            113.239864
2017-10-09 09:01:00             65.784981            133.319458
2017-10-09 09:02:00             70.204933            141.997871
2017-10-09 09:03:00                   NaN                   NaN

                     test_cpu{host=host1}  test_cpu{host=host2}
Time
2017-10-09 09:00:00              1.606581              3.213163
2017-10-09 09:01:00              1.765905              3.531810
2017-10-09 09:02:00              1.846433              3.692867
2017-10-09 09:03:00                   NaN                   NaN
>>> type(connection.read_ts(**BodyContent))
<class 'tsdata.TsDataSet'>
>>> connection.read_df(**BodyContent)
                     test_rps{host=host1}  test_rps{host=host2}  \
Time
2017-10-09 09:00:00             54.581566            113.239864
2017-10-09 09:01:00             65.784981            133.319458
2017-10-09 09:02:00             70.204933            141.997871
2017-10-09 09:03:00                   NaN                   NaN

                     test_cpu{host=host1}  test_cpu{host=host2}
Time
2017-10-09 09:00:00              1.606581              3.213163
2017-10-09 09:01:00              1.765905              3.531810
2017-10-09 09:02:00              1.846433              3.692867
2017-10-09 09:03:00                   NaN                   NaN
>>> type(connection.read_df(**BodyContent))
<class 'pandas.core.frame.DataFrame'>
>>> BodyContent = \
...         [
...             {
...                 "metric": "test_rps",
...                 "timestamp": 1507510800,
...                 "value": 54.58156394958496,
...                 "tags": {
...                     "host": "host1"
...                 }
...             },
...             {
...                 "metric": "test_rps",
...                 "timestamp": 1507510830,
...                 "value": 54.58156394958496,
...                 "tags": {
...                     "host": "host1"
...                 }
...             },
...             {
...                 "metric": "test_rps",
...                 "timestamp": 1507510860,
...                 "value": 65.78498077392578,
...                 "tags": {
...                     "host": "host1"
...                 }
...             },
...         ]
>>> connection.write_ts(BodyContent)
{failed:0, success:3}
>>> BodyContent = {
...         "start": 1507510800000,
...         "end": 1507510980000,
...         "queries": [{
...             "metric": "test_rps",
...             "aggregator": "avg",
...             "downsample": "1m-avg-nan",
...             "filters": [{
...                     "tagk": "host",
...                     "type": "wildcard",
...                     "filter": "*",
...                     "group_by": True
...                     }
...             ]
...         }, {
...             "metric": "test_cpu",
...             "aggregator": "avg",
...             "downsample": "1m-avg-nan",
...             "filters": [{
...                 "tagk": "host",
...                 "type": "wildcard",
...                 "filter": "*",
...                 "group_by": True
...             }
...             ]
...         }
...         ]
...     }
>>> tsdataset = connection.read_ts(**BodyContent)
>>> df = connection.read_df(**BodyContent)
>>> connection.write_ts(tsdataset)
{failed:0, success:12}
>>> connection.write_ts(df)
{failed:0, success:12}
```