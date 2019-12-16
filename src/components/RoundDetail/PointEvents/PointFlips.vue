<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">
            <v-select v-model="newEvent.controlling_side" :items="sides"
                      item-text="name" item-value="id" label="Controlling side">

            </v-select>

            <v-btn class='primary raised' v-on:click="addEvent">Add point flip</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="point_flips" v-if="point_flips" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>
                    <span v-if="props.item.controlling_side ==='L'">Left</span>
                    <span v-if="props.item.controlling_side ==='R'">Right</span>
                </td>
                <td v-if="can_edit">

        <v-layout layout="row" layout-align="space-between">
                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateEvent(props.item)">access_time
                        </v-icon>
                        <span>Update time to current</span>
                    </v-tooltip>
            <v-flex></v-flex>
                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="deleteEvent(props.item.id)">
                            remove_circle
                        </v-icon>
                        <span>Remove</span>
                    </v-tooltip>
        </v-layout>
                </td>
            </template>
        </v-data-table>
    </div>
</template>

<script>

    import {mapGetters} from 'vuex'

    const events = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['./BaseRoundEvents'], () => {
            resolve(require('./BaseRoundEvents'))
        })
    };

    export default {
        name: "point_flips",
        extends: events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'point_flips',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'point_flips',
            ]),
            headers() {
                return [
                    {text: 'Time', sortable: false, width: "5px"},
                    {text: 'Controlling side', sortable: false},
                    {text: 'Actions', sortable: false, width: "130px"}]
            }
        },
        methods: {

            eventChangeHandler(newNewEvent) {
                console.log(newNewEvent)
            },
            timeChangeHandler(new_timestamp) {
                console.log(this.currentTime);
            },

        },
    }
</script>
