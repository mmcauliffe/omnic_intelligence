<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">

            <v-btn class='primary raised' v-on:click="addEvent">Add replay</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="replays" v-if="replays" :rows-per-page-items="rowsPerPage">

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
                <td>
                <v-select v-if="replay_types" v-model="props.item.type" :items="replay_types"
                                              item-text="name" item-value="id"
                 v-on:change="updateEvent(props.item)" clearable></v-select>
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
        name: "replays",
        extends: interval_events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'replays',
                rowsPerPage: [5]
            }
        },
        created(){

            this.getReplayTypes();
        },
        computed: {
            ...mapState({
                replay_types: state => state.overwatch.replay_types.items,
            }),
            ...mapGetters('rounds', [
                'replays',
            ]),
            headers(){
                return [
                {text: '', sortable: false},
                {text: 'Start time', sortable: false},
                {text: '', sortable: false},
                {text: 'End time', sortable: false},
                {text: 'Type', sortable: false},
                {text: 'Actions', sortable: false}]
            }
        },
        methods: {
            ...mapActions('overwatch', [
                'getReplayTypes',
            ]),
            eventChangeHandler(newNewEvent) {
                console.log(newNewEvent)
            },
            timeChangeHandler(new_timestamp) {
                console.log(this.currentTime);
            },

        },
    }
</script>
