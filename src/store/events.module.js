import {eventService} from '../api';

const state = {
    all: {},
    one: {},
    matches: {},
    available_vods: {},
    stream_vods: {},
    teams: {}
};

const actions = {
    getAll({ commit }) {
        commit('getAllRequest');

        eventService.getAll()
            .then(
                events => commit('getAllSuccess', events),
                error => commit('getAllFailure', error)
            );
    },
    getOne( { commit }, id){
        commit('getOneRequest');

        eventService.getById(id)
            .then(
                event => commit('getOneSuccess', event),
                error => commit('getOneFailure', error)
            );

    },
    getOneTeams( { commit }, id){
        commit('getOneTeamsRequest');

        eventService.getOneTeams(id)
            .then(
                teams => commit('getOneTeamsSuccess', teams),
                error => commit('getOneTeamsFailure', error)
            );

    },
    getAvailableVods({commit}, id){
        eventService.getAvailableVods(id).then(
            vods => commit('getAvailableVodsSuccess', vods),
                error => commit('getAvailableVodsFailure', error)
        )
    },
    getStreamVods({commit}, id){
        eventService.getStreamVods(id).then(
            vods => commit('getStreamVodsSuccess', vods),
                error => commit('getStreamVodsFailure', error)
        )
    },
    getOneMatches({ commit }, id){
        commit('getOneMatchesRequest');

        eventService.getMatches(id)
            .then(
                matches => commit('getOneMatchesSuccess', matches),
                error => commit('getOneMatchesFailure', error)
            );
    },
    delete({ commit }, id) {
        commit('deleteRequest', id);

        eventService.delete(id)
            .then(
                event => commit('deleteSuccess', id),
                error => commit('deleteSuccess', { id, error: error.toString() })
            );
    }
};

const mutations = {
    getAllRequest(state) {
        state.all = { loading: true };
    },
    getAllSuccess(state, events) {
        state.all = { items: events };
    },
    getAllFailure(state, error) {
        state.all = { error };
    },

    getOneRequest(state) {
        state.one = { loading: true };
    },
    getOneSuccess(state, event) {
        state.one = { item: event };
    },
    getOneFailure(state, error) {
        state.one = { error };
    },

    getOneTeamsRequest(state) {
        state.teams = { loading: true };
    },
    getOneTeamsSuccess(state, teams) {
        state.teams = { items: teams };
    },
    getOneTeamsFailure(state, error) {
        state.teams = { error };
    },

    getOneMatchesRequest(state) {
        state.matches = { loading: true };
    },
    getOneMatchesSuccess(state, matches) {
        state.matches = { items: matches };
    },
    getOneMatchesFailure(state, error) {
        state.matches = { error };
    },

    getStreamVodsRequest(state) {
        state.stream_vods = {loading: true};
    },
    getStreamVodsSuccess(state, vods) {
        console.log(vods);
        state.stream_vods = {items: vods.data, loading: false};
    },
    getStreamVodsFailure(state, error) {
        console.log(error);
        state.stream_vods = {error, loading: false};
    },

    getAvailableVodsRequest(state) {
        state.available_vods = {loading: true};
    },
    getAvailableVodsSuccess(state, vods) {
        state.available_vods = {items: vods.data, loading: false};
        console.log(vods.data)
    },
    getAvailableVodsFailure(state, error) {
        state.available_vods = {error, loading:false};
    },

    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        state.all.items = state.all.items.map(event =>
            event.id === id
                ? { ...event, deleting: true }
                : event
        )
    },
    deleteSuccess(state, id) {
        // remove deleted user from state
        state.all.items = state.all.items.filter(event => event.id !== id)
    },
    deleteFailure(state, { id, error }) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        state.all.items = state.items.map(event => {
            if (event.id === id) {
                // make copy of user without 'deleting:true' property
                const { deleting, ...eventCopy } = event;
                // return copy of user with 'deleteError:[error]' property
                return { ...eventCopy, deleteError: error };
            }

            return user;
        })
    }
};

export const events = {
    namespaced: true,
    state,
    actions,
    mutations
};