(function () {
    angular.module('univisApp')
    .controller('uploadCtrl', ['$scope', '$location', 'dataservice',
        function($scope, $location, dataservice) {

        $scope.model = {
            uid_column: 'id',
            label_column: 'label',
            csvFile: undefined,
            uploadStatus: ''};

        function goReport() {
            $location.path('/report');
        }

        $scope.submit = function() {
            if ($scope.model.csvFile === undefined) {
                $scope.model.uploadStatus = "No file selected";
                return;
            }
            $scope.model.uploadStatus = "working..."
            var otherInfo = {unit_id_feature : $scope.model.uid_column,
                             label_feature : $scope.model.label_column}
            dataservice.putCSV($scope.model.csvFile, otherInfo)
            .then(function () {
                $scope.model.uploadStatus = "Upload Complete"
                goReport();
            })
            .catch(function (response) {
                $scope.model.uploadStatus = "Failed with status: " + 
                    response.status;
            });
        }

        //TODO just here for development. Remove in production
        $scope.resetServer = function () {
            dataservice.resetServer();
            goReport();
        }

    }]);
})();
