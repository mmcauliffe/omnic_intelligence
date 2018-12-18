<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">
            <v-select v-model="newSwitch.player" :items="allPlayers"
                      item-text="name" item-value="id" label="Player">

            </v-select>

            <v-select v-model="newSwitch.new_hero" :items="availableHeroes"
                      item-text="name" item-value="id" label="New hero">

            </v-select>

            <v-btn class='primary raised' v-on:click="addSwitch">Add switch</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="switches" v-if="switches" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td>

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateSwitch(props.item)">access_time
                        </v-icon>
                        <span>Update time to current</span>
                    </v-tooltip>

                </td>
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>{{ props.item.player.name }}</td>
                <td>{{ props.item.new_hero.name }}</td>
                <td v-if="can_edit">

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="deleteSwitch(props.item.id)">
                            remove_circle
                        </v-icon>
                        <span>Remove</span>
                    </v-tooltip>
                </td>
            </template>
        </v-data-table>
    </div>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'

    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";
    import VSelect from "vuetify/es5/components/VSelect/VSelect";

    export default {
        name: "switches",
        components: {
            VSelect,
            VBtn,
            VIcon,
            VTooltip,
            VDataTable,
        },
        data() {
            return {
                newSwitch: {},
                availableHeroes: [],
                can_edit: true,
                event_type: 'switches',
                rowsPerPage: [10]
            }
        },
        computed: {
            ...mapState({
                account: state => state.account,
                round: state => state.rounds.one.item,
                timestamp: state => state.vods.timestamp,
            }),
            ...mapGetters('rounds', [
                'switches',
                'leftPlayers',
                'rightPlayers',
                'playerOnLeftTeam',
                'heroAtTime',
                'allPlayers'
            ]),
            currentTime() {
                return Math.round((this.timestamp - this.round.begin) * 10) / 10;
            },
        },
        created() {

            this.headers = [{
                text: '', sortable: false
            },
                {text: 'Time', sortable: false},
                {text: 'Player', sortable: false},
                {text: 'New hero', sortable: false},
                {text: 'Actions', sortable: false}];


        },
        methods: {
            ...mapActions('rounds', {
                getRoundEvents: 'getRoundEvents',
                addRoundEvent: 'addRoundEvent',
                deleteRoundEvent: 'deleteRoundEvent',
                updateRoundEvent: 'updateRoundEvent',
            }),
            ...mapActions('vods', {
                updateTimestamp: 'updateTimestamp',
            }),
            seekTo(time) {
                this.updateTimestamp(this.round.begin + time);
            },
            closeToCurrent(time) {
                return Math.abs(time - this.currentTime) < 1
            },
            addSwitch() {
                this.newSwitch.time_point = this.currentTime;
                this.newSwitch.round = this.$store.state.rounds.one.item.id;
                console.log(this.newSwitch)
                this.addRoundEvent({type: this.event_type, event: this.newSwitch}).then(
                    function (res) {
                        this.newSwitch = {};
                    });
            },
            updateSwitch(event) {
                event.time_point = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
            },
            deleteSwitch(event_id) {
                this.deleteRoundEvent({type: this.event_type, id: event_id});
            },
            generate_available_heroes(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.availableHeroes = []
                }
                let used_heroes = [];
                let players;
                if (this.playerOnLeftTeam(player_id)) {
                    players = this.leftPlayers;
                }
                else {
                    players = this.rightPlayers;
                }
                players.forEach(player => {
                    used_heroes.push(this.heroAtTime(player.id, this.currentTime).id)
                });
                console.log(used_heroes)
                this.availableHeroes = this.$store.state.overwatch.heroes.items.filter(function (h) {
                    return used_heroes.indexOf(h.id) === -1;
                });
            },
        },
        watch: {
            newSwitch(newNewSwitch) {
                if (newNewSwitch.player) {
                    console.log(newNewSwitch)

                    this.generate_available_heroes(newNewSwitch.player);
                    console.log(this.availableHeroes)
                }
            },
            timestamp(new_timestamp) {
                if (this.newSwitch.player) {

                    console.log(this.currentTime);
                    this.generate_available_heroes(this.newSwitch.player);
                }
            },
        }
    }
</script>

<style scoped>
    td.active {
        background-color: lightgreen;
    }

    td.clickable {
        cursor: pointer;
    }
</style>