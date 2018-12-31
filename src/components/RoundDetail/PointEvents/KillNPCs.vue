<template>
    <div>

        <v-layout row v-if="can_edit">
            <div>
                <v-select v-model="newEvent.killing_player" :items="allPlayers"
                          item-text="name" item-value="id" label="Killing player">

                </v-select>
            </div>
            <div>
                <v-select v-model="newEvent.ability" :items="availableAbilities"
                          item-text="name" item-value="id" label="Ability">

                </v-select>

                <v-btn class='primary raised' v-on:click="addEvent">Add kill</v-btn>
            </div>
            <div>
                <v-select v-model="newEvent.killed_npc" :items="killableNPCs"
                          item-text="name" item-value="id" label="Killed NPC">

                </v-select>
            </div>
        </v-layout>
        <v-data-table :headers="headers" :items="kill_npcs" v-if="kill_npcs" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>{{ props.item.killing_player }}</td>
                <td>
                    <v-select v-model="props.item.assisting_players" multiple chips deletable-chips
                              item-text="name" item-value="id" :items="props.item.possible_assists"
                              v-on:change="updateEvent(props.item)">
                    </v-select>
                </td>
                <td>
                    <v-select v-model="props.item.ability.id"
                              item-text="name" item-value="id" :items="props.item.possible_abilities"
                              v-on:change="updateEvent(props.item)">

                    </v-select>
                </td>
                <td>{{ props.item.killed_npc}}</td>
                <td v-if="can_edit">

        <v-layout layout="row" layout-align="space-between">
                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateEvent(props.item)">
                            access_time
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
        name: "killnpcs",
        extends: events,
        data() {
            return {
                newEvent: {},
                availableAbilities: [],
                killableNPCs: [],
                can_edit: true,
                event_type: 'kill_npcs',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'kill_npcs',
            ]),
            headers() {
                return [
                    {text: 'Time', sortable: false, width: "5px"},
                    {text: 'Killing player', sortable: false},
                    {text: 'Assists', sortable: false, width: "100px"},
                    {text: 'Ability', sortable: false, width: "50px"},
                    {text: 'Killed NPC', sortable: false},
                    {text: 'Actions', sortable: false, width: "130px"}]
            }
        },
        methods: {
            eventChangeHandler(newNewEvent) {
                if (newNewEvent.killing_player) {
                    console.log(newNewEvent);
                    this.generate_available_abilities(newNewEvent.killing_player);
                    this.generate_killable_npcs(newNewEvent.killing_player);
                    if (newNewEvent.killed_npc && this.killableNPCs.filter(npc => {
                        return npc.id === newNewEvent.killed_npc
                    }).length === 0) {
                        newNewEvent.killed_npc = undefined;
                    }
                    if (newNewEvent.ability && this.availableAbilities.filter(ability => {
                        return ability.id === newNewEvent.ability
                    }).length === 0) {

                        newNewEvent.ability = undefined;
                    }
                    console.log(this.availableAbilities)

                }
            },
            timeChangeHandler(new_timestamp) {
                if (this.newEvent.killing_player) {
                    console.log(this.currentTime);
                    this.generate_available_abilities(this.newEvent.killing_player);
                    this.generate_killable_npcs(this.newEvent.killing_player);
                    if (this.newEvent.killed_npc && this.killableNPCs.filter(npc => {
                        return npc.id === this.newEvent.killed_npc
                    }).length === 0) {
                        this.newEvent.killed_npc = undefined;
                    }
                }
            }
        },
    }
</script>

<style scoped>

    td.active {
        background-color: lightgreen;
    }

    td.clickable {
        cursor: pointer;
    }
</style>