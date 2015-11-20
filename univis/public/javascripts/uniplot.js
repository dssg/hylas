var Uniplot = {};
Uniplot.makeBins = function(data, options) {
    // Options must provide either nBins or centers
    if (!('centers' in options)) {
        var nBins = options.nBins;
        var min = Math.min.apply(null, data);
        var max = Math.max.apply(null, data);
        var range = max - min;
        var barWidth = range / nBins;
        var centers = [];
        for (var i = 0; i < nBins; i++) {
            centers.push((i / nBins) * range + min - (barWidth / 2));
        }
    } else {
        var centers = options.centers;
        var nBins = centers.length;
        var barWidth = centers[1] - centers[0];
        var min = centers[0] - barWidth / 2;
        var max = centers[centers.length-1] + barWidth / 2;
        var range = max - min;
    }
    // http://stackoverflow.com/questions/1295584/most-efficient-way-to-create-a-zero-filled-javascript-array
    var height = Array.apply(null, Array(nBins)).map(Number.prototype.valueOf,0);
    data.forEach(function(x) {
        var bin = Math.min(Math.round(((x - min) / range) * nBins), nBins -1);
        height[bin]++;
    });
    return {'centers': centers, 'heights': height, 'barWidth': barWidth, 'nBins': nBins};
}

Uniplot.toData = function(x, y, key) {
    console.log(x);
    console.log(y);
    var points = [];
    for (var i = 0; i < x.length; ++i) {
        points.push({
            'x': x[i],
            'y': y[i]
        });
    }
    return {values: points, key: key};
}

Uniplot.line = function (context, x, y, title, xLabel, yLabel) {
    context.data = [Uniplot.toData(x, y, 'series')];
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

Uniplot.distributions = function (context, positive, negative, special_point, title) {
    var all_entries = positive.concat(negative);
    var hist_all = Uniplot.makeBins(all_entries, {nBins: 10});
    var hist_positive = Uniplot.makeBins(positive, {centers: hist_all.centers});
    var hist_negative = Uniplot.makeBins(negative, {centers: hist_all.centers});
    context.options = {
        chart: {
            type: 'lineChart',
            height: 180,
            x: function(d){return d.x},
            y: function(d){return d.y},
            xAxis: {
                axisLabel: 'X Axis',
                tickFormat: function(d){
                    return d3.format('.02f')(d);
                }
            }
        },
        title: {
            enable: true,
            text: title
        }
    }
    var data_pos = Uniplot.toData(hist_positive.centers, hist_positive.heights, 'positive');
    var data_neg = Uniplot.toData(hist_negative.centers, hist_negative.heights, 'negative');
    var data_special = Uniplot.toData([special_point], [Math.max.apply(null, hist_all.heights)/2], 'value for unit'); 
    context.data = [data_pos, data_neg, data_special];
}
