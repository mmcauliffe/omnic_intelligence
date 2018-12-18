<template>
    <v-layout row>
        <div class="vod-column" v-if="round.item">
        <StatusBar></StatusBar>
        <Vod :vod_type="round.item.stream_vod.vod_link[0]" :id="round.item.stream_vod.vod_link[1]"
             :round_begin="round.item.begin" :round_end="round.item.end"></Vod>
            <KillFeed></KillFeed>
        </div>
        <v-flex style="height:100%">
                <v-tabs md-border-bottom md-dynamic-height v-if="round.item">
                    <v-tab>
                        Round
                    </v-tab>
                    <v-tab>
                        Switches
                    </v-tab>
                    <v-tab>
                        Kills
                    </v-tab>
                    <v-tab>
                        Deaths
                    </v-tab>
                    <v-tab>
                        Revives
                    </v-tab>
                    <v-tab>
                        Ultimates
                    </v-tab>
                    <v-tab>
                        Points
                    </v-tab>
                    <v-tab>
                        Broadcast events
                    </v-tab>
                    <v-tabs-items>
                        <v-tab-item>
                            <v-card>
                                <v-card-title>
                                    <span class="headline mb-0">Round {{ round.item.round_number }} of Game {{ round.item.game.game_number }} ({{ round.item.game.map.name }})</span>

                                </v-card-title>
                                <v-card-text>
                                    <div>
                                        <p>{{round.item.stream_vod.title }}</p>
                                        <div>
                                            <label>Begin
                                            </label><span>
                                            {{round.item.begin | secondsToMoment | moment('HH:mm:ss')}}
                                        </span>
                                            <v-btn class="raised" v-on:click="updateBegin">Update from current timestamp
                                            </v-btn>
                                        </div>
                                        <div>
                                            <label>End
                                            </label>
                                            <span>
                                                {{ round.item.end |secondsToMoment | moment('HH:mm:ss')}}
                                            </span>
                                            <v-btn class="raised" v-on:click="updateEnd">Update from current timestamp
                                            </v-btn>
                                        </div>

                                        <v-select v-model="round.item.annotation_status"
                                                  v-on:change="saveRound" :items="annotation_sources"
                                                  item-text="name" item-value="id" label="Annotation status">
                                        </v-select>
                                        <v-select v-model="round.item.attacking_side"
                                                  v-on:change="saveRound" :items="sides"
                                                  item-text="name" item-value="id" label="Attacking side">

                                        </v-select>
                                        <v-btn class='raised primary' v-on:click="saveRound">Save</v-btn>
                                    </div>


                                </v-card-text>
                            </v-card>
                        </v-tab-item>
                        <v-tab-item>
                            <v-card>
                                <v-card-text>

                                    <Switches></Switches>

                                </v-card-text>
                            </v-card>

                        </v-tab-item>
                        <v-tab-item>
                            <v-card>
                                <v-card-text>

                                    <Kills></Kills>

                                </v-card-text>
                            </v-card>

                        </v-tab-item>
                    </v-tabs-items>


                </v-tabs>
        </v-flex>
    </v-layout>
</template>

