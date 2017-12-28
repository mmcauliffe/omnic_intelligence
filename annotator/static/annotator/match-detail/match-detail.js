
angular.module('matchDetail', [])
.controller('MatchDetailCtrl', function ($scope, Matches, Teams, Maps, $state, $stateParams) {
    $scope.newGame = {};
    $scope.player_count = 6;

    $scope.range = function (num) {
        return new Array(num);
    };
    $scope.addGame = function () {
        $scope.newGame.match = $scope.match.id;

        Matches.addGame($scope.newGame)
            .then(function (res) {
                // redirect to homepage once added
                $state.go('match-detail', {match_id: $stateParams.match_id});
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