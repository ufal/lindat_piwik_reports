hits_visits_aggregated = """
SELECT count(*) as hits, count( DISTINCT idvisit, idaction) as visits, idsite, YEAR(server_time) as year, 
MONTH(server_time) as month, DAY(server_time) as day
    FROM piwik_log_link_visit_action
        LEFT JOIN piwik_log_action ON piwik_log_action.idaction = piwik_log_link_visit_action.idaction_url
            WHERE type = 1 AND server_time >= '2014-01-01' {}
                        GROUP BY year, month, day, idsite WITH ROLLUP;
"""

segment2where = {
    'overall': 'AND idsite IN (2,4) ',
    'downloads': 'AND idsite = 4',
    'repository': """
        AND idsite = 2 AND name like 'lindat.mff.cuni.cz/repository%'
    """,
    'others': """
        AND idsite = 2 AND name not like 'lindat.mff.cuni.cz%'
    """,
    'services': """
        AND idsite = 2 AND name like 'lindat.mff.cuni.cz/services%'
    """,
    'lrt': """
        AND idsite = 2 AND name like 'lindat.mff.cuni.cz/repository%LRT%'
    """
}

