<template>
    <div class='row text-center'>
        <div class="col-sm-3"></div>
        <div class='col-sm-6'>
            <em v-if="event.loading">Loading event...</em>
            <span v-if="event.error" class="text-danger">ERROR: {{event.error}}</span>
            <div v-if="event.item">
                <h1>{{ event.item.name }}</h1>


                <v-select :items="spectator_modes.items" label="Spectator mode"
                          v-model="event.item.spectator_mode" item-text="name" item-value="id">

                </v-select>
                <v-select :items="streams.items" label="Stream" v-model="event.item.channel" item-text="name"
                          item-value="id">

                </v-select>

                <v-btn class='success' v-on:click="saveEvent">Save</v-btn>

                <v-tabs md-border-bottom md-dynamic-height v-if="event.item">
                    <v-tab>
                        Participating teams
                    </v-tab>
                    <v-tab>
                        Matches
                    </v-tab>
                    <v-tab>
                        Vods
                    </v-tab>
                    <v-tab>
                        Vods available to import
                    </v-tab>

                    <v-tabs-items>
                        <v-tab-item>

                        </v-tab-item>
                        <v-tab-item>
                            <em v-if="matches.loading">Loading matches...</em>
                            <span v-if="matches.error" class="text-danger">ERROR: {{matches.error}}</span>

                            <v-expansion-panel v-if="matches.items">
                                <v-expansion-panel-content v-for="match in matches.items" :key="match.id">

                                    <div slot="header">
                                        <router-link :to="{name: 'match-detail', params: {id: match.id}}">{{
                                            match.teams[0] }} vs {{ match.teams[1] }}
                                        </router-link>
                                        <span v-if="match.date">({{match.date}})</span></div>
                                    <span v-if="match.deleting"><em> - Deleting...</em></span>
                                    <span v-else-if="match.deleteError" class="text-danger"> - ERROR: {{match.deleteError}}</span>
                                    <span v-else> - <a @click="deleteMatch(match.id)"
                                                       class="text-danger">Delete</a></span>
                                </v-expansion-panel-content>
                            </v-expansion-panel>
                        </v-tab-item>
                        <v-tab-item>
                            <v-data-table :headers="vod_headers" :items="vods.items" v-if="vods.items"
                                          :rows-per-page-items="rowsPerPage">

                                <template slot="items" slot-scope="props">
                                    <td>
                                        <router-link :to="{name: 'vod-detail', params: {id: props.item.id}}">
                                            {{props.item.title}}
                                        </router-link>
                                        (<a :href="props.item.url">View on Twitch</a>)
                                    </td>
                                    <td>
                                        {{props.item.broadcast_date}}
                                    </td>
                                    <td>
                                        {{props.item.last_modified}}
                                    </td>
                                    <td>
                                        {{ props.item.type }}
                                    </td>
                                    <td>
                                        {{ props.item.status }}
                                    </td>
                                </template>
                            </v-data-table>
                        </v-tab-item>
                        <v-tab-item>

                            <v-data-table :headers="available_vod_headers" :items="available_vods.items"
                                          v-if="available_vods.items" :rows-per-page-items="rowsPerPage">

                                <template slot="items" slot-scope="props">
                                    <td>
                                        {{props.item.title}} (<a :href="props.item.url">Link</a>)
                                    </td>
                                    <td>
                                        {{props.item.channel_title}} ({{props.item.channel_type}})
                                    </td>
                                    <td>{{props.item.published_at}}</td>
                                    <td>{{props.item.duration}}</td>
                                    <td>
                                        <v-btn class='primary raised' v-on:click="importVod(props.item)">Import VOD
                                        </v-btn>
                                    </td>
                                </template>
                            </v-data-table>
                        </v-tab-item>
                    </v-tabs-items>
                </v-tabs>
            </div>
        </div>
        <div class="col-sm-3"></div>
    </div>
</template>

