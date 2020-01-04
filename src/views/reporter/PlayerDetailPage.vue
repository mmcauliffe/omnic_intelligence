<template>
    <v-layout row flex-nowrap>
        <v-flex xs8>

            <v-card v-if="stats">
                <v-card-title>
                    <span class="headline mb-0">Statistics (per 10 minutes)</span>
                </v-card-title>
                <v-card-text>

                    <v-data-table :headers="stats_headers" :items="stats.stats"
                                  :rows-per-page-items="stat_row_count" hide-headers hide-actions>

                        <template slot="items" slot-scope="props">
                            <td>
                                {{ props.item.name }}
                            </td>
                            <td>
                                {{ props.item.value }}
                            </td>
                        </template>
                    </v-data-table>

                </v-card-text>
            </v-card>
            <v-card v-if="stats">
                <v-card-title>
                    <span class="headline mb-0">Hero play time</span>
                </v-card-title>
                <v-card-text>

                    <v-flex>
                    <v-data-table :headers="playtime_headers" :items="stats.hero_play_time"
                                  :rows-per-page-items="stat_row_count" hide-headers hide-actions>

                        <template slot="items" slot-scope="props">
                            <td>
                <img style="width: 32px;height:32px" class="hero-icon" slot="activator"
                     :src="require('../../assets/'+ make_safe(props.item.name) +'.png')"/>
                                {{ props.item.name }}
                            </td>
                            <td>
                                {{ props.item.value |secondsToMoment | moment('DD:HH:mm:ss.S') }}
                            </td>
                        </template>
                    </v-data-table>
                        </v-flex>
                </v-card-text>
            </v-card>
        </v-flex>
        <v-flex v-if="player" xs4>
            <v-card>
                <v-card-title>
                    <span class="headline mb-0">{{player.name}}</span>
                </v-card-title>
                <v-card-text>


                    <v-data-table :headers="team_headers" :items="teams" v-if="teams"
                                  :rows-per-page-items="team_row_count" hide-headers hide-actions>

                        <template slot="items" slot-scope="props">
                            <td>
                                <router-link :to="{name: 'team-detail', params: {id: props.item.team.id}}">{{
                                    props.item.team.name }}
                                </router-link>
                            </td>
                            <td>
                                {{ props.item.start }}
                            </td>
                            <td>
                                {{ props.item.end }}
                            </td>
                        </template>
                    </v-data-table>
                </v-card-text>
            </v-card>
            <v-card v-if="recent_matches">
                <v-card-title >
                    <span class="headline mb-0">Recent matches</span>
                </v-card-title>
                <v-card-text>
                    <v-data-table :headers="match_headers" :items="recent_matches"
                                  :rows-per-page-items="match_row_count">

                        <template slot="items" slot-scope="props">
                            <td>
                                <router-link :to="{name: 'match-detail', params: {id: props.item.id}}">{{
                                    props.item.name }}
                                </router-link>
                            </td>
                            <td>
                                <router-link :to="{name: 'event-detail', params: {id: props.item.event.id}}">{{
                                    props.item.event.name }}
                                </router-link>
                            </td>
                            <td>
                                {{props.item.date}}
                            </td>
                        </template>
                    </v-data-table>
                </v-card-text>
            </v-card>
        </v-flex>
    </v-layout>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'

    export default {
        name: "player-page",

        data() {
            return {
                team_row_count: [50],
                match_row_count: [5],
                stat_row_count: [50]
            }
        },

        computed: {
            ...mapState({
                account: state => state.account,
                player: state => state.players.one.item,
                stats: state => state.players.stats.item,
                recent_matches: state => state.players.recent_matches.item,
                teams: state => state.players.teams.item,
            }),
            team_headers() {
                return [
                    {text: 'Team', sortable: false},
                    {text: 'Start date', sortable: false},
                    {text: 'End date', sortable: false},
                ];
            },
            match_headers() {
                return [
                    {text: 'Match', sortable: false},
                    {text: 'Event', sortable: false},
                    {text: 'Date', sortable: false},
                ];
            },
            stats_headers() {
                return [
                    {text: 'Stat', sortable: false, width: '50px'},
                    {text: 'Value', sortable: false, width: '50px'},
                ];
            },
            playtime_headers() {
                return [
                    {text: 'Hero', sortable: false},
                    {text: 'Playtime', sortable: false},
                ];
            },
        },
        created() {
            this.can_edit = true;
            this.getPlayer(this.$route.params.id);
            this.getPlayerStatistics(this.$route.params.id);
            this.getPlayerRecentMatches(this.$route.params.id);
            this.getPlayerTeams(this.$route.params.id);
        },
        methods: {
            make_safe(name) {
                if (name !== undefined) {
                    return name.replace(':', '')
                }
                return ''
            },
            ...mapActions('players', {
                getPlayer: 'getPlayer',
                getPlayerStatistics: 'getPlayerStatistics',
                getPlayerRecentMatches: 'getPlayerRecentMatches',
                getPlayerTeams: 'getPlayerTeams',
            }),
        },
    }
</script>

<style scoped>

</style>