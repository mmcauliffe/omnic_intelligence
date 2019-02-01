<template>
    <div>

        <v-layout row v-if="can_edit">
            <div>
                <v-select v-model="newEvent.reviving_player" :items="allPlayers"
                          item-text="name" item-value="id" label="Reviving player">

                </v-select>
            </div>
            <div>
                <v-select v-model="newEvent.ability" :items="availableAbilities"
                          item-text="name" item-value="id" label="Ability">

                </v-select>

                <v-btn class='primary raised' v-on:click="addEvent">Add revive</v-btn>
            </div>
            <div>

                <v-select v-model="newEvent.revived_player" :items="revivablePlayers"
                          item-text="name" item-value="id" label="Revived player">

                </v-select>
            </div>
        </v-layout>
        <v-data-table :headers="headers" :items="revives" v-if="revives" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>{{ props.item.reviving_player }}</td>
                <td>{{props.item.ability}}
                </td>
                <td>{{ props.item.revived_player }}</td>
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
        name: "revives",
        extends: events,
        data() {
            return {
                newEvent: {},
                availableAbilities: [],
                revivablePlayers: [],
                can_edit: true,
                event_type: 'revives',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'revives',
            ]),
            headers(){
                return [
                {text: 'Time', sortable: false, width: "5px"},
                {text: 'Reviving player', sortable: false},
                {text: 'Ability', sortable: false, width: "50px"},
                {text: 'Revived player', sortable: false},
                {text: 'Actions', sortable: false, width: "130px"}];
            }
        },
        methods: {
            eventChangeHandler(newNewEvent){
                if (newNewEvent.reviving_player) {
                    console.log(newNewEvent);
                    this.generate_revivable_abilities(newNewEvent.reviving_player);
                    this.generate_revivable_players(newNewEvent.reviving_player);
                    if (newNewEvent.revived_player && this.revivablePlayers.filter(player=>{return player.id === newNewEvent.revived_player}).length === 0){
                        newNewEvent.revived_player = undefined;
                    }
                    if (newNewEvent.ability && this.availableAbilities.filter(ability=>{return ability.id === newNewEvent.ability}).length === 0){

                        newNewEvent.ability = undefined;
                        newNewEvent.headshot = false;
                    }
                    console.log(this.availableAbilities)

                }
            },
            timeChangeHandler(new_timestamp){
                    if (this.newEvent.reviving_player) {
                    console.log(this.currentTime);
                    this.generate_revivable_abilities(this.newEvent.reviving_player);
                }
            }
        },
    }
</script>
