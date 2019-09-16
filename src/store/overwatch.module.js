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
    heroRevivingAbilities: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).reviving_abilities
    },
    heroDenyingAbilities: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).denying_abilities
    },
    heroDeniableAbilities: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).deniable_abilities
    },
    heroNPCs: (state, getters) => (hero_id) => {
        return getters.hero(hero_id).npcs
    },
    availableNPCs: (state, getters) => (hero_id_list) => {
        let hero, i, npcs=[], j;
        console.log('NPCS', state.npcs.items)
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
        console.log('GET NPCS', npcs)
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