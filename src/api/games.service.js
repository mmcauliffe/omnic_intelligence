import config from 'config';
import { authHeader } from '../helper';
import axios from "axios/index";

export const gameService = {
    getAll,
    getById,
    getRounds,
    getTeams,
    createGame,
    updateGame,
    deleteGame
};

function getAll() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/games/`, requestOptions).then(handleResponse);
}

function createGame(game) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' }
    };
    return axios.post(`${config.apiUrl}/games/`, game, requestOptions);
}


function updateGame(game) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' }
    };

    return axios.put(`${config.apiUrl}/games/${game.id}/`, game, requestOptions);
}

function deleteGame(id){
    const requestOptions = {
        headers: { ...authHeader()},
    };

    return axios.delete(`${config.apiUrl}/games/${id}/`, requestOptions);
}


function getById(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/games/${id}/`, requestOptions).then(handleResponse);
}

function getTeams(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/games/${id}/teams/`, requestOptions).then(handleResponse);
}

function getRounds(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/games/${id}/rounds/`, requestOptions).then(handleResponse);
}


function handleResponse(response) {
    return response.text().then(text => {
        const data = text && JSON.parse(text);
        if (!response.ok) {
            if (response.status === 401) {
                // auto logout if 401 response returned from api
                logout();
                location.reload(true);
            }
            const error = (data && data.non_field_errors) || response.statusText;
            return Promise.reject(error);
        }

        return data;
    });
}