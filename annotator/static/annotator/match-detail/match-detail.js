
angular.module('matchDetail', [])
.controller('MatchDetailCtrl', function ($scope, Matches, Games, Teams, Maps, $state, $stateParams, $window, Streams) {
    $scope.newGame = {};
    $scope.player_count = 6;

    Matches.film_formats().then(function (res){
        $scope.film_formats = res.data;
        console.log($scope.film_formats);
    });


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

    $scope.updateAllTimes = function(){
        var time;
        if ($scope.vod_type === 'twitch'){
            time = $scope.twitch_player.getCurrentTime();
        }
        else if ($scope.vod_type === 'youtube'){
            time = $scope.youtube_player.getCurrentTime();
        }
        $scope.match.start_time = time;
        Matches.update( $scope.match);
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

    $scope.range = function (num) {
        return new Array(num);
    };
    $scope.addGame = function () {
        $scope.newGame.match = $scope.match.id;

        Matches.addGame($scope.newGame)
            .then(function (res) {
                Matches.games($stateParams.match_id).then(function (res) {
                    $scope.games = res.data;
                });
            });
    };
    $scope.deleteGame = function(id){

    var deleteGame = $window.confirm('Are you absolutely sure you want to delete?');

    if (deleteGame) {
      Games.delete(id).then(function(res){
          Matches.games($stateParams.match_id).then(function (res) {
        $scope.games = res.data;
    });
      });
    }
    };
    $scope.saveMatch = function(){
        Matches.update($scope.match).then(function (res){

            Matches.one($stateParams.match_id).then(function (res) {
                $scope.match = res.data;
            })
            });
    };

    Matches.teams($stateParams.match_id).then(function (res) {
        $scope.teams = res.data;
    });

    Teams.colors().then(function (res) {
        $scope.colors = res.data;
    });

    Matches.one($stateParams.match_id).then(function (res) {
        $scope.match = res.data;

    });
    Matches.games($stateParams.match_id).then(function (res) {
        $scope.games = res.data;
    });
    Matches.players($stateParams.match_id).then(function (res) {
        $scope.players = res.data;
    });
    Maps.all().then(function (res) {
        $scope.maps = res.data;
    });
});