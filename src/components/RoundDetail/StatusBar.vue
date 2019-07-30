<template>
    <v-layout row class="status">
        <div class="offset"></div>
        <div class="team">
            <div v-for="status in left_player_statuses" class="left player">
                <v-layout row>
                <div v-if="status.ult_state==='has_ult'">
                    <v-tooltip bottom>
                        <v-icon slot="activator" @click="addUltUsePlayer(status.id)"
                                :disabled="!can_edit">check_circle
                        </v-icon>
                        <span>Use ult</span></v-tooltip>

                </div>
                <div v-else-if="status.ult_state==='no_ult'">
                    <v-tooltip bottom>
                        <v-icon slot="activator" @click="addUltGainPlayer(status.id)"
                                :disabled="!can_edit">check_circle_outline
                        </v-icon>
                        <span>Gain ult</span></v-tooltip>
                </div>
                <div v-else-if="status.ult_state==='using_ult'">
                    <v-tooltip bottom>
                        <v-icon slot="activator" @click="addUltEndPlayer(status.id)"
                                :disabled="!can_edit">new_releases
                        </v-icon>
                        <span>Using ult</span></v-tooltip>
                </div>
                    <v-tooltip bottom v-if="status.hero.name">
                        <img class="hero-icon" slot="activator" :src="require('../../assets/'+ make_safe(status.hero.name) +'.png')"/>

                        <span>{{ status.hero.name}}</span>
                    </v-tooltip>

                </v-layout>
                <span>{{ status.name}}</span><br>
                <v-layout row>
                    <v-icon v-if="!status.alive">person_outline</v-icon>
                    <v-icon v-else-if="status.frozen">ac_unit</v-icon>
                    <v-icon v-else-if="status.asleep">notifications_paused</v-icon>
                    <v-icon v-else-if="status.stunned">star_rate</v-icon>
                    <v-icon v-else>person</v-icon>
                    <v-icon v-if="status.antiheal">block</v-icon>
                </v-layout>
            </div>
        </div>
        <div class="mid">
            <v-layout column>
                <span>{{  currentTime |secondsToMoment | moment('mm:ss.S')}}</span>
                <span>{{round_state}}</span>
                <span v-if="isOvertime">Overtime</span>
                <span v-if="isPaused">Paused</span>

            </v-layout>
        </div>
        <div class="team">
            <div v-for="status in right_player_statuses" class="right-player player">

                <v-layout row>
                <div v-if="status.ult_state==='has_ult'">
                    <v-tooltip bottom>
                        <v-icon slot="activator" @click="addUltUsePlayer(status.id)"
                                :disabled="!can_edit">check_circle
                        </v-icon>
                        <span>Use ult</span></v-tooltip>

                </div>
                <div v-else-if="status.ult_state==='no_ult'">
                    <v-tooltip bottom>
                        <v-icon slot="activator" @click="addUltGainPlayer(status.id)"
                                :disabled="!can_edit">check_circle_outline
                        </v-icon>
                        <span>Gain ult</span></v-tooltip>
                </div>
                <div v-else-if="status.ult_state==='using_ult'">
                    <v-tooltip bottom>
                        <v-icon slot="activator"
                                :disabled="!can_edit">new_releases
                        </v-icon>
                        <span>Using ult</span></v-tooltip>
                </div>
                    <v-tooltip bottom v-if="status.hero.name">
                        <img class="hero-icon" slot="activator" :src="require('../../assets/'+ make_safe(status.hero.name) +'.png')"/>

                        <span>{{ status.hero.name}}</span>
                    </v-tooltip>

                </v-layout>
                <span>{{ status.name}}</span><br>
                <div>
                    <v-icon v-if="!status.alive">person_outline</v-icon>
                    <v-icon v-else-if="status.alive && status.frozen">ac_unit</v-icon>
                    <v-icon v-else-if="status.alive && status.asleep">notifications_paused</v-icon>
                    <v-icon v-else-if="status.alive && status.stunned">star_rate</v-icon>
                    <v-icon v-else-if="status.alive && !status.frozen">person</v-icon>
                    <v-icon v-if="status.alive && status.antiheal">block</v-icon>
                </div>
            </div>
        </div>

    </v-layout>
</template>

<script>
    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import VImg from "vuetify/es5/components/VImg/VImg";
    import {mapState, mapActions, mapGetters} from 'vuex'

    export default {
        name: "status-bar",
        components: {
            VBtn,
            VIcon,
            VTooltip,
            VImg
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
            ...mapGetters('rounds', [
                'leftPlayers',
                'rightPlayers',
                'playerOnLeftTeam',
                'heroAtTime',
                'hasUltAtTime',
                'ultStateAtTime',
                'pausedAtTime',
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
                        frozen: this.stateAtTime(player.id, this.currentTime, 'frozen'),
                        stunned: this.stateAtTime(player.id, this.currentTime, 'stunned'),
                        asleep: this.stateAtTime(player.id, this.currentTime, 'asleep'),
                        antiheal: this.stateAtTime(player.id, this.currentTime, 'antiheal'),
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
                        frozen: this.stateAtTime(player.id, this.currentTime, 'frozen'),
                        stunned: this.stateAtTime(player.id, this.currentTime, 'stunned'),
                        asleep: this.stateAtTime(player.id, this.currentTime, 'asleep'),
                        antiheal: this.stateAtTime(player.id, this.currentTime, 'antiheal'),
                    })
                });
                return statuses
            }
        },
        methods: {
            ...mapActions('rounds', {
                addRoundEvent: 'addRoundEvent'
            }),
            addUltUsePlayer(player_id) {
                let newEvent = {};
                newEvent.time_point = this.currentTime;
                newEvent.round = this.$store.state.rounds.one.item.id;
                newEvent.player = player_id;
                this.addRoundEvent({type: 'ult_uses', event: newEvent});

            },
            addUltGainPlayer(player_id) {

                let newEvent = {};
                newEvent.time_point = this.currentTime;
                newEvent.round = this.$store.state.rounds.one.item.id;
                newEvent.player = player_id;
                this.addRoundEvent({type: 'ult_gains', event: newEvent});
            },
            addUltEndPlayer(player_id) {

                let newEvent = {};
                newEvent.time_point = this.currentTime;
                newEvent.round = this.$store.state.rounds.one.item.id;
                newEvent.player = player_id;
                this.addRoundEvent({type: 'ult_ends', event: newEvent});
            },
            make_safe(name){
                if (name !== undefined){
                return name.replace(':', '')
                }
                return ''
            },
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