import {roundService, teamService, vodService} from '../api';

const state = {
    annotation_sources: {},
    spectator_modes: {},
    film_formats: {},
    vod_type_choices: {},
    vod_status_choices: {},
    stream_channels: {},
    timestamp: 0.0,
    duration: 0,
    vod_status: {},
    pagination: {
        page: 1,
        rowsPerPage: 10,
    },
    one: {},
    available_vods: {},
    stream_vods: {},
    vod_event_matches: {},
    rounds: {},
    matches: {},
    games: {}
};

const actions = {
    getOne({commit}, id) {
        commit('getOneRequest');

        vodService.getVod(id)
            .then(
                vod => commit('getOneSuccess', vod),
                error => commit('getOneFailure', error)
            );

    },
    getOnePossibleMatches({commit}, id) {
        commit('getOnePossibleMatchesRequest');

        vodService.getVodPossibleMatches(id)
            .then(
                matches => commit('getOnePossibleMatchesSuccess', matches),
                error => commit('getOnePossibleMatchesFailure', error)
            );

    },
    getOneRounds({commit}, id) {
        commit('getOneRoundsRequest');

        vodService.getRounds(id)
            .then(
                rounds => commit('getOneRoundsSuccess', rounds),
                error => commit('getOneRoundsFailure', error)
            );
    },
    getOneGames({commit}, id) {
        commit('getOneGamesRequest');

        vodService.getGames(id)
            .then(
                games => commit('getOneGamesSuccess', games),
                error => commit('getOneGamesFailure', error)
            );
    },
    getOneMatches({commit}, id) {
        commit('getOneMatchesRequest');

        vodService.getMatches(id)
            .then(
                matches => commit('getOneMatchesSuccess', matches),
                error => commit('getOneMatchesFailure', error)
            );
    },
    createVod( { commit }, vod){
        commit('createRequest');

        vodService.createVod(vod)
            .then(
                vod => commit('createSuccess', vod),
                error => commit('createFailure', error)
            );

    },
    updateVod( { commit }, vod){
        commit('updateRequest');

        vodService.updateVod(vod)
            .then(
                vod => commit('updateSuccess', vod),
                error => commit('updateFailure', error)
            );

    },
    deleteVod({ commit }, id) {
        commit('deleteRequest', id);

        vodService.deleteVod(id)
            .then(
                vod => commit('deleteSuccess', id),
                error => commit('deleteSuccess', { id, error: error.toString() })
            );
    },
    getAvailableVods({commit}, id){
        vodService.getAvailableVods(id).then(
            vods => commit('getAvailableVodsSuccess', vods),
                error => commit('getAvailableVodsFailure', error)
        )
    },
    getStreamVods({commit}, id){
        vodService.getStreamVods(id).then(
            vods => commit('getStreamVodsSuccess', vods),
                error => commit('getStreamVodsFailure', error)
        )
    },
    updatePagination({commit}, value){
       commit('setPagination', value)
    },
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
    getVodStatusChoices({ commit }) {
        commit('getVodStatusChoicesRequest');

        vodService.getVodStatusChoices()
            .then(
                events => commit('getVodStatusChoicesSuccess', events),
                error => commit('getVodStatusChoicesFailure', error)
            );
    },
    getVodTypeChoices({ commit }) {
        commit('getVodTypeChoicesRequest');

        vodService.getVodTypeChoices()
            .then(
                events => commit('getVodTypeChoicesSuccess', events),
                error => commit('getVodTypeChoicesFailure', error)
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
    updateDuration({ commit }, duration){
       commit('updateDurationSuccess', duration) ;
    },
    getVods({commit}, data) {
        commit('getVodsRequest');
        vodService.getVods(data)
            .then(
                vods => commit('getVodsSuccess', vods.data),
                error => commit('getVodsFailure', error)
            );
    },
};

const getters = {
    pagination(state) {
        return state.pagination
    },
}

const mutations = {
    setPagination (state, payload) {
      state.pagination = payload
    },
    getVodsRequest(state) {
        state.vod_status = {loading: true};
    },
    getVodsSuccess(state, vods) {
        console.log(vods);
        state.vod_status = {items: vods.results, loading: false, count: vods.count};
    },
    getVodsFailure(state, error) {
        console.log(error);
        state.vod_status = {error, loading: false};
    },

    getStreamVodsRequest(state) {
        state.stream_vods = {loading: true};
    },
    getStreamVodsSuccess(state, vods) {
        console.log(vods);
        state.stream_vods = {items: vods.data, loading: false};
    },
    getStreamVodsFailure(state, error) {
        console.log(error);
        state.stream_vods = {error, loading: false};
    },

    getAvailableVodsRequest(state) {
        state.available_vods = {loading: true};
    },
    getAvailableVodsSuccess(state, vods) {
        state.available_vods = {items: vods.data, loading: false};
        console.log(vods.data)
    },
    getAvailableVodsFailure(state, error) {
        state.available_vods = {error, loading:false};
    },

    getOneRequest(state) {
        state.one = {loading: true};
    },
    getOneSuccess(state, vod) {
        state.one = {item: vod.data, loading: false};
    },
    getOneFailure(state, error) {
        state.one = {error, loading:false};
    },

    getOnePossibleMatchesRequest(state) {
        state.vod_event_matches = {loading: true};
    },
    getOnePossibleMatchesSuccess(state, matches) {
        state.vod_event_matches = {items: matches.data, loading: false};
    },
    getOnePossibleMatchesFailure(state, error) {
        state.vod_event_matches = {error, loading:false};
    },

    getOneRoundsRequest(state) {
        state.rounds = {loading: true};
    },
    getOneRoundsSuccess(state, rounds) {
        state.rounds = {items: rounds.data, loading: false};
    },
    getOneRoundsFailure(state, error) {
        state.rounds = {error, loading:false};
    },

    getOneGamesRequest(state) {
        state.games = {loading: true};
    },
    getOneGamesSuccess(state, games) {
        state.games = {items: games.data, loading: false};
    },
    getOneGamesFailure(state, error) {
        state.games = {error, loading:false};
    },

    getOneMatchesRequest(state) {
        state.matches = {loading: true};
    },
    getOneMatchesSuccess(state, matches) {
        state.matches = {items: matches.data, loading: false};
    },
    getOneMatchesFailure(state, error) {
        state.matches = {error, loading:false};
    },

    updateTimestampSuccess(state, timestamp){
        state.timestamp = timestamp
        console.log('UPDATED TO', state.timestamp)
    },

    updateDurationSuccess(state, duration){
        state.duration = duration
    },
    getAnnotationSourcesRequest(state) {
        state.annotation_sources = { loading: true };
    },
    getAnnotationSourcesSuccess(state, sources) {
        state.annotation_sources = { items: sources.data };
    },
    getAnnotationSourcesFailure(state, error) {
        state.annotation_sources = { error };
    },

    getSpectatorModesRequest(state) {
        state.spectator_modes = { loading: true };
    },
    getSpectatorModesSuccess(state, sources) {
        state.spectator_modes = { items: sources.data };
    },
    getSpectatorModesFailure(state, error) {
        state.spectator_modes = { error };
    },

    getVodStatusChoicesRequest(state) {
        state.vod_status_choices = { loading: true };
    },
    getVodStatusChoicesSuccess(state, choices) {
        state.vod_status_choices = { items: choices.data };
    },
    getVodStatusChoicesFailure(state, error) {
        state.vod_status_choices = { error };
    },

    getVodTypeChoicesRequest(state) {
        state.vod_type_choices = { loading: true };
    },
    getVodTypeChoicesSuccess(state, choices) {
        state.vod_type_choices = { items: choices.data };
    },
    getVodTypeChoicesFailure(state, error) {
        state.vod_type_choices = { error };
    },

    getFilmFormatsRequest(state) {
        state.film_formats = { loading: true };
    },
    getFilmFormatsSuccess(state, sources) {
        state.film_formats = { items: sources.data };
    },
    getFilmFormatsFailure(state, error) {
        state.film_formats = { error };
    },

    getStreamChannelsRequest(state) {
        state.stream_channels = { loading: true };
    },
    getStreamChannelsSuccess(state, sources) {
        state.stream_channels = { items: sources.data };
    },
    getStreamChannelsFailure(state, error) {
        state.stream_channels = { error };
    },

    createRequest(state) {
    },
    createSuccess(state, vod) {

    },
    createFailure(state, error) {
        console.log(error)
    },

    updateRequest(state) {
    },
    updateSuccess(state, vod) {

    },
    updateFailure(state, error) {
        console.log(error)
        state.one = { error };
    },

    deleteRequest(state, id) {
        // add 'deleting:true' property to user being deleted
        state.all.items = state.all.items.map(vod =>
            vod.id === id
                ? { ...vod, deleting: true }
                : vod
        )
    },
    deleteSuccess(state, id) {
        // remove deleted user from state
        state.all.items = state.all.items.filter(vod => vod.id !== id)
    },
    deleteFailure(state, { id, error }) {
        // remove 'deleting:true' property and add 'deleteError:[error]' property to user
        state.all.items = state.items.map(vod => {
            if (vod.id === id) {
                // make copy of user without 'deleting:true' property
                const { deleting, ...vodCopy } = vod;
                // return copy of user with 'deleteError:[error]' property
                return { ...vodCopy, deleteError: error };
            }

            return vod;
        })
    }

};

export const vods = {
    namespaced: true,
    state,
    actions,
    mutations,
    getters
};