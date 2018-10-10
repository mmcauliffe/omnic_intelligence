angular.module('roundStatus', [
    'annotator.roundstatus'
]).directive('dlEnterKey', function () {
    return function (scope, element, attrs) {

        element.bind("keydown keypress", function (event) {
            var keyCode = event.which || event.keyCode;

            // If enter key is pressed
            if (keyCode === 13) {
                scope.$apply(function () {
                    // Evaluate the expression
                    scope.$eval(attrs.dlEnterKey);
                });

                event.preventDefault();
            }
        });
    };
})
    .controller('RoundStatusCtrl', function ($scope, RoundStatus, Rounds, __env, $state, $stateParams, djangoAuth, Users) {
        $scope.paginateParams = {
                page: 1,
                limit: 5,
                ordering:'-game__match__event__name',
            search: ''
        };

        $scope.export_url = __env.exportUrl;

        $scope.downloadRound = function(round){
            Rounds.downloadOne(round.id).then(function(res){
                if (res.data.success){
                    round.video_status = 'Local file available';
                }
                else{
                    round.video_status = 'Error in processing';
                }
            });
        };

        $scope.exportRoundVideo = function(round){
            Rounds.exportOne(round.id).then(function(res){
                if (res.data.success){
                    round.video_status = 'Successfully exported';
                }
                else{
                    round.video_status = 'Error in processing';
                }
            });
        };


        function success(results) {
            console.log(results)
            $scope.results = results;
        }

        $scope.paginatorCallback = function () {
            $scope.paginateParams.offset = ($scope.paginateParams.page - 1) * $scope.paginateParams.limit;
            $scope.paginateParams.corpus_id = $stateParams.corpus_id;
            $scope.paginateParams.id = $stateParams.query_id;
            $scope.promise = RoundStatus.results.get($scope.paginateParams, success).$promise;

        };



        $scope.refreshOrdering = function (new_ordering) {
            if (new_ordering == $scope.paginateParams.ordering) {
                new_ordering = '-' + new_ordering
            }
            $scope.paginateParams.ordering = new_ordering;
            $scope.paginatorCallback();
        };

        $scope.refreshSearch = function () {
            $scope.paginatorCallback()
        }


        $scope.paginatorCallback();
    });