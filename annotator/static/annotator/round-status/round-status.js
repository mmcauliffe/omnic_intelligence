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
    .controller('RoundStatusCtrl', function ($scope, RoundStatus, Rounds, __env, $state, $stateParams) {
        $scope.ordering = '-game__match__event__name';
        $scope.currentPage = 1;
        $scope.resultsPerPage = 100;
        $scope.offset = 0;
        $scope.numPages = 0;
        $scope.export_url = __env.exportUrl;
        $scope.update = function () {
            RoundStatus.all($scope.offset, $scope.ordering, $scope.searchText).then(function (res) {
                console.log(res.data);
                $scope.count = res.data.count;
                $scope.numPages = Math.ceil($scope.count / $scope.resultsPerPage);
                $scope.rounds = res.data.results;
                $scope.updatePagination();
            });

        };

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


        $scope.updatePagination = function () {
            $scope.pages = [];
            $scope.pages.push(1);
            for (i = 2; i < $scope.numPages; i++) {
                if (i === 2 && $scope.currentPage - i >= 3) {
                    console.log('HELLO');
                    $scope.pages.push('...');
                }
                if (Math.abs($scope.currentPage - i) < 3) {
                    $scope.pages.push(i);
                }
                if (i === $scope.numPages - 1 && $scope.numPages - 1 - $scope.currentPage >= 3) {
                    $scope.pages.push('...');
                }
            }
            $scope.pages.push($scope.numPages);
            console.log($scope.pages);
        };

        $scope.next = function () {
            if ($scope.currentPage != $scope.numPages) {
                $scope.refreshPagination($scope.currentPage + 1);
            }
        };
        $scope.first = function () {
            if ($scope.currentPage != 1) {
            $scope.refreshPagination(1);
            }
        };
        $scope.last = function () {
            if ($scope.currentPage != $scope.numPages) {
            $scope.refreshPagination($scope.numPages);
            }
        };

        $scope.previous = function () {
            if ($scope.currentPage != 1) {
                $scope.refreshPagination($scope.currentPage - 1);
            }
        };

        $scope.refreshPagination = function (newPage) {
            $scope.currentPage = newPage;
            $scope.offset = ($scope.currentPage - 1) * $scope.resultsPerPage;
            $scope.update()
        };

        $scope.update();

        $scope.refreshOrdering = function (new_ordering) {
            if (new_ordering == $scope.ordering) {
                new_ordering = '-' + new_ordering
            }
            $scope.ordering = new_ordering;
            $scope.update();
        };

        $scope.refreshSearch = function () {
            $scope.update()
        }
    });