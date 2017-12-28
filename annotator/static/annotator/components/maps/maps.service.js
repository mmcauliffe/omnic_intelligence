

angular.module('annotator.maps')
.service('Maps', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'maps/';
    var Maps = {};
    Maps.all = function () {
        return $http.get(base_url);
    };

    return Maps;
});