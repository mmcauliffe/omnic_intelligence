import { teamService } from '../api';

const state = {
    all: {},
    one: {},
};

const actions = {
    getAllTeams({ commit }) {
        commit('getAllRequest');
        console.log('hello')
        teamService.getAllTeams()
            .then(
                teams => commit('getAllSuccess', teams),
                error => commit('getAllFailure', error)
            );
    },
    getTeam( { commit }, id){
        commit('getOneRequest');

        teamService.getTeam(id)
            .then(
                team => commit('getOneSuccess', team),
                error => commit('getOneFailure', error)
            );

    },
    updateTeam( { commit }, team){
        commit('updateRequest');

        teamService.updateTeam(team)
            .then(
                team => commit('updateSuccess', team),
                error => commit('updateFailure', error)
            );

    },
    deleteTeam({ commit }, id) {
        commit('deleteRequest', id);

        teamService.deleteTeam(id)
            .then(
                team => commit('deleteSuccess', id),
                error => commit('deleteSuccess', { id, error: error.toString() })
            );
    }
};

const mutations = {
    getAllRequest(state) {
        state.all = { loading: true };
    },
    getAllSuccess(state, teams) {
        state.all = { items: teams.data };
    },
    getAllFailure(state, error) {
        state.all = { error };
    },

    getOneRequest(state) {
        state.one = { loading: true };
    },
    getOneSuccess(state, team) {
        state.one = { item: team.data };
    },
    getOneFailure(state, error) {
        state.one = { error };
    },

    updateRequest(state) {
    },
    updateSuccess(state, team) {

    },
    updateFailure(state, error) {
        console.log(error)
        state.one = { error };
    },

    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        state.all.items = state.all.items.map(team =>
            team.id === id
                ? { ...team, deleting: true }
                : team
        )
    },
    deleteSuccess(state, id) {
        // remove deleted user from state
        state.all.items = state.all.items.filter(team => team.id !== id)
    },
    deleteFailure(state, { id, error }) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        state.all.items = state.items.map(team => {
            if (team.id === id) {
                // make copy of user without 'deleting:true' property
                const { deleting, ...teamCopy } = team;
                // return copy of user with 'deleteError:[error]' property
                return { ...teamCopy, deleteError: error };
            }

            return team;
        })
    }
};

export const teams = {
    namespaced: true,
    state,
    actions,
    mutations
};