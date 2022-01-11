import json
import os
import time

import mysql.connector

from config import *
from statements import statements, segment2where

segments = ['overall', 'downloads', 'repository', 'others', 'services', 'lrt']


def _fetch_and_write(cursor, stats_kind):
    start_time = time.perf_counter()
    for segment in segments:
        segment_start_time = time.perf_counter()
        query = _format_query_for_segment(statements[stats_kind], segment)
        prefix = os.path.join(stats_kind, _segment2prefix(segment))
        mapper = _stats_kind2mapper[stats_kind]
        cursor.execute(query)
        yearly_report, per_month_report, per_day_report = _process_results(cursor, mapper)
        _write_results(prefix, yearly_report, per_month_report, per_day_report)
        elapsed_time = time.perf_counter() - segment_start_time
        print("Elapsed time in {} segment '{}': {}".format(stats_kind, segment, elapsed_time))
        # download report from overall???
        # elif row['idsite'] == 4:
    elapsed_time = time.perf_counter() - start_time
    print("Elapsed time in {}: {}".format(stats_kind, elapsed_time))


def get_views(cursor):
    # XXX these totals include also numbers from anyone using our footer by accident
    _fetch_and_write(cursor, 'views')


def get_visits(cursor):
    _fetch_and_write(cursor, 'visits')


def get_country(cursor):
    pass


def get_urls(cursor):
    pass


def _segment2prefix(segment):
    if segment == 'overall':
        return ''
    else:
        return segment


def _format_query_for_segment(query, segment):
    segment_where_selector = segment2where[segment]
    return query.format(segment_where_selector)


_stats_kind2mapper = {
    'views': lambda row: {
        'nb_pageviews': row['hits'],
        'nb_uniq_pageviews': row['visits']
    },
    'visits': lambda row: {
        'nb_uniq_visitors': row['visitors'],
        'nb_visits': row['visits']
    }
}


def _process_results(cursor, mapper):
    yearly_report = {}
    per_month_report = {}
    per_day_report = {}
    for row in cursor:
        # grand total
        if not row['idsite'] and not row['year'] and not row['month'] and not row['day']:
            yearly_report['total'] = mapper(row)
        # per year total
        elif not row['idsite'] and not row['month'] and not row['day']:
            yearly_report[row['year']] = mapper(row)
        # per month total
        elif not row['idsite'] and not row['day']:
            year = per_month_report.setdefault(row['year'], {})
            year[row['month']] = mapper(row)
        # per day total
        elif not row['idsite']:
            year = per_day_report.setdefault(row['year'], {})
            month = year.setdefault(row['month'], {})
            month[row['day']] = mapper(row)
    return yearly_report, per_month_report, per_day_report


def _write_results(prefix, yearly_report, per_month_report, per_day_report):
    output_prefix = os.path.join(output_dir, prefix)
    print("Writing to {}".format(output_prefix))
    os.makedirs(output_prefix, exist_ok=True)
    with open(os.path.join(output_prefix, 'response.json'), 'w') as f:
        json.dump({'response': yearly_report}, f)
    for year in per_month_report.keys():
        filename = os.path.join(output_prefix, str(year), 'response.json')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump({'response': {year: per_month_report[year]}}, f)
        for month in per_day_report[year].keys():
            filename = os.path.join(output_prefix, str(year), str(month), 'response.json')
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump({'response': {year: {month: per_day_report[year][month]}}}, f)


def main():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        start_time = time.perf_counter()
        get_views(cursor)
        get_visits(cursor)
        elapsed_time = time.perf_counter() - start_time
        print("Elapsed time fetching all: {}".format(elapsed_time))
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    main()
