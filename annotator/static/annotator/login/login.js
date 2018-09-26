angular.module("login", ['annotator.auth']).controller("LoginCtrl", [
    '$scope', '$rootScope', '$state', 'Config', 'AuthService', 'CookieService', '$http', '$timeout', function($scope, $rootScope, $state, Config, AuthService, CookieService, $http, $timeout) {
      $scope.state = $state;
      $scope.Config = Config;
      $scope.user = {
        username: "",
        password: ""
      };

      $scope.login = function() {
        AuthService.login($scope.user).then(function(result) {
            console.log(result);
          CookieService.put('oi_token', result.data.token);
          $rootScope.$broadcast('logged_in');
          $state.go('home');
        }).catch(function(errors) {
          $scope.errors = errors.data;
          delete $rootScope.user;
          delete $rootScope.session;
          return $rootScope.$broadcast("loginFailed");
        })
      };

    }
  ]);