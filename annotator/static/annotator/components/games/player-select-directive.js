angular.module('annotator.game.player-select', [])
    .directive('playerSelectBox', function ($filter) {
        return {
            restrict: 'E',
            replace: true,
            scope: {
                optionList: '=',
                allOptions: '=',
                index: '='
            },
            templateUrl: 'playerSelectTemplate.html',
            link: function (scope) {
                scope.onChange = function () {
                    for (var i = 0; i < scope.optionList.length; i++) {
                        scope.optionList[i].Show = true;
                    }
                    scope.person.Show = false;
                };

                scope.getValues = function (val) {
                    if (scope.index > 0) {
                        var j = scope.index;
                        for (var l = j; l > 0; l = l - 1) {
                            var previousVal = $filter('filter')(scope.allOptions[j - 1].optionList, {ID: val.ID}, true);
                            if (!previousVal[0].Show) {
                                return false;
                            } else {
                                j = j - 1;
                            }
                        }
                    }
                    return true;
                }
            }
        }
    });
