<template>
    <div>
        <v-layout row>
            <div v-if="status.ult_state.state==='has_ult'">
                <v-tooltip bottom>
                    <v-icon slot="activator" @click="addUltUsePlayer(status.ult_state.id)"
                            :disabled="!can_edit">check_circle
                    </v-icon>
                    <span>Use ult</span></v-tooltip>

            </div>
            <div v-else-if="status.ult_state.state==='no_ult'">
                <v-tooltip bottom>
                    <v-icon slot="activator" @click="addUltGainPlayer(status.id)"
                            :disabled="!can_edit">check_circle_outline
                    </v-icon>
                    <span>Gain ult</span></v-tooltip>
            </div>
            <div v-else-if="status.ult_state.state==='using_ult'">
                <v-tooltip bottom>
                    <v-icon slot="activator"
                            :disabled="!can_edit">new_releases
                    </v-icon>
                    <span>Using ult</span></v-tooltip>
            </div>
            <v-tooltip bottom v-if="status.hero.name">
                <img class="hero-icon" slot="activator"
                     :src="require('../../assets/'+ make_safe(status.hero.name) +'.png')"/>

                <span>{{ status.hero.name}}</span>
            </v-tooltip>

        </v-layout>
            <v-tooltip bottom>
        <div class="caption text-no-wrap text-truncate" style="width: 60px;" slot="activator">{{ status.name}}</div>
                <span>{{ status.name}}</span>
            </v-tooltip>
        <v-layout row>

            <v-icon v-if="status.status === 'resurrecting'" small>call_merge</v-icon>
            <v-icon v-else-if="!status.alive" small>person_outline</v-icon>
            <v-icon v-else-if="status.status === 'frozen'" small>ac_unit</v-icon>
            <v-icon v-else-if="status.status === 'asleep'" small>notifications_paused</v-icon>
            <v-icon v-else-if="status.status === 'stunned'" small>stars</v-icon>
            <v-icon v-else-if="status.status === 'hacked'" small>wifi_lock</v-icon>
            <v-icon v-else-if="status.status === 'discord'" small>remove_circle</v-icon>
            <v-icon v-else small>person</v-icon>
            <v-icon v-if="status.antiheal" small>block</v-icon>
            <v-icon v-if="status.immortal" small>android</v-icon>
            <v-icon v-if="status.nanoboosted" small>trending_up</v-icon>
        </v-layout>
    </div>
</template>

<script>
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import VLayout from "vuetify/es5/components/VGrid/VLayout";
    import {mapState, mapActions, mapGetters} from 'vuex'


    export default {
        name: "status-portrait",
        props: ['status'],
        components: {
            VIcon,
            VTooltip,
            VLayout
        },
        computed:{
            ...mapState({
                timestamp: state => state.vods.timestamp,
                round: state => state.rounds.one.item,
            }),
            can_edit() {
                return true;
            },
            currentTime() {
                return  Math.round((this.timestamp - this.round.begin) * 10) / 10;
            },
        },
        methods: {
            ...mapActions('rounds', {
                addRoundEvent: 'addRoundEvent',
                addUltimateUse: 'addUltimateUse',
            }),
            addUltUsePlayer(ultimate_id) {
                this.addUltimateUse({id: ultimate_id, time_point: this.currentTime});

            },
            addUltGainPlayer(player_id) {

                let newEvent = {};
                newEvent.gained = this.currentTime;
                newEvent.round = this.$store.state.rounds.one.item.id;
                newEvent.player = player_id;
                this.addRoundEvent({type: 'ultimates', event: newEvent});
            },
            make_safe(name) {
                if (name !== undefined) {
                    return name.replace(':', '')
                }
                return ''
            },
        }
    }
</script>

<style scoped>

    .player {
        display: table-cell;
        height: 80px;
        width: 67px;
        padding-left: 10px;
        padding-right: 10px;
    }
    .hero-icon{
        height: 35px;
    }

</style>