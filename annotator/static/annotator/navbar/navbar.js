angular.module('navbar', [
    'oi.auth',
    'oi.users'
])
    .controller('NavCtrl', function ($scope, $rootScope, $http, djangoAuth, Users) {
        $rootScope.authenticated = false;
        $scope.authenticated = false;
        $scope.static = static;

        djangoAuth.authenticationStatus(true).then(function () {
            $scope.authenticated = true;

            Users.current_user().then(function (res) {
                console.log(res)
                $scope.user = res.data;
            });
        }).catch(function(res){
                console.log(res)
            $scope.authenticated = false;
        });


        // Wait and respond to the logout event.
        $scope.$on('djangoAuth.logged_out', function () {
            $scope.authenticated = false;
            delete $scope.user;

        });
        // Wait and respond to the log in event.
        $scope.$on('djangoAuth.logged_in', function (data) {
            $scope.authenticated = true;
            Users.current_user().then(function (res) {
                $scope.user = res.data;
            });
        });
    }).directive('navbar', function () {

    return {
        restrict: 'E',
        replace: true,
        templateUrl: static('annotator/navbar/navbar.html'),
        scope: {},
        controller: 'NavCtrl'
    }
});