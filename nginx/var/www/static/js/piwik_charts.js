var current_view  = "year";
var current_year  = null;
var current_month = null;
var current_day   = null;
var current_date = null;
var current_tab   = "#overall";
var loaded_data = {};
var already_loaded_dates = {};
//var base_url = "https://lindat.mff.cuni.cz/statistics/";
var base_url = "http://localhost:8080/";

var today     = new Date();
var today_str = today.getFullYear() + "-" + (today.getMonth()+1) + "-" + today.getDate();

var metrices = {
				"Page Views": "The number of times a page was visited.",
				"Unique Page Views": "If a page was viewed multiple times during one visit, it is only counted once.",
				"Downloads": "The number of times a downloadable link was clicked.",
				"Unique Downloads": "If a link was clicked multiple times during one visit, it is only counted once.",
				"Visits": "If a visitor comes to the website for the first time or if they visit a page more than 30 minutes after their last page view, this will be recorded as a new visit.",
				"Unique Visitors": "The number of unduplicated visitors coming to the website. Every user is only counted once, even if they visit the website multiple times a day."
			   };


jQuery(document).ready(function (){

	$.jqplot.config.enablePlugins = true;

    already_loaded_dates = {"overall":{}, "repository":{}, "downloads":{}, "lrt":{}, "lrt-downloads":{}, "services":{}, "others":{}};
    loaded_data = {"overall":{}, "repository":{}, "downloads":{}, "lrt":{}, "lrt-downloads":{}, "services":{}, "others":{}};

	$.when(
	    loadData("views",   null, "year", "overall"),
		$.get(base_url, function( data ) {
			$("#last_updated").html("<h6>Last Updated: " + data + "</h6>");
		})
	).then(function() {

		$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
			var current_tab = $(e.target).attr("href") // activated tab

            current_view = "year";
            current_month = null;
            current_year = null;
            current_date = null;

			showTab(current_tab);
		});

		showTab($(".active a[data-toggle='tab']").attr("href"));

		$("#current_span_btn").click(function (){
			if(current_view == "year") {
			} else if(current_view == "month") {
				current_view = "year";
				current_month = null;
				current_year = null;
				current_date = null;
			} else if(current_view == "day") {
				current_view = "month";
				current_date = current_year;
			}
			showTab($(".active a[data-toggle='tab']").attr("href"));
		});

	});

});


loadData = function(what, date, period, segment) {
    // XXX Bit of a hack to do this here; but it's a single place where it can be done
    // Only the "page views over time" are displayed day by day; the others are aggregates for the given month, it
    // should be enough to take one month from the json with month resolution (period)
    // For now this handles only the urls
    if(what === "urls" && period === "day"){
        period = "month";
        date = date.split("-")[0];
    }
    // /hack
    if(date != null) {
        params = "?date=" + date + "&period=" + period;
    } else {
        params = "?period=" + period;
    }
    if(segment!="overall"){
        params += "&segment=" + segment;
    }
    if(!(what in already_loaded_dates[segment])){
        already_loaded_dates[segment][what] = {};
        loaded_data[segment][what] = {};
    }
    if(!(period in already_loaded_dates[segment][what] && date in already_loaded_dates[segment][what][period])) {
        return $.getJSON(base_url + what + params, function(data) {
            loaded_data[segment][what] = $.extend(true, loaded_data[segment][what], data["response"]);
            if(!(period in already_loaded_dates[segment][what])) already_loaded_dates[segment][what][period] = {};
            if(!(date in already_loaded_dates[segment][what][period])) already_loaded_dates[segment][what][period][date] = true;
        });
	}
}


showTab = function(target) {

    $("#loading").css("display", "inline");

    if(current_view == "year") {
        var years = Object.keys(loaded_data["overall"]["views"]).sort().filter(function(e) { return e !== 'total' });
        $(".current_span").html(years[0] + " - " + years[years.length-1]);
        $("#current_span_btn").hide();
    } else if(current_view == "month") {
        $(".current_span").html(current_year);
        $("#current_span_btn").show();
    } else if(current_view == "day") {
        $(".current_span").html(monthNames[parseInt(current_month)] + ", " + current_year);
        $("#current_span_btn").show();
    }
    if(target == "#overall") {
        overallTab();
    } else if(target == "#repository") {
        repositoryTab();
    } else if(target == "#downloads") {
        downloadsTab();
    } else if(target == "#services") {
        servicesTab();
    } else if(target == "#others") {
        othersTab();
    } else if(target == "#lrt") {
        lrtTab();
    } else {
        $("#loading").css("display", "none");
    }
    $('[data-toggle="tooltip"]').tooltip({
        placement: 'auto',
        template : '<div class="tooltip"><div class="tooltip-inner"></div></div>'
    });
}

