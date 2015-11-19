var Uniplot = {};
Uniplot.makeBins = function(data, nBins) {
    var min = Math.min.apply(null, data);
    var max = Math.max.apply(null, data);
    var range = max - min;
    // http://stackoverflow.com/questions/1295584/most-efficient-way-to-create-a-zero-filled-javascript-array
    var bins = Array.apply(null, Array(nBins)).map(Number.prototype.valueOf,0);
    data.forEach(function(x) {
        var bin = Math.min(Math.round(((x - min) / range) * nBins), nBins -1);
        bins[bin]++;
    });
    var barWidth = range / nBins;
    var centers = [];
    for (var i = 0; i < nBins; i++) {
        centers.push((i / nBins) * range + min - (barWidth / 2));
    }
    return {'centers': centers, 'height': height};
}

Uniplot.toData = function(x, y) {
    var points = [];
    for (var i = 0; i < x.length; ++i) {
        points.push({
            'x': x[i],
            'y': y[i]
        });
    }
    return [{values: points, key: 'series'}];
}

Uniplot.line = function (context, x, y, title, xLabel, yLabel) {
    context.data = Uniplot.toData(x, y);
    context.options = {
        chart: {
            type: 'lineChart',
            height: 180,
            margin : {
                top: 20,
                right: 20,
                bottom: 40,
                left: 55
            },
            x: function(d){ return d.x; },
            y: function(d){ return d.y; },
            xAxis: {
                axisLabel: xLabel
            },
            yAxis: {
                axislabel: yLabel
            },
        },
        title: {
            enable: true,
            text: title
        }
    }
} 
