var express = require('express');
var http = require('http');

var router = express.Router();

router.get('/top_features', function(req, res, next) {
    var callback = function(response) {
        var body = '';
        response.on('data', function(data) {
            body += data;
        });
            response.on('end', function() {
                //TODO render something
        });
    }
});

/* GET home page. */
router.get('/', function(req, res, next) {
    res.render('index', { title: 'Express' });
});

module.exports = router;
