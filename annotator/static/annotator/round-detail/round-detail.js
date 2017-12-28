angular.module('roundDetail', [
    'annotator.rounds',
    'annotator.games',
    'annotator.npcs',
    'annotator.heroes',
    'annotator.teams'
])

    .filter('secondsToDateTime', [function () {
        return function (seconds) {
            return new Date(1970, 0, 1).setSeconds(seconds);
        };
    }])
    .controller('SwitchCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams) {
        Heroes.all().then(function (res) {
            $scope.heroes = res.data;
            $scope.available_heroes = $scope.heroes;
        });
        $scope.newSwitch = {};
        $scope.$on('TIME_UPDATED', function (e, response) {
            $scope.newSwitch.time_point = response;
        });
        $scope.updateSwitchList = function () {
            Rounds.switches($stateParams.round_id).then(function (res) {
                $scope.switches = res.data;
            });
        };

        $scope.updateSwitchList();

        $scope.deleteSwitch = function (id) {
            Rounds.deleteSwitch(id);
            // update the list in ui
            $scope.switches = $scope.switches.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addSwitch = function () {
            $scope.newSwitch.round = $scope.round.id;
            Rounds.addSwitch($scope.newSwitch).then($scope.updateSwitchList);
            $scope.newSwitch = {};
            $scope.updateTimes();
        };

        $scope.heroAtTime = function (player_id, time_point) {
            var hero = '';
            for (i = 0; i < $scope.switches.length; i++) {
                if ($scope.switches[i].player.id == player_id) {
                    if ($scope.switches[i].time_point > time_point) {
                        break;
                    }
                    hero = $scope.switches[i].new_hero;
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

    })
    .controller('DeathCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams) {

        $scope.newDeath = {};
        $scope.newNPCDeath = {};
        $scope.$on('TIME_UPDATED', function (e, response) {
            $scope.newDeath.time_point = response;
            $scope.newNPCDeath.time_point = response;
        });
        $scope.$on('KILL_UPDATED', function (e, response) {
            console.log('hello!');
            $scope.updateDeathList();
        });
        $scope.$on('NPCKILL_UPDATED', function (e, response) {
            $scope.updateNPCDeathList();
        });

        NPCs.all().then(function (res) {
            $scope.NPCs = res.data;
        });
        $scope.updateDeathList = function () {
            Rounds.deaths($stateParams.round_id).then(function (res) {
                $scope.deaths = res.data;
            });
        };

        $scope.updateDeathList();


        $scope.deleteDeath = function (id) {
            Rounds.deleteDeath(id);
            // update the list in ui
            $scope.deaths = $scope.deaths.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addDeath = function () {
            $scope.newDeath.round = $scope.round.id;
            Rounds.addDeath($scope.newDeath).then($scope.updateDeathList);
            $scope.newDeath = {};
            $scope.updateTimes();
        };


        $scope.updateNPCDeathList = function () {
            Rounds.npcdeaths($stateParams.round_id).then(function (res) {
                $scope.npcdeaths = res.data;
            });
        };

        $scope.updateNPCDeathList();


        $scope.deleteNPCDeath = function (id) {
            Rounds.deleteNPCDeath(id);
            // update the list in ui
            $scope.npcdeaths = $scope.npcdeaths.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addNPCDeath = function () {
            $scope.newNPCDeath.round = $scope.round.id;
            Rounds.addNPCDeath($scope.newNPCDeath).then($scope.updateNPCDeathList);
            $scope.newNPCDeath = {};
            $scope.updateTimes();
        };
    })
    .controller('KillCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams, $rootScope) {
        $scope.newKill = {};
        $scope.newKillNPC = {};
        $scope.damaging_abilities = [];
        $scope.killnpc_damaging_abilities = [];
        $scope.$on('TIME_UPDATED', function (e, response) {
            $scope.newKill.time_point = response;
            $scope.newKillNPC.time_point = response;
        });

        NPCs.all().then(function (res) {
            $scope.NPCs = res.data;
        });
        $scope.updateKillList = function () {
            Rounds.kills($stateParams.round_id).then(function (res) {
                $scope.kills = res.data;
            });
        };

        $scope.updateKillList();


        $scope.deleteKill = function (id) {
            Rounds.deleteKill(id);
            // update the list in ui
            $scope.kills = $scope.kills.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addKill = function () {
            $scope.newKill.round = $scope.round.id;
            Rounds.addKill($scope.newKill).then($scope.updateKillList);
            $scope.newKill = {};
            $scope.updateTimes();
            $rootScope.$broadcast('KILL_UPDATED', '');
        };


        $scope.updateKillNPCList = function () {
            Rounds.killnpcs($stateParams.round_id).then(function (res) {
                $scope.killnpcs = res.data;
            });
        };

        $scope.updateKillNPCList();


        $scope.deleteKillNPC = function (id) {
            Rounds.deleteKillNPC(id);
            // update the list in ui
            $scope.killnpcs = $scope.killnpcs.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addKillNPC = function () {
            $scope.newKillNPC.round = $scope.round.id;
            Rounds.addKillNPC($scope.newKillNPC).then($scope.updateKillNPCList);
            $scope.newKillNPC = {};
            $scope.updateTimes();
            $rootScope.$broadcast('NPCKILL_UPDATED', '');
        };

        $scope.updateKillProperties = function () {
            var player_id = $scope.newKill.killing_player;
            console.log(player_id);
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
            Rounds.hero_at_time($scope.round.id, player_id, $scope.newKill.time_point).then(function (res) {
                var hero = res.data;
                console.log(hero);
                console.log(player_id);
                if (hero == '' || hero == null) {
                    $scope.damaging_abilities = [];
                }
                else {
                    Heroes.damaging_abilities(hero.id).then(function (res) {
                        $scope.damaging_abilities = res.data;
                        console.log($scope.damaging_abilities);
                    });
                }
            });

        };
        $scope.updateHeadshotability = function () {
            var ability_id = $scope.newKill.ability;
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
            var player_id = $scope.newKillNPC.killing_player;
            Rounds.hero_at_time($scope.round.id, player_id, $scope.newKillNPC.time_point).then(function (res) {
                var hero = res.data;
                console.log(hero);
                console.log(player_id);
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

    })
    .controller('ReviveCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams) {
        $scope.newRevive = {};
        $scope.$on('TIME_UPDATED', function (e, response) {
            $scope.newRevive.time_point = response;
        });

        $scope.updateReviveList = function () {
            Rounds.revives($stateParams.round_id).then(function (res) {
                $scope.revives = res.data;
            });
        };

        $scope.updateReviveList();


        $scope.deleteRevive = function (id) {
            Rounds.deleteRevive(id);
            // update the list in ui
            $scope.revives = $scope.revives.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addRevive = function () {
            $scope.newRevive.round = $scope.round.id;
            Rounds.addRevive($scope.newRevive).then($scope.updateReviveList);
            $scope.newRevive = {};
            $scope.updateTimes();
        };

        $scope.updateReviveProperties = function () {
            var player_id = $scope.newRevive.reviving_player;
            console.log(player_id);
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

            Rounds.hero_at_time($scope.round.id, player_id, $scope.newRevive.time_point).then(function (res) {
                var hero = res.data;
                console.log(hero);
                console.log(player_id);
                if (hero == '' || hero == null) {
                    $scope.reviving_abilities = [];
                }
                else {
                    Heroes.reviving_abilities(hero.id).then(function (res) {
                        $scope.reviving_abilities = res.data;
                        console.log($scope.damaging_abilities);
                    });
                }
            });

        };
    })
    .controller('UltCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams) {
        $scope.newUltGain = {};
        $scope.newUltUse = {};
        $scope.$on('TIME_UPDATED', function (e, response) {
            $scope.newUltGain.time_point = response;
            $scope.newUltUse.time_point = response;
            $scope.updateUltGainProperties();
            $scope.updateUltUseProperties();
        });


        $scope.updateUltUseList = function () {
            Rounds.ultuses($stateParams.round_id).then(function (res) {
                $scope.ultuses = res.data;
            });
        };

        $scope.updateUltUseList();


        $scope.deleteUltUse = function (id) {
            Rounds.deleteUltUse(id);
            // update the list in ui
            $scope.ultuses = $scope.ultuses.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addUltUse = function () {
            $scope.newUltUse.round = $scope.round.id;
            Rounds.addUltUse($scope.newUltUse).then($scope.updateUltUseList);
            $scope.newUltUse = {};
            $scope.ultUseAddable = false;
            $scope.updateTimes();
        };


        $scope.updateUltGainList = function () {
            Rounds.ultgains($stateParams.round_id).then(function (res) {
                $scope.ultgains = res.data;
            });
        };

        $scope.updateUltGainList();


        $scope.deleteUltGain = function (id) {
            Rounds.deleteUltGain(id);
            // update the list in ui
            $scope.ultgains = $scope.ultgains.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addUltGain = function () {
            $scope.newUltGain.round = $scope.round.id;
            Rounds.addUltGain($scope.newUltGain).then($scope.updateUltGainList);
            $scope.newUltGain = {};
            $scope.ultGainAddable = false;
        };

        $scope.updateUltGainProperties = function () {
            Rounds.ult_at_time($scope.round.id, $scope.newUltUse.player, $scope.newUltUse.time_point).then(function (res) {
                $scope.ultGainAddable = !res.data;
            });
        };
        $scope.updateUltUseProperties = function () {
            Rounds.ult_at_time($scope.round.id, $scope.newUltUse.player, $scope.newUltUse.time_point).then(function (res) {
                $scope.ultUseAddable = res.data;
            });
        };
    })
    .controller('PauseCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams) {
        $scope.newPause = {};
        $scope.newUnpause = {};
        $scope.newReplayStart = {};
        $scope.newReplayEnd = {};
        $scope.$on('TIME_UPDATED', function (e, response) {
            $scope.newPause.time_point = response;
            $scope.newUnpause.time_point = response;
            $scope.newReplayStart.time_point = response;
            $scope.newReplayEnd.time_point = response;
            $scope.updatePauseProperties();
            $scope.updateReplayProperties();
        });

        $scope.updatePauseProperties = function () {
            $scope.isPaused = false;
            var last_pause = -1;
            for (i = 0; i < $scope.pauses.length; i++) {
                if ($scope.pauses[i].time_point > $scope.newPause.time_point) {
                    break
                }
                last_pause = $scope.pauses[i].time_point
            }
            if (last_pause >= 0) {
                var last_unpause = -1;
                for (i = 0; i < $scope.unpauses.length; i++) {
                    if ($scope.unpauses[i].time_point > $scope.newPause.time_point) {
                        break
                    }
                    last_unpause = $scope.unpauses[i].time_point
                }
                if (last_pause > last_unpause) {
                    $scope.isPaused = true;
                }
            }
            console.log($scope.isPaused);
        };

        $scope.updateReplayProperties = function () {
            $scope.isReplay = false;
            var last_start = -1;
            for (i = 0; i < $scope.replaystarts.length; i++) {
                if ($scope.replaystarts[i].time_point > $scope.newReplayStart.time_point) {
                    break
                }
                last_start = $scope.replaystarts[i].time_point
            }
            if (last_start >= 0) {
                var last_end = -1;
                for (i = 0; i < $scope.replayends.length; i++) {
                    if ($scope.replayends[i].time_point > $scope.newReplayStart.time_point) {
                        break
                    }
                    last_end = $scope.replayends[i].time_point
                }
                if (last_start > last_end) {
                    $scope.isReplay = true;
                }
            }
            console.log($scope.isReplay);
        };

        $scope.updatePauseList = function () {
            Rounds.pauses($stateParams.round_id).then(function (res) {
                $scope.pauses = res.data;
            });
        };

        $scope.updatePauseList();


        $scope.deletePause = function (id) {
            Rounds.deletePause(id);
            // update the list in ui
            $scope.pauses = $scope.pauses.filter(function (event) {
                return event.id !== id;
            });
            $scope.updatePauseProperties();
        };

        $scope.addPause = function () {
            $scope.newPause.round = $scope.round.id;
            Rounds.addPause($scope.newPause).then($scope.updatePauseList);
            $scope.updatePauseProperties();
        };


        $scope.updateUnpauseList = function () {

            Rounds.unpauses($stateParams.round_id).then(function (res) {
                $scope.unpauses = res.data;
            });
        };

        $scope.updateUnpauseList();

        $scope.deleteUnpause = function (id) {
            Rounds.deleteUnpause(id);
            // update the list in ui
            $scope.unpauses = $scope.unpauses.filter(function (event) {
                return event.id !== id;
            });
            $scope.updatePauseProperties();
        };

        $scope.addUnpause = function () {
            $scope.newUnpause.round = $scope.round.id;
            Rounds.addUnpause($scope.newUnpause).then($scope.updateUnpauseList);
            $scope.updatePauseProperties();
        };

        $scope.updateReplayStartList = function () {
            Rounds.replaystarts($stateParams.round_id).then(function (res) {
                $scope.replaystarts = res.data;
                $scope.updateReplayProperties();
            });
        };

        $scope.updateReplayStartList();


        $scope.deleteReplayStart = function (id) {
            Rounds.deleteReplayStart(id);
            // update the list in ui
            $scope.replaystarts = $scope.replaystarts.filter(function (event) {
                return event.id !== id;
            });
            $scope.updateReplayProperties();
        };

        $scope.addReplayStart = function () {
            $scope.newReplayStart.round = $scope.round.id;
            Rounds.addReplayStart($scope.newReplayStart).then($scope.updateReplayStartList);
        };

        $scope.updateReplayEndList = function () {
            Rounds.replayends($stateParams.round_id).then(function (res) {
                $scope.replayends = res.data;
                $scope.updateReplayProperties();
            });
        };

        $scope.updateReplayEndList();


        $scope.deleteReplayEnd = function (id) {
            Rounds.deleteReplayEnd(id);
            // update the list in ui
            $scope.replayends = $scope.replayends.filter(function (event) {
                return event.id !== id;
            });
            $scope.updateReplayProperties();
        };

        $scope.addReplayEnd = function () {
            $scope.newReplayEnd.round = $scope.round.id;
            Rounds.addReplayEnd($scope.newReplayEnd).then($scope.updateReplayEndList);
        };


    })
    .controller('PointCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams) {
        $scope.newPointFlip = {};
        $scope.newPointGain = {};
        $scope.newOvertimeStart = {};
        $scope.$on('TIME_UPDATED', function (e, response) {
            $scope.newPointFlip.time_point = response;
            $scope.newPointGain.time_point = response;
            $scope.newOvertimeStart.time_point = response;
        });


        $scope.updateOvertimeStartList = function () {
            Rounds.overtimestarts($stateParams.round_id).then(function (res) {
                $scope.overtimestarts = res.data;
                $scope.overtimeAddable = ($scope.overtimestarts.length == 0);
                console.log($scope.overtimeAddable);
            });
        };

        $scope.updateOvertimeStartList();

        $scope.deleteOvertimeStart = function (id) {
            Rounds.deleteOvertimeStart(id);
            // update the list in ui
            $scope.overtimestarts = $scope.overtimestarts.filter(function (event) {
                return event.id !== id;
            });
            $scope.overtimeAddable = true;
        };

        $scope.addOvertimeStart = function () {
            $scope.newOvertimeStart.round = $scope.round.id;
            Rounds.addOvertimeStart($scope.newOvertimeStart).then($scope.updateOvertimeStartList);
            $scope.overtimeAddable = false;
        };


        $scope.updatePointGainList = function () {
            Rounds.pointgains($stateParams.round_id).then(function (res) {
                $scope.pointgains = res.data;
            });
        };

        $scope.updatePointGainList();

        $scope.deletePointGain = function (id) {
            Rounds.deletePointGain(id);
            // update the list in ui
            $scope.pointgains = $scope.pointgains.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addPointGain = function () {
            $scope.newPointGain.round = $scope.round.id;
            Rounds.addPointGain($scope.newPointGain).then($scope.updatePointGainList);
        };

        $scope.updatePointFlipList = function () {
            Rounds.pointflips($stateParams.round_id).then(function (res) {
                $scope.pointflips = res.data;
            });
        };

        $scope.updatePointFlipList();

        $scope.deletePointFlip = function (id) {
            Rounds.deletePointFlip(id);
            // update the list in ui
            $scope.pointflips = $scope.pointflips.filter(function (event) {
                return event.id !== id;
            })
        };

        $scope.addPointFlip = function () {
            $scope.newPointFlip.round = $scope.round.id;
            Rounds.addPointFlip($scope.newPointFlip).then($scope.updatePointFlipList);
        };
    })
    .controller('RoundDetailCtrl', function ($scope, Rounds, Games, NPCs, Heroes, Teams, $state, $stateParams, $rootScope) {

        Teams.sides().then(function (res) {
            $scope.sides = res.data;
        });

        Rounds.one($stateParams.round_id).then(function (res) {
            $scope.round = res.data;
            $scope.vod_type = $scope.round.vod_link[0];
            $scope.vod_link = $scope.round.vod_link[1];

        });

        Rounds.players($stateParams.round_id).then(function (res) {
            $scope.left_players = res.data.left_team;
            $scope.right_players = res.data.right_team;
            $scope.all_players = $scope.left_players.concat($scope.right_players);
            $scope.reviver_players = $scope.all_players;
        });

        $scope.initPlayer = function () {
            $scope.twitch_player = new Twitch.Player("twitch-embed", {
                width: 1280,
                height: 760,
                video: $scope.vod_link,
                autoplay: false,
                time: $scope.round.begin
            });
            $scope.updateTimes();
        };

        $scope.updateTimes = function () {
            var cur_time = Math.round($scope.twitch_player.getCurrentTime());
            var time = 0;
            if (cur_time > $scope.round.end) {
                time = $scope.round.end - $scope.round.begin;
            }
            else if (cur_time > $scope.round.begin) {
                time = cur_time - $scope.round.begin
            }
            $rootScope.$broadcast('TIME_UPDATED', time);
        };

        $scope.seekForward = function () {
            var new_time = Math.round($scope.twitch_player.getCurrentTime()) + 1;
            console.log(new_time);
            console.log($scope.round.end);
            if (new_time <= $scope.round.end) {
                $scope.twitch_player.seek(new_time);
            }
            $scope.updateTimes();
        };

        $scope.seekBackward = function () {
            var new_time = Math.round($scope.twitch_player.getCurrentTime()) - 1;
            if (new_time >= $scope.round.begin) {
                $scope.twitch_player.seek(new_time);
            }
            $scope.updateTimes();
        };

    });

