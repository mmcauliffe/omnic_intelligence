
angular.module('annotator.teams')
.service('Teams', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'teams/';
    var Teams = {};
    Teams.all = function () {
        return $http.get(base_url);
    };
    Teams.colors = function () {
        return $http.get(BASE_URL + 'team_colors/')
    };

    Teams.sides = function () {
        return $http.get(BASE_URL + 'sides/')
    };

    return Teams
});