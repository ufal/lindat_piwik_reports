AUTH_TOKEN=[Add Piwik autorization token here]
PIWIK_URL=http://ufal.mff.cuni.cz/piwik/index.php
REPORTS_DIR=reports
START_DATE=2014-01-01
END_DATE=$(shell date +'%Y-%m-%d')
SCRIPT:=scripts/generate_piwik_reports.py --url=$(PIWIK_URL) --authToken=$(AUTH_TOKEN)

generate_over_all_reports:
	#overall views for all LINDAT pages + downloads
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2,4 --columns=nb_pageviews,nb_uniq_pageviews \
		--countColumns=nb_pageviews,nb_uniq_pageviews \
		--method=Actions.get  > $(REPORTS_DIR)/overall_views.json
	#overall visits / visitors
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2,4 --columns=nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits \
		--method=VisitsSummary.get  > $(REPORTS_DIR)/overall_visits.json
	#overall views country wise
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2,4 --columns=code,nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits --groupBy=code \
		--method=UserCountry.getCountry  > $(REPORTS_DIR)/overall_visits_countrywise.json
	#overall most visited pages
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=month \
		--idSite=2,4 --columns=label,url,nb_visits,nb_hits \
		--countColumns=nb_visits,nb_hits --groupBy=label \
		--textColumns=url --flat=1 \
		--method=Actions.getPageUrls > $(REPORTS_DIR)/overall_accessed_urls.json


generate_repository_reports:
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_pageviews,nb_uniq_pageviews \
		--countColumns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository" \
		--method=Actions.get  > $(REPORTS_DIR)/repository_views.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository" \
		--method=VisitsSummary.get  > $(REPORTS_DIR)/repository_visits.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=code,nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits --groupBy=code \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository" \
		--method=UserCountry.getCountry > $(REPORTS_DIR)/repository_visits_countrywise.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=label,url,nb_visits,nb_hits \
		--countColumns=nb_visits,nb_hits --groupBy=label \
		--textColumns=url --flat=1 \
		--ignoreURLQueryStrings=1 \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository/xmlui/handle" \
		--method=Actions.getPageUrls > $(REPORTS_DIR)/repository_accessed_urls.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=nb_pageviews,nb_uniq_pageviews \
		--countColumns=nb_pageviews,nb_uniq_pageviews \
		--method=Actions.get  > $(REPORTS_DIR)/repository_downloads.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits \
		--method=VisitsSummary.get  > $(REPORTS_DIR)/repository_downloads_visits.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=code,nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits --groupBy=code \
		--method=UserCountry.getCountry > $(REPORTS_DIR)/repository_downloads_countrywise.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=label,url,nb_visits,nb_hits \
		--countColumns=nb_visits,nb_hits --groupBy=label \
		--textColumns=url --flat=1 \
		--expanded=1 --ignoreURLQueryStrings=1 \
		--method=Actions.getPageUrls > $(REPORTS_DIR)/overall_downloaded_urls.json

generate_LRT_reports:
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_pageviews,nb_uniq_pageviews \
		--countColumns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=Actions.get  > $(REPORTS_DIR)/LRT_views.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=VisitsSummary.get  > $(REPORTS_DIR)/LRT_visits.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=code,nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits --groupBy=code \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=UserCountry.getCountry > $(REPORTS_DIR)/LRT_visits_countrywise.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=label,url,nb_visits,nb_hits \
		--countColumns=nb_visits,nb_hits --groupBy=label \
		--textColumns=url --flat=1 \
		--ignoreURLQueryStrings=1 \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository/xmlui/handle;pageUrl=@/LRT-" \
		--method=Actions.getPageUrls > $(REPORTS_DIR)/LRT_accessed_urls.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=nb_pageviews,nb_uniq_pageviews \
		--countColumns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=Actions.get  > $(REPORTS_DIR)/LRT_downloads.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=VisitsSummary.get  > $(REPORTS_DIR)/LRT_download_visits.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=code,nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits --groupBy=code \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=UserCountry.getCountry > $(REPORTS_DIR)/LRT_downloads_countrywise.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=label,url,nb_visits,nb_hits \
		--countColumns=nb_visits,nb_hits --groupBy=label \
		--textColumns=url --flat=1 \
		--expanded=1 --ignoreURLQueryStrings=1 \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=Actions.getPageUrls > $(REPORTS_DIR)/LRT_downloaded_urls.json


generate_services_reports:
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_pageviews,nb_uniq_pageviews \
		--countColumns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl=@lindat.mff.cuni.cz/services" \
		--method=Actions.get  > $(REPORTS_DIR)/services_views.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/services" \
		--method=VisitsSummary.get  > $(REPORTS_DIR)/services_visits.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=code,nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits --groupBy=code \
		--segment="pageUrl=@lindat.mff.cuni.cz/services" \
		--method=UserCountry.getCountry > $(REPORTS_DIR)/services_visits_countrywise.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=label,url,nb_visits,nb_hits \
		--countColumns=nb_visits,nb_hits --groupBy=label \
		--textColumns=url --flat=1 \
		--ignoreURLQueryStrings=1 \
		--segment="pageUrl=@lindat.mff.cuni.cz/services" \
		--method=Actions.getPageUrls > $(REPORTS_DIR)/services_accessed_urls.json


generate_others_reports:
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_pageviews,nb_uniq_pageviews \
		--countColumns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl!@lindat.mff.cuni.cz" \
		--method=Actions.get  > $(REPORTS_DIR)/other_views.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl!@lindat.mff.cuni.cz" \
		--method=VisitsSummary.get  > $(REPORTS_DIR)/other_visits.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=code,nb_uniq_visitors,nb_visits \
		--countColumns=nb_uniq_visitors,nb_visits --groupBy=code \
		--segment="pageUrl!@lindat.mff.cuni.cz" \
		--method=UserCountry.getCountry > $(REPORTS_DIR)/other_visits_countrywise.json
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=label,url,nb_visits,nb_hits \
		--countColumns=nb_visits,nb_hits --groupBy=label \
		--textColumns=url --flat=1 \
		--ignoreURLQueryStrings=1 \
		--segment="pageUrl!@lindat.mff.cuni.cz" \
		--method=Actions.getPageUrls > $(REPORTS_DIR)/other_accessed_urls.json


all: generate_over_all_reports generate_repository_reports generate_LRT_reports generate_services_reports generate_others_reports
	date > $(REPORTS_DIR)/last_updated.txt
