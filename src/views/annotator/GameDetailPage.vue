<template>
    <div class="container-fluid">
        <em v-if="game.loading">Loading game...</em>
        <span v-if="game.error" class="text-danger">ERROR: {{game.error}}</span>
    <div class="row">

    <div class="col-md-7" v-if="game.item">
        {{game.item}}
    </div>
    <div class="col-md-5" v-if="game.item">
        <div class="sidebar-nav pull-right">
            <div class='row'>

                    <v-select :items="maps.items" item-text="name" item-value="id" v-model="game.item.map" label="Map">

                    </v-select>

                <div class='row text-center'>
                        <div class="col-xs-6">
                            <h3>Left team</h3>
                            <v-select v-model="game.item.left_team.team"
                                                 :items="game.teams" item-text="name" item-value="id" label="'Team">

                            </v-select>
                            <v-select v-model="game.item.left_team.color" item-text="name" item-value="name"
                                                  :items="colors.items" label="Color">

                            </v-select>
                            <v-input type="text" v-model="game.item.left_team.points" label="Points" />
                            <v-input type="text" v-model="game.item.left_team.subpoints" label="Subpoints"/>
                            <ul>
                                <li v-for="i in 6">
                                    <v-select v-model="game.item.left_team.players[i]"
                                        :items="leftPlayers" item-text="name" item-value="id" :label="i | playerTemplate">

                                </v-select>
                                </li>
                            </ul>
                        </div>

                        <div class="col-xs-6">
                            <h3>Right team</h3>
                            <v-select label="Team" v-model="game.item.right_team.team"
                                                 :items="game.teams" item-text="name" item-value="id">

                            </v-select>

                            <v-select label="Color" v-model="game.item.right_team.color" item-text="name" item-value="name"
                                                  :items="colors.items" >

                            </v-select>
                            <v-input type="text" v-model="game.item.right_team.points" label="Points"/>
                            <v-input type="text" ng-model="game.item.right_team.subpoints" label="Subpoints"/>
                            <ul>
                                <li v-for="i in 6">
                                    <v-select
                                        v-model="game.item.right_team.players[i]" :label="i | playerTemplate"
                                        :items="rightPlayers" item-text="name" item-value="id">

                                </v-select>
                                </li>
                            </ul>
                        </div>
                    <v-btn class='success'>Save</v-btn>
                </div>
                <div class="row">
                <div class='col'>

                    <h1>Rounds</h1>

                <v-data-table :headers="round_headers" :items="rounds.items">

                    <template slot="items" slot-scope="props">
                        <td class="text-xs-right">

                            <router-link :to="{name: 'round-detail', params: {id: props.item.id}}">
                                Round {{ props.item.round_number}}
                            </router-link>

                        </td>
                            <td v-on:click="seekTo(props.item.begin)">
                                {{ props.item.begin | secondsToMoment |  moment('HH:mm:ss.S') }}
                            </td>
                            <td v-on:click="seekTo(props.item.end)">
                                {{ props.item.end | secondsToMoment | moment('HH:mm:ss') }}
                            </td>
                        <td>

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="deleteRound(props.item.id)">
                            remove_circle
                        </v-icon>
                        <span>Remove</span>
                    </v-tooltip>

                        </td>
                    </template>
                </v-data-table>

                </div>
            </div>
                </div>
    </div>
        </div>
    </div>
</div>
</template>

<script>
    import Vod from '../../components/Vod'
import { mapState, mapActions } from 'vuex'
    const VDataTable = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VDataTable/VDataTable'], () => {
            resolve(require('vuetify/es5/components/VDataTable/VDataTable'))
        })
    };
    const VInput = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VInput/VInput'], () => {
            resolve(require('vuetify/es5/components/VInput/VInput'))
        })
    };
    const VSelect = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VSelect/VSelect'], () => {
            resolve(require('vuetify/es5/components/VSelect/VSelect'))
        })
    };

    export default {
        name: "game-detail-page",
        components: {
            VSelect,
            VInput,
            VDataTable,
            Vod},
    computed: {
        ...mapState({
            account: state => state.account,
            game: state => state.games.one,
            rounds: state => state.games.rounds,
            teams: state => state.matches.teams,
            maps: state => state.overwatch.maps,
            colors: state => state.overwatch.team_colors,
        }),
        leftPlayers(){
            if (this.$store.state.games.one.loading){
                return []
            }
            console.log('left', this.$store.state.games.one.item.left_team)
            console.log(this.$store.state.games.one.teams[0])
            if (this.$store.state.games.one.item.left_team.id === this.$store.state.games.one.teams[0].id){
                return this.$store.state.games.one.teams[0].players
            }
            else {
                return this.$store.state.games.one.teams[1].players
            }

        },
        rightPlayers(){
            if (this.$store.state.games.one.loading){
                return []
            }
            console.log('right', this.$store.state.games.one.item.right_team)
            console.log(this.$store.state.games.one.teams[0])
            if (this.$store.state.games.one.item.right_team.id === this.$store.state.games.one.teams[0].id){
                return this.$store.state.games.one.teams[0].players
            }
            else {
                return this.$store.state.games.one.teams[1].players
            }

        },
    },
    created () {
        this.getOneGame(this.$route.params.id);
        this.getRounds(this.$route.params.id);
        this.getTeamColors();
        this.getMaps();
        this.round_headers = [{text: 'Round'}, {text: 'Begin'}, {text: 'End'},  {text: 'Actions'}]
    },
    methods: {
        ...mapActions('games', {
            getOneGame: 'getOne',
            getRounds: 'getOneRounds',
        }),
        ...mapActions('rounds', {
            deleteRound: 'deleteRound'
        }),
        ...mapActions('overwatch', {
            getMaps: 'getMaps',
            getTeamColors: 'getTeamColors',
        }),
        seekTo(time){
            console.log(time)
        }
    }
    }
</script>

<style scoped>

</style>