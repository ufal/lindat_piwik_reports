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
