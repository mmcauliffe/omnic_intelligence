import config from 'config';
import { authHeader } from '../helper';
import axios from 'axios';

export const roundService = {
    getById,
    getRounds,
    createRound,
    updateRound,
    deleteRound,
    getPlayers,
    getRoundStates,
    getKillFeedEvents,
    getPlayerStates,
    getRoundEvents,
    addRoundEvent,
    updateRoundEvent,
    deleteRoundEvent,

};


function getById(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/rounds/${id}/`, requestOptions).then(handleResponse);
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
    console.log(round)
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

function getPlayers(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/rounds/${id}/players/`, requestOptions).then(handleResponse);
}


function getRoundStates(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/rounds/${id}/round_states/`, requestOptions).then(handleResponse);
}


function getKillFeedEvents(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/rounds/${id}/kill_feed_events/`, requestOptions).then(handleResponse);
}


function getPlayerStates(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/rounds/${id}/player_states/`, requestOptions).then(handleResponse);
}


function getRoundEvents(id, type) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };
    console.log(id, type)
    return fetch(`${config.apiUrl}/rounds/${id}/${type}/`, requestOptions).then(handleResponse);
}


function addRoundEvent(type, event) {
    const requestOptions = {
        method: 'POST',
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
    };

    return fetch(`${config.apiUrl}/${type}/`, requestOptions).then(handleResponse);
}


function updateRoundEvent(type, event) {
    const requestOptions = {
        method: 'PUT',
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
    };
    console.log(event)
    return fetch(`${config.apiUrl}/${type}/${event.id}/`, requestOptions).then(handleResponse);
}


function deleteRoundEvent(type, event_id) {
    const requestOptions = {
        method: 'DELETE',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/${type}/${event_id}/`, requestOptions).then(handleResponse);
}


function handleResponse(response) {
    console.log(response)
    return response.text().then(text => {
        const data = text && JSON.parse(text);
        console.log(response.ok)
        if (!response.ok) {
            if (response.status === 401) {
                // auto logout if 401 response returned from api
                logout();
                location.reload(true);
            }
            const error = (data && data.non_field_errors) || response.statusText;
            return Promise.reject(error);
        }
        console.log(data)
        return data;
    });
}