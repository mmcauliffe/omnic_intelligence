var env = {};

// Import variables if present (from env.js)
if (window) {
    Object.assign(env, window.__env);
}

var app = angular.module('annotator', [
    'ngResource',
    'ui.router',
    'ui.bootstrap',
    'ngCookies',
    'md.data.table',
    'ngMaterial',
    'eventList',
    'eventDetail',
    'matchDetail',
    'gameDetail',
    'roundDetail',
    'roundStatus',
    'navbar',
    'login',
    'logout'
]).run(
    function ($http, $cookies) {
    $http.defaults.withCredentials = true;
    //    $http.defaults.headers.post['X-CSRFToken'] = $cookies.get('csrftoken');
        // Add the following two lines
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    });


app.constant('__env', env);

app.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
        .state('home', {
            url: '/',
            template: '<div></div>'
        })
        .state('user-profile', {
            url: '/',
            template: '<div></div>'
        })
        .state('event-list', {
            url: '/events',
            templateUrl: static('annotator/event-list/event_list.html'),
            controller: 'EventListCtrl'
        }).state('event-detail', {
        url: '/events/{event_id:int}',
        templateUrl: static('annotator/event-detail/event_detail.html'),
        controller: 'EventDetailCtrl'
    }).state('match-detail', {
        url: '/matches/:match_id',
        templateUrl: static('annotator/match-detail/match_detail.html'),
        controller: 'MatchDetailCtrl'
    }).state('game-detail', {
        url: '/games/:game_id',
        templateUrl: static('annotator/game-detail/game_detail.html'),
        controller: 'GameDetailCtrl'
    }).state('round-detail', {
        url: '/round/:round_id',
        templateUrl: static('annotator/round-detail/round_detail.html'),
        controller: 'RoundDetailCtrl'
    }).state('add-match', {
        url: '/:event_id/add_match',
        templateUrl: static('annotator/event-detail/add_match.html'),
        controller: 'EventDetailCtrl'
    }).state('round-status', {
        url: '/rounds',
        templateUrl: static('annotator/round-status/round_status.html'),
        controller: 'RoundStatusCtrl'
    }).state('heroes', {
        url: '/heroes',
        templateUrl: static('annotator/heroes/heroes.html'),
        controller: 'HeroesCtrl'
    }).state('check', {
        url: '/check'
    })
        .state('login', {
            url: '/login',
            templateUrl: static('annotator/login/login.html'),
            controller: 'LoginCtrl',
            resolve: {}
        }).state('logout', {
        url: '/logout',
        templateUrl: static('annotator/logout/logout.html'),
        controller: 'LogoutCtrl',
        resolve: {}
    });

    $urlRouterProvider.otherwise('/');
});