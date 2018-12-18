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
    import Navigation from './components/Navigation';
    import {mapState, mapActions} from 'vuex';
    import VApp from "vuetify/es5/components/VApp/VApp";

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
