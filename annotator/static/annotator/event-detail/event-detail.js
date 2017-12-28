
angular.module('eventDetail', [
    'annotator.events',
    'annotator.teams',
])
.controller('EventDetailCtrl', function ($scope, Events, Teams, $state, $stateParams) {
    $scope.newMatch = {};
    $scope.addMatch = function () {
        console.log($scope);
        $scope.newMatch.event = $scope.event.id;
        $scope.newMatch.teams = [$scope.newMatch.team1_id, $scope.newMatch.team2_id];
        console.log($scope.newMatch);

        Events.addMatch($scope.newMatch)
            .then(function (res) {
                // redirect to homepage once added
                $state.go('events-detail', {event_id: $stateParams.event_id});
            });
    };
    Teams.all().then(function (res) {
        $scope.teams = res.data;
    });
    Events.one($stateParams.event_id).then(function (res) {
        $scope.event = res.data;
    });
    Events.matches($stateParams.event_id).then(function (res) {
        $scope.matches = res.data;
    });
});