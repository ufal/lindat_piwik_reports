var current_view = "years";
var current_year = null;
var current_month = null;
var current_day = null;

var overall_views = null;
var overall_visits = null;
var overall_visits_countrywise = null;
var overall_accessed_urls = null;
var repository_views = null;
var repository_visits = null;
var repository_visits_countrywise = null;
var repository_accessed_urls = null;
var repository_downloads = null;
var repository_downloads_visits = null;
var repository_downloads_countrywise = null;
var overall_downloaded_urls = null;
var services_views = null;
var services_visits = null;
var services_visits_countrywise = null;
var services_accessed_urls = null;
var other_views = null;
var other_visits = null;
var other_visits_countrywise = null;
var other_accessed_urls = null;

var LRT_views = null;
var LRT_visits = null;
var LRT_visits_countrywise = null;
var LRT_accessed_urls = null;
var LRT_downloads = null;
var LRT_downloads_visits = null;
var LRT_downloads_countrywise = null;
var LRT_downloaded_urls = null;

var start_date = '2014-01-01';
var today = new Date();
var end_date = date.getFullYear() + '-' + date.getMonth() + '-' + date.getDate();

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
	
	$.when(
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/views", function( data ) {
			overall_views = data;
		}),

		$.getJSON("https://lindat.mff.cuni.cz/statistics/country", function( data ) {
			overall_visits_countrywise = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/urls", function( data ) {
			overall_accessed_urls = data;
		}),		

		$.getJSON("https://lindat.mff.cuni.cz/statistics/views?segment=repository", function( data ) {
			repository_views = data;
		}),

		$.getJSON("https://lindat.mff.cuni.cz/statistics/country?segment=repository", function( data ) {
			repository_visits_countrywise = data;
		}),		
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/urls?segment=repository", function( data ) {
			repository_accessed_urls = data;
		}),		

		$.getJSON("https://lindat.mff.cuni.cz/statistics/views?segment=downloads", function( data ) {
			repository_downloads = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/country?segment=downloads", function( data ) {
			repository_downloads_countrywise = data;
		}),	
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/urls?segment=downloads", function( data ) {
			overall_downloaded_urls = data;
		}),		
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/views?segment=services", function( data ) {
			services_views = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/country?segment=services", function( data ) {
			services_visits_countrywise = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/urls?segment=services", function( data ) {
			services_accessed_urls = data;
		}),				
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/views?segment=others", function( data ) {
			other_views = data;
		}),

		$.getJSON("https://lindat.mff.cuni.cz/statistics/country?segment=others", function( data ) {
			other_visits_countrywise = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/urls?segment=others", function( data ) {
			other_accessed_urls = data;
		}),						
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/views?segment=lrt", function( data ) {
			LRT_views = data;
		}),

		$.getJSON("https://lindat.mff.cuni.cz/statistics/country?segment=lrt", function( data ) {
			LRT_visits_countrywise = data;
		}),		
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/urls?segment=lrt", function( data ) {
			LRT_accessed_urls = data;
		}),		

		$.getJSON("https://lindat.mff.cuni.cz/statistics/views?segment=lrt-downloads", function( data ) {
			LRT_downloads = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/country?segment=lrt-downloads", function( data ) {
			LRT_downloads_countrywise = data;
		}),	
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/urls?segment=lrt-downloads", function( data ) {
			LRT_downloaded_urls = data;
		}),		
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/visits", function( data ) {
			overall_visits = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/visits?segment=repository", function( data ) {
			repository_visits = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/visits?segment=downloads", function( data ) {
			repository_downloads_visits = data;
		}),				

		$.getJSON("https://lindat.mff.cuni.cz/statistics/visits?segment=lrt", function( data ) {
			LRT_visits = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/visits?segment=lrt-downloads", function( data ) {
			LRT_downloads_visits = data;
		}),
		
		$.getJSON("https://lindat.mff.cuni.cz/statistics/visits?segment=services", function( data ) {
			services_visits = data;
		}),								

		$.getJSON("https://lindat.mff.cuni.cz/statistics/visits?segment=others", function( data ) {
			other_visits = data;
		}),								

		$.get("https://lindat.mff.cuni.cz/statistics/", function( data ) {
			$("#last_updated").html("<h6>Last Updated: " + data + "</h6>");
		})
				
	).then(function() {
		
		$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
			var target = $(e.target).attr("href") // activated tab
			showTab(target);
		});
		
		showTab($(".active a[data-toggle='tab']").attr("href"));
				
		$("#current_span_btn").click(function (){
			if(current_view == "years") {
			} else if(current_view == "year") {
				current_view = "years";
				current_year = null;
				current_month = null;			
			} else if(current_view == "month") {
				current_view = "year";
				current_month = null;
			}
			showTab($(".active a[data-toggle='tab']").attr("href"));
		});
				
	});
	
});


