
angular.module('univisApp')
    .factory('dataservice', dataservice);

    function dataservice($http) {

        var service = {
            getSimilar: getSimilar,
            getUnits: getUnits,
            getDistribution: getDistribution,
            getTopUnits: getTopUnits,
            getTopFeatures: getTopFeatures,
            getModelInfo: getModelInfo
        };

        return service;

        function getRest(resource, params) {
            $http.get(resource, {params: params})
                .then(function(response) {
                    return angular.fromJson(response.data).data;
                })
                .catch(function(response) {
                    //TODO don't just eat the error
                    return 'ERROR'
                });
        }

        function getSimilar(modelId, unitId) {
            //TODO here
        }
