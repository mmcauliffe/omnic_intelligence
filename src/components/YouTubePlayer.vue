<template>
    <div id="player"></div>
</template>

<script>
    import Vue from 'vue';
    import LoadScript from 'vue-plugin-load-script';
    import {mapState, mapActions, mapGetters} from 'vuex';

    Vue.use(LoadScript);
    let player, initial=true;

    export default {
        name: "youtube-player",
        props: {
            video: String,
            controls: Boolean
        },
        computed: {
            ...mapState({
                timestamp: state => state.vods.timestamp,
                duration: state => state.vods.duration,
            }),
        },
        beforeCreate() {
            this.width = 1280;
            this.height = 720;

            Vue.loadScript('https://www.youtube.com/iframe_api')
                .then(() => {
                    console.log('helloooooo', this.video)
                    player = new window.YT.Player('player', {
                        height: this.height,
                        width: this.width,
                        videoId: this.video,
                        playerVars: {
                            autoplay: 0,
                            controls: 0,
                            rel: 0,
                            modestbranding: 1
                        },
                        events: {
                            'onReady': () => {
                                this.seek(this.timestamp)
                                console.log('READY', this.timestamp, this.getCurrentTime())
                                //player.setPlaybackQuality('hd720');
                                //player.pauseVideo();
                                this.$emit('ready');
                            },
                            'onStateChange': e => {
                                if (initial && e.data === 1){
                                    player.pauseVideo();
                                    initial = false;
                                    this.seek(this.timestamp);
                                    this.updateDuration(this.getDuration());
                                }
                            }
                        }
                    });
                    console.log(player)
                }).catch((e) => (this.$emit('error', e)));
        },
        beforeDestroy: function () {

    player.stopVideo();
    player.destroy();
},
        methods: {
            ...mapActions('vods', {
                updateDuration: 'updateDuration',
            }),
            play() { // Begins playing the specified video.
                player.play();
            },
            pause() { // Pauses the player.
                player.pauseVideo();
            },
            seek(timestamp) { // Seeks to the specified timestamp (in seconds) in the video and resumes playing if paused. Does not work for live streams.
                player.seekTo(timestamp);
                if (player.getPlayerState() == 1){
                    this.pause()
                }
            },
            getCurrentTime() { // Returns the current video’s timestamp, in seconds. Works only for VODs, not live streams.
                return !player.getCurrentTime ? 0.0 : player.getCurrentTime();
            },
            getDuration() { // Returns the duration of the video, in seconds. Works only for VODs,not live streams.
                return player.getDuration();
            },
            getPlaybackStats() { // Returns an object with statistics the embedded video player and the current live stream or VOD.
                return player.getPlaybackStats();
            },
            getQuality() { // Returns the current quality of video playback.
                return player.getQuality();
            },
            isPaused() { // Returns true if the video is paused; otherwise, false. Buffering or seeking is considered playing.
                return player.isPaused();
            },
            hasEnded() { // Returns true if the live stream or VOD has ended; otherwise, false.
                return player.getEnded();
            },
            getVolume() { // Returns the volume level, a value between 0.0 and 1.0.
                return player.getVolume();
            },
            isMuted() { // Returns true if the player is muted; otherwise, false.
                return player.getMuted();
            },
            mute() { // Mutes the player.
                player.setMuted(true);
            },
            unmute() { // Unmutes the player.
                player.setMuted(false);
            },
        },
        watch: {
            video(newVideo) {
                player.setVideo(newVideo);
            },
            timestamp(timestamp) {
                console.log('hello', timestamp, this.getCurrentTime())
                this.seek(timestamp);
            },
        },
    }
</script>

<style scoped>

</style>