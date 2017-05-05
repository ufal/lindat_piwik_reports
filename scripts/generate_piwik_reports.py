#!/usr/bin/python3.5

import argparse
from piwik.analytics import Analytics
from datetime import date, timedelta
from json import dump, dumps, load
from copy import deepcopy

today = date.today().strftime('%Y-%m-%d')
update_file = None


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
    parser.add_argument('--update',
                        help='if available will use the update-file parameter to read the already available report',
                        default=False,
                        action='store_true'
                        )
    parser.add_argument('--update-file',
                        help='filename of the report to be updated',
                        default=None
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

    report = None
    response = pa.get()

    if config.update:
        with open(config.update_file) as data_file:
            report = load(data_file)
        if ',' in config.idSite:
            for key in response.keys():
                iterate_response_remove_counts(response[key], report, remove_counts)
        else:
            iterate_response_remove_counts(response, report, remove_counts)
    else:
        report = dict()

        if ',' in config.idSite:
            for key in response.keys():
                iterate_response(response[key], report, add_counts)
        else:
            iterate_response(response, report, add_counts)

    if config.update:
        with open(config.update_file, 'w', encoding='utf8') as data_file:
            dump(report, data_file, indent=4, ensure_ascii=False)
    else:
        print(dumps(report))


def iterate_response(response, report, function):

    keys = response.keys()

    # lazy counting -- can be fast
    for key in keys:
        dmy = key.split('-')
        year = dmy[0]
        row = response[key]
        # total
        if 'total' not in report:
            report['total'] = dict()
        function(row, report['total'])
        # year total
        if 'years' not in report:
            report['years'] = dict()
        if year not in report['years']:
            report['years'][year] = dict()
        function(row, report['years'][year])
        if len(dmy) > 1:
            month = dmy[1]
            if 'months' not in report['years'][year]:
                report['years'][year]['months'] = dict()
            if month not in report['years'][year]['months']:
                report['years'][year]['months'][month] = dict()
            # month total
            function(row, report['years'][year]['months'][month])
        if len(dmy) > 2:
            day = dmy[2]
            if 'days' not in report['years'][year]['months'][month]:
                report['years'][year]['months'][month]['days'] = dict()
            if day not in report['years'][year]['months'][month]['days']:
                report['years'][year]['months'][month]['days'][day] = dict()
            # day count
            function(row, report['years'][year]['months'][month]['days'][day])


def add_counts(row, report):
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
                    if group_by not in report:
                        report[group_by] = dict()
                    if len(tc) > 0:
                        report[group_by].update({tcc: row[tcc].split('?')[0] for tcc in tc if tcc in r})
                else:
                    if group_by not in report:
                        report[group_by] = dict()
                    if len(tc) > 0:
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
                        if group_by not in report:
                            report[group_by] = dict()
                        if len(tc) > 0:
                            report[group_by].update({tcc: r[tcc].split('?')[0] for tcc in tc if tcc in r})
                    else:
                        if group_by not in report:
                            report[group_by] = dict()
                        if len(tc) > 0:
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


def iterate_response_remove_counts(response, report, function):

    keys = response.keys()

    # lazy counting -- can be fast
    for key in keys:
        dmy = key.split('-')
        year = dmy[0]
        if len(dmy) > 2:
            day = dmy[2]
            month = dmy[1]
            # day count
            if day in report['years'][year]['months'][month]['days']:
                row = deepcopy(report['years'][year]['months'][month]['days'][day])
                function(row, report['years'][year]['months'][month]['days'][day])
                function(row, report['years'][year]['months'][month])
                function(row, report['years'][year])
                function(row, report['total'])
        elif len(dmy) > 1:
            month = dmy[1]
            if month in report['years'][year]['months']:
                row = deepcopy(report['years'][year]['months'][month])
                function(row, report['years'][year]['months'][month])
                function(row, report['years'][year])
                function(row, report['total'])
        else:
            if year not in report['years']:
                row = deepcopy(report['years'][year])
                function(row, report['years'][year])
                function(row, report['total'])


def remove_counts(row, report):

    for key in row.keys():
        if key in report:
            if isinstance(row[key], dict):
                for innerKey in row[key].keys():
                    if innerKey in report[key]:
                        if isinstance(row[key][innerKey], int):
                            report[key][innerKey] -= row[key][innerKey]
            else:
                if isinstance(row[key], int):
                    report[key] -= row[key]


if __name__ == '__main__':
    main()
