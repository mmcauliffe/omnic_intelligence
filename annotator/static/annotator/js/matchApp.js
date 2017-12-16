var myServices = angular.module('switchServices', ['ngResource']);

myServices.factory('Switch', ['$resource', function($resource) {
    return $resource('/annotator/crud/switch/', {'pk': '@pk'}, {
    });
}]);

var switch_app = angular.module('SwitchApp', [/* other dependencies */, 'ngCookies']).run(
    function($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        // Add the following two lines
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

switch_app
    .controller('SwitchController', ['$scope', 'Switch', function($scope, Switch) {
        $scope.switches = Switch.query();
}]);