showTab = function(target) {	
		
	if(current_view == "years") {
		var years = Object.keys(overall_views["years"]).sort();
		$(".current_span").html(years[0] + " - " + years[years.length-1]);
		$("#current_span_btn").hide();
	} else if(current_view == "year") {
		$(".current_span").html(current_year);
		$("#current_span_btn").show();
	} else if(current_view == "month") {
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
	}	
	
	
	  $('[data-toggle="tooltip"]').tooltip({
		  placement: 'auto',
		  template : '<div class="tooltip"><div class="tooltip-inner"></div></div>'
	  });	
}

overallTab = function() {
	if($("#overall").length) {		
		var ov = overall_views["years"];
		var ovc = overall_visits_countrywise["total"];
		var ocu = overall_accessed_urls["total"];
		var tf = "%Y";
		var ti = "1 year";		
		if(current_view == "year") {
			ov = overall_views["years"][current_year]["months"];
			ovc = overall_visits_countrywise["years"][current_year];
			ocu = overall_accessed_urls["years"][current_year];
			tf = "%b";
			ti = "1 month";
		} else
		if(current_view == "month") {
			ov = overall_views["years"][current_year]["months"][current_month]["days"];
			ovc = overall_visits_countrywise["years"][current_year]["months"][current_month];
			ocu = overall_accessed_urls["years"][current_year]["months"][current_month];
			tf = "%d";
			ti = "1 day";
		}

		plotViews("overall_views_chart", ov, "#004563", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");			
		showMetrics("overall_visits_count", overall_views, overall_visits, repository_downloads, repository_downloads_visits, false);
		plotDistribution("overall_distribution_chart");		
		plotMap("overall_visits_map", ovc, "#004563");
		showTopURLs("overall_accessed_url", ocu);

	}	
}

repositoryTab = function() {
	if($("#repository").length) {
		
		var rv = repository_views["years"];
		var rvc = repository_visits_countrywise["total"];
		var rcu = repository_accessed_urls["total"];		
		var tf = "%Y";
		var ti = "1 year";

		if(current_view == "year") {
			rv = repository_views["years"][current_year]["months"];
			rvc = repository_visits_countrywise["years"][current_year];
			rcu = repository_accessed_urls["years"][current_year];			
			tf = "%b";
			ti = "1 month";			
		} else
		if(current_view == "month") {
			rv = repository_views["years"][current_year]["months"][current_month]["days"];
			rvc = repository_visits_countrywise["years"][current_year]["months"][current_month];
			rcu = repository_accessed_urls["years"][current_year]["months"][current_month];
			tf = "%d";
			ti = "1 day";			
		}		
		
		plotViews("repository_views_chart", rv, "#00749f", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
		showMetrics("repository_visits_count", repository_views, repository_visits, null, null);		
		plotMap("repository_visits_map", rvc, "#004563");
		showTopURLs("repository_accessed_url", rcu);
	}	
}

lrtTab = function() {
	if($("#lrt").length) {
		
		var rv = LRT_views["years"];
		var rd = LRT_downloads["years"];
		var rvc = LRT_visits_countrywise["total"];
		var rdc = LRT_downloads_countrywise["total"];
		var rcu = LRT_accessed_urls["total"];
		var rdu = LRT_downloaded_urls["total"];
		var tf = "%Y";
		var ti = "1 year";

		if(current_view == "year") {
			rv = LRT_views["years"][current_year]["months"];
			rvc = LRT_visits_countrywise["years"][current_year];
			rcu = LRT_accessed_urls["years"][current_year];
			rd = LRT_downloads["years"][current_year]["months"];
			rdc = LRT_downloads_countrywise["years"][current_year];
			rdu = LRT_downloaded_urls["years"][current_year];						
			tf = "%b";
			ti = "1 month";			
		} else
		if(current_view == "month") {
			rv = LRT_views["years"][current_year]["months"][current_month]["days"];
			rvc = LRT_visits_countrywise["years"][current_year]["months"][current_month];
			rcu = LRT_accessed_urls["years"][current_year]["months"][current_month];
			rd = LRT_downloads["years"][current_year]["months"][current_month]["days"];
			rdc = LRT_downloads_countrywise["years"][current_year]["months"][current_month];
			rdu = LRT_downloaded_urls["years"][current_year]["months"][current_month];									
			tf = "%d";
			ti = "1 day";			
		}		
		
		plotViews("lrt_views_chart", rv, "#7e35a5", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
		plotViews("lrt_downloads_chart", rd, "#004563", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Downloads</div>");
		showMetrics("lrt_visits_count", LRT_views, LRT_visits, LRT_downloads, LRT_downloads_visits);		
		plotMap("lrt_visits_map", rvc, "#004563");
		showTopURLs("lrt_accessed_url", rcu);
		showTopURLs("lrt_download_url", rdu, true);
	}	
}

downloadsTab = function() {
	if($("#downloads").length) {
		var rd = repository_downloads["years"];
		var rdc = repository_downloads_countrywise["total"];
		var odu = overall_downloaded_urls["total"];
		var tf = "%Y";
		var ti = "1 year";
		if(current_view == "year") {
			rd = repository_downloads["years"][current_year]["months"];
			rdc = repository_downloads_countrywise["years"][current_year];
			odu = overall_downloaded_urls["years"][current_year];
			tf = "%b";
			ti = "1 month";			
		} else
		if(current_view == "month") {
			rd = repository_downloads["years"][current_year]["months"][current_month]["days"];
			rdc = repository_downloads_countrywise["years"][current_year]["months"][current_month];
			odu = overall_downloaded_urls["years"][current_year]["months"][current_month];			
			tf = "%d";
			ti = "1 day";			
		}		
		plotViews("downloads_chart", rd, "#73C774", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Downloads</div>");
		showMetrics("downloads_count", null, null, repository_downloads, repository_downloads_visits);
		plotMap("downloads_map", rdc, "#004563");
		showTopURLs("downloads_url", odu, true);		
	}		
}

servicesTab = function() {
	if($("#services").length) {
		var sv = services_views["years"];
		var svc = services_visits_countrywise["total"];
		var sau = services_accessed_urls["total"];		
		var tf = "%Y";
		var ti = "1 year";
		if(current_view == "year") {
			sv = services_views["years"][current_year]["months"];
			svc = services_visits_countrywise["years"][current_year];
			sau = services_accessed_urls["years"][current_year];
			tf = "%b";
			ti = "1 month";			
		} else
		if(current_view == "month") {
			sv = services_views["years"][current_year]["months"][current_month]["days"];
			svc = services_visits_countrywise["years"][current_year]["months"][current_month];
			sau = services_accessed_urls["years"][current_year]["months"][current_month];
			tf = "%d";
			ti = "1 day";			
		}		
		plotViews("services_views_chart", sv, "#C7754C", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
		showMetrics("services_visits_count", services_views, services_visits, null, null);		
		plotMap("services_visits_map", svc, "#004563");
		showTopURLs("services_visits_urls", sau);		
	}			
}

othersTab = function() {
	if($("#others").length) {
		var ov = other_views["years"];
		var ovc = other_visits_countrywise["total"];
		var oau = other_accessed_urls["total"];
		var tf = "%Y";
		var ti = "1 year";
		if(current_view == "year") {
			ov = other_views["years"][current_year]["months"];
			ovc = other_visits_countrywise["years"][current_year];
			oau = other_accessed_urls["years"][current_year];
			tf = "%b";
			ti = "1 month";			
		} else
		if(current_view == "month") {
			ov = other_views["years"][current_year]["months"][current_month]["days"];
			ovc = other_visits_countrywise["years"][current_year]["months"][current_month];
			oau = other_accessed_urls["years"][current_year]["months"][current_month];
			tf = "%d";
			ti = "1 day";			
		}		
		plotViews('others_views_chart', ov, "#17BDB8", tf, ti, "<div style='font-size: 110%; padding: 5px; color: #FFFFFF;'>%s<BR/><strong style='font-size: 14px;'>%s</strong> Views</div>");
		showMetrics("others_visits_count", other_views, other_visits, null, null);
		plotMap("others_visits_map", ovc, "#004563");
		showTopURLs("others_visits_urls", oau);
	}			
}

plotDistribution = function (div) {
	
	$("#" + div).html("");
		
	var distribution = null;
	
	if(current_view=="years") {
		distribution = 
			[
	 		    ['Repository', repository_views["total"]["nb_pageviews"]],
	 		    ['Downloads', repository_downloads["total"]["nb_pageviews"]],
	 		    ['Services', services_views["total"]["nb_pageviews"]],
	 		    ['Others', other_views["total"]["nb_pageviews"]]
 		    ];		
	} else if(current_view=="year"){
		distribution = 
			[
	 		    ['Repository', repository_views["years"][current_year]["nb_pageviews"]],
	 		    ['Downloads', repository_downloads["years"][current_year]["nb_pageviews"]],
	 		    ['Services', services_views["years"][current_year]["nb_pageviews"]],
	 		    ['Others', other_views["years"][current_year]["nb_pageviews"]]
 		    ];			
	} else if(current_view=="month"){
		distribution = 
			[
	 		    ['Repository', repository_views["years"][current_year]["months"][current_month]["nb_pageviews"]],
	 		    ['Downloads', repository_downloads["years"][current_year]["months"][current_month]["nb_pageviews"]],
	 		    ['Services', services_views["years"][current_year]["months"][current_month]["nb_pageviews"]],
	 		    ['Others', other_views["years"][current_year]["months"][current_month]["nb_pageviews"]]
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
	
	var ticks = Object.keys(data).sort().filter(function(e) { return e !== 'months' && e !== 'days' });
	var x = [];
	var y = [];
	var locations = {};
	for(index in ticks) {
		var tick = ticks[index];
		if(current_view == "year") {
			tick = current_year + "-" + tick;
		} else
		if(current_view == "month") {
			tick = current_year + "-" + current_month + "-" + tick;
		}
		x.push(tick);
		var v = data[ticks[index]]["nb_pageviews"];
		y.push([tick, v?v:0]);
	}
	
	$("#" + div).html("");
	
	var xa = { 	renderer : $.jqplot.DateAxisRenderer,
				tickOptions : {formatString:tf},
				tickInterval : ti };
	
	if(current_view == "years") {
		xa["min"] = x[0];
		xa["max"] = x[x.length-1];
	} else if(current_view == "year") {
		xa["min"] = current_year + "-01";
		xa["max"] = current_year + "-12";		
	} else if(current_view == "month") {
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
            if(current_view == "years") {
            	current_view = "year";            	
            	current_year = ticks[pointIndex];
            } else if(current_view == "year") {
            	current_view = "month";
            	current_month = ticks[pointIndex];
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
	
	var locKeys = Object.keys(data).filter(function(e) { return e !== 'months' && e !== 'days' });
	var locations = {};
	for(locInd in locKeys) {
		var loc = locKeys[locInd];
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

	$('#' + div + "_cz").html("<img src='/media/mod_languages/images/cz.gif' /> Visits from Czech Republic <strong>" + cz + " (" + cz_per +"%)</strong>");
	$('#' + div + "_cz").show();
}


showTopURLs = function(div, data, bitstream) {
	$("#" + div + ">table thead").html("");
	$("#" + div + ">table tbody").html("");
	var i = 1;
	var v = 0;
	var uv = 0;
	var v100 = 0;
	var uv100 = 0;
	sortedUrls = Object.keys(data)
						.filter(function(e) { return e !== 'months' && e !== 'days' })
						.sort(function(a,b){return data[b]["nb_hits"]-data[a]["nb_hits"]});
	$("#" + div + ">table thead").append("<tr><th class='col-md-8'>URL</th><th class='col-md-2 text-right'>Views</th><th class='col-md-2 text-right'>Unique Views</th>");	
	for(urlInd in sortedUrls) {
		var url = sortedUrls[urlInd];
		if(i<=100) {
			var link = url;
			if("url" in data[url]) {
				link = data[url]["url"];
			} 
			if(link.startsWith("http")) {
				if(bitstream) {
					link = link.replace("/bitstream", "");
					link = link.substring(0, link.lastIndexOf('/'));
					link = "<a target='_blank' href='" + link + "'>" + url + "</a>";
				} else {
					link = "<a target='_blank' href='" + link + "'>" + url + "</a>";
				}
			}
			$("#" + div + ">table tbody").append("<tr>" +
					"<td class='col-md-8'><span class='pull-left'>" + i + ".</span>&nbsp;<span>" + link + "</span></td>" +
					"<td class='col-md-2 big-font text-right'><span class='top-urls-visits'>" + data[url]["nb_hits"] + "</span></td>" +
					"<td class='col-md-2 big-font text-right'><span class='top-urls-visitors'>" + data[url]["nb_visits"] + "</span></td>" +
							"</tr>");
			v100  += data[url]["nb_hits"];
			uv100 += data[url]["nb_visits"]			
		}
		i++;
		//if(i==101) break;
		v  += data[url]["nb_hits"];
		uv += data[url]["nb_visits"]
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
		var ov = views["total"];
		var ovc = visits["total"];
		
		if(current_view=="year") {
			ov = views["years"][current_year];
			ovc = visits["years"][current_year];
		} else if (current_view=="month") {
			ov = views["years"][current_year]["months"][current_month];
			ovc = visits["years"][current_year]["months"][current_month];
		}
		
		total_visits = ovc["nb_visits"];
		uniq_visitors = ovc["nb_uniq_visitors"];
		
		$("#" + div+ ">table").append("<tr><td><abbr data-toggle='tooltip' title='" + metrices["Page Views"] + "'>Page Views</abbr></td><td class='big-font'>" + ov["nb_pageviews"]  + "</td><td><abbr data-toggle='tooltip' title='" + metrices["Unique Page Views"] + "'>Unique Page Views</abbr></td><td class='big-font'>" + ov["nb_uniq_pageviews"] + "</td></tr>");		
	}
		
	if(downloads!=null) {
		var od = downloads["total"];	
		var odc = downloads_visits["total"];
		if(current_view=="year") {
			od = downloads["years"][current_year];		
			odc = downloads_visits["years"][current_year];
		} else if (current_view=="month") {
			od = downloads["years"][current_year]["months"][current_month];		
			odc = downloads_visits["years"][current_year]["months"][current_month];		
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
		
	$("#" + div+ ">table").append("<tr><td><abbr data-toggle='tooltip' title='" + metrices["Visits"] + "'>Visits</abbr></td><td class='big-font'>" + total_visits  + "</td><td><abbr data-toggle='tooltip' title='" + metrices["Unique Visitors"] + "'>Unique Visitors</abbr></td><td class='big-font'>" + uniq_visitors + "</td></tr>");	
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
