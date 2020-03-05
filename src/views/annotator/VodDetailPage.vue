<template>

    <v-layout row>
        <vue-headful :title="title"/>
        <div class="vod-column" v-if="vod.item">
            <TeamBar :game="selectedGame" :match="selectedMatch"></TeamBar>
            <Vod :vod_type="vod.item.vod_link[0]" :id="vod.item.vod_link[1]"></Vod>
        </div>
        <v-flex style="height:100%" xs4 v-if="vod.item">
            <v-layout column>
                <v-flex>
                    <v-select :items="vod_status_choices.items" v-on:change="update_vod()"
                              label="Vod Status" v-model="vod.item.status" item-text="name" item-value="id">

                    </v-select>
                    <v-select :items="vod_type_choices.items" v-on:change="update_vod()"
                              label="Vod Type" v-model="vod.item.type" item-text="name" item-value="id">

                    </v-select>
                </v-flex>
                <v-tabs md-border-bottom md-dynamic-height>
                    <v-tab v-for="m in vod.item.matches">
                        {{m.name}}
                    </v-tab>
                <v-tabs-items>
                    <v-tab-item v-for="m in vod.item.matches">
                        <v-card>
                            <v-flex>
                                {{m.date}}
                                <v-flex xs4>
                                    <v-btn v-on:click="addGame(m)">
                                    <v-icon flat icon>add_circle</v-icon>
                                    </v-btn>

                                </v-flex>
                                <v-expansion-panel v-if="m.games">
                                    <v-expansion-panel-content v-for="g in m.games" :key="g.id">
                                        <div slot="header" v-on:click="selectGame(g)">Game {{g.game_number}}</div>
                                        <v-form>
                                            <v-container>
                                                <v-layout row>
                                            <v-flex xs3>
                                        <v-text-field label="Game number" v-model="g.game_number" v-on:change="changeGame(g)"></v-text-field>

                                            </v-flex>
                                            <v-flex xs3>
                                    <v-select label="Map" :items="maps.items" v-model="g.map" v-on:change="changeGame(g)"
                              item-text="name" item-value="id"></v-select>

                                            </v-flex>
                                            <v-flex xs3>
                                                <v-btn v-on:click="addRound(g)">
                                                <v-icon flat icon>add_circle</v-icon>
                                                </v-btn>

                                            </v-flex>
                                                    <v-flex xs3>

                                                <v-btn v-on:click="removeGame(g.id)">
                                                <v-icon flat icon>remove_circle</v-icon>
                                                </v-btn>
                                                    </v-flex>

                                        </v-layout>
                                            </v-container>
                                        </v-form>

                                        <v-data-table
                                                :items="g.rounds" v-if="g.rounds"
                                                :headers="headers" :rows-per-page-items="rowsPerPage">

                                            <template slot="items" slot-scope="props">
                                                <td>
                                                    <v-select v-model="props.item.game" :items="m.games"
                                                              item-text="game_number" item-value="id"
                                                              v-on:change="changeRound(props.item)"></v-select>

                                                </td>
                                                <td>
                                                    <v-text-field v-model="props.item.round_number"
                                                                  v-on:change="changeRound(props.item)"></v-text-field>
                                                </td>
                                                <td>
                                                    <v-select v-model="props.item.attacking_side" :items="sides.items"
                                                              item-text="name" item-value="id"
                                                              v-on:change="changeRound(props.item)"></v-select>
                                                </td>
                                                <td class="unclickable" v-if="isDifferentVod(props.item)">
                                                    {{ props.item.begin | secondsToMoment | moment('HH:mm:ss.S') }}
                                                </td>
                                                <td v-else class="clickable" v-on:click="seekTo(props.item.begin)"
                                                    v-bind:class="{ active: isCurrentRound(props.item)}">
                                                    {{ props.item.begin | secondsToMoment | moment('HH:mm:ss.S') }}
                                                </td>
                                                <td class="unclickable" v-if="isDifferentVod(props.item)">
                                                    {{ props.item.end | secondsToMoment | moment('HH:mm:ss.S') }}
                                                </td>
                                                <td v-else class="clickable" v-on:click="seekTo(props.item.end)"
                                                    v-bind:class="{ active: isCurrentRound(props.item) }">
                                                    {{ props.item.end | secondsToMoment | moment('HH:mm:ss.S') }}
                                                </td>
                                                <td>
                                                    <v-select v-model="props.item.annotation_status"
                                                              :items="annotation_source_choices.items"
                                                              item-text="name" item-value="id"
                                                              v-on:change="changeRound(props.item)"></v-select>
                                                </td>
                                                <td>
                                                    <router-link
                                                            :to="{name: 'round-detail', params: {id: props.item.id}}">
                                                        View
                                                    </router-link>
                                                    <v-tooltip bottom>
                                                        <v-icon class="clickable" slot="activator"
                                                                v-on:click="updateRoundBegin(props.item)">
                                                            access_time
                                                        </v-icon>
                                                        <span>Update begin to current</span>
                                                    </v-tooltip>
                                                    <v-tooltip bottom>
                                                        <v-icon class="clickable" slot="activator"
                                                                v-on:click="updateRoundEnd(props.item)">
                                                            access_time
                                                        </v-icon>
                                                        <span>Update end to current</span>
                                                    </v-tooltip>
                                                    <v-tooltip bottom v-if="props.item.annotation_status === 'N'">
                                                        <v-icon class="clickable" slot="activator"
                                                                v-on:click="removeRound(props.item.id)">
                                                            remove_circle
                                                        </v-icon>
                                                        <span>Delete</span>
                                                    </v-tooltip>
                                                </td>
                                            </template>
                                        </v-data-table>

                                    </v-expansion-panel-content>
                                </v-expansion-panel>
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
    import {mapState, mapActions, mapGetters} from 'vuex'

    const Vod = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['../../components/Vod'], () => {
            resolve(require('../../components/Vod'))
        })
    };
    const TeamBar = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['../../components/TeamBar'], () => {
            resolve(require('../../components/TeamBar'))
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
    const VTabs = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTabs/VTabs'], () => {
            resolve(require('vuetify/es5/components/VTabs/VTabs'))
        })
    };
    const VTab = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTabs/VTab'], () => {
            resolve(require('vuetify/es5/components/VTabs/VTab'))
        })
    };
    const VTabsItems = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTabs/VTabsItems'], () => {
            resolve(require('vuetify/es5/components/VTabs/VTabsItems'))
        })
    };
    const VTabItem = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTabs/VTabItem'], () => {
            resolve(require('vuetify/es5/components/VTabs/VTabItem'))
        })
    };
    const VSelect = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VSelect/VSelect'], () => {
            resolve(require('vuetify/es5/components/VSelect/VSelect'))
        })
    };

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
        data() {
            return {
                newRound: {},
                newMatch: {teams: {}},
                newGame: {},
                match: 0,
                rowsPerPage: [10],
                selectedGame: {},
                selectedMatch: {},
            }
        },
        computed: {
            title() {
                if (this.vod.item) {
                    return this.vod.item.title + ' | Omnic Intelligence'
                }
            },
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
            gameHeaders() {
                return [
                    {text: 'Game number', sortable: false},
                    {text: 'Map', sortable: false},
                    {text: 'Actions', sortable: false}

                ]
            },
            matchHeaders() {
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
            }),
            update_vod() {
                this.updateVod(this.vod.item);
            },
            isCurrentRound(round) {

                return this.currentTime >= round.begin && this.currentTime <= round.end
            },
            isDifferentVod(round) {

                return round.stream_vod !== this.vod.item.id
            },
            seekTo(time) {
                this.updateTimestamp(time);
                let m, g;
                let found = false;
                for (let mi = 0; mi < this.vod.item.matches.length; mi++) {
                    m = this.vod.item.matches[mi];
                    for (let gi = 0; gi < m.games.length; gi++) {
                        g = m.games[gi];
                        if (g.rounds[0].begin <= time && time <= g.rounds[g.rounds.length - 1].end) {
                            this.selectedGame = g;
                            this.selectedMatch = m;
                            this.found = true;
                            break
                        }
                    }
                    if (found) {
                        break
                    }
                }
            },
            selectGame(game) {
                let m, g;
                let found = false;
                for (let mi = 0; mi < this.vod.item.matches.length; mi++) {
                    m = this.vod.item.matches[mi];
                    for (let gi = 0; gi < m.games.length; gi++) {
                        g = m.games[gi];
                        if (g.id === game.id){
                            this.selectedMatch = m;
                            found = true;
                            break
                        }
                    }
                    if (found){
                        break
                    }
                }
                this.selectedGame = game;
                if (game.rounds.length > 0){
                    this.updateTimestamp(game.rounds[0].begin);

                }

            },
            addMatch() {
                this.createMatch(this.newMatch).then(x => this.getOne(this.$route.params.id));
            },
            addGame(match) {
                this.newGame.game_number = 1;
                if (match.games.length > 0){
                    this.newGame.game_number += parseInt(match.games[match.games.length - 1].game_number);
                    this.newGame.left_team = match.games[match.games.length - 1].left_team;
                    this.newGame.right_team = match.games[match.games.length - 1].right_team;
                }
                this.newGame.map = this.maps.items[0].id;
                this.newGame.match = match.id;
                console.log(this.newGame)
                this.createGame(this.newGame).then(x => this.getOne(this.$route.params.id));
            },
            addRound(game) {
                console.log('CLICKSDISJFSOIHG')
                this.newRound.vod = this.$route.params.id;
                this.newRound.begin = this.currentTime;
                this.newRound.end = this.currentTime;
                this.newRound.attacking_side = 'N';
                this.newRound.game = game.id;
                this.newRound.round_number = 1;
                if (game.rounds.length > 0){
                    this.newRound.round_number += parseInt(game.rounds[game.rounds.length - 1].round_number);
                }
                console.log(this.newRound)
                console.log(this.currentTime)
                this.selectedGame = {};
                this.selectedMatch = {};
                this.createRound(this.newRound).then(x => {
                    this.getOne(this.$route.params.id)
                });
            },
            updateRoundBegin(round) {
                round.begin = this.currentTime;
                this.updateRound({data: round, refresh: false});
            },
            updateRoundEnd(round) {
                round.end = this.currentTime;
                this.updateRound({data: round, refresh: false});
            },
            changeRound(round) {
                if (!round.round_number) {
                    return
                }
                this.updateRound({data: round, refresh: false});
            },
            changeGame(game) {
                if (!game.game_number) {
                    return
                }
                this.updateGame(game);
            },
            changeMatch(match) {
                this.updateMatch(match);
            },
            removeMatch(id) {
                this.deleteMatch(id).then(x => this.getOne(this.$route.params.id));
            },
            removeGame(id) {
                this.deleteGame(id).then(x => this.getOne(this.$route.params.id));
            },
            removeRound(id) {
                this.selectedGame = {};
                this.selectedMatch = {};
                this.deleteRound(id).then(x => this.getOne(this.$route.params.id));
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

    td.unclickable {
        background-color: darkgrey;
    }
</style>