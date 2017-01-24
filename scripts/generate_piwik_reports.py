import argparse
from piwik.analytics import Analytics
from datetime import date, timedelta
from collections import defaultdict
from json import dumps


today = date.today().strftime('%Y-%m-%d')


def parse_args():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--url',
                        help='Your Piwik API URL',
                        required=True
                        )
    parser.add_argument('--authToken',
                        help='Authenticate to the API via token_auth parameter',
                        required=True
                        )
    parser.add_argument('--method',
                        help='the API method you want to call.',
                        required=True
                        )
    parser.add_argument('--segment',
                        help='defines the Custom Segment you wish to filter your reports to',
                        default=None
                        )
    parser.add_argument('--idSite',
                        help='the integer id of your website',
                        required=True
                        )
    parser.add_argument('--period',
                        help='the period you request the statistics for.',
                        default='month'
                        )
    parser.add_argument('--date',
                        help='YYYY-MM-DD or lastX or today or yesterday',
                        default=today + ',' + today
                        )
    parser.add_argument('--columns',
                        help='a comma separated list of columns.',
                        default=None
                        )
    parser.add_argument('--groupBy',
                        help='a id column that should exist in all rows of the result',
                        default=None
                        )
    parser.add_argument('--countColumns',
                        help='a comma separated list of columns.',
                        required=True,
                        )
    parser.add_argument('--textColumns',
                        help='a comma separated list of columns, work only if groupBy is present '
                             'and text columns are unique',
                        default=None,
                        )
    parser.add_argument('--expanded',
                        help='If expanded is set to 1, the returned data will contain the first level results,'
                             ' as well as all sub-tables',
                        default=0
                        )
    parser.add_argument('--depth',
                        help='related to expanded',
                        default=None
                        )
    parser.add_argument('--flat',
                        help='return flat view of hierarchical records',
                        default=None
                        )
    parser.add_argument('--ignoreURLQueryStrings',
                        help='only count base urls',
                        default=0
                        )
    return parser.parse_args()


config = parse_args()


def main():
    pa = Analytics(url=config.url, id_site=config.idSite, token_auth=config.authToken)
    pa.set_param('date', config.date)
    pa.set_param('period', config.period)
    pa.set_param('method', config.method)
    pa.set_param('filter_limit', '-1')
    if config.expanded:
        pa.set_param('expanded', config.expanded)
        if config.depth:
            pa.set_param('depth', config.depth)
    if config.flat:
        pa.set_param('flat', config.flat)
    if config.segment:
        pa.set_param('segment', config.segment)
    if config.columns:
        pa.set_param('showColumns', config.columns)
    response = pa.get()

    report = defaultdict(lambda: defaultdict(dict))
    report['total'] = defaultdict(lambda: defaultdict(dict))
    report['years'] = defaultdict(lambda: defaultdict(dict))

    if ',' in config.idSite:
        for key in response.keys():
            iterate_response(response[key], report)
    else:
        iterate_response(response, report)

    print(dumps(report))


def iterate_response(response, report):

    keys = response.keys()

    # lazy counting -- can be fast
    for key in keys:
        dmy = key.split('-')
        year = dmy[0]
        row = response[key]
        # total
        add_counts(row, report['total'])
        # year total
        add_counts(row, report['years'][year])
        if len(dmy) > 1:
            month = dmy[1]
            if 'months' not in report['years'][year]:
                report['years'][year]['months'] = defaultdict(lambda: defaultdict(dict))
            # month total
            add_counts(row, report['years'][year]['months'][month])
        if len(dmy) > 2:
            day = dmy[2]
            if 'days' not in report['years'][year]['months'][month]:
                report['years'][year]['months'][month]['days'] = defaultdict(lambda: defaultdict(dict))
            # day count
            add_counts(row, report['years'][year]['months'][month]['days'][day])


def add_counts(row, report):
    try:
        if config.groupBy:
            lc = config.groupBy
            tc = []
            if config.textColumns:
                tc = config.textColumns.split(',')
            for cc in config.countColumns.split(','):
                if isinstance(row, dict):
                    group_by = row[lc]
                    if config.ignoreURLQueryStrings == '1':
                        group_by = group_by.split('?')[0]
                        report[group_by].update({tcc: row[tcc].split('?')[0] for tcc in tc if tcc in r})
                    else:
                        report[group_by].update({tcc: row[tcc] for tcc in tc if tcc in r})
                    if cc in report[group_by]:
                        report[group_by][cc] += row[cc]
                    else:
                        report[group_by][cc] = row[cc]
                elif isinstance(row, list):
                    for r in row:
                        group_by = r[lc]
                        if config.ignoreURLQueryStrings == '1':
                            group_by = group_by.split('?')[0]
                            report[group_by].update({tcc: r[tcc].split('?')[0] for tcc in tc if tcc in r})
                        else:
                            report[group_by].update({tcc: r[tcc] for tcc in tc if tcc in r})
                        if cc in report[group_by]:
                            report[group_by][cc] += r[cc]
                        else:
                            report[group_by][cc] = r[cc]
        else:
            for cc in config.countColumns.split(','):
                if isinstance(row, dict):
                    if cc in report:
                        report[cc] += row[cc]
                    else:
                        report[cc] = row[cc]
                elif isinstance(row, list):
                    for r in row:
                        if cc in report:
                            report[cc] += r[cc]
                        else:
                            report[cc] = r[cc]
    except KeyError:
        return


if __name__ == '__main__':
    main()
