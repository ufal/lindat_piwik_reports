import json
import os
import time

import mysql.connector

from config import *
from statements import *


def get_views(cursor):
    # XXX these totals include also numbers from anyone using our footer by accident

    start_time = time.perf_counter()
    cursor.execute(hits_visits_aggregated)
    yearly_report = {}
    per_month_report = {}
    per_day_report = {}
    for row in cursor:
        # grand total
        if not row['idsite'] and not row['year'] and not row['month'] and not row['day']:
            yearly_report['total'] = {
                'nb_pageviews': row['hits'],
                'nb_uniq_pageviews': row['visits']
            }
        # per year total
        elif not row['idsite'] and not row['month'] and not row['day']:
            yearly_report[row['year']] = {
                'nb_pageviews': row['hits'],
                'nb_uniq_pageviews': row['visits']
            }
        # per month total
        elif not row['idsite'] and not row['day']:
            year = per_month_report.setdefault(row['year'], {})
            year[row['month']] = {
                    'nb_pageviews': row['hits'],
                    'nb_uniq_pageviews': row['visits']
            }
        # per day total
        elif not row['idsite']:
            year = per_day_report.setdefault(row['year'], {})
            month = year.setdefault(row['month'], {})
            month[row['day']] = {
                'nb_pageviews': row['hits'],
                'nb_uniq_pageviews': row['visits']
            }
        # download report
        # elif row['idsite'] == 4:
    output_prefix = os.path.join(output_dir, 'views')
    print("Writing to {}".format(output_prefix))
    os.makedirs(output_prefix)
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
    elapsed_time = time.perf_counter() - start_time
    print("Elapsed time in get_views: {}".format(elapsed_time))


def main():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        get_views(cursor)
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    main()
