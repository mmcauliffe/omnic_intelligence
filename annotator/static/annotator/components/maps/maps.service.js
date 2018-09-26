

angular.module('annotator.maps')
.service('Maps', function ($http, __env) {
    var base_url = __env.apiUrl + 'maps/';
    var Maps = {};
    Maps.all = function () {
        return $http.get(base_url);
    };

    return Maps;
});