import config from 'config';
import { authHeader } from '../helper';

export const vodService = {
    getAnnotationSources,
    getSpectatorModes,
    getFilmFormats,
    getStreamChannels
};

function getAnnotationSources() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/annotation_sources/`, requestOptions).then(handleResponse);
}

function getSpectatorModes() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/spectator_modes/`, requestOptions).then(handleResponse);
}

function getFilmFormats() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/film_formats/`, requestOptions).then(handleResponse);
}

function getStreamChannels() {
    const requestOptions = {
        method: 'GET',
        headers: authHeader()
    };

    return fetch(`${config.apiUrl}/stream_channels/`, requestOptions).then(handleResponse);
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