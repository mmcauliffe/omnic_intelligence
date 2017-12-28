
angular.module('annotator.npcs', [])
.service('NPCs', function ($http, BASE_URL) {
    var base_url = BASE_URL + 'npcs/';
    var NPCs = {};
    NPCs.all = function () {
        return $http.get(base_url);
    };

    return NPCs;
});