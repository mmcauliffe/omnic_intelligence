<template>

</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'
    const VDataTable = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VDataTable/VDataTable'], () => {
            resolve(require('vuetify/es5/components/VDataTable/VDataTable'))
        })
    };
    const VBtn = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VBtn/VBtn'], () => {
            resolve(require('vuetify/es5/components/VBtn/VBtn'))
        })
    };
    const VIcon = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VIcon/VIcon'], () => {
            resolve(require('vuetify/es5/components/VIcon/VIcon'))
        })
    };
    const VTooltip = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTooltip/VTooltip'], () => {
            resolve(require('vuetify/es5/components/VTooltip/VTooltip'))
        })
    };
    const VSelect = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VSelect/VSelect'], () => {
            resolve(require('vuetify/es5/components/VSelect/VSelect'))
        })
    };
    const VCheckbox = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VCheckbox/VCheckbox'], () => {
            resolve(require('vuetify/es5/components/VCheckbox/VCheckbox'))
        })
    };
    const VInput = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VInput/VInput'], () => {
            resolve(require('vuetify/es5/components/VInput/VInput'))
        })
    };


    export default {
        name: "interval_events",
        components: {
            VSelect,
            VInput,
            VBtn,
            VIcon,
            VTooltip,
            VDataTable,
            VCheckbox
        },
        data() {
            return {
                newEvent: {},
                can_edit: true,
                event_type: '',
                rowsPerPage: [5]
            }
        },
        computed: {
            ...mapState({
                account: state => state.account,
                round: state => state.rounds.one.item,
                timestamp: state => state.vods.timestamp,
            }),
            ...mapGetters('overwatch', [
                'sides'
            ]),
            currentTime() {
                return Math.round((this.timestamp - this.round.begin) * 10) / 10;
            },
            headers(){
                return [
                {text: '', sortable: false},
                {text: 'Start time', sortable: false},
                {text: '', sortable: false},
                {text: 'End time', sortable: false},
                {text: 'Actions', sortable: false}]
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
                this.newEvent.start_time = this.currentTime;
                this.newEvent.round = this.$store.state.rounds.one.item.id;
                console.log(this.newEvent)
                this.addRoundEvent({type: this.event_type, event: this.newEvent}).then(
                    function (res) {
                        this.newEvent = {};
                    });
            },
            updateEventStart(event) {
                event.start_time = this.currentTime;
                this.updateRoundEvent({type: this.event_type, event: event});
            },
            updateEventEnd(event) {
                event.end_time = this.currentTime;
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