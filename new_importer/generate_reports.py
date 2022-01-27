from datetime import datetime
import json
import logging as log
import os
import re
import time

import mysql.connector
from pathvalidate import ValidationError, validate_filename
import pycountry

from config import *
from statements import statements, segment2where

lvl = os.environ.get('LOG_LEVEL', 'INFO')
log.basicConfig(level=getattr(log, lvl.upper(), None))

segments = ['overall', 'downloads', 'repository', 'others', 'services', 'lrt', 'lrt-downloads']
handle_pattern = re.compile('.*handle/([-\w+]+)/([-\w+]+)/?.*', re.ASCII)


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
    log.info("Elapsed time in %s: %s",stats_kind, elapsed_time)


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


def get_handles(cursor):
    start_time = time.perf_counter()
    handles = {}
    for what in ['views', 'downloads']:  #
        segment_start_time = time.perf_counter()
        query = _format_query_for_segment(statements['handles'], 'handle-' + what)
        cursor.execute(query)
        for row in cursor:
            if not row['handle']:
                continue
            try:
                hdl_prefix, hdl_suffix = row['handle'].split('/', 1)
                m = handle_pattern.match(row['name'])
                if m:
                    extracted_hdl_prefix, extracted_hdl_suffix = m.groups()
                    if not (hdl_prefix == extracted_hdl_prefix and hdl_suffix == extracted_hdl_suffix):
                        log.debug("Skipping row '%s'", row)
                        continue
                else:
                    continue
                validate_filename(hdl_prefix)
                validate_filename(hdl_suffix)
            except Exception as e:
                log.debug("Skipping (invalid filename) handle='%s'\nname='%s'", row['handle'], row['name'])
                continue

            handle = handles.setdefault(row['handle'], {'views': {}, 'downloads': {}})
            handle = handle.setdefault(what, {})
            _handle_mapper(row, handle)
        elapsed_time = time.perf_counter() - segment_start_time
        log.info("Elapsed time in %s '%s': %s", 'handles', what, elapsed_time)

    log.debug("There are %s items in the handles dict", len(handles))
    for hdl in handles.keys():
        hdl_prefix, hdl_suffix = hdl.split('/', 1)
        try:
            validate_filename(hdl_prefix)
            validate_filename(hdl_suffix)
        except ValidationError as e:
            log.error("%s", e)
            log.debug("Skipping writing of '%s'", hdl)
            continue

        prefix = os.path.join('handle', hdl_prefix, hdl_suffix)
        yearly_report = {
            'views': handles[hdl]['views'].setdefault('year', {}),
            'downloads': handles[hdl]['downloads'].setdefault('year', {})
        }
        output_prefix = os.path.join(output_dir, prefix)
        log.debug("Writing to %s", output_prefix)
        os.makedirs(output_prefix, exist_ok=True)
        with open(os.path.join(output_prefix, 'response.json'), 'w') as f:
            json.dump({'response': yearly_report}, f)
        years = set(yearly_report['views'].keys()).union(yearly_report['downloads'].keys())
        years.discard('total')
        for year in years:
            views = {
                year: handles[hdl]['views'].setdefault('month', {}).setdefault(year, {}),
                'total': {
                    year: handles[hdl]['views'].setdefault('month', {}).setdefault('total', {}).setdefault(year, {})
                }
            }
            downloads = {
                year: handles[hdl]['downloads'].setdefault('month', {}).setdefault(year, {}),
                'total': {
                    year: handles[hdl]['downloads'].setdefault('month', {}).setdefault('total', {})
                    .setdefault(year, {})
                }
            }
            per_month_report = {
                'views': views,
                'downloads': downloads
            }
            filename = os.path.join(output_prefix, str(year), 'response.json')
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump({'response': per_month_report}, f)
            months = set(views[year].keys()).union(downloads[year].keys())
            for month in months:
                views = {
                    year: {
                        month: handles[hdl]['views'].setdefault('day', {}).setdefault(year, {}).setdefault(month, {}),
                    },
                    'total':
                        {
                            year: {
                                month:
                                    handles[hdl]['views'].setdefault('day', {}).setdefault('total', {})
                                    .setdefault(year, {}).setdefault(month, {})
                            }
                        }
                }
                downloads = {
                    year: {
                        month: handles[hdl]['downloads'].setdefault('day', {}).setdefault(year, {}).setdefault(month, {}),
                    },
                    'total':
                        {
                            year: {
                                month:
                                    handles[hdl]['downloads'].setdefault('day', {}).setdefault('total', {})
                                    .setdefault(year, {}).setdefault(month, {})
                            }
                        }
                }
                per_day_report = {
                    'views': views,
                    'downloads': downloads
                }
                filename = os.path.join(output_prefix, str(year), str(month), 'response.json')
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'w') as f:
                    json.dump({'response': per_day_report}, f)

    elapsed_time = time.perf_counter() - start_time
    log.info("Elapsed time in %s: %s", 'handles', elapsed_time)


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
            with open(os.path.join(output_prefix, 'country_response.json'), 'w') as f:
                json.dump({date: countries}, f)
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
        'nb_uniq_pageviews': row['visits']
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


def _handle_mapper(row, handle):
    # sum of all under handle n-y-m-d doesn't matter -> views.total.nb_hits/visits -> year
    # sum of all under handle in a year n-m-d doesn't matter -> views.total["2018"].nb_hits -> year
    # sum of all under handle in a year-month n-d doesn't matter -> views.total["2018"]["3"].nb_hits -> month
    # sum of all under handle in a year-month-day name doesn't matter ->views.total["2018"]["3"]["27"].nb_hits -> day
    # sum of all under handle, year and name, m-d doesn't matter ->views["2018"].`name`.nb_hits -> year
    # sum of all under handle, year, month and name, d doesn't matter ->views["2018"]["3"].`name`.nb_hits -> month
    # sum of all under handle, year, month, day and name ->views["2018"]["3"]["27"].`name`.nb_hits -> day
    y = row['year']
    m = row['month']
    d = row['day']
    n = row['name']
    hits = row['hits']
    visits = row['visits']
    for x in [
        # year
        handle.setdefault('year', {}).setdefault('total', {'nb_hits': 0, 'nb_visits': 0}),
        handle['year']['total'].setdefault(y, {'nb_hits': 0, 'nb_visits': 0}),
        handle['year'].setdefault(y, {}).setdefault(n, {'nb_hits': 0, 'nb_visits': 0}),

        # month
        handle.setdefault('month', {}).setdefault('total', {}).setdefault(y, {})
            .setdefault(m, {'nb_hits': 0, 'nb_visits': 0}),
        handle['month'].setdefault(y, {}).setdefault(m, {}).setdefault(n, {'nb_hits': 0, 'nb_visits': 0}),

        # day
        handle.setdefault('day', {}).setdefault('total', {}).setdefault(y, {})
            .setdefault(m, {}).setdefault(d, {'nb_hits': 0, 'nb_visits': 0}),
        handle['day'].setdefault(y, {}).setdefault(m, {}).setdefault(d, {})
            .setdefault(n, {'nb_hits': 0, 'nb_visits': 0})
    ]:
        x['nb_hits'] += hits
        x['nb_visits'] += visits


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
        get_handles(cursor)
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
