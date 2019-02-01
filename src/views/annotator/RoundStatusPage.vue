<template>
    <v-data-table
            :total-items="totalItems"
            :pagination.sync="pagination"
            :items="items"
            :headers="headers">

        <template slot="items" slot-scope="props">
            <td>
                <router-link :to="{name: 'event-detail', params:{id: props.item.game.match.event.id}}">
                    {{ props.item.game.match.event.name }}
                </router-link>
            </td>
            <td>
                <router-link :to="{name: 'match-detail', params:{id: props.item.game.match.id}}">
                    {{ props.item.game.match.teams[0] }} vs {{ props.item.game.match.teams[1] }}
                </router-link>
            </td>
            <td>
                <router-link :to="{name: 'game-detail', params:{id: props.item.game.id}}">
                    Game {{ props.item.game.game_number }}
                </router-link>
            </td>
            <td> {{ props.item.game.map.name }}</td>
            <td>
                <router-link :to="{name: 'round-detail', params:{id: props.item.id}}">
                    Round {{ props.item.round_number }}

                </router-link>
            </td>
            <td>{{ props.item.attacking_side }}</td>
            <td>
                <a :href="props.item.stream_vod.url">{{ props.item.stream_vod.title }}
                    ({{ props.item.stream_vod.id }})</a>
            </td>
            <td>{{ props.item.stream_vod.broadcast_date }}</td>
            <td>{{ props.item.duration |secondsToMoment | moment('mm:ss.S') }}</td>
            <td>{{ props.item.annotation_status }}</td>
        </template>
    </v-data-table>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";

    export default {
        name: "round-status-page",
        components: {
            VDataTable
        },
        data: () => ({

            selected: [],
            headers: [
                {text: 'Event', value: 'game__match__event__name'},
                {text: 'Match', value: 'match', sortable: false},
                {text: 'Game', value: 'game__game_number'},
                {text: 'Map', value: 'map', sortable: false},
                {text: 'Round', value: 'round_number'},
                {text: 'Attacking side', value: 'attacking_side'},
                {text: 'VOD', value: 'vod', sortable: false},
                {text: 'Date', value: 'stream_vod__broadcast_date'},
                {text: 'Duration', value: 'duration', sortable: false},
                {text: 'Annotation status', value: 'annotation_status'},
            ]
        }),
        computed: {

            ...mapState({
                account: state => state.account,
                rounds: state => state.rounds.round_status,
                round_state: state => state.rounds
            }),
            loading() {
                return this.rounds.loading
            },
            items() {
                return this.rounds.items
            },
            totalItems() {
                return this.rounds.count
            },
            pagination: {
                get: function () {
                    console.log(this.$store)
                    return this.round_state.pagination
                },
                set: function (value) {
                    this.updatePagination(value)
                }
            }
        },
        methods: {
            ...mapActions('rounds', {
                getRounds: 'getRounds',
                updatePagination: 'updatePagination'
            }),
        },
        watch: {
            pagination: {
                handler() {
                    let ordering;
                    if (this.pagination.descending) {
                        ordering = '-' + this.pagination.sortBy;
                    }
                    else {
                        ordering = this.pagination.sortBy;
                    }
                    const params = {
                        offset: (this.pagination.page - 1) * this.pagination.rowsPerPage,
                        limit: this.pagination.rowsPerPage,
                        ordering: ordering,
                    };
                    this.getRounds(params);
                },
                deep: true
            }
        },
    }
</script>

<style scoped>

</style>