<template>
    <v-layout row flex-nowrap>
        <vue-headful :title="title"/>
        <div class="vod-column" v-if="game.item">
            <Vod :vod_type="game.item.stream_vod.vod_link[0]" :id="game.item.stream_vod.vod_link[1]"
                 :round_begin="game.item.begin" :round_end="game.item.end"></Vod>
        </div>
    </v-layout>

</template>

<script>
    import {mapState, mapActions, mapGetters} from 'vuex'

    const Vod = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['../../components/Vod'], () => {
            resolve(require('../../components/Vod'))
        })
    };
    const StatusBar = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['../../components/RoundDetail/StatusBar'], () => {
            resolve(require('../../components/RoundDetail/StatusBar'))
        })
    };
    const KillFeed = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['../../components/RoundDetail/KillFeed'], () => {
            resolve(require('../../components/RoundDetail/KillFeed'))
        })
    };
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
    export default {
        name: "GameReportPage",
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
            Vod,
            StatusBar,
            KillFeed
        },
        data() {
            return {
                current_round_index: 0,
                window: {
                    width: 0,
                    height: 0,
                    colWidth: 0
                }
            }
        },
        created() {
            this.getOneGame(this.$route.params.id);
            this.getRounds(this.$route.params.id);
        },
        computed: {
            current_round() {
                if (this.game.rounds !== undefined) {
                    return this.game.rounds[this.current_round_index]
                }
                return {}
            },
            ...mapState({
                account: state => state.account,
                game: state => state.games.one,
                rounds: state => state.games.rounds,
                teams: state => state.matches.teams,
            }),
            title() {
                if (this.game.item !== undefined) {
                    return this.game.item.match.name + ' | ' + 'Game ' + this.game.item.game_number + ' | Game Report | Omnic Intelligence'
                }
            },
        },
        methods: {
            ...mapActions('games', {
                getOneGame: 'getOne',
                getRounds: 'getOneRounds',
            }),
            seekTo(time) {
                console.log(time)
            },
            ...mapActions('vods', {
                updateTimestamp: 'updateTimestamp',
            }),
            handleResize() {
                this.window.width = window.innerWidth;
                this.window.height = window.innerHeight;
                this.window.colWidth = this.window.width - 1280 - 40;
                if (this.window.colWidth < 400) {
                    this.window.colWidth = 600;
                }
            }
        },

        watch: {
            current_round(newRound) {
                if (newRound !== undefined) {
                    this.updateTimestamp(newRound.begin);

                }
            },
        }
    }
</script>

<style scoped>

</style>