import config from 'config';
import { authHeader } from '../helper';
import axios from 'axios';

export const matchService = {
    getAll,
    getById,
    getGames,
    getTeams,
    updateMatch,
    deleteMatch
};

function getAll() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/matches/`, requestOptions);
}


function getById(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/matches/${id}/`, requestOptions);
}

function getGames(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/matches/${id}/games/`, requestOptions);
}

function getTeams(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/matches/${id}/teams/`, requestOptions);
}

function updateMatch(match) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.put(`${config.apiUrl}/matches/${match.id}/`, match, requestOptions);
}

// prefixed function name with underscore because delete is a reserved word in javascript
function deleteMatch(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.delete(`${config.apiUrl}/matches/${id}/`, requestOptions);
}
