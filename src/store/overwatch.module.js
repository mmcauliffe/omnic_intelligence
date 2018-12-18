import {overwatchService} from '../api';

const state = {
    heroes: {},
    hero_damaging_abilities: {},
    hero_reviving_abilities: {},
    maps: {},
    map_types: {},
    npcs: {},
    team_colors: {},
    sides: {},
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
                events => commit('getMapsSuccess', events),
                error => commit('getMapsFailure', error)
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
};


const getters = {
    hero: (state) => (hero_id) => {
        console.log(state.heroes)
        let i, hero;
        for (i = 0; i < state.heroes.items.length; i++) {
            hero = state.heroes.items[i];
            if (hero.id == hero_id) {
                return hero
            }
        }

    },
    heroDamagingAbilities: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).damaging_abilities
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


};

export const overwatch = {
    namespaced: true,
    state,
    actions,
    mutations,
    getters
};