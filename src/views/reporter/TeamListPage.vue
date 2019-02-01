<template>

    <v-layout row>
        <v-flex>

            <v-data-table :headers="headers" :items="teams.items" v-if="teams.items" :rows-per-page-items="rowsPerPage">

                <template slot="items" slot-scope="props">
                    <td>
                        <router-link :to="{name: 'team-detail', params: {id: props.item.id}}">{{ props.item.name }}</router-link>

                    </td>
                </template>
            </v-data-table>
        </v-flex>
    </v-layout>
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
        name: "team-list-page",

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
                headers: [
                    {text: '', sortable: true}
                ],
                rowsPerPage: [10]
            }
        },
        computed: {
            ...mapState({
                account: state => state.account,
                teams: state => state.teams.all,
            }),
        },
        created() {
            this.getAllTeams();

        },
        methods: {
            ...mapActions('teams', {
                getAllTeams: 'getAllTeams',
            }),
        }
    }
</script>

<style scoped>

</style>