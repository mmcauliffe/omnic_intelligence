
angular.module('annotator.events')
    .service('Events', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'events/';
    var Events = {};

    Events.all = function () {
        return $http.get(base_url);
    };

    Events.one = function (id) {
        return $http.get(base_url + id + '/');
    };

    Events.matches = function (id) {
        return $http.get(base_url + id + '/matches/');
    };

    Events.update = function (updatedEvent) {
        return $http.put(base_url + updatedEvent.id, updatedEvent);
    };

    Events.delete = function (id) {
        return $http.delete(base_url + id + '/');
    };

    Events.addOne = function (newEvent) {
        return $http.post(base_url, newEvent)
    };

    Events.addMatch = function (newMatch) {
        return $http.post(BASE_URL + 'matches/', newMatch)
    };

    return Events;
});
