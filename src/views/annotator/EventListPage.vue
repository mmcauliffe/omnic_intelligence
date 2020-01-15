<template>
    <div>
        <vue-headful :title="title" />
        <em v-if="events.loading">Loading events...</em>
        <span v-if="events.error" class="text-danger">ERROR: {{events.error}}</span>
        <v-expansion-panel v-if="events.items">
            <v-expansion-panel-content v-for="event in events.items" :key="event.id">

                <div slot="header">
                    <router-link :to="{name: 'event-detail', params: {id: event.id}}">{{event.name}}</router-link>
                    <span v-if="event.start_date">({{event.start_date}} to {{event.end_date}})</span></div>
                {{event}}
                <span v-if="event.deleting"><em> - Deleting...</em></span>
                <span v-else-if="event.deleteError" class="text-danger"> - ERROR: {{event.deleteError}}</span>
                <span v-else> - <a @click="deleteEvent(event.id)" class="text-danger">Delete</a></span>
            </v-expansion-panel-content>
        </v-expansion-panel>
    </div>

</template>

<script>
    import {mapState, mapActions} from 'vuex'

    export default {
        name: "event-list-page",
        data() {
            return {
                title: 'Events | Omnic Intelligence'
            }
        },
        computed: {
            ...mapState({
                account: state => state.account,
                events: state => state.events.all
            })
        },
        created() {
            this.getAllEvents();
        },
        methods: {
            ...mapActions('events', {
                getAllEvents: 'getAll',
                deleteEvent: 'delete'
            })
        }
    }
</script>

<style scoped>

</style>