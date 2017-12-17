# -*- coding: utf-8 -*-
from tsdata import TsDataSet
import pandas as pd
try:
    # Use ujson if available.
    import ujson as json
except Exception:
    import json
import socket
import requests
import unittest
# import timeit


def ping(host, port):
    """
    Ping http://host:port.
    :param
        host:(str)
        port:(int)
    :return
        bool

    :doctest
    >>> ping('192.168.1.91', 4243)
    True
    >>> ping('192.168.1.91', 4243)
    True
    >>> ping('192.168.1.91', 4243)
    True
    """
    try:
        socket.socket().connect((host, port))
        print 'Ping {!s}:{!s} ... OpenTSDB connection status: OK'.format(
            host, port)
        return True
    except socket.error as err:
        if err.errno == socket.errno.ECONNREFUSED:
            raise Exception('Can\'t connect to OpenTSDB Server')
        raise Exception('Fail to test OpenTSDB connection status')


class Connection(object):
    __timedelta = +8

    def __init__(self, server='localhost', port=4242):
        self.server = server
        self.port = port
        # test the OpenTSDB connection status
        ping(server, port)
        self.url = 'http://{!s}:{:d}'.format(server, port)
        self.headers = {'content-type': 'application/json'}

    @staticmethod
    def __metric_tags(str_data):
        metric, tag_list = str_data[:-1].split('{')
        tags = dict(tuple(i.split('=')) for i in tag_list.split(','))
        return metric, tags

    def _read(self, **kwargs):
        r = requests.post(self.url + '/api/query',
                          data=json.dumps(kwargs), headers=self.headers)
        # check the response status
        r.raise_for_status()
        return json.loads(r.text)

    def _write(self, data):
        r = requests.post(self.url + '/api/put?summary',
                          data=json.dumps(data), headers=self.headers)
        # check the response status
        r.raise_for_status()
        result = json.loads(r.text)
        return '{' + ', '.join([str(k) + ':' + str(v)
                                for (k, v) in result.iteritems()]) + '}'

    def _write_df(self, df):
        # timestamp = [i.value // 10**9 for i in df.index]
        json_list = []
        for i in df.index:
            for j in df.columns:
                timestamp = (i - pd.Timedelta(
                    '{} h'.format(self.__timedelta))).value // 10**9
                metric, tags = self.__metric_tags(j)
                if pd.isna(df.loc[i, j]):
                    continue
                json_data = dict(
                    metric=metric,
                    timestamp=timestamp,
                    value=df.loc[i, j],
                    tags=tags)
                json_list.append(json_data)
        return self._write(json_list)

    def read_ts(self, **kwargs):
        """
        Return a TsDataSet object by querying the OpenTSDB
        with a json BodyContent.
        """
        result = self._read(**kwargs)
        return TsDataSet(result)

    def read_df(self, **kwargs):
        """
        Return a pandas.DataFrame object by querying the OpenTSDB
        with a json BodyContent.
        """
        return self.read_ts(**kwargs).dps

    def write_ts(self, data):
        """Return the summary results of writing."""
        if isinstance(data, list):
            print self._write(data)
        elif isinstance(data, pd.DataFrame):
            print self._write_df(data)
        elif isinstance(data, TsDataSet):
            print self._write_df(data.dps)
        else:
            raise Exception("***Data type must be list, "
                            "pd.DataFrame or TsDataSet!***")


class TestClientFuctions(unittest.TestCase):
    """
    Unittest.
    """

    def test_ping(self):
        self.assertEqual(ping('192.168.1.91', 4243), True)

    def test_connection(self):
        connection = Connection(server='192.168.1.91', port=4243)
        BodyContent = {
            "start": 1507510800000,
            "end": 1507510920000,
            "queries": [{
                "metric": "test_rps",
                "aggregator": "avg",
                "downsample": "1m-avg-nan",
                "filters": [{
                    "tagk": "host",
                    "type": "literal_or",
                    "filter": "host1",
                    "group_by": True
                }]
            }]
        }
        response = json.loads(
            '''
            [
                {
                    "metric": "test_rps",
                    "tags": {
                        "host": "host1"
                    },
                    "aggregateTags": [],
                    "dps": {
                        "1507510800": 54.58156204223633,
                        "1507510860": 65.78498077392578,
                        "1507510920": 70.2049331665039
                    }
                }
            ]
            '''
        )
        self.assertEqual(connection.read(**BodyContent), response)
        BodyContent = {
            "start": 1507510800000,
            "end": 1507510980000,
            "queries": [{
                "metric": "test_rps",
                "aggregator": "avg",
                "downsample": "1m-avg-nan",
                "filters": [{
                    "tagk": "host",
                    "type": "wildcard",
                    "filter": "*",
                    "group_by": True
                }
                ]
            }, {
                "metric": "test_cpu",
                "aggregator": "avg",
                "downsample": "1m-avg-nan",
                "filters": [{
                    "tagk": "host",
                    "type": "wildcard",
                    "filter": "*",
                    "group_by": True
                }
                ]
            }
            ]
        }
        response = json.loads(
            '''
                [
                    {
                        "metric": "test_rps",
                        "tags": {
                            "host": "host1"
                        },
                        "aggregateTags": [],
                        "dps": {
                            "1507510800": 54.58156394958496,
                            "1507510860": 65.78498077392578,
                            "1507510920": 70.2049331665039
                        }
                    }
                ]
                '''
        )
        self.assertEqual(connection.read_ts(**BodyContent).dps.shape, (4, 4))