<script>
    import {mapState, mapActions} from 'vuex'

    const VInput = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VInput/VInput'], () => {
            resolve(require('vuetify/es5/components/VInput/VInput'))
        })
    };
    const VTabs = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTabs/VTabs'], () => {
            resolve(require('vuetify/es5/components/VTabs/VTabs'))
        })
    };
    const VTab = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTabs/VTab'], () => {
            resolve(require('vuetify/es5/components/VTabs/VTab'))
        })
    };
    const VTabsItems = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTabs/VTabsItems'], () => {
            resolve(require('vuetify/es5/components/VTabs/VTabsItems'))
        })
    };
    const VTabItem = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VTabs/VTabItem'], () => {
            resolve(require('vuetify/es5/components/VTabs/VTabItem'))
        })
    };
    const VCard = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VCard/VCard'], () => {
            resolve(require('vuetify/es5/components/VCard/VCard'))
        })
    };
    const VSelect = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VSelect/VSelect'], () => {
            resolve(require('vuetify/es5/components/VSelect/VSelect'))
        })
    };
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
    const VFlex = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VGrid/VFlex'], () => {
            resolve(require('vuetify/es5/components/VGrid/VFlex'))
        })
    };
    const VLayout = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VGrid/VLayout'], () => {
            resolve(require('vuetify/es5/components/VGrid/VLayout'))
        })
    };
    const VExpansionPanel = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VExpansionPanel/VExpansionPanel'], () => {
            resolve(require('vuetify/es5/components/VExpansionPanel/VExpansionPanel'))
        })
    };
    const VExpansionPanelContent = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VExpansionPanel/VExpansionPanelContent'], () => {
            resolve(require('vuetify/es5/components/VExpansionPanel/VExpansionPanelContent'))
        })
    };

    export default {
        components: {
            VTabItem,
            VTabsItems,
            VTab,
            VTabs,
            VSelect,
            VExpansionPanel,
            VExpansionPanelContent,
            VDataTable,
            VBtn
        },
        name: "event-detail-page",
        computed: {
            ...mapState({
                account: state => state.account,
                spectator_modes: state => state.vods.spectator_modes,
                streams: state => state.vods.stream_channels,
                event: state => state.events.one,
                matches: state => state.events.matches,
                available_vods: state => state.events.available_vods,
                vods: state => state.events.stream_vods
            }),
        },
        data() {
            return {
                vod_headers: [
                    {text: 'Title', sortable: true, value: 'title'},
                    {text: 'Broadcast date', sortable: true, value: 'broadcast_date'},
                    {text: 'Last modified', sortable: true, value: 'last_modified'},
                    {text: 'Type', sortable: true, value: 'type'},
                    {text: 'Status', sortable: true, value: 'status'},
                ],
                available_vod_headers: [
                    {text: 'Title', sortable: true, value: 'title'},
                    {text: 'Channel', sortable: true, value: 'channel_title'},
                    {text: 'Date', sortable: true, value: 'published_at'},
                    {text: 'Duration', sortable: true, value: 'duration'},
                    {text: 'Actions', sortable: false},
                ],
                rowsPerPage: [10]
            }
        },
        created() {
            this.getOneEvent(this.$route.params.id);
            this.getMatches(this.$route.params.id);
            this.getAvailableVods(this.$route.params.id);
            this.getStreamVods(this.$route.params.id);
            this.getSpectatorModes();
            this.getStreamChannels();
        },
        methods: {
            ...mapActions('events', {
                getOneEvent: 'getOne',
                getMatches: 'getOneMatches',
                deleteEvent: 'delete',
                getAvailableVods: 'getAvailableVods',
                getStreamVods: 'getStreamVods',
            }),
            ...mapActions('vods', {
                getStreamChannels: 'getStreamChannels',
                getSpectatorModes: 'getSpectatorModes',
                createVod: 'createVod',
            }),
            saveEvent() {

            },
            importVod(vod_info) {
                console.log(vod_info)
                const newVod = {
                    channel: vod_info.channel,
                    url: vod_info.url,
                    title: vod_info.title,
                    film_format: this.event.item.film_format,
                    broadcast_date: vod_info.published_at
                };
                console.log(newVod)
                this.createVod(newVod).then(v => {
                    this.getStreamVods(this.$route.params.id)
                })
            }
        },

    }
</script>

<style scoped>

</style>