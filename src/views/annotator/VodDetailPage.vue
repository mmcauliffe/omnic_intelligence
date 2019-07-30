<template>

    <v-layout row>
        <div class="vod-column" v-if="vod.item">
            <TeamBar :game="selectedGame" :match="selectedMatch"></TeamBar>
            <Vod :vod_type="vod.item.vod_link[0]" :id="vod.item.vod_link[1]"></Vod>
        </div>
        <v-flex style="height:100%" xs4 v-if="vod.item">
            <v-layout column>
                <v-flex>
                    {{vod.item}}
                    <v-select :items="vod_status_choices.items" v-on:change="update_vod()"
                              label="Vod Status" v-model="vod.item.status" item-text="name" item-value="id">

                    </v-select>
                    <v-select :items="vod_type_choices.items" v-on:change="update_vod()"
                              label="Vod Type" v-model="vod.item.type" item-text="name" item-value="id">

                    </v-select>
                </v-flex>
                <v-tabs md-border-bottom md-dynamic-height>
                    <v-tab>
                        Matches
                    </v-tab>
                    <v-tab>
                        Games
                    </v-tab>
                    <v-tab>
                        Rounds
                    </v-tab>

                    <v-tabs-items>
                        <v-tab-item>
                            <v-card>
                <v-flex>

                <v-data-table
                        :items="matches.items" v-if="matches.items"
                        :headers="matchHeaders" :rows-per-page-items="rowsPerPage">

                    <template slot="items" slot-scope="props">
                        <td>
                            <v-select v-model="props.item.teams[0]" v-on:change="changeMatch(props.item)" :items="props.item.event.teams"
                                                  item-text="name" item-value="id">

                            </v-select>
                        </td>
                        <td>
                            <v-select v-model="props.item.teams[1]" v-on:change="changeMatch(props.item)" :items="props.item.event.teams"
                                                  item-text="name" item-value="id">

                            </v-select>

                        </td>
                        <td>
                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="removeMatch(props.item.id)">
                            remove_circle
                        </v-icon>
                        <span>Delete</span>
                    </v-tooltip>
                        </td>
                    </template>
                </v-data-table>
                </v-flex>
                            </v-card>
                        </v-tab-item>
                        <v-tab-item>
                            <v-card>

                            <v-flex>
                    <v-select label="Match" :items="event_matches.items" v-model="newGame.match"
                              item-text="name" item-value="id"></v-select>
                    <v-text-field label="Game number" v-model="newGame.game_number"></v-text-field>
                    <v-select label="Map" :items="maps.items" v-model="newGame.map"
                              item-text="name" item-value="id"></v-select>
                    <v-btn v-on:click="addGame()">Add game</v-btn>
                </v-flex>
                <v-flex>

                <v-data-table
                        :items="games.items" v-if="games.items"
                        :headers="gameHeaders" :rows-per-page-items="rowsPerPage">

                    <template slot="items" slot-scope="props">
                        <td>

                    <v-select :items="event_matches.items" v-model="props.item.match"
                              item-text="name" item-value="id" v-on:change="changeGame(props.item)"></v-select>
                        </td>
                        <td>
                                <v-text-field v-model="props.item.game_number" v-on:change="changeGame(props.item)"></v-text-field>
                        </td>
                        <td>
                    <v-select :items="maps.items" v-model="props.item.map" v-on:change="changeGame(props.item)"
                              item-text="name" item-value="id"></v-select>
                        </td>
                        <td>
                            <v-tooltip bottom>
                                <v-icon class="clickable" slot="activator" v-on:click="selectGame(props.item)">
                            build
                                </v-icon>
                                <span>Edit game</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                                <v-icon class="clickable" slot="activator" v-on:click="removeGame(props.item.id)">
                            remove_circle
                                </v-icon>
                                <span>Delete</span>
                            </v-tooltip>
                        </td>
                    </template>
                </v-data-table>
                </v-flex>
                            </v-card>
                        </v-tab-item>
                        <v-tab-item>
                            <v-card>

                            <v-flex>
                    <v-select label="Match" :items="event_matches.items" v-model="match"
                              item-text="name" item-value="id" v-on:change="updateGames()"></v-select>
                    <v-select label="Game" v-model="newRound.game" :items="match_games.items" item-text="name" item-value="id"></v-select>
                    <v-text-field label="Round number" v-model="newRound.round_number"></v-text-field>
                    <v-select :items='sides.items' label="Attacking side" v-model="newRound.attacking_side"
                              item-text="name" item-value="id"></v-select>
                    <v-btn v-on:click="addRound()">Add round</v-btn>
                </v-flex>
                <v-flex>

                <v-data-table
                        :items="rounds.items" v-if="rounds.items"
                        :headers="headers" :rows-per-page-items="rowsPerPage">

                    <template slot="items" slot-scope="props">
                        <td>
                    <v-select v-model="props.item.game" :items="games.items" item-text="game_number" item-value="id" v-on:change="changeRound(props.item)"></v-select>

                        </td>
                        <td>
                                <v-text-field v-model="props.item.round_number" v-on:change="changeRound(props.item)"></v-text-field>
                        </td>
                        <td>
                    <v-select  v-model="props.item.attacking_side" :items="sides.items" item-text="name" item-value="id" v-on:change="changeRound(props.item)"></v-select>
                        </td>
                        <td class="clickable" v-on:click="seekTo(props.item.begin)"
                            v-bind:class="{ active: isCurrentRound(props.item) }">
                            {{ props.item.begin | secondsToMoment | moment('HH:mm:ss.S') }}
                        </td>
                        <td class="clickable" v-on:click="seekTo(props.item.end)"
                            v-bind:class="{ active: isCurrentRound(props.item) }">
                            {{ props.item.end | secondsToMoment | moment('HH:mm:ss.S') }}
                        </td>
                        <td>
                            <v-select  v-model="props.item.annotation_status" :items="annotation_source_choices.items"
                                       item-text="name" item-value="id" v-on:change="changeRound(props.item)"></v-select>
                        </td>
                        <td>
                            <router-link :to="{name: 'round-detail', params: {id: props.item.id}}">
                                View
                            </router-link>
                            <v-tooltip bottom>
                                <v-icon class="clickable" slot="activator" v-on:click="updateRoundBegin(props.item)">
                                    access_time
                                </v-icon>
                                <span>Update begin to current</span>
                            </v-tooltip>
                            <v-tooltip bottom>
                                <v-icon class="clickable" slot="activator" v-on:click="updateRoundEnd(props.item)">
                                    access_time
                                </v-icon>
                                <span>Update end to current</span>
                            </v-tooltip>
                            <v-tooltip bottom v-if="props.item.annotation_status == 'N'">
                                <v-icon class="clickable" slot="activator" v-on:click="removeRound(props.item.id)">
                            remove_circle
                                </v-icon>
                                <span>Delete</span>
                            </v-tooltip>
                        </td>
                    </template>
                </v-data-table>
                </v-flex>
                            </v-card>
                        </v-tab-item>
                    </v-tabs-items>
                </v-tabs>

            </v-layout>
        </v-flex>
    </v-layout>
