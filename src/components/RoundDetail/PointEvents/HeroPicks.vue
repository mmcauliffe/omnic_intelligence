<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">
            <v-select v-model="newEvent.player" :items="allPlayers"
                      item-text="name" item-value="id" label="Player">

            </v-select>

            <v-select v-model="newEvent.new_hero" :items="availableHeroes"
                      item-text="name" item-value="id" label="New hero">

            </v-select>

            <v-btn class='primary raised' v-on:click="addEvent">Add switch</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="hero_picks" v-if="hero_picks" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>{{ props.item.player.name }}</td>
                <td>{{ props.item.new_hero.name }}</td>
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
        name: "switches",
        extends: events,
        data() {
            return {
                newEvent: {},
                availableHeroes: [],
                can_edit: true,
                event_type: 'hero_picks',
                rowsPerPage: [15]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'hero_picks',
            ]),
            headers(){
                return  [
                {text: 'Time', sortable: false, width: "5px"},
                {text: 'Player', sortable: false},
                {text: 'New hero', sortable: false},
                {text: 'Actions', sortable: false, width: "130px"}];
            }
        },
        methods: {

            generate_available_heroes(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.availableHeroes = []
                }
                let used_heroes = [];
                let players;
                if (this.playerOnLeftTeam(player_id)) {
                    players = this.leftPlayers;
                }
                else {
                    players = this.rightPlayers;
                }
                players.forEach(player => {
                    used_heroes.push(this.heroAtTime(player.id, this.currentTime).id)
                });
                console.log(used_heroes)
                this.availableHeroes = this.$store.state.overwatch.heroes.items.filter(function (h) {
                    return used_heroes.indexOf(h.id) === -1;
                });
            },
            eventChangeHandler(newNewEvent){
                if (newNewEvent.player) {
                    console.log(newNewEvent);

                    this.generate_available_heroes(newNewEvent.player);
                    console.log(this.availableHeroes)
                }
            },
            timeChangeHandler(new_timestamp){
                    if (this.newEvent.player) {
                    console.log(this.currentTime);
                    this.generate_available_heroes(this.newEvent.player);
                }
            }
        }
    }
</script>
