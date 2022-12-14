var incidentApp = angular.module('incidentApp', ["ngRoute"
//  ,"angular-jquery-locationpicker",
//  "ui.bootstrap.datetimepicker"
    , 'daterangepicker'
    , 'ngMap'
    , "chart.js"
]);

//http://creative-punch.net/2014/04/preserve-html-text-output-angularjs/
//Allow popup content to show HTML tags/divs...
incidentApp.filter('unsafe', function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
});


//https://stackoverflow.com/questions/41211875/angularjs-1-6-0-latest-now-routes-not-working
incidentApp.config(['$locationProvider', '$httpProvider', function($locationProvider,$httpProvider) {
    $locationProvider.hashPrefix('');
    //$httpProvider.defaults.xsrfCookieName = 'csrftoken';
    //$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

}]);



// incidentApp.run(['$http', '$cookies', function($http, $cookies) {
//   $http.defaults.headers.post['X-CSRFToken'] = "QpdYvCe8068SmOXMvRGkZpKnN9z8mA2CaHzcHxMPAHB35O3ah6tJM0yCvYKz3Zqc";
// }]);

// incidentApp.run(run);

// run.$inject = ['$http'];

// *
// * @name run
// * @desc Update xsrf $http headers to align with Django's defaults

// function run($http) {
//   $http.defaults.xsrfHeaderName = 'X-CSRFToken';
//   $http.defaults.xsrfCookieName = 'csrftoken';
// }

function incidentService($http) {


  this.get = function(url) {
    return $http.get(url)
    .then(function(res) {
      // return the enveloped data
      //console.log(res.data);
      return res.data;
    })
  }


  this.post = function(url, data) {

    return $http({
      url: '/incident/api/',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: data
    }).then( function successCallback(res){
      return {response: res.data};
    }, function errorCallback(res){
      return {error: res.data};
    })
  }
};

// incidentApp.run( function run( incidentService, $http, $cookies ){
//     //titleService.setSuffix( '[title]' );

//     // For CSRF token compatibility with Django
//     $http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
// })


