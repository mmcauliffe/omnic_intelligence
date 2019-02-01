import config from 'config';
import { authHeader } from '../helper';
import axios from "axios/index";


export const teamService = {
    getTeam,
    getAllTeams,
    createTeam,
    updateTeam,
    deleteTeam
};

function getTeam(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/teams/${id}/`, requestOptions);
}

function getAllTeams() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/teams/`, requestOptions);
}

function createTeam(team) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.post(`${config.apiUrl}/teams/`, team, requestOptions);
}

function updateTeam(team) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
    };

    return axios.put(`${config.apiUrl}/teams/${team.id}/`, team, requestOptions);
}

function deleteTeam(id){
    const requestOptions = {
        headers: { ...authHeader()},
    };

    return axios.delete(`${config.apiUrl}/teams/${id}/`, requestOptions);
}