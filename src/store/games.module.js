import {gameService, teamService} from '../api';
import { matchService} from '../api';


const state = {
    all: {},
    one: {},
    rounds: {},
};

const actions = {
    getAll({ commit }) {
        commit('getAllRequest');

        gameService.getAll()
            .then(
                games => commit('getAllSuccess', games.data),
                error => commit('getAllFailure', error)
            );
    },
    createGame( { commit }, game){
        commit('createRequest');

        return gameService.createGame(game)
            .then(
                game => commit('createSuccess', game),
                error => commit('createFailure', error)
            );

    },
    updateGame( { commit }, game){
        commit('updateRequest');

        return gameService.updateGame(game)
            .then(
                game => commit('updateSuccess', game),
                error => commit('updateFailure', error)
            );

    },
    updateTeams( { commit }, game){
        commit('updateTeamsRequest');

        return gameService.updateTeams(game)
            .then(
                game => commit('updateTeamsSuccess', game),
                error => commit('updateTeamsFailure', error)
            );

    },
    getOne( { commit }, id){
        commit('getOneRequest');

        gameService.getById(id)
            .then(
                game => {
                    game = game.data;
                    console.log(game)
                console.log(game.match)
                    matchService.getTeams(game.match).then(
                        teams => commit('getOneSuccess', {game:game, teams:teams.data}),
                        error => commit('getOneFailure', error)
                    )
                },
                error => commit('getOneFailure', error)
            );

    },
    getOneRounds({ commit }, id){
        commit('getOneRoundsRequest');

        gameService.getRounds(id)
            .then(
                rounds => commit('getOneRoundsSuccess', rounds.data),
                error => commit('getOneRoundsFailure', error)
            );
    },
    deleteGame({ commit }, id) {
        commit('deleteRequest', id);

        gameService.deleteGame(id)
            .then(
                game => commit('deleteSuccess', id),
                error => commit('deleteSuccess', { id, error: error.toString() })
            );
    }
};

const mutations = {
    getAllRequest(state) {
        state.all = { loading: true };
    },
    getAllSuccess(state, games) {
        state.all = { items: games };
    },
    getAllFailure(state, error) {
        state.all = { error };
    },

    getOneRequest(state) {
        state.one = { loading: true };
    },
    getOneSuccess(state, game) {
        console.log('GETONE')
        console.log(game.game)
        console.log(game.game.left_team)
        console.log(game.teams)
        state.one = { item: game.game, teams: game.teams };
    },
    getOneFailure(state, error) {
        state.one = { error };
    },

    getOneRoundsRequest(state) {
        state.rounds = { loading: true };
    },
    getOneRoundsSuccess(state, rounds) {
        state.rounds = { items: rounds };
    },
    getOneRoundsFailure(state, error) {
        state.rounds = { error };
    },

    updateRequest(state) {
    },
    updateSuccess(state, game) {

    },
    updateFailure(state, error) {
        console.log(error)
        state.one = { error };
    },

    updateTeamsRequest(state) {
    },
    updateTeamsSuccess(state, game) {

    },
    updateTeamsFailure(state, error) {
        console.log(error)
    },

    createRequest(state) {
    },
    createSuccess(state, game) {

    },
    createFailure(state, error) {
        console.log(error)
    },
    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        if (state.all.items) {
            state.all.items = state.all.items.map(game =>
                game.id === id
                    ? {...game, deleting: true}
                    : game
            )
        }
    },
    deleteSuccess(state, id) {
        // remove deleted user from state
        if (state.all.items){
            state.all.items = state.all.items.filter(game => game.id !== id)
        }
    },
    deleteFailure(state, { id, error }) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        if (state.all.items) {
            state.all.items = state.items.map(game => {
                if (game.id === id) {
                    // make copy of user without 'deleting:true' property
                    const {deleting, ...gameCopy} = game;
                    // return copy of user with 'deleteError:[error]' property
                    return {...gameCopy, deleteError: error};
                }

                return user;
            })
        }
    }
};

export const games = {
    namespaced: true,
    state,
    actions,
    mutations
};