<template>
    <div>

        <vue-headful :title="title" />
    <v-flex>
        <v-layout row>

        <v-select :items="spectator_modes.items" clearable
                  label="Spectator mode" v-model="filters.spectator_mode" item-text="name" item-value="id">
        </v-select>
        <v-select :items="annotation_sources.items" clearable
                  label="Annotation status" v-model="filters.annotation_status" item-text="name" item-value="id">
        </v-select>
        <v-select :items="heroes.items" clearable
                  label="Hero" v-model="filters.hero" item-text="name" item-value="id">
        </v-select>
        <v-btn class='primary raised' v-on:click="refresh()">Update filters
        </v-btn>
        </v-layout>

    </v-flex>
    <v-data-table
            :total-items="totalItems"
            :pagination.sync="pagination"
            :items="items"
            :headers="headers">

        <template slot="items" slot-scope="props">
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
            <td> <v-layout row><div v-for="hero in props.item.heroes_used">
            <v-tooltip bottom v-if="hero.name">
                <img style="width: 32px;height:32px" class="hero-icon" slot="activator"
                     :src="require('../../assets/'+ make_safe(hero.name) +'.png')"/>
                <span>{{ hero.play_time |secondsToMoment | moment('mm:ss.S') }}</span>
            </v-tooltip>
            </div></v-layout>
            </td>
        </template>
    </v-data-table>
    </div>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";

    export default {
        name: "search-page",
        components: {
            VDataTable
        },
        data: () => ({
            title: 'Ult deny search | Omnic Intelligence',
            selected: [],
            filters: {},
            headers: [
                {text: 'Round', value: 'round_number'},
                {text: 'Attacking side', value: 'attacking_side'},
                {text: 'VOD', value: 'vod', sortable: false},
                {text: 'Date', value: 'stream_vod__broadcast_date', sortable: true},
                {text: 'Duration', value: 'duration', sortable: true},
                {text: 'Annotation status', value: 'annotation_status', sortable: true},
                {text: 'Heroes', value: 'heroes'},
            ]
        }),
        computed: {

            ...mapState({
                account: state => state.account,
                maps: state => state.overwatch.maps,
                heroes: state => state.overwatch.heroes,
                rounds: state => state.rounds.round_status,
                round_state: state => state.rounds,
                annotation_sources: state => state.vods.annotation_sources,
                spectator_modes: state => state.vods.spectator_modes,
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
        created() {
            this.getAnnotationSources();
            this.getMaps();
            this.getHeroes();
            this.getFilmFormats();
            this.getSpectatorModes();
        },
        methods: {
            make_safe(name) {
                if (name !== undefined) {
                    return name.replace(':', '')
                }
                return ''
            },
            ...mapActions('rounds', {
                getPossibleDenyRounds: 'getPossibleDenyRounds',
                updatePagination: 'updatePagination'
            }),
            ...mapActions('overwatch', {
                getMaps: 'getMaps',
                getHeroes: 'getHeroes',
            }),
            ...mapActions('vods', {
                getAnnotationSources: 'getAnnotationSources',
                getFilmFormats: 'getFilmFormats',
                getSpectatorModes: 'getSpectatorModes',
            }),
            refresh(){
                if (Object.keys(this.filters).length === 0){
                    return
                }
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
                    ordering: ordering, ...this.filters
                };

                this.getPossibleDenyRounds(params);
            }
        },
        watch: {
            pagination: {
                handler() {
                    this.refresh();
                },
                deep: true
            }
        },
    }
</script>

<style scoped>

</style>