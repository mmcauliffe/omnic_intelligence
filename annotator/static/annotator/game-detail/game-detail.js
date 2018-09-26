
angular.module('gameDetail', ['annotator.games',
    'annotator.matches',
    'annotator.teams',
    'annotator.maps'])
    .filter('secondsToDateTime', [function () {
        return function (seconds) {
            return new Date(1970, 0, 1).setSeconds(seconds);
        };
    }])
.controller('GameDetailCtrl', function ($scope, Games, Matches, Teams, Maps, Rounds, $state, $stateParams) {
    console.log($stateParams);
    $scope.player_count = 6;
    $scope.range = function (num) {
        return new Array(num);
    };
    $scope.newRound = {};
    $scope.addRound = function () {
        $scope.newRound.game = $scope.game.id;
        Games.addRound($scope.newRound).then(function(res){
            $scope.newRound = {};
            Games.rounds($stateParams.game_id).then(function (res) {
                $scope.rounds = res.data;
            });
            $scope.next_round_number = $scope.next_round_number + 1;
            $scope.newRound.round_number = $scope.next_round_number;
        });
    };

    $scope.deleteRound = function (id){
        Rounds.delete(id);
        $scope.rounds = $scope.rounds.filter(function (r) {
            return r.id !== id;
        })
    };

    $scope.initTwitchPlayer = function () {
        $scope.twitch_player = new Twitch.Player("twitch-embed", {
            width: 1280,
            height: 760,
            video: $scope.vod_link,
            autoplay: false,
            time: "0h0m0s"
        });
    };

    $scope.initYoutubePlayer = function (){
        $scope.youtube_player = new YT.Player('youtube-embed', {
          height: '760',
          width: '1280',
          videoId: $scope.vod_link
        });
    };


    $scope.seekTo = function(time){
        if ($scope.vod_type === 'twitch'){
            $scope.twitch_player.seek(time);
        }
        else if ($scope.vod_type === 'youtube'){
            $scope.youtube_player.seekTo(time);
        }
    };

    $scope.seekForward = function (amount) {
        var time = 0;
        if ($scope.vod_type === 'twitch'){
            time = $scope.twitch_player.getCurrentTime();
        }
        else if ($scope.vod_type === 'youtube'){
            time = $scope.youtube_player.getCurrentTime();
        }
        $scope.seekTo(time + amount);
    };
    $scope.seekBackward = function (amount) {
        var time = 0;
        if ($scope.vod_type === 'twitch'){
            time = $scope.twitch_player.getCurrentTime();
        }
        else if ($scope.vod_type === 'youtube'){
            time = $scope.youtube_player.getCurrentTime();
        }
        $scope.seekTo(time - amount);
    };

    $scope.updateBegin = function () {
        var time;
        if ($scope.vod_type === 'twitch'){
            time = $scope.twitch_player.getCurrentTime();
        }
        else if ($scope.vod_type === 'youtube'){
            time = $scope.youtube_player.getCurrentTime();
        }

        $scope.newRound.begin = Math.round(time);
    };

    $scope.updateEnd = function () {
        var time;
        if ($scope.vod_type === 'twitch'){
            time = $scope.twitch_player.getCurrentTime();
        }
        else if ($scope.vod_type === 'youtube'){
            time = $scope.youtube_player.getCurrentTime();
        }
        $scope.newRound.end = Math.round(time);
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
        console.log($scope.game );

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
        console.log($scope.colors)
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