function updateTimes() {
    var cur_time = player.getCurrentTime();
    if (cur_time > end_time) {
        cur_time = end_time;
    }
    var time = Math.round(cur_time - begin_time);
    if (time < 0) {
        time = 0;
    }
    $("input[name='time_point']").val(time);
}

function refreshPlayers() {
    left_players = [];
    right_players = [];
    $("#left-team select[name='player']").each(function () {
        left_players.push($(this).val());
    });
    $("#right-team select[name='player']").each(function () {
        right_players.push($(this).val());
    });
    all_players = left_players.concat(right_players);
}

function updateSelects() {
    $("#switch-form select[name='player'] option").each(function () {
        if (jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $("#kill-form select[name='killing_player'] option").each(function () {
        if ($(this).val() && jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $("#kill-form select[name='killed_player'] option").each(function () {
        if ($(this).val() && jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $("#killnpc-form select[name='killing_player'] option").each(function () {
        if (jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $("#death-form select[name='player'] option").each(function () {
        if (jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $("#revive-form select[name='reviving_player'] option").each(function () {
        if (jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $("#revive-form select[name='revived_player'] option").each(function () {
        if (jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $("#ultgain-form select[name='player'] option").each(function () {
        if (jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $("#ultuse-form select[name='player'] option").each(function () {
        if (jQuery.inArray($(this).val(), all_players) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });
}

function updateRevivees() {
    var reviver = $("#revive-form select[name='reviving_player']").val();
    $("#kill-form select[name='killed_player']").val($("#kill-form select[name='killed_player'] option:first").val());
    if (reviver) {
        if (jQuery.inArray(reviver, left_players) > 0) {
            var possible_revivees = left_players;
        }
        else {
            var possible_revivees = right_players;
        }
        $("#revive-form select[name='revived_player'] option").each(function () {
            if (jQuery.inArray($(this).val(), possible_revivees) < 0) {
                $(this).hide();
            }
            else {
                $(this).show();
            }
        });

    }
}

function updateKilledPlayers() {
    var killer = $("#kill-form select[name='killing_player']").val();
    $("#kill-form select[name='killed_player']").val($("#kill-form select[name='killed_player'] option:first").val());
    if (killer) {
        if (jQuery.inArray(killer, left_players) > 0) {
            var possible_killees = right_players;
        }
        else {
            var possible_killees = left_players;
        }
        $("#kill-form select[name='killed_player'] option").each(function () {
            if ($(this).val() && jQuery.inArray($(this).val(), possible_killees) < 0) {
                $(this).hide();
            }
            else {
                $(this).show();
            }
        });

    }

}

function updateAbilities(abilities) {

    $("#kill-form select[name='ability'] option").each(function () {
        if ($(this).val() && jQuery.inArray($(this).val(), abilities) < 0) {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });
}