var app = angular.module('Annotator', [
    'ui.router',
    'ngCookies',
    'ngMaterial'
]).run(
    function ($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        // Add the following two lines
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

app.filter('secondsToDateTime', [function() {
    return function(seconds) {
        return new Date(1970, 0, 1).setSeconds(seconds);
    };
}])

app.constant('BASE_URL', 'http://127.0.0.1:8000/annotator/api/');

app.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
        .state('events', {
            url: '/',
            templateUrl: '/static/annotator/ng_templates/event_list.html',
            controller: 'EventListCtrl'
        }).state('events-detail', {
        url: '/:event_id',
        templateUrl: '/static/annotator/ng_templates/event_detail.html',
        controller: 'EventDetailCtrl'
    }).state('match-detail', {
        url: '/matches/:match_id',
        templateUrl: '/static/annotator/ng_templates/match_detail.html',
        controller: 'MatchDetailCtrl'
    }).state('game-detail', {
        url: '/games/:game_id',
        templateUrl: '/static/annotator/ng_templates/game_detail.html',
        controller: 'GameDetailCtrl'
    }).state('round-detail', {
        url: '/round/:round_id',
        templateUrl: '/static/annotator/ng_templates/round_detail.html',
        controller: 'RoundDetailCtrl'
    });

    $urlRouterProvider.otherwise('/');
});

app.service('Events', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'events/';
    var Events = {};

    Events.all = function () {
        return $http.get(base_url);
    };

    Events.one = function (id) {
        return $http.get(base_url + id + '/');
    };

    Events.matches = function (id) {
        return $http.get(base_url + id + '/matches/');
    };

    Events.update = function (updatedEvent) {
        return $http.put(base_url + updatedEvent.id, updatedEvent);
    };

    Events.delete = function (id) {
        return $http.delete(base_url + id + '/');
    };

    Events.addOne = function (newEvent) {
        return $http.post(base_url, newEvent)
    };

    return Events;
});

app.service('Matches', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'matches/';
    var Matches = {};

    Matches.all = function () {
        return $http.get(base_url);
    };

    Matches.one = function (id) {
        return $http.get(base_url + id + '/');
    };

    Matches.games = function (id) {
        return $http.get(base_url + id + '/games/');
    };

    Matches.update = function (updatedMatch) {
        return $http.put(base_url + updatedMatch.id, updatedMatch);
    };

    Matches.delete = function (id) {
        return $http.delete(base_url + id + '/');
    };

    Matches.addOne = function (newMatch) {
        return $http.post(base_url, newMatch)
    };

    return Matches;
});

app.service('Games', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'games/';
    var Games = {};

    Games.all = function () {
        return $http.get(base_url);
    };

    Games.one = function (id) {
        return $http.get(base_url + id + '/');
    };

    Games.rounds = function (id) {
        return $http.get(base_url + id + '/rounds/');
    };

    Games.update = function (updatedGame) {
        return $http.put(base_url + updatedGame.id, updatedGame);
    };

    Games.delete = function (id) {
        return $http.delete(base_url + id + '/');
    };

    Games.addOne = function (newGame) {
        return $http.post(base_url, newGame)
    };

    return Games;
});

