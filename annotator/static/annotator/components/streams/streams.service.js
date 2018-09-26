
angular.module('annotator.streams')
    .service('Streams', function ($http, __env) {
    var base_url = __env.apiUrl + 'stream_channels/';
    var Streams = {};

    Streams.all = function () {
        return $http.get(base_url);
    };

    Streams.one = function (id) {
        return $http.get(base_url + id + '/');
    };

    Streams.vods = function (id) {
        return $http.get(base_url + id + '/vods/');
    };

    Streams.update = function (updatedStream) {
        return $http.put(base_url + updatedStream.id + '/', updatedStream);
    };

    Streams.delete = function (id) {
        return $http.delete(base_url + id + '/');
    };

    Streams.addOne = function (newStream) {
        return $http.post(base_url, newStream)
    };

    Streams.addVod = function (newVod) {
        return $http.post(__env.apiUrl + 'vods/', newVod)
    };

    return Streams;
});
