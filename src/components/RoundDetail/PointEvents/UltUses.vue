<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">
            <v-select v-model="newEvent.player" :items="allPlayers"
                      item-text="name" item-value="id" label="Player">

            </v-select>

            <v-btn class='primary raised' v-on:click="addEvent">Add ult use</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="ult_uses" v-if="ult_uses" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>{{ props.item.player.name }}</td>
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

    export default {
        name: "ult_uses",
        extends: events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'ult_uses',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'ult_uses',
            ]),
            headers(){
                return [
                {text: 'Time', sortable: false, width: "5px"},
                {text: 'Player', sortable: false},
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
