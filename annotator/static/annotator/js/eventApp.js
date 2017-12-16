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

app.constant('BASE_URL', 'http://127.0.0.1:8000/annotator/api/events/');

app.config(function($stateProvider, $urlRouterProvider){
    $stateProvider
        .state('home', {
            url: '/',
            templateUrl: '/static/annotator/ng_templates/event_list.html',
            controller: 'MainCtrl'
        });

    $urlRouterProvider.otherwise('/');
});

app.service('Events', function($http, BASE_URL){
    var Events = {};

    Events.all = function(){
        return $http.get(BASE_URL);
    };

    Events.update = function(updatedEvent){
        return $http.put(BASE_URL + updatedEvent.id, updatedEvent);
    };

    Events.delete = function(id){
        return $http.delete(BASE_URL + id + '/');
    };

    Events.addOne = function(newEvent){
        return $http.post(BASE_URL, newEvent)
    };

    return Events;
});

app.controller('MainCtrl', function($scope, Events, $state){
    $scope.newEvent = {};
    $scope.addEvent = function() {
        Events.addOne($scope.newEvent);
        Events.all().then(function(res){
            $scope.events = res.data;
        });
        $scope.newEvent = {}
    };

    $scope.deleteEvent = function(id){
        Events.delete(id);
        // update the list in ui
        $scope.events = $scope.events.filter(function(event){
            return event.id !== id;
        })
    };

    Events.all().then(function(res){
        $scope.events = res.data;
    });
});