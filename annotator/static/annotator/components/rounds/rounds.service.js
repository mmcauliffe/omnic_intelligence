angular.module('annotator.rounds')
    .service('Rounds', function ($http, __env) {
        var base_url = __env.apiUrl + 'rounds/';
        var Rounds = {};

        Rounds.all = function () {
            return $http.get(base_url);
        };

        Rounds.annotation_sources = function(){
            return $http.get(__env.apiUrl + 'annotationsources/');
        };

        Rounds.one = function (id) {
            return $http.get(base_url + id + '/');
        };

        Rounds.players = function (id) {
            return $http.get(base_url + id + '/players/');
        };

        Rounds.player_states = function(id){
            return $http.get(base_url + id + '/player_states/');
        };

        Rounds.statuses = function(id, time_point){
            return $http.get(base_url + id + '/statuses_at_time/', {
                params: {
                time_point: time_point}
            });
        };

        Rounds.hero_at_time = function (id, player_id, time_point) {
            return $http.get(base_url + id + '/hero_at_time/', {
                params: {player_id: player_id,
                time_point: time_point}
            });
        };

        Rounds.killfeed_at_time = function (id, time_point) {
            return $http.get(base_url + id + '/killfeed_at_time/', {
                params: {time_point: time_point}
            });
        };

        Rounds.alive_at_time = function (id, player_id, time_point) {
            return $http.get(base_url + id + '/alive_at_time/', {
                params: {player_id: player_id,
                time_point: time_point}
            });
        };

        Rounds.getAllRoundEvents = function(id, type_identifier){
            return $http.get(base_url + id + '/'+ type_identifier +'/');
        };

        Rounds.addRoundEvent = function (newEvent, type_identifier){
            return $http.post(__env.apiUrl + type_identifier +'/', newEvent);
        };

        Rounds.updateRoundEvent = function(id, updatedEvent, type_identifier){
            return $http.put(__env.apiUrl + type_identifier +'/' + id + "/", updatedEvent);
        };

        Rounds.deleteRoundEvent = function (id, type_identifier) {
            return $http.delete(__env.apiUrl + type_identifier +'/' + id + "/")
        };

        Rounds.update = function (updatedRound) {
            return $http.put(base_url + updatedRound.id  + '/', updatedRound);
        };

        Rounds.delete = function (id) {
            return $http.delete(base_url + id + '/');
        };

        Rounds.addOne = function (newRound) {
            return $http.post(base_url, newRound)
        };

        Rounds.downloadOne = function(id){
            return $http.post(base_url + id + '/download/', {})
        };

        Rounds.exportOne = function(id){
            return $http.post(base_url + id + '/export/', {})
        };

        return Rounds;
    });