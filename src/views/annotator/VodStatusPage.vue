<template>
    <div>

        <vue-headful :title="title" />
     <v-data-table
            :total-items="totalItems"
            :pagination.sync="pagination"
            :items="items"
            :headers="headers">

        <template slot="items" slot-scope="props">
            <td>
                <router-link :to="{name: 'vod-detail', params:{id: props.item.id}}">
                    {{ props.item.title }}
                </router-link>
            </td>
            <td>{{ props.item.film_format }}</td>
            <td>{{ props.item.broadcast_date }}</td>
            <td>
                <a :href="props.item.url">Link</a>
            </td>
        </template>
    </v-data-table>
    </div>
</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'
    import VDataTable from "vuetify/es5/components/VDataTable/VDataTable";

    export default {
        name: "vod-status-page",
        components: {
            VDataTable
        },
        data: () => ({
            title: 'VOD status | Omnic Intelligence',
            selected: [],
            headers: [
                {text: 'VOD', value: 'title'},

                {text: 'Film format', value: 'film_format'},
                {text: 'Date', value: 'broadcast_date'},
                {text: 'Link', value: 'url', sortable: false},
            ]
        }),
        computed: {

            ...mapState({
                account: state => state.account,
                vods: state => state.vods.vod_status,
                vod_state: state => state.vods
            }),
            loading() {
                return this.vods.loading
            },
            items() {
                return this.vods.items
            },
            totalItems() {
                return this.vods.count
            },
            pagination: {
                get: function () {
                    console.log(this.$store)
                    return this.vod_state.pagination
                },
                set: function (value) {
                    this.updatePagination(value)
                }
            }
        },
        methods: {
            ...mapActions('vods', {
                getVods: 'getVods',
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
                    this.getVods(params);
                },
                deep: true
            }
        },
    }
</script>

<style scoped>

</style>