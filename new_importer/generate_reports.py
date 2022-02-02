from datetime import datetime
import json
import logging as log
import os
import re
import time

import mysql.connector
import numpy as np
from pathvalidate import ValidationError, validate_filename
import pandas as pd
import pycountry

from config import *
from statements import statements, segment2where

lvl = os.environ.get('LOG_LEVEL', 'INFO')
log.basicConfig(level=getattr(log, lvl.upper(), None))

segments = ['overall', 'downloads', 'repository', 'others', 'services', 'lrt', 'lrt-downloads']
handle_pattern = re.compile('.*handle/([-\w+.]+)/([-\w+.]+)/?.*', re.ASCII)


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
        log.info("Elapsed time in %s segment '%s': %s", stats_kind, segment, elapsed_time)
        # download report from overall???
        # elif row['idsite'] == 4:
    elapsed_time = time.perf_counter() - start_time
    log.info("Elapsed time in %s: %s", stats_kind, elapsed_time)


def get_views(cursor):
    # XXX these totals include also numbers from anyone using our footer by accident
    _fetch_and_write(cursor, 'views')


def get_visits(cursor):
    _fetch_and_write(cursor, 'visits')


def get_country(cursor):
    _fetch_and_write(cursor, 'country')


def get_urls(cursor):
    start_time = time.perf_counter()
    for segment in segments:
        yearly_report = {}
        per_month_report = {}
        segment_start_time = time.perf_counter()
        query = _format_query_for_segment(statements['urls_total'], segment)
        cursor.execute(query)
        for row in cursor:
            _url_mapper(row, yearly_report, 'total')
        query = _format_query_for_segment(statements['urls_year'], segment)
        for result in cursor.execute(query, multi=True):
            if result.with_rows:
                for row in result:
                    _url_mapper(row, yearly_report, row['year'])
        query = _format_query_for_segment(statements['urls_month'], segment)
        for result in cursor.execute(query, multi=True):
            if result.with_rows:
                for row in result:
                    year = per_month_report.setdefault(row['year'], {})
                    _url_mapper(row, year, row['month'])

        prefix = os.path.join('urls', _segment2prefix(segment))
        _write_results(prefix, yearly_report, per_month_report, {})
        elapsed_time = time.perf_counter() - segment_start_time
        log.info("Elapsed time in %s segment '%s': %s", 'urls', segment, elapsed_time)
    elapsed_time = time.perf_counter() - start_time
    log.info("Elapsed time in %s: %s", 'urls', elapsed_time)


def get_handles(db):
    start_time = time.perf_counter()
    result = {}
    stats_kinds = ['views', 'downloads']
    data = {}
    for what in stats_kinds:
        query = _format_query_for_segment(statements['handles'], 'handle-' + what)
        db_fetch_start = time.perf_counter()
        df = pd.read_sql(query, db)
        db_fetch_elapsed = time.perf_counter() - db_fetch_start
        log.info("Elapsed time in handles fetching %s: %s", what, db_fetch_elapsed)
        filter_start = time.perf_counter()
        df = df[list(map(_sensible_handle_filter, df['handle'], df['name']))]
        filter_elapsed = time.perf_counter() - filter_start
        log.info("Elapsed time in handles filtering %s: %s", what, filter_elapsed)
        data[what] = df

    # with day resolution
    for what in stats_kinds:
        df = data[what]
        df.groupby(["handle", "name", "year", "month", "day"]) \
            .agg(**aggregates).reset_index().apply(
            lambda row: _handles_mapper(result, row, ['handle', what, 'year', 'month', 'day', 'name']),
            axis=1
        )
        df.groupby(["handle", "year", "month", "day"]) \
            .agg(**aggregates).reset_index().apply(
            lambda row: _handles_mapper(result, row, ['handle', what, 'total', 'year', 'month', 'day']),
            axis=1
        )
    _write_handle_result(result, 'day')
    result = {}
    # with month resolution
    for what in stats_kinds:
        df = data[what]
        df.groupby(["handle", "name", "year", "month"]) \
            .agg(**aggregates).reset_index().apply(
            lambda row: _handles_mapper(result, row, ['handle', what, 'year', 'month', 'name']),
            axis=1
        )
        df.groupby(["handle", "year", "month"]) \
            .agg(**aggregates).reset_index().apply(
            lambda row: _handles_mapper(result, row, ['handle', what, 'total', 'year', 'month']),
            axis=1
        )
    _write_handle_result(result, 'month')
    result = {}
    # with year resolution
    for what in stats_kinds:
        df = data[what]
        df.groupby(["handle", "name", "year"]) \
            .agg(**aggregates).reset_index().apply(
            lambda row: _handles_mapper(result, row, ['handle', what, 'year', 'name']),
            axis=1
        )
        df.groupby(["handle", "year"]) \
            .agg(**aggregates).reset_index().apply(
            lambda row: _handles_mapper(result, row, ['handle', what, 'total', 'year']),
            axis=1
        )
        # grand total
        df.groupby(["handle"]) \
            .agg(**aggregates).reset_index().apply(
            lambda row: _handles_mapper(result, row, ['handle', what, 'total']),
            axis=1
        )
    _write_handle_result(result, 'year')
    elapsed_time = time.perf_counter() - start_time
    log.info("Elapsed time in handles: %s", elapsed_time)


