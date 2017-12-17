from __future__ import division
import pandas as pd


class TsData(object):
    __unit_table = {10: 's', 13: 'ms', 16: 'ns'}
    __timedelta = +8

    def __init__(self, **kwargs):
        self._metric = str(kwargs['metric'])
        self._tags = self.__format_tags(kwargs['tags'])
        self._aggregateTags = self.__format_aggr(kwargs['aggregateTags'])
        self._dps = self.__dict2df(kwargs['dps'])
        self._dps.index.name = 'Time'

    def __repr__(self):
        return "{{\n    'metric': {!r},\n    'tags': {{\n \
        {!r}\n    }},\n    'aggregateTags': {!r},\n    'dps': \n{!r}\n}}" \
        .format(self._metric, self._tags, self._aggregateTags, self._dps)

    def __dict2df(self, dict_data, timedelta=__timedelta):
        timestamps, data = zip(*sorted(dict_data.items()))
        try:
            unit = self.__unit_table[len(str(timestamps[0]))]
        except Exception as e:
            raise e('Timestamp Error!')
        return pd.DataFrame(list(data),
                            index=pd.to_datetime(timestamps, unit=unit) +
                            pd.Timedelta('{!r} h'.format(timedelta)),
                            columns=[self._metric + self._tags],
                            dtype='f8')

    def __format_tags(self, tags_dict):
        return '{' + ', '.join(str(k) + '=' + str(v)
                               for (k, v) in tags_dict.iteritems()) + '}'

    def __format_aggr(self, aggr_list):
        return [str(i) for i in aggr_list]

    @property
    def dps(self):
        """Return the pandas.DataFrame data."""
        return self._dps

    @property
    def metric(self):
        """Return the metric."""
        return self._metric

    @property
    def tags(self):
        """Return the tags."""
        return self._tags.replace('=', ': ')

    @property
    def aggr(self):
        """Return the aggregateTags"""
        return self._aggregateTags

    @property
    def data_info(self):
        """Show the data information and return a tuple of that."""
        idx = self._dps.index
        start = idx[0].strftime('%Y-%m-%d %H:%M:%S')
        end = idx[-1].strftime('%Y-%m-%d %H:%M:%S')
        date_list = sorted({i.strftime('%Y-%m-%d') for i in self._dps.index})
        shape = self._dps.shape
        nans = self._dps.isnull().sum().sum()
        nan_precent = self._dps.isnull().sum().sum() / self._dps.size
        print str(type(self)) + '\n' + \
            ('From: \t{!r}\nTo: \t{!r}\nDays: \t{!r}\n'
             'Shape: \t{!r}\nNaN: \t{!r}({:.1f}%)\nPPD: \t{!r}') \
            .format(start, end, len(date_list),
                    shape, nans, nan_precent * 100, shape[0] / len(date_list))
        return (start, end, len(date_list),
                shape, nans, nan_precent * 100, shape[0] / len(date_list))


class TsDataSet(object):
    def __init__(self, tsdata_list):
        self._tsdata_list = [TsData(**i) for i in tsdata_list]
        self._dps = pd.concat([i.dps for i in self._tsdata_list], axis=1)
        self._metrics = set(i.metric for i in self._tsdata_list)
        self._tags = set(i.tags for i in self._tsdata_list)

    def __repr__(self):
        return repr(self._dps)

    def __getitem__(self, key):
        """Return the pandas.Dataframe with columns included key."""
        frames = [
            i.dps for i in self._tsdata_list if key in i.metric + i.tags]
        if frames:
            return pd.concat(frames, axis=1)
        else:
            raise KeyError(key)

    @property
    def tsdata_list(self):
        """Return TsData object list."""
        return self._tsdata_list

    @property
    def metrics(self):
        """Return the metrics."""
        return self._metrics

    @property
    def tags(self):
        """Return the tags."""
        return self._tags

    @property
    def dps(self):
        """Return the pandas.DataFrame data."""
        return self._dps

    @property
    def info(self):
        """Show the data information and return a tuple of that."""
        idx = self._dps.index
        start = idx[0].strftime('%Y-%m-%d %H:%M:%S')
        end = idx[-1].strftime('%Y-%m-%d %H:%M:%S')
        date_list = sorted({i.strftime('%Y-%m-%d') for i in self._dps.index})
        shape = self._dps.shape
        nans = self._dps.isnull().sum().sum()
        nan_precent = self._dps.isnull().sum().sum() / self._dps.size
        print str(type(self)) + '\n' + \
            ('From: \t{!r}\nTo: \t{!r}\nDays: \t{!r}\n'
             'Shape: \t{!r}\nNaN: \t{!r}({:.1f}%)\nPPD: \t{!r}') \
            .format(start, end, len(date_list),
                    shape, nans, nan_precent * 100, shape[0] / len(date_list))
        return (start, end, len(date_list),
                shape, nans, nan_precent * 100, shape[0] / len(date_list))


if __name__ == '__main__':
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
    TsData_response = \
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

    print TsDataSet(TsDataSet_response)['host3']
    print TsData(**TsData_response).tags
