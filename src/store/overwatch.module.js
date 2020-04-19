import {overwatchService} from '../api';

const state = {
    heroes: {},
    hero_damaging_abilities: {},
    hero_reviving_abilities: {},
    maps: {},
    map_types: {},
    npcs: {},
    status_effect_choices: {},
    team_colors: {},
    sides: {},
    submaps: {},
    pause_types: {},
    replay_types: {},
    smaller_window_types: {},
};

const actions = {
    getHeroes({commit}) {
        commit('getHeroesRequest');

        overwatchService.getHeroes()
            .then(
                events => commit('getHeroesSuccess', events),
                error => commit('getHeroesFailure', error)
            );
    },
    getHeroDamagingAbilities({commit}, id) {

        overwatchService.getHeroDamagingAbilities(id)
            .then(
                abilities => commit('getHeroDamagingAbilitiesSuccess', {id: id, abilities: abilities}),
                error => commit('getHeroDamagingAbilitiesFailure', error)
            );
    },
    getHeroRevivingAbilities({commit}, id) {

        overwatchService.getHeroRevivingAbilities(id)
            .then(
                abilities => commit('getHeroRevivingAbilitiesSuccess', {id: id, abilities: abilities}),
                error => commit('getHeroRevivingAbilitiesFailure', error)
            );
    },
    getMaps({commit}) {
        commit('getMapsRequest');

        overwatchService.getMaps()
            .then(
                maps => commit('getMapsSuccess', maps),
                error => commit('getMapsFailure', error)
            );
    },
    getStatusEffectChoices({commit}) {
        commit('getStatusEffectChoicesRequest');

        overwatchService.getStatusEffectChoices()
            .then(
                events => commit('getStatusEffectChoicesSuccess', events),
                error => commit('getStatusEffectChoicesFailure', error)
            );
    },
    getMapTypes({commit}) {
        commit('getMapTypesRequest');

        overwatchService.getMapTypes()
            .then(
                events => commit('getMapTypesSuccess', events),
                error => commit('getMapTypesFailure', error)
            );
    },
    getNPCs({commit}) {
        commit('getNPCsRequest');

        overwatchService.getNPCs()
            .then(
                events => commit('getNPCsSuccess', events),
                error => commit('getNPCsFailure', error)
            );
    },
    getTeamColors({commit}) {
        commit('getTeamColorsRequest');

        overwatchService.getTeamColors()
            .then(
                events => commit('getTeamColorsSuccess', events),
                error => commit('getTeamColorsFailure', error)
            );
    },
    getSides({commit}) {
        commit('getSidesRequest');

        overwatchService.getSides()
            .then(
                events => commit('getSidesSuccess', events),
                error => commit('getSidesFailure', error)
            );
    },
    getSubmaps({commit}) {
        commit('getSubmapsRequest');

        overwatchService.getSubmaps()
            .then(
                events => commit('getSubmapsSuccess', events),
                error => commit('getSubmapsFailure', error)
            );
    },
    getPauseTypes({commit}) {
        commit('getPauseTypesRequest');

        overwatchService.getPauseTypes()
            .then(
                types => commit('getPauseTypesSuccess', types),
                error => commit('getPauseTypesFailure', error)
            );
    },
    getReplayTypes({commit}) {
        commit('getReplayTypesRequest');

        overwatchService.getReplayTypes()
            .then(
                types => commit('getReplayTypesSuccess', types),
                error => commit('getReplayTypesFailure', error)
            );
    },
    getSmallerWindowTypes({commit}) {
        commit('getSmallerWindowTypesRequest');

        overwatchService.getSmallerWindowTypes()
            .then(
                types => commit('getSmallerWindowTypesSuccess', types),
                error => commit('getSmallerWindowTypesFailure', error)
            );
    },
};


