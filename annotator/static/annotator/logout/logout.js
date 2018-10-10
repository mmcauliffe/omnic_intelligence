angular.module("logout", ['oi.auth']).controller("LogoutCtrl", [
    '$scope', '$rootScope', '$state',  'djangoAuth', function ($scope, $rootScope, $state, djangoAuth) {
        $scope.state = $state;

    djangoAuth.logout();
    return $state.go("home");
    }
]);
