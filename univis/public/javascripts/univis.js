var app = angular.module('univisApp', ['ui.bootstrap']);
app.controller('univisCtrl', function($scope, $http) {

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
            console.log('top_n_feature_names');
            console.log($scope.top_n_feature_names);
        }, function (response) {});
    $scope.model_performance_open = true;
}

$http.get('/list_models').then( function (response) {
    $scope.model_list = angular.fromJson(response.data).data;
    $scope.models_open = true;
}, function (response) {});

$scope.pickUnit = function ($index, pool) {
    if (pool === 'similar') {
        $scope.unit_id = $scope.similar_units[$index].unit_id;
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
    $scope.unit_performance_open=true;
}

$scope.pickSimilarFeature = function (feature) {
    $scope.similar_feature = feature;
    console.log('similar feature = ' + $scope.similar_feature);
    $http.get('/similar', {'params': {
        'model_id': $scope.model_id,
        'unit_id': $scope.unit_id,
        'features': feature}})
        .then( function (response) {
            $scope.similar_units = angular.fromJson(
                response.data).data;
        }, function (response) {});
}

$scope.models_open = false;
$scope.model_performance_open = false;
$scope.unit_performance_open = false;

$scope.model_list = [];
$scope.top_features = [];
$scope.top_n_feature_names = [];
$scope.top_units = [];
$scope.unit = {};
$scope.similar_feature = 'Choose a Feature'
$scope.similar_units = [];
});
