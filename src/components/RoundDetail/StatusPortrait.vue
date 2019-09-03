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
        <span>{{ status.name}}</span><br>
        <v-layout row>
            <v-icon v-if="!status.alive">person_outline</v-icon>
            <v-icon v-else-if="status.status === 'frozen'">ac_unit</v-icon>
            <v-icon v-else-if="status.status === 'asleep'">notifications_paused</v-icon>
            <v-icon v-else-if="status.status === 'stunned'">star_rate</v-icon>
            <v-icon v-else-if="status.status === 'hacked'">wifi_lock</v-icon>
            <v-icon v-else>person</v-icon>
            <v-icon v-if="status.antiheal">block</v-icon>
            <v-icon v-if="status.immortal">android</v-icon>
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