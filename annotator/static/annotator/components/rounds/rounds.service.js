angular.module('annotator.rounds')
    .service('Rounds', function ($http, BASE_URL) {
        var base_url = BASE_URL + 'rounds/';
        var Rounds = {};

        Rounds.all = function () {
            return $http.get(base_url);
        };

        Rounds.one = function (id) {
            return $http.get(base_url + id + '/');
        };

        Rounds.players = function (id) {
            return $http.get(base_url + id + '/players/');
        };

        Rounds.switches = function (id) {
            return $http.get(base_url + id + '/switches/');
        };

        Rounds.hero_at_time = function (id, player_id, time_point) {
            return $http.get(base_url + id + '/hero_at_time/', {
                params: {player_id: player_id,
                time_point: time_point}
            });
        };

        Rounds.ult_at_time = function (id, player_id, time_point) {
            return $http.get(base_url + id + '/ult_at_time/', {
                params: {player_id: player_id,
                time_point: time_point}
            });
        };

        Rounds.addSwitch = function (newSwitch) {
            return $http.post(BASE_URL + 'switches/', newSwitch);
        };

        Rounds.deleteSwitch = function (id) {
            return $http.delete(BASE_URL + 'switches/' + id + "/")
        };

        Rounds.deaths = function (id) {
            return $http.get(base_url + id + '/deaths/');
        };

        Rounds.addDeath = function (newDeath) {
            return $http.post(BASE_URL + 'deaths/', newDeath);
        };

        Rounds.deleteDeath = function (id) {
            return $http.delete(BASE_URL + 'deaths/' + id + "/")
        };

        Rounds.npcdeaths = function (id) {
            return $http.get(base_url + id + '/npcdeaths/');
        };

        Rounds.addNPCDeath = function (newNPCDeath) {
            return $http.post(BASE_URL + 'npcdeaths/', newNPCDeath);
        };

        Rounds.deleteNPCDeath = function (id) {
            return $http.delete(BASE_URL + 'npcdeaths/' + id + "/")
        };

        Rounds.kills = function (id) {
            return $http.get(base_url + id + '/kills/');
        };

        Rounds.addKill = function (newKill) {
            return $http.post(BASE_URL + 'kills/', newKill);
        };

        Rounds.deleteKill = function (id) {
            return $http.delete(BASE_URL + 'kills/' + id + "/")
        };

        Rounds.killnpcs = function (id) {
            return $http.get(base_url + id + '/killnpcs/');
        };

        Rounds.addKillNPC = function (newKillNPC) {
            return $http.post(BASE_URL + 'killnpcs/', newKillNPC);
        };

        Rounds.deleteKillNPC = function (id) {
            return $http.delete(BASE_URL + 'killnpcs/' + id + "/")
        };

        Rounds.revives = function (id) {
            return $http.get(base_url + id + '/revives/');
        };

        Rounds.addRevive = function (newRevive) {
            return $http.post(BASE_URL + 'revives/', newRevive);
        };

        Rounds.deleteRevive = function (id) {
            return $http.delete(BASE_URL + 'revives/' + id + "/")
        };

        Rounds.ultuses = function (id) {
            return $http.get(base_url + id + '/ultuses/');
        };

        Rounds.addUltUse = function (newUltUse) {
            return $http.post(BASE_URL + 'ultuses/', newUltUse);
        };

        Rounds.deleteUltUse = function (id) {
            return $http.delete(BASE_URL + 'ultuses/' + id + "/")
        };

        Rounds.ultgains = function (id) {
            return $http.get(base_url + id + '/ultgains/');
        };

        Rounds.addUltGain = function (newUltGain) {
            return $http.post(BASE_URL + 'ultgains/', newUltGain);
        };

        Rounds.deleteUltGain = function (id) {
            return $http.delete(BASE_URL + 'ultgains/' + id + "/")
        };

        Rounds.pauses = function (id) {
            return $http.get(base_url + id + '/pauses/');
        };

        Rounds.addPause = function (newPause) {
            return $http.post(BASE_URL + 'pauses/', newPause);
        };

        Rounds.deletePause = function (id) {
            return $http.delete(BASE_URL + 'pauses/' + id + "/")
        };

        Rounds.unpauses = function (id) {
            return $http.get(base_url + id + '/unpauses/');
        };

        Rounds.addUnpause = function (newUnpause) {
            return $http.post(BASE_URL + 'unpauses/', newUnpause);
        };

        Rounds.deleteUnpause = function (id) {
            return $http.delete(BASE_URL + 'unpauses/' + id + "/")
        };

        Rounds.replaystarts = function (id) {
            return $http.get(base_url + id + '/replaystarts/');
        };

        Rounds.addReplayStart = function (newReplayStart) {
            return $http.post(BASE_URL + 'replaystarts/', newReplayStart);
        };

        Rounds.deleteReplayStart = function (id) {
            return $http.delete(BASE_URL + 'replaystarts/' + id + "/")
        };

        Rounds.replayends = function (id) {
            return $http.get(base_url + id + '/replayends/');
        };

        Rounds.addReplayEnd = function (newReplayEnd) {
            return $http.post(BASE_URL + 'replayends/', newReplayEnd);
        };

        Rounds.deleteReplayEnd = function (id) {
            return $http.delete(BASE_URL + 'replayends/' + id + "/")
        };

        Rounds.pointgains = function (id) {
            return $http.get(base_url + id + '/pointgains/');
        };

        Rounds.addPointGain = function (newPointGain) {
            return $http.post(BASE_URL + 'pointgains/', newPointGain);
        };

        Rounds.deletePointGain = function (id) {
            return $http.delete(BASE_URL + 'pointgains/' + id + "/")
        };

        Rounds.pointflips = function (id) {
            return $http.get(base_url + id + '/pointflips/');
        };

        Rounds.addPointFlip = function (newPointFlip) {
            return $http.post(BASE_URL + 'pointflips/', newPointFlip);
        };

        Rounds.deletePointFlip = function (id) {
            return $http.delete(BASE_URL + 'pointflips/' + id + "/")
        };

        Rounds.overtimestarts = function (id) {
            return $http.get(base_url + id + '/overtimestarts/');
        };

        Rounds.addOvertimeStart = function (newOvertimeStart) {
            return $http.post(BASE_URL + 'overtimestarts/', newOvertimeStart);
        };

        Rounds.deleteOvertimeStart = function (id) {
            return $http.delete(BASE_URL + 'overtimestarts/' + id + "/")
        };


        Rounds.update = function (updatedRound) {
            return $http.put(base_url + updatedRound.id, updatedRound);
        };

        Rounds.delete = function (id) {
            return $http.delete(base_url + id + '/');
        };

        Rounds.addOne = function (newRound) {
            return $http.post(base_url, newRound)
        };

        return Rounds;
    });