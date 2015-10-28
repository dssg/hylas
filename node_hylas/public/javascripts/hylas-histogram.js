var makeBins = function(data, nBins, specialPoint) {
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
    var result = [];
    for (var i = 0; i < nBins; i++) {
        result.push([(i / nBins) * range + min - (barWidth / 2), bins[i]]);
    }
    var specialBin = Math.min(
        Math.round(((specialPoint - min) / range) * nBins), 
        nBins - 1);
    var specialHeight = bins[specialBin];
    return {
        data: result, 
        barWidth: barWidth,
        specialPoint: [specialPoint, specialHeight]
    };
}

var plotHistogram = function(dom_element, data, nBins, special_point) {
    var result = makeBins(data, nBins, special_point);
    var bins = result.data;
    var barWidth = result.barWidth;
    $.plot(dom_element, [
        {
            data: bins, 
            bars: {
                show: true,
                barWidth: barWidth
            }
        },
        {
            data: [result.specialPoint],
            points: { show: true }
        }
    ]);
};
