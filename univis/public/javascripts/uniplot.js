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