def get_handles_country(cursor):
    start_time = time.perf_counter()
    query = statements['handles_country']
    handles_country_report = {}
    for result in cursor.execute(query, multi=True):
        if result.with_rows:
            for row in result:
                hdl = row['handle']
                date = str(row['year']) + '/' + str(row['month'])
                countries = handles_country_report.setdefault(hdl, {}).setdefault(date, [])
                countries.append({
                    'label': _country_lookup(row['location_country']),
                    'nb_visits': row['visits']
                })
    for hdl, d in handles_country_report.items():
        hdl_prefix, hdl_suffix = hdl.split('/', 1)
        # Expects this is run after get_handles and dirs are created; if not skip
        for date, countries in d.items():
            output_prefix = os.path.join(output_dir, 'handle', hdl_prefix, hdl_suffix, date)
            if not os.path.isdir(output_prefix):
                log.debug("Skipping writing of '%s'; '%s' is not a dir", hdl, output_prefix)
                continue
            try:
                validate_filename(hdl_prefix)
                validate_filename(hdl_suffix)
            except ValidationError as e:
                log.error("%s", e)
                log.debug("Skipping writing of '%s'", hdl)
                continue
            output_prefix = os.path.join(output_prefix, 'country')
            os.mkdir(output_prefix)
            with open(os.path.join(output_prefix, 'response.json'), 'w') as f:
                json.dump({date.replace('/', '-'): countries}, f)
    elapsed_time = time.perf_counter() - start_time
    log.info("Elapsed time in %s: %s", 'handles country', elapsed_time)


def _segment2prefix(segment):
    if segment == 'overall':
        return ''
    else:
        return segment


def _format_query_for_segment(query, segment):
    segment_where_selector = segment2where[segment]
    return query.format(segment_where_selector)


def _views_mapper(row, result_dict, result_key):
    result_dict[result_key] = {
        'nb_pageviews': row['hits'],
        'nb_uniq_pageviews': row['uniq_pageviews']
    }


def _visits_mapper(row, result_dict, result_key):
    result_dict[result_key] = {
        'nb_uniq_visitors': row['visitors'],
        'nb_visits': row['visits']
    }


def _country_mapper(row, result_dict, result_key):
    d = result_dict.setdefault(result_key, {})
    d[row['location_country']] = {
        'nb_uniq_visitors': row['visitors'],
        'nb_visits': row['visits']
    }


def _url_mapper(row, result_dict, result_key):
    d = result_dict.setdefault(result_key, {})
    d[row['name']] = {
        'nb_hits': row['hits'],
        'nb_visits': row['visits']
    }


_stats_kind2mapper = {
    'views': _views_mapper,
    'visits': _visits_mapper,
    'country': _country_mapper
}


def _process_results(cursor, mapper):
    yearly_report = {}
    per_month_report = {}
    per_day_report = {}
    for row in cursor:
        # grand total
        if not row['idsite'] and not row['year'] and not row['month'] and not row['day']:
            mapper(row, yearly_report, 'total')
        # per year total
        elif not row['idsite'] and not row['month'] and not row['day']:
            mapper(row, yearly_report, row['year'])
        # per month total
        elif not row['idsite'] and not row['day']:
            year = per_month_report.setdefault(row['year'], {})
            mapper(row, year, row['month'])
        # per day total
        elif not row['idsite']:
            year = per_day_report.setdefault(row['year'], {})
            month = year.setdefault(row['month'], {})
            mapper(row, month, row['day'])
    return yearly_report, per_month_report, per_day_report


def _write_results(prefix, yearly_report, per_month_report, per_day_report):
    output_prefix = os.path.join(output_dir, prefix)
    log.info("Writing to %s", output_prefix)
    os.makedirs(output_prefix, exist_ok=True)
    with open(os.path.join(output_prefix, 'response.json'), 'w') as f:
        json.dump({'response': yearly_report}, f)
    for year in per_month_report.keys():
        filename = os.path.join(output_prefix, str(year), 'response.json')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump({'response': {year: per_month_report[year]}}, f)
        for month in per_day_report.get(year, {}).keys():
            filename = os.path.join(output_prefix, str(year), str(month), 'response.json')
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump({'response': {year: {month: per_day_report[year][month]}}}, f)


