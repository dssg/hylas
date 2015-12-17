(function () {
    angular.module('univisApp')
    .controller('uploadCtrl', ['$scope', 'dataservice',
        function($scope, dataservice) {

        $scope.submit = function() {dataservice.putCSV($scope.csvFile)}

    }]);
})();
