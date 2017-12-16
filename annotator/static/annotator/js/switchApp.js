var app = angular.module('ng-events', [
    'ui.router',
    'ngCookies'
]).run(
    function($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        // Add the following two lines
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

app.constant('BASE_URL', 'http://127.0.0.1:8000/annotator/api/switches/');

app.config(function($stateProvider, $urlRouterProvider){
    $stateProvider
        .state('home', {
            url: '/',
            templateUrl: '/static/annotator/ng_templates/switch_list.html',
            controller: 'MainCtrl'
        });

    $urlRouterProvider.otherwise('/');
});

app.service('Switches', function($http, BASE_URL){
    var Switches = {};

    Switches.all = function(){
        return $http.get(BASE_URL);
    };

    Switches.update = function(updatedSwitch){
        return $http.put(BASE_URL + updatedSwitch.id, updatedSwitch);
    };

    Switches.delete = function(id){
        return $http.delete(BASE_URL + id + '/');
    };

    Switches.addOne = function(newSwitch){
        return $http.post(BASE_URL, newSwitch)
    };

    return Switches;
});

app.controller('MainCtrl', function($scope, Switches, $state){
    $scope.newSwitch = {};
    $scope.addEvent = function() {
        Switches.addOne($scope.newSwitch);
        Switches.all().then(function(res){
            $scope.switches = res.data;
        });
        $scope.newSwitch = {}
    };

    $scope.deleteEvent = function(id){
        Switches.delete(id);
        // update the list in ui
        $scope.switches = $scope.switches.filter(function(s){
            return s.id !== id;
        })
    };

    Switches.all().then(function(res){
        $scope.switches = res.data;
    });
});