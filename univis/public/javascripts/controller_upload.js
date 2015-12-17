(function () {
    angular.module('univisApp')
    .controller('uploadCtrl', ['$scope', 'dataservice',
        function($scope, dataservice) {

        $scope.uid_column = 'id';
        $scope.label_column = 'label';

        $scope.submit = function() {
            $scope.uploadStatus = "working..."
            var otherInfo = {unit_id_feature : $scope.uid_column,
                             label_feature : $scope.label_column}
            dataservice.putCSV($scope.csvFile, otherInfo)
            .then(function () {
                $scope.uploadStatus = "Upload Complete"
            });
        }

    }]);
})();
