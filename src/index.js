import Vue from 'vue'
import Vuetify from 'vuetify'

import vueHeadful from 'vue-headful';
Vue.use(Vuetify);

Vue.use(require('vue-moment'))

Vue.component('vue-headful', vueHeadful);
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
import './f&d/directives'
import './f&d/filters'



new Vue({
    el: '#app',
    router,
    store,
    render: h => h(App)
});