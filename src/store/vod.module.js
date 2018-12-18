import { vodService } from '../api';

const state = {
    annotation_sources: {},
    spectator_modes: {},
    film_formats: {},
    stream_channels: {},
    timestamp: 0.0
};

const actions = {
    getAnnotationSources({ commit }) {
        commit('getAnnotationSourcesRequest');

        vodService.getAnnotationSources()
            .then(
                events => commit('getAnnotationSourcesSuccess', events),
                error => commit('getAnnotationSourcesFailure', error)
            );
    },
    getSpectatorModes({ commit }) {
        commit('getSpectatorModesRequest');

        vodService.getSpectatorModes()
            .then(
                events => commit('getSpectatorModesSuccess', events),
                error => commit('getSpectatorModesFailure', error)
            );
    },
    getFilmFormats({ commit }) {
        commit('getFilmFormatsRequest');

        vodService.getFilmFormats()
            .then(
                events => commit('getFilmFormatsSuccess', events),
                error => commit('getFilmFormatsFailure', error)
            );
    },
    getStreamChannels({ commit }) {
        commit('getStreamChannelsRequest');

        vodService.getStreamChannels()
            .then(
                events => commit('getStreamChannelsSuccess', events),
                error => commit('getStreamChannelsFailure', error)
            );
    },
    updateTimestamp({ commit }, timestamp){
        console.log('update', timestamp)
       commit('updateTimestampSuccess', timestamp) ;
    },
};

const mutations = {
    updateTimestampSuccess(state, timestamp){
        state.timestamp = timestamp
    },
    getAnnotationSourcesRequest(state) {
        state.annotation_sources = { loading: true };
    },
    getAnnotationSourcesSuccess(state, sources) {
        state.annotation_sources = { items: sources };
    },
    getAnnotationSourcesFailure(state, error) {
        state.annotation_sources = { error };
    },

    getSpectatorModesRequest(state) {
        state.spectator_modes = { loading: true };
    },
    getSpectatorModesSuccess(state, sources) {
        state.spectator_modes = { items: sources };
    },
    getSpectatorModesFailure(state, error) {
        state.spectator_modes = { error };
    },

    getFilmFormatsRequest(state) {
        state.film_formats = { loading: true };
    },
    getFilmFormatsSuccess(state, sources) {
        state.film_formats = { items: sources };
    },
    getFilmFormatsFailure(state, error) {
        state.film_formats = { error };
    },

    getStreamChannelsRequest(state) {
        state.stream_channels = { loading: true };
    },
    getStreamChannelsSuccess(state, sources) {
        state.stream_channels = { items: sources };
    },
    getStreamChannelsFailure(state, error) {
        state.stream_channels = { error };
    },

};

export const vods = {
    namespaced: true,
    state,
    actions,
    mutations
};