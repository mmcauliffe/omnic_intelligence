import {gameService, roundService} from '../api';

const kf_event_types = ['kill_feed_events'];
const player_state_types = ['kill_feed_events','ultimates', 'status_effects'];
const event_types = ['hero_picks', 'kill_feed_events', 'ultimates', 'status_effects',
    'revives', 'point_gains', 'point_flips', 'pauses', 'replays', 'overtimes', 'smaller_windows', 'zooms'];
const state = {
    all: {},
    round_status: {},
    pagination: {
        page: 1,
        rowsPerPage: 10,
    },
    one: {},
    hero_picks: [],
    kill_feed_events: [],
    ultimates: [],
    status_effects: [],
    revives: [],
    point_gains: [],
    point_flips: [],
    pauses: [],
    replays: [],
    overtimes: [],
    smaller_windows: [],
    zooms: [],
    kill_feed_items: {},
    player_states: {},
    round_states: {},
};

const actions = {
    updatePagination({commit}, value){
       commit('setPagination', value)
    },
    getAll({commit}) {
        commit('getAllRequest');

        roundService.getAll()
            .then(
                rounds => commit('getAllSuccess', rounds),
                error => commit('getAllFailure', error)
            );
    },
    createRound( { commit }, round){
        commit('createRequest');

        return roundService.createRound(round)
            .then(
                round => commit('createSuccess', round),
                error => commit('createFailure', error)
            );

    },
    updateRound( { commit }, round){
        commit('updateRequest');

        roundService.updateRound(round.data)
            .then(
                round => commit('updateSuccess', round.data),
                error => commit('updateFailure', error)
            );

    },
    getRounds({commit}, data) {
        roundService.getRounds(data)
            .then(
                rounds => commit('getRoundsSuccess', rounds.data),
                error => commit('getRoundsFailure', error)
            );
    },
    getOne({commit}, id) {
        commit('getOneRoundRequest');

        roundService.getById(id)
            .then(
                round => {
                    roundService.getPlayers(round.data.id).then(
                        teams => {
                            commit('getOneRoundSuccess', {round: round, teams: teams});
                            },
                        error => {console.log('booooo', error)
                            commit('getOneRoundFailure', error)}
                    )
                },
                error => commit('getOneRoundFailure', error)
            );

    },
    getRoundEvents({commit}, data) {
        roundService.getRoundEvents(data.round, data.type)
            .then(
                events => commit('getEventsSuccess', {type: data.type, events: events.data}),
                error => commit('getEventsFailure', error)
            );

    },
    addRoundEvent({commit, dispatch, getters}, data) {
        roundService.addRoundEvent(data.type, data.event)
            .then(
                event => {
                    dispatch('getRoundEvents', {round: data.event.round, type: data.type})
                    if (kf_event_types.indexOf(data.type) >= 0) {
                        console.log('GETTING NEW KILL FEED')
                        dispatch('getKillFeedItems', getters.round_id)
                    }
                    if (player_state_types.indexOf(data.type) >= 0) {
                        console.log('GETTING NEW PLAYER STATES')
                        dispatch('getPlayerStates', getters.round_id)
                    }
                },
                error => {
                    console.log("ERROR", error)
                    commit('addRoundEventFailure', error)
                }
            );

    },
    addUltimateUse({commit, dispatch, getters}, data) {
        roundService.addUltimateUse(data.id, data.time_point).then(

                event => {
                    dispatch('getRoundEvents', {round: getters.round_id, type: 'ultimates'});
                        dispatch('getPlayerStates', getters.round_id)
                }
        ).catch(
            error => {
                console.log("ERROR", error)
                commit('addUltimateUseFailure', error)
            });
    },
    clearUltimateUse({commit, dispatch, getters}, data) {
        roundService.clearUltimateUse(data.id).then(

                event => {
                    dispatch('getRoundEvents', {round: getters.round_id, type: 'ultimates'});
                        dispatch('getPlayerStates', getters.round_id)
                }
        ).catch(
            error => {
                console.log("ERROR", error)
                commit('clearUltimateUseFailure', error)
            });
    },
    updateRoundEvent({commit, dispatch, getters}, data) {
        roundService.updateRoundEvent(data.type, data.event)

            .then(
                event => {
                    console.log('UPDATED EVENT', event, data, getters.round_id)
                    dispatch('getRoundEvents', {round: getters.round_id, type: data.type})
                    if (kf_event_types.indexOf(data.type) >= 0) {
                        console.log('GETTING NEW KILL FEED')
                        dispatch('getKillFeedItems', getters.round_id)

                    }
                    if (player_state_types.indexOf(data.type) >= 0) {
                        console.log('GETTING NEW PLAYER STATES')
                        dispatch('getPlayerStates', getters.round_id)
                    }
                }
            ).catch(
            error => {
                console.log("ERROR", error)
                commit('updateRoundEventFailure', error)
            });

    },
    deleteRoundEvent({commit, dispatch, getters}, data) {
        roundService.deleteRoundEvent(data.type, data.id)

            .then(
                event => {
                    console.log('DELETED EVENT', event, data, getters.round_id)
                    dispatch('getRoundEvents', {round: getters.round_id, type: data.type})
                    if (kf_event_types.indexOf(data.type) >= 0) {
                        console.log('GETTING NEW KILL FEED')
                        dispatch('getKillFeedItems', getters.round_id)

                    }
                    if (player_state_types.indexOf(data.type) >= 0) {
                        console.log('GETTING NEW PLAYER STATES')
                        dispatch('getPlayerStates', getters.round_id)
                    }
                }
            ).catch(
            error => {
                console.log("ERROR", error)
                commit('deleteRoundEventFailure', error)
            });

    },
    getKillFeedItems({commit}, id) {
        commit('getKillFeedRequest');

        roundService.getKillFeedItems(id)
            .then(
                events => commit('getKillFeedSuccess', events.data),
                error => commit('getKillFeedFailure', error)
            );

    },
    getPlayerStates({commit}, id) {
        commit('getPlayerStatesRequest');

        roundService.getPlayerStates(id)
            .then(
                events => commit('getPlayerStatesSuccess', events.data),
                error => commit('getPlayerStatesFailure', error)
            );

    },
    getRoundStates({commit}, id) {
        commit('getRoundStatesRequest');

        roundService.getRoundStates(id)
            .then(
                events => commit('getRoundStatesSuccess', events.data),
                error => commit('getRoundStatesFailure', error)
            );

    },


    updateRound({commit, dispatch}, data) {
        let refresh = data.refresh;
        data = data.data;
        commit('updateRequest', data);

        roundService.updateRound(data)
            .then(
                round => {
                    commit('updateSuccess', round.data);
                    if (refresh) {
                        let i;
                        for (i = 0; i < event_types.length; i++) {
                            dispatch('getRoundEvents', {round: data.id, type: event_types[i]})

                        }
                        dispatch('getPlayerStates', data.id);
                        dispatch('getKillFeedItems', data.id);
                        dispatch('getRoundStates', data.id);

                    }


                },
                error => commit('updateFailure', {id, error: error.toString()})
            );
    },


    deleteRound({commit}, id) {
        commit('deleteRequest', id);

        roundService.deleteRound(id)
            .then(
                round => commit('deleteSuccess', round),
                error => commit('deleteFailure', {id, error: error.toString()})
            );
    }
};

