
angular.module('gameDetail', ['annotator.games',
    'annotator.matches',
    'annotator.teams',
    'annotator.maps'])
.controller('GameDetailCtrl', function ($scope, Games, Matches, Teams, Maps, $state, $stateParams) {
    console.log($stateParams);
    $scope.player_count = 6;
    $scope.range = function (num) {
        return new Array(num);
    };
    $scope.newRound = {};
    $scope.addRound = function () {
        $scope.newRound.game = $scope.game.id;
        Games.addRound($scope.newRound);
        $scope.newRound = {};
        Games.rounds($stateParams.game_id).then(function (res) {
            $scope.rounds = res.data;
        });
        $scope.next_round_number = $scope.next_round_number + 1;
        $scope.newRound.round_number = $scope.next_round_number;
    };

    $scope.initPlayer = function () {
        $scope.twitch_player = new Twitch.Player("twitch-embed", {
            width: 1280,
            height: 760,
            video: $scope.vod_link,
            autoplay: false,
            time: "0h0m0s"
        });
    };

    $scope.seekForward = function () {
        $scope.twitch_player.seek($scope.twitch_player.getCurrentTime() + 1);
    };
    $scope.seekBackward = function () {
        $scope.twitch_player.seek($scope.twitch_player.getCurrentTime() - 1);
    };

    $scope.updateBegin = function () {
        $scope.newRound.begin = Math.round($scope.twitch_player.getCurrentTime());
    };

    $scope.updateEnd = function () {
        $scope.newRound.end = Math.round($scope.twitch_player.getCurrentTime());
    };

    $scope.updateAvailablePlayers = function () {
        var used_players = [];
        console.log($scope.game.left_team.players);
        angular.forEach($scope.game.left_team.players, function (value, key) {
            used_players.push(value);
        });
        angular.forEach($scope.game.right_team.players, function (value, key) {
            used_players.push(value);
        });
        $scope.available_players = $scope.players.filter(function (p) {
            return used_players.indexOf(p.id) == -1;
        });
        console.log(used_players);
        console.log($scope.available_players);
    };

    $scope.saveGame = function () {
        Games.update($scope.game).then(function (res) {
            Games.one($stateParams.game_id).then(function (res) {
                $scope.game = res.data;
                var left_players = {};
                var right_players = {};
                for (i = 0; i < $scope.game.left_team.players.length; i++) {
                    left_players[$scope.game.left_team.players[i].player_index] = $scope.game.left_team.players[i].player;
                }
                for (i = 0; i < $scope.game.right_team.players.length; i++) {
                    right_players[$scope.game.left_team.players[i].player_index] = $scope.game.right_team.players[i].player;
                }
                $scope.game.left_team.players = left_players;
                $scope.game.right_team.players = right_players;
                console.log($scope.game);
            });
        });
    };

    Games.one($stateParams.game_id).then(function (res) {
        $scope.game = res.data;
        $scope.vod_type = $scope.game.vod_link[0];
        $scope.vod_link = $scope.game.vod_link[1];

        Matches.players($scope.game.match).then(function (res) {
            $scope.players = res.data;
            $scope.available_players = $scope.players;
        });
        var left_players = {};
        var right_players = {};
        for (i = 0; i < $scope.game.left_team.players.length; i++) {
            left_players[$scope.game.left_team.players[i].player_index] = $scope.game.left_team.players[i].player;
        }
        for (i = 0; i < $scope.game.right_team.players.length; i++) {
            right_players[$scope.game.left_team.players[i].player_index] = $scope.game.right_team.players[i].player;
        }
        $scope.game.left_team.players = left_players;
        $scope.game.right_team.players = right_players;
        console.log($scope.game);
        Matches.teams($scope.game.match).then(function (res) {
            $scope.teams = res.data;
        });
    });

    Maps.all().then(function (res) {
        $scope.maps = res.data;
    });
    Teams.colors().then(function (res) {
        $scope.colors = res.data;
    });
    Games.rounds($stateParams.game_id).then(function (res) {
        $scope.rounds = res.data;
        $scope.next_round_number = 1;
        angular.forEach($scope.rounds, function (r, i) {
            if (r.round_number + 1 > $scope.next_round_number) {
                $scope.next_round_number = r.round_number + 1
            }
        });
        $scope.newRound.round_number = $scope.next_round_number;
    });
    Teams.sides().then(function (res) {
        $scope.sides = res.data;
    });

});