app.service('Rounds', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'rounds/';
    var Rounds = {};

    Rounds.all = function () {
        return $http.get(base_url);
    };

    Rounds.one = function (id) {
        return $http.get(base_url + id + '/');
    };

    Rounds.switches = function (id) {
        return $http.get(base_url + id + '/switches/');
    };

    Rounds.delete_switch = function(id){
        return $http.delete(BASE_URL + 'switches/' + id + "/")
    };

    Rounds.deaths = function (id) {
        return $http.get(base_url + id + '/deaths/');
    };

    Rounds.delete_death = function(id){
        return $http.delete(BASE_URL + 'deaths/' + id + "/")
    };

    Rounds.npcdeaths = function (id) {
        return $http.get(base_url + id + '/npcdeaths/');
    };

    Rounds.delete_npcdeath = function(id){
        return $http.delete(BASE_URL + 'npcdeaths/' + id + "/")
    };

    Rounds.kills = function (id) {
        return $http.get(base_url + id + '/kills/');
    };

    Rounds.delete_kill = function(id){
        return $http.delete(BASE_URL + 'kills/' + id + "/")
    };

    Rounds.killnpcs = function (id) {
        return $http.get(base_url + id + '/killnpcs/');
    };

    Rounds.delete_killnpc = function(id){
        return $http.delete(BASE_URL + 'killnpcs/' + id + "/")
    };

    Rounds.revives = function (id) {
        return $http.get(base_url + id + '/revives/');
    };

    Rounds.delete_revive = function(id){
        return $http.delete(BASE_URL + 'revives/' + id + "/")
    };

    Rounds.ultuses = function (id) {
        return $http.get(base_url + id + '/ultuses/');
    };

    Rounds.delete_ultuse = function(id){
        return $http.delete(BASE_URL + 'ultuses/' + id + "/")
    };

    Rounds.ultgains = function (id) {
        return $http.get(base_url + id + '/ultgains/');
    };

    Rounds.delete_ultgain = function(id){
        return $http.delete(BASE_URL + 'ultgains/' + id + "/")
    };

    Rounds.pauses = function (id) {
        return $http.get(base_url + id + '/pauses/');
    };

    Rounds.delete_pause = function(id){
        return $http.delete(BASE_URL + 'pauses/' + id + "/")
    };

    Rounds.unpauses = function (id) {
        return $http.get(base_url + id + '/unpauses/');
    };

    Rounds.delete_unpause = function(id){
        return $http.delete(BASE_URL + 'unpauses/' + id + "/")
    };

    Rounds.pointgains = function (id) {
        return $http.get(base_url + id + '/pointgains/');
    };

    Rounds.delete_pointgain = function(id){
        return $http.delete(BASE_URL + 'pointgains/' + id + "/")
    };

    Rounds.pointflips = function (id) {
        return $http.get(base_url + id + '/pointflips/');
    };

    Rounds.delete_pointflip = function(id){
        return $http.delete(BASE_URL + 'pointflips/' + id + "/")
    };



    Rounds.update = function (updatedRound) {
        return $http.put(base_url + updatedRound.id, updatedRound);
    };

    Rounds.delete = function (id) {
        return $http.delete(base_url + id + '/');
    };

    Rounds.addOne = function (newRound) {
        return $http.post(base_url, newRound)
    };

    return Rounds;
});

app.controller('EventListCtrl', function ($scope, Events, $state) {
    $scope.newEvent = {};
    $scope.addEvent = function () {
        Events.addOne($scope.newEvent);
        Events.all().then(function (res) {
            $scope.events = res.data;
        });
        $scope.newEvent = {}
    };

    $scope.deleteEvent = function (id) {
        Events.delete(id);
        // update the list in ui
        $scope.events = $scope.events.filter(function (event) {
            return event.id !== id;
        })
    };

    Events.all().then(function (res) {
        $scope.events = res.data;
    });
});

app.controller('EventDetailCtrl', function ($scope, Events, $state, $stateParams) {

    Events.one($stateParams.event_id).then(function (res) {
        $scope.event = res.data;
    });
    Events.matches($stateParams.event_id).then(function (res) {
        $scope.matches = res.data;
    });
});

app.controller('MatchDetailCtrl', function ($scope, Matches, $state, $stateParams) {

    Matches.one($stateParams.match_id).then(function (res) {
        $scope.match = res.data;
    });
    Matches.games($stateParams.match_id).then(function (res) {
        $scope.games = res.data;
    });
});

app.controller('GameDetailCtrl', function ($scope, Games, $state, $stateParams) {

    Games.one($stateParams.game_id).then(function (res) {
        $scope.game = res.data;
    });
    Games.rounds($stateParams.game_id).then(function (res) {
        $scope.rounds = res.data;
    });
});

