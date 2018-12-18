<template>
    <div class='row text-center'>
    <div class="col-sm-3"></div>
    <div class='col-sm-6'>
        <em v-if="event.loading">Loading event...</em>
        <span v-if="event.error" class="text-danger">ERROR: {{event.error}}</span>
        <div v-if="event.item">

        <h1>{{ event.item.name }}</h1>


            <v-select :items="spectator_modes.items" label="Spectator mode" v-model="event.item.spectator_mode" item-text="name" item-value="id">

            </v-select>
            <v-select :items="streams.items" label="Stream" v-model="event.item.channel" item-text="name" item-value="id">

            </v-select>

        <v-btn class='success' v-on:click="saveEvent">Save</v-btn>

        <h1>All Matches</h1>
        <em v-if="matches.loading">Loading matches...</em>
        <span v-if="matches.error" class="text-danger">ERROR: {{matches.error}}</span>

        <v-expansion-panel v-if="matches.items">
            <v-expansion-panel-content v-for="match in matches.items" :key="match.id">

                <div slot="header"><router-link :to="{name: 'match-detail', params: {id: match.id}}">{{ match.teams[0] }} vs {{ match.teams[1] }}</router-link> <span v-if="match.date">({{match.date}})</span></div>
                <span v-if="match.deleting"><em> - Deleting...</em></span>
                <span v-else-if="match.deleteError" class="text-danger"> - ERROR: {{match.deleteError}}</span>
                <span v-else> - <a @click="deleteMatch(match.id)" class="text-danger">Delete</a></span>
            </v-expansion-panel-content>
        </v-expansion-panel>
        </div>
    </div>
    <div class="col-sm-3"></div>
</div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import VSelect from "vuetify/es5/components/VSelect/VSelect";
    export default {
        components: {VSelect},
        name: "event-detail-page",
    computed: {
        ...mapState({
            account: state => state.account,
            spectator_modes: state => state.vods.spectator_modes,
            streams: state => state.vods.stream_channels,
            event: state => state.events.one,
            matches: state => state.events.matches
        })
    },
    created () {
        this.getOneEvent(this.$route.params.id);
        this.getMatches(this.$route.params.id);
        this.getSpectatorModes();
        this.getStreamChannels();
    },
    methods: {
        ...mapActions('events', {
            getOneEvent: 'getOne',
            getMatches: 'getOneMatches',
            deleteEvent: 'delete'
        }),
        ...mapActions('vods', {
            getStreamChannels: 'getStreamChannels',
            getSpectatorModes: 'getSpectatorModes',
        }),
        saveEvent (){

        }
    }
    }
</script>

<style scoped>

</style>