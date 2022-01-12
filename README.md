# Custom PIWIK reports for CLARIN Dspace

A python application to periodically retrieve the PIWIK counts and store them locally in lucene index for generation of quick custom dspace statistics reports.

## Requirements
access to piwik mysql database


## Setup
Clone the git project.
```
git clone --recurse-submodules https://github.com/ufal/custom_piwik_reports.git [PATH]
```

install python requirements
```
pip install -r new_importer/requirements.txt

```

create `new_importer/config.py`:
```
db_config = {
    'host': 'localhost',
    'user': 'reports',
    'password': '',
    'database': 'piwik_db'
}

output_dir = '/tmp/new_reports/'
```

`output_dir` should be set according to `nginx.conf`

see the `nginx/conf/nginx.conf` or run
```
docker run -v "$(pwd)"/nginx/conf/nginx.conf:/etc/nginx/nginx.conf:ro -v "$(pwd)"/nginx/var/www:/var/www -d -p 8080:80 --name lindat_stats nginx
```
Which expect the output_dir to be `nginx/var/www/statistics/`


## Initializing the reports
To retrive all the data from PIWIK server use the following command:
```
python new_importer/generate_reports.py
```

Create a cron job to periodically retrive the statistics. *currently no update* implemented; full import takes aprox 20 min.

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

### TBD /statistics/handle?h=[handle]
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

Add the dependencies mentioned in https://github.com/ufal/piwik-charts#how-to-use (js, css) and also:
```html
<link href="js/lib/jquery-jvectormap-2.0.3.css" rel="stylesheet" type="text/css" />
<script src="js/lib/jquery-jvectormap-2.0.3.min.js" type="text/javascript"></script>
<script src="js/lib/jquery-jvectormap-world-mill.js" type="text/javascript"></script>
<script src="piwik-charts/lib/jqplot/plugins/jqplot.categoryAxisRenderer.min.js" type="text/javascript"> </script>
<script src="piwik-charts/lib/jqplot/plugins/jqplot.pointLabels.min.js" type="text/javascript"> </script>
```
