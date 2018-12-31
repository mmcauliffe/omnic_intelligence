<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">
            <v-select v-model="newEvent.side" :items="sides"
                      item-text="name" item-value="id" label="Sides">

            </v-select>
            <v-select v-model="newEvent.npc" :items="npcs"
                      item-text="name" item-value="id" label="NPC">

            </v-select>

            <v-btn class='primary raised' v-on:click="addEvent">Add NPC death</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="npc_deaths" v-if="npc_deaths" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>
            <v-select v-if="can_edit" v-model="props.item.side" :items="sides"
                      item-text="name" item-value="id" v-on:change="updateEvent(props.item)">
            </v-select>
                                                    <span v-if="!can_edit && props.item.side ==='L'">Left</span>
<span v-if="!can_edit && props.item.side ==='R'">Right</span>
                </td>
                <td>{{ props.item.npc }}</td>
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
        name: "npc_deaths",
        extends: events,
        data() {
            return {
                newEvent: {},
                availableHeroes: [],
                can_edit: true,
                event_type: 'npc_deaths',
                rowsPerPage: [10]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'npc_deaths',
            ]),
            ...mapGetters('overwatch', [
                'npcs',
            ]),
            headers(){
                return [
                {text: 'Time', sortable: false, width: "5px"},
                {text: 'Side', sortable: false, width: "5px"},
                {text: 'NPC', sortable: false},
                {text: 'Actions', sortable: false, width: "130px"}]
            }
        },
    }
</script>
