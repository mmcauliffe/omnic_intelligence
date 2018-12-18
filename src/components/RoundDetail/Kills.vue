<template>
    <div>

        <v-layout row v-if="can_edit">
            <div>
                <v-select v-model="newKill.killing_player" :items="allPlayers"
                          item-text="name" item-value="id" label="Killing player">

                </v-select>
            </div>
            <div>
                <v-select v-model="newKill.ability" :items="availableAbilities"
                          item-text="name" item-value="id" label="Ability">

                </v-select>
                <v-checkbox label="Headshot" v-model="newKill.headshot" :disabled="notHeadshotCapable">

                </v-checkbox>

                <v-btn class='primary raised' v-on:click="addKill">Add kill</v-btn>
            </div>
            <div>

                <v-select v-model="newKill.killed_player" :items="killablePlayers"
                          item-text="name" item-value="id" label="Killed player">

                </v-select>
            </div>
        </v-layout>
        <v-data-table :headers="headers" :items="kills" v-if="kills" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td>
                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateKill(props.item)">
                            access_time
                        </v-icon>
                        <span>Update time to current</span>
                    </v-tooltip>

                </td>
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>{{ props.item.killing_player }}</td>
                <td>
                    <v-select v-model="props.item.assisting_players" multiple chips deletable-chips
                              item-text="name" item-value="id" :items="props.item.possible_assists"
                     v-on:change="updateKill(props.item)">
                    </v-select>
                </td>
                <td>
                    <v-select v-model="props.item.ability.id"
                              item-text="name" item-value="id" :items="props.item.possible_abilities"
                     v-on:change="updateKill(props.item)">

                    </v-select>
                </td>
                <td>
                    <v-checkbox
                            v-model="props.item.headshot" :disabled="!props.item.ability.headshot_capable"
                     v-on:change="updateKill(props.item)">

                    </v-checkbox>
                </td>
                <td>{{ props.item.killed_player }}</td>
                <td v-if="can_edit">

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="deleteKill(props.item.id)">
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
    import VCheckbox from "vuetify/es5/components/VCheckbox/VCheckbox";

    export default {
        name: "switches",
        components: {
            VSelect,
            VCheckbox,
            VBtn,
            VIcon,
            VTooltip,
            VDataTable,
        },
        data() {
            return {
                newKill: {},
                availableAbilities: [],
                killablePlayers: [],
                can_edit: true,
                event_type: 'kills',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapState({
                account: state => state.account,
                round: state => state.rounds.one.item,
                timestamp: state => state.vods.timestamp,
            }),
            ...mapGetters('rounds', [
                'kills',
                'leftPlayers',
                'rightPlayers',
                'playerOnLeftTeam',
                'heroAtTime',
                'allPlayers',
            ]),
            ...mapGetters('overwatch', [
                'heroDamagingAbilities'
            ]),
            currentTime() {
                return Math.round((this.timestamp - this.round.begin) * 10) / 10;
            },
            notHeadshotCapable(){
                if (!this.newKill.ability){
                    return true;
                }
                let i;
                for (i=0; i< this.availableAbilities.length; i++){
                    if (this.availableAbilities[i].id == this.newKill.ability){
                        return !this.availableAbilities[i].headshot_capable
                    }
                }
                return true
            }
        },
        created() {

            this.headers = [
                {text: '', sortable: false, width: "5px"},
                {text: 'Time', sortable: false, width: "5px"},
                {text: 'Killing player', sortable: false},
                {text: 'Assists', sortable: false, width: "100px"},
                {text: 'Ability', sortable: false, width: "50px"},
                {text: 'Headshot', sortable: false, width: "5px"},
                {text: 'Killed player', sortable: false},
                {text: 'Actions', sortable: false, width: "5px"}];


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
            addKill() {
                console.log(this.newKill)
                this.newKill.time_point = this.currentTime;
                this.newKill.round = this.$store.state.rounds.one.item.id;
                console.log(this.newKill)
                this.addRoundEvent({type: this.event_type, event: this.newKill}).then(
                    function (res) {
                        this.newKill = {};
                    });
            },
            updateKill(event) {
                event.time_point = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
            },
            deleteKill(event_id) {
                this.deleteRoundEvent({type: this.event_type, id: event_id});
            },
            generate_available_abilities(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.availableAbilities = []
                }
                let current_hero = this.heroAtTime(player_id, this.currentTime);
                this.availableAbilities = this.heroDamagingAbilities(current_hero.id);
            },
            generate_killable_players(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.killablePlayers = []
                }
                if (this.playerOnLeftTeam(player_id)) {
                    this.killablePlayers = this.rightPlayers;
                }
                else {
                    this.killablePlayers = this.leftPlayers;
                }
            },
        },
        watch: {
            newKill: {
                    handler(newNewKill) {
                        if (newNewKill.killing_player) {
                            console.log(newNewKill);
                            this.generate_available_abilities(newNewKill.killing_player);
                            this.generate_killable_players(newNewKill.killing_player);
                            if (newNewKill.killed_player && this.killablePlayers.filter(player=>{return player.id === newNewKill.killed_player}).length === 0){
                                newNewKill.killed_player = undefined;
                            }
                            if (newNewKill.ability && this.availableAbilities.filter(ability=>{return ability.id === newNewKill.ability}).length === 0){

                                newNewKill.ability = undefined;
                                newNewKill.headshot = false;
                            }
                            console.log(this.availableAbilities)

                        }
                    },
                    deep: true
                },
            timestamp(new_timestamp) {
                if (this.newKill.killing_player) {
                    console.log(this.currentTime);
                    this.generate_available_abilities(this.newKill.killing_player);
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