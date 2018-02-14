var kthesisApp = angular.module('kthesisApp', ["ngRoute"
]);

//https://stackoverflow.com/questions/41211875/angularjs-1-6-0-latest-now-routes-not-working
kthesisApp.config(['$locationProvider', '$httpProvider', function($locationProvider,$httpProvider) {
    $locationProvider.hashPrefix('');

}]);


function kthesisService($http) {

  this.get = function(url) {
    return $http.get(url)
    .then(function(res) {
      // return the enveloped data
      //console.log(res.data);
      return res.data;
    })
  }


  /*this.post = function(url, data) {

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
  }*/
};


function KthesisCtrl(kthesisService, $scope, $filter) {

  initializeOrderDirection = function() {
     $scope.isAscendingOrder = false;
     $scope.orderIcon = "glyphicon glyphicon-arrow-down";

     //console.log("initializing order");
     //console.log($scope.orderIcon);
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

    kthesisService.get(url)
    .then(function(incidents) {

      $scope.incidents = incidents.results;
      $scope.incidentCount = incidents.count;
      $scope.pages = incidents;
      $scope.pages.results = undefined;
      console.log($scope.incidents);
      console.log($scope.pages);

    });

    url = '/incident/aggregate?' + queryUrl;
    kthesisService.get(url)
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

    //console.log($scope.typeSelected);

    if($scope.typeSelected && $scope.typeSelected.name != "All"){
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

  kthesisService.get('/kthesis/api/thesis')
    .then(function(output) {

      $scope.these = output.results;
      $scope.thesisCount = output.count;
      $scope.pages = output;
      $scope.pages.results = undefined;
      console.log($scope.these);
      console.log($scope.pages);

  });


  $scope.gotoPage = function(pageUrl){
    //console.log("daterange: " + JSON.stringify($scope.datePicker));
    //console.log(typeof($scope.datePicker.date.startDate));
    kthesisService.get(pageUrl)
    .then(function(output) {

      $scope.these = output.results;
      $scope.thesisCount = output.count;
      $scope.pages = output;
      $scope.pages.results = undefined;
      console.log($scope.these);
      console.log($scope.pages);

    });
  }
}


kthesisApp
  .controller('KthesisController', KthesisCtrl)
  .service('kthesisService', kthesisService);


kthesisApp.config(function($routeProvider) {
    $routeProvider
    .when("/", {
        templateUrl : "/static/shared/kthesis.html",
        controller: "KthesisController"
    })
   .otherwise({
      redirectTo: '/'
    });
});
