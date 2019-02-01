<template>
    <v-layout column style="background-color: #1b2b3a;">
        <div v-for="item in kill_feed">

            <v-layout row justify-center>

            <div class="first-hero text-xs-left" :class="item.first_color">
                <v-tooltip bottom v-if="item.first_hero != 'N/A'">
                    <img class="hero-icon" slot="activator"
                         :src="require('../../assets/'+ make_safe(item.first_hero) +'.png')"/>

                    <span>{{ item.first_hero}}</span>
                </v-tooltip>
                <v-tooltip v-for="h in item.assisting_heroes" v-bind:key="h" bottom>
                    <img class="hero-icon" slot="activator" :src="require('../../assets/'+ make_safe(h) +'.png')"/>

                    <span>{{ h }}</span>
                </v-tooltip>

            </div>
            <div class="ability text-xs-center">
                <v-tooltip bottom v-if="item.first_hero === 'N/A'|| item.ability === 'Primary' || item.ability === 'Melee'">
                    <v-icon slot="activator" color="red" v-if="item.headshot">arrow_right_alt</v-icon>
                    <v-icon slot="activator" color="white" v-else>arrow_right_alt</v-icon>
                    <span>{{ item.ability}}</span>
                </v-tooltip>
                <v-tooltip bottom v-if="item.first_hero !== 'N/A' &&item.ability !== 'Primary' && item.ability !== 'Melee'">
                    <img class="hero-icon" slot="activator"
                         :src="require('../../assets/'+ make_safe(item.ability) +'.png')"/>

                    <span>{{ item.ability}}</span>
                </v-tooltip>

            </div>
            <div class="second-hero text-xs-right" :class="item.second_color">
                <v-tooltip bottom>
                    <img class="hero-icon" slot="activator"
                         :src="require('../../assets/'+ make_safe(item.second_hero) +'.png')"/>

                    <span>{{ item.second_hero}}</span>
                </v-tooltip>

            </div>
            </v-layout>

        </div>
    </v-layout>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'

    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";


    export default {
        name: "kill-feed",
        components: {
            VBtn,
            VIcon,
            VTooltip,
            VDataTable,
        },

        data: function () {
            return {
                headers: [
                    {text: "Time"},
                    {text: "Acting hero"},
                    {text: "Assists"},
                    {text: "Ability"},
                    {text: "Dying entity"},
                ]
            }
        },
        computed: {
            ...mapState({
                kill_feed_events: state => state.rounds.kill_feed_events.item,
                timestamp: state => state.vods.timestamp,
                round: state => state.rounds.one.item,
            }),
            ...mapGetters('rounds', [
                'killFeedAtTime',
            ]),
            kill_feed() {
                return this.killFeedAtTime(this.currentTime);
            },
            currentTime() {
                return Math.round((this.timestamp - this.round.begin) * 10) / 10
            },
        },

        methods: {
            make_safe(name) {
                return name.replace(':', '').replace('!', '')
            },
        }
    }
</script>

<style scoped>

    .hero-icon {
        height: 40px;
    }
    .first-hero{
        width: 150px;
    }
    .ability {
        width:50px;
    }
    .second-hero{
        width:100px;
    }
    .Red {
        background-color: #ff122c;
    }
    .Blue {
        background-color: #54fefd;
    }
</style>