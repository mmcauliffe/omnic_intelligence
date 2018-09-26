

angular.module('annotator.games')
.service('Games', function ($http, __env) {
    var base_url = __env.apiUrl + 'games/';
    var Games = {};

    Games.all = function () {
        return $http.get(base_url);
    };

    Games.one = function (id) {
        return $http.get(base_url + id + '/');
    };

    Games

    Games.rounds = function (id) {
        return $http.get(base_url + id + '/rounds/');
    };

    Games.update = function (updatedGame) {
        var left_players = [];
        var right_players = [];
        for (i = 0; i < 6; i++) {
            if (updatedGame.left_team.players != undefined && updatedGame.left_team.players[i] != null) {
                left_players.push({'player_index': i, 'player': updatedGame.left_team.players[i]});
            }
            if (updatedGame.right_team.players != undefined && updatedGame.right_team.players[i] != null) {
                right_players.push({'player_index': i, 'player': updatedGame.right_team.players[i]});
            }
        }
        updatedGame.left_team.players = left_players;
        updatedGame.right_team.players = right_players;
        console.log(updatedGame);
        return $http.put(base_url + updatedGame.id + '/', updatedGame);
    };

    Games.delete = function (id) {
        return $http.delete(base_url + id + '/');
    };

    Games.addOne = function (newGame) {
        return $http.post(base_url, newGame)
    };

    Games.addRound = function (newRound) {
        return $http.post(__env.apiUrl + 'rounds/', newRound);
    };

    return Games;
});