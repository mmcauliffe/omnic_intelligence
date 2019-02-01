import config from 'config';
import { authHeader } from '../helper';
import axios from "axios/index";

export const eventService = {
    getAll,
    getById,
    getMatches,
    update,
    delete: _delete,
    getStreamVods,
    getAvailableVods,
};

function getAll() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/events/`, requestOptions).then(handleResponse);
}


function getById(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/events/${id}/`, requestOptions).then(handleResponse);
}

function getMatches(id) {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/events/${id}/matches/`, requestOptions).then(handleResponse);
}


function getStreamVods(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/events/${id}/vods/`, requestOptions);
}


function getAvailableVods(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/events/${id}/available_vods/`, requestOptions);
}


function update(event) {
    const requestOptions = {
        method: 'PUT',
        headers: { ...authHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
    };

    return fetch(`${config.apiUrl}/events/${event.id}/`, requestOptions).then(handleResponse);
}

// prefixed function name with underscore because delete is a reserved word in javascript
function _delete(id) {
    const requestOptions = {
        method: 'DELETE',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/events/${id}/`, requestOptions).then(handleResponse);
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