const getters = {
    denying_heroes: (state) => {
        return state.heroes.items.filter(x => x.ability_denier).map(x=> x.name);
    },
    sides: (state) => {
        return state.sides.items.filter(x => x.id !== 'N');
    },
    npcs: (state) => {
        return state.npcs.items;
    },
    status_effect_choices: (state) => {
        return state.status_effect_choices.items;
    },
    hero: (state) => (hero_id) => {
        if (state.heroes.items === undefined){
            return {}
        }
        let i, hero;
        for (i = 0; i < state.heroes.items.length; i++) {
            hero = state.heroes.items[i];
            if (hero.id == hero_id) {
                return hero
            }
        }

    },
    heroDamagingAbilities: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).abilities.filter(x => {return x.type === 'D'})
    },
    heroRevivingAbilities: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).abilities.filter(x => {return x.type === 'R'})
    },
    heroDenyingAbilities: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).abilities.filter(x => {return x.type === 'E'})
    },
    heroDeniableAbilities: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).abilities.filter(x => x.deniable)
    },
    heroNPCs: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).npc_set
    },
    availableNPCs: (state, getters) => (hero_id_list) => {
        let hero, i, npcs=[], j;
        if (hero_id_list.length === 0){
            return state.npcs.items
        }
        for (i=0; i<state.npcs.items.length; i++){
            if (hero_id_list.indexOf(state.npcs.items[i].spawning_hero.id) >= 0){
                npcs.push(state.npcs.items[i])
            }

        }
        return npcs
    },
};

const mutations = {
    getHeroesRequest(state) {
        state.heroes = {loading: true};
    },
    getHeroesSuccess(state, sources) {
        state.heroes = {items: sources};
    },
    getHeroesFailure(state, error) {
        state.heroes = {error};
    },

    getHeroDamagingAbilitiesSuccess(state, abilities) {
        state.hero_damaging_abilities[abilities.id] = abilities.abilities;
    },
    getHeroDamagingAbilitiesFailure(state, error) {
        state.hero_damaging_abilities = {error};
    },

    getHeroRevivingAbilitiesSuccess(state, abilities) {
        state.hero_reviving_abilities[abilities.id] = abilities.abilities;
    },
    getHeroRevivingAbilitiesFailure(state, error) {
        state.hero_reviving_abilities = {error};
    },

    getMapsRequest(state) {
        state.maps = {loading: true};
    },
    getMapsSuccess(state, maps) {
        state.maps = {items: maps};
    },
    getMapsFailure(state, error) {
        state.maps = {error};
    },

    getStatusEffectChoicesRequest(state) {
        state.status_effect_choices = {loading: true};
    },
    getStatusEffectChoicesSuccess(state, status_effect_choices) {
        state.status_effect_choices = {items: status_effect_choices};
    },
    getStatusEffectChoicesFailure(state, error) {
        state.status_effect_choices = {error};
    },

    getMapTypesRequest(state) {
        state.map_types = {loading: true};
    },
    getMapTypesSuccess(state, map_types) {
        state.map_types = {items: map_types};
    },
    getMapTypesFailure(state, error) {
        state.map_types = {error};
    },

    getNPCsRequest(state) {
        state.npcs = {loading: true};
    },
    getNPCsSuccess(state, npcs) {
        state.npcs = {items: npcs};
    },
    getNPCsFailure(state, error) {
        state.npcs = {error};
    },

    getTeamColorsRequest(state) {
        state.team_colors = {loading: true};
    },
    getTeamColorsSuccess(state, team_colors) {
        state.team_colors = {items: team_colors};
    },
    getTeamColorsFailure(state, error) {
        state.team_colors = {error};
    },

    getSidesRequest(state) {
        state.sides = {loading: true};
    },
    getSidesSuccess(state, sides) {
        state.sides = {items: sides};
    },
    getSidesFailure(state, error) {
        state.sides = {error};
    },

    getSubmapsRequest(state) {
        state.submaps = {loading: true};
    },
    getSubmapsSuccess(state, submaps) {
        state.submaps = {items: submaps};
    },
    getSubmapsFailure(state, error) {
        state.submaps = {error};
    },

    getPauseTypesRequest(state) {
        state.pause_types = {loading: true};
    },
    getPauseTypesSuccess(state, types) {
        state.pause_types = {items: types};
    },
    getPauseTypesFailure(state, error) {
        state.pause_types = {error};
    },

    getReplayTypesRequest(state) {
        state.replay_types = {loading: true};
    },
    getReplayTypesSuccess(state, types) {
        state.replay_types = {items: types};
    },
    getReplayTypesFailure(state, error) {
        state.replay_types = {error};
    },

    getSmallerWindowTypesRequest(state) {
        state.smaller_window_types = {loading: true};
    },
    getSmallerWindowTypesSuccess(state, types) {
        state.smaller_window_types = {items: types};
    },
    getSmallerWindowTypesFailure(state, error) {
        state.smaller_window_types = {error};
    },


};

export const overwatch = {
    namespaced: true,
    state,
    actions,
    mutations,
    getters
};