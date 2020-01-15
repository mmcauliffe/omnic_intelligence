<template>
<div>
    <v-flex>
        <vue-headful :title="title" />

        <v-layout row>

            <v-text-field label="Search" v-model="filters.name"></v-text-field>
        </v-layout>

        <v-btn class='primary raised' v-on:click="refresh()">Update filters
        </v-btn>
    </v-flex>

            <v-data-table
            :total-items="totalItems"
            :pagination.sync="pagination"
            :headers="headers" :items="items"
                          :rows-per-page-items="rowsPerPage">

                <template slot="items" slot-scope="props">
                    <td>
                        <router-link :to="{name: 'player-detail', params: {id: props.item.id}}">{{ props.item.name }}</router-link>

                    </td>
                    <td>{{props.item.position}}</td>
                    <td><v-layout row><div v-for="hero in props.item.heroes">
            <v-tooltip bottom v-if="hero.name && hero.name !== 'n/a'">
                <img style="width: 32px;height:32px" class="hero-icon" slot="activator"
                     :src="require('../../assets/'+ make_safe(hero.name) +'.png')"/>
                <span>{{ hero.play_time |secondsToMoment | moment('mm:ss.S') }}</span>
            </v-tooltip>
            </div></v-layout></td>
                    <td>{{props.item.last_match}}</td>
                </template>
            </v-data-table>
    </div>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'
    import VInput from "vuetify/es5/components/VInput/VInput";
    import VTabs from "vuetify/es5/components/VTabs/VTabs";
    import VTab from "vuetify/es5/components/VTabs/VTab";
    import VCard from "vuetify/es5/components/VCard/VCard";
    import VSelect from "vuetify/es5/components/VSelect/VSelect";
    import VBtn from "vuetify/es5/components/VBtn/VBtn";
    import VIcon from "vuetify/es5/components/VIcon/VIcon";
    import VTooltip from "vuetify/es5/components/VTooltip/VTooltip";
    import VTabsItems from "vuetify/es5/components/VTabs/VTabsItems";
    import VTabItem from "vuetify/es5/components/VTabs/VTabItem";
    import VFlex from "vuetify/es5/components/VGrid/VFlex";
    import VLayout from "vuetify/es5/components/VGrid/VLayout";
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";

    export default {
        name: "player-list-page",

        components: {
            VTabItem,
            VTabsItems,
            VSelect,
            VTabs,
            VTab,
            VCard,
            VBtn,
            VIcon,
            VTooltip,
            VInput,
            VLayout,
            VFlex,
            VDataTable
        },

        data() {
            return {
                title: 'Players | Omnic Intelligence',
                selected: [],
                filters: {},
                headers: [
                    {text: 'Name', value: 'name', sortable: true},
                    {text: 'Position', value: 'position', sortable: true},
                    {text: 'Most played heroes', value: 'heroes', sortable: true},
                    {text: 'Last match', value: 'last_match', sortable: true},
                ],
                rowsPerPage: [10]
            }
        },
        computed: {
            ...mapState({
                account: state => state.account,
                players: state => state.players.player_status,
                player_state: state => state.players,
            }),
            loading() {
                return this.players.loading
            },
            items() {
                return this.players.items
            },
            totalItems() {
                return this.players.count
            },
            pagination: {
                get: function () {
                    return this.player_state.pagination
                },
                set: function (value) {
                    this.updatePagination(value)
                }
            }
        },
        created() {

        },
        methods: {
            make_safe(name) {
                if (name !== undefined) {
                    return name.replace(':', '')
                }
                return ''
            },
            ...mapActions('players', {
                getPlayers: 'getPlayers',
                updatePagination: 'updatePagination'
            }),
            refresh(){

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

                this.getPlayers(params);
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