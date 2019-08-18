<template>
    <v-layout column style="background-color: #1b2b3a;">

            <v-layout row justify-center>
        <table class="kill-feed-table">
            <tr v-for="item in kill_feed">
                <td class="first-hero" :class="item.first_color">
                <v-tooltip bottom v-if="item.first_hero != 'N/A'">
                    <img class="hero-icon" slot="activator"
                         :src="require('../../assets/'+ make_safe(item.first_hero) +'.png')"/>

                    <span>{{ item.first_hero}}</span>
                </v-tooltip>

                </td>
                <td class="assisting-heroes" :class="item.first_color">
                <v-tooltip v-for="h in item.assisting_heroes" v-bind:key="h" bottom>
                    <img class="hero-icon" slot="activator" :src="require('../../assets/'+ make_safe(h) +'.png')"/>

                    <span>{{ h }}</span>
                </v-tooltip>
                </td>
                <td class="ability">
                <v-tooltip bottom v-if="item.first_hero === 'N/A'">
                    <img class="hero-icon" slot="activator"
                         :src="require('../../assets/Primary.png')"/>
                    <span>death</span>
                </v-tooltip>
                <v-tooltip bottom v-else>
                    <img class="hero-icon" v-if="item.headshot" slot="activator"
                         :src="require('../../assets/'+ make_safe(item.ability) +' headshot.png')"/>
                    <img class="hero-icon" v-else slot="activator"
                         :src="require('../../assets/'+ make_safe(item.ability) +'.png')"/>

                    <span>{{ item.ability}}</span>
                </v-tooltip>

                </td>
                <td class="second-hero" :class="item.second_color">
                <v-tooltip bottom>
                    <img class="hero-icon" slot="activator"
                         :src="require('../../assets/'+ make_safe(item.second_hero) +'.png')"/>

                    <span>{{ item.second_hero}}</span>
                </v-tooltip>

                </td>
            </tr>
        </table>
            </v-layout>

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
        background-color: #000000;
    }
    .first-hero{
        width: 100px;
    }
    .ability {
        width:40px;
    }
    .second-hero{
        width:100px;
        text-align: right;
    }
    .Blue {
        background-color: #54fefd;
    }
    .Red {
        background-color: #ff122c;
    }
    .White {
        background-color: #ffffff;
    }
    .Green {
        background-color: #8cba11;
    }
    .Orange {
        background-color: #f99d2a;
    }
    .Yellow {
        background-color: #fedb00;
    }
    .Purple {
        background-color: #381460;
    }
    .Pink {
        background-color: #fb7299;
    }
    .Black {
        background-color: #000000;
    }
</style>