import Vue from 'vue'
import Vuetify from 'vuetify'
import moment from 'moment'

Vue.use(Vuetify);

Vue.use(require('vue-moment'))
import 'vuetify/dist/vuetify.min.css' // Ensure you are using css-loader
import App from './App.vue'
import BootstrapVue from 'bootstrap-vue';
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue);


import {store} from './store';
import {router} from './router';

Vue.config.productionTip = false;

// Vue.use(VueRouter)


Vue.filter('secondsToMoment', function (seconds) {
        var m = moment({hour: 0, minute: 0});
        m.seconds(Math.round(seconds));
        m.milliseconds(Math.round(seconds % 1 * 1000));
        return m;
    }
);

Vue.filter('playerTemplate', function (playerNum){
    return 'Player '+ playerNum
});

new Vue({
    el: '#app',
    router,
    store,
    render: h => h(App)
});