overallTab = function() {

	$.when(
	    loadData("views", current_date, current_view, "overall"),
        loadData("visits", current_date, current_view, "overall"),
        loadData("country", current_date, current_view, "overall"),
        loadData("urls", current_date, current_view, "overall"),
	    loadData("views", current_date, current_view, "repository"),
        loadData("views", current_date, current_view, "downloads"),
        loadData("visits", current_date, current_view, "downloads"),
        loadData("views", current_date, current_view, "services"),
        loadData("views", current_date, current_view, "others")
    ).then(function() {

        var overall_views = loaded_data["overall"]["views"];
        var total_views = overall_views["total"]["nb_pageviews"];
        var total_uniq_views= overall_views["total"]["nb_uniq_pageviews"];
        var overall_visits = loaded_data["overall"]["visits"];
        var overall_country = loaded_data["overall"]["country"]["total"];
        var overall_urls = loaded_data["overall"]["urls"]["total"];
        var overall_downloads = loaded_data["downloads"]["views"];
        var overall_downloads_visits = loaded_data["downloads"]["visits"];
        var tf  = "%Y";
        var ti  = "1 year";

        if($("#overall").length) {
            if(current_view == "month") {
                overall_views = loaded_data["overall"]["views"][current_year];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["overall"]["visits"][current_year];
                overall_country = loaded_data["overall"]["country"][current_year];
                overall_urls = loaded_data["overall"]["urls"][current_year];
                overall_downloads = loaded_data["downloads"]["views"][current_year];
                overall_downloads_visits = loaded_data["downloads"]["visits"][current_year];
                tf = "%b";
                ti = "1 month";
            }else
            if(current_view == "day") {
                overall_views = loaded_data["overall"]["views"][current_year][current_month];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["overall"]["visits"][current_year][current_month];
                overall_country = loaded_data["overall"]["country"][current_year][current_month];
                overall_urls = loaded_data["overall"]["urls"][current_year][current_month];
                overall_downloads = loaded_data["downloads"]["views"][current_year][current_month];
                overall_downloads_visits = loaded_data["downloads"]["visits"][current_year][current_month];
                tf = "%d";
                ti = "1 day";
            }
            plotViews("overall_views_chart", overall_views, "#004563", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
            showMetrics("overall_visits_count", overall_views, overall_visits, overall_downloads, overall_downloads_visits, false);
            plotDistribution("overall_distribution_chart");
            plotMap("overall_visits_map", overall_country, "#004563");
            showTopURLs("overall_accessed_url", overall_urls, total_views, total_uniq_views);

            $("#loading").css("display", "none");

        }
	});
}

repositoryTab = function() {

	$.when(
	    loadData("views", current_date, current_view, "repository"),
        loadData("visits", current_date, current_view, "repository"),
        loadData("country", current_date, current_view, "repository"),
        loadData("urls", current_date, current_view, "repository"),
    ).then(function() {

        var overall_views = loaded_data["repository"]["views"];
        var total_views = overall_views["total"]["nb_pageviews"];
        var total_uniq_views= overall_views["total"]["nb_uniq_pageviews"];
        var overall_visits = loaded_data["repository"]["visits"];
        var overall_country = loaded_data["repository"]["country"]["total"];
        var overall_urls = loaded_data["repository"]["urls"]["total"];
        var tf  = "%Y";
        var ti  = "1 year";


        if($("#repository").length) {

            if(current_view == "month") {
                overall_views = loaded_data["repository"]["views"][current_year];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["repository"]["visits"][current_year];
                overall_country = loaded_data["repository"]["country"][current_year];
                overall_urls = loaded_data["repository"]["urls"][current_year];
                tf = "%b";
                ti = "1 month";
            }else
            if(current_view == "day") {
                overall_views = loaded_data["repository"]["views"][current_year][current_month];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["repository"]["visits"][current_year][current_month];
                overall_country = loaded_data["repository"]["country"][current_year][current_month];
                overall_urls = loaded_data["repository"]["urls"][current_year][current_month];
                tf = "%d";
                ti = "1 day";
            }

            plotViews("repository_views_chart", overall_views, "#00749f", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
            showMetrics("repository_visits_count", overall_views, overall_visits, null, null);
            plotMap("repository_visits_map", overall_country, "#004563");
            showTopURLs("repository_accessed_url", overall_urls, total_views, total_uniq_views);

            $("#loading").css("display", "none");
        }
	});
}

lrtTab = function() {

	$.when(
	    loadData("views", current_date, current_view, "lrt"),
        loadData("visits", current_date, current_view, "lrt"),
        loadData("country", current_date, current_view, "lrt"),
        loadData("urls", current_date, current_view, "lrt"),
	    loadData("views", current_date, current_view, "lrt-downloads"),
        loadData("visits", current_date, current_view, "lrt-downloads"),
        loadData("country", current_date, current_view, "lrt-downloads"),
        loadData("urls", current_date, current_view, "lrt-downloads")
    ).then(function() {

        var overall_views = loaded_data["lrt"]["views"];
        var total_views = overall_views["total"]["nb_pageviews"];
        var total_uniq_views= overall_views["total"]["nb_uniq_pageviews"];
        var overall_visits = loaded_data["lrt"]["visits"];
        var overall_country = loaded_data["lrt"]["country"]["total"];
        var overall_urls = loaded_data["lrt"]["urls"]["total"];

        var download_views = loaded_data["lrt-downloads"]["views"];
        var total_downloads = download_views["total"]["nb_pageviews"];
        var total_uniq_downloads= download_views["total"]["nb_uniq_pageviews"];
        var download_visits = loaded_data["lrt-downloads"]["visits"];
        var download_country = loaded_data["lrt-downloads"]["country"]["total"];
        var download_urls = loaded_data["lrt-downloads"]["urls"]["total"];

        var tf  = "%Y";
        var ti  = "1 year";


        if($("#lrt").length) {

            if(current_view == "month") {
                overall_views = loaded_data["lrt"]["views"][current_year];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["lrt"]["visits"][current_year];
                overall_country = loaded_data["lrt"]["country"][current_year];
                overall_urls = loaded_data["lrt"]["urls"][current_year];

                download_views = loaded_data["lrt-downloads"]["views"][current_year];
                total_downloads = download_views["nb_pageviews"];
                total_uniq_downloads= download_views["nb_uniq_pageviews"];
                download_visits = loaded_data["lrt-downloads"]["visits"][current_year];
                download_country = loaded_data["lrt-downloads"]["country"][current_year];
                download_urls = loaded_data["lrt-downloads"]["urls"][current_year];

                tf = "%b";
                ti = "1 month";
            }else
            if(current_view == "day") {
                overall_views = loaded_data["lrt"]["views"][current_year][current_month];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["lrt"]["visits"][current_year][current_month];
                overall_country = loaded_data["lrt"]["country"][current_year][current_month];
                overall_urls = loaded_data["lrt"]["urls"][current_year][current_month];

                download_views = loaded_data["lrt-downloads"]["views"][current_year][current_month];
                total_downloads = download_views["nb_pageviews"];
                total_uniq_downloads= download_views["nb_uniq_pageviews"];
                download_visits = loaded_data["lrt-downloads"]["visits"][current_year][current_month];
                download_country = loaded_data["lrt-downloads"]["country"][current_year][current_month];
                download_urls = loaded_data["lrt-downloads"]["urls"][current_year][current_month];

                tf = "%d";
                ti = "1 day";
            }

            plotViews("lrt_views_chart", overall_views, "#7e35a5", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
            plotViews("lrt_downloads_chart", download_views, "#004563", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Downloads</div>");
            showMetrics("lrt_visits_count", overall_views, overall_visits, download_views, download_visits);
            plotMap("lrt_visits_map", overall_country, "#004563");
            showTopURLs("lrt_accessed_url", overall_urls, total_views, total_uniq_views);
            showTopURLs("lrt_download_url", download_urls, total_downloads, total_uniq_downloads);

            $("#loading").css("display", "none");
        }
	});

}

downloadsTab = function() {

	$.when(
	    loadData("views", current_date, current_view, "downloads"),
        loadData("visits", current_date, current_view, "downloads"),
        loadData("country", current_date, current_view, "downloads"),
        loadData("urls", current_date, current_view, "downloads"),
    ).then(function() {

        var overall_views = loaded_data["downloads"]["views"];
        var total_views = overall_views["total"]["nb_pageviews"];
        var total_uniq_views= overall_views["total"]["nb_uniq_pageviews"];
        var overall_visits = loaded_data["downloads"]["visits"];
        var overall_country = loaded_data["downloads"]["country"]["total"];
        var overall_urls = loaded_data["downloads"]["urls"]["total"];
        var tf  = "%Y";
        var ti  = "1 year";


        if($("#downloads").length) {

            if(current_view == "month") {
                overall_views = loaded_data["downloads"]["views"][current_year];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["downloads"]["visits"][current_year];
                overall_country = loaded_data["downloads"]["country"][current_year];
                overall_urls = loaded_data["downloads"]["urls"][current_year];
                tf = "%b";
                ti = "1 month";
            }else
            if(current_view == "day") {
                overall_views = loaded_data["downloads"]["views"][current_year][current_month];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["downloads"]["visits"][current_year][current_month];
                overall_country = loaded_data["downloads"]["country"][current_year][current_month];
                overall_urls = loaded_data["downloads"]["urls"][current_year][current_month];
                tf = "%d";
                ti = "1 day";
            }

            plotViews("downloads_chart", overall_views, "#73C774", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Downloads</div>");
            showMetrics("downloads_count", null, null, overall_views, overall_visits);
            plotMap("downloads_map", overall_country, "#004563");
            showTopURLs("downloads_url", overall_urls, total_views, total_uniq_views);

            $("#loading").css("display", "none");
        }
	});

}

servicesTab = function() {

	$.when(
	    loadData("views", current_date, current_view, "services"),
        loadData("visits", current_date, current_view, "services"),
        loadData("country", current_date, current_view, "services"),
        loadData("urls", current_date, current_view, "services"),
    ).then(function() {

        var overall_views = loaded_data["services"]["views"];
        var total_views = overall_views["total"]["nb_pageviews"];
        var total_uniq_views= overall_views["total"]["nb_uniq_pageviews"];
        var overall_visits = loaded_data["services"]["visits"];
        var overall_country = loaded_data["services"]["country"]["total"];
        var overall_urls = loaded_data["services"]["urls"]["total"];
        var tf  = "%Y";
        var ti  = "1 year";


        if($("#services").length) {

            if(current_view == "month") {
                overall_views = loaded_data["services"]["views"][current_year];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["services"]["visits"][current_year];
                overall_country = loaded_data["services"]["country"][current_year];
                overall_urls = loaded_data["services"]["urls"][current_year];
                tf = "%b";
                ti = "1 month";
            }else
            if(current_view == "day") {
                overall_views = loaded_data["services"]["views"][current_year][current_month];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["services"]["visits"][current_year][current_month];
                overall_country = loaded_data["services"]["country"][current_year][current_month];
                overall_urls = loaded_data["services"]["urls"][current_year][current_month];
                tf = "%d";
                ti = "1 day";
            }
            plotViews("services_views_chart", overall_views, "#C7754C", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
            showMetrics("services_visits_count", overall_views, overall_visits, null, null);
            plotMap("services_visits_map", overall_country, "#004563");
            showTopURLs("services_visits_urls", overall_urls, total_views, total_uniq_views);

            $("#loading").css("display", "none");

        }
	});

}

othersTab = function() {


	$.when(
	    loadData("views", current_date, current_view, "others"),
        loadData("visits", current_date, current_view, "others"),
        loadData("country", current_date, current_view, "others"),
        loadData("urls", current_date, current_view, "others"),
    ).then(function() {

        var overall_views = loaded_data["others"]["views"];
        var total_views = overall_views["total"]["nb_pageviews"];
        var total_uniq_views= overall_views["total"]["nb_uniq_pageviews"];
        var overall_visits = loaded_data["others"]["visits"];
        var overall_country = loaded_data["others"]["country"]["total"];
        var overall_urls = loaded_data["others"]["urls"]["total"];
        var tf  = "%Y";
        var ti  = "1 year";


        if($("#others").length) {

            if(current_view == "month") {
                overall_views = loaded_data["others"]["views"][current_year];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["others"]["visits"][current_year];
                overall_country = loaded_data["others"]["country"][current_year];
                overall_urls = loaded_data["others"]["urls"][current_year];
                tf = "%b";
                ti = "1 month";
            }else
            if(current_view == "day") {
                overall_views = loaded_data["others"]["views"][current_year][current_month];
                total_views = overall_views["nb_pageviews"];
                total_uniq_views= overall_views["nb_uniq_pageviews"];
                overall_visits = loaded_data["others"]["visits"][current_year][current_month];
                overall_country = loaded_data["others"]["country"][current_year][current_month];
                overall_urls = loaded_data["others"]["urls"][current_year][current_month];
                tf = "%d";
                ti = "1 day";
            }

            plotViews('others_views_chart', overall_views, "#17BDB8", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
            showMetrics("others_visits_count", overall_views, overall_visits, null, null);
            plotMap("others_visits_map", overall_country, "#004563");
            showTopURLs("others_visits_urls", overall_urls, total_views, total_uniq_views);

            $("#loading").css("display", "none");
        }
	});
}

plotDistribution = function (div) {

	$("#" + div).html("");

	var distribution = null;

	if(current_view=="year") {
		distribution =
			[
	 		    ['Repository', loaded_data["repository"]["views"]["total"]["nb_pageviews"]],
	 		    ['Downloads', loaded_data["downloads"]["views"]["total"]["nb_pageviews"]],
	 		    ['Services', loaded_data["services"]["views"]["total"]["nb_pageviews"]],
	 		    ['Others', loaded_data["others"]["views"]["total"]["nb_pageviews"]]
 		    ];
	} else if(current_view=="month"){
		distribution =
			[
	 		    ['Repository', loaded_data["repository"]["views"][current_year]["nb_pageviews"]],
	 		    ['Downloads', loaded_data["downloads"]["views"][current_year]["nb_pageviews"]],
	 		    ['Services', loaded_data["services"]["views"][current_year]["nb_pageviews"]],
	 		    ['Others', loaded_data["others"]["views"][current_year]["nb_pageviews"]]
 		    ];
	} else if(current_view=="day"){
		distribution =
			[
	 		    ['Repository', loaded_data["repository"]["views"][current_year][current_month]["nb_pageviews"]],
	 		    ['Downloads', loaded_data["downloads"]["views"][current_year][current_month]["nb_pageviews"]],
	 		    ['Services', loaded_data["services"]["views"][current_year][current_month]["nb_pageviews"]],
	 		    ['Others', loaded_data["others"]["views"][current_year][current_month]["nb_pageviews"]]
 		    ];
	}

	$.jqplot(div, [ distribution ], {


		seriesColors:['#00749F', '#73C774', '#C7754C', '#17BDB8'],

		seriesDefaults : {
			renderer : $.jqplot.BarRenderer,
			rendererOptions : {
				barWidth: "80" ,
				varyBarColor : true,
			}
	  	},

		axes : {
			xaxis : {
				renderer : $.jqplot.CategoryAxisRenderer,
			},
			yaxis : {
				tickOptions : {
					formatter : tickFormatter
				}
			}
		},

		highlighter: {
			show: false,
		},

		cursor: {
	        show: false,
		},

		grid: {
            backgroundColor: '#F8F8F8'
        }

	});
}

var monthNames = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

plotViews = function (div, data, color, tf, ti, highlightString) {

	var ticks = Object.keys(data)
	                .filter(function(e) { return e !== 'total' && !e.startsWith('nb') })
	                .sort(function(a,b){return parseInt(a)-parseInt(b)});
	var x = [];
	var y = [];
	var locations = {};
	for(index in ticks) {
		var tick = ticks[index];
		if(current_view == "month") {
			tick = current_year + "-" + tick.padStart(2, "0");
		} else
		if(current_view == "day") {
			tick = current_year + "-" + current_month.padStart(2, "0") + "-" + tick;
		}
		x.push(tick);
		var v = data[ticks[index]]["nb_pageviews"];
		y.push([tick, v?v:0]);
	}

	$("#" + div).html("");

	var xa = { 	renderer : $.jqplot.DateAxisRenderer,
				tickOptions : {formatString:tf},
				tickInterval : ti };

	if(current_view == "year") {
		xa["min"] = x[0];
		xa["max"] = x[x.length-1];
	} else if(current_view == "month") {
		xa["min"] = current_year + "-01";
		xa["max"] = current_year + "-12";
	} else if(current_view == "day") {
		xa["min"] = current_year + "-" + current_month + "-01";
		xa["max"] = current_year + "-" + current_month + "-" + new Date(current_year, current_month, 0).getDate();
	}

	$.jqplot(div, [ y ], {

	    seriesColors: [color],

		axes : {
			xaxis : xa,
			yaxis : {
				min : 0,
				tickOptions : {
					formatter : tickFormatter,
				}
			}
		},

		highlighter: {
			show: true,
		},

		cursor: {
	        show: false,
		},

		seriesDefaults: {
			highlighter: {formatString: highlightString},
			pointLabels: { show:false }
	  	},

	  	grid: {
            backgroundColor: '#F8F8F8',
        },

	});

	$('#' + div).unbind('jqplotDataClick');

	$('#' + div).bind('jqplotDataClick',
        function (ev, seriesIndex, pointIndex, d) {
            if(current_view == "year") {
            	current_view = "month";
            	current_year = ticks[pointIndex];
            	current_date = current_year;
            } else if(current_view == "month") {
            	current_view = "day";
            	current_month = ticks[pointIndex];
            	current_date = current_year + "-" + current_month;
            }
            var target = $("ul#statistics_tab li.active a").attr("href");
            showTab(target);
        }
	);
}


plotMap = function(div, data, color) {
	$('#' + div).html("");
	$('#' + div).css("display", "block");

	var total = 0;
	var cz = 0;
	var cz_per = 0;

	var locKeys = Object.keys(data);
	var locations = {};
	for(locInd in locKeys) {
		var loc = locKeys[locInd];
	    if(isNaN(data[loc]["nb_visits"])) continue;
		locations[loc.toUpperCase()] = data[loc]["nb_visits"]?data[loc]["nb_visits"]:0;
		total += data[loc]["nb_visits"];
	}
	cz = locations["CZ"];
	cz_per = cz / total * 100;
	cz_per = cz_per.toFixed(2);

	$('#' + div).vectorMap({
	  map: 'world_mill',
	  backgroundColor: '#F8F8F8',
	  series: {
	    regions: [{
	      values: locations,
	      scale: ["#FFFFFF", color],
	      normalizeFunction: 'polynomial',
	      legend: {
	          vertical: true,
	          labelRender: function(code){
	        	  return tickFormatter(null, code);
	          }
	      },
	    }]
	  },

	  onRegionTipShow: function(e, el, code){
		var v = locations[code]?locations[code]:0;
		var p = v / total * 100;
		p = p.toFixed(2);
	    el.html("<div style='font-size: 120%; padding: 5px;'>" + el.html() + '<br><strong>' + v + '</strong> visits<br>(' + p + '%)</div>');
	  }
	});

	$('#' + div + "_cz").html("<img src='media/mod_languages/images/cz.gif' /> Visits from Czech Republic" +
        " <strong>" + cz + " (" + cz_per +"%)</strong>");
	$('#' + div + "_cz").show();
}


showTopURLs = function(div, data, total_views, total_uniq_views) {
	$("#" + div + ">table thead").html("");
	$("#" + div + ">table tbody").html("");
	var i = 1;
    // v, uv are totals displayed above the urls
    var v = total_views;
    var uv = total_uniq_views;
	var v100 = 0;
	var uv100 = 0;
	sortedUrls = Object.keys(data)
						.sort(function(a,b){return data[b]["nb_hits"]-data[a]["nb_hits"]});
	$("#" + div + ">table thead").append("<tr><th class='col-md-8'>URL</th><th class='col-md-2 text-right'>Views</th><th class='col-md-2 text-right'>Unique Views</th>");
	for(urlInd in sortedUrls) {
		var url = sortedUrls[urlInd];
		if(isNaN(data[url]["nb_hits"])) continue;
		if(i<=100) {
			$("#" + div + ">table tbody").append("<tr>" +
					"<td class='col-md-8'><span class='pull-left'>" + i + ".</span>&nbsp;<span>" + url + "</span></td>" +
					"<td class='col-md-2 big-font text-right'><span class='top-urls-visits'>" + data[url]["nb_hits"] + "</span></td>" +
					"<td class='col-md-2 big-font text-right'><span class='top-urls-visitors'>" + data[url]["nb_visits"] + "</span></td>" +
							"</tr>");
			v100  += data[url]["nb_hits"];
			uv100 += data[url]["nb_visits"]
		}
		i++;
		//if(i==101) break;
	}
	$("#" + div + ">table tbody").prepend("<tr>" +
			"<td class='col-md-8'><strong>Total top 100</strong></td>" +
			"<td class='col-md-2 text-right big-font'><span class='top-urls-visits'>" + v100 + "</span></td>" +
			"<td class='col-md-2 text-right big-font'><span class='top-urls-visitors'>" + uv100 + "</span></td></tr>");
	$("#" + div + ">table tbody").prepend("<tr class='warning'>" +
			"<td class='col-md-8'><strong>Total</strong></td>" +
			"<td class='col-md-2 text-right big-font'>" + v + "</td>" +
			"<td class='col-md-2 text-right big-font'>" + uv + "</td></tr>");
	$("#" + div + "_count").html("(showing top 100)")

	$(".top-urls-visits").each(function (){
		var val = $(this).text();
		var per = (val/v*100).toFixed(2);
		$(this).tooltip({
			title:  per + '%',
			placement: 'left',
			template : '<div class="tooltip" style="padding: 5px;"><div class="tooltip-inner"></div></div>'
		});
	});

	$(".top-urls-visitors").each(function (){
		var val = $(this).text();
		var per = (val/uv*100).toFixed(2);
		$(this).tooltip({
			title:  per + '%',
			placement: 'left',
			template : '<div class="tooltip" style="padding: 5px;"><div class="tooltip-inner"></div></div>'
		});
	});


	$("#" + div).css("display", "block");
}

showMetrics = function(div, views, visits, downloads, downloads_visits, combine_visits) {

	var total_visits = 0;
	var uniq_visitors = 0;
	$("#" +div+ ">table").html("");

	if(views!=null) {
	    var ov = null;
	    var ovc = null;
	    if(current_view == "year") {
		    ov = views["total"]; ovc = visits["total"];
		} else {
		    ov = views; ovc = visits;
		}

		total_visits = ovc["nb_visits"];
		uniq_visitors = ovc["nb_uniq_visitors"];

		$("#" + div+ ">table").append("<tr><td><abbr data-toggle='tooltip' title='" + metrices["Page Views"] + "'>Page Views</abbr></td><td class='big-font'>" + ov["nb_pageviews"]  + "</td><td><abbr data-toggle='tooltip' title='" + metrices["Unique Page Views"] + "'>Unique Page Views</abbr></td><td class='big-font'>" + ov["nb_uniq_pageviews"] + "</td></tr>");
	}

	if(downloads!=null) {
	    var od = null;
	    var odc = null;
	    if(current_view == "year") {
		    od = downloads["total"]; odc = downloads_visits["total"];
		} else {
			od = downloads; odc = downloads_visits;
		    od = downloads; odc = downloads_visits;
		}

		if(combine_visits) {
			total_visits += odc["nb_visits"];
			uniq_visitors += odc["nb_uniq_visitors"];
		} else if(views==null) {
			total_visits = odc["nb_visits"];
			uniq_visitors = odc["nb_uniq_visitors"];
		}
		$("#" + div+ ">table").append("<tr><td><abbr data-toggle='tooltip' title='" + metrices["Downloads"] + "'>Downloads</abbr></td><td class='big-font'>" + od["nb_pageviews"]  + "</td><td><abbr data-toggle='tooltip' title='" + metrices["Unique Downloads"] + "'>Unique Downloads</abbr></td><td class='big-font'>" + od["nb_uniq_pageviews"] + "</td></tr>");
	}

	$("#" + div+ ">table").append("<tr><td><abbr data-toggle='tooltip' title='" + metrices["Visits"] + "'>Visits</abbr></td><td class='big-font'>" + total_visits  + "</td><td><abbr data-toggle='tooltip' title='" + metrices["Unique Visitors"] + "'>Unique Visitors</abbr></td><td class='big-font'>" + (uniq_visitors==0?"N/A":uniq_visitors) + "</td></tr>");
	$("#" + div).css("display", "block");
}


tickFormatter = function (format, val) {
    if (val >= 1000000) {
        val = val / 1000000;
    return val.toFixed(1)+"M";
    }
    if (val >= 1000) {
        val = val / 1000;
            if (val < 10) {
                return val.toFixed(1)+"K";
            }
        return val.toFixed(1)+"K";
    }
    return val;
}
