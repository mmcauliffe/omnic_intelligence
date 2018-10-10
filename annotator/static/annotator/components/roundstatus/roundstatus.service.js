angular.module('annotator.roundstatus')

    .factory('RoundStatus',  ['$resource', function ($resource) {
  'use strict';
        var base_url = __env.apiUrl + 'round_status/';

  return {
    results: $resource(base_url)
  };
}]);