<template>
<div></div>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'

    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";
    import VSelect from "vuetify/es5/components/VSelect/VSelect";
    import VCheckbox from "vuetify/es5/components/VCheckbox/VCheckbox";
    import VInput from "vuetify/es5/components/VInput/VInput";
    import VFlex from "vuetify/es5/components/VGrid/VFlex";
    import VLayout from "vuetify/es5/components/VGrid/VLayout";

    export default {
        name: "events",
        components: {
            VSelect,
            VInput,
            VBtn,
            VIcon,
            VTooltip,
            VDataTable,
            VCheckbox,
            VLayout,
            VFlex
        },
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: '',
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
                'leftPlayers',
                'rightPlayers',
                'playerOnLeftTeam',
                'heroAtTime',
                'allPlayers',
            ]),
            ...mapGetters('overwatch', [
                'sides',
                'status_effect_choices',
                'heroDamagingAbilities',
                'heroDeniableAbilities',
                'heroRevivingAbilities',
                'availableNPCs'
            ]),
            currentTime() {
                return Math.round((this.timestamp - this.round.begin) * 10) / 10;
            },
            headers() {
                return [];
            }
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
            addEvent() {
                this.newEvent.time_point = this.currentTime;
                this.newEvent.round = this.$store.state.rounds.one.item.id;
                console.log(this.newEvent)
                this.addRoundEvent({type: this.event_type, event: this.newEvent}).then(
                    function (res) {
                        this.newEvent = {};
                    });
            },
            updateEvent(event) {
                event.time_point = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
            },
            deleteEvent(event_id) {
                this.deleteRoundEvent({type: this.event_type, id: event_id});
            },
            eventChangeHandler(newNewEvent) {
                console.log(newNewEvent)
            },
            timeChangeHandler(new_timestamp) {
                console.log(this.currentTime);
            },


            generate_available_abilities(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.availableAbilities = []
                }
                let current_hero = this.heroAtTime(player_id, this.currentTime);
                this.availableAbilities = this.heroDamagingAbilities(current_hero.id);
            },
            generate_revivable_abilities(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.availableAbilities = []
                }
                let current_hero = this.heroAtTime(player_id, this.currentTime);
                this.availableAbilities = this.heroRevivingAbilities(current_hero.id);
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
            generate_revivable_players(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.revivablePlayers = []
                }
                if (this.playerOnLeftTeam(player_id)) {
                    this.revivablePlayers = this.leftPlayers.filter(x=> x.id !== player_id);
                }
                else {
                    this.revivablePlayers = this.rightPlayers.filter(x=> x.id !== player_id);
                }
            },
            generate_killable_npcs(player_id) {
                console.log(this.currentTime, player_id)
                let hero_ids;
                if (!this.currentTime || !player_id) {
                    this.killableNPCs = []
                }
                if (this.playerOnLeftTeam(player_id)) {
                    hero_ids = this.rightPlayers.map(x => {return this.heroAtTime(x.id, this.currentTime).id});
                }
                else {
                    hero_ids = this.leftPlayers.map(x => {return this.heroAtTime(x.id, this.currentTime).id});
                }
                this.killableNPCs = this.availableNPCs(hero_ids)
                console.log('killable npcs', this.killableNPCs)
            },
        },
        watch: {
            newEvent: {
                handler(newNewEvent) {
                    this.eventChangeHandler(newNewEvent);

                },
                deep: true
            },
            timestamp(new_timestamp) {
                this.timeChangeHandler(new_timestamp);
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