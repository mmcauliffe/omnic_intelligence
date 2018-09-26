angular.module('annotator.roundstatus')
    .service('RoundStatus', function ($http, __env) {
        var base_url = __env.apiUrl + 'round_status/';
        var RoundStatus = {};

        RoundStatus.all = function (offset, ordering, search) {
            var url = base_url + "?ordering=" + ordering;
            url += '&offset=' + offset;
            url += '&limit=100';
            if (search) {
                url += '&search=' + search;
            }
            console.log(search);
            console.log(url);
            return $http.get(url);
        };

        return RoundStatus;
    });