<template>
<div>
    <v-layout row align-content-space-between class="status" v-if="game.left_team">
        <v-flex></v-flex>
        <div class="mid" v-if="game.left_team">
            <v-layout row>
                <v-flex>
                    {{left_team_name}}
                </v-flex>
            <v-flex sm3>

            <v-select v-model="game.left_team.color" :items="team_colors.items"  v-on:change="saveTeams()"
                      item-text="name" item-value="id"></v-select>
            </v-flex>
        <v-btn v-on:click="swapTeams()">Swap</v-btn>
                <v-flex sm3>

            <v-select v-model="game.right_team.color" :items="team_colors.items"  v-on:change="saveTeams()"
                      item-text="name" item-value="id"></v-select>
                </v-flex>
                <v-flex>
                    {{right_team_name}}
                </v-flex>
            </v-layout>
        </div>
        <v-flex></v-flex>
    </v-layout>

    <v-layout row align-content-space-between class="status" v-if="game.left_team">
        <v-flex></v-flex>
        <div class="team" v-if="game.left_team" >
            <div v-for="player in game.left_team.players"class="left player">
                <v-layout row>

                    <v-select v-model="player.player" :items="left_players"
                              item-text="name" item-value="id"  v-on:change="saveTeams()"></v-select>
                </v-layout>
            </div>
        </div>
        <v-flex></v-flex>
        <div class="team" v-if="game.right_team" >
            <div v-for="player in game.right_team.players" v-if="game.right_team" class="right-player player">
                <v-layout row>
                    <v-select v-model="player.player" :items="right_players"
                              item-text="name" item-value="id"  v-on:change="saveTeams()" ></v-select>
                </v-layout>
            </div>
        </div>

    </v-layout>
</div>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'
    import VSelect from "vuetify/es5/components/VSelect/VSelect";

    export default {
        components: {VSelect},
        name: "team-bar",
        props: {
            game: {type: Object},
            match: {type: Object},
        },
        data() {
            return {
                left_players: [],
                right_players: [],
                right_team_name: "",
                left_team_name: "",
            }
        },
        computed: {
            ...mapState({
                team_colors: state => state.overwatch.team_colors,
            }),
        },
        created(){
            this.getTeamColors();
        },
        methods: {
            ...mapActions('overwatch', {
                getTeamColors: 'getTeamColors',
            }),
            ...mapActions('games', {
                updateTeams: 'updateTeams',
            }),
            swapTeams() {
                [this.game.left_team, this.game.right_team] = [this.game.right_team, this.game.left_team];
                this.saveTeams();
            },
            saveTeams(){
                const left_p = [... new Set(this.game.left_team.players.map(x=>x.player))];
                const right_p = [... new Set(this.game.right_team.players.map(x=>x.player))];
                let left_player_ids = this.game.left_team.players.map(x=>x.player);
                let i;
                console.log('LEFT PLAYERS')
                for (i=0; i<left_player_ids.length; i++){
                    console.log(this.left_players.filter(x=>x.id===left_player_ids[i])[0].name)
                }
                console.log(this.game.left_team.players.map(x=>x.player))
                console.log(left_p.length,this.game.left_team.players.map(x=>x.player),
                    right_p.length, this.game.right_team.players.map(x=>x.player))
                if (left_p.length < 6 || right_p < 6){
                    return
                }
                console.log('SAVING TEAMS')
                this.updateTeams(this.game);
            },
        },
        watch:{
            game: {
                handler(newGame) {

                this.left_players = this.match.event.teams.filter(x=>{return x.id === newGame.left_team.team})[0].players;
                this.right_players = this.match.event.teams.filter(x=>{return x.id === newGame.right_team.team})[0].players;
                this.left_team_name = this.match.event.teams.filter(x=>{return x.id === newGame.left_team.team})[0].name;
                this.right_team_name = this.match.event.teams.filter(x=>{return x.id === newGame.right_team.team})[0].name;

                console.log(this.left_players)
                },
                deep: true
            },
        }


    }
</script>

<style scoped>


    .status {
        width: 1280px;
        height: 80px;
    }

    .team {
        width: 600px;
        display: table-cell;
    }

    .player {
        display: table-cell;
        height: 80px;
        width: 80px;
        padding-left: 10px;
        padding-right: 10px;
        margin-left: 10px;
        margin-right: 10px;
    }


    .left {
    }

    .right-player {
        float: left;
    }

    .v-btn {
        min-width: 0;
        min-height: 0;
    }

    .mid {
        width: 800px;
        text-align: center;
    }
    .hero-icon{
        height: 35px;
    }

</style>