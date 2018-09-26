angular.module("logout", ['annotator.auth']).controller("LogoutCtrl", [
    '$scope', '$rootScope', '$state', 'AuthService', 'CookieService', '$timeout', function ($scope, $rootScope, $state, AuthService, CookieService) {
        $scope.state = $state;

        CookieService.remove('oi_token');
        CookieService.remove('oi_sessionid');
        delete $rootScope.session;
        $rootScope.$broadcast('logged_out');
        return $state.go("home");

    }
]);