# The ROLLUP creates (sub)totals based on the grouping columns; these will have NULL in that column; eg. if year,
# month, day and idsite are NULL this is the grand total across all ymd and sites
# The queries can be filtered to only return the (sub)totals using:
# HAVING
# (v.idsite AND day AND month AND year) IS NULL;
# (AND returns null if any of the operands is null)
# ; but that doesn't seem to be faster than without the filtering
hits_visits_aggregated = """
SELECT count(*) as hits, count( DISTINCT idvisit, idaction) as uniq_pageviews, v.idsite, YEAR(server_time) as year, 
MONTH(server_time) as month, DAY(server_time) as day
    FROM piwik_log_link_visit_action v
    LEFT JOIN piwik_log_visit USING(idvisit)
        LEFT JOIN piwik_log_action ON piwik_log_action.idaction = v.idaction_url
            WHERE type = 1 AND server_time >= '2014-01-01' {}
                        GROUP BY year, month, day, v.idsite WITH ROLLUP;
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


##### URLs #####
# if you have a concrete url (idaction is fixed) uniq_pageviews should be the same thing as visits;
# ie. just distinct idvisit
# The piwik_charts actually calls these "Unique views", but looks for nb_visits. We are modifying the name (removing
# url params) so there might be multiple idaction involved.

# No window functions/partition by in mysql 5.5;
# so the inner most select grabs the data and orders them
# the next one numbers the rows for given year-month combination
# the outer most selects the top N rows for the year-month combination
top_urls_by_month = """
set @my_row_number = 0;
set @last_date = '';
SELECT hits, visits, year, month, name, my_row_number FROM (
SELECT hits, visits, year, month, name,
    @my_row_number:=CASE
        WHEN @last_date = concat(year, '-', month) then @my_row_number + 1
        ELSE 0
    END as my_row_number,
    @last_date:=concat(year, '-', month) FROM (
SELECT count(*) as hits, count( DISTINCT idvisit, idaction) as visits, YEAR(server_time) as year, MONTH(server_time) as month, substring_index(name, '?', 1) as name
    FROM piwik_log_link_visit_action v
    LEFT JOIN piwik_log_visit USING(idvisit)
    LEFT JOIN piwik_log_action ON piwik_log_action.idaction = v.idaction_url
    WHERE type = 1
    AND server_time >= '2014-01-01'
    {}
    GROUP BY year, month, substring_index(name, '?', 1)
    order by year, month, hits desc
 ) data ) data_numbered where my_row_number < 100;
"""

top_urls_by_year = """
set @my_row_number = 0;
set @last_date = '';
SELECT hits, visits, year, name, my_row_number FROM (
SELECT hits, visits, year, name,
    @my_row_number:=CASE
        WHEN @last_date = year then @my_row_number + 1
        ELSE 0
    END as my_row_number,
    @last_date:=year FROM (
SELECT count(*) as hits, count( DISTINCT idvisit, idaction) as visits, YEAR(server_time) as year, substring_index(name, '?', 1) as name
    FROM piwik_log_link_visit_action v
    LEFT JOIN piwik_log_visit USING(idvisit)
    LEFT JOIN piwik_log_action ON piwik_log_action.idaction = v.idaction_url
    WHERE type = 1
    AND server_time >= '2014-01-01'
    {}
    GROUP BY year, substring_index(name, '?', 1)
    order by year, hits desc
 ) data ) data_numbered where my_row_number < 100;
"""

top_urls_total = """
SELECT count(*) as hits, count( DISTINCT idvisit, idaction) as visits, substring_index(name, '?', 1) as name
    FROM piwik_log_link_visit_action v
    LEFT JOIN piwik_log_visit USING(idvisit)
    LEFT JOIN piwik_log_action ON piwik_log_action.idaction = v.idaction_url
    WHERE type = 1
    AND server_time >= '2014-01-01'
    {}
    GROUP BY substring_index(name, '?', 1)
    order by hits desc
    limit 100
"""

##### /URLs #####

##### handles - used by the repository not the summary /statistics #####
# see the URLs comment about visits and uniq pageviews, note that we are exposing both metrics and also visitors for
# pdf export

# not using rollup; can't get all the needed combinations without GROUPING SETS, the grouping is done in code with pandas
# visits may be higher due to javascript (see the # cleanup); handle is derived from the url there might be unsafe chars
# substring_index(hdl, '?', 1) ~ search for first '?' in hdl and return all to the left of it
# the query removes url params and the domain (ie. lindat.cz and lindat.mff.cuni.cz will be grouped together)
handles = """
select substring_index(substring_index(hdl, '?', 1), '#', 1) as handle, name, idvisit, idaction, concat(idvisit,'/',idaction) as visit_action, hex(idvisitor) as 
idvisitor, idsite, YEAR(server_time) as year, MONTH(server_time) as month, DAY(server_time) as day FROM (
SELECT if(substring(name, locate('handle', name) + 7) like '%/%/%',
            substring_index(substring(name, locate('handle', name) + 7), '/', 2),
            substring(name, locate('handle', name) + 7)) as hdl,
    substring_index(replace(name, 'lindat.cz', 'lindat.mff.cuni.cz'), '?', 1) as name, v.idvisit, idaction, v.idsite, v.idvisitor, server_time
    FROM piwik_log_visit v
    LEFT JOIN piwik_log_link_visit_action ON v.idvisit = piwik_log_link_visit_action.idvisit
    LEFT JOIN piwik_log_action ON piwik_log_action.idaction = piwik_log_link_visit_action.idaction_url
            WHERE type = 1 AND server_time >= '2014-01-01' {} 
    ) visits_actions