def _country_lookup(code):
    code = code.upper()
    if code == 'AP':
        ret = 'Asia/Pacific'
    elif code == 'EU':
        ret = 'Europe'
    elif code == 'A1':
        ret = 'anonymous proxy'
    elif code == 'A2':
        ret = 'satellite provider'
    elif code == 'XX':
        ret = 'Unknown'
    else:
        ret = pycountry.countries.lookup(code).name
    return ret


def _count_distinct(column):
    return len(np.unique(column))


aggregates = {
    'hits': pd.NamedAgg("idaction", "count"),
    'visits': pd.NamedAgg("idvisit", _count_distinct),
    'uniq_pageviews': pd.NamedAgg("visit_action", _count_distinct),
    'visitors': pd.NamedAgg("idvisitor", _count_distinct)
}


def _sensible_handle_filter(handle, name):
    if not handle:
        return False
    try:
        hdl_prefix, hdl_suffix = handle.split('/', 1)
        m = handle_pattern.match(name)
        if m:
            extracted_hdl_prefix, extracted_hdl_suffix = m.groups()
            if not (hdl_prefix == extracted_hdl_prefix and hdl_suffix == extracted_hdl_suffix):
                log.debug("Skipping row handle='%s'; name='%s'", handle, name)
                return False
        else:
            log.debug("Skipping, name not matching pattern '%s'", name)
            return False
        validate_filename(hdl_prefix)
        validate_filename(hdl_suffix)
    except Exception as e:
        log.debug("Skipping (invalid filename) handle='%s'\nname='%s'", handle, name)
        return False
    return True


def _write_handle_result(result, resolution):
    for hdl in result.keys():
        report = result[hdl]
        hdl_prefix, hdl_suffix = hdl.split('/', 1)
        prefix = os.path.join('handle', hdl_prefix, hdl_suffix)
        views = report.get('views', {})
        downloads = report.get('downloads', {})
        if resolution != 'year':
            years = set(views.keys()).union(downloads.keys())
            years.discard('total')
            for year in years:
                if resolution == 'day':
                    months = set(views.get(year, {}).keys()).union(downloads.get(year, {}).keys())
                    for month in months:
                        v = {
                            year: {
                                month: views.setdefault(year, {}).setdefault(month, {})
                            },
                            'total': {
                                year: {
                                    month: views.setdefault('total', {}).setdefault(year, {}).setdefault(month, {})
                                }
                            }
                        }
                        d = {
                            year: {
                                month: downloads.setdefault(year, {}).setdefault(month, {})
                            },
                            'total': {
                                year: {
                                    month: downloads.setdefault('total', {}).setdefault(year, {}).setdefault(month, {})
                                }
                            }
                        }
                        p = os.path.join(output_dir, prefix, str(year), str(month))
                        _write_response(p, v, d)
                else:
                    v = {
                        year: views.setdefault(year, {}),
                        'total': {
                            year: views.setdefault('total', {}).setdefault(year, {}),
                        }
                    }
                    d = {
                        year: downloads.setdefault(year, {}),
                        'total': {
                            year: downloads.setdefault('total', {}).setdefault(year, {}),
                        }
                    }
                    p = os.path.join(output_dir, prefix, str(year))
                    _write_response(p, v, d)
        else:
            p = os.path.join(output_dir, prefix)
            _write_response(p, views, downloads)


def _write_response(path, views, downloads):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'response.json'), 'w') as f:
        json.dump({
            'response': {
                'views': views,
                'downloads': downloads
            }
        }, f)


def _handles_mapper(result_dict, row, keys):
    hits = row.hits
    visits = row.visits
    uniq_pageviews = row.uniq_pageviews
    visitors = row.visitors
    d = result_dict
    for key in keys:
        if key in row:
            key = row[key]
        d = d.setdefault(key, {})
    d['nb_hits'] = hits
    d['nb_visits'] = visits
    d['nb_uniq_visitors'] = visitors
    d['nb_uniq_pageviews'] = uniq_pageviews


def main():
    log.debug("Debug logging is enabled")
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        start_time = time.perf_counter()
        # These are for /statistics report
        get_views(cursor)
        get_visits(cursor)
        get_country(cursor)
        get_urls(cursor)
        # These are for repository
        get_handles(db)
        get_handles_country(cursor)
        elapsed_time = time.perf_counter() - start_time
        log.info("Elapsed time fetching all: %s", elapsed_time)
        today = datetime.now()
        with open(os.path.join(output_dir, 'last_updated.txt'), 'w') as f:
            print(today, file=f)
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    main()
