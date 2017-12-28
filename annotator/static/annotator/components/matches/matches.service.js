
angular.module('annotator.matches')
.service('Matches', function ($http, BASE_URL) {
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

    Matches.addGame = function (newGame) {
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
        newGame.left_team.players = left_players;
        newGame.right_team.players = right_players;
        return $http.post(BASE_URL + 'games/', newGame);
    };

    Matches.teams = function (id) {
        return $http.get(base_url + id + '/teams/');
    };

    Matches.players = function (id) {
        return $http.get(BASE_URL + 'players/');
    };


    return Matches;
});