(function () {
    angular.module('univisApp')
        .controller('univisCtrl', ['$scope', 'dataservice', 'uniplot',
            function($scope, dataservice, uniplot) {

        var updateModelInfo = function() {
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

        var updateSelectedFeature = function () {
            feature = $scope.selected_feature;

            dataservice.getSimilar($scope.model_id, $scope.unit_id)
                .then( function (data) {
                    $scope.similar_units = data;
                    var similar_unit_ids = $scope.similar_units.map(
                        function (unit) {return unit.unit_id;});
                    dataservice.getUnits($scope.model_id, similar_unit_ids)
                        .then( function (data) {
                            $scope.similar_unit_features = data;
                        });
                });
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

        $scope.pickModel = function ($index) {
            $scope.model_id = $index;
            console.log('model id= ' + $scope.model_id);
            dataservice.getTopUnits($scope.model_id)
                .then( function (data) {
                    $scope.top_units = data;
                    var top_unit_ids = $scope.top_units.map(function (unit) {
                        return unit.unit_id
                    });
                    dataservice.getUnits($scope.model_id, top_unit_ids)
                        .then( function (data) {
                            $scope.top_unit_features = data;
                        });
                });   
            dataservice.getTopFeatures($scope.model_id)
                .then( function (data) {
                    $scope.top_features = data;
                    $scope.top_n_feature_names.length = 0;
                    for (var i = 0; i < 3; ++i) {
                        $scope.top_n_feature_names.push($scope.top_features[i].feature);
                    }
                    $scope.selected_feature = $scope.top_n_feature_names[0];
                    console.log('top_n_feature_names');
                    console.log($scope.top_n_feature_names);
                });
            dataservice.getModelInfo($scope.model_id)
                .then( function (data) {
                    $scope.model_info = data;
                    updateModelInfo();
                });
            $scope.model_picked = true;
            $scope.goTo('model_performance');
        }


        $scope.pickUnit = function ($index, pool) {
            if (pool === 'similar') {
                $scope.unit_id = $scope.similar_units[$index].unit_id;
                $scope.pickFeature($scope.selected_feature);
            } else {
                $scope.unit_id = $scope.top_units[$index].unit_id;
            }
            console.log('unit id= ' + $scope.unit_id);
            var feature_list = $scope.top_n_feature_names.join(',');
            dataservice.getUnit(
                    $scope.model_id, 
                    $scope.unit_id, 
                    $scope.top_n_feature_names)
                .then(function (data) {
                    $scope.unit = data;
                });
            //TODO for multiple features
            updateSelectedFeature();    
            $scope.unit_picked = true;
            $scope.goTo('unit_performance');
        }


        $scope.pickFeature = function (feature) {
            $scope.selected_feature = feature;
            console.log('similar feature = ' + $scope.selected_feature);
            updateSelectedFeature();    
        }

        $scope.goTo = function (place, $event) {
            if (typeof $event !== 'undefined') {
                $event.preventDefault();
                $event.stopPropagation();
            }
            console.log('going to: ' + place);
            $scope.view_models_open = false;
            $scope.view_model_performance_open = false;
            $scope.view_unit_performance_open = false;
            if (place === 'model_performance' && $scope.model_picked) {
                $scope.open_view = 'model_performance';
                $scope.view_model_performance_open = true;
                return;
            }
            if (place === 'unit_performance' && $scope.unit_picked) {
                $scope.open_view = 'unit_performance';
                $scope.view_unit_performance_open = true;
                return;
            }
            $scope.open_view = 'models'
            $scope.view_models_open = true;
        }

        $scope.views = function () {
            console.log('models: ' + $scope.view_models_open)
            console.log('model_performance: ' + $scope.view_model_performance_open)
            console.log('unit_performance: ' + $scope.view_unit_performance_open)
        }

        $scope.model_list = [];
        $scope.model_info = {};
        $scope.roc = {};
        $scope.pr = {};
        $scope.top_features = [];
        $scope.top_n_feature_names = [];
        $scope.top_units = [];
        $scope.top_unit_features = [];
        $scope.unit = {};
        $scope.selected_feature = 'Choose a Feature';
        $scope.similar_units = [];
        $scope.similar_unit_features = [];
        $scope.dist = {};
        $scope.model_picked = false;
        $scope.unit_picked = false;

        dataservice.getListModels().then(function (data) {
            $scope.model_list = data;
        });

        $scope.open_view = '';
        $scope.goTo('models');
    }]);
})();
