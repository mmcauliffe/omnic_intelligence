<template>
    <v-layout row class="status">
        <div class="offset"></div>
        <div class="team">
            <div v-for="status in left_player_statuses" class="left player">
            <StatusPortrait :status="status">
            </StatusPortrait>

            </div>
        </div>
        <div class="mid">
            <v-layout column>
                <span>{{  currentTime |secondsToMoment | moment('mm:ss.S')}}</span>
                <span>{{round_state}}</span>
                <span v-if="isOvertime">Overtime</span>
                <span v-if="isPaused">Paused</span>
                <span v-if="isReplay">Replay</span>

            </v-layout>
        </div>
        <div class="team">
            <div v-for="status in right_player_statuses" class="right-player player">
                <StatusPortrait :status="status"></StatusPortrait>
            </div>
        </div>

    </v-layout>
</template>

<script>
    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VImg from "vuetify/es5/components/VImg/VImg";
    import VLayout from "vuetify/es5/components/VGrid/VLayout";
    import StatusPortrait from "./StatusPortrait";
    import {mapState, mapActions, mapGetters} from 'vuex'

    export default {
        name: "status-bar",
        components: {
            VBtn,
            VImg,
            VLayout,
            StatusPortrait
        },
        computed: {
            ...mapState({
                player_states: state => state.rounds.player_states,
                round_states: state => state.rounds.round_states,
                timestamp: state => state.vods.timestamp,
                round: state => state.rounds.one.item,
            }),
            can_edit() {
                return true;
            },
            isOvertime(){
               return this.overtimeAtTime(this.currentTime)
            },
            round_state(){
               return this.roundStateAtTime(this.currentTime)
            },
            isPaused(){
                return this.pausedAtTime(this.currentTime)
            },
            isReplay(){
                return this.replayAtTime(this.currentTime)
            },
            ...mapGetters('rounds', [
                'leftPlayers',
                'rightPlayers',
                'playerOnLeftTeam',
                'heroAtTime',
                'hasUltAtTime',
                'ultStateAtTime',
                'pausedAtTime',
                'replayAtTime',
                'overtimeAtTime',
                'roundStateAtTime',
                'aliveAtTime',
                'stateAtTime',
                'allPlayers'
            ]),
            currentTime() {
                return  Math.round((this.timestamp - this.round.begin) * 10) / 10;
            },
            left_player_statuses() {
                let statuses = [];
                this.leftPlayers.forEach(player => {
                    statuses.push({
                        id: player.id,
                        name: player.name,
                        hero: this.heroAtTime(player.id, this.currentTime),
                        ult_state: this.ultStateAtTime(player.id, this.currentTime),
                        alive: this.aliveAtTime(player.id, this.currentTime),
                        status: this.stateAtTime(player.id, this.currentTime, 'status'),
                        antiheal: this.stateAtTime(player.id, this.currentTime, 'antiheal'),
                        immortal: this.stateAtTime(player.id, this.currentTime, 'immortal'),
                        nanoboosted: this.stateAtTime(player.id, this.currentTime, 'nanoboosted'),
                    })
                });
                return statuses
            },
            right_player_statuses() {
                let statuses = [];
                this.rightPlayers.forEach(player => {
                    statuses.push({
                        id: player.id,
                        name: player.name,
                        hero: this.heroAtTime(player.id, this.currentTime),
                        ult_state: this.ultStateAtTime(player.id, this.currentTime),
                        alive: this.aliveAtTime(player.id, this.currentTime),
                        status: this.stateAtTime(player.id, this.currentTime, 'status'),
                        antiheal: this.stateAtTime(player.id, this.currentTime, 'antiheal'),
                        immortal: this.stateAtTime(player.id, this.currentTime, 'immortal'),
                        nanoboosted: this.stateAtTime(player.id, this.currentTime, 'nanoboosted'),
                    })
                });
                return statuses
            }
        }
    }
</script>

<style scoped>


    .status {
        width: 1280px;
        height: 80px;
    }

    .team {
        display: table-cell;
    }

    .player {
        display: table-cell;
        height: 80px;
        width: 67px;
        padding-left: 10px;
        padding-right: 10px;
    }

    .offset {
        width: 60px;
    }

    .left {
    }

    .right-player {
        float: left;
    }

    .v-btn {
        min-width: 0;
        min-height: 0;
    }

    .mid {
        width: 392px;
        text-align: center;
    }
    .hero-icon{
        height: 35px;
    }

</style>