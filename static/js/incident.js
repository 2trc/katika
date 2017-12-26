var incidentApp = angular.module('incidentApp', ["ngRoute"
//  ,"angular-jquery-locationpicker",
//  "ui.bootstrap.datetimepicker"
    , 'daterangepicker'
]);

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


function IncidentCtrl(incidentService, $scope, $filter) {

  initializeOrderDirection = function() {
     $scope.isAscendingOrder = false;
     $scope.orderIcon = "glyphicon glyphicon-arrow-down";

     console.log("initializing order");
     console.log($scope.orderIcon);
  }

  var self = this;

  $scope.incidentTypes = [];
  $scope.incident = {};
  $scope.incidents = [];
  $scope.pages = {};
  $scope.orderType ="";
  $scope.prevOrderType="";
  $scope.orderIcon ="";
  $scope.isAscendingOrder = false;
  initializeOrderDirection();
  $scope.incidentCount = 0;
  $scope.woundedCount = 0;
  $scope.deathsCount= 0;

  $scope.orderByList = ['date', 'wounded', 'deaths'];

  $scope.datePicker = { 'date': {startDate: null, endDate: null} };

  /*ToDo function should be renamed
  it's called when many things change from date range,
  to filter or order by ...
  */
  $scope.applyDateRange = function(ev, picker) {
    console.log('date range applied');
    console.log(ev);
    console.log(picker);
    console.log("daterange: " + JSON.stringify($scope.datePicker));

    queryUrl = getQueryUrl();

    url = '/incident/api?' + queryUrl;
    console.log('url: ' + url);

    incidentService.get(url)
    .then(function(incidents) {

      $scope.incidents = incidents.results;
      $scope.incidentCount = incidents.count;
      $scope.pages = incidents;
      $scope.pages.results = undefined;
      console.log($scope.incidents);
      console.log($scope.pages);

    });

    url = '/incident/aggregate?' + queryUrl;
    incidentService.get(url)
    .then(function(result) {
      $scope.woundedCount = result.wounded__sum;
      $scope.deathsCount= result.deaths__sum;
    });

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
    $scope.applyDateRange(null,null);
  }

  $scope.orderDirectionChanged = function() {

    invertOrderDirection();
    $scope.applyDateRange(null, null);

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

    console.log($scope.typeSelected);

    if($scope.typeSelected && $scope.incidentTypes.indexOf($scope.typeSelected)!=-1){
        queryUrl += "&type="+ String($scope.typeSelected.name);
    }

    return queryUrl;
  }

  invertOrderDirection = function() {

    $scope.isAscendingOrder = !$scope.isAscendingOrder;

    if( $scope.isAscendingOrder ){
        $scope.orderIcon = "glyphicon glyphicon-arrow-up";
    }else{
        $scope.orderIcon = "glyphicon glyphicon-arrow-down";
    }

    console.log("inverting order");
    console.log($scope.isAscendingOrder);

  }

  dateToString  = function (someDate) {
    //return String(someDate).split("T")[0];
    //return $filter('date', someDate, 'yyyy-MM-dd');
    return someDate.format('YYYY-MM-DD');
  }

  incidentService.get('/incident/api/')
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
    });

  incidentService.get('/incident/api/type/')
    .then(function(types){
      //$scope.incidentTypes = [{"name": "All"}].concat(types.results);
      //[].push.apply($scope.incidentType.types, {"name": "All"});
      $scope.incidentTypes = types.results;
    });

  $scope.gotoPage = function(pageUrl){
    console.log("daterange: " + JSON.stringify($scope.datePicker));
    console.log(typeof($scope.datePicker.date.startDate));
    incidentService.get(pageUrl)
    .then(function(incidents) {

      $scope.incidents = incidents.results;
      $scope.pages = incidents;
      $scope.pages.results = undefined;
      console.log($scope.incidents);
      console.log($scope.pages);

    });
  }


  $scope.submit = function() {

    var data = $scope.incident;
    data.date = $filter('date')(data.date, 'yyyy-MM-dd');

    console.log("submit function()");
    console.log(data);

    incidentService.post('/incident/api/', data)
      .then( function (res_data) {

          $scope.response = res_data.response;
          $scope.error = res_data.error;

          if('response' in res_data){
            $scope.incident = {};
          }

          console.log($scope.response);
          console.log($scope.error);

      });
    };

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
      redirectTo: '/'
    });
});
