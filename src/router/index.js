import Vue from 'vue';
import Router from 'vue-router';

import HomePage from '../views/HomePage'
import LoginPage from '../views/LoginPage'
import LogoutPage from '../views/LogoutPage'
import RegisterPage from '../views/RegisterPage'
import AnnotatorPage from '../views/annotator/AnnotatorPage'
import EventDetailPage from '../views/annotator/EventDetailPage'
import EventListPage from '../views/annotator/EventListPage'
import MatchDetailPage from '../views/annotator/MatchDetailPage'
import GameDetailPage from '../views/annotator/GameDetailPage'
import RoundDetailPage from '../views/annotator/RoundDetailPage'

Vue.use(Router);

export const router = new Router({
    mode: 'history',
    routes: [
        {path: '/', component: HomePage, name: 'home'},
        {path: '/login', component: LoginPage, name:'login'},
        {path: '/register', component: RegisterPage, name: 'register'},
        {path: '/logout', component: LogoutPage, name: 'logout'},
        {
            path: '/annotator', component: AnnotatorPage,
            children: [
                {
                    path: '',
                    component: EventListPage,
                    name: 'annotator'
                },
                {
                    path: 'event/:id',
                    component: EventDetailPage,
                    name: 'event-detail'
                },
                {
                    path: 'match/:id',
                    component: MatchDetailPage,
                    name: 'match-detail'
                },
                {
                    path: 'game/:id',
                    component: GameDetailPage,
                    name: 'game-detail'
                },
                {
                    path: 'round/:id',
                    component: RoundDetailPage,
                    name: 'round-detail'
                }
            ]
        },

        // otherwise redirect to home
        {path: '*', redirect: '/'}
    ]
});

router.beforeEach((to, from, next) => {
    // redirect to login page if not logged in and trying to access a restricted page
    const publicPages = ['/login', '/register', '/'];
    const authRequired = !publicPages.includes(to.path);
    const loggedIn = localStorage.getItem('auth');

    if (authRequired && !loggedIn) {
        return next('/login');
    }

    next();
})