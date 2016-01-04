(function () {
    angular.module('univisApp')
        .controller('reportCtrl', ['$scope', 'dataservice', 'uniplot',
            function($scope, dataservice, uniplot) {

        // initialization
        // These uniquely define state
        $scope.model_id = undefined;
        $scope.unit_id = undefined;
        $scope.open_view = undefined;
        $scope.selected_feature = undefined;

        // These set from the server
        $scope.model_info = undefined;
        $scope.model_list = [];
        $scope.roc = {};
        $scope.pr = {};
        $scope.top_features = [];
        $scope.top_n_feature_names = [];
        $scope.top_units = [];
        $scope.top_unit_features = [];
        $scope.unit = {};
        $scope.similar_units = [];
        $scope.similar_unit_features = [];
        $scope.dist = {};
        $scope.model_picked = false;
        $scope.unit_picked = false;

        $scope.$watch('model_id', updateModel);
        $scope.$watch('model_info', updateModelInfo);
        $scope.$watch('unit_id', updateUnit);
        $scope.$watch('selected_feature', updateFeature);
        $scope.$watch('open_view', updateView);

        initModelList();

        $scope.open_view = 'models';

        function initModelList() {
            dataservice.getListModels().then(function (data) {
                $scope.model_list = data;
            });
        }

        // functions
        function updateModel(new_value) {
            if (new_value === undefined) return;
            console.log('model id= ' + $scope.model_id);
            dataservice.getTopFeatures($scope.model_id)
                .then( function (data) {
                    $scope.top_features = data;
                    $scope.top_n_feature_names.length = 0;
                    for (var i = 0; i < 3; ++i) {
                        $scope.top_n_feature_names.push(
                            $scope.top_features[i].feature);
                    }
                    return dataservice.getTopUnits($scope.model_id);
                })
                .then( function (data) {
                    $scope.top_units = data;
                    var top_unit_ids = $scope.top_units.map(function (unit) {
                        return unit.unit_id
                    });
                    return dataservice.getUnits($scope.model_id, top_unit_ids);
                })   
                .then( function (data) {
                    $scope.top_unit_features = data;
                    return dataservice.getModelInfo($scope.model_id)
                })
                .then( function (data) {
                    $scope.model_info = data;
                });
            $scope.model_picked = true;
        }

        function updateModelInfo(new_value) {
            if (new_value === undefined) return;
            uniplot.line(
                $scope.roc,
                $scope.model_info.graphs.roc.fpr,
                $scope.model_info.graphs.roc.tpr,
                'ROC',
                'FPR',
                'TPR');
            uniplot.line(
                $scope.pr,
                $scope.model_info.graphs.pr.recall,
                $scope.model_info.graphs.pr.precision,
                'Precision/Recall',
                'recall',
                'precision');
        }

        function updateUnit(new_value) {
            if (new_value === undefined) return;
            console.log('unit id= ' + $scope.unit_id);
            var feature_list = $scope.top_n_feature_names.join(',');
            dataservice.getUnit(
                    $scope.model_id, 
                    $scope.unit_id, 
                    $scope.top_n_feature_names)
                .then(function (data) {
                    $scope.unit = data;
                    if ($scope.selected_feature === undefined) {
                        $scope.selected_feature = $scope.top_n_feature_names[0];
                    } else {
                        updateFeature($scope.selected_feature);    
                    }
                });
            //TODO for multiple features
            dataservice.getSimilar($scope.model_id, $scope.unit_id)
                .then( function (data) {
                    $scope.similar_units = data;
                    var similar_unit_ids = $scope.similar_units.map(
                        function (unit) {return unit.unit_id;});
                    return dataservice.getUnits(
                        $scope.model_id, 
                        similar_unit_ids);
                })
                .then( function (data) {
                    $scope.similar_unit_features = data;
                });
            $scope.unit_picked = true;
        }

        function updateFeature(new_value) {
            if (new_value === undefined) return;
            var feature = new_value;
            console.log('feature = ' + feature);
            dataservice.getDistribution($scope.model_id, feature)
                .then( function (data) {
                    $scope.dist = data;
                    uniplot.distributions(
                        $scope.dist, 
                        $scope.dist.positive, 
                        $scope.dist.negative,
                        $scope.unit[feature],
                        feature);
                });
        }

        function updateView(new_value) {
            if (new_value === undefined) return;
            var place = new_value;
            console.log('going to: ' + place);
            $scope.view_models_open = false;
            $scope.view_model_performance_open = false;
            $scope.view_unit_performance_open = false;
            if (place === 'model_performance') {
                $scope.view_model_performance_open = true;
                return;
            }
            if (place === 'unit_performance') {
                $scope.view_unit_performance_open = true;
                return;
            }
            $scope.view_models_open = true;
        }

        $scope.pickModel = function ($index) {
            $scope.model_id = $index;
            $scope.open_view='model_performance';
        }

        $scope.pickUnit = function ($index, pool) {
            if (pool === 'similar') {
                $scope.unit_id = $scope.similar_units[$index].unit_id;
            } else {
                $scope.unit_id = $scope.top_units[$index].unit_id;
            }
            $scope.open_view = 'unit_performance';
        }


        $scope.pickFeature = function (feature) {
            $scope.selected_feature = feature;
        }


        $scope.goTo = function (place, $event) {
            if (typeof $event !== 'undefined') {
                $event.preventDefault();
                $event.stopPropagation();
                if (place === 'model_performance' && !$scope.model_picked) {
                    return;
                }
                if (place === 'unit_performance' && !$scope.unit_picked) {
                    return;
                }
            }
            $scope.open_view = place
        }

        //TODO just here for development. Remove in production
        $scope.resetServer = function () {
            dataservice.resetServer();
            initModelList();
        }


    }]);
})();