const getters = {
    pagination (state) {
      return state.pagination
    },
    hero_picks: (state) => {
        console.log('HEROPICKS', state.hero_picks)
        return state.hero_picks;
    },
    kill_feed_events: (state) => {
        return state.kill_feed_events;
    },
    ultimates: (state) => {
        console.log('ULTIMATES', state.ultimates)
        return state.ultimates;
    },
    status_effects: (state) => {
        return state.status_effects;
    },
    point_gains: (state) => {
        return state.point_gains;
    },
    point_flips: (state) => {
        return state.point_flips;
    },
    pauses: (state) => {
        return state.pauses;
    },
    replays: (state) => {
        return state.replays;
    },
    overtimes: (state) => {
        return state.overtimes;
    },
    smaller_windows: (state) => {
        return state.smaller_windows;
    },
    zooms: (state) => {
        return state.zooms;
    },

    round_id: (state) => {
        console.log(state.one.item)
        return state.one.item.id
    },
    pausedAtTime: (state) => (time_point) => {

        if (state.round_states.loading) {
            return false
        }
        let i;
        for (i = 0; i < state.round_states.item.pauses.length; i++) {

            if (state.round_states.item.pauses[i].begin <= time_point && time_point < state.round_states.item.pauses[i].end) {
                return state.round_states.item.pauses[i].status === 'paused'
            }
        }

    },
    overtimeAtTime: (state) => (time_point) => {

        if (state.round_states.loading) {
            return false
        }
        let i;
        for (i = 0; i < state.round_states.item.overtimes.length; i++) {

            if (state.round_states.item.overtimes[i].begin <= time_point && time_point < state.round_states.item.overtimes[i].end) {
                return state.round_states.item.overtimes[i].status === 'overtime'
            }
        }

    },
    roundStateAtTime: (state) => (time_point) => {

        if (state.round_states.loading) {
            return false
        }
        let i;
        for (i = 0; i < state.round_states.item.point_status.length; i++) {

            if (state.round_states.item.point_status[i].begin <= time_point && time_point < state.round_states.item.point_status[i].end) {
                return state.round_states.item.point_status[i].status
            }
        }

    },
    heroAtTime: (state) => (player_id, time_point) => {
        if (state.one.loading) {
            return ''
        }
        if (!state.hero_picks) {
            return ''
        }
        let i, hero = '';

        for (i = 0; i < state.hero_picks.length; i++) {
            if (state.hero_picks[i].player.id === player_id) {
                if (state.hero_picks[i].time_point > time_point) {
                    break;
                }
                hero = state.hero_picks[i].new_hero;
            }
        }
        return hero
    },
    killFeedAtTime: (state, getters) => (time_point) => {
        if (state.kill_feed_items.loading || state.kill_feed_items.item === undefined) {
            return []
        }
        console.log('KILLFEEDITEMS', state.kill_feed_items.item)
        let i, event, events = [];

        for (i = 0; i < state.kill_feed_items.item.length; i++) {
            event = state.kill_feed_items.item[i];
            if (event.time_point < time_point - 7) {
                continue
            }
            if (event.time_point > time_point) {
                break
            }
            events.push(event);

        }
        events.reverse();

        return events.slice(0, 6)
    },
    ultStateAtTime: (state, getters) => (player_id, time_point) => {
        if (state.player_states.item) {
            let index, ult_states, i;
            index = getters.leftPlayerIndex(player_id);
            if (index >= 0) {
                ult_states = state.player_states.item.left[index].ult;
            }
            else {
                index = getters.rightPlayerIndex(player_id);
                if (index >= 0) {
                    ult_states = state.player_states.item.right[index].ult;

                }
                else {
                    return false
                }
            }
            for (i = 0; i < ult_states.length; i++) {
                if (ult_states[i].begin <= time_point && time_point < ult_states[i].end) {
                    return {'state': ult_states[i].status, 'id':ult_states[i].id}
                }
            }

        }
        return false
    },
    hasUltAtTime: (state, getters) => (player_id, time_point) => {
        if (state.player_states.item) {
            let index, ult_states, i;
            index = getters.leftPlayerIndex(player_id);
            if (index >= 0) {
                ult_states = state.player_states.item.left[index].ult;
            }
            else {
                index = getters.rightPlayerIndex(player_id);
                if (index >= 0) {
                    ult_states = state.player_states.item.right[index].ult;

                }
                else {
                    return false
                }
            }
            for (i = 0; i < ult_states.length; i++) {
                if (ult_states[i].begin <= time_point && time_point < ult_states[i].end) {
                    return ult_states[i].status === 'has_ult'
                }
            }

        }
        return false
    },
    aliveAtTime: (state, getters) => (player_id, time_point) => {
        if (state.player_states.item) {
            let index, alive_states, i;
            index = getters.leftPlayerIndex(player_id);
            if (index >= 0) {
                alive_states = state.player_states.item.left[index].alive;
            }
            else {
                index = getters.rightPlayerIndex(player_id);
                if (index >= 0) {
                    alive_states = state.player_states.item.right[index].alive;
                }
                else {
                    return false
                }
            }
            for (i = 0; i < alive_states.length; i++) {
                if (alive_states[i].begin <= time_point && time_point < alive_states[i].end) {
                    return alive_states[i].status === 'alive'
                }
            }
        }
        return false
    },
    stateAtTime: (state, getters) => (player_id, time_point, state_name) => {
        if (state.player_states.item) {
            let index, states, i;
            index = getters.leftPlayerIndex(player_id);
            if (index >= 0) {
                states = state.player_states.item.left[index][state_name];
            }
            else {
                index = getters.rightPlayerIndex(player_id);
                if (index >= 0) {
                    states = state.player_states.item.right[index][state_name];
                }
                else {
                    return false
                }
            }
            if (!states){
                    return false
            }
            for (i = 0; i < states.length; i++) {
                if (states[i].begin <= time_point && time_point < states[i].end) {
            if (state_name === 'status'){
                return states[i].status
            }
            else{
                    return states[i].status === state_name

            }
                }
            }
        }
        return false
    },
    playerOnLeftTeam: (state, getters) => (player_id) => {
        var on_left = false;
        getters.leftPlayers.forEach(player => {
            if (player.id === player_id) {
                on_left = true;
            }
        });
        return on_left
    },
    leftPlayerIndex: (state, getters) => (player_id) => {
        var index = 0, found = false;
        if (!state.one.loading) {
            getters.leftPlayers.forEach(player => {
                if (player_id == player.id) {
                    found = true;
                }
                if (!found) {

                    index += 1;
                }
            })
        }
        if (found) {
            return index
        }
        return -1
    },
    rightPlayerIndex: (state) => (player_id) => {
        let index = 0, found = false;
        if (state.one.teams.right_team) {
            state.one.teams.right_team.forEach(player => {
                if (player_id === player.id) {
                    found = true;
                }
                if (!found) {

                    index += 1;
                }
            });
        }
        if (found) {
            return index
        }
        return -1
    },
    leftPlayers: state => {
        return state.one.teams.left_team
    },
    rightPlayers: state => {
        return state.one.teams.right_team
    },
    allPlayers: (state, getters) => {
        return getters.leftPlayers.concat(getters.rightPlayers)
    },

};

