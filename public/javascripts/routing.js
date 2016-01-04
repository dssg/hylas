(function () {
    angular.module('univisApp')
    .config(['$routeProvider',
        function($routeProvider) {
            $routeProvider.
                when('/report', {
                    templateUrl: 'views/report.html',
                    controller: 'reportCtrl'
                })
                .when('/upload', {
                    templateUrl: 'views/upload.html',
                    controller: 'uploadCtrl'
                })
                .otherwise({
                    redirectTo: '/upload'
                });
        }]);
})()
