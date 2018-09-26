
angular.module('annotator.matches')
.service('Matches', function ($http, __env) {
    var base_url = __env.apiUrl + 'matches/';
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
        return $http.put(base_url + updatedMatch.id  + '/', updatedMatch);
    };

    Matches.delete = function (id) {
        return $http.delete(base_url + id + '/');
    };

    Matches.addOne = function (newMatch) {
        return $http.post(base_url, newMatch)
    };

    Matches.addGame = function (newGame) {
        var data = {};
        data.game_number = newGame.game_number;
        data.left_team = {};
        data.left_team.color = newGame.left_team.color;
        data.left_team.team = newGame.left_team.team;
        data.right_team = {};
        data.right_team.color = newGame.right_team.color;
        data.right_team.team = newGame.right_team.team;
        data.map = newGame.map;
        data.match = newGame.match;
        var left_players = [];
        var right_players = [];
        for (i = 0; i < 6; i++) {
            if (newGame.left_team.players != undefined && newGame.left_team.players[i] != null) {
                left_players.push({'player_index': i, 'player': newGame.left_team.players[i]});
            }
            if (newGame.right_team.players != undefined && newGame.right_team.players[i] != null) {
                right_players.push({'player_index': i, 'player': newGame.right_team.players[i]});
            }
        }
        data.left_team.players = left_players;
        data.right_team.players = right_players;
        console.log(data)
        return $http.post(__env.apiUrl + 'games/', data);
    };

    Matches.teams = function (id) {
        return $http.get(base_url + id + '/teams/');
    };

    Matches.film_formats = function () {
        return $http.get(__env.apiUrl + 'film_formats/')
    };

    Matches.players = function (id) {
        return $http.get(__env.apiUrl + 'players/');
    };


    return Matches;
});