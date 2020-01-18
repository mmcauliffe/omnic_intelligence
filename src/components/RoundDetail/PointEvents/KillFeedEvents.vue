<template>
    <div>

        <v-layout column v-if="can_edit">
            <v-layout row flex-nowrap>
            <v-select v-model="eventType" :items="kill_feed_types" label="Event type"></v-select>
                <v-flex><v-select v-model="newEvent.killing_player" :items="allPlayers"
                          item-text="name" item-value="id" :label="killing_player_label" v-if="eventType !== 'death'">

                </v-select></v-flex>
                <v-flex>
                <v-select v-model="newEvent.ability" :items="availableAbilities"
                          item-text="name" item-value="id" label="Ability" v-if="eventType !== 'death'">

                </v-select>

                </v-flex>

                <v-checkbox label="Headshot" v-model="newEvent.headshot" :disabled="notHeadshotCapable" v-if="eventType === 'kill'">

                </v-checkbox>

                <v-select v-model="newEvent.dying_player" :items="killablePlayers"
                          item-text="name" item-value="id" :label="dying_player_label">

                </v-select>
                <v-select v-model="newEvent.dying_npc" :items="killableNPCs"
                          item-text="name" item-value="id" label="NPC" v-if="(eventType==='kill' || eventType === 'death') && killableNPCs.length > 0">

                </v-select>
                <v-select v-model="newEvent.denied_ult" :items="deniableAbilities"
                          item-text="name" item-value="id" label="Ultimate" v-if="eventType === 'deny'">

                </v-select>
            </v-layout>
                <v-btn class='primary raised' v-on:click="addEvent">Add event</v-btn>

        </v-layout>
        <v-data-table :headers="headers" :items="kill_feed_events" v-if="kill_feed_events" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td class="clickable" v-on:click="seekTo(props.item.time_point)"
                    v-bind:class="{ active: closeToCurrent(props.item.time_point) }">
                    {{ props.item.time_point | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>
                    <v-select v-model="props.item.killing_player" dense single-line
                              item-text="name" item-value="id" :items="possible_killers(props.item.dying_player, props.item.ability)" clearable
                     v-on:change="updateEvent(props.item)">
      <template slot="selection" slot-scope="{ item, index }">
          <span class="caption text-no-wrap text-truncate" style="max-width: 67px;">{{ item.name }}</span>
      </template>
                    </v-select>
                </td>
                <td>

                    <v-select v-if="props.item.ability && props.item.ability.type==='D'
                    && props.item.killing_player && playerOnLeftTeam(props.item.dying_player.id)"
                              v-model="props.item.assists" multiple dense single-line
                              item-text="name" item-value="id" :items="rightPlayers.filter(x=>{return x.id !== props.item.killing_player})"
                     v-on:change="updateEvent(props.item)">
                          <template slot="selection" slot-scope="{ item, index }">
          <span v-if="props.item.assists.length === 1 && index === 0"
          class="caption text-no-wrap text-truncate" style="max-width: 67px;">
              {{ item.name }}
          </span>
        <span
          v-else-if="props.item.assists.length !== 1 && index === 0"
          class="caption text-no-wrap text-truncate" style="max-width: 67px;">
            {{ props.item.assists.length}} assists
        </span>
      </template>
                    </v-select>
                    <v-select v-else-if="props.item.ability && props.item.ability.type==='D'
                    && props.item.killing_player && !playerOnLeftTeam(props.item.dying_player.id)"
                              v-model="props.item.assists" multiple dense single-line
                              item-text="name" item-value="id" :items="leftPlayers.filter(x=>{return x.id !== props.item.killing_player})"
                     v-on:change="updateEvent(props.item)">
                          <template slot="selection" slot-scope="{ item, index }">
          <span v-if="props.item.assists.length === 1 && index === 0"
                class="caption text-no-wrap text-truncate" style="max-width: 67px;">
              {{ item.name }}
          </span>
        <span
          v-else-if="props.item.assists.length !== 1 && index === 0"
          class="caption text-no-wrap text-truncate" style="max-width: 67px;">
            {{ props.item.assists.length}} assists
        </span>
      </template>
                    </v-select>
                </td>
                <td>
                    <v-layout row flex-nowrap v-if="props.item.killing_player && props.item.ability && props.item.ability.type==='D'">
                    <v-select v-model="props.item.ability.id" dense single-line
                              item-text="name" item-value="id" :items="heroDamagingAbilities(heroAtTime(props.item.killing_player, props.item.time_point).id)"
                     v-on:change="updateEvent(props.item)">
      <template slot="selection" slot-scope="{ item, index }">
          <span class="caption text-no-wrap text-truncate" style="max-width: 120px;">{{ item.name }}</span>
      </template>

                    </v-select>
                    <v-checkbox
                            v-model="props.item.headshot" v-if="props.item.ability.headshot_capable" dense
                     v-on:change="updateEvent(props.item)">

                    </v-checkbox>

                    </v-layout>
                    <v-layout row v-else-if="props.item.killing_player && props.item.ability && props.item.ability.type==='E'">
                    <v-select v-model="props.item.ability.id" dense single-line
                              item-text="name" item-value="id" :items="heroDenyingAbilities(heroAtTime(props.item.killing_player, props.item.time_point).id)"
                     v-on:change="updateEvent(props.item)">
      <template slot="selection" slot-scope="{ item, index }">
          <span class="caption text-no-wrap text-truncate" style="max-width: 120px;">{{ item.name }}</span>
      </template>

                    </v-select>

                    </v-layout>
                    <v-layout row v-else-if="props.item.killing_player && props.item.ability">
                        <span>{{props.item.ability.name}}</span>
                    </v-layout>
                </td>
                <td>
                    <div class="caption text-no-wrap text-truncate" style="max-width: 67px;">
                        {{ props.item.dying_player.name }}
                    </div>
                    <div v-if="!(props.item.ability && ['R', 'E'].indexOf(props.item.ability.type) !== -1)
                        && heroNPCs(heroAtTime(props.item.dying_player.id, props.item.time_point).id).length > 0">

                    <v-select v-model="props.item.dying_npc" clearable dense single-line
                              item-text="name" item-value="id" :items="heroNPCs(heroAtTime(props.item.dying_player.id, props.item.time_point).id)"
                     v-on:change="updateEvent(props.item)">
      <template slot="selection" slot-scope="{ item, index }">
          <span class="caption text-no-wrap text-truncate" style="max-width: 67px;">{{ item.name }}</span>
      </template>

                    </v-select>
                    </div>
                    <div v-if="props.item.denied_ult" class="caption text-no-wrap text-truncate" style="max-width: 67px;">
                    {{props.item.denied_ult}}
                    </div>
                </td>
                <td v-if="can_edit">

        <v-layout layout="row" layout-align="space-between">
                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateEvent(props.item)">
                            access_time
                        </v-icon>
                        <span>Update time to current</span>
                    </v-tooltip>
            <v-flex></v-flex>
                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="deleteEvent(props.item.id)">
                            remove_circle
                        </v-icon>
                        <span>Remove</span>
                    </v-tooltip>
        </v-layout>
                </td>
            </template>
        </v-data-table>
    </div>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'

    import events from './BaseRoundEvents';
    import VSelect from "vuetify/es5/components/VSelect/VSelect";

    export default {
        components: {VSelect},
        name: "kill_feed_events",
        extends: events,
        data() {
            return {
                newEvent: {},
                eventType: 'kill',
                killing_player_label: 'Killing player',
                dying_player_label: 'Killed player',
                availableAbilities: [],
                killablePlayers: [],
                killableNPCs: [],
                deniableAbilities: [],
                kill_feed_types: ['kill', 'death', 'deny', 'revive'],
                can_edit: true,
                event_type: 'kill_feed_events',
                rowsPerPage: [10]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'kill_feed_events',
            ]),
            ...mapGetters('overwatch', [
                'denying_heroes',
                'heroNPCs'
            ]),
            notHeadshotCapable(){
                if (!this.newEvent.ability){
                    return true;
                }
                let i;
                for (i=0; i< this.availableAbilities.length; i++){
                    if (this.availableAbilities[i].id == this.newEvent.ability){
                        return !this.availableAbilities[i].headshot_capable
                    }
                }
                return true
            },
            headers(){
                return [
                {text: 'Time', sortable: false, width: "5px"},
                {text: 'Killing player', sortable: false, width:"100px"},
                {text: 'Assists', sortable: false, width: "200px"},
                {text: 'Ability', sortable: false},
                {text: 'Killed player', sortable: false, width:"100px"},
                {text: 'Actions', sortable: false, width: "5px"}];
            }
        },
        methods: {
            resetEvent(){
                this.newEvent = {};
            },
            addEvent() {
                this.newEvent.time_point = this.currentTime;
                this.newEvent.event_type = this.eventType;
                this.newEvent.round = this.$store.state.rounds.one.item.id;
                console.log(this.newEvent)
                this.addRoundEvent({type: this.event_type, event: this.newEvent}).then(this.resetEvent);
            },
            possible_killers(dying_player, ability){
                if (ability && ability.type === 'R'){
                    if ( this.playerOnLeftTeam(dying_player.id)){
                        return this.leftPlayers;
                    }
                    else{
                        return this.rightPlayers;
                    }

                }
                else{
                    if ( this.playerOnLeftTeam(dying_player.id)){
                        return this.rightPlayers;
                    }
                    else{
                        return this.leftPlayers;
                    }
                }

            },
            generate_deniable_abilities(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.deniableAbilities = []
                }
                let current_hero = this.heroAtTime(player_id, this.currentTime);
                this.deniableAbilities = this.heroDeniableAbilities(current_hero.id);
                console.log('DENIABLE', this.deniableAbilities)
            },

            generate_denying_abilities(player_id) {
                console.log(this.currentTime, player_id)
                if (!this.currentTime || !player_id) {
                    this.availableAbilities = []
                }
                let current_hero = this.heroAtTime(player_id, this.currentTime);
                this.availableAbilities = this.heroDenyingAbilities(current_hero.id);

            },
            generate_dyable_players() {
                this.killablePlayers = this.allPlayers;
            },
            eventChangeHandler(newNewEvent){
                this.generate_dyable_players();
                if (newNewEvent.killing_player) {
                    console.log(newNewEvent);
                    if (this.eventType === 'revive'){
                        this.generate_revivable_players(newNewEvent.killing_player);
                        this.generate_revivable_abilities(newNewEvent.killing_player)
                    }
                    else if (this.eventType === 'deny'){
                        this.generate_denying_abilities(newNewEvent.killing_player);
                        this.generate_killable_players(newNewEvent.killing_player);
                    }
                    else if (this.eventType === 'kill'){

                    this.generate_available_abilities(newNewEvent.killing_player);
                    this.generate_killable_players(newNewEvent.killing_player);
                    }
                    if (newNewEvent.dying_player && this.killablePlayers.filter(player=>{return player.id === newNewEvent.dying_player}).length === 0){
                        newNewEvent.dying_player = undefined;
                    }
                    if (newNewEvent.ability && this.availableAbilities.filter(ability=>{return ability.id === newNewEvent.ability}).length === 0){

                        newNewEvent.ability = undefined;
                        newNewEvent.headshot = false;
                    }
                    console.log(this.availableAbilities)

                }
                if (newNewEvent.dying_player){

                    if (this.eventType === 'deny'){
                        this.generate_deniable_abilities(newNewEvent.dying_player)
                    }
                    else if (this.eventType === 'kill' || this.eventType === 'death'){
                        this.generate_killable_npcs(newNewEvent.dying_player)
                    }
                }
            },
            timeChangeHandler(new_timestamp){
                    if (this.newEvent.killing_player) {
                    console.log(this.currentTime);
                    this.generate_available_abilities(this.newEvent.killing_player);
                }
            }
        },
        watch: {
            eventType: {
                handler(newEventType) {
                    this.newEvent = {};
                    if (newEventType === 'deny') {

                        this.killing_player_label = 'Denying player';
                        this.dying_player_label = 'Denied player';
                    }
                    else if (newEventType === 'kill') {

                        this.killing_player_label = 'Killing player';
                        this.dying_player_label = 'Killed player';
                    }
                    else if (newEventType === 'death') {

                        this.killing_player_label = '';
                        this.dying_player_label = 'Dying player';
                    }
                    else if (newEventType === 'revive') {

                        this.killing_player_label = 'Reviving player';
                        this.dying_player_label = 'Revived player';
                    }

                }
            },
        }
    }
</script>
