<template>
    <v-layout row>
        <div class="vod-column" v-if="round.item">
        <StatusBar></StatusBar>
        <Vod :vod_type="round.item.stream_vod.vod_link[0]" :id="round.item.stream_vod.vod_link[1]"
             :round_begin="round.item.begin" :round_end="round.item.end"></Vod>
            <KillFeed></KillFeed>
        </div>
        <v-flex style="height:100%" xs4>
                <v-tabs md-border-bottom md-dynamic-height v-if="round.item">
                    <v-tab>
                        Round
                    </v-tab>
                    <v-tab>
                        Switches
                    </v-tab>
                    <v-tab>
                        Player
                    </v-tab>
                    <v-tab>
                        NPCs
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
                                            {{round.item.begin | secondsToMoment | moment('HH:mm:ss.S')}}
                                        </span>
                                            <v-btn class="raised" v-on:click="updateBegin">Update from current timestamp
                                            </v-btn>
                                        </div>
                                        <div>
                                            <label>End
                                            </label>
                                            <span>
                                                {{ round.item.end |secondsToMoment | moment('HH:mm:ss.S')}}
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
                                    <Deaths></Deaths>
                                    <StatusEffects></StatusEffects>
                                </v-card-text>
                            </v-card>

                        </v-tab-item>
                        <v-tab-item>
                            <v-card>
                                <v-card-text>


                                    <KillNPCs></KillNPCs>
                                    <NPCDeaths></NPCDeaths>
                                    <UltDenials></UltDenials>
                                </v-card-text>
                            </v-card>

                        </v-tab-item>
                        <v-tab-item>
                            <v-card>
                                <v-card-text>

                                    <Revives></Revives>

                                </v-card-text>
                            </v-card>

                        </v-tab-item>
                        <v-tab-item>
                            <v-card>
                                <v-card-text>

                                    <UltGains></UltGains>
                                    <UltUses></UltUses>
                                    <UltEnds></UltEnds>

                                </v-card-text>
                            </v-card>

                        </v-tab-item>
                        <v-tab-item>
                            <v-card>
                                <v-card-text>

                                    <PointGains v-if="round.item.game.map.mode!=='Control'"></PointGains>
                                    <PointFlips v-if="round.item.game.map.mode==='Control'"></PointFlips>
                                    <Overtimes></Overtimes>

                                </v-card-text>
                            </v-card>

                        </v-tab-item>
                        <v-tab-item>
                            <v-card>
                                <v-card-text>

                                    <Pauses></Pauses>
                                    <Replays></Replays>
                                    <SmallerWindows></SmallerWindows>

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
    import Switches from '../../components/RoundDetail/PointEvents/Switches';
    import Kills from '../../components/RoundDetail/PointEvents/Kills';
    import KillNPCs from '../../components/RoundDetail/PointEvents/KillNPCs';
    import Deaths from '../../components/RoundDetail/PointEvents/Deaths';
    import NPCDeaths from '../../components/RoundDetail/PointEvents/NPCDeaths';
    import Revives from '../../components/RoundDetail/PointEvents/Revives';
    import UltGains from '../../components/RoundDetail/PointEvents/UltGains';
    import UltUses from '../../components/RoundDetail/PointEvents/UltUses';
    import UltEnds from '../../components/RoundDetail/PointEvents/UltEnds';
    import UltDenials from '../../components/RoundDetail/PointEvents/UltDenials';
    import StatusEffects from '../../components/RoundDetail/IntervalEvents/StatusEffects';
    import PointGains from '../../components/RoundDetail/PointEvents/PointGains';
    import PointFlips from '../../components/RoundDetail/PointEvents/PointFlips';
    import Overtimes from '../../components/RoundDetail/IntervalEvents/Overtimes';
    import Pauses from '../../components/RoundDetail/IntervalEvents/Pauses';
    import Replays from '../../components/RoundDetail/IntervalEvents/Replays';
    import SmallerWindows from '../../components/RoundDetail/IntervalEvents/SmallerWindows';
    import StatusBar from '../../components/RoundDetail/StatusBar';
    import KillFeed from '../../components/RoundDetail/KillFeed';
    import {mapState, mapActions, mapGetters} from 'vuex'
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
    import VFlex from "vuetify/es5/components/VGrid/VFlex";
    import VLayout from "vuetify/es5/components/VGrid/VLayout";

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
            VLayout,
            VFlex,
            Vod,
            Switches,
            Kills,
            KillNPCs,
            Deaths,
            NPCDeaths,
            Revives,
            UltGains,
            UltUses,
            UltEnds,
            UltDenials,
            StatusEffects,
            PointGains,
            PointFlips,
            Overtimes,
            Pauses,
            Replays,
            SmallerWindows,
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
                timestamp: state => state.vods.timestamp,
            }),
        },
        created() {
            this.can_edit = true;
            this.getOne(this.$route.params.id);
            this.getSides();
            this.getHeroes();
            this.getNPCs();
            this.getAnnotationSources();
            this.getStatusEffectChoices();

            this.getPlayerStates(this.$route.params.id);
            this.getKillFeedEvents(this.$route.params.id);
            this.getRoundStates(this.$route.params.id);

            this.player_event_types = ['switches', 'kills', 'kill_npcs', 'deaths', 'npc_deaths', 'revives',
                'ult_gains', 'ult_uses', 'ult_ends', 'ult_denials', 'status_effects'];
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
                updateRound: 'updateRound',
                deleteRound: 'deleteRound',
            }),
            ...mapActions('overwatch', {
                getSides: 'getSides',
                getHeroes: 'getHeroes',
                getNPCs: 'getNPCs',
                getStatusEffectChoices: 'getStatusEffectChoices',
            }),
            ...mapActions('vods', {
                getAnnotationSources: 'getAnnotationSources',
                updateTimestamp: 'updateTimestamp',
            }),
            updateBegin() {
                this.round.item.begin = this.timestamp;

                this.updateRound({data:this.round.item, refresh:true});
            },
            updateEnd() {
                this.round.item.end = this.timestamp;

                this.updateRound({data:this.round.item, refresh:false});

            },
            saveRound() {
                this.updateRound({data:this.round.item, refresh:false});
            }
        },

        watch: {
            round(newRound) {
                if (newRound.item !== undefined){
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