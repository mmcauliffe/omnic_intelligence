
import Vue from 'vue'
import moment from 'moment'

Vue.filter('secondsToMoment', function (seconds) {
        var m = moment({hour: 0, minute: 0});
        m.seconds(Math.floor(seconds));
        m.milliseconds(Math.round(seconds % 1 * 1000));
        return m;
    }
);

Vue.filter('playerTemplate', function (playerNum){
    return 'Player '+ playerNum
});