import { gameService} from '../api';
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
                games => commit('getAllSuccess', games),
                error => commit('getAllFailure', error)
            );
    },
    getOne( { commit }, id){
        commit('getOneRequest');

        gameService.getById(id)
            .then(
                game => {
                console.log(game.match)
                    matchService.getTeams(game.match).then(
                        teams => commit('getOneSuccess', {game:game, teams:teams}),
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
                rounds => commit('getOneRoundsSuccess', rounds),
                error => commit('getOneRoundsFailure', error)
            );
    },
    delete({ commit }, id) {
        commit('deleteRequest', id);

        gameService.delete(id)
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
        console.log(game.game)
        console.log(game.game.left_team)
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

    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        state.all.items = state.all.items.map(game =>
            game.id === id
                ? { ...game, deleting: true }
                : game
        )
    },
    deleteSuccess(state, id) {
        // remove deleted user from state
        state.all.items = state.all.items.filter(game => game.id !== id)
    },
    deleteFailure(state, { id, error }) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        state.all.items = state.items.map(game => {
            if (game.id === id) {
                // make copy of user without 'deleting:true' property
                const { deleting, ...gameCopy } = game;
                // return copy of user with 'deleteError:[error]' property
                return { ...gameCopy, deleteError: error };
            }

            return user;
        })
    }
};

export const games = {
    namespaced: true,
    state,
    actions,
    mutations
};