# my test case
def test_ping(host, port):
    print "=== Begin Test ==="
    for i in range(3):
        if ping(host, port):
            print i, 'OpenTSDB connection OK!'
    print "=== End Test ==="


if __name__ == '__main__':
    do_unittest = False
    do_doctest = False

    # doctest
    if do_doctest:
        import doctest
        doctest.testmod()

    # test TsData class
    if do_unittest:
        # unittest.main()
        suite = unittest.TestLoader().loadTestsFromTestCase(TestClientFuctions)
        unittest.TextTestRunner(verbosity=2).run(suite)

    connection = Connection('192.168.1.91', 4243)
    BodyContent = {
        "start": 1507510800000,
        "end": 1507510980000,
        "queries": [{
            "metric": "test_rps",
            "aggregator": "avg",
            "downsample": "1m-avg-nan",
            "filters": [{
                    "tagk": "host",
                    "type": "wildcard",
                    "filter": "*",
                    "group_by": True
                    }
            ]
        }, {
            "metric": "test_cpu",
            "aggregator": "avg",
            "downsample": "1m-avg-nan",
            "filters": [{
                "tagk": "host",
                "type": "wildcard",
                "filter": "*",
                "group_by": True
            }
            ]
        }
        ]
    }
    data = connection.read_ts(**BodyContent)
    # df = data.dps
    print data.metrics
    # print data.tags
    # print data.dps
    df = connection.read_df(**BodyContent)
    print df

    # test write_ts
    TsDataSet_response = \
        [
            {
                "metric": "test_rps",
                "tags": {
                    "host": "host1"
                },
                "aggregateTags": [],
                "dps": {
                    "1507510800": 54.58156394958496,
                    "1507510860": 65.78498077392578,
                    "1507510920": 70.2049331665039
                }
            },
            {
                "metric": "test_rps",
                "tags": {
                    "host": "host2"
                },
                "aggregateTags": [],
                "dps": {
                    "1507510800": 109.16312789916992,
                    "1507510860": 131.56996154785156,
                    "1507510920": 140.4098663330078
                }
            },
            {
                "metric": "test_cpu",
                "tags": {
                    "host": "host1"
                },
                "aggregateTags": [
                    "dc"
                ],
                "dps": {
                    "1507510800": 1.6055501103401184,
                    "1507510860": 1.7576613426208496,
                    "1507510920": 1.845413327217102
                }
            },
            {
                "metric": "test_cpu",
                "tags": {
                    "host": "host2"
                },
                "aggregateTags": [
                    "dc"
                ],
                "dps": {
                    "1507510800": 3.211100220680237,
                    "1507510860": 3.515322685241699,
                    "1507510920": 3.690826654434204
                }
            }
        ]
    print TsDataSet(TsDataSet_response)
    BodyContent = \
        [
            {
                "metric": "test_rps",
                "timestamp": 1507510800,
                "value": 54.58156394958496,
                "tags": {
                    "host": "host1"
                }
            },
            {
                "metric": "test_rps",
                "timestamp": 1507510830,
                "value": 54.58156394958496,
                "tags": {
                    "host": "host1"
                }
            },
            {
                "metric": "test_rps",
                "timestamp": 1507510860,
                "value": 65.78498077392578,
                "tags": {
                    "host": "host1"
                }
            },
        ]
    # print connection.write_ts(BodyContent)
    response = connection.write_ts(df)

    # print data.metrics
