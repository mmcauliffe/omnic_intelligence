angular.module('navbar', [
    'annotator.auth'
])
    .controller('NavCtrl', function ($scope, $rootScope, CookieService, $http, AuthService) {
        $rootScope.authenticated = false;
        $scope.authenticated = false;
        $scope.static = static;

        $scope.checkAuth = function (){
            $scope.token = CookieService.get('oi_token');
            console.log($http.defaults.headers)
            if ($scope.token != undefined){
                console.log($scope.token);
                $http.defaults.headers.common["Authorization"] = "Token " + $scope.token;
            }
            AuthService.checkAuth().then(function (user) {
                console.log(user)
                if (user.data.id === null) {
                    $rootScope.user = undefined;
                    $rootScope.authenticated = false;
                    $scope.authenticated = false;
                }
                else {
                    $rootScope.user = user.data;

                    $rootScope.authenticated = true;
                    $scope.authenticated = true;
                    $rootScope.session = AuthService.createSessionFor(user.data);
                    $rootScope.$broadcast("authenticated", user);
                }

            }).catch(function(res){
                $rootScope.user = undefined;
                $rootScope.authenticated = false;
                $scope.authenticated = false;
            });

        };
        $scope.checkAuth();
        $scope.$on('logged_in', $scope.checkAuth);
        $scope.$on('authenticated', function (e, res) {
            $scope.user = $rootScope.user;
            $rootScope.authenticated = true;
            $scope.authenticated = true;
        });
        $scope.$on('logged_out', function (e, res){
           delete $scope.user;
           delete $scope.token;
            delete $http.defaults.headers.common["Authorization"];
            console.log($http.defaults.headers)
            $scope.authenticated = false;
            $rootScope.authenticated = false;
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