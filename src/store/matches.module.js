import { matchService} from '../api';

const state = {
    all: {},
    one: {},
    games: {},
    teams: {},
    left_player_options: [],
    right_player_options: [],
};

const actions = {
    updateLeftPlayerOptions({commit}, value){
       commit('setLeftPlayerOptions', value)
    },
    updateRightPlayerOptions({commit}, value){
       commit('setRightPlayerOptions', value)
    },
    getAll({ commit }) {
        commit('getAllRequest');

        matchService.getAll()
            .then(
                matches => commit('getAllSuccess', matches),
                error => commit('getAllFailure', error)
            );
    },
    getOne( { commit }, id){
        commit('getOneRequest');

        matchService.getById(id)
            .then(
                match => commit('getOneSuccess', match),
                error => commit('getOneFailure', error)
            );

    },
    getOneGames({ commit }, id){
        commit('getOneGamesRequest');

        matchService.getGames(id)
            .then(
                games => commit('getOneGamesSuccess', games),
                error => commit('getOneGamesFailure', error)
            );
    },
    getOneTeams({ commit }, id){
        commit('getOneTeamsRequest');

        matchService.getTeams(id)
            .then(
                games => commit('getOneTeamsSuccess', games),
                error => commit('getOneTeamsFailure', error)
            );
    },
    delete({ commit }, id) {
        commit('deleteRequest', id);

        matchService.delete(id)
            .then(
                match => commit('deleteSuccess', id),
                error => commit('deleteSuccess', { id, error: error.toString() })
            );
    }
};

const mutations = {
    setLeftPlayerOptions (state, payload) {
      state.left_player_options = payload
    },
    setRightPlayerOptions (state, payload) {
      state.right_player_options = payload
    },
    getAllRequest(state) {
        state.all = { loading: true };
    },
    getAllSuccess(state, matches) {
        state.all = { items: matches };
    },
    getAllFailure(state, error) {
        state.all = { error };
    },

    getOneRequest(state) {
        state.one = { loading: true };
    },
    getOneSuccess(state, match) {
        console.log(match)
        state.one = { item: match };
    },
    getOneFailure(state, error) {
        state.one = { error };
    },

    getOneGamesRequest(state) {
        state.games = { loading: true };
    },
    getOneGamesSuccess(state, games) {
        state.games = { items: games };
    },
    getOneGamesFailure(state, error) {
        state.games = { error };
    },

    getOneTeamsRequest(state) {
        state.teams = { loading: true };
    },
    getOneTeamsSuccess(state, match) {
        console.log(match)
        state.teams = { items: match };
    },
    getOneTeamsFailure(state, error) {
        state.teams = { error };
    },

    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        state.all.items = state.all.items.map(match =>
            match.id === id
                ? { ...match, deleting: true }
                : match
        )
    },
    deleteSuccess(state, id) {
        // remove deleted user from state
        state.all.items = state.all.items.filter(match => match.id !== id)
    },
    deleteFailure(state, { id, error }) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        state.all.items = state.items.map(match => {
            if (match.id === id) {
                // make copy of user without 'deleting:true' property
                const { deleting, ...matchCopy } = match;
                // return copy of user with 'deleteError:[error]' property
                return { ...matchCopy, deleteError: error };
            }

            return user;
        })
    }
};

export const matches = {
    namespaced: true,
    state,
    actions,
    mutations
};