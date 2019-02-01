import {userService} from '../api';
import {router} from '../router';

const auth = JSON.parse(localStorage.getItem('auth'));
const user = JSON.parse(localStorage.getItem('user'));
const state = auth
    ? {status: {loggedIn: true}, auth, user}
    : {status: {}, auth: null, user: null};

const actions = {
    login({dispatch, commit}, {username, password}) {

        commit('loginRequest', {username});

        userService.login(username, password)
            .then(
                auth => {
                    userService.getCurrent().then(
                        user => {
                            commit('loginSuccess', user);
                            router.push({ name: 'home' });
                        },
                        error => {
                            commit('loginFailure', error);
                            dispatch('alert/error', error, {root: true});
                        }
                    )
                },
                error => {
                    commit('loginFailure', error);
                    dispatch('alert/error', error, {root: true});
                }
            );
    },
    logout({commit}) {
        userService.logout();
        commit('logout');
        router.push({ name: 'home' });
    },
    register({dispatch, commit}, user) {
        commit('registerRequest', user);

        userService.register(user)
            .then(
                user => {
                    commit('registerSuccess', user);
                    router.push({name: "login"});
                    setTimeout(() => {
                        // display success message after route change completes
                        dispatch('alert/success', 'Registration successful', {root: true});
                    })
                },
                error => {
                    commit('registerFailure', error);
                    dispatch('alert/error', error, {root: true});
                }
            );
    }
};

const mutations = {
    loginRequest(state, user) {
        state.status = {loggingIn: true};
        state.user = user;
    },
    loginSuccess(state, user) {
        state.status = {loggedIn: true};
        state.user = user;
    },
    loginFailure(state) {
        state.status = {};
        state.user = null;
    },
    logout(state) {
        state.status = {};
        state.user = null;
    },
    registerRequest(state, user) {
        state.status = {registering: true};
    },
    registerSuccess(state, user) {
        state.status = {};
    },
    registerFailure(state, error) {
        state.status = {};
    }
};

export const account = {
    namespaced: true,
    state,
    actions,
    mutations
};