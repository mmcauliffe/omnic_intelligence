import {gameService, roundService} from '../api';

const kf_event_types = ['kills', 'kill_npcs', 'deaths', 'npc_deaths', 'revives', 'ult_denials'];
const player_state_types = ['kills', 'deaths', 'revives', 'ult_gains', 'ult_uses', 'ult_ends'];
const event_types = ['switches', 'kills', 'kill_npcs', 'deaths', 'npc_deaths', 'ult_gains', 'ult_uses',
    'ult_ends', 'ult_denials', 'status_effects',
    'revives', 'point_gains', 'point_flips', 'pauses', 'replays', 'overtimes', 'smaller_windows'];
const state = {
    all: {},
    round_status: {},
    pagination: {
        page: 1,
        rowsPerPage: 10,
    },
    one: {},
    switches: [],
    kills: [],
    kill_npcs: [],
    deaths: [],
    npc_deaths: [],
    ult_gains: [],
    ult_uses: [],
    ult_ends: [],
    ult_denials: [],
    status_effects: [],
    revives: [],
    point_gains: [],
    point_flips: [],
    pauses: [],
    replays: [],
    overtimes: [],
    smaller_windows: [],
    kill_feed_events: {},
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
                round => commit('updateSuccess', round),
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
        commit('getOneRequest');

        roundService.getById(id)
            .then(
                round => {
                    roundService.getPlayers(round.id).then(
                        teams => commit('getOneSuccess', {round: round, teams: teams}),
                        error => commit('getOneFailure', error)
                    )
                },
                error => commit('getOneFailure', error)
            );

    },
    getRoundEvents({commit}, data) {
        console.log('GETTING EVENTS', data)
        roundService.getRoundEvents(data.round, data.type)
            .then(
                events => commit('getEventsSuccess', {type: data.type, events: events}),
                error => commit('getEventsFailure', error)
            );

    },
    addRoundEvent({commit, dispatch, getters}, data) {
        roundService.addRoundEvent(data.type, data.event)
            .then(
                event => {
                    console.log('ADDED EVENT', event, data)
                    dispatch('getRoundEvents', {round: data.event.round, type: data.type})
                    if (kf_event_types.indexOf(data.type) >= 0) {
                        console.log('GETTING NEW KILL FEED')
                        dispatch('getKillFeedEvents', getters.round_id)
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
    updateRoundEvent({commit, dispatch, getters}, data) {
        roundService.updateRoundEvent(data.type, data.event)

            .then(
                event => {
                    console.log('UPDATED EVENT', event, data, getters.round_id)
                    dispatch('getRoundEvents', {round: getters.round_id, type: data.type})
                    console.log('CHECK', kf_event_types.indexOf(data.type) >= 0)
                    if (kf_event_types.indexOf(data.type) >= 0) {
                        console.log('GETTING NEW KILL FEED')
                        dispatch('getKillFeedEvents', getters.round_id)

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
                        dispatch('getKillFeedEvents', getters.round_id)

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
    getKillFeedEvents({commit}, id) {
        commit('getKillFeedRequest');

        roundService.getKillFeedEvents(id)
            .then(
                events => commit('getKillFeedSuccess', events),
                error => commit('getKillFeedFailure', error)
            );

    },
    getPlayerStates({commit}, id) {
        commit('getPlayerStatesRequest');

        roundService.getPlayerStates(id)
            .then(
                events => commit('getPlayerStatesSuccess', events),
                error => commit('getPlayerStatesFailure', error)
            );

    },
    getRoundStates({commit}, id) {
        commit('getRoundStatesRequest');

        roundService.getRoundStates(id)
            .then(
                events => commit('getRoundStatesSuccess', events),
                error => commit('getRoundStatesFailure', error)
            );

    },


    update({commit, dispatch}, data) {
        let refresh = data.refresh;
        data = data.data;
        commit('updateRequest', data);

        roundService.update(data)
            .then(
                round => {
                    commit('updateSuccess', round);
                    if (refresh) {
                        let i;
                        for (i = 0; i < event_types.length; i++) {
                            dispatch('getRoundEvents', {round: data.id, type: event_types[i]})

                        }
                        dispatch('getPlayerStates', data.id);
                        dispatch('getKillFeedEvents', data.id);
                        dispatch('getRoundStates', data.id);

                    }


                },
                error => commit('updateFailure', {id, error: error.toString()})
            );
    },


    delete({commit}, id) {
        commit('deleteRequest', id);

        roundService.delete(id)
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
    switches: (state) => {
        return state.switches;
    },
    kills: (state) => {
        return state.kills;
    },
    kill_npcs: (state) => {
        return state.kill_npcs;
    },
    deaths: (state) => {
        return state.deaths;
    },
    npc_deaths: (state) => {
        return state.npc_deaths;
    },
    revives: (state) => {
        return state.revives;
    },
    ult_gains: (state) => {
        return state.ult_gains;
    },
    ult_uses: (state) => {
        return state.ult_uses;
    },
    ult_ends: (state) => {
        return state.ult_ends;
    },
    ult_denials: (state) => {
        return state.ult_denials;
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
                if (state.round_states.item.pauses[i].status === 'paused') {
                    return true
                }
                else {
                    return false
                }
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
                if (state.round_states.item.overtimes[i].status === 'paused') {
                    return true
                }
                else {
                    return false
                }
            }
        }

    },
    heroAtTime: (state) => (player_id, time_point) => {
        if (state.one.loading) {
            return ''
        }
        if (!state.switches) {
            return ''
        }
        let i, hero = '';

        for (i = 0; i < state.switches.length; i++) {
            if (state.switches[i].player.id === player_id) {
                if (state.switches[i].time_point > time_point) {
                    break;
                }
                hero = state.switches[i].new_hero;
            }
        }
        return hero
    },
    killFeedAtTime: (state, getters) => (time_point) => {
        console.log('KILL FEED EVENTS', state.kill_feed_events.error)
        if (state.kill_feed_events.loading || state.kill_feed_events.item == undefined) {
            return []
        }
        let i, event, events = [];

        for (i = 0; i < state.kill_feed_events.item.length; i++) {
            event = state.kill_feed_events.item[i];
            if (event.time_point < time_point - 7) {
                continue
            }
            console.log(event.time_point, time_point)
            if (event.time_point > time_point) {
                break
            }
            events.push(event);
            console.log(event);

        }
        events.reverse();

        return events.slice(0, 6)
    },
    ultStateAtTime: (state, getters) => (player_id, time_point) => {
        if (state.player_states.item) {
            let index, ult_states, i;
            index = getters.leftPlayerIndex(player_id);
            if (index >= 0) {
                console.log(index, state.player_states.item.left[index])
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
                    return ult_states[i].status
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
                console.log(index, state.player_states.item.left[index])
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
                    if (ult_states[i].status === 'has_ult') {
                        return true
                    }
                    else {
                        return false
                    }
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

                if (alive_states[i].begin <= time_point && time_point <= alive_states[i].end) {
                    if (alive_states[i].status === 'alive') {
                        return true
                    }
                    else {
                        return false
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

    getOneRequest(state) {
        state.one = {loading: true};
    },
    getOneSuccess(state, round) {
        state.one = {item: round.round, teams: round.teams, loading:false};
    },
    getOneFailure(state, error) {
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
        console.log(data.type, data.events)
    },
    getEventsFailure(state, error) {
        state.events = {error};
    },

    getKillFeedRequest(state) {
        state.kill_feed_events = {loading: true};
    },
    getKillFeedSuccess(state, kill_feed_events) {
        state.kill_feed_events = {item: kill_feed_events};
    },
    getKillFeedFailure(state, error) {
        state.kill_feed_events = {error};
    },

    getPlayerStatesRequest(state) {
        state.player_states = {loading: true};
    },
    getPlayerStatesSuccess(state, player_states) {
        state.player_states = {item: player_states};
    },
    getPlayerStatesFailure(state, error) {
        state.player_states = {error};
    },

    getRoundStatesRequest(state) {
        state.round_states = {loading: true};
    },
    getRoundStatesSuccess(state, round_states) {
        state.round_states = {item: round_states};
    },
    getRoundStatesFailure(state, error) {
        state.round_states = {error};
    },

    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        state.all.items = state.all.items.map(round =>
            round.id === id
                ? {...round, deleting: true}
                : round
        )
    },
    deleteSuccess(state, id) {
        // remove deleted user from state
        state.all.items = state.all.items.filter(round => round.id !== id)
    },
    deleteFailure(state, {id, error}) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        state.all.items = state.items.map(round => {
            if (round.id === id) {
                // make copy of user without 'deleting:true' property
                const {deleting, ...roundCopy} = round;
                // return copy of user with 'deleteError:[error]' property
                return {...roundCopy, deleteError: error};
            }

            return round;
        })
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