(function () {
    angular.module('univisApp')
        .factory('uniplot', [uniplot]);

    function uniplot() {

        var service = {
            makeBins: makeBins,
            toData: toData,
            line: line,
            distributions: distributions
        };

        return service;

        function makeBins(data, options) {
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

        function toData(x, y, key) {
            var points = [];
            for (var i = 0; i < x.length; ++i) {
                points.push({
                    'x': x[i],
                    'y': y[i]
                });
            }
            return {values: points, key: key};
        }

        function line(context, x, y, title, xLabel, yLabel) {
            context.data = [toData(x, y, '')];
            context.options = {
                chart: {
                    type: 'lineChart',
                    height: 180,
                    width: 360,
                    x: function(d){ return d.x; },
                    y: function(d){ return d.y; },
                    xAxis: {
                        tickFormat: function(d){
                            return d3.format('.02f')(d);
                        },
                        axisLabel: xLabel
                    },
                    yAxis: {
                        tickFormat: function(d){
                            return d3.format('.02f')(d);
                        },
                        axisLabel: yLabel
                    },
                    showLegend: false
                },
                title: {
                    enable: true,
                    text: title
                }
            }
        } 

        function distributions(context, positive, negative, special_point, title) {
            var all_entries = positive.concat(negative);
            var hist_all = makeBins(all_entries, {nBins: 10});
            var hist_positive = makeBins(positive, {centers: hist_all.centers});
            var hist_negative = makeBins(negative, {centers: hist_all.centers});
            context.options = {
                chart: {
                    type: 'lineChart',
                    height: 180,
                    width: 360,
                    x: function(d){return d.x},
                    y: function(d){return d.y},
                    xAxis: {
                        tickFormat: function(d){
                            return d3.format('.02f')(d);
                        }
                    },
                    yAxis: {
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
            var data_pos = toData(hist_positive.centers, hist_positive.heights, 'positive');
            var data_neg = toData(hist_negative.centers, hist_negative.heights, 'negative');
            console.log('UNIPLOT::::::::: ' + special_point);
            var data_special = toData([special_point], [1], 'value for unit'); 
            context.data = [data_pos, data_neg, data_special];
        }
    }
})();