app.controller('RoundDetailCtrl', function ($scope, Rounds, $state, $stateParams) {

    Rounds.one($stateParams.round_id).then(function (res) {
        $scope.round = res.data;
    });
    Rounds.switches($stateParams.round_id).then(function (res) {
        $scope.switches = res.data;
    });

    $scope.deleteSwitch = function (id) {
        Rounds.delete_switch(id);
        // update the list in ui
        $scope.switches = $scope.switches.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.deaths($stateParams.round_id).then(function (res) {
        $scope.deaths = res.data;
    });

    $scope.deleteDeath = function (id) {
        Rounds.delete_death(id);
        // update the list in ui
        $scope.deaths = $scope.deaths.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.npcdeaths($stateParams.round_id).then(function (res) {
        $scope.npcdeaths = res.data;
    });

    $scope.deleteNPCDeath = function (id) {
        Rounds.delete_npcdeath(id);
        // update the list in ui
        $scope.npcdeaths = $scope.npcdeaths.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.kills($stateParams.round_id).then(function (res) {
        $scope.kills = res.data;
    });

    $scope.deleteKill = function (id) {
        Rounds.delete_kill(id);
        // update the list in ui
        $scope.kills = $scope.kills.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.killnpcs($stateParams.round_id).then(function (res) {
        $scope.killnpcs = res.data;
    });

    $scope.deleteKillNPC = function (id) {
        Rounds.delete_killnpc(id);
        // update the list in ui
        $scope.killnpcs = $scope.killnpcs.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.revives($stateParams.round_id).then(function (res) {
        $scope.revives = res.data;
    });

    $scope.deleteRevive = function (id) {
        Rounds.delete_revive(id);
        // update the list in ui
        $scope.revives = $scope.revives.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.ultuses($stateParams.round_id).then(function (res) {
        $scope.ultuses = res.data;
    });

    $scope.deleteUltUse = function (id) {
        Rounds.delete_ultuse(id);
        // update the list in ui
        $scope.ultuses = $scope.ultuses.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.ultgains($stateParams.round_id).then(function (res) {
        $scope.ultgains = res.data;
    });

    $scope.deleteUltGain = function (id) {
        Rounds.delete_ultgain(id);
        // update the list in ui
        $scope.ultgains = $scope.ultgains.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.pauses($stateParams.round_id).then(function (res) {
        $scope.pauses = res.data;
    });

    $scope.deletePause = function (id) {
        Rounds.delete_pause(id);
        // update the list in ui
        $scope.pauses = $scope.pauses.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.unpauses($stateParams.round_id).then(function (res) {
        $scope.unpauses = res.data;
    });

    $scope.deleteUnpause = function (id) {
        Rounds.delete_unpause(id);
        // update the list in ui
        $scope.unpauses = $scope.unpauses.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.pointgains($stateParams.round_id).then(function (res) {
        $scope.pointgains = res.data;
    });

    $scope.deletePointGain = function (id) {
        Rounds.delete_pointgain(id);
        // update the list in ui
        $scope.pointgains = $scope.pointgains.filter(function (event) {
            return event.id !== id;
        })
    };

    Rounds.pointflips($stateParams.round_id).then(function (res) {
        $scope.pointflips = res.data;
    });

    $scope.deletePointFlip = function (id) {
        Rounds.delete_pointflip(id);
        // update the list in ui
        $scope.pointflips = $scope.pointflips.filter(function (event) {
            return event.id !== id;
        })
    };

});

app.controller('MatchListCtrl', function ($scope, Matches, $state) {
    $scope.newMatch = {};
    $scope.addMatch = function () {
        Events.addOne($scope.newMatch);
        Events.all().then(function (res) {
            $scope.matches = res.data;
        });
        $scope.newMatch = {}
    };

    $scope.deleteMatch = function (id) {
        Matches.delete(id);
        // update the list in ui
        $scope.matches = $scope.matches.filter(function (event) {
            return event.id !== id;
        })
    };

    Matches.all().then(function (res) {
        $scope.matches = res.data;
    });
});

app.controller('GameListCtrl', function ($scope, Games, $state) {
    $scope.newGame = {};
    $scope.addGame = function () {
        Events.addOne($scope.newGame);
        Events.all().then(function (res) {
            $scope.games = res.data;
        });
        $scope.newEvent = {}
    };

    $scope.deleteEvent = function (id) {
        Events.delete(id);
        // update the list in ui
        $scope.events = $scope.events.filter(function (event) {
            return event.id !== id;
        })
    };

    Events.all().then(function (res) {
        $scope.events = res.data;
    });
});