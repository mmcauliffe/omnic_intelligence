<template>
    <div id="vod-container">

        <div v-if="vod_type=='null'"></div>
        <TwitchPlayer v-if="vod_type=='twitch'" :video="id" :timestamp="timestamp" :controls="controls"></TwitchPlayer>
        <YouTubePlayer v-if="vod_type=='youtube'" :video="id" :timestamp="timestamp" :controls="controls"></YouTubePlayer>
        <div id="player-controls" class="text-center controls-container">
            <v-layout row v-if="duration">
            <v-slider
              v-model="timestamp"
              min="0"
              step="0.1"
              :max="duration"
        thumb-size="64"
          thumb-label>
        <template
          slot="thumb-label"
          slot-scope="props">
          <span>
            {{ props.value|secondsToMoment | moment('HH:mm:ss.S') }}
          </span>
        </template>
            </v-slider>
            <v-flex>
                {{timestamp | secondsToMoment| moment('HH:mm:ss.S')}} / {{duration | secondsToMoment| moment('HH:mm:ss.S')}}
            </v-flex>
            </v-layout>
            <v-layout row justify-center>

            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="seekBackward(60)">
                    <v-icon>fast_rewind</v-icon>
                </v-btn>
                <span>Go back 60 seconds</span>
            </v-tooltip>
            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="seekBackward(5)">
                    <v-icon>arrow_back_ios</v-icon>
                </v-btn>
                <span>Go back 5 seconds</span>
            </v-tooltip>

            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="seekBackward(1)">
                    <v-icon>chevron_left</v-icon>
                </v-btn>
                <span>Go back 1 seconds</span>
            </v-tooltip>

            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="seekBackward(0.1)">
                    <v-icon>arrow_left</v-icon>
                </v-btn>
                <span>Go back 0.1 seconds</span>
            </v-tooltip>

            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="roundLock = !roundLock">
                    <v-icon v-if="!roundLock">lock_open</v-icon>
                    <v-icon v-if="roundLock">lock</v-icon>
                </v-btn>
                <span v-if="roundLock">Unlock seeking to round</span>
                <span v-if="!roundLock">Lock seeking to round</span>
            </v-tooltip>

            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="seekForward(0.1)">
                    <v-icon>arrow_right</v-icon>
                </v-btn>
                <span>Go forward 0.1 seconds</span>
            </v-tooltip>

            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="seekForward(1)">
                    <v-icon>chevron_right</v-icon>
                </v-btn>
                <span>Go forward 1 seconds</span>
            </v-tooltip>
            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="seekForward(5)">
                    <v-icon>arrow_forward_ios</v-icon>
                </v-btn>
                <span>Go forward 5 seconds</span>
            </v-tooltip>
            <v-tooltip bottom>
                <v-btn slot="activator" v-on:click="seekForward(60)">
                    <v-icon>fast_forward</v-icon>
                </v-btn>
                <span>Go forward 60 seconds</span>
            </v-tooltip>
            </v-layout>
        </div>

    </div>
</template>

<script>
    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import TwitchPlayer from './TwitchPlayer';
    import YouTubePlayer from './YouTubePlayer';
    import {mapState, mapActions, mapGetters} from 'vuex';

    export default {
        props: {
            vod_type: {type: String},
            id: {type: String},
            round_begin: {type: Number},
            round_end: {type: Number},
            controls: Boolean
        },
        name: "Vod",
        components: {
            VBtn,
            VIcon,
            VTooltip,
            TwitchPlayer,
            YouTubePlayer
        },
        data: function () {
            if (!this.round_begin) {
                return {roundLock: false}
            }
            else {
                return {roundLock: true}
            }
        },
        computed: {
            ...mapState({
                duration: state => state.vods.duration,
                vod_state: state => state.vods
            }),
            timestamp: {
                get: function () {
                    return this.vod_state.timestamp
                },
                set: function (value) {
                    this.updateTimestamp(value)
                }
            }
        },
        destroyed() {
            window.removeEventListener('keypress', this.doCommand);
        },
          created() {
            window.addEventListener('keypress', this.doCommand);
        },
        methods: {
            ...mapActions('vods', {
                updateTimestamp: 'updateTimestamp',
            }),
            seekBackward(time) {
                console.log('SEEKBACKWARD', this.timestamp, time)
                let new_timestamp = this.timestamp - time;
                new_timestamp = Math.round(new_timestamp * 10) / 10;
                if (this.roundLock && this.round_begin && new_timestamp < this.round_begin) {
                    new_timestamp = this.round_begin;
                }
                this.timestamp = new_timestamp;
            },
            seekForward(time) {
                console.log('SEEKFORWARD', this.timestamp, time)
                let new_timestamp = this.timestamp + time;
                new_timestamp = Math.round(new_timestamp * 10) / 10;
                if (this.roundLock && this.round_end && new_timestamp > this.round_end) {
                    new_timestamp = this.round_end;
                }
                this.timestamp = new_timestamp;
            },
            doCommand(e){
                if (e.key === 'w') {
                this.seekForward(1);
              }
              else if (e.key === 's') {
                this.seekBackward(1);
              }
              else if (e.key === 'a') {
                this.seekBackward(0.1);
              }
              else if (e.key === 'd') {
                this.seekForward(0.1);
              }
              else if (e.key === 'ArrowRight') {
                this.seekForward(30);
              }
              else if (e.key === 'ArrowLeft') {
                this.seekBackward(30);
              }
              else if (e.key === 'ArrowUp') {
                this.seekForward(60);
              }
              else if (e.key === 'ArrowDown') {
                this.seekBackward(60);
              }
            }
        }
    }
</script>

<style scoped>
    #vod-container {
        width: 1280px;
    }
</style>