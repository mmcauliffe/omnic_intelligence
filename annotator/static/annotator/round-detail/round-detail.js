angular.module('roundDetail', [
    'annotator.rounds',
    'annotator.games',
    'annotator.npcs',
    'annotator.heroes',
    'annotator.teams'
])

    .filter('secondsToDateTime', [function () {
        return function (seconds) {
            return new Date(1970, 0, 1).setSeconds(seconds, Math.round(seconds % 1 * 1000));
        };
    }])
    .controller('RoundDetailCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams, $rootScope, Streams) {
        $scope.events = {};
        $scope.initializing = {};
        $scope.newEvents = {};
        $scope.roundLock = true;
        $scope.lockButtonText = 'Unlock from round';
        $scope.eventTypes = ['switches', 'deaths', 'npc_deaths', 'kills', 'kill_npcs', 'revives', 'ult_gains', 'ult_uses',
            'pauses', 'unpauses', 'replay_starts', 'replay_ends', 'smaller_window_starts', 'smaller_window_ends',
            'point_gains', 'point_flips', 'overtime_starts', 'overtime_ends'];
        $scope.left_player_statuses = [];
        $scope.right_player_statuses = [];
        $scope.player_ready = false;
        $scope.currentTime = 0.0;

        Heroes.all().then(function (res) {
            $scope.heroes = res.data;
            $scope.available_heroes = $scope.heroes;
        });
        NPCs.all().then(function (res) {
            $scope.NPCs = res.data;
        });
        Teams.sides().then(function (res) {
            $scope.sides = res.data;
        });
        Rounds.annotation_sources().then(function (res){
            $scope.annotation_choices = res.data;
        });

        // Functions

        $scope.toggleLock = function(){
            if ($scope.roundLock){
                $scope.roundLock = false;
                $scope.lockButtonText = 'Lock to round';

            }
            else {
                $scope.roundLock = true;
                $scope.lockButtonText = 'Unlock from round';
            }
        };

        $scope.addEvent = function(type){
            $scope.newEvents[type].round = $scope.round.id;
            $scope.newEvents[type].time_point = $scope.currentTime;
            Rounds.addRoundEvent($scope.newEvents[type], type).then(function (res){
                $scope.updateList(type);
                $scope.updateStatuses();
            });

        };

        $scope.deleteEvent = function (id, type) {
            Rounds.deleteRoundEvent(id, type);
            // update the list in ui
            $scope.events[type] = $scope.events[type].filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.updateEvent = function (id, e, type) {
            if (e.initial){
                e.initial = false;
            }
            else {
            if ($scope.initializing[type]){
                return
            }
            if (e.id == undefined){
                return
            }
            e.time_point = $scope.currentTime;
            Rounds.updateRoundEvent(id, e, type).then(function(res){
                $scope.updateStatuses();

            });

            }
        };

        $scope.updateList = function(type){
            $scope.initializing[type] = true;
            Rounds.getAllRoundEvents($stateParams.round_id, type).then(function (res) {
                $scope.events[type] = res.data;
                $scope.initializing[type] = false;
            });

        };

        $scope.updateStatuses = function () {
            Rounds.player_states($scope.round.id).then(function(res) {
                $scope.player_states = res.data;
                    $scope.updateStatusesAtTime()
            });

        };
        $scope.updateStatusesAtTime = function(){
            var time = $scope.currentTime;
            var hero_states, ult_states, alive_states;
            for (i=0; i< 6; i ++){
                hero_states = $scope.player_states.left[i].hero;
                for (j=0; j< hero_states.length; j ++){
                    if (hero_states[j].begin <= time && time < hero_states[j].end){
                        $scope.left_player_statuses[i].hero = hero_states[j].hero;
                        break
                    }
                }
                hero_states = $scope.player_states.right[i].hero;
                for (j=0; j< hero_states.length; j ++){
                    if (hero_states[j].begin <= time && time < hero_states[j].end){
                        $scope.right_player_statuses[i].hero = hero_states[j].hero;
                        break
                    }
                }

                $scope.left_player_statuses[i].has_ult = false;
                $scope.right_player_statuses[i].has_ult = false;
                ult_states = $scope.player_states.left[i].ult;
                for (j=0; j< ult_states.length; j ++){
                    if (ult_states[j].begin <= time && time < ult_states[j].end){
                        if (ult_states[j].status === 'has_ult'){
                            $scope.left_player_statuses[i].has_ult = true;
                        }
                        break
                    }
                }
                ult_states = $scope.player_states.right[i].ult;
                for (j=0; j< ult_states.length; j ++){
                    if (ult_states[j].begin <= time && time < ult_states[j].end){
                        if (ult_states[j].status === 'has_ult'){
                            $scope.right_player_statuses[i].has_ult = true;
                        }
                        break
                    }
                }
                $scope.left_player_statuses[i].alive = false;
                $scope.right_player_statuses[i].alive = false;
                alive_states = $scope.player_states.left[i].alive;
                for (j=0; j< alive_states.length; j ++){
                    if (alive_states[j].begin <= time && time < alive_states[j].end){
                        if (alive_states[j].status === 'alive'){
                            $scope.left_player_statuses[i].alive = true;
                        }
                        break
                    }
                }
                alive_states = $scope.player_states.right[i].alive;
                for (j=0; j< alive_states.length; j ++){
                    if (alive_states[j].begin <= time && time < alive_states[j].end){
                        if (alive_states[j].status === 'alive'){
                            $scope.right_player_statuses[i].alive = true;
                        }
                        break
                    }
                }
            }
        };

        Rounds.one($stateParams.round_id).then(function (res) {
            $scope.round = res.data;
            Streams.vods($scope.round.game.match.event.channel).then(function(res){
                $scope.vods = res.data;
            });
            $scope.vod_type = $scope.round.stream_vod.vod_link[0];
            $scope.vod_link = $scope.round.stream_vod.vod_link[1];
            $scope.updateStatuses();


        });
        for (i = 0; i < 6; i++) {
            $scope.left_player_statuses.push({});
            $scope.right_player_statuses.push({});
        }
        for (i=0; i < $scope.eventTypes.length; i++){
            $scope.updateList($scope.eventTypes[i]);
            $scope.newEvents[$scope.eventTypes[i]] = {}
        }

        $scope.inCurrentSecond = function (time) {
            return Math.abs(time - $scope.currentTime) <= 1
        };

        $scope.seekTo = function (time) {
            $rootScope.$broadcast('SEEK', time);
        };


        $scope.heroAtTime = function (player_id, time_point) {
            var hero = '';
            for (i = 0; i < $scope.events.switches.length; i++) {
                if ($scope.events.switches[i].player.id == player_id) {
                    if ($scope.events.switches[i].time_point > time_point) {
                        break;
                    }
                    hero = $scope.events.switches[i].new_hero;
                }
            }
            return hero
        };

        $scope.updateAvailableHeroes = function () {
            $scope.used_heroes = [];
            angular.forEach($scope.players, function (p) {
                $scope.used_heroes.push($scope.heroAtTime(p.id, $scope.newSwitch.time_point));
            });
            $scope.available_heroes = $scope.heroes.filter(function (h) {
                return $scope.used_heroes.indexOf(h.id) == -1;
            });
        };

        $scope.killfeed = [];
        $scope.round_function = function (value, decimals) {
            return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
        };
        $scope.getCurrentPlayerTime = function () {
            var current_time = 0;
            if ($scope.player_ready) {
                if ($scope.vod_type === 'twitch') {
                    current_time = $scope.round_function($scope.twitch_player.getCurrentTime(), 1);
                }
                else if ($scope.vod_type === 'youtube') {
                    current_time = $scope.round_function($scope.youtube_player.getCurrentTime(), 1);
                }
            }
            else {
                return $scope.round.begin;
            }
            return current_time
        };

        $scope.getCurrentRoundTime = function () {
            return $scope.round_function($scope.getCurrentPlayerTime() - $scope.round.begin, 1)
        };

        $scope.addUltUsePlayer = function (player) {
            $scope.newEvents.ult_uses.player = player.id;
            $scope.addEvent('ult_uses');

        };

        $scope.addUltGainPlayer = function (player) {
            $scope.newEvents.ult_gains.player = player.id;
            $scope.addEvent('ult_gains');


        };
        Rounds.players($stateParams.round_id).then(function (res) {
            $scope.left_players = res.data.left_team;
            $scope.right_players = res.data.right_team;
            $scope.all_players = $scope.left_players.concat($scope.right_players);
            $scope.reviver_players = $scope.all_players;
        });

        $scope.saveRound = function () {
            Rounds.update($scope.round).then(function(res){
                $scope.currentTime = $scope.getCurrentRoundTime();
                for (i=0; i < $scope.eventTypes.length; i++){
                    $scope.updateList($scope.eventTypes[i]);
                }
            });
        };

        $scope.initTwitchPlayer = function () {
            $scope.twitch_player = new Twitch.Player("twitch-embed", {
                width: 1280,
                height: 760,
                video: $scope.vod_link,
                autoplay: false,
                time: $scope.round.begin
            });
            $scope.twitch_player.addEventListener(Twitch.Embed.VIDEO_READY, $scope.onPlayerReady)
        };
        $scope.onPlayerReady = function () {
            $scope.player_ready = true;
        };
        $scope.initYoutubePlayer = function () {
            $scope.youtube_player = new YT.Player('youtube-embed', {
                height: '760',
                width: '1280',
                videoId: $scope.vod_link,
                playerVars: {
                    start: $scope.round.begin
                },
                events: {
                    'onReady': $scope.onPlayerReady
                }
            });
        };

        $scope.updateBegin = function () {
            var duration = $scope.round.end - $scope.round.begin;
            if ($scope.vod_type === 'twitch') {
                $scope.round.begin = $scope.twitch_player.getCurrentTime();
            }
            else if ($scope.vod_type === 'youtube') {
                $scope.round.begin = $scope.youtube_player.getCurrentTime();
            }
        };

        $scope.updateEnd = function () {
            if ($scope.vod_type === 'twitch') {
                $scope.round.end = $scope.twitch_player.getCurrentTime();
            }
            else if ($scope.vod_type === 'youtube') {
                $scope.round.end = $scope.youtube_player.getCurrentTime();
            }
        };

        $scope.$on('SEEK', function (e, response) {
            if ($scope.vod_type === 'twitch') {
                $scope.twitch_player.seek(response);
            }
            else if ($scope.vod_type === 'youtube') {
                $scope.youtube_player.seekTo(response);
            }
            $rootScope.$broadcast('TIME_UPDATED', response);
        });


        $scope.$on('STATES_UPDATED', function (e, response) {
            $scope.updateStatuses();
        });

        $scope.$on('TIME_UPDATED', function (e, response) {
                if (response > $scope.round.end) {
                    $scope.currentTime = $scope.round.end - $scope.round.begin;
                }
                else if (response > $scope.round.begin) {
            $scope.currentTime = response - $scope.round.begin;
                }
                else {
                    $scope.currentTime = 0;
                }
            $scope.currentTime = $scope.round_function($scope.currentTime, 1);
            $scope.updateStatusesAtTime($scope.currentTime);
            Rounds.killfeed_at_time($scope.round.id, $scope.currentTime).then(function (res) {
                $scope.killfeed = res.data;
            });
        });
        $scope.updateTimes = function () {
            var cur_time;
            if ($scope.vod_type === 'twitch') {
                cur_time = $scope.twitch_player.getCurrentTime();
            }
            else if ($scope.vod_type === 'youtube') {
                cur_time = $scope.youtube_player.getCurrentTime();
            }
            var time = 0;
            if (cur_time > $scope.round.end) {
                time = $scope.round.end - $scope.round.begin;
            }
            else if (cur_time > $scope.round.begin) {
                time = cur_time - $scope.round.begin
            }
            $rootScope.$broadcast('TIME_UPDATED', time);
        };

        $scope.seekForward = function (amount) {
            var new_time;
            if ($scope.vod_type === 'twitch') {
                new_time = $scope.twitch_player.getCurrentTime() + amount;
            }
            else if ($scope.vod_type === 'youtube') {
                new_time = $scope.youtube_player.getCurrentTime() + amount;
            }

            if ($scope.roundLock && new_time > $scope.round.end) {
                return
            }
            if ($scope.vod_type === 'twitch') {
                $scope.twitch_player.seek(new_time);
            }
            else if ($scope.vod_type === 'youtube') {
                $scope.youtube_player.seekTo(new_time);
            }
            $rootScope.$broadcast('TIME_UPDATED', new_time);
        };

        $scope.seekBackward = function (amount) {
            var new_time;
            if ($scope.vod_type === 'twitch') {
                new_time = $scope.twitch_player.getCurrentTime() - amount;
            }
            else if ($scope.vod_type === 'youtube') {
                new_time = $scope.youtube_player.getCurrentTime() - amount;
            }
            if ($scope.roundLock && new_time < $scope.round.begin) {
                return
            }
                if ($scope.vod_type === 'twitch') {
                    $scope.twitch_player.seek(new_time);
                }
                else if ($scope.vod_type === 'youtube') {
                    $scope.youtube_player.seekTo(new_time);
                }
                $rootScope.$broadcast('TIME_UPDATED', new_time);
        };


        // Kills



        $scope.kill_assist_settings = {displayProp: 'name'};
        $scope.damaging_abilities = [];
        $scope.killnpc_damaging_abilities = [];
        $scope.updateKillProperties = function () {
            var player_id = $scope.newEvents.kills.killing_player;
            var is_left_team = false;
            for (i = 0; i < $scope.left_players.length; i++) {
                if ($scope.left_players[i].id == player_id) {
                    is_left_team = true;
                    break
                }
            }
            if (is_left_team) {
                $scope.killable_players = $scope.right_players;
            }
            else {
                $scope.killable_players = $scope.left_players;
            }
            Rounds.hero_at_time($scope.round.id, player_id, $scope.currentTime).then(function (res) {
                var hero = res.data;
                if (hero == '' || hero == null) {
                    $scope.damaging_abilities = [];
                }
                else {
                    Heroes.damaging_abilities(hero.id).then(function (res) {
                        $scope.damaging_abilities = res.data;
                    });
                }
            });

        };
        $scope.updateHeadshotability = function () {
            var ability_id = $scope.newEvents.kills.ability;
            $scope.headshotable = false;
            for (i = 0; i < $scope.damaging_abilities.length; i++) {
                if ($scope.damaging_abilities[i].id == ability_id) {
                    $scope.headshotable = $scope.damaging_abilities[i].headshot_capable;
                    break
                }
            }
            if (!$scope.headshotable) {
                $scope.newKill.headshot = false;
            }
        };

        $scope.updateKillNPCproperties = function () {
            var player_id = $scope.newEvents.kill_npcs.killing_player;
            Rounds.hero_at_time($scope.round.id, player_id, $scope.currentTime).then(function (res) {
                var hero = res.data;
                if (hero == '' || hero == null) {
                    $scope.killnpc_damaging_abilities = [];
                }
                else {
                    Heroes.damaging_abilities(hero.id).then(function (res) {
                        $scope.killnpc_damaging_abilities = res.data;
                    });
                }
            });
        };

        // Revives

        $scope.updateReviveProperties = function () {
            var player_id = $scope.newEvents.revives.reviving_player;
            var is_left_team = false;
            for (i = 0; i < $scope.left_players.length; i++) {
                if ($scope.left_players[i].id == player_id) {
                    is_left_team = true;
                    break
                }
            }
            if (is_left_team) {
                $scope.revivable_players = $scope.left_players;
            }
            else {
                $scope.revivable_players = $scope.right_players;
            }
            $scope.revivable_players = $scope.revivable_players.filter(function (p) {
                return p.id != player_id;
            });

            Rounds.hero_at_time($scope.round.id, player_id, $scope.currentTime).then(function (res) {
                var hero = res.data;
                if (hero == '' || hero == null) {
                    $scope.reviving_abilities = [];
                }
                else {
                    Heroes.reviving_abilities(hero.id).then(function (res) {
                        $scope.reviving_abilities = res.data;
                    });
                }
            });

        };
    });