<script>
    import Vod from '../../components/Vod';
    import Switches from '../../components/RoundDetail/Switches';
    import Kills from '../../components/RoundDetail/Kills';
    import StatusBar from '../../components/RoundDetail/StatusBar';
    import KillFeed from '../../components/RoundDetail/KillFeed';
    import {mapState, mapActions, mapGetters} from 'vuex'
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";
    import VInput from "vuetify/es5/components/VInput/VInput";
    import VTabs from "vuetify/es5/components/VTabs/VTabs";
    import VTab from "vuetify/es5/components/VTabs/VTab";
    import VCard from "vuetify/es5/components/VCard/VCard";
    import VSelect from "vuetify/es5/components/VSelect/VSelect";
    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import VTabsItems from "vuetify/es5/components/VTabs/VTabsItems";
    import VTabItem from "vuetify/es5/components/VTabs/VTabItem";

    export default {
        name: "round-detail-page",
        components: {
            VTabItem,
            VTabsItems,
            VSelect,
            VTabs,
            VTab,
            VCard,
            VBtn,
            VIcon,
            VTooltip,
            VInput,
            VDataTable,
            Vod,
            Switches,
            Kills,
            StatusBar,
            KillFeed,
        },

        computed: {
            ...mapState({
                account: state => state.account,
                round: state => state.rounds.one,
                events: state => state.rounds.events,
                annotation_sources: state => state.vods.annotation_sources.items,
                sides: state => state.overwatch.sides.items,
            }),
        },
        created() {
            this.can_edit = true;
            this.getOne(this.$route.params.id);
            this.getSides();
            this.getHeroes();
            this.getAnnotationSources();

            this.getPlayerStates(this.$route.params.id);
            this.getKillFeedEvents(this.$route.params.id);
            this.getRoundStates(this.$route.params.id);
            this.headers = {
                switches: [{text: ''}, {text: 'Time'}, {text: 'Player'}, {text: 'New hero'}, {text: 'Actions'}],
                kills: [{text: ''}, {text: 'Time'}, {text: 'Killing player'},
                    {text: 'Killed player'}, {text: 'Ability'}, {text: 'Headshot'}, {text: 'Assists'}, {text: 'Actions'}],
                kill_npcs: [{text: ''}, {text: 'Time'}, {text: 'Killing player'},
                    {text: 'Killed NPC'}, {text: 'Ability'}, {text: 'Assists'}, {text: 'Actions'}],
                deaths: [{text: ''}, {text: 'Time'}, {text: 'Player'}, {text: 'Actions'}],
                npc_deaths: [{text: ''}, {text: 'Time'}, {text: 'NPC'}, {text: 'Side'}, {text: 'Actions'}],
                revives: [{text: ''}, {text: 'Time'}, {text: 'Reviving player'},
                    {text: 'Revived player'}, {text: 'Ability'}, {text: 'Actions'}],
                ult_gains: [{text: ''}, {text: 'Time'}, {text: 'Player'}, {text: 'Actions'}],
                ult_uses: [{text: ''}, {text: 'Time'}, {text: 'Player'}, {text: 'Actions'}],

                pauses: [{text: ''}, {text: 'Begin'}, {text: 'End'}, {text: 'Actions'}],
                replays: [{text: ''}, {text: 'Begin'}, {text: 'End'}, {text: 'Actions'}],
                smaller_windows: [{text: ''}, {text: 'Begin'}, {text: 'End'}, {text: 'Actions'}],

                point_gains: [{text: ''}, {text: 'Time'}, {text: 'Point total'}, {text: 'Actions'}],
                point_flips: [{text: ''}, {text: 'Time'}, {text: 'Controlling side'}, {text: 'Actions'}],
                overtimes: [{text: ''}, {text: 'Begin'}, {text: 'End'}, {text: 'Actions'}],

            };
            this.player_event_types = ['switches', 'kills', 'kill_npcs', 'deaths', 'npc_deaths', 'revives', 'ult_gains', 'ult_uses'];
            this.round_event_types = ['overtimes', 'point_gains', 'point_flips'];
            this.broadcast_event_types = ['replays', 'pauses', 'smaller_windows'];

            this.player_event_types.forEach(type => {
                this.getRoundEvents({round: this.$route.params.id, type: type})
            });
            this.round_event_types.forEach(type => {
                this.getRoundEvents({round: this.$route.params.id, type: type})
            });
            this.broadcast_event_types.forEach(type => {
                this.getRoundEvents({round: this.$route.params.id, type: type});
            });
        },
        methods: {
            ...mapActions('rounds', {
                getOne: 'getOne',
                getRoundEvents: 'getRoundEvents',
                getKillFeedEvents: 'getKillFeedEvents',
                getPlayerStates: 'getPlayerStates',
                getRoundStates: 'getRoundStates',
                delete: 'delete',
            }),
            ...mapActions('overwatch', {
                getSides: 'getSides',
                getHeroes: 'getHeroes',
            }),
            ...mapActions('vods', {
                getAnnotationSources: 'getAnnotationSources',
                updateTimestamp: 'updateTimestamp',
            }),
            seekTo(time) {
                console.log(time)
            },
            updateBegin() {

            },
            updateEnd() {

            },
            saveRound() {
            }
        },

        watch: {
            round(newRound) {
                if (newRound.item !== undefined){
                    console.log(newRound)
                    this.updateTimestamp(newRound.item.begin);

                }
            },
        }
    }
</script>

<style scoped>
.vod-column {
    width:1280px;
}
</style>