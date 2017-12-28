var app = angular.module('annotator', [
    'ui.router',
    'ngCookies',
    'ngMaterial',
    'eventList',
    'eventDetail',
    'matchDetail',
    'gameDetail',
    'roundDetail'
]).run(
    function ($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        // Add the following two lines
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    });


app.constant('BASE_URL', 'http://127.0.0.1:8000/annotator/api/');

app.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
        .state('event-list', {
            url: '/',
            templateUrl: '/static/annotator/event-list/event_list.html',
            controller: 'EventListCtrl'
        }).state('event-detail', {
        url: '/:event_id',
        templateUrl: '/static/annotator/event-detail/event_detail.html',
        controller: 'EventDetailCtrl'
    }).state('match-detail', {
        url: '/matches/:match_id',
        templateUrl: '/static/annotator/match-detail/match_detail.html',
        controller: 'MatchDetailCtrl'
    }).state('game-detail', {
        url: '/games/:game_id',
        templateUrl: '/static/annotator/game-detail/game_detail.html',
        controller: 'GameDetailCtrl'
    }).state('round-detail', {
        url: '/round/:round_id',
        templateUrl: '/static/annotator/round-detail/round_detail.html',
        controller: 'RoundDetailCtrl'
    }).state('add-match', {
        url: '/:event_id/add_match',
        templateUrl: '/static/annotator/event-detail/add_match.html',
        controller: 'EventDetailCtrl'
    }).state('add-game', {
        url: '/matchs/:match_id/add_game',
        templateUrl: '/static/annotator/match-detail/add_game.html',
        controller: 'MatchDetailCtrl'
    });

    $urlRouterProvider.otherwise('/');
});