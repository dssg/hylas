(function () {
    angular.module('univisApp')
    .config(['$routeProvider',
        function($routeProvider) {
            $routeProvider.
                when('/', {
                    templateUrl: 'views/report.html',
                    controller: 'reportCtrl'
                });
        }]);
})()
