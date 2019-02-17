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
    deleteGame,
    updateTeams
};

function getAll() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/games/`, requestOptions);
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
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/games/${id}/`, requestOptions);
}

function getTeams(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/games/${id}/teams/`, requestOptions);
}

function updateTeams(game) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.put(`${config.apiUrl}/games/${game.id}/update_teams/`, game, requestOptions);
}


function getRounds(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/games/${id}/rounds/`, requestOptions);
}
