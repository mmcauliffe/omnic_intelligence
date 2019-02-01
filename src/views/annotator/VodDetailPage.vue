<template>

    <v-layout row>
        <div class="vod-column" v-if="vod.item">
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
                <v-flex>
                    <v-select label="Match" :items="matches.items" v-model="match"
                              item-text="name" item-value="id" v-on:change="updateGames()"></v-select>
                    <v-select label="Game" v-model="newRound.game" :items="games.items" item-text="name" item-value="id"></v-select>
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
                            <router-link :to="{name: 'match-detail', params:{id: props.item.game.match.id}}">
                                {{ props.item.game.match.teams[0] }} vs {{ props.item.game.match.teams[1] }}
                            </router-link>
                        </td>
                        <td>
                            <router-link :to="{name: 'game-detail', params:{id: props.item.game.id}}">
                                Game {{ props.item.game.game_number }} ({{props.item.game.map.name}})
                            </router-link>
                        </td>
                        <td>
                            <router-link :to="{name: 'round-detail', params:{id: props.item.id}}">
                                Round {{ props.item.round_number }}
                            </router-link>
                        </td>
                        <td>
                            {{ props.item.attacking_side }}
                        </td>
                        <td class="clickable" v-on:click="seekTo(props.item.begin)"
                            v-bind:class="{ active: closeToCurrent(props.item.begin) }">
                            {{ props.item.begin | secondsToMoment | moment('mm:ss.S') }}
                        </td>
                        <td class="clickable" v-on:click="seekTo(props.item.end)"
                            v-bind:class="{ active: closeToCurrent(props.item.end) }">
                            {{ props.item.end | secondsToMoment | moment('mm:ss.S') }}
                        </td>
                        <td>
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
                        </td>
                    </template>
                </v-data-table>
                </v-flex>
            </v-layout>
        </v-flex>
    </v-layout>
</template>

<script>
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";
    import Vod from '../../components/Vod';
    import {mapState, mapActions, mapGetters} from 'vuex'
    import VTextField from "vuetify/es5/components/VTextField/VTextField";

    export default {
        name: "vod-detail-page",
        components: {
            VTextField,
            Vod,
            VDataTable
        },
        data(){
            return {
                newRound: {},
                match: 0,
                rowsPerPage: [10]
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
                matches: state => state.vods.vod_event_matches,
                games: state => state.matches.games,
                rounds: state => state.vods.rounds,
            }),
            currentTime() {
                return Math.round((this.timestamp) * 10) / 10;
            },
            headers() {
                return [
                    {text: 'Match', sortable: false},
                    {text: 'Game', sortable: false},
                    {text: 'Round', sortable: false},
                    {text: 'Attacking side', sortable: false},
                    {text: 'Begin', sortable: false},
                    {text: 'End', sortable: false},
                    {text: 'Actions', sortable: false}]
            }
        },
        created() {
            this.can_edit = true;
            this.getOne(this.$route.params.id);
            this.getOneMatches(this.$route.params.id);
            this.getOneRounds(this.$route.params.id);
            this.getVodStatusChoices();
            this.getVodTypeChoices();
            this.getSides();
        },
        methods: {
            ...mapActions('vods', {
                getOne: 'getOne',
                getOneMatches: 'getOneMatches',
                getOneRounds: 'getOneRounds',
                updateVod: 'updateVod',
                deleteVod: 'deleteVod',
                updateTimestamp: 'updateTimestamp',
                getVodStatusChoices: 'getVodStatusChoices',
                getVodTypeChoices: 'getVodTypeChoices',
            }),
            ...mapActions('overwatch', {
                getSides: 'getSides'
            }),
            ...mapActions('rounds', {
                createRound: 'createRound',
                updateRound: 'updateRound',
            }),
            ...mapActions('matches', {
                getOneGames: 'getOneGames',
            }),
            update_vod() {
                this.updateVod(this.vod.item);
            },
            closeToCurrent(time) {
                return Math.abs(time - this.currentTime) < 1
            },
            seekTo(time) {
                this.updateTimestamp(time);
            },
            updateGames(){
                this.getOneGames(this.match);
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