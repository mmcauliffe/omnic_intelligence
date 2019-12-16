<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">
            <v-text-field v-model="newEvent.point_total" label="Point total"></v-text-field>

            <v-btn class='primary raised' v-on:click="addEvent">Add point gain</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="point_gains" v-if="point_gains" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>{{ props.item.point_total }}</td>
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

    import {mapState, mapActions, mapGetters} from 'vuex'

    import events from './BaseRoundEvents';
    import VTextField from "vuetify/es5/components/VTextField/VTextField";

    export default {
        components: {VTextField},
        name: "point_gains",
        extends: events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'point_gains',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'point_gains',
            ]),
            headers(){
                return [
                {text: 'Time', sortable: false, width: "5px"},
                {text: 'Point total', sortable: false},
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
