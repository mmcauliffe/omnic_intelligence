
angular.module('annotator.teams')
.service('Teams', function ($http, __env) {
    var base_url = __env.apiUrl + 'teams/';
    var Teams = {};
    Teams.all = function () {
        return $http.get(base_url);
    };
    Teams.colors = function () {
        return $http.get(__env.apiUrl + 'team_colors/')
    };

    Teams.sides = function () {
        return $http.get(__env.apiUrl + 'sides/')
    };

    return Teams
});