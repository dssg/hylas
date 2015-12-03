(function () {
    angular.module('univisApp')
        .factory('dataservice', ['$http', dataservice]);

    function dataservice($http) {

        var service = {
            getSimilar: getSimilar,
            getUnit: getUnit,
            getUnits: getUnits,
            getDistribution: getDistribution,
            getTopUnits: getTopUnits,
            getTopFeatures: getTopFeatures,
            getModelInfo: getModelInfo,
            getListModels: getListModels
        };

        return service;

        function getRest(resource, params) {
            console.log(resource, params);
            return $http.get(resource, {params: params})
                .then(function(response) {
                    var data = angular.fromJson(response.data).data;
                    console.log(data);
                    return data;
                })
                .catch(function(response) {
                    //TODO don't just eat the error
                    return 'ERROR'
                });
        }

        function getSimilar(modelId, unitId) {
            return getRest('/similar', {
                model_id: modelId,
                unit_id: unitId
            });
        }

        function getUnits(modelId, unitIds) {
            return getRest('/units', {
                model_id: modelId,
                unit_id: unitIds.join(',')
            });
        }

        function getUnit(modelId, unitId, features) {
            return getRest('/unit', {
                model_id: modelId,
                unitId: unitId,
                features: features.join(',')
            });
        }

        function getDistribution(modelId, feature) {
            return getRest('/distribution', {
                model_id: modelId,
                feature: feature
            });
        }

        function getTopUnits(modelId) {
            return getRest('/top_units', {
                model_id: modelId
            });
        }

        function getTopFeatures(modelId) {
            return getRest('/top_features', {
                model_id: modelId
            });
        }

        function getModelInfo(modelId) {
            return getRest('/model_info', {
                model_id: modelId
            });
        } 

        function getListModels() {
            return getRest('/list_models', {});
        }
    }
})();                

