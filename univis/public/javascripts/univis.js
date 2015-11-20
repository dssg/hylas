var app = angular.module('univisApp', ['ui.bootstrap', 'nvd3']);
app.controller('univisCtrl', function($scope, $http) {

    var updateModelInfo = function() {
        Uniplot.line(
            $scope.roc,
            $scope.model_info.graphs.roc.fpr,
            $scope.model_info.graphs.roc.tpr,
            'ROC',
            'FPR',
            'TPR');
    }

    var updateSelectedFeature = function () {
        feature = $scope.selected_feature;

        $http.get('/similar', {'params': {
            'model_id': $scope.model_id,
            'unit_id': $scope.unit_id,
            'features': feature}})
            .then( function (response) {
                $scope.similar_units = angular.fromJson(
                    response.data).data;
            }, function (response) {});

        $http.get('/distribution', {'params': {
            'model_id': $scope.model_id,
            'feature': feature}})
            .then( function (response) {
                var dist = angular.fromJson(response.data).data;
                Uniplot.distributions(
                    $scope.dist, 
                    dist.positive, 
                    dist.negative,
                    $scope.unit[feature],
                    feature);
            }, function (response) {});
    }

    $scope.pickModel = function ($index) {
        $scope.model_id = $index;
        console.log('model id= ' + $scope.model_id);
        $http.get('/top_units', {'params': 
            {'model_id' : $scope.model_id}})
            .then( function (response) {
                $scope.top_units = angular.fromJson(
                    response.data).data;
            }, function (response) {});
        $http.get('/top_features', {'params': 
            {'model_id' : $scope.model_id}})
            .then( function (response) {
                $scope.top_features = angular.fromJson(
                    response.data).data;
                $scope.top_n_feature_names.length = 0;
                for (var i = 0; i < 3; ++i) {
                    $scope.top_n_feature_names.push($scope.top_features[i].feature);
                }
                $scope.selected_feature = $scope.top_n_feature_names[0];
                console.log('top_n_feature_names');
                console.log($scope.top_n_feature_names);
            }, function (response) {});
        $http.get('/model_info', {'params':
            {'model_id': $scope.model_id}})
            .then( function (response) {
                $scope.model_info = angular.fromJson(
                    response.data).data;
                updateModelInfo();
            }, function (response) {});
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
        $http.get('/unit', {'params': {
            'model_id': $scope.model_id,
            'unit_id': $scope.unit_id,
            'features': feature_list}})
            .then( function (response) {
                $scope.unit = angular.fromJson(
                    response.data).data;
            }, function (response) {});
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

    $scope.goTo = function (place) {
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

    $scope.model_list = [];
    $scope.model_info = {};
    $scope.roc = {};
    $scope.top_features = [];
    $scope.top_n_feature_names = [];
    $scope.top_units = [];
    $scope.unit = {};
    $scope.selected_feature = 'Choose a Feature';
    $scope.similar_units = [];
    $scope.dist = {};
    $scope.model_picked = false;
    $scope.unit_picked = false;

    $http.get('/list_models').then( function (response) {
        $scope.model_list = angular.fromJson(response.data).data;
    }, function (response) {});

    $scope.open_view = '';
    $scope.goTo('models');
});
