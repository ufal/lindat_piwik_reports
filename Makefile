AUTH_TOKEN=[Add Piwik autorization token here]
PIWIK_URL=http://ufal.mff.cuni.cz/piwik/index.php
START_DATE=$(shell date -d 'yesterday' +'%Y-%m-%d')
END_DATE=$(shell date +'%Y-%m-%d')
SCRIPT:=/opt/custom_piwik_reports/scripts/generate_piwik_reports2.py --url=$(PIWIK_URL) --authToken=$(AUTH_TOKEN)

generate_over_all_reports:
	#overall views for all LINDAT pages + downloads
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2,4 --columns=nb_pageviews,nb_uniq_pageviews \
		--method=Actions.get 
	#overall visits / visitors
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2,4 --columns=nb_uniq_visitors,nb_visits \
		--method=VisitsSummary.get
	#overall views country wise
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2,4 --columns=code,nb_uniq_visitors,nb_visits \
		--method=UserCountry.getCountry
	#overall most visited pages
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2,4 --columns=label,url,nb_visits,nb_hits \
		--flat=1 \
		--method=Actions.getPageUrls


generate_repository_reports:
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository" \
		--method=Actions.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository" \
		--method=VisitsSummary.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=code,nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository" \
		--method=UserCountry.getCountry
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=label,url,nb_visits,nb_hits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository/xmlui/handle" \
		--method=Actions.getPageUrls
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=nb_pageviews,nb_uniq_pageviews \
		--method=Actions.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=nb_uniq_visitors,nb_visits \
		--method=VisitsSummary.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=code,nb_uniq_visitors,nb_visits \
		--method=UserCountry.getCountry
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=label,url,nb_visits,nb_hits \
		--flat=1 --expanded=1 \
		--method=Actions.getPageUrls

generate_LRT_reports:
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=Actions.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=VisitsSummary.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=code,nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=UserCountry.getCountry
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=label,url,nb_visits,nb_hits \
		--flat=1 \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository/xmlui/handle;pageUrl=@/LRT-" \
		--method=Actions.getPageUrls
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=Actions.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=VisitsSummary.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=code,nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=UserCountry.getCountry
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=4 --columns=label,url,nb_visits,nb_hits \
		--flat=1 --expanded=1 \
		--segment="pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-" \
		--method=Actions.getPageUrls


generate_services_reports:
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl=@lindat.mff.cuni.cz/services" \
		--method=Actions.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/services" \
		--method=VisitsSummary.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=code,nb_uniq_visitors,nb_visits \
		--segment="pageUrl=@lindat.mff.cuni.cz/services" \
		--method=UserCountry.getCountry
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=label,url,nb_visits,nb_hits \
		--flat=1 \
		--segment="pageUrl=@lindat.mff.cuni.cz/services" \
		--method=Actions.getPageUrls


generate_others_reports:
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_pageviews,nb_uniq_pageviews \
		--segment="pageUrl!@lindat.mff.cuni.cz" \
		--method=Actions.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=nb_uniq_visitors,nb_visits \
		--segment="pageUrl!@lindat.mff.cuni.cz" \
		--method=VisitsSummary.get
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=code,nb_uniq_visitors,nb_visits \
		--segment="pageUrl!@lindat.mff.cuni.cz" \
		--method=UserCountry.getCountry
	$(SCRIPT) --date=$(START_DATE),$(END_DATE) --period=day \
		--idSite=2 --columns=label,url,nb_visits,nb_hits \
		--flat=1 \
		--segment="pageUrl!@lindat.mff.cuni.cz" \
		--method=Actions.getPageUrls


all: generate_over_all_reports generate_repository_reports generate_LRT_reports generate_services_reports generate_others_reports
	date > $(REPORTS_DIR)/last_updated.txt
