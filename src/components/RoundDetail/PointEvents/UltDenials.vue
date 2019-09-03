<template>
    <div>

        <v-layout row v-if="can_edit">
            <div>
                <v-select v-model="newEvent.denying_player" :items="denyingPlayers"
                          item-text="name" item-value="id" label="Denying player">

                </v-select>
            </div>
            <div>
                <v-select v-model="newEvent.denied_player" :items="deniablePlayers"
                          item-text="name" item-value="id" label="Denied Player">

                </v-select>

                <v-btn class='primary raised' v-on:click="addEvent">Add deny</v-btn>
            </div>
            <div>
                <v-select v-model="newEvent.ability" :items="deniableAbilities"
                          item-text="name" item-value="id" label="Ability">

                </v-select>
            </div>
        </v-layout>
        <v-data-table :headers="headers" :items="ult_denials" v-if="ult_denials" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>{{ props.item.denying_player }}</td>
                <td>{{ props.item.denied_player}}</td>
                <td>
                    {{ props.item.ability}}
                </td>
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
        name: "ult_denials",
        extends: events,
        data() {
            return {
                newEvent: {},
                denyingPlayers: [],
                deniablePlayers: [],
                deniableAbilities: [],
                can_edit: true,
                event_type: 'ult_denials',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'ult_denials',
            ]),
            ...mapGetters('overwatch', [
                'denying_heroes',
            ]),
            headers() {
                return [
                    {text: 'Time', sortable: false, width: "5px"},
                    {text: 'Denying player', sortable: false},
                    {text: 'Denied player', sortable: false},
                    {text: 'Ability', sortable: false, width: "50px"},
                    {text: 'Actions', sortable: false, width: "130px"}]
            }
        },
        methods: {
            generate_denying_players() {
                if (!this.currentTime) {
                    this.denyingPlayers = []
                }
                let deniers = this.denying_heroes;
                this.denyingPlayers = this.leftPlayers.filter(x=> {
                    return deniers.indexOf(this.heroAtTime(x.id, this.currentTime).name) > -1
                });
                this.denyingPlayers = this.denyingPlayers.concat(this.rightPlayers.filter(x=> {
                    return deniers.indexOf(this.heroAtTime(x.id, this.currentTime).name) > -1
                }));
            },
            eventChangeHandler(newNewEvent) {
                if (newNewEvent.denying_player) {
                    this.generate_deniable_players(newNewEvent.denying_player);
                    if (newNewEvent.denied_player && this.deniablePlayers.filter(player => {
                        return player.id === newNewEvent.denied_player
                    }).length === 0) {
                        newNewEvent.denied_player = undefined;
                    }

                }
                if (newNewEvent.denied_player) {
                    console.log(newNewEvent);
                    this.generate_deniable_abilities(newNewEvent.denied_player);
                    if (newNewEvent.ability && this.deniableAbilities.filter(ability => {
                        return ability.id === newNewEvent.ability
                    }).length === 0) {

                        newNewEvent.ability = undefined;
                    }

                }
            },
            timeChangeHandler(new_timestamp) {
                this.generate_denying_players();
                if (this.newEvent.denying_player) {
                    if (this.denyingPlayers.filter(player => {
                        return player.id === this.newEvent.denied_player
                    }).length === 0) {
                        this.newEvent.denying_player = undefined;
                    }
                }

                if (this.newEvent.denying_player) {
                    this.generate_deniable_players(this.newEvent.denying_player);
                    if (this.newEvent.denied_player && this.deniablePlayers.filter(player => {
                        return player.id === this.newEvent.denied_player
                    }).length === 0) {
                        this.newEvent.denied_player = undefined;
                    }

                }
                if (this.newEvent.denied_player) {
                    console.log(this.newEvent);
                    this.generate_deniable_abilities(this.newEvent.denied_player);
                    if (this.newEvent.ability && this.deniableAbilities.filter(ability => {
                        return ability.id === newEvent.ability
                    }).length === 0) {

                        this.newEvent.ability = undefined;
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