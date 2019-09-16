<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">
            <v-select v-model="newEvent.player" :items="allPlayers"
                      item-text="name" item-value="id" label="Player">

            </v-select>
            <v-select v-model="newEvent.status" :items="status_effect_choices"
                      item-text="name" item-value="id" label="Status">

            </v-select>
            <v-btn class='primary raised' v-on:click="addEvent">Add status effect</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="status_effects" v-if="status_effects" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td>
                    {{props.item.player}}
                </td>
                <td>
                    {{props.item.status}}
                </td>
                <td>

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateEventStart(props.item)">access_time
                        </v-icon>
                        <span>Update start time to current</span>
                    </v-tooltip>

                </td>
                <td class="clickable" v-on:click="seekTo(props.item.start_time)"
                    v-bind:class="{ active: closeToCurrent(props.item.start_time) }">
                    {{ props.item.start_time | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateEventEnd(props.item)">access_time
                        </v-icon>
                        <span>Update end time to current</span>
                    </v-tooltip>

                </td>
                <td class="clickable" v-on:click="seekTo(props.item.end_time)"
                    v-bind:class="{ active: closeToCurrent(props.item.end_time) }">
                    {{ props.item.end_time | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td v-if="can_edit">

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="deleteEvent(props.item.id)">
                            remove_circle
                        </v-icon>
                        <span>Remove</span>
                    </v-tooltip>
                </td>
            </template>
        </v-data-table>
    </div>
</template>

<script>

    import {mapState, mapActions, mapGetters} from 'vuex'

    import interval_events from './BaseIntervalEvents';
    import VSelect from "vuetify/es5/components/VSelect/VSelect";

    export default {
        components: {VSelect},
        name: "status_effects",
        extends: interval_events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'status_effects',
                rowsPerPage: [15]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'status_effects',
                'allPlayers',
            ]),
            ...mapGetters('overwatch', [
                'status_effect_choices',
                ]),
            headers(){
                return [
                {text: 'Player', sortable: false},
                {text: 'Status', sortable: false},
                {text: '', sortable: false},
                {text: 'Start time', sortable: false},
                {text: '', sortable: false},
                {text: 'End time', sortable: false},
                {text: 'Actions', sortable: false}]
            }
        },
        methods: {
            addEvent() {
                this.newEvent.start_time = this.currentTime;
                this.newEvent.end_time = this.currentTime;
                this.newEvent.round = this.$store.state.rounds.one.item.id;
                console.log(this.newEvent)
                this.addRoundEvent({type: this.event_type, event: this.newEvent});
            },
            eventChangeHandler(newNewEvent) {
                console.log(newNewEvent)
            },
            timeChangeHandler(new_timestamp) {
                console.log(this.currentTime);
            },

        },
    }
</script>
