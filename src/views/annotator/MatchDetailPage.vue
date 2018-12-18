<template>
    <div class='row text-center'>
        <div class="col-sm-3"></div>
        <div class='col-sm-6'>
            <em v-if="match.loading">Loading match...</em>
            <span v-if="match.error" class="text-danger">ERROR: {{match.error}}</span>
            <div v-if="match.item">

                <div class="container-fluid">

                    <div class="col-md-9">
                        <div class="sidebar-nav pull-right">
                            <div class='row text-center'>
                                <div class="col">

                                    <h1>{{ match.item.teams[0] }} vs {{ match.item.teams[1] }}</h1>
                                    <h4>{{ match.item.event.name }}</h4>

                                    <v-btn color='success' v-on:click="saveMatch">Save</v-btn>


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
                    </div>
                </div>

            </div>
        </div>


    <div class="col-sm-3"></div>
    </div>
</template>

<script>
    import Vod from '../../components/Vod'
    import {mapState, mapActions} from 'vuex'
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";

    export default {
        components: {VDataTable, Vod},
        name: "match-detail-page",
        computed: {
            ...mapState({
                account: state => state.account,
                match: state => state.matches.one,
                games: state => state.matches.games
            })
        },
        created() {
            this.getOneEvent(this.$route.params.id);
            this.getGames(this.$route.params.id);
            this.game_headers = [{text: 'Game'}, {text: 'Actions'}]
        },
        methods: {
            ...mapActions('matches', {
                getOneEvent: 'getOne',
                getGames: 'getOneGames',
                deleteMatch: 'delete'
            }),
            saveMatch() {

            },
            updateAllTimes() {

            },
            deleteGame(id) {

            }
        }
    }
</script>

<style scoped>

</style>