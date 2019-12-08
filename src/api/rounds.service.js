import config from 'config';
import { authHeader } from '../helper';
import axios from 'axios';

export const roundService = {
    getById,
    getRounds,
    getPossibleDenyRounds,
    getPossibleErrorRounds,
    createRound,
    updateRound,
    deleteRound,
    getPlayers,
    getRoundStates,
    getKillFeedItems,
    getPlayerStates,
    getRoundEvents,
    addRoundEvent,
    addUltimateUse,
    clearUltimateUse,
    updateRoundEvent,
    deleteRoundEvent,

};


function getById(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/rounds/${id}/`, requestOptions);
}

function createRound(round) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' }
    };
    return axios.post(`${config.apiUrl}/rounds/`, round, requestOptions);
}


function updateRound(round) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' }
    };
    return axios.put(`${config.apiUrl}/rounds/${round.id}/`, round, requestOptions);
}

function deleteRound(id){
    const requestOptions = {
        headers: { ...authHeader()},
    };

    return axios.delete(`${config.apiUrl}/rounds/${id}/`, requestOptions);
}

function getRounds(params){
    const requestOptions = {
        headers: authHeader(),
        params: params
    };

    return axios.get(`${config.apiUrl}/round_status/`, requestOptions);

}

function getPossibleDenyRounds(params){
    const requestOptions = {
        headers: authHeader(),
        params: params
    };

    return axios.get(`${config.apiUrl}/possible_denies/`, requestOptions);

}

function getPossibleErrorRounds(params){
    const requestOptions = {
        headers: authHeader(),
        params: params
    };

    return axios.get(`${config.apiUrl}/possible_errors/`, requestOptions);

}

function getPlayers(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/rounds/${id}/players/`, requestOptions);
}


function getRoundStates(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/rounds/${id}/round_states/`, requestOptions);
}


function getKillFeedItems(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/rounds/${id}/kill_feed_items/`, requestOptions);
}


function getPlayerStates(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/rounds/${id}/player_states/`, requestOptions);
}


function getRoundEvents(id, type) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/rounds/${id}/${type}/`, requestOptions);
}


function addRoundEvent(type, event) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.post(`${config.apiUrl}/${type}/`, event, requestOptions);
}


function addUltimateUse(ultimate_id, time_point) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.put(`${config.apiUrl}/ultimates/${ultimate_id}/add_use/`, {used: time_point}, requestOptions);
}


function clearUltimateUse(ultimate_id) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.put(`${config.apiUrl}/ultimates/${ultimate_id}/clear_use/`, {}, requestOptions);
}


function updateRoundEvent(type, event) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.put(`${config.apiUrl}/${type}/${event.id}/`,event, requestOptions);
}


function deleteRoundEvent(type, event_id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.delete(`${config.apiUrl}/${type}/${event_id}/`, requestOptions);
}

