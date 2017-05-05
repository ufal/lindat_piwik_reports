#!/usr/bin/python3.5

import argparse
from piwik.analytics import Analytics
from datetime import date
from luc import indexer

today = date.today().strftime('%Y-%m-%d')

m2m = {
    "Actions.get": "index_views",
    "VisitsSummary.get": "index_visits",
    "UserCountry.getCountry": "index_country",
    "Actions.getPageUrls": "index_urls"
}


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

    if ',' in config.idSite:
        for key in response.keys():
            iterate_response(key, response[key])
    else:
        iterate_response(config.idSite, response)


def iterate_response(site_id, response):

    keys = response.keys()

    for key in keys:
        dmy = key.split('-')
        row = response[key]
        if row:
            ind = indexer.Indexer()
            function_to_call = getattr(ind, m2m[config.method])
            function_to_call(site_id, dmy, row, config.segment, False)
            ind.close()


if __name__ == '__main__':
    main()
