<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">

            <v-btn class='primary raised' v-on:click="addEvent">Add pause</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="pauses" v-if="pauses" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
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

    export default {
        name: "pauses",
        extends: interval_events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'pauses',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'pauses',
            ]),
        },
        methods: {

            addEvent() {
                this.newEvent.start_time = this.currentTime;
                this.newEvent.round = this.$store.state.rounds.one.item.id;
                console.log(this.newEvent)
                this.addRoundEvent({type: this.event_type, event: this.newEvent}).then(
                    function (res) {
                        this.newEvent = {};
                    });
            },
            updateEventStart(event) {
                event.start_time = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
            },
            updateEventEnd(event) {
                event.end_time = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
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
