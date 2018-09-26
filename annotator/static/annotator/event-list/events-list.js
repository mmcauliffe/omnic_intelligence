angular.module('eventList', [
    'annotator.events'
])
    .controller('EventListCtrl', function ($scope, Events, $state) {
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