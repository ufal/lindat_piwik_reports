# The ROLLUP creates (sub)totals based on the grouping columns; these will have NULL in that column; eg. if year,
# month, day and idsite are NULL this is the grand total across all ymd and sites
# The queries can be filtered to only return the (sub)totals using:
# HAVING
# (v.idsite AND day AND month AND year) IS NULL;
# (AND returns null if any of the operands is null)
# ; but that doesn't seem to be faster than without the filtering
hits_visits_aggregated = """
SELECT count(*) as hits, count( DISTINCT idvisit, idaction) as visits, idsite, YEAR(server_time) as year, 
MONTH(server_time) as month, DAY(server_time) as day
    FROM piwik_log_link_visit_action v
        LEFT JOIN piwik_log_action ON piwik_log_action.idaction = v.idaction_url
            WHERE type = 1 AND server_time >= '2014-01-01' {}
                        GROUP BY year, month, day, idsite WITH ROLLUP;
"""


# should use idvisitor from piwik_log_visits
# Need to join actions to be able to select based on url; the join with log_visits seems redundant; but for some
# reason there are many (at the time of writing almost twice as many) idvisitor in log_link_visit_action that are not
# in log_visit
visits_visitors = """
SELECT count(DISTINCT v.idvisit) as visits, count( DISTINCT v.idvisitor) as visitors,
 v.idsite, YEAR(server_time) as year, MONTH(server_time) as month, DAY(server_time) as day
    FROM piwik_log_visit v
    LEFT JOIN piwik_log_link_visit_action ON v.idvisit = piwik_log_link_visit_action.idvisit
    LEFT JOIN piwik_log_action ON piwik_log_action.idaction = piwik_log_link_visit_action.idaction_url
            WHERE server_time >= '2014-01-01' {}
                        GROUP BY year, month, day, v.idsite WITH ROLLUP;
"""

# Not sure we actually need the visitors here
visits_countries = """
SELECT location_country, count(distinct v.idvisit) as visits, count( DISTINCT v.idvisitor) as visitors,  
 v.idsite, YEAR(server_time) as year, MONTH(server_time) as month, DAY(server_time) as day
    FROM piwik_log_visit v
    LEFT JOIN piwik_log_link_visit_action ON v.idvisit = piwik_log_link_visit_action.idvisit
    LEFT JOIN piwik_log_action ON piwik_log_action.idaction = piwik_log_link_visit_action.idaction_url
            WHERE server_time >= '2014-01-01' {}
                        GROUP BY location_country, year, month, day, v.idsite WITH ROLLUP
                        HAVING location_country IS NOT NULL AND
                        (v.idsite AND day AND month AND year) IS NULL
                        ;
"""

# Note: for this to work you must alias the correct table with idsite as "v"
segment2where = {
    'overall': 'AND v.idsite IN (2,4) ',
    'downloads': 'AND v.idsite = 4',
    'repository': """
        AND v.idsite = 2 AND name like 'lindat.mff.cuni.cz/repository%'
    """,
    'others': """
        AND v.idsite = 2 AND name not like 'lindat.mff.cuni.cz%'
    """,
    'services': """
        AND v.idsite = 2 AND name like 'lindat.mff.cuni.cz/services%'
    """,
    'lrt': """
        AND v.idsite = 2 AND name like 'lindat.mff.cuni.cz/repository%LRT%'
    """
}

statements = {
    'views': hits_visits_aggregated,
    'visits': visits_visitors,
    'country': visits_countries
}