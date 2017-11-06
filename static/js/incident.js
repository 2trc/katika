var incidentApp = angular.module('incidentApp', ["ngRoute"
//  ,"angular-jquery-locationpicker",
//  "ui.bootstrap.datetimepicker"
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

  console.log("Hollalalalalal");

  var self = this;

  $scope.incidentType = {};
  $scope.incident = {};
  $scope.incidents = [];
  $scope.pages = {};

  incidentService.get('/incident/api/')
    .then(function(incidents) {

      $scope.incidents = incidents.results;
      $scope.pages = incidents;
      $scope.pages.results = undefined;
      console.log($scope.incidents);
      console.log($scope.pages);

    });

  incidentService.get('/incident/api/type/')
    .then(function(types){
      $scope.incidentType.types = types.results;
    });

  $scope.gotoPage = function(pageNumber){
    incidentService.get('/incident/api/?page='+pageNumber)
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
