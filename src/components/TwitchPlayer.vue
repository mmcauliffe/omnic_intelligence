<template>
    <div ref="player"></div>
</template>

<script>
    import Vue from 'vue';
    import LoadScript from 'vue-plugin-load-script';
    import {mapState, mapActions, mapGetters} from 'vuex';

    Vue.use(LoadScript);
    let player;

    export default {
        name: "twitch-player",
        props: {
            video: String,
            controls: Boolean
        },
        computed: {
            ...mapState({
                timestamp: state => state.vods.timestamp,
            }),
        },
        beforeCreate() {
            this.width=1280;
            this.height=720;
            this.playsInLine = false;
            Vue.loadScript('https://player.twitch.tv/js/embed/v1.js')
                .then(() => {
                    let options = {
                        width: this.width,
                        height: this.height,
                        autoplay: false,
                        time: this.timestamp,
                    };
                    options.controls = this.controls;
                    if (this.playsInline) {
                        options.playsinline = true;
                    }
                    if (this.video) {
                        options.video = this.video;
                    } else {
                        this.$emit('error', 'no source specified');
                    }
                    player = new window.Twitch.Player(this.$refs.player, options);
                    player.addEventListener('ended', () => (this.$emit('ended')));
                    player.addEventListener('pause', () => (this.$emit('pause')));
                    player.addEventListener('play', () => (this.$emit('play')));
                    player.addEventListener('offline', () => (this.$emit('offline')));
                    player.addEventListener('online', () => (this.$emit('online')));
                    player.addEventListener('ready', () => {
                        player.seek(this.timestamp);
                        console.log('READY', this.timestamp, this.getCurrentTime())
                        this.$emit('ready');
                        player.setQuality('720p60');
                        console.log('QUALITIES', player.getQualities(), player.getQuality());
                    });
                }).catch((e) => (this.$emit('error', e)));
        },
        methods: {
            play() { // Begins playing the specified video.
                player.play();
            },
            pause() { // Pauses the player.
                player.pause();
            },
            seek(timestamp) { // Seeks to the specified timestamp (in seconds) in the video and resumes playing if paused. Does not work for live streams.
                player.seek(timestamp);
            },
            getCurrentTime() { // Returns the current video’s timestamp, in seconds. Works only for VODs, not live streams.
                return player.getCurrentTime();
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
                        player.setQuality('720p60');
                console.log('hello', timestamp, this.getCurrentTime())
                this.seek(timestamp);
            },
        },
    };
</script>

<style scoped>

</style>