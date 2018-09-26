
angular.module('annotator.npcs', [])
.service('NPCs', function ($http, __env) {
    var base_url = __env.apiUrl + 'npcs/';
    var NPCs = {};
    NPCs.all = function () {
        return $http.get(base_url);
    };

    return NPCs;
});