
angular.module('annotator.heroes')
.service('Heroes', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'heroes/';
    var Heroes = {};
    Heroes.all = function () {
        return $http.get(base_url);
    };

    Heroes.damaging_abilities = function (id) {
        return $http.get(base_url + id + '/damaging_abilities/');
    };

    Heroes.reviving_abilities = function (id) {
        return $http.get(base_url + id + '/reviving_abilities/');
    };

    return Heroes;
});