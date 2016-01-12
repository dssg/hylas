(function () {
    angular.module('univisApp')
    .controller('uploadCtrl', ['$scope', '$location', 'dataservice',
        function($scope, $location, dataservice) {

        $scope.model = {
            uid_column: 'id',
            label_column: 'label',
            csvFile: undefined,
            pklFile: undefined,
            uploadStatus: '',
            paramsSpec: undefined,
            clfs: []};

        dataservice.getParamSpec()
            .then(function (response) {
                $scope.model.paramSpec = response;
                $scope.model.clfs.push(
                    [Object.keys($scope.model.paramSpec)[0],
                     []]);
            });
    
        function goReport() {
            $location.path('/report');
        }

        //http://stackoverflow.com/questions/25411291/angularjs-inline-check-if-an-array-check
        $scope.isArray = angular.isArray;

        $scope.add_clf = function() {
            $scope.model.clfs.push(['', []]);
        }

        $scope.remove_clf = function() {
            $scope.model.clfs.pop();
        }

        $scope.add_param = function(clf_idx) {
            $scope.model.clfs[clf_idx][1].push(['', []]);
        }

        $scope.remove_param = function(clf_idx) {
            $scope.model.clfs[clf_idx][1].pop();
        }

        $scope.add_param_setting = function(clf_idx, param_idx) {
            $scope.model.clfs[clf_idx][1][param_idx][1].push(null);
        }

        $scope.remove_param_setting = function(clf_idx) {
            $scope.model.clfs[clf_idx][1].pop();
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

        $scope.submitPkl = function() {
            if ($scope.model.pklFile === undefined) {
                $scope.model.uploadStatus = "No file selected";
                return;
            }
            $scope.model.uploadStatus = "working..."
            var otherInfo = {unit_id_feature : $scope.model.uid_column}
            dataservice.putPkl($scope.model.pklFile, otherInfo)
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