function IncidentCtrl(incidentService, $scope, $filter, $window, $routeParams, NgMap) {

  initializeOrderDirection = function() {
     $scope.isAscendingOrder = false;
     // $scope.orderIcon = "glyphicon glyphicon-arrow-down";
     $scope.orderIcon = "glyphicon glyphicon-sort-by-attributes-alt";

     //console.log("initializing order");
     //console.log($scope.orderIcon);
  }

  //var self = this;

  $scope.incidentTypes = [];
  $scope.tags_facet = []
  $scope.incident = {};
  $scope.incidents = [];
  $scope.pages = {};
  $scope.orderType ="";
  $scope.showStats = false;
  $scope.showHideStatsText = "Show Stats";
  $scope.showSearch = false;

  if(typeof($routeParams.tags) == "undefined"){
    $scope.selectedTag = "";
  }else{
    $scope.selectedTag = {"id": $routeParams.tags};
  }

  if(typeof($routeParams.type) != "undefined"){
    $scope.typeSelected = {"id": $routeParams.type};
  }

  //console.log("Selected Type: " + JSON.stringify($scope.typeSelected));

  $scope.prevOrderType="";
  $scope.orderIcon ="";
  $scope.isAscendingOrder = false;
  initializeOrderDirection();
  $scope.incidentCount = 0;
  $scope.woundedCount = 0;
  $scope.deathsCount= 0;
  $scope.missingCount= 0;
  $scope.statsInfo = [];

  $scope.orderByList = ['date', 'deaths', 'wounded', 'missing'];

  $scope.datePicker = { 'date': {startDate: null, endDate: null} };


  var self = this;
  $scope.applyDateRange = function(ev, picker) {
    /*console.log('date range applied');
    console.log(ev);
    console.log(picker);
    console.log("daterange: " + JSON.stringify($scope.datePicker));*/

    var filters = self.buildFilters();
    //console.log("filters"); console.log(filters);
    clusterer.filter(filters);

    incidentsQuery();
    clusterer.cluster(false);

  }


  $scope.applyIncidentType = function() {

    if($scope.typeSelected && $scope.incidentTypes.indexOf($scope.typeSelected)!=-1){
        var filters = self.buildFilters();
        //console.log("filters"); console.log(filters);
        clusterer.filter(filters);
    }

    incidentsQuery();
    clusterer.cluster(false);

  }

  $scope.showSearchBox = function() {
    $scope.showSearch = true;
  }

  $scope.closeSearchBox = function() {
    $scope.showSearch = false;
    $scope.searchInput = "";
    $scope.applySearch();
  }

  $scope.applySearch = function() {

    console.log("Query text: " + $scope.searchInput);
    var filters = self.buildFilters();
    clusterer.filter(filters);
    incidentsQuery();
    clusterer.cluster(false);
  }

  //https://embed.plnkr.co/plunk/tswjcE
  $scope.toggleStats = function() {

    $scope.showStats = $scope.showStats? false: true;

    $scope.showHideStatsText = $scope.showStats? "Hide Stats": "Show Stats";

    // console.log("show stats: " + $scope.showStats);
      return $scope.showStats;
  }


  /*
  * Choose 'tag' filter
  */
  var self = this;
  $scope.filterByTag = function( selectedTag ) {

    if($scope.selectedTag.id === selectedTag.id){

        return $scope.deselectTag();

    }

    $scope.selectedTag = selectedTag;

    if( !selectedTag ){
        return;
    }

    var filters = self.buildFilters();
    clusterer.filter(filters);
    incidentsQuery();
    clusterer.cluster(false);

  }

  /**
  **/
  $scope.tagClassOption = function( tag ){
    if($scope.selectedTag.id == tag.id){
        return "tag-selected";
    }else{
        return "tag-default";
    }
  }

  /*

  */
  var self = this;
  $scope.deselectTag = function() {
    $scope.selectedTag = "";
    var filters = self.buildFilters();
    clusterer.filter(filters);
    incidentsQuery();
    clusterer.cluster(false);
  }

  $scope.updateStats = function(){

      $scope.statsColors = ['#000000',
                        '#ff84af', '#ff6300', '#006384', //'#336384',
                        '#ff84af', '#ff6300', '#006384', //'#336384',
                        '#ff84af', '#ff6300', '#006384', //'#336384'
       ]

      $scope.statsLabels = [];

      $scope.statsData = [[], [],[],[], [],[],[], [], [],[]];

      stats = $scope.statsInfo;

      //console.log(stats);

        for (let ii=0; ii<stats.length;ii++){
            $scope.statsLabels[ii] = make_label([stats[ii]["year"], stats[ii]["month"], stats[ii]["day"]]);
            $scope.statsData[0][ii] = stats[ii]["incident_count"];
            $scope.statsData[1][ii] = stats[ii]["deaths"];
            $scope.statsData[2][ii] = stats[ii]["wounded"];
            $scope.statsData[3][ii] = stats[ii]["missing"];

            $scope.statsData[4][ii] = stats[ii]["deaths_security_forces"];
            $scope.statsData[5][ii] = stats[ii]["wounded_security_forces"];
            $scope.statsData[6][ii] = stats[ii]["missing_security_forces"];

            $scope.statsData[7][ii] = stats[ii]["deaths_perpetrator"];
            $scope.statsData[8][ii] = stats[ii]["wounded_perpetrator"];
            $scope.statsData[9][ii] = stats[ii]["missing_perpetrator"];
        }

//        console.log($scope.statsData);
//        console.log($scope.statsLabels);

        $scope.statsSeries = ['incident count','deaths', 'wounded', 'missing',
        'deaths security forces', 'wounded security forces', 'missing security forces',
        'deaths assailants', 'wounded assailants', 'missing assailants'
        ];

        $scope.statsOptions = {
//            scales: {
//              xAxes: [{
//                  stacked: true
//              }],
//              yAxes: [{
//                  stacked: true
//              }]
//            },
            size: {
                height: 300
            },
            title: {
                      display: true,
                      text: 'Incident Statistics'
                    },
            legend: {
                    display: true,
                    position: 'bottom',

//                    labels: {
//                        fontColor: 'rgb(255, 99, 132)'
//                    }
                }

         };

         $scope.statsOverride = [
            {}, {}, {}, {},
            {borderDash: [1, 2]},{borderDash: [1, 2]},{borderDash: [1, 2]},
            {borderDash: [5, 15]},{borderDash: [5, 15]},{borderDash: [5, 15]}
         ]

     }




  /*
    Create filter array for modified AnyCluster query
    TODO Anycluster and tagging not working any longer
  */
  this.buildFilters = function() {

    var filters = [];

    if($scope.typeSelected){

        filters.push({'type_id':{"values": String($scope.typeSelected.id) , "operator":"="}});

    }

    startdate = $scope.datePicker.date.startDate;
    if(startdate){
        filters.push({'date':{"values": dateToString(startdate) , "operator":">="}});
    }
    enddate = $scope.datePicker.date.endDate;
    if(enddate){
        filters.push({'date':{"values": dateToString(enddate) , "operator":"<="}});
    }

    if( typeof($scope.selectedTag.id) != "undefined"){
        //tag_ids = get_tags_string($scope.selectedTag)
        filters.push({'tag_ids' :{"values": String($scope.selectedTag.id), "operator": "contains"}});
    }

    return filters;
  }

  function get_tags_string(tag){

    tags_string = ""

    if( typeof(tag.name) == "undefined" && typeof(tag.name_fr) == "undefined"){

        // doesn't work just at beginning/initialization
        for(ii=0; ii<length(tags_facet); ii++){

            if( tag.id == tags_facet[ii].id){
                tag = tags_facet[ii];
                break;
            }

        }

    }

    if(tag.name)
            tags_string += tag.name + ","
    if(tag.name_fr)
        tags_string += tag.name_fr

    return tags_string
  }

  $scope.orderTypeChanged = function() {

    console.log('order type change, current type');
    console.log($scope.prevOrderType);

    if( $scope.orderType == $scope.prevOrderType ){
        return;
    }
    console.log('new type');
    console.log($scope.orderType);

    $scope.prevOrderType = $scope.orderType;

    initializeOrderDirection();

    //TODO no aggregation should be done
    //Change name and break function
    incidentsQuery();
  }

  $scope.orderDirectionChanged = function() {

    invertOrderDirection();
    incidentsQuery();

  }

  getQueryUrl = function() {

    queryUrl = '';

    startdate = $scope.datePicker.date.startDate;
    if(startdate){
        queryUrl += "startdate="+dateToString(startdate);
    }
    enddate = $scope.datePicker.date.endDate;
    if(enddate){
        queryUrl += "&enddate=" + dateToString(enddate);
    }

    if($scope.orderType){
        queryUrl += "&orderby=" + $scope.orderType;
        if($scope.isAscendingOrder){
            queryUrl += "&order=ascending";
        }else{
            queryUrl += "&order=descending";
        }
    }

    if($scope.selectedTag){
        queryUrl += "&tags=" + $scope.selectedTag.id;
    }

    //console.log($scope.typeSelected);

    if($scope.typeSelected ){
        queryUrl += "&type="+ String($scope.typeSelected.id);
    }

    if($scope.searchInput){
        queryUrl += "&q=" + $scope.searchInput;
    }

    console.log(queryUrl);

    return queryUrl;
  }

  invertOrderDirection = function() {

    $scope.isAscendingOrder = !$scope.isAscendingOrder;

    if( $scope.isAscendingOrder ){
        //$scope.orderIcon = "glyphicon glyphicon-arrow-up";
        $scope.orderIcon = "glyphicon glyphicon-sort-by-attributes";
    }else{
        //$scope.orderIcon = "glyphicon glyphicon-arrow-down";
        $scope.orderIcon = "glyphicon glyphicon-sort-by-attributes-alt";
    }

    //console.log("inverting order");
    //console.log($scope.isAscendingOrder);

  }

  dateToString  = function (someDate) {
    //return String(someDate).split("T")[0];
    //return $filter('date', someDate, 'yyyy-MM-dd');
    return someDate.format('YYYY-MM-DD');
  }

  /*incidentService.get('/incident/api/')
    .then(function(incidents) {

      $scope.incidents = incidents.results;
      $scope.incidentCount = incidents.count;
      $scope.pages = incidents;
      $scope.pages.results = undefined;
      console.log($scope.incidents);
      console.log($scope.pages);

  });

  incidentService.get("/incident/aggregate")
    .then(function(result) {
      //$scope.incidentCount = result.count;
      $scope.woundedCount = result.wounded__sum;
      $scope.deathsCount= result.deaths__sum;
      $scope.missingCount= result.missing__sum;
    });*/

  incidentsQuery = function() {

    queryUrl = getQueryUrl();

    url = '/incident/api?' + queryUrl;
    //console.log('url: ' + url);

    incidentService.get(url)
    .then(function(incidents) {

      $scope.incidents = incidents.results;
      $scope.incidentCount = incidents.count;
      $scope.pages = incidents;
      $scope.pages.results = undefined;
      //console.log($scope.incidents);
      //console.log($scope.pages);
    });

    url = '/incident/aggregate?' + queryUrl;
    //console.log('url: ' + url);
    incidentService.get(url)
    .then(function(result) {
      $scope.woundedCount = result.wounded__sum;
      $scope.deathsCount= result.deaths__sum;
      $scope.missingCount= result.missing__sum;
    });

    url = '/incident/tags_facet?' + queryUrl;
    //console.log('url: ' + url);
    incidentService.get(url)
    .then(function(result) {
      $scope.tags_facet = result;
      //console.log(JSON.stringify($scope.tags_facet));
    })

    url = '/incident/stats?' + queryUrl;
    //console.log('url: ' + url);
    incidentService.get(url)
    .then(function(result) {
    console.log("inside incidentService: " + result);
      $scope.statsInfo = result;
      $scope.updateStats();
    });
/*    .then(function() {
        clusterer.removeAllMarkers();
    })*/

  }

  incidentsQuery();

  incidentService.get('/incident/api/type/')
    .then(function(types){
      //$scope.incidentTypes = [{"name": "All"}].concat(types.results);
      //[].push.apply($scope.incidentType.types, {"name": "All"});
      $scope.incidentTypes = types.results;
    });

  $scope.gotoPage = function(pageUrl){
    //console.log("daterange: " + JSON.stringify($scope.datePicker));
    //console.log(typeof($scope.datePicker.date.startDate));

    // Currently due to nginx proxy, django is returning 'localhost'
    var url = new URL(pageUrl);

    incidentService.get(url.pathname + url.search)
    .then(function(incidents) {

      $scope.incidents = incidents.results;
      $scope.pages = incidents;
      $scope.pages.results = undefined;
      //console.log($scope.incidents);
      //console.log($scope.pages);

      // scroll to page top
      //console.log("anchor scrolling");
      $window.scrollTo(0, angular.element('#incident-filter').offsetTop);

    });
  }


  $scope.submit = function() {

    var data = $scope.incident;
    data.date = $filter('date')(data.date, 'yyyy-MM-dd');

    //console.log("submit function()");
    //console.log(data);

    incidentService.post('/incident/api/', data)
      .then( function (res_data) {

          $scope.response = res_data.response;
          $scope.error = res_data.error;

          if('response' in res_data){
            $scope.incident = {};
          }

          //console.log($scope.response);
          //console.log($scope.error);

      });
    };


/* AnyCluster addition*/


    var clusterer = this;

    clusterer.finalMarkerHtmlContent = "regard social";

    //very risky scoping
    $scope.clusterer = this;

    clusterer.anyclusterSettings = {
      mapType : "google", // "google" or "osm"
      //zoom: 6,
      //center: [6.9182, 13.8516],
      gridSize: 768, //integer
      //gridSize: 512, //integer
      //zoom: 5, //initial zoom
      //autostart: true,
      //center: [49,11], //initial center in lng lat
      MapTypeId: "TERRAIN", //google only - choose from  ROADMAP,SATELLITE,HYBRID or TERRAIN
      //clusterMethod : "kmeans", //"grid" or "kmeans" or "centroid"
      clusterMethod : "kmeans", //"grid" or "kmeans" or "centroid"
      iconType: "exact", //"exact" (with exact cluster counts) or "simple" (with rounded counts)
      singlePinImages: {
        'imperial':'/static/anycluster/pin_imperial.png', //optional, use in conjunction with django settings: 'ANYCLUSTER_PINCOLUMN'
        'stone':'/static/anycluster/pin_stone.png',
        'wild':'/static/anycluster/pin_wild.png',
        'japanese':'/static/anycluster/pin_japan.png',
        'flower':'/static/anycluster/pin_flower.png'
      },
      onFinalClick : function(entries){
        $scope.popupContent = entries;
        $scope.$apply();
      }

    }

    this.startClustering = function(){
        var firstLoad = true;

        // To remove temptation
        //clusterer.cluster(false);
/*        if( typeof($scope.selectedTag["id"]) != "undefined" )
    {*/
        var filters = this.buildFilters();
        clusterer.filter(filters);
  /*  }*/

        google.maps.event.addListener(clusterer.gmap, 'idle', function() {

//            if (firstLoad === true){
//                firstLoad = false;
//                clusterer.cluster(true);
//            }
//            else {
//                clusterer.cluster(false);
//            }

           clusterer.cluster(false);
        });


        google.maps.event.addListener(clusterer.gmap, 'zoom_changed', function() {
             clusterer.removeAllMarkers();
        });
    }

    this.initializeMap = function() {

        NgMap.getMap().then(function(map) {

            clusterer.gmap = map;
            clusterer.startClustering();

        });
    }

    this.loadSettings = function(settings_) {

		this.baseURL = settings_.baseURL || "/anycluster/"
		this.autostart = typeof(settings_.autostart) == "boolean" ? settings_.autostart : true;
		this.filters = settings_.filters || [];
		this.center = settings_.center || [0,0];
		this.clusterMethod = settings_.clusterMethod || "grid";
		this.iconType = settings_.iconType || "exact";
		this.gridSize = settings_.gridSize || 256;
		this.mapType = settings_.mapType;
		this.mapTypeId = settings_.mapTypeId || "HYBRID";
		this.zoom = settings_.zoom || 3;
		this.singlePinImages = settings_.singlePinImages ? settings_.singlePinImages : {};
		this.onFinalClick = settings_.onFinalClick || this.onFinalClick;
		this.loadEnd = settings_.loadEnd || this.loadEnd;
		this.loadStart = settings_.loadStart || this.loadStart;
		this.clusterArea = settings_.clusterArea || false;

	}

	this.viewportMarkerCount = 0;
	this.markerList = [];
	this.clearMarkers = false;

	this.setMap = function(lng,lat){

        var zoom = clusterer.gmap.getZoom();
        zoom = zoom + 3;
        clusterer.zoom = zoom;
        var center = new google.maps.LatLng(lat,lng);
        clusterer.gmap.setCenter(center, zoom);
        clusterer.gmap.setZoom(zoom);

    }

	this.drawMarker = function(cluster){

        var center = new google.maps.LatLng(cluster['center']['y'], cluster['center']['x']);
        var count = cluster['count'];
        var pinimg = cluster['pinimg'];
        var ids = cluster["ids"];
        var type = cluster["type"];

        var piniconObj = clusterer.selectPinIcon(count, pinimg, type);

        var pinicon = piniconObj.url;

        /*var marker = new google.maps.Marker({
            position: center,
            latitude: center.lat(),
            longitude: center.lng(),
            map: clusterer.gmap,
            count: count,
            icon: pinicon,
            geojson: cluster.geojson,
            ids: ids
        });*/

        var marker = {
            position: center,
            latitude: center.lat(),
            longitude: center.lng(),
            //map: clusterer.gmap,
            count: count,
            icon: piniconObj,
            geojson: cluster.geojson,
            ids: ids
        };

        //console.log(marker);

        clusterer.markerList.push(marker);

    }

	this.drawMarkerExactCount = function(cluster){

        var center = new google.maps.LatLng(cluster['center']['y'], cluster['center']['x']);
        var count = cluster['count'];
        var pinimg = cluster['pinimg'];
        var ids = cluster["ids"];

        var piniconObj = clusterer.selectPinIcon(count,pinimg);

        var marker = {
            position: center,
            latitude: center.lat(),
            longitude: center.lng(),
            //map: clusterer.gmap,
            count: count,
            icon: piniconObj,
            geojson: cluster.geojson,
            ids: ids
        };

        clusterer.markerList.push(marker);

    }

    this.drawCell = function(cluster,i){

        var geojson = {
            "type": "Feature",
            "count": cluster.count,
            "geometry": JSON.parse(cluster.geojson),
            "properties": {"count": cluster.count}
        }

        clusterer.gmap.data.addGeoJson(geojson);

    }

    this.onClick = function(event, marker){

        if (clusterer.zoom >= 13 || marker.count <= 3) {

            clusterer.markerFinalClickFunction(marker);

            id = String(marker.latitude) + "" + String(marker.longitude);
            clusterer.gmap.showInfoWindow('popup', id);
        }
        else {
            clusterer.markerClickFunction(marker);
        }
    }

    this.paintGridColors = function(){

        var setColorStyleFn = function(feature) {

            var count = feature.getProperty('count');
            var rounded_count = roundMarkerCount(count);

            return {
                  fillColor: gridColorValues[rounded_count],
                  strokeWeight: 0
            }

        }

        clusterer.gmap.data.setStyle(setColorStyleFn);

    }

    this.getZoom = function(){
        return clusterer.gmap.getZoom();
    }

    this.cluster = function(cache, clusteredCB){

        if (clusterer.clusterArea == false){
            var viewport_json = this.getViewport();
            var geoJson = this.viewportToGeoJson(viewport_json);
            var geometry_type = "viewport";
        }
        else {
            var geoJson = clusterer.clusterArea;
            var geometry_type = "strict";
        }
        clusterer.getClusters(geoJson, geometry_type, clusteredCB, cache);

    }

    this.getViewport = function(){
        var viewport = clusterer.gmap.getBounds();
        var viewport_json = {'left':viewport.getSouthWest().lng(), 'top':viewport.getNorthEast().lat(), 'right':viewport.getNorthEast().lng(), 'bottom':viewport.getSouthWest().lat()};
        return viewport_json
    }


    //on small markers or on final zoom, this function is launched
	this.markerFinalClickFunction = function(mapmarker) {

		if (this.clusterMethod == "kmeans") {
			this.getClusterContent(mapmarker, this.onFinalClick);
		}
		else if (this.clusterMethod = "grid"){
			var geojson = { type: "Feature",
				geometry: JSON.parse(mapmarker["geojson"])
			};
			this.getAreaContent(geojson, this.onFinalClick);
		}
	}

	this.markerClickFunction = function(marker) {

		this.removeAllMarkers();
		this.setMap(marker.longitude, marker.latitude);

	}

	this.filter = function(filterObj){
		this.filters = filterObj;
		this.clearMarkers = true;
		this.cluster();
	}

	this.addFilters = function(newfilters){

		for (var f=0; f<newfilters.length; f++){

			this.filters.push(newfilters[f]);
		}

		this.clearMarkers = true;

	},

	this.removeFilters = function(activefilters){

		for (i=0; i<= activefilters.length; i++){

			delete this.filters[ activefilters[i] ];
		}

		this.clearMarkers = true;

	},

	this.removeAllMarkers = function(){

        // http://www.jstips.co/en/javascript/two-ways-to-empty-an-array/
		this.markerList.length = 0;
		$scope.$apply();

	}

	this.getClusters = function(geoJson, geometry_type, gotClusters, cache){

	    // console.log("geoJson");console.log(geoJson);
        // console.log("geometry_type");console.log(geometry_type)
        // console.log("gotClusters");console.log(gotClusters)

		this.zoom = this.getZoom();

		var clusterer = this;

		// console.log("In getClusters var clusterer = ");
		// console.log(clusterer);

		// console.log("$scope.clusterer");
		// console.log($scope.clusterer);

		this.loadStart();

		var url = this.baseURL + this.clusterMethod + '/' + this.zoom + '/' + this.gridSize + '/'; // + urlParams;

		postParams = {
			'geojson' : geoJson,
			'filters': this.filters,
			'geometry_type': geometry_type
		}

		/*if (cache === true){
			postParams['cache'] = 'load';
		}*/

		//send the ajax request
		url = encodeURI(url);
		var xhr = new XMLHttpRequest();

		xhr.onreadystatechange = function(){
			if (xhr.readyState==4 && xhr.status==200) {


				if (clusterer.clearMarkers == true){
					clusterer.markerList.length = 0;
					clusterer.clearMarkers = false;
				}

				var clusters = JSON.parse(xhr.responseText);

				//route the clusters
				if (clusterer.clusterMethod == 'grid'){
					var clusterFunction = clusterer.drawCell;
				}
				else if (clusterer.clusterMethod == 'kmeans'){
					if (clusterer.iconType == "simple"){
						var clusterFunction = clusterer.drawMarker;
					}
					else {
						var clusterFunction = clusterer.drawMarkerExactCount;
					}
				}

				if (clusters.length > 0 && geometry_type == "strict"){

					clusterer.removeAllMarkers();
				}

                // console.log("clusters retrieved:");
                // console.log(clusters);

                // console.log("$scope.clusterer");
		        // console.log($scope.clusterer);

				for(i=0; i<clusters.length; i++) {

					var cluster = clusters[i];


					if ( cluster.count == 1) {
						clusterer.drawMarker(cluster);
					}
					else {
					    // console.log("Drawing cluster: ");
					    // console.log(cluster);
						clusterFunction(cluster);
					}

				}

				if (clusterer.clusterMethod == 'grid'){
					clusterer.paintGridColors();
				}

				//update totalcount
				clusterer.viewportMarkerCount = clusterer.getViewportMarkerCount();

				clusterer.loadEnd();

				if (typeof clusteredCB === "function") {
					gotClusters();
				}

			}
		}
		xhr.open("POST", url, true);

		var csrftoken = getCookieValue('csrftoken');
    	xhr.setRequestHeader("X-CSRFToken", csrftoken);

		xhr.send(JSON.stringify(postParams));

	},

	this.getClusterContent = function(cluster, gotClusterContent){

		var postParams = {
			"x": cluster.longitude,
			"y": cluster.latitude,
			"ids":cluster.ids,
			"filters": this.filters
		}


		var url = encodeURI(this.baseURL + 'getClusterContent/' + this.zoom + '/' + this.gridSize + '/');

		var xhr = new XMLHttpRequest();

		xhr.onreadystatechange = function(){
			if (xhr.readyState==4 && xhr.status==200) {
				gotClusterContent(xhr.responseText);
			}
		}


		xhr.open("POST",url,true);

		var csrftoken = getCookieValue('csrftoken');
    		xhr.setRequestHeader("X-CSRFToken", csrftoken);

		xhr.send(JSON.stringify(postParams));

	},

	this.getViewportContent = function(gotViewportContent){
		var viewport_json = this.getViewport();
		var geoJson = this.viewportToGeoJson(viewport_json);

		this.getAreaContent(geoJson, gotViewportContent);

	},

	this.getAreaContent = function(geoJson, gotAreaContent){

		this.zoom = this.getZoom();

		var postParams = {
			"geojson":geoJson,
			"filters":this.filters
		}


		var url = this.baseURL + "getAreaContent/" + this.zoom + '/' + this.gridSize + '/'

		url = encodeURI(url);
		var xhr = new XMLHttpRequest();

		xhr.onreadystatechange = function(){
			if (xhr.readyState==4 && xhr.status==200) {

				gotAreaContent(xhr.responseText);

			}
		}
		xhr.open("POST",url,true);

		var csrftoken = getCookieValue('csrftoken');
    		xhr.setRequestHeader("X-CSRFToken", csrftoken);

		xhr.send(JSON.stringify(postParams));

	},

	this.viewportToGeoJson = function(viewport){

		//check if the viewport spans the edges of coordinate system

		if (viewport["left"] > viewport["right"]) {
			var geomtype = "MultiPolygon";
			var coordinates = [ [
					[ viewport["left"], viewport["top"] ],
					[ 179, viewport["top"] ],
					[ 179, viewport["bottom"] ],
					[ viewport["left"], viewport["bottom"] ],
					[ viewport["left"], viewport["top"] ]
			],
			[
					[ -179, viewport["top"] ],
					[ viewport["right"], viewport["top"] ],
					[ viewport["right"], viewport["bottom"] ],
					[ -179, viewport["bottom"] ],
					[ -179, viewport["top"] ]
			]];
		}
		else {
			var geomtype = "Polygon";
			var coordinates = [ [
				[ viewport["left"], viewport["top"] ],
				[ viewport["right"], viewport["top"] ],
				[ viewport["right"], viewport["bottom"] ],
				[ viewport["left"], viewport["bottom"] ],
				[ viewport["left"], viewport["top"] ]
			]];
		}

		var geoJson = {
			"type": "Feature",
			"geometry": {
				"type": geomtype,
				"coordinates": coordinates
			}
		}

		return geoJson

	},

	this.selectPinIcon = function(count, pinimg, type) {

		if (count == 1) {

			var singlePinURL = "/static/anycluster/images/pin_unknown.png";

			/*if( typeof(this.singlePinImages) == "function"){
				singlePinURL = this.singlePinImages(pinimg);
			}
			else {

				if (this.singlePinImages.hasOwnProperty(pinimg)){
					singlePinURL = this.singlePinImages[pinimg];
				}
			}*/
		    if( type ) {
			    //console.log("type: " + type);
			    type = type.replace(" ", "_").toLowerCase();
			    singlePinURL = "/static/anycluster/images/pin_" + type + ".png"
			}

	    }

	    else if (count > 10000){
	        var pinicon = '10000';
	    }

	    else if (count > 1000) {
	        var pinicon = '1000';
	    }

	    else if (count > 100) {
	        var pinicon = '100';
	    }

	    else if (count > 50) {
	        var pinicon = '50';
	    }

	    else if (count > 10) {
	        var pinicon = '10';
	    }

	    else {
	        var pinicon = '5';
	    }

	    if (count == 1){
	    		var imgurl = singlePinURL;
	    		var pinicon = 1;
	    }
	    else {

			if (this.iconType == "exact"){
				var imgurl = "/static/anycluster/images/" + pinicon + "_empty.png";
			}
			else {
				var imgurl = "/static/anycluster/images/" + pinicon + ".png";
			}
	    }

        var size = markerImageSizes[pinicon];

	    var imgObj = {
	    	url : imgurl,
	    	size : size,
	    	anchor : [ size[0]/2, size[1]/2 ],
	    	label: count> 1? String(count):null
	    }

	    return imgObj;

	},

	urlizeObject = function(obj){
		var urlParams = "?";
		var first = true;
		for (var key in obj){

			if (first == true){
				first = false;
				urlParams = urlParams + key + "=" + obj[key];
			}
			else {
				urlParams = urlParams + "&" + key + "=" + obj[key];
			}
		}

		return urlParams

	},

	this.markerIsInRectangle = function(marker, rectangle){
		if (rectangle["right"] > marker.longitude && rectangle["left"] < marker.longitude && rectangle["top"] > marker.latitude && rectangle["bottom"] < marker.latitude) {
			return true;
		}
		else {
			return false;
		}
	},

	this.getViewportMarkerCount = function(){
		var viewport = this.getViewport();
		var totalCount = 0;
		for (var i=0; i<this.markerList.length; i++){
			var marker = this.markerList[i];
			if (viewport["left"] > viewport["right"]) {

				var viewport_part1 = {"left": viewport["left"], "top": viewport["top"], "right": 180, "bottom": viewport["bottom"]},
					viewport_part2 = {"left": -180, "top": viewport["top"], "right": viewport["right"], "bottom": viewport["bottom"]};

				if ( this.markerIsInRectangle(marker, viewport_part1) || this.markerIsInRectangle(marker, viewport_part2) ){
					totalCount += marker.count;
				}
			}
			else {
				if ( this.markerIsInRectangle(marker, viewport) ){
					totalCount += marker.count;
				}
			}
		}
		return totalCount
	},

	this.loadStart = function(){}
	this.loadEnd = function(){

	    $scope.$apply();

	}

    // TODO: Settings loading could be done by mere initialization
    this.loadSettings(clusterer.anyclusterSettings);
    this.initializeMap();

/* End of AnyCluster stuff*/

//    incidentService.get('/incident/api/type')
//    .then(function(types) {
//
//      $scope.incidentTypes = types.results;
//      console.log($scope.incidentTypes);
//
//    })


    //(function(){this.init()})();
//    $scope.locationpickerOptions = {
//      location: {
//          latitude: 3.8480,
//          longitude: 11.5021
//      },
//      inputBinding: {
//          latitudeInput: $('#us3-lat'),
//          longitudeInput: $('#us3-lon'),
//          radiusInput: $('#us3-radius'),
//          //locationNameInput: $('#us3-address')
//          locationNameInput: $('#id_address')
//      },
//      radius: 0,
//      enableAutocomplete: true
//    };
}



incidentApp
  .controller('IncidentController', IncidentCtrl)
  .service('incidentService', incidentService);


incidentApp.config(function($routeProvider) {
    $routeProvider
    .when("/", {
        templateUrl : "/static/shared/incident.html",
        controller: "IncidentController"
    })
//   .when("/add", {
//       templateUrl : "/static/shared/add_incident.html",
//       controller : "IncidentController"
//   })
   .otherwise({
      //console.log(JSON.stringify(location));
      redirectTo: '/'
    });
});

function roundMarkerCount(count){

    if (count == 1){
        count = 1;
    }
    else if (count <= 5) {
        count = 5;
    }
    else if (count <= 10) {
        count = 10;
    }
    else if (count <= 50) {
        count = 50;
    }
    else if (count <= 100) {
        count = 100;
    }
    else if (count <= 1000) {
        count = 1000;
    }
    else {
        count = 10000
    }

    return count;
}

function make_label( info ){

    output = info[0];

    //https://stackoverflow.com/questions/8043026/how-to-format-numbers-by-prepending-0-to-single-digit-numbers
     for (ii=1; ii<info.length; ii++){
        if (info[ii]) {output += "-" + ("0" + info[ii]).slice(-2)}
     }
     return output;

}