(function () {
    angular.module('univisApp')
    .config(['$routeProvider',
        function($routeProvider) {
            $routeProvider
                .when('/upload', {
                    templateUrl: 'views/upload.html',
                    controller: 'uploadCtrl'
                })
                .when('/report', {
                    templateUrl: 'views/report.html',
                    controller: 'reportCtrl'
                })
                .when('/download', {
                    templateUrl: 'views/download.html',
                    controller: 'downloadCtrl'
                })
                .otherwise({
                    redirectTo: '/upload'
                });
        }]);
})()
