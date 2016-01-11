(function () {
    angular.module('univisApp')
        .factory('dataservice', ['$http', 'Upload', dataservice]);

    function dataservice($http, Upload) {

        var service = {
            getSimilar: getSimilar,
            getUnit: getUnit,
            getUnits: getUnits,
            getDistribution: getDistribution,
            getTopUnits: getTopUnits,
            getTopFeatures: getTopFeatures,
            getModelInfo: getModelInfo,
            getListModels: getListModels,
            putCSV: putCSV,
            putPkl: putPkl,
            resetServer: resetServer
        };

        return service;

        function getRest(resource, params) {
            console.log('fetching from host:', resource, params);
            for (var key in params) {
                if (params.hasOwnProperty(key)) {
                    // todo return failed request if value is undefined
                }
            }
            return $http.get(resource, {params: params})
                .then(function(response) {
                    var data = angular.fromJson(response.data).data;
                    console.log('got for ' + resource + ':', data);
                    return data;
                })
                .catch(function(response) {
                    console.log('REQUEST FAILED', response);
                    return response;
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
                unit_ids: unitIds.join(',')
            });
        }

        function getUnit(modelId, unitId, features) {
            return getRest('/unit', {
                model_id: modelId,
                unit_id: unitId,
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

        function putCSV(file, otherInfo) {
            return Upload.upload({
                url: 'upload_csv',
                data: {file: file, otherInfo: otherInfo}
            });
        }

        function putPkl(file, otherInfo) {
            return Upload.upload({
                url: 'upload_pkl',
                data: {file: file, otherInfo: otherInfo}
            });
        }

        // TODO just here for development. Remove in production
        function resetServer() {
            return $http.post('/reset')
        }
    }
})();                