</template>

<script>
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";
    import Vod from '../../components/Vod';
    import TeamBar from '../../components/TeamBar';
    import {mapState, mapActions, mapGetters} from 'vuex'
    import VTextField from "vuetify/es5/components/VTextField/VTextField";
    import VTabsItems from "vuetify/es5/components/VTabs/VTabsItems";
    import VTabItem from "vuetify/es5/components/VTabs/VTabItem";
    import VTabs from "vuetify/es5/components/VTabs/VTabs";
    import VTab from "vuetify/es5/components/VTabs/VTab";
    import VSelect from "vuetify/es5/components/VSelect/VSelect";

    export default {
        name: "vod-detail-page",
        components: {
            VSelect,
            VTextField,
            Vod,
            VDataTable,
            VTabs,
            VTab,
            VTabItem,
            VTabsItems,
            TeamBar
        },
        data(){
            return {
                newRound: {},
                newMatch:{teams:{}},
                newGame: {},
                match: 0,
                rowsPerPage: [10],
                selectedGame: {},
                selectedMatch: {},
            }
        },
        computed: {
            ...mapState({
                account: state => state.account,
                vod: state => state.vods.one,
                timestamp: state => state.vods.timestamp,
                vod_status_choices: state => state.vods.vod_status_choices,
                vod_type_choices: state => state.vods.vod_type_choices,
                sides: state => state.overwatch.sides,
                event_matches: state => state.vods.vod_event_matches,
                match_games: state => state.matches.games,
                rounds: state => state.vods.rounds,
                games: state => state.vods.games,
                matches: state => state.vods.matches,
                maps: state => state.overwatch.maps,
                annotation_source_choices: state => state.vods.annotation_sources
            }),
            currentTime() {
                return Math.round((this.timestamp) * 10) / 10;
            },
            headers() {
                return [
                    {text: 'Game', sortable: false},
                    {text: 'Round', sortable: false},
                    {text: 'Attacking side', sortable: false},
                    {text: 'Begin', sortable: false},
                    {text: 'End', sortable: false},
                    {text: 'Annotations', sortable: false},
                    {text: 'Actions', sortable: false}]
            },
            gameHeaders(){
                return [
                    {text: 'Match', sortable: false},
                    {text: 'Game number', sortable: false},
                    {text: 'Map', sortable: false},
                    {text: 'Actions', sortable: false}

                ]
            },
            matchHeaders(){
                return [
                    {text: 'Team one', sortable: false},
                    {text: 'Team two', sortable: false},
                    {text: 'Actions', sortable: false}

                ]
            }
        },
        created() {
            this.can_edit = true;
            this.getOne(this.$route.params.id);
            this.getOnePossibleMatches(this.$route.params.id);
            this.getOneRounds(this.$route.params.id);
            this.getOneGames(this.$route.params.id);
            this.getOneMatches(this.$route.params.id);
            this.getVodStatusChoices();
            this.getAnnotationSources();
            this.getVodTypeChoices();
            this.getSides();
            this.getMaps();
        },
        methods: {
            ...mapActions('vods', {
                getOne: 'getOne',
                getOnePossibleMatches: 'getOnePossibleMatches',
                getOneRounds: 'getOneRounds',
                getOneGames: 'getOneGames',
                getOneMatches: 'getOneMatches',
                updateVod: 'updateVod',
                deleteVod: 'deleteVod',
                updateTimestamp: 'updateTimestamp',
                getVodStatusChoices: 'getVodStatusChoices',
                getAnnotationSources: 'getAnnotationSources',
                getVodTypeChoices: 'getVodTypeChoices',
            }),
            ...mapActions('overwatch', {
                getSides: 'getSides',
                getMaps: 'getMaps'
            }),
            ...mapActions('rounds', {
                createRound: 'createRound',
                updateRound: 'updateRound',
                deleteRound: 'deleteRound',
            }),
            ...mapActions('games', {
                createGame: 'createGame',
                updateGame: 'updateGame',
                deleteGame: 'deleteGame',
            }),
            ...mapActions('matches', {
                createMatch: 'createMatch',
                updateMatch: 'updateMatch',
                deleteMatch: 'deleteMatch',
                getOneMatchGames: 'getOneGames',
            }),
            update_vod() {
                this.updateVod(this.vod.item);
            },
            isCurrentRound(round) {

                return this.currentTime >= round.begin && this.currentTime <= round.end
            },
            seekTo(time) {
                this.updateTimestamp(time);
            },
            updateGames(){
        this.$nextTick(() => {
            console.log(this.match)
            this.getOneMatchGames(this.match);
        });
            },
            selectGame(game){
                this.selectedMatch = this.matches.items.filter(x => {return x.id === game.match})[0];
                this.selectedGame = game;
            },
            addMatch(){
                this.createMatch(this.newMatch).then(x=>this.getOneMatches(this.$route.params.id));
            },
            addGame(){
                console.log(this.newGame)
                this.createGame(this.newGame).then(x=>this.getOneGames(this.$route.params.id));
            },
            addRound(){
                this.newRound.vod = this.$route.params.id;
                this.newRound.begin = this.currentTime;
                this.newRound.end = this.currentTime;
                console.log(this.newRound)
                console.log(this.currentTime)
                this.createRound(this.newRound).then(x =>{this.getOneRounds(this.$route.params.id)});
            },
            updateRoundBegin(round) {
                round.begin = this.currentTime;
                this.updateRound({data: round, refresh: false});
            },
            updateRoundEnd(round) {
                round.end = this.currentTime;
                this.updateRound({data: round, refresh: false});
            },
            changeRound(round){
                if (!round.round_number){
                    return
                }
                this.updateRound({data: round, refresh: false});
            },
            changeGame(game){
                if (!game.game_number){
                    return
                }
                this.updateGame(game);
            },
            changeMatch(match){
                this.updateMatch(match);
            },
            removeMatch(id){
                this.deleteMatch(id).then(x=>this.getOneMatches(this.$route.params.id));
            },
            removeGame(id){
                this.deleteGame(id).then(x=>this.getOneGames(this.$route.params.id));
            },
            removeRound(id){
                this.deleteRound(id).then(x=>this.getOneRounds(this.$route.params.id));
            }
        },
    }
</script>

<style scoped>
    .vod-column {
        width: 1280px;
    }

    td.active {
        background-color: lightgreen;
    }

    td.clickable {
        cursor: pointer;
    }
</style>