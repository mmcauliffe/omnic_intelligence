import {playerService, roundService} from '../api';

const state = {
    all: {},
    one: {},
    pagination: {
        page: 1,
        rowsPerPage: 10,
    },
    player_status: {},
    stats: {},
    recent_matches: {},
    teams: {},
};

const actions = {
    updatePagination({commit}, value){
       commit('setPagination', value)
    },
    getPlayers({commit}, data) {
        playerService.getPlayers(data)
            .then(
                players => commit('getPlayersSuccess', players.data),
                error => commit('getPlayersFailure', error)
            );
    },
    getPlayer( { commit }, id){
        commit('getOneRequest');

        playerService.getPlayer(id)
            .then(
                player => commit('getOneSuccess', player),
                error => commit('getOneFailure', error)
            );

    },
    getPlayerStatistics( { commit }, id){
        commit('getStatisticsRequest');

        playerService.getPlayerStatistics(id)
            .then(
                stats => commit('getStatisticsSuccess', stats),
                error => commit('getStatisticsFailure', error)
            );

    },
    getPlayerRecentMatches( { commit }, id){
        commit('getRecentMatchesRequest');

        playerService.getPlayerRecentMatches(id)
            .then(
                matches => commit('getRecentMatchesSuccess', matches),
                error => commit('getRecentMatchesFailure', error)
            );

    },
    getPlayerTeams( { commit }, id){
        commit('getTeamsRequest');

        playerService.getPlayerTeams(id)
            .then(
                matches => commit('getTeamsSuccess', matches),
                error => commit('getTeamsFailure', error)
            );

    },
    updatePlayer( { commit }, player){
        commit('updateRequest');

        playerService.updatePlayer(player)
            .then(
                player => commit('updateSuccess', player),
                error => commit('updateFailure', error)
            );

    },
    deletePlayer({ commit }, id) {
        commit('deleteRequest', id);

        playerService.deletePlayer(id)
            .then(
                player => commit('deleteSuccess', id),
                error => commit('deleteSuccess', { id, error: error.toString() })
            );
    }
};

const mutations = {
    setPagination (state, payload) {
      state.pagination = payload
    },
    getAllRequest(state) {
        state.all = { loading: true };
    },
    getAllSuccess(state, teams) {
        state.all = { items: teams.data };
    },
    getAllFailure(state, error) {
        state.all = { error };
    },

    getPlayersRequest(state) {
        state.player_status = {loading: true};
    },
    getPlayersSuccess(state, players) {
        console.log(players);
        state.player_status = {items: players.results, loading: false, count: players.count};
    },
    getPlayersFailure(state, error) {
        console.log(error);
        state.player_status = {error, loading: false};
    },

    getOneRequest(state) {
        state.one = { loading: true };
    },
    getOneSuccess(state, player) {
        state.one = { item: player.data };
    },
    getOneFailure(state, error) {
        state.one = { error };
    },

    getStatisticsRequest(state) {
        state.stats = { loading: true };
    },
    getStatisticsSuccess(state, stats) {
        state.stats = { item: stats.data };
    },
    getStatisticsFailure(state, error) {
        state.stats = { error };
    },

    getRecentMatchesRequest(state) {
        state.recent_matches = { loading: true };
    },
    getRecentMatchesSuccess(state, matches) {
        state.recent_matches = { item: matches.data };
    },
    getRecentMatchesFailure(state, error) {
        state.recent_matches = { error };
    },

    getTeamsRequest(state) {
        state.teams = { loading: true };
    },
    getTeamsSuccess(state, teams) {
        state.teams = { item: teams.data };
    },
    getTeamsFailure(state, error) {
        state.teams = { error };
    },

    updateRequest(state) {
    },
    updateSuccess(state, player) {

    },
    updateFailure(state, error) {
        console.log(error)
        state.one = { error };
    },

    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        state.all.items = state.all.items.map(player =>
            player.id === id
                ? { ...player, deleting: true }
                : player
        )
    },
    deleteSuccess(state, id) {
        // remove deleted user from state
        state.all.items = state.all.items.filter(player => player.id !== id)
    },
    deleteFailure(state, { id, error }) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        state.all.items = state.items.map(player => {
            if (player.id === id) {
                // make copy of user without 'deleting:true' property
                const { deleting, ...playerCopy } = player;
                // return copy of user with 'deleteError:[error]' property
                return { ...playerCopy, deleteError: error };
            }

            return player;
        })
    }
};

const getters = {
    pagination(state) {
        return state.pagination
    },
};

export const players = {
    namespaced: true,
    state,
    actions,
    mutations,
    getters
};