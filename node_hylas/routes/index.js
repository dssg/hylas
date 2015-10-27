var express = require('express');
var http = require('http');
var url = require('url');

var router = express.Router();

router.get('/data/*', function(req, res, next) {
    var callback = function(response) {
        var body = '';
        response.on('data', function(data) {
            body += data;
        });
            response.on('end', function() {
                res.send(body);
        });
    }
    var dataUrl = req.url.substring(req.url.lastIndexOf('/'));
    // http://stackoverflow.com/questions/6912584/how-to-get-get-query-string-variables-in-express-js-on-node-js
    var data_req = http.get({
        host: 'localhost',
        port: '5000',
        path: dataUrl
    }, callback);
});

/* GET home page. */
router.get('/', function(req, res, next) {
    res.render('index', { title: 'Express' });
});

module.exports = router;
