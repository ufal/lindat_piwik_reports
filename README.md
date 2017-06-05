# Custom PIWIK reports for CLARIN Dspace

A python application to periodically retrieve the PIWIK counts and store them locally in lucene index for generation of quick custom dspace statistics reports.

## Requirments
### PyLucene (http://lucene.apache.org/pylucene/)
Follow the installation instruction on the apache website. JCC is also required for PyLucene.

### Gunicorn
To run the python application as a webservice.

## Setup
Clone the git project.
```
git clone https://github.com/ufal/custom_piwik_reports.git [PATH]
```

open the [PATH]/scripts/search_application.py and change the value of the index variable to the folder where indexes will be created.
```
index = [INDEXES_PATH]
```

Create an init.d startup script to run application and bind with a unix socket. Use the following settings.

```
#!/bin/sh
### BEGIN INIT INFO
# Provides:          statistics
# Required-Start:
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: statistics
# Description:       statistics
### END INIT INFO


DAEMON_PATH="[PATH]/scripts/"

DAEMON=gunicorn
DAEMONOPTS="--log-level=debug --timeout 90 --workers 3 --bind unix:statistics.sock --user www-data --group devs --umask 007 wsgi"

NAME=statistics
DESC="Gunicorn statistics server for local piwik statistics"
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME
LOG_DIR=/var/log/statistics
mkdir -p $LOG_DIR
stdout_log="$LOG_DIR/$NAME.log"
stderr_log="$LOG_DIR/$NAME.err"
```
We can now use the service command to start/stop the statistics gunicorn server.
```
sudo service statistics start
```

Create a proxy in nginx.

```
location /statistics {
        rewrite /statistics(.+) /$1 break;
        include proxy_params;
        proxy_pass http://unix:[PATH]/scripts/statistics.sock;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
}
```
Restart nginx and the service is now accessible https://localhost/statistics/

## Initializing the reports
To retrive all the data from PIWIK server use the following command:
```
sudo make SCRIPT_PATH=[PATH]/scripts/generate_piwik_reports.py INDEX=[INDEXES_PATH]
              AUTH_TOKEN=[PIWIK_AUTH_TOKEN] START_DATE=YYYY-MM-DD END_DATE=YYY-MM-DD all
```

Create a cron job to periodically retrive the statistics. Set the START and END DATE occordingly.

## API

### /statistics/
The default route will return the timestamp of last run of the cron job.

### /statistics/views
Return the yearly page views of all services.
```
Generated using the Actions.get PIWIK command.
returns nb_pageviews and nb_uniq_pageviews
```

### /statistics/visits
Return the yearly visits of all services.
```
Generated using the VisitsSummary.get PIWIK command.
returns nb_visits and nb_uniq_visitors
```
Please note that nb_uniq_visitors metric for years is not enable by default in PIWIK.

### /statistics/country
Return the yearly countrywise visits.
```
Generated using the UserCountry.getCountry PIWIK command.
returns nb_visits and nb_uniq_visitors with two letter country code.
```

### /statistics/urls
Return the yearly hits by specific urls.
```
Generated using the Actions.getPageUrls PIWIK command.
returns nb_hits and nb_visits with label of the page.
```
nb_hits is equivalent to nb_pageviews

### /statistics/handle?h=[handle]
Return the views for specific handle.


## API Params
All the above routes can be customized using following url parameters.

### period 
year, month or day

### date
YYYY[-MM][-DD]

month and day is optional.

### segment
Segment can have the following values:

repository, downloads, lrt, lrt-downloads, others, services

for /handle the segment can be views or downloads

Not providing segment will return the overall counts combining all.


### Example
#### Return monthly visits for repository
```
/statistics/visits?segment=repository&period=month
```


## Integration in Joomla

Use the joomla.html file to create an article with piwik_charts.js javascript.

jqplot is required to generate the charts.
