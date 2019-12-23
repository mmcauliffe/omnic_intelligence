import config from 'config';
import { authHeader } from '../helper';

export const overwatchService = {
    getHeroes,
    getHeroDamagingAbilities,
    getHeroRevivingAbilities,
    getAbilities,
    getMaps,
    getMapTypes,
    getNPCs,
    getTeamColors,
    getMapModes,
    getSides,
    getSubmaps,
    getStatusEffectChoices,
};

function getHeroes() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/heroes/`, requestOptions).then(handleResponse);
}

function getHeroDamagingAbilities(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/heroes/${id}/damaging_abilities/`, requestOptions).then(handleResponse);
}

function getHeroRevivingAbilities(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/heroes/${id}/reviving_abilities/`, requestOptions).then(handleResponse);
}


function getAbilities() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/abilities/`, requestOptions).then(handleResponse);
}

function getMaps() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/maps/`, requestOptions).then(handleResponse);
}

function getStatusEffectChoices() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/status_effect_choices/`, requestOptions).then(handleResponse);
}

function getMapTypes() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/map_types/`, requestOptions).then(handleResponse);
}

function getNPCs() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/npcs/`, requestOptions).then(handleResponse);
}

function getTeamColors() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/team_colors/`, requestOptions).then(handleResponse);
}

function getMapModes() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/map_modes/`, requestOptions).then(handleResponse);
}

function getSides() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/sides/`, requestOptions).then(handleResponse);
}

function getSubmaps() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/submaps/`, requestOptions).then(handleResponse);
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