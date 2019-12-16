<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit && sides">
            <v-select v-model="newEvent.side" :items="sides"
                      item-text="name" item-value="id" label="Sides">

            </v-select>

            <v-btn class='primary raised' v-on:click="addEvent">Add bar zoom</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="zooms" v-if="zooms" :rows-per-page-items="rowsPerPage">

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
                  <span v-if=" props.item.side ==='L'">Left</span>
<span v-if="props.item.side ==='R'">Right</span>
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
    const VSelect = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VSelect/VSelect'], () => {
            resolve(require('vuetify/es5/components/VSelect/VSelect'))
        })
    };

    export default {
        name: "zooms",
        extends: interval_events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'zooms',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'zooms',
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
