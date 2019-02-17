import config from 'config';
import { authHeader } from '../helper';
import axios from "axios/index";

export const vodService = {
    getAnnotationSources,
    getSpectatorModes,
    getFilmFormats,
    getStreamChannels,
    getVods,
    getVod,
    createVod,
    updateVod,
    deleteVod,
    getAvailableVods,
    getStreamVods,
    getVodStatusChoices,
    getVodTypeChoices,
    getVodPossibleMatches,
    getRounds,
    getMatches,
    getGames,
};


function getVod(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/vods/${id}/`, requestOptions);
}

function getVodPossibleMatches(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/vods/${id}/possible_matches/`, requestOptions);
}

function getRounds(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/vods/${id}/rounds/`, requestOptions);
}

function getGames(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/vods/${id}/games/`, requestOptions);
}

function getMatches(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/vods/${id}/matches/`, requestOptions);
}


function createVod(vod) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' }
    };
    return axios.post(`${config.apiUrl}/vods/`, vod, requestOptions);
}


function updateVod(vod) {
    const requestOptions = {
        headers: { ...authHeader(), 'Content-Type': 'application/json' }
    };

    return axios.put(`${config.apiUrl}/vods/${vod.id}/`, vod, requestOptions);
}

function deleteVod(id){
    const requestOptions = {
        headers: { ...authHeader()},
    };

    return axios.delete(`${config.apiUrl}/vods/${id}/`, requestOptions);
}


function getStreamVods(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/stream_channels/${id}/vods/`, requestOptions);
}


function getAvailableVods(id) {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/stream_channels/${id}/available_vods/`, requestOptions);
}

function getAnnotationSources() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/annotation_source_choices/`, requestOptions);
}

function getVodStatusChoices() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/vod_status_choices/`, requestOptions);
}

function getVodTypeChoices() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/vod_type_choices/`, requestOptions);
}

function getSpectatorModes() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/spectator_mode_choices/`, requestOptions);
}

function getVods(params){
    const requestOptions = {
        headers: authHeader(),
        params: params
    };

    return axios.get(`${config.apiUrl}/vod_status/`, requestOptions);

}

function getFilmFormats() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/film_format_choices/`, requestOptions);
}

function getStreamChannels() {
    const requestOptions = {
        headers: authHeader()
    };

    return axios.get(`${config.apiUrl}/stream_channels/`, requestOptions);
}


