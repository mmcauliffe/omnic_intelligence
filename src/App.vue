<template>
<v-app>
  <v-content>
    <v-container fluid>
            <Navigation></Navigation>
                    <div v-if="alert.message" :class="`alert ${alert.type}`">{{alert.message}}</div>
      <router-view></router-view>
    </v-container>
  </v-content>
</v-app>
</template>

<script>
    import {mapState, mapActions} from 'vuex';
    const VApp = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['vuetify/es5/components/VApp/VApp'], () => {
            resolve(require('vuetify/es5/components/VApp/VApp'))
        })
    };
    const Navigation = resolve => {
        // require.ensure is Webpack's special syntax for a code-split point.
        require.ensure(['./components/Navigation'], () => {
            resolve(require('./components/Navigation'))
        })
    };

    export default {
        name: 'app',
        components: {
            Navigation,
            VApp,
        },
        computed: {
            ...mapState({
                alert: state => state.alert
            })
        },
        methods: {
            ...mapActions({
                clearAlert: 'alert/clear'
            })
        },
        watch: {
            $route(to, from) {
                // clear alert on location change
                this.clearAlert();
            }
        }
    };
</script>
<style lang="scss">
    @import './styles/custom-bootstrap.scss';
</style>
