import config from 'config';
import { authHeader } from '../helper';
import axios from "axios/index";


export const playerService = {
    getPlayer,
    getPlayerStatistics,
    getPlayerRecentMatches,
    getPlayerTeams,
    getPlayers,
    getAllPlayers,
    createPlayer,
    updatePlayer,
    deletePlayer
};

function getPlayer(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/player_status/${id}/`, requestOptions);
}

function getPlayerStatistics(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/player_status/${id}/stats/`, requestOptions);
}

function getPlayerRecentMatches(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/player_status/${id}/recent_matches/`, requestOptions);
}

function getPlayerTeams(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/player_status/${id}/teams/`, requestOptions);
}

function getPlayers(params){
    const requestOptions = {
        headers: authHeader(),
        params: params
    };

    return axios.get(`${config.apiUrl}/player_status/`, requestOptions);

}

function getAllPlayers() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/player_status/`, requestOptions);
}

function createPlayer(players) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.post(`${config.apiUrl}/players/`, player, requestOptions);
}

function updatePlayer(players) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.put(`${config.apiUrl}/players/${player.id}/`, player, requestOptions);
}

function deletePlayer(id){
    const requestOptions = {
        headers: { ...authHeader()},
    };

    return axios.delete(`${config.apiUrl}/players/${id}/`, requestOptions);
}