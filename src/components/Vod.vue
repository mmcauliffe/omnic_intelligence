<template>
    <div id="vod-container">
        <div v-if="vod_type=='null'"></div>
        <TwitchPlayer v-if="vod_type=='twitch'" :video="id" :timestamp="timestamp"></TwitchPlayer>
        <div id="youtube-embed" v-else-if="vod_type == 'youtube'"></div>
        <div id="player-controls" class="text-center controls-container">

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
                    <v-icon v-if="roundLock">lock_open</v-icon>
                    <v-icon v-if="!roundLock">lock</v-icon>
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
        </div>

    </div>
</template>

<script>
    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import TwitchPlayer from './TwitchPlayer';
    import {mapState, mapActions, mapGetters} from 'vuex';

    export default {
        props: {
            vod_type: {type: String},
            id: {type: String},
            round_begin: {type: Number},
            round_end: {type: Number}
        },
        name: "Vod",
        components: {
            VBtn,
            VIcon,
            VTooltip,
            TwitchPlayer
        },
        data: function(){
            return {roundLock: true}
        },
        computed: {
            ...mapState({
                timestamp: state => state.vods.timestamp,
            }),
        },
        created() {
        },
        methods: {
            ...mapActions('vods', {
                updateTimestamp: 'updateTimestamp',
            }),
            seekBackward(time) {
                let new_timestamp = this.timestamp - time;
                if (this.roundLock && this.round_begin && new_timestamp < this.round_begin) {
                    new_timestamp = this.round_begin;
                }
                this.updateTimestamp(new_timestamp);
            },
            seekForward(time) {
                let new_timestamp = this.timestamp + time;
                if (this.roundLock && this.round_end && new_timestamp > this.round_end) {
                    new_timestamp = this.round_end;
                }
                console.log(new_timestamp);
                this.updateTimestamp(new_timestamp);
            }
        }
    }
</script>

<style scoped>
    #vod-container {
        width: 1280px;
    }
</style>