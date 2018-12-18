import Vue from 'vue';
import Vuex from 'vuex';

import { alert } from './alert.module';
import { account } from './account.module';
import { users } from './users.module';
import { events } from './events.module';
import { matches } from './matches.module';
import { games } from './games.module';
import { vods } from './vod.module';
import { overwatch } from './overwatch.module';
import { rounds } from './rounds.module'

Vue.use(Vuex);

export const store = new Vuex.Store({
    modules: {
        alert,
        account,
        users,
        events,
        matches,
        games,
        rounds,
        vods,
        overwatch
    }
});