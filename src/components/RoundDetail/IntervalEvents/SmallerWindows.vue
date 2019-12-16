<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">

            <v-btn class='primary raised' v-on:click="addEvent">Add smaller window</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="smaller_windows" v-if="smaller_windows" :rows-per-page-items="rowsPerPage">

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

    import {mapGetters} from 'vuex'

    const interval_events = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['./BaseIntervalEvents'], () => {
            resolve(require('./BaseIntervalEvents'))
        })
    };

    export default {
        name: "smaller_windows",
        extends: interval_events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'smaller_windows',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'smaller_windows',
            ]),
        },
        methods: {
            eventChangeHandler(newNewEvent) {
                //console.log(newNewEvent)
            },
            timeChangeHandler(new_timestamp) {
                //console.log(this.currentTime);
            },

        },
    }
</script>
