angular.module('eventDetail', [
    'annotator.events',
    'annotator.teams',
    'annotator.streams'
])
    .controller('EventDetailCtrl', function ($scope, Events, Teams, $state, $stateParams, Streams) {
        $scope.newMatch = {};
        $scope.addMatch = function () {
            $scope.newMatch.event = $scope.event.id;
            $scope.newMatch.teams = [$scope.newMatch.team1_id, $scope.newMatch.team2_id];

            Events.addMatch($scope.newMatch)
                .then(function (res) {
                    Events.matches($stateParams.event_id).then(function (res) {
                        $scope.matches = res.data;
                    });
                });
        };

        Streams.all().then(function(res) {
           $scope.streams = res.data;
        });

        Teams.all().then(function (res) {
            $scope.teams = res.data;
        });
        Events.one($stateParams.event_id).then(function (res) {
            $scope.event = res.data;
            console.log($scope.event)
        });

        Events.spectatorModes().then(function (res) {
            $scope.spectator_modes = res.data;
        });

        $scope.saveEvent = function () {
            Events.update($scope.event);
        };

        Events.matches($stateParams.event_id).then(function (res) {
            $scope.matches = res.data;
        });
    });