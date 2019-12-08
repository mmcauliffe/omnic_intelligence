<template>
    <div class='row text-center'>
        <div class="col-sm-3"></div>
        <div class='col-sm-6'>
            <em v-if="match.loading">Loading match...</em>
            <span v-if="match.error" class="text-danger">ERROR: {{match.error}}</span>
            <div v-if="match.item">


                <h1>{{ match.item.teams[0] }} vs {{ match.item.teams[1] }}</h1>
                <h4>{{ match.item.event.name }}</h4>
                <v-flex>
                    <v-text-field label="Game number" v-model="newGame.game_number"></v-text-field>
                        <v-select :items="maps.items" label="Map" v-model="newGame.map"
                                  item-text="name"item-value="id">
                        </v-select>
                </v-flex>
                <v-layout row>
                    <v-flex>

                        <v-select :items="teams.items" label="Left team" v-model="left_team"
                                  item-text="name" v-on:change="updateLeftTeam()" item-value="id">

                        </v-select>
                        <v-layout column>
                            <v-flex v-for="n in 6">
                                <v-select :label="'Player ' + n" :items="left_player_options" v-model="left_players[n]"
                                          item-text="name" item-value="id">

                                </v-select>

                            </v-flex>
                        </v-layout>
                    </v-flex>
                    <v-flex>

                        <v-select :items="teams.items" label="Right team" v-model="right_team"
                                  item-text="name" v-on:change="updateRightTeam()" item-value="id">

                        </v-select>
                        <v-layout column>
                            <v-flex v-for="n in 6">
                                <v-select :label="'Player ' + n" :items="right_player_options"
                                          v-model="right_players[n]"
                                          item-text="name" item-value="id">

                                </v-select>

                            </v-flex>
                        </v-layout>
                    </v-flex>
                </v-layout>
            <v-btn v-on:click="addGame()">Save Game</v-btn>
            </div>
            <div class="col">

                <h6>All Games</h6>

                <v-data-table :headers="game_headers" :items="games.items">

                    <template slot="items" slot-scope="props">
                        <td class="text-xs-right">

                            <router-link :to="{name: 'game-detail', params: {id: props.item.id}}">Game {{
                                props.item.game_number}}
                            </router-link>

                        </td>
                        <td>

                            <span class='badge' v-on:click="deleteGame(props.item.id)">X</span>

                        </td>
                    </template>
                </v-data-table>
            </div>

        </div>
    </div>

</template>

<script>
    import {mapState, mapActions} from 'vuex'
    const Vod = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['../../components/Vod'], () => {
            resolve(require('../../components/Vod'))
        })
    };
    const VDataTable = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VDataTable/VDataTable'], () => {
            resolve(require('vuetify/es5/components/VDataTable/VDataTable'))
        })
    };
    const VTextField = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTextField/VTextField'], () => {
            resolve(require('vuetify/es5/components/VTextField/VTextField'))
        })
    };

    export default {
        components: {
            VTextField,
            VDataTable,
            Vod},
        name: "match-detail-page",

        data() {
            return {
                newGame: {},
            }
        },
        computed: {
            ...mapState({
                account: state => state.account,
                maps: state => state.overwatch.maps,
                match: state => state.matches.one,
                games: state => state.matches.games,
                teams: state => state.matches.teams,
                matches: state => state.matches,
            }),
            left_player_options: {
                get: function () {
                    return this.matches.left_player_options
                },
                set: function (value) {
                    this.updateLeftPlayerOptions(value)
                }
            },
            right_player_options: {
                get: function () {
                    return this.matches.right_player_options
                },
                set: function (value) {
                    this.updateRightPlayerOptions(value)
                }
            }
        },
        created() {
            this.getOneEvent(this.$route.params.id);
            this.getGames(this.$route.params.id);
            this.getOneTeams(this.$route.params.id);
            this.getMaps();
            this.game_headers = [{text: 'Game'}, {text: 'Actions'}];
            this.left_team = null;
            this.right_team = null;
            this.left_players = {};
            this.right_players = {};
        },
        methods: {
            ...mapActions('matches', {
                getOneEvent: 'getOne',
                getOneTeams: 'getOneTeams',
                getGames: 'getOneGames',
                deleteMatch: 'delete',
                updateLeftPlayerOptions: 'updateLeftPlayerOptions',
                updateRightPlayerOptions: 'updateRightPlayerOptions',
            }),
            ...mapActions('games', {
                createGame: 'createGame'
            }),
            ...mapActions('overwatch', {
                getMaps: 'getMaps'
            }),
            saveMatch() {

            },
            addGame(){
                this.newGame.match = this.$route.params.id;
                this.newGame.left_team = this.left_team;
                this.newGame.right_team = this.right_team;
                this.newGame.left_players = this.left_players;
                this.newGame.right_players = this.right_players;
                this.createGame(this.newGame).then(x => {this.getGames(this.$route.params.id)})
            },
            updateAllTimes() {

            },
            updateLeftTeam() {
                console.log(this.left_team)
                let team = this.teams.items.filter(x => {
                    return x.id === this.left_team
                })[0]
                this.left_player_options = team.players;
                console.log(this.left_player_options)
            },
            updateRightTeam() {
                let team = this.teams.items.filter(x => {
                    return x.id === this.right_team
                })[0];
                this.right_player_options = team.players;
                console.log(this.right_player_options)
            },
            deleteGame(id) {

            }
        }
    }
</script>

<style scoped>

</style>