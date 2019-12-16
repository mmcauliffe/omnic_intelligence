<template>
    <div>

        <v-layout layout="row" layout-align="space-between start" v-if="can_edit">
            <v-select v-model="newEvent.player" :items="allPlayers"
                      item-text="name" item-value="id" label="Player">

            </v-select>
            <v-btn class='primary raised' v-on:click="addEvent">Add ultimate gain</v-btn>
        </v-layout>
        <v-data-table :headers="headers" :items="ultimates" v-if="ultimates" :rows-per-page-items="rowsPerPage">

            <template slot="items" slot-scope="props">
                <td>
                    {{props.item.player.name}}
                </td>
                <td>

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateGainedAt(props.item)">access_time
                        </v-icon>
                        <span>Update ult gained to current</span>
                    </v-tooltip>

                </td>
                <td class="clickable" v-on:click="seekTo(props.item.gained)"
                    v-bind:class="{ active: closeToCurrent(props.item.gained) }">
                    {{ props.item.gained | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateUsedAt(props.item)">access_time
                        </v-icon>
                        <span>Update ult used to current</span>
                    </v-tooltip>

                </td>
                <td class="clickable" v-on:click="seekTo(props.item.used)"
                    v-bind:class="{ active: closeToCurrent(props.item.used) }">
                    {{ props.item.used | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td>

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="updateEndedAt(props.item)">access_time
                        </v-icon>
                        <span>Update ult end to current</span>
                    </v-tooltip>

                </td>
                <td class="clickable" v-on:click="seekTo(props.item.ended)"
                    v-bind:class="{ active: closeToCurrent(props.item.ended) }">
                    {{ props.item.ended | secondsToMoment | moment('mm:ss.S') }}
                </td>
                <td v-if="can_edit">

                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="clearUltimateUse({id: props.item.id})">
                            report_off
                        </v-icon>
                        <span>Clear use</span>
                    </v-tooltip>
                    <v-tooltip bottom>
                        <v-icon class="clickable" slot="activator" v-on:click="deleteEvent(props.item.id)">
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

    import {mapActions, mapGetters} from 'vuex'

    const interval_events = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['./BaseIntervalEvents'], () => {
            resolve(require('./BaseIntervalEvents'))
        })
    };
    const VSelect = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VSelect/VSelect'], () => {
            resolve(require('vuetify/es5/components/VSelect/VSelect'))
        })
    };

    export default {
        components: {VSelect},
        name: "ultimates",
        extends: interval_events,
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: 'ultimates',
                rowsPerPage: [15]
            }
        },
        computed: {
            ...mapGetters('rounds', [
                'ultimates',
                'allPlayers',
            ]),
            headers(){
                return [
                {text: 'Player', sortable: false},
                {text: '', sortable: false},
                {text: 'Gained', sortable: false},
                {text: '', sortable: false},
                {text: 'Used', sortable: false},
                {text: '', sortable: false},
                {text: 'Ended', sortable: false},
                {text: 'Actions', sortable: false}]
            }
        },
        methods: {
            ...mapActions('rounds', {
                clearUltimateUse: 'clearUltimateUse',
            }),
            addEvent() {
                this.newEvent.gained = this.currentTime;
                this.newEvent.round = this.$store.state.rounds.one.item.id;
                this.addRoundEvent({type: this.event_type, event: this.newEvent}).then(
                    function (res) {
                        this.newEvent = {};
                    });
            },
            updateGainedAt(event) {
                event.gained = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
            },
            updateUsedAt(event) {
                event.used = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
            },
            updateEndedAt(event) {
                event.ended = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
            },
            eventChangeHandler(newNewEvent) {
                console.log(newNewEvent)
            },
            timeChangeHandler(new_timestamp) {
                console.log(this.currentTime);
            },

        },
    }
</script>