"""

handles_country = """
set @my_row_number=0;
set @last_group = '';
SELECT handle, location_country, visits, year, month, my_row_number FROM
(
SELECT handle, location_country, visits, year, month,     
    @my_row_number:=CASE
    WHEN @last_group = CONCAT(handle, '/', year, '-', month) THEN @my_row_number + 1
    ELSE 0
    END as my_row_number,
    @last_group:=CONCAT(handle, '/', year, '-', month) FROM
(
SELECT substring_index(substring_index(if(substring(name, locate('handle', name) + 7) like '%/%/%',
            substring_index(substring(name, locate('handle', name) + 7), '/', 2),
            substring(name, locate('handle', name) + 7)), '?', 1), '#', 1) as handle,
       location_country, count( DISTINCT v.idvisit) as visits, YEAR(server_time) as year, MONTH(server_time) as month
    FROM piwik_log_visit v
    LEFT JOIN piwik_log_link_visit_action ON v.idvisit = piwik_log_link_visit_action.idvisit
    LEFT JOIN piwik_log_action ON piwik_log_action.idaction = piwik_log_link_visit_action.idaction_url
            WHERE server_time >= '2014-01-01' and v.idsite=2 and name like 'lindat.%cz/repository/%handle/%/%'
                        GROUP BY handle, location_country, year, month
            ORDER BY handle, year, month, visits desc
) data ) data_numbered where my_row_number < 10                       
    ;
"""

##### /handles #####

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
    """,
    'lrt-downloads': """
        AND v.idsite = 4 AND name like 'lindat.mff.cuni.cz/repository%LRT%'
    """,
    'mff-repository-internal-views': """
        AND server_time >= '2023-01-01' AND v.idsite = 2 AND name like 'lindat.mff.cuni.cz/repository%' AND NOT name 
        like '%handle/20.500.12801%' AND {MFF_RANGE}
    """,
    'mff-repository-internal-downloads': """
        AND server_time >= '2023-01-01' AND v.idsite = 4 AND name like 'lindat.mff.cuni.cz/repository%' AND NOT name 
        like '%handle/20.500.12801%' AND {MFF_RANGE}
    """,
    'mff-repository-external-downloads': """
        AND server_time >= '2023-01-01' AND v.idsite = 4 AND name like 'lindat.mff.cuni.cz/repository%' AND NOT name 
        like '%handle/20.500.12801%' AND NOT {MFF_RANGE}
    """,
    'mff-repository-external-views': """
        AND server_time >= '2023-01-01' AND v.idsite = 2 AND name like 'lindat.mff.cuni.cz/repository%' AND NOT name 
        like '%handle/20.500.12801%' AND NOT {MFF_RANGE}
    """,
    'nfa-repository-internal-views': f"""
        AND server_time >= '2023-01-01' AND v.idsite = 2 AND name like 'lindat.mff.cuni.cz/repository%' AND name 
        like '%handle/20.500.12801%' AND {NFA_RANGE}
    """,
    'nfa-repository-internal-downloads': f"""
        AND server_time >= '2023-01-01' AND v.idsite = 4 AND name like 'lindat.mff.cuni.cz/repository%' AND name 
        like '%handle/20.500.12801%' AND {NFA_RANGE}
    """,
    'nfa-repository-external-downloads': f"""
        AND server_time >= '2023-01-01' AND v.idsite = 4 AND name like 'lindat.mff.cuni.cz/repository%' AND name 
        like '%handle/20.500.12801%' AND NOT {NFA_RANGE}
    """,
    'nfa-repository-external-views': f"""
        AND server_time >= '2023-01-01' AND v.idsite = 2 AND name like 'lindat.mff.cuni.cz/repository%' AND name 
        like '%handle/20.500.12801%' AND NOT {NFA_RANGE}
    """,
    'handle-views': """
        AND v.idsite=2 AND name like 'lindat.%cz/repository/%handle/%/%'
    """,
    'handle-downloads': """
        AND v.idsite=4
    """
}

statements = {
    'views': hits_visits_aggregated,
    'visits': visits_visitors,
    'country': visits_countries,
    'urls_total': top_urls_total,
    'urls_year': top_urls_by_year,
    'urls_month': top_urls_by_month,
    'handles': handles,
    'handles_country': handles_country
}