const mutations = {
    setPagination (state, payload) {
      state.pagination = payload
    },
    getAllRequest(state) {
        state.all = {loading: true};
    },
    getAllSuccess(state, rounds) {
        state.all = {items: rounds};
    },
    getAllFailure(state, error) {
        state.all = {error};
    },
    getRoundsRequest(state) {
        state.round_status = {loading: true};
    },
    getRoundsSuccess(state, rounds) {
        console.log(rounds);
        state.round_status = {items: rounds.results, loading: false, count: rounds.count};
    },
    getRoundsFailure(state, error) {
        console.log(error);
        state.round_status = {error, loading: false};
    },

    getOneRoundRequest(state) {
        state.one = {loading: true};
    },
    getOneRoundSuccess(state, round) {
        state.one = {item: round.round.data, teams: round.teams.data, loading:false};
        console.log(state.one)
    },
    getOneRoundFailure(state, error) {
        console.log(error)
        state.one = {error, loading:false};
    },

    updateRequest(state) {
    },
    updateSuccess(state, game) {

    },
    updateFailure(state, error) {
        console.log(error)
        state.one = { error };
    },

    createRequest(state) {
    },
    createSuccess(state, game) {

    },
    createFailure(state, error) {
        console.log(error)
    },

    getEventsSuccess(state, data) {
        state[data.type] = data.events;
    },
    getEventsFailure(state, error) {
        console.log(error)
        state.events = {error};
    },

    getKillFeedRequest(state) {
        state.kill_feed_items = {loading: true};
    },
    getKillFeedSuccess(state, kill_feed_items) {
        state.kill_feed_items = {item: kill_feed_items};
    },
    getKillFeedFailure(state, error) {
        console.log(error)
        state.kill_feed_items = {error};
    },

    getPlayerStatesRequest(state) {
        state.player_states = {loading: true};
    },
    getPlayerStatesSuccess(state, player_states) {
        state.player_states = {item: player_states};
    },
    getPlayerStatesFailure(state, error) {
        console.log(error)
        state.player_states = {error};
    },

    getRoundStatesRequest(state) {
        state.round_states = {loading: true};
    },
    getRoundStatesSuccess(state, round_states) {
        state.round_states = {item: round_states};
    },
    getRoundStatesFailure(state, error) {
        console.log(error)
        state.round_states = {error};
    },

    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        if (state.all.items) {
            state.all.items = state.all.items.map(round =>
                round.id === id
                    ? {...round, deleting: true}
                    : round
            )
        }
    },
    deleteSuccess(state, id) {
        // remove deleted user from state

        if (state.all.items) {
            state.all.items = state.all.items.filter(round => round.id !== id)
        }
    },
    deleteFailure(state, {id, error}) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user

        if (state.all.items) {
            state.all.items = state.items.map(round => {
                if (round.id === id) {
                    // make copy of user without 'deleting:true' property
                    const {deleting, ...roundCopy} = round;
                    // return copy of user with 'deleteError:[error]' property
                    return {...roundCopy, deleteError: error};
                }

                return round;
            })
        }
    },
    updateRequest(state, round) {

    },
    updateSuccess(state, round) {

    },
    updateFailure(state, {round, error}) {
        console.log('ERROR', error);
    }
};

export const rounds = {
    namespaced: true,
    state,
    actions,
    mutations,
    getters
};